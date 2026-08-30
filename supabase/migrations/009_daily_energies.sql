-- Migration 009: Daily Energies
-- Persistent daily transit/energy result generated per user per local calendar date.

create table public.daily_energies (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null references auth.users(id) on delete cascade,

  energy_date date not null,

  signals jsonb not null default '[]'::jsonb,
  interpretation jsonb not null default '{}'::jsonb,

  engine_version text not null,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint daily_energy_unique_user_date
    unique (user_id, energy_date)
);
