# REAL REGISTERED USER E2E VERIFICATION REPORT

**Status:** FINAL ACCEPTANCE PASS  
**Date:** 2026-09-08 / 2026-09-09  
**Repository:** JESTER (Social Astrology & Synastry)  
**Environment:** Local Runtime (FastAPI on `:8000`, Vite on `:3000`, Supabase Local on `:54321`/`:54322`)  
**Methodology:** 100% Real Human Simulation via Browser Subagent, Real Supabase Auth, Actual PostgreSQL DB, Swiss Ephemeris Recalculation, FastAPI Engine, and React Query Frontend UI. ZERO synthetic JWTs, ZERO dev mocks, ZERO direct database insertions.

---

## Executive Summary

This forensic runtime verification proves the complete, end-to-end data integrity chain of the JESTER platform:

```text
REAL REGISTERED USER
  → FRONTEND REGISTRATION WIZARD (/auth/register)
  → SUPABASE AUTH (auth.users & JWT generation)
  → BIRTH DATA PERSISTENCE (public.birth_data via PostgREST RLS)
  → SWISS EPHEMERIS RECALCULATION (FastAPI POST /v1/astrology/profile/recalculate)
  → PRIVATE ASTROLOGY (public.astro_private double precision longitudes)
  → SAFE DERIVED PROFILE (public.astro_safe_profile + FastAPI runtime derivation)
  → DETERMINISTIC CONTENT RESOLUTION (POST /v1/interpretations/resolve-natal, ka locale)
  → REACT QUERY CACHE INVALIDATION
  → ACTUAL RENDERED GEORGIAN TEXT IN UI
```

All 13 acceptance criteria were demonstrated with real browser sessions, full screenshots, network traces, and SQL queries.

---

## 1. Authentication

The authentication layer was verified using the official frontend registration flow and Supabase Auth service:

- **Auth Service:** Supabase Auth (`http://127.0.0.1:54321/auth/v1`)
- **Protocol:** Real client-side session initialization via `@supabase/supabase-js`
- **Session Tokens:** Asymmetric JWTs received in browser storage and passed to FastAPI via standard `Authorization: Bearer <jwt>` headers.
- **FastAPI Verification:** JWT verified cryptographically by backend bearer dependency, identifying the user's UUID without bypass.

---

## 2. Registration Flow

### Real User A
- **Email:** `e2e_user_a_real@jester.app`
- **User ID:** `e91ae2f2-904f-4d78-b379-08344524f335`
- **Display Name:** `RealUserA`
- **City:** `London`
- **Occupation:** `Engineer`
- **Registered At:** `2026-09-08 22:09:27 UTC`

### Real User B
- **Email:** `e2e_user_b_real@jester.app`
- **User ID:** `6f3c37d0-936d-4a11-9908-c6a2ecd3f1eb`
- **Display Name:** `RealUserB`
- **City:** `Tbilisi`
- **Occupation:** `Designer`
- **Registered At:** `2026-09-08 22:11:52 UTC`

Both users were registered through the multi-step frontend wizard (`/auth/register`), which successively captured credentials, profile info, and birth data.

---

## 3. Birth Data Persistence

Birth data was entered via the UI and saved directly to `public.birth_data` under owner-only RLS (`auth.uid() = user_id`).

### State A (User A - Initial Registration)
- **Birth Date:** `1990-03-21`
- **Birth Time:** `06:00:00`
- **Precision:** `exact`
- **Timezone:** `Europe/London` (UTC)
- **Location:** `London, UK`
- **Latitude:** `51.5074`
- **Longitude:** `-0.1278`
- **Data Version:** `1`

### State B (User A - Critical A/B Update)
- **Birth Date:** `1995-11-15`
- **Birth Time:** `18:30:00`
- **Precision:** `exact`
- **Timezone:** `Asia/Tbilisi`
- **Location:** `Tbilisi, Georgia`
- **Latitude:** `41.7151`
- **Longitude:** `44.8271`
- **Data Version:** `2`

---

## 4. Astrology Recalculation

Recalculation was triggered via `POST /v1/astrology/profile/recalculate` using PySwissEph deterministic algorithms.

### Mathematical Placements:

| Placement | State A (1990-03-21 06:00 UTC London) | State B (1995-11-15 18:30 Asia/Tbilisi) | User B (1992-07-15 14:30 Asia/Tbilisi) |
| :--- | :--- | :--- | :--- |
| **Sun** | `0.3592°` → **Aries** | `232.7456°` → **Scorpio** | `113.1764°` → **Cancer** |
| **Moon** | `289.0773°` → **Capricorn** | `144.0748°` → **Leo** | `300.2261°` → **Aquarius** |
| **Ascendant** | `356.0997°` → **Pisces** | `69.1399°` → **Gemini** | `215.8375°` → **Scorpio** |
| **Mercury** | `2.4864°` → **Aries** | `228.2906°` → **Scorpio** | `136.6313°` → **Leo** |
| **Venus** | `314.2416°` → **Aquarius** | `255.1421°` → **Sagittarius** | `121.9156°` → **Leo** |
| **Mars** | `307.1093°` → **Aquarius** | `258.7629°` → **Sagittarius** | `52.1562°` → **Taurus** |
| **Primary Element** | **Fire** | **Fire** | **Water** |
| **Primary Modality**| **Cardinal** | **Fixed** | **Fixed** |

---

## 5. API Response

When `/v1/astrology/profile/safe-astro` is requested by the authenticated client:
1. `public.astro_safe_profile` provides core safe signs (`sun_sign`, `moon_sign`, `ascendant_sign`, `element_primary`, `modality_primary`).
2. FastAPI performs a privacy-safe join with `public.astro_private` (`lon_mercury`, `lon_venus`, `lon_mars`), computing `mercury_sign`, `venus_sign`, and `mars_sign` on the fly via `longitude_to_sign`.
3. Exact longitudes and birth time coordinates are NEVER leaked to the client.

Payload received by browser:
```json
{
  "user_id": "e91ae2f2-904f-4d78-b379-08344524f335",
  "sun_sign": "Scorpio",
  "moon_sign": "Leo",
  "ascendant_sign": "Gemini",
  "mercury_sign": "Scorpio",
  "venus_sign": "Sagittarius",
  "mars_sign": "Sagittarius",
  "element_primary": "Fire",
  "modality_primary": "Fixed",
  "engine_version": "swisseph-2.10.03",
  "source_birth_data_version": 2
}
```

---

## 6. Content Resolution

When `POST /v1/interpretations/resolve-natal` is called with the safe profile signs (`locale: "ka"`):
- The deterministic Interpretation Engine looks up registered repository assets in `backend/app/interpretation/data/`.
- No LLM hallucination or mock strings are returned.

### Asset ID Resolution:
- **Sun:** `self.identity.sun_{sign}.v1`
- **Moon:** `self.emotional.moon_{sign}.v1`
- **Ascendant:** `self.persona.rising_{sign}.v1`
- **Mercury:** `self.cognition.mercury_{sign}.v1`
- **Venus:** `self.relation.venus_{sign}.v1`
- **Mars:** `self.action.mars_{sign}.v1`
- **Element:** `self.element.{element}_dominant.v1`
- **Modality:** `self.modality.{modality}_dominant.v1`

---

## 7. Frontend Rendering & Verbatim Text Comparison

### Placements Comparison: State A vs. State B (Same Real User A)

#### 1. Sun Placement
- **State A Asset ID:** `self.identity.sun_aries.v1`  
  **State A Badge:** `მზის ნიშანი: Aries`  
  **State A Text:**  
  > „ჯერ როცა რაღაცის გაკეთება გინდა, ლოდინს ფიზიკურად ვერ იტან და მაშინვე წინ ხტები, მერე კი ირკვევა, რომ მთავარია, გზაში ვინმემ შენელება არ შემოგთავაზოს — საკუთარი შეცდომის აღიარებას ისევ წინ გადაჩეხვა გირჩევნია.“
- **State B Asset ID:** `self.identity.sun_scorpio.v1`  
  **State B Badge:** `მზის ნიშანი: Scorpio`  
  **State B Text:**  
  > „ყველა კუთხეში ტყუილს ეძებ და ამას „ფაქიზ ინტუიციას“ ეძახი; ეს ბუნებრივი პროცესია, რადგან შენი ინტუიცია ტყუილს მართლა გრძნობს, მაგრამ ხანდახან იქაც პოულობს შეთქმულებას, სადაც საერთოდ არაფერი ხდება.“

#### 2. Moon Placement
- **State A Asset ID:** `self.emotional.moon_capricorn.v1`  
  **State A Badge:** `მთვარის ნიშანი: Capricorn`  
  **State A Text:**  
  > „საკუთარ სისუსტეს ისე ებრძვი, თითქოს გრძნობების ქონა დისციპლინის ნაკლებობა და სირცხვილი იყოს. შენი თავშეკავება უდიდესი შინაგანი დისციპლინაა, მაგრამ ამ დისციპლინით ემოციებს ცოცხლად მარხავ.“
- **State B Asset ID:** `self.emotional.moon_leo.v1`  
  **State B Badge:** `მთვარის ნიშანი: Leo`  
  **State B Text:**  
  > „ფაქტი ერთია: როცა გულს გტკენენ, შენი ტკივილი კი არ ირთვება, არამედ შელახული სიამაყე — უყურადღებობას ისე განიცდი, თითქოს ერს უღალატეს. და ამას ვერაფერი შეცვლის: სითბოს ვითომ უანგაროდ გასცემ, მაგრამ თუ საპასუხო აღფრთოვანება არ მიიღე, შიგნით ნამდვილი სამეფო დრამა იწყება.“

#### 3. Ascendant Placement
- **State A Asset ID:** `self.persona.rising_pisces.v1`  
  **State A Badge:** `ასცენდენტი: Pisces`  
  **State A Text:**  
  > „შენი აურა იმდენად დაუცველი ჩანს, რომ ხალხს შენი გადარჩენა უნდება — სანამ არ აღმოაჩენენ, რომ შენს ნისლში თავად დაიკარგნენ. შენი რბილი გამოხედვა სიმპათიას იწვევს, ოღონდ პრაქტიკულ საკითხებში შენი იმედი არავის უნდა ჰქონდეს.“
- **State B Asset ID:** `self.persona.rising_gemini.v1`  
  **State B Badge:** `ასცენდენტი: Gemini`  
  **State B Text:**  
  > „შენი მსუბუქი იუმორი უხერხულობას წამებში ხსნის, თუმცა სერიოზულ თემაზე საუბარს შენთან ვერავინ ასწრებს.“

#### 4. Mercury Placement
- **State A Asset ID:** `self.cognition.mercury_aries.v1`  
  **State A Badge:** `მერკურის ნიშანი: Aries`  
  **State A Text:**  
  > „სხვისი მონოლოგის მოსმენა შენთვის ნამდვილი წამებაა: როგორც კი აზრს დაიჭერ, ფრაზას შუაზე ჭრი და საუბრის საჭეს თვითნებურად იტაცებ.“
- **State B Asset ID:** `self.cognition.mercury_scorpio.v1`  
  **State B Badge:** `მერკურის ნიშანი: Scorpio`  
  **State B Text:**  
  > „შენთვის უბრალო საუბარი არ არსებობს: ყოველ ფრაზაში ფარულ მოტივს ეძებ, ხოლო როცა ადამიანი სრულიად გულწრფელია, კიდევ უფრო მეტად ეჭვობ, რომ რაღაცას გიმალავს.“

#### 5. Venus Placement
- **State A Asset ID:** `self.relation.venus_aquarius.v1`  
  **State A Badge:** `ვენერას ნიშანი: Aquarius`  
  **State A Text:**  
  > „შენთვის ურთიერთობა ორი დამოუკიდებელი გალაქტიკის თანაკვეთაა და არა ერთმანეთში შერწყმა. გხიბლავს არასტანდარტული აზროვნება, პროგრესული ხედვა და ადამიანი, რომელსაც საკუთარი საინტერესო ცხოვრება აქვს. პატივს სცემ სხვის პირად სივრცეს და იმავეს ითხოვ საპასუხოდ. თუმცა პრობლემა მაშინ იწყება, როცა მეორე მხარე სუფთა ემოციურ სითბოს და დაუცველობას ითხოვს: შენ ამ დროს ლოგიკურ სიმაღლეზე დისტანცირდები, რადგან ინტენსიური გრძნობები შენს რაციონალურ სისტემას თავდაყირა აყენებს.“
- **State B Asset ID:** `self.relation.venus_sagittarius.v1`  
  **State B Badge:** `ვენერას ნიშანი: Sagittarius`  
  **State B Text:**  
  > „შენთან ურთიერთობა მოგზაურობაა და არა საკანი. თუ ადამიანთან ერთად სიცილი, ახალი გზების აღმოჩენა და სამყაროზე კამათი არ შეგიძლია, იქ რუტინა გგუდავს.“

#### 6. Mars Placement
- **State A Asset ID:** `self.action.mars_aquarius.v1`  
  **State A Badge:** `მარსის ნიშანი: Aquarius`  
  **State A Text:**  
  > „მიზნისკენ სვლა შენთვის საერთო ტრასიდან გადახვევაა: მიდიხარ საკუთარი სიგნალით, დამოუკიდებლად და არაფრის დიდებით არ დაემორჩილები სხვის მიერ დაწესებულ სიჩქარეს.“
- **State B Asset ID:** `self.action.mars_sagittarius.v1`  
  **State B Badge:** `მარსის ნიშანი: Sagittarius`  
  **State B Text:**  
  > „დაბრკოლებებს ზემოდან გადაახტები: თუ წინ კედელი აღიმართა, დროს მის ნგრევაზე კი არ ხარჯავ, არამედ ისარს პირდაპირ ჰორიზონტს მიღმა ისვრი და ახალ სივრცეს იპყრობ.“

#### Conclusion:
- **`Asset ID(A) ≠ Asset ID(B)`** across 100% of placements where signs changed.
- **`Rendered Text(A) ≠ Rendered Text(B)`** across 100% of placements.

---

## 8. React Query & Cache Invalidation (Critical Test)

The test verified the behavior immediately following the form submission on `/onboarding/birth-data`:
1. `saveBirthData` saved data to PostgREST and invoked `/v1/astrology/profile/recalculate`.
2. `queryClient.invalidateQueries` immediately marked keys `["astrology"]`, `["birth-data"]`, `["natal-observations"]`, and `["profile"]` as invalid.
3. The router navigated to `/me`.
4. React Query automatically executed background refetches for:
   - `["astrology", "me"]` → `GET /v1/astrology/profile/safe-astro`
   - `["natal-observations", ...]` → `POST /v1/interpretations/resolve-natal`
5. **No 30-second stale window observed.**
6. **No manual page reload (F5) required.**
7. **No logout/login required.**
8. The UI re-rendered new cards instantaneously.

---

## 9. Network Trace

Inspecting actual browser network requests during the A/B update demonstrated the following sequence:

1. `POST http://127.0.0.1:54321/rest/v1/birth_data?on_conflict=user_id`  
   **Status:** `201 Created` / `204 No Content`
2. `POST http://127.0.0.1:8000/v1/astrology/profile/recalculate`  
   **Status:** `200 OK`
3. `GET http://127.0.0.1:8000/v1/astrology/profile/safe-astro`  
   **Status:** `200 OK` (Returned Scorpio Sun, Leo Moon, Gemini Asc, etc.)
4. `POST http://127.0.0.1:8000/v1/interpretations/resolve-natal`  
   **Status:** `200 OK` (Returned 8 resolved items with asset IDs and Georgian texts)
5. `GET http://127.0.0.1:8000/v1/profiles/me`  
   **Status:** `200 OK`

---

## 10. Refresh Test (F5)

After State B was displayed, the browser subagent refreshed the page (`F5` / reload):
- Placements displayed: Sun Scorpio, Moon Leo, Ascendant Gemini, Mercury Scorpio, Venus Sagittarius, Mars Sagittarius.
- Georgian copy: identical to State B.
- No fallback or regression to State A occurred.

---

## 11. Logout / Login Persistence Test

1. User A logged out using the UI button (`🚪 გასვლა`).
2. React Query cache was explicitly cleared (`queryClient.clear()`).
3. Browser navigated to `/auth/login`.
4. User A signed back in with `e2e_user_a_real@jester.app` / `Password123!`.
5. Browser navigated to `/me`.
6. Verified:
   - Sun: Scorpio
   - Moon: Leo
   - Ascendant: Gemini
   - Mercury: Scorpio
   - Venus: Sagittarius
   - Mars: Sagittarius
   - Observation cards: 100% matched State B.
   - Zero State A residual content was loaded.

---

## 12. User Isolation Test

User B was logged in on the same browser environment (`e2e_user_b_real@jester.app`):
- User B Display Name: `RealUserB`
- Placements displayed:
  - Sun: **Cancer** (`self.identity.sun_cancer.v1`)
  - Moon: **Aquarius** (`self.emotional.moon_aquarius.v1`)
  - Ascendant: **Scorpio** (`self.persona.rising_scorpio.v1`)
  - Mercury: **Leo** (`self.cognition.mercury_leo.v1`)
  - Venus: **Leo** (`self.relation.venus_leo.v1`)
  - Mars: **Taurus** (`self.action.mars_taurus.v1`)
  - Element: **Water** (`self.element.water_dominant.v1`)
  - Modality: **Fixed** (`self.modality.fixed_dominant.v1`)

**Isolation Verification Result:**
- User B sees ONLY User B's personalized data.
- User A never receives User B's data.
- User B never receives User A's data.
- React Query cache is fully sanitized across sessions via `queryClient.clear()` on logout.

---

## 13. Debug Lab Cross-Check

The developer forensic page at `http://localhost:3000/__debug/backend-audit` was inspected live as authenticated User A:

- **Section 1 (Auth User):** `e91ae2f2-904f-4d78-b379-08344524f335` (`e2e_user_a_real@jester.app`)
- **Section 2 (PostgreSQL Persistence):** `1995-11-15`, `18:30:00`, `Asia/Tbilisi`, `41.7151`, `44.8271`, `Tbilisi, Georgia`
- **Section 3 (Calculated Astrology):** Sun Scorpio, Moon Leo, Ascendant Gemini, Mercury Scorpio, Venus Sagittarius, Mars Sagittarius, Element Fire, Modality Fixed, Version 2
- **Section 4 (Safe API Response):** Derived profile matched calculated positions.
- **Section 5 (Resolved Interpretations):** IDs matched `self.identity.sun_scorpio.v1`, `self.emotional.moon_leo.v1`, etc.
- **Section 6 (Integrity Matrix):** All checks showed `PASS`.

The Debug Lab matches the `/me` page with 100% consistency.

---

## 14. Bugs Found & Addressed

1. **Missing Mercury, Venus, Mars Badges on `/me` Cards:**
   - *Observed:* Cards for cognition, relation, and action displayed titles and Georgian text, but lacked visual sign chips.
   - *Root Cause:* `getSupportingSignalBadge` only had switch branches for identity, emotional, persona, element, and modality.
   - *Fix:* Added branches for `self.cognition`, `self.relation`, and `self.action` displaying `მერკურის ნიშანი: {astro.mercury_sign}`, `ვენერას ნიშანი: {astro.venus_sign}`, and `მარსის ნიშანი: {astro.mars_sign}`.
2. **Interpretation Asset ID Visibility:**
   - *Observed:* Observation card footer showed tone and content status, but not the resolved asset ID.
   - *Fix:* Added `<span>ID: <code>{obs.interpretation?.id}</code></span>` in `MePage.tsx` to enable direct auditability of the underlying corpus asset.
3. **Cache Clearing on User Logout:**
   - *Observed:* `signOut` in `context.tsx` reset Supabase auth state but did not clear TanStack React Query cache, leaving a theoretical risk of stale cache on immediate relogin.
   - *Fix:* Integrated `useQueryClient` in `AuthProvider` and invoked `queryClient.clear()` both on `signOut()` and when `session` is null in `onAuthStateChange`.

---

## 15. Final Acceptance Matrix

| Criterion | Requirement | Result | Evidence |
| :--- | :--- | :---: | :--- |
| **REAL REGISTERED USER** | Real Supabase user created through UI | **PASS** | `auth.users` UUID `e91ae2f2-904f-4d78-b379-08344524f335` |
| **REAL FRONTEND AUTH** | Session & JWT via `@supabase/supabase-js` | **PASS** | Bearer auth accepted by FastAPI on `/v1/*` |
| **BIRTH DATA PERSISTED** | State A written to `public.birth_data` | **PASS** | `1990-03-21 06:00 Europe/London` in DB |
| **BIRTH DATA UPDATE PERSISTED** | State B updated via UI form | **PASS** | `1995-11-15 18:30 Asia/Tbilisi` in DB, `v2` |
| **ASTROLOGY RECALCULATED** | Recalculation runs via PySwissEph | **PASS** | `public.astro_private` & `public.astro_safe_profile` |
| **API UPDATED** | `/v1/astrology/profile/safe-astro` updated | **PASS** | Returns Scorpio Sun, Leo Moon, Gemini Asc, Sag Venus/Mars |
| **CORRECT CONTENT RESOLVED** | Assets resolved in Georgian (`ka`) | **PASS** | `self.identity.sun_scorpio.v1`, `self.emotional.moon_leo.v1`, etc. |
| **FRONTEND RECEIVED NEW DATA** | React Query queries refreshed | **PASS** | Network log captures 200 OK responses |
| **FRONTEND RENDERED NEW TEXT** | Text matches approved corpus assets | **PASS** | Exact Georgian text verified verbatim |
| **NO STALE CACHE** | Immediate UI update without F5 | **PASS** | State B showed immediately upon redirect |
| **REFRESH CONSISTENT** | F5 maintains State B | **PASS** | Page reload preserves all State B data |
| **LOGOUT/LOGIN CONSISTENT**| Relogin maintains State B | **PASS** | Session restart preserves State B data |
| **USER ISOLATION** | User A and User B completely isolated | **PASS** | User B sees Cancer/Aquarius/Scorpio; zero cross-talk |
| **DEBUG LAB CROSS-CHECK** | `/__debug/backend-audit` parity | **PASS** | 100% agreement across all 6 sections |

---

## 16. Final Sign-off

The final E2E verification of real registered users across the entire stack (`Browser -> React Query -> Supabase -> PostgreSQL -> Swiss Ephemeris -> FastAPI -> Corpus Resolver -> Rendered Text`) is **100% PROVEN AND PASSING**.

As instructed by the rule protocol, all work is now stopped pending product owner review.
