| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `wrapped` |
| **Effort** | M |
| **Epic** | WEBAPP_APP_SHELL_ACCOUNT |
| **Depends on** | — |
| **Blocks** | [WEBAPP_COMPANIES_VIEW](WEBAPP_COMPANIES_VIEW_SPEC.md), [WEBAPP_POSITIONS_VIEW](WEBAPP_POSITIONS_VIEW_SPEC.md) |
| **Touches** | `webapp/frontend/app/layout.tsx` (or a new `(app)` route-group layout), a new Nav component, `webapp/frontend/app/digest/page.tsx`, `webapp/frontend/app/settings/page.tsx`, `webapp/frontend/middleware.ts` |

## Overview

There is no shared layout or persistent nav, and no visible sign-out anywhere in the app - both foundational gaps as more pages are added. Each page currently rolls its own header. This task introduces a shared app shell so every authenticated page renders a consistent header with navigation and account controls.

## Behaviour

- A shared app shell (header + nav) rendered on authenticated pages: links to Digest, Settings, plus slots for Companies / Positions (and future pages) shown as they exist.
- The shell shows a visible "Sign out" control and "signed in as <email>".
- Consistent header across digest, settings, and the new pages; mobile-responsive (collapsible nav / hamburger menu).
- Sign out calls `supabase.auth.signOut()` and returns the user to `/landing`.
- Redirect to `/auth` when unauthenticated, via `middleware.ts` or a per-page guard - replacing the current ad-hoc handling.
- Keep the dark theme and green accent.

## Files to Touch

- `webapp/frontend/app/layout.tsx` — wire the shared shell, or introduce a new `(app)` route-group layout that wraps authenticated pages
- a new Nav component (e.g. `webapp/frontend/app/components/Nav.tsx`) — header, nav links, sign-out, signed-in email, mobile collapse
- `webapp/frontend/app/digest/page.tsx` — adopt the shell, drop the page-local header
- `webapp/frontend/app/settings/page.tsx` — adopt the shell, drop the page-local header
- `webapp/frontend/middleware.ts` — redirect unauthenticated users to `/auth`

## How to QA

1. The nav shell shows on both the digest and settings pages.
2. Sign out works and returns the user to `/landing`.
3. The signed-in email is displayed in the header.
4. The nav collapses to a hamburger/menu on a mobile viewport.
5. Visiting an authenticated page while logged out redirects to `/auth`.
6. The dark theme and green accent are preserved.
7. `uv run python3 -m pytest tests/ -v` passes.
8. `uv run python score.py --dry-run` passes.
