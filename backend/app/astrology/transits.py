"""
Deterministic Real Planetary Transit Calculation Engine for JESTER V1.
Calculates active daily transits from Swiss Ephemeris against a user's natal placements.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone, timedelta
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

DAY_NAMES_KA: dict[str, str] = {
    "Monday": "ორშაბათი",
    "Tuesday": "სამშაბათი",
    "Wednesday": "ოთხშაბათი",
    "Thursday": "ხუთშაბათი",
    "Friday": "პარასკევი",
    "Saturday": "შაბათი",
    "Sunday": "კვირა",
}

MONTH_NAMES_KA: dict[int, str] = {
    1: "იანვარი",
    2: "თებერვალი",
    3: "მარტი",
    4: "აპრილი",
    5: "მაისი",
    6: "ივნისი",
    7: "ივლისი",
    8: "აგვისტო",
    9: "სექტემბერი",
    10: "ოქტომბერი",
    11: "ნოემბერი",
    12: "დეკემბერი",
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

# Genitive case for planetary subjects (ნათესაობითი ბრუნვა: მზის, მთვარის, მერკურის...)
PLANET_GENITIVE_KA: dict[str, str] = {
    "sun": "მზის",
    "moon": "მთვარის",
    "mercury": "მერკურის",
    "venus": "ვენერას",
    "mars": "მარსის",
    "jupiter": "იუპიტერის",
    "saturn": "სატურნის",
    "uranus": "ურანის",
    "neptune": "ნეპტუნის",
    "pluto": "პლუტონის",
    "ascendant": "ასცენდენტის",
}

# Postposition "-თან" for target natal points (თანდებულიანი ფორმა: მზესთან, მთვარესთან, მერკურთან...)
PLANET_WITH_POSTPOSITION_KA: dict[str, str] = {
    "sun": "მზესთან",
    "moon": "მთვარესთან",
    "mercury": "მერკურთან",
    "venus": "ვენერასთან",
    "mars": "მარსთან",
    "jupiter": "იუპიტერთან",
    "saturn": "სატურნთან",
    "uranus": "ურანთან",
    "neptune": "ნეპტუნთან",
    "pluto": "პლუტონთან",
    "ascendant": "ასცენდენტთან",
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
                        n_post = PLANET_WITH_POSTPOSITION_KA.get(n_name, f"{n_name}-თან")
                        asp_label = ASPECT_NAMES_KA.get(asp_type, asp_type)
                        context_label = f"ტრანზიტული {t_label} {asp_label} ნატალურ {n_post}"

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


def format_georgian_week_period(start_d: date, end_d: date) -> str:
    """
    Formats a 7-day ISO calendar week into natural Georgian period typography.
    e.g. '2–8 ნოემბერი, 2026', '28 ოქტომბერი – 3 ნოემბერი, 2026', or '29 დეკემბერი, 2025 – 4 იანვარი, 2026'.
    """
    if start_d.year == end_d.year:
        if start_d.month == end_d.month:
            month_name = MONTH_NAMES_KA.get(start_d.month, "")
            return f"{start_d.day}–{end_d.day} {month_name}, {start_d.year}"
        m_start = MONTH_NAMES_KA.get(start_d.month, "")
        m_end = MONTH_NAMES_KA.get(end_d.month, "")
        return f"{start_d.day} {m_start} – {end_d.day} {m_end}, {start_d.year}"
    m_start = MONTH_NAMES_KA.get(start_d.month, "")
    m_end = MONTH_NAMES_KA.get(end_d.month, "")
    return f"{start_d.day} {m_start}, {start_d.year} – {end_d.day} {m_end}, {end_d.year}"


def swe_jd_to_datetime_utc(jd: float) -> datetime:
    """
    Converts a Swiss Ephemeris Julian Day number into a UTC datetime.
    """
    y, m, d, h_float = swe.revjul(jd)
    total_seconds = int(round(h_float * 3600))
    hour = min(23, total_seconds // 3600)
    minute = (total_seconds % 3600) // 60
    second = min(59, total_seconds % 60)
    return datetime(y, m, d, hour, minute, second, tzinfo=timezone.utc)


@dataclass(frozen=True)
class SignificantPeriod:
    peak_date_iso: str
    day_name_ka: str
    transit_label_ka: str
    aspect_type: str
    orb_diff: float
    aspect_strength: float
    significance_description_ka: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "peak_date_iso": self.peak_date_iso,
            "day_name_ka": self.day_name_ka,
            "transit_label_ka": self.transit_label_ka,
            "aspect_type": self.aspect_type,
            "orb_diff": round(self.orb_diff, 2),
            "aspect_strength": round(self.aspect_strength, 2),
            "significance_description_ka": self.significance_description_ka,
        }


@dataclass(frozen=True)
class ActiveWeeklyTransitSignal:
    transit_planet: str
    natal_point: str
    aspect_type: str
    min_orb_diff: float
    max_orb: float
    aspect_strength: float
    peak_jd: float
    peak_datetime_iso: str
    peak_day_ka: str
    duration_days: float
    duration_factor: float
    is_applying_start: bool
    transit_retrograde: bool
    archetype_id: str
    ranking_score: float
    context_label_ka: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "transit_planet": self.transit_planet,
            "natal_point": self.natal_point,
            "aspect_type": self.aspect_type,
            "min_orb_diff": round(self.min_orb_diff, 4),
            "max_orb": self.max_orb,
            "aspect_strength": round(self.aspect_strength, 4),
            "peak_datetime_iso": self.peak_datetime_iso,
            "peak_day_ka": self.peak_day_ka,
            "duration_days": round(self.duration_days, 1),
            "duration_factor": round(self.duration_factor, 2),
            "transit_retrograde": self.transit_retrograde,
            "archetype_id": self.archetype_id,
            "ranking_score": round(self.ranking_score, 4),
            "context_label_ka": self.context_label_ka,
        }


@dataclass
class WeeklyTransitsResult:
    iso_year: int
    iso_week: int
    start_date: date
    end_date: date
    period_ka: str
    dominant_transit: ActiveWeeklyTransitSignal | None
    supporting_transits: list[ActiveWeeklyTransitSignal]
    significant_periods: list[SignificantPeriod]
    active_archetype: str


def compute_weekly_transits(
    natal_placements: dict[str, float | None],
    target_date: date,
    user_timezone: str = "UTC",
    birth_time_precision: str = "exact",
) -> WeeklyTransitsResult:
    """
    Calculates deterministic real planetary transits across an entire ISO calendar week (Monday 00:00 to Sunday 23:59:59)
    in the user's local timezone.

    Respects varying planetary speeds:
    - Moon moves ~13.2 deg/day -> aspect lasts ~8-10 hours.
    - Sun, Mercury, Venus move ~1.0-1.5 deg/day -> aspect lasts 2-4 days.
    - Mars moves ~0.5 deg/day -> aspect lasts 4-6 days.
    - Outer/Social planets move <0.1 deg/day -> aspect persists all week.

    Applies duration weighting, analytical exact peak finding, and prevents Moon from dominating the 7-day
    cycle when longer-lived personal/social transits are active, while preserving Moon peaks for significant periods.
    """
    try:
        tz = ZoneInfo(user_timezone)
    except Exception:
        tz = ZoneInfo("UTC")

    iso_year, iso_week, iso_weekday = target_date.isocalendar()
    start_d = target_date - timedelta(days=iso_weekday - 1)
    end_d = start_d + timedelta(days=6)
    period_ka = format_georgian_week_period(start_d, end_d)

    dt_start = datetime.combine(start_d, time(0, 0, 0), tzinfo=tz).astimezone(timezone.utc)
    dt_end = datetime.combine(end_d, time(23, 59, 59), tzinfo=tz).astimezone(timezone.utc)

    hour_start_float = dt_start.hour + dt_start.minute / 60.0 + dt_start.second / 3600.0
    jd_start = swe.julday(dt_start.year, dt_start.month, dt_start.day, hour_start_float)

    hour_end_float = dt_end.hour + dt_end.minute / 60.0 + dt_end.second / 3600.0
    jd_end = swe.julday(dt_end.year, dt_end.month, dt_end.day, hour_end_float)
    total_days = max(jd_end - jd_start, 6.999)

    if birth_time_precision == "unknown":
        allowed_natal_keys = [k for k in natal_placements.keys() if k not in ("ascendant", "mc") and natal_placements.get(k) is not None]
    else:
        allowed_natal_keys = [k for k in natal_placements.keys() if natal_placements.get(k) is not None]

    # Sample points across the 7 days (every 6 hours)
    step_days = 0.25
    sample_jds: list[float] = [jd_start + i * step_days for i in range(int(total_days / step_days) + 1)]
    if jd_end not in sample_jds:
        sample_jds.append(jd_end)

    # Analytical exact crossing calculation from start velocities
    start_positions = calculate_transit_positions(jd_start)
    for t_name, (t_lon0, t_speed0, _) in start_positions.items():
        if abs(t_speed0) < 0.0001:
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
                    if 0.0 <= dt_days <= total_days:
                        sample_jds.append(jd_start + dt_days)

    unique_jds = sorted(set(round(j, 5) for j in sample_jds))

    # Track best peak per (transit_planet, natal_point, aspect_type)
    pair_tracking: dict[tuple[str, str, str], dict[str, Any]] = {}

    for jd in unique_jds:
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
                        if pair_key not in pair_tracking or orb_diff < pair_tracking[pair_key]["min_orb"]:
                            pair_tracking[pair_key] = {
                                "t_name": t_name,
                                "n_name": n_name,
                                "asp_type": asp_type,
                                "min_orb": orb_diff,
                                "max_orb": max_allowed_orb,
                                "peak_jd": jd,
                                "peak_speed": t_speed,
                                "t_retro": t_retro,
                            }

    all_weekly_signals: list[ActiveWeeklyTransitSignal] = []

    for pair_key, info in pair_tracking.items():
        t_name = info["t_name"]
        n_name = info["n_name"]
        asp_type = info["asp_type"]
        min_orb = info["min_orb"]
        max_allowed_orb = info["max_orb"]
        peak_jd = info["peak_jd"]
        peak_speed = info["peak_speed"]
        t_retro = info["t_retro"]

        strength = calculate_aspect_strength(min_orb, max_allowed_orb)
        archetype_id = map_transit_to_archetype(t_name, n_name, asp_type)

        # Duration factor based on planetary velocity
        abs_speed = max(abs(peak_speed), 0.0001)
        est_duration_days = min(7.0, (2.0 * max_allowed_orb) / abs_speed)

        if t_name == "moon":
            # Moon transit is brief (~8-10 hours). Weight reduced so it does not overshadow weekly multi-day transits
            duration_factor = 0.35
        elif t_name in ("mercury", "venus", "sun"):
            duration_factor = 0.80
        elif t_name == "mars":
            duration_factor = 0.90
        else:
            duration_factor = 1.00

        # Peak bonus if aspect reaches closest alignment between Monday and Sunday
        if jd_start <= peak_jd <= jd_end and min_orb <= 0.60 * max_allowed_orb:
            peak_bonus = 1.25
        else:
            peak_bonus = 1.00

        w_natal = NATAL_POINT_WEIGHTS.get(n_name, 1.0)
        w_transit = TRANSIT_PLANET_WEIGHTS.get(t_name, 1.0)
        w_aspect = ASPECT_WEIGHTS.get(asp_type, 0.70)
        rank_score = round(strength * (w_natal + w_transit) * w_aspect * duration_factor * peak_bonus, 4)

        t_label = PLANET_NAMES_KA.get(t_name, t_name)
        n_post = PLANET_WITH_POSTPOSITION_KA.get(n_name, f"{n_name}-თან")
        asp_label = ASPECT_NAMES_KA.get(asp_type, asp_type)
        context_label = f"ტრანზიტული {t_label} {asp_label} ნატალურ {n_post}"

        peak_dt_utc = swe_jd_to_datetime_utc(peak_jd)
        peak_dt_local = peak_dt_utc.astimezone(tz)
        peak_day_name = DAY_NAMES_KA.get(peak_dt_local.strftime("%A"), "")
        month_name = MONTH_NAMES_KA.get(peak_dt_local.month, "")
        peak_day_ka = f"{peak_day_name}, {peak_dt_local.day} {month_name}"

        planet_id = PLANETS[t_name]
        is_applying_start = check_is_applying(jd_start, planet_id, natal_placements[n_name], ASPECT_DEFINITIONS[asp_type].target_angle)

        all_weekly_signals.append(
            ActiveWeeklyTransitSignal(
                transit_planet=t_name,
                natal_point=n_name,
                aspect_type=asp_type,
                min_orb_diff=round(min_orb, 4),
                max_orb=max_allowed_orb,
                aspect_strength=round(strength, 4),
                peak_jd=peak_jd,
                peak_datetime_iso=peak_dt_local.isoformat(),
                peak_day_ka=peak_day_ka,
                duration_days=round(est_duration_days, 1),
                duration_factor=round(duration_factor, 2),
                is_applying_start=is_applying_start,
                transit_retrograde=t_retro,
                archetype_id=archetype_id,
                ranking_score=rank_score,
                context_label_ka=context_label,
            )
        )

    sorted_signals = sorted(
        all_weekly_signals,
        key=lambda s: (s.ranking_score, -s.min_orb_diff),
        reverse=True,
    )

    # Moon Uncertainty Policy:
    # If birth_time_precision == 'unknown', natal Moon position cannot define the dominant theme
    eligible_dominant_signals = [
        s for s in sorted_signals
        if not (birth_time_precision == "unknown" and s.natal_point == "moon")
    ]

    # Non-Moon dominance policy:
    # Prioritize multi-day transits over Moon transit for the overarching 7-day theme,
    # unless Moon is the only active transit
    non_moon_eligible = [s for s in eligible_dominant_signals if s.transit_planet != "moon"]
    if non_moon_eligible:
        dominant = non_moon_eligible[0]
    elif eligible_dominant_signals:
        dominant = eligible_dominant_signals[0]
    else:
        dominant = None

    supporting = [s for s in sorted_signals if s != dominant][:2] if dominant else sorted_signals[:2]
    active_archetype = dominant.archetype_id if dominant else "neutral"

    # Detect Significant Periods (peak days across the week)
    significant_periods: list[SignificantPeriod] = []
    # Pick top peak moments that culminate inside the 7 days with tight orbs
    candidate_peaks = [
        s for s in sorted_signals
        if s.min_orb_diff <= 0.75 * s.max_orb and jd_start <= s.peak_jd <= jd_end
    ]

    # Deduplicate significant periods by day to provide varied highlights across the week
    seen_days: set[str] = set()
    for s in candidate_peaks:
        day_key = s.peak_day_ka
        if day_key in seen_days:
            continue
        seen_days.add(day_key)

        t_gen = PLANET_GENITIVE_KA.get(s.transit_planet, s.transit_planet)
        n_post = PLANET_WITH_POSTPOSITION_KA.get(s.natal_point, s.natal_point)
        asp_lbl = ASPECT_NAMES_KA.get(s.aspect_type, s.aspect_type)

        desc = f"{t_gen} {asp_lbl} {n_post} აღწევს მაქსიმალურ სიზუსტეს — კვირის ერთ-ერთი ენერგეტიკულად გამორჩეული მომენტი."

        significant_periods.append(
            SignificantPeriod(
                peak_date_iso=s.peak_datetime_iso[:10],
                day_name_ka=s.peak_day_ka,
                transit_label_ka=s.context_label_ka,
                aspect_type=s.aspect_type,
                orb_diff=s.min_orb_diff,
                aspect_strength=s.aspect_strength,
                significance_description_ka=desc,
            )
        )
        if len(significant_periods) >= 3:
            break

    return WeeklyTransitsResult(
        iso_year=iso_year,
        iso_week=iso_week,
        start_date=start_d,
        end_date=end_d,
        period_ka=period_ka,
        dominant_transit=dominant,
        supporting_transits=supporting,
        significant_periods=significant_periods,
        active_archetype=active_archetype,
    )
