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


