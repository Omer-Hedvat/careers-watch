| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `in-progress` |
| **Effort** | M |
| **Epic** | WEBAPP_APP_SHELL_ACCOUNT |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/auth/page.tsx`, new reset-password + (stub) legal pages, `webapp/frontend/app/auth/callback/route.ts` (if needed) |

## Overview

Auth lacks a forgot-password flow, handles email-confirmation poorly (it routes to `/onboarding` even when no session exists yet, so onboarding's API calls fail), and has no terms/privacy links or password guidance - all of which a product storing CVs and API keys needs. This task completes the auth flow.

## Behaviour

- "Forgot password?" -> Supabase reset-password email flow, plus a reset page that sets the new password.
- Email-confirmation handling: if `supabase.auth.signUp` returns no active session (confirmation required), show a "Check your email to confirm your account" state instead of routing into onboarding; once confirmed, route to `/onboarding`.
- Show password requirements (e.g. minimum length) and surface clear auth errors.
- Add Terms and Privacy links (stub pages acceptable) covering CV and API-key handling.
- A back-to-landing link on the auth page.

## Files to Touch

- `webapp/frontend/app/auth/page.tsx` — forgot-password entry, email-confirm state, password requirements, error surfacing, back-to-landing link, Terms/Privacy links
- new reset-password page (e.g. `webapp/frontend/app/auth/reset/page.tsx`) — sets the new password from the reset email link
- new stub legal pages (e.g. `webapp/frontend/app/terms/page.tsx`, `webapp/frontend/app/privacy/page.tsx`) — cover CV + API-key handling
- `webapp/frontend/app/auth/callback/route.ts` — handle the confirmation/reset callback if needed

## How to QA

1. Forgot-password sends a reset email, and the reset page changes the password.
2. Signing up with confirmation enabled shows "check your email" with no broken onboarding (onboarding API calls no longer fire without a session).
3. Password rules are shown, and auth errors are surfaced clearly.
4. Terms and Privacy links are present and reachable.
5. A back-to-landing link is present on the auth page.
6. `uv run python3 -m pytest tests/ -v` passes.
7. `uv run python score.py --dry-run` passes.
