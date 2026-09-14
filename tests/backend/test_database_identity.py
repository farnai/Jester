import pytest
import uuid
import psycopg
from backend.app.core.database import verify_database_identity, DatabaseIdentityError, db_manager


def test_database_identity_passes_on_canonical_db():
    """Verify that current canonical local Supabase database passes all checks."""
    info = verify_database_identity()
    assert info["status"] == "healthy"
    assert info["port"] == 54322
    assert info["migration_version"] >= "025"
    assert info["city_count"] > 100000


def test_database_identity_fails_on_connection_error(monkeypatch):
    """Verify that fail-fast triggers on unconnectable DATABASE_URL."""
    monkeypatch.setattr(
        db_manager.settings,
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:54398/postgres?connect_timeout=2",
    )
    with pytest.raises(DatabaseIdentityError) as exc_info:
        verify_database_identity()
    assert "CRITICAL DATABASE CONNECTION FAILURE" in str(exc_info.value)
