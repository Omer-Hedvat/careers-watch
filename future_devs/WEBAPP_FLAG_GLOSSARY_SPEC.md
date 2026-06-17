# WEBAPP_FLAG_GLOSSARY

| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | WEBAPP_DIGEST_TRUST |
| **Depends on** | — |
| **Blocks** | WEBAPP_JOB_DETAIL_VIEW |
| **Touches** | webapp/frontend/app/digest/page.tsx |

## Overview

Each job card renders its flags as raw slugs (e.g. `tier1-vc`, `location-unclear`, `lead-path-implied`) with no meaning. A user cannot tell whether a flag is a positive signal, a caveat, or a dealbreaker. This maps known flags to human-readable labels with tooltip definitions and adds a glossary popover. The label/tooltip mapping is reused by the job detail view (`WEBAPP_JOB_DETAIL_VIEW`).

## Behaviour

- Map each known flag slug to a friendly label plus a one-line tooltip definition. Unknown flags fall back to a prettified label (slug split on `-`, Title Cased) and no tooltip.
- Render the friendly label on the flag tag; show the definition on hover (tooltip).
- Add a small "What do these tags mean?" link near the flags (or in the header) that opens a glossary popover listing all known flags with their definitions.
- Keep the slug -> label/definition map in a single shared module so the job detail view can import it (do not duplicate).

### Canonical flag set

Flags are produced by the Gemini scorer (`matcher/gemini_scorer.py`) as a free-form `flags` list per job; the prompt seeds the model with example flags (around lines 73 and 173). They are persisted onto each job (`score.py`, e.g. line 455) and surfaced in the digest. The model may emit flags outside this set, so the unknown-flag fallback is required, not optional.

Known flags to map (derive labels from the scorer's intent):

| Slug | Friendly label | Definition |
|---|---|---|
| `tier1-vc` | Top-tier cyber VC | Backed by a top-tier cyber VC |
| `location-unclear` | Location unclear | Location not stated in the posting |
| `dealbreaker-location` | Out of commute range | Location is outside the commute radius |
| `lead-path-implied` | Lead path implied | Posting implies a path to a lead role |
| `management-gap` | Management gap | Requires more people-management than the profile shows |
| `wrong-domain` | Wrong domain | Domain is outside fraud/cyber/security focus |
| `title-laundering` | Title mismatch | Title oversells the actual scope of the role |
| `llm-not-security` | LLM, not security | LLM/GenAI role without a security or fraud focus |
| `scorer-error` | Scoring error | The scorer failed on this job; treat with caution |

(Verify the exact slugs against `matcher/gemini_scorer.py` at implementation time and extend the map if the prompt examples have changed.)

## Files to Touch

- webapp/frontend/app/digest/page.tsx (plus a small shared flags map module, e.g. webapp/frontend/lib/flags.ts, importable by the future job detail view)

## How to QA

1. A job with `tier1-vc` shows the friendly label "Top-tier cyber VC" and a tooltip definition on hover.
2. Click "What do these tags mean?": the glossary popover lists all known flags with definitions.
3. A job with an unknown flag (e.g. a slug not in the map) still renders a readable Title-Cased label.
4. The slug map lives in a shared module so the job detail view can reuse it.
5. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
