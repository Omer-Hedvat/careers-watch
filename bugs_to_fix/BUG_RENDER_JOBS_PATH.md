# BUG: Render scoring endpoint always 503 — new_jobs.json unreachable on persistent disk

## Status
🟢 Completed

## Severity
P0

## Description

`render.yaml` sets `JOBS_PATH=/data/new_jobs.json` (persistent disk). The GitHub Actions collect workflow commits `new_jobs.json` to the repo — it never writes to `/data/`. On Render, the persistent disk is separate from the deployed repo, so `/data/new_jobs.json` never exists unless manually seeded. The scoring endpoint will always return HTTP 503 "new_jobs.json not found" in production.

Root cause: two assumptions conflict — the workflow treats `new_jobs.json` as a repo file; the backend treats it as a disk file.

Simplest fix: change `JOBS_PATH` in `render.yaml` to Render's standard repo checkout path:
```
/opt/render/project/src/new_jobs.json
```
Render auto-deploys on every push to main. After each collect run (which commits `new_jobs.json`), Render redeploys and the fresh file is available at the repo checkout path. No disk needed for this file.

Also remove the `disk:` block from `render.yaml` unless needed for another purpose — free-tier persistent disks are limited.

## Steps to Reproduce

1. Deploy to Render using `render.yaml` as-is
2. Wait for GitHub Actions collect to run and commit `new_jobs.json`
3. Trigger a scoring run via `POST /score/`
4. Expected: scoring runs against latest collected jobs
5. Actual: HTTP 503 "new_jobs.json not found"

## Dependencies

- **Depends on:** —
- **Blocks:** Production deployment of the webapp
- **Touches:** `render.yaml`
- **Spec files to update:** `future_devs/archive/WEBAPP_DEPLOY_SPEC.md`

## Fix Notes
- Removed `disk:` block from `render.yaml` (free-tier disk was unused)
- Changed `JOBS_PATH` from `/data/new_jobs.json` → `/opt/render/project/src/new_jobs.json`
- Changed `COMPANIES_PATH` from `/data/companies.json` → `/opt/render/project/src/companies.json`
- Both files are committed to the repo; Render redeploys on every push so they are always current
