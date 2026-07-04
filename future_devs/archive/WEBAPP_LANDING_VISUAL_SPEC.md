| Field | Value |
|---|---|
| **Phase** | P10 |
| **Status** | `wrapped` |
| **Effort** | M |
| **Epic** | WEBAPP_VISUAL_DESIGN |
| **Depends on** | WEBAPP_DESIGN_TOKENS ✅, WEBAPP_DIGEST_VISUAL ✅ |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/landing/page.tsx`, `webapp/frontend/app/(app)/digest/page.tsx` (export JobCard for reuse) |

## Overview

Visual glow-up of the landing page: hero, how-it-works, the digest-preview card, who-it's-for, and FAQ. Make it read as a polished product landing using the design tokens. Presentation only — copy and value-prop content are owned by the wrapped P7 `WEBAPP_LANDING_REVAMP`; this task does not rewrite messaging.

## Why

The landing page is the first impression for both prospective users and portfolio viewers. It currently uses the same unstyled ad-hoc Tailwind as the rest of the app and a hardcoded static mock digest card that can drift from the real one.

## Behaviour

- Elevate hero, section rhythm, spacing, and visual hierarchy with tokens.
- Replace the hardcoded static "digest preview" mock (currently `landing/page.tsx` ~lines 155-200 duplicating card markup) with the **real** `JobCard` component fed sample data, so the two cannot drift. Export/reuse `JobCard` from the digest module (extract to a shared component if cleaner).
- Polish the FAQ accordion with smooth expand animation.
- Add subtle section-level motion where it improves polish (no gratuitous animation).

### Edge cases
- Keep all existing links/CTAs and routing intact.
- Do not change landing copy or FAQ text.
- Reusing `JobCard` must not pull auth/data-only logic into the public landing route — pass static sample props.

## Files to Touch
- `webapp/frontend/app/landing/page.tsx`
- `webapp/frontend/app/(app)/digest/page.tsx` (or a new `app/components/JobCard.tsx`) — make `JobCard` reusable

## How to QA
1. `cd webapp/frontend && npm run build` succeeds.
2. Landing renders polished; preview card is the real `JobCard`, not a separate mock.
3. All CTAs/links still navigate correctly; FAQ expands smoothly.
4. Editing a `JobCard` style visibly updates both the digest and the landing preview.
