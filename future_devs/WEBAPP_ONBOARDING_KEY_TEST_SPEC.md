| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | XS |
| **Epic** | WEBAPP_FIRST_RUN_COMPREHENSION |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/onboarding/page.tsx, webapp/backend/routers/user.py |

## Overview

An invalid Gemini key isn't caught until the first scan silently fails. Settings already has a "Test key" button, but onboarding Step 3 (API key) does not. This task adds a "Test key" action to onboarding Step 3 so a bad key is caught before the user proceeds.

## Behaviour

- Add a "Test key" action to onboarding Step 3 that fires the existing test-key endpoint and shows success/failure inline before the user proceeds.
- Non-blocking: the user may still proceed even after a failed test, but a failed test shows a clear warning.
- Reuse the existing `/user/test-key` logic. If that endpoint requires the key to be saved first, accept the key in the request body for a pre-save test (a small backend tweak in routers/user.py).
- Keep the dark theme; copy uses hyphens, not em-dashes.

## Files to Touch

- webapp/frontend/app/onboarding/page.tsx
- webapp/backend/routers/user.py (only if test-key must accept an unsaved key in the request body)

## How to QA

1. In onboarding Step 3, entering a valid key and clicking "Test key" shows an inline success state.
2. Entering an invalid key and clicking "Test key" shows a clear inline error.
3. After a failed test, the user can still proceed to the next step.
4. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
