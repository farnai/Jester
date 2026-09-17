# JESTER — TRUST & VERIFICATION SYSTEM V1
## Product, UX, Data Architecture & Safety Specification

**Document Type:** Core Architecture & Product Safety Specification  
**System Domain:** Trust, Profile Authenticity, Verification & Moderation  
**System Version:** `trust-v1.0.0`  
**Parent Specifications:**
- [`docs/archive/historical/PRODUCT_SPECIFICATION.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/archive/historical/PRODUCT_SPECIFICATION.md) (Historical Parent)
- [`docs/SECURITY.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/SECURITY.md)
- [`docs/DISCOVERY_PREFERENCES_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/DISCOVERY_PREFERENCES_SYSTEM_V1_SPEC.md)
- [`docs/FRONTEND_CAPABILITY_SPECIFICATION.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/FRONTEND_CAPABILITY_SPECIFICATION.md)
- [`docs/AI.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/AI.md)  
**Status:** Authoritative Architectural Specification (V1 Frozen)

---

## 1. Executive Summary & Core Product Axioms

JESTER is a **People Discovery and Relationship Intelligence** platform. Connecting with other humans requires a baseline of trust and physical authenticity. However, trust in JESTER must increase user confidence **without turning the platform into a surveillance system or a dystopian credit-scoring product**.

### Core Product Axioms:
1. **"People first. Signals second. Scores last."**
   Trust must protect human dignity. JESTER will never compute or display a numerical "Trust Score" (e.g. *"Trustworthiness: 84/100"*). Humans cannot be reduced to a credit rating.
2. **"Verification proves a limited fact, not human character."**
   Identity/Face Verification proves strictly one narrow physical fact: **"A live human holding a camera matches the person depicted in the active profile photos at the time of verification."**
   - Verification does **NOT** prove that a person is safe.
   - Verification does **NOT** prove that a person is trustworthy, kind, honest, or desirable.
   - Verification does **NOT** predict future interpersonal behavior.
3. **"The insight becomes the invitation, but safety guards the doorway."**
   Curiosity drives connection; verification and moderation ensure that the people discovered are authentic, accountable, and real.
4. **"Keep critical concepts strictly decoupled:"**

```text
PROFILE PHOTO
      ≠
FACE VERIFICATION
      ≠
TRUSTWORTHINESS
      ≠
SAFETY & MODERATION
```

---

## 2. Current System Audit

A thorough audit of the active repository ([`backend/app/`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/backend/app/), [`supabase/migrations/`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/supabase/migrations/), and [`docs/`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/)) establishes the current baseline:

### 2.1 Implemented & Active Code
1. **Profiles (`public.profiles`):**
   - Single photo URL field: `avatar_url: text` (Migration 003).
   - Discoverability toggle: `is_discoverable: boolean default true` (Migration 003).
   - Profile updating: `PATCH /v1/profiles/me` updates `avatar_url`, `display_name`, `bio`, `city`, `occupation`.
2. **Storage (`avatars` bucket):**
   - Migration 019 configures the `avatars` bucket in Supabase Storage (`public = true`, `5MB limit`, JPEG/PNG/WebP/GIF).
   - Folder-isolated RLS: `(storage.foldername(name))[1] = auth.uid()::text`.
   - Cascading account deletion cleanup trigger `cleanup_user_storage_on_account_deletion()`.
3. **Blocking & Privacy Semantics:**
   - Canonical connection table (`public.connections`) stores status `'blocked'` and `blocked_by: uuid` (Migration 007).
   - Helper function `public.is_user_blocked(u1, u2)` enforces reciprocal blocking across profiles, comparisons, and discovery (Migration 016).
   - Reciprocal 404 (`PrivacySafeNotFoundException`) prevents existence oracles.

### 2.2 Documented vs. Missing Infrastructure
- **Multi-Photo Capability:** Currently documented conceptually as profile photos, but the database only provides a single scalar `avatar_url` column.
- **Verification System:** Invariant 9 in `docs/SECURITY.md` mandates the strict separation between profile presentation and identity verification, but no verification tables or endpoints exist yet.
- **Reporting & Moderation:** No dedicated `reports` or `moderation_cases` tables exist; blocking is currently co-located inside the `connections` table.
- **Moderation States:** Profiles do not currently possess a `moderation_status` column (only `is_discoverable`).

---

## 3. The Multi-Layered Trust Model

JESTER rejects the idea of a singular, algorithmic "trust score". Instead, trust is modeled through a series of independent, orthogonal layers that evaluate distinct dimensions of an account:

```text
+-----------------------------------------------------------------------------------+
| LAYER 1: ACCOUNT INTEGRITY & AUTHENTICATION                                       |
| Valid Supabase Auth JWT, verified email, rate-limit adherence, bot/proxy screening|
+-----------------------------------------------------------------------------------+
                                      ↓
+-----------------------------------------------------------------------------------+
| LAYER 2: PROFILE AUTHENTICITY & PHOTO PRESENCE                                    |
| At least 1 clear, authentic primary photo showing the user's face                 |
+-----------------------------------------------------------------------------------+
                                      ↓
+-----------------------------------------------------------------------------------+
| LAYER 3: BIOMETRIC FACE VERIFICATION (OPTIONAL TRUST BADGE)                       |
| Liveness selfie check matching primary profile photo (✓ Verified badge)           |
+-----------------------------------------------------------------------------------+
                                      ↓
+-----------------------------------------------------------------------------------+
| LAYER 4: COMMUNITY ACCOUNTABILITY & REPORTING                                     |
| Reciprocal blocking, structured abuse reports, community flag thresholds          |
+-----------------------------------------------------------------------------------+
                                      ↓
+-----------------------------------------------------------------------------------+
| LAYER 5: PLATFORM MODERATION & SAFETY ENFORCEMENT                                 |
| Active, Limited, Under Review, Suspended, Banned standing                         |
+-----------------------------------------------------------------------------------+
                                      ↓
                     DISCOVERY & INTERACTION ELIGIBILITY
```

---

## 4. Profile Photo System

Profile photos represent the primary visual anchor of a user's presence. JESTER balances self-expression with platform integrity.

### 4.1 Photo Requirements & Capacity
- **Minimum Requirement for Discovery:** **1 valid photo** where the user's face is clearly visible.
  - *Product Rule:* An account without a photo may exist, explore settings, and edit their private profile, but **cannot appear in the public Discovery feed**.
- **Recommended Capacity:** **3 to 6 photos** (V1 supports up to 6 photos per profile).
- **Primary Photo Designation:** Exactly 1 photo is marked as `is_primary = true` (serves as avatar thumbnail and verification anchor).

### 4.2 Primary Photo Integrity Rules
1. **Clear Facial Visibility:** The user's face must be unobscured, in focus, and adequately lit. Sunglasses, heavy shadow, extreme tilt, or dramatic face filters covering the eyes or facial geometry are prohibited.
2. **Solo Subject:** The primary photo must show only the account owner. Group photos as the primary photo are prohibited to eliminate ambiguity.
3. **No Inanimate Objects / Memes / Animals:** Cars, landscapes, text memes, illustrations, and pet photos are strictly barred from the primary photo slot. (Pets and hobbies are permitted in secondary slots 2–6).
4. **No Synthetic / AI-Generated Faces:** Photorealistic AI avatars (e.g. Midjourney, Stable Diffusion personas) are strictly prohibited as primary photos. JESTER connects real human beings.
5. **No Sexually Explicit / Nude Media:** Complete zero tolerance for nudity, partial nudity, or sexually suggestive imagery.

### 4.3 Secondary Photo Flexibility (Slots 2–6)
Secondary photos are designed to express human lifestyle, passions, and social rhythm:
- Lifestyle shots, outdoor activities, creative projects, pets, travel, and candid moments.
- Group photos are permitted in secondary slots provided the primary photo already established unambiguous identity.

### 4.4 Photo Moderation & Replacement Lifecycle
- **Automated Ingestion Screen:** Every upload is scanned via an automated perceptual hash (blocklist against known illegal content) and NSFW/nudity classifier before storage.
- **Photo Deletion:** A user can delete any secondary photo freely. If the primary photo is deleted, an existing secondary photo must be promoted to primary. If all photos are removed, the profile drops out of Discovery.
- **Photo Replacement Invalidation:** If a verified user replaces their primary photo with a new image, **verification status resets to `needs_review` or `expired`** to prevent bait-and-switch identity hijacking.

---

## 5. Face Verification System

Face Verification is an optional, high-trust feature that allows users to prove their physical authenticity.

### 5.1 Verification Architecture
```text
USER CAMERA (Mobile / Web)
       ↓
EPHEMERAL LIVENESS SESSION (Passive / Active Liveness Check)
       ├── Frame 1..N: Motion, 3D mesh, texture reflection (Anti-Spoof)
       └── High-Resolution Verification Selfie
              ↓
BIOMETRIC MATCHING ENGINE (Server-Side Abstraction)
       ├── Compare Verification Selfie vs. Active Primary Profile Photo
       └── Compute Similarity Score & Liveness Confidence
              ↓
DECISION MATRIX
       ├── High Confidence Match (>= 85%): Status -> 'verified'
       ├── Borderline / Low Quality (60-84%): Status -> 'needs_review'
       └── Definite Mismatch / Spoof (< 60%): Status -> 'failed'
              ↓
PRIVATE EVIDENCE STORAGE
       ├── Verification selfie stored in private, encrypted bucket
       └── NEVER EXPOSED TO CLIENT / NEVER PASSED TO JESTER AI
```

### 5.2 Anti-Spoofing & Deepfake Protections
- **Liveness Detection:** Enforces temporal and depth continuity to reject printed paper photos, digital screen replays, and silicone masks.
- **Session Salt / Challenge:** Verification requests require a short-lived nonce (`session_token`) generated by the server, valid for 5 minutes.
- **Deepfake Artifact Detection:** AI texture and frequency analysis identifies synthetic facial warping or generative deepfake overlays.
- **Attempt Throttling:** Maximum **3 verification attempts per 24 hours**. Exceeding 3 failed attempts locks verification for 48 hours to prevent brute-force presentation attacks.

### 5.3 Verification Media Privacy Guarantee
> **"Verification media is private verification evidence. It must never appear publicly."**

- The verification selfie is **NEVER** added to the user's public profile gallery.
- The verification selfie is **NEVER** serialized to any public API response.
- The verification selfie is **NEVER** accessible to other users, connections, or third parties.
- Verification media is stored in a private, encrypted storage bucket (`verification-evidence`) with `public = false`.

---

## 6. Verification State Machine

JESTER defines a canonical 7-state verification lifecycle:

```text
               ┌────────────────────────┐
               │      not_started       │
               └───────────┬────────────┘
                           │ User initiates verification
                           ▼
               ┌────────────────────────┐
               │        pending         │
               └─────┬────────────┬─────┘
                     │            │
         Match >= 85%│            │ Match < 60%
                     ▼            ▼
      ┌─────────────────┐      ┌─────────────────┐
      │    verified     │      │     failed      │◄───┐
      └──────┬──────────┘      └────────┬────────┘    │ Retry
             │                          │             │ (max 3/24h)
             │ Primary photo changed /  └─────────────┘
             │ Expired (1 year)
             ▼
      ┌─────────────────┐
      │     expired     │
      └─────────────────┘
             ▲
             │ Admin revocation / Fraud detected
      ┌──────┴──────────┐
      │     revoked     │
      └─────────────────┘

   * Note: Borderline scores (60–84%) transition from `pending` -> `needs_review`
     before resolving to `verified` or `failed`.
```

### State Definitions & Permissions:

| State | Definition | Public Badge | Discovery Impact | Permitted Actions |
| :--- | :--- | :--- | :--- | :--- |
| **`not_started`** | User has never attempted verification. | None | Normal browsing & discovery (if photo present). | Full platform features. |
| **`pending`** | Selfie submitted, awaiting processing. | None | Unchanged from previous state. | Full platform features. |
| **`verified`** | Biometric match confirmed. | `✓ Photo Verified` | Subtle trust boost in candidate feeds. | Full platform features. |
| **`failed`** | Liveness failed or face did not match. | None | Normal browsing; retry option visible. | Full platform features; 3 retries/24h. |
| **`needs_review`** | Borderline match; routed to admin queue. | None | Normal browsing; status displayed as pending. | Full platform features. |
| **`expired`** | Validity elapsed (1 year) or photo changed. | Badge removed | Treated as unverified until renewed. | Full platform features. |
| **`revoked`** | Admin revoked due to fraud or impersonation.| Badge removed | Account flagged; moderation review opened. | Restricted until investigation concludes. |

---

## 7. Discovery Eligibility Architecture

Discovery visibility is governed by a clear, non-discriminatory multi-factor gate. Verification is a **trust signal**, not a hard exclusionary gate.

```text
DISCOVERY ELIGIBILITY FORMULA:
   Account Standing == 'active' (Not suspended, not banned)
AND
   Profile Discoverability == true (is_discoverable)
AND
   Primary Photo Presence == true (>= 1 valid public photo)
AND
   Viewer is not Blocked (is_user_blocked == false)
AND
   Verification Policy Satisfied (Verified is OPTIONAL for entry)
=
   ELIGIBLE TO APPEAR IN DISCOVERY FEED
```

### Core Discovery Invariants:
1. **Unverified Users CAN Appear in Discovery:** Unverified users with an authentic public photo appear normally in candidate feeds. JESTER does not create a paywalled or discriminatory "verified-only marketplace".
2. **Users Without Photos CANNOT Appear in Discovery:** An account without at least 1 public photo remains private to the user.
3. **Optional User Filtering:** Viewers can configure their discovery preferences with an optional preference:
   `"Prioritize verified profiles"` (surfaces verified candidates with higher ranking) or `"Verified profiles only"` (strictly for users who choose maximum caution).

---

## 8. Connection & Messaging Eligibility

| User State | Send Request | Receive Request | Accept Request | Send Message | Run Synastry |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Verified (with photo)** | 🟢 Yes | 🟢 Yes | 🟢 Yes | 🟢 Yes | 🟢 Yes |
| **Unverified (with photo)**| 🟢 Yes | 🟢 Yes | 🟢 Yes | 🟢 Yes | 🟢 Yes |
| **No Photo (Private)** | 🟢 Yes (to direct link)| 🟢 Yes | 🟢 Yes | 🟢 Yes | 🟢 Yes |
| **Limited (Rate-limited)** | 🟡 Throttled (max 5/day)| 🟢 Yes | 🟢 Yes | 🟢 Yes | 🟢 Yes |
| **Under Review** | 🚫 Paused | 🚫 Paused | 🟢 Yes (Existing)| 🟡 Existing only| 🚫 Paused |
| **Suspended (Temporary)** | 🚫 Blocked | 🚫 Blocked | 🚫 Blocked | 🚫 Blocked | 🚫 Blocked |
| **Banned (Permanent)** | 🚫 Blocked | 🚫 Blocked | 🚫 Blocked | 🚫 Blocked | 🚫 Blocked |

---

## 9. Report, Block & Safety Systems

Safety mechanisms are strictly differentiated by scope, permanence, and intent:

```text
┌─────────────┐
│    BLOCK    │  User-Initiated Immediate Personal Exclusion (Reciprocal 404, Zero Notification)
└─────────────┘
       │
┌─────────────┐
│   REPORT    │  User-Initiated Safety Signal with Evidence (Sent to Moderation Queue)
└─────────────┘
       │
┌─────────────┐
│ MODERATION  │  Platform-Level Investigation & Disciplinary Review
└─────────────┘
       │
┌─────────────┐
│ SUSPENSION  │  Temporary Platform Access Revocation (7–30 Days)
└─────────────┘
       │
┌─────────────┐
│     BAN     │  Permanent Identity & Credential Expulsion
└─────────────┘
```

### 9.1 Block Mechanics
- **Immediate & Reciprocal:** When User A blocks User B, both users become immediately invisible to each other.
- **Reciprocal 404:** Any direct profile lookup, safe astrology request, comparison check, or message retrieval returns `HTTP 404 PrivacySafeNotFoundException`.
- **Zero Existence Oracle:** The blocked user is never alerted and receives no differential error code (e.g. never receives HTTP 403).
- **Existing Conversations:** Direct conversation threads are immediately detached and archived.

### 9.2 Report Mechanics
- **Structured Categories:**
  1. `fake_profile` (Catfishing, stolen photos, celebrity impersonation)
  2. `harassment` (Bullying, hostile communication, offensive language)
  3. `inappropriate_content` (Nudity, sexual solicitation, violence)
  4. `spam_scam` (Commercial spam, phishing links, financial solicitation)
  5. `underage` (User appears to be under 18 years old)
  6. `other` (Free-form report description)
- **Reporter Protection:** Reports are 100% confidential. The reported user is never informed who submitted the report.
- **Automated Protective Threshold:** If an account receives $\ge 3$ distinct reports from unlinked users within 48 hours, the account automatically transitions to `under_review`, pausing new outbound connection requests pending moderator review.

---

## 10. Platform Moderation States

```text
+-------------------+---------------------------------------------------------------+
| MODERATION STATE  | PLATFORM BEHAVIOR & CONSTRAINTS                               |
+-------------------+---------------------------------------------------------------+
| 1. active         | Normal standing. Full platform access.                        |
+-------------------+---------------------------------------------------------------+
| 2. limited        | High outbound velocity detected. Outbound requests capped to  |
|                   | 5 per day. Messaging throttled. Profile remains visible.      |
+-------------------+---------------------------------------------------------------+
| 3. under_review   | Multiple reports received. Profile temporarily hidden from    |
|                   | Discovery. Outbound requests paused. Existing chats preserved.|
+-------------------+---------------------------------------------------------------+
| 4. suspended      | Temporary lockout (7 to 30 days) following confirmed policy   |
|                   | violation. Account login blocked; profile hidden platform-wide|
+-------------------+---------------------------------------------------------------+
| 5. banned         | Permanent platform expulsion. JWT rejected immediately.       |
|                   | Profile scrubbed from search. Photos and storage deleted.     |
+-------------------+---------------------------------------------------------------+
```

---

## 11. Anti-Fraud & Scam Defense Architecture

To protect users without over-engineering V1, JESTER deploys high-impact, low-complexity safety defenses:

1. **Connection Velocity Throttling:**
   - Free/standard users are limited to **20 outbound connection requests per 24-hour rolling window**.
   - Rapid bursting ($> 5$ requests within 60 seconds) triggers an automated 1-hour cooldown.
2. **External Link Guard in Early Chat:**
   - In new direct conversations ($< 10$ mutual messages exchanged), raw URLs and external links are visually flagged with an inline safety warning:
     *"Safety notice: Be cautious opening links or sending money to people you have recently met."*
3. **Perceptual Image Hashing:**
   - On upload, profile photos are converted into a discrete pHash (perceptual hash).
   - Accounts uploading identical images across multiple user IDs are flagged for coordinated bot-farm review.
4. **Disposable Email & Anomaly Detection:**
   - Supabase Auth prevents registration from known temporary/disposable email domains.

---

## 12. Public Trust Signals in UX

JESTER displays trust signals with semantic accuracy, avoiding moral judgments or false promises:

### 12.1 Approved Public Badges
- **`✓ Photo Verified` Badge:** Displayed next to the display name on the profile and candidate cards.
  - *Tooltip / Explainer:* *"JESTER verified that this person's live selfie matches their profile photos."*
- **Profile Completeness (Subtle Visual Cue):** Indicated through natural content richness (presence of signature interest, 3 prompts, cadence pills) rather than a gamified progress percentage bar.

### 12.2 Explicitly Prohibited UX Claims
- 🚫 *"Trust Score: 94%"* (Never quantify human trustworthiness).
- 🚫 *"Verified Safe Person"* (Verification does not prove safety).
- 🚫 *"100% Real & Honest"* (Verification proves facial matching, not honesty).
- 🚫 *"Top Rated Connection"* (Avoid marketplace rating dynamics).

---

## 13. Privacy, Encryption & Security Architecture

Biometric verification data represents sensitive personal identifiable information (PII). JESTER establishes rigorous security protections:

```text
PUBLIC CLOUD STORAGE (CDN)                PRIVATE ENCRYPTED STORAGE
Bucket: avatars                           Bucket: verification-evidence
- Public read via CDN                     - public = false
- Profile photos (1 to 6)                 - Ephemeral selfie media
- RLS: Owner insert/update/delete         - RLS: REVOKE ALL from client roles
- Safe, non-sensitive                     - Accessible ONLY via backend service-role
                                          - Auto-deleted after 30 days
```

### Security Invariants:
1. **Zero Client Access to Verification Media:** All database grants and storage policies on `verification-evidence` are completely revoked from `authenticated`, `anon`, and `public` roles.
2. **Zero Biometric Data to JESTER AI:** Verification media, face vectors, and raw selfie frames are **NEVER** passed to LLM prompts, context synthesizers, or external AI providers.
3. **Data Retention & Auto-Pruning:**
   - Once a verification session is approved or rejected, the raw capture media is scheduled for permanent hard deletion after **30 days** (retained briefly solely for fraud dispute resolution).
   - Only the boolean decision (`status = 'verified'`), provider reference ID, and timestamp are retained long-term.
4. **Zero PII Logging:** Backend application logs must never record facial vectors, biometric coordinates, or photo binary data.

---

## 14. Verification Provider Architecture

JESTER adopts an extensible provider abstraction interface (`VerificationProvider`), insulating the core architecture from vendor lock-in:

```python
class VerificationProvider(ABC):
    @abstractmethod
    async def create_session(self, user_id: uuid.UUID) -> VerificationSessionInit:
        """Initializes a secure capture session with provider."""
        pass

    @abstractmethod
    async def evaluate_liveness_and_match(
        self,
        session_id: str,
        selfie_media: bytes,
        reference_photo_url: str,
    ) -> VerificationEvaluationResult:
        """Evaluates liveness and face similarity score."""
        pass
```

### Supported Provider Backends:
- **`MockVerificationProvider`:** Offline deterministic provider for local testing and automated CI test suites (returns instant success/failure based on test fixtures).
- **`ExternalLivenessProvider` (e.g. Persona, Veriff, AWS Rekognition):** Production provider handling enterprise active liveness, anti-spoofing, and biometric comparison without storing biometric data in JESTER's application database.

---

## 15. Age & Identity Verification Boundaries

- **Age Verification in V1:** Self-declared birth date during onboarding (`birth_date`). The backend asserts that the user is **at least 18 years of age** (`age >= 18`). Users under 18 receive an immediate validation error (`HTTP 400 underage_not_permitted`).
- **Government ID Verification:** **Strictly out of scope for V1.** Requiring national passports or driver's licenses creates massive onboarding friction, alienates users, and introduces catastrophic data breach liability. Face-to-photo liveness verification provides sufficient authenticity for social connection.

---

## 16. Discoverability vs. Verification Matrix

Discoverability and Verification are completely orthogonal concepts:

| Quadrant | Status | UX Presentation | Discovery Feed Presence |
| :--- | :--- | :--- | :--- |
| **1. Discoverable + Verified** | `is_discoverable = true`, `is_verified = true` | Profile visible; displays `✓ Photo Verified` badge. | ✅ Appears normally with verified trust badge. |
| **2. Discoverable + Unverified**| `is_discoverable = true`, `is_verified = false` | Profile visible; no badge displayed. | ✅ Appears normally (if photo present). |
| **3. Private + Verified** | `is_discoverable = false`, `is_verified = true` | Profile hidden from search; visible only via direct link to accepted connections. | 🚫 Excluded from Discovery feed. |
| **4. Private + Unverified** | `is_discoverable = false`, `is_verified = false` | Profile hidden from search; no badge. | 🚫 Excluded from Discovery feed. |

---

## 17. Security Threat Model & Mitigations

| Threat | Attack Vector | Severity | V1 Mitigation |
| :--- | :--- | :---: | :--- |
| **Presentation Spoof** | Showing photo of photo or tablet screen to camera. | High | 3D liveness detection, micro-movement texture analysis, reflection checks. |
| **Deepfake Video** | Real-time generative face-swap software. | High | Temporal artifact analysis, challenge-response gestures (blink, turn head). |
| **Bait-and-Switch** | User verifies face, then replaces photo with celebrity. | High | **Photo Hash Invariant:** Changing primary photo resets verification to `needs_review` or `expired`. |
| **Mass Bot Creation** | Scripted account registrations via automated tools. | Medium | Supabase Auth rate-limiting, disposable email domain blocking, connection caps. |
| **Malicious Reporting** | Coordinated false reporting to get an innocent user banned.| Medium | Reports require distinct unlinked accounts; automated review threshold only triggers `under_review`, never automatic ban. |
| **Account Takeover** | Attacker compromises credentials and alters profile. | High | Asymmetric JWKS JWT verification; re-authentication required for sensitive profile changes. |

---

## 18. Database Architecture Specification

To implement the Trust & Verification system cleanly, JESTER introduces 6 structured entities:

```text
public.profile_photos (User Gallery)
├── id: uuid PRIMARY KEY DEFAULT gen_random_uuid()
├── user_id: uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE
├── url: text NOT NULL
├── is_primary: boolean NOT NULL DEFAULT false
├── sort_order: smallint NOT NULL DEFAULT 0
├── created_at: timestamptz NOT NULL DEFAULT now()
└── CONSTRAINT unique_primary_per_user EXCLUDE USING gist (user_id WITH =) WHERE (is_primary = true)

public.user_verifications (Active Trust State)
├── user_id: uuid PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE
├── status: text NOT NULL CHECK (status IN ('not_started', 'pending', 'verified', 'failed', 'needs_review', 'expired', 'revoked'))
├── provider: text NOT NULL DEFAULT 'internal'
├── confidence_score: numeric(4,3) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0)
├── verified_at: timestamptz
├── expires_at: timestamptz
└── updated_at: timestamptz NOT NULL DEFAULT now()

public.verification_attempts (Audit Trail)
├── id: uuid PRIMARY KEY DEFAULT gen_random_uuid()
├── user_id: uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE
├── session_token: text UNIQUE NOT NULL
├── status: text NOT NULL CHECK (status IN ('initiated', 'passed', 'failed', 'flagged'))
├── failure_reason: text
├── attempt_ip_hash: text
└── created_at: timestamptz NOT NULL DEFAULT now()

public.reports (Community Safety Signals)
├── id: uuid PRIMARY KEY DEFAULT gen_random_uuid()
├── reporter_id: uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE
├── reported_id: uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE
├── reason: text NOT NULL CHECK (reason IN ('fake_profile', 'harassment', 'inappropriate_content', 'spam_scam', 'underage', 'other'))
├── details: text
├── status: text NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'dismissed'))
├── created_at: timestamptz NOT NULL DEFAULT now()
└── CONSTRAINT no_self_report CHECK (reporter_id <> reported_id)

public.user_blocks (Dedicated Two-Way Blocking)
├── id: uuid PRIMARY KEY DEFAULT gen_random_uuid()
├── blocker_id: uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE
├── blocked_id: uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE
├── created_at: timestamptz NOT NULL DEFAULT now()
├── CONSTRAINT no_self_block CHECK (blocker_id <> blocked_id),
└── CONSTRAINT unique_block_pair UNIQUE (blocker_id, blocked_id)

public.moderation_actions (Disciplinary Audit Log)
├── id: uuid PRIMARY KEY DEFAULT gen_random_uuid()
├── user_id: uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE
├── action: text NOT NULL CHECK (action IN ('warning', 'limit_rate', 'put_under_review', 'suspend', 'ban', 'lift_restriction'))
├── reason: text NOT NULL
├── expires_at: timestamptz
├── issued_by: uuid REFERENCES public.profiles(id)
└── created_at: timestamptz NOT NULL DEFAULT now()
```

---

## 19. API Architecture & Endpoint Contracts

All trust and safety operations are cleanly partitioned into secure REST endpoints:

### 19.1 Profile Photos API
- `GET /v1/profiles/me/photos` — List own photos with order and primary flags.
- `POST /v1/profiles/me/photos` — Upload and attach a new profile photo (max 6).
- `PATCH /v1/profiles/me/photos/{photo_id}/primary` — Set specified photo as primary (resets verification if face changes).
- `DELETE /v1/profiles/me/photos/{photo_id}` — Delete a photo.

### 19.2 Verification API
- `POST /v1/verification/face/session` — Initialize ephemeral face verification session (returns `session_token`, valid 5 mins).
- `POST /v1/verification/face/submit` — Submit encrypted selfie capture payload for evaluation.
- `GET /v1/verification/face/status` — Get authenticated user's current verification state and badge status.

### 19.3 Safety, Reporting & Blocking API
- `POST /v1/safety/block` — Block a target user (`target_user_id`). Immediately triggers reciprocal 404.
- `POST /v1/safety/unblock` — Unblock a target user.
- `GET /v1/safety/blocks` — List users blocked by caller.
- `POST /v1/safety/report` — Submit a structured safety report (`reported_user_id`, `reason`, `details`).

---

## 20. Frontend & UX Behavioral States

```text
+-------------------------------+---------------------------------------------------+
| UX STATE                      | USER INTERFACE & BEHAVIORAL BEHAVIOR              |
+-------------------------------+---------------------------------------------------+
| 1. No Photo                   | Banner on profile: "Add a photo to appear in      |
|                               | Discovery." Profile hidden from search feed.      |
+-------------------------------+---------------------------------------------------+
| 2. Has Photos (Unverified)    | Profile active in Discovery. "Get Verified" card  |
|                               | gently visible in profile settings. No badge.     |
+-------------------------------+---------------------------------------------------+
| 3. Verification Pending       | Badge in review state: "Verifying...". Normal     |
|                               | browsing active.                                  |
+-------------------------------+---------------------------------------------------+
| 4. Verification Succeeded     | Subtle green/accent checkmark badge ✓ Photo       |
|                               | Verified rendered next to display name.           |
+-------------------------------+---------------------------------------------------+
| 5. Verification Failed        | Polite notification: "We couldn't confirm your    |
|                               | selfie. Ensure good lighting and try again."      |
+-------------------------------+---------------------------------------------------+
| 6. Rate Limited (Throttled)   | Action snackbar: "You've sent several connection  |
|                               | requests today. Take a break and explore later."  |
+-------------------------------+---------------------------------------------------+
| 7. Account Under Review       | Friendly banner: "Your account is temporarily     |
|                               | under review by our safety team."                 |
+-------------------------------+---------------------------------------------------+
| 8. Account Suspended / Banned | Full-screen barrier: "This account has been       |
|                               | suspended for violating JESTER safety policies."  |
+-------------------------------+---------------------------------------------------+
```

---

## 21. Trust + Discovery Feed Experience

1. **Candidate Feed Display:** Verified candidates display the subtle `✓ Photo Verified` badge. Unverified candidates display their standard primary photo without penalty.
2. **Relevance Weighting:** Being verified provides a minor positive quality weight ($+5\%$ soft boost) in the recommendation feed algorithm to reward authenticity, but never suppresses unverified users with quality profiles.
3. **User Search Preference:** Users can toggle `preferences.verified_only = true` in their discovery settings if they strictly want to browse verified profiles.

---

## 22. JESTER AI + Trust Boundaries

JESTER AI ingests trust state solely to protect safety and ensure contextually appropriate conversation guidance:

### What JESTER AI Receives:
```json
{
  "trust_context": {
    "is_verified": true,
    "has_public_photo": true,
    "moderation_status": "active",
    "can_message": true
  }
}
```

### What JESTER AI NEVER Receives:
- 🚫 Verification selfie media or raw photos.
- 🚫 Biometric similarity vectors or facial geometry points.
- 🚫 Abuse report contents, descriptions, or reporter identities.
- 🚫 Historical disciplinary notes.

---

## 23. Privacy-Conscious Telemetry & Analytics

Telemetry tracks platform safety metrics without logging sensitive personal data:

### Safe Telemetry Events:
- `photo_upload_completed` (user_id, photo_count, is_primary)
- `photo_deleted` (user_id, remaining_count)
- `verification_session_started` (user_id, attempt_number)
- `verification_evaluation_completed` (user_id, result: 'passed' | 'failed', latency_ms)
- `block_created` (blocker_id, blocked_id)
- `report_submitted` (reporter_id, reason)
- `moderation_action_taken` (target_user_id, action_type)

### Strictly Banned Telemetry Data:
- 🚫 Never log raw facial image binaries or Base64 strings.
- 🚫 Never log facial feature coordinates or biometric templates.
- 🚫 Never log government IDs or physical address tokens.

---

## 24. V1 Scope vs. Future Roadmap

| Capability | In Scope for V1 | Deferred to Future (V1.1 / V2) |
| :--- | :--- | :--- |
| **Profile Photos** | Up to 6 photos, primary selector, automated NSFW filter | Video profile clips, smart photo reordering |
| **Face Verification** | Liveness selfie vs. primary profile photo | 3D depth-sensor scanning, biometric continuous auth |
| **Verification Badge** | `✓ Photo Verified` badge on profile & discovery | Multi-tier verification badges (e.g. Identity Verified)|
| **Blocking System** | Reciprocal 2-way block with zero existence leakage | Domain / IP range blocking |
| **Reporting System** | 6 structured abuse categories, auto-review threshold | Machine-learning proactive toxicity detection in chat |
| **Moderation Engine** | Manual review queue, rate limiting, suspension, ban | Automated community moderation appeals portal |
| **Age Verification** | Declared birth date validation ($\ge 18$ check) | Government ID scanning / digital ID NFC verification |
| **AI Trust Awareness** | Awareness of verified badge & moderation limits | Proactive conversational risk intervention |

---

## 25. Conflict Audit & Code Reconciliation

1. **Storage Bucket & Photo Management:**
   - *Current Code Reality:* `public.profiles` has a single `avatar_url: text` column; `019_storage.sql` configures an `avatars` bucket.
   - *Architecture Resolution:* V1 specification defines `public.profile_photos` (1:N gallery) while keeping `profiles.avatar_url` as the cached primary avatar reference for backward compatibility.
2. **Blocking Co-Location vs. Dedicated Table:**
   - *Current Code Reality:* Blocking is currently recorded as `connections.status = 'blocked'` and `connections.blocked_by`.
   - *Architecture Resolution:* To allow users to block someone *before* an invitation exists (e.g. directly from Discovery), the architecture introduces `public.user_blocks`, updating `is_user_blocked()` to check both sources.
3. **Face Verification vs. Profile Photo Invariant:**
   - *Audit Confirmation:* Confirmed compliance with Invariant 9 in `docs/SECURITY.md`. Verification selfie media is strictly segregated in `verification-evidence` and never displayed publicly.
