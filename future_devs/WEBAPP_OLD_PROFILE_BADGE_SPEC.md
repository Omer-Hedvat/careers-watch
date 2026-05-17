| Field | Value |
|---|---|
| **Phase** | P2 |
| **Status** | `in-progress` |
| **Effort** | S |
| **Epic** | Web App v1 |
| **Depends on** | webapp_digest (wrapped) |
| **Blocks** | — |
| **Touches** | `webapp/supabase/migrations/`, `webapp/backend/routers/user.py`, `webapp/frontend/app/digest/page.tsx` |

## Overview

When a user updates their `profile.md`, previously-scored jobs were scored against the old profile. Those scores may no longer reflect the updated criteria. The digest should visually flag such jobs so the user knows to re-score.

## Behaviour

- Track a `profile_version` (integer, increments on every profile save) on the `users` table
- On each scoring run, record the `profile_version` at time of scoring in `scored_jobs`
- In the digest, jobs scored with a `profile_version` lower than the current one show a soft badge: "scored with old profile"
- Badge is muted (grey, small) — not alarming, just informational
- No automatic re-score triggered; user can click "Score now" to get fresh scores

## Files to Touch

- `webapp/supabase/migrations/002_profile_version.sql` — add `profile_version int default 1` to `users`; add `profile_version int` to `scored_jobs`
- `webapp/backend/routers/user.py` — `PATCH /user/profile` increments `profile_version` after saving
- `webapp/backend/routers/scoring.py` — read current `profile_version` from users table; write it into each `scored_jobs` row
- `webapp/frontend/app/digest/page.tsx` — add `profile_version` to `Job` type; show badge if `job.profile_version < currentProfileVersion`
- `webapp/frontend/app/digest/page.tsx` — fetch current profile_version from `GET /user/me`

## Migration SQL

```sql
alter table users add column if not exists profile_version int default 1;
alter table scored_jobs add column if not exists profile_version int;
```

## How to QA

1. Score a batch of jobs
2. Go to Settings → Profile, edit profile, save
3. Return to digest — confirm all existing cards show "scored with old profile" badge
4. Click "Score now" — confirm new cards do NOT show the badge
5. Confirm old cards still show badge (they weren't re-scored)
