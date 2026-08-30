import uuid
import pytest
import psycopg
from psycopg.rows import dict_row

# Standard Supabase local connection string
DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

@pytest.fixture(scope="session")
def db_conn():
    conn = psycopg.connect(DB_URL, autocommit=True, row_factory=dict_row)
    yield conn
    conn.close()

@pytest.fixture(autouse=True)
def clean_db(db_conn):
    """Clean tables before each test and create test users in auth.users"""
    with db_conn.cursor() as cur:
        # Reset role to postgres/superuser
        cur.execute("RESET ROLE;")
        
        # Clean application tables
        cur.execute("""
            TRUNCATE TABLE 
                public.messages,
                public.conversation_members,
                public.conversations,
                public.compatibility_results,
                public.connections,
                public.daily_energies,
                public.notifications,
                public.astro_safe_profile,
                public.astro_private,
                public.birth_data,
                public.profiles
            CASCADE;
        """)
        
        # Clean auth.users for test IDs
        cur.execute("DELETE FROM auth.users WHERE email LIKE '%@test.jester.app';")

def create_test_user(db_conn, user_id: str, email: str, display_name: str = "Test User"):
    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute("""
            INSERT INTO auth.users (id, email, raw_user_meta_data, role, aud)
            VALUES (%s, %s, %s, 'authenticated', 'authenticated')
            ON CONFLICT (id) DO NOTHING;
        """, (user_id, email, '{"name": "%s"}' % display_name))
        
        cur.execute("""
            INSERT INTO public.profiles (id, display_name, is_discoverable)
            VALUES (%s, %s, true)
            ON CONFLICT (id) DO UPDATE SET display_name = excluded.display_name, is_discoverable = excluded.is_discoverable;
        """, (user_id, display_name))

def set_auth_context(cur, user_id: str | None = None, role: str = "authenticated"):
    if role == "anon":
        cur.execute("SET ROLE anon;")
        cur.execute("SELECT set_config('request.jwt.claim.sub', '', false);")
        cur.execute("SELECT set_config('request.jwt.claims', '', false);")
    elif role == "authenticated":
        cur.execute("SET ROLE authenticated;")
        cur.execute("SELECT set_config('request.jwt.claim.sub', %s, false);", (user_id,))
        cur.execute("SELECT set_config('request.jwt.claims', %s, false);", (f'{{"sub": "{user_id}", "role": "authenticated"}}',))
    elif role == "service_role":
        cur.execute("SET ROLE service_role;")
        cur.execute("SELECT set_config('request.jwt.claim.sub', '', false);")
        cur.execute("SELECT set_config('request.jwt.claims', '{\"role\": \"service_role\"}', false);")
    else:
        cur.execute("RESET ROLE;")
        cur.execute("SELECT set_config('request.jwt.claim.sub', '', false);")
        cur.execute("SELECT set_config('request.jwt.claims', '', false);")

# ==============================================================================
# 1. BIRTH DATA PRIVACY TESTS
# ==============================================================================

def test_user_a_can_read_and_update_own_birth_data(db_conn):
    user_a = str(uuid.uuid4())
    create_test_user(db_conn, user_a, "user_a@test.jester.app", "User A")
    
    with db_conn.cursor() as cur:
        set_auth_context(cur, user_a, "authenticated")
        
        # User A inserts own birth data
        cur.execute("""
            INSERT INTO public.birth_data (user_id, birth_date, birth_timezone, birth_time_precision)
            VALUES (%s, '1995-05-15', 'UTC', 'unknown');
        """, (user_a,))
        
        # User A reads own birth data
        cur.execute("SELECT * FROM public.birth_data WHERE user_id = %s;", (user_a,))
        row = cur.fetchone()
        assert row is not None
        assert str(row["user_id"]) == user_a
        assert row["data_version"] == 1
        
        # User A updates birth data
        cur.execute("""
            UPDATE public.birth_data 
            SET birth_time = '14:30:00', birth_time_precision = 'exact'
            WHERE user_id = %s;
        """, (user_a,))
        
        cur.execute("SELECT * FROM public.birth_data WHERE user_id = %s;", (user_a,))
        updated = cur.fetchone()
        assert updated["birth_time_precision"] == "exact"
        assert updated["data_version"] == 2  # Bumping trigger works!

def test_user_a_cannot_read_or_update_user_b_birth_data(db_conn):
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    create_test_user(db_conn, user_a, "user_a@test.jester.app", "User A")
    create_test_user(db_conn, user_b, "user_b@test.jester.app", "User B")
    
    with db_conn.cursor() as cur:
        # Insert B's birth data as B
        set_auth_context(cur, user_b, "authenticated")
        cur.execute("""
            INSERT INTO public.birth_data (user_id, birth_date, birth_timezone, birth_time_precision)
            VALUES (%s, '1990-01-01', 'UTC', 'unknown');
        """, (user_b,))
        
        # Switch to User A
        set_auth_context(cur, user_a, "authenticated")
        
        # User A tries to read User B's birth data -> Empty
        cur.execute("SELECT * FROM public.birth_data WHERE user_id = %s;", (user_b,))
        assert cur.fetchone() is None
        
        # User A tries to update User B's birth data -> 0 rows affected
        cur.execute("UPDATE public.birth_data SET birth_date = '2000-01-01' WHERE user_id = %s;", (user_b,))
        assert cur.rowcount == 0

def test_anonymous_cannot_read_birth_data(db_conn):
    user_a = str(uuid.uuid4())
    create_test_user(db_conn, user_a, "user_a@test.jester.app", "User A")
    
    with db_conn.cursor() as cur:
        set_auth_context(cur, user_a, "authenticated")
        cur.execute("""
            INSERT INTO public.birth_data (user_id, birth_date, birth_timezone, birth_time_precision)
            VALUES (%s, '1995-05-15', 'UTC', 'unknown');
        """, (user_a,))
        
        # Switch to Anonymous
        set_auth_context(cur, None, "anon")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("SELECT * FROM public.birth_data;")

# ==============================================================================
# 2. ASTROLOGY PRIVACY BOUNDARY TESTS
# ==============================================================================

def test_authenticated_mobile_cannot_read_astro_private(db_conn):
    user_a = str(uuid.uuid4())
    create_test_user(db_conn, user_a, "user_a@test.jester.app", "User A")
    
    with db_conn.cursor() as cur:
        # Admin / backend inserts calculated private astrology
        set_auth_context(cur, None, "admin")
        cur.execute("""
            INSERT INTO public.astro_private (user_id, source_birth_data_version, engine_version, sun_longitude)
            VALUES (%s, 1, '1.0.0', 54.25);
        """, (user_a,))
        
        # Switch to Authenticated User A
        set_auth_context(cur, user_a, "authenticated")
        
        # Attempting to read astro_private is denied by grant/RLS
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("SELECT * FROM public.astro_private WHERE user_id = %s;", (user_a,))

def test_safe_astrology_profile_visibility(db_conn):
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    create_test_user(db_conn, user_a, "user_a@test.jester.app", "User A")
    create_test_user(db_conn, user_b, "user_b@test.jester.app", "User B")
    
    with db_conn.cursor() as cur:
        # Backend writes safe derived profiles
        set_auth_context(cur, None, "admin")
        cur.execute("""
            INSERT INTO public.astro_safe_profile (user_id, source_birth_data_version, engine_version, sun_sign, moon_sign)
            VALUES 
                (%s, 1, '1.0.0', 'Taurus', 'Scorpio'),
                (%s, 1, '1.0.0', 'Leo', 'Aquarius');
        """, (user_a, user_b))
        
        # User A reads own safe profile
        set_auth_context(cur, user_a, "authenticated")
        cur.execute("SELECT * FROM public.astro_safe_profile WHERE user_id = %s;", (user_a,))
        row_a = cur.fetchone()
        assert row_a is not None
        assert row_a["sun_sign"] == "Taurus"
        
        # User A reads User B's safe profile (since User B is discoverable)
        cur.execute("SELECT * FROM public.astro_safe_profile WHERE user_id = %s;", (user_b,))
        row_b = cur.fetchone()
        assert row_b is not None
        assert row_b["sun_sign"] == "Leo"
        
        # If User B is marked non-discoverable:
        set_auth_context(cur, user_b, "authenticated")
        cur.execute("UPDATE public.profiles SET is_discoverable = false WHERE id = %s;", (user_b,))
        
        # User A now CANNOT read User B's safe profile
        set_auth_context(cur, user_a, "authenticated")
        cur.execute("SELECT * FROM public.astro_safe_profile WHERE user_id = %s;", (user_b,))
        assert cur.fetchone() is None

# ==============================================================================
# 3. CONNECTIONS & BLOCK SEMANTICS TESTS
# ==============================================================================

def test_canonical_pair_constraint_and_reverse_prevention(db_conn):
    u1 = "00000000-0000-0000-0000-000000000001"
    u2 = "00000000-0000-0000-0000-000000000002"
    create_test_user(db_conn, u1, "u1@test.jester.app", "U1")
    create_test_user(db_conn, u2, "u2@test.jester.app", "U2")
    
    with db_conn.cursor() as cur:
        # 1. Insert canonical pair (u1 < u2) as u1 -> Success
        set_auth_context(cur, u1, "authenticated")
        cur.execute("""
            INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by)
            VALUES (%s, %s, 'pending', %s);
        """, (u1, u2, u1))
        
        # 2. Attempting reverse non-canonical pair (u2, u1) as u2 -> Check constraint failure
        set_auth_context(cur, u2, "authenticated")
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute("""
                INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by)
                VALUES (%s, %s, 'pending', %s);
            """, (u2, u1, u2))

def test_client_cannot_update_connections_directly(db_conn):
    """Rule 4A: Authenticated clients have NO direct UPDATE permissions on connections."""
    u1, u2 = sorted([str(uuid.uuid4()), str(uuid.uuid4())])
    create_test_user(db_conn, u1, "u1@test.jester.app", "U1")
    create_test_user(db_conn, u2, "u2@test.jester.app", "U2")
    
    with db_conn.cursor() as cur:
        set_auth_context(cur, u1, "authenticated")
        cur.execute("""
            INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by)
            VALUES (%s, %s, 'pending', %s);
        """, (u1, u2, u1))
        
        # User tries to update status to 'accepted' directly -> Insufficient privilege
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("""
                UPDATE public.connections SET status = 'accepted' WHERE user_a_id = %s AND user_b_id = %s;
            """, (u1, u2))

def test_block_visibility_and_mutual_profile_hiding(db_conn):
    u1, u2 = sorted([str(uuid.uuid4()), str(uuid.uuid4())])
    create_test_user(db_conn, u1, "u1@test.jester.app", "U1")
    create_test_user(db_conn, u2, "u2@test.jester.app", "U2")
    
    with db_conn.cursor() as cur:
        # Backend sets relationship to blocked by U1
        set_auth_context(cur, None, "admin")
        cur.execute("""
            INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by, blocked_by)
            VALUES (%s, %s, 'blocked', %s, %s);
        """, (u1, u2, u1, u1))
        
        # Blocker (U1) CAN see the blocked connection row
        set_auth_context(cur, u1, "authenticated")
        cur.execute("SELECT * FROM public.connections WHERE user_a_id = %s AND user_b_id = %s;", (u1, u2))
        assert cur.fetchone() is not None
        
        # Blocked user (U2) CANNOT discover the blocked connection row
        set_auth_context(cur, u2, "authenticated")
        cur.execute("SELECT * FROM public.connections WHERE user_a_id = %s AND user_b_id = %s;", (u1, u2))
        assert cur.fetchone() is None
        
        # Mutual profile discovery check:
        # U1 cannot see U2's profile
        set_auth_context(cur, u1, "authenticated")
        cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (u2,))
        assert cur.fetchone() is None
        
        # U2 cannot see U1's profile
        set_auth_context(cur, u2, "authenticated")
        cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (u1,))
        assert cur.fetchone() is None

# ==============================================================================
# 4. COMPATIBILITY AUTHORIZATION TESTS
# ==============================================================================

def test_compatibility_access_rules(db_conn):
    u1, u2 = sorted([str(uuid.uuid4()), str(uuid.uuid4())])
    u3 = str(uuid.uuid4())
    create_test_user(db_conn, u1, "u1@test.jester.app", "U1")
    create_test_user(db_conn, u2, "u2@test.jester.app", "U2")
    create_test_user(db_conn, u3, "u3@test.jester.app", "U3")
    
    with db_conn.cursor() as cur:
        # 1. Before connection is accepted: Backend inserts result
        set_auth_context(cur, None, "admin")
        cur.execute("""
            INSERT INTO public.compatibility_results (user_a_id, user_b_id, user_a_birth_data_version, user_b_birth_data_version, engine_version, score)
            VALUES (%s, %s, 1, 1, '1.0.0', 88.5);
        """, (u1, u2))
        
        # User 1 tries to read compatibility before connection -> Denied (0 rows)
        set_auth_context(cur, u1, "authenticated")
        cur.execute("SELECT * FROM public.compatibility_results WHERE user_a_id = %s AND user_b_id = %s;", (u1, u2))
        assert cur.fetchone() is None
        
        # 2. Connection is accepted
        set_auth_context(cur, None, "admin")
        cur.execute("""
            INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by)
            VALUES (%s, %s, 'accepted', %s);
        """, (u1, u2, u1))
        
        # Now User 1 and User 2 can read compatibility result
        set_auth_context(cur, u1, "authenticated")
        cur.execute("SELECT * FROM public.compatibility_results WHERE user_a_id = %s AND user_b_id = %s;", (u1, u2))
        row = cur.fetchone()
        assert row is not None
        assert float(row["score"]) == 88.5
        
        set_auth_context(cur, u2, "authenticated")
        cur.execute("SELECT * FROM public.compatibility_results WHERE user_a_id = %s AND user_b_id = %s;", (u1, u2))
        assert cur.fetchone() is not None
        
        # Unrelated User 3 CANNOT read U1/U2 compatibility
        set_auth_context(cur, u3, "authenticated")
        cur.execute("SELECT * FROM public.compatibility_results WHERE user_a_id = %s AND user_b_id = %s;", (u1, u2))
        assert cur.fetchone() is None
        
        # 3. Connection is blocked
        set_auth_context(cur, None, "admin")
        cur.execute("""
            UPDATE public.connections SET status = 'blocked', blocked_by = %s 
            WHERE user_a_id = %s AND user_b_id = %s;
        """, (u1, u1, u2))
        
        # Both U1 and U2 now immediately lose access to compatibility result
        set_auth_context(cur, u1, "authenticated")
        cur.execute("SELECT * FROM public.compatibility_results WHERE user_a_id = %s AND user_b_id = %s;", (u1, u2))
        assert cur.fetchone() is None
        
        set_auth_context(cur, u2, "authenticated")
        cur.execute("SELECT * FROM public.compatibility_results WHERE user_a_id = %s AND user_b_id = %s;", (u1, u2))
        assert cur.fetchone() is None

# ==============================================================================
# 5. CHAT & REALTIME PRIVACY TESTS
# ==============================================================================

def test_chat_rls_and_block_enforcement(db_conn):
    u1, u2 = sorted([str(uuid.uuid4()), str(uuid.uuid4())])
    u3 = str(uuid.uuid4())
    create_test_user(db_conn, u1, "u1@test.jester.app", "U1")
    create_test_user(db_conn, u2, "u2@test.jester.app", "U2")
    create_test_user(db_conn, u3, "u3@test.jester.app", "U3")
    
    with db_conn.cursor() as cur:
        # Create direct conversation between U1 and U2
        conv_id = str(uuid.uuid4())
        set_auth_context(cur, None, "admin")
        cur.execute("INSERT INTO public.conversations (id, conversation_type, created_by) VALUES (%s, 'direct', %s);", (conv_id, u1))
        cur.execute("INSERT INTO public.conversation_members (conversation_id, user_id) VALUES (%s, %s), (%s, %s);", (conv_id, u1, conv_id, u2))
        
        # Without accepted connection: cannot send or read messages
        set_auth_context(cur, u1, "authenticated")
        cur.execute("SELECT * FROM public.conversations WHERE id = %s;", (conv_id,))
        assert cur.fetchone() is None
        
        # Set accepted connection
        set_auth_context(cur, None, "admin")
        cur.execute("INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by) VALUES (%s, %s, 'accepted', %s);", (u1, u2, u1))
        
        # U1 sends a message
        set_auth_context(cur, u1, "authenticated")
        msg_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO public.messages (id, conversation_id, sender_user_id, body)
            VALUES (%s, %s, %s, 'Hello U2!');
        """, (msg_id, conv_id, u1))
        
        # U2 reads the message
        set_auth_context(cur, u2, "authenticated")
        cur.execute("SELECT * FROM public.messages WHERE conversation_id = %s;", (conv_id,))
        row = cur.fetchone()
        assert row is not None
        assert row["body"] == "Hello U2!"
        
        # Unrelated U3 cannot read or insert messages
        set_auth_context(cur, u3, "authenticated")
        cur.execute("SELECT * FROM public.messages WHERE conversation_id = %s;", (conv_id,))
        assert cur.fetchone() is None
        
        # If U1 blocks U2: Direct chat messages become immediately unreadable to both
        set_auth_context(cur, None, "admin")
        cur.execute("UPDATE public.connections SET status = 'blocked', blocked_by = %s WHERE user_a_id = %s AND user_b_id = %s;", (u1, u1, u2))
        
        set_auth_context(cur, u1, "authenticated")
        cur.execute("SELECT * FROM public.messages WHERE conversation_id = %s;", (conv_id,))
        assert cur.fetchone() is None
        
        set_auth_context(cur, u2, "authenticated")
        cur.execute("SELECT * FROM public.messages WHERE conversation_id = %s;", (conv_id,))
        assert cur.fetchone() is None

# ==============================================================================
# 6. ACCOUNT DELETION CASCADE TESTS
# ==============================================================================

def test_account_deletion_cascades_all_user_data(db_conn):
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    create_test_user(db_conn, user_a, "user_a@test.jester.app", "User A")
    create_test_user(db_conn, user_b, "user_b@test.jester.app", "User B")
    
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        
        # Populate tables for user A
        cur.execute("INSERT INTO public.birth_data (user_id, birth_date, birth_timezone) VALUES (%s, '1990-01-01', 'UTC');", (user_a,))
        cur.execute("INSERT INTO public.astro_private (user_id, source_birth_data_version, engine_version) VALUES (%s, 1, '1.0.0');", (user_a,))
        cur.execute("INSERT INTO public.astro_safe_profile (user_id, source_birth_data_version, engine_version, sun_sign) VALUES (%s, 1, '1.0.0', 'Aries');", (user_a,))
        cur.execute("INSERT INTO public.daily_energies (user_id, energy_date, engine_version) VALUES (%s, '2026-08-31', '1.0.0');", (user_a,))
        cur.execute("INSERT INTO public.notifications (user_id, type) VALUES (%s, 'welcome');", (user_a,))
        
        # Connections & Chat
        u_min, u_max = sorted([user_a, user_b])
        cur.execute("INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by) VALUES (%s, %s, 'accepted', %s);", (u_min, u_max, user_a))
        cur.execute("INSERT INTO public.compatibility_results (user_a_id, user_b_id, user_a_birth_data_version, user_b_birth_data_version, engine_version) VALUES (%s, %s, 1, 1, '1.0.0');", (u_min, u_max))
        
        conv_id = str(uuid.uuid4())
        cur.execute("INSERT INTO public.conversations (id, conversation_type, created_by) VALUES (%s, 'direct', %s);", (conv_id, user_a))
        cur.execute("INSERT INTO public.conversation_members (conversation_id, user_id) VALUES (%s, %s), (%s, %s);", (conv_id, user_a, conv_id, user_b))
        cur.execute("INSERT INTO public.messages (conversation_id, sender_user_id, body) VALUES (%s, %s, 'Hey');", (conv_id, user_a))
        
        # Hard-delete User A from auth.users (as superuser/admin)
        cur.execute("DELETE FROM auth.users WHERE id = %s;", (user_a,))
        
        # Verify all user A records are removed
        cur.execute("SELECT count(*) as cnt FROM public.profiles WHERE id = %s;", (user_a,))
        assert cur.fetchone()["cnt"] == 0
        
        cur.execute("SELECT count(*) as cnt FROM public.birth_data WHERE user_id = %s;", (user_a,))
        assert cur.fetchone()["cnt"] == 0
        
        cur.execute("SELECT count(*) as cnt FROM public.astro_private WHERE user_id = %s;", (user_a,))
        assert cur.fetchone()["cnt"] == 0
        
        cur.execute("SELECT count(*) as cnt FROM public.astro_safe_profile WHERE user_id = %s;", (user_a,))
        assert cur.fetchone()["cnt"] == 0
        
        cur.execute("SELECT count(*) as cnt FROM public.daily_energies WHERE user_id = %s;", (user_a,))
        assert cur.fetchone()["cnt"] == 0
        
        cur.execute("SELECT count(*) as cnt FROM public.notifications WHERE user_id = %s;", (user_a,))
        assert cur.fetchone()["cnt"] == 0
        
        cur.execute("SELECT count(*) as cnt FROM public.connections WHERE user_a_id = %s OR user_b_id = %s;", (user_a, user_a))
        assert cur.fetchone()["cnt"] == 0
        
        cur.execute("SELECT count(*) as cnt FROM public.compatibility_results WHERE user_a_id = %s OR user_b_id = %s;", (user_a, user_a))
        assert cur.fetchone()["cnt"] == 0
        
        cur.execute("SELECT count(*) as cnt FROM public.conversation_members WHERE user_id = %s;", (user_a,))
        assert cur.fetchone()["cnt"] == 0
        
        cur.execute("SELECT count(*) as cnt FROM public.messages WHERE sender_user_id = %s;", (user_a,))
        assert cur.fetchone()["cnt"] == 0

# ==============================================================================
# 7. TRIGGERS TESTS
# ==============================================================================

def test_triggers_and_version_bumping(db_conn):
    user_a = str(uuid.uuid4())
    create_test_user(db_conn, user_a, "user_a@test.jester.app", "User A")
    
    with db_conn.cursor() as cur:
        set_auth_context(cur, user_a, "authenticated")
        
        # 1. Insert birth data
        cur.execute("""
            INSERT INTO public.birth_data (user_id, birth_date, birth_timezone, place_label)
            VALUES (%s, '1995-05-15', 'UTC', 'Tbilisi');
        """, (user_a,))
        
        # 2. Update without changing astrology-relevant fields (e.g. same values)
        cur.execute("""
            UPDATE public.birth_data SET updated_at = now() WHERE user_id = %s;
        """, (user_a,))
        
        cur.execute("SELECT data_version FROM public.birth_data WHERE user_id = %s;", (user_a,))
        assert cur.fetchone()["data_version"] == 1
        
        # 3. Update place_label -> data_version increments
        cur.execute("""
            UPDATE public.birth_data SET place_label = 'Batumi' WHERE user_id = %s;
        """, (user_a,))
        
        cur.execute("SELECT data_version FROM public.birth_data WHERE user_id = %s;", (user_a,))
        assert cur.fetchone()["data_version"] == 2
        
        # 4. Profiles updated_at trigger
        cur.execute("SELECT updated_at FROM public.profiles WHERE id = %s;", (user_a,))
        orig_updated_at = cur.fetchone()["updated_at"]
        
        cur.execute("UPDATE public.profiles SET bio = 'New bio' WHERE id = %s;", (user_a,))
        cur.execute("SELECT updated_at FROM public.profiles WHERE id = %s;", (user_a,))
        new_updated_at = cur.fetchone()["updated_at"]
        assert new_updated_at >= orig_updated_at
