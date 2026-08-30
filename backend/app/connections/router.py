import uuid
from fastapi import APIRouter, Depends, status
import psycopg

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import ForbiddenException, JesterAPIException, PrivacySafeNotFoundException
from backend.app.connections.models import ConnectionCreate, ConnectionResponse, ConnectionTransition

router = APIRouter(prefix="/connections", tags=["connections"])


def get_canonical_pair(u1: uuid.UUID, u2: uuid.UUID) -> tuple[uuid.UUID, uuid.UUID]:
    if u1 == u2:
        raise JesterAPIException(status_code=400, message="Cannot connect with yourself", error_code="invalid_pair")
    return (u1, u2) if str(u1) < str(u2) else (u2, u1)


@router.get("", response_model=list[ConnectionResponse])
async def list_my_connections(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> list[ConnectionResponse]:
    with db.cursor() as cur:
        # Blocker sees blocked connection; blocked user does not
        cur.execute("""
            SELECT * FROM public.connections
            WHERE (status <> 'blocked' AND (user_a_id = %s OR user_b_id = %s))
               OR (status = 'blocked' AND blocked_by = %s)
            ORDER BY updated_at DESC;
        """, (current_user.id, current_user.id, current_user.id))
        rows = cur.fetchall()
        return [ConnectionResponse(**r) for r in rows]


@router.post("", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection_request(
    payload: ConnectionCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ConnectionResponse:
    user_a, user_b = get_canonical_pair(current_user.id, payload.target_user_id)

    with db.cursor() as cur:
        # Check if already blocked
        cur.execute("SELECT public.is_user_blocked(%s, %s) as is_blocked;", (user_a, user_b))
        res = cur.fetchone()
        if res and res["is_blocked"]:
            raise ForbiddenException("Cannot create connection with this user")

        # Check existing connection
        cur.execute("SELECT * FROM public.connections WHERE user_a_id = %s AND user_b_id = %s;", (user_a, user_b))
        existing = cur.fetchone()
        if existing:
            if existing["status"] in ["pending", "accepted"]:
                return ConnectionResponse(**existing)
            # Reactivate if previously removed/declined
            cur.execute("""
                UPDATE public.connections 
                SET status = 'pending', initiated_by = %s, blocked_by = NULL
                WHERE id = %s RETURNING *;
            """, (current_user.id, existing["id"]))
            return ConnectionResponse(**cur.fetchone())

        cur.execute("""
            INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by)
            VALUES (%s, %s, 'pending', %s)
            RETURNING *;
        """, (user_a, user_b, current_user.id))
        return ConnectionResponse(**cur.fetchone())


@router.post("/{connection_id}/transition", response_model=ConnectionResponse)
async def transition_connection(
    connection_id: uuid.UUID,
    payload: ConnectionTransition,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ConnectionResponse:
    with db.cursor() as cur:
        cur.execute("SELECT * FROM public.connections WHERE id = %s;", (connection_id,))
        conn = cur.fetchone()
        if not conn:
            raise PrivacySafeNotFoundException("Connection not found")

        # Must be participant
        if current_user.id not in [conn["user_a_id"], conn["user_b_id"]]:
            raise PrivacySafeNotFoundException("Connection not found")

        curr_status = conn["status"]
        action = payload.action

        if action == "accept":
            if curr_status != "pending" or conn["initiated_by"] == current_user.id:
                raise JesterAPIException(status_code=400, message="Cannot accept this connection", error_code="invalid_transition")
            new_status, blocked_by = "accepted", None

        elif action == "decline":
            if curr_status != "pending" or conn["initiated_by"] == current_user.id:
                raise JesterAPIException(status_code=400, message="Cannot decline this connection", error_code="invalid_transition")
            new_status, blocked_by = "declined", None

        elif action == "block":
            new_status, blocked_by = "blocked", current_user.id

        elif action == "unblock":
            if curr_status != "blocked" or conn["blocked_by"] != current_user.id:
                raise ForbiddenException("Only the blocker can unblock")
            # Rule #5: unblock transitions to removed, does not auto-restore accepted
            new_status, blocked_by = "removed", None

        elif action == "remove":
            new_status, blocked_by = "removed", None
        else:
            raise JesterAPIException(status_code=400, message="Unknown action", error_code="invalid_action")

        cur.execute("""
            UPDATE public.connections 
            SET status = %s, blocked_by = %s
            WHERE id = %s RETURNING *;
        """, (new_status, blocked_by, connection_id))
        return ConnectionResponse(**cur.fetchone())
