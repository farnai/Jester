# Jester — API Documentation & Contract Specifications

## 🌐 API Overview

Jester exposes a RESTful HTTP API built with FastAPI.
- Base Prefix: `/v1` (except root health endpoint `/healthz`).
- Authentication: `Authorization: Bearer <token>` required for all `/v1/*` routes except `/v1/health`.
- Interactive Documentation: Swagger UI at `/docs`, ReDoc at `/redoc`, OpenAPI JSON at `/openapi.json`.

---

## 📌 Endpoint Reference Index

| Method | Path | Auth Required | Implementation File | Test File |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/healthz` | ❌ No | `backend/app/api/health.py` | `tests/backend/test_health.py` |
| `GET` | `/v1/health` | ❌ No | `backend/app/api/health.py` | `tests/backend/test_health.py` |
| `GET` | `/v1/users/me` | ✅ Yes | `backend/app/users/router.py` | `tests/backend/test_jwt_verification.py` |
| `GET` | `/v1/profiles/me` | ✅ Yes | `backend/app/profiles/router.py` | `tests/backend/test_api_endpoints.py` |
| `PATCH`| `/v1/profiles/me` | ✅ Yes | `backend/app/profiles/router.py` | `tests/backend/test_api_endpoints.py` |
| `GET` | `/v1/profiles/{id}` | ✅ Yes | `backend/app/profiles/router.py` | `tests/database/test_database_security.py` |
| `POST` | `/v1/astrology/profile/recalculate` | ✅ Yes | `backend/app/astrology/router.py` | `tests/astrology/test_astrology_api.py` |
| `GET` | `/v1/astrology/profile/safe-astro` | ✅ Yes | `backend/app/astrology/router.py` | `tests/astrology/test_astrology_api.py` |
| `GET` | `/v1/astrology/people/{id}/safe-astro` | ✅ Yes | `backend/app/astrology/router.py` | `tests/astrology/test_astrology_api.py` |
| `GET` | `/v1/connections` | ✅ Yes | `backend/app/connections/router.py` | `tests/database/test_database_security.py` |
| `POST` | `/v1/connections` | ✅ Yes | `backend/app/connections/router.py` | `tests/database/test_database_security.py` |
| `POST` | `/v1/connections/{id}/transition` | ✅ Yes | `backend/app/connections/router.py` | `tests/database/test_database_security.py` |
| `POST` | `/v1/compare` | ✅ Yes | `backend/app/comparisons/router.py` | `tests/database/test_database_security.py` |
| `GET` | `/v1/people/{id}/why` | ✅ Yes | `backend/app/comparisons/router.py` | `tests/database/test_database_security.py` |
| `POST` | `/v1/conversations` | ✅ Yes | `backend/app/conversations/router.py` | `tests/database/test_database_security.py` |
| `GET` | `/v1/conversations/{id}/messages` | ✅ Yes | `backend/app/conversations/router.py` | `tests/database/test_database_security.py` |
| `POST` | `/v1/conversations/{id}/messages` | ✅ Yes | `backend/app/conversations/router.py` | `tests/database/test_database_security.py` |
| `GET` | `/v1/notifications` | ✅ Yes | `backend/app/notifications/router.py` | `tests/database/test_database_security.py` |
| `PATCH`| `/v1/notifications/{id}/read` | ✅ Yes | `backend/app/notifications/router.py` | `tests/database/test_database_security.py` |

---

## 📖 Detailed Endpoint Specifications

### System & Users

#### 1. System Health — `GET /healthz`
- **Auth**: None
- **Response 200**: `{"status": "ok"}`

#### 2. Get Account Info — `GET /v1/users/me`
- **Auth**: Bearer JWT
- **Response 200**: `UserResponse(id: UUID, email: str, role: str)`

---

### Profiles

#### 3. Get Own Profile — `GET /v1/profiles/me`
- **Auth**: Bearer JWT
- **Response 200**: `ProfileResponse(id: UUID, display_name: str, avatar_url: str, bio: str, city: str, occupation: str, timezone: str, is_discoverable: bool, created_at: datetime, updated_at: datetime)`
- **Errors**: `404 PrivacySafeNotFoundException` if profile missing.

#### 4. Update Own Profile — `PATCH /v1/profiles/me`
- **Auth**: Bearer JWT
- **Body**: `ProfileUpdate(display_name?, avatar_url?, bio?, city?, occupation?, timezone?, is_discoverable?)`
- **Response 200**: Updated `ProfileResponse`

#### 5. Get Target Profile — `GET /v1/profiles/{profile_id}`
- **Auth**: Bearer JWT
- **Response 200**: `ProfileResponse`
- **Errors**: `404 PrivacySafeNotFoundException` if non-discoverable or user is blocked.

---

### Astrology

#### 6. Recalculate Astrology — `POST /v1/astrology/profile/recalculate`
- **Auth**: Bearer JWT
- **Response 200**: `SafeDerivedAstrologyResponse(user_id: UUID, sun_sign: str, moon_sign: str, ascendant_sign: str|None, element_primary: str, modality_primary: str, source_birth_data_version: int, engine_version: str, updated_at: datetime)`
- **Errors**: `404 birth_data_not_found` if `public.birth_data` row missing; `400 placidus_polar_error` if latitude $> 66.5^\circ$.

#### 7. Get Own Safe Astrology — `GET /v1/astrology/profile/safe-astro`
- **Auth**: Bearer JWT
- **Response 200**: `SafeDerivedAstrologyResponse` (Auto-recalculates if birth_data exists).

#### 8. Get Person Safe Astrology — `GET /v1/astrology/people/{target_user_id}/safe-astro`
- **Auth**: Bearer JWT
- **Response 200**: `SafeDerivedAstrologyResponse`
- **Errors**: `404 PrivacySafeNotFoundException` if target non-discoverable or blocked.

---

### Connections & Compatibility

#### 9. List Connections — `GET /v1/connections`
- **Auth**: Bearer JWT
- **Response 200**: `list[ConnectionResponse]`

#### 10. Send Connection Request — `POST /v1/connections`
- **Auth**: Bearer JWT
- **Body**: `ConnectionCreate(target_user_id: UUID)`
- **Response 201**: `ConnectionResponse`

#### 11. Transition Connection State — `POST /v1/connections/{connection_id}/transition`
- **Auth**: Bearer JWT
- **Body**: `ConnectionTransition(action: Literal["accept", "decline", "block", "unblock", "remove"])`
- **Response 200**: `ConnectionResponse`

#### 12. Compare Users / Calculate Compatibility — `POST /v1/compare`
- **Auth**: Bearer JWT
- **Body**: `CompareRequest(target_user_id: UUID)`
- **Response 200**: `StructuredCompatibilityResponse(id: UUID, target_user_id: UUID, score: float, signals: list[dict], best_topics: list[str], conversation_starters: list[str], engine_version: str, calculated_at: datetime)`
- **Errors**: `403 ForbiddenException` if active accepted connection does not exist.
- *Implementation Note*: Returns baseline hardcoded score `82.5` until full synastry engine is built.

#### 13. Why This Person — `GET /v1/people/{target_user_id}/why`
- **Auth**: Bearer JWT
- **Response 200**: Alias for `POST /v1/compare`.

---

### Conversations & Messages

#### 14. Create / Get Direct Conversation — `POST /v1/conversations`
- **Auth**: Bearer JWT
- **Body**: `DirectConversationCreate(target_user_id: UUID)`
- **Response 201**: `ConversationResponse`
- **Errors**: `403 Forbidden` if active connection does not exist.

#### 15. List Messages — `GET /v1/conversations/{conversation_id}/messages`
- **Auth**: Bearer JWT
- **Response 200**: `list[MessageResponse]`
- **Errors**: `404 PrivacySafeNotFoundException` if not member or blocked.

#### 16. Send Message — `POST /v1/conversations/{conversation_id}/messages`
- **Auth**: Bearer JWT
- **Body**: `MessageCreate(body: str)`
- **Response 201**: `MessageResponse`
