| Field | Value |
|---|---|
| **Phase** | P8 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | POSITION_LIVENESS |
| **Depends on** | POSITION_LIVENESS_STATUS_DIFF |
| **Blocks** | — |
| **Touches** | `webapp/backend/routers/jobs.py`, webapp frontend digest card |
| **Spec files to update** | `WEBAPP_SPEC.md` |

## Overview

**What:** Surface the `status` / `closed_at` fields from `scored_jobs.json` through the webapp digest API and reflect them in the digest cards, mirroring the `digest.md` treatment.

**Why:** The webapp reads the same per-profile `scored_jobs.json` store. Once child 2 stamps `status`, the webapp should not show closed roles as live application links either — same dead-link friction, different surface.

## Behaviour

- **Backend (`jobs.py`):** include `status` and `closed_at` in the serialized job objects returned by the digest endpoint. Default missing `status` to `open` for backward compatibility with stores written before this epic.
- **Frontend digest card:** for `status: closed` jobs, apply a muted/strikethrough treatment, show a `Closed YYYY-MM-DD` badge, and either move them to a collapsed "Recently closed" group or visually de-emphasize in place. Consistent with the `digest.md` rendering in `POSITION_LIVENESS_DIGEST_RENDER`.
- Do not break existing filter/sort behaviour; closed status is additive metadata.
- This child is optional/independent of the markdown digest child — both consume the same `status` field from child 2.

## Files to Touch

- `webapp/backend/routers/jobs.py` — pass through `status` + `closed_at`.
- webapp frontend digest card component — closed-state styling + optional grouping.

## How to QA

1. With a `status: closed` job in a profile's `scored_jobs.json`, load the webapp digest; confirm the API response includes `status`/`closed_at` and the card renders the closed treatment.
2. Open jobs render unchanged.
3. A pre-epic store (no `status` field) still loads, all jobs treated as `open`.
4. Filters/sorts still work with closed jobs present.
