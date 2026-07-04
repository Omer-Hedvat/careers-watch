| Field | Value |
|---|---|
| **Phase** | P10 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | WEBAPP_VISUAL_DESIGN |
| **Depends on** | — |
| **Blocks** | WEBAPP_DIGEST_VISUAL, WEBAPP_LANDING_VISUAL, WEBAPP_ICONOGRAPHY_MOTION, WEBAPP_ONBOARDING_VISUAL |
| **Touches** | `webapp/frontend/app/globals.css`, `webapp/frontend/tailwind.config.ts`, `webapp/frontend/app/layout.tsx`, `webapp/frontend/lib/` (new `theme`/`tokens` module), `webapp/frontend/app/(app)/digest/page.tsx` (SCORE_BANDS extraction) |

## Overview

Establish the design-system foundation the rest of the epic builds on. Today `globals.css` is just the three `@tailwind` directives, `tailwind.config.ts` is bare default, and colors/spacing/radii are hardcoded Tailwind literals (`bg-gray-950/900/800`, `green-600`, `rounded-xl`) repeated across ~10 files. This task introduces a token layer, a real font, and a single source of truth for the score-band colors.

## Why

Without tokens, every downstream visual task re-invents literals and the app drifts (already happening: `SCORE_BANDS` copy is duplicated between `digest/page.tsx` and `help/page.tsx`). This is the highest-leverage task in the epic — it makes every child cheaper and keeps them consistent.

## Behaviour

- Define semantic CSS variables in `globals.css` for surfaces (page/card/input), borders, text (primary/muted/subtle), and accent + semantic colors (score green/blue/gray, warning amber, danger red). Preserve the current dark palette as the initial values.
- Map those variables into `tailwind.config.ts` under the `theme.extend.colors` so utilities like `bg-surface`, `text-muted`, `border-subtle` work.
- Add a spacing/radius scale and a base font via `next/font` wired in `layout.tsx`. Add base resets, selection color, and scrollbar styling to `globals.css`.
- Extract `SCORE_BANDS` into a shared module (e.g. `lib/scoreBands.ts`) and import it in both `digest/page.tsx` and `help/page.tsx` — remove the duplicated prose definition.
- This task does **not** restyle every page; it lays the layer and does a minimal proof-of-use (nav + one page consume tokens). Full adoption happens in the child tasks.

### Edge cases
- Keep existing class names working during migration where practical; do not break the build.
- No visual regression expected on the proof-of-use page beyond font change.

## Files to Touch
- `webapp/frontend/app/globals.css` — CSS variables, base styles, resets
- `webapp/frontend/tailwind.config.ts` — map tokens into theme
- `webapp/frontend/app/layout.tsx` — `next/font` wiring
- `webapp/frontend/lib/scoreBands.ts` — new shared score-band tokens
- `webapp/frontend/app/(app)/digest/page.tsx` + `app/(app)/help/page.tsx` — import shared SCORE_BANDS

## How to QA
1. `cd webapp/frontend && npm run build` succeeds with no type errors.
2. Grep confirms `SCORE_BANDS` is defined once and imported in both digest and help.
3. Inspect the running app: the chosen font renders, tokens resolve (no `var(--...)` showing literally), dark theme intact.
4. Changing a token value in `globals.css` visibly propagates to the proof-of-use surface.
