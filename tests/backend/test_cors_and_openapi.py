import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_openapi_schema_generated():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "/healthz" in schema["paths"]
        assert "/v1/users/me" in schema["paths"]
        assert "/v1/profiles/me" in schema["paths"]
        assert "/v1/connections" in schema["paths"]
        assert "/v1/compare" in schema["paths"]
        assert "/v1/conversations" in schema["paths"]
        assert "/v1/notifications" in schema["paths"]


@pytest.mark.asyncio
async def test_cors_preflight_headers():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.options(
            "/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
