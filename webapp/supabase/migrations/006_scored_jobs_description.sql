-- Persist the full job description at score time so the in-app detail view
-- is durable and independent of new_jobs.json rotation (WEBAPP_JOB_DETAIL_VIEW).
-- Rows scored before this migration have NULL; the detail endpoint falls back
-- to a request-time match against new_jobs.json for those.
alter table scored_jobs add column if not exists description text;
