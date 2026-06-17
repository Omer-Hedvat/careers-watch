| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | L |
| **Epic** | WEBAPP_JOBSEEKER_WORKFLOW |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/digest/page.tsx`, `webapp/backend/routers/jobs.py`, `webapp/supabase/migrations/` |

## Overview

The digest is read-only triage with a single binary "applied" toggle. A real job seeker needs to read the full posting in-app, track application status over time, dismiss irrelevant roles, see what's new since the last visit, and control sorting. These tools turn a ranked list into a job-hunt workspace.

This is the epic root for WEBAPP_JOBSEEKER_WORKFLOW. It coordinates five children that together upgrade the digest from a static triage list into a recurring-use workspace.

## Behaviour

The five children of this epic:

- **WEBAPP_JOB_DETAIL_VIEW** — Clicking a card opens a detail view with full reasoning, all flags, score/tier, company/location, and the full job description.
- **WEBAPP_APPLICATION_TRACKER** — Replaces the binary `applied` with a status (not-set / saved / applied / interviewing / rejected / offer), plus a per-job note and status date.
- **WEBAPP_HIDE_DISMISS_JOBS** — A "Not interested / Hide" action removes a job from the active list and remembers the choice.
- **WEBAPP_NEW_SINCE_LAST_VISIT** — Tracks a per-user `last_seen_at` and badges jobs scored since the previous visit.
- **WEBAPP_DIGEST_SORT_PERSIST** — Explicit sort controls plus localStorage persistence of filter/sort/min-score state.

Migration coordination note: several children add columns to `scored_jobs` (`status`, `hidden`, `note`) and a per-user `last_seen_at`. These migrations must be coordinated so column names do not collide. In particular WEBAPP_HIDE_DISMISS_JOBS and WEBAPP_APPLICATION_TRACKER both touch the "is this job out of the active list" concept - they must agree on whether `hidden` is a separate bool or a reserved status value, and not add a duplicate column.

## Files to Touch

- `webapp/frontend/app/digest/page.tsx` — the workspace surface that all children extend
- `webapp/backend/routers/jobs.py` — endpoints for detail, status, hide, last-seen
- `webapp/supabase/migrations/` — coordinated migrations adding `status`, `hidden`, `note`, `last_seen_at` (and optionally `description`)

## How to QA

1. Each child task's QA passes on its own.
2. End-to-end: a user can open a job and read its full reasoning + description, set its application status, hide noise, and see a "X new since your last visit" summary.
3. `uv run python3 -m pytest tests/ -v` passes.
4. `uv run python score.py --dry-run` passes.
