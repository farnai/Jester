import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DirectConversationCreate(BaseModel):
    target_user_id: uuid.UUID


class MessageCreate(BaseModel):
    body: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_user_id: uuid.UUID
    body: str
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_type: str
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    other_member_id: uuid.UUID | None = None
