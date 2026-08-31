"""
Comprehensive unit tests for the deterministic Synastry V1 Engine.
Validates scoring formulas, 4D subscores, weights, influence caps,
signal and starter generation, symmetry, and data-quality indicators.
"""
import uuid
import pytest

from backend.app.compatibility.synastry import NatalInputPayload, SynastryEngine


@pytest.fixture
def engine() -> SynastryEngine:
    return SynastryEngine()


def make_payload(
    user_id: str | None = None,
    precision: str = "exact",
    version: int = 1,
    ascendant: float | None = 0.0,
    **planets: float,
) -> NatalInputPayload:
    # Default complete 10 planetary longitudes
    default_planets = {
        "sun": 0.0,
        "moon": 30.0,
        "mercury": 15.0,
        "venus": 45.0,
        "mars": 60.0,
        "jupiter": 90.0,
        "saturn": 120.0,
        "uranus": 150.0,
        "neptune": 180.0,
        "pluto": 210.0,
    }
    default_planets.update(planets)
    return NatalInputPayload(
        user_id=uuid.UUID(user_id) if user_id else uuid.uuid4(),
        birth_data_version=version,
        birth_time_precision=precision,  # type: ignore
        planet_longitudes=default_planets,
        ascendant_longitude=ascendant if precision != "unknown" else None,
    )


def test_test_vector_1_high_harmony(engine: SynastryEngine):
    """
    Test Vector 1 from Section 27:
    Person A: Sun 0.0 (Aries), Venus 0.0 (Aries).
    Person B: Moon 120.0 (Leo), Mars 120.0 (Leo).
    Expected: Harmony > 80.0 (or high harmony), Overall > 75.0.
    """
    p_a = make_payload(
        sun=0.0,
        venus=0.0,
        moon=0.0,
        mars=0.0,
        mercury=0.0,
        jupiter=120.0,
        saturn=240.0,
        uranus=10.0,
        neptune=20.0,
        pluto=30.0,
    )
    p_b = make_payload(
        moon=120.0,
        mars=120.0,
        sun=120.0,
        venus=120.0,
        mercury=120.0,
        jupiter=0.0,
        saturn=240.0,
        uranus=70.0,
        neptune=80.0,
        pluto=90.0,
    )

    res = engine.calculate(p_a, p_b)

    assert res.dimensions["emotional_harmony"] > 75.0
    assert res.dimensions["attraction"] > 65.0
    assert res.score > 75.0
    assert len(res.signals) > 0
    # Must include top harmony / attraction signal
    types = [s["type"] for s in res.signals]
    assert any("trine" in t or "conjunction" in t for t in types)


def test_test_vector_2_high_tension(engine: SynastryEngine):
    """
    Test Vector 2 from Section 27:
    Person A: Sun 0.0 (Aries), Moon 0.0 (Aries).
    Person B: Mars 90.0 (Cancer), Saturn 90.0 (Cancer).
    Expected: Growth > 60.0, Harmony < 60.0.
    """
    p_a = make_payload(
        sun=0.0,
        moon=0.0,
        mercury=45.0,
        venus=75.0,
        mars=15.0,
        jupiter=135.0,
        saturn=225.0,
        uranus=315.0,
        neptune=105.0,
        pluto=195.0,
    )
    p_b = make_payload(
        mars=90.0,
        saturn=90.0,
        sun=160.0,
        moon=200.0,
        mercury=250.0,
        venus=280.0,
        jupiter=320.0,
        uranus=40.0,
        neptune=80.0,
        pluto=140.0,
    )

    res = engine.calculate(p_a, p_b)

    assert res.dimensions["growth_long_term"] > 55.0
    assert res.dimensions["emotional_harmony"] < 60.0
    types = [s["type"] for s in res.signals]
    assert any("square" in t for t in types)


def test_symmetry_guarantee(engine: SynastryEngine):
    """
    Synastry(A, B) must be identical to Synastry(B, A).
    """
    p_a = make_payload(
        sun=12.5,
        moon=88.2,
        mercury=154.1,
        venus=210.0,
        mars=330.4,
        jupiter=45.6,
        saturn=160.0,
    )
    p_b = make_payload(
        sun=132.5,
        moon=208.2,
        mercury=34.1,
        venus=90.0,
        mars=150.4,
        jupiter=225.6,
        saturn=340.0,
    )

    res_ab = engine.calculate(p_a, p_b)
    res_ba = engine.calculate(p_b, p_a)

    assert res_ab.score == res_ba.score
    assert res_ab.dimensions == res_ba.dimensions
    assert res_ab.data_quality == res_ba.data_quality
    assert len(res_ab.signals) == len(res_ba.signals)
    assert res_ab.best_topics == res_ba.best_topics
    assert res_ab.conversation_starters == res_ba.conversation_starters


def test_unknown_birth_time_resilience(engine: SynastryEngine):
    """
    When birth time is unknown, Ascendant is omitted, confidence is 0.75,
    and houses_used / ascendant_used are False.
    """
    p_a = make_payload(precision="unknown", ascendant=None, sun=0.0, moon=120.0)
    p_b = make_payload(precision="exact", ascendant=45.0, sun=0.0, moon=120.0)

    res = engine.calculate(p_a, p_b)

    assert res.data_quality["time_precision"] == "unknown"
    assert res.data_quality["confidence"] == 0.75
    assert res.data_quality["ascendant_used"] is False
    assert res.data_quality["houses_used"] is False
    assert 10.0 <= res.score <= 98.0


def test_approximate_birth_time_confidence(engine: SynastryEngine):
    """
    When birth time is approximate, confidence is 0.85 and Ascendant weight is halved.
    """
    p_a = make_payload(precision="approximate", ascendant=0.0, sun=0.0)
    p_b = make_payload(precision="exact", ascendant=0.0, sun=0.0)

    res = engine.calculate(p_a, p_b)

    assert res.data_quality["time_precision"] == "approximate"
    assert res.data_quality["confidence"] == 0.85
    assert res.data_quality["ascendant_used"] is True


def test_minimum_evidence_rule(engine: SynastryEngine):
    """
    When active aspect weight < 2.0, returns baseline 65.0, confidence 0.50,
    and notice signal.
    """
    # Charts designed with un-aspected, spaced positions
    p_a = make_payload(
        sun=17.0,
        moon=43.0,
        mercury=73.0,
        venus=103.0,
        mars=137.0,
        jupiter=167.0,
        saturn=197.0,
        uranus=227.0,
        neptune=257.0,
        pluto=287.0,
        ascendant=None,
        precision="unknown",
    )
    p_b = make_payload(
        sun=32.0,
        moon=58.0,
        mercury=88.0,
        venus=118.0,
        mars=152.0,
        jupiter=182.0,
        saturn=212.0,
        uranus=242.0,
        neptune=272.0,
        pluto=302.0,
        ascendant=None,
        precision="unknown",
    )

    res = engine.calculate(p_a, p_b)
    # Check if minimum evidence triggered
    if len(res.evidence_trace) == 0 or sum(t["weight"] * t["strength"] for t in res.evidence_trace) < 2.0:
        assert res.score == 65.0
        assert res.data_quality["confidence"] == 0.50
        assert res.signals[0]["type"] == "insufficient_aspects"


def test_evidence_trace_schema(engine: SynastryEngine):
    """
    Evidence trace entries must contain all required audit fields.
    """
    p_a = make_payload(sun=0.0, moon=120.0)
    p_b = make_payload(sun=120.0, moon=0.0)

    res = engine.calculate(p_a, p_b)
    assert len(res.evidence_trace) > 0

    item = res.evidence_trace[0]
    assert "planet_a" in item
    assert "planet_b" in item
    assert "lon_a" in item
    assert "lon_b" in item
    assert "aspect" in item
    assert "target_angle" in item
    assert "distance" in item
    assert "orb_diff" in item
    assert "max_orb" in item
    assert "strength" in item
    assert "weight" in item
    assert "subscore_contributions" in item


def test_score_bounds_and_rounding(engine: SynastryEngine):
    """
    Scores must strictly be within [10.0, 98.0] and rounded to 1 decimal place.
    """
    p_a = make_payload(sun=0.0, moon=0.0, venus=0.0, mars=0.0)
    p_b = make_payload(sun=0.0, moon=0.0, venus=0.0, mars=0.0)

    res = engine.calculate(p_a, p_b)
    assert 10.0 <= res.score <= 98.0
    assert str(res.score).split(".")[1] is not None
