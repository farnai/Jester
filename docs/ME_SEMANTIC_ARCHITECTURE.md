# JESTER — PHASE 3
## "ME" / "ვინ ვარ მე?"
### COMPLETE ASTROLOGICAL SEMANTIC ARCHITECTURE SPECIFICATION

> **Status:** ARCHITECTURE DESIGN & FORENSIC SPECIFICATION  
> **Target Subsystem:** Natal Self-Understanding Intelligence ("ME" / `self.*`)  
> **Source of Truth:** Repository Source Code (`backend/app/astrology/`, `backend/app/interpretation/`), Swiss Ephemeris (`pyswisseph`), PostgreSQL Schema (`public.astro_private`, `public.astro_safe_profile`), `content_corpus.json`  
> **Constraints:** Zero new copy generation, zero engine modification, zero invented astrology, strict determinism (`TRUTH > VARIETY`).

---

## 1. EXECUTIVE SUMMARY

The "ME" subsystem in JESTER is designed as a **deterministic natal self-understanding intelligence engine**, not a horoscope, fortune-telling service, or pop-astrology trivia widget. 

### Core Product Philosophy
```text
BIRTH DATA (Owner-Only Private)
      │
      ▼
Swiss Ephemeris (Deterministic Astronomy)
      │
      ▼
NATAL CALCULATIONS (Planetary Longitudes, Cusps, Speeds)
      │
      ▼
DETERMINISTIC SIGNALS (Signs, Elements, Modalities, Safe Profiles)
      │
      ▼
SEMANTIC INTERPRETATION (Formal Interpretation Contracts)
      │
      ▼
JESTER VOICE (Delivery Modes: Snarky, Unfiltered, Mocking, Conversational...)
      │
      ▼
COHERENT LONG-FORM NARRATIVE ("ვინ ვარ მე?")
```

### The Axiom of Astrological Integrity
- **Astrology determines WHAT JESTER is permitted to observe.** (Truth boundary)
- **JESTER voice determines HOW the observation is delivered.** (Stylistic framing)
- **Content variation determines WHICH approved phrasing is selected.** (Diversity without hallucination)

Under no circumstances may tone, style, or desire for variety fabricate an astrological claim that cannot be traced directly back to Swiss Ephemeris calculations.

### Current Baseline Reality vs. Target State
- **Current Baseline:** The UI renders up to **5 isolated cards** (`self.identity`, `self.emotional`, `self.persona`, `self.element`, `self.modality`) resolved via `resolve_natal_narrative()`. The repository contains 43 formal `self.*` contracts and 2,652 micro-draft assets (1,815 in Georgian, 100% `ai_draft`, average length ~195 characters).
- **Target State:** A **chaptered, unified personal dossier** that transforms isolated placement cards into a comprehensive, multi-depth narrative (Core Identity, Emotional Architecture, Cognitive Style, Relational Instinct, Kinetic Drive, Social Persona, Internal Friction Patterns, and JESTER Final Verdict), backed by verifiable provenance and mathematical combination rules.

---

## 2. CURRENT ME CALCULATION CAPABILITIES (FORENSIC AUDIT)

A rigorous audit of `backend/app/astrology/natal.py`, `calculator.py`, `models.py`, and database schemas reveals the exact boundary between what is calculated, what is exposed, and what is discarded.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             SWISS EPHEMERIS (pyswisseph)                         │
│   Calculates Julian Day, 10 Planetary Longitudes, Speeds, Placidus House Cusps   │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
      ┌─────────────────────────┐                 ┌─────────────────────────┐
      │  public.astro_private   │                 │       IN-MEMORY RAM     │
      │   (Server-Side Only)    │                 │       (natal.py)        │
      │                         │                 │                         │
      │ • Sun .. Pluto lons     │                 │ • mercury_sign          │
      │ • Ascendant lon         │                 │ • venus_sign            │
      │ • Placidus houses [12]  │                 │ • mars_sign             │
      │ • Retrogrades dict[10]  │                 │ (Used for weights only, │
      └────────────┬────────────┘                 │  then DISCARDED!)       │
                   │                              └────────────┬────────────┘
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
                        ┌─────────────────────────────────┐
                        │    public.astro_safe_profile    │
                        │    (Safe Public API Surface)    │
                        │                                 │
                        │ • sun_sign                      │
                        │ • moon_sign                     │
                        │ • ascendant_sign (or null)      │
                        │ • element_primary               │
                        │ • modality_primary              │
                        └─────────────────────────────────┘
```

### Detailed Capability Classification

| Calculation Item | Exact Origin / Function | Storage Location | Public API Exposure | Interpretation Status | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sun Sign** | `swe.calc_ut` $\to$ `longitude_to_sign` | `astro_safe_profile.sun_sign` | Exposed via `/v1/astrology/me` | 12 Contracts (`self.identity.sun_*`) | **SUPPORTED / IMPLEMENTED** |
| **Moon Sign** | `swe.calc_ut` $\to$ `longitude_to_sign` | `astro_safe_profile.moon_sign` | Exposed via `/v1/astrology/me` | 12 Contracts (`self.emotional.moon_*`) | **SUPPORTED / IMPLEMENTED** |
| **Ascendant Sign** | `swe.houses` (Placidus) $\to$ `longitude_to_sign` | `astro_safe_profile.ascendant_sign` | Exposed via `/v1/astrology/me` (null if time unknown) | 12 Contracts (`self.persona.rising_*`) | **SUPPORTED / IMPLEMENTED** |
| **Dominant Element** | Weighted tally (Sun:3, Moon:3, Asc:3, Mer:2, Ven:2, Mar:2) | `astro_safe_profile.element_primary` | Exposed via `/v1/astrology/me` | 4 Contracts (`self.element.*_dominant`) | **SUPPORTED / IMPLEMENTED** |
| **Dominant Modality** | Weighted tally (Sun:3, Moon:3, Asc:3, Mer:2, Ven:2, Mar:2) | `astro_safe_profile.modality_primary` | Exposed via `/v1/astrology/me` | 3 Contracts (`self.modality.*_dominant`) | **SUPPORTED / IMPLEMENTED** |
| **Mercury Sign** | `swe.calc_ut` $\to$ `longitude_to_sign` | In RAM during calculation only (`natal.py:126`) | **NOT EXPOSED** | 0 Contracts | **CALCULATED BUT DISCARDED** |
| **Venus Sign** | `swe.calc_ut` $\to$ `longitude_to_sign` | In RAM during calculation only (`natal.py:127`) | **NOT EXPOSED** | 0 Contracts | **CALCULATED BUT DISCARDED** |
| **Mars Sign** | `swe.calc_ut` $\to$ `longitude_to_sign` | In RAM during calculation only (`natal.py:128`) | **NOT EXPOSED** | 0 Contracts | **CALCULATED BUT DISCARDED** |
| **Planetary Longitudes** (Sun..Pluto, Asc) | `swe.calc_ut` (6 decimal precision) | `astro_private.*_longitude` | **NOT EXPOSED** (Security Invariant) | N/A (Raw Astrometry) | **STORED / SERVER-CONTROLLED** |
| **Placidus House Cusps** | `swe.houses(jd, lat, lon, b"P")` $\to$ 12 cusps | `astro_private.houses` (`list[float]`) | **NOT EXPOSED** | 0 Contracts | **STORED BUT UNINTERPRETED** |
| **Planetary Retrogrades** | `speed_lon < 0.0` for 10 planets | `astro_private.retrogrades` (`dict[str, bool]`) | **NOT EXPOSED** | 0 Contracts | **STORED BUT UNINTERPRETED** |
| **Natal Internal Aspects** | `aspects.py:detect_aspect()` exists, but only called for synastry | Not calculated for self | **NOT EXPOSED** | 0 Contracts | **DERIVABLE BUT NOT IMPLEMENTED** |
| **Planet-in-House Allocation** | No coordinate-in-cusp comparison exists | None | **NOT EXPOSED** | 0 Contracts | **NOT IMPLEMENTED** |
| **Multi-Placement Combinations** | No synthesis evaluation exists in `engine.py` | None | **NOT EXPOSED** | 0 Contracts | **NOT IMPLEMENTED** |
| **Unified Narrative Assembler** | No chaptered aggregation in `engine.py` | None | **NOT EXPOSED** | 0 Contracts | **NOT IMPLEMENTED** |

---

## 3. COMPLETE ME SEMANTIC LAYER MAP

To build a deep self-understanding dossier, we define a formal **10-Layer Semantic Architecture**. Each layer represents a distinct psychological and behavioral domain grounded in deterministic calculations.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LAYER 10: CHART-LEVEL SYNTHESIS                       │
│                         (The JESTER Final Verdict)                          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
         ┌─────────────────────────────┴─────────────────────────────┐
         ▼                                                           ▼
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│   LAYER 8: INTERNAL DYNAMICS    │                 │   LAYER 9: NATAL ASPECTS        │
│   (Sun ↔ Moon, Sun ↔ Asc...)    │                 │   (Conjunction, Square, Trine)  │
└────────────────┬────────────────┘                 └────────────────┬────────────────┘
                 │                                                   │
                 └─────────────────────┬─────────────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
│ LAYER 1: IDENTITY │        │  LAYER 2: EMOTION │        │  LAYER 3: PERSONA │
│    (Sun Sign)     │        │    (Moon Sign)    │        │  (Ascendant Sign) │
└───────────────────┘        └───────────────────┘        └───────────────────┘
         │                             │                             │
         ▼                             ▼                             ▼
┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
│ LAYER 4: COGNITION│        │  LAYER 5: RELATE  │        │   LAYER 6: DRIVE  │
│  (Mercury Sign)*  │        │   (Venus Sign)*   │        │   (Mars Sign)*    │
└───────────────────┘        └───────────────────┘        └───────────────────┘
         │                             │                             │
         └─────────────────────────────┼─────────────────────────────┘
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │     LAYER 7: STRUCTURAL ENERGY    │
                     │  (Dominant Element & Modality)    │
                     └───────────────────────────────────┘
(* Requires persisting RAM signs to astro_safe_profile)
```

### Layer Specifications

#### LAYER 1 — CORE IDENTITY (Sun)
- **Astronomical Input:** Ecliptic longitude of the Sun at birth date/time UTC converted to Tropical Zodiac sign (`sun_sign`).
- **Psychological Domain:** Fundamental ego orientation, life purpose, instinctive self-expression, core vitality.
- **Current Status:** `SUPPORTED / IMPLEMENTED` (12 contracts: `self.identity.sun_aries.v1` through `self.identity.sun_pisces.v1`).

#### LAYER 2 — EMOTIONAL WORLD (Moon)
- **Astronomical Input:** Ecliptic longitude of the Moon at birth date/time UTC converted to Tropical Zodiac sign (`moon_sign`).
- **Psychological Domain:** Inner emotional processing, subconscious security needs, vulnerability defense mechanisms, self-soothing rhythm.
- **Current Status:** `SUPPORTED / IMPLEMENTED` (12 contracts: `self.emotional.moon_aries.v1` through `self.emotional.moon_pisces.v1`).

#### LAYER 3 — SOCIAL PERSONA (Ascendant / Rising)
- **Astronomical Input:** Eastern horizon ecliptic intersection calculated via Swiss Ephemeris Placidus routine using geographic latitude, longitude, and birth time (`ascendant_sign`).
- **Psychological Domain:** First impression, social armor, physical and conversational entry style, external presentation.
- **Graceful Degradation:** If birth time is unknown (`precision="unknown"`), Ascendant is strictly `None`. The narrative gracefully omits this layer without breaking.
- **Current Status:** `SUPPORTED / IMPLEMENTED` (12 contracts: `self.persona.rising_aries.v1` through `self.persona.rising_pisces.v1`).

#### LAYER 4 — COMMUNICATION & COGNITIVE STYLE (Mercury)
- **Astronomical Input:** Ecliptic longitude of Mercury at birth (`mercury_sign`).
- **Psychological Domain:** Information processing, conversational tempo, intellectual curiosity, debate style, articulation mechanics.
- **Current Status:** `CALCULATED BUT NOT EXPOSED` (Calculated in RAM in `natal.py:126`, discarded before storage; 0 contracts exist).

#### LAYER 5 — RELATIONSHIP INSTINCT & VALUES (Venus)
- **Astronomical Input:** Ecliptic longitude of Venus at birth (`venus_sign`).
- **Psychological Domain:** Attachment aesthetic, relational currency, pleasure principles, boundary mediation, how affection is offered and sought.
- **Current Status:** `CALCULATED BUT NOT EXPOSED` (Calculated in RAM in `natal.py:127`, discarded before storage; 0 contracts exist).

#### LAYER 6 — ACTION, CONFLICT & DRIVE (Mars)
- **Astronomical Input:** Ecliptic longitude of Mars at birth (`mars_sign`).
- **Psychological Domain:** Kinetic assertiveness, conflict posture, stamina deployment, anger processing, initiative execution.
- **Current Status:** `CALCULATED BUT NOT EXPOSED` (Calculated in RAM in `natal.py:128`, discarded before storage; 0 contracts exist).

#### LAYER 7 — STRUCTURAL ENERGY (Element & Modality Dominance)
- **Astronomical Input:** Deterministic weighted tally of personal placements (`element_primary`, `modality_primary`).
- **Psychological Domain:**
  - *Element (Fire, Earth, Air, Water):* Fundamental metabolic and psychological currency (Kinetic, Pragmatic, Conceptual, Intuitive).
  - *Modality (Cardinal, Fixed, Mutable):* Strategic operational tempo (Initiating, Consolidating, Adapting).
- **Current Status:** `SUPPORTED / IMPLEMENTED` (7 contracts: 4 element + 3 modality).

#### LAYER 8 — INTERNAL DYNAMICS (Pairwise Multi-Placement Synthesis)
- **Astronomical Input:** Joint presence of two personal placements (e.g., Sun in Air + Moon in Water; Sun in Aries + Ascendant in Capricorn).
- **Psychological Domain:** Internal dialogue, behavioral contradictions, tension between conscious intention (Sun) and unconscious reaction (Moon) or social mask (Ascendant).
- **Current Status:** `DERIVABLE FROM CURRENT DATA BUT NOT IMPLEMENTED` (No combination rules or contracts exist).

#### LAYER 9 — NATAL INTERNAL ASPECTS
- **Astronomical Input:** Angular distance between bodies in the user's chart within allowable orbs (`aspects.py:ASPECT_DEFINITIONS`), evaluating Conjunction ($0^\circ$), Sextile ($60^\circ$), Square ($90^\circ$), Trine ($120^\circ$), Opposition ($180^\circ$).
- **Psychological Domain:** Specific internal structural alignments—congenital friction (Squares/Oppositions) or organic fluidities (Trines/Sextiles) between cognitive, emotional, and ego centers.
- **Current Status:** `DERIVABLE FROM CURRENT MATH BUT NO NATAL CALLER IMPLEMENTED` (Engine evaluates aspects only in cross-chart synastry).

#### LAYER 10 — CHART-LEVEL SYNTHESIS (The JESTER Verdict)
- **Astronomical Input:** Holistic deterministic evaluation integrating dominant element, dominant modality, luminary dynamic, and primary personal planets.
- **Psychological Domain:** The overarching JESTER psychological summary—cutting through ego self-deception with biting, accurate wit.
- **Current Status:** `CONCEPTUAL ARCHITECTURE ONLY / NOT IMPLEMENTED`.

---

## 4. WHAT EACH LAYER IS ALLOWED TO SAY (BOUNDARIES & SAFETY)

To prevent pseudo-astrological hallucination and generic horoscope filler, every layer is bound by explicit epistemological boundaries.

| Layer | Input Received | Permitted Semantic Claims | Strictly Prohibited Claims | Temporal State |
| :--- | :--- | :--- | :--- | :--- |
| **1. Sun (Identity)** | `sun_sign` (Aries..Pisces) | Fundamental motivations, core focus, natural creative stance, ego pride points. | Future events, career fortunes, partner compatibility, health outcomes. | **STATIC** (Natal) |
| **2. Moon (Emotions)** | `moon_sign` (Aries..Pisces) | Stress reset patterns, private boundaries, how emotions are felt and contained. | Psychiatric diagnoses, childhood trauma claims, future relationship fate. | **STATIC** (Natal) |
| **3. Ascendant (Persona)** | `ascendant_sign` (or None) | Initial conversational demeanor, outward posture, first-impression dynamics. | Moral character, internal self-worth, deterministic physical appearance. | **STATIC** (Natal) |
| **4. Mercury (Cognition)** | `mercury_sign` | Reasoning patterns, communication tempo, debate style, focus biases. | Clinical cognitive abilities, IQ claims, academic achievements. | **STATIC** (Natal) |
| **5. Venus (Relating)** | `venus_sign` | Social grace, values, what feels restorative, aesthetic discernment. | Soulmate predictions, marriage dates, guaranteed relationship success/failure. | **STATIC** (Natal) |
| **6. Mars (Drive)** | `mars_sign` | Conflict instincts, assertiveness pacing, frustration handling, ambition style. | Propensity for violence, physical danger, guaranteed competitive victory. | **STATIC** (Natal) |
| **7. Structural Energy** | `element_primary`, `modality_primary` | Broad energetic baseline, operational tempo, environmental adaptability. | Total personality reductionism, behavioral determinism. | **STATIC** (Natal) |
| **8. Internal Dynamics** | Sign Pairings (e.g. Sun + Moon) | Contradictions between intent and feeling, friction between mask and core. | Severe psychological pathology, deterministic inner torment. | **STATIC** (Natal) |
| **9. Natal Aspects** | Exact angular geometry ($0^\circ, 60^\circ, 90^\circ, 120^\circ, 180^\circ$) | Explicit functional links between psychic functions (e.g. mind vs. drive). | Unalterable curses, guaranteed tragedies, external events. | **STATIC** (Natal) |
| **10. JESTER Verdict** | Chart-level synthesis | Holistically grounded psychological portrait, signature blind spots. | Fatalistic life judgments, clinical assessments. | **STATIC** (Natal) |

---

## 5. SUPPORTED VS. NOT IMPLEMENTED MATRIX

| Subsystem Component | Calculated in Repo? | Exposed in API? | Interpretation Contract? | Content Assets in Corpus? | Architectural Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Sun Identity** | YES | YES | 12 Contracts | 862 Assets (KA: 591, EN: 271) | **ALREADY IMPLEMENTED** |
| **Moon Emotional** | YES | YES | 12 Contracts | 702 Assets (KA: 480, EN: 222) | **ALREADY IMPLEMENTED** |
| **Ascendant Persona** | YES | YES (if time known) | 12 Contracts | 682 Assets (KA: 467, EN: 215) | **ALREADY IMPLEMENTED** |
| **Dominant Element** | YES | YES | 4 Contracts | 215 Assets (KA: 147, EN: 68) | **ALREADY IMPLEMENTED** |
| **Dominant Modality** | YES | YES | 3 Contracts | 191 Assets (KA: 130, EN: 61) | **ALREADY IMPLEMENTED** |
| **Mercury Sign** | YES (in RAM) | NO | 0 Contracts | 0 Assets | **CALCULATED BUT NOT EXPOSED** |
| **Venus Sign** | YES (in RAM) | NO | 0 Contracts | 0 Assets | **CALCULATED BUT NOT EXPOSED** |
| **Mars Sign** | YES (in RAM) | NO | 0 Contracts | 0 Assets | **CALCULATED BUT NOT EXPOSED** |
| **Placidus House Cusps** | YES (12 cusps) | NO | 0 Contracts | 0 Assets | **STORED BUT UNINTERPRETED** |
| **Planetary Retrogrades** | YES (10 flags) | NO | 0 Contracts | 0 Assets | **STORED BUT UNINTERPRETED** |
| **Natal Internal Aspects** | Math exists | NO | 0 Contracts | 0 Assets | **DERIVABLE BUT NOT IMPLEMENTED** |
| **Planet-in-House** | NO | NO | 0 Contracts | 0 Assets | **NOT IMPLEMENTED** |
| **Multi-Placement Combinations** | NO | NO | 0 Contracts | 0 Assets | **NOT IMPLEMENTED** |
| **Unified Narrative Assembler** | NO | NO | 0 Contracts | 0 Assets | **NOT IMPLEMENTED** |

---

## 6. COMBINATION ARCHITECTURE & VALID SYNTHESIS RULES

### The Combinatorial Fallacy
A naive mathematical approach produces staggering numbers:
- Sun $\times$ Moon = $12 \times 12 = 144$ sign combinations.
- Sun $\times$ Moon $\times$ Ascendant = $144 \times 12 = 1,728$ combinations.
- 6 Personal Placements (Sun, Moon, Asc, Mer, Ven, Mar) = $12^6 = 2,985,984$ combinations!

**Blindly creating 1,728 independent astrological meanings is a catastrophic architectural error.** It results in pseudo-scientific micro-distinctions, massive textual duplication, and unmaintainable content databases.

### The Antidote: Deterministic Synthesis Rules
Instead of multiplying every placement into an isolated universe, JESTER defines **3 Legitimate Synthesis Paradigms**:

```
                              DETERMINISTIC SYNTHESIS
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
  RULE TYPE 1:                   RULE TYPE 2:                     RULE TYPE 3:
  ELEMENTAL DYNAMICS             MODAL DYNAMICS                   EXACT NATAL ASPECTS
  (Cross-Element Matrix)         (Operational Conflict)           (Geometric Geometry)
  e.g., Fire Sun + Water Moon    e.g., Cardinal Sun + Fixed Moon  e.g., Sun square Moon (90°)
  = Kinetic-Emotional Friction   = Initiative vs Stubbornness     = Hard Internal Tension
```

#### Synthesis Rule 1: Elemental Luminary Dynamic (16 Pairs)
Rather than 144 independent Sun-Moon texts, evaluate the interaction between the **Sun's Element** and the **Moon's Element**:
- $4 \text{ Elements} \times 4 \text{ Elements} = 16 \text{ Deterministic Structural Dynamics}$.
  - *Fire + Fire:* Unfiltered momentum, rapid emotional expression, low internal resistance.
  - *Fire + Water (Steam):* Volatile emotional friction; intense passion clashing with sudden vulnerability withdrawals.
  - *Earth + Water (Mud/Clay):* Highly fertile, deeply grounded, protective, slow to dislodge.
  - *Air + Earth:* Abstract ideas constrained by pragmatic reality; intellectual perfectionism.

#### Synthesis Rule 2: Luminary-Ascendant Persona Discrepancy (16 Pairs)
Evaluate the relationship between the **Inner Core (Sun Element)** and the **Outer Mask (Ascendant Element)**:
- *Harmonious (Same Element / Compatible):* "What you see is what you get." High presentation transparency.
- *Incongruent (e.g. Water Sun + Fire Ascendant):* Socially aggressive/vibrant exterior masking a highly guarded, vulnerable core. "The Trojan Horse dynamic."

#### Synthesis Rule 3: Exact Angular Natal Aspects (Geometry Grounded)
When two personal placements form an aspect within orb ($<8.0^\circ$ for luminaries):
- *Conjunction ($0^\circ$):* Fusion of psychic drives (e.g., Sun conjunct Mercury = thoughts and identity are indivisible).
- *Square ($90^\circ$) / Opposition ($180^\circ$):* Conscious tension and struggle (e.g., Moon square Mars = emotional impatience, reactive defense).
- *Trine ($120^\circ$) / Sextile ($60^\circ$):* Organic ease, unconscious talent (e.g., Sun trine Moon = harmony between desires and feelings).

### Classification of Proposed Synthesis Rules

| Synthesis Rule | Astrological Basis | Engine Implementation Status | Required Action |
| :--- | :--- | :--- | :--- |
| **Luminary Element Dynamic** (16 pairs) | `sun_sign.element` $\times$ `moon_sign.element` | **DERIVABLE FROM CURRENT DATA** | Needs semantic contract registry & resolver rule |
| **Persona Incongruence** (16 pairs) | `sun_sign.element` $\times$ `ascendant_sign.element` | **DERIVABLE FROM CURRENT DATA** | Needs semantic contract registry & resolver rule |
| **Mercury-Mars Cognitive Drive** (16 pairs) | `mercury_sign.element` $\times$ `mars_sign.element` | **DERIVABLE (Once Mer/Mar exposed)** | Needs Mercury/Mars exposure + contracts |
| **Sun-Moon Natal Aspects** (5 aspect types) | Ecliptic distance between Sun & Moon | **DERIVABLE FROM CURRENT MATH** | Needs internal aspect scanner in `natal.py` |
| **Big Three 1,728 Unique Matrix** | Independent text per $12 \times 12 \times 12$ | **REJECTED (Combinatorial Hallucination)** | DO NOT IMPLEMENT. Assemble via synthesis rules instead. |

---

## 7. THE NARRATIVE ARCHITECTURE ("ME" AS A UNIFIED LIFE DOSSIER)

JESTER will transition away from rendering 5 disconnected, floating cards into a structured, episodic **Personal Life Dossier**.

```
                           THE JESTER PERSONAL DOSSIER
                                      ("ME")
                                        │
    ┌───────────────────────────────────┼───────────────────────────────────┐
    ▼                                   ▼                                   ▼
CHAPTER 1: IDENTITY              CHAPTER 2: INNER LIFE               CHAPTER 3: ENGAGEMENT
• Core Essence (Sun)             • Emotional Reset (Moon)            • Thought Tempo (Mercury)
• Structural Mode (Element/Mod)  • Internal War (Sun ↔ Moon)         • Desire & Grace (Venus)
                                                                     • Combat Style (Mars)
                                                                     • First Contact (Ascendant)
    │                                   │                                   │
    └───────────────────────────────────┼───────────────────────────────────┘
                                        │
                                        ▼
                             CHAPTER 4: SYNTHESIS & VERDICT
                             • Paradoxes & Blind Spots (Tensions)
                             • The Unvarnished JESTER Verdict
```

### Chapter Structure & Grounding Matrix

| Chapter Section | Title (KA / EN) | Astrological Grounding | Engine Status | Output Nature |
| :--- | :--- | :--- | :--- | :--- |
| **Section 1** | **Core Identity** / "ვინ ხარ სინამდვილეში" | Sun Sign + Dominant Element | `SUPPORTED` | Stable baseline vitality & purpose |
| **Section 2** | **Emotional World** / "შენი შინაგანი სივრცე" | Moon Sign + Dominant Modality | `SUPPORTED` | Private emotional security & defense |
| **Section 3** | **How You Think** / "როგორ აზროვნებ და კამათობ" | Mercury Sign | `CALCULATED BUT DISCARDED` | Cognitive speed & debating style |
| **Section 4** | **How You Love** / "როგორ გიყვარს და რა გიზიდავს" | Venus Sign | `CALCULATED BUT DISCARDED` | Relational values & aesthetic attraction |
| **Section 5** | **How You Act** / "როგორ მოქმედებ და იბრძვი" | Mars Sign | `CALCULATED BUT DISCARDED` | Kinetic execution & conflict handling |
| **Section 6** | **The Social Mask** / "როგორ აღგიქვამს სამყარო" | Ascendant Sign (or Graceful Omission) | `SUPPORTED` | Outward armor & initial presence |
| **Section 7** | **Internal Contradictions** / "შენი შინაგანი კონფლიქტები" | Sun-Moon Element Clash / Natal Squares | `DERIVABLE` | Conscious intent vs. subconscious reaction |
| **Section 8** | **Native Strengths** / "შენი ბუნებრივი იარაღი" | Dominant Element + Trine Aspects | `PARTIALLY SUPPORTED` | Organic capabilities & effortless flow |
| **Section 9** | **Friction Patterns** / "სად ისპობ თავს" | Planetary Obstacles / Hard Aspects | `DERIVABLE` | Blind spots, recurring self-sabotage |
| **Section 10** | **The JESTER Verdict** / "JESTER-ის საბოლოო განაჩენი" | Holistic Chart Synthesis | `CONCEPTUAL DESIGN` | Unfiltered, sarcastic, signature verdict |

---

## 8. LONG-FORM CONTENT MODEL (DEPTH ARCHITECTURE)

To serve multiple product surfaces (mobile cards, onboarding reveals, deep profile reading), the content system supports **3 Explicit Depths**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEPTH A: MICRO (1–2 Sentences)                     │
│  Length: 100–250 characters | Format: Punchy, shareable, high-impact hook   │
│  Surfaces: Mobile overview cards, Discover badges, Quick share story        │
├─────────────────────────────────────────────────────────────────────────────┤
│                          DEPTH B: MEDIUM (1–3 Paragraphs)                   │
│  Length: 400–800 characters | Format: Nuanced behavioral analysis           │
│  Surfaces: Standard profile drawer, deep-dive section inspect               │
├─────────────────────────────────────────────────────────────────────────────┤
│                          DEPTH C: DEEP (Multi-Paragraph Narrative)          │
│  Length: 1,000–2,500 characters | Format: Immersive, chaptered exposition   │
│  Surfaces: "Read My Full Dossier" web view, long-form exported PDF/report   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Depth Support by Semantic Layer

| Semantic Layer | Micro Support | Medium Support | Deep Support | Primary Role |
| :--- | :---: | :---: | :---: | :--- |
| **Layer 1: Sun Identity** | YES | YES | YES | Foundational core statement |
| **Layer 2: Moon Emotional** | YES | YES | YES | Subconscious depth exploration |
| **Layer 3: Ascendant Persona** | YES | YES | NO | Social surface portrait |
| **Layer 4: Mercury Cognition** | YES | YES | NO | Intellectual habits breakdown |
| **Layer 5: Venus Relating** | YES | YES | NO | Relational criteria breakdown |
| **Layer 6: Mars Kinetic** | YES | YES | NO | Drive and conflict portrait |
| **Layer 7: Structural Energy** | YES | YES | NO | Energetic baseline framing |
| **Layer 8: Internal Dynamics** | YES | YES | YES | The core contradictory drama |
| **Layer 9: Natal Aspects** | YES | YES | NO | Technical psychic linkages |
| **Layer 10: JESTER Verdict** | YES | YES | YES | Overarching psychological verdict |

---

## 9. JESTER VOICE SYSTEM & DELIVERY MODES

The JESTER personality is neither a warm affirmations coach nor an aggressive bully. It is an **astrologically razor-sharp, satirical observer** who perceives human defense mechanisms and names them with devastating accuracy.

### The 8 JESTER Voice Delivery Dimensions

| Dimension | Icon | Georgian Label | Vocal Attitude & Framing | Example Delivery Focus |
| :--- | :---: | :--- | :--- | :--- |
| **1. Snarky** | 😈 | წაკბენს | Witty, biting, highlights petty hypocrisies with intellectual precision. | "შენ არ ხარ მშვიდი — უბრალოდ სხვებზე მეტი დრო გჭირდება რეაქციისთვის." |
| **2. Mocking** | 😂 | დაგცინის | Amused disbelief at human predictability; laughs at ego posturing. | "ისეთი თავდაჯერებით ამტკიცებ ამას, თითქოს თვითონ მაინც გჯეროდეს." |
| **3. Unfiltered** | 🔥 | თავს არ იკავებს | Cuts through social pleasantries; brutal, unapologetic directness. | "შენი 'სიღრმე' ხშირად უბრალოდ წყენის დიდხანს შენახვის უნარია." |
| **4. Cocky** | 😏 | ზედმეტად თავდაჯერებულია | Radiates superior diagnostic confidence; treats human psyche as solved. | "ვიცი ზუსტად რას იტყვი შემდეგში, ამიტომ პირდაპირ პასუხზე გადავიდეთ." |
| **5. Dramatic** | 🎭 | ყველაფერს აძლიერებს | Operatic amplification of minor quirks into Shakespearean comedy. | "ყოველ დილით სამყაროსთან დუელში გადიხარ, მაშინ როცა ყავა უბრალოდ გაცივდა." |
| **6. Conversational** | 🗣️ | რეალურ ადამიანივით | Intimate, direct, unpretentious late-night bar talk without jargon. | "მოდი სიმართლე ვთქვათ: ეს სტრატეგია კი არა, უბრალოდ სიჯიუტეა." |
| **7. Unexpected** | ⚡ | ვერ ხვდები რას იზამს | Sharp tonal pivot; starts flattering, ends with an intellectual slap. | "გაქვს საოცარი ინტუიცია... რომელსაც მხოლოდ არასწორ მომენტში იყენებ." |
| **8. Sarcastic Jester** | 🃏 | სარკასტული | Canonical JESTER baseline: ironical detachment, playful cynicism. | "შენი დამოუკიდებლობა აღმაფრთოვანებელია, სანამ ვინმე ყურადღებას მოგაკლებს." |

### Conceptual Metadata Schema for Delivery
To support these 8 dimensions cleanly in future schema iterations:
```json
{
  "tone_primary": "snarky",
  "tone_secondary": "unfiltered",
  "intensity": 2,
  "persona": "jester",
  "delivery_mode": "satirical_diagnosis"
}
```
*Rule:* The astrological meaning remains invariant across all 8 tones. A Taurus Moon is steadfast and slow to reset whether delivered Conversational or Mocking.

---

## 10. CONTENT VARIATION ARCHITECTURE & SAFEGUARDS

### Distinguishing the 4 Types of Variation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. ASTROLOGICAL VARIANT                                                     │
│ A genuinely distinct calculated signal.                                     │
│ Example: Sun in Aries (Fire) vs. Sun in Taurus (Earth).                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. SEMANTIC VARIANT                                                         │
│ A different valid psychological facet of the SAME astrological signal.      │
│ Example: Sun in Aries Facet A: "Initiating Impulse"                         │
│          Sun in Aries Facet B: "Low Boredom Threshold"                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. CONTENT VARIANT                                                          │
│ Different copywriting and phrasing expressing the SAME semantic facet.      │
│ Example: Variant 1 (Metaphor: Sparks & Gasoline)                            │
│          Variant 2 (Metaphor: Unfinished Sprints)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. TONE VARIANT                                                             │
│ Different JESTER vocal delivery modes for the SAME content asset.           │
│ Example: Snarky Delivery vs. Conversational Delivery.                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Deterministic Asset Selection Algorithm
To prevent AI hallucination and runtime randomness while delivering endless fresh variety:
1. Every content asset possesses an immutable `asset_id` and tags.
2. Given a user's deterministic signal and a requested depth/tone, the resolver constructs a deterministic selection key:
   $$\text{Seed} = \text{SHA256}(\text{user\_id} + \text{interpretation\_id} + \text{depth} + \text{tone})$$
3. The resolver selects the asset via modulo index over available approved assets:
   $$\text{Index} = \text{Seed} \pmod{\text{len(approved\_assets)}}$$
4. *Result:* The text is 100% reproducible for the user, completely free of runtime LLM hallucination, yet feels uniquely tailored.

### Hard Safeguards Against Astrological Hallucination
- **No Medical / Diagnostic Claims:** Strictly prohibited from diagnosing psychiatric disorders (e.g. ADHD, BPD, Depression) under the guise of astrology.
- **No Fate / Fortune Telling:** No predictions of specific events, financial windfalls, or calendar death/marriage dates.
- **No Jargon Clutter:** Forbid terms like "trine", "quincunx", "12th house", "midheaven" in user-facing prose. Speak purely in observable human behaviors.
- **The "Insufficient Basis" Circuit Breaker:** If a user has an unknown birth time, JESTER strictly outputs:
  `[INSUFFICIENT_ASTROLOGICAL_BASIS: ascendant_unknown]`
  rather than fabricating a generic persona.

---

## 11. PROVENANCE ARCHITECTURE

Every string presented in JESTER's "ME" narrative must possess an unbroken, verifiable audit trail back to physical astronomy:

```text
[PROVENANCE CHAIN AUDIT TRAIL]

User Reads Sentence:
"შენი გონება ყოველთვის სამი ნაბიჯით წინ გარბის, მაგრამ როცა გადაწყვეტილების მიღებაზე
მიდგება საქმე, უეცრად დეტალებში იკარგები."
      │
      ▼
Content Asset ID: `ca_self_cog_gem_vir_001_ka_snarky_a`
      │
      ▼
Interpretation Contract: `self.cognition.mercury_gemini_contrast.v1`
      │
      ▼
Semantic Rule: `Cognitive Synthesis: Mercury in Gemini + Virgo Modality Dominance`
      │
      ▼
Deterministic Signals:
  • `mercury_sign: gemini` (Longitude: 74.321948°)
  • `modality_primary: mutable` (Weighted score: 8.0)
      │
      ▼
Engine Calculation:
  • `backend/app/astrology/natal.py:recalculate_user_astrology()`
  • `backend/app/astrology/calculator.py:compute_natal_placements()`
      │
      ▼
Astronomical Source:
  • Swiss Ephemeris (`swe.calc_ut(jd=2459000.5, planet=swe.MERCURY)`)
  • Birth Data: `1990-05-15 14:30:00+04:00, 41.7151°N, 44.8271°E` (User-Owned Private)
```

If any link in this chain cannot be established, **the text is invalid and must not be served.**

---

## 12. EXISTING CORPUS MAPPING (`self.*`)

A forensic extraction of `backend/app/interpretation/data/content_corpus.json` reveals the exact current inventory:

```
Total Assets in System: 7,363
Total "self.*" Assets:  2,652 (36.0% of entire repository corpus)
  ├── Georgian (ka):    1,815 assets (68.4%)
  └── English (en):       837 assets (31.6%)
```

### Forensic Distribution Across the 43 Contracts

```
CATEGORY BREAKDOWN:
• self.identity.* (12 Sun signs):      862 assets (ka: 591, en: 271)  | Avg: 49.2 ka/contract
• self.emotional.* (12 Moon signs):    702 assets (ka: 480, en: 222)  | Avg: 40.0 ka/contract
• self.persona.* (12 Rising signs):    682 assets (ka: 467, en: 215)  | Avg: 38.9 ka/contract
• self.element.* (4 Dominant elem):    215 assets (ka: 147, en: 68)   | Avg: 36.8 ka/contract
• self.modality.* (3 Dominant modal):  191 assets (ka: 130, en: 61)   | Avg: 43.3 ka/contract
```

### Critical Forensic Insights on Current Corpus
1. **Asset Status:** **100% of all 2,652 assets are marked `ai_draft`**. Exactly **0** assets have reached `approved` or `winner` status.
2. **Length Profile:** Average text length in Georgian is **194.8 characters** (min: 53, max: 280).
   - *Verdict:* The entire existing corpus is strictly **MICRO DEPTH** (1–2 sentences).
   - *Gap:* Zero Medium-depth (1–3 paragraphs) or Deep-depth (narrative) assets currently exist.
3. **Tone Bias:**
   - `witty`: 657 (36.2%)
   - `playful`: 539 (29.7%)
   - `soft`: 407 (22.4%)
   - `savage`: 144 (7.9%)
   - `bold`: 68 (3.7%)
   - *Verdict:* Current copy heavily skews toward gentle and playful banter; biting, unfiltered, and dramatic JESTER voices are severely under-covered.

---

## 13. CONTENT SCALE CALCULATION

To avoid arbitrary numbers ("we need 10,000 texts"), future content requirements are derived via a strict combinatorial formula based purely on engine capabilities:

### The Mathematical Formula

$$\text{Volume} = \sum_{\text{Layer}} \left( N_{\text{Signals}} \times N_{\text{Facets}} \times N_{\text{Depths}} \times N_{\text{Tones}} \times N_{\text{Variants}} \right)$$

Where:
- $N_{\text{Signals}}$: Count of distinct astrological signals in that layer.
- $N_{\text{Facets}}$: Valid semantic angles per signal (typically 2: Light/Strength vs. Shadow/Friction).
- $N_{\text{Depths}}$: Required formats (Micro, Medium, Deep).
- $N_{\text{Tones}}$: Target JESTER tones selected for that layer.
- $N_{\text{Variants}}$: Paraphrasing variants for non-repetition (typically 2–3).

### Layer-by-Layer Signal Base
1. **Base Layer 1–3 (Sun, Moon, Ascendant):** $12 + 12 + 12 = 36$ signals.
2. **Base Layer 4–6 (Mercury, Venus, Mars - Once Exposed):** $12 + 12 + 12 = 36$ signals.
3. **Base Layer 7 (Elements & Modalities):** $4 + 3 = 7$ signals.
4. **Synthesis Layer 8 (Luminary Elemental Dynamics):** $4 \times 4 = 16$ structural pairs.
5. **Synthesis Layer 8b (Persona-Core Incongruence):** $4 \times 4 = 16$ structural pairs.
6. **Synthesis Layer 9 (Core Natal Aspects):** 10 primary personal aspect types (Sun-Moon, Sun-Mars, Moon-Mars, etc.).
7. **Synthesis Layer 10 (JESTER Verdicts):** 12 elemental-modal archetype syntheses.

$$\text{Total Grounded Semantic Targets} = 36 + 36 + 7 + 16 + 16 + 10 + 12 = \mathbf{133 \text{ Unique Astrological Targets}}$$

---

## 14. MINIMUM / PRODUCTION / HIGH-DIVERSITY ESTIMATES

Using the derived 133 semantic targets, we calculate precise scale benchmarks:

| Target Tier | Facets / Signal | Depths Supported | Active Tones | Variants / Tone | Formulas & Math | Target Georgian Assets |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| **Tier 1: MVP / Minimal Viable** | 1 | Micro only (1) | 2 (Witty, Snarky) | 2 | $133 \times 1 \times 1 \times 2 \times 2$ | **532** |
| **Tier 2: Good Production** | 2 | Micro (1) + Medium (1) | 4 (Snarky, Mocking, Unfiltered, Conversational) | 2 | $133 \times 2 \times 2 \times 4 \times 2$ | **4,256** |
| **Tier 3: High-Diversity Corpus** | 3 | Micro (1) + Medium (1) + Deep (1) | 6 Tones | 3 | $133 \times 3 \times 3 \times 6 \times 3$ | **21,546** |

### Immediate Priority Target: Tier 2 (Good Production)
Targeting **~4,200 Grade-A approved Georgian assets** across the 133 legitimate semantic targets achieves deep diversity, zero hallucination, and full narrative continuity across all 10 chapters.

---

## 15. EXACT IMPLEMENTATION GAPS (CODE & DATABASE)

The following specific engineering changes are required before the semantic architecture can reach full maturity:

1. **Database Migration (`public.astro_safe_profile`):**
   - Add columns: `mercury_sign TEXT`, `venus_sign TEXT`, `mars_sign TEXT`.
   - Update `natal.py:recalculate_user_astrology()` to persist these signs (they are already computed in lines 126–128!).
2. **Pydantic Model Updates (`backend/app/astrology/models.py`):**
   - Add `mercury_sign`, `venus_sign`, `mars_sign` to `SafeDerivedAstrology` and `SafeDerivedAstrologyResponse`.
3. **Contract Registry Expansion (`backend/app/interpretation/contracts.py`):**
   - Register 36 new contracts:
     - 12 `self.cognition.mercury_*`
     - 12 `self.relating.venus_*`
     - 12 `self.action.mars_*`
   - Register 16 `self.synthesis.element_dynamic.*` contracts.
4. **Narrative Aggregator Engine (`backend/app/interpretation/engine.py`):**
   - Replace the naive 5-element array in `resolve_natal_narrative()` with a chapter-based `NatalDossierResponse` containing structured sections.
5. **Natal Internal Aspect Scanner (Optional Phase 3.5):**
   - Create a single-chart aspect detection function leveraging existing `detect_aspect()` in `aspects.py` to identify personal planet aspects within user's chart.

---

## 16. EXACT CONTENT GAPS (EDITORIAL & CORPUS)

1. **Depth Vacuum:** 100% of current `self.*` assets are short micro-cards (~195 chars). Zero medium or deep narrative copy exists.
2. **Personal Planet Omission:** Exactly 0 assets exist for Mercury (Thinking), Venus (Loving), and Mars (Acting).
3. **Tone Imbalance:** Over 88% of current Georgian text is soft/playful/witty. Snarky, unfiltered, dramatic, and sarcastic delivery modes need aggressive expansion.
4. **Zero Synthesis Assets:** No text currently exists that addresses the friction between a user's Sun and Moon or Core and Mask.
5. **Review Status:** 100% of existing assets are unreviewed `ai_draft`.

---

## 17. RECOMMENDED IMPLEMENTATION ORDER

```
PHASE 3.1: FOUNDATION (Zero Astrology Invention)
├── 1. Expose Mercury, Venus, Mars in astro_safe_profile (migration + natal.py)
├── 2. Register 36 contracts for Mercury, Venus, Mars
└── 3. Register 16 Luminary Elemental Synthesis contracts

PHASE 3.2: NARRATIVE BACKEND & CONTRACT WIRING
├── 4. Design NatalDossierResponse Pydantic schema
├── 5. Wire chapter assembler in InterpretationEngine
└── 6. Implement deterministic seed-based resolver for ME

PHASE 3.3: EDITORIAL REVIEW & HIGH-TIER ASSET CREATION
├── 7. Audit & graduate top Grade-A micro assets from ai_draft to approved
├── 8. Author Medium-depth assets for Core, Emotions, Cognition, Relating, Drive
└── 9. Author Synthesis assets for the 16 Elemental Dynamics & JESTER Verdicts

PHASE 3.4: FRONTEND DOSSIER UI
├── 10. Upgrade MePage.tsx from 5 disconnected cards to Chaptered Dossier
└── 11. Add Depth toggle (Summary / Deep Narrative)
```

---

## 18. EXPLICIT LIST OF THINGS WE MUST NOT IMPLEMENT YET

To maintain rock-solid discipline and prevent scope corruption:

- ❌ **DO NOT generate new content copy yet.**
- ❌ **DO NOT modify Swiss Ephemeris calculations or alter `calculator.py`.**
- ❌ **DO NOT modify Synastry V1 calculations, scoring, or orbs.**
- ❌ **DO NOT create 1,728 individual Big Three text files.**
- ❌ **DO NOT touch transit calculations or Daily Energy yet.**
- ❌ **DO NOT expose raw longitudes or house cusps to the frontend.**
- ❌ **DO NOT introduce LLMs at runtime to dynamically invent natal claims.**

---

### FINAL ARCHITECTURAL PRINCIPLE

> **JESTER's "ME" intelligence will feel deeply personal not because we generated thousands of generic sentences, but because JESTER understands real deterministic natal signals and their legitimate geometric relationships.**
>
> **ASTROLOGY DETERMINES THE TRUTH.**  
> **JESTER DETERMINES THE VOICE.**  
> **VARIATION DETERMINES THE SELECTION.**  
> **TRUTH > VARIETY.**
