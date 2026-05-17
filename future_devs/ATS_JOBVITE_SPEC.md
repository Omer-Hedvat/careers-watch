| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | PROPRIETARY_ATS_PULLERS |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/jobvite.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build a Jobvite puller. Activates **Varonis** and any other Jobvite-hosted careers we discover.

## Behaviour

- Endpoint pattern: `https://jobs.jobvite.com/api/v1/jobs/page?company={slug}&page=1`
  - Backup: scrape `https://jobs.jobvite.com/{slug}` page and parse the embedded JSON
- For Varonis: `https://jobs.jobvite.com/varonis` (slug=`varonis`)
- Each job has `id`, `title`, `location`, `description`, `applyUrl`
- Detect signature: `jobs.jobvite.com/{slug}` URL pattern
- Register in `ATS_PULLERS` and `detect.py`
- big_companies.yml: Varonis entry to `ats: jobvite`, params=`{company_slug: varonis}`

## How to QA

1. `uv run ats/jobvite.py varonis` returns ≥5 jobs with all four normalized keys filled.
2. `uv run python collect_jobs.py` includes Varonis jobs in `new_jobs.json`.
3. `uv run python -m pytest tests/ -v` passes.
