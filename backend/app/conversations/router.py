import uuid
from fastapi import APIRouter, Depends, status
import psycopg

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import ForbiddenException, PrivacySafeNotFoundException
from backend.app.conversations.models import (
    ConversationInboxResponse,
    ConversationResponse,
    DirectConversationCreate,
    MessageCreate,
    MessageResponse,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationInboxResponse])
async def list_my_conversations(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> list[ConversationInboxResponse]:
    """Lists active direct conversations for the caller's Messages inbox.

    The current schema has no per-member read-state representation, so
    ``unread_count`` is deliberately returned as 0 for every conversation.
    """
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT
                c.id,
                other_member.user_id AS other_member_id,
                c.updated_at,
                latest_message.id AS last_message_id,
                latest_message.conversation_id AS last_message_conversation_id,
                latest_message.sender_user_id AS last_message_sender_user_id,
                latest_message.body AS last_message_body,
                latest_message.created_at AS last_message_created_at
            FROM public.conversations c
            JOIN public.conversation_members current_member
              ON current_member.conversation_id = c.id
             AND current_member.user_id = %s
            JOIN public.conversation_members other_member
              ON other_member.conversation_id = c.id
             AND other_member.user_id <> %s
            LEFT JOIN LATERAL (
                SELECT id, conversation_id, sender_user_id, body, created_at
                FROM public.messages
                WHERE conversation_id = c.id
                ORDER BY created_at DESC, id DESC
                LIMIT 1
            ) latest_message ON TRUE
            WHERE c.conversation_type = 'direct'
              AND public.is_active_direct_conversation(c.id, %s)
            ORDER BY COALESCE(latest_message.created_at, c.updated_at) DESC, c.id DESC;
            """,
            (current_user.id, current_user.id, current_user.id),
        )
        rows = cur.fetchall()

    result: list[ConversationInboxResponse] = []
    for row in rows:
        last_message = None
        if row["last_message_id"] is not None:
            last_message = MessageResponse(
                id=row["last_message_id"],
                conversation_id=row["last_message_conversation_id"],
                sender_user_id=row["last_message_sender_user_id"],
                body=row["last_message_body"],
                created_at=row["last_message_created_at"],
            )
        result.append(
            ConversationInboxResponse(
                id=row["id"],
                other_member_id=row["other_member_id"],
                last_message=last_message,
                unread_count=0,
                updated_at=row["updated_at"],
            )
        )
    return result


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_or_get_direct_conversation(
    payload: DirectConversationCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ConversationResponse:
    with db.cursor() as cur:
        # Check active connection
        cur.execute("SELECT public.has_active_connection(%s, %s) as is_active;", (current_user.id, payload.target_user_id))
        res = cur.fetchone()
        if not res or not res["is_active"]:
            raise ForbiddenException("Active connection required to create a direct conversation")

        # Find existing direct conversation between these two
        cur.execute("""
            SELECT c.*, cm2.user_id as other_id
            FROM public.conversations c
            JOIN public.conversation_members cm1 ON cm1.conversation_id = c.id AND cm1.user_id = %s
            JOIN public.conversation_members cm2 ON cm2.conversation_id = c.id AND cm2.user_id = %s
            WHERE c.conversation_type = 'direct';
        """, (current_user.id, payload.target_user_id))
        existing = cur.fetchone()
        if existing:
            return ConversationResponse(
                id=existing["id"],
                conversation_type=existing["conversation_type"],
                created_by=existing["created_by"],
                created_at=existing["created_at"],
                updated_at=existing["updated_at"],
                other_member_id=existing["other_id"],
            )

        # Create conversation
        conv_id = uuid.uuid4()
        cur.execute("""
            INSERT INTO public.conversations (id, conversation_type, created_by)
            VALUES (%s, 'direct', %s)
            RETURNING *;
        """, (conv_id, current_user.id))
        conv_row = cur.fetchone()

        cur.execute("""
            INSERT INTO public.conversation_members (conversation_id, user_id)
            VALUES (%s, %s), (%s, %s);
        """, (conv_id, current_user.id, conv_id, payload.target_user_id))

        return ConversationResponse(
            id=conv_row["id"],
            conversation_type=conv_row["conversation_type"],
            created_by=conv_row["created_by"],
            created_at=conv_row["created_at"],
            updated_at=conv_row["updated_at"],
            other_member_id=payload.target_user_id,
        )


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conversation_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> list[MessageResponse]:
    with db.cursor() as cur:
        # Verify active direct conversation
        cur.execute("SELECT public.is_active_direct_conversation(%s, %s) as is_active;", (conversation_id, current_user.id))
        res = cur.fetchone()
        if not res or not res["is_active"]:
            raise PrivacySafeNotFoundException("Conversation not found")

        cur.execute("""
            SELECT * FROM public.messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC;
        """, (conversation_id,))
        rows = cur.fetchall()
        return [MessageResponse(**r) for r in rows]


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: uuid.UUID,
    payload: MessageCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> MessageResponse:
    with db.cursor() as cur:
        cur.execute("SELECT public.is_active_direct_conversation(%s, %s) as is_active;", (conversation_id, current_user.id))
        res = cur.fetchone()
        if not res or not res["is_active"]:
            raise PrivacySafeNotFoundException("Conversation not found")

        cur.execute("""
            INSERT INTO public.messages (conversation_id, sender_user_id, body)
            VALUES (%s, %s, %s)
            RETURNING *;
        """, (conversation_id, current_user.id, payload.body))
        return MessageResponse(**cur.fetchone())
