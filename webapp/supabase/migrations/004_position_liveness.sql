-- Add position liveness fields to scored_jobs.
-- status defaults to 'open' so all existing rows stay live after migration.
alter table scored_jobs add column if not exists status text not null default 'open';
alter table scored_jobs add column if not exists closed_at date;
