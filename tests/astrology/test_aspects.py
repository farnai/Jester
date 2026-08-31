"""
Comprehensive unit tests for the deterministic astrology aspects module.
Validates angular distance, circle wraparound, orb modifiers, quadratic strength decay,
and aspect detection.
"""
import pytest
from backend.app.astrology.aspects import (
    ASPECT_DEFINITIONS,
    LUMINARIES,
    angular_distance,
    calculate_aspect_strength,
    detect_aspect,
    get_max_orb,
    normalize_angle,
)


def test_normalize_angle():
    assert normalize_angle(0.0) == 0.0
    assert normalize_angle(360.0) == 0.0
    assert normalize_angle(370.5) == 10.5
    assert normalize_angle(-10.0) == 350.0
    assert normalize_angle(720.0) == 0.0


def test_angular_distance_direct():
    assert angular_distance(10.0, 50.0) == 40.0
    assert angular_distance(50.0, 10.0) == 40.0
    assert angular_distance(0.0, 180.0) == 180.0
    assert angular_distance(180.0, 0.0) == 180.0


def test_angular_distance_wraparound():
    # 355 to 5 crosses 0/360 boundary -> 10 deg
    assert angular_distance(355.0, 5.0) == 10.0
    assert angular_distance(5.0, 355.0) == 10.0
    assert angular_distance(1.0, 359.0) == 2.0
    assert angular_distance(350.0, 20.0) == 30.0


def test_aspect_definitions_coverage():
    assert "conjunction" in ASPECT_DEFINITIONS
    assert "sextile" in ASPECT_DEFINITIONS
    assert "square" in ASPECT_DEFINITIONS
    assert "trine" in ASPECT_DEFINITIONS
    assert "opposition" in ASPECT_DEFINITIONS

    assert ASPECT_DEFINITIONS["conjunction"].target_angle == 0.0
    assert ASPECT_DEFINITIONS["conjunction"].base_max_orb == 8.0
    assert ASPECT_DEFINITIONS["conjunction"].base_weight == 1.00

    assert ASPECT_DEFINITIONS["sextile"].target_angle == 60.0
    assert ASPECT_DEFINITIONS["sextile"].base_max_orb == 6.0
    assert ASPECT_DEFINITIONS["sextile"].base_weight == 0.70

    assert ASPECT_DEFINITIONS["square"].target_angle == 90.0
    assert ASPECT_DEFINITIONS["square"].base_max_orb == 7.0
    assert ASPECT_DEFINITIONS["square"].base_weight == 0.75

    assert ASPECT_DEFINITIONS["trine"].target_angle == 120.0
    assert ASPECT_DEFINITIONS["trine"].base_max_orb == 8.0
    assert ASPECT_DEFINITIONS["trine"].base_weight == 0.90

    assert ASPECT_DEFINITIONS["opposition"].target_angle == 180.0
    assert ASPECT_DEFINITIONS["opposition"].base_max_orb == 8.0
    assert ASPECT_DEFINITIONS["opposition"].base_weight == 0.85


def test_get_max_orb_modifiers():
    # Non-luminary base
    assert get_max_orb("trine", "mercury", "venus") == 8.0
    assert get_max_orb("sextile", "mars", "jupiter") == 6.0
    assert get_max_orb("square", "mercury", "saturn") == 7.0

    # Luminary boost (+2.0)
    assert get_max_orb("conjunction", "sun", "moon") == 10.0
    assert get_max_orb("trine", "sun", "jupiter") == 10.0
    assert get_max_orb("opposition", "venus", "moon") == 10.0
    assert get_max_orb("square", "sun", "mars") == 9.0
    assert get_max_orb("sextile", "moon", "mercury") == 8.0

    # Ascendant constraint: capped at 6.0
    assert get_max_orb("conjunction", "sun", "ascendant") == 6.0
    assert get_max_orb("trine", "ascendant", "moon") == 6.0
    assert get_max_orb("square", "venus", "ascendant") == 6.0
    assert get_max_orb("sextile", "ascendant", "mars") == 6.0


def test_calculate_aspect_strength_quadratic_decay():
    # Exact -> 1.0
    assert calculate_aspect_strength(0.0, 8.0) == 1.0
    # Half-orb -> (1 - 4/8)^2 = 0.5^2 = 0.25
    assert calculate_aspect_strength(4.0, 8.0) == 0.25
    # 1/4 orb -> (1 - 2/8)^2 = 0.75^2 = 0.5625
    assert calculate_aspect_strength(2.0, 8.0) == 0.5625
    # At boundary -> 0.0
    assert calculate_aspect_strength(8.0, 8.0) == 0.0
    # Beyond boundary -> 0.0
    assert calculate_aspect_strength(8.5, 8.0) == 0.0
    # Zero or negative max orb safety
    assert calculate_aspect_strength(1.0, 0.0) == 0.0


@pytest.mark.parametrize(
    "p1, lon1, p2, lon2, expected_type, expected_angle, expected_dist, expected_orb",
    [
        ("sun", 0.0, "moon", 0.0, "conjunction", 0.0, 0.0, 0.0),
        ("mercury", 10.0, "venus", 70.0, "sextile", 60.0, 60.0, 0.0),
        ("mars", 0.0, "jupiter", 90.0, "square", 90.0, 90.0, 0.0),
        ("sun", 0.0, "moon", 120.0, "trine", 120.0, 120.0, 0.0),
        ("sun", 10.0, "saturn", 190.0, "opposition", 180.0, 180.0, 0.0),
        # Wraparound cases
        ("sun", 359.0, "venus", 1.0, "conjunction", 0.0, 2.0, 2.0),
        ("moon", 350.0, "mars", 52.0, "sextile", 60.0, 62.0, 2.0),
        ("sun", 355.0, "uranus", 85.0, "square", 90.0, 90.0, 0.0),
        ("jupiter", 350.0, "neptune", 110.0, "trine", 120.0, 120.0, 0.0),
        ("pluto", 5.0, "sun", 185.0, "opposition", 180.0, 180.0, 0.0),
    ],
)
def test_detect_aspect_exact_and_wraparound(
    p1, lon1, p2, lon2, expected_type, expected_angle, expected_dist, expected_orb
):
    asp = detect_aspect(p1, lon1, p2, lon2)
    assert asp is not None
    assert asp.aspect_type == expected_type
    assert asp.target_angle == expected_angle
    assert asp.actual_distance == expected_dist
    assert asp.orb_diff == expected_orb
    assert asp.strength > 0.0


def test_detect_aspect_outside_orb():
    # Distance is 45 deg - no major aspect (Sextile is 60, Conjunction is 0)
    asp = detect_aspect("mercury", 0.0, "mars", 45.0)
    assert asp is None

    # Distance 100 deg between mercury & mars: Square target is 90, orb is 10 deg > base max 7
    asp2 = detect_aspect("mercury", 0.0, "mars", 100.0)
    assert asp2 is None
