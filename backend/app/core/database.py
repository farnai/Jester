from contextlib import asynccontextmanager
from typing import AsyncGenerator
import psycopg
from psycopg.rows import dict_row

from backend.app.config import get_settings


class DatabaseManager:
    def __init__(self):
        self.settings = get_settings()

    def get_connection(self) -> psycopg.Connection:
        """
        Creates a new connection directly to PostgreSQL with dict_row factory.
        """
        return psycopg.connect(
            self.settings.DATABASE_URL,
            autocommit=True,
            row_factory=dict_row,
        )

    def get_admin_headers(self) -> dict[str, str]:
        """
        Returns headers for privileged admin/service_role operations.
        """
        return {
            "apikey": self.settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value(),
            "Authorization": f"Bearer {self.settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value()}",
        }

    def get_user_headers(self, user_token: str) -> dict[str, str]:
        """
        Returns headers for user-scoped operations respecting RLS.
        """
        return {
            "apikey": self.settings.SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {user_token}",
        }


db_manager = DatabaseManager()


class DatabaseIdentityError(RuntimeError):
    """Raised when the connected database fails JESTER identity/schema verification."""
    pass


def verify_database_identity(conn: psycopg.Connection | None = None) -> dict[str, any]:
    """
    Validates that the database connected via DATABASE_URL is the authoritative
    JESTER local Supabase PostgreSQL database (or production equivalent) and has
    all required schemas, migrations, tables, and columns.
    
    Fails fast with actionable instructions if connected to an unmigrated or wrong database.
    """
    should_close = False
    if conn is None:
        try:
            conn = db_manager.get_connection()
            should_close = True
        except Exception as e:
            raise DatabaseIdentityError(
                f"\n{'=' * 80}\n"
                f"CRITICAL DATABASE CONNECTION FAILURE:\n"
                f"Could not connect to database at DATABASE_URL: {db_manager.settings.DATABASE_URL}\n"
                f"Underlying error: {e}\n\n"
                f"ACTION REQUIRED:\n"
                f"1. Ensure the local Supabase Docker stack is running: 'npx supabase start'\n"
                f"2. Verify that Docker is running and port 54322 is exposed.\n"
                f"{'=' * 80}"
            ) from e

    try:
        with conn.cursor() as cur:
            # 1. Verify schema_migrations table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'supabase_migrations' 
                      AND table_name = 'schema_migrations'
                );
            """)
            if not cur.fetchone()["exists"]:
                raise DatabaseIdentityError(
                    f"\n{'=' * 80}\n"
                    f"CRITICAL DATABASE IDENTITY ERROR: Missing Supabase Migrations Table!\n"
                    f"The connected database ({conn.info.host}:{conn.info.port}/{conn.info.dbname}) "
                    f"does not appear to be the JESTER Supabase database.\n"
                    f"Table 'supabase_migrations.schema_migrations' does not exist.\n\n"
                    f"ACTION REQUIRED:\n"
                    f"1. Run local Supabase migrations: 'npx supabase migration up --local'\n"
                    f"2. Ensure DATABASE_URL points to the Supabase database (default port 54322).\n"
                    f"{'=' * 80}"
                )

            # 2. Verify latest migration
            cur.execute("SELECT version FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 1;")
            latest_row = cur.fetchone()
            latest_version = latest_row["version"] if latest_row else None
            required_migration = "025"
            if not latest_version or latest_version < required_migration:
                raise DatabaseIdentityError(
                    f"\n{'=' * 80}\n"
                    f"CRITICAL DATABASE SCHEMA ERROR: Stale Migration State!\n"
                    f"Connected database ({conn.info.host}:{conn.info.port}/{conn.info.dbname}) "
                    f"is at migration version '{latest_version}', but JESTER requires version '{required_migration}'.\n\n"
                    f"ACTION REQUIRED:\n"
                    f"Run: 'npx supabase migration up --local'\n"
                    f"{'=' * 80}"
                )

            # 3. Verify required schemas and tables
            required_tables = [
                ("auth", "users"),
                ("public", "profiles"),
                ("public", "birth_data"),
                ("public", "countries"),
                ("public", "cities"),
                ("public", "connections"),
                ("public", "compatibility_results"),
            ]
            for schema, table in required_tables:
                cur.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s);",
                    (schema, table)
                )
                if not cur.fetchone()["exists"]:
                    raise DatabaseIdentityError(
                        f"\n{'=' * 80}\n"
                        f"CRITICAL DATABASE SCHEMA ERROR: Missing Required Table '{schema}.{table}'!\n"
                        f"Target DB: {conn.info.host}:{conn.info.port}/{conn.info.dbname}\n\n"
                        f"ACTION REQUIRED:\n"
                        f"Run: 'npx supabase migration up --local'\n"
                        f"{'=' * 80}"
                    )

            # 4. Verify required columns
            required_columns = [
                ("public", "profiles", "first_name"),
                ("public", "profiles", "last_name"),
                ("public", "profiles", "city_id"),
                ("public", "birth_data", "birth_city_id"),
            ]
            for schema, table, col in required_columns:
                cur.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = %s AND table_name = %s AND column_name = %s);",
                    (schema, table, col)
                )
                if not cur.fetchone()["exists"]:
                    raise DatabaseIdentityError(
                        f"\n{'=' * 80}\n"
                        f"CRITICAL DATABASE SCHEMA ERROR: Missing Column '{schema}.{table}.{col}'!\n"
                        f"Target DB: {conn.info.host}:{conn.info.port}/{conn.info.dbname}\n\n"
                        f"ACTION REQUIRED:\n"
                        f"Run: 'npx supabase migration up --local'\n"
                        f"{'=' * 80}"
                    )

            # 5. Verify canonical geo seed data
            cur.execute("SELECT count(*) as cnt FROM public.cities;")
            city_count = cur.fetchone()["cnt"]
            if city_count < 100:
                raise DatabaseIdentityError(
                    f"\n{'=' * 80}\n"
                    f"CRITICAL DATABASE DATA ERROR: Canonical Geo Dataset Not Seeded!\n"
                    f"Found {city_count} cities in public.cities (expected ~152k).\n\n"
                    f"ACTION REQUIRED:\n"
                    f"Run: 'python scripts/seed_geo_dataset.py'\n"
                    f"{'=' * 80}"
                )

            return {
                "status": "healthy",
                "host": conn.info.host,
                "port": conn.info.port,
                "dbname": conn.info.dbname,
                "migration_version": latest_version,
                "city_count": city_count,
            }
    finally:
        if should_close:
            conn.close()


def get_db():
    conn = db_manager.get_connection()
    try:
        yield conn
    finally:
        conn.close()

