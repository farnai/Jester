# JESTER V1 — Interpretation Contract & JESTER Voice Content Layer Specification

## 🃏 1. Strategic & Architectural Overview

**JESTER** is a **People Discovery and Relationship Intelligence** platform.
Astrology provides the deterministic, mathematical intelligence layer, but **Jester is not positioned as an astrology app**.
The user-facing experience is about human connection, personality dynamics, and relationship intelligence:
> *"They show the match. JESTER explains the connection."*

To protect this vision, JESTER strictly decouples astrological calculations from human semantic meaning and consumer-facing copy:

```text
Astrology Engine (PySwissEph, Synastry V1)
      ↓ (Deterministic planetary positions, aspect math, weights)
Structured Signal (e.g. venus_conjunction_mars, 1.2° orb)
      ↓ (Semantic mapping)
Interpretation Contract (e.g. relationship.attraction.strong_chemistry.v1)
      ↓ (Voice transformation guidelines, constraints, persona)
JESTER Voice Content Layer
      ↓ (Content lifecycle: Approved Final Copy or AI Draft Fallback)
User-Facing Text ("აქ მიზიდულობას ზედმეტი ახსნა ნამდვილად არ სჭირდება.")
```

### Critical Architectural Invariants
1. **Separation of Concerns**: Astrology engines (`pyswisseph`, `synastry.py`, `aspects.py`) calculate signals and scores. They do **not** know, generate, or contain user-facing copy strings.
2. **Stable Semantic IDs**: Interpretation IDs are structured around human relationship concepts (e.g., `relationship.attraction.strong_chemistry.v1`), **never** raw celestial bodies or aspects.
3. **Copy Replacement Without Code Changes**: Professional copywriters can modify, refine, or translate any user-facing text without altering calculations, database schemas, or frontend components.
4. **Zero Astrology Jargon**: Consumer-facing text strictly forbids terms such as *conjunction, opposition, trine, square, orb, transit, synastry, house, etc.* (both in English and Georgian). Jargon filtering is programmatically validated.
5. **No Hallucinated Astrology**: The system only generates interpretations for verified astronomical signals. Unrecognized signals return `None` (HTTP 404).

---

## 📐 2. Formal Interpretation Contract Schema

Every interpretation in JESTER conforms to the following formal contract schema:

```json
{
  "interpretation_id": "relationship.attraction.strong_chemistry.v1",
  "context": "relationship",
  "signal": {
    "category": "attraction",
    "type": "venus_mars_aspect",
    "strength": 0.91
  },
  "meaning": {
    "type": "strong_chemistry",
    "intensity": "high",
    "human_meaning": [
      "strong interpersonal pull",
      "easy attraction",
      "high interpersonal magnetism"
    ]
  },
  "voice": {
    "tone": "witty",
    "sarcasm": "light",
    "warmth": "high",
    "directness": "high",
    "no_astrology_jargon": true
  },
  "output": {
    "format": "short_insight",
    "max_sentences": 2,
    "language": "ka"
  },
  "constraints": {
    "must_not": [
      "predict the future",
      "claim certainty about another person's feelings",
      "use astrology jargon",
      "sound generic or horoscope-like",
      "humiliate or degrade user"
    ]
  }
}
```

### Field Definitions:
- **`interpretation_id`**: Globally unique, hierarchical semantic identifier (`{context}.{category}.{theme}.v{version}`).
- **`context`**: Scope of applicability (`relationship`, `daily_energy`, `self`).
- **`signal`**: Deterministic astrological signal trigger (`category`, `type`, normalized `strength` from 0.0 to 1.0).
- **`meaning`**: Core psychological / interpersonal translation (`type`, `intensity`, list of concrete human behavioral observations).
- **`voice`**: JESTER voice persona settings (`tone`, `sarcasm`, `warmth`, `directness`, `no_astrology_jargon`).
- **`output`**: Rendering specifications (`format`, `max_sentences`, `language`).
- **`constraints`**: Guardrails preventing harmful, mystic, fatalistic, or generic language.

---

## 🗃️ 3. Interpretation ID Taxonomy & Inventory

JESTER organizes interpretations into a hierarchical dot-notation taxonomy:

```text
{context}.{category}.{theme}.{version}
```

### Relational Dynamics Inventory (Synastry V1)

| Interpretation ID | Signal Trigger | Human Meaning Theme | Intensity |
| :--- | :--- | :--- | :--- |
| `relationship.attraction.strong_chemistry.v1` | `venus_mars_aspect` / `conjunction` | Strong interpersonal pull, natural attraction, magnetism | High |
| `relationship.attraction.magnetic_chemistry.v1` | `venus_mars_aspect` / `trine`/`sextile` | Kinetic spark, effortless attraction | High |
| `relationship.attraction.warm_affection.v1` | `sun_venus_harmony` | Natural warmth, comforting affection, easy liking | Medium |
| `relationship.attraction.intense_magnetism.v1` | `venus_pluto_aspect` | Deep fascination, intense emotional gravity | High |
| `relationship.attraction.energized_collaboration.v1` | `sun_trine_mars` | Shared kinetic momentum, productive chemistry | Medium |
| `relationship.attraction.dynamic_drive.v1` | `sun_conjunction_mars` | High shared drive, assertive motivation | High |
| `relationship.harmony.emotional_resonance.v1` | `sun_moon_harmony` | Deep emotional comfort, instinctive understanding | High |
| `relationship.harmony.core_harmony.v1` | `sun_sun_harmony` | Shared core values, mutual validation, life rhythm | High |
| `relationship.harmony.gentle_affinity.v1` | `moon_venus_harmony` | Soothing empathy, emotional gentleness | Medium |
| `relationship.harmony.generous_affection.v1` | `venus_jupiter_harmony` | Generous goodwill, lighthearted optimism | Medium |
| `relationship.communication.intellectual_flow.v1` | `mercury_mercury_harmony` | Effortless banter, mental synchrony, rapid rapport | High |
| `relationship.communication.mutual_understanding.v1` | `sun_mercury_harmony` | Lucid communication, easy alignment on ideas | Medium |
| `relationship.growth.complementary_balance.v1` | `sun_moon_opposition` | Complementary contrast, different angles of awareness | Medium |
| `relationship.growth.dynamic_emotional_tension.v1` | `sun_moon_square` | Shifting emotional climate, stimulating learning curve | Medium |
| `relationship.growth.contrasting_perspectives.v1` | `sun_sun_opposition` | Different styles of self-expression, creative mirror | Medium |
| `relationship.growth.ego_friction.v1` | `sun_sun_square` | Leadership negotiation, spirited healthy friction | Medium |
| `relationship.growth.pacing_tension.v1` | `saturn_square_personal` | Different pacing styles, patience-building dynamics | Medium |
| `relationship.growth.dynamic_spark.v1` | `mars_sun_square` | High kinetic tension, passionate directness | High |
| `relationship.stability.shared_optimism.v1` | `jupiter_harmony` | Infectious positivity, mutual encouragement | Medium |
| `relationship.stability.long_term_grounding.v1` | `saturn_trine_personal` | Steadfast reliability, calm emotional grounding | High |
| `relationship.notice.independent_dynamics.v1` | `insufficient_aspects` | Low major aspect density, high autonomy, fresh canvas | Low |

### Macro Compatibility Score Interpretations

| Interpretation ID | Score Bracket | Tone & Dynamic |
| :--- | :--- | :--- |
| `relationship.overall.exceptional_flow.v1` | 85.0 – 100.0 | Effortless synergy, rare instinctive alignment |
| `relationship.overall.balanced_synergy.v1` | 70.0 – 84.9 | Balanced connection with complementary perspectives |
| `relationship.overall.stimulating_friction.v1` | 50.0 – 69.9 | Dynamic spark with growth opportunities and distinct styles |
| `relationship.overall.independent_paths.v1` | 0.0 – 49.9 | Independent rhythms, high individuality, no assumptions |

### Daily Energy Interpretations

| Interpretation ID | Transit Type | Tone & Dynamic |
| :--- | :--- | :--- |
| `daily_energy.confidence.elevated.v1` | `sun_mars_transit` | Assertive, charismatic, high presence |
| `daily_energy.communication.direct.v1` | `mercury_transit` | Sharp conversation, quick wit, direct delivery |
| `daily_energy.focus.scattered.v1` | `jupiter_mercury_transit` | Overflowing ideas, scattered focus, creative chaos |
| `daily_energy.creativity.exploration.v1` | `venus_neptune_transit` | Novel perspective, breaking routine, lateral thinking |

---

## 🔄 4. Content Lifecycle: AI Draft vs Approved Copy

Every registered interpretation maintains two content slots:
1. **`draft` (`ai_draft`)**: Automatically pre-seeded or AI-generated baseline copy. Enables instant operational launch.
2. **`final` (`approved` or `not_reviewed`)**: Copy written or approved by human editorial/copywriting staff.

```text
ContentSlot Record:
├── draft: { text: "...", status: "ai_draft", author: "jester_voice_v1", updated_at: "..." }
└── final: { text: "...", status: "approved", author: "copywriter", updated_at: "..." }
```

### Deterministic Resolution Priority:
When client applications request copy for an interpretation ID:
1. **Priority 1**: If `final.status == "approved"` and `final.text` is non-empty, return `final.text` with `content_status = "approved"`.
2. **Priority 2**: If `draft.text` is non-empty, return `draft.text` with `content_status = "ai_draft"`.
3. **Priority 3**: If neither is available, return `None` (HTTP 404).

---

## 🎭 5. JESTER Voice Persona & Jargon Rules

### Persona Guidelines
- **Witty, Observant & Socially Intelligent**: Notices micro-behaviors, communication quirks, and modern social situations.
- **Tease With Warmth**: Never cruel, mocking, or cynical. Users laugh *with* the observation.
- **Conversational & Human**: Speaks like an articulate, perceptive friend—never like a guru, psychic, or mystical chart-reader.

### Forbidden Astrology Jargon Blacklist

The following terms are strictly prohibited from appearing in any consumer-facing copy:

```text
English:
- conjunction, opposition, trine, square, sextile, quincunx
- orb, synastry, transit, house, aspect, planetary longitude
- placidus, ephemeris, natal chart, horoscope, ascendant, midheaven, ecliptic, declination

Georgian:
- კონიუნქცია, ოპოზიცია, ტრინი, კვადრატურა, სექსტილი
- ორბი, სინასტრია, ტრანზიტი, პლაციდუსი, ეფემერიდი
- ნატალური, ჰოროსკოპი, ასცენდენტი, ეკლიპტიკა, ასპექტი
```

The system provides `find_astrology_jargon(text)`, `validate_no_jargon(text)`, and `assert_no_jargon(text)` in `backend/app/interpretation/jester.py`. All initial drafts are validated against this blacklist.

---

## 📱 6. Frontend Integration Contract

The API delivers user-facing interpretation copy in a clean, self-contained, frontend-safe model:

```typescript
interface ResolvedInterpretation {
  id: string;             // e.g. "relationship.attraction.strong_chemistry.v1"
  text: string;           // e.g. "აქ მიზიდულობას ზედმეტი ახსნა ნამდვილად არ სჭირდება."
  content_status: "ai_draft" | "approved";
  language: string;       // "ka"
}
```

### Compatibility Endpoint Example: `POST /v1/compare` & `GET /v1/people/{id}/why`

```json
{
  "id": "18fba892-d6cb-402a-9f5e-141a4a6217c0",
  "target_user_id": "787cbf9b-a010-449e-b9bb-20e4debb74a1",
  "score": 88.5,
  "dimensions": {
    "harmony": 91.0,
    "growth": 82.0,
    "attraction": 95.0,
    "stability": 84.0
  },
  "interpretation": {
    "id": "relationship.attraction.strong_chemistry.v1",
    "text": "აქ მიზიდულობას ზედმეტი ახსნა ნამდვილად არ სჭირდება.",
    "content_status": "ai_draft",
    "language": "ka"
  },
  "signals": [
    {
      "type": "venus_conjunction_mars",
      "category": "attraction",
      "strength": "strong",
      "source_aspects": ["venus_conjunction_mars 1.2 deg"],
      "interpretation": {
        "id": "relationship.attraction.strong_chemistry.v1",
        "text": "აქ მიზიდულობას ზედმეტი ახსნა ნამდვილად არ სჭირდება.",
        "content_status": "ai_draft",
        "language": "ka"
      }
    }
  ]
}
```

Frontend components render `response.interpretation.text` directly without running any aspect calculations or translation layers.

---

## 🔍 7. Deep Analysis & Daily Energy Architecture

### Deep Analysis Pipeline
Deep Analysis operates on structured, verified signals rather than open-ended prompt hallucinations:

```text
Synastry Evidence Trace
      ↓
Ranked Signals
      ↓
Interpretation Contracts
      ↓
JESTER Voice Narrative Blocks
      ↓
Deep Analysis Payload (Traceable to specific astrological aspects)
```

The `InterpretationEngine.build_deep_analysis_payload()` method bundles:
- `primary_interpretation`: Top-level relationship insight.
- `blocks`: Dimension-specific blocks (`attraction`, `harmony`, `growth`, `stability`), each with its resolved copy and underlying `evidence_aspects`.
- `data_confidence`: Confidence factor based on birth time precision.

### Daily Energy Pipeline
Follows identical principles in `backend/app/jobs/daily_energy.py`:
- Deterministic transit signal → `resolve_daily_energy(energy_type)`.
- Stored as structured `ResolvedInterpretation` JSON in PostgreSQL `public.daily_energies.interpretation`.

---

## ✍️ 8. Copywriter Replacement Workflow

To replace an AI draft with professional copywriter copy, the following workflow is executed:

### Step 1: Inspect Available Contracts
Call `GET /v1/interpretations`:
```bash
curl -X GET "https://api.jester.app/v1/interpretations" \
     -H "Authorization: Bearer <ADMIN_OR_COPYWRITER_JWT>"
```

### Step 2: Update Approved Text
Call `PATCH /v1/interpretations/{interpretation_id}/copy`:
```bash
curl -X PATCH "https://api.jester.app/v1/interpretations/relationship.attraction.strong_chemistry.v1/copy" \
     -H "Authorization: Bearer <ADMIN_OR_COPYWRITER_JWT>" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "აქ მიზიდულობას ზედმეტი ახსნა ნამდვილად არ სჭირდება.",
       "status": "approved",
       "author": "tamuna_copywriter"
     }'
```

### Step 3: Instant Verification
Subsequent calls to `/v1/compare`, `/v1/people/{id}/why`, or `GET /v1/interpretations/{id}` immediately return the updated copy with `"content_status": "approved"`.
Calculations, scores, and aspect math remain 100% unchanged.

### Step 4: Reverting to Draft (if needed)
Call `POST /v1/interpretations/{interpretation_id}/reset`:
Reverts status back to `"not_reviewed"`, gracefully restoring the AI draft fallback.

---

## 🛡️ 9. Verification & Automated Test Coverage

The subsystem is validated by dedicated tests in `tests/interpretation/test_interpretation.py` and `tests/interpretation/test_content_v2.py`, verifying all requirements:
- Deterministic mapping: `test_deterministic_signal_to_interpretation_mapping`
- Stable semantic IDs: `test_stable_semantic_interpretation_ids`
- AI draft fallback: `test_ai_draft_fallback`
- Approved copy priority: `test_approved_copy_priority`
- Missing final copy fallback: `test_missing_final_copy_fallback`
- Engine independence: `test_no_astrology_engine_dependency_on_copy`
- Frontend safety: `test_frontend_safe_api_response`
- Unsupported signal protection: `test_unsupported_signals_do_not_generate_invented_interpretations`
- Deterministic output: `test_deterministic_output_for_same_input`
- Calculation invariant under copy change: `test_content_replacement_does_not_change_astrology_calculations`
- Versioning tolerance: `test_versioned_interpretations_remain_resolvable`
- UTF-8 Georgian fidelity: `test_georgian_content_returned_correctly`
- Jargon-free library scan: `test_no_astrology_jargon_in_draft_library`
- Deep Analysis integration: `test_deep_analysis_payload_builder`
- Full API flow: `test_interpretations_api_flow`
- Multi-asset & multi-variant resolution: `tests/interpretation/test_content_v2.py`

---

## 🚀 10. Content Architecture V2 Expansion

Under **Content Architecture V2**, the Interpretation Contract remains strictly decoupled from copy:
- **Interpretation Contract**: Defines **WHAT** the signal means (semantic meaning, behavioral observations, guardrails). It contains **zero user copy**.
- **Content Asset Library**: Holds **HOW** JESTER says it, containing collections of `ContentAsset` domain records.
- **Multi-Asset & Multi-Variant**: One interpretation contract supports unlimited content assets across multiple tones (`witty`, `playful`, `soft`, `bold`, `savage`, `romantic`), contexts (`relationship`, `friendship`, `business`, `daily_energy`), locales (`ka`, `en`), and variants (`variant_a`, `variant_b`, etc.).
- **Deterministic Resolver**: Evaluates context, locale, tone, and seed-based rotation to select the optimal approved or draft asset.

For complete architectural specifications, storage abstraction, and resolver algorithms, see [JESTER_CONTENT_ARCHITECTURE.md](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/JESTER_CONTENT_ARCHITECTURE.md).

