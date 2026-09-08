import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.interpretation.library import InMemoryContentStore, ContentResolver
from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn, set_auth_context


@pytest.mark.asyncio
async def test_registered_user_birth_data_persistence_and_version_trigger(db_conn):
    """
    Verifies registered user birth data persistence and automatic data_version
    increment via PostgreSQL trigger bump_birth_data_version.
    """
    user_id = str(uuid.uuid4())
    create_test_user(db_conn, user_id, f"audit_{user_id[:8]}@test.jester.app", "Audit User")

    # 1. Insert State A (London)
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (
                user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude, place_label
            ) VALUES (%s, '1990-03-21', '06:00:00', 'exact', 'UTC', 51.5074, -0.1278, 'London, UK')
            RETURNING data_version;
            """,
            (user_id,),
        )
        row_a = cur.fetchone()
        assert row_a["data_version"] == 1

        # 2. Update to State B (Tbilisi)
        cur.execute(
            """
            UPDATE public.birth_data
            SET birth_date = '1995-11-15',
                birth_time = '18:30:00',
                birth_timezone = 'Asia/Tbilisi',
                latitude = 41.7151,
                longitude = 44.8271,
                place_label = 'Tbilisi, Georgia'
            WHERE user_id = %s
            RETURNING data_version;
            """,
            (user_id,),
        )
        row_b = cur.fetchone()
        assert row_b["data_version"] == 2, "Trigger bump_birth_data_version must increment version to 2"


@pytest.mark.asyncio
async def test_astrology_recalculation_and_safe_api_consistency(db_conn):
    """
    Verifies that recalculating astrology and reading /v1/astrology/profile/safe-astro
    yields deterministic, complete astronomical placements including personal planets.
    """
    user_id = str(uuid.uuid4())
    email = f"audit_astro_{user_id[:8]}@test.jester.app"
    create_test_user(db_conn, user_id, email, "Audit Astro User")
    token = generate_test_jwt(user_id=user_id, email=email)

    # 1. State A: London, 1990-03-21 06:00 UTC
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (
                user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude, place_label
            ) VALUES (%s, '1990-03-21', '06:00:00', 'exact', 'UTC', 51.5074, -0.1278, 'London, UK');
            """,
            (user_id,),
        )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Recalculate State A
        res_recalc_a = await ac.post(
            "/v1/astrology/profile/recalculate",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_recalc_a.status_code == 200
        data_a = res_recalc_a.json()
        assert data_a["sun_sign"] == "Aries"
        assert data_a["moon_sign"] == "Capricorn"
        assert data_a["ascendant_sign"] == "Pisces"
        assert data_a["mercury_sign"] == "Aries"
        assert data_a["venus_sign"] == "Aquarius"
        assert data_a["mars_sign"] == "Aquarius"
        assert data_a["source_birth_data_version"] == 1

        # Read cached safe astro State A
        res_safe_a = await ac.get(
            "/v1/astrology/profile/safe-astro",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_safe_a.status_code == 200
        safe_data_a = res_safe_a.json()
        assert safe_data_a["sun_sign"] == "Aries"
        assert safe_data_a["mercury_sign"] == "Aries"
        assert safe_data_a["venus_sign"] == "Aquarius"
        assert safe_data_a["mars_sign"] == "Aquarius"

        # 2. Mutate to State B: Tbilisi, 1995-11-15 18:30 Asia/Tbilisi
        with db_conn.cursor() as cur:
            set_auth_context(cur, None, "admin")
            cur.execute(
                """
                UPDATE public.birth_data
                SET birth_date = '1995-11-15',
                    birth_time = '18:30:00',
                    birth_timezone = 'Asia/Tbilisi',
                    latitude = 41.7151,
                    longitude = 44.8271,
                    place_label = 'Tbilisi, Georgia'
                WHERE user_id = %s;
                """,
                (user_id,),
            )

        # Recalculate State B
        res_recalc_b = await ac.post(
            "/v1/astrology/profile/recalculate",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_recalc_b.status_code == 200
        data_b = res_recalc_b.json()
        assert data_b["sun_sign"] == "Scorpio"
        assert data_b["moon_sign"] == "Leo"
        assert data_b["ascendant_sign"] == "Gemini"
        assert data_b["mercury_sign"] == "Scorpio"
        assert data_b["venus_sign"] == "Sagittarius"
        assert data_b["mars_sign"] == "Sagittarius"
        assert data_b["source_birth_data_version"] == 2

        # Read cached safe astro State B
        res_safe_b = await ac.get(
            "/v1/astrology/profile/safe-astro",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_safe_b.status_code == 200
        safe_data_b = res_safe_b.json()
        assert safe_data_b["sun_sign"] == "Scorpio"
        assert safe_data_b["moon_sign"] == "Leo"
        assert safe_data_b["ascendant_sign"] == "Gemini"
        assert safe_data_b["mercury_sign"] == "Scorpio"
        assert safe_data_b["venus_sign"] == "Sagittarius"
        assert safe_data_b["mars_sign"] == "Sagittarius"
        assert safe_data_b["source_birth_data_version"] == 2


@pytest.mark.asyncio
async def test_user_isolation_and_privacy_boundary(db_conn):
    """
    Verifies that User B cannot access User A's private birth data or private astrology,
    and that unauthorized/non-discoverable profiles return privacy-safe 404.
    """
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    create_test_user(db_conn, u1, f"u1_{u1[:8]}@test.jester.app", "User One")
    create_test_user(db_conn, u2, f"u2_{u2[:8]}@test.jester.app", "User Two")

    # Set U1 discoverable = False
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute("UPDATE public.profiles SET is_discoverable = FALSE WHERE id = %s;", (u1,))
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone)
            VALUES (%s, '1990-01-01', '12:00:00', 'exact', 'UTC');
            """,
            (u1,),
        )

    token_u2 = generate_test_jwt(user_id=u2, email="u2@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # User 2 tries to view User 1's safe astro -> must be 404 (PrivacySafeNotFoundException)
        res = await ac.get(
            f"/v1/astrology/people/{u1}/safe-astro",
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        assert res.status_code == 404


def test_content_resolution_mercury_venus_mars_all_12_signs():
    """
    Forensic verification that all 12 signs for Mercury, Venus, and Mars
    resolve to valid, approved Georgian content in the interpretation library.
    """
    store = InMemoryContentStore()
    resolver = ContentResolver(store)
    signs = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
    ]

    # 1. Mercury (Cognition)
    for sign in signs:
        contract_id = f"self.cognition.mercury_{sign}.v1"
        assert contract_id in INTERPRETATION_CONTRACTS, f"Missing contract: {contract_id}"
        resolved = resolver.resolve(interpretation_id=contract_id, locale="ka")
        assert resolved is not None, f"Mercury {sign} failed to resolve content"
        assert resolved.locale == "ka"
        assert len(resolved.text.strip()) > 20

    # 2. Venus (Relation)
    for sign in signs:
        contract_id = f"self.relation.venus_{sign}.v1"
        assert contract_id in INTERPRETATION_CONTRACTS, f"Missing contract: {contract_id}"
        resolved = resolver.resolve(interpretation_id=contract_id, locale="ka")
        assert resolved is not None, f"Venus {sign} failed to resolve content"
        assert resolved.locale == "ka"
        assert len(resolved.text.strip()) > 20

    # 3. Mars (Action)
    for sign in signs:
        contract_id = f"self.action.mars_{sign}.v1"
        assert contract_id in INTERPRETATION_CONTRACTS, f"Missing contract: {contract_id}"
        resolved = resolver.resolve(interpretation_id=contract_id, locale="ka")
        assert resolved is not None, f"Mars {sign} failed to resolve content"
        assert resolved.locale == "ka"
        assert len(resolved.text.strip()) > 20
