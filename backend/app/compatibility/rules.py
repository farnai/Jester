"""
Deterministic signal extraction, topic generation, and conversation starter rules for Synastry V1.
Follows the frozen specification in docs/SYNASTRY_V1_SPEC.md (Sections 16, 17, 18).
"""
from typing import Any

# Conversation starter rules mapped to signal types (Section 18)
CONVERSATION_STARTER_RULES: dict[str, list[str]] = {
    "sun_trine_moon": [
        "What is something that instantly makes you feel understood?",
        "What is your favorite way to recharge after a long week?",
    ],
    "sun_sextile_moon": [
        "What is something that instantly makes you feel understood?",
        "What is your favorite way to recharge after a long week?",
    ],
    "sun_conjunction_moon": [
        "What is something that instantly makes you feel understood?",
        "What is your favorite way to recharge after a long week?",
    ],
    "venus_conjunction_mars": [
        "What is your idea of a perfect spontaneous date?",
        "What art or music has inspired you recently?",
    ],
    "venus_opposite_mars": [
        "What is your idea of a perfect spontaneous date?",
        "What art or music has inspired you recently?",
    ],
    "venus_trine_mars": [
        "What is your idea of a perfect spontaneous date?",
        "What art or music has inspired you recently?",
    ],
    "venus_sextile_mars": [
        "What is your idea of a perfect spontaneous date?",
        "What art or music has inspired you recently?",
    ],
    "venus_square_mars": [
        "What is your idea of a perfect spontaneous date?",
        "What art or music has inspired you recently?",
    ],
    "mercury_trine_mercury": [
        "Have you read or listened to anything surprising lately?",
        "What topic could you talk about for hours without getting bored?",
    ],
    "mercury_sextile_mercury": [
        "Have you read or listened to anything surprising lately?",
        "What topic could you talk about for hours without getting bored?",
    ],
    "mercury_conjunction_mercury": [
        "Have you read or listened to anything surprising lately?",
        "What topic could you talk about for hours without getting bored?",
    ],
    "sun_trine_jupiter": [
        "What is a dream or adventure you'd love to pursue this year?",
        "What is something that always brings you unshakeable optimism?",
    ],
    "sun_conjunction_jupiter": [
        "What is a dream or adventure you'd love to pursue this year?",
        "What is something that always brings you unshakeable optimism?",
    ],
    "moon_trine_jupiter": [
        "What is a dream or adventure you'd love to pursue this year?",
        "What is something that always brings you unshakeable optimism?",
    ],
    "mars_square_saturn": [
        "How do you prefer to navigate challenges when building something ambitious?",
        "What habit has helped you master patience and discipline?",
    ],
    "sun_square_saturn": [
        "How do you prefer to navigate challenges when building something ambitious?",
        "What habit has helped you master patience and discipline?",
    ],
    "moon_square_saturn": [
        "How do you prefer to navigate challenges when building something ambitious?",
        "What habit has helped you master patience and discipline?",
    ],
    "sun_square_mars": [
        "What kind of friendly competition or high-energy projects excite you?",
        "What is an ambitious goal you are tackling right now?",
    ],
    "mars_square_sun": [
        "What kind of friendly competition or high-energy projects excite you?",
        "What is an ambitious goal you are tackling right now?",
    ],
    "sun_trine_sun": [
        "What shared passion or creative pursuit energizes you most?",
        "What is a core value that guides your biggest life decisions?",
    ],
    "sun_conjunction_sun": [
        "What shared passion or creative pursuit energizes you most?",
        "What is a core value that guides your biggest life decisions?",
    ],
    "sun_conjunction_venus": [
        "What kind of aesthetic, atmosphere, or travel destination inspires you most?",
        "What is something simple that always brings you joy?",
    ],
    "sun_trine_venus": [
        "What kind of aesthetic, atmosphere, or travel destination inspires you most?",
        "What is something simple that always brings you joy?",
    ],
    "sun_sextile_venus": [
        "What kind of aesthetic, atmosphere, or travel destination inspires you most?",
        "What is something simple that always brings you joy?",
    ],
    "moon_conjunction_venus": [
        "What is your favorite comfort food or cozy space?",
        "What kind of music or art helps you unwind?",
    ],
    "moon_trine_venus": [
        "What is your favorite comfort food or cozy space?",
        "What kind of music or art helps you unwind?",
    ],
    "sun_trine_mercury": [
        "What is a book, podcast, or idea that recently changed your perspective?",
        "How do you like to explore new concepts or brainstorm ideas?",
    ],
    "sun_conjunction_mercury": [
        "What is a book, podcast, or idea that recently changed your perspective?",
        "How do you like to explore new concepts or brainstorm ideas?",
    ],
}

DEFAULT_CONVERSATION_STARTERS = [
    "What is something that instantly makes you feel understood?",
    "What is your favorite way to spend an inspiring afternoon?",
    "Have you discovered any great books, music, or places recently?",
]

# Signal definitions mapped by (planet_pair, aspect_type) -> (type, category, default_strength, label)
SIGNAL_DEFINITIONS: dict[tuple[str, str, str], tuple[str, str, str, str]] = {
    # Sun - Moon
    ("sun", "moon", "trine"): ("sun_trine_moon", "harmony", "high", "Emotional Resonance"),
    ("sun", "moon", "sextile"): ("sun_sextile_moon", "harmony", "high", "Emotional Resonance"),
    ("sun", "moon", "conjunction"): ("sun_conjunction_moon", "harmony", "high", "Emotional Resonance"),
    ("sun", "moon", "opposition"): ("sun_opposite_moon", "growth", "high", "Complementary Balance"),
    ("sun", "moon", "square"): ("sun_square_moon", "growth", "medium", "Dynamic Emotional Tension"),

    # Sun - Sun
    ("sun", "sun", "trine"): ("sun_trine_sun", "harmony", "high", "Core Harmony"),
    ("sun", "sun", "sextile"): ("sun_sextile_sun", "harmony", "high", "Core Harmony"),
    ("sun", "sun", "conjunction"): ("sun_conjunction_sun", "harmony", "high", "Core Harmony"),
    ("sun", "sun", "opposition"): ("sun_opposite_sun", "growth", "medium", "Contrasting Perspectives"),
    ("sun", "sun", "square"): ("sun_square_sun", "growth", "medium", "Ego Friction"),

    # Venus - Mars
    ("venus", "mars", "conjunction"): ("venus_conjunction_mars", "attraction", "high", "Magnetic Chemistry"),
    ("venus", "mars", "opposition"): ("venus_opposite_mars", "attraction", "high", "Magnetic Chemistry"),
    ("venus", "mars", "trine"): ("venus_trine_mars", "attraction", "high", "Magnetic Chemistry"),
    ("venus", "mars", "sextile"): ("venus_sextile_mars", "attraction", "high", "Magnetic Chemistry"),
    ("venus", "mars", "square"): ("venus_square_mars", "attraction", "high", "Magnetic Chemistry"),

    # Sun - Venus
    ("sun", "venus", "conjunction"): ("sun_conjunction_venus", "attraction", "high", "Warm Affection"),
    ("sun", "venus", "trine"): ("sun_trine_venus", "attraction", "high", "Warm Affection"),
    ("sun", "venus", "sextile"): ("sun_sextile_venus", "attraction", "high", "Warm Affection"),

    # Moon - Venus
    ("moon", "venus", "conjunction"): ("moon_conjunction_venus", "harmony", "high", "Gentle Affinity"),
    ("moon", "venus", "trine"): ("moon_trine_venus", "harmony", "high", "Gentle Affinity"),
    ("moon", "venus", "sextile"): ("moon_sextile_venus", "harmony", "high", "Gentle Affinity"),

    # Mercury - Mercury
    ("mercury", "mercury", "trine"): ("mercury_trine_mercury", "communication", "high", "Intellectual Flow"),
    ("mercury", "mercury", "sextile"): ("mercury_sextile_mercury", "communication", "high", "Intellectual Flow"),
    ("mercury", "mercury", "conjunction"): ("mercury_conjunction_mercury", "communication", "high", "Intellectual Flow"),

    # Sun - Mercury
    ("sun", "mercury", "trine"): ("sun_trine_mercury", "communication", "medium", "Mutual Understanding"),
    ("sun", "mercury", "sextile"): ("sun_sextile_mercury", "communication", "medium", "Mutual Understanding"),
    ("sun", "mercury", "conjunction"): ("sun_conjunction_mercury", "communication", "medium", "Mutual Understanding"),

    # Mars / Sun / Moon - Saturn (Squares)
    ("mars", "saturn", "square"): ("mars_square_saturn", "growth", "medium", "Pacing Tension"),
    ("sun", "saturn", "square"): ("sun_square_saturn", "growth", "medium", "Pacing Tension"),
    ("moon", "saturn", "square"): ("moon_square_saturn", "growth", "medium", "Pacing Tension"),

    # Mars - Sun
    ("mars", "sun", "square"): ("mars_square_sun", "growth", "medium", "Dynamic Spark"),
    ("sun", "mars", "square"): ("sun_square_mars", "growth", "medium", "Dynamic Spark"),
    ("sun", "mars", "trine"): ("sun_trine_mars", "attraction", "high", "Energized Collaboration"),
    ("sun", "mars", "conjunction"): ("sun_conjunction_mars", "attraction", "high", "Dynamic Drive"),

    # Sun / Moon / Venus - Jupiter
    ("sun", "jupiter", "trine"): ("sun_trine_jupiter", "stability", "high", "Shared Optimism"),
    ("sun", "jupiter", "conjunction"): ("sun_conjunction_jupiter", "stability", "high", "Shared Optimism"),
    ("moon", "jupiter", "trine"): ("moon_trine_jupiter", "stability", "high", "Shared Optimism"),
    ("venus", "jupiter", "trine"): ("venus_trine_jupiter", "harmony", "high", "Generous Affection"),
    ("venus", "jupiter", "conjunction"): ("venus_conjunction_jupiter", "harmony", "high", "Generous Affection"),

    # Venus - Pluto
    ("venus", "pluto", "trine"): ("venus_trine_pluto", "attraction", "high", "Intense Magnetism"),
    ("venus", "pluto", "conjunction"): ("venus_conjunction_pluto", "attraction", "high", "Intense Magnetism"),
    ("venus", "pluto", "opposite"): ("venus_opposite_pluto", "attraction", "high", "Intense Magnetism"),
    ("venus", "pluto", "opposition"): ("venus_opposite_pluto", "attraction", "high", "Intense Magnetism"),

    # Saturn Trines
    ("saturn", "sun", "trine"): ("saturn_trine_sun", "stability", "high", "Long-term Grounding"),
    ("sun", "saturn", "trine"): ("saturn_trine_sun", "stability", "high", "Long-term Grounding"),
    ("saturn", "moon", "trine"): ("saturn_trine_moon", "stability", "high", "Long-term Grounding"),
    ("moon", "saturn", "trine"): ("saturn_trine_moon", "stability", "high", "Long-term Grounding"),
    ("saturn", "venus", "trine"): ("saturn_trine_venus", "stability", "high", "Long-term Grounding"),
    ("venus", "saturn", "trine"): ("saturn_trine_venus", "stability", "high", "Long-term Grounding"),
}


def extract_signals_from_aspects(active_aspects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Extracts up to 6 deterministic signals from active aspects where strength >= 0.40.
    Aspects must be sorted by importance (weight * strength).
    """
    signals: list[dict[str, Any]] = []
    seen_signal_types: set[str] = set()

    for item in active_aspects:
        if item["strength"] < 0.40:
            continue

        p_a = item["planet_a"].lower()
        p_b = item["planet_b"].lower()
        asp_type = item["aspect"].lower()
        orb_deg = round(item["orb_diff"], 1)

        # Lookup rule in direct and reverse order
        key = (p_a, p_b, asp_type)
        rev_key = (p_b, p_a, asp_type)

        rule = SIGNAL_DEFINITIONS.get(key) or SIGNAL_DEFINITIONS.get(rev_key)
        if rule:
            sig_type, category, default_strength, label = rule
            if sig_type not in seen_signal_types:
                seen_signal_types.add(sig_type)
                sig_strength = "high" if item["strength"] >= 0.70 else default_strength
                source_label = f"{p_a.capitalize()} {asp_type.capitalize()} {p_b.capitalize()} (Orb {orb_deg}°)"
                signals.append({
                    "type": sig_type,
                    "category": category,
                    "strength": sig_strength,
                    "source_aspects": [source_label],
                    "label": label,
                })
        else:
            # Generic fallback signal if significant high-weight aspect
            sig_type = f"{min(p_a, p_b)}_{asp_type}_{max(p_a, p_b)}"
            if sig_type not in seen_signal_types and item.get("weight", 1.0) >= 2.0:
                seen_signal_types.add(sig_type)
                category = "harmony" if asp_type in ("trine", "sextile", "conjunction") else "growth"
                sig_strength = "high" if item["strength"] >= 0.70 else "medium"
                source_label = f"{p_a.capitalize()} {asp_type.capitalize()} {p_b.capitalize()} (Orb {orb_deg}°)"
                signals.append({
                    "type": sig_type,
                    "category": category,
                    "strength": sig_strength,
                    "source_aspects": [source_label],
                    "label": f"{p_a.capitalize()}-{p_b.capitalize()} {asp_type.capitalize()}",
                })

        if len(signals) >= 6:
            break

    return signals[:6]


def extract_best_topics(dominant_element: str | None = None, dominant_aspect_pattern: str | None = None) -> list[str]:
    """
    Derives up to 4 conversation topics deterministically according to Section 17.
    """
    elem = (dominant_element or "").lower()
    pattern = (dominant_aspect_pattern or "").lower()

    if elem == "air" or "mercury" in pattern or "air" in pattern:
        return ["books", "philosophy", "ideas", "creative_work"]
    elif elem == "fire" or "mars" in pattern or "sun" in pattern or "fire" in pattern:
        return ["travel", "adventure", "fitness", "ambition"]
    elif elem == "water" or "moon" in pattern or "venus" in pattern or "water" in pattern:
        return ["art", "music", "psychology", "cinema"]
    elif elem == "earth" or "saturn" in pattern or "earth" in pattern:
        return ["architecture", "food", "design", "lifestyle"]

    return ["travel", "books", "creative_work", "lifestyle"]


def extract_conversation_starters(signals: list[dict[str, Any]]) -> list[str]:
    """
    Generates up to 3 conversation starters deterministically based on top signals.
    """
    starters: list[str] = []
    seen: set[str] = set()

    for sig in signals:
        sig_type = sig.get("type", "")
        rule_starters = CONVERSATION_STARTER_RULES.get(sig_type, [])
        for st in rule_starters:
            if st not in seen:
                seen.add(st)
                starters.append(st)
                if len(starters) >= 3:
                    return starters

    # Fill up with defaults if needed
    for fallback in DEFAULT_CONVERSATION_STARTERS:
        if fallback not in seen:
            seen.add(fallback)
            starters.append(fallback)
            if len(starters) >= 3:
                break

    return starters[:3]
