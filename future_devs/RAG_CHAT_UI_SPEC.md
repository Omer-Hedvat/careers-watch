| Field | Value |
|---|---|
| **Phase** | P6 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | [RAG_CHATBOT](RAG_CHATBOT_SPEC.md) (child 3 of 3) |
| **Depends on** | [RAG_CHAT_API](RAG_CHAT_API_SPEC.md) |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/chat/page.tsx` (new), `webapp/frontend/app/layout.tsx` |
| **Owner** | Fable |

## Overview

Child 3 of the RAG_CHATBOT epic. The `/chat` UI over `POST /api/chat`. Low risk,
boilerplate-shaped. Do not start until RAG_CHAT_API is done.

## Behaviour

### `webapp/frontend/app/chat/page.tsx`
- New `/chat` route: message thread, text input, send button.
- On send: show a "thinking…" state while awaiting the **blocking** `/api/chat` response (no streaming / SSE).
- Each assistant response shows a collapsible "Sources" section (collapsed by default) listing the retrieved job/company documents (company + job title).
- History is session-scoped only — not persisted to Supabase in this task.
- Match the existing webapp visual design system (P10) — reuse existing components/tokens, don't invent new styling.

### `webapp/frontend/app/layout.tsx`
- Add a "Chat" link to the main nav.

## Files to Touch
- `webapp/frontend/app/chat/page.tsx` — new
- `webapp/frontend/app/layout.tsx` — add "Chat" nav link

## How to QA
1. Navigate to `/chat` — UI renders; "Chat" appears in main nav.
2. Ask a question — "thinking…" state shows, then the response appears with Sources collapsed.
3. Expand Sources — lists the cited company + job titles from the API.
4. Ask a question with an empty vector store — friendly message renders, no crash.
5. `uv run python3 -m pytest tests/ -v` passes.
6. `uv run python score.py --dry-run` passes.
