| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | WEBAPP_JOBSEEKER_WORKFLOW |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/backend/routers/user.py` or `jobs.py`, `webapp/frontend/app/digest/page.tsx`, `webapp/supabase/migrations/` (last_seen_at) |

## Overview

Returning users can't tell what's new since they last looked - core to a recurring-use product.

## Behaviour

- Track a per-user `last_seen_at`, updated when the digest loads. Jobs scored after the PREVIOUS `last_seen_at` get a "New" badge and a top summary "X new since your last visit".
- A quick "show only new" filter.
- Read the previous `last_seen_at` to compute "new", then update it to now - so the very next visit clears the "new" markers.
- Edge case: first-ever visit (no prior `last_seen_at`). Pick and document one behaviour: either show everything as new, or suppress the banner on first visit. (Documented choice: suppress the banner on first visit and do not badge anything, since "everything is new" is noise on first run.)

## Files to Touch

- `webapp/backend/routers/user.py` or `jobs.py` — read/update `last_seen_at`; return previous value so the frontend can compute "new"
- `webapp/frontend/app/digest/page.tsx` — "New" badge, summary banner, "show only new" filter
- `webapp/supabase/migrations/` — per-user `last_seen_at` column (or row)

## How to QA

1. After a scan, jobs scored since the previous visit show a "New" badge and the summary count.
2. Reloading and returning clears "new" on the next visit (previous `last_seen_at` advanced).
3. The "show only new" filter works.
4. First-ever visit follows the documented behaviour (banner suppressed, nothing badged).
5. `uv run python3 -m pytest tests/ -v` passes.
6. `uv run python score.py --dry-run` passes.
