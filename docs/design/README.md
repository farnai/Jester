# JESTER Brand Identity & Design System Assets

This directory contains the Founder-selected **JESTER Color & Design System v1** documentation, token references, UI mockups, and brand identity context.

## 1. Brand Identity Assets
- **`jester_brand_identity_board.png`**: Canonical approved brand identity board showing:
  - Three-point Jester Hat Symbol with golden bells (Curiosity, Understanding, Empathy)
  - Logo palette: Terracotta (`#C7614B`), Dusty Rose (`#D9A69A`), Cream (`#F8EFE6`), Deep Espresso (`#3A2A22`), Muted Copper (`#C8966B`)
  - Horizontal lockup, app icon, and monochrome lockups
- **Vector assets in `frontend/src/assets/brand/`**:
  - `JESTER_Logo_Stacked.eps`
  - `JESTER_Hat_Icon.eps`
  - `JESTER_Logo_Stacked_Outlined.svg`
  - `jester_brand_identity_board.png`

## 2. Design System Documentation & Tokens (v1)
- **`JESTER_COLOR_DESIGN_SYSTEM_V1.md`**: Detailed design system documentation, token philosophy, surface hierarchy, and accessibility rules.
- **`JESTER_Color_Design_System_v1.docx`**: Word documentation format of the approved design system.
- **`jester.tokens.json`**: Design token definitions and semantic aliases (Carrot Orange `#FF7A2F`, Warm paper surfaces `#FAF7F2`, `#FFFFFF`, `#F3EEE6`, Supportive Sage `#788A69`, Peach insight `#FBEEE7`).
- **`jester.reference-tokens.css`**: CSS variables reference handoff.
- **`GEMINI_IMPLEMENTATION_PROMPT.md`**: Implementation brief; verify each capability against current source.
- **`JESTER_SELECTED_UI_MOCKUP_REFERENCE.png`**: Founder-selected visual reference (Home, Discover, Why this person, Profile, Compare, Conversation Starters); selection does not establish final approval of rendered application implementations.

## 3. Active Implementation in Repository
- `frontend/src/ui/tokens/colors.ts`: Active TypeScript token matrix.
- `frontend/tailwind.config.js`: Active Tailwind color scales and classes.
- `frontend/src/index.css`: Active `:root` CSS variables and base component styles.
- `frontend/src/shared/ui/`: Active shared DOM components.
- `frontend/src/ui/primitives/`: Active universal cross-platform primitives.
