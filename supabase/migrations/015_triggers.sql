-- Migration 015: Triggers
-- Generic updated_at trigger and birth_data version auto-increment trigger.

-- 1. Generic set_updated_at function
create or replace function public.set_updated_at()
returns trigger
language plpgsql
security definer
set search_path = public, pg_temp
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Apply set_updated_at triggers
drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

drop trigger if exists birth_data_set_updated_at on public.birth_data;
create trigger birth_data_set_updated_at
before update on public.birth_data
for each row execute function public.set_updated_at();

drop trigger if exists astro_private_set_updated_at on public.astro_private;
create trigger astro_private_set_updated_at
before update on public.astro_private
for each row execute function public.set_updated_at();

drop trigger if exists astro_safe_profile_set_updated_at on public.astro_safe_profile;
create trigger astro_safe_profile_set_updated_at
before update on public.astro_safe_profile
for each row execute function public.set_updated_at();

drop trigger if exists connections_set_updated_at on public.connections;
create trigger connections_set_updated_at
before update on public.connections
for each row execute function public.set_updated_at();

drop trigger if exists compatibility_set_updated_at on public.compatibility_results;
create trigger compatibility_set_updated_at
before update on public.compatibility_results
for each row execute function public.set_updated_at();

drop trigger if exists daily_energies_set_updated_at on public.daily_energies;
create trigger daily_energies_set_updated_at
before update on public.daily_energies
for each row execute function public.set_updated_at();

drop trigger if exists conversations_set_updated_at on public.conversations;
create trigger conversations_set_updated_at
before update on public.conversations
for each row execute function public.set_updated_at();

-- 2. Birth data version bumping function
create or replace function public.bump_birth_data_version()
returns trigger
language plpgsql
security definer
set search_path = public, pg_temp
as $$
begin
  if (
    new.birth_date is distinct from old.birth_date
    or new.birth_time is distinct from old.birth_time
    or new.birth_time_precision is distinct from old.birth_time_precision
    or new.birth_timezone is distinct from old.birth_timezone
    or new.latitude is distinct from old.latitude
    or new.longitude is distinct from old.longitude
    or new.place_label is distinct from old.place_label
  ) then
    new.data_version = old.data_version + 1;
  else
    new.data_version = old.data_version;
  end if;

  return new;
end;
$$;

drop trigger if exists birth_data_bump_version on public.birth_data;
create trigger birth_data_bump_version
before update on public.birth_data
for each row execute function public.bump_birth_data_version();
