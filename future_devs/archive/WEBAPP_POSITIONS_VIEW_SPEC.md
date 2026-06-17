| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `completed` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | [WEBAPP_COMPANIES_VIEW](WEBAPP_COMPANIES_VIEW_SPEC.md) |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/positions/page.tsx` (new), `webapp/backend/routers/jobs.py` |

## Overview

The digest page shows scored jobs grouped by tier, but there is no way to browse raw open positions across all tracked companies. A Positions page exposes the full `new_jobs.json` dataset — every open role currently pulled from the pipeline — without requiring a score.

## Behaviour

- New route `/positions`.
- Lists all jobs from the latest `new_jobs.json` (served by the backend).
- Per-job row shows: company name, job title, location, apply link (opens in new tab).
- Default sort: by company name, then title.
- Search: a text input that filters rows by company name or job title (client-side, no server round-trip).
- No score data shown on this page — that stays on Digest.
- Navigation: link added to the main nav alongside Digest and Companies.
- Pagination or virtual scroll if job count exceeds 200 rows — otherwise a flat list.

## Files to Touch

- `webapp/frontend/app/positions/page.tsx` — new page
- `webapp/backend/routers/jobs.py` — add `GET /api/positions` endpoint returning the flat job list
- `webapp/frontend/app/layout.tsx` — add "Positions" nav link

## How to QA

1. Navigate to `/positions` — all jobs from the latest pipeline run are listed.
2. Typing in the search box filters the list by company or title in real time.
3. Clicking an apply link opens the job URL in a new tab.
4. "Positions" appears in main navigation.
5. If `new_jobs.json` is empty, the page shows a "no positions found" empty state (not a crash).
6. `uv run python3 -m pytest tests/ -v` passes.
7. `uv run python score.py --dry-run` passes.
