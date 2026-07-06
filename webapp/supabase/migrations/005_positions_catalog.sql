-- Shared, global catalog of every open position pulled from the pipeline.
--
-- Unlike scored_jobs (per-user scoring OUTPUT), this table is one copy for ALL
-- users. It backs the Positions page, which shows the full market of open roles
-- to everyone - including brand-new users who have no profile or scoring yet.
-- Populated by scripts/sync_positions.py from new_jobs.json on each collect run.
create table if not exists positions (
  apply_url  text primary key,
  company    text not null default '',
  title      text not null default '',
  location   text default '',
  first_seen date,
  synced_at  timestamptz not null default now()
);

-- Fast alphabetical listing (endpoint orders by company, then title).
create index if not exists positions_company_title_idx on positions (company, title);

alter table positions enable row level security;

-- The catalog is shared and non-sensitive; any signed-in user may read it.
-- Writes happen only via the service-role key (sync script + backend), which
-- bypasses RLS, so no insert/update/delete policy is granted to end users.
drop policy if exists "authenticated can read positions" on positions;
create policy "authenticated can read positions"
  on positions for select
  to authenticated
  using (true);
