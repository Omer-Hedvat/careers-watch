| Field | Value |
|---|---|
| **Phase** | P9 |
| **Status** | `completed` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/bamboohr.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build a BambooHR puller. BambooHR is a common ATS for small-to-mid Israeli startups. Companies currently stuck in `ats: other` or `ats: unknown`:

- **Nilus** (`nilus.bamboohr.com`) — `other`
- **Blinkmoon** (`blinkmoongames.bamboohr.com`) — `unknown`
- **Turbine AI** (`turbineai.bamboohr.com`) — `unknown`
- **Skycatch** (`skycatch.bamboohr.com`) — `unknown`
- **Mercuryo** (`mercuryo.bamboohr.com`) — `unknown`

## Behaviour

- Public JSON endpoint (no auth):
  `GET https://{slug}.bamboohr.com/jobs/embed2.php?format=json`
  Returns an array of job objects with `id`, `jobOpeningName` (title), `location`, `jobOpeningStatus`, `applicationUrl`
- Filter to `jobOpeningStatus == "Open"` only
- Normalize location: BambooHR location is a free-text string (e.g. `"Tel Aviv, IL"` or `"Remote, Israel"`). Append country expansion if needed so `location_filter: israel` matches — check if `"IL"` abbreviation would be missed and expand to `"Israel"` if so.
- `ats_params` key: `company_slug` (the subdomain, e.g. `nilus`)
- Detection in `detect.py`: `{slug}.bamboohr.com/careers` URL pattern — extract slug from subdomain
- Add to `ATS_PULLERS`
- Update `big_companies.yml` for Nilus; `detect.py` picks up the others automatically on next `refresh_companies.py` run

## Files to Touch

- `ats/bamboohr.py` — new puller; export `fetch_positions(company_slug) -> list[dict]`
- `ats/__init__.py` — add `"bamboohr": lambda p: _fetch_bamboohr(p["company_slug"])`
- `ats/detect.py` — add detection rule for `*.bamboohr.com/careers` URLs
- `big_companies.yml` — update Nilus entry to `ats: bamboohr`, `ats_params: {company_slug: nilus}`

## How to QA

1. `uv run ats/bamboohr.py nilus` returns ≥1 job with all four normalized keys (`title`, `location`, `description`, `apply_url`).
2. `uv run ats/bamboohr.py blinkmoongames` returns results (or empty list if no openings — confirm the endpoint responds 200).
3. `uv run python collect_jobs.py` — Nilus appears in `new_jobs.json`.
4. `uv run python -m pytest tests/ -v` passes.
