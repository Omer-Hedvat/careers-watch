# BUG: Viola Getro board sends duplicate jobs across all portfolio companies

## Status
🔵 Open

## Severity
P2

## Description
The Viola VC adapter fetches from `careers.viola-group.com` (Getro board). The Getro board returns 3 generic synthetic job listings ("Principal Data Scientist", "Lead Data Scientist", "Team Lead Data Scientist") for every portfolio company on the board (~60 companies). This produces ~180 near-identical jobs per collection run, all burned through Gemini scoring even though they likely share the same or very similar `apply_url`.

## Steps to Reproduce
1. Run `uv run python collect_jobs.py`
2. Observe output: `Zyg: 20 open positions`, `Tenna: 20 open positions`, etc. — all Viola companies report "20 open positions" from the same Getro board
3. Run `uv run python score.py` — observe 60+ jobs titled "Principal/Lead/Team Lead Data Scientist" across different companies being sent to Gemini

Expected: Each unique job (by `apply_url`) scored once.
Actual: Same job scored under 60 different company names.

## Dependencies
- **Depends on:** —
- **Blocks:** —
- **Touches:** `vcs/viola.py`, and whichever `ats/` module handles Getro (likely `ats/getro.py` or `ats/comeet.py`)
- **Spec files to update:** —

## Fix Notes
<!-- populated after fix -->
Likely fix: deduplicate by `apply_url` after fetching, before adding to `all_jobs`. Or fix the Viola adapter to fetch jobs per-company rather than fetching the full board.
