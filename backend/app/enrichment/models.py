import uuid
from pydantic import BaseModel, ConfigDict


class PersonalityTraitItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    name_ka: str
    name_en: str
    sort_order: int = 0


class PersonalityTraitsListResponse(BaseModel):
    items: list[PersonalityTraitItem]


class UserPersonalityTraitsResponse(BaseModel):
    trait_ids: list[uuid.UUID]


class UserPersonalityTraitsUpdateRequest(BaseModel):
    trait_ids: list[uuid.UUID]


class ConnectionIntentionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    name_ka: str
    name_en: str
    icon: str | None = None
    sort_order: int = 0


class ConnectionIntentionsListResponse(BaseModel):
    items: list[ConnectionIntentionItem]


class UserConnectionIntentionsResponse(BaseModel):
    intention_ids: list[uuid.UUID]


class UserConnectionIntentionsUpdateRequest(BaseModel):
    intention_ids: list[uuid.UUID]


class PersonPersonalityResponse(BaseModel):
    items: list[PersonalityTraitItem]
    visibility: str = "public"


class PersonIntentionsResponse(BaseModel):
    items: list[ConnectionIntentionItem]
    visibility: str = "public"

