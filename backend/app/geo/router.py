import uuid
from fastapi import APIRouter, Depends, Query, status
import psycopg

from backend.app.core.database import get_db
from backend.app.core.errors import JesterAPIException
from backend.app.geo.models import CanonicalCity, CanonicalCountry, CitySearchResponse
from backend.app.geo.service import (
    get_city_by_id,
    get_popular_cities,
    list_countries,
    search_cities,
)

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get(
    "/cities/search",
    response_model=CitySearchResponse,
    status_code=status.HTTP_200_OK,
)
async def search_canonical_cities(
    q: str = Query(default="", max_length=100),
    limit: int = Query(default=10, ge=1, le=20),
    db: psycopg.Connection = Depends(get_db),
) -> CitySearchResponse:
    """
    High-performance indexed city search endpoint.
    - If q is empty: returns curated popular cities (top 10 Georgian hubs).
    - If q is 1 char: returns empty list.
    - If q is 2+ chars: executes ranked search over 152k cities.
    """
    clean_q = q.strip()
    if not clean_q:
        items = get_popular_cities(limit=limit, db=db)
    elif len(clean_q) < 2:
        items = []
    else:
        items = search_cities(query=clean_q, limit=limit, db=db)
    return CitySearchResponse(items=items)


@router.get(
    "/cities/{city_id}",
    response_model=CanonicalCity,
    status_code=status.HTTP_200_OK,
)
async def get_canonical_city(
    city_id: uuid.UUID,
    db: psycopg.Connection = Depends(get_db),
) -> CanonicalCity:
    """
    Retrieves canonical city details by UUID.
    Used by frontend to resolve a selected canonical city or verify city metadata.
    """
    city = get_city_by_id(city_id=city_id, db=db)
    if not city:
        raise JesterAPIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="city_not_found",
            message="Canonical city not found.",
        )
    return city


@router.get(
    "/countries",
    response_model=list[CanonicalCountry],
    status_code=status.HTTP_200_OK,
)
async def get_canonical_countries(
    db: psycopg.Connection = Depends(get_db),
) -> list[CanonicalCountry]:
    """
    Returns the list of all canonical countries.
    """
    return list_countries(db=db)
