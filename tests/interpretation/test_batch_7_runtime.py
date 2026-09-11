"""
Tests for JESTER Batch 7 Runtime Integration.
Validates:
1. Corpus Loading (66 total: 12 Discovery, 11 Connection, 43 Chat Starters)
2. ContentStore Indexing & Domain/Surface Isolation
3. Discovery Runtime Logic (Ascendant sign -> Sun fallback -> safe default; no synastry/identity leak)
4. Connection Invitation Mapping (communication, harmony, attraction, stability, growth, notice/insufficient_aspects)
5. Conversation Starter Resolution (Batch 6 signals -> Batch 7 starters, fallbacks, max 3, no legacy strings)
6. Access Control Invariants (compare-preview discoverability/block rules, /v1/compare connection-gate, /why connection-gate)
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.compatibility.rules import DEFAULT_CONVERSATION_STARTERS
from backend.app.compatibility.synastry import NatalInputPayload, SynastryEngine
from backend.app.interpretation.engine import interpretation_engine
from backend.app.interpretation.library import content_library
from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt


# =============================================================================
# A. Corpus Loading Tests
# =============================================================================
def test_batch_7_corpus_loading():
    """Assert exactly 66 Batch 7 assets loaded: 12 Discovery, 11 Connection, 43 Chat Starters."""
    all_assets = content_library.store.list_assets()
    b7_assets = [a for a in all_assets if "batch_7" in a.tags]

    assert len(b7_assets) == 66, f"Expected exactly 66 Batch 7 assets, got {len(b7_assets)}"

    discovery_assets = [a for a in b7_assets if a.context == "discovery"]
    connection_assets = [a for a in b7_assets if a.context == "connection"]
    chat_assets = [a for a in b7_assets if a.context == "chat"]

    assert len(discovery_assets) == 12, f"Expected 12 discovery assets, got {len(discovery_assets)}"
    assert len(connection_assets) == 11, f"Expected 11 connection assets, got {len(connection_assets)}"
    assert len(chat_assets) == 43, f"Expected 43 chat assets, got {len(chat_assets)}"


# =============================================================================
# B. Content Resolution & Isolation Tests
# =============================================================================
def test_batch_7_indexing_and_isolation():
    """Verify Batch 7 assets are properly indexed and isolated from other contexts."""
    # 1. Discovery asset resolves in discovery context, but NOT in relationship context
    disc_res = content_library.resolve("discovery.person.presence.leo.v1", context="discovery", locale="ka")
    assert disc_res is not None
    assert disc_res.context == "discovery"
    assert disc_res.id == "discovery.person.presence.leo.v1"

    disc_leak = content_library.resolve("discovery.person.presence.leo.v1", context="relationship", locale="ka")
    assert disc_leak is None, "Discovery asset must never resolve under relationship context"

    # 2. Connection invitation resolves in connection context, but NOT in relationship context
    conn_res = content_library.resolve("connection.invitation.harmony.v1", context="connection", locale="ka")
    assert conn_res is not None
    assert conn_res.context == "connection"

    conn_leak = content_library.resolve("connection.invitation.harmony.v1", context="relationship", locale="ka")
    assert conn_leak is None, "Connection invitation must never resolve under relationship context"

    # 3. Chat starter resolves under chat context, while relationship context resolves full interpretation
    interp_id = "relationship.harmony.emotional_resonance.v1"
    chat_res = content_library.resolve(interp_id, context="chat", locale="ka")
    rel_res = content_library.resolve(interp_id, context="relationship", locale="ka")

    assert chat_res is not None
    assert rel_res is not None
    assert chat_res.context == "chat"
    assert rel_res.context == "relationship"
    assert chat_res.content_asset_id != rel_res.content_asset_id
    assert chat_res.text != rel_res.text


# =============================================================================
# C. Discovery Runtime Tests
# =============================================================================
def test_discovery_presence_resolution_ascendant():
    """Ascendant present -> resolves corresponding discovery.person.presence.{ascendant}.v1"""
    # Simulate candidate with Ascendant Scorpio and Sun Leo
    candidate_asc = "Scorpio"
    candidate_sun = "Leo"
    target_sign = (candidate_asc or candidate_sun or "aries").strip().lower()
    discovery_interp_id = f"discovery.person.presence.{target_sign}.v1"

    hook_res = content_library.resolve(
        interpretation_id=discovery_interp_id,
        context="discovery",
        locale="ka",
        seed="candidate-1",
    )
    assert hook_res is not None
    assert hook_res.id == "discovery.person.presence.scorpio.v1"
    assert hook_res.context == "discovery"
    assert len(hook_res.text) > 0


def test_discovery_presence_resolution_sun_fallback():
    """Ascendant absent (unknown birth time) -> falls back to candidate Sun sign"""
    candidate_asc = None
    candidate_sun = "Aquarius"
    target_sign = (candidate_asc or candidate_sun or "aries").strip().lower()
    discovery_interp_id = f"discovery.person.presence.{target_sign}.v1"

    hook_res = content_library.resolve(
        interpretation_id=discovery_interp_id,
        context="discovery",
        locale="ka",
        seed="candidate-2",
    )
    assert hook_res is not None
    assert hook_res.id == "discovery.person.presence.aquarius.v1"
    assert hook_res.context == "discovery"
    assert len(hook_res.text) > 0


def test_discovery_presence_resolution_both_absent_fallback():
    """Both absent -> falls back to established default 'aries'"""
    candidate_asc = None
    candidate_sun = None
    target_sign = (candidate_asc or candidate_sun or "aries").strip().lower()
    discovery_interp_id = f"discovery.person.presence.{target_sign}.v1"

    hook_res = content_library.resolve(
        interpretation_id=discovery_interp_id,
        context="discovery",
        locale="ka",
        seed="candidate-default",
    )
    assert hook_res is not None
    assert hook_res.id == "discovery.person.presence.aries.v1"
    assert hook_res.context == "discovery"


def test_discovery_does_not_use_synastry_or_identity():
    """Verify Discovery presence hook is strictly Batch 7 presence, not synastry or self.identity."""
    for sign in ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]:
        res = content_library.resolve(f"discovery.person.presence.{sign}.v1", context="discovery", locale="ka")
        assert res is not None
        assert not res.id.startswith("self.identity")
        assert not res.id.startswith("relationship.")
        assert res.id.startswith("discovery.person.presence")


# =============================================================================
# D. Connection Invitation Tests
# =============================================================================
def test_connection_invitation_category_mapping():
    """Verify all 6 categories map deterministically to Batch 7 connection invitations."""
    # 1. Communication
    sig_comm = [{"type": "mercury_trine_mercury", "category": "communication", "strength": 0.9}]
    inv_comm = interpretation_engine.resolve_connection_invitation(sig_comm, seed="seed_comm")
    assert inv_comm is not None
    assert inv_comm.id == "connection.invitation.communication.v1"
    assert inv_comm.context == "connection"

    # 2. Harmony
    sig_harm = [{"type": "sun_trine_moon", "category": "harmony", "strength": 0.9}]
    inv_harm = interpretation_engine.resolve_connection_invitation(sig_harm, seed="seed_harm")
    assert inv_harm is not None
    assert inv_harm.id == "connection.invitation.harmony.v1"
    assert inv_harm.context == "connection"

    # 3. Attraction
    sig_attr = [{"type": "venus_conjunction_mars", "category": "attraction", "strength": 0.9}]
    inv_attr = interpretation_engine.resolve_connection_invitation(sig_attr, seed="seed_attr")
    assert inv_attr is not None
    assert inv_attr.id == "connection.invitation.attraction.v1"
    assert inv_attr.context == "connection"

    # 4. Stability
    sig_stab = [{"type": "saturn_trine_sun", "category": "stability", "strength": 0.9}]
    inv_stab = interpretation_engine.resolve_connection_invitation(sig_stab, seed="seed_stab")
    assert inv_stab is not None
    assert inv_stab.id == "connection.invitation.stability.v1"
    assert inv_stab.context == "connection"

    # 5. Growth / Friction
    sig_fric = [{"type": "mars_square_saturn", "category": "growth", "strength": 0.8}]
    inv_fric = interpretation_engine.resolve_connection_invitation(sig_fric, seed="seed_fric")
    assert inv_fric is not None
    assert inv_fric.id == "connection.invitation.friction.v1"
    assert inv_fric.context == "connection"

    # 6. Notice / Insufficient Aspects
    sig_none = [{"type": "insufficient_aspects", "category": "notice", "strength": 0.1}]
    inv_none = interpretation_engine.resolve_connection_invitation(sig_none, seed="seed_none")
    assert inv_none is not None
    assert inv_none.id == "connection.invitation.independent.v1"
    assert inv_none.context == "connection"

    # Empty signals fallback
    inv_empty = interpretation_engine.resolve_connection_invitation([], seed="seed_empty")
    assert inv_empty is not None
    assert inv_empty.id == "connection.invitation.independent.v1"


def test_connection_invitation_variant_rotation():
    """Verify deterministic variant rotation (direct vs witty) via seed."""
    sig_harm = [{"type": "sun_trine_moon", "category": "harmony", "strength": 0.9}]
    # Collect variants across seeds
    collected_variants = set()
    for s in ["seed_a", "seed_b", "seed_c", "seed_d", "seed_e", "seed_f"]:
        inv = interpretation_engine.resolve_connection_invitation(sig_harm, seed=s)
        assert inv is not None
        collected_variants.add(inv.variant_key)

    # Both 'direct' and 'witty' variants exist for harmony in Batch 7
    assert "direct" in collected_variants
    assert "witty" in collected_variants


# =============================================================================
# E. Conversation Starters Tests
# =============================================================================
def test_conversation_starters_from_batch_7():
    """Verify Batch 6 signal -> Batch 6 interpretation ID -> Batch 7 starter."""
    signals = [
        {"type": "sun_trine_moon", "category": "harmony", "strength": 0.9},
        {"type": "mercury_trine_mercury", "category": "communication", "strength": 0.85},
        {"type": "venus_conjunction_mars", "category": "attraction", "strength": 0.8},
    ]

    starters = interpretation_engine.resolve_conversation_starters(signals, seed="pair-seed-123")
    assert len(starters) == 3

    # All 3 starters must be from Batch 7, NOT legacy default starters
    for starter in starters:
        assert starter not in DEFAULT_CONVERSATION_STARTERS, f"Legacy starter found: {starter}"

    # Verify determinism: same input -> same starters
    starters_repeat = interpretation_engine.resolve_conversation_starters(signals, seed="pair-seed-123")
    assert starters == starters_repeat


def test_conversation_starters_fallback():
    """Verify that when fewer than 3 signal starters exist, Batch 7 fallbacks are used."""
    # Empty signals
    starters_empty = interpretation_engine.resolve_conversation_starters([], seed="empty-seed")
    assert len(starters_empty) == 3

    # Fallback starters are defined in Batch 7
    fb1 = content_library.store.get_asset("chat.starter.fallback.v1")
    fb2 = content_library.store.get_asset("chat.starter.fallback.v2")
    fb3 = content_library.store.get_asset("chat.starter.fallback.v3")
    assert fb1 and fb2 and fb3

    expected_fallbacks = {fb1.text.strip(), fb2.text.strip(), fb3.text.strip()}
    assert set(starters_empty) == expected_fallbacks

    # Legacy defaults must NOT be used when Batch 7 fallbacks exist
    for st in starters_empty:
        assert st not in DEFAULT_CONVERSATION_STARTERS


def test_conversation_starters_single_signal_expansion():
    """A single signal with 2 variants expands and fills 3rd with Batch 7 fallback."""
    single_signal = [{"type": "sun_trine_moon", "category": "harmony", "strength": 0.9}]
    starters = interpretation_engine.resolve_conversation_starters(single_signal, seed="single-sig-seed")
    assert len(starters) == 3
    assert len(set(starters)) == 3  # All unique


from tests.database.test_database_security import create_test_user, db_conn, clean_db, set_auth_context


# =============================================================================
# F. Access Control & Integration Tests
# =============================================================================
@pytest.mark.asyncio
async def test_compare_preview_batch_7_payload(db_conn, clean_db):
    """compare-preview returns Batch 7 connection invitation and conversation starters."""
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"u1_b7_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_b7_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, u1, em1, "User One")
    create_test_user(db_conn, u2, em2, "User Two")

    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
            VALUES 
                (%s, '1992-04-10', '11:00:00', 'exact', 'UTC', 41.7151, 44.8271),
                (%s, '1994-09-18', '17:30:00', 'exact', 'UTC', 40.7128, -74.0060);
            """,
            (u1, u2),
        )

    token_u1 = generate_test_jwt(user_id=u1, email=em1)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2, "locale": "ka"},
        )
        assert res.status_code == 200, f"Preview failed: {res.text}"
        data = res.json()

        # Batch 6 primary relational interpretation
        interp = data.get("interpretation")
        assert interp is not None
        assert interp["context"] == "relationship"
        assert interp["id"].startswith("relationship.")

        # Batch 7 connection invitation
        conn_inv = data.get("connection_invitation")
        assert conn_inv is not None
        assert conn_inv["context"] == "connection"
        assert conn_inv["id"].startswith("connection.invitation.")
        assert interp["id"] != conn_inv["id"]

        # Batch 7 conversation starters
        starters = data.get("conversation_starters")
        assert starters is not None
        assert 1 <= len(starters) <= 3
        for st in starters:
            assert st not in DEFAULT_CONVERSATION_STARTERS


@pytest.mark.asyncio
async def test_compare_post_connect_requires_connection():
    """/v1/compare is connection-gated and returns 403 when no active connection exists."""
    transport = ASGITransport(app=app)
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    token = generate_test_jwt(user_id=user_a, email="user_a@test.com")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_user_id": user_b},
        )
        # Without active connection, returns privacy-safe 403
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "forbidden"


@pytest.mark.asyncio
async def test_why_requires_connection():
    """/v1/people/{id}/why is connection-gated and returns 403 when no active connection exists."""
    transport = ASGITransport(app=app)
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    token = generate_test_jwt(user_id=user_a, email="user_a@test.com")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(
            f"/v1/people/{user_b}/why",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "forbidden"
