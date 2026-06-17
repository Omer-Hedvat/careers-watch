# WEBAPP_SCORE_LEGEND

| Field | Value |
|---|---|
| **Phase** | P7 |
| **Status** | `not-started` |
| **Effort** | S |
| **Epic** | WEBAPP_DIGEST_TRUST |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | webapp/frontend/app/digest/page.tsx |

## Overview

Job cards show a score 0-10 with a colored badge (green >=9, blue >=7, gray otherwise), but there is no legend anywhere on the digest. A first-time user does not know what "good" is, where the cutoffs are, or what the colors mean. This adds a lightweight, always-available explanation of the scoring tiers.

## Behaviour

- Add a compact inline score key on the digest (near the filters/header) showing the tier bands and their colors, matching the colors already used on the badges:
  - 9-10 (green): reach out today
  - 7-8 (blue): strong, worth a look
  - 5-6 (gray): adjacent
  - below 5 (not surfaced)
- Add an expandable "How scoring works" popover that explains the bands in one short paragraph each. Keep it lightweight - not a wall of text.
- Hovering a score badge on any job card shows a tooltip with that badge's band meaning (e.g. hovering a 9 shows "reach out today").
- Copy and colors must match the existing badge tiers in `digest/page.tsx` - do not introduce new thresholds or colors.

## Files to Touch

- webapp/frontend/app/digest/page.tsx

## How to QA

1. Load the digest: a compact score legend is visible without any interaction.
2. Click "How scoring works": a popover explains the four bands concisely.
3. Hover a score badge on a job card: a tooltip shows that band's meaning.
4. Confirm the legend colors (green/blue/gray) and thresholds match the existing badge logic.
5. `uv run python3 -m pytest tests/ -v` passes and `uv run python score.py --dry-run` passes.
