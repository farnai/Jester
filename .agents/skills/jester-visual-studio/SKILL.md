---
name: jester-visual-studio
description: Design Jester screens with repository-grounded brand/product context and pen.dev visual canvas. Activate for UI redesign, visual design, art direction, graphic assets, design exploration, pen.dev canvas work, and visual evaluation before application implementation.
---

# Jester Visual Studio

This is for **the JESTER social discovery / relationship intelligence application**, NOT JesterAICompany and not a generic dating or horoscope template. Product truth comes ONLY from documents and code checked in the current repository. Do not invent features, palette values, audiences, charts or imagery rights.

## Start with verified context
1. Inspect current git state; do not rewrite existing changes.
2. Read root `AGENTS.md` / `GEMINI.md` if present. Follow their rules.
3. Run `python design/visual-studio/scripts/build_context_index.py` in the repository root if the index is absent or stale.
4. Read `design/visual-studio/CONTEXT_INDEX.md` and open the real documents: product foundation, marketing positioning, design system/tokens, Georgian fonts, existing component library, design explorations, relevant page code, and visual assets. Do not just skim the index.
5. Prepare/update `design/visual-studio/PROJECT_BRIEF.md` with verified constraints and repo-relative source paths, plus explicit unknowns/conflicts. Never silently replace project brand rules with your preferences.
6. Read `design/visual-studio/roles/` and `design/visual-studio/WORKFLOW.md`.

## Roles and handoffs
- **Art Director**: visual thesis, visual-world rationale, 3 meaningfully distinct explorations.
- **UI Designer**: detailed layout, typography, spacing, imagery, reusable components, mobile states; must edit an actual `.pen` design.
- **Graphic Designer**: Jester-specific reusable art direction/motifs; avoid random unrelated graphics.
- **Visual Critic**: inspect actual render/screenshot, provide concrete defects and strengths, request focused revisions.

## pen.dev MCP
- Ensure pen.dev desktop is running and the desired `.pen` document is open.
- Check the `pencil` MCP server. Call the available `get_app_state` to verify the **active path** before edits; read pen's `read_skill()` guidance where available.
- Modify the live canvas through available documented MCP tools, not by pretending a Markdown description is a visual design.
- If MCP is absent, STOP at a specific blocker for the canvas step; leave the app source untouched. Do not claim a visual was produced.
- Use real design variables/components. If none exist, build only what's needed for this experiment based on **verified** repo tokens.

## Hard constraints
- Initial visual work only: `design/visual-studio/` and pen design canvas. No React/backend changes or dependency installation without explicit founder approval.
- Keep Jester's 18+ gate and privacy restrictions intact; do not expose sensitive birth metadata or invent scientific certainty in compatibility graphics.
- Georgian typesetting is mandatory in rendered examples; inspect long strings and mobile wraps.
- Never use production private data for experiments. Use anonymized/synthetic text/images.
- Produce 3 conceptually different layouts (not just recolors), and critique each. Founder chooses before implementation.
- Never report COMPLETED unless the artifact exists, the canvas was inspected, and limitations are stated.

## Output artifact
- `design/visual-studio/experiments/home-01/EXPERIMENT.md`
- `design/visual-studio/experiments/home-01/REVIEW.md`
- `.pen` canvas saved under `design/visual-studio/canvas/`
- Optional reference screenshots under `design/visual-studio/experiments/home-01/`, avoiding PII.
