"""
Tests for Profile Identity V1: first_name, last_name, display_name.
Verifies column existence, API responses, updates, and backward-compatible self-healing.
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import db_conn
from tests.backend.test_profiles_self_healing import create_auth_only_user


def test_profile_identity_columns_exist(db_conn):
    """Verifies that first_name and last_name columns exist in public.profiles and are nullable."""
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'profiles'
              AND column_name IN ('first_name', 'last_name', 'display_name')
            ORDER BY column_name;
        """)
        rows = {r["column_name"]: {"type": r["data_type"], "nullable": r["is_nullable"]} for r in cur.fetchall()}
        
        assert "display_name" in rows
        assert rows["display_name"]["nullable"] == "NO"
        
        assert "first_name" in rows
        assert rows["first_name"]["nullable"] == "YES"
        
        assert "last_name" in rows
        assert rows["last_name"]["nullable"] == "YES"


@pytest.mark.asyncio
async def test_initialized_profile_has_null_names_when_not_provided(db_conn):
    """
    Given: An auth user without a profile row.
    When: POST /v1/profiles/initialize is called with empty payload.
    Then: Profile is created with display_name=email_prefix and first_name/last_name=None.
    """
    uid = str(uuid.uuid4())
    prefix = f"identity_init_{uid[:8]}"
    email = f"{prefix}@test.jester.app"
    create_auth_only_user(db_conn, uid, email)

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # GET returns 404 before initialization
        get_before = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
        assert get_before.status_code == 404

        # Explicit initialization
        res = await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == uid
        assert data["display_name"] == prefix
        assert data["first_name"] is None
        assert data["last_name"] is None


@pytest.mark.asyncio
async def test_patch_profile_identity_fields(db_conn):
    """
    Given: An authenticated user with an initialized profile.
    When: PATCH /v1/profiles/me with first_name, last_name, and display_name.
    Then: 200 OK, response reflects updated values, and DB row persists all three.
    """
    uid = str(uuid.uuid4())
    email = f"identity_patch_{uid[:8]}@test.jester.app"
    create_auth_only_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Initialize profile first
        await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})

        # 1. Update identity
        patch_res = await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "Nika",
                "last_name": "Iordanishvili",
                "display_name": "Nika",
                "city": "Tbilisi",
            },
        )
        assert patch_res.status_code == 200
        patch_data = patch_res.json()
        assert patch_data["first_name"] == "Nika"
        assert patch_data["last_name"] == "Iordanishvili"
        assert patch_data["display_name"] == "Nika"
        assert patch_data["city"] == "Tbilisi"

        # 2. Verify subsequent GET /v1/profiles/me returns persisted values
        get_res = await ac.get(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["first_name"] == "Nika"
        assert get_data["last_name"] == "Iordanishvili"
        assert get_data["display_name"] == "Nika"

        # 3. Verify direct DB persistence
        with db_conn.cursor() as cur:
            cur.execute("SELECT first_name, last_name, display_name, city FROM public.profiles WHERE id = %s;", (uid,))
            db_row = cur.fetchone()
            assert db_row is not None
            assert db_row["first_name"] == "Nika"
            assert db_row["last_name"] == "Iordanishvili"
            assert db_row["display_name"] == "Nika"
            assert db_row["city"] == "Tbilisi"


@pytest.mark.asyncio
async def test_partial_name_updates(db_conn):
    """
    Given: An established profile with first_name, last_name, display_name.
    When: Only last_name is patched.
    Then: first_name and display_name are preserved.
    """
    uid = str(uuid.uuid4())
    email = f"partial_{uid[:8]}@test.jester.app"
    create_auth_only_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Initialize profile first
        await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Alex", "last_name": "Smith"},
        )

        # Explicit display name override
        await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"display_name": "AlexS"},
        )

        # Partial update: only last_name
        res = await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"last_name": "Johnson"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["first_name"] == "Alex"
        assert data["last_name"] == "Johnson"
        assert data["display_name"] == "AlexS"
