# JESTER — Data Architecture & Test Isolation Specification
## Canonical Technical Blueprint: Phase A1
**Document Version:** 1.0.0  
**Status:** Approved Architecture Blueprint (Pre-implementation)  
**Authority:** Founder Directive (Phase A1)  
**Scope:** Repository-wide (Database, Testing, Scripts, Backend, Security)

---

## 1. Executive Summary & Problem Statement

### 1.1 Context
JESTER is a People Discovery and Relationship Intelligence engine powered by deterministic Swiss Ephemeris calculations, deterministic Synastry scoring, and a high-integrity Stars economy. 

During early development and rapid prototyping, integration tests, demo seed utilities, and local development instances operated on the same PostgreSQL database cluster (`127.0.0.1:54322`) and Supabase GoTrue authentication service (`127.0.0.1:54321`). 

### 1.2 The Root Vulnerability
The former test fixture `clean_db` in `tests/database/test_database_security.py` had `@pytest.fixture(autouse=True)` and executed:
```sql
TRUNCATE TABLE public.messages, ..., public.birth_data, public.profiles CASCADE;
```
Because multiple backend and astrology test suites imported `db_conn` from that module, pytest automatically registered this autouse fixture across unrelated tests. Whenever any developer or agent ran `pytest`, all records in `public.profiles` and `public.birth_data` were silently wiped from the local development database, while `auth.users` credentials remained intact. 

This created a severe architectural desynchronization:
1. Upon logging in, existing users received `404 Not Found` from `GET /v1/profiles/me`.
2. The frontend caught 404 and called `/v1/profiles/initialize`, creating an empty profile with `onboarding_completed: false, onboarding_step: 1`.
3. Users who had previously finished onboarding were repeatedly forced into Step 1 (Name/Surname) and Step 2 (Birth Date).
4. Thousands of orphan records accumulated in `auth.users` (2,181 auth identities vs only 73 profile rows).

### 1.3 Strategic Directive
Per Founder Decision:
1. Previously deleted profiles will **not** be reconstructed through speculative means.
2. 20 fresh, complete, realistic synthetic demo users (`@jester.test`) have been created with full Swiss Ephemeris charts.
3. A permanent, non-negotiable **CRITICAL — User Data Protection** policy is established across all agent instructions.
4. **Phase A1** establishes the permanent architectural foundation to physically isolate test execution from development and production data, preventing data corruption forever.

---

## 2. Forensic Audit of Existing Database State

An exhaustive, read-only analysis of the current local database (`127.0.0.1:54322`) reveals:

### 2.1 Quantitative Inventory
- **`auth.users` Total:** 2,181
- **`public.profiles` Total:** 73
  - `onboarding_completed = true`: 29
  - `onboarding_completed = false`: 44
- **`public.birth_data` Total:** 50
- **`public.wallets` Total:** 31
- **`public.wallet_transactions` Total:** 30
- **`public.entitlements` Total:** 10
- **`public.astro_safe_profile` Total:** 23
- **`public.astro_private` Total:** 23

### 2.2 Account Classification & Cohort Analysis
The 2,181 records in `auth.users` fall into six distinct categories:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ TOTAL AUTH IDENTITIES: 2,181                                           │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Ephemeral Automated Test Fixtures:  1,923 (88.2%)                   │
│    - Domains: @example.com (1,762), @test.jester.app, @jester.local   │
│    - Created during historical registration boundary & API tests       │
│    - 0 profiles, 0 birth data, 0 wallets                               │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Unclassified / Manual / OAuth Test Residue: 225 (10.3%)             │
│    - Domains: @gmail.com (111), @privaterelay.appleid.com (106)        │
│    - Early manual registrations and Apple/Google OAuth smoke tests     │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Synthetic Demo Cohort V1: 20 (0.9%)                                 │
│    - Namespace: demo01@jester.test through demo20@jester.test          │
│    - 100% complete profiles, adult 18+, Swiss Ephemeris placements     │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Historical Core Demo Accounts: 9 (0.4%)                             │
│    - demo_user, elene, giorgi, davit, mariam, luka, salome, nino, ana  │
│    - Intact wallets (1,000 / 995 Stars) & historical transaction ledger│
├────────────────────────────────────────────────────────────────────────┤
│ 5. Founder Real Accounts: 2 (0.1%)                                     │
│    - farna@yahoo.com, farna1@gmail.com                                 │
│    - Intact wallets (1,000 Stars initial grant)                        │
├────────────────────────────────────────────────────────────────────────┤
│ 6. Core Development Accounts: 2 (0.1%)                                 │
│    - dev@jester.app, dev-alias@jester.app                              │
│    - Fully restored complete profile, London coordinates, natal chart  │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Why Localhost-Based Safeguards Are Insufficient
Relying solely on `127.0.0.1` checks in code or tests provides **zero isolation** between Development and Testing:

1. **Shared Port Hazard (`54322`):**  
   The FastAPI server (`uvicorn` on `:8000`), the Vite frontend (`:3000`), and `pytest` all connect to `postgresql://postgres:postgres@127.0.0.1:54322/postgres`. An unhandled error, an uncommitted test rollback, or a developer running a test script directly affects the live development application state.
2. **Shared Authentication Authority (`54321`):**  
   Supabase GoTrue runs a single instance. Registration tests that invoke the HTTP API create users in the exact same `auth.users` table where developers and demo users reside.
3. **No Database Environment Fingerprinting:**  
   The PostgreSQL instance has no schema table declaring whether the database is `development`, `test`, `staging`, or `production`. Tests cannot programmatically verify whether they are operating in a sandbox.
4. **Lack of Transaction Isolation in Fixtures:**  
   Tests previously committed changes directly to tables and relied on teardown fixtures to issue `DELETE` or `TRUNCATE` statements. If a test runner was cancelled (Ctrl+C, timeout, memory crash), test records remained permanently in the database.

---

## 3. Target Architecture: Physical Stack & Container Isolation

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      DEVELOPMENT STACK (Project: "Jester")                       │
│                                                                                  │
│   Frontend (Port 3000) ───────► Backend API (Port 8000)                         │
│                                           │                                      │
│                                           ▼                                      │
│                             Supabase Kong Gateway (Port 54321)                   │
│                                ├── Auth / GoTrue (Port 54321/auth/v1)            │
│                                ├── PostgREST API (Port 54321/rest/v1)            │
│                                ├── Realtime & Storage APIs                       │
│                                           ▼                                      │
│                       PostgreSQL DB: "postgres" (Port 54322)                     │
│                       - Container: "supabase_db_Jester"                          │
│                       - Network: "supabase_network_Jester"                       │
│                       - Dedicated Docker Volumes (Dev Persistent Data)           │
│                       - Environment: "development"                               │
│                       - Destructive testing: BLOCKED (Fail-Closed)               │
│                       - Retains: 2,181 Auth identities, 73 profiles,             │
│                                  20 Demo accounts, Wallets, Ledger               │
└──────────────────────────────────────────────────────────────────────────────────┘

                                        ▲
                                        │ COMPLETE PHYSICAL AIR-GAP
                                        │ (Independent Ports, Daemons & Volumes)
                                        ▼

┌──────────────────────────────────────────────────────────────────────────────────┐
│                     ISOLATED TESTING STACK (Project: "jester_test")              │
│                                                                                  │
│   Pytest Runner / Test API ──────────────────────────────────────────────┐       │
│                                                                          ▼       │
│                             Supabase Kong Gateway (Port 54421)                   │
│                                ├── Auth / GoTrue (Port 54421/auth/v1)            │
│                                ├── PostgREST API (Port 54421/rest/v1)            │
│                                ├── Storage & Mailpit (Port 54424)                │
│                                           ▼                                      │
│                       PostgreSQL DB: "postgres" (Port 54422)                     │
│                       - Container: "supabase_db_jester_test"                     │
│                       - Network: "supabase_network_jester_test"                  │
│                       - Independent Docker Volumes (Ephemeral Test Data)         │
│                       - Environment: "test"                                      │
│                       - Destructive testing: PERMITTED ONLY HERE                 │
│                       - Multi-signal Fail-Closed Identity Verification           │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 True Physical Stack Isolation Architecture
Earlier draft proposals of sharing a single PostgreSQL container between Development and Test databases do not provide true physical isolation. In our approved Phase A2 architecture, the Test stack is a fully independent local Supabase deployment:

1. **Independent Docker Daemons & Containers:**  
   The test environment runs separate containers (`supabase_db_jester_test`, `supabase_auth_jester_test`, `supabase_kong_jester_test`, `supabase_storage_jester_test`, etc.). If a test crashes the database, starves memory, or restarts the container, the Development environment (`supabase_*_Jester`) is completely untouched.
2. **Independent Network Ports:**  
   - API / Kong: `54421` (Dev is `54321`)
   - PostgreSQL DB: `54422` (Dev is `54322`)
   - Shadow DB: `54420` (Dev is `54320`)
   - Studio: `54423` (Dev is `54323`)
   - Inbucket/Mailpit: `54424` (Dev is `54324`)
   - Analytics: `54427` (Dev is `54327`)
   - Pooler: `54429` (Dev is `54329`)
   - Edge Runtime Inspector: `8084` (Dev is `8083`)
3. **Independent Supabase Auth / GoTrue Service:**  
   Integration and registration tests produce users strictly inside the test GoTrue instance (`54421`), ensuring 0 orphan test users ever pollute the development `auth.users` table.
4. **Independent Supabase Storage & Buckets:**  
   Avatar and media uploads during tests are written to test-specific storage volumes and cannot overwrite development assets.
5. **Dedicated Configuration Directory:**  
   Managed via `supabase_test/supabase/config.toml` using `npx supabase start --workdir supabase_test`.

### 3.2 Fail-Closed Multi-Signal Environment Identity Verification
To guarantee that no test or script ever executes destructive commands against the Development environment even if a configuration file is misconfigured, a multi-signal fail-closed verification guard (`backend/app/core/environment_verifier.py`) is enforced:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     FAIL-CLOSED MULTI-SIGNAL VERIFIER                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Signal 1: Operating Port Check       ──► Port MUST NOT be 54322 (Dev DB)       │
│ Signal 2: API Gateway Port Check     ──► Port MUST NOT be 54321 (Dev Kong)     │
│ Signal 3: Environment Variable Check ──► ENV must be explicitly 'test'          │
│ Signal 4: Database Metadata Check    ──► public.database_environment_meta       │
│                                          environment == 'test' AND              │
│                                          is_destructive_testing_allowed == true │
│ Signal 5: Project Container Tag      ──► Docker container must match test id    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ DECISION: IF ANY DEV SIGNAL DETECTED OR SIGNALS AMBIGUOUS ──► ABORT IMMEDIATELY │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Fail-Closed Guard Enforcement Rule:
```python
def assert_test_environment_safety(db_url: str, env_name: str, conn: psycopg.Connection):
    # Signal 1: Port safety
    if ":54322" in db_url or ":54321" in db_url:
        raise RuntimeError("CRITICAL SAFETY VIOLATION: Target URL matches DEVELOPMENT ports (54322/54321)!")
    
    # Signal 2: ENV safety
    if env_name != "test":
        raise RuntimeError(f"CRITICAL SAFETY VIOLATION: ENV is set to '{env_name}', expected 'test'!")
        
    # Signal 3: Database metadata safety
    with conn.cursor() as cur:
        cur.execute("SELECT environment, is_destructive_testing_allowed FROM public.database_environment_meta LIMIT 1;")
        meta = cur.fetchone()
        if not meta or meta["environment"] != "test" or not meta["is_destructive_testing_allowed"]:
            raise RuntimeError(
                f"CRITICAL SAFETY VIOLATION: Database metadata is not approved for testing! "
                f"Detected: {meta}. Execution aborted to protect user data."
            )
```

### 3.3 Test Execution Boundaries
Tests in JESTER are categorized into three distinct execution boundaries:

1. **DB Unit & Security Tests (Database Tier):**  
   - Target: `TEST_DATABASE_URL` (`postgresql://postgres:postgres@127.0.0.1:54422/postgres`)  
   - Scope: RLS policies, database triggers, constraints, migration validity, Swiss Ephemeris calculations.  
   - Mechanism: Executed against the isolated test database within function-level transaction rollbacks (`test_txn`), leaving the test database clean.
2. **Backend HTTP Integration Tests (API Tier):**  
   - Target: Test FastAPI server backed by Test Supabase (`54421` / `54422`).  
   - Scope: Registration, login, profile initialization, stars wallet, notifications, discovery endpoints.  
   - Mechanism: Isolated test accounts in Test GoTrue; never touch Dev GoTrue.
3. **Browser E2E Tests (Full-Stack Tier):**  
   - Target: Frontend connecting to Test API & Test Kong (`54421`).  
   - Scope: Playwright browser flows, onboarding UI, wallet purchase modals.  
   - Mechanism: Complete end-to-end sandbox. Dev frontend (`:3000`) and Dev stack (`:54321`) remain completely separate.

---

## 4. Centralized Pytest Lifecycle & Isolation Architecture

### 4.1 Implemented `tests/conftest.py` Architecture
JESTER now features a root `tests/conftest.py` that serves as the single source of truth for all test execution:

1. **`pytest_configure(config)`:**
   - Early hook setting `ENV=test`, pointing `DATABASE_URL` and `TEST_DATABASE_URL` strictly to `54422`, and `SUPABASE_URL` to `54421`.
   - Clears `get_settings.cache_clear()` so all backend configuration models reload the test settings.
2. **`verified_test_env` (Session-scoped):**
   - Connects strictly to `TEST_DATABASE_URL` (`postgresql://postgres:postgres@127.0.0.1:54422/postgres`).
   - Runs `verify_environment_safety(expected_env="test")`. Fails fast with `EnvironmentSafetyError` if any DEV port (54322/54321) or DEV metadata is detected.
   - Idempotently cleans prior ephemeral test residue strictly within the verified test database at session start.
3. **`db_conn` (Session-scoped):**
   - Authoritative connection to the dedicated TEST PostgreSQL instance on port `54422`.
4. **`test_txn` (Function-scoped — Transaction Rollback):**
   - Opens a PostgreSQL transaction: `conn.execute("BEGIN;")`.
   - Yields the connection to the test.
   - On teardown, executes `conn.execute("ROLLBACK;")`.
   - **Benefit:** Zero `DELETE`, zero `TRUNCATE`, zero cleanup SQL. Every test leaves the database identically pristine, 100x faster execution, and zero leak risk.
5. **`clean_db` (Function-scoped — Safe Tracked Cleanup):**
   - Test-scoped cleanup fixture for tests that commit outside of `test_txn`.
   - Cleans ONLY records explicitly registered in `_test_user_registry` and `_test_conv_registry`.
   - Strictly prohibits broad truncate or pattern deletes (`DELETE FROM ... WHERE email LIKE ...`).
6. **`create_test_user` & `set_auth_context`:**
   - Standardized helpers for creating test users in `auth.users` and `public.profiles`, and switching PostgreSQL RLS roles (`anon`, `authenticated`, `service_role`).

### 4.2 Migration Portability Strategy
To avoid maintaining two separate migration histories and to guarantee 100% portability across Windows, Linux, macOS, and CI:
1. **Single Source of Truth:** `supabase/migrations/` remains the sole canonical migration directory.
2. **Ignored Test Migrations:** `.gitignore` explicitly ignores `supabase_test/supabase/migrations/`, preventing Git from committing duplicate migration histories or fragile NTFS junctions.
3. **Cross-Platform Sync (`scripts/setup_test_environment.py`):** Automatically creates a Windows Directory Junction (`mklink /J`) on Windows, a symbolic link (`os.symlink`) on POSIX, or falls back to file copy (`shutil.copytree`).

---

## 5. Declarative Data Catalog & Cohort Registry (Implemented in Phase A4)

The JESTER Data Catalog provides a centralized, versioned, declarative specification for all persistent and synthetic data cohorts across Development and Testing environments. It replaces ad-hoc seed scripts with a single source of truth without requiring extra database migrations or administration services.

### 5.1 Architecture & Schema
The catalog is defined declaratively in `backend/app/data_catalog/catalog.json` and backed by typed models in `backend/app/data_catalog/models.py`:

Each cohort defines:
- `id`: Unique identifier (e.g., `demo-people-v1`, `protected-core-dev-v1`).
- `category`: Cohort category from the approved taxonomy.
- `version`: SemVer string (e.g., `1.0.0`).
- `description`: Plaintext summary of cohort purpose and composition.
- `environment`: List of target environments (`["development"]`, `["test"]`, etc.).
- `origin`: Data provenance (`"synthetic"`, `"founder"`, `"qa_test"`, `"historical_migration"`).
- `persistence_policy`: Persistence guarantee (`"permanent"`, `"ephemeral_test"`, `"protected_historical"`).
- `status`: Lifecycle state (`"active"`, `"disabled"`, `"retired"`).
- `source`: Repository path to JSON source definition or test module.
- `expected_count`: Exact integer count of members.
- `dependencies`: List of prerequisite cohort IDs.
- `validation_rules`: Declarative dictionary of validation flags (e.g., `require_profiles`, `require_birth_data`, `require_adult_age`, `require_astrology_calculated`, `unique_emails`).

### 5.2 Approved Cohort Categories
The catalog enforces 8 strictly defined categories:
1. **`persistent_demo`**: Verified synthetic personas for product demonstration and UX exploration (e.g. `demo-people-v1`).
2. **`protected_dev`**: Essential developer and founder accounts with preserved wallets and credentials (`protected-core-dev-v1`).
3. **`auth_qa`**: Synthetic fixtures for authentication, JWKS, and token lifecycle tests (`auth-qa-v1`).
4. **`onboarding_qa`**: Step boundary and completion verification fixtures (`onboarding-qa-v1`).
5. **`discovery_qa`**: Decks for validating 18+ enforcement, location fallback, and mutual blocking (`discovery-qa-v1`).
6. **`wallet_qa`**: Concurrency, idempotency, and ledger consistency fixtures (`wallet-qa-v1`).
7. **`privacy_rls_qa`**: PostgreSQL Row-Level Security and owner-only privacy tests (`privacy-rls-qa-v1`).
8. **`historical_unmanaged`**: Legacy unclassified identities in DEV protected from unauthorized deletion (`historical-unmanaged-dev`).

### 5.3 Dynamic Lifecycle States
Cohorts support three lifecycle states:
- **`active`**: Participates in validation, seeding, and management workflows.
- **`disabled`**: Temporarily excluded from management workflows without deleting any database records.
- **`retired`**: Permanently preserved historical cohort; excluded from active provisioning.

Lifecycle states control catalog workflows only; they do not trigger automatic user deletion or alter application-layer discovery visibility.

### 5.4 Read-Only Validation Layer
The catalog provides a guaranteed 100% read-only validation layer (`backend/app/data_catalog/validator.py`):
1. **In-Memory Validation (`validate_catalog_metadata`)**: Checks for duplicate IDs, invalid SemVer, unsupported environments, missing dependencies, cyclic dependencies, and source existence.
2. **Database Verification (`validate_cohort_in_database`)**: Executes pure `SELECT` queries against PostgreSQL to verify actual user IDs, profile existence, adult age (18+), and complete Swiss Ephemeris natal charts without mutating any records.

### 5.5 Phase A5 CLI Integration Roadmap
In Phase A5, the unified management CLI (`backend/app/tools/data_manager.py`) will consume this catalog:
- `python -m backend.app.tools.data_manager status`: Reads catalog and reports DB cohort counts.
- `python -m backend.app.tools.data_manager verify [--cohort <id>]`: Runs read-only validation against the target environment.
- `python -m backend.app.tools.data_manager list [--category <cat>]`: Lists cohort members without exposing secrets.
- `python -m backend.app.tools.data_manager plan <cohort>`: Computes non-destructive diff against target DB.
- `python -m backend.app.tools.data_manager seed <cohort>`: Executes idempotent, creation-only provisioning.

### 5.6 Test-Cleanup Architecture & Policy Blocker
During Phase A4 analysis, the test lifecycle was evaluated against the Founder's strict no-deletion directive:
- Unit tests (`tests/database/`) can be isolated via function-level transaction rollbacks (`test_txn`).
- However, HTTP integration tests (`tests/backend/test_discovery.py`, etc.) communicate with the FastAPI server via independent connections where transaction rollback is not visible across processes.
- Disabling teardown deletions entirely causes leftover discoverable test profiles to accumulate, pushing newly seeded candidates past pagination thresholds (`LIMIT 20`).
- **Conclusion / Blocker:** Safely eliminating teardown deletions for HTTP tests requires either:
  1. An ASGI-scoped shared test transaction dependency, OR
  2. Cohort-scoped test discovery filtering, OR
  3. Explicit Founder authorization for ephemeral test-runner teardown strictly restricted to `auth.users` rows created by the running test session on port `54422`.

---

## 6. Protection of Existing Data & Financial State

The permanent **CRITICAL — User Data Protection** rules established in `AGENTS.md` and `docs/AI.md` are backed by database-level triggers in the development database:

### 6.1 Database Immortality Trigger for Protected Cohorts
```sql
CREATE OR REPLACE FUNCTION public.protect_immutable_user_data()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME = 'profiles' AND OLD.id IN (
        '44444444-4444-4444-4444-444444444444', -- dev@jester.app
        '44444444-4444-4444-4444-444444444445'  -- dev-alias@jester.app
    ) THEN
        RAISE EXCEPTION 'DATABASE PROTECTION ERROR: Deletion of core developer profile is prohibited!';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
```

---

## 7. Incremental Refactoring Roadmap: Phases A2 – A6

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  PHASE A2    │────►│  PHASE A3    │────►│  PHASE A4    │
│  Meta Table  │     │  jester_test │     │  Unified CLI │
│  & Guards    │     │  Provisioning│     │  & Catalog   │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                     ┌──────────────┐            │
                     │  PHASE A6    │◄───────────┤
                     │  Orphan User │            ▼
                     │  Quarantine  │     ┌──────────────┐
                     └──────────────┘     │  PHASE A5    │
                                          │  Pytest Txn  │
                                          │  Refactoring │
                                          └──────────────┘
```

### Phase A2: Independent Test Supabase Stack & Identity Guards (COMPLETED)
- **Status:** [x] Done
- **Migration:** Created `033_database_environment_meta.sql` tagging `development` and `test` environments.
- **Backend Guard:** Implemented `backend/app/core/environment_verifier.py` with multi-signal fail-closed verification.
- **Infrastructure:** Provisioned fully independent Supabase test stack on ports `54420`–`54429`.

### Phase A3: Centralized Test Architecture & Fail-Closed Isolation (COMPLETED)
- **Status:** [x] Done
- **Central Conftest:** Created `tests/conftest.py` with `verified_test_env`, `db_conn`, `test_txn`, `clean_db`, `create_test_user`.
- **Port Isolation:** Eliminated hardcoded port `54322` from all tests; all tests route to `:54422` (DB) and `:54421` (API).
- **Migration Portability:** Canonical migrations stay in `supabase/migrations/`; `.gitignore` ignores test migrations; automated cross-platform sync helper added.
- **Verification:** Unit tests execute without database; DB/API integration tests execute exclusively against `:54422`/`:54421`; Development database remains 100% untouched.

### Phase A4: Declarative Data Catalog & Cohort Registry (COMPLETED)
- **Status:** [x] Done
- **Package Architecture:** Implemented `backend/app/data_catalog/` containing:
  - `models.py`: Pydantic models for `Cohort`, `CohortCategory`, `CohortStatus`, `PersistencePolicy`, and `CatalogSchema`.
  - `catalog.json`: Canonical declarative registry of all 8 cohorts across environments.
  - `loader.py`: Safe catalog and source loading utilities.
  - `validator.py`: Comprehensive schema and database integrity validation.
  - `sources/demo_people_v1.json`: Declarative personas specification for the 20 synthetic demo accounts.
- **Verification:** 8 automated tests in `tests/backend/test_data_catalog.py` passing 100%.

### Phase A5: Unified Data Management CLI & Safe Test Lifecycle (COMPLETED)
- **Status:** [x] Done
- **Canonical CLI Tool:** Implemented `backend/app/tools/data_manager.py` with 5 safe commands:
  - `list`: Browse registered cohorts, categories, versions, and lifecycle status (supports table and JSON).
  - `status`: Comprehensive diagnostic report comparing catalog expected counts with real DB metrics across DEV and TEST.
  - `verify`: Preflight integrity and presence verification against active database targets.
  - `plan`: Deterministic, non-destructive preview of proposed seed operations without committing writes.
  - `seed`: Guarded, creation-only provisioning strictly requiring `--apply-plan`. 100% idempotent; rejects protected cohorts.
- **Safety Invariants Enforced in CLI:**
  - Strictly NO destructive subcommands (`delete`, `truncate`, `drop`, `reset`, `purge`, `wipe`).
  - Protected cohorts (`protected-core-dev-v1`, `historical-unmanaged-dev`) are strictly immutable and rejected from plan/seed.
  - Inactive lifecycle states (`disabled`, `retired`) are rejected from plan/seed.
  - Creation-only writes: zero updates or overwrites of existing user records.
- **P0 Automatic Test Deletion Resolution:**
  - Removed all `DELETE FROM auth.users` statements from `tests/conftest.py` (`verified_test_env`, `clean_db`, `create_test_user`).
  - Switched test suites to unique email namespacing (`{local}_{uid[:8]}@{domain}`) and unique connection pairs.
  - Refactored `test_database_security.py` and `test_discovery.py` to eliminate dependencies on empty database tables.
  - Result: Complete test suite (439 tests) executes with **ZERO automatic deletions**.
- **CLI Automated Test Suite:** Implemented `tests/backend/test_data_manager_cli.py` (13 tests passing 100%).
- **DEV Database Integrity:** Verified 100% identical state (2,180 users, 72 profiles) with zero corruption.

### Phase A6: Final Engineering & Security Audit (COMPLETED)
- **Status:** [x] Done
- **DEV / TEST Physical Isolation:** Verified 100% independent Docker containers, storage volumes, and ports.
  - DEV Stack: PostgreSQL `:54322`, Kong `:54321`, Inbucket `:54324`, Studio `:54323`.
  - TEST Stack: PostgreSQL `:54422`, Kong `:54421`, Inbucket `:54424`, Studio `:54423`.
- **Environment Metadata Canonical Table:** Verified and unified as `public.database_environment_meta` across both stacks and `backend/app/core/environment_verifier.py`.
- **Plan Execution Integrity (TOCTOU Guard):** Implemented cryptographic SHA256 plan fingerprinting in `generate_seed_plan`, displayed in `plan`, and enforced in `seed --apply-plan --fingerprint <hash>`.
- **Zero Automatic Test Deletions:** Eliminated teardown user deletions across all test fixtures (`test_discovery_deck.py`, `test_messaging_wave4.py`, `test_social_profiles.py`, `conftest.py`).
- **Regression Verification:** All 442 automated tests passing in 47.69s.
- **DEV Database Integrity:** 100% match with pre-refactoring baseline (2,180 users, 72 profiles, 32 wallets, 30 transactions, 10 entitlements).
- **Known Limitations:** Automated Playwright browser E2E test suite remains absent (documented as coverage limitation; not substituted with backend pytest).

---

## 8. Non-Destructive Retention Strategy & AI Agent Instructions

### 8.1 Retention Policy for Test Environments
1. **Zero Deletion Invariant:** Pytest suites must never delete accounts from `auth.users` or user-owned tables.
2. **Unique Namespacing:** Dynamic test fixtures must use unique namespaced identifiers (e.g. `{prefix}_{uuid[:8]}@{domain}`) and dynamic sorted ID pairs (`min(u1, u2), max(u1, u2)`).
3. **Container-Level Lifecycle:** If the TEST database accumulates excessive rows (>50,000 rows), the entire test container may be reset via explicit, Founder-approved infrastructure tooling (`scripts/setup_test_environment.py`), which fail-closes against port 54322. Pytest fixtures themselves must remain 100% non-destructive.

### 8.2 Instructions for Future AI Agents
1. **Never use ad-hoc seed scripts:** All seed, status, and verification operations must execute strictly via `python -m backend.app.tools.data_manager`.
2. **Read-Only First:** Always run `status`, `verify`, or `plan` before attempting provisioning.
3. **Never delete users:** The Founder policy against user deletion applies to dev, staging, and synthetic accounts.
4. **Environment check:** Always ensure `ENV=test` and ports `:54422`/`:54421` before running any test command.

---

## 9. Risks, Mitigations & Acceptance Criteria

### 8.1 Risk Matrix
| Risk | Probability | Severity | Mitigation Strategy |
|---|---|---|---|
| Accidental test run against Development DB | Medium | Critical | Fail-Closed Environment Guard aborts session if DB != `test` |
| Orphan accounts in Test GoTrue | Low | Low | Dedicated `jester_test` DB uses transaction rollback; no persistent rows |
| Seed script overwriting valid user edits | Low | High | Creation-only `ON CONFLICT DO NOTHING`; CLI `plan` dry-run required |
| Migration drift between Dev and Test DBs | Medium | Medium | `setup_test_db.py` applies all canonical migrations in order |

### 8.2 Phase A1 Acceptance Criteria
- [x] Read-only audit completed across all 2,181 auth users and 73 profiles.
- [x] Exact causes of localhost test vulnerability identified and documented.
- [x] Dual-database physical isolation architecture specified.
- [x] Fail-closed environment guard and meta schema designed.
- [x] Pytest transaction rollback lifecycle specified.
- [x] Unified Data CLI and Cohort registry designed.
- [x] Phased implementation roadmap (A2–A6) detailed with dependencies.
- [x] Existing data, wallets, and entitlements left untouched.
- [x] Execution paused after A1 for Founder review.

