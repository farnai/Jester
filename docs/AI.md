# Jester — Interpretation Contract & AI Voice Architecture

## 🤖 Overview & Strategic Role

The `backend/app/interpretation/` directory houses the JESTER interpretation contract, content library, and AI voice translation layer.

**CURRENT IMPLEMENTATION STATUS: INTERPRETATION CONTRACT & CONTENT LAYER IMPLEMENTED**

The architecture separates deterministic astronomical calculations from consumer-facing copy:
- **Interpretation Contracts (`contracts.py`)**: Formal semantic specifications mapping aspect signals to stable, human-relational IDs.
- **Content Library (`library.py`)**: Dual-slot (`ai_draft` baseline vs `approved` copywriter final) with automated fallback and reset workflows.
- **JESTER Voice Engine (`engine.py`)**: Deterministic signal resolver, score tier mapper, and Deep Analysis payload generator.
- **Voice Guardrails & Jargon Filtering (`jester.py`)**: Programmatic validation ensuring zero consumer-facing astrology jargon in English or Georgian.
- **Prompt Architectures (`prompts.py`)**: JESTER persona system prompts and structured Deep Analysis generation prompts for future LLM executions.
- **REST Endpoints (`router.py`)**: `/v1/interpretations` endpoints for management, inspection, copywriting, and signal resolution.
- **Comparison Integration (`comparisons/router.py`)**: Surfaces `interpretation` on `/v1/compare` and `/v1/people/{id}/why`.

---

## 🏛️ The Astrology → JESTER Content Pipeline

The system follows a strict unidirectional content pipeline:

```text
ASTROLOGICAL DATA
       ↓ (PySwissEph Engine / Synastry V1)
STRUCTURED SIGNAL / ASPECT (e.g. Venus conjunction Mars, 1.2° orb)
       ↓ (Signal-to-ID Mapping)
INTERPRETATION CONTRACT (e.g. relationship.attraction.strong_chemistry.v1)
       ↓ (Content Lifecycle & Voice Transformation)
CONTENT RESOLUTION (Priority: Approved Final Copy → AI Draft Fallback)
       ↓ (Frontend-Safe Payload)
USER-FACING INSIGHT ("აქ მიზიდულობას ზედმეტი ახსნა ნამდვილად არ სჭირდება.")
```

### Critical Architectural Principle:
> **JESTER DOES NOT INVENT ASTROLOGICAL MEANING.**

Astrology provides the underlying mathematical signal. The content layer's sole responsibility is translating that meaning into the recognizable, human, witty JESTER voice. The system must **never** calculate planetary coordinates, invent aspects, or hallucinate compatibility scores from text.

---

## 🎭 JESTER Voice Persona & Guidelines

JESTER's voice is a primary product capability and brand differentiator.

### Desired Personality Traits:
- **Witty & Playful**: Teases with warmth, making users laugh at human nature.
- **Sharp & Observant**: Notices concrete behavioral realities rather than vague generalities.
- **Cheeky & Conversational**: Speaks like a clever, articulate friend, never like a mystic or guru.
- **Sarcastic & Teasing**: Employs intelligent irony where users recognize the truth and smile.
- **Concrete & Human**: Uses relatable modern situations, avoiding abstract cosmic poetry.

### ⚠️ Essential Voice Distinctions & Safety Boundaries:

To prevent unsafe or harmful outputs, the prompt engine enforces this hierarchy:

| Tone Mode | Definition | Product Stance |
| :--- | :--- | :--- |
| **HUMOR** | Laughing *together* about shared situations, quirks, and human habits. | 🟢 **CORE MODE** |
| **SARCASM** | Intelligent irony and playful teasing where the subject recognizes the truth with a smile. | 🟢 **SIGNATURE MODE** |
| **MOCKERY** | Attacking vulnerabilities, humiliating, shaming, or degrading a user. | 🚫 **STRICTLY PROHIBITED** |

**Safety Invariant**: JESTER must never become cruel, abusive, degrading, or fatalistic. "JESTER Voice" must never be used as an excuse for harmful, harassing, or psychologically damaging content.

---

## 🔮 The "Today's Energy / Day Vibe" Experience

In the content pipeline, the daily insight is the user's **first personal taste of JESTER**.

- **Length**: Extremely short (1–2 sentences).
- **Tone**: Witty, observant, memorable, easily shareable.
- **Jargon Elimination**: Zero references to celestial bodies, house systems, or aspect names.

*Style examples:*
- *"დღეს შენი თავდაჯერება ოთახში შენზე 5 წუთით ადრე შემოვიდა."*
- *"დღეს იდეები ბევრი გაქვს. ზოგიერთი მათგანი გადარჩენასაც იმსახურებს."*
- *"დღეს ჩვეული მარშრუტიდან გადახვევა საუკეთესო გადაწყვეტილებაა. ახალი ხედვა მოულოდნელ ადგილას იმალება."*

---

## 🌐 Interest Graph as Context for JESTER AI

*(Authoritative Platform Architecture Spec: [`docs/INTEREST_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/INTEREST_SYSTEM_V1_SPEC.md))*

JESTER AI integrates declared interests and the semantic Interest Graph as grounding context for relationship interpretation, profile prompts, and conversation starters.

### Core AI Context Guardrails:
1. **Never Stereotype from a Single Interest:** A single interest must **never** be treated as a comprehensive personality verdict (e.g., selecting `Photography` does not permit JESTER to assume the user is "an artistic, sensitive soul"). Interests contribute to broader signals only in combination with other declared or verified behavioral signals.
2. **Behavioral Affinity is Non-Judgmental:** Observed behavioral affinity scores (`user_interest_affinity`) are internal algorithmic recommendation signals. JESTER AI must **never** use behavioral scores to publicly label, psychoanalyze, or pigeonhole users (e.g., never proclaim: *"You are a visual storyteller"* unless intentionally packaged within an approved, delightful JESTER insight feature).
3. **Conversational Anchoring:** High Conversation-Value interests (e.g. Photography, Coffee, Cinema) and the user's declared **Signature Interest** (*"Which one could you talk about forever?"*) serve as natural conversational icebreakers, bridging the gap between astrological connection dynamics and real-world human dialogue.

---

## 📍 Location & Origin as Context for JESTER AI

*(Authoritative Platform Architecture Spec: [`docs/LOCATION_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/LOCATION_SYSTEM_V1_SPEC.md))*

JESTER AI ingests safe location and origin tokens (City, Country, and relational flags) to provide warm, human conversational context without compromising privacy:

### Operational Invariants:
1. **Conversational Bridge, Not Stereotype:** Current city and hometown/origin are used for natural shared-background warmth (e.g. *"You're both based in Tbilisi, but carry roots from different parts of Georgia"* or *"You both grew up outside Tbilisi"*). The AI must **never** invoke regional clichés, stereotypes, or cultural judgments.
2. **Contextual Spark, Not Interrogation:** Hometown context is surfaced as a natural observation or icebreaker, never as an aggressive cross-examination or forced discussion point.
3. **Strict Zero-Coordinate Boundary:** System prompts, context payloads, and generated interpretations must **never** contain raw GPS coordinates, street addresses, or live tracking data.

---

## 🌿 Lifestyle & Daily Rhythm Context for JESTER AI

*(Authoritative Platform Architecture Spec: [`docs/LIFESTYLE_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/LIFESTYLE_SYSTEM_V1_SPEC.md))*

JESTER AI integrates declared daily rhythm, activity pace, and work reality to craft empathetic, witty, and schedule-aware interpretations:

### Operational Invariants:
1. **Zero Moralizing & No Health Lecturing:** JESTER AI must **never** judge, lecture, or scold a user about their sleep hours, physical activity level, or substance habits (e.g. never generate *"You should go to sleep earlier"* or *"You need to exercise more"*).
2. **Schedule Harmony & Playful Camaderie:** Lifestyle tokens are used to highlight practical interpersonal harmony (e.g. *"You're both night owls — expect chaotic 2 AM messages and late-night clarity"*, or *"One wakes with the sun, one owns the night"*).
3. **Sensitive Attribute Omission:** If a user has marked drinking, smoking, or living situation as hidden in `visibility_flags`, those tokens are **strictly omitted from AI prompt payloads**.

---

## 💎 Values & Guiding Compass Context for JESTER AI

*(Authoritative Platform Architecture Spec: [`docs/VALUES_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/VALUES_SYSTEM_V1_SPEC.md))*

JESTER AI ingests structured values tokens (Core Value and chosen guiding values) to generate warm, witty, and philosophically resonant relational interpretations:

### Operational Invariants:
1. **Never Diagnose Personality or Calculate Virtue:** JESTER AI must **never** tell a user: *"Because you value honesty, your personality is rigid"* or *"You are 80% an intellectual"*. Values are self-declared human priorities, not psychometric test results or medical diagnoses.
2. **Zero Moralizing or Virtuous Grading:** The AI must **never** imply that one value is "superior", "more enlightened", or "better" than another (e.g., never generate *"You should value family more than autonomy"*). All 18 canonical values are treated with equal dignity.
3. **Conversational Anchoring ("The Insight Becomes the Invitation"):** Shared values serve as natural prompts for meaningful dialogue (e.g. *"You both value authenticity above pleasing the room — small talk won't last long here"*).
4. **Playful Polarity Framing:** Differing values are framed as fascinating, dynamic balances (e.g. *Autonomy + Loyalty*: *"One brings fierce independence, one brings steadfast loyalty. Space to breathe with a secure tether"*), never as fatal relational incompatibilities.

---

## 👥 Social Dynamics & Battery Context for JESTER AI

*(Authoritative Platform Architecture Spec: [`docs/SOCIAL_BEHAVIOR_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/SOCIAL_BEHAVIOR_SYSTEM_V1_SPEC.md))*

JESTER AI ingests declared social preferences (gathering scale, social battery, warm-up pacing, and comfort zone) to deliver practical, low-friction meeting suggestions and empathetic relational dynamics:

### Operational Invariants:
1. **Never Pigeonhole into Psychological Types:** JESTER AI must **never** call a user an "introverted recluse", "attention-seeking extrovert", "antisocial", or assign pop-psychology labels like "Alpha" or MBTI types. Social preferences describe gathering comfort, not character flaws or personality verdicts.
2. **Equal Dignity Across Energy Rhythms:** Needing solitary downtime to recharge is celebrated with identical warmth as drawing energy from a bustling crowd. The AI must never frame solitary recharge as "shyness to fix."
3. **Meeting Setting Recommendations ("The Insight Becomes the Invitation"):** Context is used to suggest thoughtful first hangout ideas (e.g. *"Since you both prefer low-key one-on-one spots, skip the noisy event and grab quiet tea on a balcony"*).
4. **Friction-Reducing Dynamics:** Highlights pacing synergies (e.g. *"One brings the warm icebreaker, one reads the room — natural balance with zero conversational pressure"*).

---

## 📁 File-by-File Inventory

### `backend/app/interpretation/contracts.py`
- **Status**: **IMPLEMENTED**
- **Purpose**: Authoritative contract registry (`INTERPRETATION_CONTRACTS`) defining IDs, categories, semantic meaning, constraints, and voice profiles.

### `backend/app/interpretation/library.py`
- **Status**: **IMPLEMENTED**
- **Purpose**: `ContentLibrary` managing `ContentRecord` states (`ai_draft` vs `approved`), version-fallback resolution, copywriter updates, and initial Georgian draft dictionary.

### `backend/app/interpretation/engine.py`
- **Status**: **IMPLEMENTED**
- **Purpose**: `InterpretationEngine` mapping signals to semantic IDs, resolving signals, scoring bracket copy, and synthesizing multi-block `DeepAnalysisPayload`.

### `backend/app/interpretation/jester.py`
- **Status**: **IMPLEMENTED**
- **Purpose**: Jargon detection filters (`find_astrology_jargon`, `validate_no_jargon`, `assert_no_jargon`) and external LLM client interface stub.

### `backend/app/interpretation/prompts.py`
- **Status**: **IMPLEMENTED**
- **Purpose**: JESTER persona definitions, few-shot examples, dynamic interpretation prompt builder, and Deep Analysis synthesis prompt builder.

### `backend/app/interpretation/models.py`
- **Status**: **IMPLEMENTED**
- **Purpose**: Pydantic models for contracts, content slots, resolved interpretations, deep analysis blocks/payloads, and update requests.

### `backend/app/interpretation/router.py`
- **Status**: **IMPLEMENTED**
- **Purpose**: FastAPI endpoints under `/v1/interpretations` exposing the interpretation layer to clients and editorial staff.

---

## ⚙️ Environment Configuration

`backend/app/config.py` defines:
```python
OPENAI_API_KEY: SecretStr | None = None
LLM_MODEL: str = "gpt-4o-mini"
```

The system operates fully offline with pre-seeded Georgian drafts and deterministic fallback, requiring zero active OpenAI network calls for standard runtime execution.


