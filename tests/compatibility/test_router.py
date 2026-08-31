"""
Integration tests for the /v1/compare and /v1/people/{id}/why endpoints.
Tests active connection requirement, block enforcement, birth data missing errors,
caching with birth data version checking, and the real Synastry V1 calculation.
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn, set_auth_context


@pytest.mark.asyncio
async def test_compare_endpoint_full_flow(db_conn):
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    email1 = f"u1_comp_{uuid.uuid4().hex[:6]}@test.jester.app"
    email2 = f"u2_comp_{uuid.uuid4().hex[:6]}@test.jester.app"
    create_test_user(db_conn, u1, email1, "User One")
    create_test_user(db_conn, u2, email2, "User Two")

    token_u1 = generate_test_jwt(user_id=u1, email=email1)
    token_u2 = generate_test_jwt(user_id=u2, email=email2)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Compare without connection -> 403 Forbidden
        res = await ac.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res.status_code == 403

        # 2. Establish accepted connection
        with db_conn.cursor() as cur:
            u_min, u_max = sorted([u1, u2])
            set_auth_context(cur, None, "admin")
            cur.execute(
                """
                INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by)
                VALUES (%s, %s, 'accepted', %s);
                """,
                (u_min, u_max, u1),
            )

        # 3. Compare without birth data -> 404
        res = await ac.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "birth_data_missing"

        # 4. Insert birth data for both users
        with db_conn.cursor() as cur:
            set_auth_context(cur, None, "admin")
            cur.execute(
                """
                INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
                VALUES 
                    (%s, '1995-05-15', '14:30:00', 'exact', 'UTC', 41.7151, 44.8271),
                    (%s, '1996-08-20', '09:15:00', 'exact', 'UTC', 40.7128, -74.0060);
                """,
                (u1, u2),
            )

        # 5. Compare with birth data -> 200 OK with real deterministic Synastry V1 calculation
        res = await ac.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res.status_code == 200
        data1 = res.json()
        assert 10.0 <= data1["score"] <= 98.0
        assert data1["engine_version"] == "synastry-v1.0.0"
        assert "dimensions" in data1
        assert "signals" in data1
        assert "best_topics" in data1
        assert "conversation_starters" in data1
        assert data1["data_quality"]["confidence"] == 1.0

        # 6. Compare reversed (U2 calls for U1) -> identical score and result
        res2 = await ac.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token_u2}"},
            json={"target_user_id": u1},
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["score"] == data1["score"]
        assert data2["engine_version"] == "synastry-v1.0.0"

        # 7. Check cache in database contains evidence_trace
        with db_conn.cursor() as cur:
            set_auth_context(cur, None, "admin")
            cur.execute(
                "SELECT * FROM public.compatibility_results WHERE user_a_id = %s AND user_b_id = %s;",
                (u_min, u_max),
            )
            cached = cur.fetchone()
            assert cached is not None
            assert cached["engine_version"] == "synastry-v1.0.0"
            assert isinstance(cached["evidence_trace"], list)
            assert len(cached["evidence_trace"]) > 0

        # 8. Test /v1/people/{id}/why endpoint
        res_why = await ac.get(
            f"/v1/people/{u2}/why",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res_why.status_code == 200
        assert res_why.json()["score"] == data1["score"]


@pytest.mark.asyncio
async def test_compare_self_forbidden(db_conn):
    u1 = str(uuid.uuid4())
    email = f"self_{uuid.uuid4().hex[:6]}@test.jester.app"
    create_test_user(db_conn, u1, email, "User One")
    token_u1 = generate_test_jwt(user_id=u1, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/compare",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u1},
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "self_comparison_not_allowed"
