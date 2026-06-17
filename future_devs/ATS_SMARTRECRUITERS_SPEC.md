| Field | Value |
|---|---|
| **Phase** | P9 |
| **Status** | `completed` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/smartrecruiters.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml`, `companies.json` |

## Overview

Build a SmartRecruiters puller. SmartRecruiters is already detected by `detect.py` (Palo Alto Networks is correctly tagged `smartrecruiters`) but there is no entry in `ATS_PULLERS`, so every SmartRecruiters company is silently skipped by `collect_jobs.py`. CyberArk is stuck in `ats: other` despite having a plain SmartRecruiters URL — reclassify it as part of this task.

Companies unlocked: **Palo Alto Networks** (`PaloAltoNetworks2`) and **CyberArk** (`Cyberark1`).

## Behaviour

- Public endpoint (no auth required):
  `GET https://api.smartrecruiters.com/v1/companies/{company_slug}/postings?limit=100`
  Returns `{"content": [{...}, ...], "totalFound": N}`
- Each posting has `id`, `name` (title), `location.city`, `location.country`, `ref` (apply URL)
- Normalize location to `"{city}, {country}"` — SmartRecruiters country is a full string (e.g. `"Israel"`), so the `location_filter: israel` substring match works directly
- `ats_params` key: `company_slug` (e.g. `PaloAltoNetworks2`)
- Detection in `detect.py`: `jobs.smartrecruiters.com/{slug}` or `careers.smartrecruiters.com/{slug}` — extract slug from path segment 1
- Add to `ATS_PULLERS` in `ats/__init__.py`
- Reclassify CyberArk in `companies.json`: change `ats` from `other` to `smartrecruiters`, set `ats_params: {company_slug: Cyberark1}`
- big_companies.yml: update CyberArk entry to `ats: smartrecruiters`, `ats_params: {company_slug: Cyberark1}`, `location_filter: israel`

## Files to Touch

- `ats/smartrecruiters.py` — new puller; export `fetch_positions(company_slug) -> list[dict]`
- `ats/__init__.py` — add `"smartrecruiters": lambda p: _fetch_smartrecruiters(p["company_slug"])`
- `ats/detect.py` — extraction logic already detects `smartrecruiters`; verify slug extraction is correct
- `big_companies.yml` — update CyberArk entry
- `companies.json` — patch CyberArk entry in-place (or via a re-run of `refresh_companies.py`)

## How to QA

1. `uv run ats/smartrecruiters.py PaloAltoNetworks2` returns ≥5 jobs with all four normalized keys (`title`, `location`, `description`, `apply_url`).
2. `uv run ats/smartrecruiters.py Cyberark1` returns ≥5 jobs.
3. `uv run python collect_jobs.py` — both PAN and CyberArk appear in `new_jobs.json`.
4. `uv run python -m pytest tests/ -v` passes.
