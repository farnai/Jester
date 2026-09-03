# JESTER SYNASTRY V1 — Mathematical & Engine Specification

**Document Type:** Engineering & Mathematical Specification  
**Engine Version:** `synastry-v1.0.0`  
**Parent Product Spec:** [`docs/PRODUCT_SPECIFICATION.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/PRODUCT_SPECIFICATION.md)  
**Status:** Authoritative Specification (Frozen)

---

## 1. Purpose

This document is the authoritative mathematical, architectural, and algorithmic specification for the **Jester Synastry V1** compatibility engine.

The purpose of Synastry V1 is to compare the astronomical natal placement data of two users (Person A and Person B), compute cross-chart planetary aspects, evaluate elemental and modality balances, and derive:
1. A multi-dimensional compatibility model (4 internal sub-scores).
2. A normalized, deterministic composite overall compatibility score ($10.0 - 98.0$).
3. Structured, machine-readable relationship signals (e.g. `sun_trine_moon`, `venus_conjunction_mars`).
4. Recommended conversation topics and rule-based conversation starters.
5. Audit evidence traces and data-quality indicators.

All calculations defined in this document are **100% deterministic**, **reproducible**, **symmetric**, and **completely decoupled from AI/LLM interpretation layers**.

---

## 2. Scope

### In Scope for Synastry V1:
- Inter-chart aspect detection for 10 core planetary bodies (Sun to Pluto) + Ascendant (when available).
- Quadratic orb strength decay and planet-pair weight matrices.
- Multi-dimensional scoring ($S_{\text{harmony}}$, $S_{\text{attraction}}$, $S_{\text{communication}}$, $S_{\text{growth}}$).
- Element and modality balance matrices.
- Score normalization, inflation controls, and influence capping.
- Unknown and approximate birth-time resilience with confidence indicators.
- Symmetrical evaluation ($f(A, B) \equiv f(B, A)$).
- Automatic birth-data version cache invalidation.

### Out of Scope for Synastry V1:
- Extended celestial bodies (Chiron, Lilith, Nodes, Asteroids).
- Minor aspects (Quincunx, Semi-Sextile, Quintile).
- House overlays (deferred to V1.1).
- OpenAI / LLM text generation (handled separately in `interpretation/`).

---

## 3. Existing-System Audit & Implementation Status

A direct code and database audit of the repository reveals the current implementation status:

| Subsystem / Feature | Location | Code Reality / Status | Implementation Note |
| :--- | :--- | :--- | :--- |
| **Natal Planetary Ephemeris** | `backend/app/astrology/calculator.py` | `IMPLEMENTED`. Computes 10 main planets, retrogrades, Placidus houses, and Ascendant. | Longitudes used as input. |
| **Birth Data Versioning** | `supabase/migrations/015_triggers.sql` | `IMPLEMENTED`. `birth_data.data_version` auto-increments via trigger on parameter changes. | Triggers stale cache recalculation. |
| **Canonical User Pairs** | `backend/app/connections/router.py` | `IMPLEMENTED`. Enforces `user_a_id < user_b_id` sorting. | Primary key in DB storage. |
| **Connection & RLS Guards** | `supabase/migrations/018_rls.sql` | `IMPLEMENTED`. `public.has_active_connection` and `public.is_user_blocked` active. | Access guard in API & DB. |
| **Aspect Calculation Math** | `backend/app/astrology/aspects.py` | `IMPLEMENTED`. Quadratic decay, 5 major aspects, luminary boost, Ascendant cap. | Verified by 17 unit tests. |
| **Synastry Overlay Math** | `backend/app/compatibility/synastry.py`| `IMPLEMENTED`. 4 sub-scores, dynamic signals, topics, starters, normalization. | Verified by 8 unit tests. |
| **Compatibility Service** | `backend/app/compatibility/engine.py` | `IMPLEMENTED`. Service layer connecting DB & `SynastryEngine`. | Fully operational. |
| **Compatibility Router** | `backend/app/comparisons/router.py` | `IMPLEMENTED`. `/v1/compare` and `/v1/people/{id}/why` run Synastry V1 engine. | Cached per canonical pair. |


---

## 4. Input Contract

The Synastry V1 Engine consumes two structured natal payloads (`PersonA` and `PersonB`):

```python
class NatalInputPayload(BaseModel):
    user_id: uuid.UUID
    birth_data_version: int
    birth_time_precision: Literal["exact", "approximate", "unknown"]
    planet_longitudes: dict[str, float]  # Sun..Pluto in [0, 360)
    ascendant_longitude: float | None    # in [0, 360) or None
    retrogrades: dict[str, bool]         # planet_name -> is_retrograde
```

### Birth Time Precision Handling Rules:
1. **`exact`**: Full calculation including Ascendant (if coordinates exist). Data confidence = `1.00`.
2. **`approximate`**: Ascendant used if available, but Ascendant aspect weights are scaled by `0.50`. Data confidence = `0.85`.
3. **`unknown`**: `ascendant_longitude` is `None`. Ascendant aspects and house-based logic are strictly omitted. Calculation proceeds using the 10 planetary longitudes. Data confidence = `0.75`.

---

## 5. Supported Bodies

### Included Celestial Bodies (11 Total):
1. **Sun** (`sun`)
2. **Moon** (`moon`)
3. **Mercury** (`mercury`)
4. **Venus** (`venus`)
5. **Mars** (`mars`)
6. **Jupiter** (`jupiter`)
7. **Saturn** (`saturn`)
8. **Uranus** (`uranus`)
9. **Neptune** (`neptune`)
10. **Pluto** (`pluto`)
11. **Ascendant** (`ascendant`, conditionally available)

*Scope Freeze*: Chiron, Lilith, North Node, South Node, Asteroids, and Midheaven are **EXCLUDED** from Synastry V1.

---

## 6. Aspect Model Specifications

### Angular Distance & Wraparound
For any two longitudes $L_A, L_B \in [0^\circ, 360^\circ)$:
$$\Delta\theta = |L_A - L_B|$$
$$d = \min(\Delta\theta, 360^\circ - \Delta\theta)$$

### Supported Aspect Angles ($\theta_T$):
- **Conjunction** ($0^\circ$)
- **Sextile** ($60^\circ$)
- **Square** ($90^\circ$)
- **Trine** ($120^\circ$)
- **Opposition** ($180^\circ$)

---

## 7. Orb Model & Maximum Tolerances

An aspect is active if the orb deviation $\delta = |d - \theta_T| \le \text{Orb}_{\text{max}}$.

### Base Maximum Orbs ($\text{Orb}_{\text{base}}$):
- **Conjunction ($0^\circ$)**: $8.0^\circ$
- **Opposition ($180^\circ$)**: $8.0^\circ$
- **Trine ($120^\circ$)**: $8.0^\circ$
- **Square ($90^\circ$)**: $7.0^\circ$
- **Sextile ($60^\circ$)**: $6.0^\circ$

### Dynamic Orb Modifiers:
- **Luminary Boost**: If either body in the pair is the Sun or Moon, add $+2.0^\circ$ to $\text{Orb}_{\text{base}}$ (e.g. Sun-Moon Conjunction max orb $= 10.0^\circ$).
- **Ascendant Constraint**: If either body is the Ascendant, max orb is capped at $6.0^\circ$.

---

## 8. Aspect Strength Formula

Aspect strength $S_{\text{aspect}} \in [0.0, 1.0]$ uses a **quadratic decay function**:

$$S_{\text{aspect}} = \left(1.0 - \frac{\delta}{\text{Orb}_{\text{max}}}\right)^2$$

### Mathematical Properties:
- Exact aspect ($\delta = 0.0^\circ$) $\implies S_{\text{aspect}} = 1.00$.
- Halfway orb ($\delta = 0.5 \times \text{Orb}_{\text{max}}$) $\implies S_{\text{aspect}} = 0.25$.
- Edge of orb ($\delta = \text{Orb}_{\text{max}}$) $\implies S_{\text{aspect}} = 0.00$.
- *Rationale*: Quadratic decay eliminates out-of-orb noise while giving strong emphasis to tight aspects.

---

## 9. Planet-Pair Weighting Matrix ($W_{\text{pair}}$)

The weight $W_{\text{pair}}$ reflects the interpersonal significance of planet pairs:

| Planet Pair Category | Specific Pair Cross-Matches | Weight ($W_{\text{pair}}$) |
| :--- | :--- | :--- |
| **Tier 1: Luminaries & Core Romance** | Sun-Sun, Sun-Moon, Moon-Moon, Sun-Venus, Moon-Venus, Venus-Mars | **3.0** |
| **Tier 2: Personal Communication & Drive** | Mercury-Mercury, Sun-Mercury, Moon-Mercury, Venus-Venus, Mars-Mars, Sun-Mars, Moon-Mars, Mercury-Venus | **2.0** |
| **Tier 3: Social & Structural Growth** | Sun-Jupiter, Moon-Jupiter, Venus-Jupiter, Sun-Saturn, Moon-Saturn, Venus-Saturn, Mars-Jupiter, Mars-Saturn | **1.0** |
| **Tier 4: Transpersonal Dynamics** | Outer planet cross-aspects (Uranus, Neptune, Pluto with personal planets) | **0.5** |
| **Tier 5: Ascendant Pairings** | Sun-Asc, Moon-Asc, Venus-Asc, Mars-Asc (if present) | **2.0** (or $1.0$ if approx) |

---

## 10. Aspect Base Weights ($W_{\text{aspect\_type}}$)

- **Conjunction ($0^\circ$)**: $1.00$
- **Trine ($120^\circ$)**: $0.90$
- **Opposition ($180^\circ$)**: $0.85$
- **Square ($90^\circ$)**: $0.75$
- **Sextile ($60^\circ$)**: $0.70$

---

## 11. Interaction Polarity & Multi-Dimensional Mapping

Aspects do NOT map to binary "good/bad" values. They map into **4 multidimensional sub-scores**:

$$\text{Effect}_{\text{aspect}} = W_{\text{pair}} \times W_{\text{aspect\_type}} \times S_{\text{aspect}}$$

### Dimension Mapping Rules:
1. **Trines & Sextiles**: Add positive points ($+\text{Effect}$) to $S_{\text{harmony}}$ and $S_{\text{communication}}$.
2. **Venus-Mars / Sun-Moon / Venus-Pluto Aspects**: Add positive points ($+\text{Effect}$) to $S_{\text{attraction}}$.
3. **Squares ($90^\circ$)**: Add $+\text{Effect}$ to $S_{\text{growth}}$ (dynamic tension) and $+\text{Effect} \times 0.6$ to $S_{\text{attraction}}$, while subtracting $-\text{Effect} \times 0.4$ from raw $S_{\text{harmony}}$.
4. **Oppositions ($180^\circ$)**: Add $+\text{Effect} \times 0.9$ to $S_{\text{attraction}}$ and $S_{\text{growth}}$, while subtracting $-\text{Effect} \times 0.3$ from raw $S_{\text{harmony}}$.
5. **Saturn Aspects**: Add $+\text{Effect}$ to $S_{\text{growth}}$ and $S_{\text{harmony}}$ (stability).

---

## 12. Four Compatibility Dimensions (Formulas)

Each internal sub-score $S \in [0.0, 100.0]$ starts at a baseline of $50.0$:

### 1. Emotional Harmony ($S_{\text{harmony}}$)
$$S_{\text{harmony}} = \text{Clamp}\left(50.0 + \sum \Delta H_{\text{aspects}} + 0.35 \times (E_{\text{harmony}} - 50.0), 0.0, 100.0\right)$$

### 2. Communication ($S_{\text{communication}}$)
$$S_{\text{communication}} = \text{Clamp}\left(50.0 + \sum \Delta C_{\text{aspects}} + 0.25 \times (M_{\text{mercury}} - 50.0), 0.0, 100.0\right)$$

### 3. Attraction / Chemistry ($S_{\text{attraction}}$)
$$S_{\text{attraction}} = \text{Clamp}\left(50.0 + \sum \Delta A_{\text{aspects}} + 0.20 \times (E_{\text{fire\_air}} - 50.0), 0.0, 100.0\right)$$

### 4. Growth & Long-Term Dynamics ($S_{\text{growth}}$)
$$S_{\text{growth}} = \text{Clamp}\left(50.0 + \sum \Delta G_{\text{aspects}} + 0.25 \times (\text{Modality}_{\text{balance}} - 50.0), 0.0, 100.0\right)$$

---

## 13. Overall Compatibility Score Formula

$$\text{Raw Overall} = 0.30 \times S_{\text{harmony}} + 0.30 \times S_{\text{attraction}} + 0.20 \times S_{\text{communication}} + 0.20 \times S_{\text{growth}}$$

---

## 14. Score Normalization & Curve Stretch

To prevent score clustering around $75 - 85$ and produce meaningful distribution ($20.0 - 95.0$), a non-linear stretch curve is applied:

$$\text{Centered} = \frac{\text{Raw Overall} - 50.0}{50.0}$$
$$\text{Stretched} = 50.0 + 50.0 \times \text{sign}(\text{Centered}) \times |\text{Centered}|^{0.85}$$
$$\text{Final Score} = \text{Round}\left(\text{Clamp}\left(\text{Stretched}, 10.0, 98.0\right), 1\right)$$

---

## 15. Score Inflation Controls & 17. Influence Caps

1. **Max Impact per Planet Pair**: No single planet pair can add or subtract more than $\pm 18.0$ points to any single sub-score.
2. **Duplicate Outer Aspect Capping**: Outer planet cross-aspects (Uranus, Neptune, Pluto) are capped at a combined maximum contribution of $+12.0$ points across all sub-scores.
3. **Absolute Score Bounds**: Final score is hard-clamped between $10.0$ and $98.0$. Perfect $100.0$ or $0.0$ scores are strictly impossible.

---

## 16. Signal Extraction Layer

Signals are extracted deterministically based on active aspects with strength $S_{\text{aspect}} \ge 0.40$:

### Signal Schema:
```json
{
  "type": "sun_trine_moon",
  "category": "harmony",
  "strength": "high",
  "source_aspects": ["Sun Trine Moon (Orb 1.2°)"],
  "label": "Emotional Resonance"
}
```

### Signal Extraction Rules:
- **`sun_trine_moon` / `sun_sextile_moon`**: `category: "harmony"`, `strength: "high"`, `label: "Emotional Resonance"`
- **`venus_conjunction_mars` / `venus_opposite_mars`**: `category: "attraction"`, `strength: "high"`, `label: "Magnetic Chemistry"`
- **`mercury_trine_mercury` / `mercury_sextile_mercury`**: `category: "communication"`, `strength: "high"`, `label: "Intellectual Flow"`
- **`mars_square_saturn` / `sun_square_saturn`**: `category: "growth"`, `strength: "medium"`, `label: "Pacing Tension"`
- **`sun_trine_jupiter`**: `category: "stability"`, `strength: "high"`, `label: "Shared Optimism"`

*Max Signals*: Top **6** highest-weighted signals returned per calculation.

---

## 17. Topic Extraction Layer

Best topics derived deterministically from Mercury aspects and dominant elements:

| Dominant Element / Aspect Pattern | Derived Topics (Max 4) |
| :--- | :--- |
| **Air Dominant / Mercury-Air** | `["books", "philosophy", "ideas", "creative_work"]` |
| **Fire Dominant / Mars-Sun** | `["travel", "adventure", "fitness", "ambition"]` |
| **Water Dominant / Moon-Venus** | `["art", "music", "psychology", "cinema"]` |
| **Earth Dominant / Saturn-Venus** | `["architecture", "food", "design", "lifestyle"]` |

---

## 18. Conversation Starters Layer

Generated deterministically from top active signals:

```python
CONVERSATION_STARTER_RULES = {
    "sun_trine_moon": [
        "What is something that instantly makes you feel understood?",
        "What is your favorite way to recharge after a long week?"
    ],
    "venus_conjunction_mars": [
        "What is your idea of a perfect spontaneous date?",
        "What art or music has inspired you recently?"
    ],
    "mercury_trine_mercury": [
        "Have you read or listened to anything surprising lately?",
        "What topic could you talk about for hours without getting bored?"
    ]
}
```

---

## 19. Unknown & 20. Approximate Birth-Time Behavior

If either user has `birth_time_precision == 'unknown'`:
- Ascendant is `None`. Ascendant aspects are safely omitted.
- `data_quality` metadata in response indicates reduced precision:
  ```json
  {
    "time_precision": "unknown",
    "confidence": 0.75,
    "ascendant_used": false,
    "houses_used": false
  }
  ```

---

## 21. Symmetry Rules

The engine strictly guarantees symmetry:

$$\text{Synastry}(A, B) \equiv \text{Synastry}(B, A)$$

### Mathematical Enforcement:
- Cross-chart aspect distance $d(A_i, B_j) \equiv d(B_j, A_i)$.
- Inter-chart aspect pairs are evaluated bidirectionally: $(A_{\text{Sun}}, B_{\text{Moon}})$ and $(B_{\text{Sun}}, A_{\text{Moon}})$.
- Canonical sorting `user_a_id < user_b_id` is used solely for database primary key indexing, not calculation flow.

---

## 22. Minimum Evidence Rules

If total active aspect weight $\sum (W_{\text{pair}} \times S_{\text{aspect}}) < 2.0$:
- Engine returns neutral score `65.0`.
- Data confidence set to `0.50`.
- Includes signal `{"type": "insufficient_aspects", "category": "notice", "strength": "low", "label": "Independent Chart Dynamics"}`.

---

## 23. Output Contract

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "target_user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "score": 82.5,
  "dimensions": {
    "emotional_harmony": 85.0,
    "communication": 78.0,
    "attraction": 88.0,
    "growth_long_term": 75.0
  },
  "signals": [
    {
      "type": "sun_trine_moon",
      "category": "harmony",
      "strength": "high",
      "source_aspects": ["Sun Trine Moon (Orb 1.2°)"],
      "label": "Emotional Resonance"
    }
  ],
  "best_topics": ["travel", "creative_work", "philosophy"],
  "conversation_starters": [
    "What is something that instantly makes you feel understood?",
    "What creative project or travel memory inspires you most?"
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

---

## 24. Deterministic Explainability & Evidence Model

Every calculation retains an internal `evidence_trace` array for auditability and debugging:

```json
{
  "evidence_trace": [
    {
      "planet_a": "sun",
      "planet_b": "moon",
      "lon_a": 54.25,
      "lon_b": 174.10,
      "aspect": "trine",
      "target_angle": 120.0,
      "distance": 119.85,
      "orb_diff": 0.15,
      "max_orb": 10.0,
      "strength": 0.97,
      "weight": 3.0,
      "subscore_contributions": {
        "harmony": 12.5,
        "attraction": 6.0
      }
    }
  ]
}
```

---

## 25. Versioning

- Engine version identifier: `synastry-v1.0.0`.
- Any modifications to aspect orbs, planet weights, or score formulas require incrementing `engine_version`.

---

## 26. Test Strategy & 27. Deterministic Test Vectors

### Automated Test Suite Requirements:

1. **`tests/astrology/test_aspects.py`**:
   - Test exact $0^\circ, 60^\circ, 90^\circ, 120^\circ, 180^\circ$ aspects.
   - Test $360^\circ$ boundary wraparound ($355^\circ$ to $5^\circ = 10^\circ$).
   - Test quadratic orb decay formula.

2. **`tests/compatibility/test_synastry.py`**:
   - Test deterministic score calculation for synthetic chart vectors.
   - Test symmetry $f(A,B) == f(B,A)$.
   - Test unknown birth-time resilience.

### Test Vector 1: High Harmony (Sun Trine Moon, Venus Trine Mars)
- Person A: Sun $0.0^\circ$ (Aries), Venus $0.0^\circ$ (Aries).
- Person B: Moon $120.0^\circ$ (Leo), Mars $120.0^\circ$ (Leo).
- Expected Result: $S_{\text{harmony}} > 85.0$, $S_{\text{attraction}} > 80.0$, Overall Score $> 82.0$.

### Test Vector 2: High Tension (Sun Square Mars, Moon Square Saturn)
- Person A: Sun $0.0^\circ$ (Aries), Moon $0.0^\circ$ (Aries).
- Person B: Mars $90.0^\circ$ (Cancer), Saturn $90.0^\circ$ (Cancer).
- Expected Result: $S_{\text{growth}} > 75.0$, $S_{\text{harmony}} < 55.0$, Signal includes `mars_square_sun`.

---

## 28. Known Technical Limitations

1. **Latitude $> 66.5^\circ$ Placidus Error**: If birth coordinates are polar, natal calculation raises `placidus_polar_error`. Synastry engine falls back gracefully to longitudes only.
2. **House Overlays Omitted**: V1 does not evaluate planet-in-house overlays.

---

## 29. Implementation Checklist

- [ ] Create `backend/app/astrology/aspects.py` (Aspect math, orb decay, wraparound).
- [ ] Create `tests/astrology/test_aspects.py`.
- [ ] Create `backend/app/compatibility/rules.py` (Signal maps, topics, starters).
- [ ] Create `backend/app/compatibility/synastry.py` (Synastry calculation engine).
- [ ] Create `tests/compatibility/test_synastry.py`.
- [ ] Re-implement `backend/app/compatibility/engine.py` (Service wrapper connecting DB & `SynastryEngine`).
- [ ] Update `backend/app/comparisons/router.py` (Remove hardcoded `82.5`, connect to service layer).
- [ ] Update `tests/database/test_database_security.py` (`test_compatibility_access_rules`).
- [ ] Update `docs/PROJECT_STATE.md`, `docs/ASTROLOGY_ENGINE.md`, and `docs/API.md`.

---

## Implementation Status

### CURRENTLY IMPLEMENTED:
- `public.birth_data` and `public.astro_private` DB tables & RLS policies.
- `public.compatibility_results` DB caching table & version invalidation queries.
- `public.has_active_connection` and `public.is_user_blocked` SQL helper functions.
- Canonical user pair sorting (`user_a_id < user_b_id`).
- PySwissEph natal planetary longitude calculation (10 planets + Ascendant).

### REQUIRED BACKEND CHANGES:
- Implement aspect distance and quadratic orb decay module (`backend/app/astrology/aspects.py`).
- Implement rule-based signal and conversation starter maps (`backend/app/compatibility/rules.py`).
- Implement Synastry Engine domain module (`backend/app/compatibility/synastry.py`).
- Update `backend/app/compatibility/engine.py` and `backend/app/comparisons/router.py` to replace hardcoded `82.5` score with deterministic calculation.

### FUTURE / OUT OF SCOPE:
- House overlay synastry (V1.1).
- Chiron, Lilith, and Lunar Nodes synastry (V2.0).
- OpenAI / LLM dynamic interpretation integration.
