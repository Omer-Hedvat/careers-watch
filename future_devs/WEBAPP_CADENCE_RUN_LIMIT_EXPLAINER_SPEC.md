# WEBAPP_CADENCE_RUN_LIMIT_EXPLAINER

| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | WEBAPP_DIGEST_TRUST |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/digest/page.tsx, webapp/backend/routers/user.py (or jobs.py) |

## Overview

The "Score now" button and its "2 of 2 runs used" state are opaque. A user does not know what scoring actually does, why it is capped, when the cap resets, or when new jobs to score arrive. This adds inline explanations of the action, the weekly run limit and reset timing, and surfaces the data-collection cadence in the header.

## Behaviour

- Add a tooltip/popover on the "Score now" button explaining what it does: scores newly collected jobs against your profile using your Gemini key.
- Explain the weekly limit and reset: 2 runs per week, resets Monday.
- When the limit is exhausted, the disabled button (or adjacent text) explains when it resets - not just "2 of 2 runs used" (e.g. "Run limit reached - resets Monday").
- Surface data cadence in the digest header: "New jobs collected Mon & Thu" and, if available, "Next collection: <when>".
- Backend: `/user/me` already returns `scoring_runs_this_week`. Extend the user (or jobs) router to expose the run-limit reset date and, if known, the next-collection date so the frontend does not hardcode them. If the next-collection date is not derivable, ship the static "Mon & Thu" copy and leave the dynamic field optional.

## Files to Touch

- webapp/frontend/app/digest/page.tsx
- webapp/backend/routers/user.py (extend `/user/me` with reset date / next-collection date) or webapp/backend/routers/jobs.py

## How to QA

1. Hover "Score now": a tooltip/popover explains what it does and the 2-runs-per-week limit.
2. With runs exhausted, the button/adjacent text shows the reset timing (e.g. "resets Monday"), not just "2 of 2 runs used".
3. The header shows the collection cadence ("New jobs collected Mon & Thu"), plus a next-collection date if the backend provides one.
4. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
