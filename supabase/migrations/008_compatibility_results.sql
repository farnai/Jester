-- Migration 008: Compatibility Results
-- Current compatibility result per canonical user pair. Upserted on recalculation without historical bloat.

create table public.compatibility_results (
  id uuid primary key default gen_random_uuid(),

  user_a_id uuid not null references auth.users(id) on delete cascade,
  user_b_id uuid not null references auth.users(id) on delete cascade,

  user_a_birth_data_version integer not null
    check (user_a_birth_data_version >= 1),

  user_b_birth_data_version integer not null
    check (user_b_birth_data_version >= 1),

  engine_version text not null,

  score numeric(5,2)
    check (score >= 0 and score <= 100),

  signals jsonb not null default '[]'::jsonb,
  best_topics jsonb not null default '[]'::jsonb,
  conversation_starters jsonb not null default '[]'::jsonb,

  calculated_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint compatibility_distinct_users
    check (user_a_id <> user_b_id),

  constraint compatibility_canonical_pair
    check (user_a_id < user_b_id),

  constraint compatibility_current_pair_unique
    unique (user_a_id, user_b_id)
);
