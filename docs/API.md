# Jester — API Specification

## 📡 Base URLs & Versioning

- **API Base Prefix**: `/v1`
- **Current Active Version**: `v1`
- **System Health Endpoints**: `/healthz`, `/v1/health`

---

## 🔐 Authentication & Global Security Headers

All protected endpoints require an `Authorization` header containing a valid Supabase JWT Bearer token:
```http
Authorization: Bearer <supabase_jwt_token>
```

---

## 🗺️ Complete Endpoints Directory

### System & Health

#### 1. Liveness Check — `GET /healthz`
- **Auth**: Public
- **Response 200**: `{"status": "ok"}`

#### 2. Service Health & DB Connectivity — `GET /v1/health`
- **Auth**: Public
- **Response 200**: `{"status": "healthy", "environment": "development", "database": "connected"}`
- **Response 503**: `{"status": "degraded", "environment": "development", "database": "disconnected"}`

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
- **Response 200**: `StructuredCompatibilityResponse(id: UUID, target_user_id: UUID, score: float, dimensions: dict[str, float], signals: list[dict], interpretation: ResolvedInterpretation | None, best_topics: list[str], conversation_starters: list[str], data_quality: dict, engine_version: str, calculated_at: datetime)`
- **Errors**: `403 ForbiddenException` if active accepted connection does not exist. `404 PrivacySafeNotFoundException` if blocked.
- *Implementation & Product Note*: Computed by deterministic Synastry V1 engine (`synastry-v1.0.0`) using exact astronomical longitudes and cached per canonical user pair. Enriched with JESTER Voice interpretations: `interpretation` provides the primary relationship insight, and each entry in `signals` is enriched with its resolved interpretation.

#### 13. Why This Person — `GET /v1/people/{target_user_id}/why`
- **Auth**: Bearer JWT
- **Response 200**: Alias for `POST /v1/compare`. Explains interpersonal connection dynamics, relationship insights, and conversation bridges.

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

---

### Interpretation & JESTER Voice Content Layer (Content Architecture V2)

#### 16. List All Interpretations — `GET /v1/interpretations`
- **Auth**: Bearer JWT
- **Response 200**: `list[ContentRecord]`
- **Description**: Returns all registered interpretation entries across categories with both AI draft and copywriter final states.

#### 17. Get Interpretation Details — `GET /v1/interpretations/{interpretation_id}`
- **Auth**: Bearer JWT
- **Response 200**: `{"contract": InterpretationContract, "resolved": ResolvedInterpretation}`
- **Errors**: `404 Not Found` if interpretation ID is not registered.

#### 18. List Interpretation Assets — `GET /v1/interpretations/{interpretation_id}/assets`
- **Auth**: Bearer JWT
- **Query Params**: `locale?: str, context?: str, tone?: str, status?: str, include_archived: bool = false`
- **Response 200**: `list[ContentAsset]`
- **Description**: Lists all active copy assets associated with a semantic interpretation contract. Internal editorial metadata (notes, author) is sanitized for regular users.

#### 19. Create Content Asset — `POST /v1/interpretations/{interpretation_id}/assets`
- **Auth**: Bearer JWT (Roles: `copywriter`, `admin`, or `service_role`)
- **Body**: `ContentAssetCreatePayload(locale, context, tone, text, status?, priority?, variant_key?, author?, tags?, internal_notes?, experiment_id?, weight?)`
- **Response 201**: `ContentAsset`
- **Errors**: `403 Forbidden` if user lacks editorial privileges; `404 Not Found` if contract missing.

#### 20. Get Content Asset by ID — `GET /v1/content/assets/{asset_id}`
- **Auth**: Bearer JWT
- **Response 200**: `ContentAsset`
- **Errors**: `404 PrivacySafeNotFoundException` if asset missing. Internal notes stripped for standard users.

#### 21. Update Content Asset — `PATCH /v1/content/assets/{asset_id}`
- **Auth**: Bearer JWT (Roles: `copywriter`, `admin`, or `service_role`)
- **Body**: `ContentAssetUpdatePayload(text?, locale?, context?, tone?, persona?, status?, priority?, variant_key?, tags?, internal_notes?, experiment_id?, weight?, archived?)`
- **Response 200**: `ContentAsset`
- **Errors**: `403 Forbidden` if unauthorized.

#### 22. Approve Content Asset — `POST /v1/content/assets/{asset_id}/approve`
- **Auth**: Bearer JWT (Roles: `copywriter`, `admin`, or `service_role`)
- **Response 200**: `ContentAsset`
- **Description**: Promotes asset to `status="approved"`. Takes immediate precedence over AI drafts during resolution without touching calculations.

#### 23. Archive Content Asset — `POST /v1/content/assets/{asset_id}/archive`
- **Auth**: Bearer JWT (Roles: `copywriter`, `admin`, or `service_role`)
- **Response 200**: `ContentAsset`
- **Description**: Soft-archives asset, permanently excluding it from user resolution.

#### 24. Content Inventory Matrix — `GET /v1/content/inventory`
- **Auth**: Bearer JWT (Roles: `copywriter`, `admin`, or `service_role`)
- **Response 200**: `list[ContentInventoryItem]`
- **Description**: Returns editorial inventory across all 30 contracts, reporting total assets, approved assets, AI drafts, tones, locales, and status.

#### 25. Update Approved Copy (Legacy V1) — `PATCH /v1/interpretations/{interpretation_id}/copy`
- **Auth**: Bearer JWT (Roles: `copywriter`, `admin`, or `service_role`)
- **Body**: `ContentUpdatePayload(text: str, status: "approved"|"not_reviewed", author?: str)`
- **Response 200**: `ContentRecord`

#### 26. Reset Interpretation to Draft (Legacy V1) — `POST /v1/interpretations/{interpretation_id}/reset`
- **Auth**: Bearer JWT (Roles: `copywriter`, `admin`, or `service_role`)
- **Response 200**: `ContentRecord`

#### 27. Resolve Deterministic Signal — `POST /v1/interpretations/resolve-signal`
- **Auth**: Bearer JWT
- **Body**: `dict` (signal object, e.g. `{"type": "venus_conjunction_mars", "strength": "strong"}`)
- **Query Params**: `context?: str, locale: str = "ka", tone?: str, persona: str = "jester", variant_key?: str, seed?: str`
- **Response 200**: `{"signal": dict, "interpretation": ResolvedInterpretation}`
- **Errors**: `404 Not Found` if signal does not map to any recognized interpretation.

#### 28. Build Deep Analysis — `POST /v1/interpretations/deep-analysis`
- **Auth**: Bearer JWT
- **Body**: `{"score": float, "signals": list[dict], "confidence": float, "context"?: str, "locale"?: str, "tone"?: str, "seed"?: str}`
- **Response 200**: `DeepAnalysisPayload(overall_score: float, primary_interpretation: ResolvedInterpretation, blocks: list[DeepAnalysisBlock], data_confidence: float)`
- **Description**: Compiles verified signals into structured thematic narrative blocks grounded in aspect evidence trace.


