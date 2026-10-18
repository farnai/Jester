-- Match bounded keyset and canonical-city filters without introducing ranking.
create index if not exists profiles_discoverable_id on public.profiles(id) where is_discoverable;
create index if not exists profiles_discoverable_city_id on public.profiles(current_city_id, id) where is_discoverable;
