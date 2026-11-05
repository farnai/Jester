"""
scripts/verify_isolation_proof.py
=================================
Automated proof of physical isolation between DEV and TEST Supabase environments.
"""

import uuid
import psycopg
from psycopg.rows import dict_row

DEV_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
TEST_URL = "postgresql://postgres:postgres@127.0.0.1:54422/postgres"


def main():
    dev_conn = psycopg.connect(DEV_URL, autocommit=True, row_factory=dict_row)
    test_conn = psycopg.connect(TEST_URL, autocommit=True, row_factory=dict_row)

    print("=== 1. PRE-MUTATION COUNTS ===")
    with dev_conn.cursor() as cur:
        cur.execute("SELECT count(*) as cnt FROM auth.users;")
        dev_users_before = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.profiles;")
        dev_profiles_before = cur.fetchone()["cnt"]
        print(f"DEV DB: users={dev_users_before}, profiles={dev_profiles_before}")

    with test_conn.cursor() as cur:
        cur.execute("SELECT count(*) as cnt FROM auth.users;")
        test_users_before = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.profiles;")
        test_profiles_before = cur.fetchone()["cnt"]
        print(f"TEST DB: users={test_users_before}, profiles={test_profiles_before}")

    print("\n=== 2. PERFORMING WRITE MUTATION ON TEST DB (54422) ===")
    test_user_id = str(uuid.uuid4())
    with test_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at, raw_app_meta_data, raw_user_meta_data, created_at, updated_at)
            VALUES (%s, %s, 'test_encrypted_pw', now(), '{"provider":"email"}'::jsonb, '{"name":"Isolated Test User"}'::jsonb, now(), now());
            """,
            (test_user_id, f"isolated_{test_user_id[:8]}@jester.test"),
        )
        cur.execute(
            """
            INSERT INTO public.profiles (id, display_name, first_name, last_name, onboarding_completed, onboarding_step)
            VALUES (%s, 'IsolatedTester', 'Isolated', 'Tester', true, 3);
            """,
            (test_user_id,),
        )
        print(f"Created test user {test_user_id} in TEST DB.")

    print("\n=== 3. POST-MUTATION COUNTS & ISOLATION VERIFICATION ===")
    with dev_conn.cursor() as cur:
        cur.execute("SELECT count(*) as cnt FROM auth.users;")
        dev_users_after = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.profiles;")
        dev_profiles_after = cur.fetchone()["cnt"]
        cur.execute("SELECT 1 FROM auth.users WHERE id = %s;", (test_user_id,))
        leaked_user = cur.fetchone()
        print(f"DEV DB: users={dev_users_after} (delta: {dev_users_after - dev_users_before}), profiles={dev_profiles_after} (delta: {dev_profiles_after - dev_profiles_before})")
        print(f"Did test user leak into DEV DB? {bool(leaked_user)}")

    with test_conn.cursor() as cur:
        cur.execute("SELECT count(*) as cnt FROM auth.users;")
        test_users_after = cur.fetchone()["cnt"]
        cur.execute("SELECT count(*) as cnt FROM public.profiles;")
        test_profiles_after = cur.fetchone()["cnt"]
        print(f"TEST DB: users={test_users_after} (delta: {test_users_after - test_users_before}), profiles={test_profiles_after} (delta: {test_profiles_after - test_profiles_before})")

    assert dev_users_before == dev_users_after, "DEV users count changed!"
    assert dev_profiles_before == dev_profiles_after, "DEV profiles count changed!"
    assert leaked_user is None, "Test user leaked into DEV DB!"
    assert test_users_after == test_users_before + 1, "TEST user was not added to TEST DB!"

    print("\n>>> ISOLATION VERIFICATION 100% SUCCESSFUL: ZERO IMPACT ON DEV ENVIRONMENT! <<<")
    dev_conn.close()
    test_conn.close()


if __name__ == "__main__":
    main()
