# Jester — Database Documentation & Migrations Guide

## 🗄️ Database Architecture Overview

Jester uses **PostgreSQL 15+** managed via **Supabase**. The database structure includes 11 application tables, multiple security-definer helper functions, triggers for automated timestamping and data versioning, and strict Row-Level Security (RLS) policies.

---

## 🔒 Data Classification

To maintain privacy and prevent data leakage, data is partitioned into 4 access classification tiers:

| Tier | Target Tables / Views | Access Scope | Enforced By |
| :--- | :--- | :--- | :--- |
| **PUBLIC** | `profiles` | Authenticated users (if `is_discoverable = true` and not blocked). | RLS policy `profiles_select` |
| **SAFE DERIVED** | `astro_safe_profile` | High-level summary (signs, element, modality). Authenticated users. | RLS policy `astro_safe_profile_select` |
| **PRIVATE** | `birth_data`, `connections`, `conversations`, `messages`, `daily_energies`, `notifications` | Owner or active connected participants only. | RLS policies + security-definer functions |
| **SERVICE-ONLY** | `astro_private` | Server-side calculation service ONLY. | `REVOKE ALL` from client roles |

---

## 📜 Complete Migration Inventory (001 – 020)

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
