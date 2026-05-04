# cyber-jobs-radar

Personal job-search automation. Scrapes Israeli cyber/fintech VC portfolio
companies, pulls open roles via ATS APIs, scores them against my profile
via Gemini, outputs a markdown digest.

Not actively maintained for general use.

## Three-script flow

```
refresh_companies.py   # weekly  — VC scrape + careers discovery + ATS detection
collect_jobs.py        # daily   — hit ATS APIs, write new_jobs.json
score.py               # on demand — score jobs via Gemini, write digest.md
```

### refresh_companies.py

Scrapes VC portfolio pages (currently: YL Ventures), discovers the careers
page and ATS for each company, and writes `companies.json`. This file is a
persistent cache — it accumulates over time and is never overwritten.

Re-verification runs automatically for any company whose `last_verified_at`
is older than 30 days or whose `consecutive_failures` counter is ≥ 3.

```
uv run python refresh_companies.py
```

### collect_jobs.py

Reads `companies.json`, calls ATS APIs (currently: Comeet) using cached
credentials, and writes `new_jobs.json`. Does no VC knowledge or discovery —
all it needs is `ats` and `ats_params` from the cache.

Increments `consecutive_failures` on errors, resets to 0 on success.

```
uv run python collect_jobs.py
```

### score.py

Reads `new_jobs.json` (or `tests/sample_jobs.json` with `--sample`),
scores each job against `profile.md` and `cv.md` via Gemini, and writes
`digest.md` grouped by score tier.

```
uv run python score.py --dry-run --sample   # inspect prompt, no API call
uv run python score.py --sample             # score sample jobs
uv run python score.py                      # score real jobs
```

## Setup

```
uv sync
uv run playwright install chromium
cp .env.example .env   # add GEMINI_API_KEY
```

## companies.json schema

```json
{
  "name": "Grip Security",
  "website": "https://www.grip.security",
  "source_vc": "YL Ventures",
  "vc_tier": "tier1",
  "careers_url": "https://www.comeet.com/jobs/grip/A8.001",
  "ats": "comeet",
  "ats_params": { "company_uid": "A8.001", "company_name": "grip", "token": "..." },
  "discovered_at": "2026-05-04T...",
  "last_verified_at": "2026-05-04T...",
  "last_jobs_pulled_at": "2026-05-04T...",
  "consecutive_failures": 0
}
```
