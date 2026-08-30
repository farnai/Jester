import uuid
from typing import Any
import jwt
from jwt import PyJWKClient, PyJWKClientError, InvalidTokenError, ExpiredSignatureError

from backend.app.config import get_settings
from backend.app.core.errors import UnauthorizedException
from backend.app.auth.models import AuthenticatedUser, TokenPayload

# Global in-memory cache for PyJWKClient
_jwks_client: PyJWKClient | None = None


def get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        settings = get_settings()
        _jwks_client = PyJWKClient(settings.jwks_url, cache_jwk_set=True, lifespan=3600)
    return _jwks_client


def verify_supabase_jwt(token: str) -> AuthenticatedUser:
    """
    Verifies a Supabase-issued JWT token.
    
    Security Rules:
    - In Production: ONLY asymmetric algorithms (ES256/RS256/EdDSA) via JWKS are allowed.
      NO HS256 fallback is ever permitted in production.
    - In Development/Test: Explicit HS256 tokens signed with SUPABASE_JWT_SECRET
      are supported only when the token header explicitly declares alg=HS256.
    - An asymmetric token that fails JWKS lookup NEVER falls back to HS256.
    """
    settings = get_settings()
    if not token or not isinstance(token, str):
        raise UnauthorizedException(message="Missing authentication token", error_code="missing_token")

    # 1. Inspect unverified header for algorithm and key identifier
    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception as e:
        raise UnauthorizedException(message="Malformed JWT token header", error_code="invalid_token", details=str(e))

    alg = unverified_header.get("alg")
    if not alg:
        raise UnauthorizedException(message="JWT header missing 'alg' parameter", error_code="invalid_token")

    payload_data: dict[str, Any] | None = None

    # 2. Asymmetric Verification (RS256 / ES256 / EdDSA) via Supabase JWKS
    if alg in ["RS256", "ES256", "EdDSA"]:
        try:
            jwks_client = get_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload_data = jwt.decode(
                token,
                signing_key.key,
                algorithms=[alg],
                options={"verify_exp": True, "verify_aud": False},
            )
        except PyJWKClientError as e:
            # Under NO circumstances fall back to HS256 for asymmetric tokens
            raise UnauthorizedException(
                message=f"JWKS key resolution failed for key ID: {unverified_header.get('kid')}",
                error_code="invalid_token",
                details=str(e),
            )
        except ExpiredSignatureError:
            raise UnauthorizedException(message="Token has expired", error_code="token_expired")
        except InvalidTokenError as e:
            raise UnauthorizedException(message=f"Invalid token: {str(e)}", error_code="invalid_token")

    # 3. Symmetric Verification (HS256) — ONLY permitted in non-production environments
    elif alg == "HS256":
        if settings.is_production:
            raise UnauthorizedException(
                message="Symmetric algorithm HS256 is strictly prohibited in production",
                error_code="invalid_token",
            )

        secret = settings.SUPABASE_JWT_SECRET.get_secret_value()
        try:
            payload_data = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options={"verify_exp": True, "verify_aud": False},
            )
        except ExpiredSignatureError:
            raise UnauthorizedException(message="Token has expired", error_code="token_expired")
        except InvalidTokenError as e:
            raise UnauthorizedException(message=f"Invalid token signature: {str(e)}", error_code="invalid_token")

    else:
        raise UnauthorizedException(
            message=f"Unsupported JWT algorithm '{alg}'",
            error_code="invalid_token",
        )

    # 4. Parse payload, validate claims and subject format
    try:
        payload = TokenPayload(**payload_data)
        user_uuid = uuid.UUID(payload.sub)
    except (ValueError, TypeError, Exception) as e:
        raise UnauthorizedException(
            message="Invalid subject identifier in token (must be valid UUID)",
            error_code="invalid_token",
            details=str(e),
        )

    return AuthenticatedUser(
        id=user_uuid,
        email=payload.email or payload_data.get("email"),
        role=payload.role or payload_data.get("role", "authenticated"),
        app_metadata=payload.app_metadata or payload_data.get("app_metadata", {}),
        user_metadata=payload.user_metadata or payload_data.get("user_metadata", {}),
    )
