---
name: jester-orchestrator
description: Execute JESTER development tasks through the repository's .jester control plane while respecting AGENTS.md, canonical documentation, verification requirements, and Git safety rules.
---

# JESTER Agent Skill: Orchestration & Task Execution

## 1. Purpose & Identity

The **JESTER Orchestrator** skill is the standard operational procedure for autonomous and pair-programming agents executing development tasks within the JESTER repository.

This skill:
- Governs how an agent intakes, executes, verifies, and hands off development tasks via the `.jester/` control plane.
- Standardizes operational transitions across the task lifecycle.

This skill is **NOT**:
- A replacement for [`AGENTS.md`](../../../AGENTS.md).
- A replacement for [`.agents/rules/autonomous_workflow.md`](../../rules/autonomous_workflow.md).
- A documentation system or product specification.
- An architecture authority or second task database.
- An autonomous Git deployment system.

---

## 2. Constitutional Hierarchy & Authority

This skill is strictly subordinate to [`AGENTS.md`](../../../AGENTS.md). When evaluating requirements, resolving ambiguities, or modifying files, agents must follow the repository's established authority hierarchy:

1. **Implementation behavior:** Source code, configuration, and runtime wiring.
2. **Persistence and security:** Migrations, database schema, RLS policies, grants, constraints, functions, and triggers.
3. **Verified behavior:** Automated tests and reproducible runtime behavior.
4. **Product intent:** Explicitly approved canonical specifications under `docs/` and owner decisions.
5. **Mathematical behavior:** Frozen synastry/astrology specifications and relevant engine tests.
6. **Historical evidence:** `docs/archive/**` snapshots are read-only historical evidence and must **never** be treated as active requirements.

If any instruction or task definition conflicts with [`AGENTS.md`](../../../AGENTS.md), [`AGENTS.md`](../../../AGENTS.md) takes precedence.

---

## 3. Mandatory Context Loading

Before executing any task, the agent must load the following foundation files:

```text
AGENTS.md
.jester/config/orchestrator.json
.jester/project/index.json
```

### Targeted Documentation Resolution
- **Do NOT load the entire documentation tree by default.**
- Use [`.jester/project/index.json`](../../../.jester/project/index.json) as the lightweight catalog to resolve **only** the canonical documents relevant to the current task's domain (e.g., `product`, `architecture`, `database`, `security`, `api`, `astrology`, `synastry`, `ai`, `frontend_architecture`, `frontend_capabilities`, `design`, `agent_governance`).
- If a relevant canonical document is missing or ambiguous, report the discrepancy instead of inventing a replacement.
- Never duplicate canonical specifications into `.jester/`. Canonical truth remains solely under `docs/`.

---

## 4. Task Protocol & Lifecycle

Tasks are structured JSON documents conforming to Task Protocol v1 ([`.jester/tasks/templates/task.template.json`](../../../.jester/tasks/templates/task.template.json)).

### Lifecycle State Transitions

```text
.jester/tasks/inbox/
       │
       ▼ (Intake validation & dependencies met)
.jester/tasks/active/
       │
       ├─────────────────────────────────┐
       ▼ (Implementation & verification pass) ▼ (Missing decision / unresolved blocker)
.jester/tasks/review/                 .jester/tasks/blocked/
       │
       ▼ (Explicit user/review approval)
.jester/tasks/completed/
```

### Stage 1: Task Intake & Validation
1. Read the task definition from `.jester/tasks/inbox/TASK-XXXX.json`.
2. Validate required fields:
   - `id`: Unique identifier (`TASK-XXXX`).
   - `title`: Concise summary.
   - `status`: Must be `"inbox"`.
   - `agent`: Must be `"gemini"` (or explicitly authorized agent).
   - `scope`: Bounded list of authorized targets.
   - `constraints`: Specific guardrails.
   - `acceptance_criteria`: Discrete testable statements.
   - `verification`: Explicit test/build commands.
   - `dependencies`: List of prerequisite task IDs or external states.
3. If intake validation fails or the task is assigned to another agent, do not proceed silently. Report the issue.

### Stage 2: Dependency Verification
1. Inspect the `dependencies` array.
2. Confirm all prerequisite tasks are in `.jester/tasks/completed/` or required conditions exist.
3. If any dependency is unsatisfied:
   - Move task: `.jester/tasks/inbox/TASK-XXXX.json` → `.jester/tasks/blocked/TASK-XXXX.json`.
   - Update `status` to `"blocked"`.
   - Write a concise blocker report in `.jester/reports/audits/` or `.jester/reports/reviews/`.
   - Stop execution. Do not guess or invent dependency resolutions.

### Stage 3: Activation
1. When intake and dependencies pass, move:
   `.jester/tasks/inbox/TASK-XXXX.json` → `.jester/tasks/active/TASK-XXXX.json`
2. Update task `status` to `"active"` and record `updated_at`.
3. The task JSON must remain strictly valid. Do not alter acceptance criteria or scope to fit easier solutions.

---

## 5. Implementation Discipline & Guardrails

During implementation, the agent must adhere to strict boundaries:

1. **Scope Control:** Make the smallest coherent change necessary to satisfy the task scope. Avoid unrelated refactors, speculative abstractions, broad renames, or touching unlisted components.
2. **No Autonomous Product Decisions:** If implementation requires an unspecified product, UX, scoring, or architecture decision, **STOP**. Transition the task (`active` → `blocked`), document the open question, and wait for human instruction.
3. **Security & Privacy Invariants:** Never compromise or bypass:
   - `public.birth_data`: Owner-only private data; must never leak to public APIs or profiles.
   - `public.astro_private`: Server-calculated engine internals; clients receive only safe DTOs (`astro_safe_profile`).
   - Production JWT/JWKS verification: Asymmetric JWT verification required in production; HS256 is permitted only in development/test.
   - Canonical connection pairs: Connection records are strictly unordered user pairs.
   - Privacy-safe 404s: Blocked/hidden profiles must resolve as 404s, not existence leaks.
4. **No Speculative Abstractions:** Do not create unused helpers, premature configuration options, or speculative wrappers.
5. **Repository Portability Invariant:** Repository artifacts MUST NOT contain developer-machine-specific absolute filesystem paths, local filesystem URLs, usernames, private workspace locations, or machine-specific links (e.g., `file:///C:/Users/...`, `/Users/...`, `OneDrive/...`, `Desktop/...`). All internal links and references must use portable repository-relative paths or plain identifiers.

---

## 6. Verification Protocol

Completion cannot be claimed without concrete, reproducible verification.

1. **Execute Task Verification:** Run the explicit commands declared in the task's `verification` field (e.g., `pytest tests`, `npm run build`).
2. **Testing Discipline:**
   - Run targeted tests first for rapid feedback.
   - Run broader test suites when modifying shared infrastructure, auth, database security/migrations, or public contracts.
3. **Record Results:** The agent must capture:
   - Exact commands run.
   - Exit codes.
   - Failure details, stack traces, or warnings.
   - Impacted files.

---

## 7. Acceptance Criteria Evaluation

After executing verification, evaluate every item in `acceptance_criteria`:
- **PASS:** Verified and demonstrated with passing tests or tangible artifacts.
- **FAIL:** Criterion not satisfied or test failed.
- **BLOCKED:** Criterion hindered by external dependency or missing specification.

If any required criterion is **FAIL** or **BLOCKED**, the task cannot move to `review`.

---

## 8. Reporting Standard

For every implementation, audit, or verification cycle, create a structured report in the appropriate `.jester/reports/` subdirectory:

- `.jester/reports/audits/`: Investigation, forensic audits, and state inventories.
- `.jester/reports/implementations/`: Execution reports for completed code changes.
- `.jester/reports/reviews/`: Code review and pre-merge evaluations.
- `.jester/reports/verification/`: Test suites, build validations, and security sweeps.

### Implementation Report Template (`.jester/reports/implementations/TASK-XXXX_report.md`)
```markdown
# Implementation Report: TASK-XXXX

## Task Details
- **ID:** TASK-XXXX
- **Title:** [Task Title]
- **Type:** [feature | bugfix | refactor | chore]

## Goal & Scope
- **Goal:** [Summary of objective]
- **Scope Executed:** [List of authorized files/areas touched]

## Changes Made
- [List of modified, created, or deleted files with brief rationale]

## Acceptance Criteria Evaluation
- [Criteria 1]: PASS | FAIL | BLOCKED - [Evidence]
- [Criteria 2]: PASS | FAIL | BLOCKED - [Evidence]

## Verification
- **Command:** `[e.g., pytest tests]` -> Exit Code `0` ([Result summary])
- **Command:** `[e.g., npm run build]` -> Exit Code `0` ([Result summary])

## Risks, Blockers & Notes
- [Document any relevant observations, residual risks, or edge cases]

## Final State
- **Task Status:** [review | blocked]
```

Keep reports factual and concise. Do not paste entire files or duplicated documentation.

---

## 9. Review Handoff & Completion

1. **Move to Review:**
   When implementation succeeds, all acceptance criteria pass, and verification passes:
   - Move: `.jester/tasks/active/TASK-XXXX.json` → `.jester/tasks/review/TASK-XXXX.json`
   - Update `status` to `"review"` and record `updated_at`.
   - **Do NOT mark the task `completed` autonomously.**
2. **Completed State:**
   A task moves to `.jester/tasks/completed/` only upon explicit human review, sign-off, or approved commit step.

---

## 10. Failure & Blocked Handling

If implementation fails, tests fail, or an unresolved decision arises:
1. Do not claim success or fabricate results.
2. Revert any unsafe or partially broken scratch changes to preserve a clean working state.
3. Move: `.jester/tasks/active/TASK-XXXX.json` → `.jester/tasks/blocked/TASK-XXXX.json`.
4. Update `status` to `"blocked"` and record `updated_at`.
5. Document the precise failure or blocking question in the task report.

---

## 11. Git Safety Invariant

The agent must strictly preserve repository Git rules:
- **NO AUTONOMOUS REMOTE PUSH:** The agent MUST NEVER execute `git push` autonomously under any circumstance. Remote pushes require explicit, direct user instructions (e.g., "ატვირთე გითზე").
- **Local Commits:** Do not create local Git commits unless explicitly requested by the user.
- **History Protection:** Never amend previous commits, rebase published branches, or rewrite history unless explicitly instructed.

---

## 12. Standard Operating Sequence

Every JESTER task run by an agent must follow this exact sequential loop:

```text
 1. Load AGENTS.md, orchestrator.json, and index.json.
 2. Resolve only the canonical documents relevant to task domain.
 3. Read task from .jester/tasks/inbox/TASK-XXXX.json.
 4. Validate task fields and agent assignment.
 5. Verify task dependencies (move to blocked if unsatisfied).
 6. Move task to .jester/tasks/active/TASK-XXXX.json.
 7. Implement smallest coherent change within declared scope.
 8. Run verification commands defined in the task.
 9. Evaluate all acceptance criteria (PASS / FAIL / BLOCKED).
10. Generate structured report in .jester/reports/implementations/.
11. If all criteria & tests pass:
      Move task to .jester/tasks/review/TASK-XXXX.json.
    If failed or blocked:
      Move task to .jester/tasks/blocked/TASK-XXXX.json.
12. Present summary to human reviewer. Await review / commit instruction.
```
