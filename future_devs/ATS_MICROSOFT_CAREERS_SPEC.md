| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `completed` |
| **Effort** | S |
| **Epic** | PROPRIETARY_ATS_PULLERS |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/microsoft_careers.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build a Microsoft Careers puller. Activates **Microsoft Israel** (R&D in Herzliya is the largest non-US Microsoft R&D site).

## Behaviour

- Endpoint: `https://gcsservices.careers.microsoft.com/search/api/v1/search?lc=Israel&pg=1&pgSz=20&o=Relevance`
- Returns JSON with `operationResult.result.jobs[]` array
- Each job has `jobId`, `title`, `properties.locations`, `properties.description`, `postingDate`
- `apply_url` = `https://jobs.careers.microsoft.com/global/en/job/{jobId}`
- Paginate via `pg` until results exhausted; throttle 0.5s between calls
- Detect signature: `jobs.careers.microsoft.com/global/en/job/` URL pattern
- Register in `ATS_PULLERS` and `detect.py`
- big_companies.yml: Microsoft Israel entry to `ats: microsoft_careers`, params=`{location_query: Israel}`

## How to QA

1. `uv run ats/microsoft_careers.py Israel` returns ≥10 jobs with all four normalized keys filled.
2. `uv run python collect_jobs.py` includes Microsoft Israel jobs in `new_jobs.json`.
3. `uv run python -m pytest tests/ -v` passes.
