-- Migration 005: Astro Private
-- Private calculated raw astrology data. Never exposed to mobile clients.

create table public.astro_private (
  user_id uuid primary key references auth.users(id) on delete cascade,

  source_birth_data_version integer not null
    check (source_birth_data_version >= 1),

  engine_version text not null,

  sun_longitude double precision,
  moon_longitude double precision,
  mercury_longitude double precision,
  venus_longitude double precision,
  mars_longitude double precision,
  jupiter_longitude double precision,
  saturn_longitude double precision,
  uranus_longitude double precision,
  neptune_longitude double precision,
  pluto_longitude double precision,

  ascendant_longitude double precision,

  houses jsonb,
  retrogrades jsonb,

  calculated_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
