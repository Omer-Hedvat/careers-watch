| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `completed` |
| **Effort** | S |
| **Epic** | WEBAPP_JOBSEEKER_WORKFLOW |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/supabase/migrations/013_hidden_jobs.sql` (new), `webapp/backend/routers/jobs.py`, `webapp/backend/routers/scoring.py`, `webapp/backend/routers/user.py`, `webapp/backend/tests/test_hidden_jobs.py` (new), `webapp/frontend/app/(app)/positions/page.tsx`, `webapp/frontend/app/(app)/digest/page.tsx`, `webapp/frontend/app/components/` (Skip button) |
| **Night-ready** | no - needs migration 013 pasted into Supabase by Omer |

## Overview

Irrelevant jobs keep showing on both Positions and the Digest, and there's no
way to say "not interested". Omer asked (2026-10-15) for a **Skip** button on
positions. A skipped job is hidden on both pages, remembered per user, and
never sent to Gemini again, which also saves scoring quota.

## Behaviour

- **One representation for both pages.** Positions is the shared catalog with no
  per-user row, so a column on `scored_jobs` can't cover it. Instead, use a per-user
  overlay keyed by URL: `hidden_jobs(user_id uuid references users(id) on delete cascade,
  apply_url text, hidden_at timestamptz default now(), primary key (user_id, apply_url))`.
  The same key works on Positions (catalog rows) and the Digest (`scored_jobs.apply_url`).
  It needs no new column on `scored_jobs`, so it doesn't conflict with
  WEBAPP_APPLICATION_TRACKER.
- **Endpoints** (`routers/jobs.py`): `POST /jobs/skip` `{apply_url}` (idempotent upsert),
  `DELETE /jobs/skip` `{apply_url}` (unskip). `GET /jobs/` and `GET /jobs/positions`
  mark rows with `skipped: true` (flag, don't drop), the same pattern as `outside_filters`.
  The backend reads the user's `hidden_jobs` set once per call.
- **Scoring** (`routers/scoring.py` `_new_pending`): skipped URLs are excluded, in the
  same place as already-scored URLs.
- **UI:**
  - A **Skip** button on the Positions row or detail panel and on the Digest card or
    detail panel. It is optimistic: the row disappears at once, and on error it
    reappears with a toast.
  - The Digest and Positions hide skipped rows by default and show a
    "N skipped - Show them" line, mirroring the "hidden by your saved filters" line.
    In that view each row offers **Unskip**.
  - Applied jobs can't be skipped: the button isn't shown when `applied` is set.
- **Delete account:** cascades through the FK. **Export data:** includes `hidden_jobs`.
- Hyphens, not em-dashes, in all UI copy.

## Files to Touch

- `webapp/supabase/migrations/013_hidden_jobs.sql` - table above. RLS on, with no policies (only the service role reads it).
- `webapp/backend/routers/jobs.py` - skip and unskip endpoints, plus the `skipped` flag on both list endpoints.
- `webapp/backend/routers/scoring.py` - exclude skipped URLs in `_new_pending`.
- `webapp/backend/routers/user.py` - add `hidden_jobs` to the data export.
- `webapp/backend/tests/test_hidden_jobs.py` - new.
- `webapp/frontend/app/(app)/positions/page.tsx`, `webapp/frontend/app/(app)/digest/page.tsx` - Skip and Unskip actions, the "N skipped" line.
- `webapp/frontend/app/components/` - shared Skip button if both pages use it.

## How to QA

1. Backend tests: skip is idempotent, unskip removes the row, list endpoints set `skipped`, and `_new_pending` excludes skipped URLs.
2. `cd webapp/backend && uv run python -c "import main"`, plus the frontend build with dummy env (exit 0).
3. `uv run python3 -m pytest tests/ -v` and `uv run python score.py --dry-run` pass.
4. Live (after Omer applies 013): Skip a job on Positions. It disappears, stays gone after a reload, and is also hidden on the Digest if it was scored.
5. Live: "N skipped - Show them" lists it, and Unskip brings it back on both pages.
6. Live: a Score now run doesn't score a skipped job, which shows in the run's total.

## Implementation notes

Shipped (2026-10-15, branch `feat/skip-jobs`):

- `webapp/supabase/migrations/013_hidden_jobs.sql` - `hidden_jobs` table, RLS on with no policies, idempotent. **Not applied** - Omer pastes it into Supabase.
- `routers/jobs.py` - `hidden_urls(user_id)` (paginated, returns an empty set if the table is missing or the read fails), `POST /jobs/skip` (upsert on `user_id,apply_url`), `DELETE /jobs/skip`. Both return 400 on an empty `apply_url` and 503 if the write fails (table missing). `GET /jobs/` and `GET /jobs/positions` add `skipped: bool`.
- `routers/scoring.py` - `_new_pending` excludes scored and skipped URLs together.
- `routers/user.py` - `/user/export` is now `{"scored_jobs": [...], "hidden_jobs": [...]}` (it was a bare list of scored jobs). `delete_account` relies on the FK cascade, since it only deletes the `users` row.
- Frontend: `app/components/SkipButton.tsx` (presentational, because JobCard also renders on the public landing page) plus `lib/skip.ts` (`saveSkip`). Skip sits on each Positions row and each Digest card, not in the detail panels. It is hidden for applied jobs. Both pages hide skipped rows behind a "N skipped - Show them" line, and the Digest tier counts and "Showing N of M" use the visible set. Both SWR cache versions were bumped.
- Tests: `webapp/backend/tests/test_hidden_jobs.py`.

Live QA still pending (needs migration 013): How to QA steps 4-6. Before 013, Skip shows the rollback message, because the endpoint returns 503.
