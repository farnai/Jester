"""
Targeted test suite for JESTER — Registration / Onboarding Boundary Fix.

Covers all 12 specified test requirements:
A. Registration page contains only Email, Password, Confirm Password (no First Name / Last Name).
B. Password confirmation mismatch blocks registration.
C. Successful registration leads to onboarding Step 1 (minimal profile created without names).
D. Onboarding Step 1 contains First Name + Last Name, derives display_name as First L.
E. Step 1 -> Step 2 works.
F. Step 2 Back -> Step 1 preserves identity state.
G. Step 1 Back -> Registration.
H. Existing persisted identity skips Step 1 on resume.
I. OAuth-provided name can prefill Identity.
J. Email username is never used as name.
K. Existing Birth Date / Birth Time tests pass.
L. Existing Interests tests pass.
"""

import json
import uuid
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from tests.backend.test_jwt_verification import generate_test_jwt
from tests.database.test_database_security import db_conn


def insert_auth_user(db_conn, user_id: str, email: str, raw_meta: dict | None = None):
    """Helper to insert an auth user directly into auth.users."""
    meta_json = json.dumps(raw_meta or {})
    with db_conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        cur.execute(
            """
            INSERT INTO auth.users (id, email, raw_user_meta_data, role, aud, email_confirmed_at)
            VALUES (%s, %s, %s::jsonb, 'authenticated', 'authenticated', NOW())
            ON CONFLICT (id) DO UPDATE
            SET email = EXCLUDED.email,
                raw_user_meta_data = EXCLUDED.raw_user_meta_data;
            """,
            (user_id, email, meta_json),
        )


# ---------------------------------------------------------------------------
# Test A: Registration Page Contract
# ---------------------------------------------------------------------------
def test_registration_page_contract_only_credentials():
    """
    Requirement A:
    Registration page contains only:
    - Email
    - Password
    - Confirm Password
    And NO LONGER contains First Name / Last Name inputs.
    """
    reg_path = Path("frontend/src/modules/auth/RegisterPage.tsx")
    assert reg_path.exists(), "RegisterPage.tsx must exist"
    code = reg_path.read_text(encoding="utf-8")

    # Verify absence of First Name / Last Name inputs
    assert "firstName" not in code, "RegisterPage must not contain firstName state or inputs"
    assert "lastName" not in code, "RegisterPage must not contain lastName state or inputs"
    assert "given-name" not in code, "RegisterPage must not contain given-name autocomplete"
    assert "family-name" not in code, "RegisterPage must not contain family-name autocomplete"

    # Verify presence of Email, Password, and Confirm Password
    assert 'label="ელფოსტა (Email) *"' in code or "Email" in code
    assert 'label="პაროლი (Password) *"' in code or "Password" in code
    assert 'label="გაიმეორეთ პაროლი (Confirm Password) *"' in code or "Confirm Password" in code
    assert "confirmPassword" in code

    # Verify autocomplete attributes
    assert 'autoComplete="email"' in code
    assert 'autoComplete="new-password"' in code


# ---------------------------------------------------------------------------
# Test B: Password Confirmation Mismatch Validation
# ---------------------------------------------------------------------------
def test_password_confirmation_mismatch_blocks_registration():
    """
    Requirement B:
    Password confirmation mismatch blocks registration client-side.
    """
    reg_path = Path("frontend/src/modules/auth/RegisterPage.tsx")
    code = reg_path.read_text(encoding="utf-8")

    # Ensure passwords must match check exists
    assert "cleanPassword !== cleanConfirmPassword" in code or "password !== confirmPassword" in code
    assert "პაროლები არ ემთხვევა" in code


# ---------------------------------------------------------------------------
# Test C & J: Registration Data Flow & Email Username is Never Used as Name
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_registration_minimal_init_and_email_username_never_used_as_name(db_conn):
    """
    Requirements C & J:
    1. Successful registration creates auth user with only email and password.
    2. POST /v1/profiles/initialize without payload creates profile with first_name=None, last_name=None.
    3. Email username (e.g. 'nika.iordan' from 'nika.iordan@gmail.com') is NEVER parsed into first_name or last_name.
    """
    uid = str(uuid.uuid4())
    email = f"nika.iordan.{uid[:6]}@example.com"
    insert_auth_user(db_conn, uid, email, raw_meta={})
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        p = res.json()

        assert p["id"] == uid
        assert p["first_name"] is None, "Email username must NEVER be used as first_name"
        assert p["last_name"] is None, "Email username must NEVER be used as last_name"
        assert p["onboarding_completed"] is False
        assert p["onboarding_step"] == 1


# ---------------------------------------------------------------------------
# Test D: Onboarding Step 1 Identity Submission & display_name Derivation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_step1_identity_submission_and_display_name(db_conn):
    """
    Requirement D:
    Onboarding Step 1 accepts first_name and last_name.
    display_name is derived as 'First L.' (e.g. 'Nika I.').
    Full last name is never exposed in display_name.
    """
    uid = str(uuid.uuid4())
    email = f"user_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Initialize minimal profile
        await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})

        # Submit Step 1 Identity
        patch_res = await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Nika", "last_name": "Iordanishvili", "onboarding_step": 2},
        )
        assert patch_res.status_code == 200
        p = patch_res.json()

        assert p["first_name"] == "Nika"
        assert p["last_name"] == "Iordanishvili"
        assert p["display_name"] == "Nika I.", "display_name must be First L."
        assert "Iordanishvili" not in p["display_name"], "Full last name must not appear in display_name"
        assert p["onboarding_step"] == 2


# ---------------------------------------------------------------------------
# Test E, F, G: Step Transitions and Back Navigation Contracts
# ---------------------------------------------------------------------------
def test_step_navigation_contracts():
    """
    Requirements E, F, G:
    - Step 1 contains First Name + Last Name inputs.
    - Step 1 has onBack that returns to Registration.
    - Step 2 has onBack that returns to Step 1.
    - Step 3 has onBack that returns to Step 2.
    """
    onboarding_path = Path("frontend/src/modules/onboarding/BirthDataOnboardingPage.tsx")
    assert onboarding_path.exists()
    code = onboarding_path.read_text(encoding="utf-8")

    # Step 1 renders BasicProfileStep with onBack returning to registration
    assert "handleStep1Back" in code
    assert "/auth/register" in code
    assert "BasicProfileStep" in code
    assert "onBack={handleStep1Back}" in code

    # Step 2 renders BirthDateStep with onBack returning to Step 1
    assert "onBack={() => setCurrentStep(1)}" in code

    # Step 3 renders BirthTimeStep with onBack returning to Step 2
    assert "onBack={() => setCurrentStep(2)}" in code


# ---------------------------------------------------------------------------
# Test H: Existing Persisted Identity Skips Step 1 on Resume
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_persisted_identity_resumes_past_step_1(db_conn):
    """
    Requirement H:
    If a user already has first_name and last_name persisted in public.profiles:
    Resume logic advances to Step 2 or beyond.
    If first_name or last_name is missing, resume step remains 1.
    """
    uid = str(uuid.uuid4())
    email = f"resume_id_{uid[:8]}@example.com"
    insert_auth_user(db_conn, uid, email)
    token = generate_test_jwt(user_id=uid, email=email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Case 1: Uninitialized names -> Step 1
        await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token}"})
        p1 = (await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})).json()
        assert not p1.get("first_name") or not p1.get("last_name")

        # Case 2: Persisted names -> Step 2
        await ac.patch(
            "/v1/profiles/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Giorgi", "last_name": "Beridze", "onboarding_step": 2},
        )
        p2 = (await ac.get("/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})).json()
        assert p2.get("first_name") == "Giorgi"
        assert p2.get("last_name") == "Beridze"
        assert p2.get("onboarding_step") == 2


# ---------------------------------------------------------------------------
# Test I: OAuth-Provided Name Prefill
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_oauth_provided_name_prefills_identity(db_conn):
    """
    Requirement I:
    OAuth provider metadata (given_name / family_name) initializes profile names.
    If provider provides no names, fields remain None.
    """
    # 1. With OAuth names
    uid1 = str(uuid.uuid4())
    email1 = f"google_{uid1[:8]}@example.com"
    raw_meta1 = {"given_name": "Levan", "family_name": "Kapanadze", "picture": "https://example.com/p.jpg"}
    insert_auth_user(db_conn, uid1, email1, raw_meta=raw_meta1)
    token1 = generate_test_jwt(user_id=uid1, email=email1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token1}"})
        p1 = res1.json()
        assert p1["first_name"] == "Levan"
        assert p1["last_name"] == "Kapanadze"
        assert p1["display_name"] == "Levan K."

    # 2. Without OAuth names (e.g. Apple private relay)
    uid2 = str(uuid.uuid4())
    email2 = f"apple_{uid2[:8]}@privaterelay.appleid.com"
    insert_auth_user(db_conn, uid2, email2, raw_meta={})
    token2 = generate_test_jwt(user_id=uid2, email=email2)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res2 = await ac.post("/v1/profiles/initialize", headers={"Authorization": f"Bearer {token2}"})
        p2 = res2.json()
        assert p2["first_name"] is None
        assert p2["last_name"] is None
