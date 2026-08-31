import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class CompareRequest(BaseModel):
    target_user_id: uuid.UUID


class CompatibilitySignal(BaseModel):
    type: str
    category: str | None = None
    strength: str
    source_aspects: list[str] = Field(default_factory=list)
    label: str | None = None
    description: str | None = None


class StructuredCompatibilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID | None = None
    target_user_id: uuid.UUID
    score: float
    dimensions: dict[str, float] = Field(default_factory=dict)
    signals: list[dict[str, Any]] = Field(default_factory=list)
    best_topics: list[str] = Field(default_factory=list)
    conversation_starters: list[str] = Field(default_factory=list)
    data_quality: dict[str, Any] = Field(default_factory=dict)
    engine_version: str = "synastry-v1.0.0"
    calculated_at: datetime
