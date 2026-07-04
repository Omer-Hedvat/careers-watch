| Field | Value |
|---|---|
| **Phase** | P10 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | WEBAPP_VISUAL_DESIGN |
| **Depends on** | WEBAPP_DESIGN_TOKENS ✅ |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/components/Nav.tsx`, `webapp/frontend/app/components/GettingStartedChecklist.tsx`, `webapp/frontend/app/(app)/positions/page.tsx`, `webapp/frontend/app/(app)/companies/page.tsx`, `webapp/frontend/app/(app)/gaps/page.tsx`, `webapp/frontend/app/auth/page.tsx` |

## Overview

Unify iconography and add consistent micro-interactions across the app. Today icons are a mix of hand-rolled inline SVGs (`Nav.tsx`, checklist), text glyphs (`▸ ▾ ▲ ▼ ← → ✓ ✗ ~ ×`), and an emoji (📬 in `auth/page.tsx`). `lucide-react` is already a dependency but has zero usages. Loading states are inconsistent (digest has skeletons; positions/companies/gaps show a bare "Loading..." text line).

## Why

Consistent icons and motion are the cheapest, most visible signal of polish. Standardizing on one icon set removes the ad-hoc glyph/emoji mix and makes future UI uniform.

## Behaviour

- Replace inline SVGs, text glyphs, and the 📬 emoji with `lucide-react` icons of consistent size/stroke, colored via tokens.
- Add smooth expand/collapse animation to accordions and expandable rows (gaps, FAQ-style toggles) and to popovers/tooltips.
- Standardize loading states: give positions/companies/gaps skeletons consistent with the digest instead of a plain text line.
- Add consistent hover/focus transitions using token colors.

### Edge cases
- Keep accessible labels: icon-only controls need `aria-label`.
- Do not change nav destinations or behavior — swap glyphs for icons only.
- Do not introduce animation that harms `prefers-reduced-motion` users; respect the media query.

## Files to Touch
- `webapp/frontend/app/components/Nav.tsx`
- `webapp/frontend/app/components/GettingStartedChecklist.tsx`
- `webapp/frontend/app/(app)/positions/page.tsx`
- `webapp/frontend/app/(app)/companies/page.tsx`
- `webapp/frontend/app/(app)/gaps/page.tsx`
- `webapp/frontend/app/auth/page.tsx`

## How to QA
1. `cd webapp/frontend && npm run build` succeeds.
2. Grep finds no remaining text-glyph icons (`▸ ▾ ▲ ▼`) or the 📬 emoji in the touched files; `lucide-react` is imported.
3. Positions/companies/gaps show skeleton loaders; accordions animate.
4. Icon-only controls have `aria-label`; `prefers-reduced-motion` disables non-essential motion.
