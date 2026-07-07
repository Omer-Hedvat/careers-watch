| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `wrapped` |
| **Effort** | M |
| **Epic** | WEBAPP_JOBSEEKER_WORKFLOW |
| **Depends on** | [WEBAPP_FLAG_GLOSSARY](WEBAPP_FLAG_GLOSSARY_SPEC.md) |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/digest/page.tsx` (+ detail panel/route), `webapp/backend/routers/jobs.py`, `score.py` (persist description), `webapp/supabase/migrations/` (if description stored) |

## Overview

Reasoning is clamped to 2 lines, clicking a card does nothing, and there's no way to read the full reasoning or the job description in-app before applying.

## Behaviour

- Clicking a card opens a detail view (a side panel or a `/digest/[id]` route) showing: full reasoning, all flags with their glossary labels (reuse WEBAPP_FLAG_GLOSSARY), score + tier band, company + location, and the full job description.
- The full description is not on `scored_jobs` today. Expose it via one of two options:
  - **Option A (request-time match):** match the scored job to `new_jobs.json` by `apply_url` when the detail is requested. No migration, but fragile if `new_jobs.json` rotates.
  - **Option B (store at score time, recommended):** persist the description onto `scored_jobs` when the job is scored, so the detail is durable and independent of `new_jobs.json`. This requires a migration adding a `description` column.
  - Recommend Option B for durability. If Option B is chosen, call out the migration `webapp/supabase/migrations/00X_scored_jobs_description.sql` and update `score.py` (or the scoring write path) to persist the description.
- Apply + Mark-applied (or set-status) actions are available from the detail view.
- Edge case: a missing description degrades gracefully, showing "Full description unavailable - open the posting" with the Apply link still active.

## Files to Touch

- `webapp/frontend/app/digest/page.tsx` — card click handler + detail panel, or a new `/digest/[id]` route
- `webapp/backend/routers/jobs.py` — `GET /jobs/{id}` returning full reasoning + description (request-time match if Option A)
- `score.py` (or the scoring write path) — persist the description onto `scored_jobs` (Option B)
- `webapp/supabase/migrations/` — `description` column on `scored_jobs` (Option B only)

## How to QA

1. Clicking a card opens the detail view with full reasoning + full description.
2. All flags show with their glossary labels; score + tier band, company, and location are shown.
3. Apply and status actions work from the detail view.
4. A job with no stored description still opens without error and shows the graceful fallback.
5. `uv run python3 -m pytest tests/ -v` passes.
6. `uv run python score.py --dry-run` passes.
