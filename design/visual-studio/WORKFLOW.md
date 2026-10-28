# JESTER Visual Design Workflow

> **Status:** Canonical Operational Workflow for Visual Exploration & Design  
> **Target:** JESTER Platform (`farnai/Jester`)  
> **Tooling:** Antigravity, pen.dev Desktop, `pencil` MCP server  

---

## The End-to-End Visual Design Lifecycle

To guarantee visual originality, typographic excellence, and strict brand fidelity, all visual design work must proceed through nine structured stages:

```text
Founder Task
    ↓
Verified Project Context (PROJECT_BRIEF.md)
    ↓
AI Art Director (Art Direction & 3 Hypotheses)
    ↓
AI UI Designer (High-Fidelity Canvas Frames)
    ↓
AI Graphic Designer (Brand Motifs & SVG Assets)
    ↓
Independent Visual Critic (Evidence-Based QA & Defect List)
    ↓
Visual Revision (Targeted Fixes & Polishing)
    ↓
Founder Review (Selection & Strategic Approval)
    ↓
Approved Implementation (Production Engineering on Dedicated Branch)
```

---

## Detailed Stage Protocols

### Stage 0 — Preflight & Context Verification
- **Actor:** Lead Agent / Coordinator
- **Input:** Founder prompt or design ticket.
- **Protocol:**
  1. Verify repository identity (`farnai/Jester`), clean git state, and target branch.
  2. Inspect `design/visual-studio/CONTEXT_INDEX.md` and refresh if source documents changed.
  3. Load verified facts from `design/visual-studio/PROJECT_BRIEF.md`.
  4. Verify pen.dev desktop is active and `pencil` MCP server is responding via `get_app_state`.
- **Output:** Validated task scope, target screen specification, and confirmed canvas connectivity.

### Stage 1 — Art Direction (AI Art Director)
- **Actor:** `jester-art-director`
- **Input:** `PROJECT_BRIEF.md`, target screen spec (e.g. `docs/HOME_EXPERIENCE.md`), current screen code.
- **Protocol:**
  1. Determine the emotional tone, user situation, and psychological impression of the screen.
  2. Define non-negotiables (brand tokens, Georgian line-height, 18+ gate) vs creative freedoms (spatial rhythm, asymmetry, composition).
  3. Formulate three distinct visual directions/hypotheses:
     - **Direction A — Social Editorial:** Magazine-style narrative hierarchy, large expressive serif/bold typography, ample negative space, rich personal voice.
     - **Direction B — Connection Atlas:** Spatial relationship mapping, asymmetric modular tiles, dynamic chemistry cards, tactile interactive surfaces.
     - **Direction C — Playful Intelligence:** Witty conversational focal points, vibrant Carrot Orange accents, quote-forward cards, and brisk social scanning.
  4. Detail specific design rationale, layout hierarchy, and risk analysis for each concept.
- **Deliverable:** Concept specifications documented in `design/visual-studio/experiments/<screen-id>/EXPERIMENT.md`.

### Stage 2 — High-Fidelity UI Design (AI UI Designer)
- **Actor:** `jester-ui-designer`
- **Input:** Art Director concepts, verified tokens (`colors.ts`, `typography.ts`), canvas `.pen` document.
- **Protocol:**
  1. Connect to `design/visual-studio/canvas/<screen-id>.pen` via `pencil` MCP.
  2. Implement actual editable frames for each concept using `execute` tool (`Insert`, `Update`, `SetVariables`).
  3. Apply authentic Georgian typography: minimum line-height 1.55, bold weight hierarchy, generous horizontal padding for Georgian word length.
  4. Create both Desktop (1440px / 1280px) and Mobile (390px) variants for each concept.
  5. Populate realistic, privacy-safe synthetic Georgian content reflecting actual API DTOs.
- **Deliverable:** Live, editable design frames saved in `.pen` canvas document.

### Stage 3 — Brand Motifs & Graphic Language (AI Graphic Designer)
- **Actor:** `jester-graphic-designer`
- **Input:** Canvas frames, brand assets, Art Director brief.
- **Protocol:**
  1. Develop 2–3 bespoke graphic motifs (conversational spark line-work, relational resonance apertures, insight quotes).
  2. Embed motifs directly into the canvas frames as scalable vector geometry.
  3. Enforce strict restrictions: NO purple occult crystal balls, NO carnival clown kitsch, NO medieval parchment heraldry, NO cartoon mascots.
- **Deliverable:** Integrated vector motifs and asset guidelines recorded in the experiment log.

### Stage 4 — Independent Visual Critique (AI Visual Critic)
- **Actor:** `jester-visual-critic`
- **Input:** Rendered canvas frames, export screenshots, `PROJECT_BRIEF.md`.
- **Protocol:**
  1. Inspect actual visual output across 6 criteria:
     - *Brand distinctiveness:* Warm Modern Editorial vs SaaS/dating tropes.
     - *Visual hierarchy & eye-flow:* Immediate primary focal point.
     - *Georgian typography craftsmanship:* Line-height >= 1.55, no clipping of ascenders/descenders, clean word-wrapping.
     - *Graphic craftsmanship:* Spacing rhythm, alignment, contrast ratios.
     - *Responsive adaptability:* 48px touch targets, mobile thumb-zone layout.
     - *Reusability:* Generalizability to Discover, Profile, Why screens.
  2. Enforce zero rubber-stamping: generate concrete defect list with frame IDs, observed issue, severity, and actionable fix.
- **Deliverable:** Comprehensive critique report in `design/visual-studio/experiments/<screen-id>/REVIEW.md`.

### Stage 5 — Visual Revision & Refinement
- **Actors:** `jester-ui-designer` + `jester-graphic-designer`
- **Input:** Visual Critic defect report.
- **Protocol:**
  1. Apply targeted modifications to the canvas frames addressing all BLOCKER and HIGH severity defects.
  2. Verify that line-heights, contrast ratios, and spacing adjustments meet standards.
  3. Re-run quick verification pass.
- **Deliverable:** Updated `.pen` canvas frames with revision changelog.

### Stage 6 — Founder Review & Direction Selection
- **Actor:** Human Founder / Product Owner
- **Input:** 3 polished concepts with visual evidence, trade-offs, and critic review.
- **Protocol:**
  1. Present the three distinct directions with key trade-offs and open questions.
  2. Founder selects the preferred concept or requests specific synthesis.
  3. **Gate:** NO implementation work proceeds without explicit Founder approval.
- **Deliverable:** Founder-approved design concept recorded in experiment log.

### Stage 7 — Production Implementation
- **Actor:** Engineering Agent (Codex / Antigravity)
- **Input:** Approved `.pen` design frames, existing React components, token architecture.
- **Protocol:**
  1. Create dedicated feature branch (e.g. `feat/redesign-<screen-id>`).
  2. Implement approved design faithfully using existing React, CSS modules, and design token imports.
  3. Run automated test suites and visual regression checks across desktop and mobile viewports.
  4. Open PR for final engineering review.
- **Deliverable:** Working, tested frontend code matching approved design without regressions.
