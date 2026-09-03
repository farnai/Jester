# Jester — Testing Suite Documentation

## 🧪 Test Suite Summary

The Jester test suite contains **74 automated test cases**, executing via `pytest` and `pytest-asyncio`.

```bash
python -m pytest
```

All 74 tests pass deterministically in development and CI environments.

---

## 📁 Complete Test Inventory & Category Breakdown (74 Tests)

```text
tests/
├── astrology/
│   ├── test_aspects.py                 [17 tests] -> Angular aspects, quadratic decay, orbs, luminary boost, Ascendant cap
│   ├── test_astrology_api.py           [ 2 tests] -> Recalculate & Safe Astro API endpoints
│   ├── test_calculation_validation.py  [10 tests] -> Birth date, timezone, polar errors, & coordinate validation
│   └── test_calculator.py              [ 5 tests] -> Swiss Ephemeris Julian Day & Sun/Moon/Placidus calculations
├── backend/
│   ├── test_api_endpoints.py           [ 1 test ] -> Profiles me GET/PATCH endpoint sanity
│   ├── test_cors_and_openapi.py        [ 2 tests] -> CORS middleware headers & OpenAPI JSON schema
│   ├── test_health.py                  [ 2 tests] -> /healthz & /v1/health endpoints
│   ├── test_jwt_verification.py        [ 9 tests] -> JWT claims, expiration, HS256/JWKS algorithms
│   └── test_profiles_self_healing.py   [ 4 tests] -> Profile auto-provisioning on first JWT authentication
├── compatibility/
│   ├── test_router.py                  [ 2 tests] -> /v1/compare endpoint integration, authorization, & block guards
│   └── test_synastry.py                [ 8 tests] -> Synastry V1 math, symmetry f(A,B)==f(B,A), dimensions, signals, normalization
└── database/
    └── test_database_security.py       [12 tests] -> RLS policies, RBAC grants, block rules, cascades
```

---

## 🔍 Detailed Subsystem Verification

### 1. Synastry V1 Compatibility Engine (`tests/compatibility/`)
- **Aspect Symmetry**: Confirms $f(\text{Person A}, \text{Person B}) \equiv f(\text{Person B}, \text{Person A})$.
- **4 Sub-Score Calculations**: Validates Emotional Harmony, Communication, Attraction/Chemistry, and Growth bounds $[0.0, 100.0]$.
- **Composite Score Normalization**: Verifies non-linear stretch curve produces scores within $[10.0, 98.0]$.
- **Resilience to Unknown Birth Time**: Verifies calculations succeed when birth time is unknown, gracefully scaling weights and setting confidence to `0.75`.
- **Signal Extraction & Starters**: Validates deterministic extraction of top relationship signals, topics, and starters.

### 2. Planetary Aspects & Orbs (`tests/astrology/test_aspects.py`)
- **Supported Angles**: Validates Conjunction ($0^\circ$), Sextile ($60^\circ$), Square ($90^\circ$), Trine ($120^\circ$), and Opposition ($180^\circ$).
- **Quadratic Decay**: Asserts exact aspects receive strength $1.00$, halfway orbs receive $0.25$, and edge orbs receive $0.00$.
- **Modifiers**: Verifies $+2.0^\circ$ boost for Luminaries (Sun, Moon) and $6.0^\circ$ cap for Ascendant.

### 3. Database Security & RLS (`tests/database/test_database_security.py`)
- Direct PostgreSQL session testing using dynamic roles (`authenticated`, `anon`, `service_role`).
- Verifies `birth_data` is strictly owner-only.
- Verifies `astro_private` triggers `InsufficientPrivilege` on client roles (`REVOKE ALL`).
- Verifies mutual block hiding (blocker and blocked users cannot read each other's profiles or compatibility).
- Verifies hard account deletion cascades across all application tables.

### 4. JWT Verification (`tests/backend/test_jwt_verification.py`)
- Rejection of symmetric `HS256` tokens in `ENV=production`.
- Support for `HS256` in dev/test only.
- Expiration and malformed payload enforcement.

---

## 🛑 Real Test Suite Gaps (Remaining Work)

While the core security, natal astrology, and Synastry V1 subsystems have 100% test coverage, the following gaps remain due to pending implementation:

1. **Daily Transit Engine**:
   - No tests verify transit aspect calculations because `backend/app/astrology/transits.py` is currently an empty stub.
2. **AI / LLM Voice Interpretation Pipeline**:
   - No tests verify OpenAI API client integration, prompt rendering, or JESTER voice generation because `backend/app/interpretation/` modules are architectural stubs.
3. **Extended Celestial Bodies**:
   - Chiron, Lilith, and Lunar Nodes do not have calculation tests because they are not yet supported in `calculator.py`.

