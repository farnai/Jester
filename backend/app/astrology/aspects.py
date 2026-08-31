"""
Deterministic astronomical aspect calculation module for Jester.
Provides angular distance math, 360-degree circle wraparound, orb evaluations,
and quadratic aspect strength decay.
"""
from dataclasses import dataclass
from typing import Literal

AspectType = Literal["conjunction", "sextile", "square", "trine", "opposition"]


@dataclass(frozen=True)
class AspectDefinition:
    type_name: AspectType
    target_angle: float
    base_max_orb: float
    base_weight: float


ASPECT_DEFINITIONS: dict[AspectType, AspectDefinition] = {
    "conjunction": AspectDefinition(
        type_name="conjunction",
        target_angle=0.0,
        base_max_orb=8.0,
        base_weight=1.00,
    ),
    "sextile": AspectDefinition(
        type_name="sextile",
        target_angle=60.0,
        base_max_orb=6.0,
        base_weight=0.70,
    ),
    "square": AspectDefinition(
        type_name="square",
        target_angle=90.0,
        base_max_orb=7.0,
        base_weight=0.75,
    ),
    "trine": AspectDefinition(
        type_name="trine",
        target_angle=120.0,
        base_max_orb=8.0,
        base_weight=0.90,
    ),
    "opposition": AspectDefinition(
        type_name="opposition",
        target_angle=180.0,
        base_max_orb=8.0,
        base_weight=0.85,
    ),
}

LUMINARIES = {"sun", "moon"}


def normalize_angle(deg: float) -> float:
    """Normalizes ecliptic longitude in degrees to range [0.0, 360.0)."""
    return deg % 360.0


def angular_distance(lon1: float, lon2: float) -> float:
    """
    Computes the shortest circular arc distance between two ecliptic longitudes in degrees [0, 180].
    Handles 0/360 degree wraparound seamlessly.
    """
    l1 = normalize_angle(lon1)
    l2 = normalize_angle(lon2)
    diff = abs(l1 - l2)
    return min(diff, 360.0 - diff)


def get_max_orb(aspect_type: AspectType, body_a: str, body_b: str) -> float:
    """
    Determines maximum orb allowance for a given aspect type and body pair.
    - Sun/Moon (Luminaries) receive a +2.0° orb expansion.
    - Ascendant aspects are capped at a max orb of 6.0°.
    """
    asp_def = ASPECT_DEFINITIONS[aspect_type]
    b_a = body_a.lower()
    b_b = body_b.lower()

    if b_a == "ascendant" or b_b == "ascendant":
        return min(asp_def.base_max_orb, 6.0)

    max_orb = asp_def.base_max_orb
    if b_a in LUMINARIES or b_b in LUMINARIES:
        max_orb += 2.0

    return max_orb


def calculate_aspect_strength(orb_diff: float, max_orb: float) -> float:
    """
    Calculates normalized aspect strength S_aspect in [0.0, 1.0] using quadratic decay:
    S_aspect = (1.0 - orb_diff / max_orb)^2
    Exact aspect (orb_diff=0) -> 1.0
    Half-orb -> 0.25
    At/beyond max_orb -> 0.0
    """
    if orb_diff >= max_orb or max_orb <= 0.0:
        return 0.0
    decay_ratio = 1.0 - (orb_diff / max_orb)
    return round(decay_ratio * decay_ratio, 4)


@dataclass
class DetectedAspect:
    body_a: str
    body_b: str
    aspect_type: AspectType
    target_angle: float
    actual_distance: float
    orb_diff: float
    max_orb: float
    strength: float
    base_weight: float


def detect_aspect(
    body_a: str,
    lon_a: float,
    body_b: str,
    lon_b: float,
) -> DetectedAspect | None:
    """
    Evaluates two longitudes and returns the closest active aspect within allowable orb.
    Returns None if no aspect falls within max orb.
    """
    dist = angular_distance(lon_a, lon_b)
    best_aspect: DetectedAspect | None = None
    min_orb_diff = float("inf")

    for asp_type, asp_def in ASPECT_DEFINITIONS.items():
        orb_diff = abs(dist - asp_def.target_angle)
        max_orb = get_max_orb(asp_type, body_a, body_b)

        if orb_diff <= max_orb and orb_diff < min_orb_diff:
            min_orb_diff = orb_diff
            strength = calculate_aspect_strength(orb_diff, max_orb)
            best_aspect = DetectedAspect(
                body_a=body_a,
                body_b=body_b,
                aspect_type=asp_type,
                target_angle=asp_def.target_angle,
                actual_distance=round(dist, 4),
                orb_diff=round(orb_diff, 4),
                max_orb=max_orb,
                strength=strength,
                base_weight=asp_def.base_weight,
            )

    return best_aspect
