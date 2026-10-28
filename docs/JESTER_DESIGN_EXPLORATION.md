# JESTER — Design Exploration & UI/UX Proposals

**Document Type:** UI/UX Design Exploration & Component Proposals  
**Authority Level:** Level 6 (Proposals & Explorations)  
**Audience:** Product Designers, UI/UX Designers, Frontend Engineers  
**Target Environment:** Mobile-First (Web, iOS, Android)  
**Status:** WORKING EXPLORATION (Subject to review and formal design approval)  

---

## ⚠️ How to Read This Document

Unlike [`docs/JESTER_PRODUCT_FOUNDATION.md`](JESTER_PRODUCT_FOUNDATION.md), **nothing in this document is a locked product requirement unless explicitly marked `[APPROVED]`**.

Every section is strictly tagged with its current status:
- **`[APPROVED]`**: Validated by product leadership or dictated by hard technical/linguistic constraints.
- **`[PROPOSAL]`**: A concrete, actionable design recommendation ready for prototyping and testing.
- **`[EXPLORATION]`**: An open concept, creative idea, or aesthetic direction undergoing exploration.
- **`[REJECTED]`**: An explicit anti-pattern or discarded direction that must not be used.

---

## 1. Aesthetic Mood & Character

### 1.1 Approved Direction: "Warm Modern Editorial Social Discovery" `[APPROVED]`
- **Concept:** A confident, human-centered, photography-rich editorial aesthetic tailored for adult social discovery. It pairs warm organic canvases with vibrant Carrot Orange accents, sophisticated sage/peach tones, and bold Georgian typography.
- **Feeling:** Human, observant, lively, warm, and subtly playful. It rejects generic SaaS dashboard cards, corporate financial sterility, neon AI mysticism, and swipe-dating commodification.
- **Core Principles:**
  - **Typographic Authority:** Noto Sans Georgian with strong weights (700/800) and generous line heights (1.55+).
  - **Human Photography First:** Authentic adult portraiture and social moments, not stock models or fake avatars.
  - **Spatial Composition:** Asymmetrical modern layouts, wide desktop breathing room (1200–1320px), no narrow 600px columns with half-blank viewports.
  - **Restrained Personality:** Witty, empathetic JESTER voice; astrology serves as deterministic intelligence, not visual clutter.

### 1.2 Rejected Visual Directions `[REJECTED]`
- ❌ **Generic SaaS Dashboard Cards:** Sea of equal white rounded boxes, tiny 10px text, repetitive numbered badges (`01`, `02`, `03`).
- ❌ **Medieval Fantasy / Renaissance Kitsch:** Parchment textures, heraldic shields, tarot cards.
- ❌ **Circus Clowns & Carnivals:** Floppy three-pronged hats, bells, carnival diamonds.
- ❌ **Cartoon Mascots:** Bouncing mascots (no Clippy, no Duolingo owl).
- ❌ **Cosmic Occult Temple:** Mystical crystal balls, purple-violet velvet gradients, zodiac wheels, planetary degree symbols in primary UI.
- ❌ **Superficial Meat-Market Clichés:** Contextless binary hot-or-not cards, gamified discard culture, and naked percentage numbers without psychological meaning. (Touch-native candidate browsing via a bounded deck is approved under [FDR-2026-01](FOUNDER_DECISION_RECORDS.md#fdr-2026-01-photo-first-human-discovery-touch-native-swipe-interaction-policy) with intentional bilateral confirmation; disposable matching mechanics remain strictly rejected).

---

## 2. Approved Brand & Color Tokens

### 2.1 Approved Brand System `[APPROVED]`
*(Reflected in `frontend/src/index.css` and `frontend/src/modules/home/home.css`)*

```typescript
export const jesterTokens = {
  // Brand Primary & Action
  brandOrange:      "#FF7A2F", // Core Carrot Orange CTA
  brandOrangeHover: "#E9681F", // Active/Hover state
  brandOrangeWash:  "#FFF6F0", // Soft pill background

  // Surfaces & Canvas
  surfaceCanvas:    "#FAF7F2", // Warm Canvas background
  surfaceCard:      "#FFFFFF", // Editorial White card surface
  surfaceElevated:  "#FFFFFF", // Modal / popover surface
  surfaceBorder:    "#E6E0D7", // Warm hairline border

  // Typography
  textPrimary:      "#222630", // Dark Ink
  textSecondary:    "#6A716F", // Muted editorial secondary
  textTertiary:     "#8B918F", // Metadata & captions
  textInverse:      "#FFFFFF", // White on orange/dark

  // Supporting Editorial Accents
  sageAccent:       "#95A686", // Calm botanical green
  sageWash:         "#E8EFE2", // Sage pill background
  peachAccent:      "#F5DDD1", // Warm peach glow
  peachWash:        "#FFF2EB", // Soft peach tint
};
```

### 2.2 Historical Explorations `[ARCHIVED]`
- Indigo / Violet palette (`#6366f1` / `#9333ea`) explored in early prototypes is archived as superseded by Warm Carrot Orange.

---

## 3. Typography & Georgian-First Rules

### 3.1 Mkhedruli Script Mechanics `[APPROVED]`
- **No Native Upper/Lower Case:** Standard Mkhedruli does not have uppercase/lowercase pairs. Visual hierarchy must rely on font weight (700/800 Bold) rather than uppercase transformations.
- **Vertical Line-Height (1.55+):** Mkhedruli letterforms (დ, ტ, ფ, ქ, ყ, შ, ჩ, ც, ძ, წ, ჭ, ხ, ჯ, ჰ) have pronounced ascenders, descenders, and rounded loop bowls. Standard English line-height (1.2–1.3) causes colliding lines. Minimum line-height is strictly **1.55**.
- **Horizontal Expansion:** Georgian words are 20% to 35% longer than English. Buttons and navigation tabs must provide generous horizontal padding to prevent wrapping or truncation.

### 3.2 Font Family Candidates `[PROPOSAL]`
- **Primary Headings & Body:** FiraGO (Clean, modern, highly legible Georgian open-source typeface with extensive weights).
- **Secondary / System Fallbacks:** Noto Sans Georgian, Sylfaen.

### 3.3 Proposed Type Scale `[PROPOSAL]`

| Token | Size | Line Height | Weight | Proposed Usage |
| :--- | :--- | :--- | :--- | :--- |
| `Display 3xl` | 32px | 48px (1.50) | Heavy (800) | Onboarding welcome, editorial punchlines |
| `Heading 2xl` | 24px | 36px (1.50) | Bold (700) | Screen titles (Discover, Why, Me) |
| `Title xl` | 20px | 30px (1.50) | Semibold (600) | Display names, Card headers |
| `Subhead lg` | 18px | 28px (1.55) | Medium (500) | Section labels, Sub-headers |
| `Body Base` | 16px | 26px (1.62) | Normal (400) | Primary conversational copy, prompt answers, WHY text |
| `Caption sm` | 14px | 22px (1.57) | Normal (400) | Secondary metadata, city/occupation labels |
| `Micro xs` | 12px | 18px (1.50) | Semibold (600) | Category pills, status indicators, badges |

---

## 4. Layout & Navigation Concepts

### 4.1 Touch-Native Discovery Deck & Curated Browsing `[APPROVED]`
*(Governed by [FDR-2026-01](FOUNDER_DECISION_RECORDS.md#fdr-2026-01-photo-first-human-discovery-touch-native-swipe-interaction-policy) and [FDR-2026-02](FOUNDER_DECISION_RECORDS.md#fdr-2026-02-photo-framing-geometric-hierarchy))*

- **Mobile Touch-Native Candidate Deck (`DiscoverSwipeCard.tsx`):**
  - **Swipe Left (or ArrowLeft / Next button):** Advances locally to the next candidate (skip/pass) without writing negative rejection telemetry to the database.
  - **Swipe Right (or ArrowRight / Connect button):** Opens a focused confirmation modal/drawer to send a connection invitation.
  - **Intentional Bilateral Consent:** A right-swipe never triggers an immediate single-flick match; connection requires explicit button confirmation. Escape or "Not Now" cancels without dispatching network requests.
- **Decoupled Gesture Hierarchy:**
  - *Candidate navigation:* Horizontal swipe ($>65\text{px}$) or keyboard arrows navigate candidate cards.
  - *Photo navigation:* Horizontal tapping or scrubbing within candidate cards cycles through photos (`photos[]`) without moving the candidate card.
  - *Detail exploration:* Vertical scrolling sweeps down into deep candidate profile details (prompts, lifestyle cadence, shared interests, and WHY relational chemistry).
- **Desktop Layout:** Presents a centered photo card with rich social context, filters, and an alternate browsable list view to conserve bandwidth.
- **Photo Geometry & Framing Hierarchy:**
  - Large candidate and lifestyle photos must use natural proportions with restrained modern rounded corners (`rounded-2xl` to `rounded-3xl` / 20–24px). Exaggerated arch masks are prohibited on full-bleed mobile candidate cards.
  - Distinctive arch framing and circular cameo apertures are reserved for small avatars, profile thumbnails, and shared-interest seals.

### 4.2 Ergonomic Thumb-Zone Architecture `[PROPOSAL]`

```text
┌──────────────────────────────────────┐
│  TOP BAR: Brand, Notifications       │ ← HARD TO REACH (Status only)
├──────────────────────────────────────┤
│                                      │
│  CONTENT VIEWPORT:                   │
│  • High-Density Discovery Cards      │ ← NATURAL READING ZONE
│  • Prompt Voice Modules              │
│  • Visual Imagery                    │
│                                      │
├──────────────────────────────────────┤
│  INTERACTION HOT-ZONE:               │
│  • "Why Us?" Floating Pill Button    │ ← NATURAL THUMB REACH ZONE
│  • Contextual Filter Strip           │   (Primary actions here)
│  • 1-Tap Connect Drawer Trigger      │
├──────────────────────────────────────┤
│  BOTTOM NAV: Home · Discover · Chat · Me │ ← PRIMARY NAVIGATION
└──────────────────────────────────────┘
```

### 4.3 The "Motley" Modular Patchwork `[EXPLORATION]`
- **Concept:** Translating the historical Jester's patchwork garment into an asymmetric, modular mosaic layout.
- **Application:** Profile cards featuring tiles of varying proportions (prompts, values, cadence, interests) rather than an endless column of uniform rectangles.

### 4.4 The 2x2 Relational Compass Grid `[PROPOSAL]`
- Modular 2x2 profile grid displaying:
  1. Core Value Anchor (e.g. *"Truth Over Harmony"*)
  2. Social Rhythm (e.g. *"Recharge Solo • Small Crews"*)
  3. Communication Style (e.g. *"Direct Banter • Unhurried"*)
  4. Lifestyle Cadence (e.g. *"Night Owl • Active Pace"*)

### 4.5 The WHY Half-Sheet Drawer `[PROPOSAL]`
- Tapping "Why Us?" on a candidate profile sweeps up an 85% viewport height bottom half-sheet.
- Allows users to inspect comparative chemistry, shared interests, and conversation starters without navigating away from their discovery position.

---

## 5. Component Specifications & Micro-Interactions

### 5.1 Touch Targets & Buttons `[PROPOSAL]`
- Minimum touch height: **48px** for primary mobile actions.
- Tactile feedback: Subtle scale compression (`scale(0.98)`) on press with light haptic feedback.

### 5.2 Elevation & Shadow Philosophy `[PROPOSAL]`
- Avoid heavy, muddy black shadows.
- Multi-layered soft ambient light:  
  `box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 8px 24px -4px rgba(15, 23, 42, 0.08);`
- Active card hover/press: Subtle indigo border light shift (`#c7d2fe`) rather than simply increasing drop shadow.

### 5.3 Radii Rhythm `[PROPOSAL]`
- `xs (4px)` / `sm (8px)`: Inline badges, status dots.
- `md (12px)`: Inputs, secondary buttons, avatar chips.
- `lg (16px)`: Interactive cards, bottom navigation bar.
- `xl (24px)`: Modal surfaces, onboarding containers.
- `full (9999px)`: Pill buttons, score badges.

---

## 6. Open UI/UX Decisions (Requiring Formal Design Validation)

The following decisions remain **open** and require formal design exploration, wireframing, and user testing:

1. **Compatibility Score Representation in Discovery Cards:**  
   - *Option A:* Prominent numeric badge (e.g., `84 / 100`) on the card header.  
   - *Option B:* Ambient color pill or spark icon without numbers; full score revealed only upon opening WHY.  
   - *Option C:* Qualitative resonance tier label (e.g., *"მაღალი ქიმია"* / *"მძლავრი სინერგია"*) instead of raw numbers.
2. **Card Density in Feed:**  
   - *Option A:* Single full-height viewport card per person (TikTok / Hinge vertical scroll pattern).  
   - *Option B:* Continuous editorial stream where cards can be scanned in partial view.
3. **WHY Breakdown Visualization:**  
   - *Option A:* 4 Category progress bars / meters (Communication, Emotional, Intellectual, Chemistry).  
   - *Option B:* Editorial text callouts with highlighted spark chips and zero progress bars.  
   - *Option C:* Polar coordinate radar/spider chart.
4. **Dark Mode Strategy:**  
   - *Option A:* System-default automatic switching (Alabaster Light / Midnight Dark).  
   - *Option B:* Dark-mode first by default (Obsidian Slate across all surfaces).
5. **Photo Framing & Aspect Ratio:**  
   - *Option A:* Standard 4:5 vertical portrait framing.  
   - *Option B:* 1:1 square editorial framing with generous surrounding text modules.  
   *(Resolved by [FDR-2026-02](FOUNDER_DECISION_RECORDS.md#fdr-2026-02-photo-framing-geometric-hierarchy): Large photographs use natural 4:5 or 3:4 portrait proportions with restrained modern rounded corners `rounded-2xl` to `rounded-3xl`; small avatars and cameo badges may use arch apertures).*

---

## 7. Visual Studio Exploration Synthesis & Directions `[APPROVED DIRECTION]`
*(Governed by [FDR-2026-03](FOUNDER_DECISION_RECORDS.md#fdr-2026-03-visual-exploration-synthesis-kzzuf-architecture-phkqc-stage))*

Following the comprehensive multi-agent exploration in Visual Studio (`design/visual-studio/canvas/JESTER - Visual Exploration 02.pen`), the Founder has approved the synthesis direction for future UI iterations:

1. **Foundational Visual Architecture: `KZzuf` (Warm Paper Salon / Personal Court):**  
   - Grounded in warm editorial paper tones (`#FAF7F2`), subtle warm hairline borders (`#E6E0D7`), and restrained Carrot Orange (`#FF7A2F`) accents.
   - Provides calm, culturally mature breathing room with high typographic authority in Noto Sans Georgian.
2. **Opening Hero Stage: `phkQC` (Theatrical Spotlight Stage with Truth-Flip & 4-Facet ME Lens):**  
   - Combines a theatrical personal spotlight with an interactive "Truth-Flip" daily hook card and structured 4-facet ME lenses (Identity, Voice, Spark, Rhythm).
3. **Screen Boundary Invariant:**  
   - **Authenticated Home (`/`):** Remains a curated editorial overview with zero binary discard mechanics.
   - **Social Discovery (`/discover`):** Employs the bounded mobile swipe deck with decoupled photo scrubbing and explicit right-swipe confirmation modal.
