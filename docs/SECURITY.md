# JESTER — Security & Privacy Architecture Policy

[![Security: RLS Enforced](https://img.shields.io/badge/Security-RLS%20Enforced-success.svg)](#postgresql-role-privileges--row-level-security-rls)
[![Auth: Asymmetric JWKS](https://img.shields.io/badge/Auth-Asymmetric%20JWKS-blue.svg)](#authentication--token-validation-backendappauth)
[![Tests: 193 Passed](https://img.shields.io/badge/Tests-193%20Passed-brightgreen.svg)](#automated-security-testing--verification)

> **In JESTER, user privacy is not an afterthought or an optional setting—it is a foundational mathematical and architectural invariant.**

JESTER is a **People Discovery and Relationship Intelligence** engine. Because interpersonal insight depends on private personal data (such as birth timestamps and exact geographical coordinates), our security architecture is designed to mathematically isolate raw user data, prevent identity impersonation, eliminate existence oracles, and enforce strict boundary separation across every layer of the stack.

---

## 📋 Supported Versions

Security updates and vulnerability patches are actively maintained for the following versions:

| Component | Version | Supported | Security Posture |
| :--- | :--- | :---: | :--- |
| **JESTER API Backend** | `1.x` (`main`) | ✅ | Active JWKS asymmetric verification, RLS enforcement |
| **Frontend Web Client** | `0.x` (`main`) | ✅ | Authenticated session lifecycle, bearer authorization |
| **Database Migrations** | `001-020` | ✅ | Least privilege roles, procedural hardening |

---

## 🔑 Authentication & Token Validation (`backend/app/auth/`)

JESTER enforces a zero-trust, stateless token validation architecture powered by Supabase Authentication and verified via FastAPI dependencies.

### 1. Dual-Mode JWT Verification (`backend/app/auth/jwt.py`)

- **Production Mode (`ENV=production`):**
  - **Strict Asymmetric Enforcement:** Requires asymmetric cryptographic algorithms (`RS256`, `ES256`, or `EdDSA`).
  - **Dynamic Key Resolution:** Public keys are fetched and cached from the Supabase JWKS endpoint (`SUPABASE_JWKS_URL`) via `PyJWKClient`.
  - **Hard Fallback Prohibition:** If an asymmetric token fails key resolution, it **never** falls back to symmetric HS256. If any token declaring `alg=HS256` arrives in production, it is rejected immediately with HTTP 401.
  - **Replay & Expiration Checks:** Tokens are validated against `exp`, `nbf`, `iat`, and valid `iss`/`aud` claims.

- **Development & Testing Mode (`ENV=development` / `ENV=test`):**
  - Symmetric `HS256` signatures are permitted exclusively for offline unit testing and automated integration pipelines using `SUPABASE_JWT_SECRET`.

### 2. Subject & Claims Validation
- Decodes the `sub` claim and verifies that it is a valid UUID (`user_id`).
- Extracts tenant roles (`authenticated`, `copywriter`, `admin`, `service_role`).
- Populates the trusted `AuthenticatedUser` dependency for downstream route authorization.

---

## 🛡️ PostgreSQL Role Privileges & Row-Level Security (RLS)

PostgreSQL security operates on the **Principle of Least Privilege**, separating public anonymous visitors, authenticated end-users, and trusted internal backend workers.

```text
                        ┌─────────────────────────────────────────┐
                        │      PostgreSQL Database (Supabase)     │
                        └────────────────────┬────────────────────┘
                                             │
             ┌───────────────────────────────┼───────────────────────────────┐
             ▼                               ▼                               ▼
     ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
     │   anon Role   │               │ authenticated │               │ service_role  │
     └───────┬───────┘               └───────┬───────┘               └───────┬───────┘
             │                               │                               │
    REVOKE ALL ON ALL               RLS Enforced Access             Bypasses RLS Policies
    Tables & Routines               (Profiles, Safe Astro,          Dedicated Backend Pool
    (Zero Data Access)              Connections, Messages)          (Trusted Engine Logic)
```

### Table Privileges & Access Boundary Matrix

| Table / Surface | `anon` Role | `authenticated` Role (Client JWT) | `service_role` (Backend Engine) |
| :--- | :--- | :--- | :--- |
| `public.birth_data` | 🚫 **REVOKED** | `SELECT, INSERT, UPDATE` (Strictly `user_id = auth.uid()`) | 🟢 Full Access |
| `public.astro_private` | 🚫 **REVOKED** | 🚫 **REVOKED** (`REVOKE ALL FROM authenticated, anon, public`) | 🟢 Full Access (Calculations only) |
| `public.astro_safe_profile` | 🚫 **REVOKED** | `SELECT` (Own profile OR discoverable/unblocked target) | 🟢 Full Access |
| `public.profiles` | 🚫 **REVOKED** | `SELECT` (If discoverable & unblocked), `UPDATE` (Own row only) | 🟢 Full Access |
| `public.connections` | 🚫 **REVOKED** | `SELECT` (Participant/blocker), `INSERT` (Initiated by self). Direct `UPDATE` revoked! | 🟢 Full Access (Transitions via function) |
| `public.compatibility_results`| 🚫 **REVOKED** | `SELECT` (Participant AND active mutual connection) | 🟢 Full Access |
| `public.conversations` | 🚫 **REVOKED** | `SELECT` (Active direct conversation member only) | 🟢 Full Access |
| `public.messages` | 🚫 **REVOKED** | `SELECT, INSERT` (Active direct conversation member only) | 🟢 Full Access |
| `public.notifications` | 🚫 **REVOKED** | `SELECT, UPDATE` (Strictly `user_id = auth.uid()`) | 🟢 Full Access |
| `public.daily_energies` | 🚫 **REVOKED** | `SELECT` (Strictly `user_id = auth.uid()`) | 🟢 Full Access |
| `public.interest_categories` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.interests` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.interest_aliases` | 🚫 **REVOKED** | `SELECT` (Taxonomy alias resolution) | 🟢 Full Access |
| `public.interest_relations` | 🚫 **REVOKED** | `SELECT` (Taxonomy graph traversal) | 🟢 Full Access |
| `public.user_interests` | 🚫 **REVOKED** | `SELECT` (Own profile OR discoverable/unblocked target), `INSERT, UPDATE, DELETE` (Strictly `user_id = auth.uid()`) | 🟢 Full Access |
| `public.user_interest_affinity`| 🚫 **REVOKED** | 🚫 **REVOKED** (`REVOKE ALL FROM authenticated, anon, public`) | 🟢 Full Access (Internal recommendation only) |
| `public.geo_countries` | `SELECT` (Geo reference) | `SELECT` (Geo reference) | 🟢 Full Access |
| `public.geo_cities` | `SELECT` (Geo reference) | `SELECT` (Geo reference) | 🟢 Full Access |
| `public.geo_city_aliases` | `SELECT` (Geo search) | `SELECT` (Geo search) | 🟢 Full Access |
| `public.user_location_private` | 🚫 **REVOKED** | 🚫 **REVOKED** (`REVOKE ALL FROM authenticated, anon, public`) | 🟢 Full Access (Service-role only) |
| `public.lifestyle_categories` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.lifestyle_options` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.user_lifestyle` | 🚫 **REVOKED** | `SELECT` (Own row OR discoverable target; filtered by visibility flags), `INSERT, UPDATE` (`user_id = auth.uid()`) | 🟢 Full Access |
| `public.values_categories` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.values_options` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.value_relations` | 🚫 **REVOKED** | `SELECT` (Taxonomy graph traversal) | 🟢 Full Access |
| `public.user_values` | 🚫 **REVOKED** | `SELECT` (Own row OR discoverable target), `INSERT, UPDATE, DELETE` (`user_id = auth.uid()`) | 🟢 Full Access |
| `public.social_categories` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.social_options` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.social_relations` | 🚫 **REVOKED** | `SELECT` (Taxonomy graph traversal) | 🟢 Full Access |
| `public.user_social_preferences`| 🚫 **REVOKED** | `SELECT` (Own row OR discoverable target; filtered by visibility flags), `INSERT, UPDATE` (`user_id = auth.uid()`) | 🟢 Full Access |
| `public.communication_categories` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.communication_options` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.communication_relations` | 🚫 **REVOKED** | `SELECT` (Taxonomy graph traversal) | 🟢 Full Access |
| `public.user_communication_preferences`| 🚫 **REVOKED** | `SELECT` (Own row OR discoverable target; filtered by visibility flags), `INSERT, UPDATE` (`user_id = auth.uid()`) | 🟢 Full Access |
| `public.intent_categories` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.intent_options` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.intent_relations` | 🚫 **REVOKED** | `SELECT` (Taxonomy graph traversal) | 🟢 Full Access |
| `public.user_intents` | 🚫 **REVOKED** | `SELECT` (Own row OR discoverable target; filtered by visibility), `INSERT, UPDATE` (`user_id = auth.uid()`) | 🟢 Full Access |
| `public.user_intent_history` | 🚫 **REVOKED** | 🚫 **REVOKED** (`REVOKE ALL FROM authenticated, anon, public`) | 🟢 Full Access (Service-role audit only) |
| `public.prompt_categories` | `SELECT` (Taxonomy) | `SELECT` (Taxonomy) | 🟢 Full Access |
| `public.prompt_templates` | `SELECT` (Templates) | `SELECT` (Templates) | 🟢 Full Access |
| `public.user_prompts` | 🚫 **REVOKED** | `SELECT` (Own row OR discoverable target; filtered by visibility & approved status), `INSERT, UPDATE, DELETE` (`user_id = auth.uid()`) | 🟢 Full Access |
| `public.user_discovery_preferences` | 🚫 **REVOKED** | `SELECT, INSERT, UPDATE` (Strictly `user_id = auth.uid()`) | 🟢 Full Access |

---

## 🔒 Security & Privacy Invariants

These invariants are permanent engineering constraints. Any pull request or refactoring that violates these rules is rejected.

### 1. Raw Birth Data Isolation (`public.birth_data`)
- **Invariant:** User-owned birth parameters (`birth_date`, `birth_time`, `birth_timezone`, `latitude`, `longitude`, `place_label`) are strictly owner-only.
- **Enforcement:** PostgreSQL RLS policy `birth_data_select_own` evaluates `user_id = auth.uid()`.
- **API Boundary:** Raw birth data is never exposed in profile responses, discovery cards, previews, compatibility responses, logs, or client-facing DTOs.

### 2. Private Astronomical Calculations (`public.astro_private`)
- **Invariant:** Server-calculated celestial longitudes, exact house cusps, and retrograde speeds are internal intellectual property and raw intelligence data.
- **Enforcement:** Migration 017 explicitly executes:
  ```sql
  REVOKE ALL ON public.astro_private FROM authenticated, anon, public;
  ```
  Any attempt by a client or standard database role to query `astro_private` raises an immediate `InsufficientPrivilege` PostgreSQL error.

### 3. Safe Profile Derivation (6 Core Planets)
- **Invariant:** Other users and discovery cards only receive safe, non-inverting derived profiles (`SafeDerivedAstrologyResponse`).
- **Planetary Protection:** All 6 core personality planets (**Sun**, **Moon**, **Ascendant**, **Mercury**, **Venus**, **Mars**) expose only their categorical zodiac sign (e.g. `Aries`, `Scorpio`) and dominant element/modality. Raw numerical degrees are never serialized to the client.

### 4. Elimination of Existence Oracles (Block & Privacy Semantics)
- **Invariant:** Blocking or hiding must never leak the target's existence through differential error codes.
- **Enforcement:** If User A blocks User B, or User B is not discoverable:
  - Profiles resolve as **HTTP 404** (`PrivacySafeNotFoundException`).
  - Safe astrology placement endpoints resolve as **HTTP 404**.
  - US / Compare previews resolve as **HTTP 404**.
  - Discovery feeds exclude the user entirely.
  - Chat message attempts resolve as **HTTP 404**.
  - The API **never** returns HTTP 403 Forbidden or existence confirmation for hidden/blocked entities.

### 5. Viewer Identity & Impersonation Protection
- **Invariant:** An authenticated caller can never calculate comparisons or discover profiles under another user's identity.
- **Enforcement:** Routes accepting a viewer/source ID (such as `/v1/interpretations/discovery-people` and `/v1/interpretations/compare-preview`) strictly bind and assert:
  ```python
  if payload.source_user_id is not None and payload.source_user_id != current_user.id:
      raise ForbiddenException(
          message="Cannot request comparison preview as another user.",
          error_code="forbidden_viewer_impersonation",
      )
  ```

### 6. Editorial Asset Protection (Content V2)
- **Invariant:** Editorial metadata (`internal_notes`, `author`, `experiment_id`, `weight`) is confidential.
- **Enforcement:** Endpoint `/v1/interpretations/{id}/assets` dynamically inspects caller roles. For general users, internal editorial metadata is stripped before response serialization. Only users with `copywriter` or `admin` roles can inspect authoring notes.

### 7. Developer Debug Isolation (`/v1/astrology/debug/*`)
- **Invariant:** Developer inspection tools and debug routes must be completely unreachable in production.
- **Enforcement:** Endpoints in `backend/app/astrology/debug.py` check `settings.ENV == "production"` and immediately abort with HTTP 403 Forbidden. Furthermore, debug endpoints are 100% read-only and never trigger mutating auto-recalculations.

### 8. Interest Graph & Behavioral Affinity Isolation (`public.user_interest_affinity`)
- **Invariant:** Behavioral affinity scores, interaction confidence, and internal cluster weights are strictly internal recommendation signals. They must **never** overwrite, mutate, or blur the boundary of a user's explicitly declared interests (`public.user_interests`).
- **Enforcement:** All database privileges on `public.user_interest_affinity` are revoked from client roles (`authenticated`, `anon`, `public`). The API and JESTER intelligence engine never project unconfirmed behavioral labels (e.g., "You are an adventurous person") onto the user.

### 9. Separation of Profile Presentation and Identity Verification
- **Invariant:** Public profile imagery (`avatar_url`) and Biometric/Face Verification are strictly distinct concepts.
- **Enforcement:** Uploading or displaying a profile photo does not grant or imply verified status. Verification tokens, status, and biometric metadata are governed by dedicated security boundaries and never conflated with casual profile presentation.

### 10. Precise Geographic Coordinate Protection & Location Privacy
- **Invariant:** Exact coordinates (`latitude`, `longitude`), street addresses, live GPS positioning, and continuous device tracking are sensitive personal data. They must **never** be publicly exposed, serialized in public client DTOs, or exposed in normal discovery feeds.
- **Enforcement:**
  - Public profile and discovery responses serialize only canonical city and country names (`location: { city, country }`, `origin: { city, country }`).
  - Origin/Hometown visibility is strictly user-controlled via `hometown_visible`.
  - Client database roles have zero read permissions on private coordinate tables (`public.user_location_private`).
  - No trilateration or precise distance stalking: future distance indicators will operate solely on broad fuzzy bands (e.g. "Within 25 km", "Same city"), never exact decimal distances.
  - Analytics and access logs are stripped of raw GPS coordinates.

### 11. Lifestyle & Sensitive Habit Privacy Boundaries
- **Invariant:** Sensitive lifestyle attributes (drinking, smoking, living situation, household structure) are strictly user-controlled. They must **never** be coerced during initial onboarding, leaked when toggled private, or used to generate moralistic or judgmental JESTER AI commentary.
- **Enforcement:**
  - `visibility_flags` on `public.user_lifestyle` dictate public serialization; private fields are stripped before client delivery.
  - Suppressed from AI prompt payloads when marked hidden.
  - Zero health lecturing or shaming algorithms permitted.

### 12. Values & Philosophical Non-Diagnostic Invariants
- **Invariant:** Values represent self-declared life priorities and principles, not clinical psychometric profiles. They must **never** be converted into percentage scores (e.g. "87% independent"), used for virtue grading, or treated as psychological labels.
- **Enforcement:**
  - JESTER AI prompts explicitly forbid personality diagnosis or moral superiority commentary.
  - The API exposes values as categorical tags with optional single Core Value status (`is_core = true`), strictly avoiding Likert-scale or decimal scores.
  - All canonical values possess equal dignity and respect across the platform.

### 13. Social Behavior & Anti-Typing Non-Diagnostic Invariants
- **Invariant:** Social behavior describes situational gathering preferences and energy mechanics, not psychological personality types. Users must **never** be boxed into clinical MBTI archetypes, labeled with pop-psychology buzzwords ("Alpha", "Loner", "Social Butterfly"), or graded as "socially awkward".
- **Enforcement:**
  - JESTER AI prompts explicitly forbid personality typing or judgmental social commentary.
  - The API exposes social behavior as discrete functional choices (e.g. `recharge_solo`, `one_on_one`), completely avoiding clinical labels or personality percentage scales.
  - All social battery and gathering styles carry equal dignity across the platform.

### 14. Communication & Anti-Surveillance Non-Diagnostic Invariants
- **Invariant:** Communication preferences define interaction mechanics, conversation depth, and pacing expectations, not personality traits or latency metrics. Surveillance mechanics (reply-time timers, read-receipt latency tracking, "fast responder" / "bad texter" badges) and automated mining of private message text for psychometric profiling are **strictly prohibited**.
- **Enforcement:**
  - JESTER AI prompts explicitly forbid personality typing, buzzword labels ("Dry Texter", "Deep Talker", "Golden Retriever Communicator"), and reply-time anxiety scorekeeping.
  - Zero private message body inspection: AI models and recommendation algorithms are architecturally barred from reading or processing private conversation message contents (`public.messages.body`) for communication profiling.
  - Declared pacing (`active_banter`, `unhurried_thoughtful`, `relaxed_async`) is treated as personal preference and emotional reassurance, never scored for algorithmic penalty or compatibility grading.
  - `visibility_flags` on `public.user_communication_preferences` allow users to selectively hide any communication dimension from their public profile.

### 15. Intent Primacy & Anti-Romantic Assumption Invariants
- **Invariant:** Declared intent defines current platform purpose and relational openness, not permanent personality or marital status. Mutually incompatible non-overlapping intents must be partitioned to prevent harassment, and astrological synastry must **never** be used to impose romantic or sexual destiny on users declaring platonic intent. Intent history is strictly private.
- **Enforcement:**
  - RLS policies on `public.user_intent_history` revoke all permissions from client roles (`REVOKE ALL FROM authenticated, anon, public`).
  - Discovery algorithms enforce bilateral intent partitioning (e.g. exclusive dating partitioned from exclusive friendship).
  - JESTER AI prompt architecture explicitly enforces Intent Primacy: when either participant declares friendship or collaboration, romantic interpretations of planetary aspects (e.g. Venus-Mars chemistry) are strictly barred and reframed as creative synergy or shared drive.

### 16. Prompts & Authentic Human Voice Invariants (`public.user_prompts`)
- **Invariant:** Prompts represent the user's authentic voice, humor, and quirks. JESTER AI is strictly prohibited from generating, hallucinating, or publishing prompt answers without explicit user prompting, review, and manual submission. Prompt answers are public user-generated content that must undergo pre-publication sanitization, but must never be treated as clinical psychological profiles or psychiatric evidence.
- **Enforcement:**
  - Automated regex and sanitization runs pre-publication on `POST /v1/prompts` and `PATCH /v1/prompts/{id}`, stripping HTML tags/scripts and detecting raw PII (phone numbers, external messaging handles, and harassment terms).
  - JESTER AI prompt construction instructions explicitly command the model: prompt text is user-authored conversational context, NOT clinical truth. Harmless sarcasm, dry humor, or hyperbole (e.g., *"I hate everyone before coffee"*) must never be diagnosed as misanthropy or antisocial behavior.
  - Moderation states (`approved`, `flagged`, `rejected`, `pending_review`): Prompts with `status = 'rejected'` are automatically excluded from public profile queries and discovery cards via RLS policy.

### 17. Discovery Preferences & Candidate Confidentiality Invariants (`public.user_discovery_preferences`)
- **Invariant:** A user's discovery preferences (`target_genders`, `age_min`, `age_max`, `location_scope`, `target_intents`, `astrology_mode`) are strictly confidential and private to the owner. Candidates who are filtered out must **never** be informed or able to deduce that they were excluded. Discovery preferences are outbound selection criteria and must never be conflated with inbound discoverability (`profiles.is_discoverable`).
- **Enforcement:**
  - `REVOKE ALL ON public.user_discovery_preferences FROM anon, public;`
  - RLS policy `user_discovery_preferences_owner_all` strictly checks `user_id = auth.uid()`.
  - Discovery query execution enforces mutual block hiding (`NOT is_user_blocked()`), returning privacy-safe empty results rather than error states.
  - Zero raw birth dates or exact timestamps are serialized; only dynamically computed integer age is exposed in candidate DTOs.
  - Hard dealbreakers are restricted to Age, Gender, and Intent; physical, racial, religious, or zodiac-sign filtering is architecturally prohibited.


---

## ⚙️ Procedural Hardening & Function Security

To prevent search path hijacking and privilege escalation in PostgreSQL functions:
- All database helper functions (`has_active_connection`, `is_user_blocked`, `is_active_direct_conversation`, `can_view_safe_astro`) are defined with:
  ```sql
  SECURITY DEFINER
  SET search_path = public, pg_temp
  ```
- Public execution is revoked:
  ```sql
  REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA public FROM public;
  GRANT EXECUTE ON FUNCTION ... TO authenticated, service_role;
  ```

---

## 🧪 Automated Security Testing & Verification

Security policies are tested continuously in the automated test suite (`193 passed tests`):

1. **Database RLS & Isolation Suite (`tests/database/test_database_security.py`):**
   - Verifies that User A cannot select, insert, or update User B's `public.birth_data`.
   - Confirms that direct `SELECT` on `public.astro_private` from authenticated client roles fails with `InsufficientPrivilege`.
   - Validates that blocking masks profiles, compatibility records, and direct messages as 404s.
   - Tests that canonical connections cannot be modified by arbitrary SQL updates.

2. **JWT & Auth Verification Suite (`tests/backend/test_jwt_verification.py`):**
   - Asserts asymmetric JWKS key fetching in production.
   - Verifies that HS256 tokens are rejected in production mode.
   - Verifies expiration, invalid signature, and malformed header rejections.

---

## 🚨 Reporting a Vulnerability

We appreciate the efforts of security researchers in keeping JESTER safe. If you discover a security vulnerability or privacy leak, please disclose it responsibly:

1. **Do NOT open a public GitHub issue.**
2. **Email your report directly to:** `security@jester.app` (or contact the repository maintainers via private communication).
3. **Include:**
   - Description of the vulnerability and potential impact.
   - Step-by-step reproduction steps or proof-of-concept payload.
   - Any proposed mitigations or fixes.

### Our Commitment:
- **Initial Response:** Within 48 hours of report receipt.
- **Triage & Assessment:** We will keep you updated as the issue is investigated and patched.
- **Safe Harbor:** We will not pursue legal action against researchers who report vulnerabilities in good faith and adhere to responsible disclosure standards.
