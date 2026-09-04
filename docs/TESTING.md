# Jester — Testing Suite Documentation

## 🧪 Test Suite Summary

The Jester test suite contains **89 automated test cases**, executing via `pytest` and `pytest-asyncio`.

```bash
python -m pytest
```

All 89 tests pass deterministically in development and CI environments.

---

## 📁 Complete Test Inventory & Category Breakdown (89 Tests)

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
├── database/
│   └── test_database_security.py       [12 tests] -> RLS policies, RBAC grants, block rules, cascades
└── interpretation/
    └── test_interpretation.py          [15 tests] -> Semantic mapping, stable IDs, AI draft fallback, copywriter priority,
                                                      engine-content independence, frontend safety, zero jargon, Deep Analysis
```

---

## 🔍 Detailed Subsystem Verification

### 1. Synastry V1 Compatibility Engine (`tests/compatibility/`)
- **Aspect Symmetry**: Confirms $f(\text{Person A}, \text{Person B}) \equiv f(\text{Person B}, \text{Person A})$.
- **4 Sub-Score Calculations**: Validates Emotional Harmony, Communication, Attraction/Chemistry, and Growth bounds $[0.0, 100.0]$.
- **Composite Score Normalization**: Verifies non-linear stretch curve produces scores within $[10.0, 98.0]$.
- **Resilience to Unknown Birth Time**: Verifies calculations succeed when birth time is unknown, gracefully scaling weights and setting confidence to `0.75`.
- **Signal Extraction & Starters**: Validates deterministic extraction of top relationship signals, topics, and starters.

### 2. Interpretation Contract & JESTER Voice Content Layer (`tests/interpretation/`)
- **Deterministic Signal Mapping**: Verified deterministic mapping of aspect signals to semantic contract IDs.
- **Stable Semantic IDs**: Verifies IDs follow `{context}.{category}.{theme}.v{version}` rather than raw planet coordinates.
- **Content Lifecycle & Fallback**: Validates `approved` copy priority, `ai_draft` fallback on unreviewed/empty final copy, and reset mechanism.
- **Zero Astrology-Engine Dependency**: Verified that updating or replacing copy text causes 0% change in compatibility math or scores.
- **No Astrology Jargon**: Scans all Georgian initial drafts against the forbidden jargon blacklist (zero matches).
- **Deep Analysis Pipeline**: Verifies multi-block synthesis traceable to aspect evidence trace.
- **REST API Flow**: Verifies list, detail, copy update, reset, and signal resolution endpoints.

### 3. Planetary Aspects & Orbs (`tests/astrology/test_aspects.py`)
- **Supported Angles**: Validates Conjunction ($0^\circ$), Sextile ($60^\circ$), Square ($90^\circ$), Trine ($120^\circ$), and Opposition ($180^\circ$).
- **Quadratic Decay**: Asserts exact aspects receive strength $1.00$, halfway orbs receive $0.25$, and edge orbs receive $0.00$.
- **Modifiers**: Verifies $+2.0^\circ$ boost for Luminaries (Sun, Moon) and $6.0^\circ$ cap for Ascendant.

### 4. Database Security & RLS (`tests/database/test_database_security.py`)
- Direct PostgreSQL session testing using dynamic roles (`authenticated`, `anon`, `service_role`).
- Verifies `birth_data` is strictly owner-only.
- Verifies `astro_private` triggers `InsufficientPrivilege` on client roles (`REVOKE ALL`).
- Verifies mutual block hiding (blocker and blocked users cannot read each other's profiles or compatibility).
- Verifies hard account deletion cascades across all application tables.

### 5. JWT Verification (`tests/backend/test_jwt_verification.py`)
- Rejection of symmetric `HS256` tokens in `ENV=production`.
- Support for `HS256` in dev/test only.
- Expiration and malformed payload enforcement.

---

## 🛑 Real Test Suite Gaps (Remaining Work)

While core security, natal astrology, Synastry V1, and the Interpretation Content Layer have 100% test coverage, the following gaps remain:

1. **Daily Transit Engine**:
   - No tests verify transit aspect calculations because `backend/app/astrology/transits.py` is currently an empty stub.
2. **External Live LLM API Testing**:
   - The interpretation content layer, prompt builder, and Deep Analysis models are fully tested offline; live OpenAI API network calls remain a planned integration.
3. **Extended Celestial Bodies**:
   - Chiron, Lilith, and Lunar Nodes do not have calculation tests because they are not yet supported in `calculator.py`.

