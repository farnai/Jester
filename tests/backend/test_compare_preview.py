"""
Integration and security tests for POST /v1/interpretations/compare-preview.
Validates:
1. Viewer identity binding to JWT and rejection of viewer impersonation (403).
2. Privacy-safe 404 on blocked relationships in either direction.
3. Privacy-safe 404 on non-discoverable targets without an active connection.
4. Correctness and presence of dimensions, signals, interpretation, best_topics, starters, and deep_analysis.
5. Absolute omission of private birth data, coordinates, and raw celestial longitudes from the response.
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn, clean_db, set_auth_context


@pytest.mark.asyncio
async def test_compare_preview_viewer_binding_and_impersonation_rejection(db_conn, clean_db):
    """
    Authenticated callers must have their viewer identity derived from the JWT.
    Supplying an arbitrary other user ID as source_user_id must return 403 Forbidden.
    """
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    u3 = str(uuid.uuid4())
    em1 = f"u1_prev_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"u2_prev_{uuid.uuid4().hex[:6]}@test.jester.app"
    em3 = f"u3_prev_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, u1, em1, "User One")
    create_test_user(db_conn, u2, em2, "User Two")
    create_test_user(db_conn, u3, em3, "User Three")

    # Seed birth data for u1 and u2
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
            VALUES 
                (%s, '1992-04-10', '11:00:00', 'exact', 'UTC', 41.7151, 44.8271),
                (%s, '1994-09-18', '17:30:00', 'exact', 'UTC', 40.7128, -74.0060);
            """,
            (u1, u2),
        )

    token_u1 = generate_test_jwt(user_id=u1, email=em1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Calling without source_user_id -> succeeds and uses u1
        res = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["source_user_id"] == u1
        assert data["target_user_id"] == u2
        assert "dimensions" in data
        assert "emotional_harmony" in data["dimensions"]
        assert "communication" in data["dimensions"]
        assert "attraction" in data["dimensions"]
        assert "growth_long_term" in data["dimensions"]
        assert "deep_analysis" in data
        assert "blocks" in data["deep_analysis"]
        assert len(data["deep_analysis"]["blocks"]) > 0
        assert "conversation_starters" in data
        assert len(data["conversation_starters"]) > 0
        import re
        eng_pattern = re.compile(r"[a-zA-Z]")
        for st in data["conversation_starters"]:
            assert not eng_pattern.search(st), f"Leaked English in preview starter: {st}"

        # 2. Calling with matching source_user_id -> succeeds
        res_self_param = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2, "source_user_id": u1},
        )
        assert res_self_param.status_code == 200

        # 3. Impersonation attempt (u1 supplies u3 as source_user_id) -> 403 Forbidden
        res_impersonate = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2, "source_user_id": u3},
        )
        assert res_impersonate.status_code == 403
        assert res_impersonate.json()["error"]["code"] == "forbidden_viewer_impersonation"


@pytest.mark.asyncio
async def test_compare_preview_excludes_blocked_relationships(db_conn, clean_db):
    """
    If either user has blocked the other, compare-preview must return privacy-safe 404.
    """
    viewer = str(uuid.uuid4())
    target_blocker = str(uuid.uuid4())
    target_blocked = str(uuid.uuid4())

    create_test_user(db_conn, viewer, f"v_{uuid.uuid4().hex[:6]}@test.jester.app", "Viewer")
    create_test_user(db_conn, target_blocker, f"tb_{uuid.uuid4().hex[:6]}@test.jester.app", "Blocker")
    create_test_user(db_conn, target_blocked, f"tbd_{uuid.uuid4().hex[:6]}@test.jester.app", "Blocked")

    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
            VALUES 
                (%s, '1991-03-12', '08:00:00', 'exact', 'UTC', 41.7151, 44.8271),
                (%s, '1993-07-22', '12:00:00', 'exact', 'UTC', 41.7151, 44.8271),
                (%s, '1995-11-05', '16:00:00', 'exact', 'UTC', 41.7151, 44.8271);
            """,
            (viewer, target_blocker, target_blocked),
        )

        # target_blocker blocked viewer
        u_min1, u_max1 = min(viewer, target_blocker), max(viewer, target_blocker)
        cur.execute(
            """
            INSERT INTO public.connections (id, user_a_id, user_b_id, status, initiated_by, blocked_by)
            VALUES (%s, %s, %s, 'blocked', %s, %s);
            """,
            (str(uuid.uuid4()), u_min1, u_max1, target_blocker, target_blocker),
        )

        # viewer blocked target_blocked
        u_min2, u_max2 = min(viewer, target_blocked), max(viewer, target_blocked)
        cur.execute(
            """
            INSERT INTO public.connections (id, user_a_id, user_b_id, status, initiated_by, blocked_by)
            VALUES (%s, %s, %s, 'blocked', %s, %s);
            """,
            (str(uuid.uuid4()), u_min2, u_max2, viewer, viewer),
        )

    token = generate_test_jwt(user_id=viewer, email="viewer@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Target who blocked viewer -> 404
        res1 = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_user_id": target_blocker},
        )
        assert res1.status_code == 404

        # Target whom viewer blocked -> 404
        res2 = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_user_id": target_blocked},
        )
        assert res2.status_code == 404


@pytest.mark.asyncio
async def test_compare_preview_respects_discoverability_and_privacy(db_conn, clean_db):
    """
    Non-discoverable profiles without active connection must return 404.
    Response must never contain private birth data, coordinates, or evidence_trace.
    """
    viewer = str(uuid.uuid4())
    hidden_target = str(uuid.uuid4())
    normal_target = str(uuid.uuid4())

    create_test_user(db_conn, viewer, f"v_{uuid.uuid4().hex[:6]}@test.jester.app", "Viewer")
    create_test_user(db_conn, hidden_target, f"ht_{uuid.uuid4().hex[:6]}@test.jester.app", "Hidden Target")
    create_test_user(db_conn, normal_target, f"nt_{uuid.uuid4().hex[:6]}@test.jester.app", "Normal Target")

    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        # Set hidden_target to is_discoverable = false
        cur.execute("UPDATE public.profiles SET is_discoverable = false WHERE id = %s;", (hidden_target,))
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
            VALUES 
                (%s, '1990-01-15', '10:00:00', 'exact', 'UTC', 41.7151, 44.8271),
                (%s, '1992-05-20', '14:00:00', 'exact', 'UTC', 41.7151, 44.8271),
                (%s, '1994-08-30', '18:00:00', 'exact', 'UTC', 41.7151, 44.8271);
            """,
            (viewer, hidden_target, normal_target),
        )

    token = generate_test_jwt(user_id=viewer, email="viewer@test.jester.app")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Non-discoverable target without connection -> 404
        res_hidden = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_user_id": hidden_target},
        )
        assert res_hidden.status_code == 404

        # 2. Normal discoverable target -> 200 OK
        res_normal = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_user_id": normal_target},
        )
        assert res_normal.status_code == 200
        preview = res_normal.json()

        # 3. Privacy invariants: No raw longitudes, birth times, coordinates, or evidence_trace
        assert "evidence_trace" not in preview
        assert "birth_date" not in preview
        assert "birth_time" not in preview
        assert "latitude" not in preview
        assert "longitude" not in preview

        # 4. Self comparison -> 400
        res_self = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token}"},
            json={"target_user_id": viewer},
        )
        assert res_self.status_code == 400
        assert res_self.json()["error"]["code"] == "self_comparison_not_allowed"


@pytest.mark.asyncio
async def test_daily_energy_and_compare_dynamic_update_on_birth_date_change(db_conn, clean_db):
    """
    Verifies that changing birth date dynamically updates:
    1. Daily Energy archetype (e.g., Aries -> confidence, Scorpio -> introspection)
    2. Comparison preview score and interpretation texts against another user.
    """
    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())
    em1 = f"dynamic_u1_{uuid.uuid4().hex[:6]}@test.jester.app"
    em2 = f"dynamic_u2_{uuid.uuid4().hex[:6]}@test.jester.app"

    create_test_user(db_conn, u1, em1, "User Dynamic 1")
    create_test_user(db_conn, u2, em2, "User Dynamic 2")

    token_u1 = generate_test_jwt(user_id=u1, email=em1)
    token_u2 = generate_test_jwt(user_id=u2, email=em2)

    # 1. Seed birth data for User 2 (Cancer: July 10, 1992)
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
            VALUES (%s, '1992-07-10', '12:00:00', 'exact', 'UTC', 41.7151, 44.8271);
            """,
            (u2,),
        )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Calculate u2 natal astrology
        res_calc2 = await ac.post(
            "/v1/astrology/profile/recalculate",
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        assert res_calc2.status_code == 200

        # 2. User 1 initially has Aries birth date (April 10, 1990)
        with db_conn.cursor() as cur:
            set_auth_context(cur, None, "admin")
            cur.execute(
                """
                INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
                VALUES (%s, '1990-04-10', '12:00:00', 'exact', 'UTC', 41.7151, 44.8271);
                """,
                (u1,),
            )

        res_calc1 = await ac.post(
            "/v1/astrology/profile/recalculate",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res_calc1.status_code == 200

        # 3. Check Daily Energy for User 1 (Real transit active archetype + primary_transit)
        res_daily1 = await ac.get(
            "/v1/interpretations/daily-energy?energy_type=auto&locale=ka",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res_daily1.status_code == 200
        daily1 = res_daily1.json()
        assert daily1["energy_type"] != ""
        assert daily1["primary_transit"] is not None
        assert "context_label_ka" in daily1["primary_transit"]

        # 4. Check Compare Preview against User 2 (State A: Aries vs Cancer)
        res_prev1 = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2, "locale": "ka"},
        )
        assert res_prev1.status_code == 200
        prev1 = res_prev1.json()
        score1 = prev1["score"]
        interp1 = prev1["interpretation"]["text"]

        # 5. User 1 changes birth date to Scorpio (November 10, 1990)
        with db_conn.cursor() as cur:
            set_auth_context(cur, None, "admin")
            cur.execute(
                """
                UPDATE public.birth_data
                SET birth_date = '1990-11-10', updated_at = NOW()
                WHERE user_id = %s;
                """,
                (u1,),
            )

        res_calc1_update = await ac.post(
            "/v1/astrology/profile/recalculate",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res_calc1_update.status_code == 200

        # 6. Daily Energy MUST immediately change dynamically when birth date changes
        res_daily2 = await ac.get(
            "/v1/interpretations/daily-energy?energy_type=auto&locale=ka",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert res_daily2.status_code == 200
        daily2 = res_daily2.json()
        assert daily2["energy_type"] != daily1["energy_type"]
        assert daily2["interpretation"]["text"] != daily1["interpretation"]["text"]
        assert daily2["primary_transit"] is not None

        # 7. Compare Preview MUST immediately update score and interpretation
        res_prev2 = await ac.post(
            "/v1/interpretations/compare-preview",
            headers={"Authorization": f"Bearer {token_u1}"},
            json={"target_user_id": u2, "locale": "ka"},
        )
        assert res_prev2.status_code == 200
        prev2 = res_prev2.json()
        score2 = prev2["score"]
        interp2 = prev2["interpretation"]["text"]

        assert score1 != score2, f"Expected score to change, but both were {score1}"
        assert interp1 != interp2, f"Expected interpretation text to change, but both were {interp1}"


