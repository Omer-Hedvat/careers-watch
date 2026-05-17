| Field | Value |
|---|---|
| **Phase** | P2 |
| **Status** | `not-started` |
| **Effort** | XS |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | Production deployment |
| **Touches** | `webapp/supabase/SETUP.md` (new) |

## Overview

There is no guide for setting up Supabase from scratch. `DEPLOY.md` tells you to set env vars but assumes the database schema already exists and Google OAuth is already configured. A new deployer would be stuck. This task writes a `webapp/supabase/SETUP.md` that covers everything needed before the first deploy.

## Behaviour

The guide must cover:

1. **Create a Supabase project** — free tier, choose region closest to target users
2. **Run the initial schema migration** — paste `webapp/supabase/migrations/001_initial_schema.sql` into the Supabase SQL editor and run it
3. **Get connection credentials** — where to find `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` in the Supabase dashboard
4. **Enable Google OAuth** (optional) — Authentication → Providers → Google → paste Client ID + Secret from Google Cloud Console; set redirect URL to `https://<your-frontend>.onrender.com/auth/callback`
5. **Verify RLS policies are active** — confirm the 4 policies from the migration appear in Authentication → Policies
6. **Test with the local backend** — `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` in `.env`, run `uv run uvicorn main:app`, hit `GET /health`

## Files to Touch

- `webapp/supabase/SETUP.md` (new)

## How to QA

1. Follow the guide on a fresh Supabase project from scratch
2. Confirm all migration tables appear in the Table Editor
3. Confirm local backend connects and `/health` returns `{"status": "ok"}`
4. Confirm Google OAuth redirect works end-to-end (if configured)
