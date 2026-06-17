| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `completed` |
| **Effort** | L |
| **Epic** | WEBAPP_FIRST_RUN_COMPREHENSION |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/landing/page.tsx, webapp/frontend/app/onboarding/page.tsx, webapp/frontend/app/settings/page.tsx, webapp/backend/routers/ |

## Overview

A first-time visitor must understand - before and during onboarding - what CareerWatch is, that it tracks a fixed universe of 100+ Israeli cyber/fraud/fintech companies (not a global job board), why it needs a free Gemini API key, what a profile is and what "good" looks like, what the filters do, and what they will get at the end.

Today onboarding drops users into a 4-step wizard (Profile/CV/API-key/Filters) with no orientation, jargon-heavy filter labels, no example profile, no inline key validation, and silent consequences for skipping profile/CV. A new user cannot tell whether the product is for them, why each step matters, or what the digest will look like.

This epic groups the first-run comprehension work into five focused children so each can ship independently while moving toward one outcome: a brand-new user completes onboarding understanding why every step matters and what they will get.

## Behaviour

Children of this epic (recommended build order):

- **WEBAPP_LANDING_REVAMP** (S) - landing page gains scope sub-line, bring-your-own-free-key section, a visual digest preview, "who it's for", and an FAQ; fixes dead GitHub links. Independent, ship early.
- **WEBAPP_ONBOARDING_KEY_TEST** (XS) - adds a "Test key" action to onboarding Step 3 reusing the existing test-key endpoint. Cheap quick win; build early (this is "A5").
- **WEBAPP_ONBOARDING_ORIENTATION** (S) - adds wizard intro, per-step "why this matters" captions, skip-consequence warnings, and a final setup summary before "Start my first scan". Cheap quick win; build early (this is "A2").
- **WEBAPP_PROFILE_EXAMPLE_GUIDANCE** (S) - adds a collapsible example profile + section guidance + a client-side completeness hint in onboarding Step 1 and the Settings Profile tab.
- **WEBAPP_FILTER_PLAIN_LANGUAGE_PREVIEW** (M) - replaces filter jargon with plain language + examples and implements the live "X of Y jobs would be scored" preview. Needs a new backend preview endpoint, so it lands after the cheap wins (this is "A4").

Build order rationale: the two quick wins (key-test, orientation) ship first for immediate value; the example-guidance and landing work are self-contained; the filter preview is last because it requires backend support.

## Files to Touch

- webapp/frontend/app/landing/page.tsx (via WEBAPP_LANDING_REVAMP)
- webapp/frontend/app/onboarding/page.tsx (via all wizard children)
- webapp/frontend/app/settings/page.tsx (via profile-example + filter-preview children)
- webapp/backend/routers/ (new filter-preview endpoint; optional test-key body tweak)

## How to QA

1. Each child task's own QA passes (see the per-child specs).
2. A brand-new user can complete onboarding end to end and articulate, for each step, why it matters and what they will get.
3. The landing page communicates scope (100+ Israeli cyber/fraud/fintech companies), the bring-your-own-free-key model, and shows a digest preview before sign-up.
4. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
