-- Migration 012: Messages
-- Messages sent within conversations. Author deletion cascades.

create table public.messages (
  id uuid primary key default gen_random_uuid(),

  conversation_id uuid not null
    references public.conversations(id) on delete cascade,

  sender_user_id uuid not null
    references auth.users(id) on delete cascade,

  body text not null,

  created_at timestamptz not null default now()
);
