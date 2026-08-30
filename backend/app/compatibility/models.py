from typing import Any
from pydantic import BaseModel, Field


class CompatibilityScore(BaseModel):
    score: float
    signals: list[dict[str, Any]] = Field(default_factory=list)
    best_topics: list[str] = Field(default_factory=list)
    conversation_starters: list[str] = Field(default_factory=list)
