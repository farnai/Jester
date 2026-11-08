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

    cand_tag = uuid.uuid4().hex[:6]
    create_test_user(db_conn, viewer, f"v_{cand_tag}@test.jester.app", f"Viewer_{cand_tag}")
    create_test_user(db_conn, candidate_normal, f"c_{cand_tag}@test.jester.app", f"Normal_{cand_tag}")
    create_test_user(db_conn, candidate_blocked_by_viewer, f"b1_{cand_tag}@test.jester.app", f"Blocked1_{cand_tag}")
    create_test_user(db_conn, candidate_blocker_of_viewer, f"b2_{cand_tag}@test.jester.app", f"Blocked2_{cand_tag}")
    create_test_user(db_conn, candidate_hidden, f"h_{cand_tag}@test.jester.app", f"Hidden_{cand_tag}")

    # Set candidate_hidden as not discoverable and seed adult birth_data for discoverability
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute("UPDATE public.profiles SET is_discoverable = false WHERE id = %s;", (candidate_hidden,))
        cur.execute("""
            INSERT INTO public.birth_data (user_id, birth_date, birth_time_precision, birth_timezone)
            VALUES 
                (%s, '1995-01-01', 'unknown', 'UTC'),
                (%s, '1995-01-01', 'unknown', 'UTC'),
                (%s, '1995-01-01', 'unknown', 'UTC'),
                (%s, '1995-01-01', 'unknown', 'UTC'),
                (%s, '1995-01-01', 'unknown', 'UTC')
            ON CONFLICT (user_id) DO NOTHING;
        """, (viewer, candidate_normal, candidate_blocked_by_viewer, candidate_blocker_of_viewer, candidate_hidden))

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
            f"/v1/interpretations/discovery-people?q={cand_tag}",
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
async def test_discovery_does_not_calculate_missing_astrology_or_synastry(db_conn, clean_db):
    """Birth data alone must not trigger per-candidate computation in a feed."""
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"u1_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_{uuid.uuid4().hex[:6]}@test.jester.app"

    natia_name = f"Natia_{u2[:6]}"
    create_test_user(db_conn, u1, em1, "Alexandre")
    create_test_user(db_conn, u2, em2, natia_name)

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
            f"/v1/interpretations/discovery-people?q={natia_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        people = res.json()
        target = next((p for p in people if p["id"] == u2), None)
        assert target is not None
        assert target["display_name"] == natia_name
        assert target["compatibility_score"] is None
        assert target["hook_observation"] is None
        with db_conn.cursor() as cur:
            cur.execute('SELECT count(*) FROM public.astro_private WHERE user_id IN (%s,%s)', (u1,u2))
            assert cur.fetchone()['count'] == 0


@pytest.mark.asyncio
async def test_discovery_strictly_enforces_18_plus_across_endpoints(db_conn, clean_db):
    """
    Social Discovery must strictly enforce the 18+ requirement across all endpoints:
    1. Users under 18 years old are strictly excluded.
    2. Users without verified birth date are strictly excluded.
    3. Adult users (>= 18) are included with correctly computed age.
    """
    viewer = str(uuid.uuid4())
    adult_cand = str(uuid.uuid4())
    minor_cand = str(uuid.uuid4())
    no_birth_cand = str(uuid.uuid4())

    adult_name = f"Adult_{adult_cand[:6]}"
    create_test_user(db_conn, viewer, f"v_{uuid.uuid4().hex[:6]}@test.jester.app", "Viewer")
    create_test_user(db_conn, adult_cand, f"a_{uuid.uuid4().hex[:6]}@test.jester.app", adult_name)
    create_test_user(db_conn, minor_cand, f"m_{uuid.uuid4().hex[:6]}@test.jester.app", "Minor Candidate")
    create_test_user(db_conn, no_birth_cand, f"n_{uuid.uuid4().hex[:6]}@test.jester.app", "No Birth Candidate")

    # Set exact birth dates:
    # Adult: 22 years old (born 2004)
    # Minor: 16 years old (born 2010)
    # No birth: delete from birth_data
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            "INSERT INTO public.birth_data (user_id, birth_date, birth_time_precision, birth_timezone) VALUES (%s, (current_date - interval '22 years')::date, 'unknown', 'UTC') ON CONFLICT (user_id) DO UPDATE SET birth_date = EXCLUDED.birth_date;",
            (adult_cand,),
        )
        cur.execute(
            "INSERT INTO public.birth_data (user_id, birth_date, birth_time_precision, birth_timezone) VALUES (%s, (current_date - interval '16 years')::date, 'unknown', 'UTC') ON CONFLICT (user_id) DO UPDATE SET birth_date = EXCLUDED.birth_date;",
            (minor_cand,),
        )
        cur.execute(
            "DELETE FROM public.birth_data WHERE user_id = %s;",
            (no_birth_cand,),
        )

    token = generate_test_jwt(user_id=viewer, email="v@test.jester.app")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Check /v1/discovery/people with newest order to locate freshly created test candidate
        res_deck = await ac.get("/v1/discovery/people?order=newest", headers=headers)
        assert res_deck.status_code == 200
        deck_ids = [p["id"] for p in res_deck.json()["items"]]
        assert adult_cand in deck_ids
        assert minor_cand not in deck_ids
        assert no_birth_cand not in deck_ids

        # Verify age calculation
        adult_item = next(p for p in res_deck.json()["items"] if p["id"] == adult_cand)
        assert adult_item["age"] == 22

        # 2. Check /v1/discovery/people?order=newest
        res_newest = await ac.get("/v1/discovery/people?order=newest", headers=headers)
        assert res_newest.status_code == 200
        newest_ids = [p["id"] for p in res_newest.json()["items"]]
        assert adult_cand in newest_ids
        assert minor_cand not in newest_ids
        assert no_birth_cand not in newest_ids

        # 3. Check /v1/interpretations/discovery-people with candidate filter
        res_legacy = await ac.get(f"/v1/interpretations/discovery-people?q={adult_name}", headers=headers)
        assert res_legacy.status_code == 200
        legacy_ids = [p["id"] for p in res_legacy.json()]
        assert adult_cand in legacy_ids
        assert minor_cand not in legacy_ids
        assert no_birth_cand not in legacy_ids


