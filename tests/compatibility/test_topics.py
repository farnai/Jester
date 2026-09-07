"""
Unit tests for JESTER Phase 6C.1 - Conversation Intelligence & Topic Selection.
Validates topic diversity across distinct relationship patterns, determinism,
deduplication, symmetry, canonical vocabulary bounds, and safe fallbacks.
"""
import uuid
import pytest

from backend.app.compatibility.rules import (
    CANONICAL_TOPICS,
    extract_best_topics,
    extract_conversation_starters,
)
from backend.app.compatibility.synastry import NatalInputPayload, SynastryEngine


def test_canonical_vocabulary_integrity():
    """All generated topics must belong strictly to the 16 canonical topics."""
    assert len(CANONICAL_TOPICS) == 16
    for topic in CANONICAL_TOPICS:
        assert isinstance(topic, str)
        assert len(topic) > 0


def test_topic_diversity_across_distinct_patterns():
    """
    Different astrological signal configurations must yield distinct,
    semantically relevant topic sets.
    """
    # Pattern 1: Intellectual Flow (Mercury aspects)
    intellectual_signals = [
        {"type": "mercury_trine_mercury", "category": "communication", "strength": "high"},
        {"type": "sun_trine_mercury", "category": "communication", "strength": "medium"},
    ]
    topics_intellectual = extract_best_topics(signals=intellectual_signals)

    # Pattern 2: Emotional Harmony & Affinity (Moon-Venus, Sun-Moon)
    emotional_signals = [
        {"type": "sun_trine_moon", "category": "harmony", "strength": "high"},
        {"type": "moon_trine_venus", "category": "harmony", "strength": "high"},
    ]
    topics_emotional = extract_best_topics(signals=emotional_signals)

    # Pattern 3: Dynamic Drive & Tension (Mars-Saturn, Sun-Mars)
    action_signals = [
        {"type": "sun_trine_mars", "category": "attraction", "strength": "high"},
        {"type": "mars_square_saturn", "category": "growth", "strength": "medium"},
    ]
    topics_action = extract_best_topics(signals=action_signals)

    # Pattern 4: Grounded Craft & Long-Term Stability (Saturn aspects)
    grounded_signals = [
        {"type": "saturn_trine_sun", "category": "stability", "strength": "high"},
        {"type": "saturn_trine_venus", "category": "stability", "strength": "high"},
    ]
    topics_grounded = extract_best_topics(signals=grounded_signals)

    # Assert all sets are non-empty and bounded to max 4
    for tset in [topics_intellectual, topics_emotional, topics_action, topics_grounded]:
        assert 1 <= len(tset) <= 4
        assert len(set(tset)) == len(tset)  # No duplicates
        assert set(tset).issubset(CANONICAL_TOPICS)  # Only canonical topics

    # Assert distinct sets across distinct archetypes
    assert topics_intellectual != topics_emotional
    assert topics_intellectual != topics_action
    assert topics_emotional != topics_action
    assert topics_grounded != topics_intellectual

    # Verify domain relevance
    assert "ideas" in topics_intellectual or "books" in topics_intellectual
    assert "psychology" in topics_emotional or "music" in topics_emotional
    assert "ambition" in topics_action or "adventure" in topics_action
    assert "lifestyle" in topics_grounded or "architecture" in topics_grounded or "design" in topics_grounded


def test_deduplication_and_ordering_determinism():
    """Repeated signals or overlapping candidates must be cleanly deduplicated and deterministically ordered."""
    overlapping_signals = [
        {"type": "sun_trine_moon", "category": "harmony", "strength": "high"},
        {"type": "sun_sextile_moon", "category": "harmony", "strength": "high"},
        {"type": "moon_conjunction_venus", "category": "harmony", "strength": "high"},
    ]

    res1 = extract_best_topics(signals=overlapping_signals)
    res2 = extract_best_topics(signals=overlapping_signals)

    # Determinism: identical input must yield identical output
    assert res1 == res2
    # Deduplication: no duplicate topic keys
    assert len(res1) == len(set(res1))
    assert len(res1) <= 4


def test_empty_and_insufficient_aspects_fallback():
    """Empty signals or insufficient aspects must safely return balanced fallback topics."""
    # Empty signals
    fallback_empty = extract_best_topics(signals=[])
    assert len(fallback_empty) == 4
    assert set(fallback_empty).issubset(CANONICAL_TOPICS)

    # None signals
    fallback_none = extract_best_topics(signals=None)
    assert len(fallback_none) == 4
    assert set(fallback_none).issubset(CANONICAL_TOPICS)

    # Insufficient aspects notice
    insufficient = [{"type": "insufficient_aspects", "category": "notice", "strength": "low"}]
    fallback_insufficient = extract_best_topics(signals=insufficient)
    assert len(fallback_insufficient) == 4
    assert set(fallback_insufficient).issubset(CANONICAL_TOPICS)


def test_legacy_call_signature_backward_compatibility():
    """Calling extract_best_topics without signals (legacy arguments) must still function properly."""
    res_air = extract_best_topics(dominant_element="air")
    assert set(res_air).issubset(CANONICAL_TOPICS)
    assert "ideas" in res_air

    res_fire = extract_best_topics(dominant_element="fire")
    assert set(res_fire).issubset(CANONICAL_TOPICS)
    assert "travel" in res_fire

    res_water = extract_best_topics(dominant_element="water")
    assert set(res_water).issubset(CANONICAL_TOPICS)
    assert "psychology" in res_water

    res_earth = extract_best_topics(dominant_element="earth")
    assert set(res_earth).issubset(CANONICAL_TOPICS)
    assert "lifestyle" in res_earth


def test_synastry_engine_end_to_end_topics():
    """SynastryEngine must populate distinct, valid, symmetric topics on calculated results."""
    engine = SynastryEngine()

    def make_payload(**planets: float) -> NatalInputPayload:
        default = {
            "sun": 0.0, "moon": 30.0, "mercury": 15.0, "venus": 45.0, "mars": 60.0,
            "jupiter": 90.0, "saturn": 120.0, "uranus": 150.0, "neptune": 180.0, "pluto": 210.0,
        }
        default.update(planets)
        return NatalInputPayload(
            user_id=uuid.uuid4(),
            birth_data_version=1,
            birth_time_precision="exact",
            planet_longitudes=default,
            ascendant_longitude=0.0,
        )

    # Pair 1: Intellectual Mercury Trine
    p1_a = make_payload(mercury=0.0, sun=10.0)
    p1_b = make_payload(mercury=120.0, sun=200.0)
    res1 = engine.calculate(p1_a, p1_b)

    # Pair 2: Magnetic Venus-Mars Opposition
    p2_a = make_payload(venus=0.0, sun=40.0)
    p2_b = make_payload(mars=180.0, sun=250.0)
    res2 = engine.calculate(p2_a, p2_b)

    assert len(res1.best_topics) <= 4
    assert len(res2.best_topics) <= 4
    assert set(res1.best_topics).issubset(CANONICAL_TOPICS)
    assert set(res2.best_topics).issubset(CANONICAL_TOPICS)

    # Symmetry check
    res1_rev = engine.calculate(p1_b, p1_a)
    assert res1.best_topics == res1_rev.best_topics


def test_conversation_starters_georgian_rules_integrity():
    """
    Every conversation starter in CONVERSATION_STARTER_RULES and DEFAULT_CONVERSATION_STARTERS
    must be natural Georgian text and contain NO English/ASCII letters.
    """
    import re
    from backend.app.compatibility.rules import (
        CONVERSATION_STARTER_RULES,
        DEFAULT_CONVERSATION_STARTERS,
    )

    georgian_pattern = re.compile(r"[\u10D0-\u10FA]")
    english_pattern = re.compile(r"[a-zA-Z]")

    # Check defaults
    assert len(DEFAULT_CONVERSATION_STARTERS) >= 3
    for starter in DEFAULT_CONVERSATION_STARTERS:
        assert georgian_pattern.search(starter), f"Starter must contain Georgian characters: {starter}"
        assert not english_pattern.search(starter), f"Starter contains English characters: {starter}"

    # Check all rules
    assert len(CONVERSATION_STARTER_RULES) > 0
    for signal_type, starters in CONVERSATION_STARTER_RULES.items():
        assert len(starters) > 0
        for starter in starters:
            assert georgian_pattern.search(starter), f"Starter for {signal_type} must contain Georgian characters: {starter}"
            assert not english_pattern.search(starter), f"Starter for {signal_type} contains English characters: {starter}"


def test_conversation_starters_deterministic_and_deduplicated():
    """
    extract_conversation_starters must return up to 3 deterministic,
    deduplicated Georgian prompts based on top signals.
    """
    import re
    english_pattern = re.compile(r"[a-zA-Z]")

    signals = [
        {"type": "sun_trine_moon", "category": "harmony", "strength": "high"},
        {"type": "mercury_trine_mercury", "category": "communication", "strength": "high"},
        {"type": "venus_conjunction_mars", "category": "attraction", "strength": "high"},
    ]

    res1 = extract_conversation_starters(signals)
    res2 = extract_conversation_starters(signals)

    assert res1 == res2
    assert 1 <= len(res1) <= 3
    assert len(res1) == len(set(res1))

    for item in res1:
        assert not english_pattern.search(item), f"Leaked English in starter: {item}"
        assert len(item.strip()) > 10


def test_conversation_starters_empty_fallback():
    """Empty or unmapped signals must gracefully fall back to Georgian default starters."""
    import re
    english_pattern = re.compile(r"[a-zA-Z]")

    empty_starters = extract_conversation_starters([])
    assert len(empty_starters) == 3
    for item in empty_starters:
        assert not english_pattern.search(item), f"Leaked English in fallback: {item}"

    # Unmapped signal type
    unmapped_starters = extract_conversation_starters([{"type": "unknown_aspect_signal"}])
    assert len(unmapped_starters) == 3
    for item in unmapped_starters:
        assert not english_pattern.search(item), f"Leaked English in fallback: {item}"


def test_synastry_engine_end_to_end_georgian_starters():
    """SynastryEngine end-to-end output must contain Georgian conversation starters."""
    import re
    english_pattern = re.compile(r"[a-zA-Z]")
    engine = SynastryEngine()

    def make_payload(**planets: float) -> NatalInputPayload:
        default = {
            "sun": 0.0, "moon": 30.0, "mercury": 15.0, "venus": 45.0, "mars": 60.0,
            "jupiter": 90.0, "saturn": 120.0, "uranus": 150.0, "neptune": 180.0, "pluto": 210.0,
        }
        default.update(planets)
        return NatalInputPayload(
            user_id=uuid.uuid4(),
            birth_data_version=1,
            birth_time_precision="exact",
            planet_longitudes=default,
            ascendant_longitude=0.0,
        )

    p1 = make_payload(sun=0.0, moon=120.0)
    p2 = make_payload(sun=120.0, moon=0.0)

    res = engine.calculate(p1, p2)
    assert 1 <= len(res.conversation_starters) <= 3
    for starter in res.conversation_starters:
        assert not english_pattern.search(starter), f"Leaked English in SynastryEngine starter: {starter}"

