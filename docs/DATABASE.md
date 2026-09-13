# Jester — Database Documentation & Migrations Guide

## 🗄️ Database Architecture Overview

Jester uses **PostgreSQL 15+** managed via **Supabase**. The database structure includes 11 application tables, multiple security-definer helper functions, triggers for automated timestamping and data versioning, and strict Row-Level Security (RLS) policies.

---

## 🔒 Data Classification

To maintain privacy and prevent data leakage, data is partitioned into 4 access classification tiers:

| Tier | Target Tables / Views | Access Scope | Enforced By |
| :--- | :--- | :--- | :--- |
| **PUBLIC** | `profiles`, `interest_categories`, `interests`, `interest_aliases`, `interest_relations`, `geo_countries`, `geo_cities`, `geo_city_aliases`, `lifestyle_categories`, `lifestyle_options`, `values_categories`, `values_options`, `value_relations`, `social_categories`, `social_options`, `social_relations` | Authenticated users (profile discoverable and not blocked; taxonomy, geo, lifestyle, values & social options publicly readable). | RLS policies |
| **SAFE DERIVED** | `astro_safe_profile`, `user_interests`, `user_lifestyle`, `user_values`, `user_social_preferences` | High-level summary (signs, element, modality, declared interests, safe location, safe cadence pills, guiding compass values, social rhythm). Authenticated users. | RLS policies |
| **PRIVATE** | `birth_data`, `connections`, `conversations`, `messages`, `daily_energies`, `notifications` | Owner or active connected participants only. | RLS policies + security-definer functions |
| **SERVICE-ONLY** | `astro_private`, `user_interest_affinity`, `user_location_private` | Server-side calculation & recommendation engine ONLY. Never exposed to client. | `REVOKE ALL` from client roles / RLS restriction |

---

## 📜 Complete Migration Inventory (001 – 021)

### `001_extensions.sql`
- **Purpose**: Enables required PostgreSQL extensions.
- **Extensions**: `uuid-ossp` (UUID generation), `pgcrypto` (cryptographic primitives).

### `002_enums.sql`
- **Purpose**: Defines custom domain Enum types.
- **Enums**:
  - `birth_time_precision`: `'exact'`, `'approximate'`, `'unknown'`
  - `connection_status`: `'pending'`, `'accepted'`, `'declined'`, `'blocked'`, `'removed'`
  - `conversation_type`: `'direct'`, `'group'`
  - `notification_type`: `'connection_request'`, `'connection_accepted'`, `'daily_energy'`, `'system'`

### `003_profiles.sql`
- **Purpose**: User profile table linked to Supabase Auth (`auth.users`).
- **Table**: `public.profiles` (`id uuid primary key references auth.users(id)`, `display_name`, `avatar_url`, `bio`, `city`, `occupation`, `timezone`, `is_discoverable boolean default true`).

### `004_birth_data.sql`
- **Purpose**: Private raw birth parameters.
- **Table**: `public.birth_data` (`user_id uuid primary key`, `birth_date date`, `birth_time time`, `birth_time_precision`, `birth_timezone text`, `latitude double precision`, `longitude double precision`, `place_label text`, `data_version integer default 1`).
- **Constraints**: Enforces `birth_time_precision_consistency` (time must be NULL if precision is unknown).

### `005_astro_private.sql`
- **Purpose**: Raw astronomical planet longitudes and houses.
- **Table**: `public.astro_private` (`user_id uuid primary key`, `sun_longitude` ... `pluto_longitude`, `ascendant_longitude`, `houses jsonb`, `retrogrades jsonb`, `source_birth_data_version`, `engine_version`).
- **Security**: Strictly server-side only. Client access revoked in migration 017.

### `006_astro_safe_profile.sql`
- **Purpose**: Safe derived non-sensitive astrology profile.
- **Table**: `public.astro_safe_profile` (`user_id uuid primary key`, `sun_sign`, `moon_sign`, `ascendant_sign`, `element_primary`, `modality_primary`, `source_birth_data_version`, `engine_version`).

### `007_connections.sql`
- **Purpose**: Friendship and relationship social graph.
- **Table**: `public.connections` (`id uuid`, `user_a_id uuid`, `user_b_id uuid`, `status`, `initiated_by uuid`, `blocked_by uuid`).
- **Constraint**: `canonical_user_pair_ordering CHECK (user_a_id < user_b_id)`. Prevents duplicate opposite-direction connection rows.

### `008_compatibility_results.sql`
- **Purpose**: Cached synastry compatibility calculation results.
- **Table**: `public.compatibility_results` (`user_a_id`, `user_b_id`, `score numeric(5,2)`, `signals jsonb`, `best_topics jsonb`, `conversation_starters jsonb`).

### `009_daily_energies.sql`
- **Purpose**: Personal daily transit energy index and summary.
- **Table**: `public.daily_energies` (`user_id`, `energy_date date`, `signals jsonb`, `interpretation jsonb`).

### `010_conversations.sql`
- **Purpose**: Chat conversation threads.
- **Table**: `public.conversations` (`id uuid`, `conversation_type`, `created_by uuid`).

### `011_conversation_members.sql`
- **Purpose**: Junction table linking users to conversations.
- **Table**: `public.conversation_members` (`conversation_id uuid`, `user_id uuid`).

### `012_messages.sql`
- **Purpose**: Individual chat messages.
- **Table**: `public.messages` (`id uuid`, `conversation_id uuid`, `sender_user_id uuid`, `body text`, `read_at timestamptz`).

### `013_notifications.sql`
- **Purpose**: Push and in-app notifications.
- **Table**: `public.notifications` (`id uuid`, `user_id uuid`, `type`, `payload jsonb`, `read_at timestamptz`).

### `014_indexes.sql`
- **Purpose**: B-tree performance indexes.
- **Indexes**: `idx_connections_pair_status`, `idx_messages_conversation_created`, `idx_notifications_user_read`, `idx_profiles_discoverable`.

### `015_triggers.sql`
- **Purpose**: Automated database triggers.
- **Triggers**:
  - `update_profiles_updated_at`: Auto-updates `updated_at` timestamp.
  - `bump_birth_data_version`: Automatically increments `data_version` when birth date, time, timezone, latitude, or longitude are updated.

### `016_helper_functions.sql`
- **Purpose**: Security-Definer SQL functions with fixed `search_path = public, pg_temp`.
- **Functions**:
  - `has_active_connection(u1, u2)`: Returns true if users have an accepted, unblocked connection.
  - `is_user_blocked(u1, u2)`: Returns true if either user has blocked the other.
  - `is_active_direct_conversation(conv_id, user_id)`: Checks membership AND active connection status.

### `017_grants.sql`
- **Purpose**: Role-Based Access Control (RBAC).
- **Rules**:
  - `anon`: All access revoked on all tables.
  - `authenticated`: Granted `SELECT, INSERT, UPDATE` on `profiles`, `birth_data`; `SELECT` on `astro_safe_profile`, `compatibility_results`, `daily_energies`; `SELECT, INSERT` on `connections`, `messages`. Direct `UPDATE/DELETE` on `connections` is explicitly revoked.
  - `astro_private`: `REVOKE ALL` from `authenticated` and `anon`.

### `018_rls.sql`
- **Purpose**: Enables RLS on all 11 tables and establishes privacy policies.
- **Key Policies**:
  - `birth_data_select_own`: `user_id = auth.uid()`
  - `profiles_select`: Owner OR (`is_discoverable = true` AND NOT `is_user_blocked`).
  - `compatibility_results_select`: Participant AND `has_active_connection(user_a, user_b)`.
  - `messages_select_member`: `is_active_direct_conversation(conversation_id, auth.uid())`.

### `019_storage.sql`
- **Purpose**: Supabase Storage bucket policy setup for user avatar uploads.

### `020_realtime.sql`
- **Purpose**: Adds `messages` and `notifications` to `supabase_realtime` publication.

### `021_compatibility_evidence_trace.sql`
- **Purpose**: Adds dedicated JSONB `evidence_trace` column to `public.compatibility_results` for deterministic auditability and explainability of Synastry V1 calculations.

---

## 🌐 Interest Graph V1 Schema Specification (Architecture Blueprint)

*(Detailed Product & Platform Specification: [`docs/INTEREST_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/INTEREST_SYSTEM_V1_SPEC.md))*

The Interest System introduces 6 conceptual entities supporting canonical taxonomy management, graph edges, and dual-layer user affinity:

### 1. `public.interest_categories`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `name` TEXT NOT NULL,
- `slug` TEXT UNIQUE NOT NULL,
- `icon` TEXT,
- `sort_order` INT NOT NULL DEFAULT 0,
- `status` TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deprecated'))

### 2. `public.interests`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `category_id` UUID NOT NULL REFERENCES public.interest_categories(id) ON DELETE CASCADE,
- `name` TEXT NOT NULL,
- `slug` TEXT UNIQUE NOT NULL,
- `description` TEXT,
- `status` TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'hidden', 'deprecated'))

### 3. `public.interest_aliases`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `interest_id` UUID NOT NULL REFERENCES public.interests(id) ON DELETE CASCADE,
- `alias` TEXT NOT NULL,
- CONSTRAINT uq_interest_alias UNIQUE (interest_id, alias)

### 4. `public.interest_relations`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `interest_id` UUID NOT NULL REFERENCES public.interests(id) ON DELETE CASCADE,
- `related_interest_id` UUID NOT NULL REFERENCES public.interests(id) ON DELETE CASCADE,
- `relation_type` TEXT NOT NULL CHECK (relation_type IN ('sub_genre', 'semantic_peer', 'complementary', 'contextual')),
- `weight` NUMERIC(3,2) NOT NULL CHECK (weight >= 0.0 AND weight <= 1.0),
- CONSTRAINT uq_interest_relation UNIQUE (interest_id, related_interest_id),
- CONSTRAINT check_no_self_relation CHECK (interest_id != related_interest_id)

### 5. `public.user_interests`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `user_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `interest_id` UUID NOT NULL REFERENCES public.interests(id) ON DELETE RESTRICT,
- `type` TEXT NOT NULL CHECK (type IN ('primary', 'secondary')),
- `is_signature` BOOLEAN NOT NULL DEFAULT false,
- `source` TEXT NOT NULL DEFAULT 'declared' CHECK (source IN ('declared', 'profile_edit', 'prompt')),
- `visibility` TEXT NOT NULL DEFAULT 'public' CHECK (visibility IN ('public', 'connections_only', 'hidden')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT uq_user_interest UNIQUE (user_id, interest_id)

### 6. `public.user_interest_affinity`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `user_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `interest_id` UUID NOT NULL REFERENCES public.interests(id) ON DELETE RESTRICT,
- `score` NUMERIC(4,3) NOT NULL CHECK (score >= 0.0 AND score <= 1.0),
- `confidence` NUMERIC(4,3) NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
- `source` TEXT NOT NULL CHECK (source IN ('declared', 'prompt', 'conversation', 'behavioral', 'inferred')),
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT uq_user_interest_affinity UNIQUE (user_id, interest_id)
- *Security Note:* Classified as **SERVICE-ONLY / PRIVATE**. Client roles possess zero read permissions on this table; affinity scores power internal candidate generation and recommendation ranking only.

---

## 📍 Location & Origin System V1 Schema Specification (Architecture Blueprint)

To maintain normalized geographic data, support internationalization (Georgian & English), and ensure high-performance discovery queries without leaking exact coordinates, the Location System V1 defines the following canonical entities:

### 1. `public.geo_countries`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `iso_code` VARCHAR(2) NOT NULL UNIQUE,       -- 'GE', 'DE', 'US', etc.
- `name_en` VARCHAR(100) NOT NULL,              -- 'Georgia'
- `name_ka` VARCHAR(100) NOT NULL,              -- 'საქართველო'
- `phone_code` VARCHAR(10),                     -- '+995'
- `flag_emoji` VARCHAR(10),                     -- '🇬🇪'
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 2. `public.geo_cities`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `country_id` UUID NOT NULL REFERENCES public.geo_countries(id) ON DELETE RESTRICT,
- `name_en` VARCHAR(100) NOT NULL,              -- 'Tbilisi'
- `name_ka` VARCHAR(100) NOT NULL,              -- 'თბილისი'
- `slug` VARCHAR(120) NOT NULL UNIQUE,          -- 'ge-tbilisi'
- `region_en` VARCHAR(100),                     -- 'Tbilisi'
- `region_ka` VARCHAR(100),                     -- 'თბილისი'
- `latitude` DOUBLE PRECISION NOT NULL,         -- Canonical City Center Coordinate
- `longitude` DOUBLE PRECISION NOT NULL,        -- Canonical City Center Coordinate
- `timezone` VARCHAR(64) NOT NULL,              -- 'Asia/Tbilisi'
- `is_major_hub` BOOLEAN DEFAULT false,         -- True for quick onboarding chips (Tbilisi, Batumi, Kutaisi, Rustavi)
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 3. `public.geo_city_aliases`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `city_id` UUID NOT NULL REFERENCES public.geo_cities(id) ON DELETE CASCADE,
- `alias` VARCHAR(100) NOT NULL,                -- 'Tiflis', 'ტფილისი'
- `locale` VARCHAR(10) DEFAULT 'en',
- CONSTRAINT uq_geo_city_alias UNIQUE (city_id, alias)

### 4. `public.profiles` Location Extensions
- `current_city_id` UUID REFERENCES public.geo_cities(id) ON DELETE SET NULL,
- `current_country_id` UUID REFERENCES public.geo_countries(id) ON DELETE SET NULL,
- `hometown_city_id` UUID REFERENCES public.geo_cities(id) ON DELETE SET NULL,
- `hometown_country_id` UUID REFERENCES public.geo_countries(id) ON DELETE SET NULL,
- `hometown_visible` BOOLEAN NOT NULL DEFAULT true,
- `location_source` VARCHAR(30) NOT NULL DEFAULT 'manual' CHECK (location_source IN ('manual', 'device', 'imported', 'system_derived')),
- `location_updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 5. `public.user_location_private` (Deferred Service-Role Entity)
- `user_id` UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
- `device_latitude` DOUBLE PRECISION NOT NULL,
- `device_longitude` DOUBLE PRECISION NOT NULL,
- `accuracy_meters` DOUBLE PRECISION,
- `recorded_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Security Invariant:* Classified as **SERVICE-ONLY**. Client roles have zero privileges. Never exposed in public profile DTOs or normal discovery feeds.

---

## 🌿 Lifestyle System V1 Schema Specification (Architecture Blueprint)

To capture how users actually live (cadence, daily rhythm, activity pace, work environment, living reality) without cluttering profiles with unstructured strings or rigid questionnaires, the Lifestyle System V1 defines the following entities:

### 1. `public.lifestyle_categories`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'daily_rhythm', 'work_style', 'activity_pace', etc.
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 2. `public.lifestyle_options`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `category_id` UUID NOT NULL REFERENCES public.lifestyle_categories(id) ON DELETE CASCADE,
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'night_owl', 'early_bird', 'remote', etc.
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `badge_icon` VARCHAR(30),                    -- 'moon', 'sun', 'laptop', 'zap', etc.
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 3. `public.user_lifestyle` (Normalized Profile Extension)
- `user_id` UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
- `daily_rhythm` VARCHAR(40),                  -- e.g. 'early_bird', 'night_owl', 'flexible_rhythm'
- `activity_pace` VARCHAR(40),                 -- e.g. 'high_velocity', 'balanced_pace', 'relaxed_pace'
- `work_style` VARCHAR(40),                    -- e.g. 'remote', 'hybrid', 'on_site', 'student'
- `social_cadence` VARCHAR(40),                -- e.g. 'frequently_social', 'moderately_social', 'home_focused'
- `pet_status` VARCHAR(40),                    -- e.g. 'has_dog', 'has_cat', 'has_multiple_pets', 'pet_free'
- `living_situation` VARCHAR(40),              -- e.g. 'lives_alone', 'lives_with_roommates', 'lives_with_family'
- `drinking_habit` VARCHAR(40),                -- e.g. 'never', 'socially', 'regularly'
- `smoking_habit` VARCHAR(40),                 -- e.g. 'never', 'socially', 'regularly', 'trying_to_quit'
- `visibility_flags` JSONB NOT NULL DEFAULT '{
    "daily_rhythm": true,
    "activity_pace": true,
    "work_style": true,
    "social_cadence": true,
    "pet_status": true,
    "living_situation": false,
    "drinking": true,
    "smoking": true
}',
- `source` VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('onboarding_snapshot', 'profile_edit', 'inferred')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

---

## 💎 Values System V1 Schema Specification (Architecture Blueprint)

To capture what principles and priorities matter most to a person without turning values into a clinical personality test or psychological grading, the Values System V1 defines the following normalized entities:

### 1. `public.values_categories`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'personal_direction', 'intellectual_creative', 'relational_ethical', 'life_grounding', 'inner_spirit'
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 2. `public.values_options`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `category_id` UUID NOT NULL REFERENCES public.values_categories(id) ON DELETE CASCADE,
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'curiosity', 'growth', 'autonomy', 'honesty', etc.
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `definition_en` TEXT NOT NULL,
- `definition_ka` TEXT NOT NULL,
- `badge_icon` VARCHAR(30),                    -- 'compass', 'seedling', 'shield', 'diamond', etc.
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 3. `public.user_values` (Normalized Junction Table)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `user_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `value_id` UUID NOT NULL REFERENCES public.values_options(id) ON DELETE RESTRICT,
- `is_core` BOOLEAN NOT NULL DEFAULT false,    -- Optional single "True North" core value
- `sort_order` INTEGER DEFAULT 1,              -- UI display order (1 to 5)
- `source` VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('onboarding', 'profile_edit')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT uq_user_value UNIQUE (user_id, value_id)
- *Indexes:* `idx_user_values_user ON (user_id)`, `idx_user_values_value ON (value_id)`.
- *Invariants:* Maximum of 5 values per user enforced via application layer and trigger. Maximum 1 `is_core = true` per user.

### 4. `public.value_relations` (Synergies & Polarities Graph)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `value_a_id` UUID NOT NULL REFERENCES public.values_options(id) ON DELETE CASCADE,
- `value_b_id` UUID NOT NULL REFERENCES public.values_options(id) ON DELETE CASCADE,
- `relation_type` VARCHAR(30) NOT NULL CHECK (relation_type IN ('synergy', 'complementary_balance', 'polarity')),
- `dynamic_label_en` VARCHAR(100) NOT NULL,    -- e.g. 'Anchor and Sail', 'Deep Truth and Gentle Care'
- `dynamic_label_ka` VARCHAR(100) NOT NULL,    -- e.g. 'ღუზა და იალქანი'
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT uq_value_relation UNIQUE (value_a_id, value_b_id),
- CONSTRAINT check_no_self_value_relation CHECK (value_a_id != value_b_id)
- *Usage:* Powers JESTER AI interpretation hooks and relationship discovery dynamics without calculating clinical compatibility percentages.

---

## 👥 Social Behavior System V1 Schema Specification (Architecture Blueprint)

To capture how users prefer to interact, gather, warm up, and recharge socially without imposing psychological diagnoses, Myers-Briggs archetypes, or clinical labels, the Social Behavior System V1 defines the following normalized entities:

### 1. `public.social_categories`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'gathering_scale', 'social_battery', 'warmup_style', 'planning_style', 'comfort_zone'
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 2. `public.social_options`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `category_id` UUID NOT NULL REFERENCES public.social_categories(id) ON DELETE CASCADE,
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'one_on_one', 'recharge_solo', 'initiator', 'spontaneous', etc.
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `definition_en` TEXT NOT NULL,
- `definition_ka` TEXT NOT NULL,
- `badge_icon` VARCHAR(30),                    -- 'coffee', 'battery-charging', 'rocket', 'calendar', 'home', etc.
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 3. `public.user_social_preferences` (Normalized Profile Extension)
- `user_id` UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
- `group_preference` VARCHAR(40),              -- e.g. 'one_on_one', 'small_groups', 'lively_crowds', 'adaptable_scale'
- `social_battery` VARCHAR(40),                -- e.g. 'recharge_solo', 'recharge_social', 'recharge_fluid'
- `warmup_style` VARCHAR(40),                  -- e.g. 'initiator', 'observer_first', 'selective_deep'
- `planning_style` VARCHAR(40),                -- e.g. 'spontaneous', 'planned_advance', 'flexible_flow'
- `comfort_zone` VARCHAR(40),                  -- e.g. 'cozy_intimate', 'out_and_about', 'active_outdoor'
- `visibility_flags` JSONB NOT NULL DEFAULT '{
    "group_preference": true,
    "social_battery": true,
    "warmup_style": true,
    "planning_style": true,
    "comfort_zone": true
}',
- `source` VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('onboarding_snapshot', 'profile_edit', 'inferred')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Invariants:* Governed by RLS. Users can update only their own row. Fields toggled private are stripped from public responses and omitted from AI prompts.

### 4. `public.social_relations` (Synergies & Dynamic Interplay Graph)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `option_a_id` UUID NOT NULL REFERENCES public.social_options(id) ON DELETE CASCADE,
- `option_b_id` UUID NOT NULL REFERENCES public.social_options(id) ON DELETE CASCADE,
- `relation_type` VARCHAR(30) NOT NULL CHECK (relation_type IN ('symmetric_harmony', 'complementary_balance', 'pacing_difference')),
- `dynamic_label_en` VARCHAR(120) NOT NULL,    -- e.g. 'Mutual Quiet Refueling', 'Initiator and Observer'
- `dynamic_label_ka` VARCHAR(120) NOT NULL,
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT uq_social_relation UNIQUE (option_a_id, option_b_id),
- CONSTRAINT check_no_self_social_relation CHECK (option_a_id != option_b_id)
- *Usage:* Powers JESTER AI meeting-setting recommendations and interpersonal dynamics without calculating clinical compatibility scores.



