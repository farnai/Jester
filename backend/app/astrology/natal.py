"""
Natal astrology orchestration layer.
"""
import uuid
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
)
from backend.app.astrology.validation import validate_birth_data
from backend.app.core.errors import JesterAPIException, PrivacySafeNotFoundException


def recalculate_user_astrology(
    user_id: uuid.UUID,
    db: psycopg.Connection,
) -> SafeDerivedAstrology:
    """
    Orchestrates the calculation lifecycle:
    1. Loads authenticated user's birth data.
    2. Validates parameters.
    3. Runs deterministic Swiss Ephemeris calculations.
    4. Persists raw placements to astro_private (server-side only).
    5. Derives safe profile (signs, elements, modalities).
    6. Persists and returns astro_safe_profile.
    """
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM public.birth_data WHERE user_id = %s;",
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            raise JesterAPIException(
                status_code=404,
                error_code="birth_data_not_found",
                message="Birth data not found. Please provide birth data first.",
            )

        # 1. Validate inputs
        validate_birth_data(
            birth_date=row["birth_date"],
            birth_time=row["birth_time"],
            birth_time_precision=row["birth_time_precision"],
            birth_timezone=row["birth_timezone"],
            latitude=float(row["latitude"]) if row["latitude"] is not None else None,
            longitude=float(row["longitude"]) if row["longitude"] is not None else None,
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

        # 2. Compute Swiss Ephemeris natal chart
        placements: NatalChartPlacements = compute_natal_placements(
            birth_data=birth_input,
            data_version=row["data_version"],
        )

        # 3. Store private placements in astro_private (SERVER-SIDE ONLY)
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
                placements.source_birth_data_version,
                placements.engine_version,
            ),
        )

        # 4. Derive safe values
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

        # 5. Persist to astro_safe_profile
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
                sun_sign,
                moon_sign,
                ascendant_sign,
                element_primary,
                modality_primary,
                placements.source_birth_data_version,
                placements.engine_version,
            ),
        )
        safe_row = cur.fetchone()

        return SafeDerivedAstrology(
            user_id=safe_row["user_id"],
            sun_sign=safe_row["sun_sign"],
            moon_sign=safe_row["moon_sign"],
            ascendant_sign=safe_row["ascendant_sign"],
            element_primary=safe_row["element_primary"],
            modality_primary=safe_row["modality_primary"],
            source_birth_data_version=safe_row["source_birth_data_version"],
            engine_version=safe_row["engine_version"],
            updated_at=safe_row["updated_at"],
        )
