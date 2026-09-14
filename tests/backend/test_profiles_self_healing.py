"""
Tests for explicit profile initialization architecture.
Verifies that:
1. GET /v1/profiles/me is strictly read-oriented and returns 404 if profile does not exist.
2. POST /v1/profiles/initialize explicitly provisions the profile without side effects on GET.
3. Existing user edits are preserved and never overwritten by subsequent initialize calls.
4. Repeated POST /v1/profiles/initialize is idempotent.
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn


def create_auth_only_user(db_conn, user_id: str, email: str, raw_meta: dict | None = None):
    """Creates a user strictly in auth.users without creating a public.profiles row."""
    import json
    meta_json = json.dumps(raw_meta or {})
    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute(
            """
            INSERT INTO auth.users (id, email, raw_user_meta_data, role, aud)
            VALUES (%s, %s, %s::jsonb, 'authenticated', 'authenticated')
            ON CONFLICT (id) DO UPDATE SET raw_user_meta_data = EXCLUDED.raw_user_meta_data;
            """,
            (user_id, email, meta_json),
        )
        # Ensure no row exists in public.profiles for this user
        cur.execute("DELETE FROM public.profiles WHERE id = %s;", (user_id,))


@pytest.mark.asyncio
async def test_get_profile_me_returns_404_when_uninitialized(db_conn):
    """
    Architectural invariant:
    Given: Authenticated user exists in auth.users, but NOT in public.profiles.
    When: GET /v1/profiles/me
    Then: 404 Not Found, NO row is created in public.profiles (GET is strictly read-oriented).
    """
    uid = str(uuid.uuid4())
    prefix = f"no_heal_{uid[:8]}"
    email = f"{prefix}@test.jester.app"
    create_auth_only_user(db_conn, uid, email)

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 404

        # Verify database record was NOT created by GET
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (uid,))
            row = cur.fetchone()
            assert row is None


@pytest.mark.asyncio
async def test_explicit_initialize_creates_profile(db_conn):
    """
    Given: Authenticated user with no profile row.
    When: POST /v1/profiles/initialize
    Then: 200 OK, profile created, display_name derived, and GET /v1/profiles/me succeeds.
    """
    uid = str(uuid.uuid4())
    prefix = f"init_a_{uid[:8]}"
    email = f"{prefix}@test.jester.app"
    create_auth_only_user(db_conn, uid, email)

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Step 1: Explicitly initialize
        init_res = await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Levan", "last_name": "Kapanadze"},
        )
        assert init_res.status_code == 200
        data = init_res.json()
        assert data["id"] == uid
        assert data["first_name"] == "Levan"
        assert data["last_name"] == "Kapanadze"
        assert data["display_name"] == "Levan K."
        assert data["onboarding_completed"] is False

        # Step 2: Now GET /v1/profiles/me succeeds
        get_res = await ac.get(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_res.status_code == 200
        assert get_res.json()["display_name"] == "Levan K."


@pytest.mark.asyncio
async def test_initialize_from_auth_metadata(db_conn):
    """
    Given: OAuth user with Google/Apple metadata in auth.users.raw_user_meta_data.
    When: POST /v1/profiles/initialize without payload.
    Then: Metadata (given_name/family_name) is used to initialize profile.
    """
    uid = str(uuid.uuid4())
    email = f"oauth_user_{uid[:8]}@example.com"
    raw_meta = {
        "given_name": "Giorgi",
        "family_name": "Beridze",
        "picture": "https://example.com/avatar.jpg",
    }
    create_auth_only_user(db_conn, uid, email, raw_meta=raw_meta)

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        init_res = await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert init_res.status_code == 200
        data = init_res.json()
        assert data["id"] == uid
        assert data["first_name"] == "Giorgi"
        assert data["last_name"] == "Beridze"
        assert data["display_name"] == "Giorgi B."
        assert data["avatar_url"] == "https://example.com/avatar.jpg"


@pytest.mark.asyncio
async def test_existing_profile_is_not_overwritten_by_initialize(db_conn):
    """
    Given: User has already established profile with custom display_name and bio.
    When: POST /v1/profiles/initialize called with conflicting or OAuth metadata.
    Then: Existing user edits are preserved and NOT overwritten.
    """
    uid = str(uuid.uuid4())
    email = f"custom_user_{uid[:8]}@test.jester.app"
    create_test_user(db_conn, uid, email, display_name="Established Pioneer")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            UPDATE public.profiles
            SET first_name = 'OriginalFirst', last_name = 'OriginalLast', bio = 'Original bio'
            WHERE id = %s;
            """,
            (uid,),
        )

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "NewOAuthFirst", "last_name": "NewOAuthLast"},
        )
        assert res.status_code == 200
        data = res.json()
        # Original edits MUST be preserved
        assert data["first_name"] == "OriginalFirst"
        assert data["last_name"] == "OriginalLast"
        assert data["display_name"] == "Established Pioneer"
        assert data["bio"] == "Original bio"


@pytest.mark.asyncio
async def test_repeated_initialize_is_idempotent(db_conn):
    """
    Given: User with no initial profile.
    When: POST /v1/profiles/initialize called 3 consecutive times.
    Then: All return 200 OK with identical data, exactly 1 row in public.profiles.
    """
    uid = str(uuid.uuid4())
    prefix = f"idem_{uid[:8]}"
    email = f"{prefix}@test.jester.app"
    create_auth_only_user(db_conn, uid, email)

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"}, json={"first_name": "Anna", "last_name": "Kiknadze"})
        res2 = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})
        res3 = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})

        assert res1.status_code == 200
        assert res2.status_code == 200
        assert res3.status_code == 200

        assert res1.json()["id"] == uid
        assert res2.json()["id"] == uid
        assert res3.json()["id"] == uid

        assert res1.json()["display_name"] == "Anna K."
        assert res2.json()["display_name"] == "Anna K."
        assert res3.json()["display_name"] == "Anna K."

        with db_conn.cursor() as cur:
            cur.execute("SELECT count(*) as cnt FROM public.profiles WHERE id = %s;", (uid,))
            cnt = cur.fetchone()["cnt"]
            assert cnt == 1
