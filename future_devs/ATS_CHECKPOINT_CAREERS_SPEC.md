| Field | Value |
|---|---|
| **Phase** | P9 |
| **Status** | `in-progress` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/checkpoint_careers.py` (new), `ats/__init__.py`, `big_companies.yml` |

## Overview

Build a single-tenant puller for **Check Point Software** (`careers.checkpoint.com`). Check Point is one of Israel's largest and most important cybersecurity companies — hundreds of relevant positions. It is currently in `ats: other` with no puller.

This is a single-tenant integration (no third-party ATS, no `detect.py` rule needed).

## Behaviour

- First step: fingerprint the backend. Run `scripts/fingerprint_ats.py` or manually inspect `careers.checkpoint.com` network calls in DevTools to find the underlying API.
  - Likely candidates: Oracle Taleo (Check Point has historically used it), a proprietary REST API, or a JS-rendered SPA calling an internal endpoint.
- The puller should call the discovered API endpoint directly (avoid Playwright if a REST call works).
- Filter by Israel location (careers.checkpoint.com may serve global jobs).
- No `ats_params` needed — endpoint is hard-coded inside the puller (single tenant).
- Register in `big_companies.yml` under `ats: checkpoint_careers` with `ats_params: {}` and `location_filter: israel`.
- Register in `ATS_PULLERS` as a no-param lambda.

## Files to Touch

- `ats/checkpoint_careers.py` — new single-tenant puller; export `fetch_positions() -> list[dict]`
- `ats/__init__.py` — add `"checkpoint_careers": lambda p: _fetch_checkpoint_careers()`
- `big_companies.yml` — update Check Point entry to `ats: checkpoint_careers`, `ats_params: {}`, `location_filter: israel`

## How to QA

1. `uv run ats/checkpoint_careers.py` returns ≥20 jobs (Check Point always has many open roles).
2. All returned jobs have `title`, `location`, `description`, `apply_url` populated.
3. `uv run python collect_jobs.py` — Check Point jobs appear in `new_jobs.json`.
4. `uv run python -m pytest tests/ -v` passes.
