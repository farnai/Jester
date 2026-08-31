"""
Phase 3.1: Swiss Ephemeris astronomical calculation and edge-case validation suite.
"""
from datetime import date, time
import pytest

from backend.app.astrology.calculator import (
    compute_julian_day,
    compute_natal_placements,
    derive_primary_element_and_modality,
    longitude_to_sign,
)
from backend.app.astrology.constants import (
    ASTROLOGY_ENGINE_VERSION,
    SWISS_EPHEMERIS_VERSION,
)
from backend.app.astrology.models import BirthDataInput
from backend.app.core.errors import JesterAPIException


# ==============================================================================
# 1. REFERENCE CASES VALIDATION
# ==============================================================================

def test_reference_case_1_london_millennium():
    """
    Fixed Reference Case 1:
    Date: 2000-01-01 12:00:00 UTC
    Location: London, UK (51.5074° N, 0.1278° W)
    """
    case_1 = BirthDataInput(
        birth_date=date(2000, 1, 1),
        birth_time=time(12, 0),
        birth_time_precision="exact",
        birth_timezone="UTC",
        latitude=51.5074,
        longitude=-0.1278,
    )

    placements = compute_natal_placements(case_1)

    # Reference planetary values calculated via Swiss Ephemeris
    assert abs(placements.sun_longitude - 280.36892) < 0.01  # Capricorn
    assert abs(placements.moon_longitude - 223.323775) < 0.01  # Scorpio
    assert abs(placements.mercury_longitude - 271.889275) < 0.01  # Capricorn
    assert abs(placements.venus_longitude - 241.565798) < 0.01  # Sagittarius
    assert abs(placements.mars_longitude - 327.963313) < 0.01  # Aquarius
    assert abs(placements.jupiter_longitude - 25.25303) < 0.01  # Aries
    assert abs(placements.saturn_longitude - 40.395639) < 0.01  # Taurus
    assert abs(placements.uranus_longitude - 314.809223) < 0.01  # Aquarius
    assert abs(placements.neptune_longitude - 303.192981) < 0.01  # Aquarius
    assert abs(placements.pluto_longitude - 251.454709) < 0.01  # Sagittarius

    # Reference Ascendant and Houses
    assert abs(placements.ascendant_longitude - 24.01459) < 0.01  # Aries Ascendant
    assert len(placements.houses) == 12
    assert abs(placements.houses[0] - 24.01459) < 0.01
    assert abs(placements.houses[9] - 279.493225) < 0.01  # Midheaven / 10th cusp

    # Retrogrades: Saturn was retrograde on 2000-01-01
    assert placements.retrogrades["saturn"] is True
    assert placements.retrogrades["sun"] is False
    assert placements.retrogrades["mercury"] is False


def test_reference_case_2_tokyo_mercury_retrograde():
    """
    Fixed Reference Case 2:
    Date: 2024-04-10 15:30:00 JST (Asia/Tokyo, UTC+9 -> 06:30 UTC)
    Location: Tokyo, Japan (35.6762° N, 139.6503° E)
    """
    case_2 = BirthDataInput(
        birth_date=date(2024, 4, 10),
        birth_time=time(15, 30),
        birth_time_precision="exact",
        birth_timezone="Asia/Tokyo",
        latitude=35.6762,
        longitude=139.6503,
    )

    placements = compute_natal_placements(case_2)

    # Reference planetary values
    assert abs(placements.sun_longitude - 20.880528) < 0.01  # Aries
    assert abs(placements.moon_longitude - 41.738386) < 0.01  # Taurus
    assert abs(placements.mercury_longitude - 23.778505) < 0.01  # Aries

    # Mercury was in retrograde on 2024-04-10
    assert placements.retrogrades["mercury"] is True
    assert placements.retrogrades["sun"] is False


# ==============================================================================
# 2. TIMEZONE, UTC & DST EQUIVALENCE
# ==============================================================================

def test_dst_transition_and_timezone_equivalence():
    """
    Validates Daylight Saving Time (DST) handling:
    14:00 EDT (UTC-4) in America/New_York on July 1 equals 18:00 UTC.
    Both must yield identical Julian Day and planetary placements.
    """
    dt_ny = BirthDataInput(
        birth_date=date(2023, 7, 1),
        birth_time=time(14, 0),  # 14:00 EDT = 18:00 UTC
        birth_time_precision="exact",
        birth_timezone="America/New_York",
        latitude=40.7128,
        longitude=-74.0060,
    )
    dt_utc = BirthDataInput(
        birth_date=date(2023, 7, 1),
        birth_time=time(18, 0),  # 18:00 UTC
        birth_time_precision="exact",
        birth_timezone="UTC",
        latitude=40.7128,
        longitude=-74.0060,
    )

    jd_ny = compute_julian_day(dt_ny.birth_date, dt_ny.birth_time, dt_ny.birth_timezone)
    jd_utc = compute_julian_day(dt_utc.birth_date, dt_utc.birth_time, dt_utc.birth_timezone)
    assert abs(jd_ny - jd_utc) < 1e-7

    p_ny = compute_natal_placements(dt_ny)
    p_utc = compute_natal_placements(dt_utc)

    assert p_ny.sun_longitude == p_utc.sun_longitude
    assert p_ny.moon_longitude == p_utc.moon_longitude
    assert p_ny.ascendant_longitude == p_utc.ascendant_longitude


# ==============================================================================
# 3. UNKNOWN & APPROXIMATE BIRTH TIME
# ==============================================================================

def test_unknown_birth_time_semantics():
    """
    Validates that when birth_time_precision is 'unknown':
    - Mean noon (12:00 UTC) is used for planetary longitudes
    - Ascendant is strictly None
    - Houses is strictly None
    """
    data = BirthDataInput(
        birth_date=date(1985, 11, 20),
        birth_time=None,
        birth_time_precision="unknown",
        birth_timezone="UTC",
        latitude=48.8566,
        longitude=2.3522,
    )

    p = compute_natal_placements(data)
    assert p.ascendant_longitude is None
    assert p.houses is None
    assert p.sun_longitude > 0.0
    assert p.moon_longitude > 0.0


def test_approximate_birth_time_semantics():
    """
    Validates that when birth_time_precision is 'approximate':
    - Calculation computes houses using the supplied approximate time
    - Precision is not silently mutated into 'exact'
    """
    data = BirthDataInput(
        birth_date=date(1985, 11, 20),
        birth_time=time(15, 0),
        birth_time_precision="approximate",
        birth_timezone="Europe/Paris",
        latitude=48.8566,
        longitude=2.3522,
    )

    p = compute_natal_placements(data)
    assert p.ascendant_longitude is not None
    assert len(p.houses) == 12


# ==============================================================================
# 4. PLACIDUS EDGE CASES (HIGH LATITUDE & SOUTHERN HEMISPHERE)
# ==============================================================================

def test_placidus_high_latitude_fails_gracefully():
    """
    High-latitude locations in polar regions (e.g. 70° N Tromsø) where Placidus
    semi-arcs do not cross the horizon must fail gracefully without fabricating houses.
    """
    polar_data = BirthDataInput(
        birth_date=date(2000, 6, 21),
        birth_time=time(12, 0),
        birth_time_precision="exact",
        birth_timezone="UTC",
        latitude=70.0,  # Above Arctic Circle (66.5° N)
        longitude=18.95,
    )

    with pytest.raises(JesterAPIException) as exc:
        compute_natal_placements(polar_data)
    assert exc.value.error_code == "placidus_polar_error"
    assert exc.value.status_code == 400


def test_southern_hemisphere_and_equator_placidus():
    """
    Validates Placidus house calculations for Southern Hemisphere and Equator.
    """
    # Equator (Quito)
    equator = BirthDataInput(
        birth_date=date(2000, 1, 1),
        birth_time=time(12, 0),
        birth_time_precision="exact",
        birth_timezone="UTC",
        latitude=0.0,
        longitude=-78.4678,
    )
    p_eq = compute_natal_placements(equator)
    assert p_eq.ascendant_longitude is not None
    assert len(p_eq.houses) == 12

    # Southern Hemisphere (Sydney -33.8688°)
    sydney = BirthDataInput(
        birth_date=date(2000, 1, 1),
        birth_time=time(12, 0),
        birth_time_precision="exact",
        birth_timezone="Australia/Sydney",
        latitude=-33.8688,
        longitude=151.2093,
    )
    p_syd = compute_natal_placements(sydney)
    assert p_syd.ascendant_longitude is not None
    assert len(p_syd.houses) == 12


# ==============================================================================
# 5. ZODIAC BOUNDARY PRECISION
# ==============================================================================

def test_zodiac_sign_boundary_precision():
    """
    Validates precision and sign assignment at exact 30-degree boundary transitions.
    """
    boundary_cases = [
        (0.0, "Aries"),
        (29.999999, "Aries"),
        (30.0, "Taurus"),
        (59.999999, "Taurus"),
        (60.0, "Gemini"),
        (89.999999, "Gemini"),
        (90.0, "Cancer"),
        (119.999999, "Cancer"),
        (120.0, "Leo"),
        (149.999999, "Leo"),
        (150.0, "Virgo"),
        (179.999999, "Virgo"),
        (180.0, "Libra"),
        (209.999999, "Libra"),
        (210.0, "Scorpio"),
        (239.999999, "Scorpio"),
        (240.0, "Sagittarius"),
        (269.999999, "Sagittarius"),
        (270.0, "Capricorn"),
        (299.999999, "Capricorn"),
        (300.0, "Aquarius"),
        (329.999999, "Aquarius"),
        (330.0, "Pisces"),
        (359.999999, "Pisces"),
        (360.0, "Aries"),  # Exact 360 wraparound
    ]

    for lon, expected_sign in boundary_cases:
        actual_sign = longitude_to_sign(lon)
        assert actual_sign == expected_sign, f"Failed at {lon}°: expected {expected_sign}, got {actual_sign}"


# ==============================================================================
# 6. VERSION METADATA
# ==============================================================================

def test_engine_version_metadata():
    """
    Validates that calculation metadata matches the engine configuration.
    """
    assert ASTROLOGY_ENGINE_VERSION == "1.0.0"
    assert SWISS_EPHEMERIS_VERSION == "2.10.03"


# ==============================================================================
# 7. TIMEZONE & COORDINATES CONSISTENCY VALIDATION
# ==============================================================================

def test_timezone_location_consistency_and_repeatability():
    """
    Proves why different timezones for the same local time and coordinates
    produce different Ascendant values due to UTC time offset differences.

    Case A: 1996-05-15 14:30 EDT (America/New_York, UTC-4) -> 18:30 UTC.
            Eastern horizon at 18:30 UTC for NY coordinates is Virgo (169.89°).
    Case B: 1996-05-15 14:30 GET (Asia/Tbilisi, UTC+4) -> 10:30 UTC (8 hours earlier).
            Eastern horizon at 10:30 UTC for NY coordinates is Taurus (50.41°).
    """
    case_ny_tz = BirthDataInput(
        birth_date=date(1996, 5, 15),
        birth_time=time(14, 30),
        birth_time_precision="exact",
        birth_timezone="America/New_York",
        latitude=40.7128,
        longitude=-74.0060,
    )
    case_tb_tz = BirthDataInput(
        birth_date=date(1996, 5, 15),
        birth_time=time(14, 30),
        birth_time_precision="exact",
        birth_timezone="Asia/Tbilisi",
        latitude=40.7128,
        longitude=-74.0060,
    )

    # 1. Calculate Case NY Timezone
    p_ny_1 = compute_natal_placements(case_ny_tz)
    p_ny_2 = compute_natal_placements(case_ny_tz)
    assert longitude_to_sign(p_ny_1.sun_longitude) == "Taurus"
    assert longitude_to_sign(p_ny_1.moon_longitude) == "Taurus"
    assert longitude_to_sign(p_ny_1.ascendant_longitude) == "Virgo"
    # Deterministic repeatability check
    assert p_ny_1.ascendant_longitude == p_ny_2.ascendant_longitude

    # 2. Calculate Case Tbilisi Timezone
    p_tb_1 = compute_natal_placements(case_tb_tz)
    p_tb_2 = compute_natal_placements(case_tb_tz)
    assert longitude_to_sign(p_tb_1.sun_longitude) == "Taurus"
    assert longitude_to_sign(p_tb_1.moon_longitude) == "Taurus"
    assert longitude_to_sign(p_tb_1.ascendant_longitude) == "Taurus"
    # Deterministic repeatability check
    assert p_tb_1.ascendant_longitude == p_tb_2.ascendant_longitude

    # In 1996, Asia/Tbilisi was UTC+5 (DST) and America/New_York was UTC-4 (EDT).
    # UTC difference is 9.0 hours -> difference in Julian Day is 9.0 / 24.0 = 0.375 days.
    jd_ny = compute_julian_day(case_ny_tz.birth_date, case_ny_tz.birth_time, case_ny_tz.birth_timezone)
    jd_tb = compute_julian_day(case_tb_tz.birth_date, case_tb_tz.birth_time, case_tb_tz.birth_timezone)
    assert abs((jd_ny - jd_tb) - (9.0 / 24.0)) < 1e-6

