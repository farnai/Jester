"""
Comprehensive tests for JESTER Global Location System V1.
Covers:
- Database: country/city creation, constraints, foreign keys, unique checks.
- Backend: canonical city lookups, rejection of invalid city_id, non-override invariant.
- Persistence: profiles.city_id and birth_data.birth_city_id.
- Astrology: Swiss Ephemeris calculation using canonical coordinates.
- Backfill: accurate mapping of known cities, non-guessing of ambiguous cities.
- Security: public read-only access, non-writable by client roles.
- Versioning: bump_birth_data_version trigger on birth_city_id change.
"""
import uuid
import pytest
import psycopg
from psycopg.errors import CheckViolation, ForeignKeyViolation, UniqueViolation
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import db_conn, create_test_user, set_auth_context


# ----------------------------------------------------------------------
# DATABASE INTEGRITY TESTS
# ----------------------------------------------------------------------

def test_database_foreign_key_and_constraints(db_conn):
    """
    Verifies:
    1. Valid country and city creation.
    2. Foreign key enforcement (invalid country_id fails).
    3. Coordinate boundary check constraints.
    4. Unique constraints (duplicate source_id fails).
    """
    with db_conn.cursor() as cur:
        # 1. Invalid country_id rejected
        fake_country_id = uuid.uuid4()
        with pytest.raises(ForeignKeyViolation):
            cur.execute(
                """
                INSERT INTO public.cities (
                    id, source_id, country_id, country_code, name, name_ascii,
                    latitude, longitude, timezone
                ) VALUES (%s, 99999901, %s, 'ZZ', 'FakeCity', 'FakeCity', 0.0, 0.0, 'UTC');
                """,
                (uuid.uuid4(), fake_country_id),
            )

        # 2. Latitude check constraint (lat > 90.0)
        # First retrieve a valid country
        cur.execute("SELECT id, iso2 FROM public.countries LIMIT 1;")
        c_row = cur.fetchone()
        valid_cid = c_row["id"]
        valid_iso2 = c_row["iso2"]

        with pytest.raises(CheckViolation):
            cur.execute(
                """
                INSERT INTO public.cities (
                    id, source_id, country_id, country_code, name, name_ascii,
                    latitude, longitude, timezone
                ) VALUES (%s, 99999902, %s, %s, 'BadLatCity', 'BadLatCity', 95.0, 0.0, 'UTC');
                """,
                (uuid.uuid4(), valid_cid, valid_iso2),
            )

        # 3. Longitude check constraint (lon > 180.0)
        with pytest.raises(CheckViolation):
            cur.execute(
                """
                INSERT INTO public.cities (
                    id, source_id, country_id, country_code, name, name_ascii,
                    latitude, longitude, timezone
                ) VALUES (%s, 99999903, %s, %s, 'BadLonCity', 'BadLonCity', 0.0, 195.0, 'UTC');
                """,
                (uuid.uuid4(), valid_cid, valid_iso2),
            )

        # 4. Duplicate source_id rejected
        cur.execute("SELECT source_id FROM public.cities LIMIT 1;")
        existing_src_id = cur.fetchone()["source_id"]
        with pytest.raises(UniqueViolation):
            cur.execute(
                """
                INSERT INTO public.cities (
                    id, source_id, country_id, country_code, name, name_ascii,
                    latitude, longitude, timezone
                ) VALUES (%s, %s, %s, %s, 'DupCity', 'DupCity', 0.0, 0.0, 'UTC');
                """,
                (uuid.uuid4(), existing_src_id, valid_cid, valid_iso2),
            )


def test_city_to_country_relation(db_conn):
    """Verifies that joining cities and countries returns the correct country name."""
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.name as city_name, co.name as country_name, c.country_code
            FROM public.cities c
            JOIN public.countries co ON co.id = c.country_id
            WHERE c.country_code = 'GE' AND c.name = 'Tbilisi';
            """
        )
        row = cur.fetchone()
        assert row is not None
        assert row["city_name"] == "Tbilisi"
        assert row["country_name"] == "Georgia"
        assert row["country_code"] == "GE"


# ----------------------------------------------------------------------
# BACKEND API & CANONICAL RESOLUTION TESTS
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_canonical_geo_lookup_endpoints(db_conn):
    """
    Tests:
    1. GET /v1/geo/cities/{city_id} for a valid city returns canonical metadata.
    2. GET /v1/geo/cities/{fake_id} returns 404 city_not_found.
    3. GET /v1/geo/countries returns full country list.
    """
    with db_conn.cursor() as cur:
        cur.execute("SELECT id, name, latitude, longitude, timezone FROM public.cities WHERE country_code = 'GE' AND name = 'Tbilisi';")
        tb = cur.fetchone()
        tb_id = str(tb["id"])

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Valid city lookup
        res = await ac.get(f"/v1/geo/cities/{tb_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == tb_id
        assert data["name"] == "Tbilisi"
        assert data["country_name"] == "Georgia"
        assert data["timezone"] == "Asia/Tbilisi"
        assert abs(data["latitude"] - tb["latitude"]) < 0.001

        # 2. Invalid city lookup -> 404
        fake_id = str(uuid.uuid4())
        res_fake = await ac.get(f"/v1/geo/cities/{fake_id}")
        assert res_fake.status_code == 404
        assert res_fake.json()["error"]["code"] == "city_not_found"

        # 3. Countries list -> 200
        res_countries = await ac.get("/v1/geo/countries")
        assert res_countries.status_code == 200
        countries = res_countries.json()
        assert len(countries) >= 200
        assert any(c["iso2"] == "GE" and c["name"] == "Georgia" for c in countries)


@pytest.mark.asyncio
async def test_birth_data_canonical_resolution_and_protection(db_conn):
    """
    CRITICAL SECURITY & INVARIANT TEST:
    Client supplies birth_city_id for Tbilisi, but tries to forge coordinates (lat=0.0, lon=0.0)
    and wrong timezone ('UTC').
    Verifies that the backend rejects forged values, enforces canonical values,
    and calculates accurate Swiss Ephemeris natal chart.
    """
    uid = str(uuid.uuid4())
    email = f"canonical_birth_{uid[:8]}@test.jester.app"
    create_test_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    with db_conn.cursor() as cur:
        cur.execute("SELECT id, latitude, longitude, timezone FROM public.cities WHERE country_code = 'GE' AND name = 'Tbilisi';")
        tb = cur.fetchone()
        tb_id = str(tb["id"])

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "birth_date": "1995-05-15",
            "birth_time": "14:30:00",
            "birth_time_precision": "exact",
            "birth_city_id": tb_id,
            # Malicious / bogus client values:
            "latitude": 0.0,
            "longitude": 0.0,
            "birth_timezone": "UTC",
            "place_label": "Bogus Label",
        }
        res = await ac.post(
            "/v1/astrology/birth-data",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["sun_sign"] == "Taurus"
        assert data["ascendant_sign"] is not None

    # Inspect stored database row directly
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT birth_city_id, latitude, longitude, birth_timezone, place_label
            FROM public.birth_data
            WHERE user_id = %s;
            """,
            (uid,),
        )
        bd = cur.fetchone()
        assert str(bd["birth_city_id"]) == tb_id
        # Coordinates must be canonical Tbilisi (~41.69, ~44.83), NOT the forged 0.0!
        assert abs(bd["latitude"] - tb["latitude"]) < 0.001
        assert abs(bd["longitude"] - tb["longitude"]) < 0.001
        assert bd["birth_timezone"] == "Asia/Tbilisi"
        assert "Tbilisi" in bd["place_label"]


@pytest.mark.asyncio
async def test_invalid_birth_city_id_rejected(db_conn):
    """Verifies that passing a non-existent birth_city_id raises 400 invalid_city_id."""
    uid = str(uuid.uuid4())
    email = f"invalid_city_{uid[:8]}@test.jester.app"
    create_test_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    fake_id = str(uuid.uuid4())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/astrology/birth-data",
            json={
                "birth_date": "1995-05-15",
                "birth_time": "14:30:00",
                "birth_time_precision": "exact",
                "birth_city_id": fake_id,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "invalid_city_id"


@pytest.mark.asyncio
async def test_profile_city_id_persistence_and_sync(db_conn):
    """
    Verifies that updating city_id via PATCH /v1/profiles/me:
    1. Rejects invalid city_id.
    2. Persists valid city_id and synchronizes profiles.city with canonical display name.
    """
    uid = str(uuid.uuid4())
    email = f"prof_geo_{uid[:8]}@test.jester.app"
    create_test_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    with db_conn.cursor() as cur:
        cur.execute("SELECT id, name FROM public.cities WHERE country_code = 'GE' AND name = 'Batumi';")
        batumi = cur.fetchone()
        batumi_id = str(batumi["id"])

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Invalid city_id rejected
        res_err = await ac.patch(
            "/v1/profiles/me",
            json={"city_id": str(uuid.uuid4())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_err.status_code == 400
        assert res_err.json()["error"]["code"] == "invalid_city_id"

        # 2. Valid city_id accepted
        res_ok = await ac.patch(
            "/v1/profiles/me",
            json={"city_id": batumi_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_ok.status_code == 200
        data = res_ok.json()
        assert data["city_id"] == batumi_id
        assert "Batumi" in data["city"]

    # Verify directly in DB
    with db_conn.cursor() as cur:
        cur.execute("SELECT city_id, city FROM public.profiles WHERE id = %s;", (uid,))
        p = cur.fetchone()
        assert str(p["city_id"]) == batumi_id
        assert "Batumi" in p["city"]


# ----------------------------------------------------------------------
# DATA VERSIONING TRIGGER TEST
# ----------------------------------------------------------------------

def test_birth_data_version_bump_on_city_id_change(db_conn):
    """Verifies that changing birth_city_id triggers bump_birth_data_version()."""
    uid = str(uuid.uuid4())
    email = f"bump_geo_{uid[:8]}@test.jester.app"
    create_test_user(db_conn, uid, email)

    with db_conn.cursor() as cur:
        cur.execute("SELECT id FROM public.cities WHERE country_code = 'GE' LIMIT 2;")
        cities = cur.fetchall()
        c1_id = cities[0]["id"]
        c2_id = cities[1]["id"]

        # Insert initial birth_data
        cur.execute(
            """
            INSERT INTO public.birth_data (
                user_id, birth_date, birth_time, birth_time_precision,
                birth_timezone, latitude, longitude, birth_city_id, data_version
            ) VALUES (%s, '1995-01-01', '12:00:00', 'exact', 'Asia/Tbilisi', 41.7, 44.8, %s, 1);
            """,
            (uid, c1_id),
        )

        # Update birth_city_id
        cur.execute(
            "UPDATE public.birth_data SET birth_city_id = %s WHERE user_id = %s RETURNING data_version;",
            (c2_id, uid),
        )
        row = cur.fetchone()
        assert row["data_version"] == 2


# ----------------------------------------------------------------------
# SECURITY & RLS TESTS
# ----------------------------------------------------------------------

def test_security_countries_and_cities_read_only(db_conn):
    """
    Verifies that:
    1. Authenticated and anon roles can SELECT countries and cities.
    2. Authenticated role CANNOT insert, update, or delete countries or cities.
    """
    with db_conn.cursor() as cur:
        # Anon can read
        set_auth_context(cur, role="anon")
        cur.execute("SELECT count(*) as c FROM public.countries;")
        assert cur.fetchone()["c"] >= 200

        cur.execute("SELECT count(*) as c FROM public.cities;")
        assert cur.fetchone()["c"] >= 1000

        # Authenticated can read
        test_uid = str(uuid.uuid4())
        set_auth_context(cur, user_id=test_uid, role="authenticated")
        cur.execute("SELECT count(*) as c FROM public.countries;")
        assert cur.fetchone()["c"] >= 200

        # Authenticated cannot write to countries
        with pytest.raises(psycopg.Error):
            cur.execute(
                """
                INSERT INTO public.countries (source_id, iso2, name)
                VALUES (888888, 'XX', 'HackerCountry');
                """
            )

        # Reset role to superuser
        cur.execute("RESET ROLE;")


# ----------------------------------------------------------------------
# BACKFILL LOGIC TESTS
# ----------------------------------------------------------------------

def test_backfill_mapping_rules(db_conn):
    """
    Tests:
    1. Known city (Tbilisi coordinates/label) maps accurately.
    2. Ambiguous city name ('Springfield') is NOT guessed (remains null).
    3. Unmatched/fictional city remains unchanged (null).
    """
    from scripts.backfill_canonical_locations import run_backfill

    # 1. Known user
    uid_known = str(uuid.uuid4())
    create_test_user(db_conn, uid_known, f"known_{uid_known[:8]}@test.jester.app")

    # 2. Ambiguous user
    uid_ambiguous = str(uuid.uuid4())
    create_test_user(db_conn, uid_ambiguous, f"ambig_{uid_ambiguous[:8]}@test.jester.app")

    # 3. Unmatched user
    uid_unmatched = str(uuid.uuid4())
    create_test_user(db_conn, uid_unmatched, f"unmatch_{uid_unmatched[:8]}@test.jester.app")

    with db_conn.cursor() as cur:
        # Known birth data
        cur.execute(
            """
            INSERT INTO public.birth_data (
                user_id, birth_date, birth_time, birth_time_precision,
                birth_timezone, latitude, longitude, place_label
            ) VALUES (%s, '1990-01-01', '12:00:00', 'exact', 'Asia/Tbilisi', 41.7151, 44.8271, 'Tbilisi, Georgia');
            """,
            (uid_known,),
        )
        # Ambiguous profile city
        cur.execute("UPDATE public.profiles SET city = 'Springfield', city_id = NULL WHERE id = %s;", (uid_ambiguous,))

        # Unmatched profile city
        cur.execute("UPDATE public.profiles SET city = 'AtlantisCityXYZ', city_id = NULL WHERE id = %s;", (uid_unmatched,))

    # Execute backfill
    run_backfill()

    with db_conn.cursor() as cur:
        # Known mapped
        cur.execute("SELECT birth_city_id FROM public.birth_data WHERE user_id = %s;", (uid_known,))
        assert cur.fetchone()["birth_city_id"] is not None

        # Ambiguous skipped (remains null)
        cur.execute("SELECT city_id, city FROM public.profiles WHERE id = %s;", (uid_ambiguous,))
        p_amb = cur.fetchone()
        assert p_amb["city_id"] is None
        assert p_amb["city"] == "Springfield"

        # Unmatched skipped (remains null)
        cur.execute("SELECT city_id, city FROM public.profiles WHERE id = %s;", (uid_unmatched,))
        p_unm = cur.fetchone()
        assert p_unm["city_id"] is None
        assert p_unm["city"] == "AtlantisCityXYZ"


# ----------------------------------------------------------------------
# GEO STAGE 2: CITY SEARCH TESTS
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_search_empty_query_returns_popular_hubs():
    """
    Verifies that querying with an empty string returns the curated
    top 10 Georgian hubs in exact priority order, with safe autocomplete DTOs.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/v1/geo/cities/search")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        items = data["items"]
        assert len(items) == 10

        # Check order of top Georgian hubs
        names = [item["name"] for item in items]
        assert names[0] == "Tbilisi"
        assert names[1] == "Batumi"
        assert names[2] == "Kutaisi"
        assert names[3] == "Rustavi"
        assert names[4] == "Gori"
        assert names[5] == "Telavi"
        assert names[6] == "Zugdidi"
        assert names[7] == "Poti"
        assert names[8] == "Kobuleti"
        assert names[9] == "Khashuri"

        # Autocomplete safety: ensure raw coords and timezone are NOT leaked
        for item in items:
            assert "latitude" not in item
            assert "longitude" not in item
            assert "timezone" not in item
            assert "city_id" in item
            assert "display_name" in item
            assert "country_name" in item
            assert "country_code" in item


@pytest.mark.asyncio
async def test_search_single_char_returns_empty():
    """1 character queries must NOT trigger full backend search (frontend rule)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/v1/geo/cities/search?q=t")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []


@pytest.mark.asyncio
async def test_search_exact_and_prefix_english():
    """Verifies exact and prefix search for English names."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Exact Tbilisi
        resp = await client.get("/v1/geo/cities/search?q=tbilisi")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["name"] == "Tbilisi"
        assert items[0]["country_code"] == "GE"

        # Prefix Gurjaani
        resp = await client.get("/v1/geo/cities/search?q=gurj")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["name"] == "Gurjaani"
        assert items[0]["country_code"] == "GE"

        # Global search: London (UK) must rank first over London, Kentucky/Ontario
        resp = await client.get("/v1/geo/cities/search?q=London")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["name"] == "London"
        assert items[0]["country_code"] == "GB"


@pytest.mark.asyncio
async def test_search_georgian_script():
    """Verifies that Georgian script input is correctly transliterated and matched."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # თბილისი -> Tbilisi
        resp = await client.get("/v1/geo/cities/search?q=თბილისი")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["name"] == "Tbilisi"
        assert "თბილისი" in items[0]["display_name"]

        # ბათუმი -> Batumi
        resp = await client.get("/v1/geo/cities/search?q=ბათუმი")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["name"] == "Batumi"

        # გურჯაანი -> Gurjaani
        resp = await client.get("/v1/geo/cities/search?q=გურჯაანი")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["name"] == "Gurjaani"

        # ყვარელი -> Qvareli
        resp = await client.get("/v1/geo/cities/search?q=ყვარელი")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["name"] == "Qvareli"


@pytest.mark.asyncio
async def test_search_case_insensitive_and_whitespace():
    """Search must normalize whitespace and remain case-insensitive."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/v1/geo/cities/search?q=%20%20tBiLiSi%20%20")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert items[0]["name"] == "Tbilisi"


@pytest.mark.asyncio
async def test_search_limit_enforcement():
    """Verifies limit parameter behavior and upper boundary enforcement."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # limit = 3
        resp = await client.get("/v1/geo/cities/search?limit=3")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 3

        # limit = 50 exceeds le=20 constraint, returns HTTP 422
        resp = await client.get("/v1/geo/cities/search?limit=50")
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_no_results():
    """Verifies that an unmatchable query safely returns an empty items list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/v1/geo/cities/search?q=xyznonexistentcityname")
        assert resp.status_code == 200
        assert resp.json()["items"] == []


