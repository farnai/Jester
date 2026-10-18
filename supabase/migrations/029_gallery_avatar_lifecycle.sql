-- Do not resurrect an OAuth/legacy avatar after the owner empties a gallery.
alter table public.profiles add column photo_gallery_managed boolean not null default false;
update public.profiles set photo_gallery_managed = true
where exists(select 1 from public.profile_photos p where p.user_id = profiles.id and p.storage_path is not null);
revoke update on public.profiles from authenticated;
-- Preserve existing owner-editable fields, excluding server-owned lifecycle state.
grant update (display_name, first_name, last_name, avatar_url, bio, city, city_id,
  current_city_id, occupation, timezone, is_discoverable, onboarding_step) on public.profiles to authenticated;

create or replace function public.sync_profile_photo_avatar() returns trigger
language plpgsql security definer set search_path = public, pg_temp as $$
declare owner_id uuid;
begin
  owner_id := coalesce(new.user_id, old.user_id);
  update public.profiles set
    photo_gallery_managed = photo_gallery_managed or tg_op = 'DELETE' or new.storage_path is not null,
    avatar_url = (
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
create or replace function public.guard_gallery_avatar() returns trigger
language plpgsql security definer set search_path = public, pg_temp as $$
begin
  if pg_trigger_depth() > 1 then return new; end if;
  if old.photo_gallery_managed or exists(select 1 from public.profile_photos where user_id = new.id) then
    new.avatar_url := old.avatar_url;
  end if;
  return new;
end;
$$;
