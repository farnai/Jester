import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn


@pytest.mark.asyncio
async def test_profile_and_connections_api_flow(db_conn):
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    create_test_user(db_conn, u1, "u1@test.jester.app", "User One")
    create_test_user(db_conn, u2, "u2@test.jester.app", "User Two")

    token_u1 = generate_test_jwt(user_id=u1, email="u1@test.jester.app")
    token_u2 = generate_test_jwt(user_id=u2, email="u2@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Get profile me
        res = await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token_u1}"})
        assert res.status_code == 200
        assert res.json()["display_name"] == "User One"

        # 2. Update bio
        res = await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"bio": "Astrology enthusiast"},
        )
        assert res.status_code == 200
        assert res.json()["bio"] == "Astrology enthusiast"

        # 3. Send connection request from U1 to U2
        res = await ac.post(
            "/v1/connections",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res.status_code == 201
        conn_id = res.json()["id"]
        assert res.json()["status"] == "pending"

        # 4. U2 accepts connection
        res = await ac.post(
            f"/v1/connections/{conn_id}/transition",
            headers={"Authorization": f"Bearer {token_u2}"},
            json={"action": "accept"},
        )
        assert res.status_code == 200
        assert res.json()["status"] == "accepted"

        # 5. Compare U1 and U2
        res = await ac.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res.status_code == 200
        assert res.json()["score"] > 0
        assert len(res.json()["signals"]) > 0

        # 6. Direct chat between U1 and U2
        res = await ac.post(
            "/v1/conversations",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res.status_code == 200 or res.status_code == 201
        conv_id = res.json()["id"]

        # Send message
        res = await ac.post(
            f"/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"body": "Hello from FastAPI!"},
        )
        assert res.status_code == 201
        assert res.json()["body"] == "Hello from FastAPI!"
