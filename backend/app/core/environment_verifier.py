"""
backend.app.core.environment_verifier
======================================
Fail-closed multi-signal environment identity verification module for JESTER.

This module guarantees that no test runner, test fixture, or automated script
can execute against the persistent Development or Production databases.

Enforces:
1. Signal 1 (Port Check): Prevents test execution if URL matches canonical Dev ports (54322, 54321).
2. Signal 2 (Env Variable): Verifies ENV == 'test' when running tests.
3. Signal 3 (Database Metadata): Queries public.database_environment_meta to verify
   that environment == 'test' AND is_destructive_testing_allowed == true.
4. Fail-closed: If ANY check fails, is missing, or is ambiguous, raises EnvironmentSafetyError.
"""

from typing import Any
import os
import urllib.parse
import psycopg
from psycopg.rows import dict_row


class EnvironmentSafetyError(RuntimeError):
    """Raised when an environment safety invariant is violated."""
    pass


DEV_DB_PORT = 54322
DEV_KONG_PORT = 54321
APPROVED_TEST_DB_PORT = 54422
APPROVED_TEST_KONG_PORT = 54421


def get_target_port(url_string: str) -> int | None:
    """Extracts port number from a database or HTTP URL."""
    try:
        parsed = urllib.parse.urlparse(url_string)
        if parsed.port:
            return parsed.port
        # If postgresql format without standard scheme
        if ":" in parsed.netloc:
            parts = parsed.netloc.split(":")
            if len(parts) > 1 and parts[-1].isdigit():
                return int(parts[-1])
    except Exception:
        pass
    return None


def verify_environment_safety(
    db_url: str | None = None,
    expected_env: str = "test",
    conn: psycopg.Connection | None = None,
) -> dict[str, Any]:
    """
    Performs multi-signal fail-closed environment verification.
    
    If expected_env is 'test':
    - Signals that target matches DEV (port 54322/54321) will raise EnvironmentSafetyError immediately.
    - Database environment meta record must exist with environment == 'test' and
      is_destructive_testing_allowed == true.
    """
    effective_url = db_url or os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    current_env = os.getenv("ENV", "development").lower()
    supabase_url = os.getenv("SUPABASE_URL", "")

    # --- Signal 1: Operating Port & Configuration Check ---
    if expected_env == "test":
        if not effective_url:
            raise EnvironmentSafetyError(
                f"\n{'=' * 80}\n"
                f"CRITICAL SAFETY VIOLATION: FAIL-CLOSED TEST ABORT!\n"
                f"Missing TEST database configuration! Cannot fall back to DEV.\n"
                f"Set TEST_DATABASE_URL to the isolated test database (port {APPROVED_TEST_DB_PORT}).\n"
                f"{'=' * 80}"
            )

        target_port = get_target_port(effective_url)
        if target_port in (DEV_DB_PORT, DEV_KONG_PORT) or f":{DEV_DB_PORT}" in effective_url or f":{DEV_KONG_PORT}" in effective_url:
            raise EnvironmentSafetyError(
                f"\n{'=' * 80}\n"
                f"CRITICAL SAFETY VIOLATION: FAIL-CLOSED TEST ABORT!\n"
                f"Test execution target URL ({effective_url}) points to DEVELOPMENT port {target_port or DEV_DB_PORT}!\n"
                f"Automated tests are strictly forbidden from connecting to port {DEV_DB_PORT} / {DEV_KONG_PORT}.\n"
                f"Target must be the isolated test stack (port {APPROVED_TEST_DB_PORT} / {APPROVED_TEST_KONG_PORT}).\n"
                f"{'=' * 80}"
            )

        # Check Supabase Gateway URL
        if supabase_url:
            supa_port = get_target_port(supabase_url)
            if supa_port == DEV_KONG_PORT or f":{DEV_KONG_PORT}" in supabase_url:
                raise EnvironmentSafetyError(
                    f"\n{'=' * 80}\n"
                    f"CRITICAL SAFETY VIOLATION: FAIL-CLOSED TEST ABORT!\n"
                    f"SUPABASE_URL ({supabase_url}) points to DEVELOPMENT Kong port {DEV_KONG_PORT}!\n"
                    f"Automated tests must connect to TEST Kong port {APPROVED_TEST_KONG_PORT}.\n"
                    f"{'=' * 80}"
                )

        # Signal 2: Operating Environment Check
        if current_env != "test":
            raise EnvironmentSafetyError(
                f"\n{'=' * 80}\n"
                f"CRITICAL SAFETY VIOLATION: FAIL-CLOSED TEST ABORT!\n"
                f"Environment variable ENV is set to '{current_env}', expected 'test'.\n"
                f"Set ENV=test before executing test suites.\n"
                f"{'=' * 80}"
            )

    # --- Signal 3: Database Metadata Check ---
    should_close = False
    active_conn = conn
    if active_conn is None and effective_url:
        try:
            active_conn = psycopg.connect(effective_url, row_factory=dict_row)
            should_close = True
        except Exception as e:
            raise EnvironmentSafetyError(
                f"Could not connect to database at {effective_url} to verify environment: {e}"
            ) from e

    if active_conn is not None:
        try:
            with active_conn.cursor() as cur:
                # Check if public.database_environment_meta table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                          AND table_name = 'database_environment_meta'
                    ) as exists;
                """)
                res = cur.fetchone()
                table_exists = res["exists"] if isinstance(res, dict) else (res[0] if res else False)
                if not table_exists:
                    if expected_env == "test":
                        raise EnvironmentSafetyError(
                            f"\n{'=' * 80}\n"
                            f"CRITICAL SAFETY VIOLATION: FAIL-CLOSED TEST ABORT!\n"
                            f"Target database lacks 'public.database_environment_meta' table.\n"
                            f"Cannot verify that this is an approved isolated test database.\n"
                            f"{'=' * 80}"
                        )
                    return {"status": "unverified", "reason": "missing_meta_table"}

                cur.execute("""
                    SELECT environment, cluster_fingerprint, is_destructive_testing_allowed, initialized_at, metadata
                    FROM public.database_environment_meta
                    LIMIT 1;
                """)
                meta = cur.fetchone()
                if not meta:
                    raise EnvironmentSafetyError(
                        f"\n{'=' * 80}\n"
                        f"CRITICAL SAFETY VIOLATION: FAIL-CLOSED TEST ABORT!\n"
                        f"public.database_environment_meta has NO records!\n"
                        f"Database is un-fingerprinted. Execution aborted.\n"
                        f"{'=' * 80}"
                    )

                env_val = meta["environment"] if isinstance(meta, dict) else meta[0]
                cluster_fp = meta["cluster_fingerprint"] if isinstance(meta, dict) else meta[1]
                destructive_allowed = meta["is_destructive_testing_allowed"] if isinstance(meta, dict) else meta[2]

                if expected_env == "test":
                    if env_val != "test" or not destructive_allowed:
                        raise EnvironmentSafetyError(
                            f"\n{'=' * 80}\n"
                            f"CRITICAL SAFETY VIOLATION: FAIL-CLOSED TEST ABORT!\n"
                            f"Connected database reports environment='{env_val}', "
                            f"is_destructive_testing_allowed={destructive_allowed}.\n"
                            f"Automated test execution is REFUSED on non-test environments.\n"
                            f"{'=' * 80}"
                        )

                return {
                    "status": "verified",
                    "environment": env_val,
                    "cluster_fingerprint": str(cluster_fp),
                    "is_destructive_testing_allowed": destructive_allowed,
                    "host": active_conn.info.host,
                    "port": active_conn.info.port,
                    "dbname": active_conn.info.dbname,
                }
        finally:
            if should_close:
                active_conn.close()

    return {"status": "unverified", "reason": "no_connection"}


def assert_test_environment(conn: psycopg.Connection | None = None, db_url: str | None = None) -> None:
    """Convenience assertion helper for pytest fixtures."""
    verify_environment_safety(db_url=db_url, expected_env="test", conn=conn)
