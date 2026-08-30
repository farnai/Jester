-- Migration 003: Profiles
-- User-facing profile information. Does NOT contain private birth data or raw astrology.

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,

  display_name text not null,
  avatar_url text,
  bio text,
  city text,
  occupation text,
  timezone text not null default 'UTC',

  is_discoverable boolean not null default true,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
