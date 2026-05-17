# Frontend Deployment Notes

## Render.com setup

Set these env vars in the Render dashboard:
- `NEXT_PUBLIC_SUPABASE_URL` - from Supabase project settings
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - from Supabase API settings (anon key)
- `NEXT_PUBLIC_API_URL` - URL of the deployed FastAPI backend (e.g. https://careerwatch-api.onrender.com)

## Local development

```bash
cd webapp/frontend
cp .env.local.example .env.local   # fill in values
npm install
npm run dev
```
