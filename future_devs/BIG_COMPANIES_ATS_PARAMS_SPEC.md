| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `not-started` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `big_companies.yml`, `companies.json` |

## Overview

30 entries in `big_companies.yml` have `ats_params: {}` — they are placeholder stubs skipped by `collect_jobs.py`. These are real companies worth monitoring (large Israeli employers in cyber/fintech). This task fills in the ATS params for each stub, verifies the connection, and confirms jobs flow through to `new_jobs.json`.

## Behaviour

For each stub entry:
1. Visit the `careers_url` to confirm it still resolves to an active ATS
2. Identify the ATS type (Greenhouse, Comeet, Lever, Workday, Ashby, SmartRecruiters, other)
3. Extract the required params per ATS:
   - Greenhouse: `board_token` — verify `https://boards.greenhouse.io/<token>` loads jobs
   - Comeet: `company_uid` + `token` — extract from careers page embed script
   - Lever: `company` — from `https://jobs.lever.co/<company>`
   - Workday: varies — document the API endpoint
4. Add `location_filter: israel` where appropriate
5. Re-run `refresh_companies.py` to merge the updated entries into `companies.json`
6. Run `collect_jobs.py` and confirm at least some of the newly activated companies produce jobs

## Process per entry

```bash
# After updating big_companies.yml:
uv run python refresh_companies.py
uv run python collect_jobs.py
# Verify new companies appear in new_jobs.json
```

## How to QA

1. Count entries with `ats_params: {}` before — should be ~30
2. Fill all entries
3. Run `refresh_companies.py` — confirm count in `companies.json` grows
4. Run `collect_jobs.py` — confirm total job count in `new_jobs.json` increases
5. Spot-check 3 companies: open their `apply_url` values — confirm they're real live job postings
