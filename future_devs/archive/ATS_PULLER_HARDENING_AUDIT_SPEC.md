| Field | Value |
|---|---|
| **Phase** | P11 |
| **Status** | `wrapped` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `ats/*.py`, `ats/utils.py`, `ats/detect.py`, `ats/__init__.py`, `collect_jobs.py`, `tests/` |
| **Model** | Fable (`claude-fable-5`) |

## Overview

Repo-wide correctness + resilience audit of every ATS puller. Not a single-file
fix — a cross-file sweep hunting the *class* of bug that has already bitten this
project, across all pullers at once, then a hardening pass + regression tests.

**Why Fable:** this is a high-recall, cross-file bug-finding task with
repo-history relevance (why a given puller was written the way it was). That is
Fable's documented strength over a single-file Opus fix. Give it the full set of
pullers up front, run at `high`/`xhigh` effort, and have it self-verify with
`ats/<name>.py <token>` direct runs. Enable server-side `fallbacks` to
`claude-opus-4-8` so a spurious cyber-content refusal doesn't fail the run.

## Behaviour

Audit each puller in `ats/` against this checklist, then fix what's found:

1. **`location_filter` correctness** — the documented gotcha: Comeet/Ashby return
   bare city names, so a naive `israel` substring filter silently drops Israeli
   jobs. Every puller must append the expanded country to the location string.
   Verify each puller does, not just the two called out in CLAUDE.md.
2. **HTML stripping** — all pullers use `ats/utils.py:strip_html`, not a local
   reimplementation; entities and tags handled; UTF-8 safe for Hebrew.
3. **Pagination cutoffs** — pullers that page (Greenhouse, SmartRecruiters, etc.)
   fetch *all* pages, not just page 1. Confirm the loop termination condition.
4. **Per-company failure isolation** — a single company error increments
   `consecutive_failures` and continues; never crashes `collect_jobs.py`.
5. **Normalized output shape** — every `fetch_positions` returns
   `{title, location, description, apply_url}` with no missing/None keys.
6. **`ATS_PULLERS` dispatch** — every puller in `ats/` is wired in
   `ats/__init__.py` with the correct call signature.

## Files to Touch

- `ats/*.py` — per-puller fixes
- `ats/utils.py` — shared helpers if a gap is found
- `ats/detect.py` — detection correctness if a puller is mis-identified
- `ats/__init__.py` — dispatch wiring gaps
- `collect_jobs.py` — failure-isolation path
- `tests/` — add regression tests for each real bug found

## How to QA

1. `uv run python3 -m pytest tests/ -v` passes with new regression tests added.
2. For each puller with a known live company, `uv run ats/<name>.py <token>`
   returns jobs with country-qualified locations (filter would match `israel`).
3. `uv run python collect_jobs.py` completes; a deliberately broken company
   entry increments `consecutive_failures` and does not abort the run.
4. A written findings list: each bug found, the file, and the fix (one line each).

## Findings (audit completed 2026-07-06)

Audited all 24 pullers against the 6-point checklist. Four issues found + fixed; the rest verified clean.

**Bugs fixed:**

1. `ats/successfactors.py` — location was `"Ra'anana, IL, 4366202"` (bare ISO code `IL`, no country name); an `israel` `location_filter` dropped **all 7** live SAP Israel jobs. Fix: run the scraped location through new `qualify_location`, which appends `Israel`. Verified live: 0/7 → 7/7 match.
2. `ats/workday.py` — multi-location postings collapse to `"N Locations"` in the list view, hiding a bundled Israel role from the filter. Fix: when the list text is `"N Locations"`/empty, rebuild location from the detail endpoint's `location` + `additionalLocations` (already fetched for the description).
3. `ats/teamme.py` — `_location_str` returned only one of locality/region/country, so a city-level job would drop the country. Fix: join `City, Country` (expanding an ISO code via `expand_country`) and dedupe. Verified live: claroty stays 5/15.
4. `ats/talentbrew.py` — local `_clean` reimplemented HTML stripping instead of using the shared helper (checklist #2). Fix: use `ats/utils.py:strip_html`.

**New shared helpers** (`ats/utils.py`): `ISO_COUNTRY` map, `expand_country`, `qualify_location` — for the location_filter country-expansion gotcha.

**Verified clean (no change needed):**
- Country expansion already correct: `comeet`, `ashby`, `oracle_hcm`, `taleo` (own ISO maps); `greenhouse`/`lever` return full `"City, Country"` strings (verified live: SentinelOne 24/24 Israel jobs qualified); `smartrecruiters` uses `fullLocation` with full country name (verified live: Sutherland).
- Pagination termination correct in all paging pullers (`smartrecruiters`, `workday`, `workable`, `oracle_hcm`, `amazon_jobs`, `eightfold`, `google_careers`, `microsoft_careers`, `successfactors`, `taleo`, `consider`, `talentbrew`); documented safety caps where present.
- Per-company failure isolation in `collect_jobs.py`: single-company error increments `consecutive_failures` and continues.
- Normalized output shape `{title, location, description, apply_url}` present with no None keys in every puller (`consider`/`getro` add a harmless extra `company` key).
- `ATS_PULLERS` dispatch in `ats/__init__.py` wires all 24 pullers with correct signatures.
- Not verifiable this run (no live jobs / network): `breezy` (descope host SSL-timed out; only 1 company), `smartrecruiters` fallback ISO-code path (unreached — `fullLocation` always present in practice).

Regression tests added in `tests/test_ats_location_hardening.py` (9 tests); existing `test_successfactors_schema` updated for the new qualified location.
