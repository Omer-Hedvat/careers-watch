| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `completed` |
| **Effort** | M |
| **Epic** | WEBAPP_FIRST_RUN_COMPREHENSION |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/onboarding/page.tsx, webapp/frontend/app/settings/page.tsx, webapp/backend/routers/jobs.py |

## Overview

The filter step uses jargon ("Title denylist/allowlist") with no examples, and the spec-promised live preview ("X of Y jobs would be scored") was never built. First-timers cannot predict the effect of their filters. This task replaces the jargon with plain-language labels and examples and implements the live preview against the latest collected jobs.

## Behaviour

- Replace jargon with plain-language labels plus helper text and examples:
  - "Skip jobs whose title contains... (e.g. data engineer, analyst)"
  - "Only score jobs whose title contains at least one of... (leave blank to score all titles)"
  - "Skip these companies"
  - "Skip these industries"
  - Add small (?) tooltips for each.
- Implement the live preview: a backend endpoint that, given a set of filters, returns how many of the latest new_jobs.json would pass: "With these filters, X of today's Y collected jobs will be sent for scoring."
- The preview updates as filters change, debounced.
- The same filter component is used in onboarding Step 4 and the Settings Filters tab.
- Edge cases:
  - Empty new_jobs.json -> show "No collected jobs yet" instead of a count.
  - A location-only filter still previews correctly.
- Keep the dark theme; copy uses hyphens, not em-dashes.

## Files to Touch

- webapp/frontend/app/onboarding/page.tsx
- webapp/frontend/app/settings/page.tsx
- webapp/backend/routers/jobs.py (new filter-preview endpoint; or scoring.py if a closer fit)

## How to QA

1. Filter labels show plain language plus examples and (?) tooltips - no "denylist/allowlist" jargon.
2. Editing any filter updates the preview count live (debounced): "With these filters, X of today's Y collected jobs will be sent for scoring."
3. The same filter component renders in onboarding Step 4 and the Settings Filters tab.
4. With an empty new_jobs.json, the preview shows "No collected jobs yet" instead of a count.
5. A location-only filter still produces a preview count.
6. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
