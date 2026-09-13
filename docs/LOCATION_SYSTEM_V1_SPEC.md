# JESTER — Location & Origin System V1
## Canonical Product & Platform Architecture Specification

---

## 1. Core Product Principles

JESTER is a **People Discovery and Relationship Intelligence** platform. It helps people understand themselves, each other, and their relational dynamics.

Location provides essential human context, but:
> **Location provides context; it does not define the person.**  
> **People first. Signals second. Scores last. Privacy by default.**

The platform establishes an absolute architectural distinction between three independent geographic concepts:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         GEOGRAPHIC CONCEPTS IN JESTER                            │
├──────────────────────────┬────────────────────────────┬──────────────────────────┤
│ 1. Current Location      │ 2. Origin / Hometown       │ 3. Exact Coordinates     │
│ ("Where are you based?") │ ("Where are you from?")    │ (GPS / Street / Device)  │
├──────────────────────────┼────────────────────────────┼──────────────────────────┤
│ Operational, social base │ Cultural root & heritage   │ Internal sensitive data  │
│ e.g. Tbilisi, Batumi     │ e.g. Kvareli, Zestafoni    │ Lat/Lon, Device sensors  │
│ Safe Public Profile      │ Safe Public (User-Toggled) │ NEVER Publicly Exposed   │
└──────────────────────────┴────────────────────────────┴──────────────────────────┘
```

### Core Invariants:
1. **Exact location must NEVER be publicly exposed by default.** Coordinates, street addresses, building numbers, and real-time tracking are strictly prohibited from public presentation, public APIs, discovery cards, and unauthenticated endpoints.
2. **Current Location and Hometown must remain decoupled.** "Where are you based?" is not the same as "Where are you from?".
3. **Everyday Location is completely separate from Astrological Birth Place.** Birth place is stored in `public.birth_data` exclusively for Swiss Ephemeris astronomical calculations. It has zero required correlation with where a user currently lives or grew up.
4. **No Creepy Tracking.** JESTER is not a background surveillance or geofencing app. It never continuously tracks GPS in the background.

---

## 2. Location Data Model & Classification

The JESTER V1 Location Model defines clear attributes, storage boundaries, and accessibility rules:

| Field | Type | Storage Domain | Visibility | Requirement | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `current_city_id` | `UUID` | `public.profiles` | Public / Safe | Optional (Recommended) | References canonical `geo_cities.id` |
| `current_country_id` | `UUID` | `public.profiles` | Public / Safe | Derived / Auto | References canonical `geo_countries.id` |
| `current_city_name` | `VARCHAR(100)` | Derived Safe DTO | Public / Safe | Derived | Human-readable city (e.g. "Tbilisi") |
| `current_country_name`| `VARCHAR(100)` | Derived Safe DTO | Public / Safe | Derived | Human-readable country (e.g. "Georgia") |
| `hometown_city_id` | `UUID` | `public.profiles` | Public (Toggled) | Optional | References canonical `geo_cities.id` |
| `hometown_country_id`| `UUID` | `public.profiles` | Public (Toggled) | Derived / Auto | References canonical `geo_countries.id` |
| `hometown_city_name` | `VARCHAR(100)` | Derived Safe DTO | Public (Toggled) | Derived | Human-readable hometown (e.g. "Kvareli") |
| `hometown_country_name`| `VARCHAR(100)` | Derived Safe DTO | Public (Toggled) | Derived | Human-readable country (e.g. "Georgia") |
| `hometown_visible` | `BOOLEAN` | `public.profiles` | Owner Controlled | Required (Def: `true`)| Allows user to hide hometown from profile |
| `location_source` | `ENUM` | `public.profiles` | Internal Only | Required (Def: `manual`)| `'manual'`, `'device'`, `'imported'`, `'system_derived'` |
| `location_updated_at`| `TIMESTAMPTZ` | `public.profiles` | Internal Only | Required (Def: `now()`)| Tracks data freshness for stale checks |
| `timezone` | `VARCHAR(64)` | `public.profiles` | Safe / Internal | Optional | IANA timezone (e.g. `"Asia/Tbilisi"`) |
| `device_latitude` | `DOUBLE PRECISION`| `public.user_location_private` | Service-Only | Deferred / Future | Internal fuzzy distance only; NEVER public |
| `device_longitude` | `DOUBLE PRECISION`| `public.user_location_private` | Service-Only | Deferred / Future | Internal fuzzy distance only; NEVER public |

---

## 3. Current Location vs. Hometown UX

Human relationships thrive on shared spaces and shared roots. JESTER models both dimensions distinctly:

```text
               ┌─────────────────────────────────────────────────┐
               │           PUBLIC PROFILE PRESENTATION           │
               ├─────────────────────────────────────────────────┤
               │  Alexandre, 28                                  │
               │  📍 Based in Tbilisi · 🏡 From Kvareli          │
               │                                                 │
               │  "Product architect into film and trail runs."  │
               └─────────────────────────────────────────────────┘
```

### 3.1 Why Both Are Essential
1. **Current City ("Where are you based?"):**
   - Drives **Discovery relevance** and real-world meeting potential.
   - Establishes daily timezone, social calendar, and local community contexts.
2. **Hometown / Origin ("Where are you from?"):**
   - Adds immediate **conversational warmth and cultural resonance**.
   - Example: Two people living in Tbilisi who both grew up in Kakheti (e.g., Kvareli and Telavi) or Imereti (e.g., Kutaisi and Zestafoni) share an organic cultural connection, childhood nostalgia, and common regional idioms.
   - Provides rich contextual material for **JESTER AI conversation hooks** without feeling invasive or creepy.

### 3.2 Visual Hierarchy & Profile Placement
- **Primary Line:** Current City is always primary: `📍 Tbilisi`.
- **Secondary Descriptor:** Hometown appears as an optional origin tag: `From Kvareli` or `📍 Tbilisi · From Kvareli`.
- **Privacy Toggle:** If `hometown_visible = false`, the profile renders only `📍 Tbilisi`.
- **Cross-Border Display:** If Current Country $\neq$ Hometown Country, countries are explicitly rendered (e.g., `📍 Berlin, Germany · From Tbilisi, Georgia`). For domestic profiles in the same country, city names suffice.

---

## 4. Onboarding UX: Progressive & Low-Friction

JESTER rejects cumbersome multi-step registration forms.

### 4.1 Onboarding Philosophy: "Value Before Effort"
- Location entry is **entirely skippable**.
- Zero mandatory GPS or device location permission prompts on first launch.
- Pre-populated smart chips for primary domestic hubs with instant autocomplete search.

### 4.2 Recommended V1 Onboarding Step
```text
┌────────────────────────────────────────────────────────┐
│                   WHERE ARE YOU BASED?                 │
│                                                        │
│   Select your current city to discover people nearby.  │
│                                                        │
│   [ 🔍 Search city (e.g. Tbilisi, Batumi)...         ] │
│                                                        │
│   Popular:                                             │
│   ( Tbilisi )   ( Batumi )   ( Kutaisi )   ( Rustavi ) │
│                                                        │
│   ──────────────────────────────────────────────────   │
│   WHERE ARE YOU FROM? (OPTIONAL)                       │
│                                                        │
│   [ 🔍 Hometown (e.g. Kvareli, Telavi, Gori)...      ] │
│                                                        │
│   [  Skip for now  ]                     [  Continue ] │
└────────────────────────────────────────────────────────┘
```

### 4.3 Evaluation of UX Alternatives
| Method | Friction | Trust Impact | Accuracy | V1 Recommendation |
| :--- | :---: | :---: | :---: | :--- |
| **City Autocomplete + Chips** | **Very Low** | **High** | High (City-level) | **RECOMMENDED FOR V1** |
| **Mandatory Device GPS** | Extremely High | Very Low (Anxiety) | High (Coordinates) | **REJECTED FOR V1** (Creepy) |
| **Country $\rightarrow$ City Dropdowns**| Medium | Neutral | Moderate | Rejected (Clunky) |
| **Free Text Input** | Low | Low (Dirty Data) | Low (Typos) | Rejected (Breaks Canonical Graph) |
| **Deferred to Profile Edit** | Zero | High | Incomplete | Allowed via "Skip" button |

---

## 5. Precise Location Privacy Invariants

Precise geographic coordinates represent sensitive personal data. JESTER enforces strict architectural boundaries:

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                      PRECISE COORDINATE SECURITY GATES                    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  [ Device GPS Sensors / IP Geolocation ]                                  │
│                      │                                                    │
│                      ▼                                                    │
│  ┌──────────────────────────────────────────────┐                         │
│  │   INTERNAL SERVICE-ROLE / BACKEND ONLY       │                         │
│  │   (Fuzzy distance calculation, if enabled)   │                         │
│  └───────────────────┬──────────────────────────┘                         │
│                      │                                                    │
│                      │ 🚫 HARD SECURITY BOUNDARY                          │
│                      │ NO LAT/LON EVER CROSSES THIS LINE                  │
│                      ▼                                                    │
│  ┌──────────────────────────────────────────────┐                         │
│  │   PUBLIC API / CLIENT DTO / DISCOVERY FEED   │                         │
│  │   - "Tbilisi, Georgia"                       │                         │
│  │   - "Same City" / "Nearby"                   │                         │
│  │   - NEVER: 41.7151, 44.8271                  │                         │
│  │   - NEVER: Street Address or Building Number │                         │
│  └──────────────────────────────────────────────┘                         │
└───────────────────────────────────────────────────────────────────────────┘
```

1. **City-Level Resolution Only:** Public profiles and discovery cards only ever display canonical City and Country names (or regional descriptors such as "Near Tbilisi").
2. **No Coordinate Serialization:** The public API response models (`ProfileResponse`, `DiscoveryPerson`, `ComparePreviewResponse`) must **never** define `latitude`, `longitude`, or `street_address` fields.
3. **No Triangulation Stalking:** When distance metrics are eventually introduced in future versions, distances will be rounded into broad fuzzy bands (e.g. *"In your city"*, *"Within 25 km"*, *"Same region"*), never exact decimal meters (e.g. *"340m away"*), preventing trilateration attacks.

---

## 6. Location in Discovery V1

Discovery in JESTER is fundamentally **multi-dimensional**:

$$\text{Discovery Relevance} = f(\text{Human Profile}, \text{Interest Graph}, \text{Intent}, \text{Social Style}, \mathbf{Location}, \text{Astrology Synergy})$$

Location is **never the sole ranking factor**.

### 6.1 Soft Relevance Signal vs. Hard Filter
- In V1, location acts as a **soft relevance boost**, not a rigid exclusionary wall.
- Users living in the same city receive an organic relevance boost because physical proximity facilitates real-life conversation and friendship.
- However, cross-city connections with extraordinary Interest Graph synergy or profound Synastry V1 harmony remain discoverable.
- An optional user toggle (*"Only show people in my city"*) may be enabled by the user, but the default discovery feed is open and exploratory.

### 6.2 Hometown Overlap in Discovery
When two discoverable users share a hometown root or regional background, JESTER surfaces this as a natural conversational observation on the discovery card:
- *"You're both based in Tbilisi and originally from Kvareli."*
- *"Based in Tbilisi · Shared roots in Kakheti"*

---

## 7. Location Trust & Freshness Model

### 7.1 Minimum Viable Trust Model (V1)
- **Self-Declared with Canonical Resolution:** Users pick from a canonical autocomplete list (`geo_cities`). This guarantees data cleanliness without requiring identity verification or intrusive proof of residence.
- **Verification Decoupling:** Location is self-declared. Identity/Face verification (when implemented) verifies that a person is real; it does not audit their residential address.

### 7.2 Location Freshness & Stale Handling
- Profiles record `location_updated_at`.
- If a user's location has not been updated or confirmed in over **180 days**, the system marks the internal freshness status as `stale`.
- **UX Behavior:** The system will never penalize or publicly shame the user. During an occasional profile review or seasonal app opening, JESTER may show a gentle non-blocking prompt: *"Still based in Tbilisi?"*

---

## 8. Hometown as Human Context for JESTER AI

JESTER AI uses location and origin exclusively as **conversational bridges and cultural warmth**, never as rigid stereotypes.

### 8.1 Safe Context Ingestion
The JESTER AI engine receives sanitized location tokens:
```json
{
  "viewer": {
    "current_city": "Tbilisi",
    "current_country": "Georgia",
    "hometown": "Kvareli"
  },
  "target": {
    "current_city": "Tbilisi",
    "current_country": "Georgia",
    "hometown": "Zestafoni"
  },
  "relational_flags": {
    "is_same_current_city": true,
    "is_same_hometown": false,
    "is_same_country": true,
    "hometown_overlap_type": "different_regions"
  }
}
```

### 8.2 AI Operational Invariants
1. **No Regional Stereotyping:** The AI must never invoke derogatory, clichéd, or deterministic cultural tropes based on hometowns (e.g., never generate statements like *"People from X are always stubborn"*).
2. **Contextual Observation, Not Interrogation:** Hometown context should be used as a conversational spark (e.g. *"You're both making a life in Tbilisi, but carry roots from different corners of Georgia"*), not an intrusive background check.
3. **Strict Zero-Coordinate Boundary:** AI system prompts and user payloads must **never** contain raw GPS coordinates or private travel traces.

---

## 9. Astrology Interaction & System Boundary

The platform strictly isolates everyday geographic residency from astrological birth calculations:

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                    SEPARATION OF ASTRONOMY AND SOCIAL DATA                │
├───────────────────────────────────┬───────────────────────────────────────┤
│ Social Profile Location           │ Astrological Birth Data               │
│ (`public.profiles`)               │ (`public.birth_data`)                 │
├───────────────────────────────────┼───────────────────────────────────────┤
│ - Current City: "Tbilisi"         │ - Birth Place: "Kutaisi"              │
│ - Hometown: "Kvareli"             │ - Coordinates: 42.2679° N, 42.6946° E │
│ - Purpose: Social connection,     │ - Purpose: Swiss Ephemeris Julian Day │
│   discovery relevance, human      │   and planetary topocentric cusps     │
│   context, and conversation       │                                       │
│ - Visibility: Safe Public         │ - Visibility: OWNER-ONLY (Private)    │
│ - Mutability: Editable anytime    │ - Mutability: Fixed birth event       │
└───────────────────────────────────┴───────────────────────────────────────┘
```

A user born in Kutaisi, raised in Kvareli, and currently working in Tbilisi has three distinct, non-conflicting records in JESTER. Updating current city to "Batumi" has zero effect on the user's natal chart.

---

## 10. Database Schema Specification (Architecture Blueprint)

To ensure high performance, clean relational queries, and international readiness, JESTER implements canonical geographic reference entities.

```sql
-- ============================================================================
-- 1. CANONICAL COUNTRIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.geo_countries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    iso_code VARCHAR(2) NOT NULL UNIQUE,       -- 'GE', 'DE', 'US', etc.
    name_en VARCHAR(100) NOT NULL,              -- 'Georgia'
    name_ka VARCHAR(100) NOT NULL,              -- 'საქართველო'
    phone_code VARCHAR(10),                     -- '+995'
    flag_emoji VARCHAR(10),                     -- '🇬🇪'
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 2. CANONICAL CITIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.geo_cities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES public.geo_countries(id) ON DELETE RESTRICT,
    name_en VARCHAR(100) NOT NULL,              -- 'Tbilisi'
    name_ka VARCHAR(100) NOT NULL,              -- 'თბილისი'
    slug VARCHAR(120) NOT NULL UNIQUE,          -- 'ge-tbilisi'
    region_en VARCHAR(100),                     -- 'Tbilisi'
    region_ka VARCHAR(100),                     -- 'თბილისი'
    latitude DOUBLE PRECISION NOT NULL,         -- Canonical City Center (Approximate)
    longitude DOUBLE PRECISION NOT NULL,        -- Canonical City Center (Approximate)
    timezone VARCHAR(64) NOT NULL,              -- 'Asia/Tbilisi'
    is_major_hub BOOLEAN DEFAULT false,         -- For quick onboarding chips
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 3. CANONICAL CITY ALIASES (Search & Normalization)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.geo_city_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city_id UUID NOT NULL REFERENCES public.geo_cities(id) ON DELETE CASCADE,
    alias VARCHAR(100) NOT NULL,                -- 'Tiflis', 'ტფილისი'
    locale VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 4. PROFILE TABLE EXTENSION (Location & Origin Columns)
-- ============================================================================
-- Alter public.profiles to link canonical references:
ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS current_city_id UUID REFERENCES public.geo_cities(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS current_country_id UUID REFERENCES public.geo_countries(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS hometown_city_id UUID REFERENCES public.geo_cities(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS hometown_country_id UUID REFERENCES public.geo_countries(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS hometown_visible BOOLEAN NOT NULL DEFAULT true,
    ADD COLUMN IF NOT EXISTS location_source VARCHAR(30) NOT NULL DEFAULT 'manual',
    ADD COLUMN IF NOT EXISTS location_updated_at TIMESTAMPTZ DEFAULT now();

CREATE INDEX IF NOT EXISTS idx_profiles_current_city ON public.profiles(current_city_id) WHERE is_discoverable = true;
CREATE INDEX IF NOT EXISTS idx_profiles_hometown_city ON public.profiles(hometown_city_id) WHERE is_discoverable = true;
```

---

## 11. API Specification & Safe DTOs

### 11.1 Safe Public Profile Serialization
Public profiles and discovery cards serialize clean, non-sensitive location objects:

```json
{
  "id": "7a3e8b42-1234-4567-89ab-cdef01234567",
  "display_name": "Mariam",
  "avatar_url": "https://cdn.jester.app/avatars/mariam.webp",
  "bio": "Curious explorer, classical pianist, espresso enthusiast.",
  "location": {
    "city": "Tbilisi",
    "country": "Georgia",
    "country_code": "GE"
  },
  "origin": {
    "city": "Kvareli",
    "country": "Georgia",
    "country_code": "GE"
  },
  "is_discoverable": true
}
```

If `hometown_visible` is false, `"origin"` is serialized as `null`.  
Exact coordinates (`latitude`, `longitude`) are **never serialized** in public endpoints.

---

## 12. Security & Privacy Policy Additions

The following security constraints govern location data across the platform:

1. **`geo_countries`, `geo_cities`, `geo_city_aliases`:**
   - Public read access (`SELECT`) granted to `anon` and `authenticated` roles for onboarding city search.
   - Insert/Update/Delete strictly restricted to `service_role` and admin tooling.
2. **`public.profiles` Location Columns:**
   - Authenticated users may update their own location (`current_city_id`, `hometown_city_id`, `hometown_visible`) where `id = auth.uid()`.
   - Read access follows profile discovery rules (only discoverable, unblocked users are visible).
3. **No Exact Coordinate Leakage:**
   - Raw coordinates are restricted to internal background tasks. No client role has read access to exact device coordinate logs.
4. **Log & Telemetry Sanitization:**
   - API access logs, telemetry events, and client analytics must **never** record raw GPS coordinates. Only canonical city IDs and slugs may be tracked.

---

## 13. Scope Boundary: V1 vs. Future Roadmap

| Capability | In V1 | Deferred to Future | Rationale |
| :--- | :---: | :---: | :--- |
| **Self-Declared Current City** | ✅ | — | Core profile context |
| **Self-Declared Hometown / Origin** | ✅ | — | Cultural warmth and AI conversation context |
| **Hometown Privacy Toggle** | ✅ | — | User control over personal background |
| **Canonical City Autocomplete** | ✅ | — | Data cleanliness & i18n support |
| **Same-City Discovery Boost** | ✅ | — | Soft relevance for meeting people |
| **Hometown Commonality Observation**| ✅ | — | Contextual AI discovery hook |
| **Fuzzy Distance ("Within 25 km")** | ❌ | 🔮 | Requires high user density to be meaningful |
| **Live Device GPS Tracking** | ❌ | 🚫 | Invasive; violates privacy-first principle |
| **Interactive Discovery Map** | ❌ | 🔮 | High complexity, visual distraction in V1 |
| **Temporary "Travel / Visiting" Mode**| ❌ | 🔮 | Valuable post-launch feature for travelers |
| **Geofenced Local Events / Spaces** | ❌ | 🔮 | Community feature for future roadmap |

---

## 14. UX States & Edge Cases

1. **No Location Added (Skipped during Onboarding):**
   - Profile renders without location badges. Discovery displays candidate based on Interest Graph synergy and safe astrology.
2. **Current City Only (No Hometown Provided):**
   - Renders cleanly as `📍 Tbilisi`.
3. **Current City + Hometown:**
   - Renders as `📍 Based in Tbilisi · 🏡 From Kvareli`.
4. **Hometown Hidden by User (`hometown_visible = false`):**
   - Only `📍 Tbilisi` is visible to other users. Origin remains stored for user's personal review and can be re-enabled anytime.
5. **Cross-Country Residency:**
   - Renders full country context: `📍 Berlin, Germany · 🏡 From Tbilisi, Georgia`.
6. **City Change / Relocation:**
   - Updating `current_city_id` updates discovery relevance immediately without altering hometown or historical astrology data.
7. **Permission Denied (Device Location):**
   - If device location is ever requested in future versions, denial seamlessly defaults to standard city autocomplete with zero nag dialogs.

---

## 15. Analytics & Telemetry Events

Minimal, privacy-safe events to measure onboarding friction and feature adoption:

- `location_step_viewed`: Onboarding location screen shown.
- `location_city_selected`: User selected a canonical city (`city_id`, `source: 'chip' | 'search'`).
- `location_hometown_selected`: User selected an origin city (`city_id`).
- `location_skipped`: User clicked skip on the location onboarding step.
- `location_updated`: Existing user updated current city from profile settings.
- `hometown_visibility_toggled`: User switched hometown visibility on/off (`is_visible: boolean`).

*Strict Rule: Analytics events must never log device latitude, longitude, or IP addresses.*

---

## 16. Location System V1 — Final Decisions Summary

| Area | V1 Architecture Decision |
| :--- | :--- |
| **Current Location** | Self-declared canonical city (`current_city_id` references `geo_cities`). Visible on profile. |
| **Hometown / Origin** | Self-declared canonical city (`hometown_city_id` references `geo_cities`). Decoupled from current city. |
| **Birth Place** | Strictly private astronomical calculation data in `public.birth_data`. Completely decoupled from profile location. |
| **Exact GPS Coordinates** | NEVER publicly exposed. Not collected in V1. No real-time tracking. |
| **Public Visibility** | Current City is public. Hometown is public by default but toggleable (`hometown_visible`). |
| **Discovery Influence** | Soft relevance boost for same-city users. Contextual hook for shared hometown roots. No hard exclusionary filters. |
| **Onboarding UX** | Highly progressive: skippable, 1-tap popular city chips (Tbilisi, Batumi, etc.) + search autocomplete. Zero GPS prompts. |
| **Verification** | Unverified in V1 (self-declared). Location is decoupled from Face/Identity verification. |
| **Freshness** | Monitored via `location_updated_at`. Stale after 180 days with gentle, non-blocking check-in prompt. |
| **Database Architecture**| Normalized reference tables (`geo_countries`, `geo_cities`, `geo_city_aliases`). Profile holds canonical foreign keys. |
| **API Contract** | Safe structured objects: `location: { city, country }` and `origin: { city, country }`. Zero coordinates in client DTOs. |
| **AI Context** | Ingests safe city/country names and relational flags. Strict prohibition against regional stereotyping or stalkerish comments. |
| **Security Policy** | Enforced least privilege: client privileges revoked from raw coordinates; analytics sanitized; no existence oracles. |
| **V1 Scope** | City/Country level for Current Location and Hometown. Autocomplete search. Soft discovery signals. |
| **Future Scope** | Fuzzy distance bands, travel mode, local community hubs, geofenced activities. |
