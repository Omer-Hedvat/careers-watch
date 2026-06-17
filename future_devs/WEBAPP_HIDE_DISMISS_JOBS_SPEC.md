| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | WEBAPP_JOBSEEKER_WORKFLOW |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/backend/routers/jobs.py`, `webapp/frontend/app/digest/page.tsx`, `webapp/supabase/migrations/` (if a new column is needed) |

## Overview

Irrelevant jobs keep showing; there's no "not interested" to remove noise from the active list.

## Behaviour

- A "Not interested / Hide" action per card removes the job from the active list and remembers the choice per user. Persist via a `hidden` bool on `scored_jobs`, or a reserved status value. Coordinate with WEBAPP_APPLICATION_TRACKER to avoid adding a duplicate column for the same "out of the active list" concept - agree on one representation.
- A "Show N hidden" toggle lets the user review hidden jobs and unhide them (mirroring the existing applied collapse section).

## Files to Touch

- `webapp/backend/routers/jobs.py` — endpoint to set/clear hidden; exclude hidden from the default active list
- `webapp/frontend/app/digest/page.tsx` — Hide action per card, "Show N hidden" toggle, unhide control
- `webapp/supabase/migrations/` — `hidden` bool column (only if not represented as a status value per the coordination note)

## How to QA

1. Hiding a job removes it from the active list and the choice persists across reload.
2. Hidden jobs are reviewable via the "Show N hidden" toggle and can be unhidden.
3. No duplicate column conflicts with WEBAPP_APPLICATION_TRACKER.
4. `uv run python3 -m pytest tests/ -v` passes.
5. `uv run python score.py --dry-run` passes.
