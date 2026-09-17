# JESTER — Developer Portability & Repository Health Audit

## Executive Summary

**Status: PORTABLE WITH NOTES**

The JESTER repository possesses strong core architectural foundations, a clean separation of concerns, deterministic testing, and an operational AI control plane (`.jester/`). However, the repository currently contains significant developer-environment entanglements and portability defects that must be resolved before onboarding a team of 4–5 developers and multi-agent coding workflows:

1. **163 Absolute Machine-Specific URIs (`file:///c:/Users/fiord/...`)** are hardcoded across 25 Markdown documents, including canonical architecture specs, `SECURITY.md`, and the agent orchestrator skill.
2. **Port Configuration Discrepancy:** `README.md` documents port `5173` for the frontend web client, whereas `frontend/vite.config.ts` and `supabase/config.toml` strictly enforce port `3000`.
3. **Missing `.gitattributes`:** Absence of Git line-ending normalization causes spurious CRLF/LF working tree churn across Windows and Linux/macOS machines.
4. **AI Agent Coupling:** Governance documents and task templates hardcode `"agent": "gemini"`, restricting execution by alternative AI coding assistants (Claude, Cursor, Copilot, etc.).
5. **Multi-Developer Task Workflow Risks:** Sequential task numbering (`TASK-XXXX`) and directory-based lifecycle transitions in `.jester/tasks/` risk Git merge conflicts and ID collisions in concurrent team workflows.
6. **Missing Frontend Environment Template:** No `frontend/.env.example` exists.
7. **No CI/CD Pipeline:** No automated GitHub Actions or equivalent continuous integration workflows exist to validate builds and tests cross-platform.
8. **Personal Identity Seed Data:** Developer personal name, email, and birth parameters are committed into `scripts/seed_farna_user.py`, and developer surname is used in unit test assertions.

No active secrets, credentials, or private keys are exposed in the repository.

---

## Audit Scope

The audit encompassed the entire repository across all 353 tracked files and the `.jester` / `.agents` control planes:
- **Governance & Skills:** `AGENTS.md`, `.agents/rules/autonomous_workflow.md`, `.agents/skills/jester-orchestrator/SKILL.md`
- **Control Plane:** `.jester/config/`, `.jester/project/`, `.jester/tasks/`, `.jester/reports/`, `.jester/README.md`
- **Documentation:** `docs/` (canonical specs and active domain specs), `docs/archive/` (historical evidence and audits), root `SECURITY.md`, `README.md`
- **Backend Application:** `backend/app/`, `backend/.env.example`, `requirements.txt`
- **Frontend Application:** `frontend/src/`, `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`
- **Database & Auth:** `supabase/migrations/`, `supabase/config.toml`
- **Test Suites:** `tests/core/`, `tests/astrology/`, `tests/compatibility/`, `tests/backend/`, `tests/interpretation/`
- **Scripts & Tools:** `scripts/` (seed scripts, corpus builders, audit generators, verification utilities)
- **Git & Environment:** `.gitignore`, `.gitattributes` (check), environment files

---

## Findings

### High Severity Findings

```text
ID: FIND-01
Severity: HIGH
Category: Documentation / Machine Dependency
File: 25 Markdown files across docs/, .agents/skills/, SECURITY.md, and docs/archive/
Evidence: 163 discrete markdown links formatted as `[Label](../../..)`. Examples include `.agents/skills/jester-orchestrator/SKILL.md:17`, `SECURITY.md:123`, `docs/ARCHITECTURE.md:142`, `docs/FRONTEND_CAPABILITY_SPECIFICATION.md:6`.
Problem: Hardcoded Windows absolute filesystem URLs tied to user `fiord`'s personal OneDrive Desktop path.
Impact: Completely breaks internal documentation navigation and tool-based link resolution for other developers or AI agents operating on different machines, user directories, or operating systems (macOS/Linux).
Recommended Fix: Run a repository-wide link normalization to convert all 163 `file:///c:/Users/fiord/OneDrive/Desktop/Jester/...` URLs to standard repository-relative markdown paths (e.g. `[AGENTS.md](AGENTS.md)` or `[ARCHITECTURE.md](docs/ARCHITECTURE.md)`).
```

```text
ID: FIND-02
Severity: HIGH
Category: Configuration / Developer Experience
File: frontend/vite.config.ts, README.md, supabase/config.toml
Evidence: `frontend/vite.config.ts:8` configures `server: { port: 3000 }`. `supabase/config.toml:158` sets `site_url = "http://127.0.0.1:3000"`. In contrast, `README.md:193` instructs developers that the web client runs at `http://localhost:5173/`.
Problem: Direct conflict between documented port and actual runtime configuration.
Impact: Developers following setup instructions cannot access the web client at the documented URL. If developers change Vite to port 5173, Supabase authentication redirects fail due to port 3000 whitelist enforcement.
Recommended Fix: Update `README.md` lines 193–195 to document `http://localhost:3000/` as the client URL, aligning documentation with Vite and Supabase configurations.
```

---

### Medium Severity Findings

```text
ID: FIND-03
Severity: MEDIUM
Category: Configuration / Environment Portability
File: frontend/src/core/config/index.ts, frontend/.env.example (missing), README.md
Evidence: `frontend/src/core/config/index.ts` depends on `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, and `VITE_API_BASE_URL`. No `frontend/.env.example` exists in the repository. `README.md` only instructs `cp backend/.env.example .env`.
Problem: Missing template configuration for frontend client environment variables.
Impact: New developers cannot determine how to configure client endpoints for remote servers, custom network ports, or staging environments without inspecting TypeScript source code.
Recommended Fix: Create `frontend/.env.example` documenting `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, and `VITE_API_BASE_URL`, and document frontend environment setup in `README.md`.
```

```text
ID: FIND-04
Severity: MEDIUM
Category: OS Portability / Documentation
File: README.md, .jester/reports/implementations/TASK-0002-recovery.md
Evidence: `README.md:203` specifies execution with powershell syntax: `.venv\Scripts\python.exe -m pytest tests`. `TASK-0002-recovery.md:55` records `.\.venv\Scripts\python.exe -m pytest ...`.
Problem: Hardcoded Windows-specific virtual environment executable paths with backslashes.
Impact: Fails immediately when executed by developers or CI runners on macOS and Linux (`.venv/bin/python` or `pytest`).
Recommended Fix: Standardize documentation to use portable commands (`pytest tests` or `python -m pytest tests`) and document cross-platform venv activation (`.venv\Scripts\activate` on Windows vs `source .venv/bin/activate` on Unix).
```

```text
ID: FIND-05
Severity: MEDIUM
Category: Git / Cross-Platform Collaboration
File: .gitattributes (missing)
Evidence: `Test-Path .gitattributes` returns False. Git emits line-ending warnings during checkouts and commits: `warning: in the working copy of 'backend/app/core/canonical.py', LF will be replaced by CRLF the next time Git touches it`.
Problem: Absence of Git line-ending normalization rules.
Impact: In a team with mixed Windows, macOS, and Linux workstations, files will suffer CRLF/LF churn, generating phantom working-tree diffs, false-positive merge conflicts, and test failures in strict newline comparisons.
Recommended Fix: Add a root `.gitattributes` configuring `* text=auto eol=lf` for text files and appropriate binary handling for assets.
```

```text
ID: FIND-06
Severity: MEDIUM
Category: AI Agent Portability
File: .agents/skills/jester-orchestrator/SKILL.md, .jester/tasks/templates/task.template.json
Evidence: `SKILL.md:84` declares `agent: Must be "gemini" (or explicitly authorized agent)`. `task.template.json:7` hardcodes `"agent": "gemini"`. Historical task files `TASK-0001.json` and `TASK-0002.json` both hardcode `"agent": "gemini"`.
Problem: Control plane protocol is tightly coupled to a single AI assistant vendor.
Impact: Developers using Claude 3.7, Cursor Agent, Copilot, ChatGPT, or local LLMs cannot participate in the `.jester` task lifecycle without triggering validation failures or modifying governance rules.
Recommended Fix: Update `SKILL.md` and `task.template.json` to accept a configurable list of supported agent identifiers (e.g., `gemini`, `claude`, `cursor`, `copilot`, `human`).
```

```text
ID: FIND-07
Severity: MEDIUM
Category: Collaboration / CI/CD
File: .github/workflows/ (missing)
Evidence: No `.github/` directory or CI configuration exists in the repository.
Problem: Complete absence of automated continuous integration testing and build verification.
Impact: Code breaking cross-platform compatibility, database migrations, Python tests, or frontend builds can be merged without automated verification across multiple developer pull requests.
Recommended Fix: Create `.github/workflows/ci.yml` running backend tests (`pytest`), Supabase migration verification, and frontend bundle validation (`npm run build`) on Ubuntu and Windows matrix runners.
```

```text
ID: FIND-12
Severity: MEDIUM
Category: Multi-Developer Collaboration / Git Safety
File: .jester/tasks/, .agents/skills/jester-orchestrator/SKILL.md
Evidence: Tasks use sequential global IDs (`TASK-0001`, `TASK-0002`) and transition across shared directories (`inbox/` → `active/` → `review/` → `completed/`). All task files currently reside untracked in working trees.
Problem: No namespace allocation or concurrency coordination exists for simultaneous multi-developer task authoring.
Impact: When 4–5 developers create in-flight tasks on separate branches, they will collide on task IDs (e.g. concurrent `TASK-0003.json`). File movements between lifecycle directories create Git rename/delete merge conflicts across branches.
Recommended Fix: Establish a multi-developer task namespace policy (e.g., branch-prefixed IDs like `TASK-DEV-0003` or reservation registry) and document how `.jester/tasks/` are merged in team workflows.
```

---

### Low Severity Findings

```text
ID: FIND-08
Severity: LOW
Category: Personal Data Hygiene / Seeding
File: scripts/seed_farna_user.py
Evidence: `scripts/seed_farna_user.py` contains hardcoded personal developer details: `email: "farna@jester.app"`, `"farna@gmail.com"`, `display_name: "Farna"`, birth timestamp `1998-10-24 14:20:00`, location `Tbilisi, Georgia`, and password `"123"`.
Problem: Dedicated script commits personal developer identity and real birth data into version control.
Impact: Mixes personal developer identity into public/shared repository tooling; new developers have no generic developer persona to seed.
Recommended Fix: Refactor `seed_farna_user.py` into a generic `seed_dev_user.py` accepting parameters via environment variables or utilizing generic persona fixtures (e.g., `dev@jester.app`, "Demo User").
```

```text
ID: FIND-09
Severity: LOW
Category: Personal Data Hygiene / Test Fixtures
File: tests/backend/test_profile_identity.py, tests/backend/test_registration_onboarding_boundary.py, tests/backend/test_phase3a_onboarding_engine.py, tests/backend/test_phase2_auth_lifecycle.py
Evidence: 10 occurrences of `"last_name": "Iordanishvili"` across 4 backend test files (e.g. `test_profile_identity.py:92`).
Problem: Developer's personal family name is used as hardcoded test fixture data.
Impact: Inappropriate persistence of personal family name in committed automated test suites.
Recommended Fix: Replace the developer's surname in test assertions with generic synthetic names (e.g., "Smith", "Doe", "Testuser").
```

```text
ID: FIND-10
Severity: LOW
Category: Documentation / Hygiene
File: README.md
Evidence: `README.md:231` links to `[MIT License](LICENSE)`. `Test-Path LICENSE` confirms the `LICENSE` file does not exist.
Problem: Broken reference to missing license file in the project README.
Impact: 404 broken link error and missing formal licensing terms for external collaborators.
Recommended Fix: Add the root `LICENSE` file containing standard MIT license terms.
```

```text
ID: FIND-11
Severity: LOW
Category: Dependency / Build Portability
File: requirements.txt, README.md
Evidence: `requirements.txt:11` specifies `pyswisseph>=2.10.3.2`.
Problem: `pyswisseph` is a C extension wrapping the Swiss Ephemeris. If pre-built wheels are unavailable for a collaborator's platform (e.g., specific Linux distros, new Python minor releases, or Apple Silicon), pip must compile C source code.
Impact: Installation fails if developer machines lack a C compiler (`gcc`/`clang`/`MSVC`) and Python development headers.
Recommended Fix: Document native compilation prerequisites in `README.md` under Backend Prerequisites.
```

```text
ID: FIND-14
Severity: LOW
Category: Environment Reproducibility
File: Repository Root (.python-version missing)
Evidence: No `.python-version` file exists. The local virtual environment runs Python 3.11.16, while the host system runs Python 3.13.7.
Problem: No machine-readable Python version declaration exists for tools like `pyenv` or `asdf`.
Impact: Developers may initialize environments with untested Python versions (e.g. Python 3.13), causing unexpected wheel or dependency incompatibilities.
Recommended Fix: Add `.python-version` pinning `3.11.16`.
```

---

### Informational Findings

```text
ID: FIND-13
Severity: INFO
Category: Governance / Localization
File: .agents/rules/autonomous_workflow.md, .agents/skills/jester-orchestrator/SKILL.md
Evidence: Line 8 of `autonomous_workflow.md` and line 222 of `SKILL.md` state: `Remote pushes require explicit, direct user instructions (e.g., "ატვირთე გითზე")`.
Problem: Example instruction is written in Georgian.
Impact: Minor localization barrier for international team members, though rule semantics are unambiguous.
Recommended Fix: Add English equivalent examples alongside Georgian (e.g., `e.g., "push to remote" / "ატვირთე გითზე"`).
```

---

## Developer/Machine-Specific References

**Exact Count: 187 references** across tracked files and control plane:

| Pattern | Count | Primary Locations | Notes |
| :--- | :--- | :--- | :--- |
| `file:///c:/Users/fiord/OneDrive/Desktop/Jester/...` | **163** | 25 Markdown files (`docs/`, `SECURITY.md`, `SKILL.md`, `docs/archive/`) | Non-portable absolute machine paths |
| `OneDrive/` | **163** | Identical to above | Windows personal cloud storage path |
| `fiord` | **163** | Identical to above | Personal developer username |
| `C:/Users/` | **163** | Identical to above | Windows absolute drive path |
| `Desktop/` (Machine Path) | **163** | Identical to above | Personal desktop workspace path |
| `Desktop/` (Generic Documentation) | 2 | `FRONTEND_ARCHITECTURE_SPECIFICATION.md:14`, `FRONTEND_FOUNDATION_PHASE_4_1.md:18` | Allowed product context ("Desktop/Mobile Web") |
| `C:\Users\` | 0 | None in tracked files | No backslash user paths |
| `Users\` | 0 | None in tracked files | No backslash user paths |
| `home/` | 1 | `frontend/src/navigation/AppRoutes.tsx:10` | Allowed React module import (`modules/home/`) |
| `Documents/` | 0 | None in tracked files | Clean |
| `Downloads/` | 0 | None in tracked files | Clean |
| `AppData/` | 0 | None in tracked files | Clean |
| `Program Files/` | 0 | None in tracked files | Clean |
| `ProgramData/` | 0 | None in tracked files | Clean |
| `Farna` | **14** | `scripts/seed_farna_user.py` (10), `docs/archive/audits/` (4) | Personal developer first name |
| `Farnaozi` | 0 | None in tracked files | Clean |
| `Iordanishvili` | **10** | 4 backend test files (`tests/backend/`) | Personal developer surname in test fixtures |

---

## Non-Portable Links

**Exact Count: 164 links**

- **163 links** formatted as `[Label](../../..)`
  - `.agents/skills/jester-orchestrator/SKILL.md`: 7 links
  - Root `SECURITY.md`: 6 links
  - Active documentation (`docs/`): 122 links across 18 specifications
  - Archive README (`docs/archive/README.md`): 1 link
  - Historical archive (`docs/archive/`): 27 links across 4 documents
- **1 broken relative link:** `README.md:231` (`[MIT License](LICENSE)` -> `LICENSE` file missing)

---

## Secret/Credential Findings

**Exact Count: 0 Production Secrets**

- No committed OpenAI API keys (`sk-...`), GitHub personal access tokens (`ghp_...`), private key PEM blocks, or production credentials were found in tracked repository files.
- Local development keys (`supabase-demo` JWT service-role key, anon key, and development database URL) are present in `backend/app/config.py`, `scripts/seed_farna_user.py`, `backend/.env.example`, and `frontend/src/core/config/index.ts`. These are standard, publicly known Supabase local Docker credentials intended for offline development.
- Development password `"123"` is committed in `scripts/seed_farna_user.py`.

---

## AI Agent Portability

**Current Status: PARTIALLY PORTABLE**

1. **Vendor Lock-In:** Governance rules (`SKILL.md:84`) and task schema (`task.template.json`) enforce `agent == "gemini"`. Agents identifying as Claude, Cursor, Copilot, or GPT-4o will fail validation during task intake.
2. **Broken Skill Navigation:** `SKILL.md` contains 7 absolute `file:///` links to local governance files. AI agents executing on another developer machine cannot resolve these links.
3. **Control Plane Hygiene:** The underlying Task Protocol v1, directory hierarchy (`.jester/`), orchestrator configuration (`orchestrator.json`), and project index (`index.json`) are cleanly structured and use portable repository-relative paths.

---

## Multi-Developer Readiness

**Current Status: RISKS IDENTIFIED**

1. **Task Concurrency Collisions:** In a team of 4–5 developers, simultaneous creation of tasks will produce duplicate task IDs (e.g. two engineers creating `TASK-0003.json`).
2. **Git Merge Churn on Task Transitions:** Moving task files between folders (`inbox` → `active` → `review` → `completed`) results in Git delete/create operations that conflict across concurrent topic branches.
3. **Port Confusion:** The conflict between `README.md` (port 5173) and `vite.config.ts` / `supabase/config.toml` (port 3000) will cause immediate onboarding confusion.
4. **Line-Ending Inconsistencies:** The lack of `.gitattributes` guarantees dirty working tree states when collaborating across Windows and macOS/Linux.
5. **No Automated Gatekeeper:** The lack of a CI/CD pipeline means regressions in tests, linting, or TypeScript compilation will easily escape into the main branch.

---

## `.jester` Health

**Status: HEALTHY & OPERATIONAL**

- **Directory Integrity:** All 15 required subdirectories exist.
- **JSON Validity:** 5 of 5 JSON files (`orchestrator.json`, `index.json`, `TASK-0001.json`, `TASK-0002.json`, `task.template.json`) are strictly valid JSON.
- **Documentation Index:** All 12 mapped canonical documentation targets in `.jester/project/index.json` resolve to verified existing files.
- **Task Lifecycle:** `TASK-0001` is cleanly staged in `review/`, `TASK-0002` is cleanly closed in `blocked/`, and no duplicate copies exist in `inbox/` or `active/`.

---

## `.agents` Health

**Status: FUNCTIONAL WITH PORTABILITY DEFECTS**

- **Skill Discoverability:** `.agents/skills/jester-orchestrator/SKILL.md` is formatted with valid YAML frontmatter.
- **Governance:** Operational loop and Git push guardrails are explicitly defined in `.agents/rules/autonomous_workflow.md`.
- **Defects:** 7 hardcoded `file:///` URLs inside `SKILL.md` and restrictive `"agent": "gemini"` validation.

---

## Source-of-Truth Health

**Status: STRONG WITH MINOR RESIDUAL CITATIONS**

- Authority hierarchy codified in `AGENTS.md` is strictly respected across recent control-plane implementations.
- `docs/archive/` is cleanly segregated and demarcated as historical evidence only.
- Residual issue: 4 active V1 specifications (`SYNASTRY_V1_SPEC.md`, `TRUST_VERIFICATION_SYSTEM_V1_SPEC.md`, `ASTROLOGY_INTEGRATION_SYSTEM_V1_SPEC.md`, `FRONTEND_CAPABILITY_SPECIFICATION.md`) cite archived `PRODUCT_SPECIFICATION.md` as "Historical Parent".

---

## Recommended Remediation Plan

Prioritized remediation for subsequent controlled implementation tasks:

### Phase 1: High Priority Portability (Immediate)
1. **Normalize Documentation Links (FIND-01):** Batch-replace all 163 `file:///c:/Users/fiord/OneDrive/Desktop/Jester/...` URIs across 25 Markdown documents with portable repository-relative paths.
2. **Align Frontend Port Configuration (FIND-02):** Update `README.md` to document port `3000` matching `vite.config.ts` and `supabase/config.toml`.
3. **Add `.gitattributes` (FIND-05):** Commit root `.gitattributes` enforcing `* text=auto eol=lf`.

### Phase 2: Collaboration & Environment Readiness (Short-Term)
4. **Create `frontend/.env.example` (FIND-03):** Provide client environment defaults.
5. **Generalize AI Agent Protocol (FIND-06):** Allow multi-agent identifiers (`gemini`, `claude`, `cursor`, `copilot`, `human`) in `SKILL.md` and `task.template.json`.
6. **Add Basic CI Pipeline (FIND-07):** Create GitHub Actions workflow for backend pytest and frontend `npm run build`.
7. **Cross-Platform Test Command Documentation (FIND-04):** Update `README.md` to document portable `pytest tests` commands.
8. **Add Root `LICENSE` File (FIND-10):** Add the missing MIT License file.

### Phase 3: Team Hygiene & Concurrency (Medium-Term)
9. **Multi-Developer Task Policy (FIND-12):** Define team task namespace conventions (e.g. branch-scoped IDs).
10. **Sanitize Personal Test Fixtures & Seed Scripts (FIND-08, FIND-09):** Replace developer surname in tests and refactor `seed_farna_user.py` into a generic mock persona script.
11. **Document C Compiler Prerequisites & Pin Python Version (FIND-11, FIND-14):** Add `.python-version` and document `pyswisseph` build dependencies in `README.md`.

---

## Final Verdict

**PASS WITH NOTES**

The core codebase, database layer, astrological engine, and control plane are sound, reproducible, and verifiable. However, the repository cannot be considered fully portable or collaboration-ready until the 163 hardcoded machine URIs, port documentation discrepancy, missing `.gitattributes`, and AI agent lock-in are remediated.
