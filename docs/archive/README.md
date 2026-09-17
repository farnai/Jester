# JESTER — Historical Documentation Archive

**Archive Boundary Definition:**

```text
docs/archive/** = HISTORICAL EVIDENCE ONLY
```

---

## Purpose & Semantic Boundary

All documents located within this directory (`docs/archive/` and all subdirectories: `audits/`, `design/`, `historical/`) are **point-in-time snapshots and historical evidence**.

Archived documents:
- Are frozen historical artifacts representing past sprints, forensic verifications, or superseded design iterations.
- May contain **obsolete test counts** (e.g., 74 or 193 tests passing vs. the active test suite).
- May contain **obsolete migration counts** (e.g., 21 migrations vs. the active schema).
- May contain **superseded architecture** or early implementation stubs.
- May contain **superseded product assumptions** (e.g., old interest limits or monolithic specifications).
- **Must NOT be treated as current product requirements.**
- **Must NOT be treated as current technical contracts.**
- **Must NOT be treated as current implementation state.**

---

## Authority & Conflict Rule

When any archived document or forensic audit conflicts with the current implementation:
**Current source code, runtime configuration, automated tests, database migrations, and active canonical specifications under `docs/` ALWAYS take absolute precedence according to the authority hierarchy defined in [`AGENTS.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/AGENTS.md).**

AI coding agents must never cite or adopt specifications from `docs/archive/**` as active product or engineering requirements.
