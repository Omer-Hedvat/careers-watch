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

| Epic | Spec | Phase | Status | Rollup | Children |
|---|---|---|---|---|---|
| Web App v1 | `WEBAPP_SPEC.md` | P2 | `in-progress` | 1 wrapped · 0 completed · 0 in-progress · 8 not-started | 9 |

---

## Phase P0 — Pipeline (complete)

All Phase P0 tasks are wrapped. See `ROADMAP_ARCHIVE.md`.

---

## Phase P1 — Pipeline improvements

| Feature | Spec | Effort | Status | Depends on |
|---|---|---|---|---|
| Fix Viola Getro duplicate jobs — dedupe by apply_url before scoring | `future_devs/VIOLA_GETRO_DEDUP_SPEC.md` | S | `wrapped` | — |
| Rescore existing digest with updated profile | `future_devs/RESCORE_EXISTING_SPEC.md` | S | `wrapped` | — |
| Scheduled automation via GitHub Actions (collect Mon/Thu, refresh biweekly) | `future_devs/GITHUB_ACTIONS_SCHEDULE_SPEC.md` | S | `wrapped` | — |

---

## Phase P2 — Web App v1

Read `WEBAPP_SPEC.md` before starting any task in this phase.

| Feature | Spec | Effort | Status | Depends on |
|---|---|---|---|---|
| [webapp] Auth — email + Google OAuth, session management | `future_devs/WEBAPP_AUTH_SPEC.md` | S | `not-started` | webapp_scaffold ✅ |
| [webapp] Onboarding — profile prompt generator, CV upload, Gemini key, filters | `future_devs/WEBAPP_ONBOARDING_SPEC.md` | M | `not-started` | webapp_auth |
| [webapp] Digest view — ranked cards, applied toggle, score filter | `future_devs/WEBAPP_DIGEST_SPEC.md` | M | `not-started` | webapp_onboarding |
| [webapp] Scoring endpoint — runs score.py per user, rate-limited 2x/week | `future_devs/WEBAPP_SCORING_ENDPOINT_SPEC.md` | M | `not-started` | webapp_scaffold ✅ |
| [webapp] Settings — profile, CV, filters, API key, account tabs | `future_devs/WEBAPP_SETTINGS_SPEC.md` | S | `not-started` | webapp_digest |
| [webapp] Landing page — value prop, how it works, CTA | `future_devs/WEBAPP_LANDING_SPEC.md` | S | `not-started` | webapp_scaffold ✅ |
| [webapp] GitHub Actions wiring — scheduled collect + refresh commit to repo | `future_devs/WEBAPP_ACTIONS_WIRING_SPEC.md` | S | `not-started` | webapp_scaffold ✅ |
| [webapp] Render.com deploy — FastAPI + Next.js, persistent disk, env vars | `future_devs/WEBAPP_DEPLOY_SPEC.md` | S | `not-started` | webapp_scaffold ✅ |

---

## Spec Index

| Spec | Domain |
|---|---|
| `WEBAPP_SPEC.md` | Product spec for the web app |
| `future_devs/VIOLA_GETRO_DEDUP_SPEC.md` | P1 — Deduplicate Viola Getro jobs before scoring |
| `future_devs/RESCORE_EXISTING_SPEC.md` | P1 — Re-score stored jobs with updated profile |
| `future_devs/GITHUB_ACTIONS_SCHEDULE_SPEC.md` | P1 — Automate collect + refresh with GitHub Actions |
| `future_devs/archive/WEBAPP_SCAFFOLD_SPEC.md` | P2 — Project scaffold + Supabase schema (wrapped) |
| `future_devs/WEBAPP_AUTH_SPEC.md` | P2 — Auth: email + Google OAuth |
| `future_devs/WEBAPP_ONBOARDING_SPEC.md` | P2 — Onboarding flow (4 steps) |
| `future_devs/WEBAPP_DIGEST_SPEC.md` | P2 — Digest view with score cards |
| `future_devs/WEBAPP_SCORING_ENDPOINT_SPEC.md` | P2 — Scoring API endpoint per user |
| `future_devs/WEBAPP_SETTINGS_SPEC.md` | P2 — Settings tabs |
| `future_devs/WEBAPP_LANDING_SPEC.md` | P2 — Landing page |
| `future_devs/WEBAPP_ACTIONS_WIRING_SPEC.md` | P2 — GitHub Actions cron wiring |
| `future_devs/WEBAPP_DEPLOY_SPEC.md` | P2 — Render.com deployment |
