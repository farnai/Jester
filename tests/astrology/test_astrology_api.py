"""
Integration tests for Astrology API endpoints, privacy boundaries, and versioning.
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn


@pytest.mark.asyncio
async def test_astrology_recalculation_and_privacy_boundary(db_conn):
    """
    Verifies:
    1. POST /v1/astrology/profile/recalculate computes natal chart and safe profile.
    2. Response contains ONLY safe derived fields.
    3. Server-side astro_private is populated with high-precision raw data.
    4. Client response never leaks raw planetary longitudes or houses.
    """
    user_id = str(uuid.uuid4())
    user_email = f"astro_user_{user_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_id, user_email, "Astro Tester")

    # Insert birth data
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.birth_data (
                user_id, birth_date, birth_time, birth_time_precision, birth_timezone,
                latitude, longitude, place_label
            ) VALUES (
                %s, '1990-08-23', '08:15:00', 'exact', 'America/New_York',
                40.7128, -74.0060, 'New York, USA'
            );
            """,
            (user_id,),
        )

    token = generate_test_jwt(user_id=user_id, email=user_email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Recalculate astrology
        res = await ac.post(
            "/v1/astrology/profile/recalculate",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        data = res.json()

        # Check safe derived fields
        assert data["user_id"] == user_id
        assert data["sun_sign"] == "Virgo"
        assert data["moon_sign"] == "Libra"
        assert data["ascendant_sign"] == "Virgo"
        assert data["element_primary"] in ["Fire", "Earth", "Air", "Water"]
        assert data["modality_primary"] in ["Cardinal", "Fixed", "Mutable"]
        assert data["engine_version"] == "1.0.0"
        assert data["source_birth_data_version"] == 1

        # Check that NO raw internal fields are leaked in API response
        assert "sun_longitude" not in data
        assert "moon_longitude" not in data
        assert "houses" not in data
        assert "retrogrades" not in data

        # 2. Verify server-side astro_private was populated
        with db_conn.cursor() as cur:
            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (user_id,))
            private_row = cur.fetchone()
            assert private_row is not None
            assert float(private_row["sun_longitude"]) > 0.0
            assert float(private_row["ascendant_longitude"]) > 0.0
            assert len(private_row["houses"]) == 12
            assert private_row["source_birth_data_version"] == 1

        # 3. GET /v1/astrology/profile/safe-astro returns the same safe profile
        res_get = await ac.get(
            "/v1/astrology/profile/safe-astro",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_get.status_code == 200
        assert res_get.json()["sun_sign"] == "Virgo"

        # 4. Verify GET /v1/astrology/people/{id}/safe-astro
        other_user_id = str(uuid.uuid4())
        other_email = f"viewer_{other_user_id[:8]}@test.jester.app"
        create_test_user(db_conn, other_user_id, other_email, "Viewer Tester")
        viewer_token = generate_test_jwt(user_id=other_user_id, email=other_email)

        res_person = await ac.get(
            f"/v1/astrology/people/{user_id}/safe-astro",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert res_person.status_code == 200
        assert res_person.json()["sun_sign"] == "Virgo"


@pytest.mark.asyncio
async def test_birth_data_version_bump_updates_astrology(db_conn):
    """
    Verifies that changing birth data bumps data_version, and recalculating
    updates source_birth_data_version in astro_private and astro_safe_profile.
    """
    user_id = str(uuid.uuid4())
    user_email = f"ver_user_{user_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_id, user_email, "Version Tester")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.birth_data (
                user_id, birth_date, birth_time, birth_time_precision, birth_timezone
            ) VALUES (
                %s, '1995-01-01', NULL, 'unknown', 'UTC'
            );
            """,
            (user_id,),
        )

    token = generate_test_jwt(user_id=user_id, email=user_email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Initial calculation (v1)
        res1 = await ac.post("/v1/astrology/profile/recalculate", headers={"Authorization": f"Bearer {token}"})
        assert res1.status_code == 200
        assert res1.json()["source_birth_data_version"] == 1
        assert res1.json()["sun_sign"] == "Capricorn"
        assert res1.json()["ascendant_sign"] is None  # Unknown time -> no ascendant

        # User updates birth date to March 21 (Aries)
        with db_conn.cursor() as cur:
            cur.execute(
                """
                UPDATE public.birth_data
                SET birth_date = '1995-03-21'
                WHERE user_id = %s;
                """,
                (user_id,),
            )
            cur.execute("SELECT data_version FROM public.birth_data WHERE user_id = %s;", (user_id,))
            new_v = cur.fetchone()["data_version"]
            assert new_v == 2  # Trigger bumped version

        # Recalculate updates to v2
        res2 = await ac.post("/v1/astrology/profile/recalculate", headers={"Authorization": f"Bearer {token}"})
        assert res2.status_code == 200
        assert res2.json()["source_birth_data_version"] == 2
        assert res2.json()["sun_sign"] == "Aries"
