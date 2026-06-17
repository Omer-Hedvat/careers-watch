| Field | Value |
|---|---|
| **Phase** | P5 |
| **Status** | `wrapped` |
| **Effort** | XS |
| **Epic** | — |
| **Depends on** | — |
| **Blocks** | — |
| **Touches** | `webapp/frontend/app/layout.tsx`, `webapp/frontend/public/` |

## Overview

The webapp currently has no favicon or app icon, so browser tabs show a blank page icon. Add a simple favicon and Open Graph image so the app looks intentional in tabs, bookmarks, and link previews.

## Behaviour

- Favicon: a simple icon appropriate for a job-search tool (e.g. a briefcase or magnifying glass). SVG preferred; fall back to PNG at 32×32 and 192×192.
- The `<head>` in `layout.tsx` references the favicon via Next.js metadata or a `<link rel="icon">` tag.
- Open Graph meta tags (title: "CareerWatch", description one-liner) added to `layout.tsx` for link previews.
- No external icon font dependencies — inline SVG or a static asset only.

## Files to Touch

- `webapp/frontend/public/favicon.svg` (or `.ico`) — new icon asset
- `webapp/frontend/app/layout.tsx` — add `<link rel="icon">` or Next.js `metadata.icons`

## How to QA

1. Run the dev server — browser tab shows the favicon (not blank).
2. Inspect `<head>` in browser DevTools — `<link rel="icon">` is present and resolves to a non-404 asset.
3. Check Open Graph tags are present in `<head>`.
4. `uv run python3 -m pytest tests/ -v` passes.
5. `uv run python score.py --dry-run` passes.
