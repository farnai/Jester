"""
Developer debug endpoints for forensic backend -> frontend inspection.
STRICTLY GATED TO NON-PRODUCTION ENVIRONMENTS (ENV != "production").
STRICTLY AUTHENTICATED: Caller can only inspect their own private calculations.
"""
from typing import Any
from fastapi import APIRouter, Depends, status
import psycopg

from backend.app.astrology.calculator import longitude_to_sign, derive_primary_element_and_modality
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.config import get_settings
from backend.app.core.database import get_db
from backend.app.core.errors import ForbiddenException, PrivacySafeNotFoundException

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/my-astro", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
async def get_my_debug_astrology(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: psycopg.Connection = Depends(get_db),
) -> dict[str, Any]:
    """
    Returns complete private astrological calculation and persisted birth data
    exclusively for the authenticated caller inside developer debug environments.
    Strictly forbidden in production to preserve privacy invariants.
    """
    settings = get_settings()
    if settings.ENV == "production":
        raise ForbiddenException("Debug endpoints are disabled in production environment")

    with db.cursor() as cur:
        cur.execute(
            """
            SELECT user_id, birth_date, birth_time, birth_timezone,
                   birth_time_precision, latitude, longitude, place_label,
                   data_version, created_at, updated_at
            FROM public.birth_data
            WHERE user_id = %s;
            """,
            (current_user.id,),
        )
        bd_row = cur.fetchone()

        if not bd_row:
            return {
                "user_id": str(current_user.id),
                "birth_data": None,
                "private_astrology": None,
                "derived_signs": None,
                "calculation_status": "NO_BIRTH_DATA",
            }

        cur.execute(
            """
            SELECT user_id, sun_longitude, moon_longitude, ascendant_longitude,
                   mercury_longitude, venus_longitude, mars_longitude,
                   jupiter_longitude, saturn_longitude, uranus_longitude,
                   neptune_longitude, pluto_longitude, houses, retrogrades,
                   source_birth_data_version, engine_version, calculated_at
            FROM public.astro_private
            WHERE user_id = %s;
            """,
            (current_user.id,),
        )
        astro_row = cur.fetchone()

        # Purely read-only: do NOT mutate or auto-recalculate on GET request

    sun_sign = longitude_to_sign(astro_row.get("sun_longitude")) if astro_row else None
    moon_sign = longitude_to_sign(astro_row.get("moon_longitude")) if astro_row else None
    asc_sign = longitude_to_sign(astro_row.get("ascendant_longitude")) if astro_row and astro_row.get("ascendant_longitude") is not None else None
    mercury_sign = longitude_to_sign(astro_row.get("mercury_longitude")) if astro_row else None
    venus_sign = longitude_to_sign(astro_row.get("venus_longitude")) if astro_row else None
    mars_sign = longitude_to_sign(astro_row.get("mars_longitude")) if astro_row else None

    elem, mod = None, None
    if astro_row and sun_sign and moon_sign and mercury_sign and venus_sign and mars_sign:
        elem, mod = derive_primary_element_and_modality(
            sun_sign=sun_sign,
            moon_sign=moon_sign,
            ascendant_sign=asc_sign,
            mercury_sign=mercury_sign,
            venus_sign=venus_sign,
            mars_sign=mars_sign,
        )

    is_up_to_date = (
        astro_row is not None
        and astro_row.get("source_birth_data_version") == bd_row["data_version"]
    )

    # Convert dates/times to ISO strings for JSON serialization
    birth_data_clean = {
        "user_id": str(bd_row["user_id"]),
        "birth_date": bd_row["birth_date"].isoformat() if hasattr(bd_row["birth_date"], "isoformat") else str(bd_row["birth_date"]),
        "birth_time": bd_row["birth_time"].isoformat() if hasattr(bd_row["birth_time"], "isoformat") and bd_row["birth_time"] else (str(bd_row["birth_time"]) if bd_row["birth_time"] else None),
        "birth_timezone": bd_row["birth_timezone"],
        "birth_time_precision": bd_row["birth_time_precision"],
        "latitude": float(bd_row["latitude"]) if bd_row["latitude"] is not None else None,
        "longitude": float(bd_row["longitude"]) if bd_row["longitude"] is not None else None,
        "place_label": bd_row["place_label"],
        "data_version": bd_row["data_version"],
        "created_at": bd_row["created_at"].isoformat() if bd_row.get("created_at") else None,
        "updated_at": bd_row["updated_at"].isoformat() if bd_row.get("updated_at") else None,
    }

    private_astro_clean = None
    if astro_row:
        private_astro_clean = {
            "user_id": str(astro_row["user_id"]),
            "sun_longitude": float(astro_row["sun_longitude"]),
            "moon_longitude": float(astro_row["moon_longitude"]),
            "ascendant_longitude": float(astro_row["ascendant_longitude"]) if astro_row.get("ascendant_longitude") is not None else None,
            "mercury_longitude": float(astro_row["mercury_longitude"]),
            "venus_longitude": float(astro_row["venus_longitude"]),
            "mars_longitude": float(astro_row["mars_longitude"]),
            "jupiter_longitude": float(astro_row["jupiter_longitude"]),
            "saturn_longitude": float(astro_row["saturn_longitude"]),
            "uranus_longitude": float(astro_row["uranus_longitude"]),
            "neptune_longitude": float(astro_row["neptune_longitude"]),
            "pluto_longitude": float(astro_row["pluto_longitude"]),
            "houses": astro_row.get("houses"),
            "retrogrades": astro_row.get("retrogrades") or {},
            "source_birth_data_version": astro_row["source_birth_data_version"],
            "engine_version": astro_row["engine_version"],
            "calculated_at": astro_row["calculated_at"].isoformat() if astro_row.get("calculated_at") else None,
        }

    return {
        "user_id": str(current_user.id),
        "birth_data": birth_data_clean,
        "private_astrology": private_astro_clean,
        "derived_signs": {
            "sun_sign": sun_sign,
            "moon_sign": moon_sign,
            "ascendant_sign": asc_sign,
            "mercury_sign": mercury_sign,
            "venus_sign": venus_sign,
            "mars_sign": mars_sign,
            "element_primary": elem,
            "modality_primary": mod,
        },
        "calculation_status": "UP_TO_DATE" if is_up_to_date else "STALE",
    }
