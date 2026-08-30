import uuid
from fastapi import APIRouter, Depends
import psycopg

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import PrivacySafeNotFoundException
from backend.app.notifications.models import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_my_notifications(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> list[NotificationResponse]:
    with db.cursor() as cur:
        cur.execute("""
            SELECT * FROM public.notifications
            WHERE user_id = %s
            ORDER BY created_at DESC;
        """, (current_user.id,))
        rows = cur.fetchall()
        return [NotificationResponse(**r) for r in rows]


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> NotificationResponse:
    with db.cursor() as cur:
        cur.execute("""
            UPDATE public.notifications
            SET read_at = now()
            WHERE id = %s AND user_id = %s
            RETURNING *;
        """, (notification_id, current_user.id))
        row = cur.fetchone()
        if not row:
            raise PrivacySafeNotFoundException("Notification not found")
        return NotificationResponse(**row)
