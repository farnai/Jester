# Persistent discovery integration (append, do not overwrite)

The repo-level `AGENTS.md` (Codex) and `GEMINI.md` (Gemini CLI) may already contain mandatory rules. Do not replace them. Read both before making edits. With approval, **append this short section** if no equivalent routing exists:

```md
## JESTER visual design tasks
For tasks involving UI redesign, visual art direction, graphics, or pen.dev, invoke project skill `.agents/skills/jester-visual-studio/SKILL.md` and follow `design/visual-studio/WORKFLOW.md`. Start with `design/visual-studio/CONTEXT_INDEX.md` and read actual source documents before any design decisions. For early visual experiments work only in `design/visual-studio/` and the `.pen` canvas; do not modify app code without Founder approval. Keep brand tokens, privacy, 18+ restrictions and Georgian typography from verified repository documents.
```

This routing ensures a short future user request such as `Redesign Home visually` activates the reusable Jester process, rather than a generic ad-hoc prompt.
