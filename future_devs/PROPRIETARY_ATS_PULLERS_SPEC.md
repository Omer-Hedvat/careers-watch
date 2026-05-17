| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `not-started` |
| **Effort** | L |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | Activating ~13 inert big_companies.yml entries |
| **Touches** | `ats/successfactors.py` (new), `ats/teamme.py` (new), `ats/breezy.py` (new), `ats/jobvite.py` (new), `ats/eightfold.py` (new), `ats/__init__.py`, `ats/detect.py`, `big_companies.yml` |

## Overview

Stop missing positions from the `ats: other / ats_params: {}` entries in `big_companies.yml`. These companies appear in `companies.json` as placeholders today and contribute **zero jobs** to `new_jobs.json` because no puller exists for their ATS.

Companies blocked on this:

| ATS family | Companies |
|---|---|
| SuccessFactors | CyberArk, SAP Israel |
| TeamMe | Claroty, Quantum Machines |
| Breezy HR | Descope |
| Jobvite | Varonis |
| Eightfold | PayPal Israel |
| PhenomPeople | Imperva (Thales) |
| Proprietary | Intuit, Microsoft, Google, AWS, Meta |

## Behaviour

Build pullers in priority order. Each is independent and ships separately.

1. **SuccessFactors** (CyberArk + SAP) — largest pools, highest signal.
2. **TeamMe** (Claroty + Quantum Machines) — cyber/quantum signal.
3. **Breezy HR** (Descope) — small but easy; Breezy has a public job board.
4. **Jobvite** (Varonis).
5. **Eightfold** (PayPal Israel).
6. **Proprietary big-tech** (Microsoft/Google/AWS/Meta/Intuit) — only if a clean public REST or JSON endpoint exists. Skip otherwise; document the gap.

Each puller must:

- Export `fetch_positions(*args) -> list[dict]` returning normalized `{title, location, description, apply_url}` dicts.
- Fail per-company without crashing `collect_jobs.py` (caught at orchestrator level).
- Be runnable directly: `uv run ats/<name>.py <params...>` for debugging.
- Use `ats/utils.HEADERS` and `strip_html` — do not redefine.

Each puller must also be registered in `ats/__init__.py` `ATS_PULLERS` with the correct call signature, and `ats/detect.py` must identify it from URL pattern or HTML signature so `refresh_companies.py` can auto-discover future companies on the same ATS.

After each puller lands, fill in `ats_params` for the relevant `big_companies.yml` entries and verify jobs flow end-to-end via `collect_jobs.py`.

## Files to Touch

- `ats/successfactors.py` — new
- `ats/teamme.py` — new
- `ats/breezy.py` — new
- `ats/jobvite.py` — new
- `ats/eightfold.py` — new
- `ats/__init__.py` — register new pullers in `ATS_PULLERS`
- `ats/detect.py` — add URL/HTML signatures for each new ATS
- `big_companies.yml` — fill `ats` + `ats_params` for blocked companies

## How to QA

1. For each new ATS module, `uv run ats/<name>.py <test-params>` returns ≥1 normalized job dict with all four keys non-empty.
2. `uv run python collect_jobs.py` runs to completion. At least 3 of the blocked companies now contribute >0 jobs to `new_jobs.json` (filtered by location).
3. `uv run python score.py --dry-run` accepts the new jobs without error.
4. `uv run python -m pytest tests/ -v` passes.
5. `refresh_companies.py` correctly identifies the ATS on a fresh URL test (via `ats/detect.py`).

## Acceptance Bar

At least **3 of the 5 ATSes** above are shipped and at least **5 of the 13 blocked companies** contribute jobs end-to-end. Proprietary big-tech (Microsoft/Google/AWS/Meta) is allowed to remain unscraped if no clean endpoint is found — but document the discovery in this spec.
