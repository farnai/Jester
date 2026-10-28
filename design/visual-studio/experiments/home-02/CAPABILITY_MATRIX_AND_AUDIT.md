# JESTER Home Reimagination — Capability Matrix, Token Audit & Existing Home Critique

- **Experiment ID:** `home-02`
- **Target Surface:** Authenticated User Home (`/`)
- **Active Branch Inspected:** `codex/home-editorial-reference` (`HEAD: 97a28bc`, uncommitted Home editorial & Visual Studio work preserved intact)
- **Authority Hierarchy:** Code & Migrations (`001`–`031`) $\rightarrow$ Automated/Runtime Tests $\rightarrow$ Approved Product & Design Specs $\rightarrow$ Explorations (`docs/archive/**` excluded as truth)

---

## 1. Direct 8-Point UX Critique of Existing Home (`codex/home-editorial-reference`)

Inspected artifacts: `frontend/src/modules/home/HomePage.tsx`, `frontend/src/modules/home/HomeEditorial.tsx`, `frontend/src/modules/home/homeEditorial.css`, `.jester/reports/verification/home-refinement/home-1440.png`, `.jester/reports/verification/home-refinement/home-390-viewport.png`, and `.jester/reports/verification/home-refinement/home-390.png`.

### 1.1 What Currently Works
- **Disciplined Color & Contrast Foundation:** Warm Paper Canvas (`#FAF7F2`), Carrot Orange (`#FF7A2F`) with accessible Deep Charcoal (`#222630`) button labels inside `.home-experience`, and zero crypto/dark-SaaS/occult zodiac-wheel clichés.
- **Privacy & Data Integrity:** `ProfileImage` properly fetches protected media via authenticated `blob:` URLs without leaking JWTs into DOM attributes; blocked users are filtered; `real_transit` vs `fallback_sun_sign` provenance is tracked truthfully; independent section error/retry states prevent full-page crashes.
- **5-Destination App Navigation:** Clear top bar (Desktop) and 48px opaque bottom dock (Mobile) for `მთავარი`, `აღმოაჩინე`, `კავშირები`, `საუბრები`, `პროფილი`.

### 1.2 What Feels Generic
- **Unauthenticated Marketing Hero on an Authenticated Screen:** Nearly half of the first screen is occupied by a static slogan (*„კარგი საუბარი შემთხვევით არ იწყება“*) and two decorative registration portraits of strangers. For a logged-in returning user, seeing the exact same generic landing-page banner every morning feels impersonal and static.
- **4-Box Dashboard Shortcut Strip (`HomeQuickActions`):** Immediately beneath the top navigation bar, four pastel boxes repeat the exact same routes (`ჩემი ინსაითი`, `ახალი ადამიანები`, `ჩემი კავშირები`, `საუბრები`) already present in the header and mobile bottom dock.
- **Uniform 4-Column White Card Grid in Discovery:** Candidates without avatars collapse into oversized `SB` / `DA` / `AA` initial circles above identical boilerplate (*„აქ ჯერ ცოტა რამ წერია. გაცნობა პროფილიდან შეგიძლია დაიწყო.“*), looking like an enterprise employee directory rather than a social discovery experience.

### 1.3 What Weakens JESTER's Brand Personality
- **Polite Wellness Tone Instead of the JESTER Archetype:** Copy such as *„შეხედე საკუთარ თავს“* and *„გააგრძელე ნაცნობი ამბავი“* could belong to any journaling or mindfulness app. There is no trace of the sharp, observant, playfully irreverent court truth-teller (*„ის, ვინც გეუბნება სიმართლეს, რომელსაც სხვა ვერ გიბედავს — და თან გაღიმებს“*).
- **Zero Sense of Personal Occasion:** Entering Home feels like loading a static web template rather than stepping into your own privileged, intelligent personal court where JESTER already noticed something specific about your day and your circle.

### 1.4 What Creates Unnecessary Cognitive Load
- **Triple Navigation Duplication:** Top bar + 4 Quick Action tiles + Mobile bottom dock + inline section CTAs (`ყველა ->`, `ყველა ადამიანი ->`, `ჩემი პროფილი ->`) present 14+ navigation links for the same 5 destinations.
- **Double-Nested `<details>` Accordions (`HomePage.tsx#L232-L266`):** To see today's `Do / Don't` guidance or copy the insight, the user must expand `მინიშნებები და დეტალები` and then expand a second nested `დღის პატარა მინიშნებები` disclosure. Essential daily utility is hidden behind progressive-disclosure bureaucracy.
- **Micro-Labels & Competing Badges:** Eyebrows (`ME · პირადი სივრცე · 21 ოქტომბერი`, `დღის დაკვირვება`) stack three metadata rows before the actual headline, with several CSS rules dropping to `9px–11px`.

### 1.5 What Prevents Immediate Engagement
- **Daily Value Pushed Below the Mobile Fold:** In `home-390-viewport.png` (`390×844`), the decorative hero + 4 shortcut icons consume ~560px of vertical height, slicing the `ME` daily observation card in half before its action or `Do / Don't` items ever appear, while real people (`გაიცანი ადამიანები`) are pushed >1,200px down the page.
- **Passive Static Blocks:** Nothing in the first viewport invites a lightweight tactile micro-interaction (e.g., flipping a truth card, checking off one of today's 3 `Do` dares, switching between personal dimensions, or browsing a person's multi-photo story).

### 1.6 What Is Insufficiently Human-Centered
- **Underutilized Wave 2 & Wave 3 Human Data:** `HomePage.tsx` still consumes the legacy `DiscoveryPerson` typing (single avatar + bio/hook) instead of `DiscoveryDeckPerson` (`GET /v1/discovery/people`), ignoring up to **6 gallery photos**, **verified shared interests (`common_interest_ids`)**, and `same_city` context!
- **Disconnected Conversation Prompt:** The bottom orange card (*„ბოლოს რამ გაგაკვირვა?“*) is detached from any real person and simply drops the user at `/messages` or `/discover` without prefilling `?starter=` into an active chat.

### 1.7 What Works on Desktop vs Fails on Mobile
- **Desktop (`1440px`):** The 2-column `ME` / `US` split (`home-opening`) has reasonable editorial breathing room, though the 4-card Discovery row looks sparse when avatars/bios are missing.
- **Mobile (`390px` / `360px`):** The page becomes a ~2,900px vertical tower of stacked containers: Hero $\rightarrow$ 4 Quick Icons $\rightarrow$ `ME` Card $\rightarrow$ `US` List $\rightarrow$ 2×2 Cramped Grid $\rightarrow$ Orange Prompt $\rightarrow$ Profile Footer $\rightarrow$ 18+ Notice $\rightarrow$ Bottom Bar. A 2-column grid at `360px–390px` leaves only ~165px per person card, truncating Georgian words and squeezing human portraits into tiny squares.

### 1.8 Keep / Remove / Merge / Reinvent Decisions
- **KEEP:** Canonical Warm Paper + Carrot Orange + Sage + Peach + Deep Charcoal token system; `Noto Sans Georgian` (`line-height >= 1.55`); 5-tab navigation shell; privacy-safe `ProfileImage` (`blob:`) media loading; honest `real_transit` vs `fallback` provenance; independent section error/retry states; 18+ boundary.
- **REMOVE:** Unauthenticated-style marketing slogan hero with decorative stranger stock portraits; redundant 4-box `HomeQuickActions` bar; double-nested `<details>` hiding `Do / Don't`; cramped 2-column mobile person thumbnails; sub-`12px` micro-text.
- **MERGE:** Personal greeting + live circle pulse + today's personal JESTER hook into one immediate, mobile-first **Personal Stage / Morning Ritual** above the fold; merge standalone orange conversation prompt directly into **person/connection cards** where real `?starter=` handoff is actionable.
- **REINVENT:**
  1. **The JESTER Voice & Presence:** Turn dry headers into sharp, memorable Georgian observations with genuine humor and insight.
  2. **3 Do + 3 Don't Daily Pact:** Surface the existing 3 `do` and 3 `dont` items directly as a scannable, memorable visual ritual.
  3. **Progressive `ME` Self-Discovery:** Unlock `resolveNatal`'s 10 dimensions (`identity`, `emotional`, `cognition`, `relation`, `action`, `synthesis`, `verdict`) via effortless progressive reveal instead of a wall of text.
  4. **Human-First Discovery Cards:** Showcase real arch-framed photography, multi-photo gallery indicators, circular expressive overlays, verified shared interests (`common_interest_ids`), and JESTER's observation hook.

---

## 2. Verified Product & Technical Capability Matrix

Classification strictly per mission specification:
- **`EXISTING`** — Implemented in backend + database, exposed via API, and verified today.
- **`DERIVABLE`** — Deterministic backend endpoints/fields already exist and can be wired on Home without new backend architecture.
- **`PROPOSED`** — Specified in product docs (`*_V1_SPEC.md`) or proposed in design exploration, requiring new DB/backend/corpus work before production implementation.
- **`UNSUPPORTED`** — Cannot currently be justified by available evidence or architecture.

| Capability / Feature | User-Facing Experience on Home | Required Data & Exact Source / Endpoint | Status | Access & Privacy Gate | Missing Functionality / MVP Suitability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Daily Vibe & Personal Observation** | Archetype headline (e.g., *„სოციალური მაგნეტიზმი“*) + 1–2 sentence Georgian observation + honest provenance note | `GET /v1/interpretations/daily-energy?energy_type=auto&locale=ka` (`label`, `archetype`, `interpretation.text`, `detection_mode`, `date`) | **`EXISTING`** | `get_optional_user`; owner `birth_data` + `astro_private` stay server-only; Moon transit excluded when `birth_time_precision == 'unknown'` | **MVP-Ready.** Note: Live Swiss Ephemeris calculation runs on-demand per request; scheduled background push worker (`jobs/daily_energy.py`) is **`UNSUPPORTED`**. |
| **2. Three Daily "Do" & Three Daily "Don't" Suggestions** | Compact 3-item *Do* („დღეს გაბედე“) & 3-item *Don't* („დღეს მოერიდე“) daily ritual | `GET /v1/interpretations/daily-energy` $\rightarrow$ `do: string[3]`, `dont: string[3]` from `backend/app/interpretation/data/daily_energy_tags.json` | **`EXISTING`** (2–3 word tags)<br>**`PROPOSED`** (full witty sentences / category labels) | Public archetype guidance mapped from user's resolved `energy_type`; zero raw birth data exposed | **MVP-Ready** using existing 3+3 Georgian micro-tags. Interactive local "daily check" state is client-only **`DERIVABLE`**. Richer sentence-length per-transit Do/Don't copy requires corpus expansion (**`PROPOSED`**). |
| **3. Sharp / Sarcastic JESTER Greetings & Microcopy** | Ceremonial, witty Georgian UI framing, empty states, section hooks, and conversational transitions | Frontend localized UI copy + deterministic corpus (`tone: "witty"` in Content Architecture V2) | **`DERIVABLE`** (UI microcopy)<br>**`PROPOSED`** (new corpus tone variants) | Must roast human contradictions gently, never user dignity; dials down sarcasm on error/sensitive states | **MVP-Ready** for all structural UI headers, empty states, and transitions; new dynamic corpus copy variants are editorial **`PROPOSED`** additions. |
| **4. Deep Self-Discovery (`ME` Progressive Layers)** | Multi-facet self-exploration on Home (Identity, Emotion, Communication, Attraction, Action, Inner Synthesis, Verdict) | `GET /v1/astrology/profile/safe-astro` (`sun`, `moon`, `ascendant`, `mercury`, `venus`, `mars`, `element`, `modality`) + `POST /v1/interpretations/resolve-natal` (returns up to 10 `NatalResolveResponseItem`s) | **`DERIVABLE`** on Home (`EXISTING` in backend & `MePage.tsx`) | Strict JWT (`get_current_user`); `ascendant_sign` is `null` if birth time unknown (must gracefully omit `self.persona`); never expose degrees/houses | **MVP-Ready!** Simply pass `mercury_sign`, `venus_sign`, and `mars_sign` from `safe-astro` on Home to unlock all 9–10 resolved Georgian dimensions immediately. |
| **5. Human-First Multi-Photo Discovery Cards (6-Photo Gallery)** | Vertical / arch-cropped human portraits with multi-photo story switcher (`1..6` photos) + fallback state | `GET /v1/discovery/people` (`DiscoveryDeckPerson.photos: ProfilePhoto[]`, max 6 WebP photos, EXIF stripped) rendered via `ProfileImage` (`blob:`) | **`DERIVABLE`** on Home (`EXISTING` in `DiscoverPage.tsx` & backend) | Strict JWT + `is_discoverable = true` + `NOT is_user_blocked` (`404` privacy-safe); `Cache-Control: private, no-store` | **MVP-Ready!** Switch Home from legacy `DiscoveryPerson` typing to `API.discovery.people` (`DiscoveryDeckPerson`). |
| **6. Verified Shared Interests & Same-City Context** | Highlighted shared interest pills (`↔ არქიტექტურა`, `2 საერთო ინტერესი`) and `შენს ქალაქში · თბილისი` badge | `GET /v1/discovery/people` $\rightarrow$ `interests: InterestItem[]`, `common_interest_ids: string[]`, `same_city: boolean` | **`DERIVABLE`** on Home (`EXISTING` in backend & `DiscoverPage.tsx`) | Authenticated viewer comparison via server SQL `EXISTS`; blocked users excluded | **MVP-Ready!** Note: DB seed names in `026` are English (`Coffee`, `Travel`), so Georgian label mapping in frontend UI dictionary is recommended. |
| **7. Person Presence Observation ("რას ამჩნევს JESTER")** | Short intriguing personality hook on a person's card before opening full profile | `GET /v1/discovery/people` $\rightarrow$ `hook_observation.text`, `presence_sign_source` (`sun` or `ascendant`) | **`EXISTING`** | Safe single-person presence copy (Batch 7); never exposes birth date/time/place or unconsented synastry | **MVP-Ready.** |
| **8. User-Written Profile Prompt Answers** | Conversational Q&A cards on profiles (e.g., *„ჩემთან კამათი ღირს, თუ...“*) | Specified in `docs/PROMPTS_SELF_EXPRESSION_SYSTEM_V1_SPEC.md`; **0 tables in migrations `001`–`031`, 0 backend routes** | **`PROPOSED`** | Would require public-discoverable RLS + moderation rules; currently only `profiles.bio` and `profiles.occupation` exist (`EXISTING`) | **Not in current backend.** Must use `bio` + `hook_observation` for immediate MVP, and clearly label Prompt Q&A modules as **`PROPOSED`**. |
| **9. Connected Circle (`US`), Compatibility Why & Starter-to-Chat Handoff** | Active connections strip, unread message pulse, pairwise relationship insight, and 1-tap starter handoff into chat | `GET /v1/connections`, `GET /v1/conversations` (`unread_count`), `GET /v1/people/{id}/why` (`score`, `interpretation`, `conversation_starters`), `/chat/:id?starter=...` | **`EXISTING` / `DERIVABLE`** | `/why` & `/compare` strictly require `status == 'accepted'` (`403` otherwise); chat requires `accepted` & unblocked | **MVP-Ready!** Note: Pre-connection compatibility ranking across the discovery feed is **`UNSUPPORTED`** (`compatibility_score: null` in Wave 3). |
| **10. Native Text Share & Clipboard Copy** | One-tap sharing of JESTER's daily roast/insight with a friend (*"The insight becomes the invitation"*) | `frontend/src/platform/share.ts` (`navigator.share` + clipboard fallback) | **`EXISTING`** (text share)<br>**`PROPOSED`** (styled share-card PNG / referral link) | Shares only the user's chosen public insight quote, never private birth metadata | **MVP-Ready** for Web Share / Copy text; styled OG/story image export is **`PROPOSED`**. |

---

## 3. Documented Repository Contradictions & Design System Guardrails

1. **`typography.ts` vs `index.css` & Canonical Georgian Rules:** `frontend/src/ui/tokens/typography.ts` omits `Noto Sans Georgian` and sets `tight: 1.2`, whereas `frontend/src/index.css` loads self-hosted `NotoSansGeorgian` WOFF2 (300–900) and `docs/JESTER_PRODUCT_FOUNDATION.md#L269` mandates `line-height >= 1.55` and zero `uppercase` transforms on Mkhedruli text. **All 3 design concepts strictly enforce `Noto Sans Georgian`, `line-height >= 1.55` on body/cards (`>= 1.35` on large display headings with generous vertical clearance), bold weight contrast (`700`/`800`), and `>= 12px` minimum font size.**
2. **Primary CTA Contrast Invariant:** `docs/JESTER_DESIGN_EXPLORATION.md#L64` and legacy `.home-primary-link` in `home.css#L915` mention white text on `#FF7A2F` (2.60:1 WCAG FAIL). Per `docs/design/JESTER_COLOR_DESIGN_SYSTEM_V1.md#L46-L57` and `colors.ts#L95`, **every `#FF7A2F` surface MUST use `#222630` Deep Charcoal text (5.82:1 WCAG AA)**; white `#FFFFFF` text is permitted only on `#222630` Charcoal or `#9E4215` (`orange800`).
3. **No Astrological Jargon on Primary Surfaces:** `transits.py#L439` generates technical strings (`"ტრანზიტული ... ნატალურ ..."`), which conflicts with `jester.py#L31-L47`'s consumer jargon firewall. **All 3 Home concepts translate provenance into human-readable Georgian framing** (e.g., *„დღევანდელი რიტმისა და შენი ხასიათის გადაკვეთაზე“*) and keep raw technical labels out of primary headlines.

