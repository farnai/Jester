# Jester — Testing Suite Documentation

## 🧪 Test Suite Summary

The Jester test suite contains **42 automated test cases**, executing via `pytest` and `pytest-asyncio`.

```bash
python -m pytest
```

---

## 📁 Test Inventory & Category Breakdown

```text
tests/
├── astrology/
│   ├── test_astrology_api.py           [2 tests]  -> Recalculate & Safe Astro API endpoints
│   ├── test_calculation_validation.py  [9 tests]  -> Birth date, timezone, & coordinate validation
│   └── test_calculator.py              [5 tests]  -> Swiss Ephemeris Julian Day & Sun/Moon calculations
├── backend/
│   ├── test_api_endpoints.py           [1 test]   -> Profiles me GET/PATCH endpoint sanity
│   ├── test_cors_and_openapi.py        [2 tests]  -> CORS middleware headers & OpenAPI JSON schema
│   ├── test_health.py                  [2 tests]  -> /healthz & /v1/health endpoints
│   └── test_jwt_verification.py        [9 tests]  -> JWT claims, expiration, HS256/JWKS algorithms
└── database/
    └── test_database_security.py       [12 tests] -> RLS policies, RBAC grants, block rules, cascades
```

---

## 🔍 Detailed Category Analysis

### 1. Database Security & RLS Tests (`tests/database/test_database_security.py`)
- **Execution Setup**: Uses `psycopg3` direct connection to local PostgreSQL (`127.0.0.1:54322`). Sets PostgreSQL roles dynamically using `SET ROLE authenticated;`, `SET ROLE anon;`, `SET ROLE service_role;` and populates `request.jwt.claim.sub` session variables.
- **Scenarios Tested**:
  - `test_user_a_can_read_and_update_own_birth_data`: Confirms user can insert/read own `birth_data` and trigger increments `data_version`.
  - `test_user_a_cannot_read_or_update_user_b_birth_data`: Confirms User A cannot read or mutate User B's `birth_data`.
  - `test_anonymous_cannot_read_birth_data`: Verifies `anon` role receives `InsufficientPrivilege`.
  - `test_authenticated_mobile_cannot_read_astro_private`: Verifies `authenticated` role receives `InsufficientPrivilege` when attempting to SELECT from `astro_private`.
  - `test_safe_astrology_profile_visibility`: Verifies `is_discoverable = false` hides safe profile from other users.
  - `test_canonical_pair_constraint_and_reverse_prevention`: Verifies `user_a_id < user_b_id` check constraint throws `CheckViolation` on reverse pairs.
  - `test_client_cannot_update_connections_directly`: Verifies direct client `UPDATE` on `connections` is rejected (`InsufficientPrivilege`).
  - `test_block_visibility_and_mutual_profile_hiding`: Verifies blocker sees connection row, blocked user does not, and profiles are mutually hidden.
  - `test_compatibility_access_rules`: Verifies compatibility results require an active accepted connection and disappear if blocked.
  - `test_chat_rls_and_block_enforcement`: Verifies messaging requires active accepted connection and messages become hidden upon block.
  - `test_account_deletion_cascades_all_user_data`: Verifies hard-deletion of `auth.users` row cascades across all 11 tables.
  - `test_triggers_and_version_bumping`: Verifies trigger updates timestamps and bumps `birth_data.data_version`.

### 2. JWT Verification Tests (`tests/backend/test_jwt_verification.py`)
- **Scenarios Tested**:
  - Valid HS256 tokens in dev/test mode.
  - Token expiration (`ExpiredSignatureError`).
  - Missing `sub` or invalid UUID subject identifiers.
  - Prohibition of HS256 when `ENV=production`.
  - Unverified header decoding & algorithm enforcement.

### 3. Astrology Engine Tests (`tests/astrology/`)
- **Scenarios Tested**:
  - `test_calculator.py`: Verifies Julian Day conversion for known dates, planetary longitude bounds $[0^\circ, 360^\circ)$, and Zodiac sign derivation.
  - `test_calculation_validation.py`: Verifies date range checks (1900-today), timezone validity (`zoneinfo.ZoneInfo`), and coordinate boundaries.
  - `test_astrology_api.py`: Verifies `/v1/astrology/profile/recalculate` and safe profile endpoints.

---

## 🛑 Test Suite Gaps & False Confidence Warnings

While the 42 tests provide high confidence for security and privacy, there are critical functional testing gaps:

1. **False Confidence on Compatibility Endpoint**:
   - `test_compatibility_access_rules` asserts that a score payload is returned. However, the test passes because the endpoint returns a **hardcoded score of `82.5`**. The test does **not** verify whether synastry math was actually executed.
2. **No Tests for Aspect Calculation**:
   - Zero tests exist for angular aspects or orb tolerances because aspect calculation code does not exist in `calculator.py`.
3. **No Tests for Daily Transits**:
   - No tests verify transit calculations because `transits.py` is empty and the daily energy job inserts static hardcoded text.
4. **No Tests for AI / LLM Interpretations**:
   - No tests exist for prompt formatting or OpenAI responses because the `interpretation/` module contains empty stubs.
