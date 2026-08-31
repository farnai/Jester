"""
Compatibility Pydantic data models for Synastry V1.
"""
from typing import Any
import uuid
from pydantic import BaseModel, Field


class Signal(BaseModel):
    type: str
    category: str
    strength: str
    source_aspects: list[str] = Field(default_factory=list)
    label: str


class DataQuality(BaseModel):
    time_precision: str
    confidence: float
    houses_used: bool
    ascendant_used: bool


class Dimensions(BaseModel):
    emotional_harmony: float
    communication: float
    attraction: float
    growth_long_term: float


class CompatibilityScore(BaseModel):
    score: float
    dimensions: dict[str, float] = Field(default_factory=dict)
    signals: list[dict[str, Any]] = Field(default_factory=list)
    best_topics: list[str] = Field(default_factory=list)
    conversation_starters: list[str] = Field(default_factory=list)
    data_quality: dict[str, Any] = Field(default_factory=dict)
    evidence_trace: list[dict[str, Any]] = Field(default_factory=list)
    engine_version: str = "synastry-v1.0.0"
