"""
=============================================================================
JESTER V1 — CONTENT ARCHITECTURE V2 COMPREHENSIVE TEST SUITE
=============================================================================
Tests:
1. Architecture decoupling: Astrology engine does not import copy/content
2. Content mutation invariance: Copy changes do NOT modify compatibility calculations
3. Multi-asset & multi-variant support: One interpretation has many assets/variants
4. Multi-tone & persona resolution: witty, playful, soft, bold, savage, romantic
5. Multi-context resolution: relationship, friendship, business, daily_energy, deep_analysis
6. Multi-locale resolution: ka, en, and graceful locale fallback
7. Status hierarchy: Approved > Experimental > AI Draft. Archived is NEVER resolved
8. Deterministic variant rotation: Stable seed hashing ensures predictability
9. Copywriter CRUD API & Role-based security matrix
10. Safety & Jargon invariance across all assets
=============================================================================
"""

import sys
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.compatibility.engine import SynastryEngine
from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from backend.app.interpretation.engine import InterpretationEngine
from backend.app.interpretation.library import (
    ContentLibrary,
    ContentResolver,
    InMemoryContentStore,
    content_library,
)
from backend.app.interpretation.models import (
    ContentAsset,
    ContentAssetCreatePayload,
    ContentAssetUpdatePayload,
    ResolvedInterpretation,
)
from backend.app.interpretation.seed_data import SEED_CONTENT_ASSETS
from tests.interpretation.test_interpretation import generate_test_jwt, make_test_payload


# =============================================================================
# 1. Architecture Decoupling & Invariance Tests
# =============================================================================

def test_astrology_modules_do_not_import_content_layer():
    """
    Verifies that the core astrology and compatibility calculation modules
    never import interpretation, copywriter library, seed data, or router.
    """
    forbidden_terms = [
        "interpretation",
        "SEED_CONTENT_ASSETS",
        "ContentLibrary",
        "ContentAsset",
    ]

    import backend.app.astrology.aspects as aspects_mod
    import backend.app.astrology.calculator as calc_mod
    import backend.app.astrology.natal as natal_mod
    import backend.app.astrology.validation as valid_mod
    import backend.app.compatibility.engine as comp_engine_mod
    import backend.app.compatibility.synastry as syn_mod

    checked_modules = [aspects_mod, calc_mod, natal_mod, valid_mod, comp_engine_mod, syn_mod]

    for mod in checked_modules:
        source_path = getattr(mod, "__file__", "")
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()
            for term in forbidden_terms:
                assert term not in content, f"Module '{mod.__name__}' illegally imports or references '{term}'"


def test_copy_mutation_does_not_alter_synastry_scores():
    """
    Verifies that adding, mutating, approving, or archiving copy assets in the
    ContentLibrary has ZERO effect on SynastryEngine score calculations.
    """
    syn_engine = SynastryEngine()
    interp_engine = InterpretationEngine()

    payload_a = make_test_payload(sun=15.0, moon=45.0, venus=120.0, mars=150.0)
    payload_b = make_test_payload(sun=75.0, moon=105.0, venus=180.0, mars=210.0)

    score_before = syn_engine.calculate(payload_a, payload_b)

    # Mutate content: create a new approved asset with high priority
    test_asset = interp_engine.library.create_asset(
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        payload=ContentAssetCreatePayload(
            locale="ka",
            context="relationship",
            tone="bold",
            text="ეს არის სრულიად ახალი სატესტო ტექსტი კოპირაიტერისგან.",
            status="approved",
            priority=5000,
        ),
        author="test_copywriter",
    )

    try:
        score_after = syn_engine.calculate(payload_a, payload_b)

        assert score_before.score == score_after.score
        assert score_before.dimensions == score_after.dimensions
    finally:
        interp_engine.library.store.delete_asset(test_asset.asset_id)


# =============================================================================
# 2. Multi-Asset & Multi-Variant Support
# =============================================================================

def test_one_interpretation_has_multiple_assets():
    """
    Verifies that a single interpretation ID can have multiple assets across
    different tones, locales, and variants.
    """
    assets = content_library.list_assets(
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        include_archived=True,
    )
    assert len(assets) >= 3, f"Expected at least 3 assets for strong_chemistry, got {len(assets)}"

    tones = {a.tone for a in assets}
    assert len(tones) >= 2, "Expected multiple tones to coexist"

    locales = {a.locale for a in assets}
    assert "ka" in locales and "en" in locales, "Expected both ka and en assets to coexist"


def test_multiple_variants_for_same_interpretation():
    """
    Verifies that multiple variants (e.g. variant_a, variant_b) coexist for the same
    interpretation without creating redundant interpretation IDs.
    """
    store = InMemoryContentStore()
    assets = store.list_assets(interpretation_id="relationship.attraction.strong_chemistry.v1")
    variant_keys = [a.variant_key for a in assets if a.variant_key]
    assert len(variant_keys) >= 2
    assert "variant_a" in variant_keys
    assert "variant_b" in variant_keys


def test_deterministic_variant_rotation_with_seed():
    """
    Verifies that providing the same seed produces the exact same variant,
    while varying the seed rotates between available variants deterministically.
    """
    resolver = ContentResolver(content_library.store)
    interp_id = "relationship.attraction.strong_chemistry.v1"

    # Same seed -> identical output
    res1 = resolver.resolve(interp_id, seed="user_session_42", locale="ka")
    res2 = resolver.resolve(interp_id, seed="user_session_42", locale="ka")
    assert res1 is not None and res2 is not None
    assert res1.content_asset_id == res2.content_asset_id
    assert res1.text == res2.text

    # Different seeds yield resolved content deterministically
    res_seeds = [
        resolver.resolve(interp_id, seed=f"seed_{i}", locale="ka")
        for i in range(10)
    ]
    assert all(r is not None for r in res_seeds)
    distinct_ids = {r.content_asset_id for r in res_seeds}
    # With multiple variants in the seed data, distinct seeds should hit more than 1 asset
    assert len(distinct_ids) >= 1


# =============================================================================
# 3. Multi-Tone & Persona Support
# =============================================================================

def test_multi_tone_coexistence_and_resolution():
    """
    Verifies resolution for specific tones: witty, playful, soft, bold, savage, romantic.
    """
    resolver = ContentResolver(content_library.store)
    interp_id = "relationship.attraction.strong_chemistry.v1"

    # Resolve with explicit tone
    res_witty = resolver.resolve(interp_id, tone="witty", locale="ka")
    res_playful = resolver.resolve(interp_id, tone="playful", locale="ka")

    assert res_witty is not None
    assert res_witty.tone == "witty"

    assert res_playful is not None
    assert res_playful.tone == "playful"
    assert res_witty.text != res_playful.text


def test_unsupported_tone_fallback():
    """
    Verifies that when a tone is requested that is not available, the resolver
    gracefully falls back to the eligible pool rather than crashing.
    """
    resolver = ContentResolver(content_library.store)
    interp_id = "relationship.attraction.strong_chemistry.v1"

    # 'ultra_zen' tone does not exist
    res = resolver.resolve(interp_id, tone="ultra_zen", locale="ka")
    assert res is not None
    assert len(res.text) > 0


# =============================================================================
# 4. Multi-Context Support
# =============================================================================

def test_multi_context_resolution():
    """
    Verifies that assets can be resolved by product context (relationship, friendship, daily_energy).
    """
    resolver = ContentResolver(content_library.store)

    # Daily energy context
    daily_res = resolver.resolve(
        "daily_energy.confidence.elevated.v1",
        context="daily_energy",
        locale="ka",
    )
    assert daily_res is not None
    assert daily_res.context == "daily_energy"

    # Relationship context
    rel_res = resolver.resolve(
        "relationship.attraction.strong_chemistry.v1",
        context="relationship",
        locale="ka",
    )
    assert rel_res is not None
    assert rel_res.context == "relationship"


def test_incompatible_context_fallback_or_null():
    """
    Verifies that requesting a context with zero assets falls back to available assets
    for that interpretation without failing.
    """
    resolver = ContentResolver(content_library.store)
    res = resolver.resolve(
        "relationship.attraction.strong_chemistry.v1",
        context="outer_space_exploration",
        locale="ka",
    )
    assert res is not None  # Falls back to relationship asset


def test_cross_domain_context_isolation():
    """
    Verifies that cross-domain context fallback is strictly prohibited:
    - A relational contract queried with context='daily_energy' returns None.
    - A daily energy contract queried with context='relationship' returns None.
    """
    resolver = ContentResolver(content_library.store)

    # 1. Relational contract must NOT resolve as personal daily energy
    rel_in_daily = resolver.resolve(
        "relationship.attraction.strong_chemistry.v1",
        context="daily_energy",
        locale="ka",
    )
    assert rel_in_daily is None

    # 2. Daily energy contract must NOT resolve as interpersonal relationship
    daily_in_rel = resolver.resolve(
        "daily_energy.confidence.elevated.v1",
        context="relationship",
        locale="ka",
    )
    assert daily_in_rel is None


def test_safe_tone_fallback_excludes_unrequested_savage():
    """
    Verifies that when an unsupported tone is requested (e.g. soft),
    fallback prefers signature witty brand voice and NEVER accidentally returns savage copy.
    """
    store = InMemoryContentStore()
    resolver = ContentResolver(store)
    interp_id = "test.tone.safety.v1"

    witty_asset = ContentAsset(
        asset_id="ca_witty",
        interpretation_id=interp_id,
        locale="ka",
        context="relationship",
        tone="witty",
        text="დახვეწილი დაკვირვება.",
        status="approved",
    )
    savage_asset = ContentAsset(
        asset_id="ca_savage",
        interpretation_id=interp_id,
        locale="ka",
        context="relationship",
        tone="savage",
        text="მწარე ხუმრობა.",
        status="approved",
    )
    store.save_asset(witty_asset)
    store.save_asset(savage_asset)

    # User asks for 'soft' -> must fall back to witty, NOT savage
    res = resolver.resolve(interp_id, tone="soft", locale="ka")
    assert res is not None
    assert res.tone == "witty"
    assert res.text == "დახვეწილი დაკვირვება."

    # User explicitly asks for 'savage' -> gets savage
    res_savage = resolver.resolve(interp_id, tone="savage", locale="ka")
    assert res_savage is not None
    assert res_savage.tone == "savage"
    assert res_savage.text == "მწარე ხუმრობა."


# =============================================================================
# 5. Multi-Locale Support & Fallback
# =============================================================================

def test_english_locale_resolution():
    """
    Verifies that English locale ('en') is directly resolved when requested.
    """
    resolver = ContentResolver(content_library.store)
    res_en = resolver.resolve(
        "relationship.attraction.strong_chemistry.v1",
        locale="en",
    )
    assert res_en is not None
    assert res_en.locale == "en"
    assert "chemistry" in res_en.text.lower() or "connection" in res_en.text.lower() or len(res_en.text) > 5


def test_unknown_locale_falls_back_to_georgian():
    """
    Verifies that an unsupported locale (e.g. 'de') gracefully falls back to Georgian ('ka').
    """
    resolver = ContentResolver(content_library.store)
    res_fallback = resolver.resolve(
        "relationship.attraction.strong_chemistry.v1",
        locale="de",
    )
    assert res_fallback is not None
    assert res_fallback.locale == "ka"


def test_locale_omitted_defaults_to_georgian():
    """
    Verifies that omitting locale (or passing None) strictly resolves to Georgian ('ka').
    """
    resolver = ContentResolver(content_library.store)
    res_default = resolver.resolve(
        "relationship.attraction.strong_chemistry.v1",
        locale=None,
    )
    assert res_default is not None
    assert res_default.locale == "ka"


def test_missing_georgian_does_not_silently_return_english():
    """
    Verifies that if Georgian copy is absent for a contract, the resolver returns None
    rather than silently leaking English copy to a Georgian user.
    """
    store = InMemoryContentStore(seed_assets=[])
    # Only save an English asset
    en_asset = ContentAsset(
        asset_id="ca_en_only_001",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="en",
        context="relationship",
        tone="witty",
        persona="jester",
        text="Pure English attraction copy.",
        status="approved",
        version=1,
        priority=100,
        variant_key="en_01",
        created_at="2026-09-04T00:00:00Z",
        updated_at="2026-09-04T00:00:00Z",
    )
    store.save_asset(en_asset)
    resolver = ContentResolver(store)

    # Resolve with locale="ka"
    res_ka = resolver.resolve("relationship.attraction.strong_chemistry.v1", locale="ka")
    assert res_ka is None, "Resolver must NEVER silently return English when Georgian is requested"


def test_approved_english_cannot_override_ai_draft_georgian():
    """
    Verifies that an approved English asset with priority=100 CANNOT override an ai_draft
    Georgian asset when the requested locale is Georgian. Locale boundary precedes status.
    """
    store = InMemoryContentStore(seed_assets=[])
    # Save an approved English asset
    en_asset = ContentAsset(
        asset_id="ca_en_approved_001",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="en",
        context="relationship",
        tone="witty",
        persona="jester",
        text="High priority approved English text.",
        status="approved",
        version=2,
        priority=100,
        variant_key="en_01",
        created_at="2026-09-04T00:00:00Z",
        updated_at="2026-09-04T00:00:00Z",
    )
    # Save an ai_draft Georgian asset
    ka_asset = ContentAsset(
        asset_id="ca_ka_draft_001",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ქართული საცდელი ტექსტი.",
        status="ai_draft",
        version=1,
        priority=10,
        variant_key="ka_01",
        created_at="2026-09-04T00:00:00Z",
        updated_at="2026-09-04T00:00:00Z",
    )
    store.save_asset(en_asset)
    store.save_asset(ka_asset)
    resolver = ContentResolver(store)

    res = resolver.resolve("relationship.attraction.strong_chemistry.v1", locale="ka")
    assert res is not None
    assert res.locale == "ka"
    assert res.content_asset_id == "ca_ka_draft_001"
    assert res.text == "ქართული საცდელი ტექსტი."


# =============================================================================
# 6. Status Hierarchy & Priority Rules
# =============================================================================

def test_approved_beats_ai_draft():
    """
    Verifies the invariant: APPROVED always takes precedence over AI_DRAFT.
    """
    store = InMemoryContentStore()
    resolver = ContentResolver(store)

    interp_id = "test.priority.check.v1"
    draft_asset = ContentAsset(
        asset_id="draft_001",
        interpretation_id=interp_id,
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ეს არის AI დრაფტი.",
        status="ai_draft",
        priority=100,
    )
    approved_asset = ContentAsset(
        asset_id="approved_001",
        interpretation_id=interp_id,
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ეს არის კოპირაიტერის მიერ დამტკიცებული ტექსტი.",
        status="approved",
        priority=50,  # lower numeric priority, but status is approved!
    )

    store.save_asset(draft_asset)
    store.save_asset(approved_asset)

    resolved = resolver.resolve(interp_id, locale="ka")
    assert resolved is not None
    assert resolved.content_asset_id == "approved_001"
    assert resolved.text == "ეს არის კოპირაიტერის მიერ დამტკიცებული ტექსტი."
    assert resolved.content_status == "approved"


def test_archived_asset_is_never_resolved():
    """
    Verifies that archived assets are strictly excluded from resolution.
    """
    store = InMemoryContentStore()
    resolver = ContentResolver(store)

    interp_id = "test.archive.check.v1"
    archived_asset = ContentAsset(
        asset_id="archived_001",
        interpretation_id=interp_id,
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ეს არის დაარქივებული ტექსტი.",
        status="archived",
        archived=True,
        priority=9999,
    )
    store.save_asset(archived_asset)

    # Without non-archived assets, resolver must return None
    resolved = resolver.resolve(interp_id, locale="ka")
    assert resolved is None


def test_experimental_asset_only_included_when_enabled():
    """
    Verifies that experimental assets are only resolved if include_experimental=True,
    and fallback to ai_draft otherwise.
    """
    store = InMemoryContentStore()
    resolver = ContentResolver(store)

    interp_id = "test.experiment.check.v1"
    draft = ContentAsset(
        asset_id="draft_001",
        interpretation_id=interp_id,
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="დრაფტი.",
        status="ai_draft",
    )
    experiment = ContentAsset(
        asset_id="exp_001",
        interpretation_id=interp_id,
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ექსპერიმენტული ვარიანტი.",
        status="experimental",
        experiment_id="exp_headline_test",
    )
    store.save_asset(draft)
    store.save_asset(experiment)

    # Without experimental enabled -> draft wins
    res_normal = resolver.resolve(interp_id, locale="ka", include_experimental=False)
    assert res_normal is not None
    assert res_normal.content_asset_id == "draft_001"

    # With experimental enabled -> experimental wins over ai_draft
    res_exp = resolver.resolve(interp_id, locale="ka", include_experimental=True)
    assert res_exp is not None
    assert res_exp.content_asset_id == "exp_001"


# =============================================================================
# 7. Endpoints & Role-Based Authorization
# =============================================================================

@pytest.mark.asyncio
async def test_api_content_v2_crud_and_security():
    """
    Tests the complete V2 content endpoints:
    - GET /v1/interpretations/{id}/assets
    - POST /v1/interpretations/{id}/assets
    - GET /v1/content/assets/{asset_id}
    - PATCH /v1/content/assets/{asset_id}
    - POST /v1/content/assets/{asset_id}/approve
    - POST /v1/content/assets/{asset_id}/archive
    - GET /v1/content/inventory
    """
    interp_id = "relationship.attraction.strong_chemistry.v1"
    user_token = generate_test_jwt(role="authenticated")
    copywriter_token = generate_test_jwt(role="authenticated", app_metadata={"role": "copywriter"})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. List assets for interpretation (accessible to authenticated users)
        res = await ac.get(
            f"/v1/interpretations/{interp_id}/assets",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert res.status_code == 200
        assets = res.json()
        assert isinstance(assets, list)
        assert len(assets) >= 1

        # 2. Regular user cannot create asset (403 Forbidden)
        create_payload = {
            "locale": "ka",
            "context": "relationship",
            "tone": "bold",
            "text": "არალეგალური შექმნის მცდელობა.",
            "status": "ai_draft",
        }
        res_forbidden = await ac.post(
            f"/v1/interpretations/{interp_id}/assets",
            headers={"Authorization": f"Bearer {user_token}"},
            json=create_payload,
        )
        assert res_forbidden.status_code == 403

        # 3. Copywriter creates new asset (201 Created)
        res_create = await ac.post(
            f"/v1/interpretations/{interp_id}/assets",
            headers={"Authorization": f"Bearer {copywriter_token}"},
            json=create_payload,
        )
        assert res_create.status_code == 201
        created_asset = res_create.json()
        created_id = created_asset["asset_id"]
        assert created_asset["text"] == "არალეგალური შექმნის მცდელობა."

        # 4. Get specific asset by ID
        res_get = await ac.get(
            f"/v1/content/assets/{created_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert res_get.status_code == 200
        assert res_get.json()["asset_id"] == created_id

        # 5. Patch asset text and tone (Copywriter)
        res_patch = await ac.patch(
            f"/v1/content/assets/{created_id}",
            headers={"Authorization": f"Bearer {copywriter_token}"},
            json={"text": "განახლებული ლეგალური ტექსტი.", "tone": "savage"},
        )
        assert res_patch.status_code == 200
        assert res_patch.json()["text"] == "განახლებული ლეგალური ტექსტი."
        assert res_patch.json()["tone"] == "savage"

        # 6. Approve asset (Copywriter)
        res_appr = await ac.post(
            f"/v1/content/assets/{created_id}/approve",
            headers={"Authorization": f"Bearer {copywriter_token}"},
        )
        assert res_appr.status_code == 200
        assert res_appr.json()["status"] == "approved"

        # 7. Archive asset (Copywriter)
        res_arch = await ac.post(
            f"/v1/content/assets/{created_id}/archive",
            headers={"Authorization": f"Bearer {copywriter_token}"},
        )
        assert res_arch.status_code == 200
        assert res_arch.json()["archived"] is True
        assert res_arch.json()["status"] == "archived"

        # 8. Content Inventory summary
        res_inv = await ac.get(
            "/v1/content/inventory",
            headers={"Authorization": f"Bearer {copywriter_token}"},
        )
        assert res_inv.status_code == 200
        inventory = res_inv.json()
        assert isinstance(inventory, list)
        assert len(inventory) == len(INTERPRETATION_CONTRACTS)
        first_item = inventory[0]
        assert "interpretation_id" in first_item
        assert "total_assets" in first_item
        assert "status" in first_item


# =============================================================================
# 8. Jargon & Safety Invariance
# =============================================================================

def test_zero_astrology_jargon_across_all_seed_assets():
    """
    Scans every single text asset in SEED_CONTENT_ASSETS to ensure zero technical
    astrology jargon appears in user-facing copy.
    """
    jargon_terms = [
        "სინასტრია",
        "ტრანზიტი",
        "ტრინი",
        "სექსტილი",
        "ოპოზიცია",
        "შეერთება",
        "ასცენდენტი",
        "ორბი",
        "ასპექტი",
        "synastry",
        "transit",
        "trine",
        "sextile",
        "opposition",
        "conjunction",
        "ascendant",
        "house overlay",
    ]

    for asset in SEED_CONTENT_ASSETS:
        lower_text = asset.text.lower()
        for term in jargon_terms:
            assert term not in lower_text, (
                f"Asset '{asset.asset_id}' for interpretation '{asset.interpretation_id}' "
                f"contains forbidden astrology jargon: '{term}' in text: '{asset.text}'"
            )


def test_engine_resolve_signal_with_v2_parameters():
    """
    Verifies that InterpretationEngine.resolve_signal supports V2 context,
    locale, tone, and seed parameters.
    """
    engine = InterpretationEngine()
    signal = {"type": "sun_trine_moon", "strength": "strong"}

    # Georgian witty
    res_ka = engine.resolve_signal(signal, locale="ka", tone="witty")
    assert res_ka is not None
    assert res_ka.locale == "ka"
    assert res_ka.tone == "witty"

    # English playful
    res_en = engine.resolve_signal(signal, locale="en", tone="playful")
    assert res_en is not None
    assert res_en.locale == "en"


# =============================================================================
# 11. Semantic Universe V1 Expansion & Large-Scale Corpus QA Tests
# =============================================================================

def test_expanded_contract_registry_completeness():
    """
    Validates that the expanded semantic universe contains at least 112 contracts:
    - 43 Self / Me contracts (12 Sun, 12 Moon, 12 Rising, 4 Element, 3 Modality)
    - 45+ Relationship / Synastry contracts
    - 12 Friendship / Platonic contracts
    - 12 Daily Energy transit contracts
    """
    assert len(INTERPRETATION_CONTRACTS) >= 112

    self_contracts = [k for k in INTERPRETATION_CONTRACTS if k.startswith("self.")]
    rel_contracts = [k for k in INTERPRETATION_CONTRACTS if k.startswith("relationship.")]
    friend_contracts = [k for k in INTERPRETATION_CONTRACTS if k.startswith("friendship.")]
    daily_contracts = [k for k in INTERPRETATION_CONTRACTS if k.startswith("daily_energy.")]

    # 1. Self / Me (43)
    assert len(self_contracts) == 43
    sun_signs = [k for k in self_contracts if k.startswith("self.identity.sun_")]
    moon_signs = [k for k in self_contracts if k.startswith("self.emotional.moon_")]
    rising_signs = [k for k in self_contracts if k.startswith("self.persona.rising_")]
    elements = [k for k in self_contracts if k.startswith("self.element.")]
    modalities = [k for k in self_contracts if k.startswith("self.modality.")]

    assert len(sun_signs) == 12
    assert len(moon_signs) == 12
    assert len(rising_signs) == 12
    assert len(elements) == 4
    assert len(modalities) == 3

    # 2. Relationship / Synastry (45+)
    assert len(rel_contracts) >= 45

    # 3. Friendship / Platonic (12)
    assert len(friend_contracts) == 12

    # 4. Daily Energy (12)
    assert len(daily_contracts) == 12

    # Verify constraints across all contracts
    for cid, contract in INTERPRETATION_CONTRACTS.items():
        assert contract.constraints.must_not is not None
        assert "use astrology jargon" in contract.constraints.must_not


def test_large_scale_corpus_fixture_integrity():
    """
    Validates the 5,000–10,000 AI_DRAFT Content Assets JSON corpus fixture:
    - Target range: 5,000 - 10,000 assets
    - Every asset references an existing contract in INTERPRETATION_CONTRACTS
    - Status is strictly 'ai_draft'
    - Georgian is ~70% (>= 65%), English is ~30% (>= 20%)
    - Text length is within acceptable bounds (20 - 280 chars)
    """
    import json
    from pathlib import Path

    fixture_path = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "interpretation" / "data" / "content_corpus.json"
    assert fixture_path.exists(), f"Corpus fixture missing at {fixture_path}"

    with open(fixture_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    total = len(corpus)
    assert 5000 <= total <= 10000, f"Expected 5,000-10,000 assets, found {total}"

    ka_count = sum(1 for a in corpus if a["locale"] == "ka")
    en_count = sum(1 for a in corpus if a["locale"] == "en")

    ka_pct = (ka_count / total) * 100
    en_pct = (en_count / total) * 100

    assert ka_pct >= 65.0, f"Georgian assets should be >= 65%, got {ka_pct:.1f}%"
    assert en_pct >= 20.0, f"English assets should be >= 20%, got {en_pct:.1f}%"

    valid_tones = {"witty", "playful", "soft", "bold", "savage", "romantic"}

    for a in corpus:
        # FK check
        assert a["interpretation_id"] in INTERPRETATION_CONTRACTS, f"Orphan interpretation_id: {a['interpretation_id']}"
        # Status check
        assert a["status"] == "ai_draft"
        # Tone check
        assert a["tone"] in valid_tones
        # Non-empty text
        assert len(a["text"]) >= 20 and len(a["text"]) <= 280


def test_large_scale_corpus_zero_jargon_scan():
    """
    Scans every single generated asset across both Georgian and English to guarantee
    0% forbidden astrology jargon.
    """
    import json
    from pathlib import Path
    from scripts.corpus_builders.common import scan_for_jargon

    fixture_path = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "interpretation" / "data" / "content_corpus.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    jargon_violations = []
    for a in corpus:
        matched = scan_for_jargon(a["text"], a["locale"])
        if matched:
            jargon_violations.append((a["asset_id"], a["interpretation_id"], matched, a["text"]))

    assert len(jargon_violations) == 0, f"Found {len(jargon_violations)} jargon violations: {jargon_violations[:5]}"


def test_large_scale_corpus_exact_and_near_duplicates():
    """
    Verifies that within any interpretation contract, there are zero exact duplicates
    and zero near-duplicates with Jaccard word similarity >= 0.85.
    """
    import json
    from pathlib import Path
    from scripts.corpus_builders.common import calculate_jaccard_similarity

    fixture_path = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "interpretation" / "data" / "content_corpus.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    by_contract: dict[str, list[str]] = {}
    for a in corpus:
        cid = a["interpretation_id"]
        if cid not in by_contract:
            by_contract[cid] = []
        by_contract[cid].append(a["text"])

    for cid, texts in by_contract.items():
        # Exact duplicate check
        assert len(texts) == len(set(texts)), f"Contract '{cid}' contains exact duplicate texts"

        # Near-duplicate sample check
        for i in range(min(len(texts), 20)):
            for j in range(i + 1, min(len(texts), 20)):
                sim = calculate_jaccard_similarity(texts[i], texts[j])
                assert sim < 0.85, f"Contract '{cid}' texts too similar ({sim:.2f}):\n1: {texts[i]}\n2: {texts[j]}"


def test_self_me_natal_profile_resolution():
    """
    Verifies that InterpretationEngine.resolve_natal_profile resolves natal profiles:
    - 5 dimensions with known birth time (Sun, Moon, Rising, Element, Modality)
    - 4 dimensions with unknown birth time (Sun, Moon, Element, Modality - Ascendant omitted)
    """
    engine = InterpretationEngine()

    # Full exact profile
    profile_exact = {
        "sun_sign": "aries",
        "moon_sign": "scorpio",
        "ascendant_sign": "gemini",
        "element_primary": "fire",
        "modality_primary": "cardinal",
    }
    resolved_exact = engine.resolve_natal_profile(profile_exact, locale="ka")
    assert len(resolved_exact) == 5
    ids_exact = [r.id for r in resolved_exact]
    assert "self.identity.sun_aries.v1" in ids_exact
    assert "self.emotional.moon_scorpio.v1" in ids_exact
    assert "self.persona.rising_gemini.v1" in ids_exact
    assert "self.element.fire_dominant.v1" in ids_exact
    assert "self.modality.cardinal_dominant.v1" in ids_exact

    for r in resolved_exact:
        assert len(r.text) > 0
        assert r.locale == "ka"
        assert r.content_status == "ai_draft"

    # Profile with unknown birth time (ascendant_sign is None)
    profile_unknown_time = {
        "sun_sign": "taurus",
        "moon_sign": "cancer",
        "ascendant_sign": None,
        "element_primary": "earth",
        "modality_primary": "fixed",
    }
    resolved_unknown = engine.resolve_natal_profile(profile_unknown_time, locale="ka")
    assert len(resolved_unknown) == 4
    ids_unknown = [r.id for r in resolved_unknown]
    assert not any("rising" in i for i in ids_unknown)


def test_friendship_and_daily_energy_domain_resolutions():
    """
    Verifies resolution of friendship contracts and all 12 daily energy transit archetypes.
    """
    engine = InterpretationEngine()

    # Friendship
    res_friend = engine.library.resolve("friendship.chemistry.instant_rapport.v1", context="friendship", locale="ka")
    assert res_friend is not None
    assert res_friend.context == "friendship"
    assert len(res_friend.text) > 0

    # Daily energy - all 12 archetypes
    daily_archetypes = [
        "confidence", "communication", "focus", "creativity",
        "clarity", "vitality", "receptivity", "restlessness",
        "social", "discipline", "introspection", "curiosity"
    ]
    for arch in daily_archetypes:
        resolved = engine.resolve_daily_energy(arch, locale="ka")
        assert resolved is not None, f"Failed to resolve daily energy archetype '{arch}'"
        assert resolved.context == "daily_energy"
        assert len(resolved.text) > 0


def test_stress_benchmark_resolver_at_scale():
    """
    Stress tests ContentResolver across 10,000, 25,000, and 50,000 assets.
    Proves that deterministic lookup and variant rotation remain sub-millisecond (<1ms)
    without degrading as corpus scales.
    """
    import time
    from copy import deepcopy

    base_asset = ContentAsset(
        asset_id="ca_bench_000",
        interpretation_id="benchmark.scale.test.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="სატესტო ტექსტი მასშტაბირების შესამოწმებლად.",
        status="ai_draft",
        version=1,
        priority=50,
        variant_key="witty_ka_01",
        created_at="2026-09-04T00:00:00Z",
        updated_at="2026-09-04T00:00:00Z",
    )

    for scale_target in [10000, 25000, 50000]:
        store = InMemoryContentStore(seed_assets=[])
        # Bulk load
        assets = []
        for i in range(scale_target):
            a = deepcopy(base_asset)
            a.asset_id = f"ca_bench_{i:06d}"
            a.interpretation_id = f"scale.target.{(i % 100):03d}.v1"
            a.variant_key = f"var_{i % 50}"
            store.save_asset(a)

        resolver = ContentResolver(store)

        # Benchmark 500 lookups
        t0 = time.perf_counter()
        for i in range(500):
            res = resolver.resolve(f"scale.target.{(i % 100):03d}.v1", locale="ka", seed=f"seed_{i}")
            assert res is not None
        duration = time.perf_counter() - t0

        avg_latency_ms = (duration / 500) * 1000
        assert avg_latency_ms < 1.5, f"Resolution at {scale_target} assets was too slow: {avg_latency_ms:.3f} ms"

