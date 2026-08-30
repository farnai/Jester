-- Migration 006: Astro Safe Profile
-- Safe derived astrology profile. Contains only non-private high-level interpretations.

create table public.astro_safe_profile (
  user_id uuid primary key references auth.users(id) on delete cascade,

  source_birth_data_version integer not null
    check (source_birth_data_version >= 1),

  engine_version text not null,

  sun_sign text,
  moon_sign text,
  ascendant_sign text,

  element_primary text,
  modality_primary text,

  updated_at timestamptz not null default now()
);
