# Supabase Setup Guide

Run this once before the first deploy. After this, `DEPLOY.md` takes over.

---

## 1. Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and sign in.
2. Click **New project**.
3. Choose an organization, give the project a name (e.g. `careerwatch`), set a strong database password, and pick the region closest to your users (EU West for Israel).
4. Wait for provisioning (~1 minute).

---

## 2. Run the schema migration

1. In the Supabase dashboard, open **SQL Editor** (left sidebar).
2. Click **New query**.
3. Paste the entire contents of `webapp/supabase/migrations/001_initial_schema.sql`.
4. Click **Run**.

This creates three tables: `users`, `score_configs`, `scored_jobs` - and enables RLS on all three.

---

## 3. Get connection credentials

Open **Project Settings** → **API** (left sidebar).

| Env var | Where to find it |
|---|---|
| `SUPABASE_URL` | "Project URL" at the top |
| `SUPABASE_ANON_KEY` | Under "Project API keys" → `anon` `public` |
| `SUPABASE_SERVICE_ROLE_KEY` | Under "Project API keys" → `service_role` `secret` |

The backend uses `SUPABASE_SERVICE_ROLE_KEY` (bypasses RLS for server-side ops). The frontend uses `SUPABASE_ANON_KEY` (enforces RLS for client-side requests). Never expose the service role key in the frontend.

---

## 4. Enable Google OAuth (optional)

Skip this if you only want email/password login.

1. In the Supabase dashboard, go to **Authentication** → **Providers** → **Google**.
2. Toggle it on.
3. Paste your Google OAuth **Client ID** and **Client Secret**.
   - If you don't have these: go to [Google Cloud Console](https://console.cloud.google.com) → **APIs & Services** → **Credentials** → **Create credentials** → **OAuth client ID** → Application type: **Web application**.
4. In Google Cloud Console, under "Authorized redirect URIs", add:
   ```
   https://<your-supabase-project-ref>.supabase.co/auth/v1/callback
   ```
   You'll find the project ref in Supabase → **Project Settings** → **General**.
5. In your frontend env vars, the `NEXT_PUBLIC_SITE_URL` or the redirect URL passed to `supabase.auth.signInWithOAuth` should point to:
   ```
   https://<your-frontend>.onrender.com/auth/callback
   ```
6. Save in Supabase.

---

## 5. Verify RLS policies are active

1. Go to **Authentication** → **Policies** in the Supabase dashboard.
2. Confirm these four policies appear:

| Table | Policy name |
|---|---|
| `users` | users can read own row |
| `users` | users can update own row |
| `score_configs` | users can read own score_config |
| `scored_jobs` | users can read own scored_jobs |

If any are missing, re-run the migration SQL (the `create policy` statements are safe to re-run if you dropped them).

---

## 6. Test with the local backend

```bash
cd webapp/backend
cp .env.example .env
```

Fill in `.env`:
```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
FERNET_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
```

Then:
```bash
uv sync
uv run uvicorn main:app --reload
curl http://localhost:8000/health
# expected: {"status": "ok"}
```

If `/health` returns `{"status": "ok"}`, the backend is connected and the schema is in place. You're ready to deploy.
