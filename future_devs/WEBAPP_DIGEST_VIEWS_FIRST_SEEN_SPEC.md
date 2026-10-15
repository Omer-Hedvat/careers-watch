| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `completed` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | WEBAPP_HIDE_DISMISS_JOBS ✅ |
| **Blocks** | — |
| **Touches** | webapp/backend/routers/jobs.py, webapp/backend/tests/test_filters.py, webapp/frontend/app/components/JobCard.tsx, webapp/frontend/app/(app)/digest/page.tsx, webapp/frontend/app/(app)/positions/page.tsx, webapp/frontend/app/(app)/help/page.tsx |

## Overview
Omer asked for (1) a "first spotted" date on every position and (2) Applied and Skipped as
links at the top of the Digest instead of toggles at the bottom of the list.

## Behaviour
- Digest cards show "first seen <date>" (scored_jobs.first_seen) before "scored N ago";
  Positions rows show it after the location (positions.first_seen, now returned by
  /jobs/positions; positions cache version bumped to 3). Missing dates are omitted.
- Digest has three views at the top: Matches (the ranked list, as before), Applied (N) and
  Skipped (N). Applied/Skipped list every such job regardless of score, filters or open/closed,
  so nothing marked can go missing. Matches excludes both; the old "Show N applied" and
  "N skipped - Show them" toggles are gone.
- GET /jobs/ pages past PostgREST's 1000-row cap (was silently truncated - "of 1,000").

## How to QA
1. Digest cards and Positions rows show "first seen <date>".
2. Digest top shows Matches / Applied (N) / Skipped (N); each view lists the right jobs and
   "Undo applied" / un-skip moves a job back to Matches.
3. "Showing X of Y" shows the real total (above 1,000 for Omer).
