# Autonomous Workflow & Permission Policy

1. **Autonomous Local Execution:**
   - The agent must autonomously execute all development tasks, file edits, testing (`pytest`), server launches, and code refactoring without pausing or prompting for manual permission.
   - Do not ask for trivial confirmations or present planning barriers during routine implementation.

2. **Git Push Invariant (Strict Guardrail):**
   - The agent MUST NEVER execute `git push` autonomously.
   - Any remote Git push or deployment to production requires explicit, direct user instruction (e.g., „ატვირთე გითზე“).
