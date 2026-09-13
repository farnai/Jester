import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import clean_db, create_test_user, db_conn, set_auth_context


def _create_direct_conversation(cur, conversation_id, first_user, second_user, updated_at):
    cur.execute(
        """
        INSERT INTO public.conversations (id, conversation_type, created_by, created_at, updated_at)
        VALUES (%s, 'direct', %s, %s, %s);
        """,
        (conversation_id, first_user, updated_at, updated_at),
    )
    cur.execute(
        """
        INSERT INTO public.conversation_members (conversation_id, user_id)
        VALUES (%s, %s), (%s, %s);
        """,
        (conversation_id, first_user, conversation_id, second_user),
    )


def _create_accepted_connection(cur, first_user, second_user):
    user_a, user_b = sorted((first_user, second_user))
    cur.execute(
        """
        INSERT INTO public.connections (user_a_id, user_b_id, status, initiated_by)
        VALUES (%s, %s, 'accepted', %s);
        """,
        (user_a, user_b, first_user),
    )


@pytest.mark.asyncio
async def test_list_my_conversations_returns_active_inbox_with_latest_activity(db_conn):
    user_id, other_one, other_two, unrelated_one, unrelated_two = [str(uuid.uuid4()) for _ in range(5)]
    for index, user in enumerate((user_id, other_one, other_two, unrelated_one, unrelated_two)):
        create_test_user(db_conn, user, f"inbox_{index}_{uuid.uuid4().hex[:8]}@test.jester.app", f"User {index}")

    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        _create_accepted_connection(cur, user_id, other_one)
        _create_accepted_connection(cur, user_id, other_two)

        newest_conversation = uuid.uuid4()
        empty_conversation = uuid.uuid4()
        unrelated_conversation = uuid.uuid4()
        _create_direct_conversation(cur, newest_conversation, user_id, other_one, "2020-01-01T00:00:00Z")
        _create_direct_conversation(cur, empty_conversation, user_id, other_two, "2025-01-01T00:00:00Z")
        _create_direct_conversation(cur, unrelated_conversation, unrelated_one, unrelated_two, "2035-01-01T00:00:00Z")
        cur.execute(
            """
            INSERT INTO public.messages (conversation_id, sender_user_id, body, created_at)
            VALUES (%s, %s, 'Newest conversation message', '2030-01-01T00:00:00Z');
            """,
            (newest_conversation, other_one),
        )

    token = generate_test_jwt(user_id=user_id, email="inbox-owner@test.jester.app")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/v1/conversations", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    conversations = response.json()
    assert [item["id"] for item in conversations] == [str(newest_conversation), str(empty_conversation)]
    assert conversations[0]["other_member_id"] == other_one
    assert conversations[0]["last_message"]["body"] == "Newest conversation message"
    assert conversations[0]["unread_count"] == 0
    assert conversations[1]["other_member_id"] == other_two
    assert conversations[1]["last_message"] is None
    assert conversations[1]["unread_count"] == 0


@pytest.mark.asyncio
async def test_list_my_conversations_returns_empty_for_user_without_active_conversations(db_conn):
    user_id = str(uuid.uuid4())
    create_test_user(db_conn, user_id, f"empty_{uuid.uuid4().hex[:8]}@test.jester.app", "Empty Inbox")
    token = generate_test_jwt(user_id=user_id, email="empty-inbox@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/v1/conversations", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_my_conversations_requires_authentication():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/v1/conversations")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_token"


@pytest.mark.asyncio
async def test_send_and_list_messages_active_connection(db_conn, clean_db):
    u1, u2 = str(uuid.uuid4()), str(uuid.uuid4())
    u3 = str(uuid.uuid4())
    create_test_user(db_conn, u1, "u1@test.jester.app", "User 1")
    create_test_user(db_conn, u2, "u2@test.jester.app", "User 2")
    create_test_user(db_conn, u3, "u3@test.jester.app", "User 3")

    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        _create_accepted_connection(cur, u1, u2)

    token_u1 = generate_test_jwt(user_id=u1, email="u1@test.jester.app")
    token_u2 = generate_test_jwt(user_id=u2, email="u2@test.jester.app")
    token_u3 = generate_test_jwt(user_id=u3, email="u3@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create direct conversation
        create_res = await client.post(
            "/v1/conversations",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert create_res.status_code == 201
        conv_id = create_res.json()["id"]

        # U1 sends message
        send_res = await client.post(
            f"/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"body": "Hello from U1!"},
        )
        assert send_res.status_code == 201
        msg = send_res.json()
        assert msg["body"] == "Hello from U1!"
        assert msg["sender_user_id"] == u1

        # U2 retrieves messages
        list_res = await client.get(
            f"/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        assert list_res.status_code == 200
        msgs = list_res.json()
        assert len(msgs) == 1
        assert msgs[0]["body"] == "Hello from U1!"

        # Unrelated U3 cannot list messages -> 404 PrivacySafeNotFoundException
        u3_res = await client.get(
            f"/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {token_u3}"},
        )
        assert u3_res.status_code == 404


@pytest.mark.asyncio
async def test_disconnect_locks_message_sending(db_conn, clean_db):
    u1, u2 = str(uuid.uuid4()), str(uuid.uuid4())
    create_test_user(db_conn, u1, "disc_u1@test.jester.app", "Disconnect 1")
    create_test_user(db_conn, u2, "disc_u2@test.jester.app", "Disconnect 2")

    token_u1 = generate_test_jwt(user_id=u1, email="disc_u1@test.jester.app")
    token_u2 = generate_test_jwt(user_id=u2, email="disc_u2@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create connection request
        req_res = await client.post(
            "/v1/connections",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert req_res.status_code == 201
        conn_id = req_res.json()["id"]

        # Accept connection
        acc_res = await client.post(
            f"/v1/connections/{conn_id}/transition",
            headers={"Authorization": f"Bearer {token_u2}"},
            json={"action": "accept"},
        )
        assert acc_res.status_code == 200

        # Create direct conversation and send initial message
        conv_res = await client.post(
            "/v1/conversations",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        conv_id = conv_res.json()["id"]

        send_res = await client.post(
            f"/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"body": "First message before disconnect"},
        )
        assert send_res.status_code == 201

        # U1 disconnects (action="remove")
        disc_res = await client.post(
            f"/v1/connections/{conn_id}/transition",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"action": "remove"},
        )
        assert disc_res.status_code == 200
        assert disc_res.json()["status"] == "removed"

        # Sending new message after disconnect is locked -> 404 PrivacySafeNotFoundException
        post_disc_send = await client.post(
            f"/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"body": "Message attempted after disconnect"},
        )
        assert post_disc_send.status_code == 404

