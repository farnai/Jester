# JESTER — AI Development Control Plane

## What is `.jester/`?

`.jester/` is the persistent **AI Development Control Plane** for the JESTER project. It provides structured task lifecycle tracking, execution orchestration, audit reports, and index pointers for AI pair programmers and automated coding workflows.

---

## Core System Hierarchy

The repository enforces strict separation of concerns across four distinct layers:

```text
AGENTS.md
= agent governance & operational constitution

docs/
= canonical human-facing project specifications & policies

docs/archive/
= historical evidence snapshots (read-only)

.jester/
= AI development control-plane state
```

---

## What Belongs in `.jester/`

1. **`config/`**: Orchestrator configuration, task runner settings, and execution guardrails (such as the autonomous git push prohibition).
2. **`tasks/`**: Structured task lifecycle:
   - `tasks/inbox/`: Proposed or pending tasks awaiting assignment.
   - `tasks/active/`: Currently in-flight task definitions.
   - `tasks/review/`: Completed tasks awaiting user review or sign-off.
   - `tasks/blocked/`: Tasks impeded by unresolved product decisions or external dependencies.
   - `tasks/completed/`: Formally verified, completed task records.
   - `tasks/templates/`: Standard task blueprints (using **Task Protocol v1**).
3. **`reports/`**: Newly generated task reports, test summaries, forensic reviews, and verification logs (`audits/`, `implementations/`, `reviews/`, `verification/`).
4. **`project/`**: Lightweight catalog (`index.json`) providing direct repository-relative paths to canonical documents under `docs/`.

---

## What Does NOT Belong in `.jester/`

- **NO living specifications:** All product truths, architecture rules, database schemas, and API contracts remain strictly under `docs/`.
- **NO duplicate documentation:** Do not copy or mirror text from `docs/` or `AGENTS.md` into `.jester/`.
- **NO application code:** Application logic, frontend components, backend routers, and migrations remain in their respective source trees.
- **NO secrets or tokens:** API keys, database credentials, and service tokens are strictly forbidden in configuration files.

---

## Task Protocol v1

Tasks in `.jester/tasks/` follow **Task Protocol v1** (defined in `tasks/templates/task.template.json`). This protocol standardizes:
- Unique Task IDs (`TASK-XXXX`)
- Clear scope boundaries & constraints
- Automated verification criteria (e.g., `pytest tests`, `npm run build`)
- State transitions (`inbox` → `active` → `review` → `completed`)

Task Protocol v1 is a minimal operational baseline and may evolve through explicit project decisions.
