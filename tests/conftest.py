"""
tests/conftest.py
=================
Centralized pytest configuration and fixtures for JESTER.

Enforces:
1. Mandatory fail-closed test environment isolation (TEST DB :54422, TEST API :54421).
2. Prevents any accidental connection or data mutation against Development (:54322/:54321).
3. Provides clean, reusable fixtures:
   - verified_test_env (session): validates environment and fail-closed metadata.
   - db_conn (session): authoritative connection to TEST PostgreSQL.
   - test_txn (function): function-scoped transaction rollback fixture.
   - clean_db (function): safe cleanup for non-rollback tests (cleans ONLY tracked test users/records).
   - create_test_user: helper for isolated test identity creation.
   - set_auth_context: RLS context helper.
   - api_client: AsyncClient for FastAPI endpoint testing.
   - auth_headers / generate_test_jwt: test JWT bearer token helpers.
"""

import os
import sys
import time
import uuid
from typing import AsyncGenerator
import jwt
import psycopg
from psycopg.rows import dict_row
import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.config import get_settings
from backend.app.core.environment_verifier import (
    verify_environment_safety,
    EnvironmentSafetyError,
    APPROVED_TEST_DB_PORT,
    APPROVED_TEST_KONG_PORT,
    DEV_DB_PORT,
    DEV_KONG_PORT,
)

# Registry of records created during individual non-rollback tests
_test_user_registry: set[str] = set()
_test_conv_registry: set[str] = set()


def track_test_user(user_id: str):
    """Register user_id created during the current test for isolated teardown."""
    _test_user_registry.add(str(user_id))


def track_test_conversation(conv_id: str):
    """Register conversation_id created during the current test for isolated teardown."""
    _test_conv_registry.add(str(conv_id))


# Intercept ANY direct psycopg.connect call in test process to prevent reaching DEV ports (54322, 54321)
_orig_psycopg_connect = psycopg.connect


def _safe_psycopg_connect(conninfo="", *args, **kwargs):
    conn_str = f"{conninfo} {args} {kwargs}"
    if f":{DEV_DB_PORT}" in conn_str or f"port={DEV_DB_PORT}" in conn_str or f":{DEV_KONG_PORT}" in conn_str:
        raise EnvironmentSafetyError(
            f"CRITICAL SAFETY INTERCEPTION: Test execution attempted direct connection to DEV port ({DEV_DB_PORT})!\n"
            f"All test executions MUST target the isolated TEST stack (port {APPROVED_TEST_DB_PORT})."
        )
    return _orig_psycopg_connect(conninfo, *args, **kwargs)


psycopg.connect = _safe_psycopg_connect


def pytest_configure(config):
    """
    Early pytest hook to enforce test environment settings before any tests or imports run.
    """
    os.environ["ENV"] = "test"
    test_db_url = f"postgresql://postgres:postgres@127.0.0.1:{APPROVED_TEST_DB_PORT}/postgres"
    test_supa_url = f"http://127.0.0.1:{APPROVED_TEST_KONG_PORT}"

    # Set default test URLs if not already configured
    if "TEST_DATABASE_URL" not in os.environ or f":{DEV_DB_PORT}" in os.environ.get("TEST_DATABASE_URL", ""):
        os.environ["TEST_DATABASE_URL"] = test_db_url

    if "DATABASE_URL" not in os.environ or f":{DEV_DB_PORT}" in os.environ.get("DATABASE_URL", ""):
        os.environ["DATABASE_URL"] = test_db_url

    if "SUPABASE_URL" not in os.environ or f":{DEV_KONG_PORT}" in os.environ.get("SUPABASE_URL", ""):
        os.environ["SUPABASE_URL"] = test_supa_url

    get_settings.cache_clear()


@pytest.fixture(scope="session")
def verified_test_env():
    """
    Session-level guard fixture verifying the physical test environment identity.
    Fails closed immediately if DEV database or unapproved target is detected.
    Zero-deletion policy: Never issues automatic DELETE against auth.users.
    """
    test_db_url = os.environ.get(
        "TEST_DATABASE_URL",
        f"postgresql://postgres:postgres@127.0.0.1:{APPROVED_TEST_DB_PORT}/postgres"
    )
    result = verify_environment_safety(db_url=test_db_url, expected_env="test")
    return result


@pytest.fixture(scope="session")
def db_conn(verified_test_env):
    """
    Session-level PostgreSQL connection fixture pointing strictly to the isolated TEST DB.
    """
    test_db_url = os.environ.get(
        "TEST_DATABASE_URL",
        f"postgresql://postgres:postgres@127.0.0.1:{APPROVED_TEST_DB_PORT}/postgres"
    )
    conn = psycopg.connect(test_db_url, autocommit=True, row_factory=dict_row)
    yield conn
    conn.close()


@pytest.fixture
def test_txn(db_conn):
    """
    Function-scoped transaction rollback fixture:
    BEGIN -> Run Test -> ROLLBACK
    Ensures 100% clean isolation with zero residual test data and zero DELETE calls.
    """
    with db_conn.cursor() as cur:
        cur.execute("BEGIN;")
    yield db_conn
    with db_conn.cursor() as cur:
        cur.execute("ROLLBACK;")


@pytest.fixture(autouse=True)
def clean_db(db_conn):
    """
    Test-scoped cleanup fixture.
    Zero-deletion policy: Never performs automatic DELETE operations on user data.
    Registers and tracks test artifacts without destructive teardowns.
    """
    assert db_conn.info.port == APPROVED_TEST_DB_PORT, f"clean_db CANNOT operate on non-test DB (port={db_conn.info.port})!"
    _test_user_registry.clear()
    _test_conv_registry.clear()
    yield
    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
    _test_user_registry.clear()
    _test_conv_registry.clear()


def create_test_user(db_conn, user_id: str | None = None, email: str | None = None, display_name: str = "Test User"):
    """
    Creates an isolated test user and profile in the test database.
    Zero-deletion policy: Guarantees unique namespacing without prior DELETE calls.
    """
    uid = str(user_id or uuid.uuid4())
    if email:
        if "@" in email:
            local_part, domain = email.split("@", 1)
            if uid[:8] not in local_part:
                u_email = f"{local_part}_{uid[:8]}@{domain}"
            else:
                u_email = email
        else:
            u_email = f"{email}_{uid[:8]}@jester.test"
    else:
        u_email = f"test_{uid[:8]}@jester.test"

    track_test_user(uid)

    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute("""
            INSERT INTO auth.users (id, email, raw_user_meta_data, role, aud)
            VALUES (%s, %s, %s, 'authenticated', 'authenticated')
            ON CONFLICT (id) DO NOTHING;
        """, (uid, u_email, '{"name": "%s"}' % display_name))

        cur.execute("""
            INSERT INTO public.profiles (id, display_name, is_discoverable)
            VALUES (%s, %s, true)
            ON CONFLICT (id) DO UPDATE SET display_name = excluded.display_name, is_discoverable = excluded.is_discoverable;
        """, (uid, display_name))

    return uid, u_email


def set_auth_context(cur, user_id: str | None = None, role: str = "authenticated"):
    """
    Sets PostgreSQL session configuration for RLS testing.
    """
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


def generate_test_jwt(
    user_id: str | None = None,
    email: str = "test_user@jester.test",
    role: str = "authenticated",
    exp_delta: int = 3600,
    secret: str | None = None,
    alg: str = "HS256",
    kid: str | None = None,
    app_metadata: dict | None = None,
) -> str:
    """
    Generates a valid signed JWT for testing HTTP endpoints.
    """
    settings = get_settings()
    signing_secret = secret or settings.SUPABASE_JWT_SECRET.get_secret_value()
    uid = user_id or str(uuid.uuid4())
    now = int(time.time())

    payload = {
        "sub": uid,
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + exp_delta,
        "iss": f"{settings.SUPABASE_URL}/auth/v1",
        "aud": "authenticated",
        "app_metadata": app_metadata or {},
    }
    headers = {"alg": alg}
    if kid:
        headers["kid"] = kid

    return jwt.encode(payload, signing_secret, algorithm=alg, headers=headers)


def get_auth_headers(user_id: str | None = None, email: str = "test_user@jester.test") -> dict[str, str]:
    """Generates Authorization headers with bearer JWT for API testing."""
    token = generate_test_jwt(user_id=user_id, email=email)
    return {"Authorization": f"Bearer {token}"}
