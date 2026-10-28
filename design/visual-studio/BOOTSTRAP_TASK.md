# First run: discover and connect existing Jester source of truth

From the actual JESTER repository root:

1. Inspect current branch, file structure, `AGENTS.md`, `GEMINI.md`, any existing `.agents/` or `.gemini/` rules. Preserve all existing data and instructions.
2. Read `design/visual-studio/INTEGRATION_SNIPPETS.md`. If appropriate, append the minimal routing rule to existing project `AGENTS.md` and `GEMINI.md`; never overwrite, contradict or duplicate existing rules.
3. Run the safe source discovery script `python design/visual-studio/scripts/build_context_index.py`.
4. Read the generated `CONTEXT_INDEX.md` and inspect original source documents (product, strategy, design, colors, typographic rules, logo/brand assets, latest implementation). Use search to locate these even if the names differ from expectations. Do NOT assume the project contains any file merely because its expected name is mentioned here.
5. Create `PROJECT_BRIEF.md` from verified sources. Required sections: one-sentence product truth; user and moment; brand and differentiators; approved palette (with EXACT token values where available); typography incl. Georgian; existing components; current Home content; UI states; prohibited tropes; privacy and age rules; source map; contradictions; unknowns. For every concrete claim supply a repo-relative path. Do not fabricate.
6. Identify current Home route/components. If safe synthetic demo context exists, document how to display it. Never use actual credentials or live sensitive personal data.
7. Verify pen.dev desktop installed and `.pen` file open. If necessary ask user to do the one-time desktop installation/MCP toggle; no deception about tool connectivity.
8. Create three editable Home visual concepts in pen.dev; run role-based independent critique; save experiment and review. Do not touch product source during this first visual phase.
9. Report actual files produced, screenshots and pending founder decisions.

Success = source brief grounded + `pencil` MCP verified + three real canvas variants + critique. If the integration is not available, report blocker and keep artifacts truthful. Do not fake a `.pen` document.
