-- Migration 007: Connections
-- Canonical user-to-user social relationship with strict pair ordering and blocking support.

create table public.connections (
  id uuid primary key default gen_random_uuid(),

  user_a_id uuid not null references auth.users(id) on delete cascade,
  user_b_id uuid not null references auth.users(id) on delete cascade,

  status public.connection_status not null default 'pending',

  initiated_by uuid not null references auth.users(id) on delete cascade,

  blocked_by uuid references auth.users(id) on delete cascade,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint connections_distinct_users
    check (user_a_id <> user_b_id),

  constraint connections_canonical_pair
    check (user_a_id < user_b_id),

  constraint connections_unique_pair
    unique (user_a_id, user_b_id),

  constraint connections_initiator_is_participant
    check (initiated_by = user_a_id or initiated_by = user_b_id),

  constraint connections_blocked_by_consistency
    check (
      (status = 'blocked' and blocked_by is not null)
      or
      (status <> 'blocked' and blocked_by is null)
    ),

  constraint connections_blocker_is_participant
    check (
      blocked_by is null
      or blocked_by = user_a_id
      or blocked_by = user_b_id
    )
);
