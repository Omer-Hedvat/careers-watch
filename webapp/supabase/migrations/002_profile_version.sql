alter table users add column if not exists profile_version int default 1;
alter table scored_jobs add column if not exists profile_version int;
