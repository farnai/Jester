import uuid
from pydantic import BaseModel, ConfigDict


class CanonicalCountry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_id: int
    iso2: str
    name: str
    native_name: str | None = None
    phone_code: str | None = None


class CanonicalCity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_id: int
    country_id: uuid.UUID
    country_code: str
    country_name: str
    name: str
    name_ascii: str
    state_or_region: str | None = None
    latitude: float
    longitude: float
    timezone: str
    is_major_city: bool = False
    display_name: str


class CitySearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city_id: uuid.UUID
    name: str
    display_name: str
    country_name: str
    country_code: str
    region: str | None = None


class CitySearchResponse(BaseModel):
    items: list[CitySearchResult]

