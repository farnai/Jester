"""
tests/backend/test_environment_isolation_guards.py
==================================================
Automated regression tests proving that JESTER's fail-closed
environment verifier prevents any test execution against Development resources.
"""

import os
import pytest
import psycopg

from backend.app.core.environment_verifier import (
    verify_environment_safety,
    EnvironmentSafetyError,
    APPROVED_TEST_DB_PORT,
    APPROVED_TEST_KONG_PORT,
    DEV_DB_PORT,
    DEV_KONG_PORT,
)


def test_dev_database_port_is_strictly_rejected():
    """Verify that targeting port 54322 raises EnvironmentSafetyError."""
    dev_url = f"postgresql://postgres:postgres@127.0.0.1:{DEV_DB_PORT}/postgres"
    with pytest.raises(EnvironmentSafetyError) as exc_info:
        verify_environment_safety(db_url=dev_url, expected_env="test")
    assert f"points to DEVELOPMENT port {DEV_DB_PORT}" in str(exc_info.value)


def test_dev_kong_port_is_strictly_rejected(monkeypatch):
    """Verify that targeting port 54321 on SUPABASE_URL raises EnvironmentSafetyError."""
    test_db_url = f"postgresql://postgres:postgres@127.0.0.1:{APPROVED_TEST_DB_PORT}/postgres"
    monkeypatch.setenv("SUPABASE_URL", f"http://127.0.0.1:{DEV_KONG_PORT}")
    with pytest.raises(EnvironmentSafetyError) as exc_info:
        verify_environment_safety(db_url=test_db_url, expected_env="test")
    assert f"points to DEVELOPMENT Kong port {DEV_KONG_PORT}" in str(exc_info.value)


def test_missing_test_db_url_never_falls_back_to_dev(monkeypatch):
    """Verify that missing TEST_DATABASE_URL raises EnvironmentSafetyError and does not fall back."""
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(EnvironmentSafetyError) as exc_info:
        verify_environment_safety(db_url="", expected_env="test")
    assert "Missing TEST database configuration" in str(exc_info.value)


def test_non_test_environment_is_rejected(monkeypatch):
    """Verify that ENV=development or ENV=production is rejected in test mode."""
    test_db_url = f"postgresql://postgres:postgres@127.0.0.1:{APPROVED_TEST_DB_PORT}/postgres"
    monkeypatch.setenv("ENV", "development")
    with pytest.raises(EnvironmentSafetyError) as exc_info:
        verify_environment_safety(db_url=test_db_url, expected_env="test")
    assert "expected 'test'" in str(exc_info.value)


def test_database_metadata_rejects_non_test_environments():
    """Verify that a database marked environment='development' or is_destructive_testing_allowed=False is rejected."""
    class MockCursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, query, params=None):
            pass

        def fetchone(self):
            return {
                "exists": True,
                "environment": "development",
                "cluster_fingerprint": "dev-stack",
                "is_destructive_testing_allowed": False,
            }

    class MockConnection:
        def cursor(self):
            return MockCursor()

        def close(self):
            pass

    with pytest.raises(EnvironmentSafetyError) as exc_info:
        verify_environment_safety(
            db_url=f"postgresql://postgres:postgres@127.0.0.1:{APPROVED_TEST_DB_PORT}/postgres",
            expected_env="test",
            conn=MockConnection(),
        )
    assert "Connected database reports environment='development'" in str(exc_info.value)


def test_approved_test_environment_passes():
    """Verify that the isolated test database on port 54422 passes all checks."""
    test_db_url = f"postgresql://postgres:postgres@127.0.0.1:{APPROVED_TEST_DB_PORT}/postgres"
    res = verify_environment_safety(db_url=test_db_url, expected_env="test")
    assert res["status"] == "verified"
    assert res["environment"] == "test"
    assert res["is_destructive_testing_allowed"] is True
    assert res["port"] == APPROVED_TEST_DB_PORT

