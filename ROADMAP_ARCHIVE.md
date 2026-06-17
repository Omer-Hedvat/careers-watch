# CareerWatch — Roadmap Archive

Wrapped features only. Active work lives in `ROADMAP.md`.

---

## Epics (all wrapped)

| Epic | Spec | Phase | Status | Children |
|---|---|---|---|---|
| Web App v1 | `WEBAPP_SPEC.md` | P2 | `wrapped` | 9 |
| Proprietary ATS Pullers | `future_devs/archive/PROPRIETARY_ATS_PULLERS_SPEC.md` | P3 | `wrapped` | 9 |

---

## Phase P3 — Coverage expansion

| Feature | Spec | Effort | Status |
|---|---|---|---|
| TalentBrew puller → Intuit (474 IL jobs) | `future_devs/archive/ATS_TALENTBREW_SPEC.md` | XS | `wrapped` |
| amazon.jobs puller → AWS Israel (135 jobs) | `future_devs/archive/ATS_AMAZON_JOBS_SPEC.md` | S | `wrapped` |
| Microsoft Careers puller → Microsoft Israel (10 jobs) | `future_devs/archive/ATS_MICROSOFT_CAREERS_SPEC.md` | S | `wrapped` |
| Google Careers puller → Google Israel (70 jobs) | `future_devs/archive/ATS_GOOGLE_CAREERS_SPEC.md` | S | `wrapped` |
| Eightfold puller → PayPal Israel (4 jobs; PCSX fallback) | `future_devs/archive/ATS_EIGHTFOLD_SPEC.md` | S | `wrapped` |
| Jobvite puller → Varonis (67 jobs) | `future_devs/archive/ATS_JOBVITE_SPEC.md` | S | `wrapped` |
| SuccessFactors puller → SAP Israel (6 jobs; CyberArk → PAN/SmartRecruiters) | `future_devs/archive/ATS_SUCCESSFACTORS_SPEC.md` | M | `wrapped` |
| TeamMe puller → Claroty (24) + Quantum Machines (45) | `future_devs/archive/ATS_TEAMME_SPEC.md` | M | `wrapped` |
| Breezy HR puller → Descope (0 openings at wrap time) | `future_devs/archive/ATS_BREEZY_SPEC.md` | XS | `wrapped` |
| Fix TLV Partners scraper + clean stale entries + add missing portfolio companies | `future_devs/archive/TLV_PORTFOLIO_FIX_SPEC.md` | M | `wrapped` |
| ATS params filled for 13 stubs — Artemis Security (Ashby, 10 jobs), Kela (Comeet token, 28 jobs), PAN (SmartRecruiters documented) | `future_devs/archive/BIG_COMPANIES_ATS_PARAMS_SPEC.md` | M | `wrapped` |

---

## Phase P2 — Web App v1

| Feature | Spec | Effort | Status |
|---|---|---|---|
| [webapp] Project scaffold — Next.js + FastAPI + Supabase schema | `future_devs/archive/WEBAPP_SCAFFOLD_SPEC.md` | M | `wrapped` |
| [webapp] Auth — email + Google OAuth, session management | `future_devs/archive/WEBAPP_AUTH_SPEC.md` | S | `wrapped` |
| [webapp] Scoring endpoint — runs score.py per user, rate-limited 2x/week | `future_devs/archive/WEBAPP_SCORING_ENDPOINT_SPEC.md` | M | `wrapped` |
| [webapp] Landing page — value prop, how it works, CTA | `future_devs/archive/WEBAPP_LANDING_SPEC.md` | S | `wrapped` |
| [webapp] GitHub Actions wiring — scheduled collect + refresh commit to repo | `future_devs/archive/WEBAPP_ACTIONS_WIRING_SPEC.md` | S | `wrapped` |
| [webapp] Render.com deploy — FastAPI + Next.js, persistent disk, env vars | `future_devs/archive/WEBAPP_DEPLOY_SPEC.md` | S | `wrapped` |
| [webapp] Onboarding — profile prompt generator, CV upload, Gemini key, filters | `future_devs/archive/WEBAPP_ONBOARDING_SPEC.md` | M | `wrapped` |
| [webapp] Digest view — ranked cards, applied toggle, score filter | `future_devs/archive/WEBAPP_DIGEST_SPEC.md` | M | `wrapped` |
| [webapp] Settings — profile, CV, filters, API key, account tabs | `future_devs/archive/WEBAPP_SETTINGS_SPEC.md` | S | `wrapped` |

---

## Phase P2 — Web App v1 (post-launch)

| Feature | Spec | Effort | Status |
|---|---|---|---|
| [webapp] Supabase initial setup guide — schema migration, Google OAuth, RLS verification | `future_devs/archive/WEBAPP_SUPABASE_SETUP_GUIDE_SPEC.md` | XS | `wrapped` |

---

## Phase P1 — Pipeline improvements

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Fix Viola Getro duplicate jobs — dedupe by apply_url before scoring | `future_devs/archive/VIOLA_GETRO_DEDUP_SPEC.md` | S | `wrapped` |
| Rescore existing digest with updated profile | `future_devs/archive/RESCORE_EXISTING_SPEC.md` | S | `wrapped` |
| Scheduled automation via GitHub Actions (collect Mon/Thu, refresh biweekly) | `future_devs/archive/GITHUB_ACTIONS_SCHEDULE_SPEC.md` | S | `wrapped` |

---

## Phase P4 — Portfolio showcase

| Feature | Spec | Effort | Status |
|---|---|---|---|
| DS analysis notebook — score distribution, VC tier signal, top companies, flag frequency | `future_devs/archive/DS_ANALYSIS_NOTEBOOK_SPEC.md` | S | `wrapped` |
| README rewrite — engineering showcase with Mermaid architecture diagram and real scale numbers | `future_devs/archive/REPO_SHOWCASE_SPEC.md` | S | `wrapped` |

---

## Phase P0 — Pipeline (all wrapped)

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Multi-profile support | — | S | `wrapped` |
| Per-job deduplication — skip already-scored jobs before Gemini | `future_devs/archive/SCORING_DEDUP_SPEC.md` | S | `wrapped` |
| Batch scoring — 10 jobs per Gemini call instead of 1 | `future_devs/archive/BATCH_SCORING_SPEC.md` | S | `wrapped` |
| Title allowlist filter — only send relevant titles to Gemini | `future_devs/archive/TITLE_ALLOWLIST_SPEC.md` | S | `wrapped` |
| Per-profile score_config.json — configurable denylist/allowlist/company filters | `future_devs/archive/SCORE_CONFIG_SPEC.md` | S | `wrapped` |
| Two-CV routing — Team Lead CV vs default CV per job title | `future_devs/archive/TWO_CV_ROUTING_SPEC.md` | S | `wrapped` |
| Applied tracking in digest — Applied: 0/1 per position, synced to scored_jobs.json | `future_devs/archive/APPLIED_TRACKING_SPEC.md` | S | `wrapped` |
| Location filter hardening — Israel-only, no remote, no hybrid | `future_devs/archive/LOCATION_FILTER_SPEC.md` | XS | `wrapped` |
| Profile update — domain-agnostic scoring, cyber as small boost | `future_devs/archive/PROFILE_REWRITE_SPEC.md` | XS | `wrapped` |

---

## Phase P5 — Webapp v2 improvements

| Feature | Spec | Effort | Status |
|---|---|---|---|
| [webapp] Favicon (briefcase SVG) + Open Graph meta tags | `future_devs/archive/WEBAPP_FAVICON_SPEC.md` | XS | `wrapped` |
| [webapp] Multi-value `;`-split filters (title, company, location) + placeholder text on digest page | `future_devs/archive/WEBAPP_MULTI_FILTER_SPEC.md` | S | `wrapped` |
| [webapp] CV re-upload section in Settings — PDF upload + last-updated timestamp | `future_devs/archive/WEBAPP_CV_SETTINGS_UPLOAD_SPEC.md` | S | `wrapped` |
| [webapp] Companies page — all tracked companies, metadata, failure badges, careers link | `future_devs/archive/WEBAPP_COMPANIES_VIEW_SPEC.md` | S | `wrapped` |
| [webapp] Positions page — browse all open roles from pipeline, client-side search + pagination | `future_devs/archive/WEBAPP_POSITIONS_VIEW_SPEC.md` | S | `wrapped` |

---

## Phase P8 — Position liveness

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Persist live `apply_url` set from successful pulls | `future_devs/archive/POSITION_LIVENESS_LIVE_SET_SPEC.md` | S | `wrapped` |
| Diff scored jobs vs live set → `status` + `closed_at` in `scored_jobs.json` | `future_devs/archive/POSITION_LIVENESS_STATUS_DIFF_SPEC.md` | S | `wrapped` |
| Render closed jobs distinctly in `digest.md` (strikethrough, closed date, trailing section) | `future_devs/archive/POSITION_LIVENESS_DIGEST_RENDER_SPEC.md` | S | `wrapped` |
