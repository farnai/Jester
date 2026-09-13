# Jester — Database Documentation & Migrations Guide

## 🗄️ Database Architecture Overview

Jester uses **PostgreSQL 15+** managed via **Supabase**. The database structure includes 11 application tables, multiple security-definer helper functions, triggers for automated timestamping and data versioning, and strict Row-Level Security (RLS) policies.

---

## 🔒 Data Classification

To maintain privacy and prevent data leakage, data is partitioned into 4 access classification tiers:

| Tier | Target Tables / Views | Access Scope | Enforced By |
| :--- | :--- | :--- | :--- |
| **PUBLIC** | `profiles`, `interest_categories`, `interests`, `interest_aliases`, `interest_relations`, `geo_countries`, `geo_cities`, `geo_city_aliases`, `lifestyle_categories`, `lifestyle_options`, `values_categories`, `values_options`, `value_relations`, `social_categories`, `social_options`, `social_relations`, `communication_categories`, `communication_options`, `communication_relations`, `intent_categories`, `intent_options`, `intent_relations`, `prompt_categories`, `prompt_templates` | Authenticated users (profile discoverable and not blocked; taxonomy, geo, lifestyle, values, social, communication, intent & prompt options publicly readable). | RLS policies |
| **SAFE DERIVED** | `astro_safe_profile`, `user_interests`, `user_lifestyle`, `user_values`, `user_social_preferences`, `user_communication_preferences`, `user_intents`, `user_prompts` | High-level summary (signs, element, modality, declared interests, safe location, safe cadence pills, guiding compass values, social rhythm, communication preferences, looking for intent, user prompts). Authenticated users. | RLS policies |
| **PRIVATE** | `birth_data`, `connections`, `conversations`, `messages`, `daily_energies`, `notifications`, `user_discovery_preferences` | Owner or active connected participants only. | RLS policies + security-definer functions |
| **SERVICE-ONLY** | `astro_private`, `user_interest_affinity`, `user_location_private`, `user_intent_history` | Server-side calculation & recommendation engine ONLY. Never exposed to client. | `REVOKE ALL` from client roles / RLS restriction |

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

### `022_compatibility_dimensions.sql`
- **Purpose**: Adds dedicated JSONB `dimensions` column to `public.compatibility_results` persisting the 4 Synastry V1 relationship dimension subscores (`emotional_harmony`, `communication`, `attraction`, `growth_long_term`).

---

## 🔮 Astrology Integration System V1 Schema Specification

*(Detailed Product & Platform Specification: [`docs/ASTROLOGY_INTEGRATION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/ASTROLOGY_INTEGRATION_SYSTEM_V1_SPEC.md))*

The Astrology subsystem strictly separates sensitive raw inputs from deterministic calculations and public safe summaries:

1. **`public.birth_data` (Tier 1: Private)**: Owner-only (`user_id = auth.uid()`). Stores raw date, time, timezone, and coordinates. Auto-increments `data_version` on parameter updates to invalidate stale compatibility caches.
2. **`public.astro_private` (Tier 2: Service-Only)**: Client access completely revoked (`REVOKE ALL FROM authenticated, anon`). Stores exact float longitudes, speeds, houses, and retrogrades.
3. **`public.astro_safe_profile` (Tier 3: Safe Derived)**: Read-only for authenticated users (blocked or hidden targets return 404). Stores `sun_sign`, `moon_sign`, `ascendant_sign`, `element_primary`, `modality_primary`. Enriched on read with `mercury_sign`, `venus_sign`, and `mars_sign` via safe server DTO.
4. **`public.compatibility_results` (Tier 4: Relational Cache)**: Enforces canonical pair ordering `user_a_id < user_b_id`. Caches composite `score`, `dimensions`, `signals`, `best_topics`, `conversation_starters`, and `evidence_trace`.

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

---

## 💬 Communication System V1 Schema Specification (Architecture Blueprint)

To capture how users prefer to converse, message, pace replies, and choose formats without introducing response-time surveillance, read-receipt scorekeeping, or clinical personality typologies, the Communication System V1 defines the following normalized entities:

### 1. `public.communication_categories`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'conversation_depth', 'conversation_role', 'messaging_medium', 'response_pace'
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 2. `public.communication_options`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `category_id` UUID NOT NULL REFERENCES public.communication_categories(id) ON DELETE CASCADE,
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'deep_meaningful', 'question_curious', 'voice_notes_welcome', 'unhurried_thoughtful', etc.
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `definition_en` TEXT NOT NULL,
- `definition_ka` TEXT NOT NULL,
- `badge_icon` VARCHAR(30),                    -- 'waves', 'help-circle', 'mic', 'clock', etc.
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 3. `public.user_communication_preferences` (Normalized Profile Extension)
- `user_id` UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
- `conversation_depth` VARCHAR(40),            -- e.g. 'casual_light', 'balanced_depth', 'deep_meaningful'
- `conversation_role` VARCHAR(40),             -- e.g. 'question_curious', 'story_expressive', 'idea_conceptual', 'adaptable_flow'
- `messaging_medium` VARCHAR(40),              -- e.g. 'mostly_text', 'voice_notes_welcome', 'calls_welcome', 'flexible_medium'
- `response_pace` VARCHAR(40),                 -- e.g. 'active_banter', 'unhurried_thoughtful', 'relaxed_async'
- `visibility_flags` JSONB NOT NULL DEFAULT '{
    "conversation_depth": true,
    "conversation_role": true,
    "messaging_medium": true,
    "response_pace": true
}',
- `source` VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('onboarding_snapshot', 'profile_edit', 'inferred')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Invariants:* Governed by RLS. Users can update only their own row. Fields toggled private are stripped from public responses and omitted from AI prompts. Raw message bodies are never scanned for behavioral inference.

### 4. `public.communication_relations` (Synergies & Dynamic Interplay Graph)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `option_a_id` UUID NOT NULL REFERENCES public.communication_options(id) ON DELETE CASCADE,
- `option_b_id` UUID NOT NULL REFERENCES public.communication_options(id) ON DELETE CASCADE,
- `relation_type` VARCHAR(30) NOT NULL CHECK (relation_type IN ('symmetric_harmony', 'complementary_balance', 'pacing_awareness')),
- `dynamic_label_en` VARCHAR(120) NOT NULL,    -- e.g. 'Questioner and Storyteller', 'Mutual Deep Substance'
- `dynamic_label_ka` VARCHAR(120) NOT NULL,
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT uq_communication_relation UNIQUE (option_a_id, option_b_id),
- CONSTRAINT check_no_self_communication_relation CHECK (option_a_id != option_b_id)
- *Usage:* Powers JESTER AI first-conversation starter crafting and pacing guidance without calculating clinical compatibility scores.

---

## 🎯 Intent System V1 Schema Specification (Architecture Blueprint)

To capture what users are seeking on JESTER right now without mode-switching fragmentation, generic dating traps, or conflating temporal intent with marital status or family planning, the Intent System V1 defines the following normalized entities:

### 1. `public.intent_categories`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'social_connection', 'dating_romance', 'activity_practical', 'exploratory'
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 2. `public.intent_options`
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `category_id` UUID NOT NULL REFERENCES public.intent_categories(id) ON DELETE CASCADE,
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'friendship', 'dating_open', 'dating_serious', 'meaningful_chat', 'activity_partner', 'collaboration', 'just_exploring'
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `definition_en` TEXT NOT NULL,
- `definition_ka` TEXT NOT NULL,
- `badge_icon` VARCHAR(30),                    -- 'users', 'sparkles', 'heart', 'message-circle', 'compass', 'cpu', 'search'
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 3. `public.user_intents` (Active Declared Intent State)
- `user_id` UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
- `primary_intent` VARCHAR(60) NOT NULL REFERENCES public.intent_options(slug) ON DELETE RESTRICT,
- `secondary_intents` JSONB NOT NULL DEFAULT '[]'::jsonb,  -- Array of max 2 slugs
- `visibility` VARCHAR(20) NOT NULL DEFAULT 'public' CHECK (visibility IN ('public', 'connections_only', 'hidden')),
- `source` VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('onboarding', 'profile_edit', 'skipped')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Invariants:* Governed by RLS. Users update only their own row. Hidden intent is suppressed from public profiles and target AI prompts, but remains active internally for bilateral discovery partitioning.

### 4. `public.intent_relations` (Compatibility & Alignment Matrix)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `intent_a_slug` VARCHAR(60) NOT NULL REFERENCES public.intent_options(slug) ON DELETE CASCADE,
- `intent_b_slug` VARCHAR(60) NOT NULL REFERENCES public.intent_options(slug) ON DELETE CASCADE,
- `relation_type` VARCHAR(30) NOT NULL CHECK (relation_type IN ('symmetric_match', 'aligned_soft', 'partitioned', 'universal')),
- `alignment_label_en` VARCHAR(120) NOT NULL,
- `alignment_label_ka` VARCHAR(120) NOT NULL,
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT uq_intent_relation UNIQUE (intent_a_slug, intent_b_slug),
- CONSTRAINT check_no_self_intent_relation CHECK (intent_a_slug != intent_b_slug)
- *Usage:* Evaluated by Discovery engine to partition mutually incompatible intents and calculate candidate relevance boosts.

### 5. `public.user_intent_history` (Private Transition Audit Log)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `user_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `previous_primary` VARCHAR(60),
- `new_primary` VARCHAR(60) NOT NULL,
- `previous_secondaries` JSONB,
- `new_secondaries` JSONB,
- `changed_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Security Note:* Strictly **SERVICE-ONLY**. All privileges revoked from `authenticated`, `anon`, and `public`. Past intentions must never be exposed or weaponized.

---

## ✍️ Prompts / Self-Expression System V1 Schema Specification (Architecture Blueprint)

To capture what a person actually sounds like, their conversational rhythm, humor, and unique perspective without creating database-only chip profiles or clinical psychological typologies, the Prompts / Self-Expression System V1 defines the following normalized entities:

### 1. `public.prompt_categories` (Curated Prompt Taxonomy)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- 'voice_quirks', 'curiosities', 'daily_reality', 'connection', 'perspectives', 'action'
- `name_en` VARCHAR(100) NOT NULL,
- `name_ka` VARCHAR(100) NOT NULL,
- `description_en` TEXT,
- `description_ka` TEXT,
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 2. `public.prompt_templates` (Standardized Prompt Question Library)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `category_id` UUID NOT NULL REFERENCES public.prompt_categories(id) ON DELETE CASCADE,
- `slug` VARCHAR(60) NOT NULL UNIQUE,          -- e.g. 'unnecessary_hill', 'talk_forever', 'ordinary_day', 'get_me_talking', etc.
- `prompt_text_en` TEXT NOT NULL,              -- e.g. 'A completely unnecessary hill I''ll die on...'
- `prompt_text_ka` TEXT NOT NULL,              -- e.g. 'სრულიად უაზრო პრინციპი, რომელსაც ბოლომდე დავიცავ...'
- `placeholder_en` TEXT,                       -- e.g. 'Tell us about that tiny passionate debate...'
- `placeholder_ka` TEXT,
- `sort_order` INTEGER DEFAULT 100,
- `status` VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 3. `public.user_prompts` (Active Declared User Prompts & Answers)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `user_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `prompt_template_id` UUID NOT NULL REFERENCES public.prompt_templates(id) ON DELETE RESTRICT,
- `answer` VARCHAR(250) NOT NULL,              -- Concise answers (max 250 chars)
- `sort_order` SMALLINT NOT NULL CHECK (sort_order BETWEEN 1 AND 3),
- `visibility` VARCHAR(20) NOT NULL DEFAULT 'public' CHECK (visibility IN ('public', 'connections_only', 'hidden')),
- `source` VARCHAR(30) NOT NULL DEFAULT 'human' CHECK (source IN ('human', 'ai_assisted_edited')),
- `moderation_status` VARCHAR(20) NOT NULL DEFAULT 'approved' CHECK (moderation_status IN ('approved', 'flagged', 'rejected', 'pending_review')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- `moderated_at` TIMESTAMPTZ,
- CONSTRAINT uq_user_prompt_template UNIQUE (user_id, prompt_template_id),
- CONSTRAINT uq_user_prompt_order UNIQUE (user_id, sort_order)
- *Invariants:*
  - Max 3 published prompts per user enforced via trigger `check_user_prompt_limit` and check constraint.
  - Answers must be between 3 and 250 characters.
  - Governed by RLS: viewable by authenticated users if target user is discoverable and no active block exists; editable and deletable only by the owner.
  - Moderation status `rejected` hides the prompt from public discovery and API responses while notifying the owner.

---

## 🧭 Discovery Preferences System V1 Schema Specification (Architecture Blueprint)

To give users transparent control over who and what JESTER shows them without creating an exclusionary filter marketplace or compromising private birth dates, the Discovery Preferences System V1 defines the following normalized entity:

### 1. `public.user_discovery_preferences` (Owner-Only Candidate Steering Controls)
- `user_id` UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
- `age_min` SMALLINT NOT NULL DEFAULT 18 CHECK (age_min >= 18 AND age_min <= age_max),
- `age_max` SMALLINT NOT NULL DEFAULT 99 CHECK (age_max >= age_min AND age_max <= 99),
- `age_dealbreaker` BOOLEAN NOT NULL DEFAULT true,
- `target_genders` JSONB NOT NULL DEFAULT '["all"]'::jsonb, -- Array of ['man'], ['woman'], ['non_binary'], or ['all']
- `location_scope` VARCHAR(30) NOT NULL DEFAULT 'same_city' CHECK (location_scope IN ('same_city', 'same_country', 'regional_nearby', 'anywhere')),
- `location_dealbreaker` BOOLEAN NOT NULL DEFAULT false,
- `target_intents` JSONB NOT NULL DEFAULT '[]'::jsonb,      -- Optional intent filters (empty = natural bilateral compatibility)
- `astrology_mode` VARCHAR(30) NOT NULL DEFAULT 'full_insights' CHECK (astrology_mode IN ('full_insights', 'minimal_insights', 'hidden')),
- `diversity_level` VARCHAR(30) NOT NULL DEFAULT 'balanced' CHECK (diversity_level IN ('focused', 'balanced', 'adventurous')),
- `source` VARCHAR(30) NOT NULL DEFAULT 'default_derived' CHECK (source IN ('default_derived', 'user_configured', 'reset_to_default')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Invariants & Security:*
  - **Strictly Owner-Only:** Protected by RLS (`user_id = auth.uid()`). Revoked from `anon` and `public`. Never exposed to other users or serialized in public profile endpoints.
  - **Zero Filter Notification:** Excluded candidates are never notified that they were filtered out.
  - **Independent from Inbound Discoverability:** Operates as outbound candidate retrieval criteria, completely independent of `profiles.is_discoverable`.

---

## 🛡️ Trust & Verification System V1 Schema Specification (Architecture Blueprint)

*(Detailed Product & Platform Specification: [`docs/TRUST_VERIFICATION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/TRUST_VERIFICATION_SYSTEM_V1_SPEC.md))*

To decouple profile presentation from verification and ensure safety without building a surveillance score, the Trust & Verification System V1 defines the following 6 core entities:

### 1. `public.profile_photos` (Multi-Photo User Gallery)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `user_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `url` TEXT NOT NULL,
- `is_primary` BOOLEAN NOT NULL DEFAULT false,
- `sort_order` SMALLINT NOT NULL DEFAULT 0 CHECK (sort_order BETWEEN 0 AND 5),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Invariants:* Max 6 photos per user. Exactly 1 photo marked `is_primary = true` (synced to `profiles.avatar_url`). At least 1 photo required to appear in Discovery.

### 2. `public.user_verifications` (Active Verification State)
- `user_id` UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
- `status` VARCHAR(20) NOT NULL DEFAULT 'not_started' CHECK (status IN ('not_started', 'pending', 'verified', 'failed', 'needs_review', 'expired', 'revoked')),
- `provider` VARCHAR(50) NOT NULL DEFAULT 'internal',
- `confidence_score` NUMERIC(4,3) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
- `verified_at` TIMESTAMPTZ,
- `expires_at` TIMESTAMPTZ,
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Invariants:* Verification proves only facial match between a live selfie and the primary profile photo. Modifying the primary photo resets status to `needs_review` or `expired`.

### 3. `public.verification_attempts` (Audit Log)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `user_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `session_token` TEXT UNIQUE NOT NULL,
- `status` VARCHAR(20) NOT NULL CHECK (status IN ('initiated', 'passed', 'failed', 'flagged')),
- `failure_reason` TEXT,
- `attempt_ip_hash` TEXT,
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

### 4. `public.reports` (Community Safety Signals)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `reporter_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `reported_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `reason` VARCHAR(30) NOT NULL CHECK (reason IN ('fake_profile', 'harassment', 'inappropriate_content', 'spam_scam', 'underage', 'other')),
- `details` TEXT,
- `status` VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'dismissed')),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT no_self_report CHECK (reporter_id <> reported_id)

### 5. `public.user_blocks` (Dedicated Two-Way Blocking)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `blocker_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `blocked_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT no_self_block CHECK (blocker_id <> blocked_id),
- CONSTRAINT unique_block_pair UNIQUE (blocker_id, blocked_id)

### 6. `public.moderation_actions` (Disciplinary Audit Log)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `user_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `action` VARCHAR(30) NOT NULL CHECK (action IN ('warning', 'limit_rate', 'put_under_review', 'suspend', 'ban', 'lift_restriction')),
- `reason` TEXT NOT NULL,
- `expires_at` TIMESTAMPTZ,
- `issued_by` UUID REFERENCES public.profiles(id),
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

---

## 🧠 Behavioral Intelligence System V1 Schema Specification (Architecture Blueprint)

*(Detailed Product & Platform Specification: [`docs/BEHAVIORAL_INTELLIGENCE_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/BEHAVIORAL_INTELLIGENCE_SYSTEM_V1_SPEC.md))*

To enable observable product personalization without psychological profiling or surveillance, the Behavioral Intelligence System V1 defines the following 4 entities:

### 1. `public.behavioral_events` (Partitioned Raw Event Stream)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `actor_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `event_name` VARCHAR(50) NOT NULL,              -- e.g. 'candidate_profile_opened', 'why_opened', 'connection_request_sent'
- `target_id` UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
- `target_type` VARCHAR(30),                      -- 'candidate', 'interest', 'prompt', 'preference'
- `context` JSONB DEFAULT '{}'::jsonb,            -- sanitized minimal context (dwell_time_ms, has_note, category_slug)
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Invariants & Security:*
  - **Service-Only:** `REVOKE ALL ON public.behavioral_events FROM anon, authenticated;`. Written solely via rate-limited backend RPC or backend service-role.
  - **Zero Content Mining:** No message text, no coordinates, no birth data, no biometric data.
  - **Automated 60-Day TTL:** Partitioned monthly; records older than 60 days are automatically pruned by background cron.

### 2. `public.user_behavioral_signals` (Aggregated Profile Summary)
- `user_id` UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
- `exploration_breadth` VARCHAR(20) NOT NULL DEFAULT 'balanced' CHECK (exploration_breadth IN ('focused', 'balanced', 'exploratory')),
- `interaction_depth` NUMERIC(4,3) NOT NULL DEFAULT 0.500 CHECK (interaction_depth BETWEEN 0.0 AND 1.0),
- `connection_conversion_rate` NUMERIC(4,3) NOT NULL DEFAULT 0.000 CHECK (connection_conversion_rate BETWEEN 0.0 AND 1.0),
- `total_impressions_count` INTEGER NOT NULL DEFAULT 0,
- `total_opens_count` INTEGER NOT NULL DEFAULT 0,
- `total_requests_sent` INTEGER NOT NULL DEFAULT 0,
- `total_requests_accepted` INTEGER NOT NULL DEFAULT 0,
- `last_aggregated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Invariants:* Derived summary table maintained by background aggregation jobs. Never exposes personality scores or psychological diagnostics.

### 3. `public.user_interest_affinity` (Decayed Topic Weights)
- `id` UUID PRIMARY KEY DEFAULT gen_random_uuid(),
- `user_id` UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
- `interest_id` UUID NOT NULL REFERENCES public.interests(id) ON DELETE CASCADE,
- `affinity_score` NUMERIC(4,3) NOT NULL DEFAULT 0.500 CHECK (affinity_score BETWEEN 0.0 AND 1.0),
- `observation_count` INTEGER NOT NULL DEFAULT 1,
- `last_observed_at` TIMESTAMPTZ NOT NULL DEFAULT now(),
- CONSTRAINT uq_user_interest_affinity UNIQUE (user_id, interest_id)
- *Invariants:* Subject to 30-day exponential half-life decay. Independent layer that **never overwrites** declared interests in `user_interests`.

### 4. `public.user_behavioral_settings` (User Sovereign Controls)
- `user_id` UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
- `personalization_enabled` BOOLEAN NOT NULL DEFAULT true,
- `allow_activity_learning` BOOLEAN NOT NULL DEFAULT true,
- `last_reset_at` TIMESTAMPTZ,
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- *Invariants:* User-controlled settings. Calling reset clears all rows in `user_interest_affinity` and resets `user_behavioral_signals` to defaults.







