# BUG: Settings Filters look empty while loading, and Save can wipe saved filters

## Status
🟢 Completed

## Severity
P1

## Description
Settings - Filters fetched `/user/filters` with no loading or error state. While the
free-plan backend woke up (or if the call failed) the tab showed empty fields, which a user
reported as "all my filters are missing" although score_configs still held them. Worse,
clicking Save in that state PATCHed empty filters over the real ones. Onboarding had the
same hole: if saved filters failed to load, finishing the wizard saved its defaults.

## Steps to Reproduce
1. User with saved filters; backend cold or `/user/filters` failing.
2. Open Settings - Filters.
3. Expected: a loading/error state, saved filters untouched | Actual: empty fields; Save overwrites.

## Dependencies
- **Depends on:** —
- **Blocks:** —
- **Touches:** webapp/frontend/app/(app)/settings/page.tsx, webapp/frontend/app/onboarding/page.tsx
- **Spec files to update:** —

## Fix Notes
Settings: `filtersState` (loading/ok/error). The tab shows the waking-up box while loading,
an error with Retry on failure ("they are still saved"), and the form only when loaded;
Save is disabled and guarded unless loaded. Onboarding: if saved filters exist but failed to
load, the final step skips the filters PATCH instead of saving defaults over them, and the filters step says so (review: career-night).
