| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/digest/page.tsx`, `webapp/frontend/app/positions/page.tsx` |

## Overview

Filter inputs currently accept a single value. Users need to filter by multiple values at once (e.g. several job titles or multiple companies). Adding `;`-separated multi-value support and example placeholder text makes filters more powerful and self-documenting.

## Behaviour

### Multi-value parsing

- Any filter input that accepts text now splits on `;` and treats each segment as an OR condition.
- Whitespace around `;` is trimmed. `Senior DS; Lead ML; Applied Scientist` matches any of the three.
- A single value (no `;`) behaves exactly as before — no regression.
- Empty segments (double `;`, trailing `;`) are silently ignored.

### Placeholder text

Each filter box shows a placeholder that demonstrates the `;` syntax with a realistic example:

| Filter box | Placeholder example |
|---|---|
| Job title | `e.g. Data Scientist; Machine Learning; Applied Scientist` |
| Company | `e.g. Wiz; CrowdStrike; Palo Alto` |
| Location | `e.g. Tel Aviv; Herzliya; Remote` |
| Category | `e.g. cyber; fraud; fintech` |

Placeholders disappear when the user starts typing (standard HTML `placeholder` attribute behaviour).

### Applies to

- Digest page — existing title/company filters updated.
- Positions page (`WEBAPP_POSITIONS_VIEW`) — search input follows the same multi-value rule.

## Files to Touch

- `webapp/frontend/app/digest/page.tsx` — update filter inputs to split on `;` + add placeholder text
- `webapp/frontend/app/positions/page.tsx` — same (coordinate with `WEBAPP_POSITIONS_VIEW`)

## How to QA

1. On Digest, enter `Senior; Lead` in the title filter — only jobs matching either term are shown.
2. Trailing semicolon `Senior;` — no blank match; behaves as single-value `Senior`.
3. Single value with no `;` — results unchanged from current behaviour.
4. All filter boxes display their placeholder text when empty.
5. On Positions page, same `;` multi-value filtering works.
6. `uv run python3 -m pytest tests/ -v` passes.
7. `uv run python score.py --dry-run` passes.
