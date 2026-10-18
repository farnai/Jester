-- Private gallery. Position zero is the only primary-photo source of truth.
create table public.profile_photos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  position smallint not null check (position between 0 and 5),
  storage_path text unique,
  legacy_url text,
  created_at timestamptz not null default now(),
  constraint photo_source check ((storage_path is null) <> (legacy_url is null)),
  constraint photo_owner_path check (storage_path is null or storage_path like user_id::text || '/%'),
  constraint photo_position unique (user_id, position) deferrable initially deferred
);
alter table public.profile_photos enable row level security;
revoke all on public.profile_photos from anon, authenticated;
grant all on public.profile_photos to service_role;

-- Durable compensating operations, deliberately independent of account lifetime.
create table public.profile_photo_cleanup (
  storage_path text primary key,
  not_before timestamptz not null default now(),
  created_at timestamptz not null default now()
);
alter table public.profile_photo_cleanup enable row level security;
revoke all on public.profile_photo_cleanup from anon, authenticated;
grant all on public.profile_photo_cleanup to service_role;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('profile-photos', 'profile-photos', false, 5242880, array['image/webp']);
-- No client storage policies: only the backend service key accesses this bucket.

insert into public.profile_photos (user_id, position, legacy_url)
select id, 0, avatar_url from public.profiles where nullif(avatar_url, '') is not null;

create function public.sync_profile_photo_avatar() returns trigger
language plpgsql security definer set search_path = public, pg_temp as $$
declare owner_id uuid;
begin
  owner_id := coalesce(new.user_id, old.user_id);
  update public.profiles set avatar_url = (
    select coalesce(legacy_url, '/v1/profiles/' || user_id || '/photos/' || id || '/content')
    from public.profile_photos where user_id = owner_id order by position limit 1
  ) where id = owner_id;
  if tg_op = 'DELETE' and old.storage_path is not null then
    insert into public.profile_photo_cleanup(storage_path) values(old.storage_path)
    on conflict (storage_path) do update set not_before = now();
  end if;
  return null;
end;
$$;
create trigger profile_photo_avatar after insert or update or delete on public.profile_photos
for each row execute function public.sync_profile_photo_avatar();

-- Keep legacy clients working only until the gallery is managed. They cannot
-- replace a gallery's primary with an unrelated avatar_url (including via REST).
create function public.guard_gallery_avatar() returns trigger
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  if pg_trigger_depth() > 1 then return new; end if;
  if exists(select 1 from public.profile_photos where user_id = new.id) then
    new.avatar_url := old.avatar_url;
  end if;
  return new;
end;
$$;
create trigger guard_gallery_avatar before update of avatar_url on public.profiles
for each row execute function public.guard_gallery_avatar();

create function public.capture_legacy_avatar() returns trigger
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  if pg_trigger_depth() > 1 then return null; end if;
  if nullif(new.avatar_url, '') is not null and not exists (
    select 1 from public.profile_photos where user_id = new.id
  ) then
    insert into public.profile_photos(user_id, position, legacy_url) values(new.id, 0, new.avatar_url);
  end if;
  return null;
end;
$$;
create trigger capture_legacy_avatar after insert or update of avatar_url on public.profiles
for each row execute function public.capture_legacy_avatar();

-- Storage API, not SQL metadata deletion, must remove private physical objects.
create or replace function public.cleanup_user_storage_on_account_deletion()
returns trigger language plpgsql security definer set search_path = public, storage, pg_temp as $$
begin
  delete from storage.objects
  where bucket_id <> 'profile-photos' and (storage.foldername(name))[1] = old.id::text;
  return old;
exception when others then
  raise warning 'Legacy storage cleanup requires retry';
  return old;
end;
$$;
revoke all on function public.sync_profile_photo_avatar(), public.guard_gallery_avatar(), public.capture_legacy_avatar() from public;

-- Interests use the same visibility boundary as the social profile.
drop policy user_interests_select on public.user_interests;
create policy user_interests_select on public.user_interests for select to authenticated
using (user_id = auth.uid() or exists (
  select 1 from public.profiles p where p.id = user_id and p.is_discoverable
  and not public.is_user_blocked(auth.uid(), user_id)
));
