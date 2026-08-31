# Jester — Security & Privacy Architecture

## 🔒 Security Model Overview

Jester uses a multi-layered security model combining **FastAPI JWT Authentication**, **PostgreSQL Role-Based Grants**, and **Database Row-Level Security (RLS)**.

---

## 🔑 Authentication & Token Validation (`backend/app/auth/`)

1. **Bearer Token Extraction**:
   - `get_token_from_header` extracts the `Authorization: Bearer <token>` header.
2. **Dual-Mode JWT Verification (`backend/app/auth/jwt.py`)**:
   - **Production Mode (`ENV=production`)**: Strictly requires asymmetric signing algorithms (`RS256`, `ES256`, `EdDSA`). Public keys are fetched dynamically from the Supabase JWKS endpoint (`SUPABASE_JWKS_URL`) via `PyJWKClient`.
     - *Security Invariant*: If an asymmetric token fails JWKS resolution, it **never** falls back to HS256. If a token specifies `alg=HS256` in production, it is rejected immediately.
   - **Development / Test Mode (`ENV=development` / `ENV=test`)**: Symmetric `HS256` signatures are supported using `SUPABASE_JWT_SECRET` only if `alg=HS256` is declared in the header.
3. **Claims & Subject Validation**:
   - Decodes `sub` claim and verifies it is a valid UUID (`user_id`).
   - Returns `AuthenticatedUser(id=user_uuid, email=..., role=...)`.

---

## 🛡️ Database Security & Role Privileges

PostgreSQL roles operate on a principle of least privilege:

```text
                        ┌───────────────────────────────┐
                        │      PostgreSQL Database      │
                        └───────────────┬───────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
     ┌──────────────┐           ┌──────────────┐           ┌──────────────┐
     │     anon     │           │ authenticated│           │ service_role │
     └──────┬───────┘           └──────┬───────┘           └──────┬───────┘
            │                          │                          │
   REVOKE ALL ON ALL          RLS Enforced Access        Bypasses RLS Policies
   Tables & Routines          (Profiles, Safe Astro)     Full System Privileges
```

### Privileges Matrix by Database Role:

| Table / Feature | `anon` Role | `authenticated` Role | `service_role` (Backend) |
| :--- | :--- | :--- | :--- |
| `public.profiles` | 🚫 No Access | `SELECT` (if discoverable & unblocked), `INSERT, UPDATE` (own row) | 🟢 Full Access |
| `public.birth_data` | 🚫 No Access | `SELECT, INSERT, UPDATE` (Strictly `user_id = auth.uid()`) | 🟢 Full Access |
| `public.astro_private` | 🚫 **REVOKED** | 🚫 **REVOKED** (`REVOKE ALL ON public.astro_private`) | 🟢 Full Access |
| `public.astro_safe_profile` | 🚫 No Access | `SELECT` (own profile OR discoverable/unblocked target) | 🟢 Full Access |
| `public.connections` | 🚫 No Access | `SELECT` (participant/blocker), `INSERT` (initiated_by = self). `UPDATE` REVOKED! | 🟢 Full Access |
| `public.compatibility_results` | 🚫 No Access | `SELECT` (participant AND active connection) | 🟢 Full Access |
| `public.conversations` | 🚫 No Access | `SELECT` (active direct conversation member) | 🟢 Full Access |
| `public.messages` | 🚫 No Access | `SELECT, INSERT` (active direct conversation member) | 🟢 Full Access |
| `public.notifications` | 🚫 No Access | `SELECT, UPDATE` (`user_id = auth.uid()`) | 🟢 Full Access |

---

## 🔍 Detailed Data Access Boundary Audit

### 1. Birth Data Boundary (`public.birth_data`)
- **Can User A read User B's birth date, time, latitude, or longitude?**
  - **NO**. RLS policy `birth_data_select_own` evaluates `user_id = auth.uid()`.
  - Application code in `backend/app/astrology/natal.py` only fetches birth data for `current_user.id`.

### 2. Astro Private Boundary (`public.astro_private`)
- **Can User A or client applications query exact server-calculated planet longitudes?**
  - **NO**. Migration 017 explicitly executes `REVOKE ALL ON public.astro_private FROM authenticated, anon, public;`. Attempting to query `astro_private` via client JWT triggers PostgreSQL `InsufficientPrivilege` error.

### 3. Safe Profile Boundary (`public.astro_safe_profile`)
- **What is visible to other users?**
  - Only derived signs (`sun_sign`, `moon_sign`, `ascendant_sign`), `element_primary`, and `modality_primary`.
  - Access is governed by RLS policy `astro_safe_profile_select` which checks `is_discoverable = true` and `NOT is_user_blocked(auth.uid(), target_id)`.

### 4. Block Semantics & Mutual Hiding
- **What happens when User A blocks User B?**
  - `public.is_user_blocked(user_a, user_b)` returns `true`.
  - User A and User B can no longer see each other's `profiles` or `astro_safe_profile`.
  - Both users immediately lose access to existing `compatibility_results`.
  - Both users immediately lose access to direct chat `conversations` and `messages` via `is_active_direct_conversation`.
  - API endpoints return HTTP 404 (`PrivacySafeNotFoundException`) to prevent disclosure of block existence.

### 5. Function Security Hardening (`016_helper_functions.sql`)
- All security-definer helper functions (`has_active_connection`, `is_user_blocked`, `is_active_direct_conversation`) use:
  ```sql
  SECURITY DEFINER
  SET search_path = public, pg_temp
  ```
- Public execution is revoked: `REVOKE EXECUTE ON FUNCTION ... FROM public;` and granted strictly to `authenticated, service_role`.
