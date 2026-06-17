| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `completed` |
| **Effort** | S |
| **Epic** | WEBAPP_FIRST_RUN_COMPREHENSION |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/landing/page.tsx |

## Overview

The current landing page is a thin hero plus 3 steps plus dead GitHub links (`href="#"`). A first-time job seeker cannot tell whether it is for them, that it is free-but-bring-your-own-key, what the digest looks like, or get answers to the obvious first questions. This task revamps the landing page so a visitor understands the product, its scope, and its output before signing up.

## Behaviour

- Hero keeps the one-line value prop and adds a sub-line clarifying scope: "Tracks 100+ Israeli cyber, fraud and fintech companies and scores every open role against your profile."
- New "Bring your own free AI key" section explaining the model up front: a free Google Gemini key, your data never trains a model, scoring runs on your own quota - so the API-key step in onboarding is not a surprise.
- A visual digest preview: a static example scored job card showing a score badge, company-title, one-line reasoning, flag tags, and Apply / Mark applied controls, so visitors see the output before signing up.
- "Who it's for" line: technical job seekers (data scientists, ML/security engineers) in Israel; note that non-Israel coverage is out of scope today.
- FAQ accordion answering: How often are jobs updated? Which companies? Is it really free? Do you store my CV / API key? Can I use it if I'm not a data scientist? What's the catch?
- Fix the dead GitHub links: point them at the repo with `target="_blank"` and `rel="noopener"`, and correct the author credit. (Note: also filed as standalone BUG_LANDING_DEAD_GITHUB_LINKS so the link fix can ship independently of this revamp.)
- Keep the dark theme (bg-gray-950, green-600 accents) and existing visual language; fully responsive down to mobile width.

## Files to Touch

- webapp/frontend/app/landing/page.tsx

## How to QA

1. Load `/landing`: hero shows the value prop plus the scope sub-line.
2. The "Bring your own free AI key" section is present and explains the free Gemini key + privacy model.
3. A static digest preview card renders with score badge, company-title, reasoning, flag tags, and Apply / Mark applied.
4. "Who it's for" line is present and notes non-Israel coverage is out of scope.
5. FAQ accordion expands/collapses and answers all six listed questions.
6. GitHub links resolve to the repo (no `href="#"`) and open in a new tab with `rel="noopener"`.
7. Layout is usable at mobile width (no overflow/clipping).
8. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
