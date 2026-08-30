from fastapi import APIRouter, Depends
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.users.models import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_my_user(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserResponse:
    """
    Returns the currently authenticated user's account details.
    Identity is strictly derived from verified JWT.sub.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
    )
