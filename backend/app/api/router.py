from fastapi import APIRouter

from backend.app.api.health import router as health_router
from backend.app.users.router import router as users_router
from backend.app.profiles.router import router as profiles_router
from backend.app.astrology.router import router as astrology_router
from backend.app.connections.router import router as connections_router
from backend.app.comparisons.router import router as comparisons_router
from backend.app.conversations.router import router as conversations_router
from backend.app.notifications.router import router as notifications_router

api_router = APIRouter()

# Health endpoints mounted at root and under /v1
api_router.include_router(health_router)

# Domain routers mounted under /v1 prefix
api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(profiles_router)
api_v1_router.include_router(astrology_router)
api_v1_router.include_router(connections_router)
api_v1_router.include_router(comparisons_router)
api_v1_router.include_router(conversations_router)
api_v1_router.include_router(notifications_router)

api_router.include_router(api_v1_router)
