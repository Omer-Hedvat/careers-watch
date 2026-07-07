"""RAG core for careers-watch.

Shared plumbing for the rag/ module: Gemini client construction, batched
embedding with an RPM limiter, and access to the persistent Chroma store.

Binding decisions (from RAG_CHATBOT_SPEC.md pre-flight - do not change):
- Embedding model: gemini-embedding-001, output_dimensionality=768
- Docs embed with task_type=RETRIEVAL_DOCUMENT, queries with RETRIEVAL_QUERY
- Persistence: chromadb PersistentClient at rag/.chroma (gitignored)
"""

import os
import threading
import time
from collections import deque
from pathlib import Path

RAG_DIR = Path(__file__).resolve().parent
REPO_ROOT = RAG_DIR.parent
CHROMA_PATH = RAG_DIR / ".chroma"  # resolves to rag/.chroma regardless of cwd
COLLECTION_NAME = "careers_watch"
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768
EMBED_BATCH_SIZE = 32  # contents per embed_content call (kept small to stay under per-request token caps)

# ---------------------------------------------------------------------------
# Per-minute rate limiter - mirrored from matcher/gemini_scorer.py so this
# module stays importable on its own (sliding window, thread-safe).
# ---------------------------------------------------------------------------

_RPM_LIMIT = int(os.environ.get("GEMINI_RPM", "8"))
_rpm_lock = threading.Lock()
_rpm_timestamps: deque = deque()  # timestamps of recent calls (seconds)


def _rpm_wait():
    """Block until it is safe to make another Gemini API call."""
    while True:
        with _rpm_lock:
            now = time.monotonic()
            while _rpm_timestamps and now - _rpm_timestamps[0] >= 60.0:
                _rpm_timestamps.popleft()
            if len(_rpm_timestamps) < _RPM_LIMIT:
                _rpm_timestamps.append(now)
                return
            oldest = _rpm_timestamps[0]
            wait_secs = 60.0 - (now - oldest) + 0.05
        time.sleep(wait_secs)


# ---------------------------------------------------------------------------
# Gemini client
# ---------------------------------------------------------------------------

def get_gemini_client():
    """Build a Gemini client from GEMINI_API_KEY (loaded via .env), as score.py does."""
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set - add it to .env in the repo root.")
    from google import genai

    return genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def _embed_with_backoff(client, batch: list[str], task_type: str, max_retries: int = 6):
    """One embed_content call, retrying on 429 RESOURCE_EXHAUSTED with exponential backoff."""
    from google.genai.errors import ClientError

    delay = 5.0
    for attempt in range(max_retries):
        _rpm_wait()
        try:
            return client.models.embed_content(
                model=EMBED_MODEL,
                contents=batch,
                config={
                    "task_type": task_type,
                    "output_dimensionality": EMBED_DIM,
                },
            )
        except ClientError as exc:
            msg = str(exc)
            is_429 = getattr(exc, "code", None) == 429 or "RESOURCE_EXHAUSTED" in msg
            # A per-day quota won't clear until tomorrow - retrying just burns more of it.
            if is_429 and "PerDay" in msg:
                raise RuntimeError(
                    "Daily free-tier embedding quota (1000 requests/day) exhausted. "
                    "Resume tomorrow (store is persistent - already-embedded docs are skipped), "
                    "or enable billing on the Gemini project to finish now."
                ) from exc
            if not is_429 or attempt == max_retries - 1:
                raise
            print(f"[embed] 429 rate-limited, backing off {delay:.0f}s "
                  f"(attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
            delay = min(delay * 2, 120.0)


def embed_texts(client, texts: list[str], task_type: str) -> list[list[float]]:
    """Embed texts in batches. task_type is RETRIEVAL_DOCUMENT or RETRIEVAL_QUERY."""
    vectors: list[list[float]] = []
    for start in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[start:start + EMBED_BATCH_SIZE]
        resp = _embed_with_backoff(client, batch, task_type)
        for emb in resp.embeddings:
            if len(emb.values) != EMBED_DIM:
                raise RuntimeError(
                    f"Embedding dimension {len(emb.values)} != expected {EMBED_DIM}"
                )
            vectors.append(list(emb.values))
    return vectors


# ---------------------------------------------------------------------------
# Chroma store
# ---------------------------------------------------------------------------

def get_chroma_collection(create: bool = False):
    """Open the persistent Chroma collection. Raises if absent and create=False."""
    import chromadb
    from chromadb.config import Settings

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False),
    )
    if create:
        return client.get_or_create_collection(
            COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )
    return client.get_collection(COLLECTION_NAME)
