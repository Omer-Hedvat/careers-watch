| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | M |
| **Epic** | WEBAPP_JOBSEEKER_WORKFLOW |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/supabase/migrations/00X_application_status.sql` (new), `webapp/backend/routers/jobs.py`, `webapp/frontend/app/digest/page.tsx` |

## Overview

"Applied" is a single binary; a job seeker juggling many applications needs status, dates, and notes.

## Behaviour

- Replace the binary `applied` with a status: `not-set` / `saved` / `applied` / `interviewing` / `rejected` / `offer`. Store `status`, `status_updated_at`, and an optional free-text `note` per scored job per user. The migration adds these columns. Keep the existing `applied` bool in sync (or migrate existing `applied=true` rows to `status='applied'`).
- The digest shows the current status as a pill on each card; a small control changes it (dropdown or segmented control).
- Applied/closed statuses (`applied`, `rejected`, `offer`) collapse out of the active list, like the existing applied section.
- A simple filter by status.
- A full kanban board is explicitly out of scope (note as a possible follow-up).

## Files to Touch

- `webapp/supabase/migrations/00X_application_status.sql` — new migration adding `status`, `status_updated_at`, `note`; backfill `applied` rows
- `webapp/backend/routers/jobs.py` — replace/extend `POST /jobs/{id}/applied` with a set-status endpoint; expose `status`/`note` in `GET /jobs`
- `webapp/frontend/app/digest/page.tsx` — status pill, status control, status filter, active-list collapse logic

## How to QA

1. A status can be set on a job and persists across reload.
2. A status pill shows on the card reflecting the current status.
3. `applied`, `rejected`, and `offer` statuses collapse out of the active list.
4. Filtering by status works.
5. The migration applies cleanly (existing `applied=true` rows become `status='applied'`).
6. `uv run python3 -m pytest tests/ -v` passes.
7. `uv run python score.py --dry-run` passes.
