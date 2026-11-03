"""
Concurrent Purchase and Race Condition Integration Tests for JESTER Stars Wallet & Entitlements.
Validates:
1. Two concurrent requests for the SAME layer -> Exactly 1 charge, idempotent second return, balance -5.
2. Two concurrent requests for DIFFERENT products -> Both succeed safely, serialized via row lock, balance -10.
3. Parallel purchases with INSUFFICIENT balance (e.g. balance=5 for two 5-star items) -> Exactly 1 succeeds, exactly 1 fails with 400, balance=0, NO double-spend.
4. Complete consistency: wallet balance == sum of ledger transactions, exactly matching entitlements.
"""
import asyncio
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.wallet.service import grant_stars, get_or_create_wallet
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn, set_auth_context


@pytest.mark.asyncio
async def test_concurrent_same_layer_purchases(db_conn):
    """
    Simulates two simultaneous unlock requests for the exact same layer (layer_2)
    from the same wallet.
    Expected: Exactly one request charges 5 Stars. The other returns already_unlocked: True.
    Balance decrements by exactly 5 Stars (NOT 10).
    """
    user_id = uuid.uuid4()
    email = f"conc_same_{user_id.hex[:8]}@test.jester.app"
    create_test_user(db_conn, str(user_id), email, "Concurrent Tester Same")

    grant_stars(
        user_id=user_id,
        amount=50,
        transaction_type="test_initial",
        reference_id="grant_conc_same",
        description_ka="საწყისი ბალანსი 50",
        db=db_conn,
    )

    token = generate_test_jwt(user_id=str(user_id), email=email)
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac1, \
               AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac2:

        # Fire both unlock requests simultaneously
        req1 = ac1.post(
            "/v1/interpretations/personal-catalog/unlock",
            headers=headers,
            json={"layer_id": "layer_2"},
        )
        req2 = ac2.post(
            "/v1/interpretations/personal-catalog/unlock",
            headers=headers,
            json={"layer_id": "layer_2"},
        )

        res1, res2 = await asyncio.gather(req1, req2)

        assert res1.status_code == 200
        assert res2.status_code == 200

        data1 = res1.json()
        data2 = res2.json()

        # One must be freshly unlocked, one must be already_unlocked
        unlocked_states = [data1["already_unlocked"], data2["already_unlocked"]]
        assert False in unlocked_states, "At least one request must perform the fresh unlock"
        assert True in unlocked_states, "The concurrent request must detect the lock and return already_unlocked"

        # Check final balance via API
        wallet_res = await ac1.get("/v1/wallet/me", headers=headers)
        assert wallet_res.status_code == 200
        final_balance = wallet_res.json()["balance"]
        assert final_balance == 45, f"Expected balance to be 45 (50 - 5), got {final_balance}"

        # Verify Ledger in DB: exactly 1 spend transaction
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM public.wallet_transactions WHERE user_id = %s AND amount < 0;",
                (str(user_id),),
            )
            spend_count = cur.fetchone()["cnt"]
            assert spend_count == 1, f"Expected 1 spend transaction, got {spend_count}"

            # Verify Entitlements: exactly 1
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM public.entitlements WHERE user_id = %s AND item_key = 'layer_2';",
                (str(user_id),),
            )
            ent_count = cur.fetchone()["cnt"]
            assert ent_count == 1, f"Expected 1 entitlement, got {ent_count}"


@pytest.mark.asyncio
async def test_concurrent_different_products(db_conn):
    """
    Simulates two simultaneous unlock requests for DIFFERENT products:
    1. Weekly Energy (2026-W45, 5 Stars)
    2. Personal Layer (layer_3, 5 Stars)
    Expected: Both succeed, row-locking serializes safely, total 10 Stars deducted.
    """
    user_id = uuid.uuid4()
    email = f"conc_diff_{user_id.hex[:8]}@test.jester.app"
    create_test_user(db_conn, str(user_id), email, "Concurrent Tester Diff")

    grant_stars(
        user_id=user_id,
        amount=50,
        transaction_type="test_initial",
        reference_id="grant_conc_diff",
        description_ka="საწყისი ბალანსი 50",
        db=db_conn,
    )

    token = generate_test_jwt(user_id=str(user_id), email=email)
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac1, \
               AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac2:

        req_weekly = ac1.post(
            "/v1/interpretations/weekly-energy/unlock",
            headers=headers,
            json={"timezone": "UTC"},
        )
        req_layer = ac2.post(
            "/v1/interpretations/personal-catalog/unlock",
            headers=headers,
            json={"layer_id": "layer_3"},
        )

        res_weekly, res_layer = await asyncio.gather(req_weekly, req_layer)

        assert res_weekly.status_code == 200
        assert res_layer.status_code == 200

        assert res_weekly.json()["success"] is True
        assert res_layer.json()["success"] is True

        # Check final balance: 50 - 5 - 5 = 40
        wallet_res = await ac1.get("/v1/wallet/me", headers=headers)
        assert wallet_res.json()["balance"] == 40

        # Verify ledger has exactly 2 spend transactions (-5, -5)
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT amount FROM public.wallet_transactions WHERE user_id = %s AND amount < 0 ORDER BY created_at;",
                (str(user_id),),
            )
            spends = [r["amount"] for r in cur.fetchall()]
            assert spends == [-5, -5]

            # Both entitlements exist
            cur.execute(
                "SELECT item_type, item_key FROM public.entitlements WHERE user_id = %s ORDER BY item_type;",
                (str(user_id),),
            )
            ents = cur.fetchall()
            assert len(ents) == 2


@pytest.mark.asyncio
async def test_concurrent_insufficient_balance_parallel_race(db_conn):
    """
    CRITICAL DOUBLE-SPEND ATTACK TEST:
    User has EXACTLY 5 Stars in wallet.
    Two concurrent requests are launched at the exact same moment:
    Request A: Weekly Energy (5 Stars)
    Request B: Personal Layer 4 (5 Stars)
    Expected: Exactly ONE request must succeed. Exactly ONE request must fail with HTTP 400 (insufficient_stars).
    Final balance MUST be 0 (NEVER -5). Double-spending is mathematically impossible.
    """
    user_id = uuid.uuid4()
    email = f"conc_race_{user_id.hex[:8]}@test.jester.app"
    create_test_user(db_conn, str(user_id), email, "Concurrent Race Tester")

    # Grant EXACTLY 5 Stars
    grant_stars(
        user_id=user_id,
        amount=5,
        transaction_type="test_initial",
        reference_id="grant_conc_race_5",
        description_ka="საწყისი ბალანსი 5",
        db=db_conn,
    )

    token = generate_test_jwt(user_id=str(user_id), email=email)
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac1, \
               AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac2:

        req1 = ac1.post(
            "/v1/interpretations/weekly-energy/unlock",
            headers=headers,
            json={"timezone": "UTC"},
        )
        req2 = ac2.post(
            "/v1/interpretations/personal-catalog/unlock",
            headers=headers,
            json={"layer_id": "layer_4"},
        )

        res1, res2 = await asyncio.gather(req1, req2)

        status_codes = sorted([res1.status_code, res2.status_code])
        assert status_codes == [200, 400], f"Expected exactly one 200 and one 400, got {status_codes}"

        # The failing request must return insufficient_stars error
        failing_res = res1 if res1.status_code == 400 else res2
        err_data = failing_res.json()
        assert err_data["error"]["code"] == "insufficient_stars"
        assert "არასაკმარისი ვარსკვლავები" in err_data["error"]["message"]

        # Check final balance: MUST BE 0 (never negative)
        wallet_res = await ac1.get("/v1/wallet/me", headers=headers)
        assert wallet_res.json()["balance"] == 0, f"Expected balance=0, got {wallet_res.json()['balance']}"

        # Check Database Ledger
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT balance FROM public.wallets WHERE user_id = %s;",
                (str(user_id),),
            )
            db_bal = cur.fetchone()["balance"]
            assert db_bal == 0, "DB balance must be exactly 0"

            cur.execute(
                "SELECT COUNT(*) AS cnt FROM public.wallet_transactions WHERE user_id = %s AND amount < 0;",
                (str(user_id),),
            )
            spend_count = cur.fetchone()["cnt"]
            assert spend_count == 1, "Exactly 1 spend transaction must be committed"

            cur.execute(
                "SELECT COUNT(*) AS cnt FROM public.entitlements WHERE user_id = %s;",
                (str(user_id),),
            )
            ent_count = cur.fetchone()["cnt"]
            assert ent_count == 1, "Exactly 1 entitlement must be granted"


@pytest.mark.asyncio
async def test_ledger_balance_mathematical_consistency(db_conn):
    """
    Verifies that for any user:
    1. wallet.balance == SUM(amount) FROM wallet_transactions WHERE user_id = ...
    2. wallet.total_earned == SUM(positive amounts)
    3. wallet.total_spent == SUM(abs(negative amounts))
    4. Database constraint prevents balance < 0 even via raw SQL.
    """
    user_id = uuid.uuid4()
    email = f"math_cons_{user_id.hex[:8]}@test.jester.app"
    create_test_user(db_conn, str(user_id), email, "Math Consistency User")

    grant_stars(user_id, 100, "grant", "ჩარიცხვა 100", db_conn, reference_id="math_g1")
    grant_stars(user_id, 50, "grant", "ჩარიცხვა 50", db_conn, reference_id="math_g2")

    from backend.app.wallet.service import spend_stars_and_entitle
    spend_stars_and_entitle(user_id, "weekly_energy", "2026-W45", db_conn)
    spend_stars_and_entitle(user_id, "personal_layer", "layer_5", db_conn)

    w = get_or_create_wallet(user_id, db_conn)
    assert w["balance"] == 140
    assert w["total_earned"] == 150
    assert w["total_spent"] == 10

    # Direct database check
    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM public.wallet_transactions WHERE user_id = %s;",
            (str(user_id),),
        )
        ledger_sum = cur.fetchone()["total"]
        assert ledger_sum == w["balance"] == 140

        # Verify DB CHECK constraint chk_wallet_balance_non_negative
        import psycopg.errors
        try:
            cur.execute(
                "UPDATE public.wallets SET balance = -10 WHERE user_id = %s;",
                (str(user_id),),
            )
            pytest.fail("Database constraint chk_wallet_balance_non_negative failed to reject balance = -10")
        except psycopg.errors.CheckViolation:
            pass  # Expected
