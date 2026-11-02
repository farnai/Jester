import pytest
from backend.app.interpretation.weekly_energy import (
    WEEKLY_ARCHETYPES_DATA,
    get_weekly_energy_content,
)

FORBIDDEN_JARGON = [
    "ორბი", "ასპექტი", "ტრანზიტ", "ტრინი", "კვადრატ",
    "სექსტილ", "ოპოზიცი", "ასცენდენტ", "პლანეტ", "ეკლიპტიკ",
    "კოსმიურ",
]

EXPECTED_ARCHETYPES = [
    "confidence", "clarity", "vitality", "creativity", "communication",
    "social", "introspection", "curiosity", "discipline", "receptivity",
    "restlessness", "focus", "neutral",
]


def test_all_13_weekly_archetypes_exist_and_distinct():
    assert len(WEEKLY_ARCHETYPES_DATA) == 13
    assert set(WEEKLY_ARCHETYPES_DATA.keys()) == set(EXPECTED_ARCHETYPES)

    quotes = set()
    themes = set()
    for arch_id, data in WEEKLY_ARCHETYPES_DATA.items():
        assert "label_ka" in data and len(data["label_ka"]) > 5
        assert "quote_ka" in data and len(data["quote_ka"]) > 10
        assert "theme_ka" in data and len(data["theme_ka"]) > 10
        assert "reflection_ka" in data and len(data["reflection_ka"]) > 10
        assert "focus_ka" in data and len(data["focus_ka"]) > 10
        assert "preview_teaser_ka" in data and len(data["preview_teaser_ka"]) > 10

        quotes.add(data["quote_ka"])
        themes.add(data["theme_ka"])

    # Ensure 100% uniqueness across archetypes
    assert len(quotes) == 13
    assert len(themes) == 13


def test_zero_astrology_jargon_in_weekly_consumer_copy():
    for arch_id, data in WEEKLY_ARCHETYPES_DATA.items():
        for field in ["label_ka", "quote_ka", "theme_ka", "reflection_ka", "focus_ka", "preview_teaser_ka"]:
            text = data[field].lower()
            for word in FORBIDDEN_JARGON:
                assert word not in text, f"Weekly archetype '{arch_id}' field '{field}' contains forbidden jargon '{word}': {data[field]}"


def test_weekly_archetype_lookup_fallback():
    # Known archetype
    conf = get_weekly_energy_content("confidence")
    assert conf["label_ka"] == WEEKLY_ARCHETYPES_DATA["confidence"]["label_ka"]

    # Case insensitive
    vitality = get_weekly_energy_content("VITALITY  ")
    assert vitality["label_ka"] == WEEKLY_ARCHETYPES_DATA["vitality"]["label_ka"]

    # Unknown falls back to neutral
    fallback = get_weekly_energy_content("unknown_archetype_xyz")
    assert fallback["label_ka"] == WEEKLY_ARCHETYPES_DATA["neutral"]["label_ka"]

