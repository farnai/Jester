-- Migration 017: Grants
-- Role-based privilege separation for anon, authenticated, and service_role.

-- Grant usage on public schema
grant usage on schema public to anon, authenticated, service_role;

-- Grant all permissions on all tables to service_role
grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to service_role;
grant all on all routines in schema public to service_role;

-- 1. Profiles & Birth Data
grant select, insert, update on public.profiles to authenticated;
grant select, insert, update on public.birth_data to authenticated;

-- 2. Astro Private: Strictly server-only. No client grants.
revoke all on public.astro_private from authenticated, anon, public;

-- 3. Astro Safe Profile: Read-only derived data
grant select on public.astro_safe_profile to authenticated;

-- 4. Connections: SELECT and INSERT only. Direct client UPDATE is forbidden (Rule 4A)
grant select, insert on public.connections to authenticated;
revoke update, delete on public.connections from authenticated, anon, public;

-- 5. Compatibility Results: Read-only for authenticated participants
grant select on public.compatibility_results to authenticated;

-- 6. Daily Energies: Read-only for authenticated owner
grant select on public.daily_energies to authenticated;

-- 7. Chat: Conversations, Members, Messages
grant select on public.conversations to authenticated;
grant select on public.conversation_members to authenticated;
grant select, insert on public.messages to authenticated;

-- 8. Notifications: Read and mark-as-read (update)
grant select, update on public.notifications to authenticated;

-- 9. Anonymous role: Revoke all data access
revoke all on all tables in schema public from anon;
