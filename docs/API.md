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
- **Response 200**: `ProfileResponse(id: UUID, display_name: str, avatar_url: str, bio: str, city: str, location: LocationDTO|None, origin: OriginDTO|None, lifestyle: LifestyleDTO|None, values: list[ValueDTO], social_behavior: SocialBehaviorDTO|None, communication: CommunicationDTO|None, intent: IntentDTO|None, prompts: list[UserPromptDTO], occupation: str, timezone: str, is_discoverable: bool, created_at: datetime, updated_at: datetime)`
  - `location`: `{ city: "Tbilisi", country: "Georgia", country_code: "GE" }`
  - `origin`: `{ city: "Kvareli", country: "Georgia", country_code: "GE" }` (or `null` if hidden or unconfigured)
  - `lifestyle`: `{ daily_rhythm, activity_pace, work_style, pet_status, drinking, smoking }` (filtered by visibility flags)
  - `values`: `[ { slug: "curiosity", name: "Curiosity", is_core: true, badge_icon: "compass" }, ... ]`
  - `social_behavior`: `{ group_preference: "one_on_one", social_battery: "recharge_solo", warmup_style: "observer_first", planning_style: "spontaneous", comfort_zone: "cozy_intimate" }` (filtered by visibility flags)
  - `communication`: `{ conversation_depth: "deep_meaningful", conversation_role: "idea_conceptual", messaging_medium: "voice_notes_welcome", response_pace: "unhurried_thoughtful" }` (filtered by visibility flags)
  - `intent`: `{ primary: { slug: "friendship", name: "New Friends", icon: "users" }, secondaries: [ { slug: "activity_partner", name: "Activity Partner", icon: "compass" } ], visibility: "public" }`
  - `prompts`: `[ { id: UUID, template_slug: "unnecessary_hill", prompt_text: "A completely unnecessary hill I'll die on...", answer: "Pineapple on pizza is culinary innovation.", sort_order: 1, visibility: "public" } ]` (max 3 prompts)
  - `city`: Kept as backward-compatible string alias.
- **Errors**: `404 PrivacySafeNotFoundException` if profile missing.

#### 4. Update Own Profile — `PATCH /v1/profiles/me`
- **Auth**: Bearer JWT
- **Body**: `ProfileUpdate(display_name?, avatar_url?, bio?, city?, current_city_id?: UUID, hometown_city_id?: UUID, hometown_visible?: bool, occupation?, timezone?, is_discoverable?)`
- **Response 200**: Updated `ProfileResponse`

#### 5. Get Target Profile — `GET /v1/profiles/{profile_id}`
- **Auth**: Bearer JWT
- **Response 200**: `ProfileResponse` (`origin` serialized only if target user has `hometown_visible = true`; `lifestyle` filtered by target's visibility flags; coordinates NEVER serialized).
- **Errors**: `404 PrivacySafeNotFoundException` if non-discoverable or user is blocked.

---

### Astrology (Platform Architecture Spec: [`docs/ASTROLOGY_INTEGRATION_SYSTEM_V1_SPEC.md`](ASTROLOGY_INTEGRATION_SYSTEM_V1_SPEC.md))

#### 6. Atomic Birth Data Onboarding — `POST /v1/astrology/birth-data`
- **Auth**: Bearer JWT
- **Body**: `BirthDataRequest(birth_date: date, birth_time: time|None, birth_time_precision: Literal["exact", "approximate", "unknown"], birth_timezone: str, latitude: float|None, longitude: float|None, place_label: str|None)`
- **Response 200**: `SafeDerivedAstrologyResponse(user_id: UUID, sun_sign: str, moon_sign: str, ascendant_sign: str|None, mercury_sign: str|None, venus_sign: str|None, mars_sign: str|None, element_primary: str, modality_primary: str, source_birth_data_version: int, engine_version: str, updated_at: datetime)`
- **Errors**: `400 placidus_polar_error` if latitude $> 66.5^\circ$; `400 invalid_timezone` if not valid IANA timezone; `400 invalid_coordinates` if out of range [-90, 90] / [-180, 180]; `400 invalid_birth_date` if future or prior to 1900.
- **Behavior**: Validates inputs and calculates Swiss Ephemeris in memory BEFORE transaction. Then executes an atomic transaction writing `public.birth_data`, `public.astro_private` (server-only), and `public.astro_safe_profile`. If calculation fails, 0 database writes occur.

#### 7. Recalculate Astrology — `POST /v1/astrology/profile/recalculate`
- **Auth**: Bearer JWT
- **Response 200**: `SafeDerivedAstrologyResponse(user_id: UUID, sun_sign: str, moon_sign: str, ascendant_sign: str|None, mercury_sign: str|None, venus_sign: str|None, mars_sign: str|None, element_primary: str, modality_primary: str, source_birth_data_version: int, engine_version: str, updated_at: datetime)`
- **Errors**: `404 birth_data_not_found` if `public.birth_data` row missing; `400 placidus_polar_error` if latitude $> 66.5^\circ$.
- **Behavior**: Recalculates natal chart and safe profile from existing stored birth data, synchronizing `astro_private` and `astro_safe_profile`.

#### 8. Get Own Safe Astrology — `GET /v1/astrology/profile/safe-astro`
- **Auth**: Bearer JWT
- **Response 200**: `SafeDerivedAstrologyResponse` (Auto-recalculates if birth_data exists). Returns safe derived signs, element, and modality.

#### 9. Get Person Safe Astrology — `GET /v1/astrology/people/{target_user_id}/safe-astro`
- **Auth**: Bearer JWT
- **Response 200**: `SafeDerivedAstrologyResponse`
- **Errors**: `404 PrivacySafeNotFoundException` if target is non-discoverable or mutually blocked.
- **Privacy Boundary**: Exposes only public safe signs and elements. Coordinates, exact birth time, birth date, and raw degree longitudes are NEVER returned.

#### 9a. Developer Debug Astrology (Non-Production Only) — `GET /astrology/debug/my-astro`
- **Auth**: Bearer JWT
- **Response 200**: Returns full private calculation (`astro_private`) and raw birth parameters (`birth_data`) for caller only.
- **Errors**: `403 ForbiddenException` if `ENV == "production"`. Strictly disabled in production.

---

### Connections & Compatibility

#### 9. List Connections — `GET /v1/connections`
- **Auth**: Bearer JWT
- **Response 200**: `list[ConnectionResponse]`

#### 10. Send Connection Request — `POST /v1/connections`
- **Auth**: Bearer JWT
- **Body**: `ConnectionCreate(target_user_id: UUID, connection_reason?: str, prompt_reference_id?: UUID, invitation_note?: str)`
  - `connection_reason`: Optional single-tap intent hook (`"shared_curiosity"`, `"creative_collaboration"`, `"philosophical_resonance"`, `"humor_banter"`, `"meaningful_chat"`, `"coffee_walk"`).
  - `prompt_reference_id`: Optional UUID of target's answered prompt if initiating via profile prompt quote.
  - `invitation_note`: Optional personal note, max 250 characters. Stripped of raw contact handles/links.
- **Response 201**: `ConnectionResponse(id: UUID, user_a_id: UUID, user_b_id: UUID, status: str, initiated_by: UUID, connection_reason: str|None, prompt_reference_id: UUID|None, invitation_note: str|None, created_at: datetime, updated_at: datetime)`
- **Errors**: `400 invalid_pair` (connecting with self); `400 invalid_invitation_note` (>250 chars); `403 forbidden` (blocked or daily cap exceeded: 15/day); `404 PrivacySafeNotFoundException` (target does not exist or blocked).

#### 11. Transition Connection State — `POST /v1/connections/{connection_id}/transition`
- **Auth**: Bearer JWT
- **Body**: `ConnectionTransition(action: Literal["accept", "decline", "block", "unblock", "remove"])`
- **Response 200**: `ConnectionResponse`
- **Actions**:
  - `"accept"`: Target accepts pending request. Transitions to `accepted`. Automatically triggers inaugural message seeding in direct chat thread if `invitation_note` or `prompt_reference_id` was provided.
  - `"decline"`: Target declines pending request. Transitions to `declined`. Silent to sender (zero decline push notification to preserve dignity).
  - `"remove"` (Disconnect): Either user disconnects. Transitions to `removed`. Locks direct chat history into read-only archive; bars new messages; 48-hour reconnection cooldown; zero notification to counterpart.
  - `"block"`: Immediate personal safety block. Transitions to `blocked`, setting `blocked_by`. Reciprocal HTTP 404 across all endpoints; counterpart immediately disappears.
  - `"unblock"`: Blocker unblocks. Transitions to `removed` (does NOT auto-restore accepted connection).
- **Errors**: `400 invalid_transition`; `403 forbidden` (unauthorized transition); `404 PrivacySafeNotFoundException`.

#### 12. Compare Users / Calculate Compatibility — `POST /v1/compare`
- **Auth**: Bearer JWT
- **Body**: `CompareRequest(target_user_id: UUID)`
- **Response 200**: `StructuredCompatibilityResponse(id: UUID, target_user_id: UUID, score: float, dimensions: dict[str, float], signals: list[dict], interpretation: ResolvedInterpretation | None, best_topics: list[str], conversation_starters: list[str], data_quality: dict, deep_analysis: DeepAnalysisPayload | None, engine_version: str, calculated_at: datetime)`
- **Errors**: `403 ForbiddenException` if active accepted connection does not exist. `404 PrivacySafeNotFoundException` if blocked.
- *Implementation & Product Note*: Computed by deterministic Synastry V1 engine (`synastry-v1.0.0`) using exact astronomical longitudes and cached per canonical user pair. Relationship dimensions (`emotional_harmony`, `communication`, `attraction`, `growth_long_term`) are persisted to `public.compatibility_results` (Migration 022) and preserved on cache hits. Enriched with JESTER Voice interpretations: `interpretation` provides the primary relationship insight, `signals` are enriched with resolved Georgian copy, and `deep_analysis` provides structured thematic blocks.

#### 13. Why This Person — `GET /v1/people/{target_user_id}/why`
- **Auth**: Bearer JWT
- **Response 200**: Alias for `POST /v1/compare`. Explains interpersonal connection dynamics, relationship insights, and conversation bridges.

---

### Conversations & Messages (Platform Architecture Spec: [`docs/CONNECTION_MESSAGING_SYSTEM_V1_SPEC.md`](CONNECTION_MESSAGING_SYSTEM_V1_SPEC.md))

#### 14. Create / Get Direct Conversation — `POST /v1/conversations`
- **Auth**: Bearer JWT
- **Body**: `DirectConversationCreate(target_user_id: UUID)`
- **Response 201**: `ConversationResponse(id: UUID, conversation_type: str, created_by: UUID, created_at: datetime, updated_at: datetime, other_member_id: UUID)`
- **Errors**: `403 Forbidden` if active `accepted` connection does not exist.

#### 15. List My Conversations — `GET /v1/conversations`
- **Auth**: Bearer JWT
- **Response 200**: `list[ConversationInboxResponse]`, where each item contains `id`, `other_member_id`, `last_message` (`MessageResponse | null`), `unread_count`, and `updated_at`.
- **Visibility**: Returns only caller's active direct conversations where `public.is_active_direct_conversation(c.id, user_id)` is true. Conversations that are blocked, removed, or no longer accepted are omitted from active list.
- **Ordering**: Most recent message activity first; conversations without messages fall back to `conversations.updated_at`.
- **Unread Tracking**: Computes `unread_count` via member's `last_read_message_id` pointer against newer messages.

#### 16. Get Conversation Details — `GET /v1/conversations/{conversation_id}`
- **Auth**: Bearer JWT
- **Response 200**: `ConversationResponse`
- **Errors**: `404 PrivacySafeNotFoundException` if conversation does not exist or caller is not an active participant.

#### 17. List Messages — `GET /v1/conversations/{conversation_id}/messages`
- **Auth**: Bearer JWT
- **Response 200**: `list[MessageResponse(id: UUID, conversation_id: UUID, sender_user_id: UUID, body: str, created_at: datetime)]`
- **Ordering**: Chronological ascending by `created_at`.
- **Errors**: `404 PrivacySafeNotFoundException` if not member or blocked.

#### 18. Send Message — `POST /v1/conversations/{conversation_id}/messages`
- **Auth**: Bearer JWT
- **Body**: `MessageCreate(body: str)`
- **Validation**: UTF-8 plain text, 1 to 2,000 characters. Unicode emoji supported. Media attachments barred in V1.
- **Enforcement**: Validates `public.is_active_direct_conversation(conversation_id, current_user.id)`. Fails if disconnected or blocked.
- **Response 201**: `MessageResponse`
- **Errors**: `400 invalid_message_body` (empty or >2,000 chars); `404 PrivacySafeNotFoundException` if conversation inactive, removed, or blocked.

#### 19. Mark Conversation Read — `PATCH /v1/conversations/{conversation_id}/read`
- **Auth**: Bearer JWT
- **Body**: `ReadReceiptUpdate(last_read_message_id: UUID)`
- **Response 200**: `{"status": "ok", "unread_count": 0}`
- **Behavior**: Updates caller's `last_read_message_id` and `last_read_at` in `public.conversation_members`. Anti-surveillance invariant: Does NOT broadcast "Seen at HH:MM" to counterpart.
- **Errors**: `404 PrivacySafeNotFoundException` if not member.

#### 20. Generate Conversation Starters — `POST /v1/conversations/{conversation_id}/starters`
- **Auth**: Bearer JWT
- **Response 200**: `ConversationStartersResponse(starters: list[ConversationStarterDTO], shared_topics: list[str])`
- **Behavior**: Scopes JESTER AI context to caller and recipient's declared public signals (interests, values, prompts, communication rhythm). Produces 3 user-reviewable opening lines. Never auto-sends without explicit user approval.
- **Errors**: `404 PrivacySafeNotFoundException` if not member or disconnected.

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

#### 29. Discovery Feed — `GET /v1/interpretations/discovery-people`
- **Auth**: Bearer JWT (Required). Caller identity is strictly bound to `JWT.sub`.
- **Query Params**: `viewer_id?: UUID` (Optional; if supplied, must strictly match `current_user.id`, otherwise returns `403 Forbidden`).
- **Response 200**: `list[DiscoveryPerson]`
  - `id`: Target user UUID
  - `display_name`: Display name
  - `bio`, `city`, `occupation`, `avatar_url`: Safe profile attributes
  - `astrology`: Safe derived signals (`sun_sign`, `moon_sign`, `ascendant_sign`, `element_primary`, `modality_primary`)
  - `compatibility_score`: Server-calculated Synastry V1 score
  - `hook_observation`: Relationship-level JESTER hook observation (ME → YOU synastry dynamic with fallback to natal hook)
- **Security & Privacy**:
  - Excludes blocked relationships in either direction via `public.is_user_blocked(viewer, candidate)`.
  - Excludes non-discoverable profiles (`is_discoverable = false`).
  - Excludes the authenticated viewer.
  - Rejects cross-user impersonation attempts (`viewer_id != current_user.id`) with `403 Forbidden`.

#### 30. Pre-Connection Relationship Preview — `POST /v1/interpretations/compare-preview`
- **Auth**: Optional / Bearer JWT. When authenticated, viewer identity is strictly derived from `JWT.sub`.
- **Body**: `ComparePreviewRequest(target_user_id: UUID, source_user_id?: UUID, locale: str = "ka", tone?: str)`
- **Response 200**:
  - `source_user_id`: Caller UUID (derived from JWT)
  - `target_user_id`: Target user UUID
  - `score`: Synastry V1 overall compatibility score (0–100)
  - `dimensions`: 4 subscores (`emotional_harmony`, `communication`, `attraction`, `growth_long_term`)
  - `signals`: Array of top relational signals with Georgian resolved copy
  - `interpretation`: Primary relationship insight (title, hook, text, tone)
  - `best_topics`: Suggested discussion topics
  - `conversation_starters`: Contextual conversation icebreakers
  - `data_quality`: Confidence factor, precision, and house/ascendant flags
  - `deep_analysis`: Structured thematic analysis blocks
  - `engine_version`: Engine version string
  - `calculated_at`: ISO timestamp
- **Security & Privacy**:
  - Strictly prevents viewer impersonation: If caller supplies `source_user_id != current_user.id`, returns `403 Forbidden` (`forbidden_viewer_impersonation`).
  - Enforces block checks in either direction: returns `404 PrivacySafeNotFoundException` if blocked.
  - Enforces discoverability: non-discoverable target profiles without an active connection return `404 PrivacySafeNotFoundException`.
  - Never exposes private birth data, coordinates, raw planetary longitudes, or evidence traces.

---

### Interest System & Graph V1 (Planned Specification)

> **Note:** The following endpoints define the API contract for the Interest System V1 architecture specification.

#### 31. List Interest Categories — `GET /v1/interests/categories`
- **Auth**: Public or Bearer JWT
- **Response 200**: `list[InterestCategoryResponse]`
  - `id`: UUID
  - `name`: Category name (e.g. "Creative", "Travel & Exploring")
  - `slug`: Canonical category slug
  - `icon`: Icon identifier
  - `sort_order`: Display sort order

#### 32. Get Onboarding Candidate Pool — `GET /v1/interests/candidate-pool`
- **Auth**: Bearer JWT
- **Response 200**: `InterestCandidatePoolResponse`
  - `items`: Curated pool of ~20 canonical interest items for onboarding
  - `rules`: `{"min_primary": 5, "max_primary": 5, "skippable": true}`

#### 33. Submit Onboarding Interests — `POST /v1/interests/onboarding`
- **Auth**: Bearer JWT
- **Body**: `InterestOnboardingRequest`
  - `primary_interest_ids`: Exactly 5 UUIDs (or empty array if skipped)
  - `signature_interest_id`: Optional UUID (must be one of the 5 primary interests if supplied)
- **Response 200**: `UserInterestsResponse`
  - Returns persisted primary interests and optional signature interest.
- **Errors**: `400 invalid_interest_count` if non-empty and count $\neq$ 5; `400 invalid_signature_interest` if signature interest is not in primary list.

#### 34. Get Own Declared Interests — `GET /v1/interests/me`
- **Auth**: Bearer JWT
- **Response 200**: `UserInterestsResponse`
  - `primary`: List of primary interests (max 5)
  - `signature`: Optional signature interest
  - `secondary`: List of secondary interests added post-onboarding

#### 35. Add Secondary Interest — `POST /v1/interests/secondary`
- **Auth**: Bearer JWT
- **Body**: `AddSecondaryInterestRequest(interest_id: UUID)`
- **Response 201**: `UserInterestItemResponse`

#### 36. Remove Secondary Interest — `DELETE /v1/interests/secondary/{interest_id}`
- **Auth**: Bearer JWT
- **Response 204**: No content

#### 37. Get Person Interests — `GET /v1/interests/people/{target_user_id}`
- **Auth**: Bearer JWT
- **Response 200**: `PersonInterestsResponse`
  - `primary`: Visible primary interests
  - `signature`: Optional signature interest
  - `secondary`: Visible secondary interests
  - `matching_summary`: Relationship matching mode (`shared`, `related`, or `complementary`)
- **Errors**: `404 PrivacySafeNotFoundException` if target is blocked or non-discoverable.
- **Privacy Enforcement**: Internal behavioral affinity scores (`public.user_interest_affinity`) are strictly service-role and never exposed.

---

### Location & Origin System V1 (Planned Specification)

> **Note:** The following endpoints define the API contract for the Location & Origin System V1 architecture specification.

#### 38. Search Canonical Cities — `GET /v1/geo/cities`
- **Auth**: Public or Bearer JWT
- **Query Params**:
  - `query: str` (Minimum 2 characters for autocomplete, e.g. "Tbi", "თბი")
  - `country_code?: str` (Optional ISO filter, e.g. "GE")
  - `limit?: int` (Default 10, max 30)
- **Response 200**: `list[GeoCitySearchResult]`
  - `id`: UUID
  - `name`: Localized city name (e.g. "Tbilisi")
  - `country_name`: Localized country name (e.g. "Georgia")
  - `country_code`: ISO code (e.g. "GE")
  - `slug`: Canonical slug (e.g. "ge-tbilisi")

#### 39. Get Major Onboarding Hubs — `GET /v1/geo/cities/major`
- **Auth**: Public or Bearer JWT
- **Query Params**: `country_code: str = "GE"`
- **Response 200**: `list[GeoCitySearchResult]`
  - Returns curated list of major domestic hubs for 1-tap onboarding chips (e.g. Tbilisi, Batumi, Kutaisi, Rustavi).

#### 40. Update Location Settings — `PATCH /v1/profiles/me/location`
- **Auth**: Bearer JWT
- **Body**: `UpdateLocationRequest`
  - `current_city_id?: UUID`
  - `hometown_city_id?: UUID`
  - `hometown_visible?: bool`
- **Response 200**: `ProfileLocationResponse`
  - `location`: `{ city: "Tbilisi", country: "Georgia", country_code: "GE" }`
  - `origin`: `{ city: "Kvareli", country: "Georgia", country_code: "GE" }` (or `null` if `hometown_visible = false`)
- **Errors**: `400 invalid_city_id` if referenced UUID does not exist in `geo_cities`.

---

### Lifestyle System V1 (Planned Specification)

> **Note:** The following endpoints define the API contract for the Lifestyle System V1 architecture specification.

#### 41. List Canonical Lifestyle Options — `GET /v1/lifestyle/options`
- **Auth**: Public or Bearer JWT
- **Response 200**: `list[LifestyleCategoryWithOptions]`
  - Returns taxonomy categories (`daily_rhythm`, `activity_pace`, `work_style`, `pet_status`, etc.) and their localized options with badge icons.

#### 42. Get Onboarding Lifestyle Snapshot Options — `GET /v1/lifestyle/onboarding-snapshot`
- **Auth**: Bearer JWT
- **Response 200**: `LifestyleOnboardingSnapshotConfig`
  - Returns the 3 curated onboarding questions (Daily Rhythm, Activity Pace, Work Style) with quick-select options and icons.

#### 43. Submit Lifestyle Onboarding — `POST /v1/lifestyle/onboarding`
- **Auth**: Bearer JWT
- **Body**: `LifestyleOnboardingRequest`
  - `daily_rhythm?: str` (e.g. `'night_owl'`, `'early_bird'`, `'flexible_rhythm'`)
  - `activity_pace?: str` (e.g. `'high_velocity'`, `'balanced_pace'`, `'relaxed_pace'`)
  - `work_style?: str` (e.g. `'remote'`, `'hybrid'`, `'on_site'`, `'student'`)
- **Response 200**: `UserLifestyleResponse`
- **Errors**: `400 invalid_option_slug` if an unrecognized slug is submitted.
- **Behavior**: All fields are optional (payload can be empty to represent a skipped step).

#### 44. Get Own Lifestyle Profile — `GET /v1/lifestyle/me`
- **Auth**: Bearer JWT
- **Response 200**: `UserLifestyleResponse`
  - Returns all declared lifestyle attributes, custom visibility flags, and metadata.

#### 45. Update Own Lifestyle & Visibility — `PATCH /v1/lifestyle/me`
- **Auth**: Bearer JWT
- **Body**: `UpdateLifestyleRequest`
  - `daily_rhythm?: str|None`
  - `activity_pace?: str|None`
  - `work_style?: str|None`
  - `social_cadence?: str|None`
  - `pet_status?: str|None`
  - `living_situation?: str|None`
  - `drinking_habit?: str|None`
  - `smoking_habit?: str|None`
  - `visibility_flags?: dict[str, bool]` (e.g. `{"living_situation": false, "drinking": true}`)
- **Response 200**: Updated `UserLifestyleResponse`

#### 46. Get Target User Lifestyle — `GET /v1/lifestyle/people/{target_user_id}`
- **Auth**: Bearer JWT
- **Response 200**: `PublicLifestyleResponse`
  - Returns target user's public lifestyle attributes filtered strictly through target's `visibility_flags`.
- **Errors**: `404 PrivacySafeNotFoundException` if target is blocked or non-discoverable.

---

### Values System V1 (Planned Specification)

> **Note:** The following endpoints define the API contract for the Values System V1 architecture specification.

#### 47. List Canonical Values Taxonomy — `GET /v1/values`
- **Auth**: Public or Bearer JWT
- **Response 200**: `list[ValuesCategoryWithOptions]`
  - Returns the 5 thematic clusters (`personal_direction`, `intellectual_creative`, `relational_ethical`, `life_grounding`, `inner_spirit`) with their 18 canonical values, localized definitions, and badge icons.

#### 48. Get Values Onboarding Candidate Pool — `GET /v1/values/candidate-pool`
- **Auth**: Bearer JWT
- **Response 200**: `ValuesCandidatePoolResponse`
  - Returns the 18 canonical values formatted for rapid interactive chip selection (with selection constraints: `min: 3`, `max: 5`, `core_allowed: 1`, `is_skippable: true`).

#### 49. Submit Values Onboarding — `POST /v1/values/onboarding`
- **Auth**: Bearer JWT
- **Body**: `ValuesOnboardingRequest`
  - `selected_value_slugs: list[str]` (Must contain between 3 and 5 valid slugs, or empty list if skipped)
  - `core_value_slug?: str|None` (Optional single True North value, must be one of `selected_value_slugs`)
- **Response 200**: `UserValuesResponse`
- **Errors**:
  - `400 invalid_selection_count` if selected count is not between 3 and 5 (unless empty array when skipping).
  - `400 invalid_core_value` if core value is not in selected list.
  - `400 invalid_value_slug` if slug is not recognized.

#### 50. Get Own Values Profile — `GET /v1/values/me`
- **Auth**: Bearer JWT
- **Response 200**: `UserValuesResponse`
  - Returns user's selected values list (`slug`, `name`, `definition`, `badge_icon`, `is_core`, `sort_order`).

#### 51. Update Own Values — `PUT /v1/values/me`
- **Auth**: Bearer JWT
- **Body**: `UpdateUserValuesRequest`
  - `selected_value_slugs: list[str]` (3 to 5 items)
  - `core_value_slug?: str|None`
- **Response 200**: Updated `UserValuesResponse`

#### 52. Get Target User Values — `GET /v1/values/people/{target_user_id}`
- **Auth**: Bearer JWT
- **Response 200**: `PublicValuesResponse`
  - Returns target user's Guiding Compass values (`slug`, `name`, `badge_icon`, `is_core`).
- **Errors**: `404 PrivacySafeNotFoundException` if target is blocked, values hidden, or user non-discoverable.

---

### Social Behavior System V1 (Planned Specification)

> **Note:** The following endpoints define the API contract for the Social Behavior System V1 architecture specification.

#### 53. List Canonical Social Behavior Options — `GET /v1/social-behavior/options`
- **Auth**: Public or Bearer JWT
- **Response 200**: `list[SocialCategoryWithOptions]`
  - Returns the 5 dimensions (`gathering_scale`, `social_battery`, `warmup_style`, `planning_style`, `comfort_zone`) with localized labels, definitions, and badge icons.

#### 54. Get Onboarding Social Snapshot Options — `GET /v1/social-behavior/onboarding-snapshot`
- **Auth**: Bearer JWT
- **Response 200**: `SocialOnboardingSnapshotConfig`
  - Returns the 3 onboarding questions (Gathering Scale, Social Battery, Warm-Up Dynamic) with interactive chips.

#### 55. Submit Social Behavior Onboarding — `POST /v1/social-behavior/onboarding`
- **Auth**: Bearer JWT
- **Body**: `SocialOnboardingRequest`
  - `group_preference?: str` (e.g. `'one_on_one'`, `'small_groups'`, `'lively_crowds'`, `'adaptable_scale'`)
  - `social_battery?: str` (e.g. `'recharge_solo'`, `'recharge_social'`, `'recharge_fluid'`)
  - `warmup_style?: str` (e.g. `'initiator'`, `'observer_first'`, `'selective_deep'`)
- **Response 200**: `UserSocialPreferencesResponse`
- **Errors**: `400 invalid_option_slug` if an unrecognized slug is passed.
- **Behavior**: All fields are optional (submitting empty body represents skipping the step).

#### 56. Get Own Social Preferences — `GET /v1/social-behavior/me`
- **Auth**: Bearer JWT
- **Response 200**: `UserSocialPreferencesResponse`
  - Returns all declared social preferences, custom visibility flags, and metadata.

#### 57. Update Own Social Preferences & Visibility — `PATCH /v1/social-behavior/me`
- **Auth**: Bearer JWT
- **Body**: `UpdateSocialPreferencesRequest`
  - `group_preference?: str|None`
  - `social_battery?: str|None`
  - `warmup_style?: str|None`
  - `planning_style?: str|None`
  - `comfort_zone?: str|None`
  - `visibility_flags?: dict[str, bool]`
- **Response 200**: Updated `UserSocialPreferencesResponse`

#### 58. Get Target User Social Preferences — `GET /v1/social-behavior/people/{target_user_id}`
- **Auth**: Bearer JWT
- **Response 200**: `PublicSocialPreferencesResponse`
  - Returns target user's public social preferences filtered strictly through target's `visibility_flags`.
- **Errors**: `404 PrivacySafeNotFoundException` if target is blocked, non-discoverable, or preferences hidden.

---

### Communication System V1 (Planned Specification)

> **Note:** The following endpoints define the API contract for the Communication System V1 architecture specification.

#### 59. List Canonical Communication Options — `GET /v1/communication/options`
- **Auth**: Public or Bearer JWT
- **Response 200**: `list[CommunicationCategoryWithOptions]`
  - Returns the 4 dimensions (`conversation_depth`, `conversation_role`, `messaging_medium`, `response_pace`) with localized labels, definitions, and badge icons.

#### 60. Get Onboarding Communication Snapshot Options — `GET /v1/communication/onboarding-snapshot`
- **Auth**: Bearer JWT
- **Response 200**: `CommunicationOnboardingSnapshotConfig`
  - Returns the 3 onboarding questions (Depth, Conversational Role, Messaging Medium) with interactive chips.

#### 61. Submit Communication Onboarding — `POST /v1/communication/onboarding`
- **Auth**: Bearer JWT
- **Body**: `CommunicationOnboardingRequest`
  - `conversation_depth?: str` (e.g. `'casual_light'`, `'balanced_depth'`, `'deep_meaningful'`)
  - `conversation_role?: str` (e.g. `'question_curious'`, `'story_expressive'`, `'idea_conceptual'`, `'adaptable_flow'`)
  - `messaging_medium?: str` (e.g. `'mostly_text'`, `'voice_notes_welcome'`, `'calls_welcome'`, `'flexible_medium'`)
- **Response 200**: `UserCommunicationPreferencesResponse`
- **Errors**: `400 invalid_option_slug` if an unrecognized slug is passed.
- **Behavior**: All fields are optional (submitting empty body represents skipping the step).

#### 62. Get Own Communication Preferences — `GET /v1/communication/me`
- **Auth**: Bearer JWT
- **Response 200**: `UserCommunicationPreferencesResponse`
  - Returns all declared communication preferences, custom visibility flags, and metadata.

#### 63. Update Own Communication Preferences & Visibility — `PATCH /v1/communication/me`
- **Auth**: Bearer JWT
- **Body**: `UpdateCommunicationPreferencesRequest`
  - `conversation_depth?: str|None`
  - `conversation_role?: str|None`
  - `messaging_medium?: str|None`
  - `response_pace?: str|None`
  - `visibility_flags?: dict[str, bool]`
- **Response 200**: Updated `UserCommunicationPreferencesResponse`

#### 64. Get Target User Communication Preferences — `GET /v1/communication/people/{target_user_id}`
- **Auth**: Bearer JWT
- **Response 200**: `PublicCommunicationPreferencesResponse`
  - Returns target user's public communication preferences filtered strictly through target's `visibility_flags`.
- **Errors**: `404 PrivacySafeNotFoundException` if target is blocked, non-discoverable, or preferences hidden.

---

### Intent System V1 (Planned Specification)

*(Authoritative Architecture Specification: [`docs/INTENT_SYSTEM_V1_SPEC.md`](INTENT_SYSTEM_V1_SPEC.md))*

> **Note:** The following endpoints define the API contract for the Intent System V1 architecture specification.

#### 65. List Canonical Intent Options — `GET /v1/intents/options`
- **Auth**: Public or Bearer JWT
- **Response 200**: `list[IntentCategoryWithOptions]`
  - Returns the 3 categories (`social_connection`, `activity_practical`, `exploratory`) with all 7 canonical options (`friendship`, `dating_open`, `dating_serious`, `meaningful_chat`, `activity_partner`, `collaboration`, `just_exploring`), localized names, definitions, and badge icons.

#### 66. Get Onboarding Intent Options — `GET /v1/intents/onboarding`
- **Auth**: Bearer JWT
- **Response 200**: `IntentOnboardingConfig`
  - Returns the primary selection card metadata and secondary openness options.

#### 67. Submit Intent Onboarding — `POST /v1/intents/onboarding`
- **Auth**: Bearer JWT
- **Body**: `IntentOnboardingRequest`
  - `primary_intent: str` (e.g. `'friendship'`, `'dating_open'`, `'dating_serious'`, `'just_exploring'`)
  - `secondary_intents?: list[str]` (Array of max 2 slugs)
- **Response 200**: `UserIntentResponse`
- **Errors**: `400 invalid_intent_slug` if unrecognized slug; `400 mutually_exclusive_intent` if primary also in secondaries.
- **Behavior**: 100% optional (submitting empty body sets default to `just_exploring` with `source = 'skipped'`).

#### 68. Get Own Intent — `GET /v1/intents/me`
- **Auth**: Bearer JWT
- **Response 200**: `UserIntentResponse(user_id: UUID, primary_intent: str, secondary_intents: list[str], visibility: str, source: str, updated_at: datetime)`

#### 69. Update Own Intent & Visibility — `PATCH /v1/intents/me`
- **Auth**: Bearer JWT
- **Body**: `UpdateIntentRequest`
  - `primary_intent?: str`
  - `secondary_intents?: list[str]`
  - `visibility?: Literal["public", "connections_only", "hidden"]`
- **Response 200**: Updated `UserIntentResponse`
- **Behavior**: Appends transition audit record to `public.user_intent_history` (service-role only) and invalidates discovery cache.

#### 70. Get Target User Intent — `GET /v1/intents/people/{target_user_id}`
- **Auth**: Bearer JWT
- **Response 200**: `PublicIntentResponse`
  - Returns target user's public primary and secondary intents.
- **Errors**: `404 PrivacySafeNotFoundException` if target is blocked, non-discoverable, or intent hidden.

---

### Prompts & Self-Expression System V1 (Planned Specification)

*(Authoritative Architecture Specification: [`docs/PROMPTS_SELF_EXPRESSION_SYSTEM_V1_SPEC.md`](PROMPTS_SELF_EXPRESSION_SYSTEM_V1_SPEC.md))*

> **Note:** The following endpoints define the API contract for the Prompts & Self-Expression System V1 architecture specification.

#### 71. List Curated Prompt Templates — `GET /v1/prompts/templates`
- **Auth**: Public or Bearer JWT
- **Response 200**: `list[PromptCategoryWithTemplates]`
  - Returns all 6 categories (`voice_quirks`, `curiosities`, `daily_reality`, `connection`, `perspectives`, `action`) with the 24 canonical prompt questions, localized texts (EN/KA), placeholders, and sort orders.

#### 72. Get Contextual Prompt Recommendations — `GET /v1/prompts/suggestions`
- **Auth**: Bearer JWT
- **Response 200**: `PromptSuggestionsResponse(recommended_templates: list[PromptTemplateDTO], context_reason: str)`
  - Returns intelligent, non-hallucinated template recommendations based on the user's declared interests, values, and communication roles (e.g. suggests rabbit hole prompts for curious thinkers). Never suggests or pre-writes answers.

#### 73. Get Own Prompts — `GET /v1/prompts/me`
- **Auth**: Bearer JWT
- **Response 200**: `list[UserPromptResponse(id: UUID, prompt_template_id: UUID, template_slug: str, prompt_text: str, answer: str, sort_order: int, visibility: str, source: str, moderation_status: str, created_at: datetime, updated_at: datetime)]`

#### 74. Publish Prompt — `POST /v1/prompts`
- **Auth**: Bearer JWT
- **Body**: `CreatePromptRequest`
  - `prompt_template_id: UUID`
  - `answer: str` (min 3, max 250 characters; non-empty)
  - `sort_order?: int` (1, 2, or 3)
  - `visibility?: Literal["public", "connections_only", "hidden"]` (default: `"public"`)
- **Response 201**: `UserPromptResponse`
- **Errors**: `400 prompt_limit_exceeded` if user already has 3 active prompts; `400 invalid_length` if $> 250$ chars; `422 moderation_flagged` if automated regex detects PII, harassment, or malicious scripts.

#### 75. Update Own Prompt — `PATCH /v1/prompts/{prompt_id}`
- **Auth**: Bearer JWT
- **Body**: `UpdatePromptRequest(answer?: str, sort_order?: int, visibility?: str)`
- **Response 200**: Updated `UserPromptResponse`
- **Errors**: `404 PrivacySafeNotFoundException` if prompt not owned by caller.

#### 76. Delete Own Prompt — `DELETE /v1/prompts/{prompt_id}`
- **Auth**: Bearer JWT
- **Response 204**: No Content
- **Behavior**: Permanently removes the prompt answer; frees up the prompt slot.

#### 77. AI Writing Assistance — `POST /v1/prompts/ai-assist`
- **Auth**: Bearer JWT
- **Body**: `PromptAIAssistRequest`
  - `prompt_template_id: UUID`
  - `draft_text: str` (user's raw thought or draft)
  - `style: Literal["sharpen", "shorten", "warmer", "wittier"]`
- **Response 200**: `PromptAIAssistResponse(original: str, suggestions: list[str])`
  - Returns up to 3 candidate formulations retaining authentic user voice.
  - *Hard Invariant*: AI suggestions are NEVER automatically published or persisted. The user must explicitly choose, edit, and submit the final text.

#### 78. Get Target User Prompts — `GET /v1/prompts/people/{target_user_id}`
- **Auth**: Bearer JWT
- **Response 200**: `list[PublicPromptDTO(id: UUID, template_slug: str, prompt_text: str, answer: str, sort_order: int)]`
  - Returns target user's active, approved prompts (filtered by visibility).
- **Errors**: `404 PrivacySafeNotFoundException` if target is blocked or non-discoverable.

---

### Discovery Preferences & Feed Engine V1 (Planned Specification)

*(Authoritative Architecture Specification: [`docs/DISCOVERY_PREFERENCES_SYSTEM_V1_SPEC.md`](DISCOVERY_PREFERENCES_SYSTEM_V1_SPEC.md))*

> **Note:** The following endpoints define the API contract for the Discovery Preferences & Feed Engine V1 architecture specification.

#### 79. Get Own Discovery Preferences — `GET /v1/discovery/preferences`
- **Auth**: Bearer JWT
- **Response 200**: `UserDiscoveryPreferencesResponse`
  - `user_id: UUID`
  - `age_min: int` (18–99)
  - `age_max: int` (18–99)
  - `age_dealbreaker: bool`
  - `target_genders: list[str]` (e.g. `["all"]`, `["woman"]`, `["man"]`, `["non_binary"]`)
  - `location_scope: str` (`"same_city"`, `"same_country"`, `"regional_nearby"`, `"anywhere"`)
  - `location_dealbreaker: bool`
  - `target_intents: list[str]` (optional sub-filter; empty = natural bilateral compatibility)
  - `astrology_mode: str` (`"full_insights"`, `"minimal_insights"`, `"hidden"`)
  - `diversity_level: str` (`"focused"`, `"balanced"`, `"adventurous"`)
  - `source: str` (`"default_derived"`, `"user_configured"`, `"reset_to_default"`)
  - `updated_at: datetime`

#### 80. Update Own Discovery Preferences — `PATCH /v1/discovery/preferences`
- **Auth**: Bearer JWT
- **Body**: `UpdateDiscoveryPreferencesRequest`
  - `age_min?: int`
  - `age_max?: int`
  - `age_dealbreaker?: bool`
  - `target_genders?: list[str]`
  - `location_scope?: str`
  - `location_dealbreaker?: bool`
  - `target_intents?: list[str]`
  - `astrology_mode?: str`
  - `diversity_level?: str`
- **Response 200**: Updated `UserDiscoveryPreferencesResponse`
- **Errors**: `400 invalid_age_range` if `age_min > age_max` or `age_min < 18`.

#### 81. Reset Discovery Preferences — `POST /v1/discovery/preferences/reset`
- **Auth**: Bearer JWT
- **Response 200**: `UserDiscoveryPreferencesResponse`
  - Re-derives sensible open defaults from caller's current age and intent.

#### 82. Get Discovery Feed — `GET /v1/discovery/feed`
- **Auth**: Bearer JWT
- **Query Params**:
  - `cursor?: str` (base64 pagination token)
  - `limit?: int` (default: 10, max: 30)
  - `lens?: Literal["for_you", "nearby", "shared_purpose", "shared_curiosities"]` (default: `"for_you"`)
- **Response 200**: `DiscoveryFeedResponse`
  - `candidates: list[DiscoveryCandidateDTO]`
    - `id: UUID`
    - `display_name: str`
    - `age: int` (computed integer age; raw birth date is NEVER returned)
    - `avatar_url: str | None`
    - `headline: str | None` (max 140 chars)
    - `location: LocationDTO` (city & country only; zero coordinates)
    - `origin: OriginDTO | None`
    - `primary_intent: IntentOptionDTO`
    - `featured_prompt: PromptDTO | None` (top featured prompt with quote)
    - `primary_interests: list[InterestDTO]` (5 core chips)
    - `safe_astrology: SafeDerivedAstrologyResponse | None` (filtered by caller's `astrology_mode`)
    - `explanation: DiscoveryExplanationDTO`
      - `primary_reason: str` (e.g. *"You both love photography and are looking for friendship in Tbilisi."*)
      - `resonance_type: str`
  - `next_cursor: str | None`
  - `has_more: bool`
- **Errors**: `401 Unauthorized` if unauthenticated.
- **Invariants**: Strictly enforces 3-tier pipeline (SQL hard gates, composite relevance scoring, diversity reranking). Excludes viewer, blocked users, non-discoverable profiles, and existing connections. Never leaks percentage match scores.

#### 83. Get Discovery Options & Taxonomy — `GET /v1/discovery/options`
- **Auth**: Public or Bearer JWT
- **Response 200**: `DiscoveryOptionsResponse`
  - Returns localized labels, descriptions, and defaults for `location_scopes`, `gender_options`, `astrology_modes`, and `diversity_levels`.

---

### Trust, Verification & Safety (Platform Architecture Spec: [`docs/TRUST_VERIFICATION_SYSTEM_V1_SPEC.md`](TRUST_VERIFICATION_SYSTEM_V1_SPEC.md))

#### 84. List Own Profile Photos — `GET /v1/profiles/me/photos`
- **Auth**: Bearer JWT
- **Response 200**: `list[ProfilePhotoDTO(id: UUID, url: str, is_primary: bool, sort_order: int, created_at: datetime)]`

#### 85. Upload Profile Photo — `POST /v1/profiles/me/photos`
- **Auth**: Bearer JWT
- **Body**: `multipart/form-data` containing image file (`image/jpeg`, `image/png`, `image/webp`, max 5MB).
- **Response 201**: `ProfilePhotoDTO`
- **Errors**: `400 max_photos_exceeded` if user already has 6 photos; `400 inappropriate_media` if NSFW scan fails.
- **Behavior**: Stores in `avatars` bucket. If first photo, automatically marks as `is_primary = true` and updates `profiles.avatar_url`.

#### 86. Set Primary Photo — `PATCH /v1/profiles/me/photos/{photo_id}/primary`
- **Auth**: Bearer JWT
- **Response 200**: `ProfilePhotoDTO`
- **Invariants**: If the user has an active `verified` status, changing the primary photo automatically resets verification to `needs_review` or `expired` to prevent identity tampering.

#### 87. Delete Profile Photo — `DELETE /v1/profiles/me/photos/{photo_id}`
- **Auth**: Bearer JWT
- **Response 204**: No Content
- **Invariants**: If the primary photo is deleted and other photos remain, another photo must be promoted. If 0 photos remain, profile is automatically removed from public Discovery.

#### 88. Start Face Verification Session — `POST /v1/verification/face/session`
- **Auth**: Bearer JWT
- **Response 200**: `VerificationSessionInitDTO(session_token: str, expires_in_seconds: int, challenge_type: str)`
- **Errors**: `429 verification_rate_limited` if $> 3$ failed attempts in 24 hours.
- **Behavior**: Generates an ephemeral session token valid for 5 minutes.

#### 89. Submit Face Verification — `POST /v1/verification/face/submit`
- **Auth**: Bearer JWT
- **Body**: `VerificationSubmitRequest(session_token: str, selfie_payload: bytes)`
- **Response 200**: `VerificationResultDTO(status: Literal["verified", "failed", "needs_review"], message: str)`
- **Errors**: `400 session_expired`, `400 liveness_failed`, `429 rate_limited`.
- **Security Boundary**: Verification selfie is evaluated server-side, encrypted into private `verification-evidence` bucket (`public = false`, auto-deleted after 30 days). NEVER exposed to clients or passed to JESTER AI.

#### 90. Get Face Verification Status — `GET /v1/verification/face/status`
- **Auth**: Bearer JWT
- **Response 200**: `UserVerificationStatusDTO(status: str, is_verified: bool, verified_at: datetime|None, expires_at: datetime|None)`

#### 91. Block User — `POST /v1/safety/block`
- **Auth**: Bearer JWT
- **Body**: `BlockRequest(target_user_id: UUID)`
- **Response 200**: `{"status": "blocked", "target_user_id": UUID}`
- **Behavior**: Inserts reciprocal block into `public.user_blocks` and transitions active connection to `blocked`. Immediately triggers reciprocal 404 on all endpoints. Zero notification sent to blocked user.

#### 92. Unblock User — `POST /v1/safety/unblock`
- **Auth**: Bearer JWT
- **Body**: `UnblockRequest(target_user_id: UUID)`
- **Response 200**: `{"status": "unblocked", "target_user_id": UUID}`

#### 93. List Blocked Users — `GET /v1/safety/blocks`
- **Auth**: Bearer JWT
- **Response 200**: `list[BlockedUserDTO(blocked_id: UUID, display_name: str, blocked_at: datetime)]`

#### 94. Submit Community Safety Report — `POST /v1/safety/report`
- **Auth**: Bearer JWT
- **Body**: `ReportCreateRequest(reported_user_id: UUID, reason: Literal["fake_profile", "harassment", "inappropriate_content", "spam_scam", "underage", "other"], details: str|None)`
- **Response 201**: `{"status": "report_received", "report_id": UUID}`
- **Privacy & Safety**: 100% confidential. Reported user is never informed of reporter identity. If reported account accumulates $\ge 3$ reports within 48 hours, outbound privileges are throttled pending moderator review.

---

### Behavioral Intelligence & Telemetry (Platform Architecture Spec: [`docs/BEHAVIORAL_INTELLIGENCE_SYSTEM_V1_SPEC.md`](BEHAVIORAL_INTELLIGENCE_SYSTEM_V1_SPEC.md))

#### 95. Batch Ingest Telemetry Events — `POST /v1/telemetry/events`
- **Auth**: Bearer JWT
- **Body**: `BatchTelemetryRequest`
  - `events`: `list[TelemetryEventDTO]` (max 50 events per batch)
    - `event_name`: `str` (from canonical taxonomy: `candidate_profile_opened`, `why_opened`, `candidate_dismissed`, etc.)
    - `target_id`: `UUID | None`
    - `target_type`: `Literal["candidate", "interest", "prompt", "preference"] | None`
    - `context`: `dict[str, Any]` (sanitized; capped `dwell_time_ms`, boolean flags; zero message text, zero coordinates)
    - `client_timestamp`: `datetime`
- **Response 202**: `{"status": "accepted", "ingested_count": int}`
- **Security & Rate Limits**: Max 120 events/min per user. Velocity anomalies (<200ms inter-event latency) dropped. Raw events stored in `public.behavioral_events` (60-day auto-prune TTL). Client read access revoked.

#### 96. Get Behavioral Personalization Settings — `GET /v1/users/me/behavioral-settings`
- **Auth**: Bearer JWT
- **Response 200**: `BehavioralSettingsResponse`
  - `personalization_enabled`: `bool`
  - `allow_activity_learning`: `bool`
  - `last_reset_at`: `datetime | None`

#### 97. Update Behavioral Personalization Settings — `PUT /v1/users/me/behavioral-settings`
- **Auth**: Bearer JWT
- **Body**: `BehavioralSettingsUpdateRequest(personalization_enabled: bool | None, allow_activity_learning: bool | None)`
- **Response 200**: `BehavioralSettingsResponse`
- **Invariants**: If `personalization_enabled = false`, Discovery Tier 2/3 ranking ignores all behavioral affinity signals, computing recommendations exclusively from declared profile attributes and deterministic synastry.

#### 98. Reset Personalization History — `POST /v1/users/me/personalization/reset`
- **Auth**: Bearer JWT
- **Response 200**: `{"status": "reset_complete", "reset_at": datetime}`
- **Invariants**: Immediately purges all rows in `public.user_interest_affinity` for the caller and resets `public.user_behavioral_signals` to default values. Declared interests, values, and profile data remain completely untouched.

---

### JESTER AI Context & Copilot System (Platform Architecture Spec: [`docs/JESTER_AI_CONTEXT_SYSTEM_V1_SPEC.md`](JESTER_AI_CONTEXT_SYSTEM_V1_SPEC.md))

#### 99. Generate Contextual JESTER Insight / Copilot Response — `POST /v1/ai/insight`
- **Auth**: Bearer JWT
- **Body**: `AiInsightRequest`
  - `surface`: `Literal["main_chat", "discovery_feed", "profile_preview", "why_card", "us_relationship", "conversation_starter", "astrology_deep"]`
  - `target_user_id`: `UUID | None` (required for relational surfaces: profile_preview, why_card, us_relationship, conversation_starter)
  - `prompt_reference_id`: `UUID | None` (optional specific prompt card target)
  - `user_query`: `str | None` (optional user message for Main Chat copilot turns)
- **Response 200**: `AiInsightResponse`
  - `insight_text`: `str` (short, witty, observant copy in Georgian/English)
  - `surface`: `str`
  - `tone`: `Literal["witty", "playful_sarcastic", "warm_observant"]`
  - `grounded_in`: `list[str]` (human explainability topics, e.g. `["shared_interest:photography", "communication:unhurried"]`)
  - `language`: `str`
- **Errors**: `404 PrivacySafeNotFoundException` if target user is blocked, non-discoverable, or non-existent; `400 invalid_surface`.
- **Invariants**: Context is assembled strictly on-demand via `ContextAssemblerService` and verified by `ContextSafetyGate`. If safety gate detects any forbidden data, execution falls back immediately to deterministic pre-approved Georgian copy from `ContentLibrary`. Zero astrology jargon permitted in output.

#### 100. Inspect Assembled AI Context (Non-Production Testing) — `GET /v1/ai/context/inspect`
- **Auth**: Bearer JWT (`admin` or `developer` role)
- **Query Parameters**:
  - `surface`: `str`
  - `target_user_id`: `UUID | None`
- **Response 200**: `JesterAiContextV1` JSON contract
- **Security Invariant**: Strictly forbidden in production (`settings.ENV == "production"` raises `403 Forbidden`). Exists purely for automated CI regression testing and privacy auditing.







