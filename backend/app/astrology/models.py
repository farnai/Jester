import uuid
from datetime import date, datetime, time
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

BirthTimePrecision = Literal["exact", "approximate", "unknown"]


class BirthDataInput(BaseModel):
    birth_date: date
    birth_time: time | None = None
    birth_time_precision: BirthTimePrecision
    birth_timezone: str
    latitude: float | None = None
    longitude: float | None = None
    place_label: str | None = None


class NatalChartPlacements(BaseModel):
    """
    Internal calculation results.
    Strictly server-side only (stored in astro_private).
    """
    sun_longitude: float
    moon_longitude: float
    mercury_longitude: float
    venus_longitude: float
    mars_longitude: float
    jupiter_longitude: float
    saturn_longitude: float
    uranus_longitude: float
    neptune_longitude: float
    pluto_longitude: float
    ascendant_longitude: float | None = None
    houses: list[float] | None = None
    retrogrades: dict[str, bool] = Field(default_factory=dict)
    source_birth_data_version: int = 1
    engine_version: str = "1.0.0"


class SafeDerivedAstrology(BaseModel):
    """
    Safe derived profile for public / product exposure (stored in astro_safe_profile).
    """
    user_id: uuid.UUID
    sun_sign: str
    moon_sign: str
    ascendant_sign: str | None = None
    element_primary: str
    modality_primary: str
    source_birth_data_version: int
    engine_version: str
    updated_at: datetime | None = None


class SafeDerivedAstrologyResponse(BaseModel):
    """
    API Response model for safe derived astrology.
    """
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    sun_sign: str
    moon_sign: str
    ascendant_sign: str | None = None
    element_primary: str
    modality_primary: str
    source_birth_data_version: int
    engine_version: str
    updated_at: datetime
