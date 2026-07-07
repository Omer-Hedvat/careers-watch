| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `wrapped` |
| **Effort** | S |
| **Epic** | — |
| **Depends on** | [WEBAPP_POSITIONS_VIEW](archive/WEBAPP_POSITIONS_VIEW_SPEC.md) ✅ |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/(app)/positions/page.tsx`, `webapp/frontend/app/components/DetailPanel.tsx` (new shared slide-over shell), `webapp/frontend/app/(app)/digest/page.tsx` (refactor `JobDetailPanel` onto the shared shell) |
| **Spec files to update** | `CLAUDE.md` (WEBAPP_SPEC.md if positions surface documented there) |

## Overview

On the Positions page, clicking a position row navigates straight out to the external ATS posting in a new tab (`positions/page.tsx:108`, a bare `<a href={apply_url} target="_blank">`). There is no way to read the position's details inside CareerWatch first.

The Digest page already solved this: clicking a card opens an in-app `JobDetailPanel` slide-over (full reasoning, flags + glossary, full JD) with an **Apply →** link out to the posting (`(app)/digest/page.tsx:155`, `:207`). This task brings the same in-app-detail-then-link-out behaviour to the Positions page so the two surfaces are consistent.

## Behaviour

- Clicking a position row opens an in-app detail view (slide-over panel) showing the position's details, instead of immediately leaving the app.
- The detail view contains a clear link (**Apply →** / "Go to posting") to the position's original page, opening in a new tab (`target="_blank" rel="noopener noreferrer"`).
- Reuse the existing `JobDetailPanel` pattern/component from the Digest page rather than building a second one. Extract it to a shared component if it is currently local to `digest/page.tsx`.
- The Positions catalog may carry less per-position data than scored jobs (no per-user reasoning/score). Show whatever the positions payload provides (title, company, location, first_seen, status) and the full description if available; degrade gracefully when a field is absent — mirror the digest panel's "Full description unavailable - open the posting" fallback with the Apply link still active.
- Closed positions: preserve current behaviour — a closed position is dimmed and non-interactive (`isClosed` → `pointer-events-none`), so it does not open the detail view.
- A position with no `apply_url` shows the detail view (if opened) but with the Apply link disabled/absent, consistent with the current dimmed-row treatment.

## Files to Touch

- `webapp/frontend/app/(app)/positions/page.tsx` — replace the direct external `<a>` row with a click handler that opens the detail panel; render the panel with an Apply link out.
- `webapp/frontend/app/(app)/digest/page.tsx` — only if `JobDetailPanel` is extracted to a shared component (e.g. `app/components/JobDetailPanel.tsx`); update the import.
- Backend: only if the positions payload must expose the full description for the panel and does not already (`webapp/backend/routers/*`). Confirm before adding — the graceful fallback means this is optional.

## How to QA

1. On the Positions page, clicking a live position opens an in-app detail view (does NOT immediately navigate away).
2. The detail view shows the position's available details and a working link to the original posting that opens in a new tab.
3. A position with no stored description still opens without error and shows the graceful fallback with the Apply link.
4. A closed position remains dimmed and does not open the detail view.
5. The Digest page's existing detail view still works unchanged (no regression from any shared-component extraction).
6. `uv run python3 -m pytest tests/ -v` passes.
7. `uv run python score.py --dry-run` passes.
