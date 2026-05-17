| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | PROPRIETARY_ATS_PULLERS |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/eightfold.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build an Eightfold AI careers puller. Activates **PayPal Israel** and any other Eightfold-hosted careers site we discover.

## Behaviour

- Endpoint pattern: `https://{tenant}.eightfold.ai/api/apply/v2/jobs?location=Israel&start=0&num=100&domain={tenant}`
- For PayPal: `https://paypal.eightfold.ai/...`
- Returns JSON `positions[]`; each has `id`, `name`, `location`, `description`, `canonical_url`
- Paginate via `start`/`num`
- Detect signature: `{subdomain}.eightfold.ai` URL pattern
- Register in `ATS_PULLERS` and `detect.py`
- big_companies.yml: PayPal Israel entry to `ats: eightfold`, params=`{tenant: paypal, location_query: Israel}`

## How to QA

1. `uv run ats/eightfold.py paypal Israel` returns ≥5 jobs with all four normalized keys filled.
2. `uv run python collect_jobs.py` includes PayPal Israel jobs in `new_jobs.json`.
3. `uv run python -m pytest tests/ -v` passes.
