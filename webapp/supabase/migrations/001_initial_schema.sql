-- users table
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password_hash text,
  created_at timestamptz default now(),
  gemini_api_key_encrypted text,
  profile_md text,
  cv_text text,
  scoring_runs_this_week int default 0,
  last_week_reset date default current_date
);

-- score_configs table
create table if not exists score_configs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  location_terms text[] default '{}',
  skip_title_terms text[] default '{}',
  keep_title_terms text[] default '{}',
  skip_companies text[] default '{}',
  skip_industries text[] default '{}',
  lead_title_terms text[] default '{}',
  cv_lead_path text,
  cv_default_path text,
  updated_at timestamptz default now()
);

-- scored_jobs table
create table if not exists scored_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  apply_url text not null,
  company text,
  title text,
  location text,
  score int,
  reasoning text,
  flags text[] default '{}',
  scored_at timestamptz default now(),
  applied boolean default false,
  unique (user_id, apply_url)
);

-- row-level security
alter table users enable row level security;
alter table score_configs enable row level security;
alter table scored_jobs enable row level security;

create policy "users can read own row" on users for select using (auth.uid() = id);
create policy "users can update own row" on users for update using (auth.uid() = id);
create policy "users can read own score_config" on score_configs for all using (auth.uid() = user_id);
create policy "users can read own scored_jobs" on scored_jobs for all using (auth.uid() = user_id);
