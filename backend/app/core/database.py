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


def get_db():
    conn = db_manager.get_connection()
    try:
        yield conn
    finally:
        conn.close()
