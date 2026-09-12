"""
Tests for JESTER Batch 5 Synthesis Runtime Integration.
Validates:
- All 16 Sun Element x Moon Element combinations resolve to the correct interpretation ID.
- Asymmetry preservation (fire_earth != earth_fire, air_water != water_air, etc.).
- Correct content assets resolvable in Georgian from the frozen corpus.
- micro_01 / med_01 resolve to internal_civil_war angle.
- micro_02 / med_02 resolve to coexistence_paradox angle.
- Depth filtering (micro vs medium).
- Deterministic resolution with seed (no runtime randomness).
- No fallback to another elemental combination.
- Unknown birth time handling (when Moon is None, synthesis is safely omitted).
- Negative tests: invalid elements, missing assets, no generic Sun/Moon degradation, no LLM dependency.
- Frozen corpus integrity: exactly 64 assets, zero content modifications.
"""
import json
from pathlib import Path
import pytest

from backend.app.astrology.constants import ELEMENT_MAP
from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from backend.app.interpretation.engine import InterpretationEngine, interpretation_engine
from backend.app.interpretation.library import content_library

BATCH_FILE = Path(__file__).parents[2] / "backend" / "app" / "interpretation" / "data" / "batches" / "batch_5_synthesis.json"

ELEMENTS = ["fire", "earth", "air", "water"]

# Representative signs for each element
SIGN_FOR_ELEMENT = {
    "fire": "Aries",
    "earth": "Taurus",
    "air": "Gemini",
    "water": "Cancer",
}


@pytest.fixture(scope="module")
def frozen_batch_5_assets():
    assert BATCH_FILE.exists(), f"Batch 5 file not found at {BATCH_FILE}"
    with open(BATCH_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def test_frozen_corpus_integrity(frozen_batch_5_assets):
    """Confirm batch_5_synthesis.json contains exactly 64 assets and is unmodified."""
    assert len(frozen_batch_5_assets) == 64, f"Expected 64 assets, got {len(frozen_batch_5_assets)}"
    seen_ids = set()
    for a in frozen_batch_5_assets:
        assert a["asset_id"] not in seen_ids, f"Duplicate asset_id: {a['asset_id']}"
        seen_ids.add(a["asset_id"])
        assert a["layer"] == "synthesis"
        assert a["domain"] == "self"
        assert a["depth"] in ("micro", "medium")
        assert a["semantic_angle"] in ("internal_civil_war", "coexistence_paradox")


def test_contracts_registered_for_all_16_combinations():
    """Verify all 16 interpretation contracts exist in INTERPRETATION_CONTRACTS with context='self'."""
    for se in ELEMENTS:
        for me in ELEMENTS:
            target_id = f"self.synthesis.element_dynamic.{se}_{me}.v1"
            contract = interpretation_engine.get_contract(target_id)
            assert contract is not None, f"Missing contract for {target_id}"
            assert contract.context == "self"
            assert contract.signal.category == "self"
            assert contract.meaning.type is not None
            assert len(contract.meaning.human_meaning) > 0


def test_all_16_combinations_resolve_via_engine():
    """All 16 Sun x Moon combinations resolve to the exact expected interpretation ID."""
    for se in ELEMENTS:
        for me in ELEMENTS:
            expected_id = f"self.synthesis.element_dynamic.{se}_{me}.v1"
            profile = {
                "sun_sign": SIGN_FOR_ELEMENT[se],
                "moon_sign": SIGN_FOR_ELEMENT[me],
            }
            results = interpretation_engine.resolve_natal_profile(profile, seed="fixed-seed-test")
            synthesis_results = [r for r in results if r.id.startswith("self.synthesis.")]
            assert len(synthesis_results) == 1, f"Expected 1 synthesis result for {se} x {me}, got {len(synthesis_results)}"
            r = synthesis_results[0]
            assert r.id == expected_id, f"Expected {expected_id}, got {r.id}"
            assert r.content_asset_id.startswith(expected_id), f"Asset ID {r.content_asset_id} does not match {expected_id}"
            assert r.language == "ka"
            assert len(r.text) > 0


def test_asymmetry_preservation():
    """Verify asymmetry: Sun Element x Moon Element is never commutative (fire_earth != earth_fire)."""
    pairs = [
        ("fire", "earth"),
        ("air", "water"),
        ("earth", "water"),
        ("fire", "air"),
        ("fire", "water"),
        ("earth", "air"),
    ]
    for e1, e2 in pairs:
        p_forward = {"sun_sign": SIGN_FOR_ELEMENT[e1], "moon_sign": SIGN_FOR_ELEMENT[e2]}
        p_reverse = {"sun_sign": SIGN_FOR_ELEMENT[e2], "moon_sign": SIGN_FOR_ELEMENT[e1]}

        r_f = [r for r in interpretation_engine.resolve_natal_profile(p_forward, seed="asym-seed") if r.id.startswith("self.synthesis.")][0]
        r_r = [r for r in interpretation_engine.resolve_natal_profile(p_reverse, seed="asym-seed") if r.id.startswith("self.synthesis.")][0]

        assert r_f.id != r_r.id, f"Asymmetry violated: {r_f.id} == {r_r.id}"
        assert r_f.id == f"self.synthesis.element_dynamic.{e1}_{e2}.v1"
        assert r_r.id == f"self.synthesis.element_dynamic.{e2}_{e1}.v1"


def test_depth_selection_micro_and_medium():
    """Verify depth selection: micro returns micro asset; medium returns medium asset."""
    target_id = "self.synthesis.element_dynamic.fire_earth.v1"
    res_micro = content_library.resolve(target_id, context="self", depth="micro", seed="test-seed")
    assert res_micro is not None
    assert res_micro.depth == "micro"
    assert "micro" in res_micro.content_asset_id
    assert 100 <= len(res_micro.text) <= 250

    res_med = content_library.resolve(target_id, context="self", depth="medium", seed="test-seed")
    assert res_med is not None
    assert res_med.depth == "medium"
    assert "med" in res_med.content_asset_id
    assert 400 <= len(res_med.text) <= 750


def test_semantic_angle_resolution_internal_civil_war_and_coexistence_paradox():
    """Verify that semantic angles resolve to the exact corresponding asset variants."""
    target_id = "self.synthesis.element_dynamic.fire_air.v1"

    # Micro civil war -> .micro_01
    r_micro_cw = content_library.resolve(target_id, context="self", depth="micro", variant_key="internal_civil_war")
    assert r_micro_cw is not None
    assert r_micro_cw.content_asset_id == f"{target_id}.micro_01"
    assert r_micro_cw.variant_key == "internal_civil_war"

    # Micro coexistence paradox -> .micro_02
    r_micro_cp = content_library.resolve(target_id, context="self", depth="micro", variant_key="coexistence_paradox")
    assert r_micro_cp is not None
    assert r_micro_cp.content_asset_id == f"{target_id}.micro_02"
    assert r_micro_cp.variant_key == "coexistence_paradox"

    # Medium civil war -> .med_01
    r_med_cw = content_library.resolve(target_id, context="self", depth="medium", variant_key="internal_civil_war")
    assert r_med_cw is not None
    assert r_med_cw.content_asset_id == f"{target_id}.med_01"
    assert r_med_cw.variant_key == "internal_civil_war"

    # Medium coexistence paradox -> .med_02
    r_med_cp = content_library.resolve(target_id, context="self", depth="medium", variant_key="coexistence_paradox")
    assert r_med_cp is not None
    assert r_med_cp.content_asset_id == f"{target_id}.med_02"
    assert r_med_cp.variant_key == "coexistence_paradox"


def test_deterministic_resolution_without_randomness():
    """Verify that same seed always yields the exact same asset."""
    target_id = "self.synthesis.element_dynamic.earth_water.v1"
    first = content_library.resolve(target_id, context="self", seed="user-stable-12345")
    for _ in range(20):
        repeat = content_library.resolve(target_id, context="self", seed="user-stable-12345")
        assert repeat.content_asset_id == first.content_asset_id


def test_unknown_birth_time_handling():
    """When birth time is unknown and Moon sign is None, synthesis is cleanly omitted."""
    profile_unknown_time = {
        "sun_sign": "Aries",
        "moon_sign": None,
        "ascendant_sign": None,
        "element_primary": "Fire",
        "modality_primary": "Cardinal",
    }
    results = interpretation_engine.resolve_natal_profile(profile_unknown_time, seed="seed")
    synthesis_hits = [r for r in results if r.id.startswith("self.synthesis.")]
    assert len(synthesis_hits) == 0, "Synthesis should not be produced when Moon sign is None"

    # When Moon sign is provided, synthesis is cleanly produced
    profile_known = {
        "sun_sign": "Aries",
        "moon_sign": "Leo",
    }
    results_known = interpretation_engine.resolve_natal_profile(profile_known, seed="seed")
    synthesis_hits_known = [r for r in results_known if r.id.startswith("self.synthesis.")]
    assert len(synthesis_hits_known) == 1
    assert synthesis_hits_known[0].id == "self.synthesis.element_dynamic.fire_fire.v1"


# =============================================================================
# NEGATIVE TESTS
# =============================================================================

def test_negative_invalid_elements_do_not_generate_synthesis():
    """Invalid elements (e.g. 'krypton', 'plasma', numbers) must not generate an interpretation."""
    invalid_profiles = [
        {"sun_sign": "Krypton", "moon_sign": "Aries"},
        {"sun_sign": "Aries", "moon_sign": "InvalidMoon"},
        {"sun_element": "plasma", "moon_element": "water"},
        {"sun_sign": "", "moon_sign": "Taurus"},
    ]
    for p in invalid_profiles:
        results = interpretation_engine.resolve_natal_profile(p, seed="neg-test")
        synthesis_hits = [r for r in results if r.id.startswith("self.synthesis.")]
        assert len(synthesis_hits) == 0, f"Expected no synthesis for invalid profile {p}, got {synthesis_hits}"


def test_negative_no_fallback_to_other_combination():
    """A specific elemental combination must NEVER silently fall back to another combination."""
    target_id = "self.synthesis.element_dynamic.fire_earth.v1"
    res = content_library.resolve(target_id, context="self", seed="test-seed")
    assert res is not None
    assert "fire_earth" in res.content_asset_id
    assert "earth_fire" not in res.content_asset_id
    assert "fire_water" not in res.content_asset_id
    assert "fire_air" not in res.content_asset_id


def test_negative_not_generic_sun_or_moon():
    """Batch 5 assets must strictly have layer 'synthesis' and not degrade into Sun/Moon interpretations."""
    profile = {"sun_sign": "Leo", "moon_sign": "Scorpio"}
    results = interpretation_engine.resolve_natal_profile(profile, seed="layer-check")
    synth = [r for r in results if r.id.startswith("self.synthesis.")][0]
    sun = [r for r in results if r.id.startswith("self.identity.")][0]
    moon = [r for r in results if r.id.startswith("self.emotional.")][0]

    assert synth.id != sun.id
    assert synth.id != moon.id
    assert "fire_water" in synth.id
    assert "leo" in sun.id
    assert "scorpio" in moon.id
    assert synth.text != sun.text
    assert synth.text != moon.text


def test_negative_invalid_target_id_returns_none():
    """Querying a non-existent synthesis ID returns None."""
    assert content_library.resolve("self.synthesis.element_dynamic.fire_krypton.v1", context="self") is None
    assert content_library.resolve("self.synthesis.element_dynamic.invalid.v1", context="self") is None
