| Field | Value |
|---|---|
| **Phase** | P8 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | POSITION_LIVENESS |
| **Depends on** | — |
| **Blocks** | POSITION_LIVENESS_STATUS_DIFF |
| **Touches** | `collect_jobs.py` |
| **Spec files to update** | `CLAUDE.md` architecture section (`collect_jobs.py` cadence note) |

## Overview

**What:** Have `collect_jobs.py` persist, each run, the set of `apply_url`s that are currently live — restricted to companies that pulled **successfully** this run.

**Why:** This is the foundation the rest of the epic diffs against. Without an authoritative "what's open right now" snapshot scoped to successful pulls, the status diff (child 2) cannot tell `closed` apart from `the pull failed`.

## Behaviour

- Track, during the collect loop, the set of companies whose pull **succeeded** (the `try` block completed without exception — note success even when a company returns 0 positions; that is a valid "nothing open here" signal).
- Build `live_apply_urls`: every `apply_url` from positions that survived the existing location filter, across all successful companies.
- Write a new file `live_positions.json` at repo root:
  ```json
  {
    "generated_at": "2026-06-17T07:00:00Z",
    "successful_companies": ["MIND", "Native", ...],
    "live_apply_urls": ["https://www.comeet.com/jobs/...", ...]
  }
  ```
  - `successful_companies` is required by child 2's guard — a job is only a `closed` candidate if its company appears here.
- A company that errored (caught in the `except`) is **excluded** from `successful_companies` and contributes **no** URLs. A company skipped for `acquired` / no-ATS / no-puller is likewise not "successful" (its jobs should not be force-closed by a config skip).
- `new_jobs.json` output is unchanged. This file is additive.
- Keep it minimal — no history, just the latest snapshot (overwrite each run), consistent with the "no caches/indexes/audit logs" scope rule in `CLAUDE.md`.

## Files to Touch

- `collect_jobs.py` — collect successful-company + live-URL sets in the loop; write `live_positions.json` after the loop.

## How to QA

1. Run `uv run python collect_jobs.py`; confirm `live_positions.json` is written with non-empty `live_apply_urls` and `successful_companies`.
2. Every URL in `live_apply_urls` also appears as an `apply_url` in `new_jobs.json` (live set ⊆ collected set).
3. Force a company to raise in its puller; confirm that company is absent from `successful_companies` and contributes no URLs.
4. A company returning 0 positions still appears in `successful_companies`.
