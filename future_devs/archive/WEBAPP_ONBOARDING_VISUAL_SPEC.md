| Field | Value |
|---|---|
| **Phase** | P10 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | WEBAPP_VISUAL_DESIGN |
| **Depends on** | WEBAPP_DESIGN_TOKENS ✅ |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/onboarding/page.tsx` |

## Overview

Visual polish of the 4-step onboarding wizard (Profile → CV → API key → Filters). Improve step progress indicator, step transitions, and the styling of form controls (`TagInput` chips, file input, text areas, the setup-summary panel). Presentation only — the onboarding copy, orientation text, and flow logic are owned by the wrapped P7 onboarding specs and must not change.

## Why

Onboarding is a high-stakes first impression: it is the user's first real interaction after signup. Native unstyled file inputs and abrupt step changes undercut the polish established elsewhere in the epic.

## Behaviour

- Polish the step progress dots/indicator using tokens.
- Add smooth transitions between steps.
- Style the form controls: `TagInput` chips, the `<input type="file">` (currently partial `file:` styling only), textareas, and the setup-summary panel.
- Keep the wizard's existing validation, step-gating, and the first-scan-then-redirect behavior exactly as-is.

### Edge cases
- Do not change any onboarding copy or the orientation/why-this-matters content (P7-owned).
- Do not alter which fields are required or the redirect target.
- Respect `prefers-reduced-motion` for step transitions.

## Files to Touch
- `webapp/frontend/app/onboarding/page.tsx`

## How to QA
1. `cd webapp/frontend && npm run build` succeeds.
2. Walk all 4 steps: progress indicator, transitions, and styled controls render polished; file input is no longer default-browser.
3. Validation/step-gating unchanged; completing the wizard still triggers the first scan and redirects to digest.
4. Copy is unchanged from the current onboarding text.
