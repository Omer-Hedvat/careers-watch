| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/settings/page.tsx`, `webapp/backend/routers/user.py` |

## Overview

CV upload is currently only accessible during onboarding (Step 2). Users who have already onboarded and want to replace their CV have no path to do so. This adds a CV re-upload section to the Settings page, reusing the same upload logic as onboarding.

## Behaviour

- Settings page grows a "CV" tab or section with a file input (PDF, max 10 MB).
- On upload, the new PDF replaces the stored CV in Supabase; the old one is overwritten.
- A "last updated" timestamp is shown next to the upload button so the user knows which version is active.
- If no CV is on file yet, the section shows a first-upload prompt (same experience as onboarding Step 2).
- Upload validation: PDF only, size limit enforced client-side with a clear error message.

## Files to Touch

- `webapp/frontend/app/settings/page.tsx` — add CV upload section
- `webapp/backend/routers/user.py` — reuse or expose the existing CV upload endpoint

## How to QA

1. Open Settings page while authenticated — CV section is visible.
2. Upload a new PDF — last-updated timestamp updates.
3. Upload a non-PDF or a file > 10 MB — clear validation error is shown.
4. Navigate away and return to Settings — the most recently uploaded CV filename/date is still shown.
5. `uv run python3 -m pytest tests/ -v` passes.
6. `uv run python score.py --dry-run` passes.
