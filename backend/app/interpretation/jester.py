"""
Jester Voice Persona Guidelines & Jargon Enforcement Layer.
Ensures consumer-facing copy remains witty, human, conversational, and free of astrological jargon.
"""
import re

# Astrology terms strictly forbidden in consumer-facing copy
FORBIDDEN_ASTROLOGY_JARGON_EN = {
    "conjunction",
    "opposition",
    "trine",
    "square",
    "sextile",
    "quincunx",
    "orb",
    "synastry",
    "transit",
    "house",
    "aspect",
    "placidus",
    "ephemeris",
    "natal chart",
    "horoscope",
    "ascendant",
    "midheaven",
    "ecliptic",
    "declination",
    "planetary longitude",
}

FORBIDDEN_ASTROLOGY_JARGON_KA = {
    "კონიუნქცია",
    "ოპოზიცია",
    "ტრინი",
    "კვადრატურა",
    "სექსტილი",
    "ორბი",
    "სინასტრია",
    "ტრანზიტი",
    "პლაციდუსი",
    "ეფემერიდი",
    "ნატალური",
    "ჰოროსკოპი",
    "ასცენდენტი",
    "ეკლიპტიკა",
    "ასპექტი",
}


def find_astrology_jargon(text: str) -> list[str]:
    """
    Scans text for prohibited astrological terminology in English or Georgian.
    Returns a list of detected jargon words.
    """
    if not text:
        return []

    detected: list[str] = []
    text_lower = text.lower()

    for term in FORBIDDEN_ASTROLOGY_JARGON_EN:
        # Match whole word boundaries where possible
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, text_lower):
            detected.append(term)

    for term in FORBIDDEN_ASTROLOGY_JARGON_KA:
        if term.lower() in text_lower:
            detected.append(term)

    return detected


def validate_no_jargon(text: str) -> bool:
    """
    Validates that the provided text contains zero prohibited astrological jargon terms.
    """
    return len(find_astrology_jargon(text)) == 0


def assert_no_jargon(text: str) -> None:
    """
    Raises ValueError if prohibited astrology jargon is detected in the copy.
    """
    found = find_astrology_jargon(text)
    if found:
        raise ValueError(f"Prohibited astrology jargon detected in copy: {', '.join(found)}")


class JesterVoicePersona:
    """
    Jester Brand Voice Constants & Guidelines.
    """
    NAME = "JESTER"
    TONE = "smart_warm_ironic"
    HUMOR_MODE = "observational_witty"
    MAX_SENTENCES = 2
    LANGUAGE = "ka"
    NO_JARGON = True
