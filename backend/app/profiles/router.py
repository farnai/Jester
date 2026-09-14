import uuid
from fastapi import APIRouter, Depends, HTTPException, status
import psycopg

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import JesterAPIException, PrivacySafeNotFoundException, UnauthorizedException
from backend.app.geo.service import get_city_by_id
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
            # Check if user exists in auth.users before attempting insert
            cur.execute("SELECT id FROM auth.users WHERE id = %s;", (current_user.id,))
            if not cur.fetchone():
                raise UnauthorizedException(
                    message="Authenticated user does not exist in database.",
                    error_code="user_not_found",
                )

            # Auto-create default profile for authenticated user if not present
            display_name = current_user.email.split("@")[0] if current_user.email else "User"
            try:
                cur.execute(
                    """
                    INSERT INTO public.profiles (id, display_name)
                    VALUES (%s, %s)
                    ON CONFLICT (id) DO NOTHING
                    RETURNING *;
                    """,
                    (current_user.id, display_name),
                )
                row = cur.fetchone()
                if not row:
                    cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (current_user.id,))
                    row = cur.fetchone()
            except psycopg.errors.ForeignKeyViolation:
                raise UnauthorizedException(
                    message="Authenticated user does not exist in database.",
                    error_code="user_not_found",
                )
        if not row:
            raise PrivacySafeNotFoundException("Profile not found")
        return ProfileResponse(**row)


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    update_data: ProfileUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ProfileResponse:
    # Ensure profile row exists
    await get_my_profile(current_user=current_user, db=db)

    # Validate and sync canonical city if city_id provided
    if update_data.city_id is not None:
        canonical_city = get_city_by_id(update_data.city_id, db)
        if not canonical_city:
            raise JesterAPIException(
                status_code=400,
                error_code="invalid_city_id",
                message="The specified city_id does not exist.",
            )
        # Keep profiles.city synchronized with canonical display name
        update_data.city = canonical_city.display_name

    fields = update_data.model_dump(exclude_unset=True)
    if not fields:
        return await get_my_profile(current_user=current_user, db=db)

    set_clause = ", ".join(f"{k} = %s" for k in fields.keys())
    values = list(fields.values()) + [current_user.id]

    try:
        with db.cursor() as cur:
            query = f"UPDATE public.profiles SET {set_clause} WHERE id = %s RETURNING *;"
            cur.execute(query, values)
            row = cur.fetchone()
            if not row:
                raise PrivacySafeNotFoundException("Profile not found")
            return ProfileResponse(**row)
    except psycopg.errors.ForeignKeyViolation:
        raise UnauthorizedException(
            message="Authenticated user does not exist in database.",
            error_code="user_not_found",
        )


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
