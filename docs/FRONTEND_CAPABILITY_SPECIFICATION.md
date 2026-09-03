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
- Multi-step birth-data onboarding wizard with precision selection (`exact`, `approximate`, `unknown`).
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
- **Birth Data CRUD Endpoint**: Direct birth data upsert currently operates via Supabase PostgREST client (`supabase.from('birth_data')`) with RLS, whereas recalculation uses `POST /v1/astrology/profile/recalculate`. Product decision needed on whether to add a dedicated FastAPI endpoint `PUT /v1/birth-data`.
- **People Discovery Feed**: The backend supports direct ID lookup `GET /v1/profiles/{id}` with discoverability check, but does not yet expose a paginated `GET /v1/people/discover` feed.
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
To establish astrological identity, the frontend must collect raw birth information:

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
- **Get Own Profile**: `GET /v1/profiles/me` -> `ProfileResponse`
- **Update Own Profile**: `PATCH /v1/profiles/me` with fields:
  - `display_name` (string)
  - `avatar_url` (string URL)
  - `bio` (string)
  - `city` (string)
  - `occupation` (string)
  - `timezone` (string)
  - `is_discoverable` (boolean)
- **Get Target Profile**: `GET /v1/profiles/{profile_id}`

### 8.2 Privacy & Discoverability Rules
- If `is_discoverable == false`, other users attempting to view `GET /v1/profiles/{id}` receive `404 PrivacySafeNotFoundException`.
- If either user blocks the other, profile requests return `404 PrivacySafeNotFoundException` to prevent existence oracles.

---

## 9. People Discovery

### 9.1 Discovery Lifecycle
1. User views a discoverable profile (`GET /v1/profiles/{target_id}`).
2. User inspects the target's public safe astrology (`GET /v1/astrology/people/{target_id}/safe-astro`).
3. User initiates a connection request (`POST /v1/connections`).

### 9.2 Public Profile vs Connection Relationship Boundary
- A user **CAN** see Sun/Moon/Ascendant signs and primary element/modality of discoverable non-connected users.
- A user **CANNOT** run compatibility analysis or initiate direct chat without an active accepted connection.

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
