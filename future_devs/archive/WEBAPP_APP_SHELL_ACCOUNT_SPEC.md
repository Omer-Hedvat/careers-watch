| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | M |
| **Epic** | WEBAPP_APP_SHELL_ACCOUNT |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/layout.tsx`, `webapp/frontend/app/auth/page.tsx`, `webapp/frontend/app/digest/page.tsx`, `webapp/frontend/app/settings/page.tsx`, `webapp/frontend/middleware.ts` |

## Overview

Each page rolls its own header. There is no persistent navigation, no visible sign-out, no getting-started guidance, no in-app help, and the auth flow lacks password reset, email-confirmation handling, and legal links. As the Companies, Positions, Gaps, and Chat pages land (all planned), the app needs a real shell and account UX. This epic groups that foundation: a shared navigation shell, onboarding guidance, in-app help, and a complete auth flow.

## Behaviour

This is the epic root. It is delivered through four children:

- [WEBAPP_GLOBAL_APP_SHELL_NAV](WEBAPP_GLOBAL_APP_SHELL_NAV_SPEC.md) — shared app shell with persistent nav (Digest, Settings, slots for Companies/Positions) and a visible sign-out. This child unblocks the nav links that the planned [[WEBAPP_COMPANIES_VIEW]] and [[WEBAPP_POSITIONS_VIEW]] pages need.
- [WEBAPP_GETTING_STARTED_CHECKLIST](WEBAPP_GETTING_STARTED_CHECKLIST_SPEC.md) — a dismissible getting-started checklist on the digest (profile, CV, API key, first scan).
- [WEBAPP_IN_APP_HELP_FAQ](WEBAPP_IN_APP_HELP_FAQ_SPEC.md) — an in-app Help/FAQ page reachable from the nav.
- [WEBAPP_AUTH_RESET_CONFIRM_LEGAL](WEBAPP_AUTH_RESET_CONFIRM_LEGAL_SPEC.md) — password reset, email-confirmation handling, password guidance, and Terms/Privacy links.

## Files to Touch

- `webapp/frontend/app/layout.tsx` — coordinate the shared shell (or a new route-group layout)
- `webapp/frontend/app/auth/page.tsx` — auth flow updates
- `webapp/frontend/app/digest/page.tsx` — shell + checklist integration
- `webapp/frontend/app/settings/page.tsx` — shell integration
- `webapp/frontend/middleware.ts` — auth redirect handling

(Each child spec owns the detailed file list. This root tracks the epic.)

## How to QA

1. Each child task's QA passes.
2. An authenticated user can navigate between pages via the shared nav, sign out, and find in-app help.
3. A new user can recover a password via the forgot-password flow.
4. `uv run python3 -m pytest tests/ -v` passes.
5. `uv run python score.py --dry-run` passes.
