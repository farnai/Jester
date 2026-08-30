-- Migration 018: Row Level Security (RLS)
-- Enables RLS and establishes privacy policies for all tables.

-- Enable Row Level Security
alter table public.profiles enable row level security;
alter table public.birth_data enable row level security;
alter table public.astro_private enable row level security;
alter table public.astro_safe_profile enable row level security;
alter table public.connections enable row level security;
alter table public.compatibility_results enable row level security;
alter table public.daily_energies enable row level security;
alter table public.conversations enable row level security;
alter table public.conversation_members enable row level security;
alter table public.messages enable row level security;
alter table public.notifications enable row level security;

-- -------------------------------------------------------------
-- 1. Profiles
-- -------------------------------------------------------------
drop policy if exists profiles_select on public.profiles;
create policy profiles_select
on public.profiles
for select
to authenticated
using (
  id = auth.uid()
  or (
    is_discoverable = true
    and not public.is_user_blocked(auth.uid(), id)
  )
);

drop policy if exists profiles_insert on public.profiles;
create policy profiles_insert
on public.profiles
for insert
to authenticated
with check (
  id = auth.uid()
);

drop policy if exists profiles_update on public.profiles;
create policy profiles_update
on public.profiles
for update
to authenticated
using (
  id = auth.uid()
)
with check (
  id = auth.uid()
);

-- -------------------------------------------------------------
-- 2. Birth Data (Strictly owner-only)
-- -------------------------------------------------------------
drop policy if exists birth_data_select_own on public.birth_data;
create policy birth_data_select_own
on public.birth_data
for select
to authenticated
using (
  user_id = auth.uid()
);

drop policy if exists birth_data_insert_own on public.birth_data;
create policy birth_data_insert_own
on public.birth_data
for insert
to authenticated
with check (
  user_id = auth.uid()
);

drop policy if exists birth_data_update_own on public.birth_data;
create policy birth_data_update_own
on public.birth_data
for update
to authenticated
using (
  user_id = auth.uid()
)
with check (
  user_id = auth.uid()
);

-- -------------------------------------------------------------
-- 3. Astro Private (Backend-only; default deny all client policies)
-- -------------------------------------------------------------

-- -------------------------------------------------------------
-- 4. Astro Safe Profile (Safe derived placements)
-- -------------------------------------------------------------
drop policy if exists astro_safe_profile_select on public.astro_safe_profile;
create policy astro_safe_profile_select
on public.astro_safe_profile
for select
to authenticated
using (
  user_id = auth.uid()
  or exists (
    select 1
    from public.profiles p
    where p.id = astro_safe_profile.user_id
      and p.is_discoverable = true
      and not public.is_user_blocked(auth.uid(), p.id)
  )
);

-- -------------------------------------------------------------
-- 5. Connections (Mutual visibility, block-aware)
-- -------------------------------------------------------------
drop policy if exists connections_select on public.connections;
create policy connections_select
on public.connections
for select
to authenticated
using (
  (
    status <> 'blocked'
    and (user_a_id = auth.uid() or user_b_id = auth.uid())
  )
  or
  (
    status = 'blocked'
    and blocked_by = auth.uid()
  )
);

drop policy if exists connections_insert on public.connections;
create policy connections_insert
on public.connections
for insert
to authenticated
with check (
  initiated_by = auth.uid()
  and (user_a_id = auth.uid() or user_b_id = auth.uid())
  and not public.is_user_blocked(user_a_id, user_b_id)
);

-- -------------------------------------------------------------
-- 6. Compatibility Results (Requires active, unblocked connection)
-- -------------------------------------------------------------
drop policy if exists compatibility_results_select on public.compatibility_results;
create policy compatibility_results_select
on public.compatibility_results
for select
to authenticated
using (
  (
    user_a_id = auth.uid()
    or user_b_id = auth.uid()
  )
  and public.has_active_connection(user_a_id, user_b_id)
);

-- -------------------------------------------------------------
-- 7. Daily Energies (Owner only)
-- -------------------------------------------------------------
drop policy if exists daily_energies_select_own on public.daily_energies;
create policy daily_energies_select_own
on public.daily_energies
for select
to authenticated
using (
  user_id = auth.uid()
);

-- -------------------------------------------------------------
-- 8. Conversations (Active direct conversation members only)
-- -------------------------------------------------------------
drop policy if exists conversations_select_member on public.conversations;
create policy conversations_select_member
on public.conversations
for select
to authenticated
using (
  public.is_active_direct_conversation(id, auth.uid())
);

-- -------------------------------------------------------------
-- 9. Conversation Members (Active direct conversation members only)
-- -------------------------------------------------------------
drop policy if exists conversation_members_select on public.conversation_members;
create policy conversation_members_select
on public.conversation_members
for select
to authenticated
using (
  user_id = auth.uid()
  or public.is_active_direct_conversation(conversation_id, auth.uid())
);

-- -------------------------------------------------------------
-- 10. Messages (Active direct conversation members only)
-- -------------------------------------------------------------
drop policy if exists messages_select_member on public.messages;
create policy messages_select_member
on public.messages
for select
to authenticated
using (
  public.is_active_direct_conversation(conversation_id, auth.uid())
);

drop policy if exists messages_insert_member on public.messages;
create policy messages_insert_member
on public.messages
for insert
to authenticated
with check (
  sender_user_id = auth.uid()
  and public.is_active_direct_conversation(conversation_id, auth.uid())
);

-- -------------------------------------------------------------
-- 11. Notifications (Owner only)
-- -------------------------------------------------------------
drop policy if exists notifications_select_own on public.notifications;
create policy notifications_select_own
on public.notifications
for select
to authenticated
using (
  user_id = auth.uid()
);

drop policy if exists notifications_update_own on public.notifications;
create policy notifications_update_own
on public.notifications
for update
to authenticated
using (
  user_id = auth.uid()
)
with check (
  user_id = auth.uid()
);
