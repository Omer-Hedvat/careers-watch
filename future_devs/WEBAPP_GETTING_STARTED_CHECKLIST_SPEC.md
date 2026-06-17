| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | WEBAPP_APP_SHELL_ACCOUNT |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/digest/page.tsx` (+ a small component); reads existing `/user/me` |

## Overview

A new account has no guidance on what is left to set up to get results. The user lands on an empty digest with no clear next step. A getting-started checklist on the digest surfaces the remaining setup items and links to where to complete each.

## Behaviour

- A dismissible "Getting started" checklist on the digest, shown until complete. Items:
  - Profile added
  - CV added
  - API key set
  - First scan run
- Each item links to where to complete it.
- Checked state derives from `/user/me`: `profile_md` present, `cv_text` present, API key set, plus whether any jobs are scored.
- The checklist auto-hides once all items are complete.
- It re-surfaces if a prerequisite is later removed (e.g. the API key is deleted).

## Files to Touch

- `webapp/frontend/app/digest/page.tsx` — render the checklist above the digest results
- a small component (e.g. `webapp/frontend/app/components/GettingStartedChecklist.tsx`) — checklist UI and completion logic, sourced from `/user/me`

## How to QA

1. A fresh account shows unchecked items, each linking to the right place (profile, CV, API key, scan).
2. Completing each item checks it.
3. The checklist disappears when all items are done.
4. Removing a prerequisite (e.g. deleting the API key) re-surfaces the checklist.
5. `uv run python3 -m pytest tests/ -v` passes.
6. `uv run python score.py --dry-run` passes.
