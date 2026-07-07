# WEBAPP_ACCESSIBILITY_PASS

| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/(app)/digest/page.tsx, webapp/frontend/app/(app)/settings/page.tsx, webapp/frontend/app/onboarding/page.tsx, webapp/frontend/app/globals.css, webapp/frontend/app/components/JobCard.tsx |

> **Touches note:** the score badge lives in `app/components/JobCard.tsx` (rendered on the
> digest), so the "convey tier without color" accessible-name fix landed there rather than in
> `digest/page.tsx` directly. Route paths are under the `(app)` group.
>
> **Implementation notes / decisions:**
> - Global `:focus-visible` (amber outline) already existed in `globals.css`; the visual-design
>   v2 pass had also added `focus-visible:ring` to most interactive controls — so focus operability
>   was already broadly covered. No blanket focus rework needed.
> - Score tier without color: `ScoreBadge` already shows the numeral; added `role="img"` +
>   `aria-label="Score N out of 10 - <tier>"` and marked the numeral `aria-hidden` so SR reads one
>   clean name. Grayscale check passes (numeral carries the tier).
> - Icon-only controls: tag-remove `×` in Settings got `aria-label={`Remove ${tag}`}` (onboarding
>   already had it); disclosure toggles got `aria-expanded`. There is no icon-only "settings gear"
>   (Settings is a text nav link); Nav menu toggle, DetailPanel close, and ThemeToggle already had
>   aria-labels.
> - Keyboard: opening a job works via the explicit "Details" button (the card-body div onClick is a
>   mouse convenience with a keyboard equivalent). Filters/wizard are native inputs/buttons.
> - Contrast: `text-muted` already clears AA in both themes; `text-subtle` failed (~3.5:1). Bumped
>   `--color-text-subtle` in both themes to clear AA (>=4.5:1) on surface and surface-raised while
>   staying below muted. Score-band badge backgrounds were left as tuned (Fable single-source
>   tokens): white-on-band clears the 3:1 UI/large threshold, and the numeral+aria-label carry the
>   tier — darkening the emerald high band to chase 4.5:1 would regress `text-score-high` contrast.

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
