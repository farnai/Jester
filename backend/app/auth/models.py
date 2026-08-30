import uuid
from typing import Any
from pydantic import BaseModel, Field


class AuthenticatedUser(BaseModel):
    id: uuid.UUID
    email: str | None = None
    role: str = "authenticated"
    app_metadata: dict[str, Any] = Field(default_factory=dict)
    user_metadata: dict[str, Any] = Field(default_factory=dict)


class TokenPayload(BaseModel):
    sub: str
    iss: str | None = None
    aud: str | list[str] | None = None
    exp: int
    iat: int | None = None
    email: str | None = None
    role: str = "authenticated"
    app_metadata: dict[str, Any] = Field(default_factory=dict)
    user_metadata: dict[str, Any] = Field(default_factory=dict)
