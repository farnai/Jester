import time
import uuid
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient

from backend.app.config import Settings, get_settings
from backend.app.core.errors import UnauthorizedException
from backend.app.auth.jwt import verify_supabase_jwt
from backend.app.main import app


def generate_test_jwt(
    user_id: str | None = None,
    email: str = "test@jester.app",
    role: str = "authenticated",
    exp_delta: int = 3600,
    secret: str | None = None,
    alg: str = "HS256",
    kid: str | None = None,
) -> str:
    settings = get_settings()
    signing_secret = secret or settings.SUPABASE_JWT_SECRET.get_secret_value()
    uid = user_id or str(uuid.uuid4())
    now = int(time.time())

    payload = {
        "sub": uid,
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + exp_delta,
        "iss": f"{settings.SUPABASE_URL}/auth/v1",
        "aud": "authenticated",
    }
    headers = {"alg": alg}
    if kid:
        headers["kid"] = kid

    return jwt.encode(payload, signing_secret, algorithm=alg, headers=headers)


# ==============================================================================
# JWT VERIFICATION TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_valid_jwt_authenticates_user():
    user_id = str(uuid.uuid4())
    token = generate_test_jwt(user_id=user_id, email="user@test.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "user@test.app"
        assert data["role"] == "authenticated"


@pytest.mark.asyncio
async def test_missing_auth_header_returns_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/users/me")
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.json()["error"]["code"] == "missing_token"


@pytest.mark.asyncio
async def test_expired_jwt_returns_401():
    token = generate_test_jwt(exp_delta=-3600)  # Expired 1 hour ago

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert "token_expired" in response.headers.get("WWW-Authenticate", "")
        assert response.json()["error"]["code"] == "token_expired"


@pytest.mark.asyncio
async def test_invalid_signature_jwt_returns_401():
    token = generate_test_jwt(secret="wrong-secret-key-that-does-not-match")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "invalid_token"


@pytest.mark.asyncio
async def test_invalid_sub_format_returns_401():
    # 'not-a-valid-uuid' in sub
    token = generate_test_jwt(user_id="not-a-valid-uuid")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "invalid_token"


# ==============================================================================
# PHASE 2 AUDIT SECURITY TESTS
# ==============================================================================

def test_production_rejects_hs256(monkeypatch):
    """Security property 1: Production configuration strictly rejects HS256 tokens."""
    monkeypatch.setenv("ENV", "production")
    get_settings.cache_clear()

    token = generate_test_jwt(alg="HS256")

    with pytest.raises(UnauthorizedException) as exc_info:
        verify_supabase_jwt(token)
    assert exc_info.value.error_code == "invalid_token"
    assert "strictly prohibited in production" in exc_info.value.message

    # Reset cache after test
    monkeypatch.undo()
    get_settings.cache_clear()


def test_asymmetric_token_with_invalid_jwks_never_falls_back_to_hs256():
    """Security property 2: Asymmetric token (RS256/ES256) failure never falls back to HS256."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    payload = {"sub": str(uuid.uuid4()), "exp": int(time.time()) + 3600}
    token = jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "non-existent-jwks-key"})

    with pytest.raises(UnauthorizedException) as exc_info:
        verify_supabase_jwt(token)
    assert exc_info.value.error_code == "invalid_token"


@pytest.mark.asyncio
async def test_client_supplied_user_id_cannot_override_jwt_sub():
    """Security property 3: Client cannot spoof identity using a query or body user_id."""
    caller_id = str(uuid.uuid4())
    victim_id = str(uuid.uuid4())
    token = generate_test_jwt(user_id=caller_id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            params={"user_id": victim_id},
        )
        assert response.status_code == 200
        # Identity MUST be caller_id derived from JWT.sub, NOT victim_id
        assert response.json()["id"] == caller_id
        assert response.json()["id"] != victim_id


@pytest.mark.asyncio
async def test_service_role_key_never_exposed_in_api():
    """Security property 4: Service role key is never leaked in any health or API response."""
    settings = get_settings()
    secret_key = settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for path in ["/healthz", "/v1/health", "/openapi.json"]:
            res = await ac.get(path)
            assert secret_key not in res.text
