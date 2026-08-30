import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
import psycopg

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import ForbiddenException, PrivacySafeNotFoundException
from backend.app.comparisons.models import CompareRequest, StructuredCompatibilityResponse
from backend.app.connections.router import get_canonical_pair

router = APIRouter(tags=["compare"])


@router.post("/compare", response_model=StructuredCompatibilityResponse)
async def compare_users(
    payload: CompareRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> StructuredCompatibilityResponse:
    """
    Compares authenticated user with target user.
    Enforces that active accepted connection exists.
    Derives identity strictly from JWT.sub.
    """
    user_a, user_b = get_canonical_pair(current_user.id, payload.target_user_id)

    with db.cursor() as cur:
        # Check active connection
        cur.execute("SELECT public.has_active_connection(%s, %s) as is_active;", (user_a, user_b))
        res = cur.fetchone()
        if not res or not res["is_active"]:
            raise ForbiddenException("Active connection required to view compatibility")

        # Load current birth data versions
        cur.execute("SELECT user_id, data_version FROM public.birth_data WHERE user_id IN (%s, %s);", (user_a, user_b))
        versions = {r["user_id"]: r["data_version"] for r in cur.fetchall()}
        ver_a = versions.get(user_a, 1)
        ver_b = versions.get(user_b, 1)

        # Check existing result
        cur.execute("SELECT * FROM public.compatibility_results WHERE user_a_id = %s AND user_b_id = %s;", (user_a, user_b))
        existing = cur.fetchone()

        if existing and existing["user_a_birth_data_version"] == ver_a and existing["user_b_birth_data_version"] == ver_b:
            return StructuredCompatibilityResponse(
                id=existing["id"],
                target_user_id=payload.target_user_id,
                score=float(existing["score"]),
                signals=existing["signals"] if isinstance(existing["signals"], list) else [],
                best_topics=existing["best_topics"] if isinstance(existing["best_topics"], list) else [],
                conversation_starters=existing["conversation_starters"] if isinstance(existing["conversation_starters"], list) else [],
                engine_version=existing["engine_version"],
                calculated_at=existing["calculated_at"],
            )

        # If missing or stale -> Deterministic v1 calculation baseline
        engine_ver = "1.0.0"
        score = 82.5
        signals = [
            {"type": "independence", "strength": "high"},
            {"type": "different_perspectives", "strength": "medium"},
            {"type": "curiosity", "strength": "high"},
        ]
        best_topics = ["travel", "books", "creative_work"]
        starters = ["What is your favorite travel memory?", "Have you read anything surprising lately?"]

        # Upsert current result
        cur.execute("""
            INSERT INTO public.compatibility_results 
                (user_a_id, user_b_id, user_a_birth_data_version, user_b_birth_data_version, engine_version, score, signals, best_topics, conversation_starters, calculated_at)
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())
            ON CONFLICT (user_a_id, user_b_id) DO UPDATE SET
                user_a_birth_data_version = excluded.user_a_birth_data_version,
                user_b_birth_data_version = excluded.user_b_birth_data_version,
                engine_version = excluded.engine_version,
                score = excluded.score,
                signals = excluded.signals,
                best_topics = excluded.best_topics,
                conversation_starters = excluded.conversation_starters,
                calculated_at = now()
            RETURNING *;
        """, (user_a, user_b, ver_a, ver_b, engine_ver, score, psycopg.types.json.Jsonb(signals), psycopg.types.json.Jsonb(best_topics), psycopg.types.json.Jsonb(starters)))
        
        row = cur.fetchone()
        return StructuredCompatibilityResponse(
            id=row["id"],
            target_user_id=payload.target_user_id,
            score=float(row["score"]),
            signals=signals,
            best_topics=best_topics,
            conversation_starters=starters,
            engine_version=engine_ver,
            calculated_at=row["calculated_at"],
        )


@router.get("/people/{target_user_id}/why", response_model=StructuredCompatibilityResponse)
async def get_why_this_person(
    target_user_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> StructuredCompatibilityResponse:
    return await compare_users(payload=CompareRequest(target_user_id=target_user_id), current_user=current_user, db=db)
