-- Migration 013: Notifications
-- In-app notifications table for v1.

create table public.notifications (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references auth.users(id) on delete cascade,

  type text not null,
  payload jsonb not null default '{}'::jsonb,

  read_at timestamptz,

  created_at timestamptz not null default now()
);
