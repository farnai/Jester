-- Migration 025: High-Performance City Search Indexes
-- Adds pg_trgm extension and optimized pattern/trigram indexes for instantaneous
-- case-insensitive prefix and substring searches across all 152k canonical cities.

-- 1. Enable pg_trgm extension for trigram similarity and substring indexing
create extension if not exists pg_trgm;

-- 2. B-Tree pattern ops index for lightning-fast case-insensitive prefix searches (e.g. 'gurj%')
create index if not exists idx_cities_name_ascii_lower on public.cities (lower(name_ascii) varchar_pattern_ops);

-- 3. GIN Trigram indexes for sub-millisecond substring/contains searches (e.g. '%gurj%')
create index if not exists idx_cities_name_ascii_trgm on public.cities using gin (name_ascii gin_trgm_ops);
create index if not exists idx_cities_name_trgm on public.cities using gin (name gin_trgm_ops);
