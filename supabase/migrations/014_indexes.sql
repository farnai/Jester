-- Migration 014: Indexes
-- Performance indexes across foreign keys, status fields, and query paths.

-- Profiles
create index if not exists profiles_is_discoverable_idx
  on public.profiles(is_discoverable);

-- Connections
create index if not exists connections_user_a_idx
  on public.connections(user_a_id);

create index if not exists connections_user_b_idx
  on public.connections(user_b_id);

create index if not exists connections_status_idx
  on public.connections(status);

create index if not exists connections_blocked_by_idx
  on public.connections(blocked_by)
  where blocked_by is not null;

-- Compatibility
create index if not exists compatibility_user_a_idx
  on public.compatibility_results(user_a_id);

create index if not exists compatibility_user_b_idx
  on public.compatibility_results(user_b_id);

create index if not exists compatibility_updated_at_idx
  on public.compatibility_results(updated_at desc);

-- Daily energy
create index if not exists daily_energies_user_date_idx
  on public.daily_energies(user_id, energy_date desc);

-- Chat
create index if not exists conversations_created_by_idx
  on public.conversations(created_by);

create index if not exists conversation_members_user_idx
  on public.conversation_members(user_id);

create index if not exists messages_conversation_created_idx
  on public.messages(conversation_id, created_at);

create index if not exists messages_sender_user_idx
  on public.messages(sender_user_id);

-- Notifications
create index if not exists notifications_user_created_idx
  on public.notifications(user_id, created_at desc);

create index if not exists notifications_user_unread_idx
  on public.notifications(user_id)
  where read_at is null;
