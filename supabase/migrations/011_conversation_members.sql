-- Migration 011: Conversation Members
-- Membership mapping for conversations.

create table public.conversation_members (
  conversation_id uuid not null
    references public.conversations(id) on delete cascade,

  user_id uuid not null
    references auth.users(id) on delete cascade,

  joined_at timestamptz not null default now(),

  primary key (conversation_id, user_id)
);
