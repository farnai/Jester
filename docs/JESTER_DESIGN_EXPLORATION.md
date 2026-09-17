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

### 1.1 Aesthetic Direction: "Editorial Digital Luxury" `[PROPOSAL]`
- **Concept:** A visual synthesis combining high-end editorial print magazines (*Kinfolk*, *Apartamento*), modern typography-led digital tools (Linear, Raycast), and warm, tactile consumer products (Cash App, Arc Browser).
- **Feeling:** Structured, mature, razor-sharp, and culturally self-assured. It rejects both sterile enterprise SaaS sterility and juvenile, gamified swipe-app aesthetics.
- **Visual References:**
  - *Linear / Raycast:* Geometric discipline, crisp micro-borders, clean typography, intentional key-lines.
  - *Kinfolk / Apartamento:* Editorial whitespace, generous margins, human photography framing.
  - *Cash App:* Bold, tactile, punchy interactive buttons, micro-interactions with weight and presence.

### 1.2 Rejected Visual Directions `[REJECTED]`
- ❌ **Medieval Fantasy / Renaissance Kitsch:** No parchment textures, gothic calligraphy, heraldic shields, or royal crowns.
- ❌ **Circus Clowns & Carnivals:** No floppy three-pronged hats, bells, oversized shoes, or harlequin diamonds.
- ❌ **Cartoon Mascots:** JESTER is an invisible editorial presence, not a bouncing mascot (no Clippy, no Duolingo owl).
- ❌ **Cosmic Occult Temple:** No mystical crystal balls, velvet gradients, zodiac wheels, or planetary degree symbols ($\degree$) in consumer flows.

---

## 2. Color Exploration

### 2.1 Baseline Token Palette `[PROPOSAL]`
*(Currently reflected in prototype token files `frontend/src/ui/tokens/colors.ts`)*

```typescript
export const colors = {
  // Foundations & Surfaces
  background:     "#f8fafc", // Cool alabaster slate
  surface:        "#ffffff", // Pure crisp white
  surfaceSubtle:  "#f1f5f9", // Gentle container grey
  surfaceMuted:   "#e2e8f0", // Divider & boundary tone
  surfaceInverse: "#0f172a", // Deep midnight obsidian

  // Typography Tones
  textPrimary:    "#0f172a", // Maximum contrast slate-black
  textSecondary:  "#64748b", // Neutral editorial slate
  textMuted:      "#94a3b8", // Quiet metadata grey
  textInverse:    "#ffffff", // High-contrast text on dark surfaces

  // Primary Accent (Electric Royal Indigo)
  accent:         "#6366f1", // Main CTAs, active indicators
  accentHover:    "#4f46e5", // Hover & press states
  accentSubtle:   "#eef2ff", // Tinted badges & pill backgrounds
  accentBorder:   "#c7d2fe", // Accent boundaries

  // Signature Brand Highlight (JESTER Royal Violet)
  highlight:      "#9333ea", // Signature hooks, WHY highlights
  highlightSubtle:"#fdf4ff", // Ambient card glow, preview tint
  highlightBorder:"#f0abfc", // High-resonance borders

  // Semantic Feedback
  success:        "#16a34a", // Verification checks, accepted states
  warning:        "#d97706", // Pending states, friction callouts
  danger:         "#dc2626", // Disconnect, block, destructive action
  info:           "#2563eb", // Contextual hints
};
```

### 2.2 Warm Terracotta & Monochromatic Alternatives `[EXPLORATION]`
- **Terracotta & Warm Paper Exploration:** Testing warm off-whites (`#faf8f5`), rich charcoal (`#1c1917`), and warm terracotta (`#c2410c`) to create an earthy, tactile book-like warmth for Georgian literary feel.
- **Monochrome Minimalist Exploration:** Pure black/white with a single stark amber or cobalt focal accent.

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

### 4.1 Anti-Swipe Vertical Discovery Feed `[APPROVED]`
- Swiping right/left to discard or like is strictly prohibited.
- Discovery is rendered as an intentional vertical stream of rich candidate cards.

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
