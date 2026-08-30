from typing import Any
from fastapi import Request, status
from fastapi.responses import JSONResponse


class JesterAPIException(Exception):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "bad_request",
        message: str = "An error occurred",
        details: Any = None,
        headers: dict[str, str] | None = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details
        self.headers = headers
        super().__init__(message)


class UnauthorizedException(JesterAPIException):
    def __init__(
        self,
        message: str = "Could not validate credentials",
        error_code: str = "unauthorized",
        details: Any = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            message=message,
            details=details,
            headers={"WWW-Authenticate": f'Bearer error="{error_code}"'},
        )


class ForbiddenException(JesterAPIException):
    def __init__(
        self,
        message: str = "Access forbidden",
        error_code: str = "forbidden",
        details: Any = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            message=message,
            details=details,
        )


class PrivacySafeNotFoundException(JesterAPIException):
    """
    Returns 404 for resources that do not exist or which the caller is not
    authorized to know exist (avoiding existence oracles for blocked/unrelated users).
    """

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "not_found",
        details: Any = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code,
            message=message,
            details=details,
        )


async def jester_exception_handler(request: Request, exc: JesterAPIException) -> JSONResponse:
    content = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
        }
    }
    if exc.details is not None:
        content["error"]["details"] = exc.details
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers,
    )
