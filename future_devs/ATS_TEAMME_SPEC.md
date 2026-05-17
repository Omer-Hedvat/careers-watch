| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `completed` |
| **Effort** | M |
| **Epic** | PROPRIETARY_ATS_PULLERS |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/teamme.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Build a TeamMe careers puller. Activates **Claroty** and **Quantum Machines** (and any other Israeli company using TeamMe).

## Behaviour

- TeamMe is a small Israeli ATS at `{tenant}.teamme.link`
- No public API documented; reverse-engineer from the careers page (Playwright network intercept)
- Endpoint to discover: `https://{tenant}.teamme.link/api/...` or `https://app.teamme.link/api/...` returning JSON
- Tenants:
  - Claroty: `claroty.teamme.link`
  - Quantum Machines: `qm.teamme.link`
- Detect signature: `teamme.link` URL pattern
- Register in `ATS_PULLERS` and `detect.py`

## How to QA

1. `uv run ats/teamme.py claroty` returns ≥5 jobs with all four normalized keys filled.
2. Same for `qm`.
3. `uv run python collect_jobs.py` includes Claroty + QM jobs in `new_jobs.json`.
4. `uv run python -m pytest tests/ -v` passes.

## Notes

- If reverse-engineering fails (e.g. all data sits in a non-JSON SPA), fall back to a Playwright-based fetch in the puller itself and document this trade-off.
