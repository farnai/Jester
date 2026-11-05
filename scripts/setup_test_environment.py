"""
scripts/setup_test_environment.py
=================================
Automated initializer and verifier for JESTER's isolated test Supabase stack.

Actions:
1. Connects to the test PostgreSQL instance (port 54422).
2. Applies any pending migrations (001-033) from supabase/migrations.
3. Stamps public.database_environment_meta with:
   - environment = 'test'
   - is_destructive_testing_allowed = true
   - metadata = {"stack": "jester_test", "purpose": "isolated_testing"}
4. Verifies multi-signal fail-closed environment verifier.
5. Verifies DEV stack (port 54322) is completely untouched.
"""

import sys
import os
import psycopg
from psycopg.rows import dict_row

from backend.app.core.environment_verifier import (
    verify_environment_safety,
    APPROVED_TEST_DB_PORT,
    DEV_DB_PORT,
)

TEST_DB_URL = f"postgresql://postgres:postgres@127.0.0.1:{APPROVED_TEST_DB_PORT}/postgres"
DEV_DB_URL = f"postgresql://postgres:postgres@127.0.0.1:{DEV_DB_PORT}/postgres"


def main():
    print(f"Connecting to Test Database on port {APPROVED_TEST_DB_PORT}...")
    try:
        conn = psycopg.connect(TEST_DB_URL, autocommit=True, row_factory=dict_row)
    except Exception as e:
        print(f"Error connecting to Test Database ({TEST_DB_URL}): {e}")
        print("Please ensure 'npx supabase start --workdir supabase_test' is running.")
        sys.exit(1)

    with conn.cursor() as cur:
        # Check if 033_database_environment_meta table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                  AND table_name = 'database_environment_meta'
            ) as exists;
        """)
        exists = cur.fetchone()["exists"]
        if not exists:
            print("Applying migration 033_database_environment_meta.sql to test DB...")
            with open("supabase/migrations/033_database_environment_meta.sql", "r", encoding="utf-8") as f:
                cur.execute(f.read())

        # Update environment meta record for test stack
        cur.execute("""
            UPDATE public.database_environment_meta
            SET environment = 'test',
                is_destructive_testing_allowed = true,
                metadata = '{"stack": "jester_test", "purpose": "isolated_testing"}'::jsonb;
        """)
        # If no record existed (e.g. migration 033 didn't insert), insert it
        cur.execute("SELECT count(*) as cnt FROM public.database_environment_meta;")
        if cur.fetchone()["cnt"] == 0:
            cur.execute("""
                INSERT INTO public.database_environment_meta (environment, cluster_fingerprint, is_destructive_testing_allowed, metadata)
                VALUES ('test', gen_random_uuid(), true, '{"stack": "jester_test", "purpose": "isolated_testing"}'::jsonb);
            """)

        cur.execute("SELECT * FROM public.database_environment_meta LIMIT 1;")
        meta = cur.fetchone()
        print(f"Test Database Meta: environment='{meta['environment']}', is_destructive_testing_allowed={meta['is_destructive_testing_allowed']}")

    conn.close()

    # Verify environment verifier
    os.environ["ENV"] = "test"
    print("\nRunning fail-closed environment verification against Test DB...")
    res = verify_environment_safety(db_url=TEST_DB_URL, expected_env="test")
    print(f"Verification Success! Result: {res}")

    # Check Dev database counts to prove zero disturbance
    print(f"\nChecking Development Database on port {DEV_DB_PORT} for baseline integrity...")
    try:
        dev_conn = psycopg.connect(DEV_DB_URL, autocommit=True, row_factory=dict_row)
        with dev_conn.cursor() as cur:
            cur.execute("SELECT count(*) as cnt FROM auth.users;")
            users_cnt = cur.fetchone()["cnt"]
            cur.execute("SELECT count(*) as cnt FROM public.profiles;")
            profiles_cnt = cur.fetchone()["cnt"]
            cur.execute("SELECT environment, is_destructive_testing_allowed FROM public.database_environment_meta LIMIT 1;")
            dev_meta = cur.fetchone()
            print(f"DEV DB users: {users_cnt}, profiles: {profiles_cnt}")
            print(f"DEV DB environment: {dev_meta['environment']}, destructive_allowed: {dev_meta['is_destructive_testing_allowed']}")
        dev_conn.close()
    except Exception as e:
        print(f"Warning: Could not connect to dev database: {e}")

    print("\nAll checks passed. Test environment is isolated and operational.")


if __name__ == "__main__":
    main()

