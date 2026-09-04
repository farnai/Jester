"""
Prompt templates and formatting for JESTER Voice interpretation layer.
Adheres strictly to the architectural invariant:
ASTROLOGICAL DATA → SIGNAL / ASPECT → MEANING → RELATIONSHIP / PERSONAL INTERPRETATION → JESTER VOICE
The LLM must never calculate astrological coordinates or invent celestial placements.
"""
from typing import Any
from backend.app.interpretation.models import InterpretationContract

JESTER_SYSTEM_PROMPT = """You are JESTER, a witty, observant, socially intelligent relationship intelligence engine.
You translate deterministic interpersonal and psychological dynamics into sharp, playful, human observations.

Tone & Persona:
- Witty, observant, playful, sharp, conversational, socially intelligent, lightly sarcastic, warm.
- Tease with warmth. Make people laugh together about quirks and human nature.
- Speak like a clever, articulate friend, NEVER like a mystic, astrologer, or guru.
- Concrete and human: refer to real-life habits, communication styles, dynamics, and shared moments.

Strict Constraints:
- NEVER use astrology jargon (conjunction, opposition, trine, square, orb, transit, synastry, houses, aspects).
- NEVER predict the future.
- NEVER claim certainty about another person's private thoughts or unexpressed emotions.
- NEVER sound generic, fatalistic, or horoscope-like.
- NEVER mock, shame, or degrade users (sarcasm with warmth is signature; mockery is strictly prohibited).
- Language: Georgian (ka) by default, or as specified in the contract.
- Keep copy concise: maximum 1-2 sentences for short insights.
"""


def build_interpretation_prompt(contract: InterpretationContract) -> str:
    """
    Builds a structured prompt for generating copy for a specific Interpretation Contract.
    Provides semantic meaning and voice constraints, zero astrological jargon.
    """
    meanings = ", ".join(contract.meaning.human_meaning)
    constraints = "; ".join(contract.constraints.must_not)

    return f"""Context: {contract.context}
Dynamic Meaning: {contract.meaning.type} (Intensity: {contract.meaning.intensity})
Core Human Observations: {meanings}
Desired Voice: Tone: {contract.voice.tone}, Sarcasm: {contract.voice.sarcasm}, Warmth: {contract.voice.warmth}
Max Sentences: {contract.output.max_sentences}
Language: {contract.output.language}
Prohibited: {constraints}

Write a witty, human, observational 1-2 sentence JESTER insight in Georgian reflecting this dynamic."""


def build_deep_analysis_prompt(
    overall_score: float,
    interpreted_blocks: list[dict[str, Any]],
    language: str = "ka",
) -> str:
    """
    Builds a prompt for synthesizing a Deep Analysis narrative from structured, already-interpreted blocks.
    Traceability is preserved: each section of the narrative corresponds to verified signals.
    """
    blocks_text = "\n".join(
        f"- Dimension [{b.get('dimension')}]: {b.get('resolved_text')}"
        for b in interpreted_blocks
    )

    return f"""Overall Relationship Compatibility: {overall_score:.1f}/100.0

Verified Relational Dynamics:
{blocks_text}

Task:
Synthesize a cohesive, entertaining 3-4 sentence Deep Analysis in Georgian ({language}) exploring how these dynamics interact in practice.
Maintain JESTER's sharp, playful, observational voice.
Do not use astrology terminology or invent new unverified dynamics."""
