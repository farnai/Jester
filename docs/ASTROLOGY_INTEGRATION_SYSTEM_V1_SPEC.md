# JESTER — ASTROLOGY INTEGRATION SYSTEM V1
## Product, UX, Data Architecture & Relationship Intelligence Specification

**Document Type:** Core Architecture & Product Integration Specification  
**System Domain:** Astrology Integration & Relational Intelligence  
**Engine Version:** `astrology-v1.0.0` / `synastry-v1.0.0`  
**Parent Specifications:**
- [`docs/archive/historical/PRODUCT_SPECIFICATION.md`](archive/historical/PRODUCT_SPECIFICATION.md) (Historical Parent)
- [`docs/ASTROLOGY_ENGINE.md`](ASTROLOGY_ENGINE.md)
- [`docs/SYNASTRY_V1_SPEC.md`](SYNASTRY_V1_SPEC.md)
- [`docs/DISCOVERY_PREFERENCES_SYSTEM_V1_SPEC.md`](DISCOVERY_PREFERENCES_SYSTEM_V1_SPEC.md)
- [`docs/AI.md`](AI.md)  
**Status:** Authoritative Architectural Specification (V1 Frozen)

---

## 1. Executive Summary & Core Product Axioms

JESTER is a **People Discovery and Relationship Intelligence** platform. It is emphatically **NOT** a conventional astrology app, horoscope generator, or zodiac dating service. In JESTER, astrology is an underlying, deterministic astronomical intelligence layer designed to help humans understand themselves, each other, and interpersonal dynamics.

### Core Product Loop
```text
ME → YOU → US → MORE PEOPLE
```

### Governing Product Axioms
1. **"People first. Signals second. Scores last."**
   Human self-expression, identity, and declared choices govern the user experience. Mathematical scores exist strictly as internal ranking mechanics or curiosity hooks, never as the consumer definition of a connection.
2. **"The insight becomes the invitation."**
   Astrology provides the underlying deterministic spark. Downstream interpretation layers translate that spark into sharp, witty, empathetic human observations that naturally inspire dialogue and connection.
3. **"Score creates curiosity. Interpretation creates value."**
   A score without an explanation is an empty number. JESTER never states a compatibility verdict without providing the qualitative, behavioral *why*.
4. **"Human reality outranks astrological symbolism."**
   Astrology is an interpretive lens, not a deterministic biographical truth. What a user explicitly declares about their identity, intent, values, lifestyle, and communication always supersedes any astrological tendency or chart inference.

---

## 2. Role of Astrology in JESTER & Architectural Boundaries

### 2.1 What Astrology Is Responsible For
- **Deterministic Astronomical Calculation:** Computing high-precision planetary ecliptic longitudes, speeds, retrograde states, and Placidus house cusps via the Swiss Ephemeris (`PySwissEph`) C-engine.
- **Relational Dynamics Extraction:** Detecting geometric aspects between natal placements, calculating angular distances, applying quadratic orb decay, and mapping multi-dimensional relationship balances (harmony, communication, attraction, growth).
- **Conversational Grounding:** Generating structured, machine-readable relational signals (e.g. `sun_trine_moon`, `venus_conjunction_mars`) that feed the JESTER Voice Engine to produce personalized conversation starters and icebreakers.
- **Explainability Hooks:** Offering qualitative narrative explanations for why two people might feel an instinctive rhythm, creative push-pull, or complementary pace.
- **Discovery Soft Relevance:** Contributing a capped, configurable soft signal (10% weight) to the candidate discovery feed to surface intriguing relational chemistry without restricting user agency.

### 2.2 What Astrology Is NOT Responsible For
- **Psychological Diagnoses or Character Verdicts:** Astrology must never label a user as "toxic", "narcissistic", "inflexible", or "depressed".
- **Predictive Fatalism or Future Telling:** Astrology must never predict future events, relationship failure, marriage dates, or financial outcomes.
- **Hard Discovery Filtering:** Astrology is strictly prohibited from being used as a hard gate (e.g. no "No Scorpios", no zodiac exclusions, no minimum astrological score requirement).
- **Overriding Declared Human Signals:** Astrology must never contradict or rewrite user-declared intent, values, lifestyle habits, or communication styles.
- **Inventing Meaning Without Deterministic Backing:** The system must never hallucinate placements, invent orbs, or approximate charts using probabilistic LLMs.

### 2.3 Astrology vs. The 9 Core Human Domains

| Domain | Human Reality (Authoritative) | Astrological Role (Interpretive Lens) | Integration Rule |
| :--- | :--- | :--- | :--- |
| **1. Identity & Origin** | Declared Name, Bio, City, Country, Hometown, Languages. | Planetary placements mapped from birth coordinates. | Astrology provides energetic flavor; origin and identity remain 100% human-declared. |
| **2. Interests** | Explicitly chosen Primary, Secondary, and Signature Interests. | Element/Modality archetype resonance. | Interests reflect real-world passions. Astrology never invents hobbies based on zodiac signs. |
| **3. Lifestyle** | Sleep rhythm, activity level, work reality, substance habits. | Mars/Sun physical vitality and pacing indicators. | Declared lifestyle is the absolute truth. If a Pisces is a 6 AM runner, JESTER honors the runner. |
| **4. Values** | Declared Core Value and Guiding Principles (18 canonical values). | Jupiter/Saturn philosophical framing. | Values reflect conscious ethical commitments. Astrology never judges or modifies a user's morals. |
| **5. Social Behavior** | Gathering scale, social battery, recharge pace, comfort zones. | Moon/Ascendant social dynamics. | Declared social battery dictates hangout suggestions. Astrology never forces extroversion/introversion. |
| **6. Communication** | Depth, conversational role, medium preference, response pacing. | Mercury sign, aspect geometry, communication dimension. | Declared pacing governs response expectations. Astrology merely explains stylistic push-pull. |
| **7. Intent** | Friendship, dating, creative collaboration, exploring. | Synastry chemistry and polarity dynamics. | **Absolute Intent Primacy:** Synastry chemistry is framed platonically or professionally if intent is not romantic. |
| **8. Prompts / Voice** | User-authored prompt questions, witty answers, authentic tone. | Icebreaker context and conversational hooks. | Prompts showcase individual human voice. Astrology never inserts horoscopic clichés into answers. |
| **9. Discovery Prefs** | Age range, location radius, gender, intent, lifestyle dealbreakers. | 10% soft relevance ranking and explainability tags. | Preferences are absolute search boundaries. Astrology never bypasses or alters hard search filters. |
| **10. JESTER AI** | Multi-signal synthesis and natural dialogue partner. | Ingests structured astrological facts as context. | AI consumes pre-calculated facts; it never independently calculates charts or hallucinates data. |

---

## 3. Current Astrology & Natal Architecture Audit

A complete audit of the repository (`backend/app/astrology/`, `backend/app/compatibility/`, `supabase/migrations/`, `tests/`) reveals the end-to-end data lifecycle:

```text
Birth Data Input (Frontend)
       ↓ POST /astrology/birth-data (Pydantic validation: date, time, precision, IANA timezone)
In-Memory Swiss Ephemeris Calculation (PySwissEph C-Engine)
       ├── compute_julian_day() (Local time -> UTC -> swe.julday)
       ├── compute_natal_placements() (10 planets + Placidus houses + Ascendant + retrogrades)
       └── derive_primary_element_and_modality() (Weighted counters)
              ↓
Atomic Single-Transaction Database Persistence
       ├── INSERT INTO public.birth_data (Owner-only RLS, auto-incrementing data_version)
       ├── INSERT INTO public.astro_private (Server-only table, exact float longitudes & cusps)
       └── INSERT INTO public.astro_safe_profile (Public-safe signs, element, modality)
              ↓
Safe Derived DTO Response (SafeDerivedAstrologyResponse)
```

### 3.1 Existing Implementation Inventory

| Component | Code Location | Status | Implementation Details |
| :--- | :--- | :--- | :--- |
| **Julian Day Engine** | `backend/app/astrology/calculator.py` | `IMPLEMENTED` | Converts local time to UTC via Python `zoneinfo.ZoneInfo`. Unknown time defaults to 12:00 UTC (mean noon). |
| **Planetary Positions** | `backend/app/astrology/calculator.py` | `IMPLEMENTED` | Computes 10 bodies (Sun through Pluto) using `swe.FLG_SWIEPH \| swe.FLG_SPEED`. |
| **Retrograde Evaluation** | `backend/app/astrology/calculator.py` | `IMPLEMENTED` | Checks ecliptic longitude speed (`speed_lon < 0.0`). Stored as boolean map in `retrogrades` JSONB. |
| **Placidus House System** | `backend/app/astrology/calculator.py` | `IMPLEMENTED` | Computes 12 cusps via `swe.houses(..., b"P")`. Polar regions (> 66.5° lat) raise `placidus_polar_error` (HTTP 400). |
| **Sign & Element Derivation** | `backend/app/astrology/calculator.py` | `IMPLEMENTED` | Maps longitudes to 12 signs. Weighted points: Sun(3), Moon(3), Ascendant(3), Mercury(2), Venus(2), Mars(2). |
| **Aspect & Orb Geometry** | `backend/app/astrology/aspects.py` | `IMPLEMENTED` | 5 major aspects (Conjunction, Sextile, Square, Trine, Opposition). Quadratic decay. Luminary boost (+2.0°), Ascendant cap (6.0°). |
| **Synastry Engine V1** | `backend/app/compatibility/synastry.py` | `IMPLEMENTED` | Evaluates cross-chart aspects, 4 dimensions, dynamic signals, topics, starters, evidence trace. Version `synastry-v1.0.0`. |
| **Daily Planetary Transits**| `backend/app/astrology/transits.py` | `IMPLEMENTED` | Real ephemeris transit calculation against natal placements, Georgina localization, daily guidance mapping. (488 lines). |
| **Developer Debug Router** | `backend/app/astrology/debug.py` | `IMPLEMENTED` | Non-production inspector (`ENV != "production"`) for caller's own raw chart data. |
| **Database Schema** | `supabase/migrations/` | `IMPLEMENTED` | `004_birth_data.sql`, `005_astro_private.sql`, `006_astro_safe_profile.sql`, `008_compatibility_results.sql`, `021`, `022`. |
| **Test Suite** | `tests/astrology/`, `tests/compatibility/` | `VERIFIED` | 83 passing tests in astrology/compatibility; 290 passing tests repository-wide. |

### 3.2 Audit Findings & Inconsistencies Resolved
1. **Transits Documentation Staleness:** `docs/ASTROLOGY_ENGINE.md` claimed `transits.py` was a 47-byte stub. In reality, `backend/app/astrology/transits.py` is a fully operational, 488-line deterministic transit engine with Georgian localization and daily energy calculation.
2. **Safe Profile Storage vs. API Response:** `public.astro_safe_profile` stores only `sun_sign`, `moon_sign`, `ascendant_sign`, `element_primary`, and `modality_primary`. The API response model `SafeDerivedAstrologyResponse` dynamically enriches these with `mercury_sign`, `venus_sign`, and `mars_sign` by joining with `astro_private` longitudes on the fly.
3. **Placidus High-Latitude Boundary:** Placidus is mathematically undefined above $66.5^\circ$ latitude. The backend catches `swe.Error` and raises a clean, structured `placidus_polar_error` (HTTP 400), which frontend onboarding must gracefully translate into user guidance.

---

## 4. Canonical Astrology Data Model

To enforce architectural cleanliness, JESTER establishes a strict, non-negotiable 5-layer pipeline:

```text
LAYER 1: SOURCE BIRTH DATA (Private, user-owned, sensitive)
       ↓
LAYER 2: DETERMINISTIC ASTRONOMICAL CALCULATIONS (Server-controlled, exact floats)
       ↓
LAYER 3: STRUCTURED ASTROLOGICAL FACTS (Discrete signs, aspects, geometry)
       ↓
LAYER 4: INTERPRETIVE RELATIONAL MEANING (Dimensions, dynamics, semantic IDs)
       ↓
LAYER 5: PRODUCT PRESENTATION (Witty JESTER voice, human-readable UI copy)
```

```
+-----------------------------------------------------------------------------------+
| LAYER 1: SOURCE BIRTH DATA                                                        |
| Table: public.birth_data (Owner-Only RLS)                                         |
| - birth_date: date (YYYY-MM-DD)                                                   |
| - birth_time: time (HH:MM:SS, optional)                                           |
| - birth_time_precision: 'exact' | 'approximate' | 'unknown'                      |
| - birth_timezone: text (IANA identifier, e.g. "Asia/Tbilisi")                     |
| - latitude: double precision (optional, [-90.0, 90.0])                            |
| - longitude: double precision (optional, [-180.0, 180.0])                         |
| - place_label: text (optional, e.g. "Tbilisi, Georgia")                           |
| - data_version: integer (auto-increments on update)                               |
+-----------------------------------------------------------------------------------+
                                      ↓
+-----------------------------------------------------------------------------------+
| LAYER 2: DETERMINISTIC CALCULATIONS                                               |
| Table: public.astro_private (Server-Only, No Client Grant)                        |
| - Julian Day: double precision (swe.julday)                                       |
| - Planetary Longitudes: Sun..Pluto [0.0, 360.0) rounded to 6 decimal places       |
| - Ascendant Longitude: double precision | null                                    |
| - Houses: 12 Placidus cusp longitudes [h1..h12] | null                            |
| - Retrogrades: jsonb map {planet_name: boolean}                                   |
| - engine_version: text (e.g. "1.0.0")                                             |
+-----------------------------------------------------------------------------------+
                                      ↓
+-----------------------------------------------------------------------------------+
| LAYER 3: STRUCTURED ASTROLOGY FACTS                                               |
| Table: public.astro_safe_profile + Aspect Detection                               |
| - Sun Sign, Moon Sign, Ascendant Sign, Mercury Sign, Venus Sign, Mars Sign       |
| - Primary Element: 'Fire' | 'Earth' | 'Air' | 'Water'                             |
| - Primary Modality: 'Cardinal' | 'Fixed' | 'Mutable'                              |
| - Detected Aspects: {body_a, body_b, aspect_type, actual_dist, orb_diff, strength}|
+-----------------------------------------------------------------------------------+
                                      ↓
+-----------------------------------------------------------------------------------+
| LAYER 4: INTERPRETATION & RELATIONAL SIGNALS                                      |
| Table: public.compatibility_results + InterpretationEngine                        |
| - Dimensions: harmony, communication, attraction, growth (0.0 - 100.0)            |
| - Relational Signals: e.g. 'sun_trine_moon', 'venus_square_mars'                   |
| - Semantic IDs: e.g. 'relationship.attraction.strong_chemistry.v1'                |
| - Topics & Conversation Starters (Georgian & English)                             |
+-----------------------------------------------------------------------------------+
                                      ↓
+-----------------------------------------------------------------------------------+
| LAYER 5: PRODUCT PRESENTATION                                                     |
| Consumer UI, Discovery Cards, Profile Badges, Chat Starters                       |
| - "Sun in Leo, Moon in Aquarius, Rising in Scorpio"                               |
| - "Dynamic Push-Pull: You inspire each other's curiosity, but process emotions at  |
|    very different speeds." (Zero raw degrees, zero aspect jargon in public UI)    |
+-----------------------------------------------------------------------------------+
```

---

## 5. Birth Time Quality & Confidence Model

A user's birth data certainty varies significantly. JESTER handles uncertainty with mathematical rigor, ensuring that unverified calculations are never presented as fact.

### 5.1 Precision Matrix & Calculation Scope

| Scenario | Input Parameters | Calculable Astronomy | Incalculable / Excluded | Engine Confidence |
| :--- | :--- | :--- | :--- | :--- |
| **A. Complete Data** | Exact date + exact time + valid lat/lon. | 10 Planets, Retrogrades, Ascendant, 12 Houses, all aspects. | None. Full chart available. | **1.00 (100%)** |
| **B. Approximate Time** | Exact date + approximate time (±1–2h) + valid lat/lon. | 10 Planets, Retrogrades. Ascendant calculated but flagged uncertain. Houses calculated. | Exact house boundary placements treated with lower weight. | **0.85 (85%)** |
| **C. Unknown Time** | Exact date + null time + timezone/coords. | 10 Planets (mean noon UTC: 12:00), Retrogrades, inter-planetary aspects. | **Ascendant is NULL**. **Houses are NULL**. Moon orb expanded/cautioned. | **0.75 (75%)** |
| **D. Unknown Place** | Exact date + time + null lat/lon. | 10 Planets, Retrogrades, planetary aspects. | **Ascendant is NULL**. **Houses are NULL** (require coordinates). | **0.75 (75%)** |
| **E. Polar Coordinates** | Exact date + time + latitude > 66.5°. | 10 Planets, Retrogrades, Ascendant. | **Placidus Houses FAIL** (`placidus_polar_error`, HTTP 400). | **N/A (Error State)** |
| **F. Invalid Data** | Future date, date < 1900, bad timezone. | None. Validation rejects immediately before computation. | Entire calculation aborted. | **0.00 (Rejected)** |

### 5.2 Handling Missing Birth Time in Synastry
When either Person A or Person B has `birth_time_precision = 'unknown'`:
1. **Ascendant Aspects Excluded:** Any cross-chart aspect involving Person A's or Person B's Ascendant is completely dropped from scoring and signal extraction.
2. **House Overlays Excluded:** No planet-to-house overlay analysis occurs.
3. **Moon Position Caution:** Because the Moon travels $\approx 13.2^\circ$ per day, Moon aspects are calculated at mean noon UTC and assigned a wider orb threshold or lower confidence weight.
4. **Data Quality Payload:** The API response explicitly sets:
   ```json
   {
     "data_quality": {
       "time_precision": "unknown",
       "confidence": 0.75,
       "houses_used": false,
       "ascendant_used": false
     }
   }
   ```
5. **UI Transparency:** The UI displays a gentle note: *"Birth time unknown — connection evaluated using planetary core dynamics (Ascendant and house dynamics omitted)."*

---

## 6. Natal Chart V1 Scope

To prevent scope creep and maintain engine speed, JESTER defines a strictly bounded astronomical model for V1:

### 6.1 Included Celestial Bodies & Points (11 Points Total)
1. **Sun** (`swe.SUN`): Core vitality, ego, self-expression, primary archetype.
2. **Moon** (`swe.MOON`): Emotional rhythm, instinctive reactions, vulnerability.
3. **Mercury** (`swe.MERCURY`): Intellectual pace, communication mechanics, curiosity.
4. **Venus** (`swe.VENUS`): Aesthetic resonance, relational affection, social warmth.
5. **Mars** (`swe.MARS`): Drive, initiative, conflict style, physical energy.
6. **Jupiter** (`swe.JUPITER`): Philosophical expansion, optimism, generosity.
7. **Saturn** (`swe.SATURN`): Structure, discipline, boundaries, long-term realism.
8. **Uranus** (`swe.URANUS`): Individuality, eccentricity, disruptive insight.
9. **Neptune** (`swe.NEPTUNE`): Imagination, empathy, idealism, mystery.
10. **Pluto** (`swe.PLUTO`): Transformation, intensity, subconscious power.
11. **Ascendant** (Calculated from geographic coordinates + exact/approximate time): Outer persona, first impression, social doorway.

### 6.2 Excluded from V1 Scope (Deferred to Future Versions)
- **Midheaven (MC), IC, Descendant (DC):** Excluded from V1 profile and synastry matrices.
- **Lunar Nodes (North Node, South Node):** Excluded from V1.
- **Chiron & Black Moon Lilith:** Excluded from V1.
- **Asteroids (Ceres, Pallas, Juno, Vesta):** Excluded from V1.
- **Part of Fortune / Arabian Parts:** Excluded from V1.
- **Minor Aspects (Quincunx, Semi-Sextile, Quintile, Sesquiquadrate):** Excluded from V1.
- **House Overlays in Synastry (Planet A in Person B's 7th House):** Deferred to V1.1.

---

## 7. Multi-Tiered Astrology Visibility & Privacy Model

Raw birth information is highly sensitive personal data (used for identity verification, financial security, and personal privacy). JESTER enforces an impenetrable multi-tiered visibility architecture:

```text
[ TIER 1: PRIVATE BIRTH DATA ]
Table: public.birth_data
Fields: birth_date, birth_time, birth_timezone, latitude, longitude, place_label
Access: OWNER ONLY (user_id = auth.uid()). NEVER readable by other users or discovery.
             ↓
[ TIER 2: PRIVATE CALCULATIONS ]
Table: public.astro_private
Fields: Exact degree longitudes, speeds, houses, retrogrades
Access: SERVER-SIDE ONLY. Revoked from authenticated, anon, and public roles.
             ↓
[ TIER 3: SAFE PUBLIC ASTROLOGY ]
Table: public.astro_safe_profile + API DTO
Fields: sun_sign, moon_sign, ascendant_sign, element_primary, modality_primary
Access: Read-only for authenticated users (provided target is discoverable and not blocked).
             ↓
[ TIER 4: DISCOVERY ASTROLOGY HOOK ]
Context: Candidate cards in Discovery feed
Fields: Qualitative relational hook, complementary energy badge (e.g. "Air & Fire Dynamic")
Access: Configurable. Suppressed entirely if viewer sets astrology_mode = 'hidden'.
             ↓
[ TIER 5: SYNASTRY & RELATIONSHIP INTELLIGENCE ]
Context: /v1/compare and /v1/people/{id}/why
Fields: 4 dimension subscores, qualitative dynamic signals, topics, starters, narrative reasons
Access: Both users must have discoverable profiles and not be mutually blocked.
             ↓
[ TIER 6: JESTER AI CONTEXT ]
Context: LLM prompt synthesizers & interpretation engines
Fields: Discrete structured facts JSON (signs, aspect types, confidence, intent, values)
Access: Strictly internal server memory. Zero raw coordinates, zero birth dates passed to LLMs.
```

### 7.1 Visibility Flags & User Controls
Users have granular control over how astrology appears on their profile via `discovery_preferences.astrology_mode` and profile settings:
- **`standard` (Default):** Displays the Big Three (Sun, Moon, Rising) and derived themes on profile. Enables qualitative synastry insights.
- **`minimal`:** Displays only Sun and Moon signs. Omits detailed astrological commentary.
- **`hidden`:** Completely hides astrological signs from the user's public profile and suppresses all astrological terminology from Discovery cards. (Synastry calculation still powers background compatibility relevance, but all explainability is delivered in human, non-astrological language).

---

## 8. Astrology on the User Profile

JESTER does **not** turn a human profile into a dense natal chart encyclopedia. The profile interface is designed for everyday human connection:

### 8.1 What a User Sees on a Profile
1. **The Big Three Badges:**
   - **Sun Sign** (e.g. ♌ Leo)
   - **Moon Sign** (e.g. ♒ Aquarius)
   - **Rising / Ascendant Sign** (e.g. ♏ Scorpio, or *"Unknown"* if birth time was omitted)
2. **Three Core Functional Themes (Concise, 1-Sentence Observations):**
   - **Communication Style (Mercury Sign + Element):** *"You process thoughts rapidly and enjoy conceptual debate, but lose patience with circular small talk."*
   - **Emotional Rhythm (Moon Sign + Venus Sign):** *"You need emotional autonomy and clear breathing room before processing intense feelings."*
   - **Drive & Curiosity (Sun Sign + Mars Sign):** *"You are motivated by creative independence and sharp momentum rather than routine maintenance."*
3. **Primary Element & Modality Pill:**
   - Badge: *"Primary Fire • Fixed Momentum"*

### 8.2 Profile Presentation Guardrails
- **No Predictive Certainty:** Never say *"You will succeed in business in October"*.
- **No Medical or Mental Health Claims:** Never say *"Your Moon square Saturn causes clinical depression"*.
- **No Toxic Stereotyping:** Never say *"As a Scorpio, you are manipulative and jealous"*.
- **No Jargon Overload:** Avoid phrases like *"Your 8th house stellium is afflicted by an out-of-sign square"*. Speak in direct, observant human language.

---

## 9. Astrology in Discovery & Ranking Architecture

### 9.1 The Anti-Filtering Rule
In conventional dating and social apps, astrology is frequently misused as a superficial, discriminatory filtering mechanism:
> *"No Geminis allowed."*  
> *"Only matching with Earth signs."*

**JESTER Architectural Rule:**
Astrology is **NEVER** an exclusion filter in Discovery. Users cannot filter candidates by zodiac sign, element, or astrological score. Discovery preferences allow filtering strictly by human real-world criteria: age, location distance, gender, and declared relationship intent.

### 9.2 The V1 Discovery Ranking Model Audit
Discovery candidates are ranked in the feed using a multi-factor weighted scoring model:

$$\text{Score}_{\text{candidate}} = 0.25 \cdot S_{\text{intent}} + 0.20 \cdot S_{\text{location}} + 0.20 \cdot S_{\text{interests}} + 0.15 \cdot S_{\text{values}} + 0.10 \cdot S_{\text{prompts}} + 0.10 \cdot S_{\text{astrology}}$$

```text
+-------------------------------------------------------------+
| JESTER DISCOVERY RELEVANCE MODEL                            |
+------------------------------------+------------------------+
| Factor                             | Weight                 |
+------------------------------------+------------------------+
| 1. Intent Alignment                | 25%                    |
| 2. Location & Origin Proximity     | 20%                    |
| 3. Shared & Semantic Interests     | 20%                    |
| 4. Values Alignment                | 15%                    |
| 5. Prompts & Conversational Voice  | 10%                    |
| 6. Astrological Synastry Dynamics  | 10% (Capped Soft Boost)|
+------------------------------------+------------------------+
```

### 9.3 Why the 10% Astrology Weight is Architecturally Sound
1. **Subordinate to Human Decisions:** The 5 human-declared domains constitute **90%** of candidate ranking. A candidate with conflicting intent or opposing values will never be ranked at the top of the feed simply because of an astrological trine.
2. **Curiosity Spark:** The 10% weight acts as a gentle tie-breaker between otherwise compatible humans, surfacing unexpected interpersonal chemistry that declared interests alone might miss.
3. **Graceful Degradation:** If a viewer sets `astrology_mode = 'hidden'`, the 10% weight is smoothly redistributed across Interests (+5%) and Values (+5%), ensuring zero ranking distortion.

---

## 10. Synastry V1 Integration

The existing Synastry V1 Engine (`backend/app/compatibility/`) operates as a self-contained, deterministic service consumed by Discovery ranking and comparison endpoints.

```text
Person A Natal Placements (astro_private)
                +
Person B Natal Placements (astro_private)
                ↓
SynastryEngine.calculate(payload_a, payload_b)
                ↓
[ DETERMINISTIC RELATIONAL RESULTS ]
- 4 Subscores: Emotional Harmony, Communication, Attraction, Growth
- Normalized Overall Score: 10.0 - 98.0 (Internal ranking use)
- Dynamic Signals: (Up to 6 strongest aspects, e.g. sun_trine_moon)
- Audit Evidence Trace: (Exact orbs, aspect angles, weights applied)
- Topic Recommendations & Georgian Conversation Starters
                ↓
Persisted in public.compatibility_results (Canonical pair: user_a < user_b)
                ↓
InterpretationEngine & JESTER AI
                ↓
Human-Readable Qualitative Relationship Insight
```

### 10.1 Mathematical Aspects & Orb Decay
Synastry V1 evaluates 5 major aspects between the 10 planets (+ Ascendant):
- **Conjunction ($0^\circ$):** Base Orb $= 8.0^\circ$, Weight $= 1.00$
- **Sextile ($60^\circ$):** Base Orb $= 6.0^\circ$, Weight $= 0.70$
- **Square ($90^\circ$):** Base Orb $= 7.0^\circ$, Weight $= 0.75$
- **Trine ($120^\circ$):** Base Orb $= 8.0^\circ$, Weight $= 0.90$
- **Opposition ($180^\circ$):** Base Orb $= 8.0^\circ$, Weight $= 0.85$

Orb expansion and constraints:
- **Luminary Boost:** If either body is Sun or Moon, Base Orb $+ 2.0^\circ$.
- **Ascendant Constraint:** Aspects involving the Ascendant are strictly capped at $6.0^\circ$.
- **Quadratic Decay:**

$$S_{\text{aspect}} = \left(1.0 - \frac{\text{orb\_diff}}{\text{max\_orb}}\right)^2$$

### 10.2 The 4 Relational Dimensions
Synastry V1 aggregates aspects into 4 focused relational sub-scores:
1. **Emotional Harmony (`emotional_harmony`):** Moon-Moon, Moon-Venus, Moon-Sun, Moon-Neptune aspects. Reflects emotional safety, vulnerability, and instinctive comfort.
2. **Communication (`communication`):** Mercury-Mercury, Mercury-Uranus, Mercury-Jupiter, Mercury-Sun aspects. Reflects conversational banter, intellectual stimulation, and processing speed.
3. **Attraction & Chemistry (`attraction`):** Venus-Mars, Mars-Mars, Sun-Venus, Venus-Pluto aspects. Reflects magnetic pull, energetic polarity, and creative excitement.
4. **Growth & Long-Term Synergy (`growth_long_term`):** Sun-Jupiter, Sun-Saturn, Moon-Saturn, Jupiter-Saturn aspects. Reflects mutual encouragement, stability, grounding, and life momentum.

---

## 11. Astrology Explainability: From Fact to Human Insight

JESTER prohibits superficial percentage labels on Discovery feeds. We never tell a user: *"You and Sophie are 87% compatible."*

### 11.1 The Explainability Pipeline
```text
CALCULATED FACT
"Person A Mercury at 14° Aries opposition Person B Mercury at 16° Libra (Orb: 2.0°)"
       ↓
RELATIONAL SIGNAL
"mercury_opposition_mercury" (High intellectual polarity, fast conversational pace)
       ↓
INTERPRETATION CONTRACT
"relationship.communication.fast_banter_differing_angles.v1"
       ↓
JESTER VOICE RESOLUTION (Georgian / English)
"თქვენი საუბარი ჭადრაკის სწრაფ პარტიას ჰგავს — ერთი იდეას ისვრის, მეორე საპირისპირო კუთხეს პოულობს. მოწყენა აქ პრაქტიკულად გამორიცხულია."
("Your conversations are like speed chess — one throws an idea, the other immediately spots the counter-angle. Boredom is practically impossible here.")
```

### 11.2 Qualitative Relationship Hooks
Instead of numerical scores, Discovery cards and comparison screens display qualitative dynamic hooks:
- *"Creative Push-Pull: High creative momentum, but you recharge at different speeds."*
- *"Instant Conversational Rapport: You naturally skip the small talk and dive into ideas."*
- *"Grounded Resonance: Calm, unhurried energy with strong mutual respect."*

---

## 12. Human Signals vs. Astrology Priority Rules

When human-declared choices conflict with astrological indicators, **human reality always wins**.

```text
HIERARCHY OF AUTHORITY:
LEVEL 1: Declared Human Reality (Identity, Intent, Lifestyle, Values, Communication)
             ↓ outranks
LEVEL 2: Observed Behavioral Signals (Interaction pacing, active interests, chat activity)
             ↓ outranks
LEVEL 3: Astrological Interpretive Dynamics (Chart placements, aspects, synastry)
```

### Concrete Resolution Scenarios:

| Dimension | Astrological Indication | Human-Declared Reality | JESTER Behavioral Rule |
| :--- | :--- | :--- | :--- |
| **Lifestyle Pacing** | Mars in Aries indicates high spontaneity and impulsive action. | User selects: *"I plan my week in advance and hate last-minute changes."* | **Trust Human Declaration:** Profile emphasizes structured rhythm. Astrology may playfully note: *"Astrologically there's a spark of spontaneous drive, but in real life you keep your calendar tightly locked."* |
| **Intent Primacy** | High Venus-Mars synastry aspect indicates intense romantic chemistry. | Both users declare intent: `creative_collaborator` or `activity_partner`. | **Strict Platonic Framing:** The chemistry is framed as creative friction, productive drive, and shared work energy. Romantic or flirtatious copy is strictly suppressed. |
| **Social Battery** | Sun in Leo with strong 1st house placements suggests high extraversion. | User selects: *"Small groups only (1–2 people), battery drains fast."* | **Respect Stated Boundaries:** JESTER suggests quiet coffee spots, never crowded events. |
| **Communication Depth** | Mercury in Gemini indicates witty, lighthearted banter. | User selects: *"Deep, conceptual conversations; skip the superficial."* | **Anchor on Stated Preference:** Conversation starters target philosophy, values, and meaningful ideas. |

---

## 13. JESTER AI + Astrology Integration

JESTER AI (LLMs and prompt synthesizers) interacts with astrology through strict, structured facts contracts.

### 13.1 Structured Facts Context Payload
The AI engine receives a sanitized JSON payload containing only discrete facts and pre-resolved signals. It never receives raw birth times, GPS coordinates, or unvetted astronomical data:

```json
{
  "user_context": {
    "sun_sign": "Leo",
    "moon_sign": "Aquarius",
    "ascendant_sign": "Scorpio",
    "element_primary": "Fire",
    "modality_primary": "Fixed",
    "confidence": 1.00
  },
  "relational_context": {
    "dimensions": {
      "emotional_harmony": 82.5,
      "communication": 74.0,
      "attraction": 88.0,
      "growth_long_term": 70.5
    },
    "top_signals": [
      {
        "signal": "venus_conjunction_mars",
        "category": "attraction",
        "strength": "strong",
        "source_planets": ["venus", "mars"]
      },
      {
        "signal": "mercury_trine_jupiter",
        "category": "communication",
        "strength": "moderate",
        "source_planets": ["mercury", "jupiter"]
      }
    ],
    "mutual_intent": "friendship",
    "shared_interests": ["Photography", "Philosophy", "Hiking"],
    "shared_values": ["Authenticity", "Curiosity"]
  }
}
```

### 13.2 Guardrails for JESTER AI
1. **Zero Independent Calculation:** The AI must never attempt to calculate planetary positions, orbs, or chart aspects. It consumes only the numbers provided.
2. **Zero Hallucination of Placements:** If a user's Ascendant is `null` (unknown birth time), the AI must never invent a Rising sign.
3. **Intent Primacy Enforcement:** When generating relationship commentary, the AI must check `mutual_intent`. If intent is non-romantic, all chemistry signals are translated into creative or intellectual synergy.
4. **Zero Astrological Jargon:** The AI must never output technical astrology terms (e.g. *"Because of your 120-degree trine"*). It must speak solely in JESTER's signature witty, observant, human voice.

---

## 14. Versioning & Reproducibility

Astrological calculations in JESTER are deterministic and mathematically immutable. Given the exact same birth data inputs and engine version, the output must be bit-identical across all environments.

### 14.1 Engine Versioning Matrix
- **`ASTROLOGY_ENGINE_VERSION`:** `1.0.0` (Governs ephemeris flags, planetary selection, coordinate rounding, and sign boundary logic).
- **`SWISS_EPHEMERIS_VERSION`:** `2.10.03` (Underlying Swiss Ephemeris C-library).
- **`SYNASTRY_ENGINE_VERSION`:** `synastry-v1.0.0` (Governs aspect definitions, orb limits, weight matrices, and scoring curves).
- **`source_birth_data_version`:** Stored in `public.birth_data.data_version` (auto-increments via trigger on any parameter change).

### 14.2 Stale Calculation & Invalidation Protocol
When a user updates their birth time or location:
1. The database trigger increments `birth_data.data_version` (e.g. from `1` to `2`).
2. `public.astro_private` and `public.astro_safe_profile` are updated atomically in the same transaction with `source_birth_data_version = 2`.
3. Cached records in `public.compatibility_results` referencing `user_a_birth_data_version = 1` or `user_b_birth_data_version = 1` become stale.
4. When either user requests `/v1/compare` or `/v1/people/{id}/why`, the comparison router detects the version mismatch and automatically re-runs `SynastryEngine.calculate()`, updating the cached result without downtime.

---

## 15. Astrology UX Behavioral States

JESTER defines 12 distinct product and UX states for the astrology subsystem:

```text
+-----------------------------------------------------------------------------------+
| STATE                         | BEHAVIORAL DEFINITION                             |
+-------------------------------+---------------------------------------------------+
| 1. Complete Data              | Exact date + time + place. All 10 planets, houses,|
|                               | Ascendant, and synastry active at 100% confidence.|
+-------------------------------+---------------------------------------------------+
| 2. Approximate Time           | Date + time window (±1–2h). Houses and Ascendant  |
|                               | calculated but flagged approximate (85% conf).    |
+-------------------------------+---------------------------------------------------+
| 3. Unknown Birth Time         | Date + place known. 10 planets calculated at noon |
|                               | UTC. Ascendant/houses omitted (75% confidence).   |
+-------------------------------+---------------------------------------------------+
| 4. Unknown Birth Place        | Date + time known, no coords. Planets calculated. |
|                               | Ascendant and houses omitted (75% confidence).    |
+-------------------------------+---------------------------------------------------+
| 5. Polar Coordinate Error     | Latitude > 66.5°. Placidus house failure caught   |
|                               | gracefully; returns HTTP 400 placidus_polar_error.|
+-------------------------------+---------------------------------------------------+
| 6. Timezone Ambiguity         | Historic municipal boundary change. Engine uses   |
|                               | canonical IANA zoneinfo database.                 |
+-------------------------------+---------------------------------------------------+
| 7. Invalid Input Data         | Future date or year < 1900. Rejected immediately  |
|                               | by validation before database or calculation.     |
+-------------------------------+---------------------------------------------------+
| 8. Calculation Pending        | Background recomputation in progress. Old safe    |
|                               | profile served until transaction commits.         |
+-------------------------------+---------------------------------------------------+
| 9. Calculation Success        | Atomic commit completed. astro_private and safe   |
|                               | profile synchronized to latest data_version.      |
+-------------------------------+---------------------------------------------------+
| 10. Engine Calculation Failure| Ephemeris exception caught. Database rolled back; |
|                               | zero partial writes persisted.                    |
+-------------------------------+---------------------------------------------------+
| 11. Astrology Hidden          | User set astrology_mode = 'hidden'. Signs hidden  |
|                               | from profile; jargon suppressed from discovery.   |
+-------------------------------+---------------------------------------------------+
| 12. Stale Compatibility Cache | Birth data changed; version mismatch detected on  |
|                               | next read; automatic on-the-fly recalculation.    |
+-------------------------------+---------------------------------------------------+
```

---

## 16. API Architecture & Endpoints

All astrology operations are managed through clean RESTful boundaries with strict DTO separation:

### 16.1 Implemented Astrology Endpoints

| Method | Endpoint | Auth | Purpose & Contracts |
| :--- | :--- | :--- | :--- |
| `POST` | `/astrology/birth-data` | Authenticated | Saves birth data and atomically calculates & persists natal chart. Returns `SafeDerivedAstrologyResponse`. |
| `POST` | `/astrology/profile/recalculate` | Authenticated | Recalculates natal chart and safe profile from existing stored birth data. Returns `SafeDerivedAstrologyResponse`. |
| `GET` | `/astrology/profile/safe-astro` | Authenticated | Retrieves caller's safe derived astrology profile (signs, element, modality). Auto-calculates if missing. |
| `GET` | `/astrology/people/{target_user_id}/safe-astro` | Authenticated | Retrieves another user's safe profile. Returns privacy-safe `404` if user is blocked or undiscoverable. |
| `GET` | `/astrology/debug/my-astro` | Authenticated | Developer debug endpoint. Returns raw longitudes and cusps. **Strictly disabled in production** (`ENV != 'production'`). |
| `POST` | `/v1/compare` | Authenticated | Runs cross-chart synastry comparison between caller and target. Returns score, dimensions, signals, starters. |
| `GET` | `/v1/people/{id}/why` | Authenticated | Retrieves relationship intelligence breakdown and qualitative reasons for connection. |

### 16.2 Proposed V1 API Extensions

#### `GET /v1/astrology/profile/me/natal-summary`
Provides the authenticated user with a deeper, personal safe view of their own chart (e.g. Mercury, Venus, Mars placements and personal themes) without exposing raw degree floats or house math.

#### `GET /v1/astrology/explain/{target_user_id}`
Dedicated relationship explainability endpoint delivering the 4 dimension balances, top qualitative dynamic hooks, and Georgian/English icebreakers, with zero exposure of underlying aspect numbers.

---

## 17. Database Architecture & Schema Audit

The database cleanly isolates sensitive inputs from calculated values and public interpretations across 4 primary tables:

```text
public.birth_data (Owner-Only)
├── user_id: uuid (PK, references auth.users)
├── birth_date: date NOT NULL
├── birth_time: time (NULL allowed if precision = 'unknown')
├── birth_time_precision: 'exact' | 'approximate' | 'unknown'
├── birth_timezone: text NOT NULL (IANA)
├── latitude: double precision, longitude: double precision
├── place_label: text
└── data_version: integer NOT NULL DEFAULT 1

public.astro_private (Server-Only, REVOKE ALL)
├── user_id: uuid (PK, references auth.users)
├── source_birth_data_version: integer NOT NULL
├── engine_version: text NOT NULL
├── sun_longitude..pluto_longitude: double precision
├── ascendant_longitude: double precision
├── houses: jsonb (List of 12 cusp floats)
├── retrogrades: jsonb (Map of planet -> boolean)
└── calculated_at: timestamptz NOT NULL DEFAULT now()

public.astro_safe_profile (Authenticated Select via RLS)
├── user_id: uuid (PK, references auth.users)
├── source_birth_data_version: integer NOT NULL
├── engine_version: text NOT NULL
├── sun_sign: text, moon_sign: text, ascendant_sign: text
├── element_primary: text, modality_primary: text
└── updated_at: timestamptz NOT NULL DEFAULT now()

public.compatibility_results (Canonical Pair Cache)
├── id: uuid (PK)
├── user_a_id: uuid, user_b_id: uuid (Constraint: user_a_id < user_b_id)
├── user_a_birth_data_version: integer, user_b_birth_data_version: integer
├── engine_version: text NOT NULL
├── score: numeric(5,2) (Bounds: 0.00 - 100.00)
├── dimensions: jsonb (emotional_harmony, communication, attraction, growth)
├── signals: jsonb, best_topics: jsonb, conversation_starters: jsonb
└── evidence_trace: jsonb (Aspects, orbs, decay scores)
```

---

## 18. Conflict Audit & Documentation Synchronization

A comprehensive audit of repository documentation against codebase reality identified and reconciled the following discrepancies:

1. **`transits.py` Implementation Status:**
   - *Documentation Discrepancy:* `docs/ASTROLOGY_ENGINE.md` marked `backend/app/astrology/transits.py` as an empty 47-byte stub.
   - *Code Reality:* `backend/app/astrology/transits.py` is an active 488-line engine calculating real Swiss Ephemeris transits and daily energy guidance with 19 passing unit tests.
   - *Resolution:* Documentation updated to reflect the operational state of the transit calculation engine.
2. **Safe Profile Storage vs. API Response Schema:**
   - *Documentation Discrepancy:* `docs/DATABASE.md` implies `astro_safe_profile` stores all personal signs.
   - *Code Reality:* Table stores Sun, Moon, Ascendant, element, and modality. The API response dynamically injects Mercury, Venus, and Mars signs by joining with `astro_private`.
   - *Resolution:* Explicitly documented this architectural choice: keeping the table lean while enriching safe DTOs at the service layer.
3. **Placidus Polar Region Contract:**
   - *Documentation Discrepancy:* Some early notes suggested automatic fallback to Whole Sign or Equal houses in polar regions.
   - *Code Reality:* `calculator.py` strictly raises `placidus_polar_error` (HTTP 400).
   - *Resolution:* Frozen in specification: Placidus polar failure is the canonical contract; alternative house fallbacks are deferred to V1.1+.
4. **Compatibility Match Scores in Discovery:**
   - *Documentation Discrepancy:* Early concept drafts mentioned showing compatibility percentages on Discovery profile cards.
   - *Code Reality & Product Invariant:* Axiom *"Scores last"* strictly bans percentage scores on Discovery cards. Only qualitative dynamic hooks and conversation topics are surfaced.

---

## 19. Testing & Deterministic Verification

The astrology subsystem is validated through an extensive test suite verifying mathematical determinism, boundary handling, and privacy boundaries.

### Test Execution Results
All 83 tests in `tests/astrology/` and `tests/compatibility/` pass with zero failures:
```text
tests/astrology/test_aspects.py (15 tests) ................. PASSED
tests/astrology/test_astrology_api.py (2 tests) ............. PASSED
tests/astrology/test_atomic_onboarding.py (8 tests) ......... PASSED
tests/astrology/test_calculation_validation.py (10 tests) ... PASSED
tests/astrology/test_calculator.py (5 tests) ................ PASSED
tests/astrology/test_transits.py (19 tests) ................. PASSED
tests/compatibility/test_router.py (2 tests) ................ PASSED
tests/compatibility/test_synastry.py (8 tests) .............. PASSED
tests/compatibility/test_topics.py (9 tests) ................ PASSED

Ran 83 tests in 2.39s. Status: 100% PASSED.
Repository-wide test suite: 290 passed in 13.5s.
```

### Verified Properties
- **Exact Determinism:** Identical date/time/timezone inputs produce identical 6-decimal longitudes across repeated executions.
- **Aspect Wraparound:** 0°/360° boundary wraparound calculates identical angular distance (e.g. 359° and 1° = 2° conjunction).
- **Polar Resilience:** Latitudes above 66.5° reliably trigger `placidus_polar_error`.
- **Atomic Rollback:** If calculation fails during onboarding, exactly 0 database writes occur; if `astro_private` fails, `birth_data` rolls back.
- **Privacy Security:** Blocked or undiscoverable users reliably return privacy-safe `404` rather than leaking existence.

---

## 20. V1 vs. Future Evolution

| Capability | In Scope for V1 | Deferred to Future (V1.1 / V2) |
| :--- | :--- | :--- |
| **Ephemeris Engine** | Swiss Ephemeris (`PySwissEph`) C-engine | Alternative astronomical models |
| **Planets Calculated** | 10 Bodies (Sun through Pluto) | Asteroids (Ceres, Juno, Pallas, Vesta) |
| **Angles Calculated** | Ascendant (exact/approximate time) | Midheaven (MC), IC, Descendant (DC) |
| **House System** | Placidus Cusps (lat $\le 66.5^\circ$) | Whole Sign / Equal House polar fallback |
| **Aspects Evaluated** | 5 Major (Conjunction, Sextile, Square, Trine, Opposition) | Minor Aspects (Quincunx, Semi-Sextile) |
| **Synastry Engine** | Inter-planetary aspects, 4 dimensions, dynamic signals | House overlays (Planet A in Person B's houses) |
| **Composite Charts** | Not in V1 | Midpoint Composite & Davison Charts |
| **Progressions & Solar** | Not in V1 | Secondary Progressions, Solar Arc Directions |
| **Daily Energy Hook** | 1-2 sentence deterministic transits insight | Realtime transit notification feed |
| **Discovery Role** | 10% soft relevance weight, qualitative dynamic tags | Personalized astrological feed filtering |
| **AI Integration** | Ingestion of pre-calculated structured facts | Live chart calculation by LLMs (Permanently Banned) |

---

## 21. Open Questions Requiring Human Approval

1. **Polar Region Fallback Strategy (V1.1):**
   *Question:* Currently, latitudes $> 66.5^\circ$ trigger `placidus_polar_error` (HTTP 400). Should V1.1 introduce an automatic fallback to Whole Sign houses (`swe.houses(..., b"W")`) or Equal House for users born in high-latitude regions (e.g. Tromsø, Reykjavik), or should they continue without house calculations (like unknown birth time)?
2. **Expansion of `astro_safe_profile` Columns:**
   *Question:* Currently, `astro_safe_profile` stores Sun, Moon, Ascendant, Element, and Modality, while Mercury, Venus, and Mars signs are derived dynamically via joins. Should a future migration add `mercury_sign`, `venus_sign`, and `mars_sign` directly to `astro_safe_profile` to eliminate the join query on profile reads?
3. **Astrology Weight in Discovery Tuning:**
   *Question:* The 10% soft relevance weight is currently configured as a baseline. Should users who express high enthusiasm for astrology be allowed to toggle an "Astrology Affinity" setting that elevates this weight to 15% (reducing Interests to 15%), while remaining capped and strictly non-filtering?
