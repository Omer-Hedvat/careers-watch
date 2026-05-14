# CareerWatch Web App — Product Spec

## Overview

CareerWatch is a self-serve job-matching platform. A user provides their CV, fills out a profile (with AI assistance), sets their filters, and the system continuously scrapes VC portfolio companies, collects open positions, and scores them against the user's profile using their own Gemini API key. The user sees a ranked digest of relevant positions and can mark what they've applied to.

The product is free. Users bring their own Gemini API key. The platform absorbs the infrastructure cost of scraping and collection; scoring runs on the user's quota.

---

## Users

Single persona: a job-seeking professional (primarily technical — data scientist, ML engineer, security researcher). Non-technical users are out of scope for v1.

---

## Core User Journey

1. Land on marketing page → understand what the product does in 10 seconds
2. Sign up with email
3. Generate a `profile.md` using an AI prompt (copy prompt → paste into ChatGPT/Claude/Gemini → paste result back)
4. Upload CV (PDF or paste text)
5. Enter Gemini API key
6. Configure filters (location, title denylist/allowlist, company exclusions)
7. Trigger first scoring run → see digest
8. Return periodically → new positions appear at the top
9. Mark positions as applied → they disappear from the active list

---

## Pages & Screens

### 1. Landing Page (`/`)

- Hero: one-line value prop + CTA ("Get started free")
- How it works: 3-step visual (Set up profile → System scrapes jobs → You get a ranked digest)
- "Built with your own AI key — your data never trains a model"
- Footer: GitHub link, author credit

### 2. Sign Up / Log In (`/auth`)

- Email + password
- Google OAuth
- No credit card, no plan selection

### 3. Onboarding Flow (first-time user, 4 steps)

**Step 1 — Generate your profile**
- Explanation: "Your profile tells the AI what you're looking for. The best way to create it is to use an AI assistant."
- A copyable prompt block:
  ```
  I'm setting up a job-matching tool that scores job postings against my profile.
  I need you to create a profile.md file for me by asking me questions about:
  - My background and years of experience
  - My target roles (title, seniority)
  - My preferred domains/industries
  - What I consider a strong fit vs. a dealbreaker
  - My location and commute constraints
  - What I explicitly don't want
  
  Ask me one section at a time. When done, output a complete profile.md in markdown.
  ```
- Paste result into a text area → validate it's non-empty → save
- "Already have a profile.md?" — skip to paste

**Step 2 — Upload your CV**
- Upload PDF or paste plain text
- CV is stored and used verbatim in scoring prompts

**Step 3 — Gemini API key**
- Input field (masked)
- "How to get a Gemini API key" expandable explanation:
  - Go to [Google AI Studio](https://aistudio.google.com)
  - Sign in with your Google account
  - Click "Get API key" → "Create API key"
  - Copy and paste the key here
  - The free tier is enough to get started (quota resets daily)
- Key is encrypted at rest, never logged, never shared
- Small note: "We never score jobs without your key. If you delete your key, scoring stops."

**Step 4 — Configure filters**
- **Location**: text input — what city/region terms to require in job location (e.g. "israel", "tel aviv"). Leave blank = no location filter.
- **Title denylist**: tags input — terms that auto-exclude a job title (e.g. "data engineer", "analyst"). Pre-populated with sensible defaults, fully editable.
- **Title allowlist**: tags input — at least one term must appear in the title for a job to be scored. Leave blank = score everything that passes denylist.
- **Excluded companies**: tags input — company names to skip entirely.
- **Excluded industries**: tags input — industry keywords to skip entirely (e.g. "gaming", "adtech", "gambling", "crypto"). Jobs whose company or description matches any term are dropped before scoring.
- Preview: "With these filters, X of today's Y collected jobs would be sent to Gemini."

→ "Start my first scoring run" → triggers scoring job in background → redirects to digest

---

### 4. Digest (`/digest`)

Main screen. Seen every return visit.

**Header bar:**
- Last scored: "2 days ago" | Next collection: "Tomorrow"
- "Score now" button (enabled if within weekly limit; shows "2 of 2 runs used this week" when exhausted)
- Settings icon

**Position cards** (sorted by score desc, then date desc):

```
┌─────────────────────────────────────────────────────────────┐
│ 9/10   Cato Networks — Research Team Lead                   │
│ Tel Aviv · Comeet · Scored today                            │
│ "Strong fit for security ML lead role with production       │
│  ownership. Team8-backed, clear leadership path."           │
│ [threat-detection] [team-lead] [tier1-vc]                  │
│                              [Apply →]  [Mark as Applied ✓] │
└─────────────────────────────────────────────────────────────┘
```

- Scores 9-10: green accent
- Scores 7-8: blue accent
- Scores 5-6: grey
- Applied positions: collapsed into "X applied — show" at the bottom
- Positions scored before the current profile version: soft badge "scored with old profile"

**Filters sidebar** (collapsible):
- Filter by score (slider: show ≥ N)
- Filter by date scored
- Search by company or title

---

### 5. Settings (`/settings`)

Tabs: **Profile** | **CV** | **Filters** | **API Key** | **Account**

**Profile tab:**
- Edit profile.md in a textarea
- "Regenerate with AI" — shows the prompt block again
- "Re-score all positions with updated profile" — triggers full rescore (burns quota, shown as warning)

**CV tab:**
- View/replace current CV text or PDF

**Filters tab:**
- Same UI as onboarding Step 4
- Live preview count updates as user edits

**API Key tab:**
- Replace key
- "Test key" — fires a single test call to verify it works
- Delete key (pauses scoring)

**Account tab:**
- Change email/password
- Export all data (JSON)
- Delete account

---

## Scheduling & Backend Behavior

| Job | Frequency | Who runs it |
|-----|-----------|-------------|
| `refresh_companies.py` | Every 2 weeks | GitHub Actions cron |
| `collect_jobs.py` | Mon + Thu | GitHub Actions cron |
| `score.py` | User-triggered | Web server (async job) |

**Scoring rate limit:** 2 runs per user per week. Enforced server-side. Shown clearly in the UI.

**Deduplication:** Per-user `all_scores.jsonl` ledger (already implemented). A position scored in a previous run is never re-sent to Gemini.

**Shared data:** `companies.json` and `new_jobs.json` are global — one copy for all users. Scoring input is shared; scoring output is fully isolated per user.

---

## Profile Generation Prompt

Surfaced in two places: onboarding Step 1 and Settings → Profile tab.

The prompt is static, copyable with one click, and includes instructions for the AI to:
- Ask about experience, target roles, domain preferences, location, dealbreakers
- Output a well-structured `profile.md` that the scoring system can parse

The prompt should explicitly mention that the output will be read by an LLM scorer, so the profile should be specific and opinionated, not generic.

---

## Data Model (simplified)

**users**
- id, email, password_hash, created_at
- gemini_api_key (encrypted)
- profile_md (text)
- cv_text (text)
- scoring_runs_this_week (int), last_week_reset (date)

**score_configs**
- user_id, location_terms (array), skip_title_terms (array), keep_title_terms (array), skip_companies (array), skip_industries (array)
- cv_lead_path (nullable), cv_default_path (nullable), lead_title_terms (array)

**scored_jobs**
- user_id, apply_url (unique per user), company, title, location, score, reasoning, flags (array), scored_at, applied (bool)

**Global files (not per-user):**
- `companies.json` — refreshed every 2 weeks
- `new_jobs.json` — refreshed Mon/Thu

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Frontend | Next.js 14 (App Router) + Tailwind + shadcn/ui | Professional, fast, well-supported |
| Backend | FastAPI (Python) | Reuses existing scoring code directly |
| Database | Supabase (PostgreSQL) free tier | Auth + storage, generous free limits |
| Job queue | Supabase Edge Functions or simple async FastAPI background tasks | Scoring runs are short enough |
| Hosting | Render.com free tier | Persistent disk, Python-native |
| Scheduling | GitHub Actions cron | Free, already where the code lives |
| API key encryption | `cryptography` (Fernet) | Simple symmetric encryption |

---

## v1 Scope (what ships)

- Landing page
- Email auth
- Onboarding flow (4 steps)
- Profile prompt generator
- CV upload (text paste + PDF extract)
- Filter configuration
- Digest view with scoring
- Mark as applied
- Settings (all tabs)
- GitHub Actions scheduled jobs

## Out of scope for v1

- Email notifications ("new positions scored")
- Multiple profiles per user
- Team/shared accounts
- Mobile app
- Re-score with updated profile (too quota-heavy to offer freely)
- Custom VC list per user (everyone gets the same VC universe)
