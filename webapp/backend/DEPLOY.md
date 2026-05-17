# Backend Deployment Notes

## Render.com setup

1. Connect repo to Render, select "Blueprint" deployment - it reads `render.yaml`
2. Set env vars in the Render dashboard (marked `sync: false` in render.yaml):
   - `SUPABASE_URL` - from Supabase project settings
   - `SUPABASE_SERVICE_ROLE_KEY` - from Supabase API settings (service_role key, NOT anon)
   - `FERNET_KEY` - generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
3. The persistent disk mounts at `/data`. On first deploy, copy `new_jobs.json` and `companies.json` there.
   GitHub Actions commits these files to the repo; seed the disk manually on first deploy.

## Local development

```bash
cd webapp/backend
cp .env.example .env   # fill in values
uv sync
uv run uvicorn main:app --reload
```

## Fernet key generation

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```
