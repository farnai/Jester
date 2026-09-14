import uuid
from fastapi import APIRouter, Depends, HTTPException, status
import psycopg

from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import JesterAPIException, PrivacySafeNotFoundException, UnauthorizedException
from backend.app.geo.service import get_city_by_id
from backend.app.profiles.models import ProfileResponse, ProfileUpdate, ProfileInitializeRequest

router = APIRouter(prefix="/profiles", tags=["profiles"])


def validate_onboarding_completion(profile_id: uuid.UUID, candidate_fields: dict, db: psycopg.Connection) -> list[str]:
    """
    Authoritative server-side validation of onboarding completion requirements.
    Required:
      - first_name: non-empty string
      - last_name: non-empty string
      - current_city_id: non-null UUID referencing public.cities
      - birth_data: row in public.birth_data with non-null birth_date and non-null birth_city_id
    Optional:
      - birth_time: (NULL is valid, NO noon fallback)
      - interests
      - avatar_url
    Returns list of missing field names. Empty list means valid.
    """
    missing = []
    fn = candidate_fields.get("first_name")
    if not fn or not str(fn).strip():
        missing.append("first_name")

    ln = candidate_fields.get("last_name")
    if not ln or not str(ln).strip():
        missing.append("last_name")

    cid = candidate_fields.get("current_city_id")
    if not cid:
        missing.append("current_city_id")
    else:
        canonical_city = get_city_by_id(cid, db)
        if not canonical_city:
            missing.append("current_city_id (invalid)")

    with db.cursor() as cur:
        cur.execute(
            "SELECT birth_date, birth_city_id FROM public.birth_data WHERE user_id = %s;",
            (profile_id,),
        )
        bd = cur.fetchone()
        if not bd:
            missing.extend(["birth_date", "birth_city_id"])
        else:
            if not bd.get("birth_date"):
                missing.append("birth_date")
            if not bd.get("birth_city_id"):
                missing.append("birth_city_id")

    return missing


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ProfileResponse:
    """
    Read-only retrieval of the authenticated user's profile.
    Returns 404 if profile has not been initialized.
    """
    with db.cursor() as cur:
        cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (current_user.id,))
        row = cur.fetchone()
        if not row:
            raise PrivacySafeNotFoundException("Profile not found")
        return ProfileResponse.model_validate(row)


@router.post("/initialize", response_model=ProfileResponse)
async def initialize_profile(
    payload: ProfileInitializeRequest | None = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ProfileResponse:
    """
    Explicit profile initialization endpoint for newly registered users or OAuth callback.
    - If profile exists: returns existing profile (never overwrites user edits; backfills empty fields if available).
    - If profile does not exist: creates profile using payload or OAuth metadata from auth.users.
    """
    with db.cursor() as cur:
        cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (current_user.id,))
        existing = cur.fetchone()

        cur.execute("SELECT email, raw_user_meta_data FROM auth.users WHERE id = %s;", (current_user.id,))
        auth_row = cur.fetchone()
        if not auth_row:
            raise UnauthorizedException(
                message="Authenticated user does not exist in database.",
                error_code="user_not_found",
            )

        user_meta = auth_row.get("raw_user_meta_data") or {}

        first_name = (payload and payload.first_name) or user_meta.get("first_name") or user_meta.get("given_name")
        last_name = (payload and payload.last_name) or user_meta.get("last_name") or user_meta.get("family_name")
        avatar_url = (payload and payload.avatar_url) or user_meta.get("avatar_url") or user_meta.get("picture")

        if existing:
            updates = {}
            if not existing.get("first_name") and first_name:
                updates["first_name"] = str(first_name).strip()
            if not existing.get("last_name") and last_name:
                updates["last_name"] = str(last_name).strip()
            if not existing.get("avatar_url") and avatar_url:
                updates["avatar_url"] = avatar_url

            if updates:
                fn = updates.get("first_name") or existing.get("first_name")
                ln = updates.get("last_name") or existing.get("last_name")
                default_prefix = current_user.email.split("@")[0] if current_user.email else "User"
                is_default_dn = (not existing.get("display_name")) or (existing.get("display_name") in (default_prefix, "User"))
                if is_default_dn and fn and ln:
                    updates["display_name"] = f"{str(fn).strip()} {str(ln).strip()[0].upper()}."

                set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
                vals = list(updates.values()) + [current_user.id]
                cur.execute(f"UPDATE public.profiles SET {set_clause} WHERE id = %s RETURNING *;", vals)
                row = cur.fetchone()
                return ProfileResponse.model_validate(row)
            return ProfileResponse.model_validate(existing)

        fn = str(first_name).strip() if first_name else None
        ln = str(last_name).strip() if last_name else None
        if fn and ln:
            display_name = f"{fn} {ln[0].upper()}."
        elif fn:
            display_name = fn
        else:
            display_name = current_user.email.split("@")[0] if current_user.email else "User"

        cur.execute(
            """
            INSERT INTO public.profiles (
                id, first_name, last_name, display_name, avatar_url, onboarding_step, onboarding_completed
            )
            VALUES (%s, %s, %s, %s, %s, 1, false)
            RETURNING *;
            """,
            (current_user.id, fn, ln, display_name, avatar_url),
        )
        row = cur.fetchone()
        return ProfileResponse.model_validate(row)


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    update_data: ProfileUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ProfileResponse:
    # Ensure profile row exists
    with db.cursor() as cur:
        cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (current_user.id,))
        current_row = cur.fetchone()
        if not current_row:
            raise PrivacySafeNotFoundException("Profile not found")
        current_profile = ProfileResponse.model_validate(current_row)

    # Validate and sync canonical city if current_city_id or city_id provided
    target_city_id = update_data.current_city_id or update_data.city_id
    if target_city_id is not None:
        canonical_city = get_city_by_id(target_city_id, db)
        if not canonical_city:
            raise JesterAPIException(
                status_code=400,
                error_code="invalid_city_id",
                message="The specified city_id does not exist.",
            )
        update_data.current_city_id = target_city_id
        update_data.city_id = target_city_id
        update_data.city = canonical_city.display_name

    # Derive display_name from first_name and last_name (First L.) if not explicitly provided
    if update_data.display_name is None and (update_data.first_name is not None or update_data.last_name is not None):
        fn = (update_data.first_name if update_data.first_name is not None else current_profile.first_name or "").strip()
        ln = (update_data.last_name if update_data.last_name is not None else current_profile.last_name or "").strip()
        default_prefix = current_user.email.split("@")[0] if current_user.email else "User"
        is_default_display_name = (not current_profile.display_name) or (current_profile.display_name == default_prefix) or (current_profile.display_name == "User")
        if is_default_display_name and fn and ln:
            update_data.display_name = f"{fn} {ln[0].upper()}."

    fields = update_data.model_dump(exclude_unset=True)
    if not fields:
        return current_profile

    # Authoritative validation if setting onboarding_completed = true
    if fields.get("onboarding_completed") is True:
        merged = {**dict(current_profile), **fields}
        missing = validate_onboarding_completion(current_user.id, merged, db)
        if missing:
            raise JesterAPIException(
                status_code=400,
                error_code="incomplete_onboarding",
                message=f"Cannot complete onboarding. Missing required fields: {', '.join(missing)}",
            )

    set_clause = ", ".join(f"{k} = %s" for k in fields.keys())
    values = list(fields.values()) + [current_user.id]

    try:
        with db.cursor() as cur:
            query = f"UPDATE public.profiles SET {set_clause} WHERE id = %s RETURNING *;"
            cur.execute(query, values)
            row = cur.fetchone()
            if not row:
                raise PrivacySafeNotFoundException("Profile not found")
            return ProfileResponse.model_validate(row)
    except psycopg.errors.ForeignKeyViolation:
        raise UnauthorizedException(
            message="Authenticated user does not exist in database.",
            error_code="user_not_found",
        )


@router.post("/me/complete-onboarding", response_model=ProfileResponse)
async def complete_my_onboarding(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> ProfileResponse:
    """
    Authoritative server-side onboarding completion.
    Validates required fields: first_name, last_name, current_city_id, birth_date, birth_city_id.
    """
    with db.cursor() as cur:
        cur.execute("SELECT * FROM public.profiles WHERE id = %s;", (current_user.id,))
        row = cur.fetchone()
        if not row:
            raise PrivacySafeNotFoundException("Profile not found")

        missing = validate_onboarding_completion(current_user.id, row, db)
        if missing:
            raise JesterAPIException(
                status_code=400,
                error_code="incomplete_onboarding",
                message=f"Cannot complete onboarding. Missing required fields: {', '.join(missing)}",
            )

        cur.execute(
            """
            UPDATE public.profiles 
            SET onboarding_completed = true, onboarding_step = 5 
            WHERE id = %s 
            RETURNING *;
            """,
            (current_user.id,),
        )
        updated = cur.fetchone()
        return ProfileResponse.model_validate(updated)


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
        return ProfileResponse.model_validate(row)
