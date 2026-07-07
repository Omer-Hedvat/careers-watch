| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `wrapped` |
| **Effort** | XS |
| **Epic** | — |
| **Depends on** | WEBAPP_POSITIONS_VIEW ✅ |
| **Blocks** | — |
| **Touches** | `webapp/backend/routers/jobs.py`, `webapp/frontend/app/(app)/digest/page.tsx` |

## Overview

> **Retargeted (2026-07-07):** WEBAPP_POSITIONS_CATALOG_SYNC changed the Positions
> page to show the shared global `positions` catalog (the full market, a 1:1 mirror
> of `new_jobs.json`) instead of the user's `scored_jobs`. On that page a "suitable
> out of collected" split is now ~N-out-of-N and meaningless. The "how much of the
> raw pool was relevant to me" contrast only makes sense where a user-scoped subset
> is shown — the **Digest**. This spec now adds the count to the Digest toolbar.

The Digest shows the user's scored, surfaced roles. It should also state how much
of the raw collected pool that represents, e.g. "12 suitable roles out of 1,847
collected", so the user understands the surfaced set is a filtered slice of a much
larger market.

- **suitable** = the user's `scored_jobs` rows at or above the digest surface threshold (score ≥ 5, what the digest shows)
- **collected** = total rows in `new_jobs.json` (everything pulled from ATSes before scoring); falls back to the shared `positions` catalog count when the file is unavailable (e.g. on the deployed backend)

## Behaviour

- The Digest toolbar gains a line: `12 suitable roles out of 1,847 collected`
- If `suitable` is 0 (nothing scored yet), the line is omitted (the empty state already explains the next step)
- If `collected` can't be resolved (no `new_jobs.json`, catalog count fails), show just `12 suitable roles` — no "out of N" clause, no error
- If the `stats` endpoint itself fails, the line is omitted entirely — no error shown
- The count is informational only; it does not filter or change the job list

## Files to Touch

1. `webapp/backend/routers/jobs.py` — add `GET /jobs/stats` (declared **before** `/{job_id}` so it isn't captured by the path param) returning `{"suitable": int, "collected": int | null}` where `suitable` is the user's `scored_jobs` count with `score >= 5` and `collected` is `len(new_jobs.json)` (falling back to the `positions` catalog row count, else `null`)
2. `webapp/frontend/app/(app)/digest/page.tsx` — fetch `/jobs/stats` on mount and after scoring; render the count line in the toolbar with the fallbacks above

## How to QA

1. Load the Digest with scored jobs — toolbar shows e.g. "12 suitable roles out of 1,847 collected"
2. A user with nothing scored — the line is absent (empty state guidance shows instead)
3. Simulate `new_jobs.json` missing but catalog populated — "out of N" still resolves from the `positions` count
4. Simulate the `stats` endpoint returning an error — the line is absent, no error surfaced, digest otherwise unchanged
5. `uv run python3 -m pytest tests/ -v` passes
6. `uv run python score.py --dry-run` passes
