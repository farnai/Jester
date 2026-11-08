-- 034_interests_system_v2.sql
-- Upgrade canonical Interest Catalog to 9 categories and 79 interests.
-- Completely non-destructive: preserves existing IDs, slugs, and user_interests records.

BEGIN;

-- 1. Ensure localized and alias columns exist on public.interest_categories and public.interests
ALTER TABLE public.interest_categories
    ADD COLUMN IF NOT EXISTS name_ka TEXT,
    ADD COLUMN IF NOT EXISTS name_en TEXT;

ALTER TABLE public.interests
    ADD COLUMN IF NOT EXISTS name_ka TEXT,
    ADD COLUMN IF NOT EXISTS name_en TEXT,
    ADD COLUMN IF NOT EXISTS aliases TEXT[] DEFAULT '{}'::TEXT[];

-- 2. Upsert the 9 canonical categories (status = 'active')
INSERT INTO public.interest_categories (id, slug, name, name_ka, name_en, icon, sort_order, status)
VALUES (gen_random_uuid(), 'music-stage', 'მუსიკა და სცენა', 'მუსიკა და სცენა', 'Music & Stage', 'music', 10, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interest_categories (id, slug, name, name_ka, name_en, icon, sort_order, status)
VALUES (gen_random_uuid(), 'cinema-books-stories', 'კინო, წიგნები და ამბები', 'კინო, წიგნები და ამბები', 'Cinema, Books & Stories', 'film', 20, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interest_categories (id, slug, name, name_ka, name_en, icon, sort_order, status)
VALUES (gen_random_uuid(), 'art-creativity', 'ხელოვნება და შემოქმედება', 'ხელოვნება და შემოქმედება', 'Art & Creativity', 'palette', 30, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interest_categories (id, slug, name, name_ka, name_en, icon, sort_order, status)
VALUES (gen_random_uuid(), 'food-city', 'გემო და ქალაქი', 'გემო და ქალაქი', 'Taste & City Life', 'utensils', 40, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interest_categories (id, slug, name, name_ka, name_en, icon, sort_order, status)
VALUES (gen_random_uuid(), 'travel-nature', 'მოგზაურობა და ბუნება', 'მოგზაურობა და ბუნება', 'Travel & Outdoors', 'compass', 50, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interest_categories (id, slug, name, name_ka, name_en, icon, sort_order, status)
VALUES (gen_random_uuid(), 'sports-movement', 'სპორტი და მოძრაობა', 'სპორტი და მოძრაობა', 'Sports & Movement', 'dumbbell', 60, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interest_categories (id, slug, name, name_ka, name_en, icon, sort_order, status)
VALUES (gen_random_uuid(), 'games-tech', 'თამაშები და ტექნოლოგიები', 'თამაშები და ტექნოლოგიები', 'Gaming & Tech', 'gamepad', 70, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interest_categories (id, slug, name, name_ka, name_en, icon, sort_order, status)
VALUES (gen_random_uuid(), 'knowledge-mind', 'ცოდნა და თვითშემეცნება', 'ცოდნა და თვითშემეცნება', 'Knowledge & Self-Discovery', 'book-open', 80, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interest_categories (id, slug, name, name_ka, name_en, icon, sort_order, status)
VALUES (gen_random_uuid(), 'hobbies-lifestyle', 'ჰობები და ცხოვრების სტილი', 'ჰობები და ცხოვრების სტილი', 'Hobbies & Lifestyle', 'sparkles', 90, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';

-- 3. Deprecate any historical categories that are not part of the 9 canonical categories
UPDATE public.interest_categories
SET status = 'deprecated'
WHERE slug NOT IN ('music-stage', 'cinema-books-stories', 'art-creativity', 'food-city', 'travel-nature', 'sports-movement', 'games-tech', 'knowledge-mind', 'hobbies-lifestyle');

-- 4. Upsert/re-link the 79 canonical interests
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'music-stage'),
    'music',
    'მუსიკის მოსმენა',
    'მუსიკის მოსმენა',
    'Listening to Music',
    ARRAY['music', 'listening', 'სიმღერები', 'მელომანი']::TEXT[],
    10,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'music-stage'),
    'pop-music',
    'პოპ-მუსიკა',
    'პოპ-მუსიკა',
    'Pop Music',
    ARRAY['pop', 'pop music', 'პოპი']::TEXT[],
    20,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'music-stage'),
    'rock-indie',
    'როკი და ინდი',
    'როკი და ინდი',
    'Rock & Indie',
    ARRAY['rock', 'indie', 'როკ მუსიკა', 'ინდი']::TEXT[],
    30,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'music-stage'),
    'electronic-music',
    'ელექტრონული მუსიკა',
    'ელექტრონული მუსიკა',
    'Electronic Music',
    ARRAY['electronic', 'techno', 'house', 'edm', 'ტექნო', 'ელექტრო']::TEXT[],
    40,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'music-stage'),
    'hiphop-rnb',
    'ჰიპ-ჰოპი და R&B',
    'ჰიპ-ჰოპი და R&B',
    'Hip-Hop & R&B',
    ARRAY['hiphop', 'rap', 'rnb', 'რეპი', 'ჰიპ-ჰოპი']::TEXT[],
    50,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'music-stage'),
    'jazz-blues',
    'ჯაზი და ბლუზი',
    'ჯაზი და ბლუზი',
    'Jazz & Blues',
    ARRAY['jazz', 'blues', 'ჯაზი']::TEXT[],
    60,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'music-stage'),
    'classical-music',
    'კლასიკური მუსიკა',
    'კლასიკური მუსიკა',
    'Classical Music',
    ARRAY['classical', 'orchestra', 'კლასიკა']::TEXT[],
    70,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'music-stage'),
    'concerts',
    'კონცერტები',
    'კონცერტები',
    'Concerts & Festivals',
    ARRAY['concerts', 'gigs', 'festivals', 'ფესტივალები', 'ლაივები']::TEXT[],
    80,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'music-stage'),
    'music-production',
    'მუსიკის შექმნა',
    'მუსიკის შექმნა',
    'Music Production',
    ARRAY['producing', 'dj', 'songwriting', 'სიმღერის შექმნა', 'დაკვრა']::TEXT[],
    90,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'cinema-books-stories'),
    'cinema',
    'კინო',
    'კინო',
    'Cinema & Movies',
    ARRAY['movies', 'film', 'cinema', 'ფილმები', 'კინემატოგრაფი']::TEXT[],
    10,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'cinema-books-stories'),
    'tv-series',
    'სერიალები',
    'სერიალები',
    'TV Shows & Series',
    ARRAY['series', 'tv shows', 'netflix', 'bingewatching']::TEXT[],
    20,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'cinema-books-stories'),
    'anime',
    'ანიმე',
    'ანიმე',
    'Anime',
    ARRAY['anime', 'animation', 'ანიმაცია', 'მანგა']::TEXT[],
    30,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'cinema-books-stories'),
    'documentaries',
    'დოკუმენტური ფილმები',
    'დოკუმენტური ფილმები',
    'Documentaries',
    ARRAY['docs', 'documentary', 'დოკუმენტური']::TEXT[],
    40,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'cinema-books-stories'),
    'books',
    'წიგნები და ლიტერატურა',
    'წიგნები და ლიტერატურა',
    'Books & Literature',
    ARRAY['books', 'reading', 'literature', 'კითხვა', 'ლიტერატურა']::TEXT[],
    50,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'cinema-books-stories'),
    'scifi-fantasy',
    'ფენტეზი და სამეცნიერო ფანტასტიკა',
    'ფენტეზი და სამეცნიერო ფანტასტიკა',
    'Sci-Fi & Fantasy',
    ARRAY['fantasy', 'sci-fi', 'science fiction', 'ფანტასტიკა']::TEXT[],
    60,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'cinema-books-stories'),
    'thrillers-mysteries',
    'დეტექტივები და თრილერები',
    'დეტექტივები და თრილერები',
    'Mysteries & Thrillers',
    ARRAY['thriller', 'detective', 'mystery', 'დეტექტივი', 'თრილერი']::TEXT[],
    70,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'cinema-books-stories'),
    'theatre',
    'თეატრი',
    'თეატრი',
    'Theatre',
    ARRAY['theatre', 'theater', 'drama', 'სპექტაკლი', 'დრამა']::TEXT[],
    80,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'cinema-books-stories'),
    'podcasts',
    'პოდკასტები',
    'პოდკასტები',
    'Podcasts',
    ARRAY['podcasts', 'podcast', 'პოდკასტი']::TEXT[],
    90,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'art-creativity'),
    'photography',
    'ფოტოგრაფია',
    'ფოტოგრაფია',
    'Photography',
    ARRAY['photo', 'photography', 'photos', 'ფოტო']::TEXT[],
    10,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'art-creativity'),
    'drawing-illustration',
    'ხატვა და ილუსტრაცია',
    'ხატვა და ილუსტრაცია',
    'Drawing & Illustration',
    ARRAY['drawing', 'painting', 'illustration', 'sketching', 'ხატვა']::TEXT[],
    20,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'art-creativity'),
    'graphic-design',
    'გრაფიკული დიზაინი',
    'გრაფიკული დიზაინი',
    'Graphic Design',
    ARRAY['design', 'graphic design', 'ui', 'visual art', 'დიზაინი']::TEXT[],
    30,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'art-creativity'),
    'writing',
    'მწერლობა',
    'მწერლობა',
    'Writing & Poetry',
    ARRAY['writing', 'poetry', 'creative writing', 'პოეზია', 'პროზა']::TEXT[],
    40,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'art-creativity'),
    'art',
    'მუზეუმები და გალერეები',
    'მუზეუმები და გალერეები',
    'Museums & Galleries',
    ARRAY['museums', 'galleries', 'exhibitions', 'art', 'ხელოვნება', 'გამოფენები']::TEXT[],
    50,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'art-creativity'),
    'architecture',
    'არქიტექტურა',
    'არქიტექტურა',
    'Architecture',
    ARRAY['architecture', 'urban design', 'არქიტექტურა']::TEXT[],
    60,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'art-creativity'),
    'crafts-handmade',
    'ხელნაკეთი ნივთები',
    'ხელნაკეთი ნივთები',
    'Crafts & Handmade',
    ARRAY['crafts', 'handmade', 'diy', 'ქსოვა', 'კერვა']::TEXT[],
    70,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'art-creativity'),
    'dance',
    'ცეკვა',
    'ცეკვა',
    'Dance',
    ARRAY['dance', 'dancing', 'ცეკვა', 'ქორეოგრაფია']::TEXT[],
    80,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'food-city'),
    'coffee',
    'ყავა და კაფეები',
    'ყავა და კაფეები',
    'Coffee & Cafes',
    ARRAY['coffee', 'cafes', 'espresso', 'ყავა', 'კაფე']::TEXT[],
    10,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'food-city'),
    'food',
    'რესტორნების აღმოჩენა',
    'რესტორნების აღმოჩენა',
    'Dining Out & Foodies',
    ARRAY['food', 'restaurants', 'dining', 'gourmet', 'გასტრონომია', 'კვება']::TEXT[],
    20,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'food-city'),
    'home-cooking',
    'სახლის კულინარია',
    'სახლის კულინარია',
    'Home Cooking',
    ARRAY['cooking', 'culinary', 'recipes', 'კულინარია', 'საჭმლის მომზადება']::TEXT[],
    30,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'food-city'),
    'baking-desserts',
    'ცხობა და დესერტები',
    'ცხობა და დესერტები',
    'Baking & Desserts',
    ARRAY['baking', 'pastry', 'desserts', 'sweets', 'ტკბილეული', 'ცხობა']::TEXT[],
    40,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'food-city'),
    'street-food',
    'ქუჩის საკვები',
    'ქუჩის საკვები',
    'Street Food',
    ARRAY['street food', 'fast food', 'ქუჩის საჭმელი']::TEXT[],
    50,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'food-city'),
    'georgian-cuisine',
    'ქართული სამზარეულო',
    'ქართული სამზარეულო',
    'Georgian Cuisine',
    ARRAY['georgian food', 'supra', 'khinkali', 'khachapuri', 'სუფრა', 'ხინკალი', 'ხაჭაპური']::TEXT[],
    60,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'food-city'),
    'asian-cuisine',
    'აზიური სამზარეულო',
    'აზიური სამზარეულო',
    'Asian Cuisine',
    ARRAY['asian food', 'sushi', 'ramen', 'სუში', 'რამენი']::TEXT[],
    70,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'food-city'),
    'wine-tasting',
    'ღვინის დეგუსტაცია',
    'ღვინის დეგუსტაცია',
    'Wine Tasting',
    ARRAY['wine', 'wine tasting', 'sommelier', 'ღვინო', 'მეღვინეობა']::TEXT[],
    80,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'food-city'),
    'nightlife',
    'ღამის ცხოვრება',
    'ღამის ცხოვრება',
    'Nightlife & Bars',
    ARRAY['nightlife', 'bars', 'clubs', 'ბარები', 'კლუბები', 'გართობა']::TEXT[],
    90,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'travel-nature'),
    'travel',
    'მოგზაურობა',
    'მოგზაურობა',
    'Travel',
    ARRAY['travel', 'trips', 'exploring', 'wandering', 'ტურიზმი']::TEXT[],
    10,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'travel-nature'),
    'hiking',
    'ლაშქრობა',
    'ლაშქრობა',
    'Hiking & Trekking',
    ARRAY['hiking', 'trekking', 'mountains', 'მთები', 'ლაშქრობა']::TEXT[],
    20,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'travel-nature'),
    'camping',
    'კემპინგი',
    'კემპინგი',
    'Camping',
    ARRAY['camping', 'tents', 'campfire', 'კარავი', 'დაბანაკება']::TEXT[],
    30,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'travel-nature'),
    'nature',
    'ბუნებაში გასვლა',
    'ბუნებაში გასვლა',
    'Nature & Outdoors',
    ARRAY['nature', 'outdoors', 'fresh air', 'პიკნიკი', 'სიმწვანე']::TEXT[],
    40,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'travel-nature'),
    'beach-coast',
    'ზღვა და სანაპირო',
    'ზღვა და სანაპირო',
    'Beach & Coast',
    ARRAY['beach', 'sea', 'coast', 'ocean', 'ზღვა', 'სანაპირო', 'პლაჟი']::TEXT[],
    50,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'travel-nature'),
    'mountain-retreats',
    'მთაში დასვენება',
    'მთაში დასვენება',
    'Mountain Retreats',
    ARRAY['mountains', 'mountain cabin', 'alpine', 'მთა', 'ალპური']::TEXT[],
    60,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'travel-nature'),
    'road-trips',
    'საგზაო მოგზაურობები',
    'საგზაო მოგზაურობები',
    'Road Trips',
    ARRAY['road trips', 'road trip', 'driving', 'როუდტრიპი']::TEXT[],
    70,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'travel-nature'),
    'city-exploring',
    'ქალაქების აღმოჩენა',
    'ქალაქების აღმოჩენა',
    'City Breaks & Urban Exploring',
    ARRAY['city exploring', 'urban exploration', 'sightseeing', 'ქალაქის ტურიზმი']::TEXT[],
    80,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'travel-nature'),
    'wildlife',
    'ველური ბუნება',
    'ველური ბუნება',
    'Wildlife & National Parks',
    ARRAY['wildlife', 'national parks', 'flora', 'fauna', 'ნაკრძალები', 'ფაუნა']::TEXT[],
    90,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'sports-movement'),
    'fitness',
    'ფიტნესი და დარბაზი',
    'ფიტნესი და დარბაზი',
    'Fitness & Gym',
    ARRAY['fitness', 'gym', 'workout', 'ვარჯიში', 'დარბაზი', 'ფიტნესი']::TEXT[],
    10,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'sports-movement'),
    'football',
    'ფეხბურთი',
    'ფეხბურთი',
    'Football / Soccer',
    ARRAY['football', 'soccer', 'ფეხბურთი']::TEXT[],
    20,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'sports-movement'),
    'basketball',
    'კალათბურთი',
    'კალათბურთი',
    'Basketball',
    ARRAY['basketball', 'nba', 'კალათბურთი']::TEXT[],
    30,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'sports-movement'),
    'running',
    'სირბილი',
    'სირბილი',
    'Running & Jogging',
    ARRAY['running', 'jogging', 'marathon', 'სირბილი', 'მარათონი']::TEXT[],
    40,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'sports-movement'),
    'swimming',
    'ცურვა',
    'ცურვა',
    'Swimming',
    ARRAY['swimming', 'pool', 'ცურვა', 'აუზი']::TEXT[],
    50,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'sports-movement'),
    'cycling',
    'ველოსიპედი',
    'ველოსიპედი',
    'Cycling',
    ARRAY['cycling', 'bike', 'bicycle', 'ველო', 'ველოსიპედი']::TEXT[],
    60,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'sports-movement'),
    'yoga-pilates',
    'იოგა და პილატესი',
    'იოგა და პილატესი',
    'Yoga & Pilates',
    ARRAY['yoga', 'pilates', 'stretching', 'იოგა', 'პილატესი', 'გაწელვები']::TEXT[],
    70,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'sports-movement'),
    'tennis',
    'ჩოგბურთი',
    'ჩოგბურთი',
    'Tennis & Padel',
    ARRAY['tennis', 'padel', 'racket', 'ჩოგბურთი', 'პადელი']::TEXT[],
    80,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'sports-movement'),
    'winter-sports',
    'ზამთრის სპორტი',
    'ზამთრის სპორტი',
    'Winter Sports',
    ARRAY['skiing', 'snowboard', 'winter sports', 'თხილამურები', 'სნოუბორდი']::TEXT[],
    90,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'games-tech'),
    'gaming',
    'ვიდეოთამაშები',
    'ვიდეოთამაშები',
    'Video Games',
    ARRAY['games', 'gaming', 'video games', 'playstation', 'pc games', 'გეიმინგი', 'თამაშები']::TEXT[],
    10,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'games-tech'),
    'board-games',
    'სამაგიდო თამაშები',
    'სამაგიდო თამაშები',
    'Board Games',
    ARRAY['board games', 'tabletop', 'სამაგიდო', 'სამაგიდო თამაშები']::TEXT[],
    20,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'games-tech'),
    'puzzles-quizzes',
    'თავსატეხები',
    'თავსატეხები',
    'Puzzles & Quizzes',
    ARRAY['puzzles', 'brain teasers', 'quizzes', 'sudoku', 'კროსვორდები', 'ვიქტორინა']::TEXT[],
    30,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'games-tech'),
    'technology',
    'ტექნოლოგიები',
    'ტექნოლოგიები',
    'Technology & Gadgets',
    ARRAY['tech', 'technology', 'gadgets', 'ტექნოლოგია', 'გაჯეტები']::TEXT[],
    40,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'games-tech'),
    'programming',
    'პროგრამირება',
    'პროგრამირება',
    'Programming & Development',
    ARRAY['coding', 'programming', 'developer', 'software', 'კოდირება', 'დეველოპმენტი']::TEXT[],
    50,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'games-tech'),
    'artificial-intelligence',
    'ხელოვნური ინტელექტი',
    'ხელოვნური ინტელექტი',
    'Artificial Intelligence',
    ARRAY['ai', 'artificial intelligence', 'llm', 'ml', 'მანქანური სწავლება']::TEXT[],
    60,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'games-tech'),
    'startups',
    'სტარტაპები',
    'სტარტაპები',
    'Startups & Innovation',
    ARRAY['startups', 'entrepreneurship', 'business', 'სტარტაპი', 'ბიზნესი']::TEXT[],
    70,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'games-tech'),
    'esports',
    'კიბერსპორტი',
    'კიბერსპორტი',
    'Esports',
    ARRAY['esports', 'competitive gaming', 'კიბერსპორტი']::TEXT[],
    80,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'knowledge-mind'),
    'psychology',
    'ფსიქოლოგია',
    'ფსიქოლოგია',
    'Psychology',
    ARRAY['psychology', 'therapy', 'mental health', 'ფსიქოლოგია', 'მენტალური ჯანმრთელობა']::TEXT[],
    10,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'knowledge-mind'),
    'philosophy',
    'ფილოსოფია',
    'ფილოსოფია',
    'Philosophy',
    ARRAY['philosophy', 'ethics', 'ideas', 'ფილოსოფია', 'აზროვნება']::TEXT[],
    20,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'knowledge-mind'),
    'history',
    'ისტორია',
    'ისტორია',
    'History',
    ARRAY['history', 'historical', 'archaeology', 'ისტორია', 'არქეოლოგია']::TEXT[],
    30,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'knowledge-mind'),
    'science',
    'მეცნიერება',
    'მეცნიერება',
    'Science',
    ARRAY['science', 'physics', 'biology', 'chemistry', 'მეცნიერება']::TEXT[],
    40,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'knowledge-mind'),
    'space-astronomy',
    'კოსმოსი და ასტრონომია',
    'კოსმოსი და ასტრონომია',
    'Space & Astronomy',
    ARRAY['space', 'astronomy', 'universe', 'cosmos', 'კოსმოსი', 'ასტრონომია']::TEXT[],
    50,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'knowledge-mind'),
    'languages',
    'უცხო ენები',
    'უცხო ენები',
    'Languages & Linguistics',
    ARRAY['languages', 'linguistics', 'polyglot', 'უცხო ენები', 'ენათმეცნიერება']::TEXT[],
    60,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'knowledge-mind'),
    'astrology',
    'ასტროლოგია',
    'ასტროლოგია',
    'Astrology',
    ARRAY['astrology', 'zodiac', 'horoscopes', 'natal chart', 'ზოდიაქო', 'ასტროლოგია']::TEXT[],
    70,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'knowledge-mind'),
    'meditation',
    'მედიტაცია',
    'მედიტაცია',
    'Mindfulness & Meditation',
    ARRAY['meditation', 'mindfulness', 'zen', 'მედიტაცია', 'ზენი']::TEXT[],
    80,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'knowledge-mind'),
    'personal-growth',
    'თვითგანვითარება',
    'თვითგანვითარება',
    'Personal Growth',
    ARRAY['self improvement', 'personal growth', 'productivity', 'თვითგანვითარება', 'პროდუქტიულობა']::TEXT[],
    90,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'hobbies-lifestyle'),
    'pets',
    'შინაური ცხოველები',
    'შინაური ცხოველები',
    'Pets & Animals',
    ARRAY['pets', 'dogs', 'cats', 'animals', 'ძაღლები', 'კატები', 'ცხოველები']::TEXT[],
    10,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'hobbies-lifestyle'),
    'gardening-plants',
    'მებაღეობა და მცენარეები',
    'მებაღეობა და მცენარეები',
    'Gardening & Houseplants',
    ARRAY['gardening', 'plants', 'flowers', 'მცენარეები', 'მებაღეობა', 'ყვავილები']::TEXT[],
    20,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'hobbies-lifestyle'),
    'fashion',
    'მოდა და სტილი',
    'მოდა და სტილი',
    'Fashion & Style',
    ARRAY['fashion', 'style', 'outfits', 'streetwear', 'მოდა', 'სტილი', 'ჩაცმულობა']::TEXT[],
    30,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'hobbies-lifestyle'),
    'vintage-thrift',
    'ვინტაჟური ნივთები',
    'ვინტაჟური ნივთები',
    'Vintage & Thrift',
    ARRAY['vintage', 'thrift', 'retro', 'antiques', 'ვინტაჟი', 'რეტრო', 'მეორადი']::TEXT[],
    40,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'hobbies-lifestyle'),
    'volunteering',
    'მოხალისეობა',
    'მოხალისეობა',
    'Volunteering & Community',
    ARRAY['volunteering', 'charity', 'social impact', 'ქველმოქმედება', 'მოხალისეობა']::TEXT[],
    50,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'hobbies-lifestyle'),
    'cars-motorsport',
    'ავტომობილები',
    'ავტომობილები',
    'Cars & Motorsport',
    ARRAY['cars', 'automotive', 'motorsport', 'f1', 'მანქანები', 'ავტო']::TEXT[],
    60,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'hobbies-lifestyle'),
    'home-diy',
    'სახლის პროექტები (DIY)',
    'სახლის პროექტები (DIY)',
    'Home Improvement / DIY',
    ARRAY['diy', 'interior design', 'home decor', 'რემონტი', 'ინტერიერი']::TEXT[],
    70,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'hobbies-lifestyle'),
    'tarot-symbolism',
    'ტარო და სიმბოლიზმი',
    'ტარო და სიმბოლიზმი',
    'Tarot & Symbolism',
    ARRAY['tarot', 'mysticism', 'symbols', 'ტარო', 'მისტიკა', 'სიმბოლოები']::TEXT[],
    80,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.interests (id, category_id, slug, name, name_ka, name_en, aliases, sort_order, status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM public.interest_categories WHERE slug = 'hobbies-lifestyle'),
    'comics-manga',
    'კომიქსები და მანგა',
    'კომიქსები და მანგა',
    'Comics & Manga',
    ARRAY['comics', 'manga', 'marvel', 'dc', 'კომიქსი', 'მანგა']::TEXT[],
    90,
    'active'
)
ON CONFLICT (slug) DO UPDATE SET
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    sort_order = EXCLUDED.sort_order,
    status = 'active';

COMMIT;
