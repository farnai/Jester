# GEMINI / ANTIGRAVITY — JESTER DESIGN SYSTEM V1 IMPLEMENTATION

## Role
Act as a Senior Product UI Architect, Design Systems Engineer, and React/TypeScript Frontend Engineer.

## Target and source
Target repository: the EXISTING Jester application ONLY (not JesterAICompany).
Founder-approved visual direction: light, airy mobile UI with vivid clean CARROT ORANGE as the sole primary brand/active accent, warm pale surfaces, deep charcoal text, measured sage supportive touches, and soft peach insight backgrounds. The selected first UI mockup is visual direction, NOT a binding screen-layout implementation or product-behavior specification.

IMPORTANT: Before editing, read the attached `JESTER_COLOR_DESIGN_SYSTEM_V1.md` and `jester.tokens.json` entirely, and inspect `JESTER_SELECTED_UI_MOCKUP_REFERENCE.png` as the selected visual reference; the reference CSS is illustrative. Verify actual project documentation and current frontend code before mapping any token. The supplied HEX values are v1 implementation choices from the selected concept, not pixel-perfect samples of the image. The token JSON is a reference mapping, not a drop-in W3C DTCG import file.

## Phase 0 — Brief, real source audit and safety checks
1. Inspect actual Jester root, Git status/HEAD, dirty files, existing Founder proposals, and affected file overlap.
2. Read `docs/JESTER_PRODUCT_FOUNDATION.md`, `docs/JESTER_DESIGN_EXPLORATION.md`, `docs/JESTER_STRATEGIC_MARKETING_FOUNDATION.md` where present and verify their authority. Also inspect any other approved design docs, component inventories and tokens.
3. Discover the real frontend styling approach, theme/token sources, references to Indigo/Blue or hard-coded HEX, component architecture and existing tests. DO NOT assume arbitrary paths.
4. Inventory screens: Home, Discover, Person/Why, Profile, Compare, Conversation Starters, Messages, Registration, Onboarding. Preserve product rules and current application behavior.
5. Report hard conflicts and dangerous overlaps. Do not overwrite previous pending proposals or dirty files. If a safe isolated worktree or feature branch is feasible using existing setup, prefer it.
6. This is JESTER-only brand/UI work. Do not inject orange into generic JesterAICompany roles/prompts/engine.

## Phase 1 — Design token architecture
1. Map the supplied primitive and semantic color tokens to the actual project token naming. Reuse existing approved infrastructure; no new styling framework.
2. Implement primary `#FF7A2F`, hover `#E9681F`, background `#FAF7F2`, card `#FFFFFF`, primary text `#222630`, secondary `#6A716F`, sage support, soft peach, soft borders; maintain one main orange brand accent.
3. Preserve all other required semantic states (success/warning/error/info) as meaning-oriented, not promotional brand colors.
4. Do not globally repaint unrelated areas until dependencies are known. Provide before/after token mapping and deprecated names plan.
5. If the project's current values are approved but conflict with the selected Founder visual direction, surface the conflict; do not silently pretend all documentation agrees.

## Phase 2 — Shared components and representative screens
Update shared presentation tokens and components (buttons, inputs, tabs, chips, cards, navigation, insights, compare progress bars, and alerts) to consume semantic aliases.

Crucial accessibility correction: White normal-size text on `#FF7A2F` is approximately 2.60:1 and fails WCAG AA. Use dark `#222630` button label on the bright carrot orange (approximately 5.82:1). Only use WHITE label when the button background is a separately named dark-orange variant `#9E4215` (approximately 6.47:1). Include focus-visible, 44px touch targets where practical, disabled/error/loading styles, and verified text contrast. Do not simply recreate inaccessible mockup details.

Show coherent changes on a small set of representative real screens: Home, Discover, Person/Why, Compare, Registration (mobile + desktop wherever available). Avoid a massive blind global redesign. Keep scoped styling and reusability. If the whole product cannot be migrated safely in one task, deliver the shared token system and a well-tested first screen batch with a transparent migration plan for remaining screens; do NOT mark total migration as complete.

## Non-negotiable product boundaries
- Jester = People Discovery & Relationship Intelligence. NOT a dating clone, horoscope frontend, swipe app or generic AI dashboard.
- ME → YOU → US → MORE PEOPLE; explanation and human insight are more important than naked compatibility scores.
- Preserve existing auth/email verification/Supabase integration, onboarding, API calls, privacy gating, connection states, navigation, and data persistence.
- No backend or database modifications. No new social login integrations. No placeholder scores or fake functionality.
- No new marketing claims based on unverified user behavior, and no English copy leakage into Georgian user-facing text.
- Do not automatically replace or redraw the three-point JESTER hat logo; logo application has its own Founder signoff.
- No unrelated refactors, external dependencies, commits, pushes or deployments.

## Verification and review
- Run relevant TypeScript/build and existing unit/integration tests.
- Add targeted tests only when needed for new token/component regressions.
- Verify responsive and accessible states; use actual browser screenshots if available (before/after on mobile + desktop). NEVER substitute conceptual AI images for live render verification.
- Audit contrast especially orange buttons, disabled states, small gray text, border visibility, text on photos, and comparison charts.
- Provide file-by-file diff, token mapping, before/after screenshots, exact commands/exit codes, known gaps and remaining screens.
- If blocked by pre-existing dirty files, incompatible proposals, missing approved docs, or a product behavior change, report HOLD and ask for a focused Founder decision. Do not claim success from compilation alone.

## Founder delivery — Georgian
Report:
1. Git baseline and safeguards
2. Docs inspected (real paths and sections)
3. Existing token architecture and mapping
4. Files changed and scope
5. New palette and semantic token setup
6. Which shared components / screens migrated
7. Contrast findings and fixes
8. Build/test results
9. True UI screenshots and visual findings, if available
10. Regression risks and untouched behavior
11. Remaining migration steps
12. Verdict: READY_FOR_FOUNDER_REVIEW / PARTIAL / HOLD

Only make changes in an authorized isolated implementation scope. Stop before applying to canonical if using an approval-gated CompanyRun/worktree workflow; do not bypass Founder review.
