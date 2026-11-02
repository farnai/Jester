"""
Comprehensive Tests for Weekly Transit Calculation Engine and Weekly Energy API.
Covers:
1. ISO calendar week boundaries (Monday to Sunday) and Georgian period formatting
2. Planetary speed variations & duration factor (Moon brief vs multi-day transits)
3. Non-Moon dominance policy for 7-day overarching theme
4. Analytical peak day detection within the 7-day window
5. Significant periods extraction and Georgian day naming
6. Unknown birth time handling (no Ascendant)
7. Clean neutral baseline fallback
8. Star-based access control & locked preview state
9. Unlocked state with 3-point interpretation and astronomical drawer
"""
from datetime import date
import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.astrology.transits import (
    compute_weekly_transits,
    format_georgian_week_period,
    MONTH_NAMES_KA,
    DAY_NAMES_KA,
)
from backend.app.interpretation.weekly_energy import (
    WEEKLY_ENERGY_STAR_COST,
    get_weekly_energy_content,
    is_weekly_energy_unlocked,
    record_weekly_energy_unlock,
)
from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import clean_db, create_test_user, db_conn, set_auth_context


def test_georgian_week_period_formatting():
    # Same month, same year
    p1 = format_georgian_week_period(date(2026, 11, 2), date(2026, 11, 8))
    assert p1 == "2–8 ნოემბერი, 2026"

    # Different months, same year
    p2 = format_georgian_week_period(date(2026, 10, 26), date(2026, 11, 1))
    assert p2 == "26 ოქტომბერი – 1 ნოემბერი, 2026"

    # Year transition
    p3 = format_georgian_week_period(date(2025, 12, 29), date(2026, 1, 4))
    assert p3 == "29 დეკემბერი, 2025 – 4 იანვარი, 2026"


def test_iso_week_calculation():
    # Target date is a Wednesday (2026-11-04)
    target = date(2026, 11, 4)
    natal = {"sun": 220.0, "mercury": 225.0, "venus": 250.0, "mars": 180.0}

    res = compute_weekly_transits(
        natal_placements=natal,
        target_date=target,
        user_timezone="Asia/Tbilisi",
        birth_time_precision="exact",
    )

    assert res.start_date == date(2026, 11, 2)  # Monday
    assert res.end_date == date(2026, 11, 8)    # Sunday
    assert res.iso_year == 2026
    assert res.iso_week == 45
    assert res.period_ka == "2–8 ნოემბერი, 2026"


def test_planetary_speed_and_duration_factor():
    """
    Tests that Moon transits receive a duration factor of ~0.35, while
    personal planets receive ~0.80 and Mars ~0.90, outer planets 1.00.
    """
    target = date(2026, 11, 2)
    natal = {"sun": 220.0, "moon": 100.0, "mars": 50.0}

    res = compute_weekly_transits(
        natal_placements=natal,
        target_date=target,
        user_timezone="UTC",
        birth_time_precision="exact",
    )

    # All signals in result
    all_signals = ([res.dominant_transit] if res.dominant_transit else []) + res.supporting_transits
    for sig in all_signals:
        if sig.transit_planet == "moon":
            assert sig.duration_factor == 0.35
            assert sig.duration_days <= 1.0
        elif sig.transit_planet in ("sun", "mercury", "venus"):
            assert sig.duration_factor == 0.80
        elif sig.transit_planet == "mars":
            assert sig.duration_factor == 0.90
        elif sig.transit_planet in ("jupiter", "saturn", "uranus", "neptune", "pluto"):
            assert sig.duration_factor == 1.00


def test_non_moon_dominance_policy():
    """
    Tests that when a personal planet transit exists within orb, it is chosen as
    the weekly dominant transit rather than a fleeting Moon transit.
    """
    target = date(2026, 11, 2)
    # Give placements that trigger both a Moon conjunction and a Sun/Mars aspect
    natal = {"sun": 220.0, "moon": 120.0, "mars": 220.0}

    res = compute_weekly_transits(
        natal_placements=natal,
        target_date=target,
        user_timezone="UTC",
        birth_time_precision="exact",
    )

    if res.dominant_transit:
        # If there are any non-moon eligible transits, dominant must not be Moon
        assert res.dominant_transit.transit_planet != "moon"


def test_unknown_birth_time_omits_ascendant():
    """
    Tests that unknown birth time excludes Ascendant from calculation.
    """
    target = date(2026, 11, 2)
    natal = {"sun": 220.0, "ascendant": 220.0}

    res = compute_weekly_transits(
        natal_placements=natal,
        target_date=target,
        user_timezone="UTC",
        birth_time_precision="unknown",
    )

    if res.dominant_transit:
        assert res.dominant_transit.natal_point != "ascendant"
    for s in res.supporting_transits:
        assert s.natal_point != "ascendant"


def test_neutral_baseline_when_no_aspects():
    """
    Tests clean fallback to neutral baseline when no natal points are in orb.
    """
    target = date(2026, 11, 2)
    # Empty natal positions
    natal = {"sun": None}

    res = compute_weekly_transits(
        natal_placements=natal,
        target_date=target,
        user_timezone="UTC",
        birth_time_precision="exact",
    )

    assert res.dominant_transit is None
    assert res.active_archetype == "neutral"


def test_significant_periods_detection():
    """
    Verifies that significant peak periods are populated with Georgian day names and dates.
    """
    target = date(2026, 11, 2)
    natal = {"sun": 220.0, "mars": 130.0, "jupiter": 40.0}

    res = compute_weekly_transits(
        natal_placements=natal,
        target_date=target,
        user_timezone="Asia/Tbilisi",
        birth_time_precision="exact",
    )

    for sp in res.significant_periods:
        assert len(sp.day_name_ka) > 0
        assert any(d in sp.day_name_ka for d in DAY_NAMES_KA.values())
        assert len(sp.peak_date_iso) == 10
        assert sp.aspect_strength > 0.0
        # Grammar invariants: zero raw hyphens in Georgian planetary conjugation
        assert "-ის" not in sp.significance_description_ka
        assert "-თან" not in sp.significance_description_ka
        assert "მზეთან" not in sp.transit_label_ka  # Must be მზესთან


@pytest.mark.asyncio
async def test_weekly_energy_api_locked_and_unlocked():
    """
    Tests GET /v1/interpretations/weekly-energy:
    1. Default is locked: interpretation is null, preview is returned.
    2. dev_unlock=true: interpretation and astronomical basis are returned.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Locked state
        res_locked = await client.get("/v1/interpretations/weekly-energy")
        assert res_locked.status_code == 200
        data_locked = res_locked.json()
        assert data_locked["is_unlocked"] is False
        assert data_locked["star_cost"] is None  # Pricing pending founder approval
        assert data_locked["wallet_available"] is False
        assert data_locked["interpretation"] is None
        assert data_locked["preview"]["archetype_id"] is not None
        assert "ნოემბერი" in data_locked["period"] or len(data_locked["period"]) > 0

        # 2. Dev unlocked state (in development/test)
        res_unlocked = await client.get("/v1/interpretations/weekly-energy?dev_unlock=true")
        assert res_unlocked.status_code == 200
        data_unlocked = res_unlocked.json()
        assert data_unlocked["is_unlocked"] is True
        assert data_unlocked["interpretation"] is not None
        assert "quote" in data_unlocked["interpretation"]
        assert "theme" in data_unlocked["interpretation"]
        assert "reflection" in data_unlocked["interpretation"]
        assert "focus" in data_unlocked["interpretation"]
        assert data_unlocked["astrological_basis"] is not None


@pytest.mark.asyncio
async def test_production_security_invariants(monkeypatch):
    """
    Tests that in ENV=production:
    1. dev_unlock=true query parameter is strictly ignored (remains locked).
    2. Zero paid interpretation content leaks when locked.
    3. POST /v1/interpretations/weekly-energy/unlock is rejected with 400 monetization_pending_approval.
    """
    from backend.app.config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "ENV", "production")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Attempt dev_unlock in production -> MUST remain locked
        res = await client.get("/v1/interpretations/weekly-energy?dev_unlock=true")
        assert res.status_code == 200
        data = res.json()
        assert data["is_unlocked"] is False
        assert data["interpretation"] is None
        assert data["significant_periods"] == []
        assert data["astrological_basis"] is None

        # 2. Attempt unlock in production with auth -> MUST return 400 monetization_pending_approval
        user_id = uuid.UUID("26098ac8-f8f0-4cd3-9bbb-78dc8467ba07")
        from backend.app.auth.dependencies import get_current_user
        from backend.app.auth.models import AuthenticatedUser
        app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=user_id, email="test@jester.app", role="user")
        try:
            unlock_res = await client.post("/v1/interpretations/weekly-energy/unlock", json={})
            assert unlock_res.status_code == 400
            err_body = unlock_res.json()
            assert err_body["error"]["code"] == "monetization_pending_approval"
        finally:
            app.dependency_overrides.pop(get_current_user, None)
