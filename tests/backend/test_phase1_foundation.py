"""
Phase 1 Foundation Test Suite:
Auth-ready database & architecture foundation, profile onboarding state & location,
interest taxonomy foundation, constraints, RLS, and birth data null invariants.
"""

import uuid
import pytest
import psycopg
from psycopg.rows import dict_row

DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


@pytest.fixture(scope="session")
def db_conn():
    conn = psycopg.connect(DB_URL, autocommit=True, row_factory=dict_row)
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def clean_test_env(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute("DELETE FROM public.user_interests WHERE user_id IN (SELECT id FROM auth.users WHERE email LIKE '%@test.jester.app');")
        cur.execute("DELETE FROM public.birth_data WHERE user_id IN (SELECT id FROM auth.users WHERE email LIKE '%@test.jester.app');")
        cur.execute("DELETE FROM public.profiles WHERE id IN (SELECT id FROM auth.users WHERE email LIKE '%@test.jester.app');")
        cur.execute("DELETE FROM auth.users WHERE email LIKE '%@test.jester.app';")


def create_user(db_conn, user_id: uuid.UUID, email: str, first_name: str = "Test", last_name: str = "User"):
    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute(
            """
            INSERT INTO auth.users (id, email, raw_user_meta_data, role, aud)
            VALUES (%s, %s, %s, 'authenticated', 'authenticated')
            ON CONFLICT (id) DO NOTHING;
            """,
            (user_id, email, '{"first_name": "%s", "last_name": "%s"}' % (first_name, last_name)),
        )
        cur.execute(
            """
            INSERT INTO public.profiles (id, first_name, last_name, display_name, is_discoverable)
            VALUES (%s, %s, %s, %s, true)
            ON CONFLICT (id) DO NOTHING;
            """,
            (user_id, first_name, last_name, f"{first_name} {last_name[0].upper()}."),
        )


def set_auth(cur, user_id: uuid.UUID | None = None, role: str = "authenticated"):
    if role == "anon":
        cur.execute("SET ROLE anon;")
        cur.execute("SELECT set_config('request.jwt.claim.sub', '', false);")
        cur.execute("SELECT set_config('request.jwt.claim.role', 'anon', false);")
    else:
        cur.execute("SET ROLE authenticated;")
        cur.execute("SELECT set_config('request.jwt.claim.sub', %s, false);", (str(user_id) if user_id else "",))
        cur.execute("SELECT set_config('request.jwt.claim.role', 'authenticated', false);")


# =====================================================================
# 1. AUTH & IDENTITY FOUNDATION TESTS
# =====================================================================

def test_auth_users_canonical_foreign_key(db_conn):
    """Verify that public.profiles.id strictly references auth.users(id)."""
    fake_user_id = uuid.uuid4()
    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            cur.execute(
                """
                INSERT INTO public.profiles (id, display_name)
                VALUES (%s, 'Orphan Profile');
                """,
                (fake_user_id,),
            )


def test_no_email_as_primary_identity(db_conn):
    """Verify profiles is keyed by UUID, not email. Changing email in auth.users does not break profile."""
    uid = uuid.uuid4()
    initial_email = f"user_{uid.hex[:6]}@test.jester.app"
    updated_email = f"user_{uid.hex[:6]}_new@test.jester.app"

    create_user(db_conn, uid, initial_email, first_name="Nika", last_name="Ivanov")

    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        # Update email in auth.users
        cur.execute("UPDATE auth.users SET email = %s WHERE id = %s;", (updated_email, uid))
        # Profile remains intact by UUID
        cur.execute("SELECT id, display_name FROM public.profiles WHERE id = %s;", (uid,))
        profile = cur.fetchone()
        assert profile is not None
        assert profile["id"] == uid
        assert profile["display_name"] == "Nika I."


# =====================================================================
# 2. PROFILE & ONBOARDING STATE FOUNDATION TESTS
# =====================================================================

def test_profile_onboarding_defaults_and_updates(db_conn):
    """Verify onboarding_step defaults to 1 and onboarding_completed defaults to false."""
    uid = uuid.uuid4()
    create_user(db_conn, uid, f"step_{uid.hex[:6]}@test.jester.app")

    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute("SELECT onboarding_step, onboarding_completed FROM public.profiles WHERE id = %s;", (uid,))
        row = cur.fetchone()
        assert row["onboarding_step"] == 1
        assert row["onboarding_completed"] is False

        # Progress onboarding to step 3
        cur.execute("UPDATE public.profiles SET onboarding_step = 3 WHERE id = %s;", (uid,))
        cur.execute("SELECT onboarding_step, onboarding_completed FROM public.profiles WHERE id = %s;", (uid,))
        row2 = cur.fetchone()
        assert row2["onboarding_step"] == 3
        assert row2["onboarding_completed"] is False

        # Complete onboarding
        cur.execute("UPDATE public.profiles SET onboarding_completed = true WHERE id = %s;", (uid,))
        cur.execute("SELECT onboarding_step, onboarding_completed FROM public.profiles WHERE id = %s;", (uid,))
        row3 = cur.fetchone()
        assert row3["onboarding_step"] == 3
        assert row3["onboarding_completed"] is True


def test_where_you_live_canonical_city_fk(db_conn):
    """Verify current_city_id enforces foreign key constraint to public.cities."""
    uid = uuid.uuid4()
    create_user(db_conn, uid, f"city_{uid.hex[:6]}@test.jester.app")

    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        # Pick a valid canonical city
        cur.execute("SELECT id, name FROM public.cities LIMIT 1;")
        valid_city = cur.fetchone()
        assert valid_city is not None

        # Assign valid city
        cur.execute("UPDATE public.profiles SET current_city_id = %s WHERE id = %s;", (valid_city["id"], uid))
        cur.execute("SELECT current_city_id FROM public.profiles WHERE id = %s;", (uid,))
        assert cur.fetchone()["current_city_id"] == valid_city["id"]

        # Attempt invalid city
        invalid_city_id = uuid.uuid4()
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            cur.execute("UPDATE public.profiles SET current_city_id = %s WHERE id = %s;", (invalid_city_id, uid))


def test_display_name_derivation_logic():
    """Verify derived display name formatting according to V1 rules: First L."""
    def derive_name(first_name: str, last_name: str) -> str:
        fn = first_name.strip()
        ln = last_name.strip()
        if fn and ln:
            return f"{fn} {ln[0].upper()}."
        return fn

    assert derive_name("Nika", "Ivanov") == "Nika I."
    assert derive_name("Ana", "Kapanadze") == "Ana K."
    assert derive_name("Giorgi", "Beridze") == "Giorgi B."
    assert derive_name("  David  ", "  smith  ") == "David S."


# =====================================================================
# 3. INTEREST TAXONOMY & USER INTERESTS TESTS
# =====================================================================

def test_authoritative_18_categories_present(db_conn):
    """Verify that all 18 canonical categories are present and active."""
    expected_slugs = {
        "travel-exploring", "food-drink", "music", "movies-tv", "books-ideas",
        "creative", "culture-arts", "sports-fitness", "nature-outdoors", "games",
        "technology", "science-space", "astrology-spirituality", "wellness-mindfulness",
        "fashion-style", "animals-pets", "social-nightlife", "learning-life"
    }
    with db_conn.cursor() as cur:
        cur.execute("SELECT slug, status FROM public.interest_categories;")
        rows = cur.fetchall()
        found_slugs = {r["slug"] for r in rows if r["status"] == "active"}
        assert expected_slugs.issubset(found_slugs)
        assert len(rows) >= 18


def test_candidate_onboarding_interests_seeded(db_conn):
    """Verify representative candidate onboarding interests exist with valid categories."""
    curated_slugs = {
        "travel", "coffee", "music", "photography", "cinema", "books",
        "astrology", "food", "hiking", "art", "fitness", "pets",
        "technology", "gaming", "fashion", "nature", "theatre",
        "writing", "psychology", "concerts", "philosophy"
    }
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT i.slug, c.slug as category_slug 
            FROM public.interests i 
            JOIN public.interest_categories c ON c.id = i.category_id
            WHERE i.slug = ANY(%s);
            """,
            (list(curated_slugs),)
        )
        rows = cur.fetchall()
        found_slugs = {r["slug"] for r in rows}
        assert curated_slugs.issubset(found_slugs)


def test_user_interests_uniqueness_constraint(db_conn):
    """Verify that (user_id, interest_id) must be unique."""
    uid = uuid.uuid4()
    create_user(db_conn, uid, f"int_{uid.hex[:6]}@test.jester.app")

    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute("SELECT id FROM public.interests LIMIT 1;")
        interest_id = cur.fetchone()["id"]

        cur.execute(
            "INSERT INTO public.user_interests (user_id, interest_id) VALUES (%s, %s);",
            (uid, interest_id)
        )

        with pytest.raises(psycopg.errors.UniqueViolation):
            cur.execute(
                "INSERT INTO public.user_interests (user_id, interest_id) VALUES (%s, %s);",
                (uid, interest_id)
            )


def test_user_interests_rls_enforcement(db_conn):
    """Verify RLS: user can manage their own interests, but cannot insert for another user."""
    user1_id = uuid.uuid4()
    user2_id = uuid.uuid4()
    create_user(db_conn, user1_id, f"u1_{user1_id.hex[:6]}@test.jester.app")
    create_user(db_conn, user2_id, f"u2_{user2_id.hex[:6]}@test.jester.app")

    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute("SELECT id FROM public.interests LIMIT 2;")
        interest_rows = cur.fetchall()
        int1, int2 = interest_rows[0]["id"], interest_rows[1]["id"]

        # User 1 adds interest for self -> SUCCEEDS
        set_auth(cur, user1_id, role="authenticated")
        cur.execute(
            "INSERT INTO public.user_interests (user_id, interest_id) VALUES (%s, %s);",
            (user1_id, int1)
        )

        # User 1 attempts to insert for User 2 -> FAILS via RLS
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute(
                "INSERT INTO public.user_interests (user_id, interest_id) VALUES (%s, %s);",
                (user2_id, int2)
            )


# =====================================================================
# 4. BIRTH DATA INVARIANT TESTS
# =====================================================================

def test_unknown_birth_time_remains_null(db_conn):
    """Verify that unknown birth time is strictly stored as NULL with no noon fallback."""
    uid = uuid.uuid4()
    create_user(db_conn, uid, f"birth_{uid.hex[:6]}@test.jester.app")

    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, place_label)
            VALUES (%s, '1995-05-15', NULL, 'unknown', 'UTC', 'Tbilisi, Georgia')
            RETURNING birth_time, birth_time_precision;
            """,
            (uid,)
        )
        row = cur.fetchone()
        assert row["birth_time"] is None
        assert row["birth_time_precision"] == "unknown"
