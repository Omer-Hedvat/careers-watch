| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | PROPRIETARY_ATS_PULLERS |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/google_careers.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build a Google Careers puller. Activates **Google Israel** (Tel Aviv R&D).

## Behaviour

- Endpoint (undocumented but stable): `https://www.google.com/about/careers/applications/v3/api/jobs?location=Israel&page_size=100`
  - Fallback: `careers.google.com/api/v3/search/jobs?location=Israel`
- Returns JSON with `jobs[]` array; each has `title`, `locations`, `description`, `job_title_slug`, `job_id`
- `apply_url` = `https://www.google.com/about/careers/applications/jobs/results/{job_id}`
- Paginate via cursor/next_page_token
- Detect signature: `google.com/about/careers/applications/jobs/` URL pattern
- Register in `ATS_PULLERS` and `detect.py`
- big_companies.yml: Google Israel entry to `ats: google_careers`, params=`{location_query: Israel}`

## How to QA

1. `uv run ats/google_careers.py Israel` returns ≥10 jobs with all four normalized keys filled.
2. `uv run python collect_jobs.py` includes Google Israel jobs in `new_jobs.json`.
3. `uv run python -m pytest tests/ -v` passes.
