| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `not-started` |
| **Effort** | XS |
| **Epic** | PROPRIETARY_ATS_PULLERS |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/breezy.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build a Breezy HR careers puller. Activates **Descope** and any other Breezy-hosted careers we discover.

## Behaviour

- Public endpoint: `https://{slug}.breezy.hr/json` returns full job list as JSON
- For Descope: slug=`descope`
- Each job has `_id`, `name`, `state`, `creation_date`, `location`, `description`, `url`
- Detect signature: `{slug}.breezy.hr` URL pattern
- Register in `ATS_PULLERS` and `detect.py`
- big_companies.yml: Descope entry to `ats: breezy`, params=`{company_slug: descope}`

## How to QA

1. `uv run ats/breezy.py descope` returns ≥3 jobs with all four normalized keys filled.
2. `uv run python collect_jobs.py` includes Descope jobs in `new_jobs.json`.
3. `uv run python -m pytest tests/ -v` passes.
