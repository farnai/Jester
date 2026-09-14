-- Migration 024: Canonical Global Location System (Countries and Cities)
-- Establishes single source of geographic truth for Birth Place and Current Location.

-- 1. Canonical Countries Table
create table if not exists public.countries (
  id uuid primary key default gen_random_uuid(),
  source_id integer not null unique,
  iso2 varchar(2) not null unique,
  name text not null,
  native_name text,
  phone_code varchar(10),
  created_at timestamptz not null default now()
);

create index if not exists idx_countries_iso2 on public.countries(iso2);

-- 2. Canonical Cities Table
create table if not exists public.cities (
  id uuid primary key default gen_random_uuid(),
  source_id integer not null unique,
  country_id uuid not null references public.countries(id) on delete restrict,
  country_code varchar(2) not null,
  name text not null,
  name_ascii text not null,
  state_or_region text,
  latitude double precision not null,
  longitude double precision not null,
  timezone text not null,
  is_major_city boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint chk_city_lat check (latitude >= -90.0 and latitude <= 90.0),
  constraint chk_city_lon check (longitude >= -180.0 and longitude <= 180.0)
);

create index if not exists idx_cities_country_id on public.cities(country_id);
create index if not exists idx_cities_country_code on public.cities(country_code);
create index if not exists idx_cities_name_ascii on public.cities(name_ascii);
create index if not exists idx_cities_is_major on public.cities(is_major_city) where is_major_city = true;

-- 3. Link Existing Tables
alter table public.birth_data
  add column if not exists birth_city_id uuid references public.cities(id) on delete restrict;

create index if not exists idx_birth_data_city_id on public.birth_data(birth_city_id);

alter table public.profiles
  add column if not exists city_id uuid references public.cities(id) on delete set null;

create index if not exists idx_profiles_city_id on public.profiles(city_id);

-- 4. Update bump_birth_data_version() trigger function to include birth_city_id
create or replace function public.bump_birth_data_version()
returns trigger as $$
begin
  if (
    new.birth_date is distinct from old.birth_date
    or new.birth_time is distinct from old.birth_time
    or new.birth_time_precision is distinct from old.birth_time_precision
    or new.birth_timezone is distinct from old.birth_timezone
    or new.latitude is distinct from old.latitude
    or new.longitude is distinct from old.longitude
    or new.place_label is distinct from old.place_label
    or new.birth_city_id is distinct from old.birth_city_id
  ) then
    new.data_version := old.data_version + 1;
  end if;
  return new;
end;
$$ language plpgsql;

-- 5. Row Level Security & Grants
alter table public.countries enable row level security;
alter table public.cities enable row level security;

drop policy if exists countries_select_all on public.countries;
create policy countries_select_all on public.countries for select using (true);

drop policy if exists cities_select_all on public.cities;
create policy cities_select_all on public.cities for select using (true);

grant select on public.countries, public.cities to authenticated, anon;
