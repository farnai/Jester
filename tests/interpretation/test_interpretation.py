"""
Comprehensive test suite for JESTER V1 Interpretation Contract and JESTER Voice Content Layer.
Validates all 13 core requirements:
1. Deterministic signal -> interpretation mapping
2. Stable interpretation IDs
3. AI draft fallback
4. Approved copy priority
5. Missing final copy fallback
6. No astrology-engine dependency on copy text
7. Frontend-safe API response
8. Unsupported signals do not generate invented interpretations
9. Deterministic output for same input
10. Content replacement does not change astrology calculations
11. Versioned interpretations remain resolvable
12. Georgian content returned correctly
13. No consumer-facing astrology jargon in draft library
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.compatibility.synastry import NatalInputPayload, SynastryEngine
from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from backend.app.interpretation.engine import InterpretationEngine, interpretation_engine
from backend.app.interpretation.jester import (
    assert_no_jargon,
    find_astrology_jargon,
    validate_no_jargon,
)
from backend.app.interpretation.library import INITIAL_GEORGIAN_DRAFTS, ContentLibrary
from backend.app.interpretation.models import ContentUpdatePayload, ResolvedInterpretation
from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt


# ---------------------------------------------------------------------------
# Requirement 1: Deterministic signal -> interpretation mapping
# ---------------------------------------------------------------------------
def test_deterministic_signal_to_interpretation_mapping():
    engine = InterpretationEngine()

    # Venus-Mars aspect deterministically maps to strong_chemistry
    interp_id = engine.signal_to_interpretation_id("venus_conjunction_mars")
    assert interp_id == "relationship.attraction.strong_chemistry.v1"

    # Sun-Moon harmony deterministically maps to emotional_resonance
    interp_id_sun_moon = engine.signal_to_interpretation_id("sun_trine_moon")
    assert interp_id_sun_moon == "relationship.harmony.emotional_resonance.v1"

    # Mercury harmony maps to intellectual_flow
    interp_id_mercury = engine.signal_to_interpretation_id("mercury_trine_mercury")
    assert interp_id_mercury == "relationship.communication.intellectual_flow.v1"


# ---------------------------------------------------------------------------
# Requirement 2: Stable interpretation IDs (semantic, not planetary coordinates)
# ---------------------------------------------------------------------------
def test_stable_semantic_interpretation_ids():
    engine = InterpretationEngine()
    contract = engine.get_contract("relationship.attraction.strong_chemistry.v1")
    assert contract is not None
    assert contract.interpretation_id == "relationship.attraction.strong_chemistry.v1"
    assert contract.context == "relationship"
    assert contract.meaning.type == "strong_chemistry"
    assert contract.meaning.intensity == "high"

    # Ensure stable semantic ID follows category.theme.specific.version pattern
    parts = contract.interpretation_id.split(".")
    assert len(parts) >= 4
    assert parts[0] in {"relationship", "daily_energy", "self"}


# ---------------------------------------------------------------------------
# Requirement 3: AI draft fallback (when copywriter hasn't reviewed)
# ---------------------------------------------------------------------------
def test_ai_draft_fallback():
    lib = ContentLibrary()
    interp_id = "relationship.attraction.strong_chemistry.v1"

    # Ensure final is unreviewed
    lib.reset_to_draft(interp_id)
    rec = lib.get_record(interp_id)
    assert rec.final.status == "not_reviewed"

    # Resolve text should return draft copy with status 'ai_draft'
    resolved = lib.resolve_text(interp_id)
    assert resolved is not None
    assert resolved.content_status == "ai_draft"
    assert "ერთ ოთახში რომ შემოდიხართ" in resolved.text
    assert resolved.language == "ka"


# ---------------------------------------------------------------------------
# Requirement 4: Approved copy priority (copywriter takes precedence)
# ---------------------------------------------------------------------------
def test_approved_copy_priority():
    lib = ContentLibrary()
    interp_id = "relationship.attraction.strong_chemistry.v1"

    # Update with approved copywriter text
    copywriter_text = "ეს არის დამტკიცებული კოპირაიტერის ტექსტი."
    lib.update_approved_copy(
        interpretation_id=interp_id,
        text=copywriter_text,
        author="lead_copywriter",
    )

    resolved = lib.resolve_text(interp_id)
    assert resolved is not None
    assert resolved.content_status == "approved"
    assert resolved.text == copywriter_text

    # Clean up by resetting to draft
    lib.reset_to_draft(interp_id)
    assert lib.resolve_text(interp_id).content_status == "ai_draft"


# ---------------------------------------------------------------------------
# Requirement 5: Missing final copy fallback (empty/whitespace final copy)
# ---------------------------------------------------------------------------
def test_missing_final_copy_fallback():
    lib = ContentLibrary()
    interp_id = "relationship.harmony.emotional_resonance.v1"

    # Update with empty text but marked approved
    rec = lib.get_record(interp_id)
    rec.final.status = "approved"
    rec.final.text = "   "

    # Should fall back cleanly to draft
    resolved = lib.resolve_text(interp_id)
    assert resolved is not None
    assert resolved.content_status == "ai_draft"
    assert len(resolved.text) > 0


def make_test_payload(
    user_id: uuid.UUID | None = None,
    precision: str = "exact",
    **planets: float,
) -> NatalInputPayload:
    default_planets = {
        "sun": 0.0,
        "moon": 30.0,
        "mercury": 15.0,
        "venus": 45.0,
        "mars": 60.0,
        "jupiter": 90.0,
        "saturn": 120.0,
        "uranus": 150.0,
        "neptune": 180.0,
        "pluto": 210.0,
    }
    default_planets.update(planets)
    return NatalInputPayload(
        user_id=user_id or uuid.uuid4(),
        birth_data_version=1,
        birth_time_precision=precision,
        planet_longitudes=default_planets,
        ascendant_longitude=0.0,
    )


# ---------------------------------------------------------------------------
# Requirement 6: No astrology-engine dependency on copy text
# ---------------------------------------------------------------------------
def test_no_astrology_engine_dependency_on_copy():
    syn_engine = SynastryEngine()
    payload_a = make_test_payload(sun=0.0, moon=120.0, venus=45.0, mars=60.0)
    payload_b = make_test_payload(sun=120.0, moon=0.0, venus=45.0, mars=45.0)

    # Calculate baseline
    result_1 = syn_engine.calculate(payload_a, payload_b)

    # Change copy in the content library
    lib = ContentLibrary()
    lib.update_approved_copy(
        "relationship.attraction.strong_chemistry.v1",
        "ახალი დამტკიცებული ტექსტი, რომელიც ძრავს არ ეხება.",
    )

    # Calculate again
    result_2 = syn_engine.calculate(payload_a, payload_b)

    # Astrology math, score, subscores, and aspect evidence must be 100% identical
    assert result_1.score == result_2.score
    assert result_1.dimensions == result_2.dimensions
    assert len(result_1.signals) == len(result_2.signals)
    assert len(result_1.evidence_trace) == len(result_2.evidence_trace)

    # Reset library
    lib.reset_to_draft("relationship.attraction.strong_chemistry.v1")


# ---------------------------------------------------------------------------
# Requirement 7: Frontend-safe API response
# ---------------------------------------------------------------------------
def test_frontend_safe_api_response():
    engine = InterpretationEngine()
    signal = {"type": "venus_conjunction_mars", "strength": "strong"}
    resolved = engine.resolve_signal(signal)

    assert isinstance(resolved, ResolvedInterpretation)
    dump = resolved.model_dump()
    assert "id" in dump
    assert "text" in dump
    assert "content_status" in dump
    assert "language" in dump
    # Ready for direct rendering in UI without any frontend calculations
    assert isinstance(dump["text"], str) and len(dump["text"]) > 0


# ---------------------------------------------------------------------------
# Requirement 8: Unsupported signals do not generate invented interpretations
# ---------------------------------------------------------------------------
def test_unsupported_signals_do_not_generate_invented_interpretations():
    engine = InterpretationEngine()

    # Unrecognized invented signal
    hallucinated_signal = {"type": "pluto_conjunct_alien_comet", "strength": "extreme"}
    resolved = engine.resolve_signal(hallucinated_signal)
    assert resolved is None

    # Empty signal
    empty_signal = {"type": ""}
    assert engine.resolve_signal(empty_signal) is None


# ---------------------------------------------------------------------------
# Requirement 9: Deterministic output for same input
# ---------------------------------------------------------------------------
def test_deterministic_output_for_same_input():
    engine = InterpretationEngine()
    signal = {"type": "sun_trine_moon"}

    res1 = engine.resolve_signal(signal)
    res2 = engine.resolve_signal(signal)
    res3 = engine.resolve_signal(signal)

    assert res1 == res2 == res3
    assert res1.id == "relationship.harmony.emotional_resonance.v1"
    assert res1.text == res2.text


# ---------------------------------------------------------------------------
# Requirement 10: Content replacement does not change astrology calculations
# ---------------------------------------------------------------------------
def test_content_replacement_does_not_change_astrology_calculations():
    syn_engine = SynastryEngine()
    interp_engine = InterpretationEngine()

    payload_a = make_test_payload(sun=0.0, moon=60.0, venus=90.0, mars=90.0)
    payload_b = make_test_payload(sun=60.0, moon=0.0, venus=90.0, mars=90.0)

    before_calc = syn_engine.calculate(payload_a, payload_b)

    # Mutate all library texts to test copy
    for record in interp_engine.library.list_records():
        interp_engine.library.update_approved_copy(
            record.interpretation_id,
            "სრულიად შეცვლილი ტექსტი კოპირაიტერის მიერ.",
        )

    after_calc = syn_engine.calculate(payload_a, payload_b)

    assert before_calc.score == after_calc.score
    assert before_calc.dimensions == after_calc.dimensions

    # Cleanup
    for record in interp_engine.library.list_records():
        interp_engine.library.reset_to_draft(record.interpretation_id)


# ---------------------------------------------------------------------------
# Requirement 11: Versioned interpretations remain resolvable
# ---------------------------------------------------------------------------
def test_versioned_interpretations_remain_resolvable():
    engine = InterpretationEngine()

    # Both v1 and v2 contracts exist and resolve
    contract_v1 = engine.get_contract("relationship.attraction.strong_chemistry.v1")
    contract_v2 = engine.get_contract("relationship.attraction.strong_chemistry.v2")
    assert contract_v1 is not None
    assert contract_v2 is not None

    resolved_v1 = engine.library.resolve_text("relationship.attraction.strong_chemistry.v1")
    resolved_v2 = engine.library.resolve_text("relationship.attraction.strong_chemistry.v2")
    assert resolved_v1 is not None
    assert resolved_v2 is not None

    # Version fallback: hypothetical v3 gracefully falls back to v1
    resolved_v3 = engine.library.resolve_text("relationship.attraction.strong_chemistry.v3")
    assert resolved_v3 is not None
    assert "ერთ ოთახში რომ შემოდიხართ" in resolved_v3.text


# ---------------------------------------------------------------------------
# Requirement 12: Georgian content returned correctly
# ---------------------------------------------------------------------------
def test_georgian_content_returned_correctly():
    engine = InterpretationEngine()
    resolved = engine.library.resolve_text("relationship.attraction.strong_chemistry.v1")
    assert resolved is not None
    assert resolved.language == "ka"

    # Verify specific expected Georgian string from spec
    expected_sample = "ერთ ოთახში რომ შემოდიხართ, ჰაერი ისე მძიმდება, თითქოს ვიღაცამ კონდიციონერი გამორთო და დრამა ჩართო. ნაპერწკლები კარგია, მაგრამ ხანძარსაწინააღმდეგო სისტემა თუ არ მუშაობს, მალე ორივე ერთად დაიფერფლებით."
    assert resolved.text == expected_sample

    # Daily energy Georgian string
    daily_res = engine.resolve_daily_energy("creativity")
    assert daily_res is not None
    assert "ახალი ხედვა" in daily_res.text

    daily_focus = engine.resolve_daily_energy("focus")
    assert daily_focus is not None
    assert "იდეები" in daily_focus.text



# ---------------------------------------------------------------------------
# Requirement 13: No consumer-facing astrology jargon in draft library
# ---------------------------------------------------------------------------
def test_no_astrology_jargon_in_draft_library():
    """
    Scans every single registered draft in INITIAL_GEORGIAN_DRAFTS to guarantee
    zero consumer-facing astrology jargon (conjunction, opposition, trine, etc.).
    """
    for interp_id, draft_text in INITIAL_GEORGIAN_DRAFTS.items():
        jargon = find_astrology_jargon(draft_text)
        assert len(jargon) == 0, f"Jargon '{jargon}' found in draft '{interp_id}': {draft_text}"
        assert validate_no_jargon(draft_text) is True
        assert_no_jargon(draft_text)


# ---------------------------------------------------------------------------
# Integration: Deep Analysis Structured Pipeline
# ---------------------------------------------------------------------------
def test_deep_analysis_payload_builder():
    engine = InterpretationEngine()
    signals = [
        {
            "type": "venus_conjunction_mars",
            "category": "attraction",
            "strength": "strong",
            "source_aspects": ["venus_conjunction_mars 1.2 deg"],
        },
        {
            "type": "sun_trine_moon",
            "category": "harmony",
            "strength": "strong",
            "source_aspects": ["sun_trine_moon 0.8 deg"],
        },
    ]

    payload = engine.build_deep_analysis_payload(
        score=92.5,
        signals=signals,
        confidence=1.0,
    )

    assert payload.overall_score == 92.5
    assert payload.primary_interpretation.id == "relationship.attraction.strong_chemistry.v1"
    assert len(payload.blocks) == 2
    assert payload.blocks[0].dimension == "attraction"
    assert payload.blocks[0].evidence_aspects == ["venus_conjunction_mars 1.2 deg"]
    assert payload.blocks[1].dimension == "harmony"


# ---------------------------------------------------------------------------
# API Endpoints Integration Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_interpretations_api_flow():
    user_id = str(uuid.uuid4())
    copywriter_id = str(uuid.uuid4())

    # Regular consumer user token
    user_token = generate_test_jwt(user_id=user_id, email="user@jester.app", role="authenticated")
    # Authorized copywriter token
    copywriter_token = generate_test_jwt(
        user_id=copywriter_id,
        email="copywriter@jester.app",
        role="copywriter",
        app_metadata={"role": "copywriter"},
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. List interpretations (accessible to regular users)
        res = await ac.get("/v1/interpretations", headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
        records = res.json()
        assert len(records) > 0
        assert any(r["interpretation_id"] == "relationship.attraction.strong_chemistry.v1" for r in records)

        # 2. Get specific interpretation (accessible to regular users)
        res = await ac.get(
            "/v1/interpretations/relationship.attraction.strong_chemistry.v1",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert res.status_code == 200
        detail = res.json()
        assert detail["contract"]["interpretation_id"] == "relationship.attraction.strong_chemistry.v1"
        assert detail["resolved"]["content_status"] == "ai_draft"

        # 3. Security check: regular user CANNOT update copywriter copy (403 Forbidden)
        new_copy = "ახალი, ოფიციალურად დამტკიცებული კოპირაითი."
        unauth_res = await ac.patch(
            "/v1/interpretations/relationship.attraction.strong_chemistry.v1/copy",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"text": new_copy, "status": "approved", "author": "attacker"},
        )
        assert unauth_res.status_code == 403

        # 4. Security check: regular user CANNOT reset copy (403 Forbidden)
        unauth_reset = await ac.post(
            "/v1/interpretations/relationship.attraction.strong_chemistry.v1/reset",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert unauth_reset.status_code == 403

        # 5. Authorized copywriter CAN update copy
        res = await ac.patch(
            "/v1/interpretations/relationship.attraction.strong_chemistry.v1/copy",
            headers={"Authorization": f"Bearer {copywriter_token}"},
            json={"text": new_copy, "status": "approved", "author": "senior_editor"},
        )
        assert res.status_code == 200
        assert res.json()["final"]["text"] == new_copy
        assert res.json()["final"]["status"] == "approved"

        # Verify resolution now returns approved copy
        res = await ac.get(
            "/v1/interpretations/relationship.attraction.strong_chemistry.v1",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert res.json()["resolved"]["content_status"] == "approved"
        assert res.json()["resolved"]["text"] == new_copy

        # 6. Authorized copywriter CAN reset back to draft
        res = await ac.post(
            "/v1/interpretations/relationship.attraction.strong_chemistry.v1/reset",
            headers={"Authorization": f"Bearer {copywriter_token}"},
        )
        assert res.status_code == 200
        assert res.json()["final"]["status"] == "not_reviewed"

        # 7. Resolve signal endpoint (accessible to regular users)
        res = await ac.post(
            "/v1/interpretations/resolve-signal",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"type": "sun_trine_moon", "strength": "strong"},
        )
        assert res.status_code == 200
        assert res.json()["interpretation"]["id"] == "relationship.harmony.emotional_resonance.v1"

        # 8. Resolve unknown signal returns 404
        res = await ac.post(
            "/v1/interpretations/resolve-signal",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"type": "totally_invented_signal"},
        )
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_copywriter_role_matrix_security():
    """
    Verifies that only authorized roles (copywriter, admin, service_role) can mutate copy,
    while anonymous requests return 401 and ordinary users return 403.
    """
    interp_id = "relationship.harmony.core_harmony.v1"
    valid_patch = {"text": "ტესტი ადმინის მიერ.", "status": "approved", "author": "tester"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Anonymous request -> 401
        res_anon = await ac.patch(f"/v1/interpretations/{interp_id}/copy", json=valid_patch)
        assert res_anon.status_code == 401

        # 2. Regular user (role: authenticated) -> 403
        reg_token = generate_test_jwt(role="authenticated")
        res_reg = await ac.patch(
            f"/v1/interpretations/{interp_id}/copy",
            headers={"Authorization": f"Bearer {reg_token}"},
            json=valid_patch,
        )
        assert res_reg.status_code == 403

        # 3. Admin user in role claim -> 200
        admin_token = generate_test_jwt(role="admin")
        res_admin = await ac.patch(
            f"/v1/interpretations/{interp_id}/copy",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=valid_patch,
        )
        assert res_admin.status_code == 200

        # 4. Service role -> 200
        service_token = generate_test_jwt(role="service_role")
        res_srv = await ac.post(
            f"/v1/interpretations/{interp_id}/reset",
            headers={"Authorization": f"Bearer {service_token}"},
        )
        assert res_srv.status_code == 200

        # 5. Copywriter via app_metadata -> 200
        meta_token = generate_test_jwt(role="authenticated", app_metadata={"role": "copywriter"})
        res_meta = await ac.patch(
            f"/v1/interpretations/{interp_id}/copy",
            headers={"Authorization": f"Bearer {meta_token}"},
            json=valid_patch,
        )
        assert res_meta.status_code == 200

        # Clean up
        await ac.post(
            f"/v1/interpretations/{interp_id}/reset",
            headers={"Authorization": f"Bearer {meta_token}"},
        )
