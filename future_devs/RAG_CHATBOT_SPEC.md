| Field | Value |
|---|---|
| **Phase** | P6 |
| **Status** | `not-started` |
| **Effort** | L |
| **Epic** | RAG_CHATBOT (this is the epic root) |
| **Depends on** | — |
| **Blocks** | [MULTI_AGENT_RESUME_TAILOR](MULTI_AGENT_RESUME_TAILOR_SPEC.md) |
| **Touches** | `rag/` (new module), `webapp/backend/routers/chat.py` (new), `webapp/frontend/app/chat/page.tsx` (new) |

## Overview

`new_jobs.json` and `companies.json` are rich, continuously-updated datasets that currently feed only static scoring. This epic adds a local vector store + chat interface so the user can query macro trends across the full job market in natural language: "What tech stacks are common in Tier 1 cyber startups right now?", "Which companies are hiring for fraud ML?", "Am I overqualified for roles scoring below 6?"

This is the next planned AI/experimental epic per the project roadmap.

## Behaviour

### Module: `rag/`

- `rag/ingest.py` — reads `new_jobs.json` + `companies.json`, chunks documents, embeds them, writes to a local vector store (ChromaDB preferred; FAISS acceptable).
  - Each job is one document: `{title, company, location, description, score (if available)}`.
  - Each company is one document: `{name, category, vc_tier, ats}`.
  - Embeddings use Gemini's embedding model (via `google-genai` — no new dependency).
- `rag/query.py` — given a natural-language question, retrieves top-K relevant chunks, builds a context window, calls Gemini to answer, and returns the response with source citations (company + job title).
- `rag/refresh.py` — re-runs ingest whenever `new_jobs.json` is updated (or on demand). Idempotent: skips documents already in the store by content hash.

### Backend: `webapp/backend/routers/chat.py`

- `POST /api/chat` — accepts `{question: str, history: list}`, calls `rag/query.py`, returns `{answer: str, sources: list}`.
- Rate-limited per user session (max 20 queries/hour) to avoid Gemini quota burn.

### Frontend: `webapp/frontend/app/chat/page.tsx`

- New `/chat` route with a chat UI: message thread, text input, send button.
- Each assistant response shows a collapsible "Sources" section listing the job/company documents retrieved.
- History is session-scoped (not persisted to Supabase in this task).
- Navigation: "Chat" link added to main nav.

### Edge cases

- If the vector store is empty (ingest has not run), the chat endpoint returns a friendly error: "No job data indexed yet. Run the pipeline first."
- Long job descriptions are chunked (max 512 tokens per chunk) with overlap to avoid context loss at boundaries.

## Files to Touch

- `rag/__init__.py` — new module
- `rag/ingest.py` — new
- `rag/query.py` — new
- `rag/refresh.py` — new
- `webapp/backend/routers/chat.py` — new endpoint
- `webapp/backend/main.py` — register chat router
- `webapp/frontend/app/chat/page.tsx` — new chat UI page
- `webapp/frontend/app/layout.tsx` — add "Chat" nav link
- `pyproject.toml` / `uv.lock` — add `chromadb` dependency (ask before adding anything else)

## How to QA

1. Run `uv run python rag/ingest.py` — no errors; vector store is created.
2. Run `uv run python rag/query.py "What companies are hiring for fraud ML?"` — returns an answer with source citations.
3. Navigate to `/chat` in the webapp — chat UI renders.
4. Ask a question in the UI — response appears with sources collapsed.
5. Ask a question when the vector store is empty — friendly error message, no 500.
6. `uv run python3 -m pytest tests/ -v` passes.
7. `uv run python score.py --dry-run` passes.
