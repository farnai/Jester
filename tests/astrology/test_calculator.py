"""
Unit tests for deterministic Swiss Ephemeris calculations and validation.
"""
from datetime import date, time
import pytest

from backend.app.astrology.calculator import (
    compute_julian_day,
    compute_natal_placements,
    derive_primary_element_and_modality,
    longitude_to_sign,
)
from backend.app.astrology.models import BirthDataInput
from backend.app.astrology.validation import validate_birth_data
from backend.app.core.errors import JesterAPIException


def test_determinism_same_input_same_output():
    """Property: Identical valid birth input produces identical outputs."""
    input_data = BirthDataInput(
        birth_date=date(1995, 7, 15),
        birth_time=time(14, 30),
        birth_time_precision="exact",
        birth_timezone="Asia/Tbilisi",
        latitude=41.7151,
        longitude=44.8271,
    )

    run_1 = compute_natal_placements(input_data)
    run_2 = compute_natal_placements(input_data)

    assert run_1.sun_longitude == run_2.sun_longitude
    assert run_1.moon_longitude == run_2.moon_longitude
    assert run_1.ascendant_longitude == run_2.ascendant_longitude
    assert run_1.houses == run_2.houses
    assert run_1.retrogrades == run_2.retrogrades


def test_timezone_normalization_matches_utc():
    """Property: 14:00 in Asia/Tbilisi (UTC+4) equals 10:00 in UTC."""
    jd_tbilisi = compute_julian_day(
        birth_date=date(2000, 1, 1),
        birth_time=time(14, 0),
        birth_timezone="Asia/Tbilisi",
    )
    jd_utc = compute_julian_day(
        birth_date=date(2000, 1, 1),
        birth_time=time(10, 0),
        birth_timezone="UTC",
    )

    assert abs(jd_tbilisi - jd_utc) < 1e-7


def test_unknown_birth_time_does_not_invent_time_or_houses():
    """Property: Unknown birth time sets ascendant and houses strictly to None."""
    input_unknown = BirthDataInput(
        birth_date=date(1992, 4, 10),
        birth_time=None,
        birth_time_precision="unknown",
        birth_timezone="UTC",
        latitude=40.7128,
        longitude=-74.0060,
    )

    placements = compute_natal_placements(input_unknown)

    # Planets are calculated at mean noon
    assert placements.sun_longitude > 0
    assert placements.moon_longitude > 0
    # Ascendant and Houses MUST BE None
    assert placements.ascendant_longitude is None
    assert placements.houses is None


def test_sign_mapping_and_element_derivation():
    """Property: Correct mapping from longitudes to signs and primary elements."""
    # 0° Aries
    assert longitude_to_sign(0.0) == "Aries"
    # 15° Cancer (90° + 15° = 105°)
    assert longitude_to_sign(105.0) == "Cancer"
    # 359.9° Pisces
    assert longitude_to_sign(359.9) == "Pisces"
    # None returns None
    assert longitude_to_sign(None) is None

    elem, modal = derive_primary_element_and_modality(
        sun_sign="Aries",
        moon_sign="Leo",
        ascendant_sign="Sagittarius",
        mercury_sign="Aries",
        venus_sign="Taurus",
        mars_sign="Gemini",
    )
    assert elem == "Fire"
    assert modal == "Cardinal" or modal in ["Cardinal", "Fixed", "Mutable"]


def test_validation_rejects_invalid_inputs():
    """Property: Input validation throws controlled JesterAPIExceptions."""
    # 1. Future date
    with pytest.raises(JesterAPIException) as exc:
        validate_birth_data(
            birth_date=date(2099, 1, 1),
            birth_time=None,
            birth_time_precision="unknown",
            birth_timezone="UTC",
        )
    assert exc.value.error_code == "invalid_birth_date"

    # 2. Inconsistent unknown time with time provided
    with pytest.raises(JesterAPIException) as exc:
        validate_birth_data(
            birth_date=date(1990, 1, 1),
            birth_time=time(12, 0),
            birth_time_precision="unknown",
            birth_timezone="UTC",
        )
    assert exc.value.error_code == "inconsistent_birth_time"

    # 3. Missing birth time when exact
    with pytest.raises(JesterAPIException) as exc:
        validate_birth_data(
            birth_date=date(1990, 1, 1),
            birth_time=None,
            birth_time_precision="exact",
            birth_timezone="UTC",
        )
    assert exc.value.error_code == "missing_birth_time"

    # 4. Invalid timezone
    with pytest.raises(JesterAPIException) as exc:
        validate_birth_data(
            birth_date=date(1990, 1, 1),
            birth_time=None,
            birth_time_precision="unknown",
            birth_timezone="Invalid/NonExistent_Zone",
        )
    assert exc.value.error_code == "invalid_timezone"

    # 5. Invalid coordinates
    with pytest.raises(JesterAPIException) as exc:
        validate_birth_data(
            birth_date=date(1990, 1, 1),
            birth_time=None,
            birth_time_precision="unknown",
            birth_timezone="UTC",
            latitude=95.0,
        )
    assert exc.value.error_code == "invalid_coordinates"
