| Field | Value |
|---|---|
| **Phase** | P6 |
| **Status** | `not-started` |
| **Effort** | L |
| **Epic** | RAG_CHATBOT (this is the epic root) |
| **Depends on** | — |
| **Blocks** | [MULTI_AGENT_RESUME_TAILOR](MULTI_AGENT_RESUME_TAILOR_SPEC.md) |
| **Touches** | `rag/` (new module), `webapp/backend/routers/chat.py` (new), `webapp/frontend/app/chat/page.tsx` (new) |
| **Owner** | Fable |

## Children (execute in order)

This spec is the epic root and shared brief. Implementation is split into three
children — run each under `/start_task`, and **review child 1's golden set
before starting child 2**. All children inherit the "Pre-flight decisions" block
below.

| # | Slug | Scope | Risk | Effort |
|---|---|---|---|---|
| 1 | [RAG_CORE](RAG_CORE_SPEC.md) | `rag/` module: ingest + query + refresh | **High** (retrieval quality) | M |
| 2 | [RAG_CHAT_API](RAG_CHAT_API_SPEC.md) | `chat.py` router + `main.py` register | Low | S |
| 3 | [RAG_CHAT_UI](RAG_CHAT_UI_SPEC.md) | `/chat` page + nav link | Low | S |

## Overview

`new_jobs.json` and `companies.json` are rich, continuously-updated datasets that currently feed only static scoring. This epic adds a local vector store + chat interface so the user can query macro trends across the full job market in natural language: "What tech stacks are common in Tier 1 cyber startups right now?", "Which companies are hiring for fraud ML?", "Am I overqualified for roles scoring below 6?"

This is the next planned AI/experimental epic per the project roadmap.

## Pre-flight decisions (resolved — do NOT re-litigate)

These are locked so the implementer executes instead of guessing. Honor them exactly.

1. **Embedding model + dimensions.** Use `gemini-embedding-001` via the existing `google-genai` SDK — reuse the `from google import genai; client = genai.Client(api_key=...)` pattern already in `score.py`. Call `client.models.embed_content(model="gemini-embedding-001", contents=[...])`. Set `output_dimensionality=768` (keeps the store lean; the Chroma collection dimension MUST match this exactly). Set `task_type="RETRIEVAL_DOCUMENT"` when embedding docs in `ingest.py` and `task_type="RETRIEVAL_QUERY"` when embedding the user question in `query.py` — these are different and both are required for good retrieval.
   - **Quota:** the ingest pass embeds ~10k job docs. Batch the `contents` list (embed many per call, do not loop one-at-a-time) and reuse the RPM limiter pattern from `matcher/gemini_scorer.py` (`_rpm_wait()` / `GEMINI_RPM` env var, default 8). Do not spin a naive tight loop that burns quota.

2. **Vector-store persistence + gitignore.** Persist ChromaDB to `rag/.chroma/` (a `PersistentClient(path="rag/.chroma")`). Add `rag/.chroma/` to `.gitignore` in the SAME commit that adds ingest. The embedded store is a rebuildable artifact and MUST NOT be committed.

3. **Response mode: blocking, not streaming.** `POST /api/chat` returns the full `{answer, sources}` JSON in one response. Do NOT build SSE / token streaming — it does not match the spec's payload shape and adds risk. The frontend shows a simple "thinking…" state while awaiting the response.

4. **No matching logic.** This epic queries the job *market*, not the candidate. Do NOT read, import, or reason over `profile.md` / `cv.md` here — that is the scorer's job, not the chatbot's. The only new dependency is `chromadb`; per CLAUDE.md, ask before adding anything else.

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

1. Run `uv run python rag/ingest.py` — no errors; vector store is created at `rag/.chroma/`, and it reports the document count (should be in the thousands, not zero).
2. Run `uv run python rag/query.py "What companies are hiring for fraud ML?"` — returns an answer with source citations.
3. **Retrieval golden set (acceptance test, not a smoke test).** Running smoothly is NOT the bar — retrieving the *right* documents is. Run each question below and confirm the cited sources actually contain the expected companies/roles. A lighter-tier implementer will produce code that runs but retrieves poorly; this step is what catches it. Record pass/fail per question in the task notes.

   | Question | Expected in cited sources |
   |---|---|
   | "Which companies are hiring for fraud ML?" | Companies whose job descriptions mention fraud + ML (cross-check against `new_jobs.json`) |
   | "What tech stacks are common in Tier 1 cyber startups?" | Jobs from `vc_tier: 1` cyber companies; answer names real stacks (Python, K8s, etc.) |
   | "Which roles are team lead or lead positions?" | Job titles containing "Lead" / "Team Lead" |
   | "Show me remote-friendly data science roles." | Jobs whose location/description indicate remote flexibility |
   | "Which companies use Comeet as their ATS?" | Companies with `ats: comeet` in `companies.json` |

   For each: eyeball the retrieved sources against the raw JSON. If a question returns confidently-wrong or empty sources, the retrieval layer (chunking, `task_type`, top-K, or dimension mismatch) is broken — fix before marking complete.
4. Navigate to `/chat` in the webapp — chat UI renders.
5. Ask a question in the UI — response appears with sources collapsed; a "thinking…" state shows while awaiting (blocking response, no streaming).
6. Ask a question when the vector store is empty — friendly error message, no 500.
7. Confirm `rag/.chroma/` is gitignored (`git status` shows no `.chroma` files staged).
8. `uv run python3 -m pytest tests/ -v` passes.
9. `uv run python score.py --dry-run` passes.
