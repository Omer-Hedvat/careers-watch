| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `completed` |
| **Effort** | S |
| **Epic** | WEBAPP_FIRST_RUN_COMPREHENSION |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/onboarding/page.tsx |

## Overview

The 4-step onboarding wizard (Profile/CV/API-key/Filters) has no "what we're about to do / why / what you'll get" framing, no final review, and skipping profile/CV silently yields an empty digest with no explanation. This task adds orientation, per-step rationale, skip-consequence warnings, and a final setup summary so a new user always knows why each step matters and what happens next.

## Behaviour

- Add a short orientation intro at the top of the wizard summarizing the 4 steps and the end result: "After setup we run your first scan and show you a ranked digest."
- Each step gets a one-line "why this matters" caption:
  - Profile: tells the AI what to look for.
  - CV: ground truth of what you've done.
  - Key: scoring runs on your free quota.
  - Filters: drop noise before scoring.
- Strong, friendly consequence warning when Profile is skipped: "Without a profile we can't score jobs - you'll see an empty digest until you add one in Settings."
- Lighter note for CV when skipped: scoring quality drops without it.
- Final step shows a compact setup summary before the primary CTA: Profile (added/skipped), CV (added/skipped), Key (set), Location filter, and the count of denylist terms.
- Primary CTA on the final step reads "Start my first scan."
- Set the expectation that the first scan runs in the background and the digest may take a moment to populate (ties into WEBAPP_DIAGNOSTIC_STATES).
- Keep the dark theme and existing wizard layout; copy uses hyphens, not em-dashes.

## Files to Touch

- webapp/frontend/app/onboarding/page.tsx

## How to QA

1. The wizard opens with an orientation intro listing the 4 steps and the end result.
2. Each of the 4 steps shows its one-line "why this matters" caption.
3. Skipping Profile shows the strong consequence warning about an empty digest.
4. Skipping CV shows the lighter quality-drop note.
5. The final step shows a setup summary (Profile/CV added-or-skipped, Key set, location filter, N denylist terms) before the "Start my first scan" CTA.
6. Copy mentions that the first scan runs in the background and may take a moment.
7. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
