-- Keep the original uploaded CV / profile files (Settings shows them as a clickable card).
-- Private bucket: only the backend's service role reads/writes it; browsers get signed URLs.
alter table users add column if not exists cv_file jsonb;
alter table users add column if not exists profile_file jsonb;
insert into storage.buckets (id, name, public)
values ('user-files', 'user-files', false)
on conflict (id) do nothing;
