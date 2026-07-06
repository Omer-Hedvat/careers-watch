| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `in-progress` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | WEBAPP_POSITIONS_VIEW ✅ |
| **Blocks** | — |
| **Touches** | `scripts/sync_positions.py`, `.github/workflows/collect-and-score.yml`, `webapp/supabase/migrations/005_positions_catalog.sql`, `webapp/backend/routers/jobs.py` |
| **Model** | — |

## Overview

The Positions page was reading the per-user `scored_jobs` table (`.eq("user_id", user_id)`),
so it showed each user only their own scored roles — and a brand-new user with no
CV/profile saw whatever leftover/seeded rows happened to exist under their id, not the
market. This closes that gap: a shared, global `positions` catalog synced automatically
from the pipeline, shown to every signed-in user regardless of profile/scoring state.

**Root cause of "I only see my positions":** the deployed `list_positions` scoped by
`user_id` against `scored_jobs`. The shared-catalog behaviour existed only as uncommitted
working-tree changes, so it was never deployed.

## Behaviour

1. New Supabase table `positions` (migration `005`): one global copy of every open role,
   keyed by `apply_url`, with `company/title/location/first_seen/synced_at`.
2. `scripts/sync_positions.py`: upserts the current `new_jobs.json` snapshot into `positions`
   and prunes rows with an older `synced_at` (dropped from the live set). No-ops cleanly when
   `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` are absent, so collect/score stay independently
   runnable. Uses `httpx` (already a pipeline dep) — no new packages.
3. `collect-and-score.yml`: runs `sync_positions.py` after `collect_jobs.py`, before `score.py`.
4. `list_positions` reads the shared `positions` table, ordered by company/title, unscored
   (`score: None`) — ranking stays on the per-user Digest.

## Remaining to land / deploy (manual, external)

- [ ] Commit + push the four touched files. *(done in this task's commit)*
- [ ] Apply migration `webapp/supabase/migrations/005_positions_catalog.sql` to the live Supabase project.
- [ ] Set GitHub Actions secrets `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (service-role key).
- [ ] Run the `Collect and Score` workflow once (or `sync_positions.py` locally) to populate the table.
- [ ] Confirm Render redeploys the backend on push and `/jobs/positions` returns the shared set.

## How to QA

1. `uv run python scripts/sync_positions.py` with SUPABASE creds set → table mirrors `new_jobs.json`;
   without creds → clean skip, exit 0.
2. Signed-in user with **no** CV/profile hits Positions → sees the full market, not an empty/personal list.
3. Two different users see the **same** Positions set.
4. Digest still shows per-user scored roles (unchanged).
