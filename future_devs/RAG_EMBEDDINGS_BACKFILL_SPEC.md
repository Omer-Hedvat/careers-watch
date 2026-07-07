| Field | Value |
|---|---|
| **Phase** | P6 |
| **Status** | `not-started` |
| **Effort** | XS (ops) |
| **Epic** | [RAG_CHATBOT](RAG_CHATBOT_SPEC.md) (follow-up to RAG_CORE) |
| **Depends on** | RAG_CORE ✅ |
| **Blocks** | — (RAG_CHAT_API can proceed on the partial store; full store improves answer quality) |
| **Touches** | none (data/ops only — runs `rag/ingest.py`, no code change expected) |
| **Owner** | Fable |

## Why this exists

RAG_CORE was wrapped with retrieval mechanics validated on a **partial store (~970 of 21,056 docs, ~4.6%)**. The full ingest could not complete because `gemini-embedding-001` on the **free tier is capped at 1,000 embedding requests/day** (`EmbedContentRequestsPerDayPerUserPerProjectPerModel-FreeTier`). Today's budget was consumed. The store is persistent and `rag/ingest.py` is idempotent (content-hash dedup), so ingestion resumes exactly where it stopped.

The golden set passed 4/5 on the partial store; the one weak answer ("tech stacks in Tier-1 cyber") was corpus-limited — the embedded subset is mostly company profiles, and stack detail lives in job descriptions not yet embedded. Completing the ingest is expected to close that gap.

## Task

Finish embedding the full corpus, then re-validate.

1. **Complete the ingest** — either:
   - **Fast path (recommended):** enable billing on the Gemini project, then `uv run python rag/ingest.py` — finishes in ~10 min (resumes from ~970).
   - **Free path:** run `uv run python rag/ingest.py` once per day (quota resets ~midnight Pacific). Remainder (~20k docs ≈ ~628 requests at batch 32) fits within one day's 1,000-request budget if paced to avoid 429 waste; allow 1-2 days. The `PerDay`-abort in `rag/__init__.py:_embed_with_backoff` stops cleanly when the daily cap is hit.
2. **Confirm store count** ≈ 21,056 docs (`uv run python -c "from rag import get_chroma_collection; print(get_chroma_collection().count())"`).
3. **Re-run the full golden set** (the 5 questions in `future_devs/archive/RAG_CORE_SPEC.md` → "How to QA" step 3) against the complete store. Confirm the "tech stacks in Tier-1 cyber" question now returns real stack detail from job descriptions.

## How to QA

1. Store count ≈ 21,056 (not ~970).
2. All 5 golden-set questions return well-grounded, correctly-cited answers; the tech-stack question is no longer corpus-limited.
3. `uv run python3 -m pytest tests/ -v` passes.
4. `uv run python score.py --dry-run` passes.
