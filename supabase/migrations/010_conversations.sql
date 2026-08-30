-- Migration 010: Conversations
-- Conversation rooms (direct chat in v1).

create table public.conversations (
  id uuid primary key default gen_random_uuid(),

  conversation_type public.conversation_type not null default 'direct',

  created_by uuid not null references auth.users(id) on delete cascade,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
