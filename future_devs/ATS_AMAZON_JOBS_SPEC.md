| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `completed` |
| **Effort** | S |
| **Epic** | PROPRIETARY_ATS_PULLERS |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/amazon_jobs.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build an Amazon Jobs (amazon.jobs) puller. Activates **AWS Israel** and all Amazon-family Israel openings.

## Behaviour

- Endpoint: `https://www.amazon.jobs/en/search.json?normalized_country_code[]=ISR&result_limit=100&offset=0`
- Public JSON; paginate via `offset` and `result_limit`
- Each hit has `id_icims`, `title`, `posted_date`, `job_path`, `normalized_location`, `description_short`
- Build `apply_url` as `https://www.amazon.jobs{job_path}`
- Detect signature: `amazon.jobs/en/jobs/` in URL/HTML
- Register in `ATS_PULLERS` and `detect.py`
- big_companies.yml: AWS Israel entry to `ats: amazon_jobs`, params=`{country: ISR}`

## How to QA

1. `uv run ats/amazon_jobs.py ISR` returns ≥10 jobs with all four normalized keys filled.
2. `uv run python collect_jobs.py` includes AWS Israel jobs in `new_jobs.json`.
3. `uv run python -m pytest tests/ -v` passes.
