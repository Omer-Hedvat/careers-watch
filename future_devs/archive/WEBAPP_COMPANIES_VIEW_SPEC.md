| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | [WEBAPP_POSITIONS_VIEW](WEBAPP_POSITIONS_VIEW_SPEC.md) |
| **Touches** | `webapp/frontend/app/companies/page.tsx` (new), `webapp/backend/routers/jobs.py` |

## Overview

Users currently have no way to see which companies are tracked by the pipeline. A dedicated Companies page lists every company in `companies.json`, shows key metadata, and lets users understand what's being monitored on their behalf.

## Behaviour

- New route `/companies`.
- Lists all companies sourced from `companies.json` (served by the backend).
- Per-company card shows: name, category (cyber/fraud/fintech), ATS type, last verified date, consecutive failures (if > 0: shown as a warning badge).
- Companies with `consecutive_failures >= 3` are visually flagged (e.g. amber/red badge).
- Sort: alphabetical by name. No pagination required for the current dataset size.
- Clicking a company card links to its `careers_url` in a new tab.
- Navigation: link added to the main nav alongside Digest.
- No add/remove/edit actions in this task — read-only view only.

## Files to Touch

- `webapp/frontend/app/companies/page.tsx` — new page
- `webapp/backend/routers/jobs.py` — add `GET /api/companies` endpoint returning the companies list
- `webapp/frontend/app/layout.tsx` — add "Companies" nav link

## How to QA

1. Navigate to `/companies` — all tracked companies are listed.
2. A company with `consecutive_failures >= 3` shows a failure badge.
3. Clicking a company card opens the careers URL in a new tab.
4. "Companies" link appears in the main navigation.
5. `uv run python3 -m pytest tests/ -v` passes.
6. `uv run python score.py --dry-run` passes.
