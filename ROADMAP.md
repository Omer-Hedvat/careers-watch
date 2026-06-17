# CareerWatch — Roadmap

> Active tasks only. Wrapped items live in `ROADMAP_ARCHIVE.md`.
> Read the relevant spec before touching files in that domain.
> Use `/tasks_status` for a dashboard view.

---

## Status Legend

| Symbol | Meaning |
|---|---|
| `not-started` | Ready to build (all dependencies met) |
| `in-progress` | Currently being implemented |
| `completed` | Dev done, awaiting `/qa_task` |
| `wrapped` | QA passed, committed, archived |

## Effort Legend

| Size | Scope |
|---|---|
| XS | < 1 hour, single file |
| S | 1–2 days |
| M | 3–5 days |
| L | 1–2 weeks |
| XL | 2+ weeks |

---

## Epics

| Slug | Title | Status | Effort | Children |
|---|---|---|---|---|
| [WEBAPP_FIRST_RUN_COMPREHENSION](future_devs/WEBAPP_FIRST_RUN_COMPREHENSION_SPEC.md) | First-run comprehension (what/why/what-you-get before & during onboarding) | `in-progress` | L | 5 |
| [WEBAPP_DIGEST_TRUST](future_devs/WEBAPP_DIGEST_TRUST_SPEC.md) | Digest legibility & trust (scores, flags, cadence, empty states) | `not-started` | M | 4 |
| [WEBAPP_JOBSEEKER_WORKFLOW](future_devs/WEBAPP_JOBSEEKER_WORKFLOW_SPEC.md) | Job-seeker workspace (detail view, status tracker, hide, new, sort) | `not-started` | L | 5 |
| [WEBAPP_APP_SHELL_ACCOUNT](future_devs/archive/WEBAPP_APP_SHELL_ACCOUNT_SPEC.md) | App shell + account UX (nav, sign-out, help, auth recovery) | `wrapped` | M | 4 |
| [POSITION_LIVENESS](future_devs/archive/POSITION_LIVENESS_SPEC.md) | Position liveness — mark & surface closed postings in the scored digest | `wrapped` | M | 4 |

Run `/orchestrate_epic <slug>` to execute an epic's children in waves.

---

## Phase P0 — Pipeline (complete)

All Phase P0 tasks are wrapped. See `ROADMAP_ARCHIVE.md`.

---

## Phase P1 — Pipeline improvements (complete)

All Phase P1 tasks are wrapped. See `ROADMAP_ARCHIVE.md`.

---

## Phase P2 — Web App v1 (complete)

All Phase P2 tasks are wrapped. See `ROADMAP_ARCHIVE.md`.

---

## Phase P2 — Web App v1 (post-launch)

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [WEBAPP_SUPABASE_SETUP_GUIDE](future_devs/archive/WEBAPP_SUPABASE_SETUP_GUIDE_SPEC.md) | Supabase initial setup guide (schema, OAuth, RLS) | `wrapped` | XS | — |
| [WEBAPP_PDF_CV_UPLOAD](future_devs/archive/WEBAPP_PDF_CV_UPLOAD_SPEC.md) | PDF CV upload in onboarding Step 2 | `wrapped` | S | — |
| [WEBAPP_OLD_PROFILE_BADGE](future_devs/archive/WEBAPP_OLD_PROFILE_BADGE_SPEC.md) | "Scored with old profile" badge on digest cards | `wrapped` | S | — |

---

## Phase P3 — Coverage expansion

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [NEW_VC_ADAPTERS](future_devs/archive/NEW_VC_ADAPTERS_SPEC.md) | Add VC adapters: State of Mind / Sequoia IL / Aleph / Lightspeed IL / Greylock / Insight IL | `wrapped` | M | — |
| [TLV_PORTFOLIO_FIX](future_devs/archive/TLV_PORTFOLIO_FIX_SPEC.md) | Fix TLV Partners scraper + clean stale entries + add missing portfolio companies | `wrapped` | M | — |
| [BIG_COMPANIES_ATS_PARAMS](future_devs/archive/BIG_COMPANIES_ATS_PARAMS_SPEC.md) | Fill ATS params for ~30 unfilled big_companies.yml stubs | `wrapped` | M | — |
| [PIPELINE_TEST_COVERAGE](future_devs/archive/PIPELINE_TEST_COVERAGE_SPEC.md) | Add test suite for pipeline scripts (ATS pullers, filters, scorer parser) | `wrapped` | M | — |

---

## Phase P4 — Portfolio showcase

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [DS_ANALYSIS_NOTEBOOK](future_devs/archive/DS_ANALYSIS_NOTEBOOK_SPEC.md) | DS analysis notebook — score distribution, VC tier signal, top companies | `wrapped` | S | — |
| [REPO_SHOWCASE](future_devs/archive/REPO_SHOWCASE_SPEC.md) | README rewrite — engineering showcase with architecture diagram and scale callouts | `wrapped` | S | — |
| [SCORING_RUBRIC_ABLATION](future_devs/SCORING_RUBRIC_ABLATION_SPEC.md) | Scoring calibration doc — rubric design, spot-check, failure modes | `completed` | S | — |

---

## Phase P5 — Webapp v2 improvements

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [WEBAPP_CV_SETTINGS_UPLOAD](future_devs/archive/WEBAPP_CV_SETTINGS_UPLOAD_SPEC.md) | CV re-upload section in Settings (outside onboarding) | `wrapped` | S | — |
| [WEBAPP_CV_UPLOAD_FORMATS](future_devs/WEBAPP_CV_UPLOAD_FORMATS_SPEC.md) | CV upload: add DOCX + TXT support alongside PDF | `completed` | S | WEBAPP_PDF_CV_UPLOAD ✅ |
| [WEBAPP_SETTINGS_STATE_VISIBILITY](future_devs/WEBAPP_SETTINGS_STATE_VISIBILITY_SPEC.md) | Settings shows current state: CV file/text, filters, API-key present/missing, account name+email | `completed` | S | — |
| [WEBAPP_PROFILE_UPLOAD_OR_PROMPT](future_devs/WEBAPP_PROFILE_UPLOAD_OR_PROMPT_SPEC.md) | Profile upload OR AI-prompt generator for building profile.md | `completed` | M | — |
| [WEBAPP_POSITIONS_VIEW](future_devs/archive/WEBAPP_POSITIONS_VIEW_SPEC.md) | Positions page — browse all open roles from pipeline | `wrapped` | S | WEBAPP_COMPANIES_VIEW ✅ |
| [PROFILE_CV_GAP_ANALYSIS](future_devs/archive/PROFILE_CV_GAP_ANALYSIS_SPEC.md) | Gap analysis: profile vs CV, position vs CV, position vs profile | `wrapped` | M | — |
| [WEBAPP_COUNTUP_ANIMATION](future_devs/archive/WEBAPP_COUNTUP_ANIMATION_SPEC.md) | Count-up animation on Companies + Positions page load | `wrapped` | XS | — |
| [POSITION_FIRST_SEEN](future_devs/POSITION_FIRST_SEEN_SPEC.md) | Stamp first_seen date on each position — persist across daily runs, show in digest + webapp cards | `completed` | S | — |

---

## Phase P6 — AI / Experimental

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [RAG_CHATBOT](future_devs/RAG_CHATBOT_SPEC.md) | RAG sandbox + "Chat with the Job Market" chatbot (next AI epic) | `not-started` | L | — |
| [MULTI_AGENT_RESUME_TAILOR](future_devs/MULTI_AGENT_RESUME_TAILOR_SPEC.md) | Actor/critic multi-agent resume tailor for high-scoring jobs | `not-started` | M | RAG_CHATBOT |

---

## Phase P7 — Webapp UX & first-run experience

First-time-user comprehension, digest trust, the job-seeker workspace, and the app shell. Filed from a UX review of the live webapp through a new job-seeker's eyes: what they need, what's missing, and which explanations a first-timer lacks.

### Epic: First-run comprehension

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [WEBAPP_FIRST_RUN_COMPREHENSION](future_devs/WEBAPP_FIRST_RUN_COMPREHENSION_SPEC.md) | First-run comprehension (epic root) | `completed` | L | — |
| [WEBAPP_LANDING_REVAMP](future_devs/WEBAPP_LANDING_REVAMP_SPEC.md) | Landing revamp — value prop, BYO-key explainer, digest preview, FAQ | `completed` | S | WEBAPP_FIRST_RUN_COMPREHENSION |
| [WEBAPP_ONBOARDING_ORIENTATION](future_devs/WEBAPP_ONBOARDING_ORIENTATION_SPEC.md) | Onboarding orientation + why-this-matters copy + setup summary | `completed` | S | WEBAPP_FIRST_RUN_COMPREHENSION |
| [WEBAPP_PROFILE_EXAMPLE_GUIDANCE](future_devs/WEBAPP_PROFILE_EXAMPLE_GUIDANCE_SPEC.md) | Profile example + section guidance + completeness hint | `completed` | S | WEBAPP_FIRST_RUN_COMPREHENSION |
| [WEBAPP_FILTER_PLAIN_LANGUAGE_PREVIEW](future_devs/WEBAPP_FILTER_PLAIN_LANGUAGE_PREVIEW_SPEC.md) | Plain-language filters + live "X of Y jobs" preview | `completed` | M | WEBAPP_FIRST_RUN_COMPREHENSION |
| [WEBAPP_ONBOARDING_KEY_TEST](future_devs/WEBAPP_ONBOARDING_KEY_TEST_SPEC.md) | Inline "Test key" in onboarding Step 3 | `completed` | XS | WEBAPP_FIRST_RUN_COMPREHENSION |

### Epic: Digest legibility & trust

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [WEBAPP_DIGEST_TRUST](future_devs/WEBAPP_DIGEST_TRUST_SPEC.md) | Digest legibility & trust (epic root) | `not-started` | M | — |
| [WEBAPP_SCORE_LEGEND](future_devs/WEBAPP_SCORE_LEGEND_SPEC.md) | Score legend & tier explainer | `wrapped` | S | WEBAPP_DIGEST_TRUST |
| [WEBAPP_FLAG_GLOSSARY](future_devs/WEBAPP_FLAG_GLOSSARY_SPEC.md) | Flag glossary & friendly labels | `not-started` | S | WEBAPP_DIGEST_TRUST |
| [WEBAPP_CADENCE_RUN_LIMIT_EXPLAINER](future_devs/WEBAPP_CADENCE_RUN_LIMIT_EXPLAINER_SPEC.md) | Cadence & run-limit explainer | `not-started` | S | WEBAPP_DIGEST_TRUST |
| [WEBAPP_DIAGNOSTIC_STATES](future_devs/WEBAPP_DIAGNOSTIC_STATES_SPEC.md) | Diagnostic empty states + scoring progress feedback | `not-started` | S | WEBAPP_DIGEST_TRUST |

### Epic: Job-seeker workspace

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [WEBAPP_JOBSEEKER_WORKFLOW](future_devs/WEBAPP_JOBSEEKER_WORKFLOW_SPEC.md) | Job-seeker workspace (epic root) | `not-started` | L | — |
| [WEBAPP_JOB_DETAIL_VIEW](future_devs/WEBAPP_JOB_DETAIL_VIEW_SPEC.md) | In-app job detail view (full reasoning + JD) | `not-started` | M | WEBAPP_FLAG_GLOSSARY |
| [WEBAPP_APPLICATION_TRACKER](future_devs/WEBAPP_APPLICATION_TRACKER_SPEC.md) | Application status tracker (saved/applied/interviewing/...) | `not-started` | M | WEBAPP_JOBSEEKER_WORKFLOW |
| [WEBAPP_HIDE_DISMISS_JOBS](future_devs/WEBAPP_HIDE_DISMISS_JOBS_SPEC.md) | Hide / dismiss irrelevant jobs | `not-started` | S | WEBAPP_JOBSEEKER_WORKFLOW |
| [WEBAPP_NEW_SINCE_LAST_VISIT](future_devs/WEBAPP_NEW_SINCE_LAST_VISIT_SPEC.md) | "New since last visit" badges + filter | `not-started` | S | WEBAPP_JOBSEEKER_WORKFLOW |
| [WEBAPP_DIGEST_SORT_PERSIST](future_devs/WEBAPP_DIGEST_SORT_PERSIST_SPEC.md) | Sort controls + persist filter/sort view + counts | `not-started` | S | WEBAPP_JOBSEEKER_WORKFLOW |

### Epic: App shell & account UX

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [WEBAPP_APP_SHELL_ACCOUNT](future_devs/archive/WEBAPP_APP_SHELL_ACCOUNT_SPEC.md) | App shell + account UX (epic root) | `wrapped` | M | — |
| [WEBAPP_GLOBAL_APP_SHELL_NAV](future_devs/archive/WEBAPP_GLOBAL_APP_SHELL_NAV_SPEC.md) | Global nav shell + sign-out + auth guard | `wrapped` | M | WEBAPP_APP_SHELL_ACCOUNT ✅ |
| [WEBAPP_GETTING_STARTED_CHECKLIST](future_devs/archive/WEBAPP_GETTING_STARTED_CHECKLIST_SPEC.md) | Getting-started checklist on the digest | `wrapped` | S | WEBAPP_APP_SHELL_ACCOUNT ✅ |
| [WEBAPP_IN_APP_HELP_FAQ](future_devs/archive/WEBAPP_IN_APP_HELP_FAQ_SPEC.md) | In-app Help / FAQ page | `wrapped` | S | WEBAPP_GLOBAL_APP_SHELL_NAV ✅ |
| [WEBAPP_AUTH_RESET_CONFIRM_LEGAL](future_devs/archive/WEBAPP_AUTH_RESET_CONFIRM_LEGAL_SPEC.md) | Auth: forgot-password + email-confirm + terms/privacy | `wrapped` | M | WEBAPP_APP_SHELL_ACCOUNT ✅ |

### Standalone

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [WEBAPP_ACCESSIBILITY_PASS](future_devs/WEBAPP_ACCESSIBILITY_PASS_SPEC.md) | Accessibility pass (color-blind-safe scores, focus, aria, keyboard) | `not-started` | S | — |

> Bug: [BUG_LANDING_DEAD_GITHUB_LINKS](bugs_to_fix/BUG_LANDING_DEAD_GITHUB_LINKS.md) — dead `href="#"` GitHub links on landing (filed in `bugs_to_fix/`).

---

## Phase P8 — Position liveness

Track open/closed liveness on the scored digest so postings taken down get marked `closed` and surfaced distinctly instead of sitting as live links that 404. The `new`/`seen` states already exist (`scored_at` recency + `_load_seen_keys` skip); only `closed` is missing.

### Epic: Position liveness

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [POSITION_LIVENESS](future_devs/archive/POSITION_LIVENESS_SPEC.md) | Position liveness (epic root) | `wrapped` | M | — |
| [POSITION_LIVENESS_LIVE_SET](future_devs/archive/POSITION_LIVENESS_LIVE_SET_SPEC.md) | Persist live `apply_url` set from successful pulls | `wrapped` | S | POSITION_LIVENESS ✅ |
| [POSITION_LIVENESS_STATUS_DIFF](future_devs/archive/POSITION_LIVENESS_STATUS_DIFF_SPEC.md) | Diff scored jobs vs live set → `status` + `closed_at` | `wrapped` | S | POSITION_LIVENESS_LIVE_SET ✅ |
| [POSITION_LIVENESS_DIGEST_RENDER](future_devs/archive/POSITION_LIVENESS_DIGEST_RENDER_SPEC.md) | Render closed jobs distinctly in `digest.md` | `wrapped` | S | POSITION_LIVENESS_STATUS_DIFF ✅ |
| [POSITION_LIVENESS_WEBAPP](future_devs/archive/POSITION_LIVENESS_WEBAPP_SPEC.md) | Reflect `status` in webapp digest API + cards | `wrapped` | S | POSITION_LIVENESS_STATUS_DIFF ✅ |

---

---

## Phase P9 — ATS expansion II

New ATS pullers for high-value companies currently stuck in `ats: other` or `ats: unknown`. Ordered by company impact.

| Slug | Title | Status | Effort | Depends on |
|---|---|---|---|---|
| [ATS_SMARTRECRUITERS](future_devs/ATS_SMARTRECRUITERS_SPEC.md) | SmartRecruiters puller - CyberArk + Palo Alto Networks | `completed` | S | — |
| [ATS_BAMBOOHR](future_devs/ATS_BAMBOOHR_SPEC.md) | BambooHR puller - Nilus + 4 others | `completed` | S | — |
| [ATS_CHECKPOINT_CAREERS](future_devs/ATS_CHECKPOINT_CAREERS_SPEC.md) | Check Point custom careers puller (single-tenant) | `completed` | S | — |
| [ATS_TALEO](future_devs/ATS_TALEO_SPEC.md) | Oracle Taleo puller - Radware | `completed` | M | — |
| [ATS_ORACLE_HCM](future_devs/ATS_ORACLE_HCM_SPEC.md) | Oracle HCM puller - Dell Technologies Israel | `completed` | M | — |

---

## Spec Index

| Spec | Domain |
|---|---|
| `future_devs/archive/WEBAPP_SUPABASE_SETUP_GUIDE_SPEC.md` | P2 post-launch — Supabase setup guide (wrapped) |
| `future_devs/WEBAPP_PDF_CV_UPLOAD_SPEC.md` | P2 post-launch — PDF CV upload in onboarding |
| `future_devs/WEBAPP_OLD_PROFILE_BADGE_SPEC.md` | P2 post-launch — "Scored with old profile" badge |
| `future_devs/archive/PROPRIETARY_ATS_PULLERS_SPEC.md` | P3 — Big-corp ATS pullers epic (wrapped) |
| `future_devs/archive/ATS_TALENTBREW_SPEC.md` | P3 — TalentBrew puller (Intuit) (wrapped) |
| `future_devs/archive/ATS_AMAZON_JOBS_SPEC.md` | P3 — amazon.jobs puller (AWS) (wrapped) |
| `future_devs/archive/ATS_MICROSOFT_CAREERS_SPEC.md` | P3 — Microsoft careers puller (wrapped) |
| `future_devs/archive/ATS_GOOGLE_CAREERS_SPEC.md` | P3 — Google careers puller (wrapped) |
| `future_devs/archive/ATS_EIGHTFOLD_SPEC.md` | P3 — Eightfold puller (PayPal) (wrapped) |
| `future_devs/archive/ATS_JOBVITE_SPEC.md` | P3 — Jobvite puller (Varonis) (wrapped) |
| `future_devs/archive/ATS_SUCCESSFACTORS_SPEC.md` | P3 — SuccessFactors puller (SAP) (wrapped) |
| `future_devs/archive/ATS_TEAMME_SPEC.md` | P3 — TeamMe puller (Claroty, QM) (wrapped) |
| `future_devs/archive/ATS_BREEZY_SPEC.md` | P3 — Breezy HR puller (Descope) (wrapped) |
| `future_devs/NEW_VC_ADAPTERS_SPEC.md` | P3 — Add VC adapters: State of Mind / Sequoia IL / Aleph / Lightspeed IL / Greylock / Insight IL |
| `future_devs/archive/TLV_PORTFOLIO_FIX_SPEC.md` | P3 — Fix TLV Partners scraper + clean stale entries (wrapped) |
| `future_devs/archive/BIG_COMPANIES_ATS_PARAMS_SPEC.md` | P3 — Fill ATS params for ~30 unfilled big_companies.yml stubs (wrapped) |
| `future_devs/PIPELINE_TEST_COVERAGE_SPEC.md` | P3 — Pipeline test suite |
| `future_devs/archive/VIOLA_GETRO_DEDUP_SPEC.md` | P1 — Deduplicate Viola Getro jobs before scoring (wrapped) |
| `future_devs/archive/RESCORE_EXISTING_SPEC.md` | P1 — Re-score stored jobs with updated profile (wrapped) |
| `future_devs/archive/GITHUB_ACTIONS_SCHEDULE_SPEC.md` | P1 — Automate collect + refresh with GitHub Actions (wrapped) |
| `future_devs/archive/WEBAPP_SCAFFOLD_SPEC.md` | P2 — Project scaffold + Supabase schema (wrapped) |
| `future_devs/archive/WEBAPP_AUTH_SPEC.md` | P2 — Auth: email + Google OAuth (wrapped) |
| `future_devs/archive/WEBAPP_SCORING_ENDPOINT_SPEC.md` | P2 — Scoring API endpoint per user (wrapped) |
| `future_devs/archive/WEBAPP_LANDING_SPEC.md` | P2 — Landing page (wrapped) |
| `future_devs/archive/WEBAPP_ACTIONS_WIRING_SPEC.md` | P2 — GitHub Actions cron wiring (wrapped) |
| `future_devs/archive/WEBAPP_DEPLOY_SPEC.md` | P2 — Render.com deployment (wrapped) |
| `future_devs/archive/WEBAPP_ONBOARDING_SPEC.md` | P2 — Onboarding flow (4 steps) (wrapped) |
| `future_devs/archive/WEBAPP_DIGEST_SPEC.md` | P2 — Digest view with score cards (wrapped) |
| `future_devs/archive/WEBAPP_SETTINGS_SPEC.md` | P2 — Settings tabs (wrapped) |
| `future_devs/archive/DS_ANALYSIS_NOTEBOOK_SPEC.md` | P4 — DS analysis notebook (wrapped) |
| `future_devs/archive/REPO_SHOWCASE_SPEC.md` | P4 — README rewrite / engineering showcase (wrapped) |
| `future_devs/SCORING_RUBRIC_ABLATION_SPEC.md` | P4 — Scoring calibration doc |
| `future_devs/archive/WEBAPP_FAVICON_SPEC.md` | P5 — Website favicon + Open Graph (wrapped) |
| `future_devs/archive/WEBAPP_CV_SETTINGS_UPLOAD_SPEC.md` | P5 — CV re-upload in Settings (wrapped) |
| `future_devs/WEBAPP_CV_UPLOAD_FORMATS_SPEC.md` | P5 — CV upload: DOCX + TXT support alongside PDF |
| `future_devs/WEBAPP_SETTINGS_STATE_VISIBILITY_SPEC.md` | P5 — Settings reflects current state (CV, filters, API-key status, account identity) |
| `future_devs/WEBAPP_PROFILE_UPLOAD_OR_PROMPT_SPEC.md` | P5 — Profile upload or AI prompt generator |
| `future_devs/archive/WEBAPP_COMPANIES_VIEW_SPEC.md` | P5 — Companies page (wrapped) |
| `future_devs/archive/WEBAPP_COUNTUP_ANIMATION_SPEC.md` | P5 — Count-up animation on Companies + Positions page load (wrapped) |
| `future_devs/archive/WEBAPP_POSITIONS_VIEW_SPEC.md` | P5 — Positions page (wrapped) |
| `future_devs/archive/WEBAPP_MULTI_FILTER_SPEC.md` | P5 — Multi-value filters with ';' (wrapped) |
| `future_devs/archive/PROFILE_CV_GAP_ANALYSIS_SPEC.md` | P5 — Gap analysis: profile vs CV, positions vs CV (wrapped) |
| `future_devs/POSITION_FIRST_SEEN_SPEC.md` | P5 — Stamp first_seen date on each position; show in digest + webapp |
| `future_devs/RAG_CHATBOT_SPEC.md` | P6 — RAG sandbox + chat UI (next AI epic) |
| `future_devs/MULTI_AGENT_RESUME_TAILOR_SPEC.md` | P6 — Multi-agent CV tailor |
| `future_devs/WEBAPP_FIRST_RUN_COMPREHENSION_SPEC.md` | P7 — First-run comprehension (epic root) |
| `future_devs/WEBAPP_LANDING_REVAMP_SPEC.md` | P7 — Landing revamp (value prop, BYO-key, digest preview, FAQ) |
| `future_devs/WEBAPP_ONBOARDING_ORIENTATION_SPEC.md` | P7 — Onboarding orientation + setup summary |
| `future_devs/WEBAPP_PROFILE_EXAMPLE_GUIDANCE_SPEC.md` | P7 — Profile example + section guidance |
| `future_devs/WEBAPP_FILTER_PLAIN_LANGUAGE_PREVIEW_SPEC.md` | P7 — Plain-language filters + live preview |
| `future_devs/WEBAPP_ONBOARDING_KEY_TEST_SPEC.md` | P7 — Inline key test in onboarding |
| `future_devs/WEBAPP_DIGEST_TRUST_SPEC.md` | P7 — Digest legibility & trust (epic root) |
| `future_devs/WEBAPP_SCORE_LEGEND_SPEC.md` | P7 — Score legend & tier explainer |
| `future_devs/WEBAPP_FLAG_GLOSSARY_SPEC.md` | P7 — Flag glossary & friendly labels |
| `future_devs/WEBAPP_CADENCE_RUN_LIMIT_EXPLAINER_SPEC.md` | P7 — Cadence & run-limit explainer |
| `future_devs/WEBAPP_DIAGNOSTIC_STATES_SPEC.md` | P7 — Diagnostic empty & progress states |
| `future_devs/WEBAPP_JOBSEEKER_WORKFLOW_SPEC.md` | P7 — Job-seeker workspace (epic root) |
| `future_devs/WEBAPP_JOB_DETAIL_VIEW_SPEC.md` | P7 — In-app job detail view |
| `future_devs/WEBAPP_APPLICATION_TRACKER_SPEC.md` | P7 — Application status tracker |
| `future_devs/WEBAPP_HIDE_DISMISS_JOBS_SPEC.md` | P7 — Hide / dismiss jobs |
| `future_devs/WEBAPP_NEW_SINCE_LAST_VISIT_SPEC.md` | P7 — New-since-last-visit badges |
| `future_devs/WEBAPP_DIGEST_SORT_PERSIST_SPEC.md` | P7 — Digest sort + persist view |
| `future_devs/archive/WEBAPP_APP_SHELL_ACCOUNT_SPEC.md` | P7 — App shell + account UX (epic root, wrapped) |
| `future_devs/archive/WEBAPP_GLOBAL_APP_SHELL_NAV_SPEC.md` | P7 — Global app shell + nav + sign-out (wrapped) |
| `future_devs/archive/WEBAPP_GETTING_STARTED_CHECKLIST_SPEC.md` | P7 — Getting-started checklist (wrapped) |
| `future_devs/archive/WEBAPP_IN_APP_HELP_FAQ_SPEC.md` | P7 — In-app Help / FAQ page (wrapped) |
| `future_devs/archive/WEBAPP_AUTH_RESET_CONFIRM_LEGAL_SPEC.md` | P7 — Auth reset / confirm / legal (wrapped) |
| `future_devs/WEBAPP_ACCESSIBILITY_PASS_SPEC.md` | P7 — Accessibility pass |
| `future_devs/archive/POSITION_LIVENESS_SPEC.md` | P8 — Position liveness (epic root, wrapped) |
| `future_devs/archive/POSITION_LIVENESS_LIVE_SET_SPEC.md` | P8 — Persist live apply_url set from successful pulls (wrapped) |
| `future_devs/archive/POSITION_LIVENESS_STATUS_DIFF_SPEC.md` | P8 — Status diff: scored jobs vs live set (wrapped) |
| `future_devs/archive/POSITION_LIVENESS_DIGEST_RENDER_SPEC.md` | P8 — Render closed jobs in digest.md (wrapped) |
| `future_devs/archive/POSITION_LIVENESS_WEBAPP_SPEC.md` | P8 — Reflect status in webapp digest (wrapped) |
| `future_devs/ATS_SMARTRECRUITERS_SPEC.md` | P9 — SmartRecruiters puller (CyberArk + PAN) |
| `future_devs/ATS_BAMBOOHR_SPEC.md` | P9 — BambooHR puller (Nilus + 4 others) |
| `future_devs/ATS_CHECKPOINT_CAREERS_SPEC.md` | P9 — Check Point custom careers (single-tenant) |
| `future_devs/ATS_TALEO_SPEC.md` | P9 — Oracle Taleo puller (Radware) |
| `future_devs/ATS_ORACLE_HCM_SPEC.md` | P9 — Oracle HCM puller (Dell Technologies Israel) |
