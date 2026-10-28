# JESTER Project Brief — Verified Repository Context

> **Document Status:** VERIFIED REPOSITORY CONTEXT  
> **Source of Truth:** Canonical docs, design tokens, and frontend code checked into `farnai/Jester`  
> **Target Audience:** Jester Visual Studio agents (`jester-art-director`, `jester-ui-designer`, `jester-graphic-designer`, `jester-visual-critic`)  
> **Authority Level:** Authoritative Visual Design Reference  

---

## 1. Verified Product Identity

JESTER is a **People Discovery and Relationship Intelligence platform**. It is engineered to help human beings understand themselves, understand others, and navigate the subtle dynamics of interpersonal chemistry—spanning friendships, creative collaborations, activity partnerships, intellectual dialogues, and intentional dating.

- **Core Product Loop:**
  $$\mathbf{ME} \longrightarrow \mathbf{YOU} \longrightarrow \mathbf{US} \longrightarrow \mathbf{MORE\ PEOPLE}$$
- **Axioms:**
  - *"They show the match. JESTER explains the connection."*
  - *"Score creates curiosity. Interpretation creates value."*
  - *"The insight becomes the invitation."*
- **Astrology’s Role:** Deterministic, mathematical computational intelligence layer running Swiss Ephemeris (`pyswisseph`) C-bindings and frozen `synastry-v1.0.0` algorithm. Astrology is **not** the consumer brand. Technical symbols ($\degree$, house cusps, natal wheel drawings) are filtered out of primary user surfaces.
- **AI’s Role:** Stylistic translator and voice engine governed by strict semantic contracts. JESTER has **no open conversational chatbot**; users chat only with authenticated humans.

*Source references:* `docs/JESTER_PRODUCT_FOUNDATION.md#L11-L30`, `docs/JESTER_STRATEGIC_MARKETING_FOUNDATION.md#L11-L26`, `AGENTS.md#L5-L15`.

---

## 2. Core Brand Differentiation

Unlike traditional astrology apps that focus on solitary self-obsession, esoteric jargon, and fatalism, and unlike dating apps that reduce humans to superficial photo-swiping, JESTER explains **why people click, clash, challenge, or complement each other**.

| Dimension | Traditional Astrology Apps | Dating & Social Apps | JESTER |
| :--- | :--- | :--- | :--- |
| **Primary Focus** | Self / Identity (*"Who am I?"*) | Visual Matching (*"Do I like them?"*) | Relationship Intelligence (*"Why do we click?"*) |
| **Tone** | Esoteric, cryptic, dramatic, fatalistic | Superficial, gamified | Sharp, witty, playful, observant, intelligent |
| **Relational Scope** | Individual natal charts | Romantic / sexual only | All relational intents (friends, collab, activity, dating) |
| **Interaction** | Solitary reading | Rapid card swiping | Intentional editorial discovery & dialogue |

*Source references:* `docs/JESTER_STRATEGIC_MARKETING_FOUNDATION.md#L116-L125`, `docs/JESTER_PRODUCT_FOUNDATION.md#L33-L59`.

---

## 3. Marketing, JESTER Archetype & Communication Principles

- **The Contemporary JESTER Archetype:** Inspired by the historical court Jester reinterpreted for contemporary culture — *"The one who tells you the truth nobody else dares to tell you — and makes you smile while doing it."* Entering Home should make the user feel like an honored guest in an intelligent, irreverent contemporary salon/court (distinguished and personally addressed, never literal medieval heraldry, crowns, parchment, or circus kitsch).
- **Organic Growth Trigger:** The primary viral loop is **"The insight becomes the invitation."** Growth occurs when an insight is so sharp, funny, and psychologically astute that the user screenshots or shares it directly:
  *„ნახე, ჩემზე რას წერს JESTER 😂“* $\rightarrow$ *„შენც ნახე შენზე, მერე ჩვენი შედარება ვნახოთ.“*
- **Tone & Voice ("Witty Truth, Not Generic Motivation"):** Sharp, playful, observant, warm, and occasionally sarcastic toward human contradictions — never cruel, never humiliating, never attacking dignity or identity, and immediately dialing down sarcasm during errors or emotionally sensitive states.
- **Intent Primacy:** Declared relationship intent governs copy tone. Non-romantic intents (`new_friends`, `creative_collab`, `deep_talks`) strictly prohibit romantic or sexual framing of synastry signals.

*Source references:* `docs/JESTER_STRATEGIC_MARKETING_FOUNDATION.md#L24-L26`, `docs/JESTER_PRODUCT_FOUNDATION.md#L77-L85`, `docs/COMMUNICATION_SYSTEM_V1_SPEC.md#L228-L232`.

---

## 4. Target Users & Main Motivations

- **Primary Demographic:** Socially curious young adults **18–28 years old** (students, young professionals, digitally native social explorers).
- **Public Launch Policy:** Strict **18+ platform boundary** (under-18 barred from registration and social features).
- **Core User Motivations (Jobs to Be Done):**
  1. *Morning Routine:* A sharp, witty 1–2 sentence personal lens on the day without wading through an essay.
  2. *Meeting Someone New:* Figure out why someone feels familiar or completely different; understand communication sparks and friction points.
  3. *Friendship Validation:* Playful insight into why best friends laugh for hours but argue over small decisions.
  4. *Social Group Dynamic:* Perceptive content to post in the group chat and laugh over together.

*Source references:* `docs/JESTER_STRATEGIC_MARKETING_FOUNDATION.md#L61-L92`, `docs/JESTER_PRODUCT_FOUNDATION.md#L259-L261`.

---

## 5. Exact Approved Colors & Design Tokens

Approved aesthetic: **"Warm Modern Editorial Social Discovery"**  
Authoritative source: `frontend/src/ui/tokens/colors.ts`, `docs/design/JESTER_COLOR_DESIGN_SYSTEM_V1.md`, `docs/JESTER_DESIGN_EXPLORATION.md#L44-L75`.

### Primary Action & Brand Accent (Carrot Orange)
- `palette.brand.orange500`: `#FF7A2F` — Core Primary Brand Accent / CTA
- `palette.brand.orange600`: `#E9681F` — Hover state
- `palette.brand.orange700`: `#C95618` — Pressed / Active state
- `palette.brand.orange800`: `#9E4215` — Focus ring & Dark-orange white-label variant
- `palette.brand.orange100`: `#FFE7D7` — Subtle accent background
- `palette.brand.orange50`:  `#FFF6F0` — Soft pill wash

### Surfaces & Canvas (Warm Editorial Paper)
- `palette.surface.canvas`:  `#FAF7F2` — Main page background (warm paper tone)
- `palette.surface.card`:    `#FFFFFF` — Editorial card surface
- `palette.surface.alt`:     `#F3EEE6` — Subtle secondary section surface
- `palette.surface.base`:    `#FFFDFA` — Elevated container base

### Typography Tones
- `palette.text.primary`:    `#222630` — Deep charcoal ink (5.82:1 WCAG contrast on `#FF7A2F`)
- `palette.text.secondary`:  `#6A716F` — Neutral slate (body, subtitles)
- `palette.text.tertiaryDecorative`: `#8B918F` — Metadata, captions, timestamps
- `palette.text.inverse`:    `#FFFFFF` — White text on dark/orange-800 surfaces

### Critical Contrast Rule
Primary button labels on `#FF7A2F` MUST use `#222630` (charcoal), achieving 5.82:1 contrast. White text on `#FF7A2F` fails WCAG AA and is strictly prohibited; white text is permitted only on `#9E4215` (`orange800`).

### Supporting Insight & Accent Tones
- `palette.support.sage500`: `#788A69` — Calm botanical sage
- `palette.support.sage100`: `#E8EFE2` — Soft calm insight card background
- `palette.support.sageInk`: `#4B6242` — High-contrast text on sage surfaces
- `palette.accent.peach`:    `#F5DDD1` — Warm peach accent
- `palette.accent.peachSoft`: `#FBEEE7` — Soft peach insight card background

### Hairline Borders
- `palette.border.soft`:        `#E6E0D7` — Default card & section divider
- `palette.border.muted`:       `#D8D1C7` — Darker border
- `palette.border.interactive`: `#8F8A83` — 3:1+ WCAG non-text input borders

---

## 6. Typography & Georgian Font Requirements

Authoritative source: `frontend/src/ui/tokens/typography.ts`, `docs/JESTER_DESIGN_EXPLORATION.md#L81-L104`, `docs/JESTER_PRODUCT_FOUNDATION.md#L264-L271`.

- **Primary Locale:** Georgian (`ka`) First; English (`en`) Secondary.
- **Font Stack:** FiraGO, Noto Sans Georgian, Sylfaen, system-ui sans-serif.
- **Mkhedruli Script Mechanics:**
  - Standard Mkhedruli has **no native uppercase/lowercase distinction**. Visual hierarchy must be achieved through font weight contrast (`700 Bold` / `800 Heavy`), size scaling, and color value, rather than `text-transform: uppercase`.
  - Mkhedruli letters (დ, ტ, ფ, ქ, ყ, შ, ჩ, ც, ძ, წ, ჭ, ხ, ჯ, ჰ) have pronounced vertical ascenders, descenders, and rounded loops. Line-height MUST be **minimum 1.55** (ideally 1.55–1.65) to prevent colliding lines.
  - Georgian words are **20% to 35% longer** than English equivalents. Containers, buttons, and navigation tabs must provide generous horizontal padding and avoid arbitrary narrow clipping widths.
- **Type Scale:**
  - `Display 3xl`: 30–32px / line-height 48px / Weight 800 (Heavy)
  - `Heading 2xl`: 24px / line-height 36px / Weight 700 (Bold)
  - `Title xl`: 20px / line-height 30px / Weight 600 (Semibold)
  - `Subhead lg`: 18px / line-height 28px / Weight 500 (Medium)
  - `Body Base`: 16px / line-height 26px (1.62) / Weight 400 (Regular)
  - `Caption sm`: 14px / line-height 22px / Weight 400 (Regular)
  - `Micro xs`: 12px / line-height 18px / Weight 600 (Semibold)

---

## 7. Current Application UI Architecture

Authoritative source: `docs/reports/JESTER_FRONTEND_PRODUCT_INVENTORY.md#L62-L100`, `frontend/src/navigation/AppRoutes.tsx`.

- **Framework:** React 19, TypeScript, Vite, TanStack React Query v5.
- **State & Auth:** Supabase Auth with central `AuthProvider`, JWT verification, and Supabase Realtime WebSocket channels (`public:messages`, `public:notifications`).
- **Core Route Structure:**
  - `/` — `HomePage` (Authenticated front door: daily energy, circle moment, discovery preview)
  - `/discover` — `DiscoverPage` (Vertical candidate browsing with `PersonCard`)
  - `/people/:id` — `PersonProfilePage` (Profile, curiosity score, compatibility hook)
  - `/people/:id/why` — `WhyPage` (Deep dive into relational dynamics, harmonic dimensions)
  - `/compare/:id` — `ComparePage` (Dual-card comparative analysis)
  - `/connections` — `ConnectionsPage` (Active, Incoming, Outgoing tabs with transitions)
  - `/messages` & `/chat/:id` — `MessagesPage` & `ChatPage` (Real-time direct messaging)
  - `/me` — `MePage` (Self natal insights & profile editing)
  - `/notifications` — `NotificationsPage` (Incoming connection & system events)
  - `/onboarding/birth-data` — `BirthDataOnboardingPage` (8-step wizard)

---

## 8. Existing Reusable UI Components

Authoritative source: `frontend/src/modules/home/HomeElements.tsx`, `frontend/src/shared/components/AppShell.tsx`, `frontend/src/modules/discover/PersonCard.tsx`.

1. `AppShell`: Persistent navigation with top bar (logo, notifications badge, profile link) and bottom mobile navigation tab bar (მთავარი, აღმოაჩინე, კავშირები, საუბრები, ჩემი პროფილი).
2. `HomeAvatar`: Circular avatar with initial fallback and ring styling (`large` variant supported).
3. `HomeIcon`: SVG icon helper supporting `sparkles`, `people`, `chevron`, `arrow`, `quote`.
4. `HomeState`: Standardized empty, loading, and error state container with retry action.
5. `HomeSkeleton`: Pulsing shimmer loading placeholder matching editorial proportions.
6. `PersonPreview` / `PersonCard`: Card container displaying avatar, name, occupation, city, connection status badge, JESTER quote, and action links.

---

## 9. Current Home Content & Data States

Authoritative source: `docs/HOME_EXPERIENCE.md`, `frontend/src/modules/home/HomePage.tsx`, `frontend/src/modules/home/homeModel.ts`.

### Content Sections
1. **Greeting & Eyebrow Pill:** `შენი სივრცე · [ქართული თარიღი]` + `გამარჯობა, [სახელი]` + `შენით იწყება. ადამიანებით გრძელდება.`
2. **01 ME Hero Insight:**
   - Label: `ME · პირადი სივრცე · [თარიღი ან პირადი ხედვა]`
   - Kicker: `დღის დაკვირვება` (if `real_transit`) or `შენი პროფილის დაკვირვება`
   - Title: `daily.data?.label || 'რას ამჩნევს JESTER'`
   - Quote: Full text observation (expandable if >180 chars)
   - Guidance Disclosure: `დღის პატარა მინიშნებები` (`სცადე ↗` / `ნუ იჩქარებ ↘`)
   - Actions: One-tap copy (`კოპირება`), "რატომ ამბობს ამას JESTER?" explanation disclosure, direct link to `/me`.
3. **02 US Relationship Moment (Contextual):**
   - If accepted connections exist: Highlights one connected person with relational synastry quote and direct CTA to `/people/:id/why`.
   - If incoming requests exist: Action banner prompting review of incoming connections.
   - If no connections: Warm prompt encouraging discovery.
4. **03 Discovery Preview (MORE PEOPLE):**
   - 2–3 distinct deduplicated profiles with name, photo, city, occupation, and authentic observation/bio quote.
   - Secondary filter toggle: `დაკვირვებით` (observed insights) vs `ყველა` (all people).
   - "ყველა ადამიანი" CTA leading to `/discover`.
5. **04 Profile Prompt:** Invitation to complete/refine own profile.

### Data States Handled
- `loading`: Pulsing skeletons on hero and discovery cards.
- `error`: Inline retry cards preserving other functional sections.
- `empty_connections`: Thoughtful first-connection path without mock data.
- `copied`: Visual feedback when copying insight text.

---

## 10. Brand Restrictions & Prohibited Visual Tropes

Authoritative source: `docs/JESTER_DESIGN_EXPLORATION.md#L34-L41`, `docs/JESTER_PRODUCT_FOUNDATION.md#L33-L59`.

Strictly prohibited visual directions:
- ❌ **No Generic SaaS Dashboard Boxes:** Monotonous grids of equal white rounded boxes, tiny 10px text, repetitive numbered cards (`01`, `02`, `03`).
- ❌ **No Cosmic Occult Temple Kitsch:** Floating purple crystal balls, celestial velvet gradients, zodiac wheels, planetary degree symbols ($\degree$) in primary UI.
- ❌ **No Circus Clowns or Carnivals:** Jester hats with bells, carnival diamonds, harlequin costumes.
- ❌ **No Medieval Fantasy Heraldry:** Parchment textures, wax seals, shields, swords.
- ❌ **No Cartoon Mascots:** Bouncing cartoon characters (no Duolingo-style owls or Clippy equivalents).
- ❌ **No Reflexive Disposable Matching Mechanics on Home:** Contextless binary hot-or-not cards, gamified discard culture, and naked percentage numbers without psychological meaning. (Note: Swipeable candidate deck is approved specifically for Mobile Discovery under [FDR-2026-01](../../docs/FOUNDER_DECISION_RECORDS.md#fdr-2026-01-photo-first-human-discovery-touch-native-swipe-interaction-policy) with intentional bilateral confirmation; Home remains a curated editorial overview).

---

## 11. Creative Opportunities

Areas where the AI Art Director, UI Designer, and Graphic Designer have complete creative freedom:

1. **Editorial Composition & Spatial Rhythm:** Asymmetrical layouts, dynamic visual weight, generous desktop breathing room (1200–1320px container), and intentional whitespace.
2. **Card Geometry & Asymmetry:** "Motley" modular patchwork where card modules vary organically in proportion rather than feeling stamped from a template.
3. **Graphic Language & Brand Motifs:**
   - Abstract conversational sparks (subtle intersecting line-work, resonance waves).
   - Warm organic apertures and light-wash highlights.
   - Elegant, minimalist geometric brackets for quotes and insights.
4. **Visual Storytelling:** Framing interpersonal chemistry through relatable editorial photography, expressive type hierarchy, and authentic human moments.
5. **Editorial Micro-Interactions:** Subtle haptic compressions, warm border light transitions, refined expandable drawer sheets.

---

## 12. Source Document Map

| Domain | Canonical Repository Document | Status / Authority |
| :--- | :--- | :--- |
| **Founder Decision Records** | `docs/FOUNDER_DECISION_RECORDS.md` | Binding (Level 1.5) |
| **Product Foundation** | `docs/JESTER_PRODUCT_FOUNDATION.md` | Authoritative (Level 2) |
| **Marketing Foundation** | `docs/JESTER_STRATEGIC_MARKETING_FOUNDATION.md` | Authoritative (Level 3) |
| **Design Exploration** | `docs/JESTER_DESIGN_EXPLORATION.md` | Explorations & Approved Tokens |
| **Color Design System** | `docs/design/JESTER_COLOR_DESIGN_SYSTEM_V1.md` | Authoritative Color Tokens |
| **Active Color Code** | `frontend/src/ui/tokens/colors.ts` | Source Implementation |
| **Active Typography Code** | `frontend/src/ui/tokens/typography.ts` | Source Implementation |
| **Home Experience Spec** | `docs/HOME_EXPERIENCE.md` | Authoritative Screen Spec |
| **Frontend Architecture** | `docs/architecture/JESTER_PRODUCT_FRONTEND_ARCHITECTURE_V1_2.md` | Authoritative Architecture |
| **Frontend Inventory** | `docs/reports/JESTER_FRONTEND_PRODUCT_INVENTORY.md` | Authoritative Technical Audit |
| **AI & Voice Architecture** | `docs/AI.md` | Authoritative Voice Spec |
| **Connections & Messaging** | `docs/CONNECTION_MESSAGING_SYSTEM_V1_SPEC.md` | Authoritative Domain Spec |
| **Security & Privacy** | `SECURITY.md`, `docs/SECURITY.md` | Authoritative Security Policy |

---

## 13. Contradictions, Token Drift & Verified Capability Boundaries

1. **Historic Violet/Indigo Palette vs Approved Carrot Orange:**  
   *Finding:* Historical prototypes (`docs/archive/historical/`) and early tokens used Indigo/Violet (`#6366f1`).  
   *Resolution:* Fully superseded by Founder-approved Warm Carrot Orange (`#FF7A2F`) and Warm Canvas (`#FAF7F2`) documented in `docs/design/JESTER_COLOR_DESIGN_SYSTEM_V1.md` and implemented in `frontend/src/ui/tokens/colors.ts`.
2. **Typography Token Drift (`typography.ts` vs `index.css` & Design Docs):**  
   *Finding:* `frontend/src/ui/tokens/typography.ts` lists system fonts without `Noto Sans Georgian` and sets `tight: 1.2`, while `frontend/src/index.css` self-hosts `NotoSansGeorgian-*.woff2` (weights 300–900) and `docs/JESTER_PRODUCT_FOUNDATION.md#L269` mandates `line-height >= 1.55` and minimum `12px` text (`homeEditorial.css` currently violates this with `9px–11px` labels and `1.24` line-height).  
   *Resolution:* Visual designs MUST use `Noto Sans Georgian`, `line-height >= 1.55` for Georgian body/UI copy, bold weight contrast (`700`/`800`) instead of `uppercase`, and a strict `12px` floor.
3. **Anti-Swipe Mandate vs Wave 3 Discovery Deck:**  
   *Finding:* `docs/JESTER_PRODUCT_FOUNDATION.md#L55` historically forbade swipe dating mechanics, creating a documented tension with Wave 3 (`docs/DISCOVERY_WAVE3.md`, `frontend/src/modules/discover/DiscoverSwipeCard.tsx`).  
   *Resolution:* Formally reconciled by Founder Decision [FDR-2026-01](../../docs/FOUNDER_DECISION_RECORDS.md#fdr-2026-01-photo-first-human-discovery-touch-native-swipe-interaction-policy). Touch-native mobile candidate deck is approved for Social Discovery with bilateral consent confirmation and gesture decoupling (photo scrubbing vs candidate navigation). Authenticated Home remains human-first, curated, and editorial (vertical/scrollable story cards, photo-first highlights) with zero binary discard swiping on Home. Photo geometry follows [FDR-2026-02](../../docs/FOUNDER_DECISION_RECORDS.md#fdr-2026-02-photo-framing-geometric-hierarchy): natural proportions with restrained rounded corners (`rounded-2xl`/`rounded-3xl`) for large photography; arches/cameos for small avatars and seals. Future iterations synthesize `KZzuf` (Warm Paper Salon) and `phkQC` (Theatrical Spotlight Stage with Truth-Flip) per [FDR-2026-03](../../docs/FOUNDER_DECISION_RECORDS.md#fdr-2026-03-visual-exploration-synthesis-kzzuf-architecture-phkqc-stage).
4. **Verified Backend Capabilities (`EXISTING` / `DERIVABLE`) vs Unimplemented Specs (`PROPOSED`):**  
   - **`EXISTING`:** `GET /v1/interpretations/daily-energy` computes real Swiss Ephemeris planetary transits (`detection_mode: "real_transit" | "neutral_baseline" | "fallback_sun_sign"`) and returns **exact 3 `do` and 3 `dont` Georgian micro-tags** (`backend/app/interpretation/data/daily_energy_tags.json`).  
   - **`DERIVABLE` on Home:** `POST /v1/interpretations/resolve-natal` resolves **10 personal `ME` dimensions** (`identity`, `emotional`, `persona`, `cognition`, `relation`, `action`, `element`, `modality`, `synthesis`, `verdict`) when `mercury_sign`, `venus_sign`, and `mars_sign` from `GET /v1/astrology/profile/safe-astro` are passed. `GET /v1/discovery/people` returns up to **6 authorized gallery photos** (`photos[]`), `interests[]`, and **`common_interest_ids[]`** (verified shared interests).  
   - **`PROPOSED` (0% DB/API today):** User-written profile prompt answers (`docs/PROMPTS_SELF_EXPRESSION_SYSTEM_V1_SPEC.md`) have no SQL migration (`001`–`031`) or FastAPI endpoint yet; only `bio` and `occupation` exist in `public.profiles`. Any prompt-answer UI in explorations must be explicitly labeled `PROPOSED`.
5. **Compatibility Gate (`POST /v1/compare` vs `POST /v1/interpretations/compare-preview`):**  
   *Finding:* `/v1/compare` and `/v1/people/{id}/why` strictly require an `accepted` connection (`403` otherwise), and Wave 3 discovery cards set `compatibility_score: null`. Home must never fabricate compatibility scores or expose private birth data.
