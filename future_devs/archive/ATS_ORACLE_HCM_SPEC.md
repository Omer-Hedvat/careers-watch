| Field | Value |
|---|---|
| **Phase** | P9 |
| **Status** | `wrapped` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/oracle_hcm.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build an Oracle Fusion HCM (Cloud Recruiting) puller. Oracle HCM is the enterprise ATS used by **Dell Technologies Israel** (`iawmqy.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/careers`) and other large corporations. Dell currently sits in `ats: other`.

Oracle HCM exposes a public Candidate Experience REST API that does not require authentication.

## Behaviour

- Oracle HCM Candidate Experience API endpoint:
  `GET https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions?expand=all&finder=findReqs;siteNumber={site_number},locationId=...&limit=100`
  — the `host` (e.g. `iawmqy.fa.ocs.oraclecloud.com`) and `site_number` (found in the careers page URL: `/sites/careers` → site name `careers`) are the key params.
- Alternative: inspect the HCM careers page network calls to find the exact `searchRequisitions` REST path and required query params (they vary slightly by version).
- Filter by Israel: pass a `locationId` or `locationName` query param, or post-filter on the `PrimaryLocation.State` field.
- `ats_params` keys: `host`, `site` (site name slug), optionally `location_filter`.
- Detection in `detect.py`: URL contains `hcmUI/CandidateExperience` — extract `host` from the netloc.
- Normalize `PrimaryLocation` structured object to `"{city}, {country}"`.

## Files to Touch

- `ats/oracle_hcm.py` — new puller; export `fetch_positions(host, site, location_query="Israel") -> list[dict]`
- `ats/__init__.py` — add `"oracle_hcm": lambda p: _fetch_oracle_hcm(p["host"], p["site"], p.get("location_query","Israel"))`
- `ats/detect.py` — add detection rule for URLs containing `/hcmUI/CandidateExperience/`
- `big_companies.yml` — update Dell Technologies Israel entry to `ats: oracle_hcm`, `ats_params: {host: iawmqy.fa.ocs.oraclecloud.com, site: careers}`, `location_filter: israel`

## How to QA

1. `uv run ats/oracle_hcm.py iawmqy.fa.ocs.oraclecloud.com careers` returns ≥5 jobs with all four normalized keys.
2. All jobs have an `apply_url` pointing to the Dell HCM careers portal.
3. `uv run python collect_jobs.py` — Dell Israel jobs appear in `new_jobs.json`.
4. `uv run python -m pytest tests/ -v` passes.
