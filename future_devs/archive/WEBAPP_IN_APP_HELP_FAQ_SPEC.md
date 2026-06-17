| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | WEBAPP_APP_SHELL_ACCOUNT |
| **Depends on** | [WEBAPP_GLOBAL_APP_SHELL_NAV](WEBAPP_GLOBAL_APP_SHELL_NAV_SPEC.md) |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/help/page.tsx` (new), the nav in the app shell |

## Overview

The how-it-works, privacy, and FAQ content lives only on the public landing page. Signed-in users have no in-app help to explain scores, flags, cadence, or how their data is handled. This task adds an in-app help page reachable from the nav.

## Behaviour

- A `/help` (or `/faq`) page reachable from the nav, covering:
  - How scoring works
  - What the scores and flags mean
  - The run limit and collection cadence
  - Data and privacy: how the CV and API key are handled
  - How to improve results (a sharper profile)
- Reuse copy from the landing FAQ and the digest-trust explainers (score legend, flag glossary, cadence).
- A persistent "Help" link in the app shell.
- Empty states and the score legend can deep-link into this page.

## Files to Touch

- `webapp/frontend/app/help/page.tsx` — new help/FAQ page with anchored sections
- the nav in the app shell (the Nav component from [WEBAPP_GLOBAL_APP_SHELL_NAV](WEBAPP_GLOBAL_APP_SHELL_NAV_SPEC.md)) — add a persistent "Help" link

## How to QA

1. `/help` renders the FAQ and how-it-works content.
2. It is reachable from the nav.
3. A deep-link anchor (e.g. `#scoring`) scrolls to the right section.
4. `uv run python3 -m pytest tests/ -v` passes.
5. `uv run python score.py --dry-run` passes.
