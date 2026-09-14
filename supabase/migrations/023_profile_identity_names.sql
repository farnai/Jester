-- Migration 023: Profile Identity Names
-- Add first_name and last_name to public.profiles.
-- display_name already exists from Migration 003.
-- Nullable at database level for full backward compatibility with existing rows and legacy paths.

alter table public.profiles
  add column if not exists first_name text,
  add column if not exists last_name text;
