| Field | Value |
|---|---|
| **Phase** | P6 |
| **Status** | `not-started` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | [RAG_CHATBOT](RAG_CHATBOT_SPEC.md) |
| **Blocks** | — |
| **Touches** | `agents/` (new module), `webapp/backend/routers/tailor.py` (new), `webapp/frontend/app/tailor/page.tsx` (new) |

## Overview

`cv.md` is a strong static ground truth, but different high-scoring roles emphasise different parts of the background (military leadership vs fraud ML engineering). An actor/critic multi-agent system drafts a tailored resume variant for any high-scoring job, then critiques it against `profile.md` to eliminate hallucinated skills before presenting the result.

## Behaviour

### Module: `agents/`

**Agent A — Actor (`agents/actor.py`)**
- Input: a single job description (from scored jobs, score >= 7) + base `cv.md`.
- Calls Gemini to produce a tailored version of the CV in Markdown: same sections as the original, reordered/emphasised to match the job's requirements.
- Strict instruction: no new skills or experiences may be invented. Only reorder and reweight existing content.

**Agent B — Critic (`agents/critic.py`)**
- Input: the Actor's draft + `profile.md` + the original `cv.md`.
- Calls Gemini to flag any line in the draft that: (a) adds a skill not in the original CV, (b) overstates seniority, (c) contradicts a dealbreaker in profile.md.
- Returns a structured critique: `{issues: [{line: str, issue_type: str, suggestion: str}], approved: bool}`.

**Orchestrator (`agents/tailor.py`)**
- Runs Actor → Critic. If `approved=False`, feeds the critique back to the Actor for one revision pass (max 2 iterations).
- Returns the final approved draft + the list of issues that were resolved.

### Backend: `webapp/backend/routers/tailor.py`

- `POST /api/tailor` — accepts `{job_id: str}`, looks up the job from scored results, runs the orchestrator, returns `{draft_md: str, issues_resolved: list, iterations: int}`.
- Only accepts jobs with score >= 7 (lower scores rejected with 400).

### Frontend: `webapp/frontend/app/tailor/page.tsx`

- New `/tailor` route.
- Lists high-scoring jobs (score >= 7) from the user's digest.
- User clicks a job → "Tailor CV" button triggers the API call (with a loading spinner).
- Result shows: the tailored CV in a side-by-side Markdown preview (original left, tailored right), plus a collapsible "Critique resolved" section showing what Agent B flagged.
- A "Copy as Markdown" button for the tailored output.

## Files to Touch

- `agents/__init__.py` — new module
- `agents/actor.py` — new
- `agents/critic.py` — new
- `agents/tailor.py` — orchestrator
- `webapp/backend/routers/tailor.py` — new endpoint
- `webapp/backend/main.py` — register tailor router
- `webapp/frontend/app/tailor/page.tsx` — new UI page
- `webapp/frontend/app/layout.tsx` — add "Tailor" nav link

## How to QA

1. Run `uv run python agents/tailor.py <job_id>` with a job scoring >= 7 — returns tailored CV markdown + issues list.
2. Verify the tailored CV contains no skills absent from the original `cv.md` (manual spot-check).
3. Navigate to `/tailor` — high-scoring jobs are listed.
4. Click a job and wait — tailored CV appears side-by-side with the original.
5. Submit a job with score < 7 via the API — 400 returned.
6. `uv run python3 -m pytest tests/ -v` passes.
7. `uv run python score.py --dry-run` passes.
