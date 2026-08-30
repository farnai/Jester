from typing import Annotated
from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.errors import ForbiddenException, UnauthorizedException
from backend.app.auth.jwt import verify_supabase_jwt
from backend.app.auth.models import AuthenticatedUser

http_bearer = HTTPBearer(auto_error=False)


def get_token_from_header(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    if credentials is not None and credentials.scheme.lower() == "bearer":
        return credentials.credentials
    if authorization is not None and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1].strip()
    raise UnauthorizedException(
        message="Missing Bearer authentication token",
        error_code="missing_token",
    )


def get_current_user(
    token: Annotated[str, Depends(get_token_from_header)],
) -> AuthenticatedUser:
    """
    Validates the Bearer token and returns the AuthenticatedUser context.
    The caller's authenticated identity is strictly derived from JWT.sub.
    """
    return verify_supabase_jwt(token)


def get_optional_user(
    request: Request,
) -> AuthenticatedUser | None:
    """
    Extracts user if a valid Bearer token is provided, otherwise returns None.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    try:
        return verify_supabase_jwt(token)
    except UnauthorizedException:
        return None


def require_role(allowed_roles: list[str]):
    def role_checker(
        current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                message=f"Role '{current_user.role}' is not authorized to access this resource"
            )
        return current_user

    return role_checker
