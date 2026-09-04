# JESTER DEEP ANALYSIS CAPABILITY
**Comprehensive Technical Blueprint: What Powers "One Deep Unlock" in Jester V1**  
**Date:** September 2026  
**Auditor:** Senior Backend Architect  

---

## 1. THE CORE ARCHITECTURAL QUESTION

> **"If we wanted to implement JESTER V1's Deep Unlock tomorrow, what can the current backend already provide without changing the astrology engine?"**

This document details the exact, verifiable data and calculations available in the Jester codebase to power a **Deep Relationship Analysis of Person B**.

---

## 2. THE CURRENT DEEP PIPELINE & DATA INVENTORY

When Person A and Person B are compared, the backend executes the Synastry V1 Engine (`synastry-v1.0.0`). The pipeline generates rich, multi-layered relational intelligence, but segregates it into three distinct exposure tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                    CALCULATED SYNASTRY INTELLIGENCE                   │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  TIER 1: EXPOSED │       │ TIER 2: INTERNAL │       │  TIER 3: MISSING │
│  IN CURRENT API  │       │ DATABASE/ENGINE  │       │  NOT IMPLEMENTED │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ Overall Score    │       │ 4 Dimensions*    │       │ AI/LLM Narrative │
│ 6 Ranked Signals │       │ Evidence Trace   │       │ House Overlays   │
│ 4 Bridge Topics  │       │ Subscore Points  │       │ Daily Transits   │
│ 3 Starters       │       │ Exact Orbs/Deg   │       │ Chiron/Nodes     │
│ Data Quality     │       │ Pair Weights     │       │ Unlock Ledger    │
└──────────────────┘       └──────────────────┘       └──────────────────┘
* Dimensions calculated on first run, but dropped on cache hit in API response.
```

---

## 3. DETAILED DATA COMPOSITION OF ONE DEEP UNLOCK

### Component 1: The Core Compatibility Index & Data Quality
* **Overall Score (`score`):** Float between `10.0` and `98.0` (with `65.0` as baseline). Normalized via non-linear curve stretch ($0.85$ power curve) to provide dynamic differentiation without clustering at extremes.
* **Confidence Level (`data_quality.confidence`):**
  * `1.0`: Exact birth times known for both users.
  * `0.85`: Approximate birth time for at least one user.
  * `0.75`: Unknown birth time for at least one user (Ascendants omitted; planets set to 12:00 UTC).
  * `0.50`: Minimum evidence rule triggered (total active aspect weight $< 2.0$).
* **Ascendant Used (`data_quality.ascendant_used`):** Boolean indicating whether relational identity axis was incorporated into the math.

### Component 2: The 4 Relational Dimensions (Internal Engine Output)
The engine deterministically computes 4 discrete relational subscores $[0.0, 100.0]$:
1. **Emotional Harmony (`emotional_harmony`):**
   * *Formula:* $50.0 + \Delta_{\text{harmony}} + 0.35 \times (\text{ElementHarmony} - 50.0)$.
   * *Drivers:* Sun-Moon trines/sextiles/conjunctions, Moon-Venus affinities, Water/Earth elemental ease, Saturn stabilizing trines.
2. **Communication & Intellectual Flow (`communication`):**
   * *Formula:* $50.0 + \Delta_{\text{comm}} + 0.25 \times (\text{MercuryElementHarmony} - 50.0)$.
   * *Drivers:* Mercury-Mercury aspects, Sun-Mercury alignments, Air element dominance, mutual cognitive rhythms.
3. **Magnetic Chemistry & Attraction (`attraction`):**
   * *Formula:* $50.0 + \Delta_{\text{attraction}} + 0.20 \times (\text{FireAirSynergy} - 50.0)$.
   * *Drivers:* Venus-Mars conjunctions/oppositions/trines, Sun-Moon polarities, Venus-Pluto intensity, Fire/Air elemental count.
4. **Growth, Endurance & Dynamic Friction (`growth_long_term`):**
   * *Formula:* $50.0 + \Delta_{\text{growth}} + 0.25 \times (\text{ModalityBalance} - 50.0)$.
   * *Drivers:* Saturn structuring contacts, challenging squares/oppositions, Cardinal/Fixed/Mutable complementary balance.

### Component 3: Top 6 Ranked Relational Signals (Exposed in API)
Up to 6 signals selected based on highest mathematical importance ($\text{Weight} \times \text{Strength}$). Each signal contains:
* `type`: Unique machine identifier (e.g. `sun_trine_moon`, `venus_conjunction_mars`, `mars_square_saturn`).
* `category`: Relational dynamic classification (`harmony`, `attraction`, `communication`, `growth`, `stability`, `notice`).
* `strength`: Signal intensity level (`high` if aspect strength $\ge 0.70$; `medium` otherwise).
* `label`: Curated human-readable title (e.g. `"Emotional Resonance"`, `"Magnetic Chemistry"`, `"Pacing Tension"`, `"Core Harmony"`).
* `source_aspects`: Exact astronomical pairing and orb (e.g. `["Sun Trine Moon (Orb 1.2°)"]`, `["Venus Conjunction Mars (Orb 0.8°)"]`).

### Component 4: Complete Astronomical Evidence Trace (Stored in DB `compatibility_results.evidence_trace`)
The exact mathematical ledger of every active cross-aspect. This contains 10 to 25 detailed aspect entries:
* `planet_a` & `planet_b`: Celestial bodies involved (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Ascendant).
* `lon_a` & `lon_b`: Exact ecliptic longitudes (rounded to 2 decimals).
* `aspect`: Aspect type (`conjunction`, `sextile`, `square`, `trine`, `opposition`).
* `target_angle`: $0^\circ, 60^\circ, 90^\circ, 120^\circ, 180^\circ$.
* `actual_distance`: Shortest arc distance in degrees $[0, 180]$.
* `orb_diff`: Exact variance from perfect aspect in degrees.
* `max_orb`: Maximum permissible orb (expands $+2.0^\circ$ for luminaries; capped at $6.0^\circ$ for Ascendant).
* `strength`: Quadratic decay score $S = (1.0 - \text{orb} / \text{max\_orb})^2 \in [0.0, 1.0]$.
* `weight`: Tier weight ($3.0$ for Luminaries/Venus-Mars; $2.0$ for Mercury/Personal; $1.0$ for Jupiter/Saturn; $0.5$ for Outer).
* `subscore_contributions`: Exact positive or negative points contributed to `harmony`, `communication`, `attraction`, and `growth`.

### Component 5: Elemental & Modality Resonance Matrix (Derived from Placements)
* **Elemental Harmony Score:** Calculated pairwise across Person A's and Person B's Sun and Moon elements (Same element: 80 pts; Fire+Air: 70 pts; Earth+Water: 70 pts; Air+Water: 45 pts; Fire+Earth: 45 pts; Earth+Air: 35 pts; Fire+Water: 35 pts).
* **Mercury Cognitive Compatibility:** Independent elemental alignment of Person A's Mercury sign with Person B's Mercury sign.
* **Fire/Air Kinetic Count:** Sum of Sun and Moon placements in Fire and Air across both charts (determines conversational and physical energy).
* **Modality Dynamic:** Sun sign modality match vs contrast (Cardinal initiates, Fixed stabilizes, Mutable adapts; contrast awards 60 pts, identical awards 50 pts for growth).

### Component 6: Curated Bridge Topics & Starters (Exposed in API)
* **4 Shared Bridge Topics:** Deterministically mapped from dominant element and aspect patterns:
  * Air: Books, Philosophy, Ideas, Creative Work
  * Fire: Travel, Adventure, Fitness, Ambition
  * Water: Art, Music, Psychology, Cinema
  * Earth: Architecture, Food, Design, Lifestyle
* **3 Curated Icebreaker Starters:** Contextual question prompts directly linked to the pair's highest-strength aspect signals.

---

## 4. WHAT DOES NOT EXIST IN THE BACKEND TODAY

To maintain absolute architectural integrity, the following features are confirmed **NON-EXISTENT**:
1. **AI / LLM Narrative Generation ("Jester Voice"):** The `backend/app/interpretation/` directory contains empty files. There is NO LLM API key, NO prompt execution, and NO generative text model active.
2. **House Overlay Calculations:** The engine does not place Person A's planets into Person B's natal houses (e.g. "His Mars in her 8th house").
3. **Daily / Transit Relationship Forecasts:** `transits.py` and `jobs/daily_energy.py` are non-functional stubs.
4. **Paywall / Entitlement Gatekeeper:** There is no database record, token ledger, coin system, or in-app purchase validation to unlock a deep result.
5. **Public / Unauthenticated Deep Result Sharing:** Deep results cannot be shared via public URL because all compatibility routes require a Supabase JWT Bearer token and active connection membership.

---

## 5. THE CRITICAL GATEKEEPER CONSTRAINT (FRONTEND BLOCKER)

Currently, the compatibility routes in `backend/app/comparisons/router.py`:
```python
@router.post("/compare")
@router.get("/people/{target_user_id}/why")
```
Enforce this check at line 42:
```python
cur.execute("SELECT public.has_active_connection(%s, %s) as is_active;", (user_a, user_b))
if not res or not res["is_active"]:
    raise ForbiddenException("Active connection required to view compatibility")
```

### Impact on Product Flow:
* **Current Behavior:** A user **CANNOT** run a Deep Analysis or view compatibility on a discovered profile unless:
  1. User A sends a connection request (`POST /v1/connections`).
  2. User B accepts the connection request (`POST /v1/connections/{id}/transition` with `action="accept"`).
* **If Deep Unlock is meant for ANY Discovered User:** This backend restriction must be relaxed or supplemented with a dedicated Deep Unlock endpoint that allows unidirectional analysis of any discoverable user.

---

## 6. ACTIONABLE BACKEND ADJUSTMENTS REQUIRED (NO ENGINE CHANGES)

To deliver a rich, state-of-the-art Deep Analysis to the frontend immediately:

### Step 1: Fix Router Cache-Hit Dimension Drop (Small Fix)
* In `backend/app/comparisons/router.py` (line 97), when returning an existing `compatibility_results` row from database, `dimensions` is omitted from the Pydantic instantiation.
* Either store `dimensions` in a JSONB column in `public.compatibility_results`, or populate it from subscores.

### Step 2: Expose `evidence_trace` in API Response (Small Fix)
* The JSONB column `evidence_trace` already exists in `public.compatibility_results` (Migration 021) and is populated by `CompatibilityEngine.calculate()`.
* Add `evidence_trace: list[dict[str, Any]] = Field(default_factory=list)` to `StructuredCompatibilityResponse` in `backend/app/comparisons/models.py`.

### Step 3: Support Unlocked Compatibility for Non-Connected Users (Design Decision)
* Provide an endpoint (or query parameter) that calculates synastry between `current_user` and `target_user` without requiring `status = 'accepted'` in `connections`, provided `target_user.is_discoverable = true`.

---

## 7. PROPOSED JSON PAYLOAD SCHEMA: "ONE DEEP UNLOCK"

```json
{
  "target_user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "target_profile": {
    "display_name": "Maya Lin",
    "avatar_url": "https://storage.jester.app/avatars/maya.jpg",
    "bio": "Urbanist & speculative fiction writer",
    "city": "Copenhagen",
    "occupation": "Urban Designer",
    "sun_sign": "Aquarius",
    "moon_sign": "Sagittarius",
    "ascendant_sign": "Gemini",
    "element_primary": "Air",
    "modality_primary": "Mutable"
  },
  "overall_compatibility": {
    "score": 91.4,
    "confidence": 1.0,
    "time_precision": "exact",
    "ascendant_included": true
  },
  "dimensional_breakdown": {
    "emotional_harmony": {
      "score": 88.5,
      "summary": "High natural ease and mutual understanding"
    },
    "communication": {
      "score": 96.2,
      "summary": "Exceptional intellectual resonance and rapid ideation"
    },
    "attraction": {
      "score": 84.0,
      "summary": "Playful, kinetic chemistry with sustained interest"
    },
    "growth_long_term": {
      "score": 79.8,
      "summary": "Stimulating differences that prompt constructive evolution"
    }
  },
  "top_relational_signals": [
    {
      "type": "mercury_trine_mercury",
      "category": "communication",
      "strength": "high",
      "label": "Intellectual Flow",
      "source_aspect": "Mercury Trine Mercury (Orb 1.4°)"
    },
    {
      "type": "sun_sextile_moon",
      "category": "harmony",
      "strength": "high",
      "label": "Emotional Resonance",
      "source_aspect": "Sun Sextile Moon (Orb 0.9°)"
    },
    {
      "type": "venus_trine_mars",
      "category": "attraction",
      "strength": "high",
      "label": "Magnetic Chemistry",
      "source_aspect": "Venus Trine Mars (Orb 2.1°)"
    }
  ],
  "elemental_modality_synergy": {
    "element_harmony_score": 80.0,
    "fire_air_kinetic_synergy": 65.0,
    "modality_balance_score": 60.0,
    "mercury_synergy_score": 80.0
  },
  "conversational_bridges": {
    "suggested_topics": ["books", "philosophy", "ideas", "creative_work"],
    "curated_starters": [
      "What topic could you talk about for hours without getting bored?",
      "What is something that instantly makes you feel understood?",
      "What art or music has inspired you recently?"
    ]
  },
  "astronomical_evidence_grid": [
    {
      "planet_a": "mercury",
      "planet_b": "mercury",
      "aspect": "trine",
      "angle": 120.0,
      "orb": 1.4,
      "strength": 0.7744,
      "contributions": {
        "communication": 2.32
      }
    },
    {
      "planet_a": "sun",
      "planet_b": "moon",
      "aspect": "sextile",
      "angle": 60.0,
      "orb": 0.9,
      "strength": 0.8836,
      "contributions": {
        "harmony": 2.65,
        "communication": 2.65
      }
    }
  ]
}
```
