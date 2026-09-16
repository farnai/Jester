# JESTER FRONTEND DATA MAP
**End-to-End Product Architecture: ME → YOU → US → MORE PEOPLE**  
**Date:** September 2026  
**Auditor:** Senior Backend Architect  

---

## ARCHITECTURAL OVERVIEW

The Jester core product loop follows the strategic growth axiom:
$$\mathbf{ME} \longrightarrow \mathbf{YOU} \longrightarrow \mathbf{US} \longrightarrow \mathbf{MORE\ PEOPLE}$$

This map documents the exact backend endpoints, payloads, response schemas, and UI components available for each stage today.

---

## 1. STAGE 1: ME (Identity & Self-Discovery)

The foundation where the user establishes their identity and discovers their personal astrological dynamics.

```
                  ┌───────────────────────────────┐
                  │          GET /v1/users/me     │
                  │        (Account & Auth Role)  │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
┌───────────────────────────────┐         ┌───────────────────────────────┐
│     GET /v1/profiles/me       │         │ GET /v1/astrology/profile/     │
│   (Display Name, Bio, City)   │         │          safe-astro           │
└───────────────┬───────────────┘         │  (Sun, Moon, Asc, Elem, Mod)  │
                │                         └───────────────┬───────────────┘
                ▼                                         ▼
┌───────────────────────────────┐         ┌───────────────────────────────┐
│    PATCH /v1/profiles/me      │         │POST /v1/astrology/profile/    │
│    (Update Profile Fields)    │         │          recalculate          │
└───────────────────────────────┘         └───────────────────────────────┘
```

### Endpoints & Data Contracts

#### A. Account Identity: `GET /v1/users/me`
* **Purpose:** Confirms caller's authenticated identity and account details.
* **Auth:** Bearer JWT
* **Response Data:**
  ```json
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "email": "user@example.com",
    "role": "authenticated"
  }
  ```
* **Frontend UI Components:** App initialization state, account settings.

#### B. User Profile: `GET /v1/profiles/me` & `PATCH /v1/profiles/me`
* **Purpose:** Retrieves and updates public user attributes. Auto-creates profile with default handle if row does not exist.
* **Auth:** Bearer JWT
* **Response Data:**
  ```json
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "display_name": "Julian",
    "avatar_url": "https://...",
    "bio": "Product builder & nocturnal reader",
    "city": "San Francisco",
    "occupation": "Designer",
    "timezone": "America/Los_Angeles",
    "is_discoverable": true,
    "created_at": "2026-09-01T12:00:00Z",
    "updated_at": "2026-09-02T15:30:00Z"
  }
  ```
* **Frontend UI Components:** User Header Card, Profile Edit Modal, Discovery Visibility Toggle.

#### C. Personal Astrology: `GET /v1/astrology/profile/safe-astro`
* **Purpose:** Retrieves the user's public safe astrology placements. Automatically computes and caches results if birth data is present in database.
* **Auth:** Bearer JWT
* **Response Data:**
  ```json
  {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "sun_sign": "Scorpio",
    "moon_sign": "Cancer",
    "ascendant_sign": "Capricorn",
    "element_primary": "Water",
    "modality_primary": "Fixed",
    "source_birth_data_version": 1,
    "engine_version": "1.0.0",
    "updated_at": "2026-09-01T12:00:00Z"
  }
  ```
* **Frontend UI Components:**
  * **The "Big Three" Card:** Displays Sun, Moon, and Rising signs (or Sun + Moon badge with "Time Unknown" prompt if Rising is null).
  * **Elemental Signature Badge:** Displays Dominant Element (Water, Fire, Earth, Air) and Modality (Cardinal, Fixed, Mutable).

#### D. Birth Data Onboarding / Update
* **Current Backend Note:** Handled via direct Supabase Client (`supabase.from('birth_data').upsert(...)`) with RLS policies, followed by calling `POST /v1/astrology/profile/recalculate` to refresh safe astrology.

### What is Missing in Stage 1 (ME)
* Single-chart natal aspect grid (e.g. "Your Sun trine Jupiter").
* Natal personality traits or narrative archetypes (Interpretation engine is a stub).
* Daily Energy / Day Vibe (transits and endpoints are not implemented).

---

## 2. STAGE 2: YOU (Perceiving Another Person)

When inspecting a potential friend, connection, or collaborator.

```
                   ┌──────────────────────────────────┐
                   │       Discovered Target ID       │
                   └────────────────┬─────────────────┘
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          ▼                                                   ▼
┌──────────────────────────────────┐        ┌──────────────────────────────────┐
│   GET /v1/profiles/{id}          │        │ GET /v1/astrology/people/{id}/   │
│   (Public Profile Details)       │        │            safe-astro            │
│   • 404 if blocked               │        │   • 404 if blocked               │
│   • 404 if is_discoverable=false │        │   • 404 if is_discoverable=false │
└──────────────────────────────────┘        └──────────────────────────────────┘
```

### Endpoints & Data Contracts

#### A. Target Public Profile: `GET /v1/profiles/{profile_id}`
* **Auth:** Bearer JWT
* **Privacy Gate:** Returns `404 Not Found` if target is blocked (either direction) or `is_discoverable == false`.
* **Returned Fields:** `id`, `display_name`, `avatar_url`, `bio`, `city`, `occupation`, `timezone`, `is_discoverable`.
* **Frontend UI Components:** Profile Header, Avatar Badge, Bio Section, Location Tag.

#### B. Target Safe Astrology: `GET /v1/astrology/people/{target_user_id}/safe-astro`
* **Auth:** Bearer JWT
* **Privacy Gate:** Strict privacy isolation. Raw birth dates, times, coordinates, and exact planetary positions are **NEVER** returned. Returns 404 if target is blocked or non-discoverable.
* **Returned Fields:**
  * `sun_sign`
  * `moon_sign`
  * `ascendant_sign` (or null if time unknown)
  * `element_primary`
  * `modality_primary`
* **Frontend UI Components:** Person B "Big Three" Banner, Element/Modality Chips.

### What is Missing in Stage 2 (YOU)
* Target natal chart wheel or house placements.
* Single-person AI psychological summary.

---

## 3. STAGE 3: US (Relationship Dynamics & Synastry)

The core relationship intelligence layer comparing User A and User B.

```
                   ┌──────────────────────────────────┐
                   │        PERSON A + PERSON B       │
                   └────────────────┬─────────────────┘
                                    │
                                    ▼
                   ┌──────────────────────────────────┐
                   │    CRITICAL GATEKEEPER CHECK     │
                   │ public.has_active_connection()   │
                   │ • Both unblocked                 │
                   │ • Status must be 'accepted'      │
                   └────────────────┬─────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
        [ACTIVE CONNECTION]                 [NO ACTIVE CONNECTION]
                  │                                   │
                  ▼                                   ▼
      POST /v1/compare (200 OK)               HTTP 403 FORBIDDEN
    GET /v1/people/{id}/why (200 OK)        "Active connection required"
                  │
                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   STRUCTURED COMPATIBILITY RESPONSE                    │
├────────────────────────────────────────────────────────────────────────┤
│ • Overall Score: 84.2                                                  │
│ • Dimensions: Harmony, Communication, Attraction, Growth               │
│ • Signals: 6 Ranked Relational Dynamics                                │
│ • Best Topics: 4 Curated Shared Intersections                          │
│ • Starters: 3 Tailored Icebreakers                                     │
│ • Data Quality: Precision & Confidence Metric                          │
└────────────────────────────────────────────────────────────────────────┘
```

### Endpoints & Data Contracts

#### A. Compare Users: `POST /v1/compare` or `GET /v1/people/{target_user_id}/why`
* **Auth:** Bearer JWT
* **Request Payload (POST):** `{"target_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}`
* **Response Schema:**
  ```json
  {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "target_user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "score": 88.4,
    "dimensions": {
      "emotional_harmony": 92.1,
      "communication": 84.5,
      "attraction": 89.0,
      "growth_long_term": 76.2
    },
    "signals": [
      {
        "type": "sun_trine_moon",
        "category": "harmony",
        "strength": "high",
        "label": "Emotional Resonance",
        "source_aspects": ["Sun Trine Moon (Orb 1.2°)"]
      },
      {
        "type": "venus_conjunction_mars",
        "category": "attraction",
        "strength": "high",
        "label": "Magnetic Chemistry",
        "source_aspects": ["Venus Conjunction Mars (Orb 0.8°)"]
      }
    ],
    "best_topics": ["art", "music", "psychology", "cinema"],
    "conversation_starters": [
      "What is something that instantly makes you feel understood?",
      "What is your idea of a perfect spontaneous date?",
      "What art or music has inspired you recently?"
    ],
    "data_quality": {
      "time_precision": "exact",
      "confidence": 1.0,
      "houses_used": false,
      "ascendant_used": true
    },
    "engine_version": "synastry-v1.0.0",
    "calculated_at": "2026-09-03T18:00:00Z"
  }
  ```

* **Frontend UI Components:**
  * **Master Compatibility Meter:** Circular radial dial displaying `score` ($10.0$ to $98.0$).
  * **4-Dimensional Spider / Bar Chart:** Visualizing Harmony, Communication, Attraction, and Growth.
  * **Relational Signal Cards:** 6 structured cards with category-coded badge (Harmony=Emerald, Attraction=Amber/Rose, Communication=Sky Blue, Growth=Violet).
  * **Conversation Bridges Drawer:** Best Topics pill tags + Copy-to-Clipboard Icebreaker Starters.
  * **Confidence Pill:** Indicates exact birth time verification.

#### B. Direct Messaging: `/v1/conversations/...`
* `POST /v1/conversations`: Initiates or retrieves 1:1 chat room.
* `GET /v1/conversations/{id}/messages`: Fetches chronological message history.
* `POST /v1/conversations/{id}/messages`: Sends a text message.
* **Gate:** Only permitted between accepted connections.

### What is Missing in Stage 3 (US)
* AI/LLM narrative prose synthesizing the connection in Jester voice.
* Accessing compatibility for non-connected profiles (Gated by 403 Forbidden).

---

## 4. STAGE 4: MORE PEOPLE (Discovery & Social Network)

The viral loop and community discovery layer.

```
                      ME (User)
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
┌────────────────────┐ ┌────────────────────┐
│ POST /connections  │ │  GET /connections  │
│ (Send Request)     │ │  (List My Friends) │
└──────────┬─────────┘ └─────────┬──────────┘
           │                     │
           ▼                     ▼
┌────────────────────┐ ┌────────────────────┐
│ POST /connections/ │ │ GET /notifications │
│  {id}/transition   │ │ (In-App Alerts)    │
│ (Accept / Decline) │ └────────────────────┘
└────────────────────┘
```

### Implemented Capabilities
1. **Connection Lifecycle:**
   * `POST /v1/connections`: Sends connection request (`status = 'pending'`).
   * `POST /v1/connections/{id}/transition`: `accept`, `decline`, `block`, `unblock`, `remove`.
   * Canonical pair enforcement $(A < B)$ ensures only one row exists per pair.
2. **List Connections:** `GET /v1/connections` retrieves all friends and pending requests.
3. **In-App Notifications:** `GET /v1/notifications` alerts users when connection requests are received.

### What is Missing in Stage 4 (MORE PEOPLE)
* **People Feed / Search API:** No endpoint to browse, search, or discover new users in the FastAPI backend.
* **Recommendation Engine:** No backend logic to suggest "high compatibility matches near you".
* **Viral Invite Links / Referral Tracking:** No endpoints to generate custom invite links (`jester.app/invite/XYZ`).
* **Shareable Synastry Cards:** No public unauthenticated URL or OpenGraph preview card endpoint.

---

## 5. SUMMARY TABLE: FRONTEND READINESS MATRIX

| Stage | Product Step | Backend Endpoint | Request | Response Data | Frontend Status | Action Required |
| --- | --- | --- | --- | --- | --- | --- |
| **ME** | View Account | `GET /v1/users/me` | None | `id`, `email`, `role` | **READY** | None |
| **ME** | View Profile | `GET /v1/profiles/me` | None | Profile attributes | **READY** | None |
| **ME** | Edit Profile | `PATCH /v1/profiles/me` | `ProfileUpdate` | Updated profile | **READY** | None |
| **ME** | View Big Three | `GET /v1/astrology/profile/safe-astro` | None | Sun, Moon, Ascendant, Elem, Mod | **READY** | None |
| **ME** | Day Vibe / Daily Energy | None | None | None | **BLOCKED** | Backend job/endpoint needed |
| **YOU** | View Person | `GET /v1/profiles/{id}` | UUID in path | Public profile | **READY** | Requires known user UUID |
| **YOU** | View Person Astro | `GET /v1/astrology/people/{id}/safe-astro` | UUID in path | Safe astrology | **READY** | Block-aware |
| **US** | View Compatibility | `POST /v1/compare` or `GET /people/{id}/why` | Target UUID | Score, dimensions, signals, topics, starters | **GATED** | Requires accepted connection |
| **US** | Deep Aspect Grid | In DB (`evidence_trace`) | Target UUID | Not exposed in schema | **BLOCKED** | Expose field in response model |
| **US** | 1:1 Direct Chat | `/v1/conversations/...` | Message body | Message thread | **READY** | Requires accepted connection |
| **MORE** | Send Friend Request | `POST /v1/connections` | Target UUID | `ConnectionResponse` | **READY** | None |
| **MORE** | Manage Requests | `POST /v1/connections/{id}/transition` | Action | `ConnectionResponse` | **READY** | None |
| **MORE** | Notifications | `GET /v1/notifications` | None | `list[NotificationResponse]` | **READY** | None |
| **MORE** | Browse / Search Feed | None | None | None | **BLOCKED** | Need `/v1/people` endpoint |
| **MORE** | Invite Link / Sharing | None | None | None | **BLOCKED** | Need referral/share endpoints |
