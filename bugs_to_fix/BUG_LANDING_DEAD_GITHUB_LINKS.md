# BUG: Landing page GitHub links are dead (href="#")

## Status
🟢 Completed

## Severity
P3

## Description
On the public landing page (webapp/frontend/app/landing/page.tsx) the hero "View on GitHub" button and the footer "GitHub" link both use href="#", so they go nowhere. A first-time visitor who wants to inspect the project (a key trust signal for a tool that asks for a CV and an API key) hits a dead link.

## Steps to Reproduce
1. Open /landing
2. Click "View on GitHub" (hero) or the footer "GitHub" link
3. Expected: opens the project's GitHub repo in a new tab | Actual: nothing happens (href="#")

## Dependencies
- **Depends on:** —
- **Blocks:** —
- **Touches:** webapp/frontend/app/landing/page.tsx
- **Spec files to update:** — (note: WEBAPP_LANDING_REVAMP also fixes this as part of a larger revamp; this bug exists so it can be fixed immediately and independently)

## Fix Notes
<!-- populated after fix -->
Point both links at the repo URL with target="_blank" rel="noopener noreferrer".
