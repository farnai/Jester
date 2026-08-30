"""
Deterministic Swiss Ephemeris calculation engine.
"""
from collections import Counter
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo
import swisseph as swe

from backend.app.astrology.constants import (
    ASTROLOGY_ENGINE_VERSION,
    DEFAULT_SWE_FLAGS,
    ELEMENT_MAP,
    MODALITY_MAP,
    PLANETS,
    ZODIAC_SIGNS,
)
from backend.app.astrology.models import BirthDataInput, NatalChartPlacements
from backend.app.core.errors import JesterAPIException


def longitude_to_sign(lon: float | None) -> str | None:
    """
    Maps an ecliptic longitude in degrees [0, 360) to a tropical Zodiac sign.
    Ensures strict boundary checking where [0, 30) is Aries, [30, 60) is Taurus, etc.
    """
    if lon is None:
        return None
    normalized = lon % 360.0
    index = int(normalized / 30.0)
    # Guard for exact 360.0 edge case
    if index >= 12:
        index = 11
    return ZODIAC_SIGNS[index]


def compute_julian_day(
    birth_date: date,
    birth_time: time | None,
    birth_timezone: str,
) -> float:
    """
    Converts local birth date/time to UTC and computes the Swiss Ephemeris Julian Day.
    When birth_time is None (unknown time), uses 12:00 UTC (mean noon).
    """
    if birth_time is not None:
        tz = ZoneInfo(birth_timezone)
        dt_local = datetime.combine(birth_date, birth_time, tzinfo=tz)
        dt_utc = dt_local.astimezone(timezone.utc)
        hour_utc = (
            dt_utc.hour
            + dt_utc.minute / 60.0
            + dt_utc.second / 3600.0
            + dt_utc.microsecond / 3600000000.0
        )
        return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_utc)
    else:
        # Unknown time -> 12:00 UTC mean noon
        return swe.julday(birth_date.year, birth_date.month, birth_date.day, 12.0)


def compute_natal_placements(
    birth_data: BirthDataInput,
    data_version: int = 1,
) -> NatalChartPlacements:
    """
    Calculates planetary longitudes, retrogrades, and houses using Swiss Ephemeris.
    If birth time is unknown, Ascendant and houses are strictly None.
    High-latitude Placidus calculations that fail in polar regions fail gracefully.
    """
    jd = compute_julian_day(
        birth_date=birth_data.birth_date,
        birth_time=birth_data.birth_time,
        birth_timezone=birth_data.birth_timezone,
    )

    planet_positions: dict[str, float] = {}
    retrogrades: dict[str, bool] = {}

    # Calculate 10 planetary bodies
    for planet_name, planet_id in PLANETS.items():
        try:
            res, _ = swe.calc_ut(jd, planet_id, DEFAULT_SWE_FLAGS)
            lon = res[0] % 360.0
            speed_lon = res[3]
            planet_positions[f"{planet_name}_longitude"] = round(lon, 6)
            retrogrades[planet_name] = speed_lon < 0.0
        except swe.Error as e:
            raise JesterAPIException(
                status_code=500,
                error_code="ephemeris_calculation_failed",
                message=f"Swiss Ephemeris calculation failed for {planet_name}: {str(e)}",
            )

    # Calculate Houses and Ascendant if precision allows and coordinates exist
    ascendant_longitude: float | None = None
    houses_list: list[float] | None = None

    if (
        birth_data.birth_time_precision in ["exact", "approximate"]
        and birth_data.latitude is not None
        and birth_data.longitude is not None
    ):
        try:
            houses_tuple, ascmc_tuple = swe.houses(
                jd,
                birth_data.latitude,
                birth_data.longitude,
                b"P",  # Placidus system
            )
            houses_list = [round(h % 360.0, 6) for h in houses_tuple]
            ascendant_longitude = round(ascmc_tuple[0] % 360.0, 6)
        except swe.Error:
            # Placidus is mathematically undefined in polar regions (lat > 66.5°)
            raise JesterAPIException(
                status_code=400,
                error_code="placidus_polar_error",
                message="Placidus house calculation is not supported for polar regions above 66.5° latitude.",
            )

    return NatalChartPlacements(
        sun_longitude=planet_positions["sun_longitude"],
        moon_longitude=planet_positions["moon_longitude"],
        mercury_longitude=planet_positions["mercury_longitude"],
        venus_longitude=planet_positions["venus_longitude"],
        mars_longitude=planet_positions["mars_longitude"],
        jupiter_longitude=planet_positions["jupiter_longitude"],
        saturn_longitude=planet_positions["saturn_longitude"],
        uranus_longitude=planet_positions["uranus_longitude"],
        neptune_longitude=planet_positions["neptune_longitude"],
        pluto_longitude=planet_positions["pluto_longitude"],
        ascendant_longitude=ascendant_longitude,
        houses=houses_list,
        retrogrades=retrogrades,
        source_birth_data_version=data_version,
        engine_version=ASTROLOGY_ENGINE_VERSION,
    )


def derive_primary_element_and_modality(
    sun_sign: str,
    moon_sign: str,
    ascendant_sign: str | None,
    mercury_sign: str,
    venus_sign: str,
    mars_sign: str,
) -> tuple[str, str]:
    """
    Deterministically computes the dominant element and modality from personal placements.
    Weights: Sun (3), Moon (3), Ascendant (3 if present), Mercury (2), Venus (2), Mars (2).
    """
    weights = [
        (sun_sign, 3),
        (moon_sign, 3),
        (mercury_sign, 2),
        (venus_sign, 2),
        (mars_sign, 2),
    ]
    if ascendant_sign:
        weights.append((ascendant_sign, 3))

    element_counts: Counter[str] = Counter()
    modality_counts: Counter[str] = Counter()

    for sign, weight in weights:
        elem = ELEMENT_MAP[sign]
        modal = MODALITY_MAP[sign]
        element_counts[elem] += weight
        modality_counts[modal] += weight

    primary_element = element_counts.most_common(1)[0][0]
    primary_modality = modality_counts.most_common(1)[0][0]

    return primary_element, primary_modality
