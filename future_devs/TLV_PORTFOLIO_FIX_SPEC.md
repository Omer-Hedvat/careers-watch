| Field | Value |
|---|---|
| **Phase** | P3 |
| **Status** | `in-progress` |
| **Effort** | M |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `vcs/tlv_partners.py`, `big_companies.yml`, `companies.json` (cleanup pass), possibly `vcs/registry.py` |

## Overview

`vcs/tlv_partners.py` has logo-filename parsing bugs that pollute `companies.json` with garbage entries. **65 TLV Partners entries exist today**, but the live portfolio shows 12 and only 6 actually pull jobs. We need to fix the scraper, dedupe and clean stale entries, add missing live-portfolio companies, and activate the inert ones.

## Concrete bugs

1. `_logo_filename_to_name` does not strip CSS `url(...)`, quotes, or parens before extracting the filename. A `background-image: url("https://.../next.svg")` style produces a final name like `Next.Svg")` after title-casing.
2. Numeric suffix variants (`Granulate` vs `Granulate 1`, `Oligo` vs `Oligo 1`, `Next` vs `Next.Svg")`) come from versioned logo files. Dedupe must be by `website`, not by derived name.
3. Acquired companies (Run AI, Granulate, Puresec, Neosec, Aporia, Rookout, Sealight) still appear because the marketing portfolio page lists them. Consider switching to `jobs.tlv.partners/companies` as the active-hiring source-of-truth.

## Missing live-portfolio companies (need to add)

- **CodiumAI** (a stale `Codium 2` entry exists; replace)
- **REAL**

## Inert TLV-portfolio entries (need ATS params filled)

- Aidoc
- Unframe
- Silverfort
- Remedio
- Unit
- Kipp

## Behaviour

1. Fix `_logo_filename_to_name` to strip leading/trailing `url(...)`, quotes, and parens before filename extraction.
2. Dedupe by `website` in `fetch_portfolio` so versioned/repeat logos collapse to one entry.
3. Strategy decision (pick one and document in this spec):
   - **(a)** Keep marketing-portfolio scraper, post-filter against `jobs.tlv.partners/companies` to keep only actively-hiring entries.
   - **(b)** Switch `fetch_portfolio` to read `jobs.tlv.partners/companies` (Getro-style) as the source-of-truth.
4. Run `refresh_companies.py`; verify no `.Svg`/`.Png`/`Artboard` entries are produced.
5. One-time cleanup of existing `companies.json`: write a short script that drops entries with `source_vc=TLV Partners` AND a name matching `(\.Svg|\.Png|Artboard|^Granulate$|^Next$|^Oligo$|^Codium 2$|^Run Ai$)`.
6. Add CodiumAI and REAL to `big_companies.yml` with verified ATS params (run `ats/detect.py` on each careers URL).
7. For each of the 6 inert companies, run `detect_ats` on its careers URL and fill `ats_params`. If detection fails, add an override entry in `big_companies.yml`.

## Files to Touch

- `vcs/tlv_partners.py` — fix parsing, add dedupe, optionally switch source
- `big_companies.yml` — add CodiumAI + REAL; possibly override inert entries
- `companies.json` — one-time cleanup pass
- (optional) one-off script under repo root or `scripts/` for the cleanup, then deleted after run

## How to QA

1. `uv run vcs/tlv_partners.py` prints clean names: no entries containing `.Svg`, `.Png`, or `Artboard`; no duplicate-website entries.
2. After `uv run python refresh_companies.py`, a script (or one-liner) shows 0 garbage entries with `source_vc=TLV Partners` in `companies.json`.
3. `companies.json` includes entries for CodiumAI and REAL with valid `ats_params`.
4. At least **4 of the 6** previously-inert TLV portfolio companies (Aidoc, Unframe, Silverfort, Remedio, Unit, Kipp) have non-empty `ats_params`.
5. `uv run python collect_jobs.py` runs to completion; the inert companies above contribute >0 jobs to `new_jobs.json`.
6. `uv run python -m pytest tests/ -v` passes.
