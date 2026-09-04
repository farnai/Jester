# JESTER BACKEND CAPABILITY AUDIT
**Authoritative Product & Technical Capability Extraction for Frontend Architecture**  
**Date:** September 2026  
**Auditor:** Senior Backend Architect & Product Capability Auditor  
**Audit Scope:** Source Code (`backend/app/`), Database Migrations (`supabase/migrations/`), Schemas, Services, Calculations, API Endpoints, and Test Suite (`tests/`).

---

## EXECUTIVE SUMMARY & AUDIT RULES

This audit is a strict, factual inventory of the Jester backend as it exists today. It adheres to the primary repository rule: **Source-of-truth hierarchy prioritizes actual code and database migrations above all documentation or hypothetical designs.**

### Audit Status Definitions:
* **IMPLEMENTED:** Code, route, service, and database persistence are fully operational and verified by automated tests.
* **PARTIALLY IMPLEMENTED:** Partial logic or schema exists, but key pipeline components (e.g. API route exposure, calculation logic, or storage) are missing or stubbed.
* **DEFINED BUT NOT IMPLEMENTED:** Data models, Pydantic schemas, or stub functions exist with no functional implementation.
* **NOT FOUND:** No code, route, schema column, or logic exists in the repository.
* **UNKNOWN:** Insufficient evidence in the codebase to confirm exact behavior.

---

## SECTION A: THE CURRENT USER / ME

This section details what the backend can calculate, persist, and return about the authenticated caller.

### 1. Birth Data
* **Status:** IMPLEMENTED in Database (PostgREST / Direct DB); NOT EXPOSED via a dedicated FastAPI endpoint.
* **Storage Table:** `public.birth_data`
* **Fields Stored:** `birth_date` (DATE), `birth_time` (TIME, nullable), `birth_time_precision` (ENUM: `'exact'`, `'approximate'`, `'unknown'`), `birth_timezone` (TEXT, IANA), `latitude` (FLOAT, nullable), `longitude` (FLOAT, nullable), `place_label` (TEXT, nullable), `data_version` (INT, default 1).
* **Validation Service:** `backend.app.astrology.validation.validate_birth_data`
  * Checks: Date between 1900-01-01 and today; valid IANA timezone; precision consistency (time null if unknown, time present if exact/approximate); lat [-90, 90], lon [-180, 180].
* **Backend Source:** Read internally by `backend.app.astrology.natal.recalculate_user_astrology` and `backend.app.comparisons.router.compare_users`.
* **FastAPI Exposure:** There is **NO** `POST /v1/birth-data` or `GET /v1/birth-data` endpoint in FastAPI. Authentication and storage for birth data rely on Supabase direct client via RLS (`birth_data_select_own`, `birth_data_insert_own`, `birth_data_update_own`).
* **Deterministic vs LLM:** Deterministic database storage and version tracking.

### 2. Natal Chart & Planetary Placements
* **Status:** IMPLEMENTED (Calculated server-side and stored in `public.astro_private`; strictly isolated from clients).
* **Storage Table:** `public.astro_private`
* **Calculation Service:** `backend.app.astrology.calculator.compute_natal_placements`
  * Swiss Ephemeris (`pyswisseph` / `swe.calc_ut`) with `FLG_SWIEPH | FLG_SPEED`.
  * Computes exact tropical ecliptic longitude (rounded to 6 decimal places) and retrograde status (`speed_lon < 0.0`) for **10 celestial bodies**: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto.
  * Julian Day calculation: local time converted to UTC via `zoneinfo.ZoneInfo`; if `birth_time_precision == 'unknown'`, uses 12:00 UTC mean noon.
* **Client Exposure:** **REVOKE ALL** for `authenticated` and `anon`. Exact planet longitudes are NEVER sent to the client.
* **Deterministic vs LLM:** 100% deterministic Swiss Ephemeris mathematical calculation.

### 3. Houses & Ascendant
* **Status:** IMPLEMENTED with strict precision rules (Internal storage in `public.astro_private`).
* **Calculation Service:** `swe.houses(jd, lat, lon, b'P')` (Placidus system).
* **Rules:**
  * If `birth_time_precision == 'unknown'` or latitude/longitude is NULL: Ascendant longitude and Houses are strictly set to `None`.
  * If latitude $> 66.5^\circ$ (polar regions): Raises `placidus_polar_error` (HTTP 400).
  * Houses stored as JSONB array of 12 cusp longitudes in degrees in `astro_private`.
* **Client Exposure:**
  * Exact Ascendant longitude: Server-side only (`astro_private`).
  * Derived Ascendant Zodiac sign: Exposed publicly via `astro_safe_profile` (or `None` if unknown time).
  * Natal House cusps: **NOT EXPOSED** in any client API.
* **Deterministic vs LLM:** 100% deterministic.

### 4. Zodiac Signs
* **Status:** IMPLEMENTED.
* **Calculation Service:** `backend.app.astrology.calculator.longitude_to_sign`
  * Normalized longitude $[0, 360) \div 30.0$ mapped to 12 signs: Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces.
* **Client Exposure:**
  * `sun_sign` (e.g. `"Aries"`)
  * `moon_sign` (e.g. `"Scorpio"`)
  * `ascendant_sign` (e.g. `"Leo"` or `null`)
  * Exposed via `GET /v1/astrology/profile/safe-astro` and `POST /v1/astrology/profile/recalculate`.
* **Deterministic vs LLM:** Deterministic.

### 5. Dominant Elements & Dominant Modalities
* **Status:** IMPLEMENTED.
* **Calculation Service:** `backend.app.astrology.calculator.derive_primary_element_and_modality`
  * Weighted formula across personal placements:
    * Sun: Weight 3
    * Moon: Weight 3
    * Ascendant: Weight 3 (if present)
    * Mercury: Weight 2
    * Venus: Weight 2
    * Mars: Weight 2
  * Elements: Fire, Earth, Air, Water
  * Modalities: Cardinal, Fixed, Mutable
  * Selects the single most common element and modality via `Counter.most_common(1)`.
* **Client Exposure:**
  * `element_primary` (e.g. `"Fire"`)
  * `modality_primary` (e.g. `"Cardinal"`)
  * Exposed in `SafeDerivedAstrologyResponse` via `GET /v1/astrology/profile/safe-astro`.
* **Deterministic vs LLM:** Deterministic.

### 6. Natal Aspects (Single User)
* **Status:** PARTIALLY IMPLEMENTED (Aspect calculation engine exists in `backend.app.astrology.aspects`, but it is ONLY utilized in synastry cross-charts, NOT exposed for a single user's natal chart).
* **Available Engine:** `aspects.py` supports Conjunction ($0^\circ$), Sextile ($60^\circ$), Square ($90^\circ$), Trine ($120^\circ$), Opposition ($180^\circ$) with orb expansions and quadratic decay.
* **Endpoint / Single Chart Service:** **NOT FOUND**. There is no endpoint or function that runs natal aspect detection solely on User A's chart.
* **Frontend Can Use Now?:** NO.

### 7. Personality-Related Signals (Single User)
* **Status:** NOT IMPLEMENTED for single users.
* **Notes:** Signals are only extracted for relationship pairs (synastry) via `backend.app.compatibility.rules`. There are no single-chart personality archetype or trait signal generators.
* **Frontend Can Use Now?:** NO.

### 8. Current Sky & Transits
* **Status:** NOT IMPLEMENTED.
* **File:** `backend/app/astrology/transits.py` contains only a 4-line docstring stub: `"""\nTransit calculations for Daily Energy.\n"""`.
* **Endpoints:** None.
* **Frontend Can Use Now?:** NO.

### 9. Daily Energy / Daily Signals (Single User)
* **Status:** DEFINED BUT NOT IMPLEMENTED (Stub only).
* **Storage Table:** `public.daily_energies` (`user_id`, `energy_date`, `signals` JSONB, `interpretation` JSONB, `engine_version`).
* **Code:** `backend/app/jobs/daily_energy.py` has a stub `generate_daily_energy_for_user()` that inserts hardcoded empty signals (`'[]'::jsonb`) and a static string (`'{"summary": "A dynamic day for creative exploration."}'::jsonb`).
* **API Route:** **NOT FOUND**. No FastAPI route exists to retrieve daily energy.
* **Frontend Can Use Now?:** NO.

### 10. Existing Interpretations & AI / LLM Output (Single User)
* **Status:** NOT IMPLEMENTED (Empty stubs).
* **Files:**
  * `backend/app/interpretation/engine.py` (empty)
  * `backend/app/interpretation/jester.py` (empty)
  * `backend/app/interpretation/prompts.py` (empty)
  * `backend/app/interpretation/models.py` (defines `JesterMessageRequest` and `JesterMessageResponse`, but they are unused)
* **Router:** Not mounted in `api_router`.
* **Frontend Can Use Now?:** NO.

---

## SECTION B: ANOTHER PERSON / YOU

What the backend supports when querying or inspecting another person.

### 1. Profile Data Available
* **Status:** IMPLEMENTED.
* **Endpoint:** `GET /v1/profiles/{profile_id}`
* **Security / Permissions:**
  * Requires valid JWT Bearer token.
  * Calls DB helper `public.is_user_blocked(current_user.id, profile_id)`. If either user blocked the other, raises `404 PrivacySafeNotFoundException`.
  * Verifies `is_discoverable = true` on the target profile. If `false` and caller is not the owner, raises `404 PrivacySafeNotFoundException`.
* **Public Profile Fields Returned:**
  * `id` (UUID)
  * `display_name` (string)
  * `avatar_url` (string or null)
  * `bio` (string or null)
  * `city` (string or null)
  * `occupation` (string or null)
  * `timezone` (string)
  * `is_discoverable` (boolean)
  * `created_at` (datetime)
  * `updated_at` (datetime)
* **Frontend Can Use Now?:** YES.

### 2. Astrology Data Available for Another Person
* **Status:** IMPLEMENTED (Safe derived view only).
* **Endpoint:** `GET /v1/astrology/people/{target_user_id}/safe-astro`
* **Security / Permissions:**
  * Requires valid JWT Bearer token.
  * Checks mutual block via `is_user_blocked()`; returns 404 if blocked.
  * Checks `is_discoverable` on target profile; returns 404 if false.
* **Fields Returned:**
  * `user_id` (UUID)
  * `sun_sign` (string, e.g. `"Aries"`)
  * `moon_sign` (string, e.g. `"Scorpio"`)
  * `ascendant_sign` (string or null, e.g. `"Leo"`)
  * `element_primary` (string, e.g. `"Fire"`)
  * `modality_primary` (string, e.g. `"Cardinal"`)
  * `source_birth_data_version` (integer)
  * `engine_version` (string, e.g. `"1.0.0"`)
  * `updated_at` (datetime)
* **Birth Data Exposure:** Raw birth date, time, timezone, latitude, longitude, and exact planetary coordinates are **STRICTLY HIDDEN**. Only derived signs and dominant element/modality are exposed.
* **Frontend Can Use Now?:** YES.

### 3. People Discovery & User Search
* **Status:** NOT IMPLEMENTED in FastAPI backend.
* **Endpoints Tested/Inspected:**
  * `GET /v1/profiles` (list / search): **NOT FOUND**.
  * `GET /v1/people` (discovery feed): **NOT FOUND**.
  * Filter by sign, element, location, or distance: **NOT FOUND**.
  * Nearby people / geolocation search: **NOT FOUND**.
  * Recommendations / matching engine: **NOT FOUND**.
* **Database / PostgREST Capability:** In Supabase RLS, `profiles` table allows `SELECT` for authenticated users where `is_discoverable = true AND NOT is_user_blocked()`. Therefore, direct PostgREST querying from Supabase client could fetch discoverable profiles, but the FastAPI backend provides no discovery or search endpoints.
* **Frontend Can Use Now?:** Only by fetching a known `profile_id` via `GET /v1/profiles/{profile_id}`.

### 4. Comparing Two Users (ME + YOU)
* **Status:** IMPLEMENTED, **BUT RESTRICTED TO ACCEPTED CONNECTIONS**.
* **Endpoints:**
  * `POST /v1/compare` (Payload: `{"target_user_id": "<UUID>"}`)
  * `GET /v1/people/{target_user_id}/why` (URL path parameter)
* **Critical Gatekeeper Restriction:**
  * The backend explicitly executes:
    `SELECT public.has_active_connection(user_a, user_b) as is_active;`
  * If `is_active` is false (meaning no connection exists, or status is `'pending'`, `'declined'`, `'blocked'`, or `'removed'`), the endpoint raises:
    `403 ForbiddenException: "Active connection required to view compatibility"`.
  * **Consequence for Frontend:** A user **CANNOT** view compatibility, scores, or why-breakdowns for a stranger or a discovered user before sending a connection request and having that person accept it!

---

## SECTION C: SYNASTRY / RELATIONSHIP ANALYSIS / US

Jester V1 contains a mathematical Synastry Engine (`synastry-v1.0.0`) implemented in `backend/app/compatibility/`.

### 1. Architectural Pipeline: PERSON A + PERSON B
```text
PERSON A (astro_private) + PERSON B (astro_private)
    │
    ├─► Aspect Detection: 10x10 Cross-aspects (Ptolemaic aspects, orbs, quadratic strength decay)
    ├─► Multi-Dimensional Calculations:
    │     ├── Emotional Harmony (Trines, Sextiles, Conjunctions, Sun-Moon, Elemental harmony)
    │     ├── Communication (Mercury aspects, Air synergy, Mercury element match)
    │     ├── Attraction (Venus-Mars, Sun-Moon, Venus-Pluto, Oppositions, Fire/Air count)
    │     └── Growth & Long-Term (Saturn aspects, Squares, Oppositions, Modality balance)
    ├─► Planetary Influence Caps (+-18.0 per pair, +12.0 outer planet limit)
    ├─► Overall Score: Weighted combination (30% Harmony + 30% Attraction + 20% Comm + 20% Growth)
    ├─► Curve Stretch: Centered power stretch (^0.85), clamped [10.0, 98.0]
    ├─► Signal Extraction: Top 6 ranked relational signals
    ├─► Bridge Topics: Up to 4 conversation topics based on dominant element/aspect
    ├─► Conversation Starters: Up to 3 tailored icebreaker questions
    └─► Evidence Trace: Complete mathematical breakdown of all detected cross-aspects
```

### 2. Available Synastry Outputs

#### Output 1: Overall Compatibility Score
* **Name:** `score`
* **Meaning:** Overall relationship dynamic index on a 10.0 to 98.0 scale. (65.0 represents baseline/neutral or insufficient aspect evidence).
* **Input Data:** Longitudes of 10 planets + Ascendants (if known) for Person A and Person B.
* **Calculation Method:** Deterministic weighted formula:
  $$\text{Raw} = 0.30 \times S_{\text{harmony}} + 0.30 \times S_{\text{attraction}} + 0.20 \times S_{\text{communication}} + 0.20 \times S_{\text{growth}}$$
  Followed by non-linear curve stretching: $\text{Centered} = (\text{Raw} - 50) / 50$; $\text{Stretched} = 50 + 50 \times \text{sign} \times |\text{Centered}|^{0.85}$.
* **Endpoint / Response Field:** `POST /v1/compare` -> `score` (float, e.g. `84.2`).
* **Deterministic:** 100% deterministic.
* **Interpretation / LLM:** None. Pure numeric score.
* **Status:** IMPLEMENTED.

#### Output 2: Relational Dimensions (4 Subscores)
* **Name:** `dimensions`
* **Meaning:** Four discrete subscores measuring specific relational facets:
  1. `emotional_harmony`: Emotional resonance, comfort, shared vulnerability (driven by Sun-Moon, Moon-Moon, Moon-Venus, elemental water/earth harmony).
  2. `communication`: Mental alignment, intellectual flow, conversational ease (driven by Mercury-Mercury, Mercury aspects, air synergy).
  3. `attraction`: Chemistry, magnetic spark, polarity (driven by Venus-Mars, Sun-Moon, Venus-Pluto, fire/air counts).
  4. `growth_long_term`: Structural endurance, dynamic friction, ambition (driven by Saturn connections, squares, oppositions, modality balance).
* **Endpoint / Response Field:** `POST /v1/compare` -> `dimensions` (dict: `{"emotional_harmony": 82.1, "communication": 74.5, "attraction": 88.0, "growth_long_term": 69.2}`).
* **Important Router Bug/Gotcha:** When a cached result is retrieved from `public.compatibility_results`, the table does NOT have a `dimensions` column (only `score`, `signals`, `best_topics`, `conversation_starters`, `evidence_trace`). The router currently fails to repopulate `dimensions` on cache hit, returning `{}`! On fresh calculation, `dimensions` is returned properly.
* **Deterministic:** 100% deterministic.
* **Status:** IMPLEMENTED in calculation; PARTIALLY IMPLEMENTED in API cache retrieval.

#### Output 3: Structured Compatibility Signals
* **Name:** `signals`
* **Meaning:** Up to 6 ranked qualitative relational indicators.
* **Fields per signal:**
  * `type` (string, e.g. `"venus_conjunction_mars"`, `"sun_trine_moon"`, `"mars_square_saturn"`)
  * `category` (string: `"harmony"`, `"attraction"`, `"communication"`, `"growth"`, `"stability"`, or `"notice"`)
  * `strength` (string: `"high"` or `"medium"`)
  * `source_aspects` (list of strings, e.g. `["Venus Conjunction Mars (Orb 1.4°)"]`)
  * `label` (human-readable title, e.g. `"Magnetic Chemistry"`, `"Emotional Resonance"`, `"Pacing Tension"`)
* **Endpoint / Response Field:** `POST /v1/compare` -> `signals` (list of dicts).
* **Deterministic:** 100% deterministic rule-based mapping from `SIGNAL_DEFINITIONS` in `rules.py`.
* **Interpretation / LLM:** Static rule-based label and category. No LLM generation.
* **Status:** IMPLEMENTED.

#### Output 4: Best Conversation Topics
* **Name:** `best_topics`
* **Meaning:** 4 shared interest topics inferred from elemental synergy and dominant aspect patterns.
* **Domain Values:** Inferred from 4 pools:
  * Air/Mercury dominant: `["books", "philosophy", "ideas", "creative_work"]`
  * Fire/Mars dominant: `["travel", "adventure", "fitness", "ambition"]`
  * Water/Moon/Venus dominant: `["art", "music", "psychology", "cinema"]`
  * Earth/Saturn dominant: `["architecture", "food", "design", "lifestyle"]`
* **Endpoint / Response Field:** `POST /v1/compare` -> `best_topics` (list of 4 strings).
* **Deterministic:** 100% deterministic.
* **Status:** IMPLEMENTED.

#### Output 5: Conversation Starters
* **Name:** `conversation_starters`
* **Meaning:** Up to 3 curated icebreaker questions mapped directly to the pair's top active astrological signals.
* **Examples:**
  * For `sun_trine_moon`: `"What is something that instantly makes you feel understood?"`
  * For `venus_conjunction_mars`: `"What is your idea of a perfect spontaneous date?"`
  * For `mercury_trine_mercury`: `"What topic could you talk about for hours without getting bored?"`
  * Fallbacks if fewer than 3 signals match: `"What is your favorite way to spend an inspiring afternoon?"`, etc.
* **Endpoint / Response Field:** `POST /v1/compare` -> `conversation_starters` (list of 3 strings).
* **Deterministic:** 100% deterministic template dictionary lookup.
* **Status:** IMPLEMENTED.

#### Output 6: Data Quality & Confidence Indicators
* **Name:** `data_quality`
* **Fields:**
  * `time_precision`: `"exact"`, `"approximate"`, or `"unknown"` (worst-case of the two users)
  * `confidence`: `1.0` (both exact), `0.85` (at least one approximate), `0.75` (at least one unknown), `0.50` (insufficient aspect evidence)
  * `houses_used`: `false` (in Synastry V1, houses are never used in synastry math)
  * `ascendant_used`: `true` only if both users have known birth times and calculated Ascendants
* **Endpoint / Response Field:** `POST /v1/compare` -> `data_quality` (dict).
* **Status:** IMPLEMENTED.

#### Output 7: Evidence Trace (All Cross-Aspects & Subscore Math)
* **Name:** `evidence_trace`
* **Meaning:** The exact, comprehensive audit trail of every active aspect between Person A and Person B.
* **Data Fields per Item:**
  * `planet_a` (string, e.g. `"sun"`)
  * `planet_b` (string, e.g. `"moon"`)
  * `lon_a` (float, e.g. `24.52`)
  * `lon_b` (float, e.g. `144.18`)
  * `aspect` (string: `"trine"`, `"conjunction"`, `"sextile"`, `"square"`, `"opposition"`)
  * `target_angle` (float: `0.0`, `60.0`, `90.0`, `120.0`, `180.0`)
  * `distance` (float circular angular distance)
  * `orb_diff` (float degrees from exact aspect)
  * `max_orb` (float allowed orb limit)
  * `strength` (float $[0.0, 1.0]$ quadratic decay)
  * `weight` (float planet pair tier weight $0.5$ to $3.0$)
  * `subscore_contributions` (dict of exact point additions/subtractions, e.g. `{"harmony": 2.25, "communication": 2.25}`)
* **Storage Location:** Stored in `public.compatibility_results.evidence_trace` (JSONB column added in Migration 021).
* **API Exposure:** **CURRENTLY HIDDEN FROM API RESPONSE**. The Pydantic model `StructuredCompatibilityResponse` does not include `evidence_trace`!
* **Status:** IMPLEMENTED in calculation & database; HIDDEN from FastAPI response model.

### 3. Missing Categories in Synastry
The following categories were investigated and confirmed **NOT FOUND / NOT IMPLEMENTED**:
* **House Overlays** (e.g. "Person A's Venus in Person B's 7th house"): NOT IMPLEMENTED.
* **Chiron / Lilith / Lunar Nodes Synastry**: NOT IMPLEMENTED (Bodies are not calculated).
* **Composite Chart** (Midpoint chart): NOT IMPLEMENTED.
* **Daily / Transit Synastry**: NOT IMPLEMENTED.
* **Relationship Archetype / Category Classifier** (e.g. "Soulmates", "Twin Flames", "Karmic", "Collaborators"): NOT IMPLEMENTED as an explicit category model (only signal categories exist: `harmony`, `attraction`, `communication`, `growth`, `stability`).

---

## SECTION D: DEEP ANALYSIS CAPABILITY

This section audits what backend data can power a **"Deep Analysis of Person B"**.

### Full Pipeline Trace
$$\text{Person A} \longrightarrow \text{Person B} \longrightarrow \text{Data Retrieval} \longrightarrow \text{Synastry Engine} \longrightarrow \text{Scoring} \longrightarrow \text{Interpretation} \longrightarrow \text{Response}$$

1. **Person A & Person B Identification:** JWT provides `current_user.id`; client provides `target_user_id`. Canonical pair sorted $(A < B)$.
2. **Permission Check:** `has_active_connection(user_a, user_b)` + `is_user_blocked(user_a, user_b)`.
3. **Data Retrieval:** Loads `public.birth_data` versions; loads or recalculates `public.astro_private` (10 planetary longitudes + Ascendant).
4. **Astrological Calculation:** Aspect detection across all 100 possible planet-to-planet combinations.
5. **Synastry Scoring:** Multi-dimensional subscores + element harmony + Mercury compatibility + Fire/Air count + Modality balance.
6. **Interpretation:** Currently **RULE-BASED ONLY** (Signals, Topics, Starters). AI/LLM narrative generation is **EMPTY**.
7. **Response:** Returns `score`, `signals`, `best_topics`, `conversation_starters`, `data_quality`.

### Inventory for Deep Analysis
| Tier | Capability | Current State |
| --- | --- | --- |
| **1. Already Available** | Overall Compatibility Score | Exposed via `POST /v1/compare` |
| **1. Already Available** | Top 6 Relational Signals (Labels, categories, strengths) | Exposed via `POST /v1/compare` |
| **1. Already Available** | Curated Conversation Starters (Up to 3 icebreakers) | Exposed via `POST /v1/compare` |
| **1. Already Available** | Best Conversation Topics (Up to 4 topics) | Exposed via `POST /v1/compare` |
| **1. Already Available** | Data Quality & Confidence Ratings | Exposed via `POST /v1/compare` |
| **1. Already Available** | Target Safe Astrology (Sun, Moon, Ascendant, Primary Element/Modality) | Exposed via `GET /v1/astrology/people/{id}/safe-astro` |
| **1. Already Available** | Target Public Profile (Name, avatar, bio, city, occupation) | Exposed via `GET /v1/profiles/{id}` |
| **2. Available Internally Only** | 4 Relational Dimensions (`emotional_harmony`, `communication`, `attraction`, `growth_long_term`) | Calculated by engine, but dropped on cache hit in API router |
| **2. Available Internally Only** | Complete Synastry Aspect Grid (`evidence_trace`: all aspects, exact orbs, exact strengths, subscore contributions) | Calculated and stored in DB table `compatibility_results.evidence_trace`, but omitted from API response schema |
| **3. Requires Small Backend Work** | Relaxing connection gate so user can view Deep Analysis of a discovered person without mutual connection | Requires adjusting `has_active_connection` check in `comparisons/router.py` |
| **3. Requires Small Backend Work** | Exposing `dimensions` reliably and `evidence_trace` in API response | Add fields to `StructuredCompatibilityResponse` model and query |
| **4. Does Not Exist** | AI/LLM-generated personalized narrative prose ("Jester Voice") | Stubs only in `backend/app/interpretation/` |
| **4. Does Not Exist** | House overlay analysis | Not implemented in `synastry.py` |
| **4. Does Not Exist** | Deep unlock payment / coin / entitlement checks | Not implemented |

---

## PROPOSED TECHNICAL COMPOSITION: ONE DEEP UNLOCK

Based **ONLY on existing backend capabilities** (without changing the astrology engine math):

```json
{
  "unlock_type": "deep_relationship_analysis",
  "target_user": {
    "profile": {
      "display_name": "Elena Rostova",
      "avatar_url": "https://...",
      "bio": "Curator & architect",
      "city": "Berlin",
      "occupation": "Architect"
    },
    "astrology": {
      "sun_sign": "Scorpio",
      "moon_sign": "Pisces",
      "ascendant_sign": "Cancer",
      "element_primary": "Water",
      "modality_primary": "Fixed"
    }
  },
  "compatibility_core": {
    "overall_score": 88.4,
    "confidence": 1.0,
    "time_precision": "exact",
    "dimensions": {
      "emotional_harmony": 94.2,
      "attraction": 86.5,
      "communication": 82.0,
      "growth_long_term": 78.6
    }
  },
  "relational_signals": [
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
    },
    {
      "type": "mercury_trine_mercury",
      "category": "communication",
      "strength": "high",
      "label": "Intellectual Flow",
      "source_aspects": ["Mercury Trine Mercury (Orb 2.1°)"]
    }
  ],
  "conversation_bridges": {
    "topics": ["art", "music", "psychology", "cinema"],
    "starters": [
      "What is something that instantly makes you feel understood?",
      "What is your idea of a perfect spontaneous date?",
      "What topic could you talk about for hours without getting bored?"
    ]
  },
  "detailed_aspect_evidence": [
    {
      "planet_a": "sun",
      "planet_b": "moon",
      "aspect": "trine",
      "target_angle": 120.0,
      "actual_distance": 121.2,
      "orb_diff": 1.2,
      "strength": 0.7744,
      "subscore_contributions": {
        "harmony": 2.09,
        "communication": 2.09
      }
    },
    {
      "planet_a": "venus",
      "planet_b": "mars",
      "aspect": "conjunction",
      "target_angle": 0.0,
      "actual_distance": 0.8,
      "orb_diff": 0.8,
      "strength": 0.81,
      "subscore_contributions": {
        "attraction": 2.43
      }
    }
  ]
}
```

---

## SECTION E: FREE VS DEEP DATA CLASSIFICATION

An analytical classification of existing backend data for product tiering:

### 1. FREE / BASIC DATA (Available for any discovered person)
* Public Profile: Display name, avatar URL, bio, city, occupation.
* Safe Astrology: Sun sign, Moon sign, Ascendant sign (if time known), Primary Element, Primary Modality.
* Connection State: Status (`pending`, `accepted`, `none`).

### 2. DEEP DATA (Reservable for Deep Unlock or Accepted Connections)
* Overall Compatibility Score (e.g. `88.4 / 100`).
* 4 Dimensional Breakdown Subscores (`emotional_harmony`, `communication`, `attraction`, `growth_long_term`).
* Top 6 Structured Relational Signals (with labels and aspect origins).
* Best Shared Conversation Topics.
* Tailored Conversation Starters / Icebreakers.
* Data Quality & Precision Confidence (Confidence score, exact vs approximate).
* Complete Astronomical Evidence Trace (Full aspect list, orbs, strengths, points).
* Direct Messaging Access (Currently gated behind active connection).

### 3. UNKNOWN / PRODUCT DECISION REQUIRED
* Showing only the overall score for free while locking the 4 dimensions and signals (Supported mathematically, but backend currently returns score and signals together).
* Daily Energy (Backend implementation is an empty stub; cannot be classified into free vs paid yet).

---

## SECTION F: DAILY ENERGY / DAY VIBE

* **Endpoint:** **NONE** (No FastAPI route exists).
* **Input:** `(user_id, energy_date, db)` in scheduled job function.
* **Calculation:** None. Inserts hardcoded placeholder.
* **Current Sky Data:** None. No ephemeris calculation of current planetary positions.
* **Natal Data Used:** None.
* **Output / Interpretation:** Hardcoded static JSON: `{"summary": "A dynamic day for creative exploration."}`.
* **LLM Involvement:** None.
* **Caching & Persistence:** Database table `public.daily_energies` exists with `UNIQUE (user_id, energy_date)`.
* **Date & Timezone Handling:** Stored as `DATE`. No timezone conversion logic implemented.
* **Implementation Status:** **DEFINED BUT NOT IMPLEMENTED (STUB ONLY)**.
* **Frontend Readiness:** **CANNOT BE CONSUMED TODAY**.

---

## SECTION G: PEOPLE DISCOVERY

| Capability | Backend Status | Evidence |
| --- | --- | --- |
| **User Search** | NOT IMPLEMENTED | No search endpoint in `profiles/router.py`. |
| **People Discovery Feed** | NOT IMPLEMENTED | No `/v1/people` or listing endpoint in FastAPI. |
| **Public Profiles** | IMPLEMENTED | `GET /v1/profiles/{id}` works for discoverable users. |
| **Recommendations** | NOT IMPLEMENTED | No matching or recommendation algorithms. |
| **Nearby People / Geo** | NOT IMPLEMENTED | Lat/lon in `birth_data` is birth location, not current user location. Profiles only have text field `city`. No PostGIS/geo queries. |
| **Random Discovery** | NOT IMPLEMENTED | No endpoint. |
| **Filtering (Sign/Element)** | NOT IMPLEMENTED | No endpoint. |
| **Compatibility-based Discovery** | NOT IMPLEMENTED | Cannot run compatibility without an active accepted connection. |
| **Profile Visibility Control** | IMPLEMENTED | `is_discoverable` boolean column in `profiles`; respected by RLS and router. |
| **Blocking Controls** | IMPLEMENTED | `is_user_blocked()` DB function; `block`/`unblock` transitions in `connections/router.py`; returns 404 Privacy-Safe Not Found. |
| **Privacy Invariants** | IMPLEMENTED | Raw birth data owner-only; `astro_private` denied to all clients; mutual blocks hide existence. |

---

## SECTION H: SHARING & SOCIAL CAPABILITIES

| Capability | Backend Status | Evidence |
| --- | --- | --- |
| **Shareable Result URLs** | NOT IMPLEMENTED | No public unauthenticated token/link resolver for results. |
| **Public Result Pages** | NOT IMPLEMENTED | All compatibility endpoints require Bearer JWT. |
| **Private Results** | IMPLEMENTED | Compatibility results restricted to pair participants via RLS and router checks. |
| **Deep Result Sharing** | NOT IMPLEMENTED | No sharing endpoint. |
| **Profile Sharing / Invite Links** | NOT IMPLEMENTED | No referral code or invite token generation. |
| **Referrals** | NOT IMPLEMENTED | No referral tracking schema. |
| **Direct Messaging** | IMPLEMENTED | `POST /v1/conversations`, `GET /v1/conversations/{id}/messages`, `POST /v1/conversations/{id}/messages`. Requires active accepted connection. |
| **Connection Requests** | IMPLEMENTED | `POST /v1/connections` (creates `pending`), `POST /v1/connections/{id}/transition` (`accept`, `decline`, `block`, `unblock`, `remove`). |
| **In-App Notifications** | IMPLEMENTED | `GET /v1/notifications`, `PATCH /v1/notifications/{id}/read`. |

---

## SECTION I: AUTH / PRIVACY / SECURITY

* **Authentication:** Supabase JWT Bearer token validated via `backend.app.auth.jwt.verify_supabase_jwt`. Uses JWKS in production; supports HS256 in test/development. Identity strictly derived from `JWT.sub`.
* **Authorization / Roles:** Role verification available via `require_role(["admin"])` in `dependencies.py`. Default role is `authenticated`.
* **Row-Level Security (RLS):** Enabled on all 11 public tables in `supabase/migrations/018_rls.sql`.
* **Private vs Public Data Separation:**
  * `birth_data`: Strictly owner-only (`user_id = auth.uid()`).
  * `astro_private`: Revoked from all clients (`REVOKE ALL`). Backend-only.
  * `astro_safe_profile`: Public for discoverable users (`is_discoverable = true AND NOT is_user_blocked()`).
* **Canonical Connection Ordering:** Always enforces `user_a_id < user_b_id` via CHECK constraints and code helper `get_canonical_pair()`.
* **Mutual Block Hiding:** `public.is_user_blocked(user_a, user_b)` checks both directions. If blocked, returns HTTP 404 (`PrivacySafeNotFoundException`) to prevent existence oracle leaks.
* **Rate Limiting & Abuse Protection:** **NOT IMPLEMENTED** in FastAPI application code.
* **Age & Consent Tracking:** **NOT FOUND** in schema (no terms acceptance timestamp, no explicit age check field).

---

## SECTION J: CURRENT API INVENTORY

| Method | Path | Purpose | Auth | Request Body | Response Model | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `GET` | `/healthz` | System liveness probe | None | None | `{"status": "ok"}` | IMPLEMENTED |
| `GET` | `/v1/health` | Detailed service & DB probe | None | None | `{"status", "project", "version", "environment", "database"}` | IMPLEMENTED |
| `GET` | `/v1/users/me` | Account ID & email | Bearer JWT | None | `UserResponse(id, email, role)` | IMPLEMENTED |
| `GET` | `/v1/profiles/me` | Current user profile | Bearer JWT | None | `ProfileResponse(...)` | IMPLEMENTED |
| `PATCH` | `/v1/profiles/me` | Update own profile | Bearer JWT | `ProfileUpdate` | `ProfileResponse(...)` | IMPLEMENTED |
| `GET` | `/v1/profiles/{id}` | Target user profile | Bearer JWT | None | `ProfileResponse(...)` | IMPLEMENTED |
| `POST` | `/v1/astrology/profile/recalculate` | Recalculate natal chart | Bearer JWT | None | `SafeDerivedAstrologyResponse(...)` | IMPLEMENTED |
| `GET` | `/v1/astrology/profile/safe-astro` | Current user safe astro | Bearer JWT | None | `SafeDerivedAstrologyResponse(...)` | IMPLEMENTED |
| `GET` | `/v1/astrology/people/{id}/safe-astro` | Target user safe astro | Bearer JWT | None | `SafeDerivedAstrologyResponse(...)` | IMPLEMENTED |
| `GET` | `/v1/connections` | List my connections | Bearer JWT | None | `list[ConnectionResponse]` | IMPLEMENTED |
| `POST` | `/v1/connections` | Send connection request | Bearer JWT | `ConnectionCreate(target_user_id)` | `ConnectionResponse(...)` | IMPLEMENTED |
| `POST` | `/v1/connections/{id}/transition` | Accept/decline/block/remove | Bearer JWT | `ConnectionTransition(action)` | `ConnectionResponse(...)` | IMPLEMENTED |
| `POST` | `/v1/compare` | Synastry compatibility | Bearer JWT | `CompareRequest(target_user_id)` | `StructuredCompatibilityResponse(...)` | IMPLEMENTED (Requires active connection) |
| `GET` | `/v1/people/{id}/why` | Alias for compare | Bearer JWT | None | `StructuredCompatibilityResponse(...)` | IMPLEMENTED (Requires active connection) |
| `POST` | `/v1/conversations` | Get/create direct chat | Bearer JWT | `DirectConversationCreate(target_user_id)` | `ConversationResponse(...)` | IMPLEMENTED (Requires active connection) |
| `GET` | `/v1/conversations/{id}/messages` | List chat messages | Bearer JWT | None | `list[MessageResponse]` | IMPLEMENTED |
| `POST` | `/v1/conversations/{id}/messages` | Send chat message | Bearer JWT | `MessageCreate(body)` | `MessageResponse(...)` | IMPLEMENTED |
| `GET` | `/v1/notifications` | List notifications | Bearer JWT | None | `list[NotificationResponse]` | IMPLEMENTED |
| `PATCH` | `/v1/notifications/{id}/read` | Mark read | Bearer JWT | None | `NotificationResponse(...)` | IMPLEMENTED |

---

## SECTION K: DATABASE ENTITY MAP

```
auth.users (Supabase Auth)
  │
  ├──► public.profiles (1:1) [display_name, avatar_url, bio, city, occupation, timezone, is_discoverable]
  ├──► public.birth_data (1:1) [birth_date, birth_time, precision, timezone, lat, lon, data_version]
  ├──► public.astro_private (1:1) [10 planet longitudes, ascendant, houses jsonb, retrogrades jsonb]
  ├──► public.astro_safe_profile (1:1) [sun_sign, moon_sign, ascendant_sign, element_primary, modality_primary]
  ├──► public.daily_energies (1:Many) [energy_date, signals jsonb, interpretation jsonb] (STUB)
  ├──► public.notifications (1:Many) [type, payload jsonb, read_at]
  │
  ├──► public.connections (Many:Many via canonical user_a_id < user_b_id)
  │      [status: pending|accepted|declined|blocked|removed, initiated_by, blocked_by]
  │
  ├──► public.compatibility_results (Many:Many via canonical user_a_id < user_b_id)
  │      [score, signals jsonb, best_topics jsonb, conversation_starters jsonb, evidence_trace jsonb]
  │
  └──► public.conversations & conversation_members & messages (Direct Chat Rooms)
```

---

## SECTION L: FRONTEND-READY CAPABILITY MATRIX

| Capability | Backend Status | Endpoint/Service | Available Data | Frontend Can Use Now? | Notes |
| --- | --- | --- | --- | --- | --- |
| **View Own Profile** | IMPLEMENTED | `GET /v1/profiles/me` | Full profile fields | **YES** | Auto-creates if missing. |
| **Edit Own Profile** | IMPLEMENTED | `PATCH /v1/profiles/me` | Name, avatar, bio, city, occupation, discoverable | **YES** | Instant update. |
| **View Own Safe Astrology** | IMPLEMENTED | `GET /v1/astrology/profile/safe-astro` | Sun, Moon, Ascendant, Primary Element & Modality | **YES** | Auto-calculates if birth data exists. |
| **Recalculate Own Astrology** | IMPLEMENTED | `POST /v1/astrology/profile/recalculate` | Updated safe astrology | **YES** | Use after editing birth data. |
| **View Another's Profile** | IMPLEMENTED | `GET /v1/profiles/{id}` | Public profile fields | **YES** | Block-aware; requires discoverable. |
| **View Another's Safe Astro** | IMPLEMENTED | `GET /v1/astrology/people/{id}/safe-astro` | Sun, Moon, Ascendant, Element, Modality | **YES** | Block-aware; requires discoverable. |
| **List My Connections** | IMPLEMENTED | `GET /v1/connections` | Connection IDs, statuses, participants | **YES** | Filters blocked users correctly. |
| **Send Connection Request** | IMPLEMENTED | `POST /v1/connections` | Target ID -> Status `pending` | **YES** | Idempotent / reactivates removed. |
| **Manage Connections** | IMPLEMENTED | `POST /v1/connections/{id}/transition` | Accept, decline, block, unblock, remove | **YES** | State machine strictly enforced. |
| **Direct Chat Messaging** | IMPLEMENTED | `/v1/conversations/...` | Direct threads, send/receive messages | **YES** | Requires accepted connection. |
| **In-App Notifications** | IMPLEMENTED | `/v1/notifications` | Notification list & mark-as-read | **YES** | Fully operational. |
| **Full Compatibility Analysis** | IMPLEMENTED | `POST /v1/compare` or `GET /v1/people/{id}/why` | Score, signals, topics, starters, data quality | **CONDITIONAL** | **Requires active accepted connection**. Cannot be viewed for unaccepted users. |
| **4 Relational Dimensions** | PARTIAL | `POST /v1/compare` | Harmony, Comm, Attraction, Growth | **NO (UNRELIABLE)** | Calculated fresh, but lost on cache hit. Needs 1-line router fix. |
| **Aspect Evidence Trace** | PARTIAL | `compatibility_results.evidence_trace` | All aspects, orbs, math points | **NO (INTERNAL)** | In DB, but not in API response model. Needs schema exposure. |
| **Browse / Search People** | NOT FOUND | None | None | **NO** | Frontend must provide known user IDs. |
| **Daily Energy / Vibe** | NOT FOUND | None (stub only) | Static string in DB | **NO** | No endpoint; transits empty. |
| **AI Jester Narrative** | NOT FOUND | None (stubs only) | None | **NO** | LLM pipeline not implemented. |
