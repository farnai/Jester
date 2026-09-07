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
    "sun_opposite_moon": [
        "In what areas of life do you feel you balance logic and emotion best?",
        "What kind of conversations make you look at things from a completely new angle?",
    ],
    "sun_square_moon": [
        "How do you usually ground yourself when your head and heart want different things?",
        "What is something you are passionate about that catches people by surprise?",
    ],
    "sun_opposite_sun": [
        "What is a perspective or philosophy that challenges the way you see the world?",
        "What kind of environment brings out your most focused creative energy?",
    ],
    "sun_square_sun": [
        "What is an ambitious challenge that brought out your strongest resilience?",
        "What kind of creative debate keeps you most engaged?",
    ],
    "sun_trine_mars": [
        "What exciting venture or project are you most eager to tackle next?",
        "What kind of shared adventure gives you the biggest boost of momentum?",
    ],
    "sun_conjunction_mars": [
        "What big goal are you pouring your most intense focus into right now?",
        "What helps you stay fully motivated when building something from scratch?",
    ],
    "moon_sextile_venus": [
        "What is your favorite comfort ritual or calming atmosphere after a busy day?",
        "What piece of music or art always restores your emotional balance?",
    ],
    "sun_sextile_mercury": [
        "What is an interesting concept or discovery you've been pondering lately?",
        "What is a question you wish people asked you more often?",
    ],
    "venus_trine_jupiter": [
        "What destination or experience is at the very top of your wish list?",
        "What is something generous or uplifting someone did that stayed with you?",
    ],
    "venus_conjunction_jupiter": [
        "What is your idea of a truly memorable, celebratory evening?",
        "What creative vision or aesthetic project brings you pure joy?",
    ],
    "venus_trine_pluto": [
        "What kind of storytelling or art truly moves you to the core?",
        "What is a personal truth that completely transformed your outlook?",
    ],
    "venus_conjunction_pluto": [
        "What kind of cinema, books, or art leave a lasting mark on you?",
        "What is an experience that radically shifted your priorities?",
    ],
    "venus_opposite_pluto": [
        "What kind of art or story explores the human psyche best for you?",
        "How do you uncover what is genuinely authentic beneath the surface?",
    ],
    "saturn_trine_sun": [
        "What long-term foundation or craft are you most dedicated to building?",
        "What principle has proven most reliable for you over time?",
    ],
    "saturn_trine_moon": [
        "What personal ritual or space gives you the deepest sense of peace and stability?",
        "What is a life lesson that gave you lasting emotional clarity?",
    ],
    "saturn_trine_venus": [
        "What is an enduring design, architectural space, or artwork you never tire of?",
        "What does quality and deliberate craftsmanship mean to you?",
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


CANONICAL_TOPICS: set[str] = {
    "ideas",
    "philosophy",
    "books",
    "creative_work",
    "travel",
    "adventure",
    "fitness",
    "ambition",
    "art",
    "music",
    "psychology",
    "cinema",
    "architecture",
    "food",
    "design",
    "lifestyle",
}

# Signal-to-topic candidates mapping: signal_type -> list of (topic, base_relevance)
SIGNAL_TOPIC_CANDIDATES: dict[str, list[tuple[str, float]]] = {
    # Sun - Moon (Deep emotional resonance, intuitive connection, inner feeling)
    "sun_trine_moon": [("psychology", 3.0), ("music", 2.0), ("lifestyle", 1.5), ("ideas", 1.0)],
    "sun_sextile_moon": [("psychology", 3.0), ("music", 2.0), ("ideas", 1.5), ("lifestyle", 1.0)],
    "sun_conjunction_moon": [("psychology", 3.0), ("music", 2.2), ("lifestyle", 1.5), ("food", 1.0)],
    "sun_opposite_moon": [("psychology", 3.0), ("philosophy", 2.0), ("lifestyle", 1.5)],
    "sun_square_moon": [("psychology", 3.0), ("lifestyle", 2.0), ("ambition", 1.5)],

    # Sun - Sun (Core identity harmony, creative drive, life paths)
    "sun_trine_sun": [("creative_work", 3.0), ("philosophy", 2.2), ("travel", 1.8), ("ambition", 1.2)],
    "sun_sextile_sun": [("creative_work", 3.0), ("ideas", 2.2), ("philosophy", 1.8), ("lifestyle", 1.2)],
    "sun_conjunction_sun": [("creative_work", 3.0), ("ambition", 2.2), ("travel", 1.8), ("philosophy", 1.2)],
    "sun_opposite_sun": [("philosophy", 3.0), ("ideas", 2.2), ("creative_work", 1.8)],
    "sun_square_sun": [("ambition", 3.0), ("creative_work", 2.0), ("fitness", 1.5)],

    # Venus - Mars (Magnetic chemistry, passion, artistic/sensory spark)
    "venus_conjunction_mars": [("art", 3.0), ("adventure", 2.2), ("cinema", 1.8), ("music", 1.5)],
    "venus_opposite_mars": [("art", 3.0), ("cinema", 2.2), ("adventure", 1.8), ("music", 1.5)],
    "venus_trine_mars": [("art", 3.0), ("adventure", 2.2), ("music", 1.8), ("lifestyle", 1.2)],
    "venus_sextile_mars": [("art", 3.0), ("adventure", 2.0), ("design", 1.8), ("music", 1.5)],
    "venus_square_mars": [("art", 3.0), ("cinema", 2.2), ("fitness", 1.8), ("adventure", 1.2)],

    # Sun - Venus (Warm affection, aesthetics, shared enjoyment)
    "sun_conjunction_venus": [("art", 3.0), ("design", 2.2), ("food", 1.8), ("lifestyle", 1.5)],
    "sun_trine_venus": [("art", 3.0), ("lifestyle", 2.2), ("travel", 1.8), ("music", 1.5)],
    "sun_sextile_venus": [("art", 3.0), ("design", 2.2), ("lifestyle", 1.8), ("creative_work", 1.5)],

    # Moon - Venus (Gentle affinity, comfort, cozy intimacy, music & culinary)
    "moon_conjunction_venus": [("music", 3.0), ("psychology", 2.2), ("food", 2.0), ("design", 1.5)],
    "moon_trine_venus": [("music", 3.0), ("psychology", 2.2), ("food", 2.0), ("lifestyle", 1.5)],
    "moon_sextile_venus": [("music", 3.0), ("art", 2.2), ("food", 2.0), ("design", 1.5)],

    # Mercury - Mercury (Intellectual flow, mental wavelength, ideas & literature)
    "mercury_trine_mercury": [("ideas", 3.0), ("philosophy", 2.5), ("books", 2.2), ("creative_work", 1.5)],
    "mercury_sextile_mercury": [("ideas", 3.0), ("books", 2.5), ("philosophy", 2.0), ("creative_work", 1.5)],
    "mercury_conjunction_mercury": [("ideas", 3.0), ("books", 2.5), ("philosophy", 2.2), ("creative_work", 1.5)],

    # Sun - Mercury (Mutual understanding, shared perspectives)
    "sun_trine_mercury": [("ideas", 3.0), ("books", 2.5), ("creative_work", 1.8), ("philosophy", 1.5)],
    "sun_sextile_mercury": [("ideas", 3.0), ("books", 2.5), ("creative_work", 1.8), ("lifestyle", 1.5)],
    "sun_conjunction_mercury": [("ideas", 3.0), ("creative_work", 2.5), ("books", 2.0), ("philosophy", 1.5)],

    # Mars - Saturn & Sun/Moon - Saturn (Pacing, mastery, discipline, ambition)
    "mars_square_saturn": [("ambition", 3.0), ("fitness", 2.2), ("lifestyle", 1.8), ("architecture", 1.2)],
    "sun_square_saturn": [("ambition", 3.0), ("lifestyle", 2.2), ("architecture", 1.8), ("philosophy", 1.2)],
    "moon_square_saturn": [("psychology", 3.0), ("lifestyle", 2.2), ("ambition", 1.8)],

    # Sun - Mars & Mars - Sun (Dynamic spark, high energy, athletic/enterprising)
    "sun_square_mars": [("ambition", 3.0), ("fitness", 2.5), ("adventure", 2.0)],
    "mars_square_sun": [("ambition", 3.0), ("fitness", 2.5), ("adventure", 2.0)],
    "sun_trine_mars": [("adventure", 3.0), ("fitness", 2.5), ("ambition", 2.0), ("travel", 1.5)],
    "sun_conjunction_mars": [("ambition", 3.0), ("adventure", 2.5), ("fitness", 2.0), ("creative_work", 1.5)],

    # Jupiter Aspects (Shared optimism, broad horizons, travel & philosophy)
    "sun_trine_jupiter": [("travel", 3.0), ("philosophy", 2.5), ("ideas", 1.8), ("adventure", 1.5)],
    "sun_conjunction_jupiter": [("travel", 3.0), ("philosophy", 2.5), ("adventure", 1.8), ("ideas", 1.5)],
    "moon_trine_jupiter": [("travel", 3.0), ("philosophy", 2.2), ("psychology", 2.0), ("lifestyle", 1.5)],
    "venus_trine_jupiter": [("travel", 3.0), ("art", 2.2), ("food", 2.0), ("lifestyle", 1.5)],
    "venus_conjunction_jupiter": [("travel", 3.0), ("food", 2.2), ("art", 2.0), ("design", 1.5)],

    # Venus - Pluto (Intense magnetism, psychological depth, transformative cinema/art)
    "venus_trine_pluto": [("psychology", 3.0), ("art", 2.2), ("cinema", 2.0), ("music", 1.5)],
    "venus_conjunction_pluto": [("psychology", 3.0), ("cinema", 2.2), ("art", 2.0), ("music", 1.5)],
    "venus_opposite_pluto": [("psychology", 3.0), ("cinema", 2.2), ("art", 1.8), ("philosophy", 1.5)],

    # Saturn Trines (Long-term grounding, architecture, design, craftsmanship, lifestyle)
    "saturn_trine_sun": [("lifestyle", 3.0), ("architecture", 2.5), ("ambition", 2.0), ("design", 1.5)],
    "saturn_trine_moon": [("lifestyle", 3.0), ("design", 2.2), ("food", 2.0), ("psychology", 1.8)],
    "saturn_trine_venus": [("design", 3.0), ("architecture", 2.5), ("lifestyle", 2.0), ("food", 1.8)],
}


def _get_signal_topic_candidates(sig: dict[str, Any]) -> list[tuple[str, float]]:
    """
    Resolves topic candidates and relevance weights for a signal.
    Uses exact definition mapping if known, or heuristic planet/category breakdown as fallback.
    """
    sig_type = sig.get("type", "").lower()
    if sig_type in SIGNAL_TOPIC_CANDIDATES:
        return SIGNAL_TOPIC_CANDIDATES[sig_type]

    candidates: list[tuple[str, float]] = []
    category = sig.get("category", "").lower()

    if "mercury" in sig_type:
        candidates.extend([("ideas", 2.5), ("books", 2.0), ("creative_work", 1.5)])
    if "moon" in sig_type:
        candidates.extend([("psychology", 2.5), ("music", 2.0), ("lifestyle", 1.5)])
    if "venus" in sig_type:
        candidates.extend([("art", 2.5), ("design", 2.0), ("cinema", 1.5)])
    if "mars" in sig_type:
        candidates.extend([("ambition", 2.5), ("adventure", 2.0), ("fitness", 1.5)])
    if "jupiter" in sig_type:
        candidates.extend([("travel", 2.5), ("philosophy", 2.0), ("ideas", 1.5)])
    if "saturn" in sig_type:
        candidates.extend([("lifestyle", 2.5), ("architecture", 2.0), ("design", 1.5)])
    if "pluto" in sig_type:
        candidates.extend([("psychology", 2.5), ("cinema", 2.0)])
    if "sun" in sig_type:
        candidates.extend([("creative_work", 2.0), ("travel", 1.5), ("ambition", 1.5)])
    if "ascendant" in sig_type:
        candidates.extend([("lifestyle", 2.0), ("adventure", 1.5)])

    if not candidates:
        if category == "communication":
            candidates = [("ideas", 2.5), ("books", 2.0), ("philosophy", 1.5)]
        elif category == "harmony":
            candidates = [("psychology", 2.5), ("music", 2.0), ("lifestyle", 1.5)]
        elif category == "attraction":
            candidates = [("art", 2.5), ("cinema", 2.0), ("adventure", 1.5)]
        elif category == "stability":
            candidates = [("lifestyle", 2.5), ("design", 2.0), ("architecture", 1.5)]
        else:
            candidates = [("ambition", 2.0), ("creative_work", 2.0), ("ideas", 1.5)]

    return candidates


def extract_best_topics(
    signals: list[dict[str, Any]] | None = None,
    dominant_element: str | None = None,
    dominant_aspect_pattern: str | None = None,
) -> list[str]:
    """
    Derives up to 4 conversation topics deterministically according to Section 17.
    Evaluates multiple relationship signals with rank decay and strength weighting.
    Guarantees symmetry, determinism, deduplication, and bounds to canonical vocabulary.
    """
    valid_signals = [s for s in (signals or []) if s.get("type") != "insufficient_aspects"]

    if valid_signals:
        scores: dict[str, float] = {}
        decay_factors = [1.0, 0.8, 0.6, 0.4, 0.25]

        for idx, sig in enumerate(valid_signals[:5]):
            rank_mult = decay_factors[idx] if idx < len(decay_factors) else 0.2
            strength = sig.get("strength", "medium")
            str_mult = 1.2 if strength == "high" else (0.8 if strength == "low" else 1.0)

            candidates = _get_signal_topic_candidates(sig)
            for topic, base_weight in candidates:
                if topic in CANONICAL_TOPICS:
                    scores[topic] = scores.get(topic, 0.0) + (base_weight * rank_mult * str_mult)

        # Apply elemental bonus if dominant element exists
        elem = (dominant_element or "").lower()
        if elem == "air":
            scores["ideas"] = scores.get("ideas", 0.0) + 1.2
            scores["books"] = scores.get("books", 0.0) + 0.8
        elif elem == "fire":
            scores["travel"] = scores.get("travel", 0.0) + 1.2
            scores["adventure"] = scores.get("adventure", 0.0) + 0.8
        elif elem == "water":
            scores["psychology"] = scores.get("psychology", 0.0) + 1.2
            scores["art"] = scores.get("art", 0.0) + 0.8
        elif elem == "earth":
            scores["lifestyle"] = scores.get("lifestyle", 0.0) + 1.2
            scores["design"] = scores.get("design", 0.0) + 0.8

        if scores:
            # Deterministic sorting: highest score first; ties broken alphabetically by topic key
            ranked = sorted(scores.keys(), key=lambda t: (-round(scores[t], 4), t))
            return ranked[:4]

    # Legacy / fallback path if signals are not passed, empty, or insufficient
    elem = (dominant_element or "").lower()
    pattern = (dominant_aspect_pattern or "").lower()

    if elem == "air" or "mercury" in pattern or "air" in pattern:
        return ["ideas", "philosophy", "books", "creative_work"]
    elif elem == "fire" or "mars" in pattern or "fire" in pattern:
        return ["travel", "adventure", "fitness", "ambition"]
    elif elem == "water" or "moon" in pattern or "water" in pattern:
        return ["psychology", "art", "music", "cinema"]
    elif elem == "earth" or "saturn" in pattern or "earth" in pattern:
        return ["lifestyle", "design", "food", "architecture"]

    return ["ideas", "lifestyle", "travel", "psychology"]


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
