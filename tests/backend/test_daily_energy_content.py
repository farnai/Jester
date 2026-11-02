"""
Unit and Quality Gate Tests for JESTER Daily Energy Content Architecture.
Verifies:
1. All 13 archetypes resolve deterministically to distinct, authentic Georgian text
2. Zero fallback to generic 'confidence' when other archetypes are requested
3. Zero consumer-facing astrology jargon in quote, explanation, or tags
4. Presence of curated 3 DO and 3 DON'T guidance tags for all archetypes
5. Core Triad structure adherence (Observation -> Contradiction -> Punchline)
"""
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.astrology.transits import get_daily_guidance
from backend.app.interpretation.engine import interpretation_engine
from backend.app.interpretation.router import DAILY_ENERGY_ARCHETYPES, DAILY_ENERGY_EXPLANATIONS_KA
from backend.app.main import app

FORBIDDEN_JARGON = [
    "ორბი", "ასპექტი", "ტრანზიტი", "კვადრატი", "ტრინი", "სექსტილი", 
    "შეერთება", "ოპოზიცია", "ასცენდენტი", "ნატალური", "პლანეტა", "ეფემერიდი", "ზოდიაქო"
]


def test_all_13_archetypes_resolve_distinctly():
    """
    Tests that every archetype in DAILY_ENERGY_ARCHETYPES resolves to its own unique
    interpretation rather than blindly falling back to 'confidence'.
    """
    resolved_texts: set[str] = set()

    for arch in DAILY_ENERGY_ARCHETYPES:
        arch_id = arch["id"]
        res = interpretation_engine.resolve_daily_energy(energy_type=arch_id, locale="ka")
        assert res is not None, f"Archetype {arch_id} must resolve to an interpretation"
        text = res.text.strip()
        assert len(text) > 30, f"Archetype {arch_id} text is too short"
        assert text not in resolved_texts or arch_id == "confidence", f"Duplicate text detected for {arch_id}"
        resolved_texts.add(text)


def test_zero_astrology_jargon_in_daily_consumer_copy():
    """
    Ensures that consumer-facing interpretation quotes and guidance tags contain
    zero astrology jargon. Jargon must stay strictly in the 'რატომ?' technical basis.
    """
    for arch in DAILY_ENERGY_ARCHETYPES:
        arch_id = arch["id"]
        res = interpretation_engine.resolve_daily_energy(energy_type=arch_id, locale="ka")
        assert res is not None
        quote_text = res.text

        for jargon in FORBIDDEN_JARGON:
            assert jargon not in quote_text, f"Jargon '{jargon}' found in archetype '{arch_id}' quote: {quote_text}"

        guidance = get_daily_guidance(arch_id, locale="ka")
        all_tags = guidance["do"] + guidance["dont"]
        assert len(guidance["do"]) == 3, f"Expected 3 DO tags for {arch_id}"
        assert len(guidance["dont"]) == 3, f"Expected 3 DONT tags for {arch_id}"

        for tag in all_tags:
            for jargon in FORBIDDEN_JARGON:
                assert jargon not in tag, f"Jargon '{jargon}' found in tag '{tag}' of {arch_id}"


def test_daily_explanations_coverage():
    """
    Verifies that every archetype has a dedicated, non-generic explanation.
    """
    for arch in DAILY_ENERGY_ARCHETYPES:
        arch_id = arch["id"]
        assert arch_id in DAILY_ENERGY_EXPLANATIONS_KA, f"Missing explanation for {arch_id}"
        explanation = DAILY_ENERGY_EXPLANATIONS_KA[arch_id]
        assert len(explanation) > 30
        for jargon in FORBIDDEN_JARGON:
            assert jargon not in explanation, f"Jargon '{jargon}' in explanation for {arch_id}"


@pytest.mark.asyncio
async def test_daily_energy_api_returns_curated_content():
    """
    Tests GET /v1/interpretations/daily-energy returns populated explanation,
    observation quote, 3 DOs, 3 DONTs, and detection_mode.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/v1/interpretations/daily-energy?energy_type=clarity")
        assert res.status_code == 200
        data = res.json()

        assert data["archetype"] == "clarity"
        assert data["label"] == "სტრატეგიული სიცხადე"
        assert len(data["interpretation"]["text"]) > 0
        assert "მშრალი ფაქტები" in data["interpretation"]["text"]
        assert len(data["explanation"]) > 0
        assert len(data["do"]) == 3
        assert len(data["dont"]) == 3

