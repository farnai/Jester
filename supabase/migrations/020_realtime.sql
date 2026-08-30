-- Migration 020: Supabase Realtime Publication Configuration
-- Enables Realtime events for messages and notifications while preserving RLS privacy boundaries.

do $$
begin
  if not exists (
    select 1 from pg_publication where pubname = 'supabase_realtime'
  ) then
    create publication supabase_realtime;
  end if;
end;
$$;

-- Add messages and notifications to supabase_realtime publication
alter publication supabase_realtime add table public.messages;
alter publication supabase_realtime add table public.notifications;
