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

No active epics. See `ROADMAP_ARCHIVE.md`.

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
| [PROPRIETARY_ATS_PULLERS](future_devs/PROPRIETARY_ATS_PULLERS_SPEC.md) **(epic)** | Pullers for Intuit/AWS/Microsoft/Google/PayPal/Varonis/CyberArk/SAP/Claroty/QM/Descope | `completed` | L | — |
| ├─ [ATS_TALENTBREW](future_devs/ATS_TALENTBREW_SPEC.md) | TalentBrew puller → Intuit | `completed` | XS | — |
| ├─ [ATS_AMAZON_JOBS](future_devs/ATS_AMAZON_JOBS_SPEC.md) | amazon.jobs puller → AWS Israel | `completed` | S | — |
| ├─ [ATS_MICROSOFT_CAREERS](future_devs/ATS_MICROSOFT_CAREERS_SPEC.md) | careers.microsoft.com puller → Microsoft Israel | `completed` | S | — |
| ├─ [ATS_GOOGLE_CAREERS](future_devs/ATS_GOOGLE_CAREERS_SPEC.md) | careers.google.com puller → Google Israel | `completed` | S | — |
| ├─ [ATS_EIGHTFOLD](future_devs/ATS_EIGHTFOLD_SPEC.md) | Eightfold puller → PayPal Israel | `completed` | S | — |
| ├─ [ATS_JOBVITE](future_devs/ATS_JOBVITE_SPEC.md) | Jobvite puller → Varonis | `completed` | S | — |
| ├─ [ATS_SUCCESSFACTORS](future_devs/ATS_SUCCESSFACTORS_SPEC.md) | SuccessFactors puller → SAP (CyberArk now on SmartRecruiters via PAN) | `completed` | M | — |
| ├─ [ATS_TEAMME](future_devs/ATS_TEAMME_SPEC.md) | TeamMe puller → Claroty, Quantum Machines | `completed` | M | — |
| └─ [ATS_BREEZY](future_devs/ATS_BREEZY_SPEC.md) | Breezy HR puller → Descope | `completed` | XS | — |
| [NEW_VC_ADAPTERS](future_devs/NEW_VC_ADAPTERS_SPEC.md) | Add VC adapters: State of Mind / Sequoia IL / Aleph / Lightspeed IL / Greylock / Insight IL | `in-progress` | M | — |
| [TLV_PORTFOLIO_FIX](future_devs/TLV_PORTFOLIO_FIX_SPEC.md) | Fix TLV Partners scraper + clean stale entries + add missing portfolio companies | `completed` | M | — |
| [BIG_COMPANIES_ATS_PARAMS](future_devs/BIG_COMPANIES_ATS_PARAMS_SPEC.md) | Fill ATS params for ~30 unfilled big_companies.yml stubs | `not-started` | M | — |
| [PIPELINE_TEST_COVERAGE](future_devs/archive/PIPELINE_TEST_COVERAGE_SPEC.md) | Add test suite for pipeline scripts (ATS pullers, filters, scorer parser) | `wrapped` | M | — |

---

## Spec Index

| Spec | Domain |
|---|---|
| `future_devs/archive/WEBAPP_SUPABASE_SETUP_GUIDE_SPEC.md` | P2 post-launch — Supabase setup guide (wrapped) |
| `future_devs/WEBAPP_PDF_CV_UPLOAD_SPEC.md` | P2 post-launch — PDF CV upload in onboarding |
| `future_devs/WEBAPP_OLD_PROFILE_BADGE_SPEC.md` | P2 post-launch — "Scored with old profile" badge |
| `future_devs/PROPRIETARY_ATS_PULLERS_SPEC.md` | P3 — Big-corp ATS pullers epic |
| `future_devs/ATS_TALENTBREW_SPEC.md` | P3 — TalentBrew puller (Intuit) |
| `future_devs/ATS_AMAZON_JOBS_SPEC.md` | P3 — amazon.jobs puller (AWS) |
| `future_devs/ATS_MICROSOFT_CAREERS_SPEC.md` | P3 — Microsoft careers puller |
| `future_devs/ATS_GOOGLE_CAREERS_SPEC.md` | P3 — Google careers puller |
| `future_devs/ATS_EIGHTFOLD_SPEC.md` | P3 — Eightfold puller (PayPal) |
| `future_devs/ATS_JOBVITE_SPEC.md` | P3 — Jobvite puller (Varonis) |
| `future_devs/ATS_SUCCESSFACTORS_SPEC.md` | P3 — SuccessFactors puller (CyberArk, SAP) |
| `future_devs/ATS_TEAMME_SPEC.md` | P3 — TeamMe puller (Claroty, QM) |
| `future_devs/ATS_BREEZY_SPEC.md` | P3 — Breezy HR puller (Descope) |
| `future_devs/NEW_VC_ADAPTERS_SPEC.md` | P3 — Add VC adapters: State of Mind / Sequoia IL / Aleph / Lightspeed IL / Greylock / Insight IL |
| `future_devs/TLV_PORTFOLIO_FIX_SPEC.md` | P3 — Fix TLV Partners scraper + clean stale entries + add missing portfolio companies |
| `future_devs/BIG_COMPANIES_ATS_PARAMS_SPEC.md` | P3 — Fill ATS params for ~30 unfilled big_companies.yml stubs |
| `future_devs/PIPELINE_TEST_COVERAGE_SPEC.md` | P3 — Pipeline test suite |
| `future_devs/VIOLA_GETRO_DEDUP_SPEC.md` | P1 — Deduplicate Viola Getro jobs before scoring |
| `future_devs/RESCORE_EXISTING_SPEC.md` | P1 — Re-score stored jobs with updated profile |
| `future_devs/GITHUB_ACTIONS_SCHEDULE_SPEC.md` | P1 — Automate collect + refresh with GitHub Actions |
| `future_devs/archive/WEBAPP_SCAFFOLD_SPEC.md` | P2 — Project scaffold + Supabase schema (wrapped) |
| `future_devs/archive/WEBAPP_AUTH_SPEC.md` | P2 — Auth: email + Google OAuth (wrapped) |
| `future_devs/archive/WEBAPP_SCORING_ENDPOINT_SPEC.md` | P2 — Scoring API endpoint per user (wrapped) |
| `future_devs/archive/WEBAPP_LANDING_SPEC.md` | P2 — Landing page (wrapped) |
| `future_devs/archive/WEBAPP_ACTIONS_WIRING_SPEC.md` | P2 — GitHub Actions cron wiring (wrapped) |
| `future_devs/archive/WEBAPP_DEPLOY_SPEC.md` | P2 — Render.com deployment (wrapped) |
| `future_devs/archive/WEBAPP_ONBOARDING_SPEC.md` | P2 — Onboarding flow (4 steps) (wrapped) |
| `future_devs/archive/WEBAPP_DIGEST_SPEC.md` | P2 — Digest view with score cards (wrapped) |
| `future_devs/archive/WEBAPP_SETTINGS_SPEC.md` | P2 — Settings tabs (wrapped) |
