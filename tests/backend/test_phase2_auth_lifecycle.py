"""
Comprehensive Phase 2 Authentication & Account Lifecycle test suite.

Covers:
1. Registration & profile initialization
2. Duplicate email handling & prevention
3. Login & identity mapping
4. Password reset integrity (preserves canonical identity)
5. Email verification state (unverified does not block initial entry)
6. Onboarding resume (persisted onboarding_step across sessions)
7. Authoritative onboarding completion validation (5 required fields)
8. NULL birth_time validity (birth_time is optional, no noon fallback)
9. display_name derivation (First L. from first_name and last_name)
10. OAuth profile initialization (Google / Apple metadata)
11. OAuth metadata non-overwrite invariant (never overwrites user edits)
12. Google identity architecture (auth.users.id == public.profiles.id)
13. Apple identity architecture (private relay email + initial name)
14. Schema verification: No provider-specific tables (google_users, apple_users)
15. Schema verification: No email-based foreign keys
16. No automatic email merge between distinct auth identities
17. Protected endpoint security (unauthenticated requests rejected)
"""

import json
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
import psycopg

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import db_conn


def insert_auth_user(
    db_conn,
    user_id: str,
    email: str,
    raw_meta: dict | None = None,
    email_confirmed: bool = True,
):
    """Helper to insert a user directly into auth.users."""
    meta_json = json.dumps(raw_meta or {})
    confirmed_at = "NOW()" if email_confirmed else "NULL"
    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute(
            f"""
            INSERT INTO auth.users (
                id, email, raw_user_meta_data, role, aud, email_confirmed_at
            )
            VALUES (%s, %s, %s::jsonb, 'authenticated', 'authenticated', {confirmed_at})
            ON CONFLICT (id) DO UPDATE
            SET email = EXCLUDED.email,
                raw_user_meta_data = EXCLUDED.raw_user_meta_data,
                email_confirmed_at = EXCLUDED.email_confirmed_at;
            """,
            (user_id, email, meta_json),
        )


def get_tbilisi_city_id(db_conn) -> str:
    """Helper to get Tbilisi city_id from canonical cities table."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT id FROM public.cities WHERE name_ascii ILIKE '%Tbilisi%' LIMIT 1;")
        row = cur.fetchone()
        assert row is not None, "Canonical Tbilisi city not found"
        return str(row["id"])


# ---------------------------------------------------------------------------
# 1. Registration & Explicit Profile Initialization
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_registration_and_initialization(db_conn):
    uid = str(uuid.uuid4())
    email = f"register_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email, raw_meta={"first_name": "David", "last_name": "Agmashenebeli"})
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # GET before init returns 404
        res_before = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
        assert res_before.status_code == 404

        # Explicit initialization with payload
        res_init = await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "David", "last_name": "Agmashenebeli"},
        )
        assert res_init.status_code == 200
        p = res_init.json()
        assert p["id"] == uid
        assert p["first_name"] == "David"
        assert p["last_name"] == "Agmashenebeli"
        assert p["display_name"] == "David A."
        assert p["onboarding_completed"] is False
        assert p["onboarding_step"] == 1


# ---------------------------------------------------------------------------
# 2. Duplicate Email Prevention
# ---------------------------------------------------------------------------
def test_duplicate_email_prevented_in_auth(db_conn):
    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
    uid1 = str(uuid.uuid4())
    uid2 = str(uuid.uuid4())

    insert_auth_user(db_conn, uid1, email)

    # Attempting to insert another auth user with the same email must fail uniqueness
    with pytest.raises(psycopg.errors.UniqueViolation):
        with db_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO auth.users (id, email, role, aud)
                VALUES (%s, %s, 'authenticated', 'authenticated');
                """,
                (uid2, email),
            )
    db_conn.rollback()


# ---------------------------------------------------------------------------
# 3. Login & Canonical Identity Mapping
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_login_identity_mapping(db_conn):
    uid = str(uuid.uuid4())
    email = f"login_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)

    # Seed profile
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.profiles (id, display_name, onboarding_completed, onboarding_step)
            VALUES (%s, 'Tester', false, 1);
            """,
            (uid,),
        )

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == uid
        assert data["display_name"] == "Tester"
        assert data["onboarding_completed"] is False


# ---------------------------------------------------------------------------
# 4. Password Reset Integrity
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_password_reset_preserves_canonical_identity(db_conn):
    uid = str(uuid.uuid4())
    email = f"pwd_reset_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)

    with db_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.profiles (id, display_name) VALUES (%s, 'PreservedProfile');",
            (uid,),
        )

    # Simulate password reset (encrypted_password updated in auth.users)
    with db_conn.cursor() as cur:
        cur.execute(
            "UPDATE auth.users SET encrypted_password = 'new_hash' WHERE id = %s;",
            (uid,),
        )

    # User re-authenticates with new token for the same user_id
    new_token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {new_token}"})
        assert res.status_code == 200
        assert res.json()["id"] == uid
        assert res.json()["display_name"] == "PreservedProfile"


# ---------------------------------------------------------------------------
# 5. Email Verification State
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_unverified_email_does_not_block_profile(db_conn):
    uid = str(uuid.uuid4())
    email = f"unverified_{uid[:8]}@example.com"
    # User has unverified email (email_confirmed_at = NULL)
    insert_auth_user(db_conn, uid, email, email_confirmed=False)

    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Initialize profile
        init_res = await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Tamar", "last_name": "Mefe"},
        )
        assert init_res.status_code == 200

        # Read profile
        get_res = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
        assert get_res.status_code == 200
        assert get_res.json()["display_name"] == "Tamar M."


# ---------------------------------------------------------------------------
# 6. Onboarding Resume
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_onboarding_step_persists_across_sessions(db_conn):
    uid = str(uuid.uuid4())
    email = f"resume_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})

        # Advance to step 2
        patch_res = await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"onboarding_step": 2},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["onboarding_step"] == 2

        # In a new request / session, verify step 2 persists
        get_res = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
        assert get_res.status_code == 200
        assert get_res.json()["onboarding_step"] == 2


# ---------------------------------------------------------------------------
# 7. Authoritative Onboarding Completion Validation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_onboarding_completion_rejected_when_fields_missing(db_conn):
    uid = str(uuid.uuid4())
    email = f"incomplete_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})

        # Attempt to set onboarding_completed = true without required fields
        res = await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"onboarding_completed": True},
        )
        assert res.status_code == 400
        data = res.json()
        assert data["error"]["code"] == "incomplete_onboarding"
        assert "first_name" in data["error"]["message"]

        # Also test POST /v1/profiles/me/complete-onboarding directly
        res_post = await ac.post(
            "/v1/profiles/me/complete-onboarding",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_post.status_code == 400
        assert res_post.json()["error"]["code"] == "incomplete_onboarding"


@pytest.mark.asyncio
async def test_onboarding_completion_succeeds_with_all_required_fields(db_conn):
    uid = str(uuid.uuid4())
    email = f"complete_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)
    city_id = get_tbilisi_city_id(db_conn)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Ilia", "last_name": "Chavchavadze"},
        )

        # Update profile with current_city_id
        await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_city_id": city_id},
        )

        # Seed birth_data row (with birth_date and birth_city_id)
        with db_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.birth_data (
                    user_id, birth_date, birth_time, birth_time_precision,
                    birth_city_id, birth_timezone, latitude, longitude
                )
                VALUES (%s, '1837-11-08', NULL, 'unknown', %s, 'Asia/Tbilisi', 41.95, 45.81)
                ON CONFLICT (user_id) DO UPDATE SET birth_date = EXCLUDED.birth_date;
                """,
                (uid, city_id),
            )

        # Now complete onboarding via POST endpoint
        res = await ac.post(
            "/v1/profiles/me/complete-onboarding",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        assert res.json()["onboarding_completed"] is True


# ---------------------------------------------------------------------------
# 8. NULL birth_time Validity (No Noon Fallback)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_null_birth_time_is_valid_and_not_fallback(db_conn):
    uid = str(uuid.uuid4())
    email = f"null_time_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)
    city_id = get_tbilisi_city_id(db_conn)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Vazha", "last_name": "Pshavela"},
        )
        await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_city_id": city_id},
        )

        # Explicitly insert birth_data with NULL birth_time
        with db_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.birth_data (
                    user_id, birth_date, birth_time, birth_time_precision,
                    birth_city_id, birth_timezone, latitude, longitude
                )
                VALUES (%s, '1861-07-26', NULL, 'unknown', %s, 'Asia/Tbilisi', 42.15, 44.91);
                """,
                (uid, city_id),
            )

        # Verify birth_time in DB is strictly NULL, not 12:00:00
        with db_conn.cursor() as cur:
            cur.execute("SELECT birth_time FROM public.birth_data WHERE user_id = %s;", (uid,))
            row = cur.fetchone()
            assert row["birth_time"] is None

        # Completion succeeds with NULL birth_time
        res = await ac.post(
            "/v1/profiles/me/complete-onboarding",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        assert res.json()["onboarding_completed"] is True


# ---------------------------------------------------------------------------
# 9. display_name Derivation (First L.)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_display_name_derived_as_first_l(db_conn):
    uid = str(uuid.uuid4())
    email = f"derive_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/profiles/initialize",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Nika", "last_name": "Iordanishvili"},
        )
        assert res.status_code == 200
        assert res.json()["display_name"] == "Nika I."


# ---------------------------------------------------------------------------
# 10. OAuth Profile Initialization (Google / Apple Metadata)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_oauth_google_profile_initialization(db_conn):
    uid = str(uuid.uuid4())
    email = f"google_oauth_{uid[:8]}@gmail.com"
    google_meta = {
        "given_name": "Sergey",
        "family_name": "Brin",
        "picture": "https://lh3.googleusercontent.com/a/photo.jpg",
        "email_verified": True,
        "iss": "https://accounts.google.com",
    }
    insert_auth_user(db_conn, uid, email, raw_meta=google_meta)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # OAuth callback calls initialize without payload
        res = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == uid
        assert data["first_name"] == "Sergey"
        assert data["last_name"] == "Brin"
        assert data["display_name"] == "Sergey B."
        assert data["avatar_url"] == "https://lh3.googleusercontent.com/a/photo.jpg"


# ---------------------------------------------------------------------------
# 11. OAuth Metadata Does Not Overwrite Existing User Edits
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_oauth_metadata_does_not_overwrite_user_edits(db_conn):
    uid = str(uuid.uuid4())
    email = f"no_overwrite_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)

    # Establish user-edited profile
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.profiles (
                id, first_name, last_name, display_name, avatar_url, bio
            )
            VALUES (%s, 'CustomFirst', 'CustomLast', 'CustomDisplayName', 'https://custom.png', 'My Bio');
            """,
            (uid,),
        )

    # Update auth user with conflicting OAuth metadata
    conflicting_meta = {
        "given_name": "OAuthDifferentFirst",
        "family_name": "OAuthDifferentLast",
        "picture": "https://oauth.png",
    }
    insert_auth_user(db_conn, uid, email, raw_meta=conflicting_meta)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Subsequent OAuth login triggers initialize
        res = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        # MUST retain user's edited data
        assert data["first_name"] == "CustomFirst"
        assert data["last_name"] == "CustomLast"
        assert data["display_name"] == "CustomDisplayName"
        assert data["avatar_url"] == "https://custom.png"
        assert data["bio"] == "My Bio"


# ---------------------------------------------------------------------------
# 12. Google Identity Architecture
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_google_identity_resolves_to_canonical_profile(db_conn):
    uid = str(uuid.uuid4())
    email = f"google_user_{uid[:8]}@gmail.com"
    insert_auth_user(db_conn, uid, email, raw_meta={"provider": "google", "given_name": "G-User"})
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["id"] == uid


# ---------------------------------------------------------------------------
# 13. Apple Identity Architecture (Private Relay Support)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_apple_identity_with_private_relay(db_conn):
    uid = str(uuid.uuid4())
    relay_email = f"{uuid.uuid4().hex[:10]}@privaterelay.appleid.com"
    apple_meta = {
        "provider": "apple",
        "email": relay_email,
        "email_verified": True,
        "first_name": "AppleFirst",
        "last_name": "AppleLast",
    }
    insert_auth_user(db_conn, uid, relay_email, raw_meta=apple_meta)
    token = generate_test_jwt(user_id=uid, email=relay_email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == uid
        assert data["first_name"] == "AppleFirst"
        assert data["last_name"] == "AppleLast"
        assert data["display_name"] == "AppleFirst A."


# ---------------------------------------------------------------------------
# 14. No Provider-Specific Profile Tables
# ---------------------------------------------------------------------------
def test_no_provider_specific_profile_tables(db_conn):
    forbidden_tables = [
        "google_users",
        "google_profiles",
        "apple_users",
        "apple_profiles",
        "oauth_users",
        "oauth_profiles",
        "social_accounts",
    ]
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = ANY(%s);
            """,
            (forbidden_tables,),
        )
        found = [r["table_name"] for r in cur.fetchall()]
        assert found == [], f"Forbidden provider-specific tables found: {found}"


# ---------------------------------------------------------------------------
# 15. No Email-Based Identity Foreign Keys
# ---------------------------------------------------------------------------
def test_no_email_based_identity_foreign_keys(db_conn):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
              AND (kcu.column_name ILIKE '%email%' OR ccu.column_name ILIKE '%email%');
            """
        )
        fks = cur.fetchall()
        assert fks == [], f"Found forbidden email-based foreign keys: {fks}"


# ---------------------------------------------------------------------------
# 16. No Automatic Email Merge
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_no_automatic_email_merge_across_distinct_uids(db_conn):
    email = f"shared_{uuid.uuid4().hex[:8]}@example.com"
    uid1 = str(uuid.uuid4())
    uid2 = str(uuid.uuid4())

    insert_auth_user(db_conn, uid1, email)
    with db_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.profiles (id, display_name) VALUES (%s, 'OriginalUser');",
            (uid1,),
        )

    # If uid2 somehow authenticates, it cannot access or overwrite uid1's profile
    token2 = generate_test_jwt(user_id=uid2, email=email)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token2}"})
        # uid2 has no profile yet -> must return 404, NOT uid1's profile
        assert res.status_code == 404

        # uid2 attempting to patch /v1/profiles/me cannot patch uid1
        patch_res = await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token2}"},
            json={"display_name": "Hacker"},
        )
        assert patch_res.status_code == 404

    # Verify uid1's profile remains intact
    with db_conn.cursor() as cur:
        cur.execute("SELECT display_name FROM public.profiles WHERE id = %s;", (uid1,))
        assert cur.fetchone()["display_name"] == "OriginalUser"


# ---------------------------------------------------------------------------
# 17. Protected Route Behavior & Auth Enforcement
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_unauthenticated_requests_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # No token
        assert (await ac.get("/v1/profiles/me")).status_code == 401
        assert (await ac.post("/v1/profiles/initialize")).status_code == 401
        assert (await ac.patch("/v1/profiles/me", json={})).status_code == 401
        assert (await ac.post("/v1/profiles/me/complete-onboarding")).status_code == 401

        # Invalid token
        bad_header = {"Authorization": "Bearer not-a-real-jwt"}
        assert (await ac.get("/v1/profiles/me", headers=bad_header)).status_code == 401
