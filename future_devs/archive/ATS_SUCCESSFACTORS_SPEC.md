| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `completed` |
| **Effort** | M |
| **Epic** | PROPRIETARY_ATS_PULLERS |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/successfactors.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build a SAP SuccessFactors careers puller. Activates **CyberArk** and **SAP Israel**.

## Behaviour

- Two surface patterns:
  - Direct: `https://{tenant}.successfactors.com/career?searchCountry=Israel&...` (with embedded JSON)
  - Branded: `https://www.cyberark.com/careers/all-job-openings/?searchCountry=Israel` (proxies the same)
- Try OData public endpoint first: `https://{tenant}.successfactors.com/api/.../JobRequisition?$filter=country eq 'IL'&$format=json` (auth may be optional for some tenants)
- Fallback: parse the public careers search HTML, extract `data-jobid`/`data-locale` blocks
- For CyberArk: tenant=`cyberark` (verify), branded URL `https://www.cyberark.com/careers/all-job-openings/`
- For SAP: tenant=`sap`, public URL `https://jobs.sap.com`
- Detect signature: `successfactors.com` URL or `data-jobid="\d+"` on careers page
- Register in `ATS_PULLERS` and `detect.py`

## How to QA

1. `uv run ats/successfactors.py cyberark` returns ≥5 jobs with all four normalized keys filled (Israel openings).
2. Same for SAP.
3. `uv run python collect_jobs.py` includes CyberArk + SAP Israel jobs in `new_jobs.json`.
4. `uv run python -m pytest tests/ -v` passes.
