"""
Regression tests for self-healing profile auto-provisioning.
Verifies that newly registered auth-only users automatically receive a default profile on GET /v1/profiles/me,
and that existing profiles remain untouched and idempotent.
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn


def create_auth_only_user(db_conn, user_id: str, email: str):
    """Creates a user strictly in auth.users without creating a public.profiles row."""
    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute(
            """
            INSERT INTO auth.users (id, email, raw_user_meta_data, role, aud)
            VALUES (%s, %s, '{}'::jsonb, 'authenticated', 'authenticated')
            ON CONFLICT (id) DO NOTHING;
            """,
            (user_id, email),
        )
        # Ensure no row exists in public.profiles for this user
        cur.execute("DELETE FROM public.profiles WHERE id = %s;", (user_id,))


@pytest.mark.asyncio
async def test_missing_profile_is_auto_created_on_get(db_conn):
    """
    Test Case A:
    Given: Authenticated user exists in auth.users, but NOT in public.profiles.
    When: GET /v1/profiles/me
    Then: 200 OK, profile.id == user_id, display_name == email prefix, and DB row is created.
    """
    uid = str(uuid.uuid4())
    prefix = f"self_heal_a_{uid[:8]}"
    email = f"{prefix}@test.jester.app"
    create_auth_only_user(db_conn, uid, email)

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == uid
        assert data["display_name"] == prefix

        # Verify database record exists
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (uid,))
            row = cur.fetchone()
            assert row is not None
            assert row["display_name"] == prefix


@pytest.mark.asyncio
async def test_profile_update_works_after_self_healing(db_conn):
    """
    Test Case B:
    Given: Authenticated user with no initial profile.
    When: GET /v1/profiles/me (auto-creates) -> PATCH /v1/profiles/me (updates fields).
    Then: 200 OK on PATCH, updated values persisted in database.
    """
    uid = str(uuid.uuid4())
    prefix = f"self_heal_b_{uid[:8]}"
    email = f"{prefix}@test.jester.app"
    create_auth_only_user(db_conn, uid, email)

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Step 1: Self-heal
        get_res = await ac.get(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_res.status_code == 200

        # Step 2: PATCH profile
        patch_res = await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "display_name": "Updated Explorer",
                "bio": "Stargazer & traveler",
                "city": "Batumi",
            },
        )
        assert patch_res.status_code == 200
        data = patch_res.json()
        assert data["display_name"] == "Updated Explorer"
        assert data["bio"] == "Stargazer & traveler"
        assert data["city"] == "Batumi"

        # Step 3: Verify DB persistence
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (uid,))
            row = cur.fetchone()
            assert row is not None
            assert row["display_name"] == "Updated Explorer"
            assert row["bio"] == "Stargazer & traveler"
            assert row["city"] == "Batumi"


@pytest.mark.asyncio
async def test_existing_profile_is_not_overwritten(db_conn):
    """
    Test Case C:
    Given: User with an already established profile (custom display_name and bio).
    When: GET /v1/profiles/me
    Then: 200 OK, existing custom display_name and bio are preserved (not replaced by email prefix).
    """
    uid = str(uuid.uuid4())
    email = f"custom_user_{uid[:8]}@test.jester.app"
    create_test_user(db_conn, uid, email, display_name="Established Pioneer")

    # Set custom bio
    with db_conn.cursor() as cur:
        cur.execute("UPDATE public.profiles SET bio = 'Original bio' WHERE id = %s;", (uid,))

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["display_name"] == "Established Pioneer"
        assert data["bio"] == "Original bio"


@pytest.mark.asyncio
async def test_repeated_get_is_idempotent(db_conn):
    """
    Test Case D:
    Given: User with no initial profile.
    When: GET /v1/profiles/me called 3 consecutive times.
    Then: All return 200 OK with identical data, exactly 1 row exists in public.profiles.
    """
    uid = str(uuid.uuid4())
    prefix = f"self_heal_d_{uid[:8]}"
    email = f"{prefix}@test.jester.app"
    create_auth_only_user(db_conn, uid, email)

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
        res2 = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
        res3 = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})

        assert res1.status_code == 200
        assert res2.status_code == 200
        assert res3.status_code == 200

        assert res1.json()["id"] == uid
        assert res2.json()["id"] == uid
        assert res3.json()["id"] == uid

        assert res1.json()["display_name"] == prefix
        assert res2.json()["display_name"] == prefix
        assert res3.json()["display_name"] == prefix

        # Verify exactly 1 row exists in public.profiles
        with db_conn.cursor() as cur:
            cur.execute("SELECT count(*) as cnt FROM public.profiles WHERE id = %s;", (uid,))
            cnt = cur.fetchone()["cnt"]
            assert cnt == 1
