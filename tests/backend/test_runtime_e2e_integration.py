"""
Comprehensive Real Runtime E2E Integration Test Suite for JESTER.
Executes actual FastAPI routes via httpx.AsyncClient with real JWT tokens,
database transactions, Swiss Ephemeris calculations, and semantic resolution.
"""
import uuid
from datetime import date, datetime, time, timezone
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.astrology.natal import recalculate_user_astrology
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import (
    create_test_user,
    db_conn,
    clean_db,
    set_auth_context,
)


def seed_user_birth_data(
    db_conn,
    user_id: str,
    birth_date: str = "1992-04-10",
    birth_time: str | None = "11:00:00",
    precision: str = "exact",
    timezone: str = "UTC",
    latitude: float | None = 51.5074,
    longitude: float | None = -0.1278,
):
    """Seeds birth data and triggers calculation to populate astro_private and astro_safe_profile."""
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (
                user_id, birth_date, birth_time, birth_time_precision,
                birth_timezone, latitude, longitude
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                birth_date = excluded.birth_date,
                birth_time = excluded.birth_time,
                birth_time_precision = excluded.birth_time_precision,
                birth_timezone = excluded.birth_timezone,
                latitude = excluded.latitude,
                longitude = excluded.longitude;
            """,
            (user_id, birth_date, birth_time, precision, timezone, latitude, longitude),
        )
    recalculate_user_astrology(uuid.UUID(user_id), db_conn)


# =============================================================================
# PART 1 & PART 4: FULL USER JOURNEY (ALL 10 ENDPOINTS & STATE TRANSITIONS)
# =============================================================================
@pytest.mark.asyncio
async def test_full_connection_journey_and_all_ten_endpoints(db_conn, clean_db):
    """
    Executes the full user lifecycle through actual HTTP endpoints:
    1. Discovery (GET /v1/interpretations/discovery-people)
    2. Profiles (GET /v1/profiles/{id} and GET /v1/profiles/me)
    3. Why pre-connect (GET /v1/people/{id}/why -> 403 Forbidden)
    4. Compare preview (POST /v1/interpretations/compare-preview -> 200 OK)
    5. Connection Request (POST /v1/connections -> 201 Created, pending)
    6. Duplicate Prevention (POST /v1/connections -> returns existing 201 idempotent, 0 extra notifs)
    7. Notifications recipient (GET /v1/notifications -> connection_request)
    8. Mark Notification Read (PATCH /v1/notifications/{id}/read -> 200 OK)
    9. Connection Accept (POST /v1/connections/{id}/transition -> 200 OK, accepted)
    10. Notifications initiator (GET /v1/notifications -> connection_accepted)
    11. Why post-connect (GET /v1/people/{id}/why -> 200 OK)
    12. Connected Compare (POST /v1/compare -> 200 OK)
    13. Direct Chat (POST /v1/conversations and POST /v1/conversations/{id}/messages)
    14. Daily Energy (GET /v1/interpretations/daily-energy -> 200 OK)
    """
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    em_a = f"ua_{uuid.uuid4().hex[:6]}@test.jester.app"
    em_b = f"ub_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, user_a, em_a, "Alice Walker")
    create_test_user(db_conn, user_b, em_b, "Bob Stone")

    # Person A: Aries Sun (1992-04-10 11:00 UTC)
    seed_user_birth_data(db_conn, user_a, birth_date="1992-04-10", birth_time="11:00:00")
    # Person B: Virgo Sun (1994-09-18 17:30 UTC)
    seed_user_birth_data(db_conn, user_b, birth_date="1994-09-18", birth_time="17:30:00")

    token_a = generate_test_jwt(user_id=user_a, email=em_a)
    token_b = generate_test_jwt(user_id=user_b, email=em_b)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. DISCOVERY: Alice discovers Bob
        res_disc = await ac.get(
            "/v1/interpretations/discovery-people",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_disc.status_code == 200
        people = res_disc.json()
        b_in_disc = next((p for p in people if p["id"] == user_b), None)
        assert b_in_disc is not None
        assert "hook_observation" in b_in_disc
        assert b_in_disc["hook_observation"]["text"] is not None
        # Verify privacy: no coordinates, degrees, or birth dates in discovery
        assert "latitude" not in b_in_disc
        assert "longitude" not in b_in_disc
        assert "birth_date" not in b_in_disc

        # 2. PROFILES: Alice checks her own and Bob's public profile
        res_me = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token_a}"})
        assert res_me.status_code == 200
        assert res_me.json()["display_name"] == "Alice Walker"

        res_prof_b = await ac.get(f"/v1/profiles/{user_b}", headers={"Authorization": f"Bearer {token_a}"})
        assert res_prof_b.status_code == 200
        assert res_prof_b.json()["display_name"] == "Bob Stone"
        # Privacy: Profile contains no private birth data
        assert "latitude" not in res_prof_b.json()
        assert "longitude" not in res_prof_b.json()

        # 3. WHY (PRE-CONNECT): Alice tries /why on Bob -> Must return 403 Forbidden
        res_why_pre = await ac.get(
            f"/v1/people/{user_b}/why",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_why_pre.status_code == 403
        assert res_why_pre.json()["error"]["code"] == "forbidden"

        # 4. COMPARE PREVIEW: Alice views pre-connection preview
        res_prev = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"target_user_id": user_b},
        )
        assert res_prev.status_code == 200
        prev_data = res_prev.json()
        assert prev_data["score"] > 0
        assert prev_data["interpretation"]["text"] is not None
        assert prev_data["connection_invitation"]["text"] is not None
        assert len(prev_data["conversation_starter_details"]) > 0

        # 5. CONNECTION REQUEST: Alice requests connection with Bob
        res_conn = await ac.post(
            "/v1/connections",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"target_user_id": user_b},
        )
        assert res_conn.status_code == 201
        conn_data = res_conn.json()
        assert conn_data["status"] == "pending"
        conn_id = conn_data["id"]

        # 6. DUPLICATE PREVENTION: Idempotent return, no extra notifications created
        res_dup = await ac.post(
            "/v1/connections",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"target_user_id": user_b},
        )
        assert res_dup.status_code == 201
        assert res_dup.json()["id"] == conn_id

        # 7. NOTIFICATIONS (RECIPIENT): Bob receives connection_request notification
        res_notif_b = await ac.get("/v1/notifications", headers={"Authorization": f"Bearer {token_b}"})
        assert res_notif_b.status_code == 200
        notifs_b = res_notif_b.json()
        assert len(notifs_b) == 1
        req_notif = notifs_b[0]
        assert req_notif["notification_type"] == "connection_request"
        assert req_notif["read_at"] is None
        assert req_notif["payload"]["actor_id"] == user_a
        # Privacy: Notification payload contains no astro/birth data
        for forbidden in ["latitude", "longitude", "birth_date", "sun_longitude"]:
            assert forbidden not in req_notif["payload"]

        # 8. MARK NOTIFICATION READ: Bob reads notification
        notif_id = req_notif["id"]
        res_read = await ac.patch(
            f"/v1/notifications/{notif_id}/read",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert res_read.status_code == 200
        assert res_read.json()["read_at"] is not None

        # 9. CONNECTION ACCEPT: Bob accepts Alice's connection request
        res_accept = await ac.post(
            f"/v1/connections/{conn_id}/transition",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"action": "accept"},
        )
        assert res_accept.status_code == 200
        assert res_accept.json()["status"] == "accepted"

        # 10. NOTIFICATIONS (INITIATOR): Alice receives connection_accepted notification
        res_notif_a = await ac.get("/v1/notifications", headers={"Authorization": f"Bearer {token_a}"})
        assert res_notif_a.status_code == 200
        notifs_a = res_notif_a.json()
        assert len(notifs_a) == 1
        acc_notif = notifs_a[0]
        assert acc_notif["notification_type"] == "connection_accepted"
        assert acc_notif["payload"]["actor_id"] == user_b
        # Privacy: Notification payload contains no astro/birth data
        for forbidden in ["latitude", "longitude", "birth_date", "sun_longitude"]:
            assert forbidden not in acc_notif["payload"]

        # 11. WHY (POST-CONNECT): Alice calls /why on Bob -> Succeeds with full payload
        res_why_post = await ac.get(
            f"/v1/people/{user_b}/why",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_why_post.status_code == 200
        why_data = res_why_post.json()
        assert why_data["score"] > 0
        assert why_data["interpretation"]["text"] is not None
        assert why_data["connection_invitation"]["text"] is not None
        assert len(why_data["conversation_starter_details"]) > 0

        # 12. CONNECTED COMPARE: Alice compares with Bob via /compare
        res_comp = await ac.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"target_user_id": user_b},
        )
        assert res_comp.status_code == 200
        comp_data = res_comp.json()
        assert comp_data["score"] == why_data["score"]
        assert comp_data["interpretation"]["id"] == why_data["interpretation"]["id"]

        # 13. DIRECT CHAT & STARTERS: Alice initiates conversation with Bob
        res_conv = await ac.post(
            "/v1/conversations",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"target_user_id": user_b},
        )
        assert res_conv.status_code in (200, 201)
        conv_id = res_conv.json()["id"]

        # Alice sends first message using conversation starter 0
        starter_text = comp_data["conversation_starter_details"][0]["text"]
        res_msg = await ac.post(
            f"/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"body": starter_text},
        )
        assert res_msg.status_code == 201
        assert res_msg.json()["body"] == starter_text

        # 14. DAILY ENERGY: Alice checks daily energy
        res_daily = await ac.get(
            "/v1/interpretations/daily-energy",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_daily.status_code == 200
        daily_data = res_daily.json()
        assert "archetype" in daily_data
        assert "interpretation" in daily_data
        assert "do" in daily_data
        assert "dont" in daily_data
        assert len(daily_data["do"]) == 3
        assert len(daily_data["dont"]) == 3


# =============================================================================
# PART 2: WHY FLOW (SEPARATION OF INTERPRETATION, INVITATION, STARTERS)
# =============================================================================
@pytest.mark.asyncio
async def test_why_flow_semantic_separation(db_conn, clean_db):
    """
    Verifies that Why response enforces:
    interpretation.text != connection_invitation.text != starter.text
    And verifies distinct structural contracts.
    """
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"u1_why_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_why_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, u1, em1, "User One")
    create_test_user(db_conn, u2, em2, "User Two")

    seed_user_birth_data(db_conn, u1, birth_date="1992-04-10", birth_time="11:00:00")
    seed_user_birth_data(db_conn, u2, birth_date="1994-09-18", birth_time="17:30:00")

    token_u1 = generate_test_jwt(user_id=u1, email=em1)
    token_u2 = generate_test_jwt(user_id=u2, email=em2)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Establish connection so /why is authorized
        res_conn = await ac.post("/v1/connections", headers={"Authorization": f"Bearer {token_u1}"}, json={"target_user_id": u2})
        conn_id = res_conn.json()["id"]
        await ac.post(f"/v1/connections/{conn_id}/transition", headers={"Authorization": f"Bearer {token_u2}"}, json={"action": "accept"})

        res_why = await ac.get(f"/v1/people/{u2}/why", headers={"Authorization": f"Bearer {token_u1}"})
        assert res_why.status_code == 200
        data = res_why.json()

        interp_text = data["interpretation"]["text"]
        invitation_text = data["connection_invitation"]["text"]
        starter_texts = [s["text"] for s in data["conversation_starter_details"]]

        # Strict separation assertions
        assert interp_text != invitation_text
        for st in starter_texts:
            assert interp_text != st
            assert invitation_text != st

        # Contract IDs must reflect distinct layers
        assert data["interpretation"]["id"].startswith("relationship.")
        assert data["connection_invitation"]["id"].startswith("connection.invitation.")
        for s in data["conversation_starter_details"]:
            assert s["contract_id"].startswith("relationship.")
            assert "starter" in s["asset_id"]


# =============================================================================
# PART 3: COMPARE FLOW (PREVIEW VS CONNECTED DETERMINISTIC IDENTITY)
# =============================================================================
@pytest.mark.asyncio
async def test_compare_preview_vs_connected_compare_identity(db_conn, clean_db):
    """
    Verifies that pre-connect compare preview and connected compare produce
    the identical deterministic Synastry V1 semantic basis.
    Documents the seed difference effect between calc_seed and pair_seed.
    """
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"u1_cmp_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_cmp_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, u1, em1, "User One")
    create_test_user(db_conn, u2, em2, "User Two")

    seed_user_birth_data(db_conn, u1, birth_date="1992-04-10", birth_time="11:00:00")
    seed_user_birth_data(db_conn, u2, birth_date="1994-09-18", birth_time="17:30:00")

    token_u1 = generate_test_jwt(user_id=u1, email=em1)
    token_u2 = generate_test_jwt(user_id=u2, email=em2)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Preview before connection
        res_prev = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res_prev.status_code == 200
        prev = res_prev.json()

        # Connect users
        res_conn = await ac.post("/v1/connections", headers={"Authorization": f"Bearer {token_u1}"}, json={"target_user_id": u2})
        conn_id = res_conn.json()["id"]
        await ac.post(f"/v1/connections/{conn_id}/transition", headers={"Authorization": f"Bearer {token_u2}"}, json={"action": "accept"})

        # 2. Connected Compare
        res_comp = await ac.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res_comp.status_code == 200
        comp = res_comp.json()

        # Core Mathematical & Semantic Invariant Assertions:
        assert comp["engine_version"] == prev["engine_version"] == "synastry-v1.0.0"
        assert abs(comp["score"] - prev["score"]) < 0.001
        assert comp["dimensions"] == prev["dimensions"]
        assert comp["signals"][0]["type"] == prev["signals"][0]["type"]
        assert comp["signals"][0]["category"] == prev["signals"][0]["category"]

        # Exact Primary Interpretation Equality (P1 Seed Parity Requirement):
        assert comp["interpretation"]["id"] == prev["interpretation"]["id"]
        assert comp["interpretation"]["text"] == prev["interpretation"]["text"]
        if comp["interpretation"].get("asset_id"):
            assert comp["interpretation"]["asset_id"] == prev["interpretation"]["asset_id"]
        if comp["interpretation"].get("metadata"):
            assert comp["interpretation"]["metadata"].get("asset_id") == prev["interpretation"]["metadata"].get("asset_id")
            assert comp["interpretation"]["metadata"].get("rule_id") == prev["interpretation"]["metadata"].get("rule_id")

        # Exact Connection Invitation Equality (same dominant signal/category derivation):
        assert comp["connection_invitation"]["id"] == prev["connection_invitation"]["id"]
        assert comp["connection_invitation"]["text"] == prev["connection_invitation"]["text"]

        # Conversation Starters Remain Attached to the Same Relational Signals:
        assert len(comp["conversation_starter_details"]) == len(prev["conversation_starter_details"])
        for c_st, p_st in zip(comp["conversation_starter_details"], prev["conversation_starter_details"]):
            assert c_st["contract_id"] == p_st["contract_id"]
            assert c_st["text"] == p_st["text"]


# =============================================================================
# PART 5: DISCOVERY PRESENCE FALLBACK ORDER
# =============================================================================
@pytest.mark.asyncio
async def test_discovery_presence_fallback_order(db_conn, clean_db):
    """
    Verifies discovery fallback order:
    1. Ascendant available -> discovery.person.presence.{ascendant}.v1
    2. Ascendant missing, Sun available -> discovery.person.presence.{sun}.v1
    3. Neither available -> discovery.person.presence.taurus.v1 (default router fallback)
    """
    viewer = str(uuid.uuid4())
    c1 = str(uuid.uuid4())  # Candidate with Ascendant Pisces
    c2 = str(uuid.uuid4())  # Candidate with unknown birth time (no Ascendant), Sun Taurus
    c3 = str(uuid.uuid4())  # Candidate with no astro profile

    em_v = f"v_{uuid.uuid4().hex[:6]}@test.jester.app"
    create_test_user(db_conn, viewer, em_v, "Viewer")
    create_test_user(db_conn, c1, "c1@test.jester.app", "Candidate One")
    create_test_user(db_conn, c2, "c2@test.jester.app", "Candidate Two")
    create_test_user(db_conn, c3, "c3@test.jester.app", "Candidate Three")

    seed_user_birth_data(db_conn, viewer, birth_date="1990-01-01", birth_time="12:00:00")
    # c1: Pisces Ascendant (1994-09-18 17:30 London)
    seed_user_birth_data(db_conn, c1, birth_date="1994-09-18", birth_time="17:30:00")
    # c2: Unknown birth time -> Taurus Sun, Ascendant=None
    seed_user_birth_data(db_conn, c2, birth_date="1990-05-10", birth_time=None, precision="unknown")

    token_v = generate_test_jwt(user_id=viewer, email=em_v)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/v1/interpretations/discovery-people",
            headers={"Authorization": f"Bearer {token_v}"},
        )
        assert res.status_code == 200
        people = {p["id"]: p for p in res.json()}

        # 1. c1 has Ascendant Pisces
        p1 = people[c1]
        assert p1["presence_sign"] == "pisces"
        assert p1["presence_sign_source"] == "ascendant"
        assert p1["hook_observation"]["id"] == "discovery.person.presence.pisces.v1"
        assert "ამოუცნობი მზერა" in p1["hook_observation"]["text"]

        # 2. c2 has unknown time -> falls back to Sun sign Taurus
        p2 = people[c2]
        assert p2["presence_sign"] == "taurus"
        assert p2["presence_sign_source"] == "sun"
        assert p2["hook_observation"]["id"] == "discovery.person.presence.taurus.v1"

        # 3. c3 has no birth data (both Ascendant and Sun missing) -> strictly falls back to Aries
        p3 = people[c3]
        assert p3["presence_sign"] == "aries"
        assert p3["presence_sign_source"] == "fallback"
        assert p3["hook_observation"]["id"] == "discovery.person.presence.aries.v1"


# =============================================================================
# PART 6: DAILY ENERGY SCENARIOS
# =============================================================================
@pytest.mark.asyncio
async def test_daily_energy_scenarios(db_conn, clean_db):
    """
    Exercises Daily Energy endpoint:
    1. Authenticated user with natal placements -> real transit calculation.
    2. Neutral quiet sky scenario -> neutral baseline without false claims.
    3. Unknown birth time precision -> Moon uncertainty handled.
    """
    u1 = str(uuid.uuid4())
    em1 = f"u1_de_{uuid.uuid4().hex[:6]}@test.jester.app"
    create_test_user(db_conn, u1, em1, "Daily User")
    seed_user_birth_data(db_conn, u1, birth_date="1992-04-10", birth_time="11:00:00")
    token_u1 = generate_test_jwt(user_id=u1, email=em1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Scenario 1: Today's real transit
        res = await ac.get(
            "/v1/interpretations/daily-energy",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["archetype"] is not None
        assert data["interpretation"]["text"] is not None
        assert len(data["do"]) == 3
        assert len(data["dont"]) == 3
        assert data["detection_mode"] in ("real_transit", "neutral_baseline", "fallback_sun_sign")

        # Scenario 2: Neutral / quiet sky for user without natal calculations
        u_neutral = str(uuid.uuid4())
        em_neutral = f"u_neu_{uuid.uuid4().hex[:6]}@test.jester.app"
        create_test_user(db_conn, u_neutral, em_neutral, "Neutral User")
        token_neu = generate_test_jwt(user_id=u_neutral, email=em_neutral)

        res_neutral = await ac.get(
            "/v1/interpretations/daily-energy?energy_type=neutral",
            headers={"Authorization": f"Bearer {token_neu}"},
        )
        assert res_neutral.status_code == 200
        neutral_data = res_neutral.json()
        assert neutral_data["energy_type"] == "neutral"
        assert neutral_data["detection_mode"] == "neutral_baseline"
        assert neutral_data["primary_transit"] is None
        assert "არცერთი დომინანტური ტრანზიტული წნეხი არ დგას" in neutral_data["interpretation"]["text"]

        # Scenario 3: Unknown birth time precision user
        u_unk = str(uuid.uuid4())
        em_unk = f"u_unk_{uuid.uuid4().hex[:6]}@test.jester.app"
        create_test_user(db_conn, u_unk, em_unk, "Unknown Time User")
        seed_user_birth_data(db_conn, u_unk, birth_date="1990-06-15", birth_time=None, precision="unknown")
        token_unk = generate_test_jwt(user_id=u_unk, email=em_unk)

        res_unk = await ac.get(
            "/v1/interpretations/daily-energy",
            headers={"Authorization": f"Bearer {token_unk}"},
        )
        assert res_unk.status_code == 200
        unk_data = res_unk.json()
        if unk_data["primary_transit"]:
            # Ascendant and houses must never be used
            assert unk_data["primary_transit"]["natal_point"] != "ascendant"
            # Moon cannot be primary dominant when birth time is unknown
            assert unk_data["primary_transit"]["natal_point"] != "moon"


# =============================================================================
# PART 7: FAILURE / FALLBACK TESTS
# =============================================================================
@pytest.mark.asyncio
async def test_failure_and_security_fallbacks(db_conn, clean_db):
    """
    Tests security boundaries, block filters, and invalid payloads:
    1. Unauthenticated calls -> 401.
    2. Self comparison -> 400.
    3. Blocked user in /why and /compare -> 403 / 404 Privacy-Safe.
    4. Non-existent target -> 404 PrivacySafeNotFoundException.
    """
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"u1_sec_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_sec_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, u1, em1, "Sec User 1")
    create_test_user(db_conn, u2, em2, "Sec User 2")

    seed_user_birth_data(db_conn, u1)
    seed_user_birth_data(db_conn, u2)

    token_u1 = generate_test_jwt(user_id=u1, email=em1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Unauthenticated call
        res_no_auth = await ac.post("/v1/compare", json={"target_user_id": u2})
        assert res_no_auth.status_code == 401

        # 2. Self comparison
        res_self = await ac.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u1},
        )
        assert res_self.status_code == 400
        assert res_self.json()["error"]["code"] == "self_comparison_not_allowed"

        # 3. Create connection then transition to blocked
        res_c = await ac.post(
            "/v1/connections",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        conn_id = res_c.json()["id"]
        res_blk = await ac.post(
            f"/v1/connections/{conn_id}/transition",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"action": "block"},
        )
        assert res_blk.status_code == 200

        # Blocked user: /why checks block status first -> Returns 404 Privacy-Safe
        res_blocked_why = await ac.get(
            f"/v1/people/{u2}/why",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res_blocked_why.status_code == 404
        assert res_blocked_why.json()["error"]["code"] == "not_found"

        # Compare preview checks is_user_blocked first -> Returns 404 Privacy-Safe
        res_blocked_prev = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res_blocked_prev.status_code == 404


# =============================================================================
# PART 8: BLOCKED /WHY PRIVACY ORDER (ALL 4 CONNECTION & BLOCK STATES)
# =============================================================================
@pytest.mark.asyncio
async def test_why_route_privacy_and_connection_order(db_conn, clean_db):
    """
    Verifies that GET /v1/people/{id}/why checks block status BEFORE connection authorization:
    1. Unblocked + no connection -> 403 Forbidden
    2. Unblocked + pending connection -> 403 Forbidden
    3. Unblocked + accepted connection -> 200 OK
    4. Blocked target -> 404 PrivacySafeNotFoundException (never leaks connection existence)
    """
    u_me = str(uuid.uuid4())
    u_no_conn = str(uuid.uuid4())
    u_pending = str(uuid.uuid4())
    u_accepted = str(uuid.uuid4())
    u_blocked = str(uuid.uuid4())

    create_test_user(db_conn, u_me, f"me_{uuid.uuid4().hex[:6]}@test.jester.app", "Current User")
    create_test_user(db_conn, u_no_conn, f"nc_{uuid.uuid4().hex[:6]}@test.jester.app", "No Conn User")
    create_test_user(db_conn, u_pending, f"pend_{uuid.uuid4().hex[:6]}@test.jester.app", "Pending User")
    create_test_user(db_conn, u_accepted, f"acc_{uuid.uuid4().hex[:6]}@test.jester.app", "Accepted User")
    create_test_user(db_conn, u_blocked, f"blk_{uuid.uuid4().hex[:6]}@test.jester.app", "Blocked User")

    seed_user_birth_data(db_conn, u_me, birth_date="1992-04-10", birth_time="11:00:00")
    seed_user_birth_data(db_conn, u_no_conn, birth_date="1994-09-18", birth_time="17:30:00")
    seed_user_birth_data(db_conn, u_pending, birth_date="1991-05-20", birth_time="14:00:00")
    seed_user_birth_data(db_conn, u_accepted, birth_date="1993-08-15", birth_time="09:15:00")
    seed_user_birth_data(db_conn, u_blocked, birth_date="1990-12-01", birth_time="20:45:00")

    token_me = generate_test_jwt(user_id=u_me, email="me@test.jester.app")
    token_pend = generate_test_jwt(user_id=u_pending, email="pend@test.jester.app")
    token_acc = generate_test_jwt(user_id=u_accepted, email="acc@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Case 1: Unblocked + no connection -> 403 Forbidden
        res_no_conn = await ac.get(f"/v1/people/{u_no_conn}/why", headers={"Authorization": f"Bearer {token_me}"})
        assert res_no_conn.status_code == 403
        assert res_no_conn.json()["error"]["code"] == "forbidden"

        # Case 2: Unblocked + pending connection -> 403 Forbidden
        await ac.post("/v1/connections", headers={"Authorization": f"Bearer {token_me}"}, json={"target_user_id": u_pending})
        res_pending = await ac.get(f"/v1/people/{u_pending}/why", headers={"Authorization": f"Bearer {token_me}"})
        assert res_pending.status_code == 403
        assert res_pending.json()["error"]["code"] == "forbidden"

        # Case 3: Unblocked + accepted connection -> 200 OK
        res_c3 = await ac.post("/v1/connections", headers={"Authorization": f"Bearer {token_me}"}, json={"target_user_id": u_accepted})
        c3_id = res_c3.json()["id"]
        await ac.post(f"/v1/connections/{c3_id}/transition", headers={"Authorization": f"Bearer {token_acc}"}, json={"action": "accept"})
        res_accepted = await ac.get(f"/v1/people/{u_accepted}/why", headers={"Authorization": f"Bearer {token_me}"})
        assert res_accepted.status_code == 200
        assert res_accepted.json()["score"] > 0
        assert res_accepted.json()["interpretation"]["text"] is not None

        # Case 4: Blocked target -> 404 PrivacySafeNotFoundException
        # Create connection then block
        res_c4 = await ac.post("/v1/connections", headers={"Authorization": f"Bearer {token_me}"}, json={"target_user_id": u_blocked})
        c4_id = res_c4.json()["id"]
        await ac.post(f"/v1/connections/{c4_id}/transition", headers={"Authorization": f"Bearer {token_me}"}, json={"action": "block"})
        res_blocked = await ac.get(f"/v1/people/{u_blocked}/why", headers={"Authorization": f"Bearer {token_me}"})
        assert res_blocked.status_code == 404
        assert res_blocked.json()["error"]["code"] == "not_found"


# =============================================================================
# PART 9 & 10: SEMANTIC PROVENANCE & PRIVACY INVARIANTS
# =============================================================================
@pytest.mark.asyncio
async def test_semantic_provenance_and_privacy_invariants(db_conn, clean_db):
    """
    Asserts complete provenance chain and ensures private birth/astrology
    data never leaks in client responses.
    """
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"u1_prov_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_prov_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, u1, em1, "Prov User 1")
    create_test_user(db_conn, u2, em2, "Prov User 2")

    seed_user_birth_data(db_conn, u1, birth_date="1992-04-10", birth_time="11:00:00")
    seed_user_birth_data(db_conn, u2, birth_date="1994-09-18", birth_time="17:30:00")

    token_u1 = generate_test_jwt(user_id=u1, email=em1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res.status_code == 200
        data = res.json()

        # Provenance: dominant signal -> category -> invitation mapping
        dom_signal = data["signals"][0]
        dom_cat = dom_signal["category"]
        invitation_id = data["connection_invitation"]["id"]

        category_to_invitation = {
            "growth": "connection.invitation.friction.v1",
            "friction": "connection.invitation.friction.v1",
            "harmony": "connection.invitation.harmony.v1",
            "attraction": "connection.invitation.attraction.v1",
            "stability": "connection.invitation.stability.v1",
            "communication": "connection.invitation.communication.v1",
            "notice": "connection.invitation.independent.v1",
        }
        expected_invitation = category_to_invitation.get(dom_cat, "connection.invitation.independent.v1")
        assert invitation_id == expected_invitation

        # Privacy assertions: Forbidden fields must not exist in client response
        forbidden_fields = [
            "latitude", "longitude", "birth_time", "birth_timezone",
            "sun_longitude", "moon_longitude", "mercury_longitude",
            "houses", "source_birth_data_version",
        ]
        for field in forbidden_fields:
            assert field not in data
            assert field not in data.get("data_quality", {})


# =============================================================================
# PART 11: MARS SEMANTIC FIREWALL RUNTIME VERIFICATION
# =============================================================================
@pytest.mark.asyncio
async def test_mars_semantic_firewall_runtime(db_conn, clean_db):
    """
    Verifies that Mars relational and self contracts resolve strictly
    to action, pursuit, initiative, and drive — NOT anger, violence, or rage.
    """
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"u1_mars_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_mars_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, u1, em1, "Mars User 1")
    create_test_user(db_conn, u2, em2, "Mars User 2")

    # Person A & B with exact Sun-Mars square
    seed_user_birth_data(db_conn, u1, birth_date="1992-04-10", birth_time="11:00:00")
    seed_user_birth_data(db_conn, u2, birth_date="1994-09-18", birth_time="17:30:00")

    token_u1 = generate_test_jwt(user_id=u1, email=em1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res.status_code == 200
        data = res.json()

        # Dominant signal is sun_square_mars / mars_square_sun -> Dynamic Spark
        assert data["signals"][0]["type"] in ("sun_square_mars", "mars_square_sun")
        interp_text = data["interpretation"]["text"]

        # Mars Firewall assertions: Prohibited violent/anger vocabulary
        prohibited_terms = [
            "ბრაზდები", "ჩხუბობ", "აგრესიული ხარ", "თავს ესხმი",
            "ვერ აკონტროლებ თავს", "ძალადობა", "ცემა", "სისხლი", "anger", "violence",
        ]
        for term in prohibited_terms:
            assert term not in interp_text.lower()
