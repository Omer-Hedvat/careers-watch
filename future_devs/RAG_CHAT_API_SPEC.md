| Field | Value |
|---|---|
| **Phase** | P6 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | [RAG_CHATBOT](RAG_CHATBOT_SPEC.md) (child 2 of 3) |
| **Depends on** | [RAG_CORE](RAG_CORE_SPEC.md) |
| **Blocks** | [RAG_CHAT_UI](RAG_CHAT_UI_SPEC.md) |
| **Touches** | `webapp/backend/routers/chat.py` (new), `webapp/backend/main.py` |
| **Owner** | Fable |

## Overview

Child 2 of the RAG_CHATBOT epic. Thin FastAPI wrapper over `rag/query.py`'s
`answer_question(...)`. Low risk — no retrieval logic here, just wiring and
rate-limiting. Do not start until RAG_CORE's golden set has passed.

**Blocking response, not streaming** (per RAG_CHATBOT_SPEC.md pre-flight decision 3).

## Behaviour

### `webapp/backend/routers/chat.py`
- `POST /api/chat` — accepts `{question: str, history: list}`, calls `rag.query.answer_question(question, history)`, returns `{answer: str, sources: list}` in a single response.
- Rate-limited per user session: max 20 queries/hour, to avoid Gemini quota burn. Match the existing per-user/session rate-limit pattern already used elsewhere in `webapp/backend/` rather than inventing a new one.
- Empty vector store → return a clean 200 (or documented 4xx) with the friendly "No job data indexed yet. Run the pipeline first." message, never a 500.

### `webapp/backend/main.py`
- Register the chat router alongside the existing routers.

## Files to Touch
- `webapp/backend/routers/chat.py` — new
- `webapp/backend/main.py` — register router

## How to QA
1. Start the backend; `POST /api/chat` with `{"question": "Which companies are hiring for fraud ML?", "history": []}` returns `{answer, sources}` — a single JSON response, no streaming.
2. Fire 21 requests in an hour on one session — the 21st is rate-limited with a clear message, not a 500.
3. With an empty/absent `rag/.chroma/`, the endpoint returns the friendly message, no 500.
4. `uv run python3 -m pytest tests/ -v` passes.
5. `uv run python score.py --dry-run` passes.
