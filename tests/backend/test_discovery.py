import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn, clean_db, set_auth_context


@pytest.mark.asyncio
async def test_discovery_requires_authentication():
    """Unauthenticated calls to /v1/interpretations/discovery-people must return 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/v1/interpretations/discovery-people")
        assert res.status_code == 401
        assert res.json()["error"]["code"] in ["missing_token", "unauthorized"]


@pytest.mark.asyncio
async def test_discovery_rejects_viewer_impersonation(db_conn, clean_db):
    """Authenticated caller cannot request discovery calculated as another user."""
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"u1_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_{uuid.uuid4().hex[:6]}@test.jester.app"
    create_test_user(db_conn, u1, em1, "Viewer One")
    create_test_user(db_conn, u2, em2, "Target Two")

    token_u1 = generate_test_jwt(user_id=u1, email=em1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Impersonating U2 with U1's token must return 403 Forbidden
        res = await ac.get(
            f"/v1/interpretations/discovery-people?viewer_id={u2}",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "forbidden_viewer_impersonation"

        # Supplying own ID or omitting query param succeeds
        res_self = await ac.get(
            f"/v1/interpretations/discovery-people?viewer_id={u1}",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res_self.status_code == 200

        res_no_param = await ac.get(
            "/v1/interpretations/discovery-people",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res_no_param.status_code == 200


@pytest.mark.asyncio
async def test_discovery_excludes_blocked_users_and_viewer(db_conn, clean_db):
    """
    Discovery must strictly exclude:
    1. The authenticated viewer.
    2. Users blocked by the viewer.
    3. Users who blocked the viewer.
    4. Non-discoverable profiles (is_discoverable = false).
    """
    viewer = str(uuid.uuid4())
    candidate_normal = str(uuid.uuid4())
    candidate_blocked_by_viewer = str(uuid.uuid4())
    candidate_blocker_of_viewer = str(uuid.uuid4())
    candidate_hidden = str(uuid.uuid4())

    create_test_user(db_conn, viewer, f"v_{uuid.uuid4().hex[:6]}@test.jester.app", "Viewer")
    create_test_user(db_conn, candidate_normal, f"c_{uuid.uuid4().hex[:6]}@test.jester.app", "Normal Candidate")
    create_test_user(db_conn, candidate_blocked_by_viewer, f"b1_{uuid.uuid4().hex[:6]}@test.jester.app", "Blocked By Viewer")
    create_test_user(db_conn, candidate_blocker_of_viewer, f"b2_{uuid.uuid4().hex[:6]}@test.jester.app", "Blocker Of Viewer")
    create_test_user(db_conn, candidate_hidden, f"h_{uuid.uuid4().hex[:6]}@test.jester.app", "Hidden Candidate")

    # Set candidate_hidden as not discoverable
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute("UPDATE public.profiles SET is_discoverable = false WHERE id = %s;", (candidate_hidden,))

        # Create block connection: viewer blocked candidate_blocked_by_viewer
        # Canonical order: user_a_id = least, user_b_id = greatest
        u_a1, u_b1 = min(viewer, candidate_blocked_by_viewer), max(viewer, candidate_blocked_by_viewer)
        cur.execute(
            """
            INSERT INTO public.connections (id, user_a_id, user_b_id, status, initiated_by, blocked_by)
            VALUES (%s, %s, %s, 'blocked', %s, %s);
            """,
            (str(uuid.uuid4()), u_a1, u_b1, viewer, viewer),
        )

        # Create block connection: candidate_blocker_of_viewer blocked viewer
        u_a2, u_b2 = min(viewer, candidate_blocker_of_viewer), max(viewer, candidate_blocker_of_viewer)
        cur.execute(
            """
            INSERT INTO public.connections (id, user_a_id, user_b_id, status, initiated_by, blocked_by)
            VALUES (%s, %s, %s, 'blocked', %s, %s);
            """,
            (str(uuid.uuid4()), u_a2, u_b2, candidate_blocker_of_viewer, candidate_blocker_of_viewer),
        )

    token = generate_test_jwt(user_id=viewer, email="viewer@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/v1/interpretations/discovery-people",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        people = res.json()
        ids = [p["id"] for p in people]

        # 1. Viewer is excluded
        assert viewer not in ids

        # 2. Blocked by viewer is excluded
        assert candidate_blocked_by_viewer not in ids

        # 3. Blocker of viewer is excluded
        assert candidate_blocker_of_viewer not in ids

        # 4. Hidden profile is excluded
        assert candidate_hidden not in ids

        # 5. Normal candidate is present
        assert candidate_normal in ids


@pytest.mark.asyncio
async def test_discovery_returns_relationship_hook_and_score(db_conn, clean_db):
    """
    When birth data is available, discovery computes a real synastry score
    and generates a relationship-level hook observation (ME -> YOU).
    """
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"u1_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, u1, em1, "Alexandre")
    create_test_user(db_conn, u2, em2, "Natia")

    # Seed birth data so Swiss Ephemeris and Synastry engine compute real placements & signals
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
            VALUES 
                (%s, '1990-05-15', '12:00:00', 'exact', 'Asia/Tbilisi', 41.7151, 44.8271),
                (%s, '1992-10-20', '15:30:00', 'exact', 'Asia/Tbilisi', 41.7151, 44.8271);
            """,
            (u1, u2),
        )

    token = generate_test_jwt(user_id=u1, email=em1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/v1/interpretations/discovery-people",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        people = res.json()
        assert len(people) == 1
        target = people[0]
        assert target["id"] == u2
        assert target["display_name"] == "Natia"
        assert target["compatibility_score"] > 0
        assert target["hook_observation"] is not None
        assert len(target["hook_observation"]["text"]) > 0
        # Hook has relationship context or valid resolution
        assert target["hook_observation"]["locale"] == "ka"

