"""
Deterministic Synastry V1 Calculation Engine for Jester.
Implements the frozen specification in docs/SYNASTRY_V1_SPEC.md.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from typing import Any, Literal
import uuid

from backend.app.astrology.aspects import (
    ASPECT_DEFINITIONS,
    LUMINARIES,
    angular_distance,
    calculate_aspect_strength,
    detect_aspect,
    get_max_orb,
)
from backend.app.astrology.calculator import longitude_to_sign
from backend.app.astrology.constants import ELEMENT_MAP, MODALITY_MAP
from backend.app.compatibility.rules import (
    extract_best_topics,
    extract_conversation_starters,
    extract_signals_from_aspects,
)


PLANET_PAIR_WEIGHTS: dict[frozenset[str], float] = {
    # Tier 1: Luminaries & Core Romance (3.0)
    frozenset(["sun", "sun"]): 3.0,
    frozenset(["sun", "moon"]): 3.0,
    frozenset(["moon", "moon"]): 3.0,
    frozenset(["sun", "venus"]): 3.0,
    frozenset(["moon", "venus"]): 3.0,
    frozenset(["venus", "mars"]): 3.0,

    # Tier 2: Personal Communication & Drive (2.0)
    frozenset(["mercury", "mercury"]): 2.0,
    frozenset(["sun", "mercury"]): 2.0,
    frozenset(["moon", "mercury"]): 2.0,
    frozenset(["venus", "venus"]): 2.0,
    frozenset(["mars", "mars"]): 2.0,
    frozenset(["sun", "mars"]): 2.0,
    frozenset(["moon", "mars"]): 2.0,
    frozenset(["mercury", "venus"]): 2.0,

    # Tier 3: Social & Structural Growth (1.0)
    frozenset(["sun", "jupiter"]): 1.0,
    frozenset(["moon", "jupiter"]): 1.0,
    frozenset(["venus", "jupiter"]): 1.0,
    frozenset(["sun", "saturn"]): 1.0,
    frozenset(["moon", "saturn"]): 1.0,
    frozenset(["venus", "saturn"]): 1.0,
    frozenset(["mars", "jupiter"]): 1.0,
    frozenset(["mars", "saturn"]): 1.0,

    # Tier 5: Ascendant Pairings (2.0)
    frozenset(["sun", "ascendant"]): 2.0,
    frozenset(["moon", "ascendant"]): 2.0,
    frozenset(["venus", "ascendant"]): 2.0,
    frozenset(["mars", "ascendant"]): 2.0,
}

OUTER_PLANETS = {"uranus", "neptune", "pluto"}

ELEMENT_COMPATIBILITY_SCORES: dict[frozenset[str], float] = {
    frozenset(["fire", "fire"]): 80.0,
    frozenset(["fire", "air"]): 70.0,
    frozenset(["fire", "earth"]): 45.0,
    frozenset(["fire", "water"]): 35.0,
    frozenset(["earth", "earth"]): 80.0,
    frozenset(["earth", "water"]): 70.0,
    frozenset(["earth", "air"]): 35.0,
    frozenset(["air", "air"]): 80.0,
    frozenset(["air", "water"]): 45.0,
    frozenset(["water", "water"]): 80.0,
}


@dataclass(frozen=True)
class NatalInputPayload:
    user_id: uuid.UUID
    birth_data_version: int
    birth_time_precision: Literal["exact", "approximate", "unknown"]
    planet_longitudes: dict[str, float]
    ascendant_longitude: float | None = None
    retrogrades: dict[str, bool] = field(default_factory=dict)


@dataclass
class EvidenceItem:
    planet_a: str
    planet_b: str
    lon_a: float
    lon_b: float
    aspect: str
    target_angle: float
    distance: float
    orb_diff: float
    max_orb: float
    strength: float
    weight: float
    subscore_contributions: dict[str, float]


@dataclass
class SynastryResult:
    score: float
    dimensions: dict[str, float]
    signals: list[dict[str, Any]]
    best_topics: list[str]
    conversation_starters: list[str]
    data_quality: dict[str, Any]
    evidence_trace: list[dict[str, Any]]
    engine_version: str = "synastry-v1.0.0"
    calculated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def get_planet_pair_weight(p1: str, p2: str, is_approximate: bool = False) -> float:
    """Returns the pair weight W_pair following Section 9 of the spec."""
    key = frozenset([p1.lower(), p2.lower()])
    if key in PLANET_PAIR_WEIGHTS:
        w = PLANET_PAIR_WEIGHTS[key]
        if "ascendant" in key and is_approximate:
            return w * 0.50
        return w

    if p1.lower() in OUTER_PLANETS or p2.lower() in OUTER_PLANETS:
        return 0.5

    if "ascendant" in key:
        return 1.0 if not is_approximate else 0.5

    return 1.0


def calculate_elemental_harmony(elements_a: list[str], elements_b: list[str]) -> float:
    """Computes elemental compatibility score [0, 100]."""
    if not elements_a or not elements_b:
        return 50.0

    scores = []
    for ea in elements_a:
        for eb in elements_b:
            pair = frozenset([ea.lower(), eb.lower()])
            score = ELEMENT_COMPATIBILITY_SCORES.get(pair, 50.0)
            scores.append(score)

    return sum(scores) / len(scores) if scores else 50.0


class SynastryEngine:
    """
    100% deterministic, symmetric Synastry V1 calculation engine.
    """

    def calculate(self, person_a: NatalInputPayload, person_b: NatalInputPayload) -> SynastryResult:
        is_approx = person_a.birth_time_precision == "approximate" or person_b.birth_time_precision == "approximate"
        is_unknown = person_a.birth_time_precision == "unknown" or person_b.birth_time_precision == "unknown"

        # Determine bodies and longitudes
        bodies_a: dict[str, float] = {k.lower(): v for k, v in person_a.planet_longitudes.items()}
        if not is_unknown and person_a.ascendant_longitude is not None:
            bodies_a["ascendant"] = person_a.ascendant_longitude

        bodies_b: dict[str, float] = {k.lower(): v for k, v in person_b.planet_longitudes.items()}
        if not is_unknown and person_b.ascendant_longitude is not None:
            bodies_b["ascendant"] = person_b.ascendant_longitude

        # Generate all cross-aspects in canonical key order to guarantee identical floating-point summation order
        all_aspects: list[dict[str, Any]] = []

        for body_a_name in sorted(bodies_a.keys()):
            lon_a = bodies_a[body_a_name]
            for body_b_name in sorted(bodies_b.keys()):
                lon_b = bodies_b[body_b_name]

                detected = detect_aspect(body_a_name, lon_a, body_b_name, lon_b)
                if not detected:
                    continue

                strength = detected.strength
                if strength <= 0.0:
                    continue

                pair_weight = get_planet_pair_weight(body_a_name, body_b_name, is_approximate=is_approx)
                aspect_base_weight = detected.base_weight
                effect = pair_weight * aspect_base_weight * strength

                asp = detected.aspect_type
                b_set = {body_a_name, body_b_name}

                # Multi-dimensional contribution calculations (Section 11)
                sub_h = 0.0
                sub_c = 0.0
                sub_a = 0.0
                sub_g = 0.0

                # 1. Trines & Sextiles
                if asp in ("trine", "sextile"):
                    sub_h += effect
                    sub_c += effect

                # 2. Venus-Mars / Sun-Moon / Venus-Pluto
                if b_set in ({"venus", "mars"}, {"sun", "moon"}, {"venus", "pluto"}):
                    sub_a += effect

                # 3. Squares (90°)
                if asp == "square":
                    sub_g += effect
                    sub_a += effect * 0.6
                    sub_h -= effect * 0.4

                # 4. Oppositions (180°)
                if asp == "opposition":
                    sub_a += effect * 0.9
                    sub_g += effect * 0.9
                    sub_h -= effect * 0.3

                # 5. Saturn Aspects
                if "saturn" in b_set:
                    sub_g += effect
                    sub_h += effect

                # 6. Conjunctions
                if asp == "conjunction":
                    if "saturn" not in b_set:
                        sub_h += effect
                    if "mercury" in b_set:
                        sub_c += effect
                    if "venus" in b_set or "mars" in b_set:
                        sub_a += effect * 0.5

                # Influence Caps (Section 15): +-18.0 max per pair
                sub_h = max(-18.0, min(18.0, sub_h))
                sub_c = max(-18.0, min(18.0, sub_c))
                sub_a = max(-18.0, min(18.0, sub_a))
                sub_g = max(-18.0, min(18.0, sub_g))

                all_aspects.append({
                    "planet_a": body_a_name,
                    "planet_b": body_b_name,
                    "canon_pair": tuple(sorted([body_a_name, body_b_name])),
                    "lon_a": lon_a,
                    "lon_b": lon_b,
                    "aspect": asp,
                    "target_angle": detected.target_angle,
                    "actual_distance": detected.actual_distance,
                    "orb_diff": detected.orb_diff,
                    "max_orb": detected.max_orb,
                    "strength": strength,
                    "pair_weight": pair_weight,
                    "effect": effect,
                    "sub_h": sub_h,
                    "sub_c": sub_c,
                    "sub_a": sub_a,
                    "sub_g": sub_g,
                })

        # Sort all aspects by canonical pair and aspect for symmetric deterministic processing
        all_aspects.sort(key=lambda x: (x["canon_pair"], x["aspect"], x["planet_a"]))

        evidence_trace: list[dict[str, Any]] = []
        active_aspects_for_signals: list[dict[str, Any]] = []
        total_active_weight: float = 0.0

        delta_harmony: float = 0.0
        delta_communication: float = 0.0
        delta_attraction: float = 0.0
        delta_growth: float = 0.0
        outer_aspect_total_points: float = 0.0

        for item in all_aspects:
            b_a = item["planet_a"]
            b_b = item["planet_b"]
            sub_h = item["sub_h"]
            sub_c = item["sub_c"]
            sub_a = item["sub_a"]
            sub_g = item["sub_g"]

            # Outer planet aspect cap: +12.0 points combined across all subscores
            if b_a in OUTER_PLANETS or b_b in OUTER_PLANETS:
                points_sum = max(0.0, sub_h) + max(0.0, sub_c) + max(0.0, sub_a) + max(0.0, sub_g)
                if outer_aspect_total_points + points_sum > 12.0:
                    scale = max(0.0, (12.0 - outer_aspect_total_points) / points_sum) if points_sum > 0 else 0.0
                    sub_h *= scale
                    sub_c *= scale
                    sub_a *= scale
                    sub_g *= scale
                    outer_aspect_total_points = 12.0
                else:
                    outer_aspect_total_points += points_sum

            delta_harmony += sub_h
            delta_communication += sub_c
            delta_attraction += sub_a
            delta_growth += sub_g
            total_active_weight += item["pair_weight"] * item["strength"]

            contributions = {}
            if abs(sub_h) > 0.01:
                contributions["harmony"] = round(sub_h, 2)
            if abs(sub_c) > 0.01:
                contributions["communication"] = round(sub_c, 2)
            if abs(sub_a) > 0.01:
                contributions["attraction"] = round(sub_a, 2)
            if abs(sub_g) > 0.01:
                contributions["growth"] = round(sub_g, 2)

            evidence_trace.append({
                "planet_a": b_a,
                "planet_b": b_b,
                "lon_a": round(item["lon_a"], 2),
                "lon_b": round(item["lon_b"], 2),
                "aspect": item["aspect"],
                "target_angle": item["target_angle"],
                "distance": round(item["actual_distance"], 2),
                "orb_diff": round(item["orb_diff"], 2),
                "max_orb": item["max_orb"],
                "strength": round(item["strength"], 4),
                "weight": item["pair_weight"],
                "subscore_contributions": contributions,
            })

            if item["strength"] >= 0.40:
                active_aspects_for_signals.append({
                    "planet_a": b_a,
                    "planet_b": b_b,
                    "aspect": item["aspect"],
                    "orb_diff": item["orb_diff"],
                    "strength": item["strength"],
                    "weight": item["pair_weight"],
                    "importance": item["pair_weight"] * item["strength"],
                })

        # Sort signals by importance (weight * strength descending)
        active_aspects_for_signals.sort(key=lambda x: x["importance"], reverse=True)
        signals = extract_signals_from_aspects(active_aspects_for_signals)

        # Derive elemental / modality balances (Section 12)
        sun_sign_a = longitude_to_sign(bodies_a.get("sun", 0.0))
        sun_sign_b = longitude_to_sign(bodies_b.get("sun", 0.0))
        moon_sign_a = longitude_to_sign(bodies_a.get("moon", 0.0))
        moon_sign_b = longitude_to_sign(bodies_b.get("moon", 0.0))

        elem_sun_a = ELEMENT_MAP.get(sun_sign_a, "Air")
        elem_sun_b = ELEMENT_MAP.get(sun_sign_b, "Air")
        elem_moon_a = ELEMENT_MAP.get(moon_sign_a, "Water")
        elem_moon_b = ELEMENT_MAP.get(moon_sign_b, "Water")

        e_harmony = calculate_elemental_harmony([elem_sun_a, elem_moon_a], [elem_sun_b, elem_moon_b])

        # Mercury compatibility
        merc_sign_a = longitude_to_sign(bodies_a.get("mercury", 0.0))
        merc_sign_b = longitude_to_sign(bodies_b.get("mercury", 0.0))
        merc_elem_a = ELEMENT_MAP.get(merc_sign_a, "Air")
        merc_elem_b = ELEMENT_MAP.get(merc_sign_b, "Air")
        m_mercury = calculate_elemental_harmony([merc_elem_a], [merc_elem_b])

        # Fire / Air synergy
        fa_count = sum(1 for e in (elem_sun_a, elem_sun_b, elem_moon_a, elem_moon_b) if e.lower() in ("fire", "air"))
        e_fire_air = 65.0 if fa_count >= 2 else 50.0

        # Modality balance
        mod_sun_a = MODALITY_MAP.get(sun_sign_a, "Cardinal")
        mod_sun_b = MODALITY_MAP.get(sun_sign_b, "Cardinal")
        modality_balance = 60.0 if mod_sun_a != mod_sun_b else 50.0

        # Compute 4 subscores (Section 12)
        s_harmony = max(0.0, min(100.0, 50.0 + delta_harmony + 0.35 * (e_harmony - 50.0)))
        s_communication = max(0.0, min(100.0, 50.0 + delta_communication + 0.25 * (m_mercury - 50.0)))
        s_attraction = max(0.0, min(100.0, 50.0 + delta_attraction + 0.20 * (e_fire_air - 50.0)))
        s_growth = max(0.0, min(100.0, 50.0 + delta_growth + 0.25 * (modality_balance - 50.0)))

        # Overall score (Section 13)
        raw_overall = 0.30 * s_harmony + 0.30 * s_attraction + 0.20 * s_communication + 0.20 * s_growth

        # Curve stretch & normalization (Section 14)
        centered = (raw_overall - 50.0) / 50.0
        sign_c = 1.0 if centered >= 0 else -1.0
        stretched = 50.0 + 50.0 * sign_c * (abs(centered) ** 0.85)
        final_score = round(max(10.0, min(98.0, stretched)), 1)

        # Minimum evidence rules (Section 22)
        confidence = 1.0
        if is_unknown:
            confidence = 0.75
        elif is_approx:
            confidence = 0.85

        if total_active_weight < 2.0:
            final_score = 65.0
            confidence = 0.50
            signals = [{
                "type": "insufficient_aspects",
                "category": "notice",
                "strength": "low",
                "source_aspects": [],
                "label": "Independent Chart Dynamics",
            }]

        # Derive topics and starters (Sections 17 & 18)
        dominant_elem = elem_sun_a if elem_sun_a == elem_sun_b else None
        dominant_pattern = signals[0]["type"] if signals else None
        best_topics = extract_best_topics(dominant_element=dominant_elem, dominant_aspect_pattern=dominant_pattern)
        starters = extract_conversation_starters(signals)

        # Data quality
        data_quality = {
            "time_precision": "unknown" if is_unknown else ("approximate" if is_approx else "exact"),
            "confidence": confidence,
            "houses_used": not is_unknown,
            "ascendant_used": (not is_unknown) and ("ascendant" in bodies_a) and ("ascendant" in bodies_b),
        }

        dimensions = {
            "emotional_harmony": round(s_harmony, 1),
            "communication": round(s_communication, 1),
            "attraction": round(s_attraction, 1),
            "growth_long_term": round(s_growth, 1),
        }

        return SynastryResult(
            score=final_score,
            dimensions=dimensions,
            signals=signals,
            best_topics=best_topics,
            conversation_starters=starters,
            data_quality=data_quality,
            evidence_trace=evidence_trace,
            engine_version="synastry-v1.0.0",
        )
