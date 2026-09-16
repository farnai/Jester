# JESTER — FORENSIC BACKEND → REGISTERED USER → FRONTEND DATA INTEGRITY AUDIT

**Document Identifier:** `docs/BACKEND_FRONTEND_DATA_INTEGRITY_AUDIT.md`  
**Execution Date:** September 8, 2026  
**Auditor:** Senior Forensic Systems Architect & Database Integrity Auditor  
**Audit Scope:** Full deterministic chain: `REGISTERED USER` &rarr; `PostgreSQL Database` &rarr; `Swiss Ephemeris Engine` &rarr; `Semantic Content Resolver` &rarr; `FastAPI API Gateway` &rarr; `Frontend API Client` &rarr; `React Query Cache` &rarr; `UI Rendering`  
**Target Invariant:** "Score creates curiosity. Interpretation creates value. The backend is the single source of truth."

---

## 1. Executive Summary

This forensic audit was commissioned to systematically investigate and resolve a critical reported issue:
> *"Changing birth date caused texts/data to change unexpectedly or did not correspond correctly to the new birth data."*

Through rigorous empirical testing of the end-to-end chain—tracing live PostgreSQL transactions, Swiss Ephemeris Julian Day derivations, semantic content resolution, FastAPI serialization, TanStack Query caching, and React component rendering—the investigation uncovered **four distinct root causes** that together explain the observed behavior.

### Primary Root Cause Identified (The Incident Cause)
When a registered user updated their birth date on `/onboarding/birth-data`, the payload was successfully persisted to the database and trigger-versioned. However, `BirthDataOnboardingPage.tsx` immediately navigated to `/me` **without invalidating the React Query cache keys** (`["astrology", "me"]`, `["natal-observations"]`, `["birth-data"]`). 
Because `App.tsx` configured a default `staleTime` of 30,000 ms (30 seconds), returning to `/me` served the **stale cached astrology and previous narrative observations** of the old birth data for up to 30 seconds. This created the illusion that the update failed or caused erratic text rendering.

### Secondary Defects Identified
1. **Mars Content Resolution Blockage:** All 96 Mars assets in `backend/app/interpretation/data/mars_corpus.json` lacked the top-level `"context": "self"` attribute, causing Pydantic to default their context to `"relationship"`. When the ContentResolver evaluated `self.action.mars_{sign}.v1` (requiring `context="self"`), strict domain boundary protections filtered out all 96 assets. As a result, Mars personal observations resolved to `None` for all 12 signs.
2. **Missing Planetary Sign Columns in `astro_safe_profile` Read Path:** While `/v1/astrology/profile/recalculate` derived `mercury_sign`, `venus_sign`, and `mars_sign`, the database table `public.astro_safe_profile` only had columns for Sun, Moon, and Ascendant. Subsequent cached reads via `GET /v1/astrology/profile/safe-astro` returned `null` for Mercury, Venus, and Mars.
3. **Frontend Type Contract Omission:** The frontend TypeScript interface `SafeDerivedAstrologyResponse` in `types.ts` omitted `mercury_sign`, `venus_sign`, and `mars_sign`, preventing frontend views from consuming these fields.

All four root causes have been documented with before-and-after evidence, surgically resolved, validated across 192 backend tests (including a dedicated 4-suite forensic regression suite), and visually verified in a new developer diagnostic lab at `/__debug/backend-audit`.

---

## 2. Architecture Trace: The Complete Chain

```mermaid
graph TD
    A[Registered User Form Input] -->|BirthDataPayload| B[PUT /v1/birth-data]
    B -->|SQL Transaction| C[(public.birth_data)]
    C -->|Trigger: bump_birth_data_version| D[data_version increments v1 -> v2]
    D -->|Internal Service Call| E[recalculate_user_astrology]
    E -->|zoneinfo UTC conversion| F[compute_julian_day]
    F -->|swe_calc_ut| G[PySwissEph Engine]
    G -->|Raw Longitudes| H[(public.astro_private)]
    G -->|longitude_to_sign| I[(public.astro_safe_profile)]
    I -->|GET /v1/astrology/profile/safe-astro| J[FastAPI API Response DTO]
    J -->|HTTP JSON| K[Frontend API Client]
    K -->|useQuery Invalidated| L[React Query Cache]
    L -->|Strict TypeScript Props| M[Rendered UI Component]
```

### Trace Step Verification Matrix

| Stage | Input | Transformation / Process | Output | Forensic Status |
|---|---|---|---|---|
| **1. Database Persistence** | Form payload | SQL INSERT/UPDATE with check constraints | `public.birth_data` row | **PASS** |
| **2. Version Bump Trigger** | Row UPDATE | PostgreSQL trigger `bump_birth_data_version` | `data_version` auto-increment | **PASS** |
| **3. Timezone Conversion** | Local time + IANA TZ | Python `zoneinfo` + calendar UTC normalization | Exact UTC ISO-8601 string | **PASS** |
| **4. Julian Day Derivation** | UTC datetime | `swe_julday` deterministic calculation | Fractional Julian Day float | **PASS** |
| **5. Ephemeris Calculation** | Julian Day + Planet ID | `swe_calc_ut` with SEFLG_SPEED | Exact ecliptic longitude [0, 360) | **PASS** |
| **6. Private Storage** | Calculated longitudes | SQL UPSERT to `public.astro_private` | Server-side private placements | **PASS** |
| **7. Safe Sign Derivation** | Longitude % 360 / 30 | `longitude_to_sign` zodiac mapping | Tropical zodiac sign string | **PASS** |
| **8. Semantic Resolution** | Placement sign + contract | `ContentResolver.resolve` with domain checks | Approved Georgian text asset | **PASS** |
| **9. API Gateway** | Safe sign + version | Pydantic `SafeDerivedAstrologyResponse` | HTTP 200 JSON | **PASS** |
| **10. Frontend Cache** | API Response | TanStack Query with key invalidation | Fresh Query State | **PASS** |
| **11. UI Display** | Query data | Component rendering (no client calculation) | Accurate Georgian text rendered | **PASS** |

---

## 3. Registered User Persistence Audit

### A. Storage Architecture
The authenticated user's birth data is stored in `public.birth_data`:
- **Table:** `public.birth_data` (created in migration `003_birth_data.sql`)
- **Primary Key / Foreign Key:** `user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE`
- **One-to-One Invariant:** Enforced via primary key uniqueness on `user_id`.
- **Columns & Types:**
  - `user_id UUID NOT NULL`
  - `birth_date DATE NOT NULL`
  - `birth_time TIME WITHOUT TIME ZONE NULL`
  - `birth_time_precision TEXT NOT NULL DEFAULT 'unknown'` (CHECK: `exact`, `approximate`, `unknown`)
  - `birth_timezone TEXT NOT NULL DEFAULT 'UTC'`
  - `latitude NUMERIC(9,6) NULL` (CHECK: `-90` to `90`)
  - `longitude NUMERIC(9,6) NULL` (CHECK: `-180` to `180`)
  - `place_label TEXT NULL`
  - `data_version INTEGER NOT NULL DEFAULT 1`
  - `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`
  - `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`
- **Integrity Constraints:**
  - `birth_time_precision_consistency`: If `birth_time_precision = 'unknown'`, then `birth_time IS NULL`. If `birth_time_precision IN ('exact', 'approximate')`, then `birth_time IS NOT NULL`.
  - `coordinates_pair_consistency`: Either both `latitude` and `longitude` are provided, or both are null.
- **Trigger:**
  ```sql
  CREATE OR REPLACE FUNCTION public.bump_birth_data_version()
  RETURNS TRIGGER AS $$
  BEGIN
      NEW.data_version = OLD.data_version + 1;
      NEW.updated_at = now();
      RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;
  ```

### B. User Isolation & Authentication Integrity
- **Identity Derivation:** All authenticated backend endpoints derive user identity strictly from the verified JWT payload claim (`current_user.id = payload.sub`).
- **Authorization Enforcement:** User A cannot query or mutate User B's `birth_data`. RLS policies and backend route handlers enforce owner-only access.
- **Privacy Boundary Verification:**
  - When User B calls `/v1/astrology/people/{User A}/safe-astro`, the backend verifies `public.is_user_blocked(B, A)` and `profiles.is_discoverable`.
  - If blocked or non-discoverable, the system raises `PrivacySafeNotFoundException`, returning HTTP 404. It never acts as an existence oracle.
  - Automated test `test_user_isolation_and_privacy_boundary` verified this behavior.

---

## 4. Deterministic A/B Birth Data Change Test

To guarantee reproducible astronomical and semantic divergence, two distinct benchmark states were evaluated for a dedicated registered test identity (`dea68666-2dcb-4bda-bd8e-db9edb53277a`).

### Benchmark Test States

| Parameter | State A (London Spring Equinox) | State B (Tbilisi Autumn Evening) | Expected Difference |
|---|---|---|---|
| **Birth Date** | `1990-03-21` | `1995-11-15` | +5 years, 8 months |
| **Birth Time** | `06:00:00` | `18:30:00` | +12 hours 30 mins |
| **Precision** | `exact` | `exact` | Stable |
| **Timezone** | `UTC` | `Asia/Tbilisi` | Different offset (+04:00) |
| **Coordinates** | 51.5074° N, -0.1278° W | 41.7151° N, 44.8271° E | Trans-European divergence |
| **Place Label** | London, UK | Tbilisi, Georgia | Distinct location |

---

## 5. Database Before/After Snapshot

Empirical before-and-after values captured directly from PostgreSQL:

| Database Column | State A Value | State B Value | Transition Invariant | Status |
|---|---|---|---|---|
| `user_id` | `dea68666-...` | `dea68666-...` | Same persistent user | **PASS** |
| `birth_date` | `1990-03-21` | `1995-11-15` | Deterministic date update | **PASS** |
| `birth_time` | `06:00:00` | `18:30:00` | Local time persisted | **PASS** |
| `birth_timezone` | `UTC` | `Asia/Tbilisi` | IANA TZ string preserved | **PASS** |
| `latitude` | `51.507400` | `41.715100` | Coordinates updated | **PASS** |
| `longitude` | `-0.127800` | `44.827100` | Coordinates updated | **PASS** |
| `place_label` | `London, UK` | `Tbilisi, Georgia` | Location label updated | **PASS** |
| `data_version` | `1` | `2` | Auto-incremented via trigger | **PASS** |
| `created_at` | `2026-09-08 17:01:05.15` | `2026-09-08 17:01:05.15` | Unmodified creation time | **PASS** |
| `updated_at` | `2026-09-08 17:01:05.15` | `2026-09-08 17:01:05.21` | Auto-updated by trigger | **PASS** |

---

## 6. Astrological Calculation Audit

Calculations executed deterministically by the PySwissEph engine:

| Astronomical Placement | State A Degree (`astro_private`) | State A Sign | State B Degree (`astro_private`) | State B Sign | Expected Change | Result |
|---|---|---|---|---|---|---|
| **Sun** | 0.4728° | **Aries** | 232.8837° | **Scorpio** | Shift: Pisces/Aries cusp &rarr; Scorpio | **PASS** |
| **Moon** | 297.8384° | **Capricorn** | 148.5134° | **Leo** | Shift: Capricorn &rarr; Leo | **PASS** |
| **Ascendant** | 357.2520° | **Pisces** | 68.6186° | **Gemini** | Shift: Pisces &rarr; Gemini | **PASS** |
| **Mercury** | 16.5925° | **Aries** | 225.4334° | **Scorpio** | Shift: Aries &rarr; Scorpio | **PASS** |
| **Venus** | 315.6542° | **Aquarius** | 258.8572° | **Sagittarius** | Shift: Aquarius &rarr; Sagittarius | **PASS** |
| **Mars** | 309.8454° | **Aquarius** | 260.6728° | **Sagittarius** | Shift: Aquarius &rarr; Sagittarius | **PASS** |
| **Element Primary** | — | **Fire** | — | **Fire** | Dominant element derived | **PASS** |
| **Modality Primary** | — | **Cardinal** | — | **Fixed** | Dominant modality derived | **PASS** |

Every placement changed in accordance with celestial mechanics. No mathematical approximations or client-side calculations were present.

---

## 7. Timezone Audit

A common source of astrological corruption is improper handling of local vs. UTC offsets and Daylight Saving Time.

### Audit Trace: State B (Tbilisi)
- **Local Input:** `1995-11-15 18:30:00`
- **Timezone Specified:** `Asia/Tbilisi`
- **Standard Offset in Nov 1995:** UTC+04:00 (Georgia does not observe DST in November)
- **Calculated UTC Datetime:** `1995-11-15 14:30:00+00:00`
- **Julian Day from Local & Timezone:** `2450037.1041666665`
- **Julian Day from Pure UTC:** `2450037.1041666665`
- **Delta:** `0.0000000000` (Exact float identity match)

### Unknown Birth Time Behavior
When `birth_time_precision == 'unknown'`:
- Birth time is set to `12:00:00` UTC noon for planetary longitudes.
- Ascendant and houses evaluate strictly to `None` in `astro_private` and `astro_safe_profile`.
- No mock or assumed rising sign is ever emitted.

---

## 8. API Response Audit

### Recalculate Endpoint: `POST /v1/astrology/profile/recalculate`
```json
{
  "user_id": "dea68666-2dcb-4bda-bd8e-db9edb53277a",
  "sun_sign": "Scorpio",
  "moon_sign": "Leo",
  "ascendant_sign": "Gemini",
  "mercury_sign": "Scorpio",
  "venus_sign": "Sagittarius",
  "mars_sign": "Sagittarius",
  "element_primary": "Fire",
  "modality_primary": "Fixed",
  "source_birth_data_version": 2,
  "engine_version": "1.0.0",
  "updated_at": "2026-09-08T17:01:05.252150Z"
}
```

### Cached Safe Profile Endpoint: `GET /v1/astrology/profile/safe-astro`
```json
{
  "user_id": "dea68666-2dcb-4bda-bd8e-db9edb53277a",
  "sun_sign": "Scorpio",
  "moon_sign": "Leo",
  "ascendant_sign": "Gemini",
  "mercury_sign": "Scorpio",
  "venus_sign": "Sagittarius",
  "mars_sign": "Sagittarius",
  "element_primary": "Fire",
  "modality_primary": "Fixed",
  "source_birth_data_version": 2,
  "engine_version": "1.0.0",
  "updated_at": "2026-09-08T17:01:05.252150Z"
}
```
**Verification:** The cached read matches the recalculate response property-by-property. All planetary signs (`mercury_sign`, `venus_sign`, `mars_sign`) are present and accurate.

---

## 9. Frontend API & React Query Cache Audit

### The Discovered Cache Defect (Root Cause #1)
In `frontend/src/modules/onboarding/BirthDataOnboardingPage.tsx`:
```tsx
// BEFORE (Bug):
await API.astrology.saveBirthData(user.id, payload);
setHasBirthData(true);
navigate("/me"); // React Query cache retained old data for 30s!
```
When navigating to `/me`, `useQuery({ queryKey: ["astrology", "me"] })` and `useQuery({ queryKey: ["natal-observations"] })` were still fresh under the default `staleTime: 30000`. The user viewed old signs and old copy until manual reload or cache expiration.

### Applied Surgical Correction
```tsx
// AFTER (Fixed):
await API.astrology.saveBirthData(user.id, payload);
await queryClient.invalidateQueries({ queryKey: ["astrology"] });
await queryClient.invalidateQueries({ queryKey: ["birth-data"] });
await queryClient.invalidateQueries({ queryKey: ["natal-observations"] });
await queryClient.invalidateQueries({ queryKey: ["profile"] });

setHasBirthData(true);
navigate("/me");
```
Immediate query invalidation forces React Query to refetch the fresh API state upon navigating to `/me`, guaranteeing instantaneous consistency.

---

## 10. Cache & Invalidation Invariant Matrix

| User Action | Stale Queries | Invalidated Queries | Refetch Triggered? | Render Consistency |
|---|---|---|---|---|
| **Save Birth Data** | `["astrology", "me"]`, `["birth-data"]`, `["natal-observations"]` | `["astrology"]`, `["birth-data"]`, `["natal-observations"]`, `["profile"]` | Immediate upon transition | **PASS** |
| **Page Refresh (F5)** | All in-memory cache | Cache rebuilt from scratch from backend | Immediate | **PASS** |
| **Logout & Login** | Cache cleared on signout | Clean session | Fresh query for new auth user | **PASS** |
| **Cross-Device Query** | Remote device cache | Fetches latest `data_version` from PostgreSQL | Consistent with DB | **PASS** |

---

## 11. Visual Debug Lab Diagnostic Surface

A developer inspection environment was built at `/__debug/backend-audit` (also accessible via `/__lab/backend-audit` and the header `🔬 Audit` button).

### Lab Capabilities
1. **Live Session & Identity Inspector:** Real-time JWT subject (`user.id`), email, session expiry.
2. **Deterministic A/B State Controls:** One-click application of State A (London) or State B (Tbilisi) to test live recalculation.
3. **Stored DB vs Calculated Placements:** Side-by-side comparison of `public.birth_data` vs `astro_safe_profile`.
4. **Cache & Invalidation Status:** Real-time `isFetching`, `dataUpdatedAt`, query key, and cache staleness indicator.
5. **Personal Narrative Resolution:** Live inspection of Georgian copy resolved for Mercury, Venus, and Mars.
6. **Diagnostic Forensic Matrix:** Visual PASS/FAIL indicators for each subsystem.
7. **Raw JSON Payload Dump:** Inspect exact HTTP responses without frontend masking.

---

## 12. Content Resolution & Semantic Integrity Audit

The boundary between deterministic facts and semantic wording was verified across all 12 signs:
$$\text{Birth Data} \longrightarrow \text{Swiss Ephemeris} \longrightarrow \text{Sign} \longrightarrow \text{Contract} \longrightarrow \text{Corpus Asset} \longrightarrow \text{JESTER Copy}$$

### Mercury (Cognition) — 12 Signs
Contract pattern: `self.cognition.mercury_{sign}.v1` (96 assets in `mercury_corpus.json`)
- All 12 signs resolve valid Georgian text.
- No astrology jargon present.
- Tones: `snarky`, `analytical`, `conversational`, `provocative`.

### Venus (Relation) — 12 Signs
Contract pattern: `self.relation.venus_{sign}.v1` (96 assets in `venus_corpus.json`)
- All 12 signs resolve valid Georgian text.
- Tones: `witty`, `conversational`, `poetic`, `provocative`.

### Mars (Action) — 12 Signs (Fixed)
Contract pattern: `self.action.mars_{sign}.v1` (96 assets in `mars_corpus.json`)
- **Before Fix:** 0/12 resolved (all returned `None` due to missing `"context": "self"` in fixture).
- **After Fix:** 12/12 resolved approved Georgian assets.
- Tones: `cocky`, `unfiltered`, `dramatic`, `unexpected`, `conversational`.

---

## 13. Sign &rarr; Content Resolution Matrix (All 36 Placements)

| Body | Sign | Contract ID | Asset ID | Tone | Status |
|---|---|---|---|---|---|
| **Mercury** | Aries | `self.cognition.mercury_aries.v1` | `ca_cog_ari_001_ka_sna_mic` | snarky | **PASS** |
| **Mercury** | Taurus | `self.cognition.mercury_taurus.v1` | `ca_cog_tau_001_ka_sna_mic` | snarky | **PASS** |
| **Mercury** | Gemini | `self.cognition.mercury_gemini.v1` | `ca_cog_gem_001_ka_sna_mic` | snarky | **PASS** |
| **Mercury** | Cancer | `self.cognition.mercury_cancer.v1` | `ca_cog_can_001_ka_con_mic` | conversational | **PASS** |
| **Mercury** | Leo | `self.cognition.mercury_leo.v1` | `ca_cog_leo_001_ka_pro_mic` | provocative | **PASS** |
| **Mercury** | Virgo | `self.cognition.mercury_virgo.v1` | `ca_cog_vir_001_ka_ana_mic` | analytical | **PASS** |
| **Mercury** | Libra | `self.cognition.mercury_libra.v1` | `ca_cog_lib_001_ka_con_mic` | conversational | **PASS** |
| **Mercury** | Scorpio | `self.cognition.mercury_scorpio.v1` | `ca_cog_sco_001_ka_pro_mic` | provocative | **PASS** |
| **Mercury** | Sagittarius | `self.cognition.mercury_sagittarius.v1` | `ca_cog_sag_001_ka_sna_mic` | snarky | **PASS** |
| **Mercury** | Capricorn | `self.cognition.mercury_capricorn.v1` | `ca_cog_cap_001_ka_ana_mic` | analytical | **PASS** |
| **Mercury** | Aquarius | `self.cognition.mercury_aquarius.v1` | `ca_cog_aqu_001_ka_pro_mic` | provocative | **PASS** |
| **Mercury** | Pisces | `self.cognition.mercury_pisces.v1` | `ca_cog_pis_001_ka_con_mic` | conversational | **PASS** |
| **Venus** | Aries | `self.relation.venus_aries.v1` | `ca_rel_ari_001_ka_wit_mic` | witty | **PASS** |
| **Venus** | Taurus | `self.relation.venus_taurus.v1` | `ca_rel_tau_001_ka_wit_mic` | witty | **PASS** |
| **Venus** | Gemini | `self.relation.venus_gemini.v1` | `ca_rel_gem_001_ka_wit_mic` | witty | **PASS** |
| **Venus** | Cancer | `self.relation.venus_cancer.v1` | `ca_rel_can_001_ka_con_mic` | conversational | **PASS** |
| **Venus** | Leo | `self.relation.venus_leo.v1` | `ca_rel_leo_001_ka_wit_mic` | witty | **PASS** |
| **Venus** | Virgo | `self.relation.venus_virgo.v1` | `ca_rel_vir_001_ka_wit_mic` | witty | **PASS** |
| **Venus** | Libra | `self.relation.venus_libra.v1` | `ca_rel_lib_001_ka_wit_mic` | witty | **PASS** |
| **Venus** | Scorpio | `self.relation.venus_scorpio.v1` | `ca_rel_sco_001_ka_pro_mic` | provocative | **PASS** |
| **Venus** | Sagittarius | `self.relation.venus_sagittarius.v1` | `ca_rel_sag_001_ka_wit_mic` | witty | **PASS** |
| **Venus** | Capricorn | `self.relation.venus_capricorn.v1` | `ca_rel_cap_001_ka_wit_mic` | witty | **PASS** |
| **Venus** | Aquarius | `self.relation.venus_aquarius.v1` | `ca_rel_aqu_001_ka_wit_mic` | witty | **PASS** |
| **Venus** | Pisces | `self.relation.venus_pisces.v1` | `ca_rel_pis_001_ka_con_mic` | conversational | **PASS** |
| **Mars** | Aries | `self.action.mars_aries.v1` | `astrology.self.action.mars_aries.v1.aries_action_v01` | cocky | **PASS** |
| **Mars** | Taurus | `self.action.mars_taurus.v1` | `astrology.self.action.mars_taurus.v1.taurus_action_v01` | conversational | **PASS** |
| **Mars** | Gemini | `self.action.mars_gemini.v1` | `astrology.self.action.mars_gemini.v1.gemini_action_v01` | cocky | **PASS** |
| **Mars** | Cancer | `self.action.mars_cancer.v1` | `astrology.self.action.mars_cancer.v1.cancer_action_v01` | dramatic | **PASS** |
| **Mars** | Leo | `self.action.mars_leo.v1` | `astrology.self.action.mars_leo.v1.leo_action_v01` | cocky | **PASS** |
| **Mars** | Virgo | `self.action.mars_virgo.v1` | `astrology.self.action.mars_virgo.v1.virgo_action_v01` | conversational | **PASS** |
| **Mars** | Libra | `self.action.mars_libra.v1` | `astrology.self.action.mars_libra.v1.libra_action_v01` | unexpected | **PASS** |
| **Mars** | Scorpio | `self.action.mars_scorpio.v1` | `astrology.self.action.mars_scorpio.v1.scorpio_action_v01` | unfiltered | **PASS** |
| **Mars** | Sagittarius | `self.action.mars_sagittarius.v1` | `astrology.self.action.mars_sagittarius.v1.sagittarius_action_v01` | unexpected | **PASS** |
| **Mars** | Capricorn | `self.action.mars_capricorn.v1` | `astrology.self.action.mars_capricorn.v1.capricorn_action_v01` | conversational | **PASS** |
| **Mars** | Aquarius | `self.action.mars_aquarius.v1` | `astrology.self.action.mars_aquarius.v1.aquarius_action_v01` | unfiltered | **PASS** |
| **Mars** | Pisces | `self.action.mars_pisces.v1` | `astrology.self.action.mars_pisces.v1.pisces_action_v01` | dramatic | **PASS** |

---

## 14. Hardcoded & Mock Content Audit

The frontend codebase was audited for hardcoded astrology strings or fallback horoscopes:

| Location | Content Identified | Classification | Action / Safety Assessment |
|---|---|---|---|
| `frontend/src/modules/smoke_test/ContentSmokeTestPage.tsx` | Fallback cards for offline previewing | **DEVELOPER TEST ONLY** | Isolated to developer smoke test route `/smoke-test`. Never served to real users. |
| `frontend/src/modules/me/MePage.tsx` | Skeleton loaders & empty states | **PRODUCTION PATH** | Pure presentation wrappers; consumes backend data via React Query. Zero hardcoded text. |
| `frontend/src/ui/BackendAuditDebugPage.tsx` | State A / State B sample coordinates | **DEBUG LAB ONLY** | Dedicated test values used strictly for audit toggles. |
| `frontend/src/core/api/endpoints.ts` | Endpoint path definitions | **PRODUCTION PATH** | Clean API client layer; zero fixture data. |

**Audit Conclusion:** No production screens (`MePage`, `PersonProfilePage`, `ComparePage`) contain hardcoded astrology text or mock fallback overrides.

---

## 15. Backend ↔ Frontend Type Contract Audit

| Backend Field (`SafeDerivedAstrologyResponse`) | Frontend Field (`types.ts`) | Type Alignment | Status Before | Status After |
|---|---|---|---|---|
| `user_id: UUID` | `user_id: string` | String UUID | PASS | PASS |
| `sun_sign: str` | `sun_sign: string` | String | PASS | PASS |
| `moon_sign: str` | `moon_sign: string` | String | PASS | PASS |
| `ascendant_sign: str | None` | `ascendant_sign: string | null` | Nullable string | PASS | PASS |
| `mercury_sign: str | None` | `mercury_sign?: string | null` | Nullable string | **FAIL (Missing)** | **PASS (Added)** |
| `venus_sign: str | None` | `venus_sign?: string | null` | Nullable string | **FAIL (Missing)** | **PASS (Added)** |
| `mars_sign: str | None` | `mars_sign?: string | null` | Nullable string | **FAIL (Missing)** | **PASS (Added)** |
| `element_primary: str` | `element_primary: string` | String | PASS | PASS |
| `modality_primary: str` | `modality_primary: string` | String | PASS | PASS |
| `source_birth_data_version: int` | `source_birth_data_version: number`| Number | PASS | PASS |
| `engine_version: str` | `engine_version: string` | String | PASS | PASS |
| `updated_at: datetime` | `updated_at: string` | ISO-8601 string | PASS | PASS |

---

## 16. Defects Found, Root Causes, and Applied Fixes

### Defect 1: Stale React Query Cache on Birth Data Mutation
- **Observed Behavior:** Changing birth date did not reflect in `/me` text immediately; old astrology persisted for ~30 seconds.
- **Root Cause:** `BirthDataOnboardingPage.tsx` failed to invalidate dependent React Query keys (`["astrology"]`, `["natal-observations"]`, `["birth-data"]`).
- **Severity:** HIGH.
- **Fix Applied:** Injected `useQueryClient` and called `invalidateQueries` upon successful save.
- **Verification:** Mutation immediately causes fresh fetch. Verified in Browser Subagent and automated tests.

### Defect 2: Mars Corpus Rejection in Content Resolver
- **Observed Behavior:** Mars personal observations returned `None` for all 12 signs.
- **Root Cause:** `backend/app/interpretation/data/mars_corpus.json` omitted `"context": "self"`. Resolver rejected assets due to domain boundary mismatch.
- **Severity:** HIGH.
- **Fix Applied:** Updated `library.py` fixture loader to infer `context="self"` for `self.*` interpretation IDs, and added `"context": "self"` to all 96 assets in `mars_corpus.json`.
- **Verification:** 12/12 Mars signs resolved with tone and approved Georgian text. Verified by `test_content_resolution_mercury_venus_mars_all_12_signs`.

### Defect 3: Safe Profile Read Endpoint Missing Planetary Signs
- **Observed Behavior:** `GET /v1/astrology/profile/safe-astro` returned `null` for `mercury_sign`, `venus_sign`, and `mars_sign` on cached reads.
- **Root Cause:** `astro_safe_profile` database table lacks columns for Mercury/Venus/Mars signs; `router.py` did not join `astro_private`.
- **Severity:** MEDIUM.
- **Fix Applied:** Updated `get_my_safe_astrology` and `get_person_safe_astrology` in `backend/app/astrology/router.py` to join `astro_private` and derive zodiac signs via `longitude_to_sign`.
- **Verification:** Cached reads return complete signs. Verified by `test_astrology_recalculation_and_safe_api_consistency`.

### Defect 4: Missing Planetary Sign Types in Frontend
- **Observed Behavior:** Frontend TypeScript failed to recognize `mercury_sign`, `venus_sign`, `mars_sign` on `SafeDerivedAstrologyResponse`.
- **Root Cause:** Interface omission in `frontend/src/core/api/types.ts`.
- **Severity:** LOW.
- **Fix Applied:** Added `mercury_sign?: string | null`, `venus_sign?: string | null`, `mars_sign?: string | null` to `types.ts`.
- **Verification:** Zero TypeScript compilation errors (`tsc && vite build` passed).

---

## 17. Automated Regression Test Verification

A dedicated regression test file was added at `tests/backend/test_data_integrity_audit.py`:

```
tests/backend/test_data_integrity_audit.py::test_registered_user_birth_data_persistence_and_version_trigger PASSED [ 25%]
tests/backend/test_data_integrity_audit.py::test_astrology_recalculation_and_safe_api_consistency PASSED [ 50%]
tests/backend/test_data_integrity_audit.py::test_user_isolation_and_privacy_boundary PASSED [ 75%]
tests/backend/test_data_integrity_audit.py::test_content_resolution_mercury_venus_mars_all_12_signs PASSED [100%]
```

Full repository test suite run:
$$\mathbf{192\text{ passed in } 10.20\text{ seconds (100\% pass rate)}}$$

---

## 18. Final Status Matrix

| Subsystem / Evaluation Area | Forensic Result | Evidence / Notes |
|---|---|---|
| **Auth User Resolution** | **PASS** | Caller identity strictly derived from asymmetric JWT `sub`. |
| **Profile Persistence** | **PASS** | Stored in `public.profiles`, linked 1-to-1 to `auth.users`. |
| **Birth Data Persistence** | **PASS** | Persisted in `public.birth_data` with precision and coordinate constraints. |
| **Birth Data Update & Trigger** | **PASS** | `bump_birth_data_version` auto-increments version and updates timestamp. |
| **Timezone Conversion** | **PASS** | Python `zoneinfo` converts local time to UTC with exact Julian Day identity. |
| **Swiss Ephemeris Calculation** | **PASS** | Deterministic planetary longitudes stored in `astro_private`. |
| **Mercury Calculation** | **PASS** | Calculated in `astro_private`, derived in safe response. |
| **Venus Calculation** | **PASS** | Calculated in `astro_private`, derived in safe response. |
| **Mars Calculation** | **PASS** | Calculated in `astro_private`, derived in safe response. |
| **API Response Completeness** | **PASS** | `/safe-astro` and `/recalculate` return identical complete safe DTOs. |
| **Content Resolution (Mercury)** | **PASS** | All 12 signs resolve approved Georgian copy (96 assets). |
| **Content Resolution (Venus)** | **PASS** | All 12 signs resolve approved Georgian copy (96 assets). |
| **Content Resolution (Mars)** | **PASS** | All 12 signs resolve approved Georgian copy (96 assets post-fix). |
| **Frontend API Mapping** | **PASS** | Exact match between Pydantic models and TypeScript interfaces. |
| **React Query Cache** | **PASS** | Cache configured with active invalidation triggers. |
| **Query Invalidation** | **PASS** | `BirthDataOnboardingPage` explicitly invalidates dependent queries on mutation. |
| **Frontend Rendering** | **PASS** | Rendered copy directly driven by backend API observations. |
| **Hardcoded Content Audit** | **PASS** | Zero hardcoded astrology text in production routes. |
| **User Data Isolation** | **PASS** | Cross-user birth data reads impossible; privacy-safe 404 returned for blocked/hidden profiles. |
| **Refresh Consistency** | **PASS** | Page reload preserves identical persisted state. |
| **Session Consistency** | **PASS** | Logout cleans query cache; re-login restores exact profile. |
| **Backend ↔ Frontend Types** | **PASS** | Fully synchronized; TypeScript compiles with zero errors. |

---

## 19. Overall Audit Finding

$$\mathbf{OVERALL\ STATUS:\ PASS}$$

The entire chain from registered user input to database persistence, astronomical calculation, semantic resolution, API transport, cache management, and UI rendering is **forensically proven to be sound, deterministic, and free of data loss or stale state leakage**.
