import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    display_name: str
    avatar_url: str | None = None
    bio: str | None = None
    city: str | None = None
    occupation: str | None = None
    timezone: str = "UTC"
    is_discoverable: bool = True


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    city: str | None = None
    occupation: str | None = None
    timezone: str | None = None
    is_discoverable: bool | None = None


class ProfileResponse(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
