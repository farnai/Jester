# Jester — AI & LLM Subsystem Architecture

## 🤖 Overview & Strategic Role

The `backend/app/interpretation/` directory houses the JESTER AI voice and LLM interpretation pipeline.

**CURRENT IMPLEMENTATION STATUS: ARCHITECTURAL STUB ONLY**

The codebase contains environment configurations (`OPENAI_API_KEY`, `LLM_MODEL`) and basic Pydantic data schemas for AI interpretations, but **no active external LLM integration or dynamic prompt execution is currently connected in production endpoints**.

In the JESTER product strategy, **AI is not an open-ended chatbot or horoscope writer**. It is a **voice translation layer** that takes deterministic astrological signals and converts them into sharp, witty, insightful human observations.

---

## 🏛️ The Astrology → JESTER Content Pipeline

The AI layer follows a strict unidirectional content pipeline:

```text
ASTROLOGICAL DATA
       ↓ (PySwissEph Engine)
STRUCTURED SIGNAL / ASPECT (e.g. Venus trine Mars, 1.2° orb)
       ↓ (Rule-Based Aggregator)
CORE INTERPERSONAL / PSYCHOLOGICAL MEANING (Chemistry, magnetic tension)
       ↓ (Interpretation Engine)
RELATIONSHIP / PERSONAL DYNAMICS CONTEXT
       ↓ (Prompt Formatter with JESTER Voice Persona)
JESTER VOICE TRANSFORMATION
       ↓ (Structured Pydantic Model)
USER-FACING INSIGHT (Short, witty, human-readable)
```

### Critical Architectural Principle:
> **JESTER DOES NOT INVENT ASTROLOGICAL MEANING.**

Astrology provides the underlying mathematical signal. The LLM's sole responsibility is translating that meaning into the recognizable, human, witty JESTER voice. The LLM must **never** calculate planetary coordinates, invent aspects, or hallucinate compatibility scores.

---

## 🎭 JESTER Voice Persona & Guidelines

JESTER's voice is a primary product capability and brand differentiator.

### Desired Personality Traits:
- **Witty & Playful**: Teases with warmth, making users laugh at human nature.
- **Sharp & Observant**: Notices concrete behavioral realities rather than vague generalities.
- **Cheeky & Conversational**: Speaks like a clever, articulate friend, never like a mystic or guru.
- **Sarcastic & Teasing**: Employs intelligent irony where users recognize the truth and smile.
- **Concrete & Human**: Uses relatable modern situations (e.g., meeting rooms, group chats, road trips), avoiding abstract cosmic poetry.

### ⚠️ Essential Voice Distinctions & Safety Boundaries:

To prevent unsafe or harmful outputs, the prompt engine must strictly enforce this hierarchy:

| Tone Mode | Definition | Product Stance |
| :--- | :--- | :--- |
| **HUMOR** | Laughing *together* about shared situations, quirks, and human habits. | 🟢 **CORE MODE** |
| **SARCASM** | Intelligent irony and playful teasing where the subject recognizes the truth with a smile. | 🟢 **SIGNATURE MODE** |
| **MOCKERY** | Attacking vulnerabilities, humiliating, shaming, or degrading a user. | 🚫 **STRICTLY PROHIBITED** |

**Safety Invariant**: JESTER must never become cruel, abusive, degrading, or fatalistic. "JESTER Voice" must never be used as an excuse for harmful, harassing, or psychologically damaging content.

---

## 🔮 The "Today's Energy / Day Vibe" Experience

In the AI pipeline, the daily insight is the user's **first personal taste of JESTER**.

- **Length**: Extremely short (1–2 sentences).
- **Tone**: Witty, observant, memorable, easily shareable.
- **Jargon Elimination**: Zero references to celestial bodies, house systems, or aspect names.

*Style examples (illustrative, not hardcoded):*
- *"დღეს შენი თავდაჯერება ოთახში შენზე 5 წუთით ადრე შემოვიდა."*
- *"დღეს იდეები ბევრი გაქვს. ზოგიერთი მათგანი გადარჩენასაც იმსახურებს."*
- *"დღეს ყველას რჩევას აძლევ. საინტერესოა, ვინ მოგთხოვა."*

---

## 📁 File-by-File Inventory

### `backend/app/interpretation/engine.py` (75 bytes)
- **Status**: **STUB**
- **Purpose**: Map structured signals (e.g. from Synastry V1 or Daily Transits) to psychological/interpersonal themes.

### `backend/app/interpretation/jester.py` (107 bytes)
- **Status**: **STUB**
- **Purpose**: OpenAI client interface, sending structured prompts and enforcing output validation.

### `backend/app/interpretation/prompts.py` (54 bytes)
- **Status**: **STUB**
- **Purpose**: System and few-shot prompt templates establishing the JESTER persona, tone constraints, and language rules.

### `backend/app/interpretation/models.py` (257 bytes)
- **Status**: **IMPLEMENTED (Schemas Only)**
- **Content**:
  ```python
  from pydantic import BaseModel

  class JesterMessageRequest(BaseModel):
      context: str
      target_user_id: str | None = None
      user_prompt: str | None = None

  class JesterMessageResponse(BaseModel):
      message: str
      tone: str = "smart_warm_ironic"
  ```

---

## ⚙️ Environment Configuration

`backend/app/config.py` defines:
```python
OPENAI_API_KEY: SecretStr | None = None
LLM_MODEL: str = "gpt-4o-mini"
```

Currently, no active endpoints trigger OpenAI HTTP calls.

---

## 🛣️ Implementation Roadmap for AI Engine

1. **Rule-Based Meaning Dictionary**: Define explicit mappings from top Synastry aspects and daily transit patterns to psychological core themes.
2. **System Prompt Hardening**: Codify the JESTER voice rules, humor vs. mockery boundaries, and few-shot examples into `prompts.py`.
3. **Async OpenAI Client Integration**: Implement robust API calling in `jester.py` with exponential backoff, timeout handling, and fallback to pre-written witty templates if API is unreachable.
4. **Structured JSON Validation**: Enforce strict JSON output parsing into `JesterMessageResponse`.

