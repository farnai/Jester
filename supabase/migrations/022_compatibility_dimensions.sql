-- Migration 022: Compatibility Dimensions
-- Adds dimensions JSONB column to public.compatibility_results to persist the 4 Synastry V1 relationship dimension subscores.

alter table public.compatibility_results
  add column if not exists dimensions jsonb not null default '{}'::jsonb;
