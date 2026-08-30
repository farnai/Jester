-- Migration 004: Birth Data
-- Private raw user birth information with data versioning and birth time precision consistency.

create table public.birth_data (
  user_id uuid primary key references auth.users(id) on delete cascade,

  birth_date date not null,
  birth_time time,
  birth_time_precision public.birth_time_precision not null default 'unknown',

  birth_timezone text not null,

  latitude double precision,
  longitude double precision,
  place_label text,

  data_version integer not null default 1
    check (data_version >= 1),

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint birth_time_precision_consistency check (
    (birth_time_precision = 'unknown' and birth_time is null)
    or
    (birth_time_precision in ('exact', 'approximate') and birth_time is not null)
  )
);
