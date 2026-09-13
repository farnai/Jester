"""
Integration tests for Phase 2: Atomic Birth Data Onboarding and Transaction Boundary.

Verifies:
1. POST /v1/astrology/birth-data creates birth_data, astro_private, and astro_safe_profile atomically.
2. Calculation runs in memory BEFORE the database transaction.
3. If calculation or validation fails, 0 database writes occur.
4. If Write #2 (astro_private) fails, Write #1 (birth_data) is rolled back.
5. If Write #3 (astro_safe_profile) fails, Writes #1 and #2 are rolled back.
6. Repeated onboarding safely upserts and bumps version without duplicate logical records.
7. Unauthenticated calls return 401.
8. API response does not expose private calculation details (houses, coordinates, retrogrades).
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
import psycopg

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn


VALID_ONBOARDING_PAYLOAD = {
    "birth_date": "1992-07-15",
    "birth_time": "14:30:00",
    "birth_time_precision": "exact",
    "birth_timezone": "America/New_York",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "place_label": "New York, NY, USA",
}


@pytest.mark.asyncio
async def test_atomic_onboarding_success(db_conn):
    """
    Test A: Successful atomic onboarding creates records across all 3 tables in one operation.
    """
    user_id = str(uuid.uuid4())
    user_email = f"onboard_{user_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_id, user_email, "Onboarding User")
    token = generate_test_jwt(user_id=user_id, email=user_email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/astrology/birth-data",
            json=VALID_ONBOARDING_PAYLOAD,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 201
        data = res.json()

        # 1. Verify safe derived response
        assert data["user_id"] == user_id
        assert data["sun_sign"] == "Cancer"
        assert data["moon_sign"] == "Aquarius"
        assert data["ascendant_sign"] == "Scorpio"
        assert data["element_primary"] in ["Fire", "Earth", "Air", "Water"]
        assert data["modality_primary"] in ["Cardinal", "Fixed", "Mutable"]
        assert data["source_birth_data_version"] == 1
        assert data["engine_version"] == "1.0.0"

        # 2. Verify public.birth_data row
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.birth_data WHERE user_id = %s;", (user_id,))
            bd_row = cur.fetchone()
            assert bd_row is not None
            assert str(bd_row["birth_date"]) == "1992-07-15"
            assert str(bd_row["birth_time"]) == "14:30:00"
            assert bd_row["birth_timezone"] == "America/New_York"
            assert float(bd_row["latitude"]) == 40.7128
            assert float(bd_row["longitude"]) == -74.0060
            assert bd_row["place_label"] == "New York, NY, USA"
            assert bd_row["data_version"] == 1

        # 3. Verify public.astro_private row
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (user_id,))
            ap_row = cur.fetchone()
            assert ap_row is not None
            assert float(ap_row["sun_longitude"]) > 0.0
            assert float(ap_row["ascendant_longitude"]) > 0.0
            assert len(ap_row["houses"]) == 12
            assert ap_row["source_birth_data_version"] == 1

        # 4. Verify public.astro_safe_profile row
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.astro_safe_profile WHERE user_id = %s;", (user_id,))
            safe_row = cur.fetchone()
            assert safe_row is not None
            assert safe_row["sun_sign"] == "Cancer"
            assert safe_row["moon_sign"] == "Aquarius"
            assert safe_row["ascendant_sign"] == "Scorpio"
            assert safe_row["source_birth_data_version"] == 1


@pytest.mark.asyncio
async def test_atomic_onboarding_repeated_updates(db_conn):
    """
    Test B: Repeated onboarding by the same user updates records without duplicates and bumps version.
    """
    user_id = str(uuid.uuid4())
    user_email = f"repeated_{user_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_id, user_email, "Repeated User")
    token = generate_test_jwt(user_id=user_id, email=user_email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Initial save
        res1 = await ac.post(
            "/v1/astrology/birth-data",
            json=VALID_ONBOARDING_PAYLOAD,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res1.status_code == 201
        assert res1.json()["source_birth_data_version"] == 1
        assert res1.json()["sun_sign"] == "Cancer"

        # Repeated save with new date (Aries)
        updated_payload = dict(VALID_ONBOARDING_PAYLOAD)
        updated_payload["birth_date"] = "1992-04-10"

        res2 = await ac.post(
            "/v1/astrology/birth-data",
            json=updated_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res2.status_code == 201
        data2 = res2.json()
        assert data2["source_birth_data_version"] == 2
        assert data2["sun_sign"] == "Aries"

        # Verify single logical row in each table (no duplicates)
        with db_conn.cursor() as cur:
            cur.execute("SELECT count(*) as count FROM public.birth_data WHERE user_id = %s;", (user_id,))
            assert cur.fetchone()["count"] == 1

            cur.execute("SELECT count(*) as count FROM public.astro_private WHERE user_id = %s;", (user_id,))
            assert cur.fetchone()["count"] == 1

            cur.execute("SELECT count(*) as count FROM public.astro_safe_profile WHERE user_id = %s;", (user_id,))
            assert cur.fetchone()["count"] == 1


@pytest.mark.asyncio
async def test_atomic_onboarding_calculation_failure_leaves_zero_writes(db_conn):
    """
    Test C: When calculation fails (e.g. polar Placidus error), ZERO writes occur to any table.
    """
    user_id = str(uuid.uuid4())
    user_email = f"polar_{user_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_id, user_email, "Polar User")
    token = generate_test_jwt(user_id=user_id, email=user_email)

    # Latitude 71.0 North triggers placidus_polar_error
    polar_payload = dict(VALID_ONBOARDING_PAYLOAD)
    polar_payload["latitude"] = 71.0

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/astrology/birth-data",
            json=polar_payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 400
        data = res.json()
        assert data["error"]["code"] == "placidus_polar_error"

        # Invariant: ZERO database records must exist across all 3 tables
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.birth_data WHERE user_id = %s;", (user_id,))
            assert cur.fetchone() is None

            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (user_id,))
            assert cur.fetchone() is None

            cur.execute("SELECT * FROM public.astro_safe_profile WHERE user_id = %s;", (user_id,))
            assert cur.fetchone() is None


@pytest.mark.asyncio
async def test_atomic_rollback_on_astro_private_failure(db_conn, monkeypatch):
    """
    Test D: When Write #2 (astro_private) fails, Write #1 (birth_data) is rolled back.
    No partial state (birth_data without astro_private).
    """
    user_id = str(uuid.uuid4())
    user_email = f"fail2_{user_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_id, user_email, "Failure 2 User")
    token = generate_test_jwt(user_id=user_id, email=user_email)

    original_execute = psycopg.Cursor.execute

    def failing_execute(self, query, params=None):
        if "INSERT INTO public.astro_private" in query:
            raise psycopg.OperationalError("Simulated DB failure writing astro_private")
        return original_execute(self, query, params)

    monkeypatch.setattr(psycopg.Cursor, "execute", failing_execute)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/astrology/birth-data",
            json=VALID_ONBOARDING_PAYLOAD,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 500
        data = res.json()
        assert data["error"]["code"] == "database_transaction_failed"
        # Ensure no internal SQL or table names leaked
        assert "INSERT" not in data["error"]["message"]
        assert "astro_private" not in data["error"]["message"]

        # Transaction invariant: Write #1 (birth_data) must have been rolled back
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.birth_data WHERE user_id = %s;", (user_id,))
            assert cur.fetchone() is None

            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (user_id,))
            assert cur.fetchone() is None

            cur.execute("SELECT * FROM public.astro_safe_profile WHERE user_id = %s;", (user_id,))
            assert cur.fetchone() is None


@pytest.mark.asyncio
async def test_atomic_rollback_on_astro_safe_profile_failure(db_conn, monkeypatch):
    """
    Test E: When Write #3 (astro_safe_profile) fails, Writes #1 and #2 are rolled back.
    No partial state (birth_data + astro_private without astro_safe_profile).
    """
    user_id = str(uuid.uuid4())
    user_email = f"fail3_{user_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_id, user_email, "Failure 3 User")
    token = generate_test_jwt(user_id=user_id, email=user_email)

    original_execute = psycopg.Cursor.execute

    def failing_execute(self, query, params=None):
        if "INSERT INTO public.astro_safe_profile" in query:
            raise psycopg.OperationalError("Simulated DB failure writing astro_safe_profile")
        return original_execute(self, query, params)

    monkeypatch.setattr(psycopg.Cursor, "execute", failing_execute)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/astrology/birth-data",
            json=VALID_ONBOARDING_PAYLOAD,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 500
        data = res.json()
        assert data["error"]["code"] == "database_transaction_failed"

        # Transaction invariant: All prior writes must have been rolled back
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.birth_data WHERE user_id = %s;", (user_id,))
            assert cur.fetchone() is None

            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (user_id,))
            assert cur.fetchone() is None

            cur.execute("SELECT * FROM public.astro_safe_profile WHERE user_id = %s;", (user_id,))
            assert cur.fetchone() is None


@pytest.mark.asyncio
async def test_atomic_onboarding_unauthenticated():
    """
    Test F: Unauthenticated requests are rejected with 401.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/v1/astrology/birth-data", json=VALID_ONBOARDING_PAYLOAD)
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_atomic_onboarding_privacy_safe_response(db_conn):
    """
    Test H: Response strictly satisfies privacy boundary.
    No raw longitudes, houses, or internal exceptions leaked.
    """
    user_id = str(uuid.uuid4())
    user_email = f"privacy_{user_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_id, user_email, "Privacy User")
    token = generate_test_jwt(user_id=user_id, email=user_email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/astrology/birth-data",
            json=VALID_ONBOARDING_PAYLOAD,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 201
        data = res.json()

        # Disallowed private fields
        assert "sun_longitude" not in data
        assert "moon_longitude" not in data
        assert "ascendant_longitude" not in data
        assert "houses" not in data
        assert "retrogrades" not in data
        assert "calculated_at" not in data


@pytest.mark.asyncio
async def test_atomic_onboarding_ownership_boundary(db_conn):
    """
    Test G: User can only write their own birth data.
    Even if payload contains another user's ID or attempts injection,
    ownership is strictly enforced from the authenticated JWT token.
    """
    user_a_id = str(uuid.uuid4())
    user_a_email = f"user_a_{user_a_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_a_id, user_a_email, "User A")

    user_b_id = str(uuid.uuid4())
    user_b_email = f"user_b_{user_b_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_b_id, user_b_email, "User B")

    token_a = generate_test_jwt(user_id=user_a_id, email=user_a_email)

    # Attempt to inject user_b_id into payload
    malicious_payload = dict(VALID_ONBOARDING_PAYLOAD)
    malicious_payload["user_id"] = user_b_id

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/astrology/birth-data",
            json=malicious_payload,
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res.status_code == 201
        data = res.json()
        # Created for authenticated User A
        assert data["user_id"] == user_a_id

        # Invariant: User B must have NO records created
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.birth_data WHERE user_id = %s;", (user_b_id,))
            assert cur.fetchone() is None

            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (user_b_id,))
            assert cur.fetchone() is None

            cur.execute("SELECT * FROM public.astro_safe_profile WHERE user_id = %s;", (user_b_id,))
            assert cur.fetchone() is None

