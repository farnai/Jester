# Home Visual Experiment 01 — JESTER Home Screen Explorations

- **Status:** COMPLETED (Canvas generated & verified)
- **Date:** 2026-10-20
- **Target Surface:** JESTER Home (`/` or `/home`)
- **Canvas Location:** `design/visual-studio/canvas/jester-home-explorations.pen`
- **Tooling:** pen.dev Desktop via native `pencil` MCP server (`execute` API)

---

## 1. Verified Source Brief & Context

Grounded directly in verified project sources:
- `docs/JESTER_PRODUCT_FOUNDATION.md`: Core loop `ME → YOU → US → MORE PEOPLE`. Axiom: *Score creates curiosity. Interpretation creates value.*
- `docs/JESTER_STRATEGIC_MARKETING_FOUNDATION.md`: Social discovery & relationship intelligence engine; anti-astrology-cliché; warmth & editorial wit.
- `docs/HOME_EXPERIENCE.md`: Daily energy card, active connections with unread counters, relationship starters, discovery entry points.
- `docs/JESTER_DESIGN_EXPLORATION.md` & `frontend/src/ui/tokens/colors.ts`:
  - Canvas: `#FAF7F2` (warm stone/paper)
  - Cards: `#FFFFFF` and `#F3EEE6`
  - Accent: `#FF7A2F` (Warm Carrot Orange)
  - Charcoal: `#222630` (WCAG compliant contrast text)
  - Secondary accents: Sage `#788A69` / `#E8EFE2`, Peach `#F5DDD1` / `#FBEEE7`, Lavender `#5A5480` / `#EDEBF4`
- Georgian Typography: `Noto Sans Georgian` / `FiraGO`, line-height $\ge 1.55$, bold weight contrast (700/800) for headings because Georgian Mkhedruli has no capital letters.

---

## 2. Three Distinct Visual Concepts

### Concept A: Social Editorial (The Intellectual / Narrative Daily)
- **Design Hypothesis:** JESTER as a bespoke relationship journal. High editorial craftsmanship, refined white card structures floating on warm `#FAF7F2` canvas, confident typographic hierarchy, and restrained decorative borders.
- **Key Composition Elements:**
  - Hero relationship card: "დღის ენერგია" (Daily Energy) with editorial insight: *"კომუნიკაციის ველი მშვიდია, თუმცა დეტალებზე დაკვირვება გაგიმარტივებთ გაუგებრობების თავიდან არიდებას."*
  - Active Connections shelf: "კავშირები" with status indicators and authentic Georgian names (ანა, გიორგი, ნინო, დავითი).
  - Conversation Starters card: "სასაუბრო თემა — რა გაძლევს ენერგიას დამღლელი კვირის შემდეგ?" with quick-action prompts.
  - Primary button: `#FF7A2F` background with `#222630` charcoal text (strictly adhering to WCAG 5.82:1 AA contrast rules).
- **Target Sentiment:** Thoughtful, adult, culturally grounded, calm curiosity.

### Concept B: Connection Atlas (The Relational Matrix & Dynamics)
- **Design Hypothesis:** JESTER as an interactive relationship radar and dynamic compatibility atlas. Visually emphasizes synastry dimensions (intellectual, emotional, communicative) and social graph proximity.
- **Key Composition Elements:**
  - Dynamic Atlas Hero: "შენი კავშირების ატლასი" showing interconnected active ties with compatibility score tags (`87% ინტელექტუალური ჰარმონია`, `92% ემოციური თანხვედრა`).
  - Synastry Category Breakdown: Pill tags for "კომუნიკაცია", "დინამიკა", and "ღირებულებები".
  - Quick Radar Grid: Direct invitation into "სიღრმისეული შედარება (Compare & Why)".
  - Card surfaces: Subtle `#F3EEE6` tinted surfaces with crisp `#222630` text hierarchy and `#788A69` sage badges.
- **Target Sentiment:** Analytical, visually structured, relationship-intelligent, curiosity-inducing.

### Concept C: Playful Intelligence (The Vibrant Social Discovery Engine)
- **Design Hypothesis:** JESTER as a witty, accessible social playground where score sparks immediate curiosity and invites deeper conversation.
- **Key Composition Elements:**
  - Vibrant Warm Orange Header Badge: "ჯესტერი — ურთიერთობების ინტელექტი".
  - Interactive Curiosity Hook: "რას ფიქრობს შენი წრე? აღმოაჩინე ახალი ადამიანები და გაიგე, როგორ ერგებით ერთმანეთს."
  - Discover Prompt Card: "ახალი ადამიანები (Discover)" with 3 prospective profile cards showing compatibility badges and direct curiosity prompts.
  - Action button: High-energy CTA "დაიწყე დიალოგი ↗" with high-contrast charcoal typography.
- **Target Sentiment:** Engaging, social, spontaneous, lively yet mathematically grounded.

---

## 3. Real Canvas Frames Produced in pen.dev

All 6 frames were generated and verified directly in `design/visual-studio/canvas/jester-home-explorations.pen`:

| # | Frame Name | Viewport Dimensions | Canvas Coordinates | Layout Mode |
|---|---|---|---|---|
| 1 | `Concept A: Social Editorial (Desktop 1440)` | 1440 × 1040 | x: 0, y: 0 | Flexbox Vertical, gap: 32, pad: [32, 60, 40, 60] |
| 2 | `Concept A: Social Editorial (Mobile 390)` | 390 × 920 | x: 1540, y: 0 | Flexbox Vertical, gap: 20, pad: [24, 20, 24, 20] |
| 3 | `Concept B: Connection Atlas (Desktop 1440)` | 1440 × 1080 | x: 0, y: 1140 | Flexbox Vertical, gap: 32, pad: [32, 60, 40, 60] |
| 4 | `Concept B: Connection Atlas (Mobile 390)` | 390 × 920 | x: 1540, y: 1140 | Flexbox Vertical, gap: 20, pad: [24, 20, 24, 20] |
| 5 | `Concept C: Playful Intelligence (Desktop 1440)` | 1440 × 1060 | x: 0, y: 2320 | Flexbox Vertical, gap: 32, pad: [32, 60, 40, 60] |
| 6 | `Concept C: Playful Intelligence (Mobile 390)` | 390 × 920 | x: 1540, y: 2320 | Flexbox Vertical, gap: 20, pad: [24, 20, 24, 20] |

---

## 4. Design Decisions & Constraint Compliance

1. **Brand Token Adherence:**
   - Backgrounds exclusively use Warm Canvas (`#FAF7F2`) and clean container cards (`#FFFFFF`, `#F3EEE6`).
   - Primary accents use Warm Carrot Orange (`#FF7A2F`).
   - No generic purple/neon gradients or crypto/dark-mode AI SaaS tropes.
2. **WCAG Accessibility Invariant:**
   - White text on `#FF7A2F` fails WCAG AA (contrast ratio 2.88:1) and is strictly forbidden.
   - All orange buttons and badges use `#222630` charcoal text (contrast ratio 5.82:1, passing WCAG AA & AAA large).
3. **Georgian Typography:**
   - Rendered using Google Font `Noto Sans Georgian`.
   - Line-height enforced $\ge 1.55$ to avoid vertical clipping of Mkhedruli ascenders/descenders.
   - Hierarchy achieved through bold weight scaling (font-weight 800 for titles, 700 for subtitles, 400/500 for body) rather than uppercase capitalization.
4. **Privacy & Content Safety:**
   - All displayed user cards use synthetic demo profiles (ანა, გიორგი, ნინო, დავითი).
   - No private birth data (time, date, place, lat/long) or raw planetary degrees are exposed on home cards.
   - Only safe relational interpretations and aggregated synastry scores are presented.

---

## 5. Review & Founder Evaluation

Next step: See `design/visual-studio/experiments/home-01/REVIEW.md` for the independent visual critique and recommended refinement iterations.
