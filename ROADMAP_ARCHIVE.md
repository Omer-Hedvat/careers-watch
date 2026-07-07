# CareerWatch — Roadmap Archive

Wrapped features only. Active work lives in `ROADMAP.md`.

---

## Epics (all wrapped)

| Epic | Spec | Phase | Status | Children |
|---|---|---|---|---|
| Web App v1 | `WEBAPP_SPEC.md` | P2 | `wrapped` | 9 |
| Proprietary ATS Pullers | `future_devs/archive/PROPRIETARY_ATS_PULLERS_SPEC.md` | P3 | `wrapped` | 9 |
| Position Liveness | `future_devs/archive/POSITION_LIVENESS_SPEC.md` | P8 | `wrapped` | 4 |
| App shell & account UX | `future_devs/archive/WEBAPP_APP_SHELL_ACCOUNT_SPEC.md` | P7 | `wrapped` | 4 |
| First-run comprehension | `future_devs/archive/WEBAPP_FIRST_RUN_COMPREHENSION_SPEC.md` | P7 | `wrapped` | 5 |
| Digest legibility & trust | `future_devs/archive/WEBAPP_DIGEST_TRUST_SPEC.md` | P7 | `wrapped` | 4 |
| Webapp visual design system | `future_devs/archive/WEBAPP_VISUAL_DESIGN_SPEC.md` | P10 | `wrapped` | 5 |

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
| Scoring calibration doc — rubric design, spot-check against real scores, failure modes | `future_devs/archive/SCORING_RUBRIC_ABLATION_SPEC.md` | S | `wrapped` |

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
| [webapp] Count-up animation on Companies + Positions page load | `future_devs/archive/WEBAPP_COUNTUP_ANIMATION_SPEC.md` | XS | `wrapped` |
| [webapp] Gap analysis — profile vs CV, position vs CV, position vs profile | `future_devs/archive/PROFILE_CV_GAP_ANALYSIS_SPEC.md` | M | `wrapped` |
| [webapp] CV upload: DOCX + TXT support alongside PDF | `future_devs/archive/WEBAPP_CV_UPLOAD_FORMATS_SPEC.md` | S | `wrapped` |
| [webapp] Full format set (.md/.txt/.pdf/.docx/.doc) for BOTH CV + profile uploads; centralized allowed-types | `future_devs/archive/WEBAPP_UNIFIED_UPLOAD_FORMATS_SPEC.md` | S | `wrapped` |
| [webapp] Settings reflects current state — CV file/text, filters, API-key status, account identity | `future_devs/archive/WEBAPP_SETTINGS_STATE_VISIBILITY_SPEC.md` | S | `wrapped` |
| [webapp] Profile upload or AI-prompt generator for building profile.md | `future_devs/archive/WEBAPP_PROFILE_UPLOAD_OR_PROMPT_SPEC.md` | M | `wrapped` |
| Stamp `first_seen` date on each position — persist across daily runs, show in digest + webapp cards | `future_devs/archive/POSITION_FIRST_SEEN_SPEC.md` | S | `wrapped` |
| [webapp] Positions page — clicking a position opens an in-app detail slide-over (shared `DetailPanel`) with a link out to the posting, instead of navigating straight out | `future_devs/archive/WEBAPP_POSITIONS_DETAIL_VIEW_SPEC.md` | S | `wrapped` |
| [webapp] Digest toolbar — "N suitable roles out of M collected" (`GET /jobs/stats`); retargeted from the Positions page to the Digest after CATALOG_SYNC made Positions the full market | `future_devs/archive/WEBAPP_POSITIONS_TOTAL_COUNT_SPEC.md` | XS | `wrapped` |

---

## Phase P6 — AI / Experimental

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Spike + adopt MarkItDown as doc→Markdown step for CV upload (+ future RAG doc ingest) | `future_devs/archive/MARKITDOWN_PDF_INGEST_SPEC.md` | S | `wrapped` |

---

## Phase P7 — App shell & account UX

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Global nav shell — shared header, Digest/Companies/Positions/Gaps/Settings/Help links, sign-out, mobile hamburger | `future_devs/archive/WEBAPP_GLOBAL_APP_SHELL_NAV_SPEC.md` | M | `wrapped` |
| Getting-started checklist — 4-item dismissible checklist on digest; auto-hides when complete | `future_devs/archive/WEBAPP_GETTING_STARTED_CHECKLIST_SPEC.md` | S | `wrapped` |
| In-app Help / FAQ — `/help` page with anchored sections (scoring, flags, cadence, privacy, improve) | `future_devs/archive/WEBAPP_IN_APP_HELP_FAQ_SPEC.md` | S | `wrapped` |
| Auth: forgot-password + email-confirm state + password requirements + Terms/Privacy stubs | `future_devs/archive/WEBAPP_AUTH_RESET_CONFIRM_LEGAL_SPEC.md` | M | `wrapped` |

---

## Phase P7 — Digest legibility & trust

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Score legend & tier explainer — inline key, "How scoring works" popover, per-badge tooltips | `future_devs/archive/WEBAPP_SCORE_LEGEND_SPEC.md` | S | `wrapped` |
| Flag glossary & friendly labels — shared `lib/flags.ts` slug→label/definition map, tooltips, glossary popover | `future_devs/archive/WEBAPP_FLAG_GLOSSARY_SPEC.md` | S | `wrapped` |
| Cadence & run-limit explainer — score-now help, reset-day copy, "Mon & Thu" cadence; `/user/me` returns `run_limit_resets_on` | `future_devs/archive/WEBAPP_CADENCE_RUN_LIMIT_EXPLAINER_SPEC.md` | S | `wrapped` |
| Diagnostic empty states + scoring progress feedback — account-state-keyed empties, in-progress indicator + result count, loading skeletons | `future_devs/archive/WEBAPP_DIAGNOSTIC_STATES_SPEC.md` | S | `wrapped` |

---

## Phase P8 — Position liveness

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Persist live `apply_url` set from successful pulls | `future_devs/archive/POSITION_LIVENESS_LIVE_SET_SPEC.md` | S | `wrapped` |
| Diff scored jobs vs live set → `status` + `closed_at` in `scored_jobs.json` | `future_devs/archive/POSITION_LIVENESS_STATUS_DIFF_SPEC.md` | S | `wrapped` |
| Render closed jobs distinctly in `digest.md` (strikethrough, closed date, trailing section) | `future_devs/archive/POSITION_LIVENESS_DIGEST_RENDER_SPEC.md` | S | `wrapped` |
| Reflect `status`/`closed_at` in webapp digest API + closed-card rendering | `future_devs/archive/POSITION_LIVENESS_WEBAPP_SPEC.md` | S | `wrapped` |

---

## Phase P9 — ATS expansion II

| Feature | Spec | Effort | Status |
|---|---|---|---|
| SmartRecruiters puller — CyberArk + Palo Alto Networks (regressed since; tracked as BUG_SMARTRECRUITERS_ROUTING) | `future_devs/archive/ATS_SMARTRECRUITERS_SPEC.md` | S | `wrapped` |
| BambooHR puller — Nilus (3 jobs) + 4 others | `future_devs/archive/ATS_BAMBOOHR_SPEC.md` | S | `wrapped` |
| Oracle Taleo puller — Radware (44+ jobs) | `future_devs/archive/ATS_TALEO_SPEC.md` | M | `wrapped` |
| Oracle HCM puller — Dell Technologies (325 jobs globally; 0 Israel openings at wrap time) | `future_devs/archive/ATS_ORACLE_HCM_SPEC.md` | M | `wrapped` |

---

## Phase P10 — Webapp visual design system

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Design tokens + theme + typography foundation (CSS variables, Tailwind mapping, next/font, shared SCORE_BANDS) | `future_devs/archive/WEBAPP_DESIGN_TOKENS_SPEC.md` | S | `wrapped` |
| Digest visual redesign — cards, badges, legend, skeleton, empty states, mount motion | `future_devs/archive/WEBAPP_DIGEST_VISUAL_SPEC.md` | M | `wrapped` |
| Landing visual glow-up — hero/section polish, FAQ animation, real JobCard reused in preview | `future_devs/archive/WEBAPP_LANDING_VISUAL_SPEC.md` | M | `wrapped` |
| Unify iconography on lucide-react + consistent micro-interactions across Nav/checklist/positions/companies/gaps/auth | `future_devs/archive/WEBAPP_ICONOGRAPHY_MOTION_SPEC.md` | S | `wrapped` |
| Onboarding wizard visual polish — step indicator, transitions, styled form controls | `future_devs/archive/WEBAPP_ONBOARDING_VISUAL_SPEC.md` | S | `wrapped` |

---

## Phase P11 — Pipeline reliability & hardening

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Repo-wide ATS puller correctness + resilience audit — fixed SuccessFactors ISO-code locations (0/7→7/7 Israel jobs), Workday "N Locations" collapse, teamme city+country join, talentbrew shared strip_html; added `expand_country`/`qualify_location` helpers + 9 regression tests | `future_devs/archive/ATS_PULLER_HARDENING_AUDIT_SPEC.md` | M | `wrapped` |

---

## Phase P12 — Webapp visual re-identity v2

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Bold visual re-identity ("Market Terminal": amber/ink palette, Instrument Serif/Sans + IBM Plex Mono, signature hero) + light/dark theme toggle with no-flash bootstrap | `future_devs/archive/WEBAPP_VISUAL_REDESIGN_V2_SPEC.md` | L | `wrapped` |

---

## Phase P7 — Job-seeker workspace

| Feature | Spec | Effort | Status |
|---|---|---|---|
| In-app job detail view — slide-over with full reasoning, flags + glossary, full JD (persisted at score time, migration 006) | `future_devs/archive/WEBAPP_JOB_DETAIL_VIEW_SPEC.md` | M | `wrapped` |

---

## Phase P7 — Standalone

| Feature | Spec | Effort | Status |
|---|---|---|---|
| Accessibility pass — score-badge accessible names (color-blind safe), `aria-label`/`aria-expanded` on icon-only controls, WCAG AA `--color-text-subtle` bump in both themes | `future_devs/archive/WEBAPP_ACCESSIBILITY_PASS_SPEC.md` | S | `wrapped` |
