# JESTER — Product Architecture Discovery & Frontend Inventory

> **Authoritative Technical & Product Architecture Report**  
> **Repository:** JESTER Platform (`farnai/Jester`)  
> **Status:** READ-ONLY Discovery & Implementation Audit  
> **Target Audience:** Founder & Lead System Architect  
> **Date:** October 2026  

---

## A. Executive Summary

JESTER is engineered as a **People Discovery & Relationship Intelligence platform**, structured around the core human journey:
$$\mathbf{ME} \longrightarrow \mathbf{YOU} \longrightarrow \mathbf{US} \longrightarrow \mathbf{MORE\ PEOPLE}$$

### Core Platform Status
- **Deterministic Intelligence Core (IMPLEMENTED):** JESTER’s astrology and synastry engine is powered by **Swiss Ephemeris** C-bindings (`pyswisseph`) executing deterministic astronomical calculations (Julian Day, planetary longitudes, Placidus house cusps) coupled with the frozen **Synastry V1.0.0** algorithm (`backend/app/compatibility/`). It computes harmonic aspects across 5 relationship dimensions with 100% mathematical determinism.
- **Explainability & Narrative Corpus (IMPLEMENTED):** Unlike conventional apps that rely on generic horoscope blurbs or ungrounded LLM hallucinations, JESTER utilizes a structured Georgian semantic corpus (`batch_1_natal.json`, `batch_2_synastry.json`, `batch_7_discovery_connection_chat.json`) in `backend/app/interpretation/data/batches/`. It deterministically maps concrete planetary aspect signals to sharp, psychological observations.
- **Relational Social Loop (IMPLEMENTED):** Canonical pair connections (`public.connections`), pending request handshakes, mutual block isolation, and direct messaging with Supabase Realtime live subscriptions are implemented and operational.
- **Onboarding Engine (IMPLEMENTED):** An 8-step wizard (`frontend/src/modules/onboarding/BirthDataOnboardingPage.tsx`) captures canonical identity, birth date/time/place, current city, interests, and profile avatar, enforced by authoritative server-side completion validation (`backend/app/profiles/router.py`).

### Critical Product & Architectural Deficits (Gaps before MVP)
1. **Photo System Limitations (PARTIAL):** Only a single avatar image is supported via Supabase storage (`avatars` bucket). **Zero multi-photo tables, gallery endpoints, reordering logic, or photo moderation systems exist.**
2. **Discovery Scalability & Filtering Bottleneck (PARTIAL):** `GET /v1/interpretations/discovery-people` queries all discoverable users into memory and executes on-the-fly Synastry calculations for every user in the database on every request. It has **no cursor pagination, no interest filtering, no geographic radius filtering, and no score ranking**.
3. **Conversations Inbox Integration Disconnect (PARTIAL):** The backend provides an inbox listing endpoint (`GET /v1/conversations`), but the frontend API client (`frontend/src/core/api/endpoints.ts`) never registered it. Consequently, `MessagesPage.tsx` falls back to querying raw connection lists rather than actual active conversation threads.
4. **Monetization Infrastructure (MISSING):** There are **no subscription models, no credit balances, no payment gateway integrations (Stripe/LemonSqueezy), no usage quotas, and no entitlement gating** anywhere in the schema or codebase.
5. **Home Information Architecture (IMPLEMENTED but flagged for UX Redesign):** The current Home screen (`frontend/src/modules/home/HomePage.tsx`) assembles daily personal energy, accepted connection highlights, and a 4-profile discovery preview, but lacks viral invitation mechanics, deep engagement hooks, and social gamification.

---

## B. Complete Frontend Route Inventory

All frontend routes are declared in `frontend/src/navigation/AppRoutes.tsx` and guarded by `frontend/src/navigation/ProtectedRoute.tsx`.

| Route Path | Rendered Component | Auth Requirement | Onboarding Requirement | Data Dependencies | Primary User Action | Status | Notes / Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | `HomePage` | Authenticated | `onboardingCompleted = true` | `GET /v1/profiles/me`<br>`GET /v1/interpretations/daily-energy`<br>`GET /v1/connections`<br>`GET /v1/interpretations/discovery-people` | View daily personal observation, manage circle, discover people | **IMPLEMENTED** | Functional, but designated by Founder for product & marketing redesign. |
| `/auth/login` | `LoginPage` | Public / Unauth | None | Supabase Auth API (`signInWithPassword`) | Sign into account | **IMPLEMENTED** | Clean Georgian auth card with email & password. |
| `/auth/register` | `RegisterPage` | Public / Unauth | None | Supabase Auth API (`signUp`) | Create new account | **IMPLEMENTED** | Captures first name, last name, email, password. |
| `/auth/reset-password` | `ResetPasswordPage` | Public / Unauth | None | Supabase Auth API (`resetPasswordForEmail`) | Request password reset email | **IMPLEMENTED** | Standard email reset flow. |
| `/auth/callback` | `AuthCallbackPage` | Public | None | Supabase Auth session exchange | Process OAuth / email confirmation tokens | **IMPLEMENTED** | Dispatches to `/onboarding` or `/`. |
| `/auth/verify-email` | `VerifyEmailPage` | Public | None | None | Instructs user to check email | **IMPLEMENTED** | Static confirmation screen. |
| `/logout` | `LogoutHandler` | Authenticated | None | `supabase.auth.signOut()` | Sign out and clear cache | **IMPLEMENTED** | Invalidates TanStack Query client and redirects. |
| `/onboarding` | `OnboardingDispatcher` | Authenticated | `onboardingCompleted = false` | `useAuth()` state | Route to onboarding wizard | **IMPLEMENTED** | Auto-redirects to `/onboarding/birth-data`. |
| `/onboarding/birth-data` | `BirthDataOnboardingPage` | Authenticated | `onboardingCompleted = false` | `GET /v1/profiles/me`<br>`GET /v1/interests`<br>`GET /v1/geo/cities/search`<br>`POST /v1/astrology/profile/recalculate`<br>`POST /v1/profiles/me/complete-onboarding` | Complete 8-step onboarding flow | **IMPLEMENTED** | 8 sequential steps: Identity, Birth Date, Time, Birth Place, Current City, Interests, Photo, Confirmation. |
| `/discover` | `DiscoverPage` | Authenticated | `onboardingCompleted = true` | `GET /v1/interpretations/discovery-people`<br>`GET /v1/connections` | Browse discoverable people | **IMPLEMENTED** | Grid feed of `PersonCard`. Lacks search, interest filters, and pagination. |
| `/people/:id` | `PersonProfilePage` | Authenticated | `onboardingCompleted = true` | `GET /v1/profiles/{id}`<br>`GET /v1/astrology/people/{id}/safe-astro`<br>`GET /v1/connections`<br>`POST /v1/interpretations/compare-preview` | View person profile, preview compatibility, send connection request | **IMPLEMENTED** | Full profile view with curiosity score and safe relationship hook preview. |
| `/people/:id/why` | `WhyPage` | Authenticated | `onboardingCompleted = true` | `GET /v1/people/{id}/why`<br>Fallback: `POST /v1/interpretations/compare-preview`<br>`GET /v1/connections` | Deep dive into "Why does JESTER say this?" | **IMPLEMENTED** | Displays harmonic dimensions, categorized signal observations, icebreakers. |
| `/compare/:id` | `ComparePage` | Authenticated | `onboardingCompleted = true` | `POST /v1/compare`<br>Fallback: `POST /v1/interpretations/compare-preview`<br>`GET /v1/connections` | Detailed US comparison view | **IMPLEMENTED** | Dual-card layout (ME + YOU) with dimension scores and evidence trace. |
| `/connections` | `ConnectionsPage` | Authenticated | `onboardingCompleted = true` | `GET /v1/connections`<br>`POST /v1/connections/{id}/transition` | Manage Active, Incoming, and Outgoing connections | **IMPLEMENTED** | Full state transition buttons: Accept, Decline, Remove, Block. |
| `/messages` | `MessagesPage` | Authenticated | `onboardingCompleted = true` | `GET /v1/connections` | View conversation inbox | **PARTIAL** | Shows list of accepted connections to initiate chat; does not yet use backend `GET /v1/conversations`. |
| `/chat/:conversation_id` | `ChatPage` | Authenticated | `onboardingCompleted = true` | `GET /v1/conversations/{id}`<br>`GET /v1/conversations/{id}/messages`<br>`POST /v1/conversations/{id}/messages`<br>Realtime: `public:messages` | Real-time direct chat with conversation partner | **IMPLEMENTED** | Supports live incoming message streaming, icebreaker insertion, auto-scroll. |
| `/me` | `MePage` | Authenticated | `onboardingCompleted = true` | `GET /v1/profiles/me`<br>`GET /v1/astrology/profile/safe-astro`<br>`POST /v1/interpretations/resolve-natal`<br>`PATCH /v1/profiles/me` | View self natal insights & edit profile settings | **IMPLEMENTED** | Tab 1: 10 personality dimensions. Tab 2: Profile edit (Name, Bio, City, Discoverable). |
| `/notifications` | `NotificationsPage` | Authenticated | `onboardingCompleted = true` | `GET /v1/notifications`<br>`PATCH /v1/notifications/{id}/read` | View incoming notifications (connection requests, acceptances) | **IMPLEMENTED** | Realtime count badge in header + list with mark-read mutations. |
| `/visual-lab` | `VisualLab` | Public / Dev | None | Local platform storage / tokens | Universal design token testing | **IMPLEMENTED** | Internal dev surface testing React Native Web primitives & tokens. |
| `/smoke-test` | `ContentSmokeTestPage` | Authenticated / Dev | None | All interpretation endpoints | Comprehensive UX & content smoke testing | **IMPLEMENTED** | Multi-tab developer audit for Daily Energy, Natal, Discovery, Synastry. |
| `/__debug/backend-audit` | `BackendAuditDebugPage` | Authenticated / Dev | None | Direct DB & API audit probes | Full-stack data integrity verification | **IMPLEMENTED** | Forensic verification of Swiss Ephemeris and database RLS. |
| `/content-inspector` | `ContentInspectorPage` | Authenticated / Dev | None | `GET /v1/interpretations/inspector-data` | Authoritative content library audit | **IMPLEMENTED** | Inspects all 7 batches of Georgian copy, signal mappings, and rules. |

---

## C. Technical Architecture & Frontend Structure

### Folder & Module Organization
The frontend application lives under `frontend/src/` with clear architectural separation:
```text
frontend/src/
├── core/                  # Core architectural foundations
│   ├── api/               # API client, HTTP methods, typed schemas (client.ts, endpoints.ts, types.ts)
│   ├── auth/              # Supabase session lifecycle, AuthContext, useAuth hook
│   ├── config.ts          # Environment variables (API URL, Supabase keys)
│   └── realtime/          # Supabase client singleton for Realtime channels
├── modules/               # Domain-specific UI modules
│   ├── auth/              # Login, Register, Password Reset, Verification
│   ├── chat/              # ChatPage & real-time messaging
│   ├── compatibility/     # WhyPage, ComparePage, DimensionCards, EvidenceTrace
│   ├── connections/       # ConnectionsPage & tabbed relationship lists
│   ├── discover/          # DiscoverPage, PersonCard
│   ├── home/              # HomePage, HomeElements, HomeNavigation, homeModel
│   ├── inspector/         # ContentInspectorPage (QA & Corpus inspection)
│   ├── me/                # MePage (Natal insights & Profile settings)
│   ├── messages/          # MessagesPage (Inbox)
│   ├── notifications/     # NotificationsPage
│   ├── onboarding/        # BirthDataOnboardingPage & 8-step subcomponents
│   ├── people/            # PersonProfilePage
│   └── smoke_test/        # ContentSmokeTestPage
├── navigation/            # AppRoutes.tsx, ProtectedRoute.tsx
├── platform/              # Web/Native platform abstractions (storage, haptics, clipboard)
├── shared/                # Universal layouts & states (AppShell, StatusState, runtime helpers)
├── ui/                    # Universal Design System primitives, tokens, and VisualLab
├── index.css              # Global tokens, CSS variables, typography, reset
├── App.tsx                # App root with QueryClientProvider & AuthProvider
└── main.tsx               # DOM bootstrap
```

### State Management & Data Fetching
- **Server Cache & Synchronization:** Powered by `@tanstack/react-query` (v5.102.8). Query keys are strictly structured (e.g. `["profile", "me"]`, `["connections"]`, `["discovery-people", userId]`, `["messages", conversationId]`).
- **Cache Invalidation:** Actions that modify relationships (`connect`, `accept`, `decline`, `block`) trigger targeted invalidations of `["connections"]`, `["compatibility-us"]`, and `["why-experience"]`.
- **Authentication State:** Centralized in `frontend/src/core/auth/context.tsx` via `AuthProvider`. Synchronizes directly with `supabase.auth.onAuthStateChange`. When session identity changes, `queryClient.clear()` is called to prevent cross-account cache leakage.
- **Client Realtime:** Supabase WebSocket channel (`supabase.channel`) manages live message inserts (`public:messages`) and unread notification updates (`public:notifications`).

### Design Tokens & Typography
- **Core Tokens (`frontend/src/index.css` & `frontend/src/ui/tokens/`):**
  - **Colors:** Neutral dark/light system with signature Warm Peach accents (`--jester-brand-orange-500: #ff7a2f`, `--jester-surface-subtle: #faf8f5`, `--jester-text-primary: #1e293b`).
  - **Typography:** Primary font family is **Noto Sans Georgian** (`Noto Sans Georgian, -apple-system, sans-serif`), providing crisp, native legibility across all Georgian copy.
  - **Component Primitives (`frontend/src/shared/ui/`):** `Card`, `Button`, `Badge`, `Avatar`, `Input`, `Skeleton`, `CitySelector`, `ErrorState`, `EmptyState`.

---

## D. Profile Data, Media & Storage Limitations

### Persistent Database Schema (`public.profiles`)
From `supabase/migrations/003_profiles.sql`, `023_profile_identity_names.sql`, `026_auth_onboarding_foundation.sql`:

| Column | Type | Nullable | Client Read | Client Write | Purpose / Invariants |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `uuid` | NO | Public | NO | References `auth.users.id`. Primary Key. |
| `display_name` | `text` | NO | Public | Authenticated | Display name (auto-derived as "First L." if unspecified). |
| `first_name` | `text` | YES | Public | Authenticated | Given name (required for onboarding completion). |
| `last_name` | `text` | YES | Public | Authenticated | Family name (required for onboarding completion). |
| `avatar_url` | `text` | YES | Public | Authenticated | Single URL pointing to public storage bucket. |
| `bio` | `text` | YES | Public | Authenticated | Self-authored bio text. |
| `city` | `text` | YES | Public | Authenticated | Denormalized display name of current city. |
| `city_id` | `uuid` | YES | Public | Authenticated | Deprecated alias for current city. |
| `current_city_id` | `uuid` | YES | Public | Authenticated | FK to `public.cities.id` (required for onboarding). |
| `occupation` | `text` | YES | Public | Authenticated | Professional or personal vocation label. |
| `timezone` | `text` | NO | Public | Authenticated | Defaults to `"UTC"`. |
| `is_discoverable` | `boolean` | NO | Public | Authenticated | Default `true`. If `false`, hidden from Discover feed. |
| `onboarding_step` | `integer`| NO | Public | Server Owned | Current step (1 to 5 / 8). |
| `onboarding_completed` | `boolean`| NO | Public | Server Owned | Validated strictly by `complete-onboarding` endpoint. |
| `created_at` | `timestamptz` | NO | Public | NO | Record creation timestamp. |
| `updated_at` | `timestamptz` | NO | Public | NO | Auto-updated via DB trigger `handle_updated_at`. |

### Storage Bucket & Media Architecture (`supabase/migrations/019_storage.sql`)
- **Bucket Configuration:** Single bucket `avatars` (public = true, 5MB file limit, MIME types: `image/jpeg`, `image/png`, `image/webp`, `image/gif`).
- **Storage Pathing:** `${userId}/${Date.now()}_${cleanFileName}`.
- **RLS Policies on `storage.objects`:**
  - `SELECT`: Publicly accessible (`bucket_id = 'avatars'`).
  - `INSERT` / `UPDATE` / `DELETE`: Authenticated users can modify objects **only if** the top-level folder name matches their own `auth.uid()`.
- **Account Deletion Cascade:** Database trigger `on_auth_user_deleted_cleanup_storage` executes `cleanup_user_storage_on_account_deletion()` on `auth.users` deletion, automatically wiping the user's storage folder.

### Critical Media Deficits
- **No Multiple Photos Support (MISSING):** There is **no `photos` or `profile_photos` table**, no secondary image storage bucket, and no gallery endpoint.
- **No Gallery or Reordering UI (MISSING):** Users cannot upload additional lifestyle, social, or portrait photographs.
- **No Photo Moderation (MISSING):** Uploaded avatars undergo no automated safety, NSFW, or face-detection moderation.
- **Avatar Management Restricted to Onboarding (PARTIAL):** Avatar upload is present in `ProfilePhotoStep.tsx` during onboarding, but `MePage.tsx` settings tab has no avatar update control.

---

## E. Interests & Social Discovery

### Interests Infrastructure (`supabase/migrations/026_auth_onboarding_foundation.sql`)
- **Tables:**
  - `public.interest_categories`: Categorized taxonomy (`name`, `slug`, `icon`, `sort_order`, `status`).
  - `public.interests`: Individual interest tags (`category_id`, `name`, `slug`, `sort_order`, `status`).
  - `public.user_interests`: Join table (`user_id`, `interest_id`, `created_at`).
- **Endpoints (`backend/app/interests/router.py`):**
  - `GET /v1/interests`: Lists all active interest categories and tags.
  - `GET /v1/interests/me`: Returns current user's selected interest UUIDs.
  - `PUT /v1/interests/me`: Transactionally updates user interests.
- **Business Rule Enforced:** Minimum 3 interests required if any are selected; 0 interests (Skipped) is permissible; 1 or 2 selected interests rejected with HTTP 400.

### Discovery Feed Implementation (`GET /v1/interpretations/discovery-people`)
- **Query Filter:** `SELECT ... FROM public.profiles WHERE is_discoverable = true AND id != viewer_id AND NOT is_user_blocked(viewer_id, id)`.
- **Astrology Projection:** Injects safe public derived placements (`sun_sign`, `moon_sign`, `ascendant_sign`, `element_primary`, `modality_primary`).
- **Presence Hook:** Injects resolved Batch 7 Georgian hook copy based on candidate's Ascendant sign (fallback to Sun sign, fallback to Aries).
- **On-the-Fly Synastry Calculation:** Computes full Synastry V1 compatibility between viewer and candidate using Swiss Ephemeris data in real time.

### Discovery Gaps & Scalability Bottlenecks
1. **Unbounded Full-Table Scan:** Fetches all discoverable users in one query without database `LIMIT` or cursor pagination.
2. **Synchronous O(N) Synastry Recalculation:** As user count grows, computing full synastry for 500+ users on every discovery page load will cause CPU starvation and gateway timeouts.
3. **No Filtering Capabilities:** Discover has **no filtering by age, gender, geographic distance/city, interest tags, or compatibility score range**.
4. **Common Interests Calculation (MISSING):** The backend does not compute or return the intersection of interests between viewer and candidate in the discovery feed.

---

## F. Astrology, Compatibility & Explainability Pipeline

### The Complete Data Pipeline
```text
┌────────────────────────┐
│   public.birth_data    │  Private date, time, timezone, lat/long (Owner-only RLS)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│    Swiss Ephemeris     │  pyswisseph C-bindings: swe_julday, swe_calc_ut, swe_houses
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  public.astro_private  │  Private calculated ecliptic degrees, polar cusps (Server-only)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ public.astro_safe_prof │  Safe public DTO: signs, qualities, elements (No degrees/houses)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│      Synastry V1       │  Deterministic aspect geometry (0°, 60°, 90°, 120°, 180° + orbs)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Structured Signals &   │  Harmonic category weights -> Harmony, Attraction, Communication,
│     Evidence Trace     │  Growth, Stability. Confidence rating based on birth-time precision.
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  Content Resolver V2   │  Idempotent seed from canonical pair -> Resolves pre-authored
│    (Georgian Corpus)   │  Georgian narrative assets from Batches 1, 2, and 7.
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Structured API Output  │  Delivered to /v1/compare, /v1/people/{id}/why, & /compare-preview
└────────────────────────┘
```

### Private vs. Public Astrological Boundaries
- **Strictly Private (Must NEVER be exposed to clients):**
  - `birth_data.birth_date`, `birth_time`, `latitude`, `longitude`, `place_label`.
  - `astro_private.sun_longitude`, `moon_longitude`, `ascendant_longitude`, `house_cusps`, `retrograde_flags`.
- **Public Safe DTO (`public.astro_safe_profile`):**
  - Sign names (`sun_sign`, `moon_sign`, `ascendant_sign`, `mercury_sign`, `venus_sign`, `mars_sign`).
  - Primary element (`Fire`, `Earth`, `Air`, `Water`) and modality (`Cardinal`, `Fixed`, `Mutable`).
  - Polar Placidus Error Handling: If birth location is polar (latitude $> 66^\circ$), Placidus fails safely with HTTP 400 (`placidus_polar_error`).
  - Unknown Birth Time Contract: If time is unknown, `ascendant_sign` and house cusps are strictly `NULL`. Longitude fallback calculates planetary signs at 12:00 UTC without fabricating rising signs.

### Structured Synastry Output & "Why" Explainability
- **Planetary Aspect Rules:** Evaluates pairwise inter-chart aspects across Sun, Moon, Mercury, Venus, Mars.
- **Dimensions (`dimensions` object):**
  1. `harmony`: Emotional resonance and domestic ease (Moon-Moon, Sun-Moon aspects).
  2. `attraction`: Interpersonal spark and physical/romantic chemistry (Venus-Mars, Sun-Venus).
  3. `communication`: Intellectual rapport and dialogue pacing (Mercury-Mercury, Mercury-Sun).
  4. `growth`: Developmental tension, motivation, and mutual evolution (Mars-Sun, Mars-Moon).
  5. `stability`: Long-term predictability and loyalty (harmonic Saturn/structural aspects).
- **Explainability Readiness ("Why does JESTER say this?"):**
  - **IMPLEMENTED:** The `deep_analysis` payload provides an `evidence_trace` containing the exact aspect rules triggered (e.g., `sun_trine_moon`, orb `2.4°`, category `harmony`, weight `1.0`), alongside contextual strengths, friction points, and communication advice.
  - **Boundary Limitation:** Interpretations are deterministic selections from pre-authored corpus batches. **There is no dynamic LLM synthesis capable of answering open-ended follow-up questions.**

---

## G. Social Connections & Communication Architecture

### Canonical Connection Lifecycle (`supabase/migrations/007_connections.sql`)
- **Canonical Ordering:** Stored as `user_a_id < user_b_id`. Enforced by DB check constraint `user_a_id < user_b_id`. Prevents duplicate inverted records regardless of who initiates the request.
- **States:** `pending`, `accepted`, `declined`, `blocked`.
- **Transitions (`backend/app/connections/router.py`):**
  - `create`: Initiator creates pending request (`initiated_by = caller.id`).
  - `accept`: Target user accepts (`initiated_by != caller.id`). Transitions to `accepted`.
  - `decline`: Target user declines. Transitions to `declined`.
  - `remove`: Either user terminates active connection. Transitions to `declined`.
  - `block`: Either user blocks the other. Transitions to `blocked`.
- **Unblock:** Not supported in current transition state machine (`MISSING`).

### Messaging & Direct Conversations (`backend/app/conversations/`)
- **Access Authorization:** Creating a direct conversation requires an active `accepted` connection verified by `public.has_active_connection(caller, target)`.
- **Realtime Messaging:**
  - Clients post messages via `POST /v1/conversations/{id}/messages`.
  - Incoming messages stream directly to connected clients via Supabase Realtime WebSocket on table `messages`.
- **Icebreaker Handoff:** WhyPage and PersonProfile pass deterministic conversation starters via query parameter `?starter=...` directly into ChatPage’s text composer.
- **Integration Gap:** As noted in Section B, `GET /v1/conversations` exists on the server, but `MessagesPage.tsx` currently lists accepted connections rather than hydrated inbox conversation threads.

---

## H. Monetization Readiness

| Monetization Subsystem | Current Status | Repository Evidence / Implementation Details |
| :--- | :--- | :--- |
| **Subscription Entities** | **MISSING** | No `subscriptions`, `plans`, or `billing_customers` tables exist in any database migration. |
| **Premium Feature Definitions** | **MISSING** | No feature flags or tier definitions (`free`, `jester_plus`, `pro`) exist in backend or frontend configs. |
| **Usage Counters** | **MISSING** | No database counters tracking daily profile views, comparisons, or message volume. |
| **AI Chat Daily Limits** | **MISSING** | Chat messaging is unlimited for connected pairs; no daily quota counters exist. |
| **Credit / Coin Balances** | **MISSING** | No user credit balance field exists on `public.profiles` or related tables. |
| **Credit Transaction Ledger** | **MISSING** | No immutable debit/credit transaction ledger table exists. |
| **Payment Gateway Integration** | **MISSING** | Zero Stripe, LemonSqueezy, Apple IAP, or Google Play Billing SDK dependencies in `package.json` or `pyproject.toml`. |
| **Payment Webhooks** | **MISSING** | No webhook handlers for invoice payment, subscription cancellation, or dispute management. |
| **Entitlement Checks** | **MISSING** | Backend routers check only auth tokens, onboarding completion, and connection state. No entitlement middleware exists. |
| **Feature Gating** | **MISSING** | All implemented features (deep why analysis, compare preview, natal observations) are completely ungated. |
| **Usage Metering** | **MISSING** | No telemetry or database tracking of computational resource consumption per user. |
| **AI Token / Cost Observability** | **MISSING** | Since interpretations use local static JSON corpus files, no external LLM tokens are consumed. |

### Computationally Expensive Operations Requiring Quotas
1. **Full Synastry Calculation on Discovery:** Recalculating synastry for hundreds of users on feed load.
2. **Deep Why / Compatibility Analysis:** High-value IP that delivers full relationship intelligence.
3. **Future Generative LLM Transit / Daily Energy:** Once external LLMs are introduced, generating daily personalized voice copy will incur recurring API costs.

---

## I. Safety, Privacy & Security Boundaries

### Implemented Security Invariants
1. **Birth Data Protection:** `public.birth_data` has strict PostgreSQL RLS (`auth.uid() = user_id`). It is impossible for another user to read raw birth coordinates or times.
2. **Astrology Isolation:** `public.astro_private` has no public grants. Safe derived astrology is projected via `public.astro_safe_profile`.
3. **Mutual Block Isolation:** Evaluated via `public.is_user_blocked(user_1, user_2)`. When a block exists in either direction:
   - Target profiles return HTTP 404 (Privacy-safe Not Found; no existence leak).
   - Discovery feed completely omits blocked users.
   - Comparison and messaging routes reject requests with HTTP 404.
4. **Account Deletion Cascade:** Deleting a user in `auth.users` triggers storage cleanup for all avatar assets and cascades through profile, birth data, connections, and messages.

### Safety & Privacy Gaps for Launch
- **Abuse Reporting & Moderation (MISSING):** No `reports` table or reporting API endpoint exists for flagging offensive bios, avatars, or chat messages.
- **User Muting (MISSING):** Only binary hard blocking exists; no temporary mute or soft hide.
- **Account Deletion API (PARTIAL):** DB triggers handle cleanup upon deletion from `auth.users`, but there is no user-facing `DELETE /v1/users/me` endpoint in the backend router.
- **Age Verification (PARTIAL):** Onboarding enforces birth date selection, but does not enforce an explicit 18+ verification handshake or parental consent check.

---

## J. Available Testing, Audit & Design Tooling

| Tool Name | Location | Type & Purpose | Operational Status | How to Invoke | Non-Destructive? | Reusable Artifacts |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Visual Lab** | `frontend/src/ui/VisualLab.tsx`<br>Route: `/visual-lab` | Universal Design System primitive & token showcase | **OPERATIONAL** | Navigate to `http://localhost:3000/visual-lab` in browser | **YES** | Pre-built token specimens, typography scale, buttons, inputs. |
| **Content Smoke Test** | `frontend/src/modules/smoke_test/ContentSmokeTestPage.tsx`<br>Route: `/smoke-test` | Developer testing surface for Daily Energy, Natal, Discovery, Synastry | **OPERATIONAL** | Navigate to `http://localhost:3000/smoke-test` | **YES** | Live UI testing of all Georgian interpretation layers. |
| **Backend Audit Debug Lab** | `frontend/src/ui/BackendAuditDebugPage.tsx`<br>Route: `/__debug/backend-audit` | Forensic verification of Swiss Ephemeris and database RLS | **OPERATIONAL** | Navigate to `http://localhost:3000/__debug/backend-audit` | **YES** | Live parameter injection tests verifying birth data isolation. |
| **Content & Logic Inspector** | `frontend/src/modules/inspector/ContentInspectorPage.tsx`<br>Route: `/content-inspector` | Full-database corpus and rule coverage inspector | **OPERATIONAL** | Navigate to `http://localhost:3000/content-inspector` | **YES** | Validates all 7 batches of Georgian copy, sign coverage, rules. |
| **MVP Entry QA Script** | `scripts/mvp-entry-qa.cjs` | Headless Playwright end-to-end registration & 8-step onboarding | **OPERATIONAL** | `node scripts/mvp-entry-qa.cjs` | **NO** (Creates real test user in local Supabase) | Generates step-by-step full-page screenshots in `.jester/reports/verification/mvp-entry/`. |
| **Home Model Verification** | `scripts/home-model.test.mjs` | Node test runner validating Home page data assembly & sorting | **OPERATIONAL** | `node --experimental-strip-types --test scripts/home-model.test.mjs` | **YES** (Pure unit logic) | Validates Home fallback rules and profile slicing. |
| **Backend Pytest Suite** | `tests/` | Comprehensive backend test suite (Astrology, Synastry, RLS, Auth) | **OPERATIONAL** | `pytest tests/` | **YES** (Uses isolated test DB) | 100+ unit tests covering Swiss Ephemeris and RLS policies. |

---

## K. MVP Gap Matrix (12 Core Domains)

| Domain | Current Implementation State | Primary Source Files | Existing API Capability | Missing Functionality for Launch | Dependencies | Est. Complexity | MVP Launch Required? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Home** | **PARTIAL** | `frontend/src/modules/home/HomePage.tsx`<br>`frontend/src/modules/home/HomeElements.tsx` | `GET /v1/profiles/me`<br>`GET /v1/interpretations/daily-energy`<br>`GET /v1/connections`<br>`GET /v1/interpretations/discovery-people` | Redesigned information architecture, viral invitation hooks, engagement loop, visual hierarchy | Marketing Foundation, Product Owner UI approval | **Medium** | **YES** |
| **2. ME / Profile** | **IMPLEMENTED** | `frontend/src/modules/me/MePage.tsx`<br>`backend/app/profiles/router.py` | `GET /v1/profiles/me`<br>`PATCH /v1/profiles/me`<br>`POST /v1/interpretations/resolve-natal` | Direct avatar change within settings tab; interest tag editor | Profile photo upload endpoint | **Low** | **YES** |
| **3. Photo Gallery** | **MISSING** | `supabase/migrations/019_storage.sql`<br>`frontend/src/modules/onboarding/steps/ProfilePhotoStep.tsx` | Single avatar upload to `avatars` bucket | `profile_photos` table, multi-photo upload/delete API, photo reordering, gallery carousel | Storage schema migration, RLS policies | **Medium** | **YES** (Crucial for people discovery) |
| **4. Interests** | **IMPLEMENTED** | `backend/app/interests/router.py`<br>`frontend/src/modules/onboarding/steps/InterestsStep.tsx` | `GET /v1/interests`<br>`GET /v1/interests/me`<br>`PUT /v1/interests/me` | Common interests calculation endpoint between 2 users; interest display on PersonProfile | Backend comparison logic | **Low** | **YES** |
| **5. Discover** | **PARTIAL** | `frontend/src/modules/discover/DiscoverPage.tsx`<br>`backend/app/interpretation/router.py` | `GET /v1/interpretations/discovery-people` | Cursor pagination, interest filtering, city/radius filtering, search by name, ranking algorithm | Backend pagination & filtering endpoints | **Medium** | **YES** |
| **6. Person Profile** | **IMPLEMENTED** | `frontend/src/modules/people/PersonProfilePage.tsx` | `GET /v1/profiles/{id}`<br>`GET /v1/astrology/people/{id}/safe-astro`<br>`POST /v1/interpretations/compare-preview` | Photo gallery display, common interests pill list | Photo Gallery infrastructure | **Low** | **YES** |
| **7. Explainability** | **IMPLEMENTED** | `backend/app/compatibility/engine.py`<br>`backend/app/interpretation/library.py` | Full evidence trace, dimension scores, resolved Georgian copy | Interactive "Why does JESTER say this?" tooltip explanations for each aspect | None (Data exists in API) | **Low** | **NO** (Can launch with current deep analysis) |
| **8. Compare / Why** | **IMPLEMENTED** | `frontend/src/modules/compatibility/WhyPage.tsx`<br>`frontend/src/modules/compatibility/ComparePage.tsx` | `POST /v1/compare`<br>`GET /v1/people/{id}/why`<br>`POST /v1/interpretations/compare-preview` | Dynamic shareable comparison card (og:image / social screenshot generator) | Canvas / SSR image generation | **Medium** | **NO** (Post-MVP growth feature) |
| **9. Connections** | **IMPLEMENTED** | `frontend/src/modules/connections/ConnectionsPage.tsx`<br>`backend/app/connections/router.py` | `GET /v1/connections`<br>`POST /v1/connections`<br>`POST /v1/connections/{id}/transition` | Unblock action; user-friendly notification toast when request accepted | Unblock transition in backend | **Low** | **YES** |
| **10. Messages** | **PARTIAL** | `frontend/src/modules/messages/MessagesPage.tsx`<br>`frontend/src/modules/chat/ChatPage.tsx`<br>`backend/app/conversations/router.py` | `GET /v1/conversations`<br>`GET /v1/conversations/{id}/messages`<br>`POST /v1/conversations/{id}/messages` | Expose `API.conversations.list()` in frontend client; wire MessagesPage to display real active conversation threads with last message & timestamp | Frontend API client update | **Low** | **YES** |
| **11. Monetization** | **MISSING** | None (No models or schemas exist) | None | Subscription plans, Stripe checkout, credit ledger, daily quota enforcement, entitlement checks | Payment provider setup, schema migrations, webhooks | **High** | **NO** (Can launch MVP as 100% Free / Beta) |
| **12. Safety & Privacy**| **PARTIAL** | `supabase/migrations/018_rls.sql`<br>`backend/app/core/errors.py` | Strict RLS, mutual block 404, storage cascade cleanup | In-app user reporting / abuse flagging (`POST /v1/reports`), user mute | Moderation schema & endpoints | **Medium** | **YES** (Required for public app store / safety compliance) |

---

## L. Strategic Architecture Questions Requiring Founder Approval

1. **Monetization Launch Strategy (Beta vs. Gate):**
   - *Option A (Recommended for MVP):* Launch initial MVP as a 100% free closed beta to maximize viral user acquisition and calibrate Synastry feedback without payment friction.
   - *Option B:* Implement a hybrid Free + Jester Plus model immediately, requiring Stripe integration, subscription tables, and paywall gates prior to public launch.
2. **Photo System Scope:**
   - Should JESTER support a multi-photo gallery (e.g. 4–6 photos) for profiles before launch, or is a single verified avatar sufficient for the initial social discovery loop?
3. **Discovery Filtering & Matching Policy:**
   - In the Discover feed, should users be able to filter by interest categories, city, or astrological sign, or should JESTER maintain an editorial "serendipitous discovery" feed ordered by compatibility score?
4. **Content Generation vs. Static Corpus:**
   - Daily Energy and Relationship Insights currently use static pre-authored Georgian batches. When should JESTER integrate real-time LLM inference (e.g. Gemini 2.5 Flash via server-side API) for personalized daily voice narratives?
5. **Safety & Reporting Requirements:**
   - Should a formal report/flagging system (`POST /v1/reports`) be built immediately before public launch to satisfy app store guidelines, or is the existing mutual block mechanism acceptable for early web testing?
