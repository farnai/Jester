# Jester — AI & LLM Subsystem Architecture

## 🤖 Overview & Current State

The `backend/app/interpretation/` directory is designed to house the Jester AI voice and LLM interpretation pipeline.

**CURRENT IMPLEMENTATION STATUS: STUB ONLY**

The codebase contains environment configurations and basic Pydantic data schemas for AI interpretations, but **no active LLM integration or prompt generation code is currently implemented**.

---

## 📁 File-by-File Inventory

### `backend/app/interpretation/engine.py` (75 bytes)
- **Status**: **STUB**
- **Content**:
  ```python
  """
  Interpretation engine mapping structured signals to human meaning.
  """
  ```
- **Missing**: Signal-to-text rules engine, planetary aspect interpretation lookup maps.

### `backend/app/interpretation/jester.py` (107 bytes)
- **Status**: **STUB**
- **Content**:
  ```python
  """
  Jester voice and LLM interface layer.
  Receives structured signals; does NOT compute compatibility.
  """
  ```
- **Missing**: OpenAI client initialization, API call dispatchers, response parsing logic.

### `backend/app/interpretation/prompts.py` (54 bytes)
- **Status**: **STUB**
- **Content**:
  ```python
  """
  Prompt templates for Jester voice generation.
  """
  ```
- **Missing**: System prompts, persona guidelines ("smart, warm, ironic"), prompt formatting templates.

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

`backend/app/config.py` includes the following LLM settings:
```python
OPENAI_API_KEY: SecretStr | None = None
LLM_MODEL: str = "gpt-4o-mini"
```

- In `.env.example`, `OPENAI_API_KEY=your_openai_api_key_here` is defined as an optional variable.
- No endpoints currently inject `OPENAI_API_KEY` or invoke external OpenAI HTTP requests.

---

## 🛣️ Planned AI Architecture (Roadmap)

When implemented, the AI interpretation subsystem will adhere to the following principles:
1. **Separation of Computation & Interpretation**:
   - The LLM will **never** calculate planetary positions or compatibility scores.
   - All astronomical input will be provided as structured signals (e.g. `{"aspect": "Sun square Mars", "orb": 1.2}`) generated deterministically by the Python/C astrology engine.
2. **Jester Voice Persona**:
   - Persona: Smart, warm, witty, slightly ironic, non-fatalistic.
3. **Structured Response Contracts**:
   - LLM output will be parsed into validated Pydantic models (`JesterMessageResponse`).
