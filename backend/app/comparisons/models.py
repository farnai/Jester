import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class CompareRequest(BaseModel):
    target_user_id: uuid.UUID


class CompatibilitySignal(BaseModel):
    type: str
    strength: str
    description: str | None = None


class StructuredCompatibilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID | None = None
    target_user_id: uuid.UUID
    score: float
    signals: list[dict[str, Any]] = Field(default_factory=list)
    best_topics: list[str] = Field(default_factory=list)
    conversation_starters: list[str] = Field(default_factory=list)
    engine_version: str
    calculated_at: datetime
