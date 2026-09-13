# JESTER V1 — FRONTEND CAPABILITY SPECIFICATION

**Document Type:** Frontend Functional & Capability Specification  
**Version:** `1.0.0`  
**Engine Version Dependency:** `synastry-v1.0.0`  
**Parent Product Spec:** [`docs/PRODUCT_SPECIFICATION.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/PRODUCT_SPECIFICATION.md)  
**Mathematical Engine Spec:** [`docs/SYNASTRY_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/SYNASTRY_V1_SPEC.md)  
**Status:** Complete / Authoritative Frontend Functional Blueprint  

---

## 1. Purpose

This document defines the functional capabilities, information architecture, state machines, and data contracts that the **Jester Frontend** (Web / React Native) must support.

It translates the underlying backend services (FastAPI, PySwissEph, Synastry V1 Engine, PostgreSQL, and Supabase Auth/Realtime) into a concrete frontend capability map.

This specification focuses strictly on **what the user can do, what information exists, what states occur, and how data transitions happen**. It intentionally avoids visual styling, colors, typography, or component design layouts.

---

## 2. Source of Truth

The requirements in this document are derived directly from the authoritative codebase:

1. **Product Vision & Architecture**: [`docs/PRODUCT_SPECIFICATION.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/PRODUCT_SPECIFICATION.md) and [`docs/ARCHITECTURE.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/ARCHITECTURE.md)
2. **Deterministic Synastry Engine**: [`docs/SYNASTRY_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/SYNASTRY_V1_SPEC.md) and [`backend/app/compatibility/synastry.py`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/backend/app/compatibility/synastry.py)
3. **Database Migrations & Security Invariants**: [`supabase/migrations/`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/supabase/migrations/) (Migrations 001 through 021)
4. **FastAPI API Contracts & Pydantic Models**: [`backend/app/`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/backend/app/)
5. **Verified System Behaviors**: 74 passing automated unit, API, and database security tests in [`tests/`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/tests/)

---

## 3. Product Loop & Strategic Experience Architecture

### 3.1 Strategic Model: ME → YOU → US → MORE PEOPLE
The frontend journey translates the underlying data into a 4-step psychological progression:
1. **ME**: Onboarding + First taste of JESTER via **Today's Energy / Day Vibe** (*"Let's see what JESTER notices about me"*).
2. **YOU**: Curiosity about a friend or connection (*"What would JESTER say about them?"*).
3. **US**: Synastry comparison (*"What connects us? Why do we click?"*).
4. **MORE PEOPLE**: Expanding into network discovery and comparing broader relationships.

### 3.2 Current Technical Frontend vs. Consumer UX
- **Current Scaffold**: Renders raw data (Sun, Moon, Ascendant, Element, Modality). Validates that the underlying data pipeline works.
- **Consumer Product**: Uses that rich data layer to deliver sharp, witty JESTER observations. Rich astrological data is strictly preserved in the backend and safe profiles.

### 3.3 The 8-Stage Operational Product Loop
The core user experience maps directly into the 8-stage operational loop:


```
┌─────────────────────────────────────────────────────────────┐
│ 1. CREATE SELF        (Birth Data & Profile Onboarding)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. UNDERSTAND SELF    (Personal Astrology Profile & Signs)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. DISCOVER PEOPLE    (Browse Discoverable Public Profiles) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. CONNECT            (Send, Accept, or Manage Requests)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. COMPARE            (Deterministic Synastry V1 Scoring)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. UNDERSTAND RELATIONSHIP ("Why This Person" & Dimensions) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. START CONVERSATION (Signals, Topics & Rule Starters)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. BUILD RELATIONSHIP (Direct Messaging & Daily Sync)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Capability Classification

Every feature is categorized into one of four capability buckets:

### A. Currently Available (Backend Operational & Tested)
- Supabase JWT authentication & session verification (`/v1/users/me`).
- Profile retrieval, bio/city/occupation updating, and discoverability toggle (`/v1/profiles/me`, `/v1/profiles/{id}`).
- Canonical user pair ordering & deterministic seed generation (`backend/app/core/canonical.py`).
- Atomic birth data onboarding endpoint (`POST /v1/astrology/birth-data`) executing validation, Swiss Ephemeris calculation, and DB transaction (`birth_data`, `astro_private`, `astro_safe_profile`) in a single backend-owned atomic operation.
- Swiss Ephemeris natal calculation (10 planets, Placidus houses, Ascendant, element/modality weighting).
- Safe derived astrology profile exposure (`/v1/astrology/profile/safe-astro`, `/v1/astrology/people/{id}/safe-astro`).
- Social connection state machine: `pending`, `accepted`, `declined`, `blocked`, `unblock`, `remove` (`/v1/connections`).
- Canonical pair comparison with deterministic Synastry V1 calculations (`/v1/compare`, `/v1/people/{id}/why`).
- 4-Dimensional sub-scores (Harmony, Communication, Attraction, Growth) and non-linear normalized overall score ($10.0 - 98.0$).
- Deterministic signal extraction (up to 6), topic suggestions (up to 4), and conversation starters (up to 3).
- Audit evidence trace retention in database cache.
- Direct conversation threads and message dispatch/retrieval (`/v1/conversations`, `/v1/conversations/{id}/messages`).
- In-app notification listing and read status update (`/v1/notifications`).
- Row-Level Security (RLS) isolation and mutual block hiding.

### B. Required Frontend Behavior (Cockpit Logic to Build)
- Client-side JWT storage and authenticated HTTP interceptor with automatic 401 handling.
- Multi-step birth-data onboarding wizard calling `POST /v1/astrology/birth-data` with precision selection (`exact`, `approximate`, `unknown`).
- **Interest Onboarding Flow**:
  - Optional step (user can skip entirely).
  - If entering selection: curated candidate pool of ~20 candidate interests.
  - Exact selection gating: user must pick exactly 5 / 5 Primary Interests before Continue activates.
  - Optional single Signature Interest follow-up (*"Which one could you talk about forever?"*).
  - Strictly **NO** intensity sliders (*Love/Like*) during onboarding.
- **Location & Origin Onboarding Flow**:
  - Optional / skippable step.
  - One-tap popular domestic city chips (Tbilisi, Batumi, Kutaisi, Rustavi) + fast autocomplete search.
  - Optional Hometown / Origin input with visibility toggle (*"Where are you originally from?"*).
  - Strictly **NO** mandatory device GPS permission prompts on onboarding.
- **Lifestyle Snapshot Onboarding Flow**:
  - Optional / skippable 3-question card (Daily Rhythm, Activity Pace, Work Style).
  - Rapid 1-tap segmented controls / chips.
  - Sensitive attributes (drinking, smoking, living situation, children) strictly excluded from onboarding.
- **Values & Guiding Compass Onboarding Flow**:
  - Optional / skippable step.
  - Curated grid of 18 canonical values across 5 clusters.
  - Selection constraint: user chooses between 3 and 5 values (Continue button active when count is 3, 4, or 5).
  - Optional single Core Value follow-up (*"If you had to pick one true north, which is it?"*).
  - Strictly **NO** 1–10 rating sliders or personality diagnosis metrics.
- **Social Rhythm Snapshot Onboarding Flow**:
  - Optional / skippable 3-question card (Gathering Scale, Social Battery, Warm-Up Dynamic).
  - Rapid 1-tap chip controls. Zero rating sliders.
  - No psychological typing, MBTI classifications, or identity box-labeling.
- **Communication Rhythm Snapshot Onboarding Flow**:
  - Optional / skippable 3-question card (Conversation Depth, Conversational Role, Messaging Medium).
  - Rapid 1-tap chip controls. Zero rating sliders.
  - Strictly no reply-time timers, read-receipt surveillance, or personality diagnosis.
- **Intent Onboarding Flow**:
  - Optional / skippable single-card selection (What brings you to JESTER right now?).
  - 1 Primary Intent (Single-Select) + up to 2 Secondary Openness (Multi-Select).
  - 100% skippable; defaults to `just_exploring` on skip.
  - Zero marital status questioning or relationship diagnosis.
- **Prompt Authoring & Self-Expression Flow**:
  - Optional profile enhancement (0 to 3 prompts; recommended 2–3).
  - Curated library of 24 prompts across 6 categories.
  - Max 250 characters per prompt answer.
  - Optional AI writing assistant (suggests up to 3 candidate polishes upon request; strictly no automatic publishing without explicit user approval).
  - Interactive prompt cards with `[ 💬 Reply to this ]` conversation opener triggers.
- **Discovery Preferences & Feed Controls Sheet**:
  - Modal sheet managing age range (dual-handle slider + dealbreaker toggle), target genders, geographic scope (`same_city`, `same_country`, `regional_nearby`, `anywhere`), astrology mode (`full_insights`, `minimal_insights`, `hidden`), and diversity steering.
  - Reset to default button.
  - Contextual Feed Lenses (`[ ✨ For You ]`, `[ 📍 Nearby ]`, `[ 🎯 Shared Purpose ]`, `[ 💡 Shared Curiosities ]`).
  - Clear mental model notice: *"Controls who you see; does not change who can see you."*
- Connection management list with action controls (Accept, Decline, Block, Remove).
- Compatibility score card displaying composite score, 4 sub-scores, data quality confidence, and active signals.
- Topic and conversation starter display with tap-to-send or tap-to-copy integration.
- Direct chat view with realtime message streaming via Supabase Realtime WebSocket subscription.
- Notification bell and in-app badge counter with realtime update subscriptions.

### C. Future / Out of Scope (Explicitly Deferred)
- Extended astrological bodies (Chiron, Black Moon Lilith, Lunar Nodes, Asteroids).
- Minor aspects (Quincunx, Semi-Sextile, Quintile) and House Overlays (deferred to Synastry V1.1 / V2.0).
- OpenAI / LLM text generation and AI interpretation pipelines (`interpretation/` stubs).
- Native OS push notification delivery (APNs / FCM).
- Group messaging threads and message pagination.
- Dynamic transit-based daily energy engine (currently returns static daily summary string).

### D. Unknown / Requires Product Decision
- **Client Evidence Trace Visibility**: Whether the technical `evidence_trace` array should be surfaced in an advanced "Astrology Breakdown" UI accordion or kept exclusively as an internal backend/audit layer.

---

## 5. Identity & Authentication

### 5.1 User Goals
- Authenticate securely via email/password or OAuth.
- Maintain a valid authenticated session across app restarts.
- View account metadata (User ID, Email, Role).
- Log out safely, clearing all client-side tokens and private cached states.

### 5.2 Required Data & Contracts
- **Input**: Email, Password (handled via Supabase Auth client SDK).
- **Session Output**: JWT Access Token (Bearer token in `Authorization` header), Refresh Token, User UUID.
- **Account Lookup**: `GET /v1/users/me` -> `UserResponse(id: UUID, email: str, role: str)`.

### 5.3 States & Error Handling
- `logged_out`: Default unauthenticated state.
- `authenticating`: Login/signup in-flight.
- `authenticated`: Token present, user verified.
- `session_expired`: JWT expired; interceptor catches HTTP 401 and prompts refresh or login.

---

## 6. Create Self / Onboarding

### 6.1 Birth Data Onboarding Specification
To establish astrological identity, the frontend collects raw birth information and submits to `POST /v1/astrology/birth-data`:

| Field | Required / Optional | Supported Formats / Values | Constraints & Logic |
| :--- | :--- | :--- | :--- |
| **Birth Date** | **Required** | `YYYY-MM-DD` | Valid calendar date. |
| **Birth Time Precision** | **Required** | `"exact"`, `"approximate"`, `"unknown"` | User-selected precision mode. |
| **Birth Time** | **Conditional** | `HH:MM:SS` (24-hour format) | **Required** if precision is `exact` or `approximate`. Must be `null` if precision is `unknown`. |
| **Birth Timezone** | **Required** | Valid IANA string (e.g. `"America/New_York"`, `"UTC"`) | Used for exact UTC Julian Day conversion. |
| **Latitude** | **Optional** | Float `[-90.0, 90.0]` | Required for Placidus houses and Ascendant calculation. |
| **Longitude** | **Optional** | Float `[-180.0, 180.0]` | Required for Placidus houses and Ascendant calculation. |
| **Place Label** | **Optional** | String (e.g. `"Tbilisi, Georgia"`) | Human-readable location display. |

### 6.2 Data Quality & Precision Handling
- **`exact`**: Full natal chart calculated (10 planets + Ascendant + 12 Placidus houses). Data confidence = `1.00`.
- **`approximate`**: Full calculation performed; Ascendant synastry weights scaled by `0.50`. Data confidence = `0.85`.
- **`unknown`**: Mean noon (12:00 UTC) calculation used for 10 planets. Ascendant and Houses are set to `None`. Data confidence = `0.75`.

### 6.3 Security Invariants for Onboarding
- The frontend **MUST NEVER** display raw coordinates (`latitude`, `longitude`) or exact birth times to other users.
- Raw birth data in `public.birth_data` is protected by Row-Level Security (`birth_data_select_own`).

### 6.4 Interest Onboarding Specification
*(Authoritative Spec: [`docs/INTEREST_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/INTEREST_SYSTEM_V1_SPEC.md))*

Following or alongside birth data entry, the user reaches the Interest step:
1. **Optional Step**: User may tap "Skip" at any time.
2. **5 / 5 Primary Gating**: If the user chooses to select interests, they **MUST select exactly 5 Primary Interests** from a curated pool of ~20 candidate interests (e.g. *Travel, Coffee, Music, Photography, Cinema, Books, Astrology, Food, Hiking, Art, Fitness, Dogs, Technology, Gaming, Fashion, Nature, Theatre, Writing, Psychology, Concerts*).
3. **Continue Gating**: The "Continue" button is active only when selection count equals 5 (or when Skip is pressed).
4. **Signature Interest (Optional Prompt)**: Upon selecting 5, a follow-up asks: *"Which one could you talk about forever?"* (skippable; designates 1 Signature Interest).
5. **No Intensity Sliders**: Never prompt for *Love / Like* intensity ratings during onboarding.
6. **Progressive Architecture**: Onboarding is lightweight; additional Secondary Interests can be added later in profile editing.

### 6.5 Location & Origin Onboarding Specification
*(Authoritative Spec: [`docs/LOCATION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/LOCATION_SYSTEM_V1_SPEC.md))*

Alongside profile creation, the user reaches the Location & Origin step:
1. **Optional Step**: User may tap "Skip for now" at any time.
2. **Current City ("Where are you based?"):**
   - Quick one-tap selection chips for major regional hubs (`Tbilisi`, `Batumi`, `Kutaisi`, `Rustavi`).
   - Autocomplete search input querying `GET /v1/geo/cities?query=...` with instant results.
3. **Hometown / Origin ("Where are you from? — Optional"):**
   - Autocomplete search for origin city/town (e.g. `Kvareli`, `Telavi`, `Gori`).
   - Toggle to make hometown visible on public profile (default: `true`).
4. **Privacy Invariant**:
   - Zero device GPS requests during onboarding. Location is self-declared.
   - Exact coordinates are NEVER surfaced to the client UI.

### 6.6 Lifestyle Snapshot Onboarding Specification
*(Authoritative Spec: [`docs/LIFESTYLE_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/LIFESTYLE_SYSTEM_V1_SPEC.md))*

Following location entry, the user reaches the rapid Lifestyle Snapshot step:
1. **Optional Step**: User may tap "Skip for now" at any time.
2. **3-Question Rapid Cadence Form**:
   - **Daily Rhythm:** Single-tap chips `[ 🌅 Early Bird ]`, `[ 🌙 Night Owl ]`, `[ ⚖️ Flexible ]`.
   - **Activity Pace:** Single-tap chips `[ ⚡ Always Moving ]`, `[ 🌿 Balanced ]`, `[ ☕ Relaxed ]`.
   - **Work Reality:** Single-tap chips `[ 💻 Remote ]`, `[ 🔄 Hybrid ]`, `[ 🏢 On-Site ]`, `[ 🎓 Student ]`, `[ 🚀 Entrepreneur ]`.
3. **Sensitive Item Exclusion**: Drinking, smoking, living situation, and children are **strictly excluded from onboarding** to eliminate friction and prevent discomfort.

### 6.7 Values Onboarding Specification
*(Authoritative Spec: [`docs/VALUES_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/VALUES_SYSTEM_V1_SPEC.md))*

Following lifestyle entry, the user reaches the optional Values step:
1. **Optional Step**: User may tap "Skip for now" at any time.
2. **Interactive 18-Value Grid**: Displayed in 5 clean thematic clusters (`Personal Direction`, `Intellectual & Creative`, `Relational & Ethical`, `Life Grounding`, `Inner Spirit`).
3. **Selection Rule (3 to 5 Values)**:
   - User taps chips to select between 3 and 5 values that guide their life.
   - Counter tracks selection (`Selected: 3 / 5`).
   - "Continue" button unlocks as soon as 3 items are selected, and stays active through 5 items. Tapping a 6th prompts to deselect one.
4. **Optional Core Value Designation**:
   - Follow-up prompt: *"If you had to pick one true north, which is it?"*
   - User may tap one of their chosen values to mark it as Core (`⭐ True North`). Skippable.
5. **Anti-Diagnosis Invariant**: Zero rating sliders (1–10), zero virtue scores, zero personality diagnoses.

### 6.8 Social Behavior Onboarding Specification
*(Authoritative Spec: [`docs/SOCIAL_BEHAVIOR_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/SOCIAL_BEHAVIOR_SYSTEM_V1_SPEC.md))*

Following values selection, the user encounters the optional Social Rhythm Snapshot:
1. **Optional Step**: User may tap "Skip for now" at any time.
2. **3-Question Rapid Preference Card**:
   - **Preferred Gathering:** `[ ☕ One-on-One ]`, `[ 👥 Small Groups ]`, `[ 🎉 Lively Crowds ]`, `[ 🌐 Adaptable ]`.
   - **Social Battery (Energy Dynamics):** `[ 🔋 Recharges Solo ]`, `[ ⚡ Recharges Around People ]`, `[ ⚖️ Context-Dependent ]`.
   - **Approach to New People:** `[ 🚀 Quick to Initiate ]`, `[ 👀 Observant First ]`, `[ 💎 Selective & Intentional ]`.
3. **Anti-Typing Invariant**: Zero personality typing ("Introvert", "Extrovert", "Alpha", MBTI codes); captures functional interaction mechanics only.

### 6.9 Communication Rhythm Onboarding Specification
*(Authoritative Spec: [`docs/COMMUNICATION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/COMMUNICATION_SYSTEM_V1_SPEC.md))*

Following social rhythm entry, the user encounters the optional Communication Rhythm Snapshot:
1. **Optional Step**: User may tap "Skip for now" at any time.
2. **3-Question Rapid Preference Card**:
   - **Conversation Depth:** `[ 🎈 Light & Casual ]`, `[ ⚖️ Balanced Flow ]`, `[ 🌊 Deep & Meaningful ]`.
   - **Conversational Dynamic:** `[ 🔍 Asks Questions ]`, `[ 📖 Shares Stories ]`, `[ 💡 Exchanges Ideas ]`, `[ 🌊 Goes with the Flow ]`.
   - **Preferred Format:** `[ 💬 Mostly Text ]`, `[ 🎙️ Voice Notes OK ]`, `[ 📞 Calls Welcome ]`, `[ 🔄 A Bit of Everything ]`.
3. **Pacing Availability**: Conversational Pacing (`active_banter`, `unhurried_thoughtful`, `relaxed_async`) can be selected during onboarding or managed later in Profile Settings.
4. **Anti-Surveillance Invariant**: Zero reply-time tracking or scorekeeping.

---

## 7. Personal Astrology

### 7.1 Data Received by Frontend
The frontend calls `GET /v1/astrology/profile/safe-astro` (or `POST /v1/astrology/profile/recalculate`) and receives `SafeDerivedAstrologyResponse`:

```json
{
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "sun_sign": "Taurus",
  "moon_sign": "Scorpio",
  "ascendant_sign": "Leo",
  "element_primary": "Earth",
  "modality_primary": "Fixed",
  "source_birth_data_version": 1,
  "engine_version": "1.0.0",
  "updated_at": "2026-08-31T20:00:00Z"
}
```

### 7.2 Data Classification Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                 SAFE DERIVED ASTROLOGY                      │
│                  (Exposed to Frontend)                      │
│  • Sun Sign            • Dominant Element                   │
│  • Moon Sign           • Dominant Modality                  │
│  • Ascendant Sign      • Birth Data Version                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                      SERVER-SIDE ONLY
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                 PRIVATE ASTRONOMICAL DATA                   │
│                 (NEVER EXPOSED TO CLIENT)                   │
│  • Exact Longitudes [0, 360)   • House Cusp Degrees         │
│  • Retrograde Speeds           • Raw Ephemeris Math         │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Profile

### 8.1 Profile Capabilities
- **Get Own Profile**: `GET /v1/profiles/me` -> `ProfileResponse` (includes `location`, `origin`)
- **Update Own Profile**: `PATCH /v1/profiles/me` with fields:
  - `display_name` (string)
  - `avatar_url` (string URL — Profile Photo)
  - `bio` (string)
  - `current_city_id` (UUID referencing canonical `geo_cities`)
  - `hometown_city_id` (UUID referencing canonical `geo_cities`)
  - `hometown_visible` (boolean)
  - `city` (string — legacy fallback)
  - `occupation` (string)
  - `timezone` (string)
  - `is_discoverable` (boolean)
- **Get Target Profile**: `GET /v1/profiles/{profile_id}`

### 8.2 Privacy & Security Boundaries
- **Discoverability**: If `is_discoverable == false`, other users attempting to view `GET /v1/profiles/{id}` receive `404 PrivacySafeNotFoundException`.
- **Block Protection**: If either user blocks the other, profile requests return `404 PrivacySafeNotFoundException` to prevent existence oracles.
- **Profile Photo vs. Face Verification Boundary**: Profile photo is an aesthetic, user-managed visual representation; Face Verification is an independent biometric identity verification security concept. They must remain strictly separate concepts.

### 8.3 Profile Interest Presentation & Management
*(Authoritative Spec: [`docs/INTEREST_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/INTEREST_SYSTEM_V1_SPEC.md))*
- **Visual Hierarchy**: The profile must NOT become a wall of 20–30 generic tags.
- **Primary Interests**: The 5 core declared interests receive prominent visual hierarchy and distinct chip styling.
- **Signature Interest**: If specified, marked with a distinctive highlight badge (*"Which one could you talk about forever?"*).
- **Secondary Interests**: Grouped under a separate expandable/progressive section.
- **Human-Readable Relational Goal**: An interest should help an observer answer: *"What could I talk to this person about?"* rather than *"This person checked a box."*

### 8.4 Location & Origin Presentation
*(Authoritative Spec: [`docs/LOCATION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/LOCATION_SYSTEM_V1_SPEC.md))*
- **Primary Location**: Renders prominently as `📍 Tbilisi` (or `📍 Berlin, Germany` if international).
- **Origin / Hometown**: If configured and `hometown_visible == true`, renders as `🏡 From Kvareli` or `📍 Tbilisi · From Kvareli`.
- **Privacy Control**: In profile settings, user can toggle hometown visibility on or off at any time.
- **Coordinate Invariant**: Exact geographic coordinates, street addresses, and live GPS tracking are NEVER displayed or fetched by the client.

### 8.5 Lifestyle Cadence Presentation & Habit Privacy
*(Authoritative Spec: [`docs/LIFESTYLE_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/LIFESTYLE_SYSTEM_V1_SPEC.md))*
- **Cadence Micro-Badges**: Displayed as compact, elegant chips under a "Cadence" card section:
  - `[ 🌙 Night Owl ]` `[ ⚡ Always Moving ]` `[ 💻 Remote ]` `[ 🐕 Has a Dog ]`
- **Avoid Checkbox Clutter**: Never present lifestyle as a clinical checklist of checkboxes or medical intake form.
- **Granular Privacy Toggles**: In profile settings, users can toggle visibility on any habit (drinking, smoking, living situation) independently.
- **Empty State Restraint**: Undeclared attributes simply do not render (no *"Drinking: Not specified"* clutter).

### 8.6 Values & Guiding Compass Presentation
*(Authoritative Spec: [`docs/VALUES_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/VALUES_SYSTEM_V1_SPEC.md))*
- **Guiding Compass Micro-Badges**: Displayed under a dedicated "Guiding Compass" or "Values" profile section:
  - `⭐ Curiosity (Core)` `[ Growth ]` `[ Honesty ]` `[ Autonomy ]`
- **Aesthetic Glassmorphism**: Clean, refined badge styling without cluttering the profile.
- **Privacy Control**: In profile settings, user can toggle the entire Values section visible or hidden.
- **Strictly Non-Clinical**: Never show percentage bars, personality labels, or diagnostic assessments.

### 8.7 Social Rhythm Presentation & Preference Privacy
*(Authoritative Spec: [`docs/SOCIAL_BEHAVIOR_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/SOCIAL_BEHAVIOR_SYSTEM_V1_SPEC.md))*
- **Social Rhythm Micro-Badges**: Displayed under a dedicated "Social Rhythm" profile section:
  - `[ ☕ One-on-One ]` `[ 🔋 Recharges Solo ]` `[ 👀 Observant First ]` `[ ⚡ Spontaneous ]`
- **Granular Privacy Toggles**: Users can independently toggle any social behavior attribute on or off in profile settings.
- **Empty State Restraint**: Undeclared preferences simply do not render.
- **Strictly Non-Diagnostic**: Never display radar charts, psychometric profiles, or clinical labels.

### 8.8 Communication Rhythm Presentation & Preference Privacy
*(Authoritative Spec: [`docs/COMMUNICATION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/COMMUNICATION_SYSTEM_V1_SPEC.md))*
- **Communication Rhythm Micro-Badges**: Displayed under a dedicated "Communication Rhythm" profile section:
  - `[ 🌊 Deep & Meaningful ]` `[ 💡 Exchanges Ideas ]` `[ 🎙️ Voice Notes OK ]` `[ ⏳ Unhurried Pace ]`
- **Granular Privacy Controls**: Users can independently toggle any communication attribute on or off in profile settings.
- **Empty State Restraint**: Undeclared preferences simply do not render.
- **Zero Latency Shaming**: Never display response-time averages, read-receipt timers, or typing speed metrics.

### 8.9 Intent Presentation & "Looking For" Badges
*(Authoritative Spec: [`docs/INTENT_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/INTENT_SYSTEM_V1_SPEC.md))*
- **Looking For Micro-Badges**: Displayed prominently near top of profile under "Looking For":
  - `[ 👥 New Friends (Main) ]` `[ 🧗 Activity Partner ]` `[ 🔍 Just Exploring ]`
- **Visual Distinction**: Primary intent receives distinct highlight badge with icon; secondary intents render as subtle companion chips.
- **Visibility Controls**: User can toggle intent visibility (`public`, `connections_only`, `hidden`) in profile settings.
- **Non-Diagnostic Stance**: Strictly descriptive of current purpose; zero relationship status interrogation.

### 8.10 Prompts & Self-Expression Presentation
*(Authoritative Spec: [`docs/PROMPTS_SELF_EXPRESSION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/PROMPTS_SELF_EXPRESSION_SYSTEM_V1_SPEC.md))*
- **Prominent Human Voice Cards**: Rendered as distinct speech/quotation cards displaying the standardized prompt question in bold accent typography alongside the user's authentic answer.
- **Capacity Limits**: Renders up to 3 published prompt cards (`sort_order` 1 to 3).
- **Interactive Action Anchor**: Every prompt card features a dedicated `[ 💬 Reply to this ]` button, inviting immediate low-friction conversational entry.
- **Authentic Voice Invariant**: Displays user-authored text exactly as approved. AI never generates profile answers without user review. Empty prompts simply do not render.

---

## 9. People Discovery

### 9.1 Discovery Lifecycle
1. User views a discoverable profile (`GET /v1/profiles/{target_id}`).
2. User inspects the target's public safe astrology (`GET /v1/astrology/people/{target_id}/safe-astro`).
3. User inspects shared, related, or complementary interest hooks.
4. User initiates a connection request (`POST /v1/connections`).

### 9.2 Public Profile vs Connection Relationship Boundary
- A user **CAN** see Sun/Moon/Ascendant signs, primary element/modality, and declared interests of discoverable non-connected users.
- A user **CANNOT** run compatibility analysis or initiate direct chat without an active accepted connection.

### 9.3 Interest Discovery Matching
The Discovery UI evaluates three relationship types:
1. **Shared**: Exact mutual canonical interest (*"You both love photography"*).
2. **Related**: Graph-connected semantic neighbors (*"You both seem to like exploring the world — just differently"*).
3. **Complementary**: Different declared interests paired with compatible communication energy (*"Different interests. Similar energy"*).
- Internal recommendation relies on multi-signal **Interest Clusters** (*Explorers*, *Creatives*, *Thinkers*, etc.) rather than flat single-tag comparisons.

### 9.4 Location Relevance in Discovery
- **Proximity Boost**: Users residing in the same current city receive an organic soft relevance boost to facilitate real-world meeting potential.
- **Shared Origin Observation**: When two users share a hometown root or regional heritage, discovery cards surface contextual observations (e.g. *"Both based in Tbilisi · Originally from Kvareli"* or *"Shared roots in Kakheti"*).
- **No Hard Exclusion**: Proximity is a soft signal; high-synergy connections in other cities remain discoverable.

### 9.5 Lifestyle Cadence in Discovery Matching
- **Rhythm Harmony**: Highlights natural late-night or early-morning conversational synergy (e.g. *"Both night owls — expect 2 AM chats"*).
- **Schedule Synergy**: Surfaces remote/flexible work synergies for daytime coffee or co-working connections.
- **Soft Relevance**: Lifestyle alignment serves as natural conversational context, never as hard exclusionary filters in V1.

### 9.6 Values & Philosophical Resonance in Discovery
*(Authoritative Spec: [`docs/VALUES_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/VALUES_SYSTEM_V1_SPEC.md))*
- **Shared Values (Direct Resonance)**: Surfaces shared life principles as conversational hooks (e.g. *"Both guided by Curiosity and Growth — endless shared rabbit holes"*).
- **Complementary Polarities**: Highlights constructive philosophical balances with trademark JESTER wit (e.g. *Autonomy + Loyalty*: *"One brings fierce independence, one brings steadfast loyalty. Space to breathe with a secure tether"*).
- **Soft Relevance**: In V1, values act as philosophical compatibility signals and conversation bridges, never as hard exclusionary dealbreaker filters.

### 9.7 Social Dynamics in Discovery Matching
*(Authoritative Spec: [`docs/SOCIAL_BEHAVIOR_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/SOCIAL_BEHAVIOR_SYSTEM_V1_SPEC.md))*
- **Gathering Harmony**: Surfaces shared preferences (e.g. *"Both thrive in one-on-one settings — quiet corner cafés over chaotic parties"*).
- **Battery Awareness**: Highlights mutual or complementary recharge styles (e.g. *"Both need quiet downtime after socializing — zero pressure, zero guilt"*).
- **Meeting Setting Intelligence**: AI uses mutual comfort zones to suggest optimal low-friction first hangouts.
- **Soft Relevance**: In V1, social dynamics serve as practical relationship context and meeting aids, never hard exclusionary gates.

### 9.8 Communication Dynamics in Discovery Matching
*(Authoritative Spec: [`docs/COMMUNICATION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/COMMUNICATION_SYSTEM_V1_SPEC.md))*
- **Depth Resonance**: Surfaces shared conversational appetite (e.g. *"Both skip the shallow small talk — conversations here get real quickly"*).
- **Role Pairing**: Identifies natural flow (e.g. Questioner + Storyteller: *"One draws stories out, one loves narrating vivid experiences"*).
- **Pacing Reassurance**: Reassures users connecting with unhurried responders (*"Unhurried, thoughtful rhythm — expect quality over immediate speed"*).
- **Decoupled from Synastry**: Complements the deterministic astrological Mercury score without altering it.

### 9.9 Intent Partitioning & Alignment in Discovery Matching
*(Authoritative Spec: [`docs/INTENT_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/INTENT_SYSTEM_V1_SPEC.md))*
- **Bilateral Partitioning**: Users seeking exclusively serious dating are never matched with users seeking exclusively platonic friendship or collaboration unless a secondary bridge or `just_exploring` exists.
- **Shared Intent Boost**: Users sharing identical primary intent receive a prominent relevance boost in discovery ordering.
- **Multi-Domain Actionable Invitations**: Combines intent with interests and lifestyle to generate concrete invitations (e.g. *"Both seeking activity partners and both love hiking — easy weekend plan"*).
- **Astrology Primacy Invariant**: Astrological synastry is framed strictly within declared intent; zero romantic assumptions projected onto platonic seekers.

### 9.10 Prompts in Discovery & Profile Preview
*(Authoritative Spec: [`docs/PROMPTS_SELF_EXPRESSION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/PROMPTS_SELF_EXPRESSION_SYSTEM_V1_SPEC.md))*
- **Human Voice Snippet**: Discovery profile previews highlight the user's #1 prompt as a conversational teaser card (*"What this person actually sounds like"*).
- **Direct Reply Action**: Viewers can tap `[ 💬 Reply to this ]` directly from the discovery card or full profile view to initiate a connection request quoting that specific prompt.
- **Differentiation Factor**: Two profiles with similar astrological charts and shared interests are instantly differentiated by their authentic prompt humor, voice, and perspective.

### 9.11 Discovery Preferences & Feed Architecture
*(Authoritative Spec: [`docs/DISCOVERY_PREFERENCES_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/DISCOVERY_PREFERENCES_SYSTEM_V1_SPEC.md))*
- **Unified Candidate Pool with Contextual Lenses**: Discovery serves candidates through a single coherent feed governed by active preferences, navigable via 4 lenses:
  - `[ ✨ For You ]`: Balanced multi-signal master feed.
  - `[ 📍 Nearby ]`: Local city and neighborhood priority.
  - `[ 🎯 Shared Purpose ]`: Direct intent alignment (e.g. Activity Partners).
  - `[ 💡 Shared Curiosities ]`: Semantic interest graph clusters.
- **Qualitative Explainability Cards**: Eliminates clinical percentage match scores. Every discovery card articulates a clear human rationale (e.g. *"You both love photography and are looking for friendship in Tbilisi"*).
- **Graceful Pool Depletion**: If tight preferences yield $< 5$ candidates, surfaces an inline notice (*"Your current settings are very specific"*); if exhausted, provides a 1-tap `[ 🌍 Broaden to Entire Country ]` action.

---

## 10. Connections

### 10.1 Connection State Machine

```
                    ┌─────────────────────────┐
                    │      [No Record]        │
                    └────────────┬────────────┘
                                 │
                         POST /connections
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │         PENDING         │
                    └──────┬───────────┬──────┘
                           │           │
           POST /transition│           │POST /transition
           (action=accept) │           │(action=decline)
                           ▼           ▼
             ┌─────────────────┐   ┌─────────────────┐
             │    ACCEPTED     │   │    DECLINED     │
             └────────┬────────┘   └────────┬────────┘
                      │                     │
      POST /transition│     POST /transition│
      (action=remove) │     (action=block)  │
                      ▼                     ▼
             ┌─────────────────┐   ┌─────────────────┐
             │     REMOVED     │   │     BLOCKED     │
             └─────────────────┘   └────────┬────────┘
                                            │
                             POST /transition
                             (action=unblock)
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │     REMOVED     │
                                   └─────────────────┘
```

### 10.2 State Permissions & Actions Matrix

| State | Initiator Can Do | Target Can Do | Compatibility Allowed? | Messaging Allowed? |
| :--- | :--- | :--- | :--- | :--- |
| **`pending`** | View pending status; Block; Remove. | Accept; Decline; Block. | ❌ No (403 Forbidden) | ❌ No (403 Forbidden) |
| **`accepted`** | Compare; Message; Block; Remove. | Compare; Message; Block; Remove. | ✅ Yes (200 OK) | ✅ Yes (201 Created) |
| **`declined`** | Re-send request (reactivates pending). | Block; Remove. | ❌ No (403 Forbidden) | ❌ No (403 Forbidden) |
| **`blocked`** | Unblock (transitions to `removed`). | Profile/Chat returns 404 (hidden).| ❌ No (404 Not Found) | ❌ No (404 Not Found) |
| **`removed`** | Re-send request (transitions to pending).| Re-send request. | ❌ No (403 Forbidden) | ❌ No (403 Forbidden) |

### 10.3 Connection Request Intent Context & "Why Connect?" Reason
- **Transparent Mutual Intent**: The connection modal highlights shared intent alignment (e.g. *"You're both open to shared activities"*).
- **Optional Context Reason (`connection_reason`)**: Senders can attach an optional 1-tap tag (`[ ☕ Grab coffee ]`, `[ 💬 Great conversation ]`, `[ 🧗 Activity ]`, `[ 🎨 Project ]`).
- **Recipient Experience**: The notification and request card show the explicit reason, eliminating cold-start ambiguity.

### 10.4 Prompt-Referenced Connection Invitations
- **Inline Quote Action**: When a user taps `[ 💬 Reply to this ]` on a prompt card, the connection invitation modal pre-populates with that prompt quoted directly at the top.
- **Contextual Note**: The sender can attach a short note (up to 200 characters) responding specifically to the prompt (e.g. Prompt: *"Finding the best khachapuri in Tbilisi"* -> Note: *"You have to try the one at Sakhachapure N1 on Rustaveli!"*).
- **Conversation Continuity**: Upon request acceptance, the quoted prompt and invitation note become the very first message bubble in the newly opened direct chat thread.

---

## 11. Compare / Synastry

### 11.1 Response Payload Contract
When calling `POST /v1/compare` or `GET /v1/people/{id}/why`, the frontend receives `StructuredCompatibilityResponse`:

```json
{
  "id": "c4b12345-6789-abcd-ef01-23456789abcd",
  "target_user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "score": 84.2,
  "dimensions": {
    "emotional_harmony": 86.5,
    "communication": 79.0,
    "attraction": 88.0,
    "growth_long_term": 74.5
  },
  "signals": [
    {
      "type": "sun_trine_moon",
      "category": "harmony",
      "strength": "high",
      "source_aspects": ["Sun Trine Moon (Orb 1.2°)"],
      "label": "Emotional Resonance"
    },
    {
      "type": "venus_conjunction_mars",
      "category": "attraction",
      "strength": "high",
      "source_aspects": ["Venus Conjunction Mars (Orb 0.8°)"],
      "label": "Magnetic Chemistry"
    }
  ],
  "best_topics": ["travel", "creative_work", "philosophy"],
  "conversation_starters": [
    "What is something that instantly makes you feel understood?",
    "What art or music has inspired you recently?"
  ],
  "data_quality": {
    "time_precision": "exact",
    "confidence": 1.0,
    "houses_used": true,
    "ascendant_used": true
  },
  "engine_version": "synastry-v1.0.0",
  "calculated_at": "2026-08-31T21:35:00Z"
}
```

### 11.2 Product Meaning of Fields
- **`score` ($10.0 - 98.0$)**: Normalized overall relationship compatibility index.
- **`dimensions` ($0.0 - 100.0$)**:
  - `emotional_harmony`: Emotional resonance, shared temperament, and instinctive comfort.
  - `communication`: Intellectual rapport, mental alignment, and conversational ease.
  - `attraction`: Chemistry, romantic vitality, and magnetic pull.
  - `growth_long_term`: Motivational dynamics, mutual ambition, resilience, and constructive tension.
- **`data_quality.confidence` ($0.50 - 1.00$)**: Reliability index based on birth time accuracy and active aspect density.

---

## 12. Relationship Understanding / "Why"

### 12.1 Endpoint
`GET /v1/people/{target_user_id}/why`

### 12.2 Prerequisites & Behavior
- Requires authenticated session and active accepted connection.
- Returns identical structured payload as `/v1/compare`.
- Designed for deep-dive relationship explanation views, highlighting dimension breakdowns and why specific dynamics occur.

---

## 13. Signals

### 13.1 Signal Characteristics
- **Limit**: Maximum **6** signals returned per relationship.
- **Threshold**: Only aspects with strength $S_{\text{aspect}} \ge 0.40$ qualify.
- **Priority**: Ordered by mathematical importance ($W_{\text{pair}} \times S_{\text{aspect}}$ descending).
- **Categories**: `"harmony"`, `"attraction"`, `"communication"`, `"growth"`, `"stability"`, `"notice"`.

### 13.2 Frontend Display Responsibilities
- The frontend renders the backend-provided `label`, `category`, and `strength`.
- The frontend **MUST NOT** execute client-side astrology calculations or re-categorize signals.

---

## 14. Topics

### 14.1 Topic Characteristics
- **Limit**: Maximum **4** topic tokens returned per pair.
- **Generation**: Deterministically derived from Mercury alignments and shared dominant elements.
- **Standard Topics**: `["books", "philosophy", "ideas", "creative_work", "travel", "adventure", "fitness", "ambition", "art", "music", "psychology", "cinema", "architecture", "food", "design", "lifestyle"]`.

### 14.2 Frontend Responsibility
- Present topics as suggested conversation themes or interest tags.

---

## 15. Conversation Starters

### 15.1 Starter Characteristics
- **Limit**: Maximum **3** high-engagement questions returned per pair.
- **Source**: Deterministically mapped from top active relationship signals.
- **Purpose**: Serve as icebreakers directly rooted in the astrological synergy of the pair.

### 15.2 Frontend Responsibility
- Provide one-tap actions (e.g. "Send as Message" or "Copy to Clipboard") directly from the Compatibility/Why screen into the active chat thread.

---

## 16. Messaging

### 16.1 Capabilities & Rules
- **Prerequisite**: Active accepted connection (`public.is_active_direct_conversation`).
- **Create / Retrieve Conversation**: `POST /v1/conversations` with `{"target_user_id": UUID}`.
- **List Messages**: `GET /v1/conversations/{id}/messages` (ordered chronologically by `created_at ASC`).
- **Send Message**: `POST /v1/conversations/{id}/messages` with `{"body": str}`.
- **Realtime Updates**: Subscribe via Supabase Realtime WebSocket channel: `public:messages:conversation_id=eq.{id}`.

### 16.2 Block & Removal Behavior
- If either user blocks the other or removes the connection, subsequent requests to `/messages` return `404 PrivacySafeNotFoundException`.

---

## 17. Notifications

### 17.1 Capabilities & Endpoints
- **List Notifications**: `GET /v1/notifications` -> `list[NotificationResponse]`.
- **Mark Notification Read**: `PATCH /v1/notifications/{id}/read`.
- **Realtime Notifications**: Subscribe via Supabase Realtime channel: `public:notifications:user_id=eq.{my_id}`.

### 17.2 Notification Types & Navigation Target Map

| Notification Type | Trigger Event | Navigation Destination in Frontend |
| :--- | :--- | :--- |
| `"connection_request"` | Target received a connection request | Connections Screen -> Pending Requests tab |
| `"connection_accepted"` | Requester's connection was accepted | Profile / Compatibility Screen for Target |
| `"message_received"` | New incoming chat message | Active Conversation Screen |
| `"daily_energy"` | Morning daily transit ready | Personal Astrology / Today's Energy Screen |
| `"system"` | Platform announcement / security notice | In-App Modal or Notification Center |

---

## 18. Frontend State Model

The frontend state machine must maintain the following global and feature-level states:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. AUTH STATE: [LoggedOut | Authenticating | Authenticated] │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ONBOARDING STATE: [NoBirthData | Saving | Calculated]   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. PROFILE STATE: [Discoverable | Private | Editing]        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. RELATIONSHIP STATE (per target user):                    │
│    [None | PendingOut | PendingIn | Accepted | Blocked]     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. COMPATIBILITY STATE (for accepted connection):           │
│    [Loading | Ready | StaleRecalculating | LowEvidence]     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. CHAT STATE: [Connecting | Idle | Sending | Realtime]     │
└─────────────────────────────────────────────────────────────┘
```

---

## 19. API → Frontend Contract

| User Action / Goal | Endpoint | Method | Payload | Expected Response | Auth Required |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Get account identity | `/v1/users/me` | `GET` | None | `UserResponse` | Bearer JWT |
| Get own profile | `/v1/profiles/me` | `GET` | None | `ProfileResponse` | Bearer JWT |
| Update profile details | `/v1/profiles/me` | `PATCH` | `ProfileUpdate` | `ProfileResponse` | Bearer JWT |
| View target profile | `/v1/profiles/{id}` | `GET` | None | `ProfileResponse` (404 if blocked/private) | Bearer JWT |
| Get own safe astrology | `/v1/astrology/profile/safe-astro` | `GET` | None | `SafeDerivedAstrologyResponse` | Bearer JWT |
| Recalculate own astrology | `/v1/astrology/profile/recalculate` | `POST` | None | `SafeDerivedAstrologyResponse` | Bearer JWT |
| View person safe astrology | `/v1/astrology/people/{id}/safe-astro` | `GET` | None | `SafeDerivedAstrologyResponse` | Bearer JWT |
| List my connections | `/v1/connections` | `GET` | None | `list[ConnectionResponse]` | Bearer JWT |
| Send connection request | `/v1/connections` | `POST` | `ConnectionCreate` | `ConnectionResponse` | Bearer JWT |
| Transition connection | `/v1/connections/{id}/transition` | `POST` | `ConnectionTransition` | `ConnectionResponse` | Bearer JWT |
| Calculate compatibility | `/v1/compare` | `POST` | `CompareRequest` | `StructuredCompatibilityResponse` | Bearer JWT (Accepted conn) |
| Deep-dive compatibility | `/v1/people/{id}/why` | `GET` | None | `StructuredCompatibilityResponse` | Bearer JWT (Accepted conn) |
| Get/create direct chat | `/v1/conversations` | `POST` | `DirectConversationCreate` | `ConversationResponse` | Bearer JWT (Accepted conn) |
| List conversation messages | `/v1/conversations/{id}/messages` | `GET` | None | `list[MessageResponse]` | Bearer JWT |
| Send chat message | `/v1/conversations/{id}/messages` | `POST` | `MessageCreate` | `MessageResponse` | Bearer JWT |
| List notifications | `/v1/notifications` | `GET` | None | `list[NotificationResponse]` | Bearer JWT |
| Mark notification read | `/v1/notifications/{id}/read` | `PATCH` | None | `NotificationResponse` | Bearer JWT |

---

## 20. Screen / Route Inventory

| Route Name | Purpose & User Goal | Required API Endpoints | Entry Points | Available Actions |
| :--- | :--- | :--- | :--- | :--- |
| **`/auth/login`** | Authenticate user | Supabase Auth login | App Launch | Login, Navigate to Register |
| **`/auth/register`** | Register new account | Supabase Auth signup | Login Screen | Signup, Verify Email |
| **`/onboarding/birth-data`**| Enter birth parameters | `birth_data` upsert, `/profile/recalculate` | Registration | Pick Date, Time, Precision, Timezone, City |
| **`/self/astrology`** | View own natal placements | `GET /v1/astrology/profile/safe-astro` | Bottom Nav / Home | View Sun/Moon/Asc signs, Element, Modality |
| **`/self/profile`** | Edit social identity | `GET/PATCH /v1/profiles/me` | Bottom Nav | Change Display Name, Bio, City, Discoverability |
| **`/people/{id}`** | View discoverable profile | `GET /v1/profiles/{id}`, `/people/{id}/safe-astro` | Search / Discovery | View public signs, Send Connection Request |
| **`/connections`** | Manage social network | `GET /v1/connections`, `POST /transition` | Bottom Nav | Accept, Decline, Remove, Block requests |
| **`/compare/{target_id}`**| View compatibility score | `POST /v1/compare` | Person Profile / Chat | View Score, 4 Dimensions, Signals, Topics |
| **`/why/{target_id}`** | Deep relationship insight | `GET /v1/people/{target_id}/why` | Compare Screen | Inspect Detailed Dynamics, Starters |
| **`/chat/{conversation_id}`**| Direct messaging | `GET/POST /conversations/{id}/messages` | Connections / Compare | Send message, Insert Conversation Starter |
| **`/notifications`** | View in-app activity | `GET/PATCH /v1/notifications` | Top Header Bell | View list, Mark as read, Tap to navigate |

---

## 21. Empty / Loading / Error / Edge States

1. **No Birth Data Entered**: Compatibility and safe astrology show onboarding prompt; `/v1/compare` returns 404 (`birth_data_missing`).
2. **Unknown Birth Time**: Personal astrology and compatibility gracefully hide Ascendant and houses; confidence badge indicates `75% (Unknown Time)`.
3. **Approximate Birth Time**: Ascendant is shown with approximate badge; confidence badge indicates `85%`.
4. **No Connections Yet**: Connections screen renders empty state with "Discover People" call to action.
5. **Pending Connection**: Compare and Chat buttons are replaced with "Connection Request Pending" badge.
6. **Declined Connection**: Displays "Request Declined" state with option to re-request after cool-down.
7. **Blocked User**: Target profile and messages disappear immediately (`404 Not Found`).
8. **Low Evidence Compatibility**: Charts with $< 2.0$ active aspect weight render baseline `65.0` with `"Independent Chart Dynamics"` notice signal.
9. **Stale Compatibility Cache**: Recalculates transparently in background on next visit after birth-data edit.

---

## 22. Privacy & Security Rules

### Data the Frontend May Display:
- Own raw birth data (to the authenticated owner only).
- Derived zodiac signs (Sun, Moon, Ascendant).
- Dominant element & dominant modality.
- Connection status and public profile information of discoverable users.
- Compatibility scores, dimension breakdowns, signals, topics, starters, and confidence indicators.

### Data the Frontend Must NEVER Request or Expose:
- Raw planetary longitudes ($[0^\circ, 360^\circ)$) of other users.
- `public.astro_private` database contents.
- Exact birth date, birth time, or GPS coordinates of other users.
- Confirmation of whether a blocked user exists.

---

## 23. Frontend vs Backend Responsibility

| Responsibility Domain | Backend Owns | Frontend Owns |
| :--- | :--- | :--- |
| **Ephemeris & Astro Calculations** | ✅ 100% Swiss Ephemeris C math | ❌ Never performs astro math |
| **Synastry Scoring & Aspects** | ✅ Aspect detection, weights, caps, stretch | ❌ Renders calculated scores |
| **Signals & Topics** | ✅ Deterministic extraction & limits | ❌ Renders provided labels |
| **Authorization & Privacy** | ✅ RLS policies, connection guards | ❌ Handles HTTP 401/403/404 responses |
| **Presentation & UI Flow** | ❌ Agnostic JSON APIs | ✅ Navigation, forms, caching, layouts |
| **Realtime Subscriptions** | ✅ PostgreSQL Realtime publications | ✅ WebSocket channel listeners |

---

## 24. Future / Out of Scope

The following features are **explicitly excluded** from V1 frontend requirements:
- House overlay synastry (Synastry V1.1).
- Extended asteroids (Chiron, Ceres, Juno, Pallas, Vesta) and Lunar Nodes (Synastry V2.0).
- OpenAI / LLM conversational voice interpretations (`interpretation/` stubs).
- Native iOS/Android push notification background receivers.
- Group chat threads and message reactions.

---

## 25. Backend Gaps Required for Complete Frontend

| Identified Gap | Description | Required Backend Action | Priority |
| :--- | :--- | :--- | :--- |
| **1. Dedicated Birth Data Endpoint** | Currently `birth_data` is written via direct Supabase client or DB scripts. A unified FastAPI `PUT /v1/birth-data` is cleaner for web clients. | Create `backend/app/astrology/birth_data_router.py`. | **HIGH** |
| **2. Paginated Discovery Feed** | Currently frontend can only fetch profiles by ID `GET /v1/profiles/{id}`. A general discovery list is needed. | Add `GET /v1/people/discover?limit=20&cursor=...` endpoint. | **HIGH** |
| **3. Realtime Chat Presence** | Typing indicators and online presence are not yet modeled in database tables. | Configure Supabase Presence channel on frontend. | **MEDIUM** |

---

## 26. Open Product Decisions

1. **Evidence Trace Visibility in UI**: Should power-users have an "Advanced Astrology Breakdown" drawer exposing aspect orbs, or should this remain strictly internal?
2. **Birth Time Unknown UI Guardrails**: Should the UI prompt users with educational tooltips explaining that Ascendant & Houses require exact birth times?
3. **Re-connection Cool-down Period**: When a connection is declined or removed, is there an immediate re-request allowance or a 24-hour cool-down?

---

## 27. Implementation Readiness Checklist

- [x] Ephemeris calculation engine operational and tested (`pyswisseph`).
- [x] Synastry V1 engine operational, verified, and passing 69/69 tests.
- [x] Database migrations 001 to 021 applied.
- [x] RLS policies isolating birth data and private astrology verified.
- [x] Connection state machine with block enforcement verified.
- [x] Direct conversation and messaging endpoints operational.
- [x] Notifications system active.
- [x] Frontend capability specification finalized (`docs/FRONTEND_CAPABILITY_SPECIFICATION.md`).
