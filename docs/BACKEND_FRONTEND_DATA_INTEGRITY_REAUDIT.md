# BACKEND / FRONTEND DATA INTEGRITY RE-AUDIT REPORT
**Timestamp:** 2026-09-08 / 2026-09-09  
**Status:** FORENSICALLY VERIFIED & RESOLVED  
**Classification:** Diagnostic Contradiction & Runtime Data Integrity Re-Investigation  
**Auditor:** Jester Engineering Team

---

## 1. Executive Summary & Contradiction Resolution

### 1.1 The Contradiction
The previous audit report (`docs/BACKEND_FRONTEND_DATA_INTEGRITY_AUDIT.md`) asserted:
> **OVERALL STATUS: PASS**

However, inspecting the live developer diagnostic lab at `/__debug/backend-audit` visibly displayed:
- `Mercury Sign: null (DB Col Missing)`
- `Venus Sign: null (DB Col Missing)`
- `Mars Sign: null (DB Col Missing)`
- Forensic Status Matrix Row: `Derived Safe Profile | astro_safe_profile | PARTIAL | Stores Sun, Moon, Asc, Elements. Mercury/Venus/Mars columns omitted in DB schema.`
- Forensic Status Matrix Row: `API Response (/safe-astro) | SafeDerivedAstrologyResponse | PARTIAL | Populated on /recalculate, but returns null for planetary signs on cached reads.`

This created an undeniable, severe contradiction between the written documentation and the running visual environment.

### 1.2 The Forensic Root Cause of the Contradiction
Forensic tracing of git history, source code, and running processes revealed the exact mechanism of this contradiction:

1. **Static Pre-Fix Matrix Left in the Debug Component:**  
   When the previous engineer initially investigated the pipeline, they authored `frontend/src/ui/BackendAuditDebugPage.tsx` and hardcoded static table rows documenting their *preliminary discovery findings* (namely that `astro_safe_profile` lacked columns and `/safe-astro` returned null for planetary signs).
2. **Failure to Update Diagnostic Matrix After Backend Fix:**  
   The previous engineer modified `backend/app/astrology/router.py` to join `astro_private` and derive planetary signs via `longitude_to_sign`. They ran targeted unit tests that passed in memory, but **they never updated the static diagnostic matrix in `BackendAuditDebugPage.tsx`**.
3. **Misleading Diagnostic Labeling (`DB Col Missing`):**  
   The author of the debug page assumed that if a property in `SafeDerivedAstrologyResponse` did not exist as an explicit column in `astro_safe_profile`, it represented a "Missing DB Column". In reality, the architecture intentionally stores raw longitudes in `astro_private` (server-controlled) and derives safe planetary signs dynamically in the API response DTO. The debug label `(DB Col Missing)` was a diagnostic misconception, not a schema failure.
4. **Unauthenticated Access State:**  
   When `/__debug/backend-audit` was opened without an active authenticated session (or prior to browser sign-in), the page rendered empty placement slots with fallback labels `null (DB Col Missing)`, while the static matrix below displayed the hardcoded `PARTIAL` claims.

---

## 2. Identity & Persistence Forensic Analysis

### 2.1 Classification of User `44444444-4444-4444-4444-444444444444`
Forensic tracing evaluated User `44444444-4444-4444-4444-444444444444`:
- **Classification:** **C. Seeded Development User**
- **Provenance:** Created and populated by `scripts/seed_farna_user.py` using the Supabase GoTrue Admin API.
- **Email:** `farna@jester.app`
- **Database Presence:**
  - `auth.users`: Row exists with `id = 44444444-4444-4444-4444-444444444444`, `email = farna@jester.app`.
  - `public.profiles`: Row exists with `display_name = Farna`, `is_discoverable = true`.
  - `public.birth_data`: Row exists with `birth_date = 1995-11-15`, `birth_time = 18:30:00`, `birth_timezone = Asia/Tbilisi`, `latitude = 41.7151`, `longitude = 44.8271`, `data_version = 5`.
- **Authentication Flow:**
  1. Browser submits credentials to Supabase Auth (`supabase.auth.signInWithPassword`).
  2. Supabase GoTrue issues a signed HS256 JWT (development environment).
  3. Browser stores session in `localStorage` under `sb-127-auth-token`.
  4. API requests include `Authorization: Bearer <JWT>`.
  5. FastAPI `get_current_user` (`backend/app/auth/dependencies.py`) decodes JWT `sub` and resolves `AuthenticatedUser(id=UUID('44444444-4444-4444-4444-444444444444'))`.

**Finding on Previous Audit:** Because `44444444-4444-4444-4444-444444444444` was a seeded identity, relying solely on this record left true runtime end-to-end user registration and dynamic onboarding unproven. A true dynamic A/B test with clean, random identities was required.

---

## 3. Database Schema & Derivation Architecture

### 3.1 Schema Inspection: `astro_safe_profile` vs `astro_private`

#### Migration `005_astro_private.sql`:
Stores exact, high-precision astronomical coordinates computed by PySwissEph:
```sql
CREATE TABLE public.astro_private (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    source_birth_data_version INTEGER NOT NULL,
    engine_version TEXT NOT NULL,
    sun_longitude DOUBLE PRECISION NOT NULL,
    moon_longitude DOUBLE PRECISION NOT NULL,
    mercury_longitude DOUBLE PRECISION NOT NULL,
    venus_longitude DOUBLE PRECISION NOT NULL,
    mars_longitude DOUBLE PRECISION NOT NULL,
    jupiter_longitude DOUBLE PRECISION NOT NULL,
    saturn_longitude DOUBLE PRECISION NOT NULL,
    uranus_longitude DOUBLE PRECISION NOT NULL,
    neptune_longitude DOUBLE PRECISION NOT NULL,
    pluto_longitude DOUBLE PRECISION NOT NULL,
    ascendant_longitude DOUBLE PRECISION,
    houses JSONB,
    retrogrades JSONB,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### Migration `006_astro_safe_profile.sql`:
Stores safe, coarsened, and non-sensitive astrological attributes:
```sql
CREATE TABLE public.astro_safe_profile (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    source_birth_data_version INTEGER NOT NULL,
    engine_version TEXT NOT NULL,
    sun_sign TEXT NOT NULL,
    moon_sign TEXT NOT NULL,
    ascendant_sign TEXT,
    element_primary TEXT NOT NULL,
    modality_primary TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3.2 Architectural Analysis: Derivation vs Redundant Columns
- **Architecture Invariant:** As defined in `AGENTS.md` ("Security & Privacy Invariants"), `astro_private` is server-controlled and must never be exposed directly to clients. The client receives only safe DTOs (`SafeDerivedAstrologyResponse`).
- **Storage Strategy:** `public.astro_safe_profile` acts as the persisted safe cache for core self metrics (Sun, Moon, Ascendant, Primary Element, Primary Modality).
- **Planetary Sign Derivation:** The API contract `SafeDerivedAstrologyResponse` includes `mercury_sign`, `venus_sign`, and `mars_sign`. The backend derives these signs by joining `astro_private` on `user_id` and passing `mercury_longitude`, `venus_longitude`, `mars_longitude` through `longitude_to_sign`.
- **Verdict on `(DB Col Missing)`:** `astro_safe_profile` was never intended to duplicate zodiac signs for all ten planetary bodies. Storing them as redundant string columns when exact longitudes already exist in `astro_private` would introduce schema denormalization and synchronization overhead. The debug UI label `(DB Col Missing)` was factually wrong and has been corrected.

---

## 4. Architectural Correction: Actual Client-Side Persistence Endpoint

The previous audit document contained a flawed architecture diagram stating:
`A[Registered User Form Input] -->|BirthDataPayload| B[PUT /v1/birth-data]`

### Forensic Fact:
There is **no `PUT /v1/birth-data` route** in the FastAPI backend. Calling `PUT /v1/birth-data` returns `404 Not Found`.

The actual production flow implemented in `frontend/src/core/api/endpoints.ts` is:
1. **Direct PostgREST Upsert under PostgreSQL RLS:**
   ```typescript
   await supabase.from("birth_data").upsert({
     user_id: userId,
     birth_date: data.birth_date,
     birth_time: data.birth_time || null,
     birth_time_precision: data.birth_time_precision,
     birth_timezone: data.birth_timezone,
     latitude: data.latitude || null,
     longitude: data.longitude || null,
     place_label: data.place_label || null,
     updated_at: new Date().toISOString(),
   });
   ```
2. **Immediate Recalculation Trigger:**
   ```typescript
   return apiRequest<SafeDerivedAstrologyResponse>(
     "/v1/astrology/profile/recalculate",
     { method: "POST" }
   );
   ```

This complies with `AGENTS.md` Section *Direct Supabase / Database Access*:
> "Direct frontend Supabase access is acceptable only where the existing architecture explicitly permits it and RLS/grants support the intended client-owned flow."

---

## 5. Empirical Live A/B Verification (Two Fresh Identities)

To eliminate all ambiguity from seeded fixtures, an automated live test was executed against the running FastAPI server and Supabase PostgreSQL instance using two freshly generated UUIDs with completely distinct birth inputs.

### 5.1 Test Subjects

| Attribute | User A (London Spring Equinox) | User B (Tbilisi Autumn Evening) |
|---|---|---|
| **User ID** | `21eaa989-1854-4957-b465-7ac68060efa7` | `01c08945-7005-47a3-a439-a176caef039b` |
| **Email** | `audit_a@jester.test` | `audit_b@jester.test` |
| **Birth Date** | `1990-03-21` | `1995-11-15` |
| **Birth Time** | `06:00:00` | `18:30:00` |
| **Timezone** | `UTC` | `Asia/Tbilisi` (UTC+4) |
| **Coordinates** | `51.5074, -0.1278` (London) | `41.7151, 44.8271` (Tbilisi) |

---

### 5.2 Exact SQL State Captured from Database

#### Table `public.birth_data`:
```
User A: user_id=21eaa989-1854-4957-b465-7ac68060efa7, birth_date=1990-03-21, birth_time=06:00:00, birth_timezone='UTC', lat=51.5074, lon=-0.1278, data_version=1
User B: user_id=01c08945-7005-47a3-a439-a176caef039b, birth_date=1995-11-15, birth_time=18:30:00, birth_timezone='Asia/Tbilisi', lat=41.7151, lon=44.8271, data_version=1
```

#### Table `public.astro_private` (Server-Only Longitudes):
```
User A:
  sun_longitude:       0.359226°   (Aries)
  moon_longitude:    289.077335°   (Capricorn)
  mercury_longitude:   2.486366°   (Aries)
  venus_longitude:   314.241550°   (Aquarius)
  mars_longitude:    307.109290°   (Aquarius)
  ascendant_longitude: 356.099657° (Pisces)

User B:
  sun_longitude:     232.745648°   (Scorpio)
  moon_longitude:    144.074798°   (Leo)
  mercury_longitude: 228.290576°   (Scorpio)
  venus_longitude:   255.142053°   (Sagittarius)
  mars_longitude:    258.762911°   (Sagittarius)
  ascendant_longitude: 69.139895°  (Gemini)
```

#### Table `public.astro_safe_profile`:
```
User A: sun_sign='Aries', moon_sign='Capricorn', ascendant_sign='Pisces', element='Fire', modality='Cardinal'
User B: sun_sign='Scorpio', moon_sign='Leo', ascendant_sign='Gemini', element='Fire', modality='Fixed'
```

---

### 5.3 Exact API Responses: Recalculate vs Cached Read

#### User A (London) API Output:
**POST `/v1/astrology/profile/recalculate`:**
```json
{
  "user_id": "21eaa989-1854-4957-b465-7ac68060efa7",
  "sun_sign": "Aries",
  "moon_sign": "Capricorn",
  "ascendant_sign": "Pisces",
  "mercury_sign": "Aries",
  "venus_sign": "Aquarius",
  "mars_sign": "Aquarius",
  "element_primary": "Fire",
  "modality_primary": "Cardinal",
  "source_birth_data_version": 1,
  "engine_version": "1.0.0",
  "updated_at": "2026-09-08T21:57:54.554095Z"
}
```

**GET `/v1/astrology/profile/safe-astro` (Cached Read):**
```json
{
  "user_id": "21eaa989-1854-4957-b465-7ac68060efa7",
  "sun_sign": "Aries",
  "moon_sign": "Capricorn",
  "ascendant_sign": "Pisces",
  "mercury_sign": "Aries",
  "venus_sign": "Aquarius",
  "mars_sign": "Aquarius",
  "element_primary": "Fire",
  "modality_primary": "Cardinal",
  "source_birth_data_version": 1,
  "engine_version": "1.0.0",
  "updated_at": "2026-09-08T21:57:54.554095Z"
}
```

#### User B (Tbilisi) API Output:
**POST `/v1/astrology/profile/recalculate`:**
```json
{
  "user_id": "01c08945-7005-47a3-a439-a176caef039b",
  "sun_sign": "Scorpio",
  "moon_sign": "Leo",
  "ascendant_sign": "Gemini",
  "mercury_sign": "Scorpio",
  "venus_sign": "Sagittarius",
  "mars_sign": "Sagittarius",
  "element_primary": "Fire",
  "modality_primary": "Fixed",
  "source_birth_data_version": 1,
  "engine_version": "1.0.0",
  "updated_at": "2026-09-08T21:57:54.636051Z"
}
```

**GET `/v1/astrology/profile/safe-astro` (Cached Read):**
```json
{
  "user_id": "01c08945-7005-47a3-a439-a176caef039b",
  "sun_sign": "Scorpio",
  "moon_sign": "Leo",
  "ascendant_sign": "Gemini",
  "mercury_sign": "Scorpio",
  "venus_sign": "Sagittarius",
  "mars_sign": "Sagittarius",
  "element_primary": "Fire",
  "modality_primary": "Fixed",
  "source_birth_data_version": 1,
  "engine_version": "1.0.0",
  "updated_at": "2026-09-08T21:57:54.636051Z"
}
```

### 5.4 Cross-User Data Isolation Check
User B requested User A's safe astrology profile via `GET /v1/astrology/people/21eaa989-1854-4957-b465-7ac68060efa7/safe-astro`:
- **Result:** HTTP 200 returned because User A is marked `is_discoverable = true`.
- **Payload Inspection:** Returned only safe sign strings (`Aries`, `Capricorn`, `Pisces`, `Aquarius`).
- **Privacy Verification:** Zero raw longitudes, zero house angles, zero birth times, zero coordinates, and zero birth places leaked.

---

## 6. Real-Flow Content Resolution Verification (Georgian Locale `ka`)

We verified end-to-end narrative resolution by calling `POST /v1/interpretations/resolve-natal` for both User A and User B across all 8 dimensions.

### 6.1 User A Resolution Results (London: Aries / Capricorn / Pisces / Aquarius)

| Dimension | Slot / Title | Resolved Asset ID | Tone | Status |
|---|---|---|---|---|
| `self.identity` | იდენტობა და არსი | `self.identity.sun_aries.v1` | `witty` | **PASS** |
| `self.emotional` | ემოციური სამყარო | `self.emotional.moon_capricorn.v1` | `grounded` | **PASS** |
| `self.persona` | სოციალური ნიღაბი (ასცენდენტი) | `self.persona.rising_pisces.v1` | `enigmatic` | **PASS** |
| `self.cognition` | აზროვნება და კომუნიკაცია (მერკური) | `self.cognition.mercury_aries.v1` | `bold` | **PASS** |
| `self.relation` | მიზიდულობა და ურთიერთობა (ვენერა) | `self.relation.venus_aquarius.v1` | `quirky` | **PASS** |
| `self.action` | ენერგია და მოქმედება (მარსი) | `self.action.mars_aquarius.v1` | `bold` | **PASS** |
| `self.element` | დომინანტური სტიქია (ცეცხლი) | `self.element.fire_dominant.v1` | `witty` | **PASS** |
| `self.modality` | ცხოვრების დინამიკა (კარდინალური) | `self.modality.cardinal_dominant.v1` | `soft` | **PASS** |

**Sample User A Georgian Text Excerpt (Mars in Aquarius — `self.action.mars_aquarius.v1`):**
> „შენი მოქმედება არაპროგნოზირებადია — როცა ყველა მარჯვნივ მიდის, შენ პრინციპულად მარცხნივ უხვევ...“

---

### 6.2 User B Resolution Results (Tbilisi: Scorpio / Leo / Gemini / Sagittarius)

| Dimension | Slot / Title | Resolved Asset ID | Tone | Status |
|---|---|---|---|---|
| `self.identity` | იდენტობა და არსი | `self.identity.sun_scorpio.v1` | `witty` | **PASS** |
| `self.emotional` | ემოციური სამყარო | `self.emotional.moon_leo.v1` | `bold` | **PASS** |
| `self.persona` | სოციალური ნიღაბი (ასცენდენტი) | `self.persona.rising_gemini.v1` | `bold` | **PASS** |
| `self.cognition` | აზროვნება და კომუნიკაცია (მერკური) | `self.cognition.mercury_scorpio.v1` | `dramatic` | **PASS** |
| `self.relation` | მიზიდულობა და ურთიერთობა (ვენერა) | `self.relation.venus_sagittarius.v1` | `jester` | **PASS** |
| `self.action` | ენერგია და მოქმედება (მარსი) | `self.action.mars_sagittarius.v1` | `cocky` | **PASS** |
| `self.element` | დომინანტური სტიქია (ცეცხლი) | `self.element.fire_dominant.v1` | `witty` | **PASS** |
| `self.modality` | ცხოვრების დინამიკა (ფიქსირებული) | `self.modality.fixed_dominant.v1` | `witty` | **PASS** |

**Sample User B Georgian Text Excerpt (Venus in Sagittarius — `self.relation.venus_sagittarius.v1`):**
> „შენთვის მიმზიდველია ის, ვინც შენს ჰორიზონტს აფართოებს — ადამიანი, რომელთანაც შეიძლება დილის ოთხ საათზე ფილოსოფიაზე იკამათო...“

**Content Integrity Metrics:**
- **Resolved Dimensions:** 8 / 8 (100%)
- **Null / Failed Resolutions:** 0 / 8 (0%)
- **Zero-Jargon Compliance:** 100% verified (no houses, degrees, or planetary ruler jargon).

---

## 7. Direct Diagnostic Lab Alignment

To ensure that the live diagnostic lab never again contradicts system reality, `frontend/src/ui/BackendAuditDebugPage.tsx` was updated:
1. **Removed Misleading Static Claims:** The static rows claiming `PARTIAL: Mercury/Venus/Mars columns omitted in DB schema` and `returns null for planetary signs on cached reads` were replaced with the verified architectural description.
2. **Updated Placement Fallbacks:** Corrected fallback labels from `null (DB Col Missing)` and `null (Not Returned by API)` to `null (Not calculated)`.
3. **Live Verification:** Navigated to `http://localhost:3000/__debug/backend-audit` under an active authenticated session. All 10 verification gates now report **PASS**, and the live placements display:
   - ☀️ **Sun Sign:** `Scorpio`
   - 🌙 **Moon Sign:** `Leo`
   - 🌅 **Ascendant:** `Gemini`
   - ☿ **Mercury Sign:** `Scorpio`
   - ♀ **Venus Sign:** `Sagittarius`
   - ♂ **Mars Sign:** `Sagittarius`

---

## 8. Final Forensic Integrity Matrix

| Subsystem / Layer | Pre-Reaudit Status | Current Verified Status | Forensic Evidence |
|---|---|---|---|
| **PostgreSQL Persistence** | Contradicted | **PASS** | Real `public.birth_data` rows verified via SQL inspection for fresh random users. |
| **Swiss Ephemeris Engine** | Unverified in report | **PASS** | Deterministic calculations validated across UTC and Asia/Tbilisi zones. |
| **Private Astrology Boundary** | Unverified | **PASS** | High-precision longitudes stored strictly in `public.astro_private`. |
| **Derived Safe Profile API** | Visible FAIL in Debug Lab | **PASS** | `GET /v1/astrology/profile/safe-astro` returns all 6 signs identically on cached reads and recalculation. |
| **User Data Isolation** | Seeded only | **PASS** | User A vs User B completely isolated; no birth coordinates or private longitudes exposed. |
| **Georgian Content Resolution** | Unverified across flow | **PASS** | 100% resolution for all 8 dimensions in `ka` locale without fallback degradation. |
| **Visual Debug Lab Alignment** | Direct Contradiction | **PASS** | Debug lab matrix and dynamic calculations now agree 100% with backend runtime truth. |
