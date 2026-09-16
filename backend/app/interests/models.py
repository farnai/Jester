import uuid
from pydantic import BaseModel, ConfigDict


class InterestItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    slug: str
    category_name: str
    category_slug: str
    category_icon: str | None = None
    sort_order: int = 0


class InterestsListResponse(BaseModel):
    items: list[InterestItem]


class UserInterestsUpdateRequest(BaseModel):
    interest_ids: list[uuid.UUID]


class UserInterestsResponse(BaseModel):
    interest_ids: list[uuid.UUID]
