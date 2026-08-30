import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

ConnectionStatus = Literal["pending", "accepted", "declined", "blocked", "removed"]


class ConnectionCreate(BaseModel):
    target_user_id: uuid.UUID


class ConnectionTransition(BaseModel):
    action: Literal["accept", "decline", "block", "unblock", "remove"]


class ConnectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_a_id: uuid.UUID
    user_b_id: uuid.UUID
    status: ConnectionStatus
    initiated_by: uuid.UUID
    blocked_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
