| Field | Value |
|---|---|
| **Phase** | P9 |
| **Status** | `in-progress` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/taleo.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build an Oracle Taleo puller. Taleo is a legacy enterprise ATS used by large companies. The primary target is **Radware** (`radware.taleo.net`), an Israeli network security company currently stuck in `ats: other`.

Taleo has no official public API; the approach is to hit the internal JSON search endpoint used by the careers page's frontend.

## Behaviour

- Each Taleo instance lives at `{tenant}.taleo.net`. The tenant for Radware is `radware`.
- The internal REST endpoint for job listings:
  `GET https://{tenant}.taleo.net/careersection/jobsearch/rest/language/en/searchcriteria`
  with a JSON body like `{"multiplecontestapplication":"false","searchByField":{"fieldName":"location","fieldValue":"Israel"}}`
  — inspect Radware's careers page network calls to confirm the exact path and payload.
- Alternative endpoint if the above doesn't work:
  `GET https://{tenant}.taleo.net/careersection/rest/jobboard/requisition?lang=en&portal=101430233&reqId=...`
  — use the list endpoint first, then fetch detail per job.
- Normalize location from Taleo's structured response (city + country fields).
- `ats_params` keys: `tenant` (subdomain) + optionally `location_filter` (for server-side filtering).
- Detection in `detect.py`: `*.taleo.net` URL pattern — extract tenant from subdomain.
- Caution: Taleo sometimes rate-limits or requires a `User-Agent` header. Use `ats/utils.py` HEADERS.

## Files to Touch

- `ats/taleo.py` — new puller; export `fetch_positions(tenant, location_query="Israel") -> list[dict]`
- `ats/__init__.py` — add `"taleo": lambda p: _fetch_taleo(p["tenant"], p.get("location_query", "Israel"))`
- `ats/detect.py` — add detection rule for `*.taleo.net` URLs
- `big_companies.yml` — update Radware entry to `ats: taleo`, `ats_params: {tenant: radware}`, `location_filter: israel`

## How to QA

1. `uv run ats/taleo.py radware` returns ≥5 jobs with all four normalized keys.
2. All jobs have an `apply_url` pointing to `radware.taleo.net/...`.
3. `uv run python collect_jobs.py` — Radware jobs appear in `new_jobs.json`.
4. `uv run python -m pytest tests/ -v` passes.
