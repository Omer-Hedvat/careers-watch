| Field | Value |
|---|---|
| **Phase** | P10 |
| **Status** | `wrapped` |
| **Effort** | M |
| **Epic** | WEBAPP_VISUAL_DESIGN |
| **Depends on** | WEBAPP_DESIGN_TOKENS ✅ |
| **Blocks** | WEBAPP_LANDING_VISUAL |
| **Touches** | `webapp/frontend/app/(app)/digest/page.tsx` |

## Overview

Visual redesign of the digest — the app's main screen. Improve the `JobCard`, `ClosedJobCard`, `JobCardSkeleton`, `ScoreBadge`, and `ScoreLegend` components for polish and scannability, using the design tokens from WEBAPP_DESIGN_TOKENS. Presentation only — no changes to scoring, filters logic, applied/closed behavior, or data.

## Why

The digest is where users spend their time and where match quality is judged. Better visual hierarchy (score prominence, company/title/location, flags) makes the ranked list faster to scan and raises trust.

## Behaviour

- Redesign `JobCard`: clearer hierarchy between score, title, company, location, flags, and apply CTA. Consistent use of token colors and radii.
- Redesign `ScoreBadge` + `ScoreLegend` using the shared `SCORE_BANDS` tokens; keep the 9-10 / 7-8 / 5-6 banding and colors.
- Distinct-but-cohesive treatment for `ClosedJobCard` (de-emphasized, still legible).
- Improve loading state: refine `JobCardSkeleton`; add subtle mount/hover motion on cards.
- Improve the `EmptyState` variants visually (no copy changes — those are owned by P7 specs).

### Edge cases
- Preserve all existing props, flags rendering, and the applied/closed sections.
- Do not alter the min-score slider's behavior; visual styling of the native control is fine.

## Files to Touch
- `webapp/frontend/app/(app)/digest/page.tsx`

## How to QA
1. `cd webapp/frontend && npm run build` succeeds.
2. Digest renders with redesigned cards; scores remain color-banded per SCORE_BANDS.
3. Applied and closed sections still render; closed cards visually de-emphasized.
4. Skeleton shows during load; cards animate in; no console errors.
5. Filters and Score-now still function unchanged.
