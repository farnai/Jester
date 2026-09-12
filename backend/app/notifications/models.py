import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    notification_type: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    read_at: datetime | None = None
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_notification_type(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("notification_type"):
                data["notification_type"] = data.get("type")
        elif hasattr(data, "type"):
            if not getattr(data, "notification_type", None):
                try:
                    setattr(data, "notification_type", getattr(data, "type"))
                except AttributeError:
                    pass
        return data

