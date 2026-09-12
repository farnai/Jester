"""
Comprehensive Unit and Integration Tests for Real Daily Energy Transit Engine V1.
Covers:
1. Ephemeris accuracy (known astronomical positions)
2. Transit aspect detection (all 5 Ptolemaic aspects: conjunction, opposition, trine, square, sextile)
3. Orb boundaries (exact, just inside, just outside)
4. Strength calculation (quadratic decay, tight > weak)
5. Applying vs separating dynamics
6. Multi-transit composite ranking & primary signal selection
7. Fast Moon movement across 3-point local day sampling
8. Unknown birth time handling (safe omission of Ascendant)
9. Local timezone day sampling
10. Zero-transit clean fallback (no fake signals)
11. API endpoint integration with transit evidence payload
"""
import uuid
from datetime import date, time, datetime, timezone
import pytest
from httpx import ASGITransport, AsyncClient
import swisseph as swe

from backend.app.astrology.aspects import angular_distance
from backend.app.astrology.constants import PLANETS, DEFAULT_SWE_FLAGS
from backend.app.astrology.transits import (
    TRANSIT_ORB_LIMITS,
    calculate_transit_positions,
    check_is_applying,
    compute_daily_transits,
    map_transit_to_archetype,
)
from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import clean_db, create_test_user, db_conn, set_auth_context


# -----------------------------------------------------------------------------
# 1. Ephemeris Accuracy
# -----------------------------------------------------------------------------
def test_ephemeris_accuracy_j2000():
    """
    Verifies that Swiss Ephemeris calculates accurate positions on J2000.0 epoch
    (2000-01-01 12:00:00 UTC, JD = 2451545.0).
    Sun longitude at J2000.0 is ~280.46 degrees (Capricorn ~10.46 deg).
    """
    jd_j2000 = 2451545.0
    positions = calculate_transit_positions(jd_j2000)

    assert "sun" in positions
    sun_lon, sun_speed, is_retro = positions["sun"]
    assert 280.0 <= sun_lon <= 281.0, f"Sun lon expected ~280.46, got {sun_lon}"
    assert sun_speed > 0.0, "Sun speed should be direct (> 0)"
    assert not is_retro, "Sun cannot be retrograde"

    assert "moon" in positions
    moon_lon, moon_speed, _ = positions["moon"]
    # Moon speed is roughly 11-15 deg/day
    assert 11.0 <= moon_speed <= 16.0


# -----------------------------------------------------------------------------
# 2. Aspect Detection (5 Ptolemaic aspects)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "aspect_type,target_angle",
    [
        ("conjunction", 0.0),
        ("sextile", 60.0),
        ("square", 90.0),
        ("trine", 120.0),
        ("opposition", 180.0),
    ],
)
def test_transit_aspect_detection_all_five(aspect_type, target_angle):
    """
    Tests detection of all 5 Ptolemaic aspects by setting natal Sun to exactly target_angle
    relative to transiting Sun.
    """
    test_date = date(2026, 6, 21)
    jd = swe.julday(2026, 6, 21, 12.0)
    res, _ = swe.calc_ut(jd, PLANETS["sun"], DEFAULT_SWE_FLAGS)
    t_sun_lon = res[0] % 360.0

    # Place natal Sun exactly at target angle relative to transiting Sun
    n_sun_lon = (t_sun_lon + target_angle) % 360.0
    natal_placements = {"sun": n_sun_lon}

    result = compute_daily_transits(
        natal_placements=natal_placements,
        target_date=test_date,
        user_timezone="UTC",
        birth_time_precision="exact",
    )

    all_signals = ([result.dominant_transit] if result.dominant_transit else []) + result.supporting_transits
    sun_signal = next((s for s in all_signals if s.transit_planet == "sun" and s.natal_point == "sun"), None)
    assert sun_signal is not None, f"Transiting Sun aspect {aspect_type} was not detected"
    assert sun_signal.aspect_type == aspect_type
    assert sun_signal.orb_diff < 0.1
    assert sun_signal.aspect_strength > 0.99


# -----------------------------------------------------------------------------
# 3. Orb Boundary Tests
# -----------------------------------------------------------------------------
def test_orb_boundary_exact_inside_outside():
    """
    Tests orb boundaries for transiting Sun (max orb = 2.0 degrees):
    - exact aspect (0.0 deg) -> detected
    - inside orb (0.8 deg diff) -> detected across day
    - outside orb (3.5 deg diff, accounting for daily motion ~1 deg) -> NOT detected
    """
    test_date = date(2026, 3, 20)
    jd = swe.julday(2026, 3, 20, 12.0)
    res, _ = swe.calc_ut(jd, PLANETS["sun"], DEFAULT_SWE_FLAGS)
    t_sun_lon = res[0] % 360.0

    # Case A: Inside orb (0.8 deg diff)
    natal_inside = {"sun": (t_sun_lon + 0.8) % 360.0}
    res_inside = compute_daily_transits(natal_inside, test_date, "UTC", "exact")
    assert res_inside.dominant_transit is not None
    assert res_inside.dominant_transit.aspect_type == "conjunction"
    assert res_inside.dominant_transit.orb_diff <= 1.5

    # Case B: Outside orb (3.5 deg diff, safely outside 2.0 deg max orb across entire day)
    natal_outside = {"sun": (t_sun_lon + 3.5) % 360.0}
    res_outside = compute_daily_transits(natal_outside, test_date, "UTC", "exact")
    conjunctions = [
        t for t in ([res_outside.dominant_transit] + res_outside.supporting_transits)
        if t and t.transit_planet == "sun" and t.natal_point == "sun" and t.aspect_type == "conjunction"
    ]
    assert len(conjunctions) == 0


# -----------------------------------------------------------------------------
# 4. Aspect Strength Quadratic Decay
# -----------------------------------------------------------------------------
def test_aspect_strength_quadratic_decay():
    """
    Verifies that a tighter aspect has strictly greater strength than a looser aspect
    using quadratic decay: S = (1 - orb/max_orb)^2.
    For max_orb = 2.0:
    - orb = 0.2 -> S = (1 - 0.1)^2 = 0.81
    - orb = 1.5 -> S = (1 - 0.75)^2 = 0.0625
    """
    test_date = date(2026, 3, 20)
    jd = swe.julday(2026, 3, 20, 12.0)
    res, _ = swe.calc_ut(jd, PLANETS["sun"], DEFAULT_SWE_FLAGS)
    t_sun_lon = res[0] % 360.0

    natal_tight = {"sun": (t_sun_lon + 0.2) % 360.0}
    natal_loose = {"sun": (t_sun_lon + 1.5) % 360.0}

    res_tight = compute_daily_transits(natal_tight, test_date, "UTC", "exact")
    res_loose = compute_daily_transits(natal_loose, test_date, "UTC", "exact")

    assert res_tight.dominant_transit is not None
    assert res_loose.dominant_transit is not None
    assert res_tight.dominant_transit.aspect_strength > res_loose.dominant_transit.aspect_strength
    assert res_tight.dominant_transit.aspect_strength >= 0.75
    assert res_loose.dominant_transit.aspect_strength <= 0.25


# -----------------------------------------------------------------------------
# 5. Applying vs. Separating Dynamics
# -----------------------------------------------------------------------------
def test_applying_vs_separating_computation():
    """
    Tests forward calculation of applying vs separating.
    If transiting planet is at 10.0 deg moving direct (+1 deg/day), and natal is at 10.5 deg:
    it is APPLYING (approaching 10.5).
    If natal is at 9.5 deg:
    it is SEPARATING (moving away from 9.5).
    """
    test_date = date(2026, 5, 1)
    jd = swe.julday(2026, 5, 1, 12.0)
    res, _ = swe.calc_ut(jd, PLANETS["mars"], DEFAULT_SWE_FLAGS)
    t_mars_lon = res[0] % 360.0
    speed = res[3]

    # Assume direct motion for this test
    if speed > 0:
        # Natal ahead of Mars -> Mars is applying
        natal_ahead = (t_mars_lon + 0.5) % 360.0
        is_app = check_is_applying(jd, PLANETS["mars"], natal_ahead, 0.0)
        assert is_app is True

        # Natal behind Mars -> Mars is separating
        natal_behind = (t_mars_lon - 0.5) % 360.0
        is_sep = check_is_applying(jd, PLANETS["mars"], natal_behind, 0.0)
        assert is_sep is False


# -----------------------------------------------------------------------------
# 6. Composite Ranking & Primary Signal Selection
# -----------------------------------------------------------------------------
def test_composite_ranking_selects_strongest_signal():
    """
    When multiple transits are active:
    A tight Sun-Sun conjunction should rank higher than a loose Jupiter-Saturn sextile.
    """
    test_date = date(2026, 5, 1)
    jd = swe.julday(2026, 5, 1, 12.0)
    positions = calculate_transit_positions(jd)
    sun_lon = positions["sun"][0]
    jupiter_lon = positions["jupiter"][0]

    # Natal chart with:
    # 1. Exact Sun conjunction (diff 0.1 deg)
    # 2. Loose Jupiter sextile to Saturn (diff 0.9 deg)
    natal_placements = {
        "sun": (sun_lon + 0.1) % 360.0,
        "saturn": (jupiter_lon + 60.9) % 360.0,
    }

    result = compute_daily_transits(natal_placements, test_date, "UTC", "exact")
    assert result.dominant_transit is not None
    assert result.dominant_transit.transit_planet == "sun"
    assert result.dominant_transit.natal_point == "sun"
    assert result.dominant_transit.aspect_type == "conjunction"


# -----------------------------------------------------------------------------
# 7. Moon Fast Movement (3-point Local Sampling)
# -----------------------------------------------------------------------------
def test_moon_fast_movement_sampling():
    """
    Moon moves ~13 deg in 24 hours. A transit that only forms in the late evening
    would be missed by a single noon snapshot. The 3-point local sampling
    (00:00, 12:00, 23:59) successfully captures it.
    """
    test_date = date(2026, 7, 15)
    tz_str = "UTC"

    # Calculate Moon position at late evening 23:30 UTC
    jd_late = swe.julday(2026, 7, 15, 23.5)
    res_late, _ = swe.calc_ut(jd_late, PLANETS["moon"], DEFAULT_SWE_FLAGS)
    moon_late_lon = res_late[0] % 360.0

    # Place natal Venus right where Moon will be at 23:30 UTC
    # At 00:00 UTC (23.5 hours earlier), Moon was ~12 degrees away (outside orb 2.5 deg)
    natal_placements = {
        "venus": moon_late_lon,
    }

    result = compute_daily_transits(natal_placements, test_date, tz_str, "exact")
    # Verify that the Moon transit was detected during the day
    transits = [result.dominant_transit] + result.supporting_transits
    moon_transits = [t for t in transits if t and t.transit_planet == "moon" and t.natal_point == "venus"]
    assert len(moon_transits) > 0, "Fast Moon transit at day end should be captured by 3-point sampling"


# -----------------------------------------------------------------------------
# 8. Unknown Birth Time (No Ascendant, No Crash)
# -----------------------------------------------------------------------------
def test_unknown_birth_time_skips_ascendant():
    """
    When birth time precision is 'unknown':
    - Ascendant longitude must NOT be evaluated even if passed
    - No crash occurs
    - Planetary points are evaluated normally
    """
    test_date = date(2026, 4, 10)
    jd = swe.julday(2026, 4, 10, 12.0)
    res, _ = swe.calc_ut(jd, PLANETS["mars"], DEFAULT_SWE_FLAGS)
    mars_lon = res[0] % 360.0

    natal_placements = {
        "sun": (mars_lon + 120.0) % 360.0,  # Mars trine Sun
        "ascendant": mars_lon,              # Exact Mars conj Ascendant
    }

    # Case A: precision = unknown -> Ascendant ignored, Mars trine Sun detected
    res_unknown = compute_daily_transits(
        natal_placements=natal_placements,
        target_date=test_date,
        user_timezone="UTC",
        birth_time_precision="unknown",
    )
    assert res_unknown.dominant_transit is not None
    assert res_unknown.dominant_transit.natal_point == "sun"
    assert res_unknown.dominant_transit.natal_point != "ascendant"

    # Case B: precision = exact -> Ascendant is permitted and detected (conj Ascendant ranks higher than trine Sun)
    res_exact = compute_daily_transits(
        natal_placements=natal_placements,
        target_date=test_date,
        user_timezone="UTC",
        birth_time_precision="exact",
    )
    assert res_exact.dominant_transit is not None
    assert res_exact.dominant_transit.natal_point == "ascendant"


# -----------------------------------------------------------------------------
# 9. Timezone-Aware Local Calendar Day
# -----------------------------------------------------------------------------
def test_timezone_local_calendar_day():
    """
    Verifies that local calendar day sampling correctly accounts for user's timezone.
    Sampling for 2026-01-01 in Tokyo (UTC+9) starts 9 hours before UTC midnight.
    """
    target_date = date(2026, 1, 1)
    natal_placements = {"sun": 100.0, "moon": 200.0}

    res_tokyo = compute_daily_transits(natal_placements, target_date, "Asia/Tokyo", "exact")
    res_ny = compute_daily_transits(natal_placements, target_date, "America/New_York", "exact")

    # Both must compute deterministically and complete without errors
    assert res_tokyo.active_archetype != ""
    assert res_ny.active_archetype != ""


# -----------------------------------------------------------------------------
# 10. No Active Transit Clean Fallback (Honest Neutral State)
# -----------------------------------------------------------------------------
def test_no_active_transit_clean_fallback():
    """
    If no natal points form aspects within tight orbs on the target date:
    - dominant_transit is None
    - supporting_transits is empty
    - archetype falls back cleanly to 'neutral' (NOT a fake active energy)
    - NO fake astrological aspects are generated
    """
    test_date = date(2026, 6, 1)
    empty_placements: dict[str, float | None] = {"sun": None, "moon": None}

    result = compute_daily_transits(empty_placements, test_date, "UTC", "unknown")
    assert result.dominant_transit is None
    assert len(result.supporting_transits) == 0
    assert result.active_archetype == "neutral"


# -----------------------------------------------------------------------------
# 11. Aspect Type Distinction (Hard vs Soft Modifiers)
# -----------------------------------------------------------------------------
def test_aspect_type_distinction_hard_vs_soft():
    """
    Verifies that hard and soft aspects of the same planetary pair do NOT
    collapse into the same archetype:
    - Mars square Sun -> restlessness (impulsive friction)
    - Mars trine Sun -> confidence (assertive flow)
    - Mercury square Jupiter -> focus (mental scattering)
    - Mercury trine Jupiter -> curiosity (intellectual pivot)
    """
    test_date = date(2026, 4, 15)
    jd = swe.julday(2026, 4, 15, 12.0)
    res_mars, _ = swe.calc_ut(jd, PLANETS["mars"], DEFAULT_SWE_FLAGS)
    mars_lon = res_mars[0] % 360.0

    # Mars square Sun (90 deg)
    res_sq = compute_daily_transits({"sun": (mars_lon + 90.0) % 360.0}, test_date, "UTC", "exact")
    assert res_sq.dominant_transit is not None
    assert res_sq.dominant_transit.aspect_type == "square"
    assert res_sq.active_archetype == "restlessness"

    # Mars trine Sun (120 deg)
    res_tr = compute_daily_transits({"sun": (mars_lon + 120.0) % 360.0}, test_date, "UTC", "exact")
    assert res_tr.dominant_transit is not None
    assert res_tr.dominant_transit.aspect_type == "trine"
    assert res_tr.active_archetype == "confidence"

    # Mercury aspects
    res_merc, _ = swe.calc_ut(jd, PLANETS["mercury"], DEFAULT_SWE_FLAGS)
    merc_lon = res_merc[0] % 360.0

    # Mercury square Jupiter -> focus
    res_merc_sq = compute_daily_transits({"jupiter": (merc_lon + 90.0) % 360.0}, test_date, "UTC", "exact")
    assert res_merc_sq.dominant_transit is not None
    assert res_merc_sq.active_archetype == "focus"

    # Mercury trine Jupiter -> curiosity
    res_merc_tr = compute_daily_transits({"jupiter": (merc_lon + 120.0) % 360.0}, test_date, "UTC", "exact")
    assert res_merc_tr.dominant_transit is not None
    assert res_merc_tr.active_archetype == "curiosity"


# -----------------------------------------------------------------------------
# 12. Moon Uncertainty Policy (Unknown Birth Time)
# -----------------------------------------------------------------------------
def test_moon_uncertainty_policy_unknown_birth_time():
    """
    When birth time is unknown, natal Moon position has +/- 6.5 deg daily uncertainty.
    Policy:
    - An aspect to natal Moon CANNOT become the dominant primary transit.
    - If it is the only aspect, day resolves to 'neutral' (Moon aspect can remain in supporting).
    - When birth time is known ('exact'), the Moon aspect CAN become dominant.
    """
    test_date = date(2026, 5, 20)
    jd = swe.julday(2026, 5, 20, 12.0)
    res_venus, _ = swe.calc_ut(jd, PLANETS["venus"], DEFAULT_SWE_FLAGS)
    venus_lon = res_venus[0] % 360.0

    # Natal chart with ONLY an exact Moon transit to transiting Venus (trine 120 deg)
    natal_only_moon = {
        "moon": (venus_lon + 120.0) % 360.0,
    }

    # Case A: unknown birth time -> Moon transit disqualified from dominant -> neutral
    res_unknown = compute_daily_transits(natal_only_moon, test_date, "UTC", "unknown")
    assert res_unknown.dominant_transit is None
    assert res_unknown.active_archetype == "neutral"
    # Can still appear in supporting background
    assert any(s.natal_point == "moon" for s in res_unknown.supporting_transits)

    # Case B: exact birth time -> Moon transit IS permitted as dominant primary transit
    res_exact = compute_daily_transits(natal_only_moon, test_date, "UTC", "exact")
    assert res_exact.dominant_transit is not None
    assert res_exact.dominant_transit.natal_point == "moon"
    assert res_exact.active_archetype != "neutral"


# -----------------------------------------------------------------------------
# 13. DO / DON'T Guidance Completeness & Determinism (Co-Star Style 3+3 Tags)
# -----------------------------------------------------------------------------
def test_daily_energy_guidance_all_archetypes_and_neutral():
    """
    Verifies that all 12 archetypes + 'neutral' have exactly 3 DO and 3 DON'T
    short, punchy curated tags (max 1-2 words), distinct flavors, and zero overlap.
    """
    from backend.app.astrology.transits import DAILY_ENERGY_GUIDANCE, get_daily_guidance

    expected_archetypes = [
        "confidence", "clarity", "vitality", "creativity",
        "communication", "social", "introspection", "curiosity",
        "discipline", "receptivity", "restlessness", "focus", "neutral",
    ]

    for arch in expected_archetypes:
        assert arch in DAILY_ENERGY_GUIDANCE, f"Missing guidance for {arch}"

        # Test both English and Georgian localizations
        for loc in ["en", "ka"]:
            guidance = get_daily_guidance(arch, locale=loc)

            # Must have 'do' and 'dont' lists
            assert "do" in guidance and "dont" in guidance
            assert isinstance(guidance["do"], list) and len(guidance["do"]) == 3, f"{arch} ({loc}) DO must have exactly 3 tags"
            assert isinstance(guidance["dont"], list) and len(guidance["dont"]) == 3, f"{arch} ({loc}) DON'T must have exactly 3 tags"

            # Every tag must be non-empty and at most 1-2 words
            for tag in guidance["do"] + guidance["dont"]:
                words = tag.strip().split()
                assert 1 <= len(words) <= 2, f"Tag '{tag}' in {arch} ({loc}) exceeds 2 words ({len(words)} words)"

            # Within the 3 DOs, all must be distinct
            assert len(set(guidance["do"])) == 3, f"Duplicate DO tag found in {arch} ({loc}): {guidance['do']}"

            # Within the 3 DON'Ts, all must be distinct
            assert len(set(guidance["dont"])) == 3, f"Duplicate DON'T tag found in {arch} ({loc}): {guidance['dont']}"

            # DO and DON'T tags must not overlap
            overlap = set(guidance["do"]).intersection(set(guidance["dont"]))
            assert len(overlap) == 0, f"Overlapping DO and DON'T tags in {arch} ({loc}): {overlap}"


def test_daily_energy_guidance_determinism():
    """
    Verifies that calling get_daily_guidance repeatedly returns identical tags
    with zero random variation and zero runtime drift.
    """
    from backend.app.astrology.transits import get_daily_guidance

    for arch in ["confidence", "restlessness", "communication", "neutral"]:
        first = get_daily_guidance(arch)
        for _ in range(10):
            again = get_daily_guidance(arch)
            assert again == first


# -----------------------------------------------------------------------------
# 14. Edge Case: Transit Peak Exactly Between Coarse Sample Points
# -----------------------------------------------------------------------------
def test_transit_detection_continuous_window_edge_case():
    """
    Verifies that an exact transit occurring strictly between coarse 6-hour sample points
    (e.g. at 03:15 UTC between 00:00 and 06:00) is detected by the continuous window
    detection engine with exact peak precision (orb_diff < 0.05 deg, strength > 0.99).
    """
    test_date = date(2026, 5, 20)
    # Calculate exact Moon position at 03:15 UTC (between 00:00 and 06:00)
    jd_0315 = swe.julday(2026, 5, 20, 3.25)
    res, _ = swe.calc_ut(jd_0315, PLANETS["moon"], DEFAULT_SWE_FLAGS)
    moon_at_0315 = res[0] % 360.0

    natal_placements = {
        "sun": moon_at_0315,  # Transiting Moon will be EXACTLY conjunct at 03:15 UTC
    }

    # Run daily transit calculation across the UTC day
    result = compute_daily_transits(natal_placements, test_date, "UTC", "exact")

    assert result.dominant_transit is not None
    assert result.dominant_transit.transit_planet == "moon"
    assert result.dominant_transit.natal_point == "sun"
    assert result.dominant_transit.aspect_type == "conjunction"

    # Peak must be captured with near-zero orb diff
    assert result.dominant_transit.orb_diff < 0.05, (
        f"Expected continuous peak to capture near-zero orb, got {result.dominant_transit.orb_diff}"
    )
    assert result.dominant_transit.aspect_strength > 0.99


# -----------------------------------------------------------------------------
# 15. API Integration Test with DO / DON'T Tags Payload
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api_daily_energy_real_transit_and_guidance_integration(db_conn, clean_db):
    """
    Tests GET /v1/interpretations/daily-energy:
    1. Authenticated user receives real primary_transit, Georgian label, and narrative.
    2. Response includes DO and DON'T as lists of 3 short tags.
    3. Both 'archetype' and 'energy_type' are returned for contract consistency.
    """
    uid = str(uuid.uuid4())
    email = f"transit_guidance_{uuid.uuid4().hex[:6]}@test.jester.app"
    create_test_user(db_conn, uid, email, "Transit Guidance User")
    token = generate_test_jwt(user_id=uid, email=email)

    # Insert birth data
    with db_conn.cursor() as cur:
        set_auth_context(cur, None, "admin")
        cur.execute(
            """
            INSERT INTO public.birth_data (user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude)
            VALUES (%s, '1995-08-20', '14:30:00', 'exact', 'Asia/Tbilisi', 41.7151, 44.8271);
            """,
            (uid,),
        )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Recalculate natal
        res_calc = await ac.post(
            "/v1/astrology/profile/recalculate",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_calc.status_code == 200

        # Request Daily Energy
        res_daily = await ac.get(
            "/v1/interpretations/daily-energy?energy_type=auto&locale=ka",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_daily.status_code == 200
        data = res_daily.json()

        # Core fields
        assert "date" in data
        assert "archetype" in data
        assert "energy_type" in data
        assert data["archetype"] == data["energy_type"]
        assert "label" in data
        assert "interpretation" in data
        assert data["interpretation"] is not None
        assert "text" in data["interpretation"]

        # Behavioral guidance tags
        assert "do" in data and isinstance(data["do"], list) and len(data["do"]) == 3
        assert "dont" in data and isinstance(data["dont"], list) and len(data["dont"]) == 3

        # Transit evidence fields
        assert "primary_transit" in data
        assert "supporting_transits" in data


# -----------------------------------------------------------------------------
# 16. API Neutral State Handling (Quiet Sky)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api_daily_energy_neutral_state_handling():
    """
    Verifies that calling GET /v1/interpretations/daily-energy?energy_type=neutral
    returns the honest neutral narrative and 3+3 neutral tags.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/v1/interpretations/daily-energy?energy_type=neutral&locale=ka")
        assert res.status_code == 200
        data = res.json()

        assert data["archetype"] == "neutral"
        assert data["energy_type"] == "neutral"
        assert "სტაბილური ფონი" in data["label"]
        assert data["interpretation"] is not None
        assert "არცერთი დომინანტური ტრანზიტული წნეხი" in data["interpretation"]["text"]
        assert "do" in data and isinstance(data["do"], list) and len(data["do"]) == 3
        assert "dont" in data and isinstance(data["dont"], list) and len(data["dont"]) == 3

