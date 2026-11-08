-- 035_onboarding_v3_enrichment.sql
-- Introduces Personality Descriptors and Connection Intentions catalogs, user relations, and visibility settings.
-- Completely non-destructive: zero deletion, idempotent.

BEGIN;

-- 1. Visibility columns on public.profiles
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS personality_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (personality_visibility IN ('public', 'connections_only', 'private')),
    ADD COLUMN IF NOT EXISTS intentions_visibility TEXT NOT NULL DEFAULT 'public'
        CHECK (intentions_visibility IN ('public', 'connections_only', 'private'));

-- 2. Personality Descriptors Catalog
CREATE TABLE IF NOT EXISTS public.personality_traits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_ka TEXT NOT NULL,
    name_en TEXT NOT NULL,
    sort_order INT DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'deprecated')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. User Personality Selections
CREATE TABLE IF NOT EXISTS public.user_personality_traits (
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    trait_id UUID NOT NULL REFERENCES public.personality_traits(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, trait_id)
);

-- 4. Connection Intentions Catalog
CREATE TABLE IF NOT EXISTS public.connection_intentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_ka TEXT NOT NULL,
    name_en TEXT NOT NULL,
    icon TEXT,
    sort_order INT DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'deprecated')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. User Connection Intentions Selections
CREATE TABLE IF NOT EXISTS public.user_connection_intentions (
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    intention_id UUID NOT NULL REFERENCES public.connection_intentions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, intention_id)
);

-- 6. Grants & RLS Policies
ALTER TABLE public.personality_traits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_personality_traits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.connection_intentions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_connection_intentions ENABLE ROW LEVEL SECURITY;

GRANT SELECT ON public.personality_traits, public.connection_intentions TO authenticated, anon;
GRANT ALL ON public.user_personality_traits, public.user_connection_intentions TO authenticated, service_role;

-- RLS: Read public catalogs
DROP POLICY IF EXISTS personality_traits_read_all ON public.personality_traits;
CREATE POLICY personality_traits_read_all ON public.personality_traits FOR SELECT USING (true);

DROP POLICY IF EXISTS connection_intentions_read_all ON public.connection_intentions;
CREATE POLICY connection_intentions_read_all ON public.connection_intentions FOR SELECT USING (true);

-- RLS: User Personality Traits (Owner full access, viewers subject to visibility)
DROP POLICY IF EXISTS user_personality_traits_owner ON public.user_personality_traits;
CREATE POLICY user_personality_traits_owner ON public.user_personality_traits
    FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS user_personality_traits_viewer ON public.user_personality_traits;
CREATE POLICY user_personality_traits_viewer ON public.user_personality_traits
    FOR SELECT USING (
        auth.uid() = user_id
        OR EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = user_personality_traits.user_id
              AND (
                p.personality_visibility = 'public'
                OR (
                    p.personality_visibility = 'connections_only'
                    AND EXISTS (
                        SELECT 1 FROM public.connections c
                        WHERE c.status = 'accepted'
                          AND ((c.user_a_id = auth.uid() AND c.user_b_id = p.id) OR (c.user_b_id = auth.uid() AND c.user_a_id = p.id))
                    )
                )
              )
        )
    );

-- RLS: User Connection Intentions (Owner full access, viewers subject to visibility)
DROP POLICY IF EXISTS user_connection_intentions_owner ON public.user_connection_intentions;
CREATE POLICY user_connection_intentions_owner ON public.user_connection_intentions
    FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS user_connection_intentions_viewer ON public.user_connection_intentions;
CREATE POLICY user_connection_intentions_viewer ON public.user_connection_intentions
    FOR SELECT USING (
        auth.uid() = user_id
        OR EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = user_connection_intentions.user_id
              AND (
                p.intentions_visibility = 'public'
                OR (
                    p.intentions_visibility = 'connections_only'
                    AND EXISTS (
                        SELECT 1 FROM public.connections c
                        WHERE c.status = 'accepted'
                          AND ((c.user_a_id = auth.uid() AND c.user_b_id = p.id) OR (c.user_b_id = auth.uid() AND c.user_a_id = p.id))
                    )
                )
              )
        )
    );

-- 7. Seed Personality Descriptors
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('communicative', 'კომუნიკაბელური', 'კომუნიკაბელური', 'Outgoing & Communicative', 10, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('observant', 'დამკვირვებელი', 'დამკვირვებელი', 'Thoughtful Observer', 20, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('spontaneous', 'სპონტანური', 'სპონტანური', 'Spontaneous & Adventurous', 30, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('calm', 'მშვიდი', 'მშვიდი', 'Calm & Grounded', 40, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('empathetic', 'ემპათიური', 'ემპათიური', 'Empathetic & Caring', 50, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('creative', 'კრეატიული', 'კრეატიული', 'Creative & Imaginative', 60, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('curious', 'ცნობისმოყვარე', 'ცნობისმოყვარე', 'Curious & Open-Minded', 70, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('energetic', 'ენერგიული', 'ენერგიული', 'Energetic & Dynamic', 80, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('practical', 'პრაქტიკული', 'პრაქტიკული', 'Practical & Realistic', 90, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('idealistic', 'იდეალისტი', 'იდეალისტი', 'Idealistic & Dreamer', 100, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('playful', 'მხიარული', 'მხიარული', 'Humorous & Playful', 110, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('independent', 'დამოუკიდებელი', 'დამოუკიდებელი', 'Independent & Self-Reliant', 120, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('attentive', 'ყურადღებიანი', 'ყურადღებიანი', 'Attentive & Listener', 130, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.personality_traits (slug, name, name_ka, name_en, sort_order, status)
VALUES ('deep-thinker', 'სიღრმისეული', 'სიღრმისეული', 'Deep Thinker', 140, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    status = 'active';

-- 8. Seed Connection Intentions
INSERT INTO public.connection_intentions (slug, name, name_ka, name_en, icon, sort_order, status)
VALUES ('new-friends', 'ახალი მეგობრები', 'ახალი მეგობრები', 'Making New Friends', '🤝', 10, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.connection_intentions (slug, name, name_ka, name_en, icon, sort_order, status)
VALUES ('meaningful-conversations', 'საინტერესო საუბრები', 'საინტერესო საუბრები', 'Meaningful Conversations', '💬', 20, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.connection_intentions (slug, name, name_ka, name_en, icon, sort_order, status)
VALUES ('romantic-connection', 'რომანტიკული ურთიერთობა', 'რომანტიკული ურთიერთობა', 'Romantic Connection', '✨', 30, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.connection_intentions (slug, name, name_ka, name_en, icon, sort_order, status)
VALUES ('collaborators', 'თანამოაზრეები და იდეები', 'თანამოაზრეები და იდეები', 'Collaborators & Co-creators', '💡', 40, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.connection_intentions (slug, name, name_ka, name_en, icon, sort_order, status)
VALUES ('activity-partner', 'აქტივობების პარტნიორი', 'აქტივობების პარტნიორი', 'Activity & Hobby Partner', '🎯', 50, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';
INSERT INTO public.connection_intentions (slug, name, name_ka, name_en, icon, sort_order, status)
VALUES ('just-exploring', 'ჯერ ვათვალიერებ', 'ჯერ ვათვალიერებ', 'Just Exploring / Open-Minded', '👀', 60, 'active')
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    name_ka = EXCLUDED.name_ka,
    name_en = EXCLUDED.name_en,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order,
    status = 'active';

COMMIT;