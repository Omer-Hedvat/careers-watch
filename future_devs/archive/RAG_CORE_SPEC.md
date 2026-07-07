| Field | Value |
|---|---|
| **Phase** | P6 |
| **Status** | `wrapped` |
| **Effort** | M |
| **QA gate** | ✅ Golden set validated on a **partial store (~970/21,056 docs)** on 2026-07-07 — 4/5 questions passed with correct retrieval + citations (fraud-ML → Melio/Forter/Riskified; team-lead titles; remote-DS correct negative; Comeet ATS companies). The 5th (tech stacks in Tier-1 cyber) was corpus-limited, not a retrieval defect. Full ingest blocked by free-tier `gemini-embedding-001` **1,000 requests/day** cap; completing it is tracked in [RAG_EMBEDDINGS_BACKFILL](../RAG_EMBEDDINGS_BACKFILL_SPEC.md). Hardened `embed_texts`: batch 100→32, 429 exponential backoff, immediate abort on per-day quota; ingest is resumable per-batch via content-hash dedup. |
| **Epic** | [RAG_CHATBOT](RAG_CHATBOT_SPEC.md) (child 1 of 3) |
| **Depends on** | — |
| **Blocks** | [RAG_CHAT_API](RAG_CHAT_API_SPEC.md) |
| **Touches** | `rag/` (new module), `.gitignore`, `pyproject.toml` / `uv.lock` |
| **Owner** | Fable |

## Overview

Child 1 of the RAG_CHATBOT epic. Builds the retrieval core: read the job-market
datasets, embed them into a local vector store, and answer natural-language
questions with cited sources — all runnable from the CLI before any web layer
exists. This is the **high-risk** child: retrieval quality is judgment-heavy and
"it runs" is not the bar. Review this child in isolation (golden set below)
before starting RAG_CHAT_API.

**Read [RAG_CHATBOT_SPEC.md](RAG_CHATBOT_SPEC.md) → "Pre-flight decisions" first
and follow them exactly.** Do not choose your own embedding model, dimension,
task types, or persistence path.

## Behaviour

### `rag/ingest.py`
- Reads `new_jobs.json` + `companies.json`.
- Each job → one document: `{title, company, location, description, score (if available)}`. Each company → one document: `{name, category, vc_tier, ats}`.
- Long job descriptions chunked at max 512 tokens with overlap.
- Embeds with `gemini-embedding-001`, `output_dimensionality=768`, `task_type="RETRIEVAL_DOCUMENT"`, **batched** contents, reusing the `_rpm_wait()` limiter pattern from `matcher/gemini_scorer.py`.
- Writes to `PersistentClient(path="rag/.chroma")`; the Chroma collection dimension MUST equal 768.
- Prints the final document count.
- Supports optional `--limit N` to ingest only the first N job docs — for cheap smoke-testing without a full ~10k-embedding run. Full ingest (no `--limit`) is a deliberate, quota-spending step run at the review gate.

### `rag/query.py`
- CLI: `uv run python rag/query.py "<question>"`.
- Embeds the question with `task_type="RETRIEVAL_QUERY"`, retrieves top-K chunks, builds a context window, calls Gemini (`gemini-2.5-flash`, matching existing scorer usage) to answer.
- Returns `{answer: str, sources: list}` where each source names company + job title. Prints answer + sources.
- Exposes a reusable function (e.g. `answer_question(question, history=None) -> dict`) that RAG_CHAT_API will import — do not bury the logic in `__main__`.

### `rag/refresh.py`
- Re-runs ingest on demand. Idempotent: skips documents already in the store by content hash (do not re-embed unchanged docs — saves quota).

### Edge cases
- Empty/absent store → `query.py` returns a friendly "No job data indexed yet. Run the pipeline first." (a value/exception the API layer can turn into a clean message), never a stack trace.

## Files to Touch
- `rag/__init__.py` — new
- `rag/ingest.py` — new
- `rag/query.py` — new
- `rag/refresh.py` — new
- `.gitignore` — add `rag/.chroma/` (same commit as ingest)
- `pyproject.toml` / `uv.lock` — add `chromadb` (the ONLY new dependency; ask before adding anything else)

## How to QA
1. `uv run python rag/ingest.py` — no errors; `rag/.chroma/` created; reports a document count in the thousands.
2. `uv run python rag/query.py "What companies are hiring for fraud ML?"` — answer + source citations.
3. **Retrieval golden set** (acceptance test — see the table in RAG_CHATBOT_SPEC.md "How to QA" step 3). Run all 5 questions; eyeball cited sources against the raw JSON; record pass/fail per question in task notes. Confidently-wrong or empty sources = retrieval is broken; fix before marking complete.
4. Re-run `rag/refresh.py` — second run re-embeds nothing (idempotent by content hash).
5. `git status` shows no `rag/.chroma/` files staged.
6. `uv run python3 -m pytest tests/ -v` passes.
7. `uv run python score.py --dry-run` passes.
