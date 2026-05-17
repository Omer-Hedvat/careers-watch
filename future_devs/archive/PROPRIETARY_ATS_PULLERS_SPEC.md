| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `completed` |
| **Effort** | L |
| **Epic** | (this is an epic) |
| **Depends on** | — |
| **Blocks** | Activating ~13 inert big_companies.yml stubs |
| **Touches** | (rolls up — see children) |

## Overview

Epic. Stop missing positions from the `ats: other / ats_params: {}` entries in `big_companies.yml`. Each child task implements one ATS family puller and activates the relevant company entries.

## Children

| Slug | Activates | Effort | Notes |
|---|---|---|---|
| [ATS_TALENTBREW](ATS_TALENTBREW_SPEC.md) | Intuit (and extensible) | XS | Endpoint confirmed: 474 Israel results live |
| [ATS_AMAZON_JOBS](ATS_AMAZON_JOBS_SPEC.md) | AWS Israel | S | Public JSON `amazon.jobs/en/search.json` |
| [ATS_MICROSOFT_CAREERS](ATS_MICROSOFT_CAREERS_SPEC.md) | Microsoft Israel | S | Undocumented `gcsservices.careers.microsoft.com` |
| [ATS_GOOGLE_CAREERS](ATS_GOOGLE_CAREERS_SPEC.md) | Google Israel | S | Undocumented `google.com/about/careers/applications/v3/api/jobs` |
| [ATS_EIGHTFOLD](ATS_EIGHTFOLD_SPEC.md) | PayPal Israel | S | `paypal.eightfold.ai/api/apply/v2/jobs` |
| [ATS_JOBVITE](ATS_JOBVITE_SPEC.md) | Varonis | S | `jobs.jobvite.com/<slug>` widget |
| [ATS_SUCCESSFACTORS](ATS_SUCCESSFACTORS_SPEC.md) | CyberArk, SAP Israel | M | SuccessFactors OData / branded HTML |
| [ATS_TEAMME](ATS_TEAMME_SPEC.md) | Claroty, Quantum Machines | M | Reverse-engineer `*.teamme.link` |
| [ATS_BREEZY](ATS_BREEZY_SPEC.md) | Descope | XS | `{slug}.breezy.hr/json` |

## Out of scope (this epic)

- **Meta Israel** — `metacareers.com`; no clean public endpoint. Tracked separately if a path opens up.
- **Phenom (Imperva/Thales)** — session-auth required; not worth the effort right now.

## Common rules for every child

Each puller must:
- Export `fetch_positions(*args) -> list[dict]` returning normalized `{title, location, description, apply_url}` dicts.
- Fail per-company without crashing `collect_jobs.py`.
- Be runnable directly: `uv run ats/<name>.py <params...>`.
- Use `ats/utils.HEADERS` and `strip_html` — do not redefine.
- Register in `ats/__init__.py` `ATS_PULLERS` with the correct call signature.
- Add a URL/HTML signature to `ats/detect.py` so future companies on the same ATS are auto-detected.

## Acceptance

- All 9 children wrapped.
- `collect_jobs.py` produces >0 jobs for at least Intuit, AWS Israel, Microsoft Israel, Google Israel, PayPal Israel, Varonis (the 6 high-confidence ones).
- SuccessFactors + TeamMe at least one of each working (CyberArk + Claroty respectively).
- `score.py --dry-run` accepts the new jobs without error.
