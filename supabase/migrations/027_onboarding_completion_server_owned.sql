-- Completion is validated by the backend, not by owner-editable profile fields.
-- Preserve existing owner RLS and editing grants for every other profile field.
create or replace function public.guard_onboarding_completion()
returns trigger
language plpgsql
set search_path = pg_catalog, public
as $$
begin
  if current_user in ('anon', 'authenticated') then
    if (tg_op = 'INSERT' and new.onboarding_completed)
       or (tg_op = 'UPDATE' and new.onboarding_completed is distinct from old.onboarding_completed) then
      raise exception 'Onboarding completion must use the validated backend endpoint'
        using errcode = '42501';
    end if;
  end if;
  return new;
end;
$$;

drop trigger if exists profiles_guard_onboarding_completion on public.profiles;
create trigger profiles_guard_onboarding_completion
before insert or update of onboarding_completed on public.profiles
for each row execute function public.guard_onboarding_completion();
