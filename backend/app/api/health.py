from typing import Any
from fastapi import APIRouter, Depends, status
import psycopg

from backend.app.config import Settings, get_settings
from backend.app.core.database import get_db

router = APIRouter(tags=["health"])


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/v1/health", status_code=status.HTTP_200_OK)
async def detailed_health_check(
    settings: Settings = Depends(get_settings),
    db: psycopg.Connection = Depends(get_db),
) -> dict[str, Any]:
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
