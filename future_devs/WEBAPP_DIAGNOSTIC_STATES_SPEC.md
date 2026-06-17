# WEBAPP_DIAGNOSTIC_STATES

| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | WEBAPP_DIGEST_TRUST |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/digest/page.tsx, webapp/frontend/app/onboarding/page.tsx, webapp/backend/routers/scoring.py |

## Overview

The digest's empty state always says "click Score now" even when the real problem is a missing profile or API key, and triggering a scan gives no progress feedback (a bare "Loading..." and a silent redirect from onboarding). Users cannot tell why the digest is empty or whether a scan is running. This makes empty states diagnostic and adds scoring-in-progress feedback.

## Behaviour

- Diagnostic empty states keyed on account state, derived from `/user/me` plus the job count:
  - No profile -> "Add a profile in Settings to start scoring" (links to Settings).
  - No API key -> "Add your Gemini key" (links to Settings).
  - Profile + key set but nothing scored yet -> "Run your first scan".
  - Scored but everything filtered out -> "No jobs match your filters" with a reset-filters action that clears the min-score slider and text filters.
- Scoring-in-progress feedback: after triggering a run (on the digest, and at the end of onboarding), show a working/progress indicator and, when done, a result count ("Scored N new jobs") instead of a silent redirect. Await or poll completion - if `routers/scoring.py` does not already expose a way to read run status / result count, add one.
- Replace the plain "Loading..." text with job-list loading skeletons.

## Files to Touch

- webapp/frontend/app/digest/page.tsx
- webapp/frontend/app/onboarding/page.tsx
- webapp/backend/routers/scoring.py (status / result-count endpoint, if needed for polling)

## How to QA

1. With no profile, the empty state says "Add a profile in Settings" (not "Score now") and links there; with no key, it prompts for the Gemini key.
2. With profile + key but nothing scored, the empty state says "Run your first scan".
3. Trigger a scan (digest or onboarding): a progress indicator shows, then a result count ("Scored N new jobs") - no silent redirect.
4. With jobs scored but all filtered out, the state says "No jobs match your filters" and offers a reset that restores the full list.
5. The loading state shows skeletons, not bare "Loading...".
6. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
