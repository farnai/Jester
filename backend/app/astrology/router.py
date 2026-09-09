import uuid
from fastapi import APIRouter, Depends, status
import psycopg

from backend.app.astrology.models import SafeDerivedAstrologyResponse
from backend.app.astrology.natal import recalculate_user_astrology
from backend.app.astrology.calculator import longitude_to_sign
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.core.database import get_db
from backend.app.core.errors import PrivacySafeNotFoundException

from backend.app.astrology.debug import router as debug_router

router = APIRouter(prefix="/astrology", tags=["astrology"])
router.include_router(debug_router)


@router.post(
    "/profile/recalculate",
    response_model=SafeDerivedAstrologyResponse,
    status_code=status.HTTP_200_OK,
)
async def recalculate_own_astrology(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> SafeDerivedAstrologyResponse:
    """
    Recalculates natal chart and safe astrology profile for the authenticated caller.
    Fetches stored birth data, recalculates Swiss Ephemeris longitudes, persists to
    astro_private and astro_safe_profile, and returns safe DTO.
    """
    return recalculate_user_astrology(user_id=current_user.id, db=db)


@router.get(
    "/profile/safe-astro",
    response_model=SafeDerivedAstrologyResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_safe_astrology(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> SafeDerivedAstrologyResponse:
    """
    Returns the authenticated user's safe derived astrology profile.
    """
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT s.*, p.mercury_longitude, p.venus_longitude, p.mars_longitude
            FROM public.astro_safe_profile s
            LEFT JOIN public.astro_private p ON p.user_id = s.user_id
            WHERE s.user_id = %s;
            """,
            (current_user.id,),
        )
        row = cur.fetchone()
        if not row:
            # Auto-calculate if birth_data exists
            result = recalculate_user_astrology(user_id=current_user.id, db=db)
            return SafeDerivedAstrologyResponse(
                user_id=result.user_id,
                sun_sign=result.sun_sign,
                moon_sign=result.moon_sign,
                ascendant_sign=result.ascendant_sign,
                mercury_sign=result.mercury_sign,
                venus_sign=result.venus_sign,
                mars_sign=result.mars_sign,
                element_primary=result.element_primary,
                modality_primary=result.modality_primary,
                source_birth_data_version=result.source_birth_data_version,
                engine_version=result.engine_version,
                updated_at=result.updated_at,
            )
        return SafeDerivedAstrologyResponse(
            user_id=row["user_id"],
            sun_sign=row["sun_sign"],
            moon_sign=row["moon_sign"],
            ascendant_sign=row["ascendant_sign"],
            mercury_sign=longitude_to_sign(row.get("mercury_longitude")),
            venus_sign=longitude_to_sign(row.get("venus_longitude")),
            mars_sign=longitude_to_sign(row.get("mars_longitude")),
            element_primary=row["element_primary"],
            modality_primary=row["modality_primary"],
            source_birth_data_version=row["source_birth_data_version"],
            engine_version=row["engine_version"],
            updated_at=row["updated_at"],
        )


@router.get(
    "/people/{target_user_id}/safe-astro",
    response_model=SafeDerivedAstrologyResponse,
    status_code=status.HTTP_200_OK,
)
async def get_person_safe_astrology(
    target_user_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> SafeDerivedAstrologyResponse:
    """
    Returns another user's safe derived astrology profile.
    Enforces privacy: blocked or non-discoverable users return 404.
    """
    with db.cursor() as cur:
        # Check mutual block
        cur.execute(
            "SELECT public.is_user_blocked(%s, %s) as is_blocked;",
            (current_user.id, target_user_id),
        )
        res = cur.fetchone()
        if res and res["is_blocked"]:
            raise PrivacySafeNotFoundException("Astrology profile not found")

        # Check target discoverability
        cur.execute(
            "SELECT is_discoverable FROM public.profiles WHERE id = %s;",
            (target_user_id,),
        )
        p_row = cur.fetchone()
        if not p_row or not p_row["is_discoverable"]:
            raise PrivacySafeNotFoundException("Astrology profile not found")

        cur.execute(
            """
            SELECT s.*, p.mercury_longitude, p.venus_longitude, p.mars_longitude
            FROM public.astro_safe_profile s
            LEFT JOIN public.astro_private p ON p.user_id = s.user_id
            WHERE s.user_id = %s;
            """,
            (target_user_id,),
        )
        row = cur.fetchone()
        if not row:
            raise PrivacySafeNotFoundException("Astrology profile not found")
        return SafeDerivedAstrologyResponse(
            user_id=row["user_id"],
            sun_sign=row["sun_sign"],
            moon_sign=row["moon_sign"],
            ascendant_sign=row["ascendant_sign"],
            mercury_sign=longitude_to_sign(row.get("mercury_longitude")),
            venus_sign=longitude_to_sign(row.get("venus_longitude")),
            mars_sign=longitude_to_sign(row.get("mars_longitude")),
            element_primary=row["element_primary"],
            modality_primary=row["modality_primary"],
            source_birth_data_version=row["source_birth_data_version"],
            engine_version=row["engine_version"],
            updated_at=row["updated_at"],
        )
