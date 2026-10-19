import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DirectConversationCreate(BaseModel):
    target_user_id: uuid.UUID


class MessageCreate(BaseModel):
    body: str
    client_nonce: uuid.UUID | None = None


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
    other_display_name: str | None = None
    other_avatar_url: str | None = None


class ConversationInboxResponse(BaseModel):
    """Privacy-safe summary used by the authenticated user's messages inbox."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    other_member_id: uuid.UUID
    last_message: MessageResponse | None = None
    unread_count: int
    updated_at: datetime
    other_display_name: str | None = None
    other_avatar_url: str | None = None
    last_activity_at: datetime


class MessagePage(BaseModel):
    items: list[MessageResponse]
    next_cursor: uuid.UUID | None


class ReadUpdate(BaseModel):
    last_read_message_id: uuid.UUID
