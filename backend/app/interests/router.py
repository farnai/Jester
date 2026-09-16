import uuid
from fastapi import APIRouter, Depends
import psycopg
from psycopg.rows import dict_row

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import JesterAPIException
from backend.app.interests.models import (
    InterestItem,
    InterestsListResponse,
    UserInterestsResponse,
    UserInterestsUpdateRequest,
)

router = APIRouter(prefix="/interests", tags=["interests"])


@router.get("", response_model=InterestsListResponse)
async def list_candidate_interests(
    db: psycopg.Connection = Depends(get_db),
) -> InterestsListResponse:
    """
    Returns the authoritative seeded candidate pool of active interests joined with category metadata.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT
                i.id,
                i.category_id,
                i.name,
                i.slug,
                c.name as category_name,
                c.slug as category_slug,
                c.icon as category_icon,
                i.sort_order
            FROM public.interests i
            JOIN public.interest_categories c ON c.id = i.category_id
            WHERE i.status = 'active' AND c.status = 'active'
            ORDER BY c.sort_order ASC, i.sort_order ASC;
            """
        )
        rows = cur.fetchall()
        items = [InterestItem.model_validate(r) for r in rows]
        return InterestsListResponse(items=items)


@router.get("/me", response_model=UserInterestsResponse)
async def get_my_interests(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> UserInterestsResponse:
    """
    Returns the list of interest UUIDs selected by the current authenticated user.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT interest_id FROM public.user_interests WHERE user_id = %s;",
            (current_user.id,),
        )
        rows = cur.fetchall()
        return UserInterestsResponse(interest_ids=[r["interest_id"] for r in rows])


@router.put("/me", response_model=UserInterestsResponse)
async def set_my_interests(
    payload: UserInterestsUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> UserInterestsResponse:
    """
    Sets the current user's selected interests.
    Enforces rules:
    - Minimum 3 interests if selecting any.
    - Zero interests (Skip) is valid.
    - 1 or 2 selected interests rejected.
    - All interest IDs must exist in public.interests.
    - Transactional replacement preventing duplicates.
    """
    raw_ids = payload.interest_ids
    # Deduplicate while preserving order
    unique_ids: list[uuid.UUID] = list(dict.fromkeys(raw_ids))

    if len(unique_ids) in (1, 2):
        raise JesterAPIException(
            status_code=400,
            error_code="min_three_interests_required",
            message="მინიმუმ 3 ინტერესის არჩევაა საჭირო, ან გამოტოვეთ ეს ეტაპი (Must select at least 3 interests or skip).",
        )

    with db.cursor(row_factory=dict_row) as cur:
        if unique_ids:
            cur.execute(
                """
                SELECT id FROM public.interests
                WHERE id = ANY(%s) AND status = 'active';
                """,
                (unique_ids,),
            )
            found_ids = {r["id"] for r in cur.fetchall()}
            invalid = [str(i) for i in unique_ids if i not in found_ids]
            if invalid:
                raise JesterAPIException(
                    status_code=400,
                    error_code="invalid_interest_id",
                    message=f"One or more specified interest IDs do not exist: {', '.join(invalid)}",
                )

        # Transactionally replace user's interests
        cur.execute("DELETE FROM public.user_interests WHERE user_id = %s;", (current_user.id,))
        if unique_ids:
            records = [(current_user.id, iid) for iid in unique_ids]
            cur.executemany(
                """
                INSERT INTO public.user_interests (user_id, interest_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, interest_id) DO NOTHING;
                """,
                records,
            )

    return UserInterestsResponse(interest_ids=unique_ids)
