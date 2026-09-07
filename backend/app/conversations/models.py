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


class ConversationInboxResponse(BaseModel):
    """Privacy-safe summary used by the authenticated user's messages inbox."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    other_member_id: uuid.UUID
    last_message: MessageResponse | None = None
    # Read receipts are not represented in the current schema. This remains 0
    # until a dedicated read-state feature is introduced.
    unread_count: int = 0
    updated_at: datetime
