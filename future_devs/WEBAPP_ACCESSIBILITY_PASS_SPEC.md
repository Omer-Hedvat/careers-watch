# WEBAPP_ACCESSIBILITY_PASS

| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/digest/page.tsx, webapp/frontend/app/settings/page.tsx, webapp/frontend/app/onboarding/page.tsx, webapp/frontend/app/globals.css |

## Overview

The webapp encodes the job score's meaning by color alone (green/blue/gray badges), which fails color-blind users; focus states, aria-labels on icon-only controls, and keyboard operability are unaudited; the app is dark-only. This is an accessibility pass over the existing screens.

## Behaviour

- Score badges must convey their tier without relying on color alone: the number is already shown; ensure the tier is also distinguishable non-visually (an accessible label / tooltip text like "9 out of 10 - reach out today") and that badge contrast meets WCAG AA.
- Add visible focus-visible styles for all interactive elements (filters, cards, buttons, tabs, links).
- Add aria-labels / accessible names to icon-only controls: the settings gear, the tag-remove "x" buttons, the copy-prompt button, any collapse toggles.
- Ensure keyboard operability: a keyboard-only user can move through filters, open a job (once a detail view exists), mark applied / change status, and operate the onboarding wizard.
- Audit gray-on-gray body text (e.g. text-gray-400/500 on gray-900/950) against WCAG AA contrast and bump where it fails.

## Files to Touch

- `webapp/frontend/app/digest/page.tsx`
- `webapp/frontend/app/settings/page.tsx`
- `webapp/frontend/app/onboarding/page.tsx`
- `webapp/frontend/app/globals.css`

## How to QA

1. With a keyboard only, you can operate the digest filters, open a job, and mark it applied / change status.
2. Icon-only buttons (gear, tag-remove x, copy) have accessible names (check with a screen reader or the accessibility inspector).
3. The score tier is distinguishable without color (label/tooltip present; passes a grayscale check).
4. Body text meets WCAG AA contrast (spot-check with a contrast tool).
5. `uv run python3 -m pytest tests/ -v` passes.
6. `uv run python score.py --dry-run` passes.
