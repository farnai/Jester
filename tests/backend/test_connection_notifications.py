import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn, clean_db


@pytest.mark.asyncio
async def test_connection_request_and_accepted_notifications_flow(db_conn, clean_db):
    """
    Verifies the end-to-end connection notifications lifecycle:
    TEST 1: User A sends connection request to User B -> notification created for User B.
    TEST 2: User B accepts connection -> notification created for User A.
    TEST 3: Declined request does not create connection_accepted notification.
    TEST 4: Duplicate connection request does not create an extra notification.
    TEST 5: GET /v1/notifications returns notifications correctly with both type and notification_type.
    TEST 6: PATCH /v1/notifications/{id}/read marks notification as read.
    TEST 7: User A cannot read User B's notifications.
    """
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    user_c = str(uuid.uuid4())

    create_test_user(db_conn, user_a, "user_a@test.jester.app", "User A")
    create_test_user(db_conn, user_b, "user_b@test.jester.app", "User B")
    create_test_user(db_conn, user_c, "user_c@test.jester.app", "User C")

    token_a = generate_test_jwt(user_id=user_a, email="user_a@test.jester.app")
    token_b = generate_test_jwt(user_id=user_b, email="user_b@test.jester.app")
    token_c = generate_test_jwt(user_id=user_c, email="user_c@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # TEST 1: User A sends connection request to User B
        res = await ac.post(
            "/v1/connections",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"target_user_id": user_b},
        )
        assert res.status_code == 201
        conn_ab = res.json()
        assert conn_ab["status"] == "pending"
        conn_id = conn_ab["id"]

        # Check notifications for User B (recipient)
        res_notif_b = await ac.get("/v1/notifications", headers={"Authorization": f"Bearer {token_b}"})
        assert res_notif_b.status_code == 200
        notifs_b = res_notif_b.json()
        assert len(notifs_b) == 1

        notif_req = notifs_b[0]
        assert notif_req["user_id"] == user_b
        assert notif_req["type"] == "connection_request"
        assert notif_req["notification_type"] == "connection_request"
        assert notif_req["read_at"] is None
        assert notif_req["payload"]["connection_id"] == conn_id
        assert notif_req["payload"]["actor_id"] == user_a
        assert notif_req["payload"]["actor_name"] == "User A"
        assert "User A" in notif_req["payload"]["message"]

        # User A should have NO notifications
        res_notif_a = await ac.get("/v1/notifications", headers={"Authorization": f"Bearer {token_a}"})
        assert res_notif_a.status_code == 200
        assert len(res_notif_a.json()) == 0

        # TEST 4: Duplicate request from User A to User B must NOT create duplicate notification
        res_dup = await ac.post(
            "/v1/connections",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"target_user_id": user_b},
        )
        assert res_dup.status_code == 201
        # Still exactly 1 notification for User B
        res_notif_b2 = await ac.get("/v1/notifications", headers={"Authorization": f"Bearer {token_b}"})
        assert len(res_notif_b2.json()) == 1

        # TEST 6: User B marks the request notification as read
        req_notif_id = notif_req["id"]
        res_read = await ac.patch(
            f"/v1/notifications/{req_notif_id}/read",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert res_read.status_code == 200
        assert res_read.json()["read_at"] is not None

        # TEST 2: User B accepts connection from User A
        res_accept = await ac.post(
            f"/v1/connections/{conn_id}/transition",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"action": "accept"},
        )
        assert res_accept.status_code == 200
        assert res_accept.json()["status"] == "accepted"

        # Verify acceptance notification for User A (initiator)
        res_notif_a2 = await ac.get("/v1/notifications", headers={"Authorization": f"Bearer {token_a}"})
        assert res_notif_a2.status_code == 200
        notifs_a = res_notif_a2.json()
        assert len(notifs_a) == 1

        notif_acc = notifs_a[0]
        assert notif_acc["user_id"] == user_a
        assert notif_acc["type"] == "connection_accepted"
        assert notif_acc["notification_type"] == "connection_accepted"
        assert notif_acc["read_at"] is None
        assert notif_acc["payload"]["connection_id"] == conn_id
        assert notif_acc["payload"]["actor_id"] == user_b
        assert notif_acc["payload"]["actor_name"] == "User B"
        assert "User B" in notif_acc["payload"]["message"]

        # TEST 7: Privacy isolation - User A cannot mark or read User B's notifications
        res_read_forbidden = await ac.patch(
            f"/v1/notifications/{req_notif_id}/read",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_read_forbidden.status_code == 404

        # TEST 3: Decline scenario between User A and User C
        res_ac = await ac.post(
            "/v1/connections",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"target_user_id": user_c},
        )
        assert res_ac.status_code == 201
        conn_ac_id = res_ac.json()["id"]

        # User C declines
        res_decline = await ac.post(
            f"/v1/connections/{conn_ac_id}/transition",
            headers={"Authorization": f"Bearer {token_c}"},
            json={"action": "decline"},
        )
        assert res_decline.status_code == 200
        assert res_decline.json()["status"] == "declined"

        # Verify User A did NOT receive any new notification from the decline
        res_notif_a3 = await ac.get("/v1/notifications", headers={"Authorization": f"Bearer {token_a}"})
        # User A should still only have the 1 accepted notification from User B
        assert len(res_notif_a3.json()) == 1
        assert res_notif_a3.json()[0]["type"] == "connection_accepted"
