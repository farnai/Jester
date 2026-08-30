"""
Input validation for birth data.
"""
from datetime import date, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from backend.app.core.errors import JesterAPIException


def validate_birth_data(
    birth_date: date,
    birth_time: time | None,
    birth_time_precision: str,
    birth_timezone: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> None:
    """
    Validates birth data parameters before astronomical calculations.
    Raises JesterAPIException on invalid inputs.
    """
    # 1. Validate birth date
    if birth_date > date.today():
        raise JesterAPIException(
            status_code=400,
            error_code="invalid_birth_date",
            message="Birth date cannot be in the future",
        )
    if birth_date < date(1900, 1, 1):
        raise JesterAPIException(
            status_code=400,
            error_code="invalid_birth_date",
            message="Birth date cannot precede 1900",
        )

    # 2. Validate timezone
    try:
        ZoneInfo(birth_timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise JesterAPIException(
            status_code=400,
            error_code="invalid_timezone",
            message=f"Invalid birth timezone '{birth_timezone}'. Must be a valid IANA timezone.",
        )

    # 3. Validate precision consistency
    if birth_time_precision not in ["exact", "approximate", "unknown"]:
        raise JesterAPIException(
            status_code=400,
            error_code="invalid_precision",
            message="birth_time_precision must be 'exact', 'approximate', or 'unknown'",
        )

    if birth_time_precision == "unknown" and birth_time is not None:
        raise JesterAPIException(
            status_code=400,
            error_code="inconsistent_birth_time",
            message="birth_time must be null when birth_time_precision is 'unknown'",
        )

    if birth_time_precision in ["exact", "approximate"] and birth_time is None:
        raise JesterAPIException(
            status_code=400,
            error_code="missing_birth_time",
            message="birth_time is required when precision is 'exact' or 'approximate'",
        )

    # 4. Validate coordinates if provided
    if latitude is not None and not (-90.0 <= latitude <= 90.0):
        raise JesterAPIException(
            status_code=400,
            error_code="invalid_coordinates",
            message="Latitude must be between -90.0 and 90.0",
        )

    if longitude is not None and not (-180.0 <= longitude <= 180.0):
        raise JesterAPIException(
            status_code=400,
            error_code="invalid_coordinates",
            message="Longitude must be between -180.0 and 180.0",
        )
