"""
Integration and Unit Tests for JESTER Stars Economy, Wallet Ledger, and Content Entitlements.
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.wallet.service import (
    get_or_create_wallet,
    grant_stars,
    spend_stars_and_entitle,
    has_entitlement,
    get_user_entitlements_map,
)
from backend.app.astrology.natal import recalculate_user_astrology
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import create_test_user, db_conn, set_auth_context


@pytest.mark.asyncio
async def test_wallet_initial_state_and_grant_idempotency(db_conn):
    user_id = uuid.uuid4()
    email = f"wallet_test_{user_id.hex[:8]}@test.jester.app"
    create_test_user(db_conn, str(user_id), email, "Wallet Test User")

    # 1. Initially wallet created with 0 balance
    w = get_or_create_wallet(user_id, db_conn)
    assert w["balance"] == 0
    assert w["total_earned"] == 0
    assert w["total_spent"] == 0

    # 2. Grant 1,000 stars
    res1 = grant_stars(
        user_id=user_id,
        amount=1000,
        transaction_type="initial_grant",
        reference_id="initial_grant_mvp_v1",
        description_ka="საწყისი ბალანსი (1,000 Stars)",
        db=db_conn,
    )
    assert res1["already_granted"] is False
    assert res1["balance"] == 1000

    # Verify wallet table
    w_after = get_or_create_wallet(user_id, db_conn)
    assert w_after["balance"] == 1000
    assert w_after["total_earned"] == 1000
    assert w_after["total_spent"] == 0

    # 3. Second call with identical reference_id is idempotent (no double grant)
    res2 = grant_stars(
        user_id=user_id,
        amount=1000,
        transaction_type="initial_grant",
        reference_id="initial_grant_mvp_v1",
        description_ka="საწყისი ბალანსი (1,000 Stars)",
        db=db_conn,
    )
    assert res2["already_granted"] is True
    assert res2["balance"] == 1000

    w_after2 = get_or_create_wallet(user_id, db_conn)
    assert w_after2["balance"] == 1000


@pytest.mark.asyncio
async def test_weekly_energy_unlock_via_api(db_conn):
    user_id = uuid.uuid4()
    email = f"weekly_wallet_{user_id.hex[:8]}@test.jester.app"
    create_test_user(db_conn, str(user_id), email, "Weekly Wallet Tester")

    # Grant 1000 stars
    grant_stars(
        user_id=user_id,
        amount=1000,
        transaction_type="initial_grant",
        reference_id="init_grant_week",
        description_ka="საწყისი ბალანსი",
        db=db_conn,
    )

    token = generate_test_jwt(user_id=str(user_id), email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Check initial wallet via API
        me_res = await ac.get("/v1/wallet/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["balance"] == 1000

        # Unlock current week energy
        unlock_res = await ac.post(
            "/v1/interpretations/weekly-energy/unlock",
            headers={"Authorization": f"Bearer {token}"},
            json={"timezone": "UTC"},
        )
        assert unlock_res.status_code == 200
        unlock_data = unlock_res.json()
        assert unlock_data["success"] is True
        assert unlock_data["already_unlocked"] is False
        assert unlock_data["star_cost"] == 5
        assert unlock_data["balance_after"] == 995

        # Calling unlock a second time for same week is idempotent & free
        unlock_res2 = await ac.post(
            "/v1/interpretations/weekly-energy/unlock",
            headers={"Authorization": f"Bearer {token}"},
            json={"timezone": "UTC"},
        )
        assert unlock_res2.status_code == 200
        unlock_data2 = unlock_res2.json()
        assert unlock_data2["success"] is True
        assert unlock_data2["already_unlocked"] is True
        assert unlock_data2["balance_after"] == 995

        # Check transactions list
        tx_res = await ac.get("/v1/wallet/transactions", headers={"Authorization": f"Bearer {token}"})
        assert tx_res.status_code == 200
        txs = tx_res.json()["items"]
        assert len(txs) == 2  # 1 initial grant + 1 spend
        spend_tx = txs[0]
        assert spend_tx["amount"] == -5
        assert spend_tx["balance_after"] == 995
        assert "კვირის" in spend_tx["description_ka"]


@pytest.mark.asyncio
async def test_personal_layer_unlock_and_content_masking(db_conn):
    user_id = uuid.uuid4()
    email = f"personal_mask_{user_id.hex[:8]}@test.jester.app"
    create_test_user(db_conn, str(user_id), email, "Personal Mask Tester")

    # Seed birth data so personal catalog can generate
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
            VALUES (%s, '1995-05-15', '14:30:00', 'exact', 'UTC', 41.7151, 44.8271)
            ON CONFLICT (user_id) DO NOTHING;
            """,
            (str(user_id),),
        )
    # Compute natal astrology
    recalculate_user_astrology(user_id, db_conn)

    grant_stars(
        user_id=user_id,
        amount=1000,
        transaction_type="initial_grant",
        reference_id="init_grant_mask",
        description_ka="საწყისი ბალანსი",
        db=db_conn,
    )

    token = generate_test_jwt(user_id=str(user_id), email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch personal catalog before unlocking layer 2
        cat_res = await ac.get("/v1/interpretations/personal-catalog", headers={"Authorization": f"Bearer {token}"})
        assert cat_res.status_code == 200
        layers = cat_res.json()["layers"]
        assert len(layers) == 7

        layer2 = next(l for l in layers if l["layer_id"] == "layer_2")
        assert layer2["is_locked"] is True
        # Content MUST be masked over the wire for locked layer
        assert all(item["text"] is None for item in layer2["items"])
        assert all(item["is_locked"] is True for item in layer2["items"])

        # 2. Unlock layer 2
        unlock_layer_res = await ac.post(
            "/v1/interpretations/personal-catalog/unlock",
            headers={"Authorization": f"Bearer {token}"},
            json={"layer_id": "layer_2"},
        )
        assert unlock_layer_res.status_code == 200
        unlocked_data = unlock_layer_res.json()
        assert unlocked_data["success"] is True
        assert unlocked_data["already_unlocked"] is False
        assert unlocked_data["star_cost"] == 5
        assert unlocked_data["balance_after"] == 995

        # 3. Fetch personal catalog after unlock: layer 2 is now unlocked and text is revealed
        cat_res2 = await ac.get("/v1/interpretations/personal-catalog", headers={"Authorization": f"Bearer {token}"})
        assert cat_res2.status_code == 200
        layer2_after = next(l for l in cat_res2.json()["layers"] if l["layer_id"] == "layer_2")
        assert layer2_after["is_locked"] is False
        assert any(item["text"] is not None and len(item["text"]) > 10 for item in layer2_after["items"])


@pytest.mark.asyncio
async def test_insufficient_stars_error(db_conn):
    user_id = uuid.uuid4()
    email = f"poor_user_{user_id.hex[:8]}@test.jester.app"
    create_test_user(db_conn, str(user_id), email, "Low Balance User")

    # Grant only 2 stars (cost is 5)
    grant_stars(
        user_id=user_id,
        amount=2,
        transaction_type="initial_grant",
        reference_id="init_small",
        description_ka="მცირე ბალანსი",
        db=db_conn,
    )

    token = generate_test_jwt(user_id=str(user_id), email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/v1/interpretations/weekly-energy/unlock",
            headers={"Authorization": f"Bearer {token}"},
            json={"timezone": "UTC"},
        )
        assert res.status_code == 400
        data = res.json()
        error_msg = data.get("error", {}).get("message", "") or data.get("message", "") or data.get("detail", "")
        assert "არასაკმარისი ვარსკვლავები" in error_msg

        # Balance remains untouched at 2
        w_res = await ac.get("/v1/wallet/me", headers={"Authorization": f"Bearer {token}"})
        assert w_res.json()["balance"] == 2


@pytest.mark.asyncio
async def test_pricing_config_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/v1/wallet/pricing")
        assert res.status_code == 200
        data = res.json()
        assert data["weekly_energy_stars"] == 5
        assert data["personal_layer_stars"] == 5
        assert "daily_energy" in data["free_features"]
        assert "do_and_dont" in data["free_features"]
        assert "discovery" in data["free_features"]
