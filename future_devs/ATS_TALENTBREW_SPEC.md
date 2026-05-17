| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `not-started` |
| **Effort** | XS |
| **Epic** | PROPRIETARY_ATS_PULLERS |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/talentbrew.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build a TalentBrew (Radancy) puller. Activates **Intuit** and is reusable for other large enterprises on the same platform (Boeing, Marriott, Verizon, Disney, etc.).

## Behaviour

- Endpoint: `https://{host}/search-jobs/results?ActiveFacetID=0&CurrentPage=1&RecordsPerPage=100&FacetTerm={facet}&FacetType=2`
- Returns JSON with HTML in the `results` field; parse jobs out of the embedded HTML
- For Intuit: host=`jobs.intuit.com`, facet=`israel`, FacetType=2 (country)
- Page through using `CurrentPage` until `total-pages` reached
- Detect signature: `tbcdn.talentbrew.com/company/{id}` in HTML
- Register in `ATS_PULLERS` dispatch and `detect.py`
- big_companies.yml: change Intuit Israel entry to `ats: talentbrew`, params=`{host: jobs.intuit.com, facet: israel}`

## How to QA

1. `uv run ats/talentbrew.py jobs.intuit.com israel` returns ≥10 jobs with all four normalized keys filled.
2. `uv run python collect_jobs.py` includes Intuit Israel jobs in `new_jobs.json`.
3. `uv run python -m pytest tests/ -v` passes (no regressions).
