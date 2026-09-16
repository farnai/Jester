# JESTER — COMPLETE USER-FACING CAPABILITY INVENTORY AUDIT
**Authoritative Systems Analysis & Product Capability Verification**  
**Audit Date:** September 2026  
**Auditor Role:** Senior Product Capability Auditor / Systems Analyst  
**Methodology:** Comprehensive inspection of Backend Source Code (`backend/app/`), Database Migrations (`supabase/migrations/`), Frontend Architecture & Code (`frontend/src/`), Test Suites (`tests/`), and Specifications (`docs/`).

---

## 1. SOURCE OF TRUTH & AUDIT HIERARCHY

This audit strictly enforces the repository's source-of-truth hierarchy:
1. **Actual Source Implementation** (`backend/app/`, `frontend/src/`)
2. **Database Migrations & PostgreSQL RLS / Functions** (`supabase/migrations/`)
3. **Automated Test Suite** (74 passing tests in `tests/`)
4. **Architecture and Specification Documentation** (`docs/*.md`)

> **Ground Rule**: If documentation describes a capability (e.g., transit-driven daily vibes, AI interpretations, people discovery feeds) that is not supported by executable code and routes, it is classified as **DOCUMENTED / PLANNED** or **STUB**, never **IMPLEMENTED**.

---

## 2. CRITICAL STATUS TAXONOMY

Every capability evaluated in this audit receives exactly one status:
* **IMPLEMENTED**: Fully coded, operational, and verified end-to-end via an active API endpoint or operational client pathway.
* **PARTIAL**: Substantial logic or schema exists, but critical integration links (such as API exposure, reliable cache hydration, or frontend hooks) are incomplete.
* **STUB**: Structural scaffolds (empty Python files, placeholder database rows, or unused Pydantic models) exist, but no functional execution occurs.
* **DOCUMENTED / PLANNED**: Explicitly detailed in architectural, marketing, or product specs, but with no functional backend code.
* **UNKNOWN**: Ambiguity in implementation where evidence is insufficient to verify operational status.

---

## 3. DOMAIN A: ACCOUNT & IDENTITY

### 1. Account Creation & Authentication
* **What the User Can Do**: Sign up via email/password, log in, refresh authentication tokens, and maintain an active authenticated session.
* **Data Involved**: `auth.users` UUID (`id`), `email`, hashed password, JWT session tokens (`access_token`, `refresh_token`).
* **Service / Table**: Supabase Auth (`auth.users`), `backend.app.auth.jwt.verify_supabase_jwt`, `backend.app.auth.dependencies.get_current_user`.
* **Status**: **IMPLEMENTED**.
* **Endpoint / Path**: Direct Supabase Auth SDK (`supabase.auth.signUp`, `supabase.auth.signInWithPassword`), backend authentication verified via `Authorization: Bearer <JWT>`.
* **Restrictions**: In production (`ENV=production`), only asymmetric cryptographic keys (`RS256`, `ES256`, `EdDSA`) via Supabase JWKS are permitted. `HS256` symmetric signing is strictly rejected.

### 2. View Current Account Details
* **What the User Can Do**: Retrieve their own account identity, registered email, and authentication role.
* **Data Involved**: `id` (UUID), `email` (string), `role` (string, e.g. `"authenticated"`).
* **Service / Table**: `backend.app.users.router.get_my_user`.
* **Status**: **IMPLEMENTED**.
* **Endpoint**: `GET /v1/users/me` -> returns `UserResponse`.
* **Restrictions**: Authenticated user only (`auth.uid() == JWT.sub`).

### 3. Profile Viewing (Self)
* **What the User Can Do**: View their own public profile information. If no profile exists upon login, the system automatically self-heals by provisioning a default profile record derived from their email username.
* **Data Involved**: `id` (UUID), `display_name` (text), `avatar_url` (text, nullable), `bio` (text, nullable), `city` (text, nullable), `occupation` (text, nullable), `timezone` (text, default `'UTC'`), `is_discoverable` (boolean, default `true`), `created_at`, `updated_at`.
* **Service / Table**: `public.profiles`, `backend.app.profiles.router.get_my_profile`.
* **Status**: **IMPLEMENTED**.
* **Endpoint**: `GET /v1/profiles/me` -> returns `ProfileResponse`.
* **Restrictions**: Read access is restricted to the owning user.

### 4. Profile Editing (Self)
* **What the User Can Do**: Update their display name, avatar image URL, bio text, current city, occupation, timezone, and discovery visibility toggle.
* **Data Involved**: Any subset of `ProfileUpdate` fields (`display_name`, `avatar_url`, `bio`, `city`, `occupation`, `timezone`, `is_discoverable`).
* **Service / Table**: `public.profiles`, `backend.app.profiles.router.update_my_profile`.
* **Status**: **IMPLEMENTED**.
* **Endpoint**: `PATCH /v1/profiles/me` -> returns updated `ProfileResponse`.
* **Restrictions**: Cannot alter another user's profile. Validated at FastAPI layer and enforced via PostgreSQL RLS `profiles_update` (`id = auth.uid()`).

### 5. Profile Discoverability Toggle
* **What the User Can Do**: Toggle their account visibility between discoverable and hidden.
* **Data Involved**: `public.profiles.is_discoverable` (boolean).
* **Service / Table**: `public.profiles`, `backend.app.profiles.router.update_my_profile`, RLS policy `profiles_select`.
* **Status**: **IMPLEMENTED**.
* **Endpoint**: `PATCH /v1/profiles/me` with `{"is_discoverable": false}`.
* **Restrictions**: When `false`, other users querying `GET /v1/profiles/{id}` or `GET /v1/astrology/people/{id}/safe-astro` receive HTTP 404 Privacy-Safe Not Found.

### 6. Account Deletion
* **What the User Can Do**: Permanently delete account and cascade-delete all associated personal and relational data.
* **Data Involved**: `auth.users`, cascading to `profiles`, `birth_data`, `astro_private`, `astro_safe_profile`, `connections`, `compatibility_results`, `conversations`, `messages`, `notifications`.
* **Service / Table**: PostgreSQL foreign key constraints with `ON DELETE CASCADE`.
* **Status**: **PARTIAL**. Database foreign keys support full cascade deletion, and Supabase Auth supports user deletion, but there is **no dedicated FastAPI endpoint** (e.g. `DELETE /v1/users/me`) implemented in the application layer.

### 7. Birth Data Input & Versioning
* **What the User Can Do**: Enter raw birth date, birth time, precision indicator, timezone, latitude, longitude, and place label. Updates automatically bump the data version counter.
* **Data Involved**: `birth_date` (DATE), `birth_time` (TIME, nullable), `birth_time_precision` (ENUM: `'exact'`, `'approximate'`, `'unknown'`), `birth_timezone` (TEXT, IANA), `latitude` (FLOAT), `longitude` (FLOAT), `place_label` (TEXT), `data_version` (INT).
* **Service / Table**: `public.birth_data`, trigger `birth_data_bump_version` (`supabase/migrations/015_triggers.sql`), validation service `backend.app.astrology.validation.validate_birth_data`.
* **Status**: **IMPLEMENTED (Client via Supabase PostgREST / Backend via DB Connection)**.
* **Endpoint / Path**: Direct Supabase Client `supabase.from("birth_data").upsert(...)` governed by strict RLS (`birth_data_select_own`, `birth_data_insert_own`, `birth_data_update_own`). No direct `POST /v1/birth-data` route exists in FastAPI.
* **Restrictions**: Raw birth data is strictly **owner-only**. Other authenticated users have zero read privileges (`REVOKE ALL`).

---

## 4. DOMAIN B: ASTROLOGY / SELF UNDERSTANDING

This audit distinguishes between:
1. **CALCULATED INTERNALLY** (Server-side mathematical execution)
2. **EXPOSED THROUGH API** (Available in FastAPI response schemas)
3. **CURRENTLY CONSUMED BY FRONTEND** (Actively fetched and rendered in `frontend/src/`)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          CALCULATED INTERNALLY                                 │
│  • Exact Julian Day (12:00 UTC mean noon fallback)                             │
│  • 10 Planet Ecliptic Longitudes (Swiss Ephemeris high precision)               │
│  • Planetary Retrograde Statuses (Speed longitude < 0.0)                        │
│  • Exact Ascendant Longitude (Placidus system)                                  │
│  • 12 Placidus House Cusps (JSONB array)                                        │
│  • 5 Ptolemaic Natal Aspect Geometries (Conjunction, Sextile, Square, Trine, Opp)│
│  • Dominant Element & Modality Weighted Derivations                             │
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           EXPOSED THROUGH API                                   │
│  • Sun Sign, Moon Sign, Ascendant Sign (or null if time unknown)                │
│  • Primary Element (Fire, Earth, Air, Water)                                    │
│  • Primary Modality (Cardinal, Fixed, Mutable)                                  │
│  • Source Birth Data Version & Engine Version ("1.0.0")                         │
│  • Updated Timestamp                                                            │
│  [EXCLUDED: Raw longitudes, retrogrades, houses, and single-chart natal aspects]│
└───────────────────────────────────────┬─────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      CURRENTLY CONSUMED BY FRONTEND                             │
│  • Rendered in `SelfAstrologyPage.tsx`:                                         │
│      - "Big Three" Summary Card (Sun, Moon, Rising)                             │
│      - Elemental Signature Badge (Dominant Element + Modality)                  │
│      - Birth Data Quality Banner (Precision indicator + Recalculate CTA)        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Astrology Capability Breakdown

| Astrological Attribute | Calculated Internally? | Stored Where? | Exposed in API? | API Endpoint | Consumed in Frontend? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Julian Day Calculation** | YES (`swe.julday`) | Memory | NO | None | NO | **IMPLEMENTED** (Internal) |
| **Sun Sign** | YES (`longitude_to_sign`) | `astro_safe_profile` | YES (`sun_sign`) | `GET /v1/astrology/profile/safe-astro` | YES (`SelfAstrologyPage.tsx`) | **IMPLEMENTED** |
| **Moon Sign** | YES (`longitude_to_sign`) | `astro_safe_profile` | YES (`moon_sign`) | `GET /v1/astrology/profile/safe-astro` | YES (`SelfAstrologyPage.tsx`) | **IMPLEMENTED** |
| **Ascendant Sign** | YES (`swe.houses` -> sign) | `astro_safe_profile` | YES (`ascendant_sign`) | `GET /v1/astrology/profile/safe-astro` | YES (`SelfAstrologyPage.tsx`) | **IMPLEMENTED** |
| **Primary Element** | YES (`Counter.most_common`) | `astro_safe_profile` | YES (`element_primary`) | `GET /v1/astrology/profile/safe-astro` | YES (`SelfAstrologyPage.tsx`) | **IMPLEMENTED** |
| **Primary Modality** | YES (`Counter.most_common`) | `astro_safe_profile` | YES (`modality_primary`) | `GET /v1/astrology/profile/safe-astro` | YES (`SelfAstrologyPage.tsx`) | **IMPLEMENTED** |
| **Exact 10 Planet Degrees** | YES (`swe.calc_ut`) | `astro_private` | NO (`REVOKE ALL`) | None | NO | **IMPLEMENTED** (Private Only) |
| **Planetary Retrogrades** | YES (`speed_lon < 0`) | `astro_private` | NO (`REVOKE ALL`) | None | NO | **IMPLEMENTED** (Private Only) |
| **12 Placidus House Cusps**| YES (`swe.houses`) | `astro_private` | NO (`REVOKE ALL`) | None | NO | **IMPLEMENTED** (Private Only) |
| **Single-User Natal Aspects**| NO (Engine exists in `aspects.py`, but only called in synastry) | None | NO | None | NO | **PARTIAL** (Engine ready; no natal pipeline) |
| **Astrology Recalculation**| YES (`recalculate_user_astrology`) | `astro_private` & `astro_safe` | YES | `POST /v1/astrology/profile/recalculate` | YES (`SelfAstrologyPage.tsx`) | **IMPLEMENTED** |
| **Unknown Time Handling** | YES (Sets Asc/Houses to None; mean noon) | Handled in math | YES (Ascendant returned as null) | Safe astro routes | YES (UI handles null Ascendant) | **IMPLEMENTED** |
| **Polar Region Error Handling**| YES (lat > 66.5° raises `placidus_polar_error`) | Handled in code | YES (HTTP 400 JSON) | Recalculate route | YES (Error state rendered) | **IMPLEMENTED** |
| **Chiron / Lilith / Nodes**| NO | None | NO | None | NO | **NOT FOUND** |

---

## 5. DOMAIN C: DAILY ENERGY / CURRENT SKY

* **Operational Status**: **STUB / NOT IMPLEMENTED**.
* **Current Code State**:
  * `backend/app/astrology/transits.py` contains only a 4-line docstring: `"""\nTransit calculations for Daily Energy.\n"""`.
  * `backend/app/jobs/daily_energy.py` defines `generate_daily_energy_for_user(user_id, energy_date, db)`, which inserts hardcoded static content into `public.daily_energies`:
    * `signals = '[]'::jsonb`
    * `interpretation = '{"summary": "A dynamic day for creative exploration."}'::jsonb`
    * `engine_version = '1.0.0'`
  * **API Route**: There is **no route** in `backend/app/api/router.py` or `astrology/router.py` to retrieve daily energy.
  * **Frontend**: `frontend/src/` contains zero queries, pages, or components for Daily Energy.
* **Documented vs Implemented Discrepancy**: While `docs/PRODUCT_SPECIFICATION.md` describes Daily Energy as the *"primary daily habit hook and first personal taste of JESTER"*, the current backend has **no ephemeris transit calculation, no automated recurring job runner, no API endpoint, and no frontend rendering**.

---

## 6. DOMAIN D: PEOPLE / DISCOVERY

| Capability | Backend Status | API Route | Frontend Support | How it Works Today |
| :--- | :--- | :--- | :--- | :--- |
| **Public Profile by UUID** | IMPLEMENTED | `GET /v1/profiles/{id}` | YES (`PersonProfilePage.tsx`) | Fetches target profile. Block-aware; requires `is_discoverable = true`. |
| **Safe Astrology by UUID** | IMPLEMENTED | `GET /v1/astrology/people/{id}/safe-astro` | YES (`PersonProfilePage.tsx`) | Fetches Sun, Moon, Rising, Element, Modality. Hides exact birth time/coordinates. |
| **Discoverability Filtering**| IMPLEMENTED | Handled in SQL & RLS | YES | Profiles with `is_discoverable = false` return 404 to other users. |
| **Mutual Block Protection**| IMPLEMENTED | `is_user_blocked(a, b)` | YES | If User A blocks User B (or vice versa), mutual queries return 404. |
| **People Search / Feed** | **NOT FOUND in FastAPI** | None | **WORKAROUND via Direct Supabase Query** | In `PersonProfilePage.tsx`, the frontend executes a direct PostgREST query: `supabase.from("profiles").select("id, display_name...").eq("is_discoverable", true).limit(20)`. No FastAPI search or directory route exists. |
| **Compatibility-Based Match**| NOT IMPLEMENTED | None | NO | Cannot calculate compatibility across a candidate feed without mutual connection. |
| **Nearby / Geolocation Search**| NOT IMPLEMENTED | None | NO | Lat/Lon in `birth_data` is birth origin, not current location. Profiles store only text `city`. |
| **Recommendations Engine** | NOT IMPLEMENTED | None | NO | No recommendation algorithms exist. |

---

## 7. DOMAIN E: RELATIONSHIP / COMPATIBILITY / SYNASTRY (SYNASTRY V1)

Jester V1 features a deterministic, mathematically rigorous relationship calculation engine (`synastry-v1.0.0`) implemented in `backend/app/compatibility/`.

### Detailed Synastry V1 Output Inventory

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          SYNASTRY V1 ENGINE OUTPUTS                              │
├────────────────────────────┬─────────────────────────┬───────────────────────────┤
│ Output Element             │ Mathematical Logic      │ API Response Field        │
├────────────────────────────┼─────────────────────────┼───────────────────────────┤
│ 1. Composite Score         │ Stretched Weighted Mean │ `score` (float 10.0-98.0) │
│ 2. Emotional Harmony       │ Lunar/Luminary + Water  │ `dimensions.emotional...` │
│ 3. Communication           │ Mercury + Air Synergy   │ `dimensions.communication`│
│ 4. Attraction              │ Venus-Mars + Fire/Air   │ `dimensions.attraction`   │
│ 5. Growth & Long-Term      │ Saturn + Modality Mix   │ `dimensions.growth...`    │
│ 6. Ranked Signals (Max 6)  │ Weight * Strength Desc  │ `signals` (list[dict])    │
│ 7. Bridge Topics (Max 4)   │ Dominant Element/Aspect │ `best_topics` (list[str]) │
│ 8. Starters (Max 3)        │ Signal Rule Lookup      │ `conversation_starters`   │
│ 9. Data Quality & Precision│ Precision worst-case    │ `data_quality` (dict)     │
│ 10. Astronomical Evidence  │ Complete Aspect Ledger  │ Stored in DB; API dropped │
└────────────────────────────┴─────────────────────────┴───────────────────────────┘
```

#### 1. Overall Compatibility Score (`score`)
* **What it Represents**: Holistic interpersonal synergy rating on a scale of `10.0` to `98.0` (with `65.0` as baseline for charts with insufficient aspect links).
* **Deterministic**: 100% deterministic mathematical formula with non-linear curve stretch ($0.85$ power curve).
* **API Response Field**: `StructuredCompatibilityResponse.score`.
* **Frontend Consumability**: Consumed and rendered prominently in `ComparePage.tsx` and `WhyPage.tsx`.

#### 2. Relational Dimensions (4 Discrete Subscores)
* **Emotional Harmony (`dimensions.emotional_harmony`)**: Derived from Sun-Moon, Moon-Moon, Moon-Venus affinities, and element resonance.
* **Communication (`dimensions.communication`)**: Derived from Mercury cross-aspects and elemental air compatibility.
* **Attraction (`dimensions.attraction`)**: Derived from Venus-Mars, Sun-Moon polarities, Venus-Pluto contacts, and Fire/Air counts.
* **Growth & Long-Term (`dimensions.growth_long_term`)**: Derived from Saturn stabilizing links, challenging squares/oppositions, and modality balance.
* **Deterministic**: 100% deterministic formula.
* **Known Cache-Hit Defect in Router**: When a compatibility result is freshly calculated, `dimensions` is returned to the caller. However, when fetched from the database cache (`public.compatibility_results`), the router fails to populate `dimensions`, resulting in an empty dictionary `{}`!

#### 3. Top 6 Ranked Relational Signals (`signals`)
* **What it Represents**: Qualitative dynamics extracted from cross-aspects where normalized strength $\ge 0.40$, sorted by importance ($\text{Weight} \times \text{Strength}$).
* **Signal Structure**:
  * `type` (e.g. `"sun_trine_moon"`, `"venus_conjunction_mars"`, `"mars_square_saturn"`)
  * `category` (`"harmony"`, `"attraction"`, `"communication"`, `"growth"`, `"stability"`, `"notice"`)
  * `strength` (`"high"` if strength $\ge 0.70$, otherwise `"medium"`)
  * `label` (Curated title, e.g. `"Emotional Resonance"`, `"Magnetic Chemistry"`, `"Pacing Tension"`)
  * `source_aspects` (e.g. `["Sun Trine Moon (Orb 1.2°)"]`)
* **API Response Field**: `StructuredCompatibilityResponse.signals`.
* **Frontend Consumability**: Consumed and rendered in `ComparePage.tsx` with category-coded badge styling.

#### 4. Bridge Conversation Topics (`best_topics`)
* **What it Represents**: Up to 4 shared conversational domains inferred from elemental synergy and dominant aspect patterns.
* **Domains Available**:
  * Air / Mercury: Books, Philosophy, Ideas, Creative Work
  * Fire / Mars: Travel, Adventure, Fitness, Ambition
  * Water / Moon: Art, Music, Psychology, Cinema
  * Earth / Saturn: Architecture, Food, Design, Lifestyle
* **API Response Field**: `StructuredCompatibilityResponse.best_topics`.
* **Frontend Consumability**: Consumed in `WhyPage.tsx` as clickable topic tags.

#### 5. Tailored Conversation Starters (`conversation_starters`)
* **What it Represents**: Up to 3 curated icebreaker prompts mapped directly to the pair's highest-strength active signals.
* **Examples**:
  * `sun_trine_moon`: *"What is something that instantly makes you feel understood?"*
  * `venus_conjunction_mars`: *"What is your idea of a perfect spontaneous date?"*
  * `mercury_trine_mercury`: *"What topic could you talk about for hours without getting bored?"*
* **API Response Field**: `StructuredCompatibilityResponse.conversation_starters`.
* **Frontend Consumability**: Consumed in `WhyPage.tsx` with "Copy to Clipboard" and "Send to Direct Chat" actions.

#### 6. Data Quality & Precision Metadata (`data_quality`)
* **Fields**:
  * `time_precision`: Worst-case precision of the two users (`"exact"`, `"approximate"`, `"unknown"`).
  * `confidence`: Float rating (`1.0` if both exact, `0.85` if approximate, `0.75` if unknown time, `0.50` if minimal aspects).
  * `houses_used`: Strictly `false` in Synastry V1.
  * `ascendant_used`: `true` only if both users have known birth times.
* **API Response Field**: `StructuredCompatibilityResponse.data_quality`.
* **Frontend Consumability**: Consumed and rendered in `ComparePage.tsx`.

#### 7. Astronomical Evidence Trace (`evidence_trace`)
* **What it Represents**: Complete audit trail of every active cross-aspect, including celestial bodies, exact longitudes, aspect type, target angle, actual circular distance, orb variance, strength decay, pair weight, and point contributions to each subscore.
* **Database Storage**: Saved in `public.compatibility_results.evidence_trace` (JSONB column added in Migration 021).
* **API Status**: **OMITTED FROM API RESPONSE MODEL**. The Pydantic model `StructuredCompatibilityResponse` does not include `evidence_trace`.
* **Frontend Consumability**: **NO** (Not accessible via API).

---

## 8. DOMAIN F: DEEP ANALYSIS CAPABILITY AUDIT

### What Data is Available for Deep Analysis Today?
1. **Target User Profile Card**: Display name, bio, city, occupation, avatar URL.
2. **Target User Public Astrology**: Sun sign, Moon sign, Ascendant sign, Primary Element, Primary Modality.
3. **Core Synastry Score**: Non-linear normalized overall score (`10.0` to `98.0`).
4. **4 Dimensional Subscores**: Numerical ratings for Emotional Harmony, Communication, Attraction, and Growth.
5. **Top 6 Ranked Relational Signals**: Categorized labels with source aspect descriptions.
6. **4 Bridge Topics & 3 Conversation Starters**: Actionable interpersonal connection points.
7. **Complete Astronomical Evidence Trace**: 10 to 25 detailed cross-aspect records stored in the database.

### What is NOT Available / Missing?
1. **AI / LLM Narrative Synthesis ("Jester Voice")**: No generative prose, contextual storytelling, or natural-language translation exists.
2. **House Overlay Calculations**: Person A's planets projected into Person B's natal houses is not implemented.
3. **Composite Midpoint Charts**: Not implemented.
4. **Deep Unlock Entitlement / Payment Ledger**: No database schema, token balance, coin transaction, or paywall gatekeeper exists.

### What is Deterministic vs AI?
* **Deterministic**: 100% of all calculations, scores, dimensions, signal mappings, topic selections, and starter prompts are deterministic.
* **AI / LLM**: 0% operational. All AI modules are stubs.

---

## 9. DOMAIN G: CONNECTIONS & SOCIAL GRAPH

### Connection State Machine
The connection system enforces strict bidirectional relationship states in `public.connections`:

```
                 ┌────────────────────────────────┐
                 │       POST /v1/connections    │
                 │     (Initiate Request)         │
                 └───────────────┬────────────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │        pending        │
                     └───────────┬───────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     accept      │     │     decline     │     │      block      │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ status:         │     │ status:         │     │ status:         │
│   accepted      │     │   declined      │     │   blocked       │
│ blocked_by:     │     │ blocked_by:     │     │ blocked_by:     │
│   null          │     │   null          │     │   <blocker_id>  │
└────────┬────────┘     └─────────────────┘     └────────┬────────┘
         │                                               │
         ├───────────────────────┬───────────────────────┘
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│     remove      │     │     unblock     │
├─────────────────┤     ├─────────────────┤
│ status:         │     │ status:         │
│   removed       │     │   removed       │
│ blocked_by:     │     │ blocked_by:     │
│   null          │     │   null          │
└─────────────────┘     └─────────────────┘
```

### Critical Rules & Invariants:
1. **Canonical Pair Constraint**: User pairs are stored as `(user_a_id, user_b_id)` where `user_a_id < user_b_id`. Duplicate or reversed rows are prohibited by unique constraint.
2. **Revoked Direct Updates**: Clients cannot issue direct SQL `UPDATE` or `DELETE` commands on `connections` (`017_grants.sql`). All state changes MUST pass through `/v1/connections/{id}/transition`.
3. **Unblock Behavior**: Unblocking transitions the connection to `'removed'`, never auto-restoring an `'accepted'` status.
4. **Mutual Block Hiding**: When blocked, the blocked user cannot see the connection row or discover the blocker's profile.

### CRITICAL PRODUCT DISCREPANCY: The Compatibility Gatekeeper
* **Implementation Reality**: In `backend/app/comparisons/router.py`:
  ```python
  cur.execute("SELECT public.has_active_connection(%s, %s) as is_active;", (user_a, user_b))
  if not res or not res["is_active"]:
      raise ForbiddenException("Active connection required to view compatibility")
  ```
* **Product Impact**: A user **CANNOT** compare themselves with another user or view "Why This Person" unless both users have established an active, accepted connection!
* **Discrepancy with Product Specs**: Product specs describe comparing discovered people before connecting (*"They show the match. JESTER explains the connection"*). Under current backend code, this is **BLOCKED (HTTP 403 Forbidden)**.

---

## 10. DOMAIN H: MESSAGING

* **Implementation Status**: **IMPLEMENTED**.
* **Supported Capabilities**:
  * `POST /v1/conversations`: Finds existing or creates new direct conversation between two users.
  * `GET /v1/conversations/{id}/messages`: Fetches chronological message history for a conversation.
  * `POST /v1/conversations/{id}/messages`: Sends a text message body.
* **Security & Connection Requirements**:
  * Enforced via PostgreSQL function `public.is_active_direct_conversation(conv_id, user_id)`.
  * Messaging is **strictly prohibited** unless the participants have an active, accepted, unblocked connection in `public.connections`.
* **Frontend Consumability**: Fully integrated in `frontend/src/modules/chat/ChatPage.tsx`, with optional pre-filled conversation starter query parameters.

---

## 11. DOMAIN I: NOTIFICATIONS

* **Implementation Status**: **IMPLEMENTED**.
* **Supported Capabilities**:
  * `GET /v1/notifications`: Lists in-app notifications for the authenticated user, ordered by `created_at DESC`.
  * `PATCH /v1/notifications/{id}/read`: Marks a notification as read (`read_at = now()`).
* **Triggering Events**:
  * Connection requests (`connection_request_received`).
  * Connection state changes (`connection_accepted`).
* **Limitations**:
  * **In-App Only**: Operates via database table `public.notifications`.
  * **No Native Push**: APNs (iOS) and FCM (Android) push notification dispatchers are **NOT IMPLEMENTED**.
  * **No Email Delivery**: No transactional email dispatcher is operational.

---

## 12. DOMAIN J: AI / LLM CAPABILITIES

| AI Subsystem Component | Architecturally Defined? | Code File | Current Operational State |
| :--- | :--- | :--- | :--- |
| **OpenAI Environment Config** | YES (`OPENAI_API_KEY`, `LLM_MODEL`) | `backend/app/config.py` | Configured; no active clients |
| **Interpretation Engine** | YES | `backend/app/interpretation/engine.py` | **STUB (75 bytes; empty)** |
| **Jester Voice Client** | YES | `backend/app/interpretation/jester.py` | **STUB (107 bytes; empty)** |
| **Prompt Templates** | YES | `backend/app/interpretation/prompts.py` | **STUB (54 bytes; empty)** |
| **Pydantic AI Schemas** | YES | `backend/app/interpretation/models.py` | Defined (`JesterMessageRequest`, `JesterMessageResponse`) |
| **Router Mounting** | NO | `backend/app/api/router.py` | Not mounted in API router |
| **Live Prompt Execution** | NO | None | **ZERO LLM CALLS OPERATIONAL** |

> **Conclusion**: The current JESTER backend cannot generate user-facing natural-language insights or dynamic Jester voice interpretations today. All user-facing text is produced via deterministic dictionary lookups.

---

## 13. DOMAIN K: PRIVACY / SAFETY / DATA VISIBILITY MATRIX

| Data Field / Entity | Owning User | Connected Friend | Discovered User | Public / Anon | Client App Storage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Raw Birth Date** | **READ / WRITE** | NO ACCESS | NO ACCESS | NO ACCESS | Server DB Only |
| **Exact Birth Time** | **READ / WRITE** | NO ACCESS | NO ACCESS | NO ACCESS | Server DB Only |
| **Birth Location / Lat / Lon** | **READ / WRITE** | NO ACCESS | NO ACCESS | NO ACCESS | Server DB Only |
| **Exact Planet Longitudes** | **NO ACCESS** | NO ACCESS | NO ACCESS | NO ACCESS | `astro_private` (Server Only) |
| **Placidus House Cusps** | **NO ACCESS** | NO ACCESS | NO ACCESS | NO ACCESS | `astro_private` (Server Only) |
| **Zodiac Signs (Sun, Moon, Asc)**| **READ ONLY** | **READ ONLY** | **READ ONLY\*** | NO ACCESS | Safe Profile View |
| **Primary Element & Modality** | **READ ONLY** | **READ ONLY** | **READ ONLY\*** | NO ACCESS | Safe Profile View |
| **Public Profile (Bio, City)** | **READ / WRITE** | **READ ONLY** | **READ ONLY\*** | NO ACCESS | Client App Cache |
| **Synastry Compatibility Score** | **READ ONLY** | **READ ONLY\*\*** | NO ACCESS | NO ACCESS | Client App Cache |
| **Detailed Aspect Evidence Trace**| **NO ACCESS** | NO ACCESS | NO ACCESS | NO ACCESS | Server DB Only |
| **Direct Chat Messages** | **READ / WRITE** | **READ / WRITE** | NO ACCESS | NO ACCESS | Client App Cache |

*\*Requires `is_discoverable = true` and no active block.*  
*\*\*Requires connection status `'accepted'`.*

---

## 14. DOMAIN L: FRONTEND CONSUMABILITY AUDIT

| Capability | Backend Operational | API Endpoint Available | Frontend Integration Active | User Can Access Today? | Evidence File |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **User Sign In / Sign Up** | YES | YES (Supabase Auth) | YES | **YES** | `modules/auth/LoginPage.tsx` |
| **Birth Data Onboarding** | YES | YES (PostgREST) | YES | **YES** | `modules/onboarding/BirthDataOnboardingPage.tsx` |
| **View Own Profile** | YES | `GET /v1/profiles/me` | YES | **YES** | `modules/self/SelfProfilePage.tsx` |
| **Edit Own Profile** | YES | `PATCH /v1/profiles/me` | YES | **YES** | `modules/self/SelfProfilePage.tsx` |
| **View Own Safe Astrology** | YES | `GET /v1/astrology/profile/safe-astro` | YES | **YES** | `modules/self/SelfAstrologyPage.tsx` |
| **Recalculate Astrology** | YES | `POST /v1/astrology/profile/recalculate`| YES | **YES** | `modules/self/SelfAstrologyPage.tsx` |
| **View Other Profile by ID**| YES | `GET /v1/profiles/{id}` | YES | **YES** | `modules/people/PersonProfilePage.tsx` |
| **View Other Safe Astrology**| YES | `GET /v1/astrology/people/{id}/safe-astro` | YES | **YES** | `modules/people/PersonProfilePage.tsx` |
| **List My Connections** | YES | `GET /v1/connections` | YES | **YES** | `modules/connections/ConnectionsPage.tsx` |
| **Send Connection Request** | YES | `POST /v1/connections` | YES | **YES** | `modules/connections/ConnectionsPage.tsx` |
| **Accept / Decline / Block** | YES | `POST /v1/connections/{id}/transition`| YES | **YES** | `modules/connections/ConnectionsPage.tsx` |
| **Compare Connected Users** | YES | `POST /v1/compare` | YES | **YES** | `modules/compatibility/ComparePage.tsx` |
| **View "Why This Person"** | YES | `GET /v1/people/{id}/why` | YES | **YES** | `modules/compatibility/WhyPage.tsx` |
| **Direct Chat Messaging** | YES | `/v1/conversations/...` | YES | **YES** | `modules/chat/ChatPage.tsx` |
| **In-App Notifications** | YES | `/v1/notifications/...` | YES | **YES** | `modules/notifications/NotificationsPage.tsx` |
| **Compare Non-Connected User**| BLOCKED | `POST /v1/compare` (Returns 403) | YES | **NO (HTTP 403)** | `modules/compatibility/ComparePage.tsx:21` |
| **Browse / Search People Feed**| NO | None | WORKAROUND | **PARTIAL** | Direct PostgREST query in `PersonProfilePage.tsx` |
| **Daily Energy / Day Vibe** | STUB | None | NO | **NO** | `jobs/daily_energy.py` |
| **View Synastry Evidence Trace**| DB ONLY | Dropped from response model | NO | **NO** | `supabase/migrations/021_...` |
| **AI Jester Interpretation**| STUB | None | NO | **NO** | `backend/app/interpretation/` |

---

## 15. DOMAIN M: COMPLETE ENDPOINT INVENTORY

| Method | Endpoint Path | Primary Purpose | Request Payload | Response Model | Auth | User Capability | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/healthz` | System liveness probe | None | `{"status": "ok"}` | Public | Load balancer check | IMPLEMENTED |
| `GET` | `/v1/health` | Service & DB probe | None | Health details | Public | Diagnostic check | IMPLEMENTED |
| `GET` | `/v1/users/me` | Account identity | None | `UserResponse` | Bearer | Account view | IMPLEMENTED |
| `GET` | `/v1/profiles/me` | Self profile view | None | `ProfileResponse` | Bearer | View my profile | IMPLEMENTED |
| `PATCH`| `/v1/profiles/me` | Self profile edit | `ProfileUpdate` | `ProfileResponse` | Bearer | Update profile | IMPLEMENTED |
| `GET` | `/v1/profiles/{id}` | Target profile view | None | `ProfileResponse` | Bearer | Inspect person | IMPLEMENTED |
| `POST` | `/v1/astrology/profile/recalculate` | Recompute natal chart | None | `SafeDerivedAstrologyResponse` | Bearer | Refresh astrology | IMPLEMENTED |
| `GET` | `/v1/astrology/profile/safe-astro` | Self safe astrology | None | `SafeDerivedAstrologyResponse` | Bearer | View Big Three | IMPLEMENTED |
| `GET` | `/v1/astrology/people/{id}/safe-astro`| Target safe astrology | None | `SafeDerivedAstrologyResponse` | Bearer | View person astro | IMPLEMENTED |
| `GET` | `/v1/connections` | List user connections | None | `list[ConnectionResponse]` | Bearer | View social graph | IMPLEMENTED |
| `POST` | `/v1/connections` | Send connection request | `ConnectionCreate` | `ConnectionResponse` | Bearer | Request connection | IMPLEMENTED |
| `POST` | `/v1/connections/{id}/transition` | State transition | `ConnectionTransition` | `ConnectionResponse` | Bearer | Accept/block friend | IMPLEMENTED |
| `POST` | `/v1/compare` | Synastry compatibility | `CompareRequest` | `StructuredCompatibilityResponse` | Bearer | Compare with friend | IMPLEMENTED (Requires connection) |
| `GET` | `/v1/people/{id}/why` | Why this person alias | None | `StructuredCompatibilityResponse` | Bearer | Relationship breakdown | IMPLEMENTED (Requires connection) |
| `POST` | `/v1/conversations` | Get/create direct chat | `DirectConversationCreate` | `ConversationResponse` | Bearer | Open direct chat | IMPLEMENTED (Requires connection) |
| `GET` | `/v1/conversations/{id}/messages` | List chat messages | None | `list[MessageResponse]` | Bearer | Read chat history | IMPLEMENTED (Requires connection) |
| `POST` | `/v1/conversations/{id}/messages` | Send chat message | `MessageCreate` | `MessageResponse` | Bearer | Dispatch chat message| IMPLEMENTED (Requires connection) |
| `GET` | `/v1/notifications` | List notifications | None | `list[NotificationResponse]` | Bearer | View in-app alerts | IMPLEMENTED |
| `PATCH`| `/v1/notifications/{id}/read` | Mark alert read | None | `NotificationResponse` | Bearer | Dismiss notification | IMPLEMENTED |

---

## 16. DOMAIN N: DATABASE CAPABILITY MAP

| User Capability | Database Table | Key Columns Utilized | Privacy & RLS Rule |
| :--- | :--- | :--- | :--- |
| **Account Identity** | `auth.users` | `id`, `email`, `role` | Supabase internal auth schema |
| **Public Profiles** | `public.profiles` | `display_name`, `avatar_url`, `bio`, `city`, `occupation`, `is_discoverable` | Public to authenticated if `is_discoverable = true` and unblocked |
| **Private Birth Info** | `public.birth_data` | `birth_date`, `birth_time`, `precision`, `birth_timezone`, `lat`, `lon`, `version` | **Owner-only** (`user_id = auth.uid()`). Strict client revoke |
| **Raw Chart Degrees** | `public.astro_private`| 10 planet longitudes, `ascendant_longitude`, `houses`, `retrogrades` | **Server-only** (`REVOKE ALL`). No client grants |
| **Safe Astrology** | `public.astro_safe_profile` | `sun_sign`, `moon_sign`, `ascendant_sign`, `element_primary`, `modality_primary` | Public to authenticated if profile is discoverable and unblocked |
| **Social Graph** | `public.connections` | `user_a_id`, `user_b_id`, `status`, `initiated_by`, `blocked_by` | Mutual participants only; direct updates revoked from clients |
| **Synastry Results** | `public.compatibility_results`| `score`, `signals`, `best_topics`, `conversation_starters`, `evidence_trace` | Both participants only; requires active accepted connection |
| **Daily Energy** | `public.daily_energies` | `energy_date`, `signals`, `interpretation`, `engine_version` | Owner-only (`user_id = auth.uid()`) |
| **Direct Chat Rooms** | `public.conversations` | `conversation_type`, `created_by` | Participants with active connection only |
| **Chat Membership** | `public.conversation_members`| `conversation_id`, `user_id`, `joined_at` | Active conversation members only |
| **Direct Messages** | `public.messages` | `conversation_id`, `sender_user_id`, `body`, `created_at` | Active conversation members only |
| **In-App Alerts** | `public.notifications` | `user_id`, `type`, `payload`, `read_at` | Owner-only (`user_id = auth.uid()`) |

---

## 17. COMPLETE USER-FACING CAPABILITY MASTER MATRIX

| # | Capability | Domain | What User Gets | Backend | API | Frontend | Status | Deterministic / AI | Operational Restrictions |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Email/Password Auth | Account | Secure session login & token refresh | Supabase | Supabase SDK | `LoginPage.tsx` | IMPLEMENTED | Deterministic | Valid email/pass required |
| **2** | View Account Details | Account | User UUID, email address, role | FastAPI | `GET /v1/users/me` | App Context | IMPLEMENTED | Deterministic | Authenticated caller only |
| **3** | Auto Profile Creation | Profile | Auto-generated profile on initial login | FastAPI | `GET /v1/profiles/me` | App Context | IMPLEMENTED | Deterministic | Self-heals missing rows |
| **4** | View Own Profile | Profile | Display name, avatar, bio, city, job | FastAPI | `GET /v1/profiles/me` | `SelfProfilePage.tsx` | IMPLEMENTED | Deterministic | Authenticated caller only |
| **5** | Edit Own Profile | Profile | Updated bio, city, avatar, occupation | FastAPI | `PATCH /v1/profiles/me` | `SelfProfilePage.tsx` | IMPLEMENTED | Deterministic | Authenticated caller only |
| **6** | Toggle Discoverability | Profile | Ability to hide account from public | FastAPI | `PATCH /v1/profiles/me` | `SelfProfilePage.tsx` | IMPLEMENTED | Deterministic | Affects all search & profile views |
| **7** | Save Birth Data | Birth Info | Raw birth date, time, location, tz | PostgREST | PostgREST Upsert | `BirthDataOnboardingPage.tsx`| IMPLEMENTED | Deterministic | Strictly owner-only |
| **8** | Precise Time Handling | Birth Info | Exact birth time & Placidus houses | Calculator | Recalculate endpoint | Onboarding Flow | IMPLEMENTED | Deterministic | Lat/Lon must be present |
| **9** | Approx Time Handling | Birth Info | Approximate Ascendant calculation | Calculator | Recalculate endpoint | Onboarding Flow | IMPLEMENTED | Deterministic | Scales confidence to 0.85 |
| **10**| Unknown Time Handling | Birth Info | Noon mean chart; Ascendant omitted | Calculator | Recalculate endpoint | Onboarding Flow | IMPLEMENTED | Deterministic | Scales confidence to 0.75 |
| **11**| Recalculate Natal Chart| Astrology | Computes ephemeris coordinates | Natal Service | `POST /v1/astrology/.../recalculate` | `SelfAstrologyPage.tsx` | IMPLEMENTED | Deterministic | Requires birth data row |
| **12**| View Own Sun Sign | Astrology | Zodiac Sun sign (e.g. "Scorpio") | Calculator | `GET /v1/astrology/.../safe-astro` | `SelfAstrologyPage.tsx` | IMPLEMENTED | Deterministic | Computed from Swiss Ephemeris |
| **13**| View Own Moon Sign | Astrology | Zodiac Moon sign (e.g. "Cancer") | Calculator | `GET /v1/astrology/.../safe-astro` | `SelfAstrologyPage.tsx` | IMPLEMENTED | Deterministic | Computed from Swiss Ephemeris |
| **14**| View Own Rising Sign | Astrology | Zodiac Ascendant sign (or null) | Calculator | `GET /v1/astrology/.../safe-astro` | `SelfAstrologyPage.tsx` | IMPLEMENTED | Deterministic | Null if birth time unknown |
| **15**| View Dominant Element | Astrology | Primary Element (Fire/Earth/Air/Water) | Calculator | `GET /v1/astrology/.../safe-astro` | `SelfAstrologyPage.tsx` | IMPLEMENTED | Deterministic | Weighted personal chart count |
| **16**| View Dominant Modality | Astrology | Primary Modality (Card/Fixed/Mut) | Calculator | `GET /v1/astrology/.../safe-astro` | `SelfAstrologyPage.tsx` | IMPLEMENTED | Deterministic | Weighted personal chart count |
| **17**| Single Natal Aspects | Astrology | User's own chart aspect list | Aspects Module | None | None | PARTIAL | Deterministic | Engine ready; no API route |
| **18**| Today's Energy / Transits| Astrology | Daily transit forecast & vibe | transits stub | None | None | STUB | Deterministic / AI | Transits file is empty stub |
| **19**| View Target Profile | People | Name, avatar, bio, city of other user | FastAPI | `GET /v1/profiles/{id}` | `PersonProfilePage.tsx` | IMPLEMENTED | Deterministic | 404 if hidden or blocked |
| **20**| View Target Safe Astro | People | Target Sun, Moon, Rising, Element | FastAPI | `GET /v1/astrology/people/{id}/...`| `PersonProfilePage.tsx` | IMPLEMENTED | Deterministic | 404 if hidden or blocked |
| **21**| Browse Discoverable Users| People | List of discoverable users | PostgREST | PostgREST Direct Query | `PersonProfilePage.tsx` | PARTIAL | Deterministic | Uses direct DB query; no API route |
| **22**| People Search / Filters | People | Filter people by sign/element/city | None | None | None | NOT FOUND | Deterministic | No search backend exists |
| **23**| List My Connections | Social | Incoming/outgoing/active connections | FastAPI | `GET /v1/connections` | `ConnectionsPage.tsx` | IMPLEMENTED | Deterministic | Block-aware |
| **24**| Send Connection Request | Social | Transition pair to 'pending' state | FastAPI | `POST /v1/connections` | `PersonProfilePage.tsx` | IMPLEMENTED | Deterministic | Block-aware |
| **25**| Accept Connection | Social | Transition pair to 'accepted' state | FastAPI | `POST /v1/connections/{id}/...` | `ConnectionsPage.tsx` | IMPLEMENTED | Deterministic | Initiator cannot accept own request|
| **26**| Decline Connection | Social | Transition pair to 'declined' state | FastAPI | `POST /v1/connections/{id}/...` | `ConnectionsPage.tsx` | IMPLEMENTED | Deterministic | Initiator cannot decline |
| **27**| Block User | Social | Transition pair to 'blocked' state | FastAPI | `POST /v1/connections/{id}/...` | `ConnectionsPage.tsx` | IMPLEMENTED | Deterministic | Creates mutual 404 block |
| **28**| Unblock User | Social | Transition pair to 'removed' state | FastAPI | `POST /v1/connections/{id}/...` | `ConnectionsPage.tsx` | IMPLEMENTED | Deterministic | Blocker only; resets to removed |
| **29**| Remove Connection | Social | Transition pair to 'removed' state | FastAPI | `POST /v1/connections/{id}/...` | `ConnectionsPage.tsx` | IMPLEMENTED | Deterministic | Resets active connection |
| **30**| Composite Synastry Score| US | 10.0-98.0 relationship synergy score | Synastry Engine| `POST /v1/compare` | `ComparePage.tsx` | IMPLEMENTED | Deterministic | Requires accepted connection |
| **31**| Emotional Harmony Score | US | Subscore 0.0-100.0 for emotional sync | Synastry Engine| `POST /v1/compare` | `ComparePage.tsx` | PARTIAL | Deterministic | Dropped on cache hit |
| **32**| Communication Score | US | Subscore 0.0-100.0 for mental flow | Synastry Engine| `POST /v1/compare` | `ComparePage.tsx` | PARTIAL | Deterministic | Dropped on cache hit |
| **33**| Attraction Score | US | Subscore 0.0-100.0 for chemistry | Synastry Engine| `POST /v1/compare` | `ComparePage.tsx` | PARTIAL | Deterministic | Dropped on cache hit |
| **34**| Growth & Long-Term Score| US | Subscore 0.0-100.0 for structural bond| Synastry Engine| `POST /v1/compare` | `ComparePage.tsx` | PARTIAL | Deterministic | Dropped on cache hit |
| **35**| Top 6 Ranked Signals | US | Curated relationship dynamic badges | Rules Module | `POST /v1/compare` | `ComparePage.tsx` | IMPLEMENTED | Deterministic | Max 6 signals; strength >= 0.40 |
| **36**| Best Bridge Topics | US | 4 conversation themes for the pair | Rules Module | `POST /v1/compare` | `WhyPage.tsx` | IMPLEMENTED | Deterministic | Air/Fire/Water/Earth mapped |
| **37**| Conversation Starters | US | 3 curated icebreakers for the pair | Rules Module | `POST /v1/compare` | `WhyPage.tsx` | IMPLEMENTED | Deterministic | Mapped to top active signals |
| **38**| Data Quality Confidence | US | Rating 0.50-1.00 based on birth time | Synastry Engine| `POST /v1/compare` | `ComparePage.tsx` | IMPLEMENTED | Deterministic | Reflects unknown time accurately |
| **39**| Synastry Evidence Grid | US | Complete aspect & orb math ledger | Synastry Engine| DB Column Only | None | PARTIAL | Deterministic | Stored in DB; dropped from API |
| **40**| Start Direct Chat | Messaging | Provision 1:1 chat room for pair | FastAPI | `POST /v1/conversations` | `WhyPage.tsx` / Chat | IMPLEMENTED | Deterministic | Requires accepted connection |
| **41**| Send Direct Message | Messaging | Post message to conversation thread | FastAPI | `POST /v1/conversations/{id}/msg`| `ChatPage.tsx` | IMPLEMENTED | Deterministic | Active members only |
| **42**| Read Chat History | Messaging | Chronological message thread | FastAPI | `GET /v1/conversations/{id}/msg` | `ChatPage.tsx` | IMPLEMENTED | Deterministic | Active members only |
| **43**| In-App Alert Feed | Alerts | Notification list for requests/events | FastAPI | `GET /v1/notifications` | `NotificationsPage.tsx` | IMPLEMENTED | Deterministic | Owner-only |
| **44**| Dismiss Notification | Alerts | Mark notification as read | FastAPI | `PATCH /v1/notifications/{id}/...`| `NotificationsPage.tsx` | IMPLEMENTED | Deterministic | Owner-only |
| **45**| AI Jester Voice Insight | AI | Witty natural-language translation | Interp Stubs | None | None | STUB | AI (LLM) | No live LLM integration |

---

## 18. READY FOR PRODUCT / UX DESIGN NOW

The following capabilities are **operational, integrated, verified by tests, and backed by working APIs**. The UX design team can immediately design complete, rich flows around them:

### ME (Self Understanding)
* **Account Onboarding**: Email/password authentication with JWT handling.
* **Birth Data Entry**: Multi-step precision input (Exact, Approximate, Unknown time) with timezone and coordinate validation.
* **Personal Astrological Card**: The "Big Three" (Sun, Moon, Rising) with unknown-time graceful degradation.
* **Elemental & Modality Signature**: Dominant element and dominant modality badges.
* **Profile Management**: Updating display name, avatar, bio, city, occupation, and discovery toggle.

### YOU (Perceiving Others)
* **Target Profile Card**: Inspecting any discoverable user's name, avatar, bio, location, and occupation.
* **Target Astrological Identity**: Viewing Person B's Sun, Moon, Rising, and Primary Element/Modality without exposing their raw birth data.
* **Privacy & Boundary Safety**: Mutual block enforcement returning privacy-safe 404 states.

### US (Relationship Dynamics — Connected Pairs)
* **Master Compatibility Index**: Displaying the normalized $10.0 - 98.0$ overall synergy rating between accepted friends.
* **Top 6 Relational Signals**: Categorized relationship indicators (`harmony`, `attraction`, `communication`, `growth`, `stability`) with human-readable labels and aspect tags.
* **Conversational Bridges**: 4 curated bridge topics based on shared elemental/aspect harmony.
* **Icebreaker Conversation Starters**: 3 tailored questions linked to specific astrological contacts with one-tap "Copy to Clipboard" or "Send to Chat".
* **Precision & Confidence Pill**: Clear indicator of whether the calculation is based on exact or approximate birth times.

### MORE PEOPLE & SOCIAL GRAPH
* **Social Graph Controls**: Sending connection requests, accepting, declining, blocking, and removing connections.
* **Direct 1:1 Messaging**: Private chat threads between accepted connections.
* **In-App Notification Feed**: Alerting users to pending connection requests with read-state tracking.

---

## 19. NOT READY FOR PRODUCT DESIGN WITHOUT BACKEND WORK

The following capabilities **must not be designed into user flows** until the backend engineering team completes the required implementations:

1. **Viewing Compatibility Before Connection ("Unconnected Synastry")**:
   * *Missing*: Backend currently raises `HTTP 403 Forbidden` if `has_active_connection()` is false.
   * *Required*: Modify `comparisons/router.py` to allow compatibility calculation for any target user where `is_discoverable = true`.
2. **People Discovery Feed / Algorithmic Search**:
   * *Missing*: No FastAPI endpoint exists to search, filter, or recommend users.
   * *Required*: Implement a paginated `GET /v1/people` endpoint supporting filtering by city, sign, or element.
3. **Deep Synastry Aspect Grid ("Evidence Trace")**:
   * *Missing*: Full aspect list with degrees, orbs, and point contributions is stored in `compatibility_results.evidence_trace` in the database, but omitted from `StructuredCompatibilityResponse`.
   * *Required*: Expose `evidence_trace` in the FastAPI response model.
4. **Relational Dimensions on Cache Hit**:
   * *Missing*: Router drops `dimensions` (`emotional_harmony`, `communication`, `attraction`, `growth_long_term`) when reading from cache.
   * *Required*: Store and retrieve `dimensions` in `public.compatibility_results`.
5. **Daily Energy / Day Vibe**:
   * *Missing*: Ephemeris transits engine is empty; scheduled generator is a static stub; no API route exists.
   * *Required*: Implement transit math in `transits.py` and build `GET /v1/daily-energy`.
6. **AI-Generated Jester Voice Interpretations**:
   * *Missing*: All files in `interpretation/` are empty stubs. No LLM client or prompt pipeline is active.
   * *Required*: Connect async OpenAI client, format prompts, and parse structured output.
7. **Native OS Push Notifications**:
   * *Missing*: No APNs or FCM push notification worker exists.

---

## 20. IMPORTANT BACKEND GAPS IDENTIFIED

1. **Gatekeeper Constraint**: `POST /v1/compare` requires `status = 'accepted'` in `connections`. Users cannot discover relationship chemistry with a prospective connection prior to mutual acceptance.
2. **Cache-Hit Dimension Drop**: `public.compatibility_results` lacks a dedicated `dimensions` column, causing cached queries in `backend/app/comparisons/router.py` to return an empty dictionary `{}` for subscores.
3. **Evidence Trace Withholding**: Migration 021 added `evidence_trace jsonb` to the database and `synastry.py` populates it, but `backend/app/comparisons/models.py` excludes it from `StructuredCompatibilityResponse`.
4. **FastAPI People Discovery Void**: FastAPI has no route to list discoverable users. The frontend is forced to bypass FastAPI and query Supabase directly via PostgREST.
5. **FastAPI Birth Data CRUD Void**: FastAPI has no route to insert or update `birth_data`. The frontend must use Supabase PostgREST client for writes and FastAPI for recalculation.
6. **Interpretation Disconnect**: Environment variables `OPENAI_API_KEY` and `LLM_MODEL` exist in `config.py`, but no application code ever imports or uses them.

---

## 21. FINAL EXECUTIVE SUMMARY

### JESTER CURRENTLY CAN:
* Authenticate users and manage profiles with strict privacy discoverability toggles.
* Calculate 100% deterministic Swiss Ephemeris natal charts (10 planets, Placidus houses, Ascendant, element/modality dominance) with strict isolation of private birth data.
* Gracefully calculate charts with unknown birth times (noon mean chart, Ascendant suppressed, confidence adjusted).
* Run deterministic Synastry V1 calculations between accepted connections, yielding an overall score ($10.0 - 98.0$), 6 ranked signals, 4 bridge topics, 3 icebreaker starters, and confidence metrics.
* Enforce a complete connection state machine (pending, accepted, declined, blocked, removed) with mutual block hiding.
* Provide 1:1 direct messaging and in-app notifications between active friends.

### JESTER CURRENTLY CANNOT:
* Allow a user to check compatibility with a discovered profile before mutual connection acceptance.
* Expose the rich astronomical aspect grid (evidence trace) through the API.
* Reliably return the 4 relational dimensions from database cache.
* Provide a FastAPI people search or discovery feed.
* Deliver dynamic transit-based Daily Energy / Day Vibe forecasts.
* Generate natural-language Jester Voice interpretations using an LLM.
* Send native OS push notifications (APNs / FCM).

### JESTER IS READY TO DESIGN AROUND:
* **The "Understand Myself" (ME) Journey**: Onboarding, Big Three cards, elemental breakdown, profile customization.
* **The "Perceive Another" (YOU) Journey**: Viewing another user's public card and derived astrology.
* **The "Connected Connection" (US) Journey**: Score meter, top 6 signals, bridge topics, icebreakers, and 1:1 direct chat for established friends.
* **Social Graph Management**: Requesting, accepting, declining, and blocking connections.

### JESTER STILL NEEDS BACKEND WORK FOR:
* Unlocking compatibility for un-connected discoverable profiles (1-line permission check modification).
* Exposing `evidence_trace` in `StructuredCompatibilityResponse` (5-line schema change).
* Storing `dimensions` in the database cache (1 database column + router update).
* Creating a `GET /v1/people` discovery endpoint in FastAPI.
* Building the transit calculation pipeline for Daily Energy.
* Implementing the OpenAI translation client in `interpretation/`.

### MOST IMPORTANT DISCOVERY:
**The Complete Astronomical Evidence Trace (`evidence_trace`) is Already Computed and Stored in the Database!**  
The Synastry V1 engine already calculates every single cross-aspect between two charts—including exact circular distances, precise orb variances, quadratic decay strengths, pair tier weights, and point-by-point contributions to emotional harmony, communication, attraction, and growth. It is already persisted in `public.compatibility_results.evidence_trace`.  
**It is currently withheld from the frontend solely because it was omitted from the Pydantic response model.** Exposing this single existing field would immediately provide all the technical data necessary to build an advanced, high-value, deep relational breakdown without altering the astrology engine.
