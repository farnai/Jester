import uuid
from fastapi import APIRouter, Depends, HTTPException, status
import psycopg

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import PrivacySafeNotFoundException
from backend.app.profiles.models import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ProfileResponse:
    with db.cursor() as cur:
        cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (current_user.id,))
        row = cur.fetchone()
        if not row:
            raise PrivacySafeNotFoundException("Profile not found")
        return ProfileResponse(**row)


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    update_data: ProfileUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ProfileResponse:
    fields = update_data.model_dump(exclude_unset=True)
    if not fields:
        return await get_my_profile(current_user=current_user, db=db)

    set_clause = ", ".join(f"{k} = %s" for k in fields.keys())
    values = list(fields.values()) + [current_user.id]

    with db.cursor() as cur:
        query = f"UPDATE public.profiles SET {set_clause} WHERE id = %s RETURNING *;"
        cur.execute(query, values)
        row = cur.fetchone()
        if not row:
            raise PrivacySafeNotFoundException("Profile not found")
        return ProfileResponse(**row)


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile_by_id(
    profile_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ProfileResponse:
    with db.cursor() as cur:
        # Check mutual block
        cur.execute("SELECT public.is_user_blocked(%s, %s) as is_blocked;", (current_user.id, profile_id))
        res = cur.fetchone()
        if res and res["is_blocked"]:
            raise PrivacySafeNotFoundException("Profile not found")

        cur.execute(
            "SELECT * FROM public.profiles WHERE id = %s AND (id = %s OR is_discoverable = true);",
            (profile_id, current_user.id),
        )
        row = cur.fetchone()
        if not row:
            raise PrivacySafeNotFoundException("Profile not found")
        return ProfileResponse(**row)
