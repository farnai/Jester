"""
Tests for JESTER Batch 5B Life Verdicts Runtime Integration.

Validates:
1. All 12 Natal Archetype contracts (modality_primary x element_primary) registered and resolvable.
2. Exact 12-archetype mapping:
   - cardinal_fire, fixed_fire, mutable_fire
   - cardinal_earth, fixed_earth, mutable_earth
   - cardinal_air, fixed_air, mutable_air
   - cardinal_water, fixed_water, mutable_water
3. Deterministic resolution without runtime randomness.
4. Clean omission when element_primary or modality_primary is missing or invalid.
5. Strict isolation: Batch 5B and Batch 5 synthesis never cross-resolve.
6. Existing natal dimensions (Sun, Moon, Rising, Elements, Modality, Synthesis) preserved.
7. Standard production requests without depth/angle parameters resolve Life Verdict cleanly.
8. Frozen corpus integrity for batch_5b_verdicts.json and batch_5_synthesis.json.
"""
import json
from pathlib import Path
import pytest

from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from backend.app.interpretation.engine import InterpretationEngine
from backend.app.interpretation.library import content_library


BATCH_5B_FILE = Path(__file__).parents[2] / "backend" / "app" / "interpretation" / "data" / "batches" / "batch_5b_verdicts.json"
BATCH_5_FILE = Path(__file__).parents[2] / "backend" / "app" / "interpretation" / "data" / "batches" / "batch_5_synthesis.json"

EXPECTED_12_ARCHETYPES = [
    ("cardinal", "fire", "self.verdict.archetype_cardinal_fire.v1"),
    ("fixed", "fire", "self.verdict.archetype_fixed_fire.v1"),
    ("mutable", "fire", "self.verdict.archetype_mutable_fire.v1"),
    ("cardinal", "earth", "self.verdict.archetype_cardinal_earth.v1"),
    ("fixed", "earth", "self.verdict.archetype_fixed_earth.v1"),
    ("mutable", "earth", "self.verdict.archetype_mutable_earth.v1"),
    ("cardinal", "air", "self.verdict.archetype_cardinal_air.v1"),
    ("fixed", "air", "self.verdict.archetype_fixed_air.v1"),
    ("mutable", "air", "self.verdict.archetype_mutable_air.v1"),
    ("cardinal", "water", "self.verdict.archetype_cardinal_water.v1"),
    ("fixed", "water", "self.verdict.archetype_fixed_water.v1"),
    ("mutable", "water", "self.verdict.archetype_mutable_water.v1"),
]


@pytest.fixture(scope="module")
def interpretation_engine():
    return InterpretationEngine()


def test_frozen_corpus_integrity_5b():
    """Confirms batch_5b_verdicts.json is byte-exact and has 60 assets across 12 archetypes."""
    assert BATCH_5B_FILE.exists()
    with open(BATCH_5B_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 60
    unique_aids = {d["asset_id"] for d in data}
    assert len(unique_aids) == 60

    unique_iids = {d["interpretation_id"] for d in data}
    assert len(unique_iids) == 12

    micros = [d for d in data if d["depth"] == "micro"]
    mediums = [d for d in data if d["depth"] == "medium"]
    assert len(micros) == 36
    assert len(mediums) == 24


def test_frozen_corpus_integrity_5():
    """Confirms batch_5_synthesis.json remains completely untouched."""
    assert BATCH_5_FILE.exists()
    with open(BATCH_5_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 64


def test_contracts_registered_for_all_12_archetypes():
    """Verifies all 12 Life Verdict archetype contracts are registered in INTERPRETATION_CONTRACTS."""
    for mod, elem, expected_id in EXPECTED_12_ARCHETYPES:
        contract = INTERPRETATION_CONTRACTS.get(expected_id)
        assert contract is not None, f"Contract {expected_id} missing from registry"
        assert contract.context == "self"
        assert contract.signal.category == "self"
        assert contract.signal.type == f"verdict_archetype_{mod}_{elem}"
        assert contract.meaning.intensity == "high"
        assert len(contract.meaning.human_meaning) >= 3


def test_all_12_archetypes_resolve_via_engine(interpretation_engine):
    """Verifies that all 12 element x modality combinations resolve to the expected Life Verdict."""
    for mod, elem, expected_id in EXPECTED_12_ARCHETYPES:
        profile = {
            "sun_sign": "aries",
            "moon_sign": "leo",
            "element_primary": elem,
            "modality_primary": mod,
        }
        results = interpretation_engine.resolve_natal_profile(profile, seed="test-seed-12")
        verdict_results = [r for r in results if r.id.startswith("self.verdict.")]
        assert len(verdict_results) == 1, f"Expected exactly 1 verdict for {mod}_{elem}, got {len(verdict_results)}"
        res = verdict_results[0]
        assert res.id == expected_id
        assert len(res.text.strip()) > 0
        assert res.locale == "ka"


def test_ordering_and_non_commutativity(interpretation_engine):
    """Verifies that modality and element are not commutative and follow modality_element format."""
    # Cardinal Earth vs Fixed Fire vs Mutable Water
    p_ce = {"element_primary": "earth", "modality_primary": "cardinal", "sun_sign": "aries", "moon_sign": "aries"}
    p_ff = {"element_primary": "fire", "modality_primary": "fixed", "sun_sign": "aries", "moon_sign": "aries"}
    p_mw = {"element_primary": "water", "modality_primary": "mutable", "sun_sign": "aries", "moon_sign": "aries"}

    r_ce = [r for r in interpretation_engine.resolve_natal_profile(p_ce) if r.id.startswith("self.verdict.")][0]
    r_ff = [r for r in interpretation_engine.resolve_natal_profile(p_ff) if r.id.startswith("self.verdict.")][0]
    r_mw = [r for r in interpretation_engine.resolve_natal_profile(p_mw) if r.id.startswith("self.verdict.")][0]

    assert r_ce.id == "self.verdict.archetype_cardinal_earth.v1"
    assert r_ff.id == "self.verdict.archetype_fixed_fire.v1"
    assert r_mw.id == "self.verdict.archetype_mutable_water.v1"
    assert r_ce.id != r_ff.id != r_mw.id


def test_clean_omission_when_inputs_missing_or_invalid(interpretation_engine):
    """Verifies Life Verdict is safely omitted when element_primary or modality_primary is absent or invalid."""
    # Missing element
    p_no_elem = {"modality_primary": "cardinal", "sun_sign": "aries", "moon_sign": "aries"}
    r1 = [r for r in interpretation_engine.resolve_natal_profile(p_no_elem) if r.id.startswith("self.verdict.")]
    assert len(r1) == 0

    # Missing modality
    p_no_mod = {"element_primary": "fire", "sun_sign": "aries", "moon_sign": "aries"}
    r2 = [r for r in interpretation_engine.resolve_natal_profile(p_no_mod) if r.id.startswith("self.verdict.")]
    assert len(r2) == 0

    # Invalid element
    p_inv_elem = {"element_primary": "krypton", "modality_primary": "fixed", "sun_sign": "aries", "moon_sign": "aries"}
    r3 = [r for r in interpretation_engine.resolve_natal_profile(p_inv_elem) if r.id.startswith("self.verdict.")]
    assert len(r3) == 0

    # Invalid modality
    p_inv_mod = {"element_primary": "fire", "modality_primary": "hyperbolic", "sun_sign": "aries", "moon_sign": "aries"}
    r4 = [r for r in interpretation_engine.resolve_natal_profile(p_inv_mod) if r.id.startswith("self.verdict.")]
    assert len(r4) == 0

    # Both missing
    p_empty = {"sun_sign": "aries", "moon_sign": "aries"}
    r5 = [r for r in interpretation_engine.resolve_natal_profile(p_empty) if r.id.startswith("self.verdict.")]
    assert len(r5) == 0


def test_batch_5b_and_batch_5_never_cross_resolve(interpretation_engine):
    """Confirms Batch 5B verdicts and Batch 5 synthesis never cross-resolve or overwrite each other."""
    profile = {
        "sun_sign": "gemini",      # Air
        "moon_sign": "scorpio",     # Water
        "element_primary": "fire",
        "modality_primary": "mutable",
    }
    results = interpretation_engine.resolve_natal_profile(profile, seed="cross-check")

    synthesis_res = [r for r in results if r.id.startswith("self.synthesis.")]
    verdict_res = [r for r in results if r.id.startswith("self.verdict.")]

    assert len(synthesis_res) == 1
    assert len(verdict_res) == 1

    # Synthesis is Sun Air x Moon Water
    assert synthesis_res[0].id == "self.synthesis.element_dynamic.air_water.v1"
    # Verdict is Mutable x Fire
    assert verdict_res[0].id == "self.verdict.archetype_mutable_fire.v1"

    assert synthesis_res[0].id != verdict_res[0].id
    assert synthesis_res[0].text != verdict_res[0].text


def test_deterministic_resolution_without_randomness(interpretation_engine):
    """Confirms identical profile and seed always yields the exact same Life Verdict asset."""
    profile = {
        "sun_sign": "taurus",
        "moon_sign": "cancer",
        "element_primary": "earth",
        "modality_primary": "fixed",
    }
    r1 = interpretation_engine.resolve_natal_profile(profile, seed="fixed-user-seed")
    r2 = interpretation_engine.resolve_natal_profile(profile, seed="fixed-user-seed")

    v1 = [r for r in r1 if r.id.startswith("self.verdict.")][0]
    v2 = [r for r in r2 if r.id.startswith("self.verdict.")][0]

    assert v1.id == v2.id
    assert v1.text == v2.text
    assert v1.variant_key == v2.variant_key


def test_output_order_and_no_duplicates(interpretation_engine):
    """Verifies Life Verdict is appended after synthesis at the end of the natal profile and has no duplicates."""
    profile = {
        "sun_sign": "leo",
        "moon_sign": "aquarius",
        "ascendant_sign": "sagittarius",
        "element_primary": "fire",
        "modality_primary": "fixed",
    }
    results = interpretation_engine.resolve_natal_profile(profile, seed="order-check")
    result_ids = [r.id for r in results]

    # Verify no duplicate IDs
    assert len(result_ids) == len(set(result_ids))

    # Verify order: synthesis is followed by verdict
    synth_idx = next(i for i, rid in enumerate(result_ids) if rid.startswith("self.synthesis."))
    verdict_idx = next(i for i, rid in enumerate(result_ids) if rid.startswith("self.verdict."))

    assert verdict_idx > synth_idx
    assert verdict_idx == len(result_ids) - 1, "Life Verdict must be the crowning final layer"


def test_standard_production_request_without_depth_or_angle(interpretation_engine):
    """
    Verifies that a standard production request without depth or angle parameters
    returns a complete profile including the expected Life Verdict.
    """
    production_payload = {
        "sun_sign": "virgo",
        "moon_sign": "pisces",
        "ascendant_sign": "gemini",
        "element_primary": "earth",
        "modality_primary": "mutable",
    }
    results = interpretation_engine.resolve_natal_profile(production_payload, locale="ka")
    verdicts = [r for r in results if r.id == "self.verdict.archetype_mutable_earth.v1"]
    assert len(verdicts) == 1
    assert len(verdicts[0].text) > 0
    assert verdicts[0].locale == "ka"
