"""
Deterministic Real Planetary Transit Calculation Engine for JESTER V1.
Calculates active daily transits from Swiss Ephemeris against a user's natal placements.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
import json
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
import swisseph as swe

from backend.app.astrology.aspects import (
    ASPECT_DEFINITIONS,
    AspectType,
    angular_distance,
    calculate_aspect_strength,
)
from backend.app.astrology.constants import DEFAULT_SWE_FLAGS, PLANETS

# Centralized V1 Transit Orb Limits (degrees)
TRANSIT_ORB_LIMITS: dict[str, float] = {
    "sun": 2.0,
    "mercury": 2.0,
    "venus": 2.0,
    "mars": 1.5,
    "moon": 2.5,
    "jupiter": 1.0,
    "saturn": 1.0,
    "uranus": 0.5,
    "neptune": 0.5,
    "pluto": 0.5,
}

# Georgian localization labels for astronomical context
PLANET_NAMES_KA: dict[str, str] = {
    "sun": "მზე",
    "moon": "მთვარე",
    "mercury": "მერკური",
    "venus": "ვენერა",
    "mars": "მარსი",
    "jupiter": "იუპიტერი",
    "saturn": "სატურნი",
    "uranus": "ურანი",
    "neptune": "ნეპტუნი",
    "pluto": "პლუტონი",
    "ascendant": "ასცენდენტი",
}

ASPECT_NAMES_KA: dict[str, str] = {
    "conjunction": "შეერთება",
    "sextile": "სექსტილი",
    "square": "კვადრატი",
    "trine": "ტრინი",
    "opposition": "ოპოზიცია",
}

# Internal Ranking Weights
NATAL_POINT_WEIGHTS: dict[str, float] = {
    "sun": 3.0,
    "moon": 2.5,
    "ascendant": 2.5,
    "mercury": 2.0,
    "venus": 2.0,
    "mars": 2.0,
    "jupiter": 1.0,
    "saturn": 1.0,
}

TRANSIT_PLANET_WEIGHTS: dict[str, float] = {
    "sun": 3.0,
    "mercury": 3.0,
    "venus": 3.0,
    "mars": 3.0,
    "moon": 2.0,
    "jupiter": 1.5,
    "saturn": 1.5,
    "uranus": 1.0,
    "neptune": 1.0,
    "pluto": 1.0,
}

ASPECT_WEIGHTS: dict[str, float] = {
    "conjunction": 1.00,
    "trine": 0.90,
    "opposition": 0.85,
    "square": 0.80,
    "sextile": 0.70,
}

APPLYING_MULTIPLIER = 1.15
SEPARATING_MULTIPLIER = 1.00


@dataclass(frozen=True)
class ActiveTransitSignal:
    transit_planet: str
    natal_point: str
    aspect_type: str
    actual_distance: float
    target_angle: float
    orb_diff: float
    max_orb: float
    aspect_strength: float
    is_applying: bool
    transit_retrograde: bool
    archetype_id: str
    ranking_score: float
    context_label_ka: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "transit_planet": self.transit_planet,
            "natal_point": self.natal_point,
            "aspect_type": self.aspect_type,
            "actual_distance": self.actual_distance,
            "target_angle": self.target_angle,
            "orb_diff": self.orb_diff,
            "max_orb": self.max_orb,
            "aspect_strength": self.aspect_strength,
            "is_applying": self.is_applying,
            "transit_retrograde": self.transit_retrograde,
            "archetype_id": self.archetype_id,
            "ranking_score": self.ranking_score,
            "context_label_ka": self.context_label_ka,
        }


TAGS_FILE_PATH = Path(__file__).resolve().parent.parent / "interpretation" / "data" / "daily_energy_tags.json"
_DAILY_ENERGY_TAGS_CACHE: dict[str, dict[str, Any]] | None = None


def load_daily_energy_tags() -> dict[str, dict[str, Any]]:
    """
    Loads curated static DO and DON'T tags from data/daily_energy_tags.json.
    Ensures zero LLM generation, zero random selection, pure static content.
    """
    global _DAILY_ENERGY_TAGS_CACHE
    if _DAILY_ENERGY_TAGS_CACHE is None:
        if TAGS_FILE_PATH.exists():
            with open(TAGS_FILE_PATH, "r", encoding="utf-8") as f:
                _DAILY_ENERGY_TAGS_CACHE = json.load(f)
        else:
            _DAILY_ENERGY_TAGS_CACHE = {}
    return _DAILY_ENERGY_TAGS_CACHE


DAILY_ENERGY_GUIDANCE: dict[str, dict[str, Any]] = load_daily_energy_tags()


def get_daily_guidance(archetype_id: str, locale: str = "en") -> dict[str, list[str]]:
    """
    Returns deterministic curated 3 DO and 3 DON'T content tags for any archetype.
    Zero LLM generation, zero random selection, pure static content data.
    """
    data = load_daily_energy_tags()
    arch_data = data.get(archetype_id.lower(), data.get("neutral", {}))

    if locale == "ka":
        do_tags = arch_data.get("do_ka") or arch_data.get("do", [])
        dont_tags = arch_data.get("dont_ka") or arch_data.get("dont", [])
    else:
        do_tags = arch_data.get("do", [])
        dont_tags = arch_data.get("dont", [])

    return {
        "do": list(do_tags),
        "dont": list(dont_tags),
    }


@dataclass
class DailyTransitsResult:
    dominant_transit: ActiveTransitSignal | None
    supporting_transits: list[ActiveTransitSignal]
    active_archetype: str


def map_transit_to_archetype(transit_planet: str, natal_point: str, aspect_type: str) -> str:
    """
    Deterministically maps an active transit pair and aspect type to one of the 12 existing Daily Energy archetypes.
    Distinguishes harmonic (conjunction, trine, sextile) vs friction/hard (square, opposition) aspects.
    """
    tp = transit_planet.lower()
    np = natal_point.lower()
    pair = frozenset([tp, np])
    is_hard = aspect_type in ["square", "opposition"]

    # 1. Sun & Mars pairings (or Mars to Ascendant)
    if pair == frozenset(["sun", "mars"]) or (tp == "mars" and np == "ascendant"):
        if is_hard:
            return "restlessness"
        return "confidence"

    # 2. Mercury & Saturn pairings
    if pair == frozenset(["mercury", "saturn"]):
        return "clarity"

    # 3. Mars & Jupiter / Mars & Mars pairings
    if pair == frozenset(["mars", "jupiter"]) or pair == frozenset(["mars", "mars"]):
        if is_hard:
            return "restlessness"
        return "vitality"

    # 4. Venus & Neptune / Venus & Venus pairings
    if pair == frozenset(["venus", "neptune"]) or pair == frozenset(["venus", "venus"]):
        if is_hard:
            return "restlessness"
        return "creativity"

    # 5. Mercury & Jupiter / Mercury & Neptune (tense vs easy)
    if pair == frozenset(["mercury", "jupiter"]) or pair == frozenset(["mercury", "neptune"]):
        if is_hard:
            return "focus"
        return "curiosity"

    # 6. Mercury personal communication pairings
    if (
        pair == frozenset(["mercury", "mercury"])
        or pair == frozenset(["sun", "mercury"])
        or pair == frozenset(["mars", "mercury"])
    ):
        return "communication"

    # 7. Moon emotional receptivity pairings
    if (
        pair == frozenset(["moon", "moon"])
        or pair == frozenset(["moon", "saturn"])
        or pair == frozenset(["moon", "neptune"])
        or pair == frozenset(["moon", "venus"])
    ):
        return "receptivity"

    # 8. Uranus disruptive restlessness pairings
    if (
        pair == frozenset(["mars", "uranus"])
        or pair == frozenset(["sun", "uranus"])
        or pair == frozenset(["moon", "uranus"])
    ):
        return "restlessness"

    # 9. Venus social / charm pairings
    if (
        pair == frozenset(["sun", "venus"])
        or (tp == "venus" and np in ["ascendant", "jupiter"])
        or (tp in ["sun", "jupiter"] and np == "venus")
    ):
        return "social"

    # 10. Saturn discipline / grounded execution
    if pair == frozenset(["sun", "saturn"]) or pair == frozenset(["mars", "saturn"]):
        return "discipline"

    # 11. Pluto introspection / deep reset
    if (
        pair == frozenset(["sun", "pluto"])
        or pair == frozenset(["moon", "pluto"])
        or pair == frozenset(["mercury", "pluto"])
        or pair == frozenset(["mars", "pluto"])
    ):
        return "introspection"

    # 12. Mercury & Uranus curiosity / spontaneous pivot
    if pair == frozenset(["mercury", "uranus"]):
        if is_hard:
            return "restlessness"
        return "curiosity"

    # Broad fallback mapping based on moving transiting planet and aspect friction
    if is_hard:
        if tp in ["mercury", "jupiter", "neptune"]:
            return "focus"
        return "restlessness"

    fallback_map = {
        "mercury": "communication",
        "venus": "social",
        "mars": "confidence",
        "moon": "receptivity",
        "sun": "confidence",
        "jupiter": "vitality",
        "saturn": "discipline",
        "uranus": "curiosity",
        "neptune": "creativity",
        "pluto": "introspection",
    }
    return fallback_map.get(tp, "confidence")


def calculate_transit_positions(jd: float) -> dict[str, tuple[float, float, bool]]:
    """
    Calculates current positions for all 10 celestial bodies at a specific Julian Day.
    Returns {planet_name: (longitude_deg, speed_lon_deg_per_day, is_retrograde)}.
    """
    positions: dict[str, tuple[float, float, bool]] = {}
    for name, planet_id in PLANETS.items():
        res, _ = swe.calc_ut(jd, planet_id, DEFAULT_SWE_FLAGS)
        lon = res[0] % 360.0
        speed_lon = res[3]
        is_retro = speed_lon < 0.0
        positions[name] = (round(lon, 6), round(speed_lon, 6), is_retro)
    return positions


def check_is_applying(
    jd: float,
    planet_id: int,
    natal_lon: float,
    target_angle: float,
) -> bool:
    """
    Determines whether a transiting planet is applying (moving towards exact aspect)
    by forward-sampling by +0.01 days (~14.4 minutes).
    """
    res1, _ = swe.calc_ut(jd, planet_id, DEFAULT_SWE_FLAGS)
    lon1 = res1[0] % 360.0

    res2, _ = swe.calc_ut(jd + 0.01, planet_id, DEFAULT_SWE_FLAGS)
    lon2 = res2[0] % 360.0

    d1 = angular_distance(lon1, natal_lon)
    d2 = angular_distance(lon2, natal_lon)

    orb1 = abs(d1 - target_angle)
    orb2 = abs(d2 - target_angle)

    return orb2 < orb1


def compute_daily_transits(
    natal_placements: dict[str, float | None],
    target_date: date,
    user_timezone: str = "UTC",
    birth_time_precision: str = "exact",
) -> DailyTransitsResult:
    """
    Calculates deterministic real planetary transits across the user's local calendar day.
    Uses 5-point local sampling (00:00, 06:00, 12:00, 18:00, 23:59) to capture fast movers (Moon, Mercury, Venus),
    deduplicates identical transit pairs to their peak exactness moment, and ranks them.

    Moon Uncertainty Policy:
    When birth_time_precision == 'unknown', natal Moon position has ~13 deg daily positional uncertainty.
    Therefore, aspects to natal Moon CANNOT become the dominant primary transit.
    """
    try:
        tz = ZoneInfo(user_timezone)
    except Exception:
        tz = ZoneInfo("UTC")

    # Local day window boundaries
    dt_start = datetime.combine(target_date, time(0, 0, 0), tzinfo=tz).astimezone(timezone.utc)
    dt_end = datetime.combine(target_date, time(23, 59, 59), tzinfo=tz).astimezone(timezone.utc)

    hour_start_float = dt_start.hour + dt_start.minute / 60.0 + dt_start.second / 3600.0
    jd_start = swe.julday(dt_start.year, dt_start.month, dt_start.day, hour_start_float)

    hour_end_float = dt_end.hour + dt_end.minute / 60.0 + dt_end.second / 3600.0
    jd_end = swe.julday(dt_end.year, dt_end.month, dt_end.day, hour_end_float)

    day_span = max(jd_end - jd_start, 0.999)

    # 1. Base 25-point hourly sampling across the local day window
    sample_jds: list[float] = [jd_start + (i / 24.0) * day_span for i in range(25)]

    # Filter natal points
    allowed_natal_keys = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
    if birth_time_precision in ["exact", "approximate"] and natal_placements.get("ascendant") is not None:
        allowed_natal_keys.append("ascendant")

    # 2. Analytical peak crossing detection (root finding for exact aspect peaks between hourly samples)
    start_positions = calculate_transit_positions(jd_start)
    for t_name, (t_lon0, t_speed0, _) in start_positions.items():
        if abs(t_speed0) < 0.001:
            continue

        for n_name in allowed_natal_keys:
            n_lon = natal_placements.get(n_name)
            if n_lon is None:
                continue

            for asp_type, asp_def in ASPECT_DEFINITIONS.items():
                target_angle = asp_def.target_angle
                target_lons = [(n_lon + target_angle) % 360.0]
                if target_angle not in (0.0, 180.0):
                    target_lons.append((n_lon - target_angle) % 360.0)

                for target_lon in target_lons:
                    if t_speed0 > 0:
                        delta = (target_lon - t_lon0) % 360.0
                    else:
                        delta = -((t_lon0 - target_lon) % 360.0)

                    dt_days = delta / t_speed0
                    if 0.0 <= dt_days <= day_span:
                        jd_exact = jd_start + dt_days
                        sample_jds.append(jd_exact)

    active_by_pair: dict[tuple[str, str, str], ActiveTransitSignal] = {}

    for jd in sample_jds:
        sky_positions = calculate_transit_positions(jd)

        for t_name, (t_lon, t_speed, t_retro) in sky_positions.items():
            max_allowed_orb = TRANSIT_ORB_LIMITS.get(t_name, 1.5)

            for n_name in allowed_natal_keys:
                n_lon = natal_placements.get(n_name)
                if n_lon is None:
                    continue

                dist = angular_distance(t_lon, n_lon)

                for asp_type, asp_def in ASPECT_DEFINITIONS.items():
                    orb_diff = abs(dist - asp_def.target_angle)

                    if orb_diff <= max_allowed_orb:
                        pair_key = (t_name, n_name, asp_type)
                        strength = calculate_aspect_strength(orb_diff, max_allowed_orb)

                        # If we already saw this transit in an earlier sample, keep the tighter peak
                        if pair_key in active_by_pair and active_by_pair[pair_key].orb_diff <= orb_diff:
                            continue

                        planet_id = PLANETS[t_name]
                        is_applying = check_is_applying(jd, planet_id, n_lon, asp_def.target_angle)
                        archetype_id = map_transit_to_archetype(t_name, n_name, asp_type)

                        # Compute internal composite ranking score
                        w_natal = NATAL_POINT_WEIGHTS.get(n_name, 1.0)
                        w_transit = TRANSIT_PLANET_WEIGHTS.get(t_name, 1.0)
                        w_aspect = ASPECT_WEIGHTS.get(asp_type, 0.70)
                        m_app = APPLYING_MULTIPLIER if is_applying else SEPARATING_MULTIPLIER

                        rank_score = round(strength * (w_natal + w_transit) * w_aspect * m_app, 4)

                        t_label = PLANET_NAMES_KA.get(t_name, t_name)
                        n_label = PLANET_NAMES_KA.get(n_name, n_name)
                        asp_label = ASPECT_NAMES_KA.get(asp_type, asp_type)
                        context_label = f"ტრანზიტული {t_label} {asp_label} ნატალურ {n_label}თან"

                        active_by_pair[pair_key] = ActiveTransitSignal(
                            transit_planet=t_name,
                            natal_point=n_name,
                            aspect_type=asp_type,
                            actual_distance=round(dist, 4),
                            target_angle=asp_def.target_angle,
                            orb_diff=round(orb_diff, 4),
                            max_orb=max_allowed_orb,
                            aspect_strength=strength,
                            is_applying=is_applying,
                            transit_retrograde=t_retro,
                            archetype_id=archetype_id,
                            ranking_score=rank_score,
                            context_label_ka=context_label,
                        )

    sorted_signals = sorted(
        active_by_pair.values(),
        key=lambda s: (s.ranking_score, -s.orb_diff),
        reverse=True,
    )

    # Moon Uncertainty Policy:
    # If birth_time_precision == 'unknown', natal Moon position is estimated at noon (+/- 6.5 deg).
    # Thus, transits to natal Moon cannot be elevated to the dominant primary signal.
    eligible_dominant_signals = [
        s for s in sorted_signals
        if not (birth_time_precision == "unknown" and s.natal_point == "moon")
    ]

    if not eligible_dominant_signals:
        # Fallback for days with zero reliable aspects within tight orbs:
        # Honest neutral state without fake astrological signals
        return DailyTransitsResult(
            dominant_transit=None,
            supporting_transits=sorted_signals[:2],
            active_archetype="neutral",
        )

    dominant = eligible_dominant_signals[0]
    supporting = [s for s in sorted_signals if s != dominant][:2]

    return DailyTransitsResult(
        dominant_transit=dominant,
        supporting_transits=supporting,
        active_archetype=dominant.archetype_id,
    )
