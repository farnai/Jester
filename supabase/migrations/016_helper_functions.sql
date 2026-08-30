-- Migration 016: Helper Functions
-- Security-definer relationship and conversation evaluation helpers with hardened search_path and permissions.

-- 1. Check if user is a participant in a specific connection row
create or replace function public.is_connection_participant(
  p_connection_id uuid,
  p_user_id uuid
)
returns boolean
language sql
security definer
set search_path = public, pg_temp
stable
as $$
  select exists (
    select 1
    from public.connections c
    where c.id = p_connection_id
      and (c.user_a_id = p_user_id or c.user_b_id = p_user_id)
  );
$$;

-- 2. Check if two users have an active, accepted, non-blocked connection
create or replace function public.has_active_connection(
  p_user_one uuid,
  p_user_two uuid
)
returns boolean
language sql
security definer
set search_path = public, pg_temp
stable
as $$
  select exists (
    select 1
    from public.connections c
    where p_user_one is not null
      and p_user_two is not null
      and p_user_one <> p_user_two
      and c.user_a_id = least(p_user_one, p_user_two)
      and c.user_b_id = greatest(p_user_one, p_user_two)
      and c.status = 'accepted'
      and c.blocked_by is null
  );
$$;

-- 3. Check if two users have a blocked relationship (either direction)
create or replace function public.is_user_blocked(
  p_user_one uuid,
  p_user_two uuid
)
returns boolean
language sql
security definer
set search_path = public, pg_temp
stable
as $$
  select exists (
    select 1
    from public.connections c
    where p_user_one is not null
      and p_user_two is not null
      and p_user_one <> p_user_two
      and c.user_a_id = least(p_user_one, p_user_two)
      and c.user_b_id = greatest(p_user_one, p_user_two)
      and c.status = 'blocked'
  );
$$;

-- 4. Check if user is a conversation member
create or replace function public.is_conversation_member(
  p_conversation_id uuid,
  p_user_id uuid
)
returns boolean
language sql
security definer
set search_path = public, pg_temp
stable
as $$
  select exists (
    select 1
    from public.conversation_members cm
    where cm.conversation_id = p_conversation_id
      and cm.user_id = p_user_id
  );
$$;

-- 5. Get the other direct conversation member
create or replace function public.get_other_direct_conversation_member(
  p_conversation_id uuid,
  p_user_id uuid
)
returns uuid
language sql
security definer
set search_path = public, pg_temp
stable
as $$
  select cm.user_id
  from public.conversation_members cm
  join public.conversations c on c.id = cm.conversation_id
  where cm.conversation_id = p_conversation_id
    and cm.user_id <> p_user_id
    and c.conversation_type = 'direct'
  limit 1;
$$;

-- 6. Check if direct conversation is active and unblocked for a user
create or replace function public.is_active_direct_conversation(
  p_conversation_id uuid,
  p_user_id uuid
)
returns boolean
language plpgsql
security definer
set search_path = public, pg_temp
stable
as $$
declare
  v_other_user_id uuid;
begin
  if p_user_id is null or p_conversation_id is null then
    return false;
  end if;

  -- User must be a member of the conversation
  if not exists (
    select 1
    from public.conversation_members cm
    where cm.conversation_id = p_conversation_id
      and cm.user_id = p_user_id
  ) then
    return false;
  end if;

  -- Find other member of direct conversation
  select cm.user_id into v_other_user_id
  from public.conversation_members cm
  where cm.conversation_id = p_conversation_id
    and cm.user_id <> p_user_id
  limit 1;

  -- If no other member exists, access is not permitted
  if v_other_user_id is null then
    return false;
  end if;

  -- Check active accepted and unblocked connection between participants
  return public.has_active_connection(p_user_id, v_other_user_id);
end;
$$;

-- Revoke execute from public and grant only to authenticated and service_role
revoke execute on function public.is_connection_participant(uuid, uuid) from public;
grant execute on function public.is_connection_participant(uuid, uuid) to authenticated, service_role;

revoke execute on function public.has_active_connection(uuid, uuid) from public;
grant execute on function public.has_active_connection(uuid, uuid) to authenticated, service_role;

revoke execute on function public.is_user_blocked(uuid, uuid) from public;
grant execute on function public.is_user_blocked(uuid, uuid) to authenticated, service_role;

revoke execute on function public.is_conversation_member(uuid, uuid) from public;
grant execute on function public.is_conversation_member(uuid, uuid) to authenticated, service_role;

revoke execute on function public.get_other_direct_conversation_member(uuid, uuid) from public;
grant execute on function public.get_other_direct_conversation_member(uuid, uuid) to authenticated, service_role;

revoke execute on function public.is_active_direct_conversation(uuid, uuid) from public;
grant execute on function public.is_active_direct_conversation(uuid, uuid) to authenticated, service_role;
