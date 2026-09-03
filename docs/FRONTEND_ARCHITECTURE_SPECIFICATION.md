# JESTER V1 — FRONTEND ARCHITECTURE SPECIFICATION

**Document Version:** `1.0.0`  
**System Role:** Lead Product Architect & Senior Frontend Systems Architect  
**Backend Reference Version:** `synastry-v1.0.0` (Production Ready, 74/74 passing tests)  
**Parent Blueprint:** [`docs/FRONTEND_CAPABILITY_SPECIFICATION.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/FRONTEND_CAPABILITY_SPECIFICATION.md)  
**Status:** Authoritative Frontend Architectural Blueprint  

---

## 1. Architectural Principles

The JESTER frontend is designed as a high-integrity, deterministic, privacy-first client application. The following core principles govern all frontend architectural decisions:

1. **Backend as the Single Source of Truth**: The frontend is a presentation and interaction layer. It never computes or derives astronomical coordinates, aspect geometries, synastry dimensions, or compatibility scores.
2. **Deterministic Rendering**: All compatibility representations (scores, dimensions, signals, topics, starters) are direct, reproducible renderings of backend JSON payloads.
3. **Privacy by Design**: The frontend strictly prevents the exposure, storage, or transmission of private astronomical data (`astro_private`), raw coordinate degrees of other users, or internal mathematical audit traces (`evidence_trace`).
4. **State-Driven Information Architecture**: UI states (loading, empty, ready, stale, blocked, low evidence) are derived deterministically from server state, authentication claims, and relationship status.
5. **Decoupled Server & Local State**: Server state (profiles, connections, compatibility, chat history) is managed via an asynchronous query caching layer; local transient state (form inputs, active modal tabs, optimistic message drafts) is strictly isolated.
6. **Graceful Privacy Degradation**: Blocked users or non-discoverable resources return standardized privacy-safe `404 Not Found` exceptions, which the frontend renders as standard "Resource Not Found" without leaking existence oracles.
7. **Calm, Non-Defective Edge Presentation**: Missing birth times (`unknown` precision) and low aspect densities ($< 2.0$ active weight) are represented as valid, transparent astrological realities, never as system bugs or red error states.
8. **Realtime-Synchronized Communication**: Direct messaging and notifications maintain seamless, bi-directional synchronization between local query caches and Supabase Realtime WebSocket streams.
9. **Zero Business Logic Duplication**: Validation rules, connection transition invariants, and access guards live on the server; the frontend adheres strictly to server-provided error codes and status transitions.
10. **Device-Agnostic Capability Parity**: The functional architecture, state machines, and API interactions remain identical across Desktop Web, Mobile Web, and Native Mobile (React Native) runtimes.
11. **Data Layer vs. Consumer Experience**: The current technical screen exposing raw signs (Sun, Moon, Ascendant, Element, Modality) verifies data layer availability, but is NOT the final consumer UX. The production client translates rich underlying astrological computations into a human-first, witty JESTER experience (`ME → YOU → US → MORE PEOPLE`). Rich astrological data is strictly preserved in the backend/data layer.


---

## 2. Application Shell

The Application Shell provides the persistent frame, authentication gating, layout boundaries, and global notification subscriptions.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          GLOBAL APP SHELL                              │
│  [Network Monitor] [Auth Interceptor] [Global Realtime Orchestrator]   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌──────────────────────────────────┐        ┌──────────────────────────────────┐
│       UNAUTHENTICATED SHELL      │        │        AUTHENTICATED SHELL       │
│  • Public Marketing / Welcome    │        │  • Global Top Navigation / Header│
│  • Login / Register Container    │        │  • Persistent Bottom Nav (Mobile)│
│  • Password Recovery             │        │  • Active Subscriptions Listener │
│  • Auth Redirect Watchdog        │        │  • Route Viewport / Sub-Routes   │
└──────────────────────────────────┘        └──────────────────────────────────┘
```

### 2.1 Unauthenticated Shell
- **Role**: Gated container for `/auth/login`, `/auth/register`, and session recovery.
- **Responsibilities**:
  - Catches unauthenticated deep links and preserves the intended redirect target (`return_to`).
  - Clears all stale local user state, query caches, and active WebSocket subscriptions upon entry.

### 2.2 Authenticated Shell
- **Role**: Persistent application cockpit for verified users.
- **Responsibilities**:
  - **Global Header**: Displays current route title, notifications bell with unread badge counter, and user profile avatar shortcut.
  - **Primary Navigation**:
    - **Desktop**: Persistent side navigation drawer or top menu bar (`Discover`, `Connections`, `Messages`, `Self`).
    - **Mobile**: Persistent bottom tab bar (`Discover`, `Connections`, `Messages`, `Self`) plus floating contextual action triggers.
  - **Global Notification & Realtime Listener**: Maintains an active WebSocket channel to `public:notifications:user_id=eq.{my_id}`.
  - **Onboarding Interceptor**: Evaluates `birth_data` presence; redirects incomplete accounts to `/onboarding/birth-data`.

---

## 3. Information Architecture

JESTER's information hierarchy maps directly to the 8-stage Product Loop:

```
JESTER V1
│
├── 1. AUTHENTICATION
│   ├── Login (/auth/login)
│   └── Register (/auth/register)
│
├── 2. ONBOARDING
│   └── Birth Data Wizard (/onboarding/birth-data)
│
├── 3. SELF (Astrological Identity & Personal Profile)
│   ├── Personal Astrology (/self/astrology) [Sun/Moon/Asc signs, Element, Modality]
│   └── Profile Settings (/self/profile) [Bio, City, Occupation, Discoverability]
│
├── 4. DISCOVER (People & Public Profiles)
│   └── Person View (/people/{id}) [Public Profile, Safe Signs, Connect Action]
│
├── 5. CONNECTIONS (Relationship Management)
│   ├── Active Connections (/connections?tab=active)
│   └── Pending Requests (/connections?tab=pending)
│
├── 6. COMPATIBILITY & RELATIONSHIP UNDERSTANDING
│   ├── Synastry Overview (/compare/{target_id}) [Score, 4 Dimensions, Signals]
│   └── Deep-Dive Explanation (/why/{target_id}) [Dynamics, Topics, Starters]
│
├── 7. CONVERSATIONS (Direct Messaging)
│   ├── Conversations List (/conversations)
│   └── Active Chat (/chat/{conversation_id}) [Realtime Messages, Starters Insertion]
│
└── 8. NOTIFICATIONS
    └── Notification Center (/notifications) [Requests, Accepts, Daily Sync]
```

---

## 4. Route Architecture

| Route | Purpose & Required Data | Entry Points | Allowed Actions | Next Destinations | Failure Handling |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`/auth/login`** | Authenticate user via Supabase Auth. | App Launch, Session Expired redirect. | Submit credentials, OAuth login. | `/self/astrology` (if onboarded) or `/onboarding/birth-data`. | Invalid credentials alert. |
| **`/auth/register`** | Create new user account. | `/auth/login`. | Submit email/password. | `/onboarding/birth-data`. | Email already in use error. |
| **`/onboarding/birth-data`** | Collect birth parameters (date, time, precision, tz, location). | Post-registration, incomplete profile. | Set date, toggle precision, select timezone/city, submit. | `/self/astrology`. | Validation error toast; retry on calculation error. |
| **`/self/astrology`** | Display own natal signs, element, and modality. Requires `GET /v1/astrology/profile/safe-astro`. | Bottom Nav ("Self"), Onboarding complete. | View placements, trigger recalculate. | `/self/profile`, `/connections`. | Missing birth data redirects to `/onboarding/birth-data`. |
| **`/self/profile`** | Edit display name, bio, city, occupation, discoverability. Requires `GET /v1/profiles/me`. | `/self/astrology`, Header Avatar. | Edit fields, toggle `is_discoverable`, save. | `/self/astrology`. | Network error toast. |
| **`/people/{id}`** | View discoverable profile and public safe signs. Requires `GET /v1/profiles/{id}` + `GET /v1/astrology/people/{id}/safe-astro`. | Discovery list, Direct deep link. | Send connection request, Block user. | `/compare/{id}` (if accepted), `/connections`. | `404 Not Found` if private or blocked. |
| **`/connections`** | View active connections and incoming/outgoing pending requests. Requires `GET /v1/connections`. | Bottom Nav ("Connections"). | Accept, Decline, Block, Remove, Navigate to Chat/Compare. | `/compare/{id}`, `/chat/{id}`. | Empty state with "Discover People" prompt. |
| **`/compare/{target_id}`** | View normalized compatibility score ($10-98$), 4 dimensions, and top signals. Requires `POST /v1/compare`. | `/connections`, `/people/{id}`, `/chat/{id}`. | View breakdown, Navigate to Why, Start Conversation. | `/why/{target_id}`, `/chat/{conv_id}`. | `403 Forbidden` if not accepted; redirects to connection flow. |
| **`/why/{target_id}`** | Deep-dive relationship dynamics, topics, and conversation starters. Requires `GET /v1/people/{target_id}/why`. | `/compare/{target_id}`. | Copy starter, Send starter to chat, View topic tags. | `/chat/{conv_id}`. | `403 Forbidden` if connection lost. |
| **`/chat/{conversation_id}`** | Realtime direct messaging. Requires `GET/POST /v1/conversations/{id}/messages`. | `/connections`, `/why/{id}`, Notifications. | Send text, insert starter, view connection profile. | `/compare/{target_id}`, `/connections`. | `404 Not Found` if connection blocked or removed. |
| **`/notifications`** | In-app activity feed. Requires `GET/PATCH /v1/notifications`. | Header Bell Icon. | Mark read, Tap notification to navigate. | Deep links to `/connections`, `/chat/{id}`, or `/self/astrology`. | Empty state ("All caught up"). |

---

## 5. User Journey Architecture

```
[Register Account]
       │
       ▼
[Enter Birth Data (Date, Time, Precision, City, Timezone)]
       │
       ▼ (Backend calculates Swiss Ephemeris natal placements)
[Understand Self (/self/astrology: Sun, Moon, Ascendant, Element, Modality)]
       │
       ▼
[Discover People (/people/{id}: View Public Profile & Safe Signs)]
       │
       ▼ (User taps "Connect")
[Connection State = PendingOut]
       │
       ▼ (Target User taps "Accept" on /connections)
[Connection State = Accepted]
       │
       ▼ (User taps "Compare")
[Synastry Engine calculates cross-chart aspects & dimensions]
       │
       ▼
[View Compatibility (/compare/{id}: Score 84.2, Dimensions, Signals)]
       │
       ▼ (User taps "Why This Person")
[Deep Dive (/why/{id}: Mutual dynamics, Topics, Starters)]
       │
       ▼ (User taps "Send Starter to Chat")
[Start Conversation (/chat/{conv_id}: Realtime message dispatch)]
       │
       ▼
[Relationship Maintenance via In-App Notifications & Daily Sync]
```

---

## 6. State Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                              STATE LAYER                               │
├────────────────────────────────────────────────────────────────────────┤
│ 1. GLOBAL AUTH STATE (Persisted in SecureStorage / LocalStorage)       │
│    • session: { access_token, refresh_token, user_id, role }          │
│    • status: "authenticated" | "unauthenticated" | "loading"           │
├────────────────────────────────────────────────────────────────────────┤
│ 2. SERVER QUERY STATE (Managed by Query Cache with TTL & Invalidation) │
│    • user_profile (Key: ["profile", "me"])                             │
│    • safe_astrology (Key: ["astrology", "me"])                         │
│    • connections_list (Key: ["connections"])                           │
│    • compatibility_result (Key: ["compatibility", target_user_id])     │
│    • conversation_messages (Key: ["messages", conversation_id])        │
│    • notifications_list (Key: ["notifications"])                       │
├────────────────────────────────────────────────────────────────────────┤
│ 3. LOCAL UI STATE (Component-Scoped / Non-Persisted)                   │
│    • birth_data_form: { date, time, precision, timezone, coordinates } │
│    • active_connection_tab: "active" | "pending"                       │
│    • chat_input_draft: string                                          │
│    • modal_visibility: { block_confirm, why_drawer }                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 7. API / Data Flow Architecture

```
User Action (e.g. Tap "Accept Connection")
    │
    ▼
UI Component dispatches Mutation
    │
    ▼
HTTP Client Interceptor (Attaches Bearer JWT, handles refresh on 401)
    │
    ▼
FastAPI Backend Endpoint (`POST /v1/connections/{id}/transition`)
    │
    ▼
Database Execution & Validation
    │
    ▼
Response 200 OK -> Normalizes into Typed DTO
    │
    ▼
Query Cache Invalidation (Marks `["connections"]` stale)
    │
    ▼
UI Automatically Re-renders with Updated State
```

---

## 8. Client Caching Strategy

| Resource | Cache Category | Cache Key | Stale Time (TTL) | Invalidation Triggers |
| :--- | :--- | :--- | :--- | :--- |
| **Own Profile** | Query Cache | `["profile", "me"]` | 10 minutes | `PATCH /v1/profiles/me` success. |
| **Own Safe Astrology** | Query Cache | `["astrology", "me"]` | 60 minutes | `POST /profile/recalculate` or birth data update. |
| **Target Safe Astrology** | Query Cache | `["astrology", target_id]` | 30 minutes | Target profile reload or connection change. |
| **Connections List** | Query Cache | `["connections"]` | 30 seconds | Any `/connections/transition` or incoming Realtime event. |
| **Compatibility Result** | Canonical Cache | `["compatibility", target_id]` | 120 minutes | Invalidate if either user's `birth_data_version` bumps. |
| **Chat Messages** | Realtime Cache | `["messages", conv_id]` | Instant / Realtime | Appended immediately on Realtime `INSERT` event. |
| **Notifications** | Realtime Cache | `["notifications"]` | 15 seconds | Updated on `PATCH /notifications/{id}/read` or Realtime alert. |

---

## 9. Realtime Architecture

Realtime updates are powered by **Supabase Realtime WebSockets**:

```
                              ┌─────────────────────────────┐
                              │    Supabase Realtime WSS    │
                              └──────────────┬──────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
       Channel: `public:messages:...`                Channel: `public:notifications:...`
                      │                                             │
                      ▼                                             ▼
        [New Message Event Received]                  [Notification Event Received]
                      │                                             │
                      ▼                                             ▼
    Append to `["messages", conv_id]`              Update unread badge counter +
      cache with deduplication                      invalidate `["notifications"]`
```

### Realtime Lifecycle Rules:
1. **Connect**: Initiated upon entering authenticated shell.
2. **Conversation Channel**: Subscribes to `public:messages:conversation_id=eq.{id}` upon entering `/chat/{id}`.
3. **Unsubscribe / Cleanup**: Destroys conversation channel immediately upon navigating away from chat.
4. **Deduplication**: Messages sent locally via optimistic dispatch use client UUID tracking to prevent duplicate message bubbles when the server broadcast arrives.

---

## 10. Loading / Empty / Error Architecture

```
┌───────────────────────────┐     Loading      ┌───────────────────────────┐
│       INITIALIZING        ├─────────────────►│      SKELETON LOADER      │
└─────────────┬─────────────┘                  └───────────────────────────┘
              │
              │ Data Fetched Successfully
              ▼
┌───────────────────────────┐     No Records   ┌───────────────────────────┐
│     CONTENT AVAILABLE     ├─────────────────►│        EMPTY STATE        │
└─────────────┬─────────────┘                  │ (Custom CTA for each view)│
              │                                └───────────────────────────┘
              │ API Returns Error
              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                             ERROR HANDLER                                │
│  • 401 Unauthorized    ──► Clear Session & Redirect to /auth/login       │
│  • 403 Forbidden       ──► Render "Active Connection Required" State     │
│  • 404 Privacy Not Found──► Render Standard "Profile Not Found" (No Leak)│
│  • 400 Polar Error     ──► Render Friendly Geolocation Warning Modal     │
│  • Network / 500       ──► Render "Retry Connection" Toast Banner        │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Auth Architecture

1. **Token Persistence**: JWT and Refresh Token are stored in OS-secure storage (Keychain/Keystore on mobile, Secure LocalStorage on Web).
2. **Automatic Refresh**: HTTP interceptor intercepts expiring JWTs and requests refreshed credentials from Supabase Auth before dispatching protected API requests.
3. **Logout Cascade**:
   - Clears tokens.
   - Cleans up and disconnects all Realtime WebSocket channels.
   - Wipes all in-memory query caches to guarantee zero data leakage between user sessions on shared devices.

---

## 12. Onboarding Architecture

```
[User Registers] ──► Route Guard checks birth data ──► Redirects to `/onboarding/birth-data`
                                                                  │
┌─────────────────────────────────────────────────────────────────┴──────────────────┐
│                                                                                    │
│  Step 1: Date of Birth (YYYY-MM-DD)                                                │
│  Step 2: Time Precision Toggle: [ Exact | Approximate | Unknown ]                  │
│          • If Exact/Approximate ──► Time Picker (HH:MM)                            │
│          • If Unknown           ──► Time Picker Disabled (Informs: Mean Noon UTC)  │
│  Step 3: Birth City / Location Search (Derives IANA Timezone, Lat, Long)           │
│  Step 4: Review & Confirm Submission                                               │
│                                                                                    │
└─────────────────────────────────┬──────────────────────────────────────────────────┘
                                  │
                                  ▼
                     [Save Birth Data & Trigger Recalculate]
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
              [Calculation 200 OK]       [Polar Error 400]
                     │                         │
                     ▼                         ▼
           Navigate to `/self/astrology`  Show Polar Fallback Alert
```

---

## 13. Relationship Architecture

The frontend renders connection states through explicit action buttons and contextual indicators:

```
┌──────────────┬───────────────────────────────┬───────────────────────────────┐
│ State        │ UI Action Controls            │ Compare & Chat Accessibility  │
├──────────────┼───────────────────────────────┼───────────────────────────────┤
│ **None**     │ [ Connect ] button            │ Disabled (Locked)             │
│ **PendingOut**│ "Request Sent" (Cancel / Block)| Disabled (Locked)             │
│ **PendingIn** │ [ Accept ] [ Decline ] [Block]│ Disabled (Locked)             │
│ **Accepted** │ [ Compare ] [ Chat ] [ Remove]│ ✅ Full Access Enabled        │
│ **Blocked**  │ [ Unblock ] (in Blocked List) │ Disabled (Target Hidden)      │
└──────────────┴───────────────────────────────┴───────────────────────────────┘
```

---

## 14. Compare → Why → Chat Architecture

```
                                  ┌─────────────────────────────┐
                                  │   /compare/{target_user_id} │
                                  │ • Overall Score (84.2)      │
                                  │ • 4 Dimension Gauges        │
                                  │ • Top 6 Signals List        │
                                  └──────────────┬──────────────┘
                                                 │
                                                 │ Tap "Why This Person"
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │     /why/{target_user_id}   │
                                  │ • Deep Dynamics Breakdown   │
                                  │ • Best Topics Tags (Max 4)  │
                                  │ • Conversation Starters(M3) │
                                  └──────────────┬──────────────┘
                                                 │
                                                 │ Tap "Send Starter to Chat"
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │   /chat/{conversation_id}   │
                                  │ • Starter pre-filled in box │
                                  │ • One-tap send into stream  │
                                  └─────────────────────────────┘
```

*Data Efficiency*: `/why/{id}` shares the identical query cache entity as `/compare/{id}`, avoiding redundant API roundtrips.

---

## 15. Responsive Architecture

- **Desktop (Viewport $\ge 1024\text{px}$)**:
  - Persistent left sidebar navigation.
  - Multi-column layout: Connections on the left, Active Chat or Compatibility View in the main panel.
  - Contextual "Why This Person" slides in as an interactive side-drawer.
- **Tablet (Viewport $768\text{px} - 1023\text{px}$)**:
  - Collapsible icon-rail navigation.
  - Two-pane master-detail views for Connections and Messaging.
- **Mobile (Viewport $< 768\text{px}$)**:
  - Persistent bottom tab bar (4 primary tabs: `Discover`, `Connections`, `Chat`, `Self`).
  - Full-screen stacked page transitions for `/compare/{id}`, `/why/{id}`, and `/chat/{id}`.

---

## 16. Privacy Architecture

The frontend enforces strict data boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│                 ALLOWED CLIENT DATA ACCESS                  │
│  • Own Birth Date, Time & Coordinates (Owner View Only)     │
│  • Public Tropical Signs (Sun, Moon, Ascendant)             │
│  • Primary Element & Modality Strings                       │
│  • Computed Compatibility Score & 4 Dimension Values        │
│  • Signal Labels & Starter Text Strings                     │
└─────────────────────────────────────────────────────────────┘
                              ▲
                       STRICT ISOLATION
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 FORBIDDEN CLIENT DATA ACCESS                │
│  • Another User's Raw Birth Coordinates or Birth Time       │
│  • `public.astro_private` Database Tables                   │
│  • Raw Mathematical `evidence_trace` Array                  │
│  • Internal Planet Longitude Floating-Point Values          │
│  • Confirmation of Existence for Blocked Accounts           │
└─────────────────────────────────────────────────────────────┘
```

---

## 17. Backend Gap Assessment

| Gap Identified | Impact on Frontend | Required Backend Work | Status / Workaround |
| :--- | :--- | :--- | :--- |
| **1. `PUT /v1/birth-data`** | Moderate | Add dedicated FastAPI endpoint to persist birth data and trigger natal recalculation in one roundtrip. | **Can begin with PostgREST / Supabase Client SDK in the interim.** |
| **2. Discovery Feed** | High | Add `GET /v1/people/discover?limit=20` to allow general user browsing beyond direct ID search. | **Can begin with direct profile ID lookup & connections list.** |
| **3. Typing & Presence** | Low | Implement Supabase Realtime Presence channel for typing state. | **Frontend can integrate Supabase Presence without DB changes.** |

---

## 18. Architectural Diagrams

### 18.1 Client-Side Application Data Flow
```
User Action (Tap/Type)
         │
         ▼
[UI View Component] ◄──────────────┐
         │                         │
         ▼                         │
[Query Cache / Store] ─────────────┤
         │                         │
         ▼ (Cache Miss / Mutation) │
[API Client Module]                │
         │                         │
         ▼ (Bearer JWT HTTP)       │
[FastAPI /v1 Backend]              │
         │                         │
         ▼                         │
[PostgreSQL DB] ───────────────────┘
```

### 18.2 Realtime Subscription Data Flow
```
[Supabase Realtime WebSocket Server]
         │
         ▼ (New Message / Notification Event)
[Realtime Subscription Manager]
         │
         ▼
[Query Cache Update (Append / Invalidate)]
         │
         ▼
[UI Component Auto-Rerenders in Realtime]
```

---

## 19. Feature Module Structure

The frontend codebase is organized into modular domain packages:

```
frontend/src/
├── core/                  # Network client, Auth interceptor, Storage, Config
├── modules/
│   ├── auth/              # Login, Register, Session Watchdog
│   ├── onboarding/        # Birth data form, Timezone search, Precision toggle
│   ├── self/              # Personal astrology view, Profile editor
│   ├── people/            # Discoverable profile view, Public safe astro cards
│   ├── connections/       # Social graph lists, State transition buttons
│   ├── compatibility/     # Score gauge, 4D charts, Signals, Topics, Starters
│   ├── chat/              # Realtime message thread, Input bar, Starter injection
│   └── notifications/     # In-app alerts list, Badge counter, Realtime toast
├── navigation/            # Router definitions, Auth guards, Deep link handlers
└── shared/                # Layout containers, Error boundaries, Skeletons
```

---

## 20. Architecture Risks & Mitigations

| Identified Risk | Potential Impact | Architecture Mitigation |
| :--- | :--- | :--- |
| **1. Business Logic Duplication** | Inconsistent scoring or orb math between web/mobile and backend. | **Strict Rule**: Zero astrology or scoring calculations in frontend; frontend purely renders server outputs. |
| **2. Stale Compatibility Caches** | Users see outdated compatibility after birth data update. | Backend returns `source_birth_data_version`; frontend invalidates cache when version differs. |
| **3. Realtime Event Duplication** | Double message bubbles displayed when sending chat messages. | Client assigns UUID `client_id` to pending messages, deduplicating upon server ACK. |
| **4. Privacy Leakage** | Exposing raw degrees or blocked user existence. | Strict Pydantic response models on server; frontend error handler treats 404 uniformly. |
| **5. Over-Centralized State** | Excessive re-renders and bloated bundle size. | Separation between Query Cache (server data) and local React component state. |

---

## 21. Implementation Readiness

### ✅ READY NOW (Immediate Frontend Development)
- Authentication flows (`/auth/login`, `/auth/register`).
- Onboarding & birth data collection wizard (`/onboarding/birth-data`).
- Personal astrology profile display (`/self/astrology`).
- Profile viewing and editing (`/self/profile`, `/people/{id}`).
- Social connection management (`/connections`).
- Deterministic compatibility scoring and breakdown (`/compare/{id}`, `/why/{id}`).
- Realtime direct messaging (`/chat/{id}`).
- In-app notification center (`/notifications`).

### ⚠️ PARTIALLY BLOCKED / PENDING BACKEND CONVENIENCES
- Paginated People Discovery feed (`GET /v1/people/discover` endpoint to be added).

### 🔒 DECISIONS FROZEN BEFORE UI/UX DESIGN
1. Compatibility is strictly connection-gated (no comparing strangers).
2. Unknown birth times gracefully hide Ascendant/Houses without erroring.
3. Re-connections after decline/removal have zero cooldown period.
4. Technical `evidence_trace` math is hidden from standard consumer UI.
5. All 5 aspects, 4 dimensions, 6 signals, 4 topics, and 3 starters are fully specified and frozen.
