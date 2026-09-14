-- Migration 026: Auth-Ready Database & Onboarding Foundation
-- Phase 1: Profiles onboarding state & location, interest taxonomy foundation, RLS and constraints.

-- 1. Profiles Table Updates: Where You Live & Resumable Onboarding State
alter table public.profiles
  add column if not exists current_city_id uuid references public.cities(id) on delete set null,
  add column if not exists onboarding_step integer not null default 1,
  add column if not exists onboarding_completed boolean not null default false;

create index if not exists idx_profiles_current_city_id on public.profiles(current_city_id);
create index if not exists idx_profiles_onboarding_completed on public.profiles(onboarding_completed);

-- Backfill current_city_id from legacy city_id for backward compatibility
update public.profiles
set current_city_id = city_id
where current_city_id is null and city_id is not null;

-- 2. Canonical Interest Categories
create table if not exists public.interest_categories (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique not null,
  icon text,
  sort_order integer not null default 0,
  status text not null default 'active' check (status in ('active', 'deprecated')),
  created_at timestamptz not null default now()
);

create index if not exists idx_interest_categories_slug on public.interest_categories(slug);
create index if not exists idx_interest_categories_sort_order on public.interest_categories(sort_order);

-- 3. Canonical Interests
create table if not exists public.interests (
  id uuid primary key default gen_random_uuid(),
  category_id uuid not null references public.interest_categories(id) on delete cascade,
  name text not null,
  slug text unique not null,
  sort_order integer not null default 0,
  status text not null default 'active' check (status in ('active', 'hidden', 'deprecated')),
  created_at timestamptz not null default now()
);

create index if not exists idx_interests_category_id on public.interests(category_id);
create index if not exists idx_interests_slug on public.interests(slug);
create index if not exists idx_interests_sort_order on public.interests(sort_order);

-- 4. User Interests Mapping
create table if not exists public.user_interests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  interest_id uuid not null references public.interests(id) on delete cascade,
  created_at timestamptz not null default now(),
  constraint uq_user_interests unique (user_id, interest_id)
);

create index if not exists idx_user_interests_user_id on public.user_interests(user_id);
create index if not exists idx_user_interests_interest_id on public.user_interests(interest_id);

-- 5. Seed Authoritative 18 Categories
insert into public.interest_categories (slug, name, icon, sort_order) values
  ('travel-exploring', 'Travel & Exploring', 'compass', 1),
  ('food-drink', 'Food & Drink', 'utensils', 2),
  ('music', 'Music', 'music', 3),
  ('movies-tv', 'Movies & Cinema', 'film', 4),
  ('books-ideas', 'Books & Literature', 'book-open', 5),
  ('creative', 'Creative & Making', 'palette', 6),
  ('culture-arts', 'Culture & Arts', 'landmark', 7),
  ('sports-fitness', 'Sports & Fitness', 'activity', 8),
  ('nature-outdoors', 'Nature & Outdoors', 'trees', 9),
  ('games', 'Gaming & Play', 'gamepad-2', 10),
  ('technology', 'Technology & Innovation', 'cpu', 11),
  ('science-space', 'Science & Space', 'atom', 12),
  ('astrology-spirituality', 'Astrology & Esotericism', 'sparkles', 13),
  ('wellness-mindfulness', 'Wellness & Mindfulness', 'heart', 14),
  ('fashion-style', 'Fashion & Style', 'shirt', 15),
  ('animals-pets', 'Animals & Pets', 'paw-print', 16),
  ('social-nightlife', 'Social & Nightlife', 'party-popper', 17),
  ('learning-life', 'Learning & Philosophy', 'brain', 18)
on conflict (slug) do nothing;

-- 6. Seed Curated Representative Candidate Pool (~21 Interests)
insert into public.interests (category_id, slug, name, sort_order)
select c.id, i.slug, i.name, i.sort_order
from (values
  ('travel-exploring', 'travel', 'Travel', 1),
  ('food-drink', 'coffee', 'Coffee', 2),
  ('music', 'music', 'Music', 3),
  ('creative', 'photography', 'Photography', 4),
  ('movies-tv', 'cinema', 'Cinema', 5),
  ('books-ideas', 'books', 'Books', 6),
  ('astrology-spirituality', 'astrology', 'Astrology', 7),
  ('food-drink', 'food', 'Food & Dining', 8),
  ('nature-outdoors', 'hiking', 'Hiking & Trekking', 9),
  ('culture-arts', 'art', 'Visual Art & Galleries', 10),
  ('sports-fitness', 'fitness', 'Fitness & Training', 11),
  ('animals-pets', 'pets', 'Pets & Animals', 12),
  ('technology', 'technology', 'Technology & Tech', 13),
  ('games', 'gaming', 'Video Games & Gaming', 14),
  ('fashion-style', 'fashion', 'Fashion & Style', 15),
  ('nature-outdoors', 'nature', 'Nature & Outdoors', 16),
  ('culture-arts', 'theatre', 'Theatre & Performing Arts', 17),
  ('creative', 'writing', 'Writing & Journaling', 18),
  ('learning-life', 'psychology', 'Psychology & Human Nature', 19),
  ('music', 'concerts', 'Live Concerts & Festivals', 20),
  ('learning-life', 'philosophy', 'Philosophy & Deep Talks', 21)
) as i(category_slug, slug, name, sort_order)
join public.interest_categories c on c.slug = i.category_slug
on conflict (slug) do nothing;

-- 7. Row Level Security
alter table public.interest_categories enable row level security;
alter table public.interests enable row level security;
alter table public.user_interests enable row level security;

-- Policies: Interest Categories (Public Read)
drop policy if exists interest_categories_select on public.interest_categories;
create policy interest_categories_select
  on public.interest_categories
  for select
  using (true);

-- Policies: Interests (Public Read)
drop policy if exists interests_select on public.interests;
create policy interests_select
  on public.interests
  for select
  using (true);

-- Policies: User Interests (Authenticated Read, Owner Write)
drop policy if exists user_interests_select on public.user_interests;
create policy user_interests_select
  on public.user_interests
  for select
  to authenticated
  using (true);

drop policy if exists user_interests_insert on public.user_interests;
create policy user_interests_insert
  on public.user_interests
  for insert
  to authenticated
  with check (
    user_id = auth.uid()
  );

drop policy if exists user_interests_update on public.user_interests;
create policy user_interests_update
  on public.user_interests
  for update
  to authenticated
  using (
    user_id = auth.uid()
  )
  with check (
    user_id = auth.uid()
  );

drop policy if exists user_interests_delete on public.user_interests;
create policy user_interests_delete
  on public.user_interests
  for delete
  to authenticated
  using (
    user_id = auth.uid()
  );

-- 8. Grants
grant select on public.interest_categories, public.interests to authenticated, anon;
grant select, insert, update, delete on public.user_interests to authenticated;
