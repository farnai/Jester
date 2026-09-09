# JESTER — Security & Privacy Architecture Policy

[![Security: RLS Enforced](https://img.shields.io/badge/Security-RLS%20Enforced-success.svg)](#postgresql-role-privileges--row-level-security-rls)
[![Auth: Asymmetric JWKS](https://img.shields.io/badge/Auth-Asymmetric%20JWKS-blue.svg)](#authentication--token-validation-backendappauth)
[![Tests: 193 Passed](https://img.shields.io/badge/Tests-193%20Passed-brightgreen.svg)](#automated-security-testing--verification)

> **In JESTER, user privacy is not an afterthought or an optional setting—it is a foundational mathematical and architectural invariant.**

JESTER is a **People Discovery and Relationship Intelligence** engine. Because interpersonal insight depends on private personal data (such as birth timestamps and exact geographical coordinates), our security architecture is designed to mathematically isolate raw user data, prevent identity impersonation, eliminate existence oracles, and enforce strict boundary separation across every layer of the stack.

---

## 📋 Supported Versions

Security updates and vulnerability patches are actively maintained for the following versions:

| Component | Version | Supported | Security Posture |
| :--- | :--- | :---: | :--- |
| **JESTER API Backend** | `1.x` (`main`) | ✅ | Active JWKS asymmetric verification, RLS enforcement |
| **Frontend Web Client** | `0.x` (`main`) | ✅ | Authenticated session lifecycle, bearer authorization |
| **Database Migrations** | `001-020` | ✅ | Least privilege roles, procedural hardening |

---

## 🔑 Authentication & Token Validation (`backend/app/auth/`)

JESTER enforces a zero-trust, stateless token validation architecture powered by Supabase Authentication and verified via FastAPI dependencies.

### 1. Dual-Mode JWT Verification (`backend/app/auth/jwt.py`)

- **Production Mode (`ENV=production`):**
  - **Strict Asymmetric Enforcement:** Requires asymmetric cryptographic algorithms (`RS256`, `ES256`, or `EdDSA`).
  - **Dynamic Key Resolution:** Public keys are fetched and cached from the Supabase JWKS endpoint (`SUPABASE_JWKS_URL`) via `PyJWKClient`.
  - **Hard Fallback Prohibition:** If an asymmetric token fails key resolution, it **never** falls back to symmetric HS256. If any token declaring `alg=HS256` arrives in production, it is rejected immediately with HTTP 401.
  - **Replay & Expiration Checks:** Tokens are validated against `exp`, `nbf`, `iat`, and valid `iss`/`aud` claims.

- **Development & Testing Mode (`ENV=development` / `ENV=test`):**
  - Symmetric `HS256` signatures are permitted exclusively for offline unit testing and automated integration pipelines using `SUPABASE_JWT_SECRET`.

### 2. Subject & Claims Validation
- Decodes the `sub` claim and verifies that it is a valid UUID (`user_id`).
- Extracts tenant roles (`authenticated`, `copywriter`, `admin`, `service_role`).
- Populates the trusted [`AuthenticatedUser`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/backend/app/auth/models.py) dependency for downstream route authorization.

---

## 🛡️ PostgreSQL Role Privileges & Row-Level Security (RLS)

PostgreSQL security operates on the **Principle of Least Privilege**, separating public anonymous visitors, authenticated end-users, and trusted internal backend workers.

```text
                        ┌─────────────────────────────────────────┐
                        │      PostgreSQL Database (Supabase)     │
                        └────────────────────┬────────────────────┘
                                             │
             ┌───────────────────────────────┼───────────────────────────────┐
             ▼                               ▼                               ▼
     ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
     │   anon Role   │               │ authenticated │               │ service_role  │
     └───────┬───────┘               └───────┬───────┘               └───────┬───────┘
             │                               │                               │
    REVOKE ALL ON ALL               RLS Enforced Access             Bypasses RLS Policies
    Tables & Routines               (Profiles, Safe Astro,          Dedicated Backend Pool
    (Zero Data Access)              Connections, Messages)          (Trusted Engine Logic)
```

### Table Privileges & Access Boundary Matrix

| Table / Surface | `anon` Role | `authenticated` Role (Client JWT) | `service_role` (Backend Engine) |
| :--- | :--- | :--- | :--- |
| `public.birth_data` | 🚫 **REVOKED** | `SELECT, INSERT, UPDATE` (Strictly `user_id = auth.uid()`) | 🟢 Full Access |
| `public.astro_private` | 🚫 **REVOKED** | 🚫 **REVOKED** (`REVOKE ALL FROM authenticated, anon, public`) | 🟢 Full Access (Calculations only) |
| `public.astro_safe_profile` | 🚫 **REVOKED** | `SELECT` (Own profile OR discoverable/unblocked target) | 🟢 Full Access |
| `public.profiles` | 🚫 **REVOKED** | `SELECT` (If discoverable & unblocked), `UPDATE` (Own row only) | 🟢 Full Access |
| `public.connections` | 🚫 **REVOKED** | `SELECT` (Participant/blocker), `INSERT` (Initiated by self). Direct `UPDATE` revoked! | 🟢 Full Access (Transitions via function) |
| `public.compatibility_results`| 🚫 **REVOKED** | `SELECT` (Participant AND active mutual connection) | 🟢 Full Access |
| `public.conversations` | 🚫 **REVOKED** | `SELECT` (Active direct conversation member only) | 🟢 Full Access |
| `public.messages` | 🚫 **REVOKED** | `SELECT, INSERT` (Active direct conversation member only) | 🟢 Full Access |
| `public.notifications` | 🚫 **REVOKED** | `SELECT, UPDATE` (Strictly `user_id = auth.uid()`) | 🟢 Full Access |
| `public.daily_energies` | 🚫 **REVOKED** | `SELECT` (Strictly `user_id = auth.uid()`) | 🟢 Full Access |

---

## 🔒 Security & Privacy Invariants

These invariants are permanent engineering constraints. Any pull request or refactoring that violates these rules is rejected.

### 1. Raw Birth Data Isolation (`public.birth_data`)
- **Invariant:** User-owned birth parameters (`birth_date`, `birth_time`, `birth_timezone`, `latitude`, `longitude`, `place_label`) are strictly owner-only.
- **Enforcement:** PostgreSQL RLS policy `birth_data_select_own` evaluates `user_id = auth.uid()`.
- **API Boundary:** Raw birth data is never exposed in profile responses, discovery cards, previews, compatibility responses, logs, or client-facing DTOs.

### 2. Private Astronomical Calculations (`public.astro_private`)
- **Invariant:** Server-calculated celestial longitudes, exact house cusps, and retrograde speeds are internal intellectual property and raw intelligence data.
- **Enforcement:** Migration 017 explicitly executes:
  ```sql
  REVOKE ALL ON public.astro_private FROM authenticated, anon, public;
  ```
  Any attempt by a client or standard database role to query `astro_private` raises an immediate `InsufficientPrivilege` PostgreSQL error.

### 3. Safe Profile Derivation (6 Core Planets)
- **Invariant:** Other users and discovery cards only receive safe, non-inverting derived profiles ([`SafeDerivedAstrologyResponse`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/frontend/src/core/api/types.ts#L35)).
- **Planetary Protection:** All 6 core personality planets (**Sun**, **Moon**, **Ascendant**, **Mercury**, **Venus**, **Mars**) expose only their categorical zodiac sign (e.g. `Aries`, `Scorpio`) and dominant element/modality. Raw numerical degrees are never serialized to the client.

### 4. Elimination of Existence Oracles (Block & Privacy Semantics)
- **Invariant:** Blocking or hiding must never leak the target's existence through differential error codes.
- **Enforcement:** If User A blocks User B, or User B is not discoverable:
  - Profiles resolve as **HTTP 404** (`PrivacySafeNotFoundException`).
  - Safe astrology placement endpoints resolve as **HTTP 404**.
  - US / Compare previews resolve as **HTTP 404**.
  - Discovery feeds exclude the user entirely.
  - Chat message attempts resolve as **HTTP 404**.
  - The API **never** returns HTTP 403 Forbidden or existence confirmation for hidden/blocked entities.

### 5. Viewer Identity & Impersonation Protection
- **Invariant:** An authenticated caller can never calculate comparisons or discover profiles under another user's identity.
- **Enforcement:** Routes accepting a viewer/source ID (such as `/v1/interpretations/discovery-people` and `/v1/interpretations/compare-preview`) strictly bind and assert:
  ```python
  if payload.source_user_id is not None and payload.source_user_id != current_user.id:
      raise ForbiddenException(
          message="Cannot request comparison preview as another user.",
          error_code="forbidden_viewer_impersonation",
      )
  ```

### 6. Editorial Asset Protection (Content V2)
- **Invariant:** Editorial metadata (`internal_notes`, `author`, `experiment_id`, `weight`) is confidential.
- **Enforcement:** Endpoint `/v1/interpretations/{id}/assets` dynamically inspects caller roles. For general users, internal editorial metadata is stripped before response serialization. Only users with `copywriter` or `admin` roles can inspect authoring notes.

### 7. Developer Debug Isolation (`/v1/astrology/debug/*`)
- **Invariant:** Developer inspection tools and debug routes must be completely unreachable in production.
- **Enforcement:** Endpoints in `backend/app/astrology/debug.py` check `settings.ENV == "production"` and immediately abort with HTTP 403 Forbidden. Furthermore, debug endpoints are 100% read-only and never trigger mutating auto-recalculations.

---

## ⚙️ Procedural Hardening & Function Security

To prevent search path hijacking and privilege escalation in PostgreSQL functions:
- All database helper functions (`has_active_connection`, `is_user_blocked`, `is_active_direct_conversation`, `can_view_safe_astro`) are defined with:
  ```sql
  SECURITY DEFINER
  SET search_path = public, pg_temp
  ```
- Public execution is revoked:
  ```sql
  REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA public FROM public;
  GRANT EXECUTE ON FUNCTION ... TO authenticated, service_role;
  ```

---

## 🧪 Automated Security Testing & Verification

Security policies are tested continuously in the automated test suite (`193 passed tests`):

1. **Database RLS & Isolation Suite ([`tests/database/test_database_security.py`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/tests/database/test_database_security.py)):**
   - Verifies that User A cannot select, insert, or update User B's `public.birth_data`.
   - Confirms that direct `SELECT` on `public.astro_private` from authenticated client roles fails with `InsufficientPrivilege`.
   - Validates that blocking masks profiles, compatibility records, and direct messages as 404s.
   - Tests that canonical connections cannot be modified by arbitrary SQL updates.

2. **JWT & Auth Verification Suite ([`tests/backend/test_jwt_verification.py`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/tests/backend/test_jwt_verification.py)):**
   - Asserts asymmetric JWKS key fetching in production.
   - Verifies that HS256 tokens are rejected in production mode.
   - Verifies expiration, invalid signature, and malformed header rejections.

---

## 🚨 Reporting a Vulnerability

We appreciate the efforts of security researchers in keeping JESTER safe. If you discover a security vulnerability or privacy leak, please disclose it responsibly:

1. **Do NOT open a public GitHub issue.**
2. **Email your report directly to:** `security@jester.app` (or contact the repository maintainers via private communication).
3. **Include:**
   - Description of the vulnerability and potential impact.
   - Step-by-step reproduction steps or proof-of-concept payload.
   - Any proposed mitigations or fixes.

### Our Commitment:
- **Initial Response:** Within 48 hours of report receipt.
- **Triage & Assessment:** We will keep you updated as the issue is investigated and patched.
- **Safe Harbor:** We will not pursue legal action against researchers who report vulnerabilities in good faith and adhere to responsible disclosure standards.
