-- Per-user "Skip" list (WEBAPP_HIDE_DISMISS_JOBS): keyed by apply_url so it covers
-- both the shared positions catalog and scored_jobs. Skipped jobs are hidden on
-- Positions + Digest and never sent to Gemini. Only the backend's service role
-- reads/writes it, so RLS is on with no policies.
create table if not exists hidden_jobs (
  user_id uuid not null references users(id) on delete cascade,
  apply_url text not null,
  hidden_at timestamptz not null default now(),
  primary key (user_id, apply_url)
);
alter table hidden_jobs enable row level security;
