# WEBAPP_DIGEST_TRUST

| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | M |
| **Epic** | WEBAPP_DIGEST_TRUST (epic root) |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/digest/page.tsx, webapp/backend/routers/ |

## Overview

The digest shows numbers, colored badges, raw flag slugs (e.g. `tier1-vc`, `location-unclear`), a rate-limited "Score now" button, and bare empty/loading states with no explanation. A first-time user cannot interpret a score, does not know what flags mean, does not understand the weekly run limit or when new jobs arrive, and cannot tell why the digest is empty.

This epic groups the work that makes the digest legible and trustworthy: a user should be able to read a score, decode a flag, understand the cadence and run limit, and know why the digest is empty when it is.

## Behaviour

This epic has four children:

- **WEBAPP_SCORE_LEGEND** — Score legend: inline score key + "How scoring works" popover for the tier bands (9-10, 7-8, 5-6, below 5), plus per-badge hover tooltips.
- **WEBAPP_FLAG_GLOSSARY** — Flag glossary: map raw flag slugs to human-readable labels + tooltip definitions, with a glossary popover listing all known flags. The glossary is reused by the job detail view in the Job-Seeker Workflow epic (this child blocks `WEBAPP_JOB_DETAIL_VIEW`).
- **WEBAPP_CADENCE_RUN_LIMIT_EXPLAINER** — Cadence & run-limit explainer: explain what "Score now" does, the weekly run cap and reset timing, and surface the data-collection cadence in the header.
- **WEBAPP_DIAGNOSTIC_STATES** — Diagnostic + progress states: empty states keyed on account state (no profile / no key / not scored / filtered out), scoring-in-progress feedback with a result count, and loading skeletons.

## Files to Touch

- webapp/frontend/app/digest/page.tsx
- webapp/backend/routers/ (user.py, jobs.py, scoring.py as needed by children)

## How to QA

1. Each child task's QA passes (see WEBAPP_SCORE_LEGEND, WEBAPP_FLAG_GLOSSARY, WEBAPP_CADENCE_RUN_LIMIT_EXPLAINER, WEBAPP_DIAGNOSTIC_STATES).
2. A first-time user can explain what a score means (which band is "good"), what a flag means (e.g. `tier1-vc`), and why the digest is empty or run-limited - without reading the source.
3. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
