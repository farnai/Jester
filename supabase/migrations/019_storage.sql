-- Migration 019: Storage Buckets & Policies + Account Deletion Cleanup

-- 1. Create avatars bucket in storage.buckets
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'avatars',
  'avatars',
  true,
  5242880, -- 5MB limit
  array['image/jpeg', 'image/png', 'image/webp', 'image/gif']
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

-- 2. Storage RLS policies for avatars
drop policy if exists "Avatar images are publicly accessible" on storage.objects;
create policy "Avatar images are publicly accessible"
on storage.objects
for select
using (bucket_id = 'avatars');

drop policy if exists "Users can upload their own avatar" on storage.objects;
create policy "Users can upload their own avatar"
on storage.objects
for insert
to authenticated
with check (
  bucket_id = 'avatars'
  and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "Users can update their own avatar" on storage.objects;
create policy "Users can update their own avatar"
on storage.objects
for update
to authenticated
using (
  bucket_id = 'avatars'
  and (storage.foldername(name))[1] = auth.uid()::text
)
with check (
  bucket_id = 'avatars'
  and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "Users can delete their own avatar" on storage.objects;
create policy "Users can delete their own avatar"
on storage.objects
for delete
to authenticated
using (
  bucket_id = 'avatars'
  and (storage.foldername(name))[1] = auth.uid()::text
);

-- 3. Account deletion storage cleanup trigger
-- When a user is hard-deleted from auth.users, clean up their storage objects
create or replace function public.cleanup_user_storage_on_account_deletion()
returns trigger
language plpgsql
security definer
set search_path = public, storage, pg_temp
as $$
begin
  -- Delete all storage objects belonging to the user's folder
  delete from storage.objects
  where (storage.foldername(name))[1] = old.id::text;

  return old;
exception
  when others then
    -- Log error and allow user deletion to complete
    raise warning 'Error cleaning up storage objects for deleted user %: %', old.id, sqlerrm;
    return old;
end;
$$;

drop trigger if exists on_auth_user_deleted_cleanup_storage on auth.users;
create trigger on_auth_user_deleted_cleanup_storage
after delete on auth.users
for each row execute function public.cleanup_user_storage_on_account_deletion();
