"""
Natal astrology orchestration layer.
"""
import logging
import uuid
from typing import Any
import psycopg
from psycopg.types.json import Jsonb

from backend.app.astrology.calculator import (
    compute_natal_placements,
    derive_primary_element_and_modality,
    longitude_to_sign,
)
from backend.app.astrology.models import (
    BirthDataInput,
    NatalChartPlacements,
    SafeDerivedAstrology,
    SafeDerivedAstrologyResponse,
)
from backend.app.astrology.validation import validate_birth_data
from backend.app.core.errors import JesterAPIException

logger = logging.getLogger(__name__)


def compute_and_derive_natal_profile(
    birth_data: BirthDataInput,
    data_version: int = 1,
) -> tuple[NatalChartPlacements, dict[str, Any]]:
    """
    Authoritative calculation and safe derivation path.
    1. Validates input parameters in memory (raises JesterAPIException on failure).
    2. Runs Swiss Ephemeris calculations in memory (raises on polar Placidus failure).
    3. Derives public-safe signs, primary element, and primary modality in memory.
    Executes entirely in Python memory with ZERO database interactions.
    """
    validate_birth_data(
        birth_date=birth_data.birth_date,
        birth_time=birth_data.birth_time,
        birth_time_precision=birth_data.birth_time_precision,
        birth_timezone=birth_data.birth_timezone,
        latitude=float(birth_data.latitude) if birth_data.latitude is not None else None,
        longitude=float(birth_data.longitude) if birth_data.longitude is not None else None,
    )

    placements: NatalChartPlacements = compute_natal_placements(
        birth_data=birth_data,
        data_version=data_version,
    )

    sun_sign = longitude_to_sign(placements.sun_longitude)
    moon_sign = longitude_to_sign(placements.moon_longitude)
    ascendant_sign = longitude_to_sign(placements.ascendant_longitude)
    mercury_sign = longitude_to_sign(placements.mercury_longitude)
    venus_sign = longitude_to_sign(placements.venus_longitude)
    mars_sign = longitude_to_sign(placements.mars_longitude)

    element_primary, modality_primary = derive_primary_element_and_modality(
        sun_sign=sun_sign,  # type: ignore
        moon_sign=moon_sign,  # type: ignore
        ascendant_sign=ascendant_sign,
        mercury_sign=mercury_sign,  # type: ignore
        venus_sign=venus_sign,  # type: ignore
        mars_sign=mars_sign,  # type: ignore
    )

    derived = {
        "sun_sign": sun_sign,
        "moon_sign": moon_sign,
        "ascendant_sign": ascendant_sign,
        "mercury_sign": mercury_sign,
        "venus_sign": venus_sign,
        "mars_sign": mars_sign,
        "element_primary": element_primary,
        "modality_primary": modality_primary,
    }
    return placements, derived


def _persist_astro_profile_records(
    cur: psycopg.Cursor,
    user_id: uuid.UUID,
    placements: NatalChartPlacements,
    derived: dict[str, Any],
    data_version: int,
) -> dict[str, Any]:
    """
    Internal helper to persist private placements to astro_private and
    safe profile to astro_safe_profile using the provided active cursor.
    Must be called within an active transaction.
    """
    # Persist private placements to astro_private (SERVER-SIDE ONLY)
    cur.execute(
        """
        INSERT INTO public.astro_private (
            user_id, sun_longitude, moon_longitude, mercury_longitude, venus_longitude,
            mars_longitude, jupiter_longitude, saturn_longitude, uranus_longitude,
            neptune_longitude, pluto_longitude, ascendant_longitude, houses, retrogrades,
            source_birth_data_version, engine_version, calculated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
        ) ON CONFLICT (user_id) DO UPDATE SET
            sun_longitude = EXCLUDED.sun_longitude,
            moon_longitude = EXCLUDED.moon_longitude,
            mercury_longitude = EXCLUDED.mercury_longitude,
            venus_longitude = EXCLUDED.venus_longitude,
            mars_longitude = EXCLUDED.mars_longitude,
            jupiter_longitude = EXCLUDED.jupiter_longitude,
            saturn_longitude = EXCLUDED.saturn_longitude,
            uranus_longitude = EXCLUDED.uranus_longitude,
            neptune_longitude = EXCLUDED.neptune_longitude,
            pluto_longitude = EXCLUDED.pluto_longitude,
            ascendant_longitude = EXCLUDED.ascendant_longitude,
            houses = EXCLUDED.houses,
            retrogrades = EXCLUDED.retrogrades,
            source_birth_data_version = EXCLUDED.source_birth_data_version,
            engine_version = EXCLUDED.engine_version,
            calculated_at = now();
        """,
        (
            user_id,
            placements.sun_longitude,
            placements.moon_longitude,
            placements.mercury_longitude,
            placements.venus_longitude,
            placements.mars_longitude,
            placements.jupiter_longitude,
            placements.saturn_longitude,
            placements.uranus_longitude,
            placements.neptune_longitude,
            placements.pluto_longitude,
            placements.ascendant_longitude,
            Jsonb(placements.houses) if placements.houses is not None else None,
            Jsonb(placements.retrogrades),
            data_version,
            placements.engine_version,
        ),
    )

    # Persist safe profile to astro_safe_profile
    cur.execute(
        """
        INSERT INTO public.astro_safe_profile (
            user_id, sun_sign, moon_sign, ascendant_sign, element_primary,
            modality_primary, source_birth_data_version, engine_version, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, now()
        ) ON CONFLICT (user_id) DO UPDATE SET
            sun_sign = EXCLUDED.sun_sign,
            moon_sign = EXCLUDED.moon_sign,
            ascendant_sign = EXCLUDED.ascendant_sign,
            element_primary = EXCLUDED.element_primary,
            modality_primary = EXCLUDED.modality_primary,
            source_birth_data_version = EXCLUDED.source_birth_data_version,
            engine_version = EXCLUDED.engine_version,
            updated_at = now()
        RETURNING *;
        """,
        (
            user_id,
            derived["sun_sign"],
            derived["moon_sign"],
            derived["ascendant_sign"],
            derived["element_primary"],
            derived["modality_primary"],
            data_version,
            placements.engine_version,
        ),
    )
    return cur.fetchone()


def save_birth_data_and_calculate(
    user_id: uuid.UUID,
    birth_data: BirthDataInput,
    db: psycopg.Connection,
) -> SafeDerivedAstrologyResponse:
    """
    Atomically saves user birth data and calculates/persists natal profile:
    1. Validates inputs and computes astrology in memory (BEFORE transaction).
    2. Executes a single atomic database transaction:
       - Upserts public.birth_data (returning data_version)
       - Upserts public.astro_private
       - Upserts public.astro_safe_profile
    3. Returns SafeDerivedAstrologyResponse.
    Guarantees: If calculation fails, 0 database writes occur.
                If any database write fails, all writes roll back.
    """
    # 1. In-memory validation & calculation (BEFORE transaction)
    placements, derived = compute_and_derive_natal_profile(
        birth_data=birth_data,
        data_version=1,
    )

    # 2. Atomic Database Transaction
    try:
        with db.transaction():
            with db.cursor() as cur:
                # 2a. Persist birth_data (returning auto-incremented data_version)
                cur.execute(
                    """
                    INSERT INTO public.birth_data (
                        user_id, birth_date, birth_time, birth_time_precision,
                        birth_timezone, latitude, longitude, place_label
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (user_id) DO UPDATE SET
                        birth_date = EXCLUDED.birth_date,
                        birth_time = EXCLUDED.birth_time,
                        birth_time_precision = EXCLUDED.birth_time_precision,
                        birth_timezone = EXCLUDED.birth_timezone,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        place_label = EXCLUDED.place_label
                    RETURNING data_version;
                    """,
                    (
                        user_id,
                        birth_data.birth_date,
                        birth_data.birth_time,
                        birth_data.birth_time_precision,
                        birth_data.birth_timezone,
                        birth_data.latitude,
                        birth_data.longitude,
                        birth_data.place_label,
                    ),
                )
                bd_row = cur.fetchone()
                actual_version = bd_row["data_version"]

                # 2b & 2c. Persist astro_private and astro_safe_profile
                safe_row = _persist_astro_profile_records(
                    cur=cur,
                    user_id=user_id,
                    placements=placements,
                    derived=derived,
                    data_version=actual_version,
                )
    except psycopg.Error as e:
        logger.error("Database transaction failed saving birth data for user %s: %s", user_id, e)
        raise JesterAPIException(
            status_code=500,
            error_code="database_transaction_failed",
            message="Failed to persist birth data and calculate astrology profile.",
        ) from None

    return SafeDerivedAstrologyResponse(
        user_id=safe_row["user_id"],
        sun_sign=safe_row["sun_sign"],
        moon_sign=safe_row["moon_sign"],
        ascendant_sign=safe_row["ascendant_sign"],
        mercury_sign=derived["mercury_sign"],
        venus_sign=derived["venus_sign"],
        mars_sign=derived["mars_sign"],
        element_primary=safe_row["element_primary"],
        modality_primary=safe_row["modality_primary"],
        source_birth_data_version=safe_row["source_birth_data_version"],
        engine_version=safe_row["engine_version"],
        updated_at=safe_row["updated_at"],
    )


def recalculate_user_astrology(
    user_id: uuid.UUID,
    db: psycopg.Connection,
) -> SafeDerivedAstrology:
    """
    Recalculates derived profile from existing stored birth data:
    1. Loads authenticated user's existing birth data.
    2. Runs deterministic calculation & derivation in memory.
    3. Persists astro_private and astro_safe_profile in an atomic transaction.
    """
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT user_id, birth_date, birth_time, birth_time_precision,
                   birth_timezone, latitude, longitude, place_label, data_version
            FROM public.birth_data
            WHERE user_id = %s;
            """,
            (user_id,),
        )
        row = cur.fetchone()

    if not row:
        raise JesterAPIException(
            status_code=404,
            error_code="birth_data_not_found",
            message="Birth data not found. Please provide birth data first.",
        )

    birth_input = BirthDataInput(
        birth_date=row["birth_date"],
        birth_time=row["birth_time"],
        birth_time_precision=row["birth_time_precision"],
        birth_timezone=row["birth_timezone"],
        latitude=float(row["latitude"]) if row["latitude"] is not None else None,
        longitude=float(row["longitude"]) if row["longitude"] is not None else None,
        place_label=row["place_label"],
    )

    placements, derived = compute_and_derive_natal_profile(
        birth_data=birth_input,
        data_version=row["data_version"],
    )

    try:
        with db.transaction():
            with db.cursor() as cur:
                safe_row = _persist_astro_profile_records(
                    cur=cur,
                    user_id=user_id,
                    placements=placements,
                    derived=derived,
                    data_version=row["data_version"],
                )
    except psycopg.Error as e:
        logger.error("Database transaction failed recalculating astrology for user %s: %s", user_id, e)
        raise JesterAPIException(
            status_code=500,
            error_code="database_transaction_failed",
            message="Failed to recalculate astrology profile.",
        ) from None

    return SafeDerivedAstrology(
        user_id=safe_row["user_id"],
        sun_sign=safe_row["sun_sign"],
        moon_sign=safe_row["moon_sign"],
        ascendant_sign=safe_row["ascendant_sign"],
        mercury_sign=derived["mercury_sign"],
        venus_sign=derived["venus_sign"],
        mars_sign=derived["mars_sign"],
        element_primary=safe_row["element_primary"],
        modality_primary=safe_row["modality_primary"],
        source_birth_data_version=safe_row["source_birth_data_version"],
        engine_version=safe_row["engine_version"],
        updated_at=safe_row["updated_at"],
    )

