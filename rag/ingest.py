#!/usr/bin/env python3
"""Ingest new_jobs.json + companies.json into the local Chroma vector store.

Each job becomes one document (title, company, location, description, score if
available); long descriptions are chunked at ~512 tokens with overlap. Each
company becomes one document (name, category, vc_tier, ats). Documents are
embedded with gemini-embedding-001 (768 dims, RETRIEVAL_DOCUMENT) in batches
and stored in rag/.chroma. Idempotent: document IDs are content hashes, so
unchanged docs are never re-embedded.

Usage:
    uv run python rag/ingest.py             # full ingest (~10k docs - quota-spending)
    uv run python rag/ingest.py --limit 40  # smoke test: first 40 jobs + 40 companies
"""

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag import (
    EMBED_BATCH_SIZE,
    REPO_ROOT,
    embed_texts,
    get_chroma_collection,
    get_gemini_client,
)

# ~512 tokens at roughly 0.75 words/token, with overlap to avoid boundary loss.
CHUNK_WORDS = 350
CHUNK_OVERLAP_WORDS = 50


def _chunk_text(text: str) -> list[str]:
    """Split text into overlapping word-window chunks of ~512 tokens."""
    words = text.split()
    if len(words) <= CHUNK_WORDS:
        return [text]
    chunks = []
    step = CHUNK_WORDS - CHUNK_OVERLAP_WORDS
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + CHUNK_WORDS]))
        if start + CHUNK_WORDS >= len(words):
            break
    return chunks


def _doc_id(prefix: str, text: str) -> str:
    return f"{prefix}-{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def _job_documents(jobs: list[dict]) -> list[tuple[str, str, dict]]:
    docs = []
    for job in jobs:
        title = str(job.get("title") or "").strip()
        company = str(job.get("company") or "").strip()
        location = str(job.get("location") or "").strip()
        description = html.unescape(str(job.get("description") or "")).strip()
        score = job.get("score")

        header = f"Job: {title}\nCompany: {company}\nLocation: {location}"
        if score is not None:
            header += f"\nScore: {score}"

        chunks = _chunk_text(description) if description else [""]
        n_chunks = len(chunks)
        for idx, chunk in enumerate(chunks):
            part = f" (part {idx + 1}/{n_chunks})" if n_chunks > 1 else ""
            text = f"{header}\nDescription{part}: {chunk}"
            meta = {
                "type": "job",
                "company": company,
                "title": title,
                "location": location,
                "chunk": idx,
            }
            docs.append((_doc_id("job", text), text, meta))
    return docs


def _company_documents(companies: list[dict]) -> list[tuple[str, str, dict]]:
    docs = []
    for c in companies:
        name = str(c.get("name") or "").strip()
        if not name:
            continue
        category = str(c.get("category") or "unknown")
        vc_tier = str(c.get("vc_tier") or "unknown")
        ats = str(c.get("ats") or "unknown")
        text = (
            f"Company: {name}\nCategory: {category}\n"
            f"VC tier: {vc_tier}\nATS: {ats}"
        )
        meta = {"type": "company", "company": name, "title": "", "location": "", "chunk": 0}
        docs.append((_doc_id("company", text), text, meta))
    return docs


def ingest(limit: int | None = None) -> dict:
    """Build, embed, and store documents. Returns {total, embedded, skipped}."""
    jobs = json.loads((REPO_ROOT / "new_jobs.json").read_text(encoding="utf-8"))
    companies = json.loads((REPO_ROOT / "companies.json").read_text(encoding="utf-8"))
    if limit is not None:
        jobs = jobs[:limit]
        companies = companies[:limit]
    print(f"[ingest] {len(jobs)} jobs + {len(companies)} companies loaded"
          + (f" (limit={limit})" if limit is not None else ""))

    docs = _job_documents(jobs) + _company_documents(companies)

    # Dedup by content-hash ID (identical postings collapse to one doc).
    seen: set[str] = set()
    unique: list[tuple[str, str, dict]] = []
    for doc in docs:
        if doc[0] not in seen:
            seen.add(doc[0])
            unique.append(doc)

    collection = get_chroma_collection(create=True)
    existing = set(collection.get(include=[])["ids"])
    new_docs = [d for d in unique if d[0] not in existing]
    skipped = len(unique) - len(new_docs)
    print(f"[ingest] {len(unique)} unique documents - {len(new_docs)} to embed, "
          f"{skipped} already in store")

    if new_docs:
        client = get_gemini_client()
        for start in range(0, len(new_docs), EMBED_BATCH_SIZE):
            batch = new_docs[start:start + EMBED_BATCH_SIZE]
            vectors = embed_texts(client, [t for _, t, _ in batch], "RETRIEVAL_DOCUMENT")
            collection.add(
                ids=[i for i, _, _ in batch],
                embeddings=vectors,
                documents=[t for _, t, _ in batch],
                metadatas=[m for _, _, m in batch],
            )
            done = min(start + EMBED_BATCH_SIZE, len(new_docs))
            print(f"[ingest] embedded {done}/{len(new_docs)}")

    total = collection.count()
    print(f"[ingest] done - {total} documents in store "
          f"({len(new_docs)} newly embedded, {skipped} skipped)")
    return {"total": total, "embedded": len(new_docs), "skipped": skipped}


def main():
    parser = argparse.ArgumentParser(description="Ingest job-market data into the RAG store.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Ingest only the first N jobs and N companies (smoke test).")
    args = parser.parse_args()
    ingest(limit=args.limit)


if __name__ == "__main__":
    main()
