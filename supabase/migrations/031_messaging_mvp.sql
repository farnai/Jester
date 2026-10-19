-- Additive messaging state. Existing messages and conversations are preserved.
alter table public.messages add column client_nonce uuid;
create unique index messages_sender_nonce on public.messages(conversation_id, sender_user_id, client_nonce)
  where client_nonce is not null;
create index messages_page_order on public.messages(conversation_id, created_at desc, id desc);
-- NOT VALID preserves historical rows while enforcing the contract on new writes.
alter table public.messages add constraint messages_body_size
  check (length(btrim(body)) between 1 and 2000) not valid;

-- A separate owner-only table avoids exposing read pointers through member SELECT.
create table public.conversation_reads (
  conversation_id uuid not null,
  user_id uuid not null,
  last_read_message_id uuid references public.messages(id) on delete set null,
  primary key (conversation_id, user_id),
  foreign key (conversation_id, user_id) references public.conversation_members(conversation_id,user_id) on delete cascade
);
alter table public.conversation_reads enable row level security;
revoke all on public.conversation_reads from public, anon, authenticated;
grant select on public.conversation_reads to authenticated;
grant all on public.conversation_reads to service_role;
create policy conversation_reads_owner on public.conversation_reads for select to authenticated
  using (user_id = auth.uid() and public.is_active_direct_conversation(conversation_id, auth.uid()));

-- Clients may request a connection, never forge its acceptance to unlock chat.
alter policy connections_insert on public.connections with check (
  initiated_by = auth.uid() and (user_a_id = auth.uid() or user_b_id = auth.uid())
  and status = 'pending' and blocked_by is null
  and not public.is_user_blocked(user_a_id, user_b_id)
);

-- Serialize inserts with connection transitions, including direct RLS inserts.
create function public.guard_message_connection() returns trigger
language plpgsql security definer set search_path = public, pg_temp as $$
declare other_id uuid; relation public.connections;
begin
  select cm.user_id into other_id from public.conversation_members cm
    join public.conversations c on c.id=cm.conversation_id and c.conversation_type='direct'
    where cm.conversation_id=new.conversation_id and cm.user_id<>new.sender_user_id
      and exists (select 1 from public.conversation_members mine
        where mine.conversation_id=cm.conversation_id and mine.user_id=new.sender_user_id);
  select * into relation from public.connections
    where user_a_id=least(new.sender_user_id,other_id) and user_b_id=greatest(new.sender_user_id,other_id)
    for update;
  if relation.id is null or relation.status <> 'accepted' or relation.blocked_by is not null then
    raise insufficient_privilege using message='Active connection required';
  end if;
  -- A direct authenticated client cannot forge another sender or historical time.
  if auth.uid() is not null then
    if new.sender_user_id <> auth.uid() then
      raise insufficient_privilege using message='Invalid message sender';
    end if;
    new.created_at := clock_timestamp();
  end if;
  return new;
end;
$$;
revoke all on function public.guard_message_connection() from public, anon, authenticated;
create trigger messages_guard_connection before insert on public.messages
  for each row execute function public.guard_message_connection();

-- Read pointers are deliberately excluded from Realtime publication.
alter publication supabase_realtime add table public.connections;
