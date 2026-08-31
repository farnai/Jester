from typing import Any
from fastapi import APIRouter, Depends, status
import psycopg

from backend.app.config import Settings, get_settings
from backend.app.core.database import get_db

# Root system health router (mounted at root -> /healthz)
health_root_router = APIRouter(tags=["health"])


@health_root_router.get("/healthz", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """
    Lightweight system liveness probe for load balancers.
    """
    return {"status": "ok"}


# Versioned API health router (mounted under /v1 -> /v1/health)
health_v1_router = APIRouter(tags=["health"])


@health_v1_router.get("/health", status_code=status.HTTP_200_OK)
async def detailed_health_check(
    settings: Settings = Depends(get_settings),
    db: psycopg.Connection = Depends(get_db),
) -> dict[str, Any]:
    """
    Detailed system and database connectivity health probe.
    """
    db_status = "healthy"
    try:
        with db.cursor() as cur:
            cur.execute("SELECT 1;")
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "database": db_status,
    }
