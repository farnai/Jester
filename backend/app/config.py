from functools import lru_cache
from typing import Literal
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENV: Literal["development", "test", "production"] = "development"
    PROJECT_NAME: str = "Jester API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/v1"

    # Supabase Connection
    SUPABASE_URL: str = "http://127.0.0.1:54321"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
    SUPABASE_SERVICE_ROLE_KEY: SecretStr = Field(
        default=SecretStr(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
        )
    )
    SUPABASE_JWT_SECRET: SecretStr = Field(
        default=SecretStr("super-secret-jwt-token-with-at-least-32-characters-long")
    )
    SUPABASE_JWKS_URL: str | None = None

    # Database Direct Connection
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

    # Security & CORS
    CORS_ORIGINS: list[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["*"]

    # AI / LLM Configuration
    OPENAI_API_KEY: SecretStr | None = None
    LLM_MODEL: str = "gpt-4o-mini"

    # Sentry Monitoring
    SENTRY_DSN: str | None = None

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def is_test(self) -> bool:
        return self.ENV == "test"

    @property
    def jwks_url(self) -> str:
        if self.SUPABASE_JWKS_URL:
            return self.SUPABASE_JWKS_URL
        return f"{self.SUPABASE_URL}/auth/v1/.well-known/jwks.json"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
