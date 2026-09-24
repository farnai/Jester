# JESTER AI Bridge — Migration & Standalone Repository Notice

> **IMPORTANT NOTICE:**  
> The **JESTER AI Bridge** subsystem, along with its provider-agnostic multi-agent orchestration engine, CLI/API adapters, prompt compilation pipeline, Founder Command Interface, automated test suite, and operational documentation, has been completely migrated to a dedicated, independent repository:
> 
> **Repository:** [https://github.com/farnai/JesterBridge](https://github.com/farnai/JesterBridge)  
> **Canonical Documentation:** [JesterBridge docs/ARCHITECTURE.md](https://github.com/farnai/JesterBridge/blob/main/docs/ARCHITECTURE.md)

---

## 1. Summary of Migration

1. **Single Source of Truth:**
   All future development, architectural decisions, configuration, adapters (Gemini, OpenAI, Antigravity CLI, Ollama), runtime selection, and testing for the Bridge live exclusively in arnai/JesterBridge.

2. **Main JESTER Repository Boundary:**
   The main JESTER repository focuses exclusively on the core relationship discovery application (astrology engine, deterministic synastry, Supabase persistence/RLS, FastAPI backend, and React/Vite web application).

3. **Getting Started with the Bridge:**
   To install, configure, start, or test JesterBridge:
   `ash
   git clone https://github.com/farnai/JesterBridge.git
   cd JesterBridge
   pip install -r requirements.txt
   pytest
   python scripts/run_founder_ui.py
   `

---

## 2. Historical Reference

The content below is retained as a frozen historical snapshot from when the Bridge was initially conceptualized in the main JESTER monorepo. For the active, canonical specification, consult docs/ARCHITECTURE.md in the JesterBridge repository.

---

# JESTER AI Bridge Architecture: Provider-Agnostic Foundation

## 1. Overview

The **JESTER AI Bridge** is the multi-agent orchestration layer for the JESTER Development Control Plane (`.jester/`). It coordinates automated and pair-programming agents across the software development lifecycle:
- **Architecting:** Decomposing goals into bounded task specifications.
- **Executing:** Implementing changes within bounded scopes and running verification suites.
- **Reviewing:** Independently verifying code diffs, criteria, and regressions.
- **Auditing:** Performing compliance sweeps and repository health audits.

### Core Architectural Invariant

> **Vendor Neutrality:** The Bridge Core is strictly decoupled from any specific AI provider or model. While ChatGPT (OpenAI) and Gemini (Google) are used for initial validation, the system does not depend on their SDKs, protocols, or schemas. Adding or replacing a provider (such as Claude, Codex, Ollama, or local LLMs) requires **zero modifications** to the Bridge Core, task protocol, state machine, or repository governance.

---

## 2. The 4-Tier Abstraction Model

The Bridge enforces a clean separation of concerns:

```text
ROLE
  ↓ (Operational responsibility & required capabilities)
AGENT
  ↓ (Configured logical worker with identity, prompt, and tool declarations)
PROVIDER
  ↓ (Technical integration adapter implementing generic invocation contract)
MODEL / RUNTIME
    (Concrete model checkpoint, API endpoint, or local engine)
```

### Definitions

1. **Role (`Role` in `jester_bridge/roles.py`):**
   - Defines *what* the agent is responsible for doing.
   - Canonical roles:
     - `architect`: Goal decomposition, task specification creation, scope setting.
     - `executor`: Implementation within scope, test execution, implementation reporting.
     - `reviewer`: Independent diff inspection, criterion verification, review reporting (read-only regarding implementation code).
     - `auditor`: Forensic sweeps, governance verification (read-only).
2. **Agent (`AgentProfile` in `jester_bridge/agent.py`):**
   - Represents a configured worker profile.
   - Encapsulates: `id`, `role`, `provider`, `model`, and declared `capabilities`.
3. **Provider (`AgentProvider` in `jester_bridge/provider.py`):**
   - Represents the technical transport/integration.
   - Exposes: `provider_id`, `health_check()`, `get_supported_capabilities()`, and `invoke(request) -> InvocationResult`.
   - **Critical Design Boundary:** Providers do not know about roles or task semantics; they merely execute normalized requests and return normalized results.
4. **Model / Runtime:**
   - Specific model name or local container passed via agent configuration. Never parsed or hardcoded by the core.

---

## 3. Task Protocol v2

Task files under `.jester/tasks/` conform to **Task Protocol v2**:

```json
{
  "id": "TASK-0004",
  "title": "Implement AI Bridge Foundation",
  "type": "feature",
  "status": "inbox",
  "priority": "high",
  "role": "executor",
  "assigned_agent": "gemini-dev",
  "required_capabilities": [
    "repository_read",
    "repository_write",
    "command_execution",
    "testing"
  ],
  "goal": "Establish provider-agnostic bridge foundation",
  "scope": [
    "jester_bridge/",
    "tests/bridge/"
  ],
  "constraints": [
    "Do not import vendor SDKs in core"
  ],
  "acceptance_criteria": [
    "Provider swappability test passes"
  ],
  "verification": [
    "pytest tests/bridge"
  ],
  "dependencies": [],
  "created_at": "2026-09-17T23:45:00+04:00",
  "updated_at": "2026-09-17T23:45:00+04:00"
}
```

### Backward Compatibility with Task Protocol v1

Historical task records (`TASK-0001.json`, `TASK-0002.json`, `TASK-0003.json`) must remain immutable historical evidence. The normalization layer in `jester_bridge/protocol.py` (`load_task_from_file` and `load_task_from_dict`) automatically infers:
- `role`: Mapped from `type` (`audit` → `auditor`, otherwise `executor`).
- `assigned_agent`: Read from legacy `agent` field (`"gemini"`).
- `required_capabilities`: Populated with canonical default capabilities for the role.

Historical task files remain 100% untouched on disk.

---

## 4. Capability Preflight Validation

Tasks declare `required_capabilities`; agents declare supported `capabilities`.

Before dispatching an invocation, the Bridge Core validates:

$$\text{RequiredCapabilities}(\text{Task}) \subseteq \text{SupportedCapabilities}(\text{Agent})$$
$$\text{RequiredCapabilities}(\text{Task}) \subseteq \text{SupportedCapabilities}(\text{Provider})$$

Standard capabilities:
- `planning`: Architectural reasoning and specification decomposition.
- `reasoning`: Logic evaluation and contract validation.
- `repository_read`: Reading project files and git logs.
- `repository_write`: Modifying files and creating reports within approved scope.
- `command_execution`: Running terminal commands (`pytest`, `npm`, Docker).
- `testing`: Executing and interpreting test suites.
- `review`: Independent adversarial evaluation of code changes.
- `local_runtime`: Direct access to local development environment.

If an assigned agent or provider lacks any required capability, the core raises `CapabilityMismatchError` **before** dispatching any execution.

---

## 5. Normalized Contracts

All communication across the Bridge Core utilizes vendor-neutral Pydantic contracts (`jester_bridge/contracts.py`):
- `InvocationRequest`: Carries `task_id`, `role`, `agent_id`, `provider`, `model`, `required_capabilities`, and contextual payload.
- `InvocationResult`: Carries `status` (`SUCCESS`, `FAILED`, `BLOCKED`, `REWORK_REQUIRED`), `summary`, `files_modified`, `reports_generated`, `error_message`, and isolated `raw_metadata`.

Zero vendor SDK response objects (OpenAI `ChatCompletion`, Google `GenerateContentResponse`, Anthropic `Message`) can leak into core logic.

---

## 6. How to Add a Future Provider (e.g. Claude or Ollama)

Adding a new AI provider requires only **three steps** with **zero core modifications**:

### Step 1: Implement the `AgentProvider` Interface
Create a new adapter module:
```python
from jester_bridge.provider import AgentProvider
from jester_bridge.contracts import InvocationRequest, InvocationResult, InvocationStatus

class AnthropicProvider(AgentProvider):
    @property
    def provider_id(self) -> str:
        return "anthropic"

    def health_check(self) -> bool:
        # Check API key presence / endpoint ping
        return True

    def get_supported_capabilities(self) -> set[str]:
        return {"planning", "reasoning", "repository_read", "review"}

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        # Call Anthropic API using request.payload
        # Normalize response into InvocationResult
        return InvocationResult(
            request_id=request.request_id,
            task_id=request.task_id,
            status=InvocationStatus.SUCCESS,
            agent_id=request.agent_id,
            provider=self.provider_id,
            summary="Completed by Claude",
            completed_at="..."
        )
```

### Step 2: Register in Configuration (`.jester/config/agents.json`)
```json
{
  "agents": {
    "claude-architect": {
      "id": "claude-architect",
      "role": "architect",
      "provider": "anthropic",
      "model": "claude-3-7-sonnet",
      "capabilities": ["planning", "reasoning", "repository_read"]
    }
  },
  "role_bindings": {
    "architect": "claude-architect"
  }
}
```

### Step 3: Register the Provider in BridgeCore
```python
core.register_provider(AnthropicProvider())
```

The Bridge Core, task protocol, state transitions, report generators, and verification suites remain completely unchanged.

---

## 7. Concrete Provider Adapters

### 7.1 OpenAI Provider (`jester_bridge/openai_provider.py`)

The `OpenAIProvider` is the concrete adapter connecting JESTER to OpenAI models (e.g. `gpt-4o`, `o3-mini`). It strictly isolates the OpenAI Python SDK behind the `AgentProvider` boundary.

#### Key Features:
- **Environment Credentials:** API keys are never stored in repository files. The provider reads `OPENAI_API_KEY`, `OPENAI_BASE_URL` (optional), and `OPENAI_ORG_ID` (optional) from environment variables.
- **Model Agnostic:** Model selection is dynamic and configuration-driven via `.jester/config/agents.json` or `request.model`.
- **Role Independence:** A single `OpenAIProvider` instance services multiple canonical roles (`architect`, `reviewer`, `auditor`) by dynamically tailoring system prompts to the role specified in `InvocationRequest`.
- **Error Sanitization:** Normalizes network timeouts, authentication rejections, and rate limits into `InvocationResult(status=InvocationStatus.FAILED)`, stripping potential credential leaks from error messages.
- **SDK Isolation:** SDK response structures (`ChatCompletion`, `Choice`, `Usage`) are decomposed into standard Python dictionaries and strings. Zero vendor SDK objects cross the provider boundary into `BridgeCore`.

#### Registration Example:
```python
from jester_bridge import BridgeCore, OpenAIProvider, load_bridge_config

config = load_bridge_config(".jester/config/agents.json")
core = BridgeCore(config=config)
core.register_provider(OpenAIProvider())  # Reads OPENAI_API_KEY from environment
```

### 7.2 Google Gemini Provider (`jester_bridge/google_provider.py`)

The `GoogleProvider` is the concrete adapter connecting JESTER to Google Gemini models (e.g. `gemini-2.5-pro`, `gemini-2.5-flash`).

#### Architectural Integration Decision (REST via httpx vs Heavy SDK):
- **Selected Mechanism:** Official Google Generative Language REST API (`generateContent`) using the repository's established `httpx` HTTP transport.
- **Rationale:** The `google-genai` and `google-generativeai` packages introduce heavy dependency trees (up to 20 subpackages including grpc/protobuf) and downgrade `websockets` from 17.1 to 16.1.1, potentially compromising FastAPI/Starlette dependencies. Utilizing `httpx` introduces zero new packages, guarantees 100% deterministic test isolation, and avoids version conflicts while adhering directly to Google's official v1beta API specification.
- **Environment Credentials:** Reads `GEMINI_API_KEY` or `GOOGLE_API_KEY` from environment variables.
- **Model Agnostic:** Model selection is dynamic and configuration-driven (defaults to `gemini-2.5-pro`).
- **Role Independence:** Formulates role-tailored system instructions (`executor`, `architect`, `reviewer`, `auditor`).
- **Error Sanitization:** Strips Google API key patterns (`AIza...`) from error messages and normalizes HTTP 4xx/5xx and timeouts into `InvocationResult(status=InvocationStatus.FAILED)`.
- **SDK Isolation:** Gemini candidates and usage metadata are unpacked into primitive Python types; zero HTTP/Google SDK objects cross the provider boundary.

#### Registration Example:
```python
from jester_bridge import BridgeCore, GoogleProvider, load_bridge_config

config = load_bridge_config(".jester/config/agents.json")
core = BridgeCore(config=config)
core.register_provider(GoogleProvider())  # Reads GEMINI_API_KEY from environment
```

---

## 8. Multi-Provider Orchestration Topology

With both `OpenAIProvider` and `GoogleProvider` implemented, JESTER supports the full target heterogeneous topology:

```text
                        JESTER BRIDGE CORE
                                │
          ┌─────────────────────┴─────────────────────┐
          │                                           │
    OpenAIProvider                              GoogleProvider
          │                                           │
       ChatGPT                                     Gemini
          │                                           │
  Architect / Reviewer                             Executor
(chatgpt-lead / chatgpt-critic)                  (gemini-dev)
```

The Bridge Core treats both providers identically through the `AgentProvider` contract. Swapping a role from OpenAI to Gemini, or from Gemini to a future provider (Claude, Ollama), requires modifying **only** configuration bindings in `.jester/config/agents.json`.

---

## 9. Multi-Agent Orchestration Layer (`jester_bridge/orchestration.py`)

The `BridgeOrchestrator` coordinates multi-agent task execution through explicit, provider-neutral stages:

```text
               ARCHITECT STAGE
         (User intent -> Task Protocol v2)
                      │
                      ▼
               EXECUTOR STAGE
    (Bounded code generation / verification)
                      │
                      ▼
               REVIEWER STAGE
   (Independent acceptance criteria evaluation)
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
    [PASS Verdict]      [REWORK_REQUIRED Verdict]
          │                       │
          ▼                       ▼
AWAITING_HUMAN_SIGNOFF      EXECUTOR STAGE
(Mandatory Gate)        (Bounded by max_rework_cycles)
          │
          ▼ (Approved by Human)
      COMPLETED
```

### Key Architectural Invariants:
1. **Zero Provider Coupling:** The orchestrator works exclusively through `BridgeCore`, `Task`, `AgentProfile`, and normalized request/result envelopes. Provider resolution occurs dynamically from configuration (`.jester/config/agents.json`).
2. **Normalized Handoffs:** Data exchanged between stages strictly adheres to typed contracts (`ArchitectInput/Result`, `ExecutorInput/Result`, `ReviewInput/Result`). Raw vendor SDK objects are prohibited.
3. **Mandatory Human Sign-off:** Reviewer `PASS` moves the orchestration state to `AWAITING_HUMAN_SIGNOFF`. The orchestrator never auto-completes tasks, creates git commits, or pushes.
4. **Bounded Rework Cycles:** If the reviewer returns `REWORK_REQUIRED`, execution returns to the executor up to `max_rework_cycles` (default: 2). Exceeding this threshold marks the task `BLOCKED`, preventing infinite retry loops.
5. **Lifecycle Coherence:** Directly drives `.jester` task states (`inbox` → `active` → `review` → `completed` / `blocked`) without maintaining a redundant secondary task database.

---

## 10. Phase 2C-2: Controlled End-to-End Workflow & Safe Execution Boundary

Phase 2C-2 establishes the first live controlled end-to-end workflow connecting Founder Request → Architect → Inbox Task → Activation → Executor → Bounded Workspace Runtime → Verification → Reviewer → Mandatory Human Sign-off.

```text
Founder Request
      │
      ▼
ChatGPT Architect (OpenAIProvider)
      │
      ▼
Task Protocol v2 Task Created (`.jester/tasks/inbox/TASK-XXXX.json`)
      │
      ▼
Preflight Validation Engine (`jester_bridge/preflight.py`)
      │
      ▼
Task Activated (`.jester/tasks/active/TASK-XXXX.json`)
      │
      ▼
Gemini Executor (GoogleProvider)
      │
      ▼
Bounded Workspace Runtime (`jester_bridge/runtime.py`)
  - Enforces `task.scope` boundaries
  - Blocks protected paths (`.git`, `.env`, `AGENTS.md`, `supabase/migrations`)
  - Applies atomic code modifications with backup rollback
  - Executes declared verification commands (`pytest ...`)
      │
      ▼
Implementation Report Generated (`.jester/reports/implementations/TASK-XXXX.md`)
      │
      ▼
Task Moved to Review (`.jester/tasks/review/TASK-XXXX.json`)
      │
      ▼
ChatGPT Reviewer (OpenAIProvider)
  - Independently evaluates implementation diffs, acceptance criteria, and test outcomes
  - Emits structured verdict (`PASS`, `REWORK_REQUIRED`, `BLOCKED`)
  - Writes review report (`.jester/reports/reviews/TASK-XXXX.md`)
      │
      ▼
MANDATORY HUMAN SIGN-OFF GATE
  - Status: `AWAITING_HUMAN_SIGNOFF`
  - Zero auto-completion, zero auto-commits, zero pushes
      │
      ├── [Human REJECT] ──► `.jester/tasks/blocked/TASK-XXXX.json` (or rework if within limit)
      └── [Human APPROVE] ─► `.jester/tasks/completed/TASK-XXXX.json`
```

### Safety Boundaries & Governance Guarantees

1. **Strict Scope Isolation:** The runtime rejects any attempt to modify files outside `task.scope`. Global scopes (`.`, `/`, `*`) are explicitly rejected by preflight validation.
2. **Protected Paths Invariant:** The paths `.git`, `.env`, `AGENTS.md`, and `supabase/migrations` can NEVER be modified by automated executions, regardless of task scope declarations.
3. **Atomic Rollback:** If any file write fails, or if declared verification commands (`task.verification`) return a non-zero exit code, all modifications are immediately and cleanly reverted from memory backups.
4. **Credential Sanitization:** API keys and credentials are never stored in reports, task files, logs, or exceptions. Preflight checks detect unconfigured or placeholder credentials cleanly before any live API call is executed.
5. **No Autonomous Daemons:** The workflow is strictly invocation-driven. It contains zero background daemons, zero auto-commits (`git commit`), zero git adds (`git add .`), and zero git pushes (`git push`).
6. **Mandatory Human Approval:** Even upon Reviewer `PASS`, execution unconditionally halts at `AWAITING_HUMAN_SIGNOFF`. Transition to `completed` requires explicit human approval via CLI (`--approve-task TASK-XXXX` or interactive confirmation).

---

## 11. Phase 2D: Token / Context Observability & Portability Hardening

Phase 2D enhances the AI Bridge with lightweight, vendor-neutral token observability and repository-wide portability hardening.

### Provider-Neutral Token Observability

Observability tracks token expenditure without coupling core logic to vendor schemas:

1. **Normalized Contract (`UsageMetrics` in `jester_bridge/contracts.py`):**
   - Fields: `input_tokens: Optional[int]`, `output_tokens: Optional[int]`, `total_tokens: Optional[int]`.
   - Helper: `UsageMetrics.add(other)` enables cumulative token aggregation.
2. **Provider Mapping:**
   - **OpenAI:** Maps `response.usage.prompt_tokens`, `completion_tokens`, and `total_tokens` directly into `UsageMetrics`.
   - **Google Gemini:** Maps REST API `usageMetadata.promptTokenCount`, `candidatesTokenCount`, and `totalTokenCount` into `UsageMetrics`.
   - **Mocks / Testing:** Injects predictable default token counts (100 in / 50 out / 150 total) for deterministic offline testing.
3. **Zero-Branching Principle:**
   - Core, orchestrator, and workflow modules contain **zero** provider checks (no `if provider == "openai": ...`) to parse or aggregate token usage. Token metrics are handled exclusively through the normalized `InvocationResult.usage` interface.
4. **Session Aggregation:**
   - `session.get_total_usage()` computes the cumulative tokens across completed stages (`architect`, `executor`, `reviewer`).
   - `session.get_stage_usage()` returns a per-stage breakdown with role, provider, model, and token metrics.
5. **Report & CLI Integration:**
   - Generated implementation reports embed executor token usage.
   - Review reports embed both reviewer tokens and the cumulative workflow aggregate tokens.
   - CLI workflow summary prints formatted stage-by-stage token breakdown and total count.

### Repository Portability Enforcement

To guarantee that repository artifacts remain 100% portable across developer machines and operating systems:

1. **Prohibited Patterns:**
   - `file:///C:/Users/...` or any local `file:///` filesystem URLs.
   - Machine-specific absolute paths (`C:\Users\...`, `C:/Users/...`, `/Users/...`, `/home/<user>/...`).
   - Sync service and environment paths (`OneDrive\...`, `Desktop\...`).
2. **Sanitization Engine (`sanitize_portable_paths` in `jester_bridge/workflow.py`):**
   - Multi-layer regex replaces absolute workspace paths with repository-relative POSIX paths.
   - Strips all `file:///` prefixes and normalizes Windows backslashes into standard forward slashes.
   - Converts external home directory paths to generic `~/`.
3. **Outcome Normalization (`WorkflowOutcome._rel_path`):**
   - All paths returned by `ControlledWorkflowRunner` (`task_file_path`, `implementation_report_path`, `review_report_path`) are guaranteed repository-relative POSIX strings.

---

## 12. Phase 2E: Context Engine, Diff Capture & Reviewer Hardening (TASK-0006)

TASK-0006 addresses the two major architectural blind spots of the early Bridge foundation:

```text
BEFORE TASK-0006 (Blind Loop):
Task Scope -> Executor (no code context) -> Runtime -> Text Summary -> Reviewer (no diff)

AFTER TASK-0006 (Evidence-Based Engineering Loop):
Task Scope -> ContextEngine -> In-Scope Code Context -> Executor -> Bounded Runtime -> Unified Diff -> Reviewer -> Human Sign-off
```

### 12.1 Deterministic Context Engine (`jester_bridge/context.py`)

Provides deterministic repository context assembly for the Executor:
1. **Scope Ingestion:** Ingests only files declared in `task.scope`.
2. **Security & Workspace Containment:** Reuses `PROTECTED_PATHS` (`.git`, `.env`, `AGENTS.md`, `supabase/migrations`) and strictly blocks path traversal (`..`) escaping the repository root.
3. **Deterministic Character Budgeting:** Enforces a hard upper bound (default: 50,000 characters total, 20,000 characters per file) with explicit truncation indicators to protect against context window exhaustion.
4. **Structured Format:** Serializes into `ContextBundle` with `FileContext` elements formatted as clean markdown blocks in prompt payloads.

### 12.2 Atomic Unified Diff Generation (`jester_bridge/runtime.py`)

The `BoundedWorkspaceRuntime` computes standard unified diffs (`difflib.unified_diff`) comparing the original in-memory file backups against the modified state on disk:
- Generates standard `a/...` and `b/...` headers, chunk line numbers, and additions/deletions.
- Captures the diff atomically before test verification.
- Stores the diff in `RuntimeExecutionResult.diff` and passes it to `ExecutorResult.diff`.

### 12.3 Hardened Reviewer Handoff & Evidence-Based Inspection

The Reviewer no longer relies on self-reported Executor summaries:
1. **Contract Enforcement:** `ReviewInput.diff` carries the actual unified code diff.
2. **Prompt Presentation:** Both `OpenAIProvider` and `GoogleProvider` format a prominent `UNIFIED CODE DIFF (CRITICAL EVIDENCE)` block in the user prompt and instruct the reviewer to independently evaluate code diffs.
3. **Independent Defect Detection:** Verified to reject changes that introduce known defects (such as security bypasses or syntax errors) even when the Executor summary claims 100% success.
4. **Report Auditability:** Unified diffs are embedded into both implementation reports (`.jester/reports/implementations/TASK-XXXX.md`) and review reports (`.jester/reports/reviews/TASK-XXXX.md`).

## 13. Controlled Delivery Pipeline & GitController (TASK-0007)

The JESTER AI Bridge enforces a strict separation between AI orchestration/review and repository delivery. AI providers never execute Git commands. Repository modifications are governed by a dedicated, non-autonomous `GitController` that operates exclusively downstream of verified human approval.

### 13.1 Architecture & Core Responsibilities

```text
Task Scope
    ↓
Context Engine
    ↓
Executor
    ↓
Bounded Workspace Runtime
    ↓
Verification
    ↓
Reviewer (Unified Diff Inspection)
    ↓
Reviewer PASS
    ↓
AWAITING_HUMAN_SIGNOFF
    ↓
Explicit Human Approval
    ↓
GitController
    ├── Inspect Working Tree & Status
    ├── Stage Explicitly Approved Files Only (NEVER git add .)
    ├── Validate Staged Diff against Approved Delivery Set
    ├── Verify CommitAuthorization
    ├── Execute Commit
    └── Optional Separate PushAuthorization → Safe Remote Push
```

`GitController` (`jester_bridge/git_controller.py`) is responsible for:
- `inspect_status()`: Inspects working tree cleanliness, modified, untracked, and staged files.
- `inspect_diff(staged=False, files=None)`: Retrieves unstaged or staged diffs safely.
- `validate_delivery(task, session, approved_files)`: Enforces prerequisite contracts before delivery.
- `stage_approved_files(approved_files)`: Stages strictly the files approved by human review.
- `validate_staged_diff(approved_files)`: Asserts staged changes match the approved delivery set without extra files.
- `commit(authorization, session, task)`: Creates commits after verifying explicit human authorization and review pass.
- `push(authorization)`: Bounded upstream push requiring independent human push authorization.

### 13.2 Human Approval & Dual Authorization Boundaries

1. **Mandatory Human Signoff:** Commit execution strictly requires `session.review_result.verdict == ReviewVerdict.PASS`, `session.current_stage` in (`AWAITING_HUMAN_SIGNOFF`, `COMPLETED`), and non-empty `session.human_signoff_by`. Reviewer PASS alone does NOT permit a commit.
2. **Explicit Commit Authorization:** Commits require a typed `CommitAuthorization` token carrying `task_id`, `approver`, `approved_files`, and `commit_message`.
3. **Independent Push Authorization:** Human approval for commit does NOT authorize push (`Commit approved ≠ Push approved`). Upstream push requires a distinct `PushAuthorization` specifying `task_id`, `approver`, `remote`, and optional `branch`.

### 13.3 Staging Safety & Diff Validation

- **No Mass Staging:** `GitController` strictly prohibits `git add .` and `git add -A`. Only files listed in `approved_files` are passed to `git add -- <files>`.
- **Fail-Closed Diff Comparison:** Following staging, `validate_staged_diff()` checks `git diff --cached --name-only`. If any file outside `approved_files` is staged or if staged changes are empty, delivery is aborted immediately.
- **Unrelated Working Tree Preservation:** Unrelated user modifications are never destroyed, reset, or stashed. If unrelated files are staged, delivery fails closed without executing destructive operations.

### 13.4 Security Invariants & Protected Paths

1. **Protected Paths Rejection:** Reuses `PROTECTED_PATHS` (`.git`, `.env`, `AGENTS.md`, `supabase/migrations`, `migrations`). Any attempt to stage or deliver protected files fails immediately with `GitSecurityError` or validation failure.
2. **Destructive Commands Blocked:** Commands like `git reset --hard`, `git clean -fd`, `git checkout -- .`, `git restore .`, `git rebase`, and `git stash` are blocked at the controller level and raise `GitSecurityError`.
3. **No Force Push:** Flags `--force`, `-f`, and `--force-with-lease` are unconditionally forbidden.
4. **Bounded Subprocess Execution:** Git operations use parameterized argument lists (`["git", ...]`), avoid `shell=True`, and enforce bounded timeouts (default 30.0s).
5. **Zero Provider Coupling:** `GitController` does not import or depend on any AI provider or vendor SDK.

## 14. Persistent Execution History (TASK-0008)

The JESTER AI Bridge includes a durable, auditable execution-history layer implemented via standard SQLite (`sqlite3`). This capability observes and records orchestration lifecycle events without creating a second task control plane or parallel state machine.

### 14.1 Purpose & Authority Separation

- **Task State Authority:** The `.jester/tasks/` file structure (`inbox/`, `active/`, `review/`, `completed/`, `blocked/`) remains the authoritative source of truth for task lifecycle.
- **Execution History:** Answers "What actually happened during this execution?" (`executions` and `execution_events` tables).
- **Execution Identity (`task_id != execution_id`):** A task can undergo multiple runs or retries over time. Each run generates a distinct `execution_id` (e.g. `exec-sess-XXXX`), allowing full multi-run auditability and historical reconstruction.

### 14.2 Storage Location & Engine

- **Database Location:** Local SQLite database at `.jester/history.db` (`DEFAULT_HISTORY_DB_REL`).
- **Standard Library:** Built purely on Python's built-in `sqlite3` with foreign keys enabled (`PRAGMA foreign_keys = ON;`), requiring zero external dependencies, no Supabase tables, and no Redis.
- **Test Isolation:** Integration and unit tests use isolated temporary databases (`tmp_path`) and never write to the real project database.

### 14.3 Data Model & Chronological Events

The store manages two relational tables:
1. **`executions` (`ExecutionRecord`):** Captures high-level execution metadata:
   - Identifiers: `execution_id`, `task_id`, `task_title`, `task_protocol_version`.
   - Timestamps & Status: `created_at`, `started_at`, `completed_at`, `overall_status`, `current_stage`.
   - Observability: `total_input_tokens`, `total_output_tokens`, `total_tokens`.
   - Results: `verification_passed`, `verification_summary`, `reviewer_verdict`, `reviewer_summary`, `human_signoff_by`, `human_signoff_notes`.
   - Git Delivery: `git_commit_hash`, `git_branch`, `git_pushed`, `git_delivery_summary`.
   - Metadata: `metadata_json`.
2. **`execution_events` (`ExecutionEvent`):** Append-oriented, chronological records of stage transitions:
   - `event_id`, `execution_id`, `event_type`, `timestamp`.
   - `stage`, `status`, `role`, `agent_id`, `provider`, `model`.
   - `summary`, `error`, `input_tokens`, `output_tokens`, `total_tokens`, `metadata_json`.

### 14.4 Bounded Storage & Secret Protection

- **Length Limits:** Summaries and error messages are capped at 1,000 characters (`MAX_SUMMARY_LENGTH = 1000`), appending `... [TRUNCATED]` if exceeded.
- **Metadata Bounding:** JSON metadata serialization is capped at 8,192 characters.
- **Credential Redaction:** Keys matching sensitive patterns (`api_key`, `secret`, `token`, `password`, `authorization`, `private_key`, `bearer`) and values containing tokens or auth headers are automatically redacted to `[REDACTED_SECRET]`.

### 14.5 Failure Semantics

Persistence failure never corrupts or alters the business workflow:
- The `ControlledWorkflowRunner` wraps history persistence in safe helpers (`_record_event_safe`, `_update_execution_safe`).
- If the SQLite database is unavailable, locked, or unwritable, the business workflow proceeds authentic to its lifecycle state (e.g. `AWAITING_HUMAN_SIGNOFF`, `COMPLETED`), and captures the issue in `WorkflowOutcome.persistence_error`.
- Direct `ExecutionHistoryStore` operations raise `ExecutionHistoryError` for deterministic caller handling.

### 14.6 Retrieval Interface

The store provides an internal, programmatic query interface:
- `get_execution(execution_id) -> Optional[ExecutionRecord]`
- `get_executions_for_task(task_id, limit=50) -> List[ExecutionRecord]`
- `list_recent_executions(limit=50) -> List[ExecutionRecord]`
- `get_events_for_execution(execution_id) -> List[ExecutionEvent]`
- `get_execution_summary(execution_id) -> Optional[Dict[str, Any]]`

---

## 15. Advanced Context Engine & Structured Handoffs (TASK-0009)

The JESTER AI Bridge incorporates an advanced, role-aware, and budget-governed context assembly engine (`ContextEngine` in `jester_bridge/context.py`) combined with formalized inter-role handoff contracts (`ArchitectHandoff`, `ExecutorHandoff`, `ReviewerHandoff` in `jester_bridge/contracts.py`).

```text
Task (.jester/tasks/)
  ↓
Task Scope & Constraints
  ↓
Context Selection (Multi-Signal)
  ↓
Context Budgeting (Total & Per-File Limits)
  ↓
Role-Specific ContextPackage
  ↓
Structured Handoff
  ↓
Agent Invocation → Provider (OpenAI / Gemini)
```

### 15.1 Context Engine Responsibilities & Separation of Concerns

- **Context Engine:** Decides "What repository and task information should this role receive?"
- **Orchestrator:** Decides "What role/stage executes next?"
- **Agent:** Decides "How should this task be performed?"
- **Provider:** Decides "How should the normalized agent request be executed by the selected AI provider?"

The Context Engine does not execute commands, modify files, route models, or transition task states.

### 15.2 ContextPackage Schema & Versioning

Context is delivered via a structured, serializable `ContextPackage` (`context_version = "v1"`), maintaining backward compatibility with `ContextBundle`:
- `task_id`, `role`, `stage`, `context_version`
- `files` (`List[FileContext]`): Selected repository files with individual truncation flags and provenance.
- `included_paths`: In-scope repository-relative paths.
- `excluded_paths`: Mapping of rejected paths to deterministic exclusion reasons.
- `selection_reasons`: Mapping of relative paths to selection rationale.
- `provenance_items`: List of `ContextItemProvenance` audit records.
- `task_context`, `diff`, `diff_truncated`, `verification_output`, `relevant_metadata`.
- `total_characters`, `max_characters`, `truncated`, `truncated_files_count`.

### 15.3 Role-Aware Context Selection

Context requirements strictly differ by role:
1. **Architect:** Needs task definition, user intent, core architecture specification (`docs/AI_BRIDGE_ARCHITECTURE.md`), relevant existing contracts, and in-scope modules.
2. **Executor:** Needs task requirements, `ArchitectHandoff` (implementation intent, architectural notes), in-scope source files, relevant interfaces, and related test suites (`tests/`).
3. **Reviewer:** Needs original task requirements, acceptance criteria, actual unified code diff (`diff`, `source_type="diff"`, `CRITICAL` priority), test verification output (`verification_output`), changed files, and related tests to compare *intended change* against *actual change*.

### 15.4 Deterministic Prioritization & Budgeting

Context candidates are evaluated deterministically using explicit priority tiers:
- **`CRITICAL` (Rank 4):** Task specification, explicit scope files (`task.scope`), actual unified code diff, changed files for Reviewer, verification output.
- **`HIGH` (Rank 3):** Directly related test files (heuristically resolved via directory mirroring), interface contracts.
- **`NORMAL` (Rank 2):** Repository files mentioned in task text (parsed deterministically), adjacent source modules, architecture documentation.
- **`LOW` (Rank 1):** Peripheral documentation, broader repository context.

**Budgeting Rules:**
- Candidates are sorted by `(-priority.rank, relative_path)`.
- Total character budget (`DEFAULT_MAX_CONTEXT_CHARACTERS = 50_000`) and per-file budget (`DEFAULT_MAX_FILE_CHARACTERS = 20_000`) are strictly enforced.
- Space is reserved for truncation markers (`[... truncated X characters ...]`) so that total characters never exceed configured limits.
- High-priority context is allocated first; lower-priority items are truncated or excluded with explicit reasons (`"Context budget exceeded"`). Critical context is never silently dropped.

### 15.5 Provenance & Exclusion Taxonomy

Every context item carries an audit record (`ContextItemProvenance`):
- `source_type`: `task`, `explicit_scope`, `source_file`, `test_file`, `contract`, `architecture_doc`, `changed_file`, `diff`, `verification`, `handoff`.
- `source_path`, `priority`, `reason`, `original_size_chars`, `included_size_chars`, `truncated`.

Exclusion reasons are explicit and deterministic:
- `"Protected repository path '<name>'"`
- `"Path traversal forbidden ('..')"`
- `"Path escapes workspace root"`
- `"Context budget exceeded (<max> chars)"`
- `"Dangerous or empty scope path"`

### 15.6 Structured Handoff Specifications

1. **`ArchitectHandoff` (Architect → Executor):**
   - `task_id`, `task_objective`, `implementation_intent`, `affected_areas`, `expected_files`, `constraints`, `acceptance_criteria`, `risks`, `architectural_notes`, `relevant_context_references`, `context_package_metadata`.
2. **`ExecutorHandoff` (Executor → Reviewer):**
   - `task_id`, `implementation_summary`, `files_modified`, `tests_changed`, `verification_passed`, `verification_output`, `diff` (actual unified diff), `relevant_context_references`, `known_limitations`, `warnings`, `runtime_result`, `usage_metrics`.
3. **`ReviewerHandoff` (Reviewer → Human Gate):**
   - `task_id`, `verdict` (`PASS`, `REWORK_REQUIRED`, `BLOCKED`, `FAILED`), `summary`, `feedback`, `criteria_verified`, `diff_inspected`, `defect_details`, `usage_metrics`.

### 15.7 Read Context vs. Write Scope Isolation

> **Critical Governance Invariant:** `ContextEngine` governs **READ CONTEXT ONLY**. Ingesting a file into a `ContextPackage` does **NOT** grant write authority to that file. Write permissions remain strictly bounded by `Task.scope` and enforced fail-closed by `BoundedWorkspaceRuntime`. Any attempt by an executor to modify files outside `Task.scope` raises `ScopeViolationError` regardless of what context was read.

### 15.8 Execution History Integration

`ControlledWorkflowRunner` emits bounded `context_assembled` events to `ExecutionHistoryStore` for each stage:
- Event metadata records `role`, `stage`, `context_version`, `selected_file_count`, `excluded_file_count`, `total_budget`, `used_budget`, `truncated_count`, and `is_truncated`.
- Full file contents, prompt dumps, and complete code diffs are **never** persisted to the history database, preserving strict database bounding rules.

---

## 16. Context Lifecycle & Multi-Turn Context Foundation (TASK-0010)

TASK-0010 extends the JESTER AI Bridge context architecture from a single-pass context collector into a deterministic, multi-stage **Context Lifecycle Engine**. It manages context across stages and rework iterations while strictly isolating current repository truth from historical execution narratives.

```text
TASK (task_id)
  │
  ▼
Context Snapshot A (Architect Stage)
  │
  ▼
Architect Handoff (context_id=A)
  │
  ▼
Context Snapshot B (Executor Stage, parent=A)
  │
  ▼
Runtime Changes & Bounded Execution (writes to disk)
  │
  ▼
Fresh Disk Read + Unified Diff + Test Verification
  │
  ▼
Context Snapshot C (Reviewer Stage, parent=B)
  │
  ▼
Reviewer Evaluation
  ├─ PASS ──> Human Signoff Gate
  │
  └─ REWORK_REQUIRED
       │
       ▼
     Extract Previous Evidence (Reviewer feedback, defects, previous diff)
       │
       ▼
     Context Snapshot D (Rework Executor Stage, parent=C)
       │  (Fresh disk read of current code + bounded historical context)
       │
       ▼
     Executor Rework ──> New Current Diff ──> Reviewer Evaluation
```

### 16.1 Context Snapshot Model

A context snapshot represents an immutable, auditable record of what context was assembled for a specific role and stage at a discrete moment in an execution attempt:

- **Identity & Association:**
  - `context_id`: Unique identifier (`ctx_...`) generated via UUID4.
  - `execution_id`: Identifier of the execution attempt (`exec_...`).
  - `task_id`: Identifier of the business task. `task_id` and `execution_id` are strictly decoupled; one task may have multiple sequential execution attempts with independent context lifecycles.
  - `role`: The active agent role (`architect`, `executor`, `reviewer`).
  - `stage`: The active workflow stage (`architect`, `executor`, `reviewer`, `rework_executor`, `rework_reviewer`).
  - `context_version`: Schema version (`v1`).
- **Lineage:**
  - `parent_context_id`: Link to the preceding context snapshot, establishing an unbroken lineage tree from Architect down to Rework Reviewer without requiring a graph database.
- **Auditing & Metrics:**
  - `created_at`: UTC timestamp of snapshot generation.
  - `selected_file_count`, `excluded_file_count`.
  - `total_budget`, `used_budget`, `truncated_count`, `is_truncated`.
  - `historical_items_count`.
  - `file_freshness_hashes`: Map of repository-relative paths to SHA-256 hashes of the file content at assembly time.
  - `is_stale`: Boolean indicating whether underlying files changed since snapshot creation.

Snapshots store **metadata only**. Raw source code blobs and complete prompts are never stored in snapshot structures or database records.

### 16.2 Static vs. Dynamic Context

Context packages explicitly separate immutable intent from evolving execution state:

1. **Static Context:** Invariant across stages for a given task.
   - Task objective and title.
   - Explicit scope (`task.scope`).
   - Task constraints and boundary rules.
   - Acceptance criteria.
   - Architectural guidelines (`docs/AI_BRIDGE_ARCHITECTURE.md`).
2. **Dynamic Context:** Mutable state assembled per stage.
   - Current repository source files (read directly from disk).
   - Current test files and test results.
   - Current unified diff produced by runtime modifications.
   - Stage verification output.
   - Reviewer feedback and defect lists.
   - Rework objectives and prior implementation summaries.

### 16.3 Current Repository Reality vs. Historical Context

The engine enforces a non-negotiable architectural invariant:

> **Current repository state is the sole authority for code reality. Historical context provides explanation, not truth.**

- **Current Repository Context:**
  - Always read directly from the workspace filesystem at the moment of stage execution.
  - Captured with SHA-256 freshness hashes and modification timestamps (`file_mtime`).
  - Marked with `is_historical=False`.
- **Historical Context:**
  - Includes prior reviewer verdicts, defect lists, previous execution diffs, previous test outputs, and earlier executor summaries.
  - Sourced with `source_type="reviewer_feedback"` or `source_type="historical_execution"`.
  - Explicitly marked with `is_historical=True`.
  - Rendered with clear contextual demarcations (`=== HISTORICAL REWORK CONTEXT ===`, `=== PREVIOUS UNIFIED DIFF (HISTORICAL) ===`) to prevent LLM agents from confusing prior rejected changes with current code.

### 16.4 Freshness Tracking & Stale Context Prevention

To prevent agents from reasoning over obsolete file states:
1. `FileContext` captures `freshness_hash` (SHA-256) and `file_mtime` during assembly.
2. `ContextEngine.check_context_freshness(package, workspace_root)` compares snapshot hashes and timestamps against active disk state.
3. If files have been modified, created, or deleted since assembly, the package is flagged `is_stale=True`.
4. When moving to a subsequent stage (e.g., Executor → Reviewer or Reviewer → Rework Executor), context is **never recycled from an existing in-memory package**. A fresh `ContextPackage` is newly assembled from the filesystem, guaranteeing that the Reviewer inspects the actual files produced by the Executor.

### 16.5 Rework Context Assembly (`assemble_rework_context`)

When the Reviewer issues a `REWORK_REQUIRED` verdict, `assemble_rework_context` produces a dedicated, role-specific package for the Rework Executor containing:

1. **Original Task Specification:** Preserved task objective, scope, and acceptance criteria.
2. **Architect Intent:** Carried over from the initial `ArchitectHandoff`.
3. **Previous Implementation Summary:** Summary from the rejected `ExecutorHandoff`.
4. **Previous Unified Diff:** The rejected diff labeled as historical evidence.
5. **Reviewer Feedback & Defect Details:** The explicit rationale for rejection and specific defects to remediate.
6. **Previous Verification Results:** Test failures or execution errors from the prior attempt.
7. **Current Repository State:** Re-read fresh from the live workspace so that the Rework Executor sees current modifications rather than the pre-execution baseline.
8. **Explicit Rework Objective:** Synthesized directive focusing the agent strictly on fixing identified defects.

### 16.6 Structured Handoff & Context Lineage

Structured handoffs maintain auditable cryptographic pointers to their underlying context snapshots:

```text
Context Snapshot A (ctx_arch)
  │
ArchitectHandoff (context_id="ctx_arch", parent_context_id=None)
  │
Context Snapshot B (ctx_exec, parent_context_id="ctx_arch")
  │
ExecutorHandoff (context_id="ctx_exec", parent_context_id="ctx_arch")
  │
Context Snapshot C (ctx_rev, parent_context_id="ctx_exec")
  │
ReviewerHandoff (context_id="ctx_rev", parent_context_id="ctx_exec", executor_context_id="ctx_exec")
```

Every handoff can be audited back to the exact context state that informed the agent's decisions.

### 16.7 Execution History Integration & Bounded Retrieval

`ExecutionHistoryStore` provides two targeted retrieval methods for multi-turn and rework cycles:
- `get_latest_execution_for_task(task_id) -> Optional[ExecutionRecord]`: Locates the most recent execution attempt for a business task.
- `get_rework_history(execution_id) -> Dict[str, Any]`: Gathers bounded historical metadata from prior review and runtime events:
  - `reviewer_feedback` and `reviewer_verdict`.
  - `defect_details`.
  - `previous_diff_stat` and line change counts (full diffs are omitted).
  - `previous_verification_output` (bounded to first 2,000 characters).
  - `implementation_summary`.

Full repository contents, raw code blobs, and chat logs are never written to the SQLite database.

### 16.8 Security & Sanitization of Historical Context

Historical context, even when retrieved from trusted internal stores, must never leak credentials or violate workspace security:
- **Secret Redaction:** `sanitize_context_text(...)` scrubs bearer tokens, private keys, API keys (`sk-...`, `AIza...`), and environment variable patterns before historical text enters a `ContextPackage`.
- **Protected Paths:** `.env`, `.git/`, `.jester/`, `secrets/`, and private keys remain strictly excluded from file selection.
- **Write Scope Invariance:** Ingesting a file into a `ContextPackage` grants **read context only**. Write permissions remain strictly governed by `Task.scope` and fail-closed runtime validation in `BoundedWorkspaceRuntime`.

---

## 17. Founder Local Interface / Command UI (TASK-0011)

TASK-0011 implements the first local browser-based Founder Interface for the JESTER AI Bridge. It serves as an operational control surface for the developer/founder to interact with the autonomous multi-agent pipeline while preserving the established governance boundaries.

```text
Founder in Browser (http://127.0.0.1:8765)
  │
  ▼
Local Founder Interface (FastAPI Server + HTML/CSS/JS UI)
  │
  ├─ POST /api/tasks ───────────> Task Control Plane (.jester/tasks/)
  │                                     │
  │                               ControlledWorkflowRunner
  │                                     │
  ├─ GET /api/executions ───────> ExecutionHistoryStore (.jester/history.db)
  │
  ├─ GET /api/executions/{id} ──> Stage Events, Diffs & Verification
  │
  ├─ POST /api/.../signoff ─────> Mandatory Human Signoff Gate
  │                                     │
  └─ POST /api/git/push ────────> GitController (Bounded Git Delivery)
```

### 17.1 Architectural Purpose & Invariants

The Founder Local Interface is **a window into the existing Bridge, not a second orchestrator**:
1. **Source of Truth:** The `.jester` task control plane, `ControlledWorkflowRunner`, `ExecutionHistoryStore`, and `GitController` remain the sole authorities for execution, state, and version control.
2. **Mandatory Human Signoff:** The interface provides explicit `[ APPROVE & COMMIT ]` and `[ REJECT / REWORK ]` controls when an execution enters `AWAITING_HUMAN_SIGNOFF`. Reviewer PASS is never treated as human approval. Zero automatic commits or pushes are permitted.
3. **Local-First & Offline:** Powered by FastAPI (`jester_bridge/server.py`) and a self-contained single-page application (`jester_bridge/ui/index.html`). Requires no cloud SaaS backend, no hosted database, and zero external build tooling.

### 17.2 API Integration Boundary

The server exposes a minimal, bounded REST API at `/api`:
- **`POST /api/tasks`**: Accepts natural-language requests, initializes `Task` specification, and launches `ControlledWorkflowRunner.run_e2e_workflow(...)`.
- **`GET /api/tasks`**: Lists all tasks categorized by `.jester/tasks/` folders (`inbox`, `active`, `review`, `completed`, `blocked`).
- **`GET /api/tasks/{task_id}`**: Retrieves specific task JSON definitions.
- **`GET /api/executions`**: Queries persistent execution history (`limit=50`).
- **`GET /api/executions/{execution_id}`**: Returns full execution details, chronological events, token observability, verification output, and structured handoffs.
- **`GET /api/executions/{execution_id}/diff`**: Returns the unified diff generated by runtime modifications.
- **`GET /api/executions/{execution_id}/context`**: Returns role-aware context snapshot metadata, budget utilization, file freshness hashes, and provenance (strictly secret-redacted).
- **`POST /api/executions/{execution_id}/signoff`**: Processes explicit human decision (`approve` or `reject`). If approved with commit parameters, triggers controlled Git delivery.
- **`POST /api/executions/{execution_id}/rework`**: Triggers a controlled rework cycle (`run_rework_cycle`) with fresh workspace context.
- **`GET /api/git/status`**: Queries workspace Git status via `GitController.inspect_status()`.
- **`POST /api/git/push`**: Executes explicit, authorized Git push via `GitController.push(...)`.

### 17.3 Operational Control Surface UI Areas

The browser interface (`jester_bridge/ui/index.html`) is structured into focused operational areas:
1. **Founder Task Intake:** Natural-language request input with optional task ID and scope overrides. Dispatches immediately to the Bridge.
2. **Current Execution Overview:** Prominent status badge, active stage, assigned role, agent, provider, model, token usage, and execution elapsed time.
3. **Lifecycle Timeline:** Step-by-step progress visualizer tracking `Task` -> `Architect` -> `Executor` -> `Verify` -> `Review` -> `Signoff` -> `Git`.
4. **Human Signoff Gate Banner:** Prominently rendered when an execution reaches `AWAITING_HUMAN_SIGNOFF`, warning that human authorization is required and providing `[ APPROVE & COMMIT ]` and `[ REJECT / REWORK ]` dialogs.
5. **Tabbed Inspection Workspace:**
   - *Unified Diff:* Visual syntax-highlighted code diff with line additions and deletions.
   - *Verification:* Test command execution result and console stdout/stderr.
   - *Reviewer Decision:* Independent Reviewer verdict (`PASS`, `REWORK_REQUIRED`, `BLOCKED`, `FAILED`), summary, and defect details.
   - *Structured Handoffs:* Inspection of `ArchitectHandoff`, `ExecutorHandoff`, and `ReviewerHandoff`.
   - *Context Inspector:* Snapshot ID, parent context ID, character budget allocation, file counts, and provenance audit log.
   - *Git Delivery:* Commit hash, target branch, pushed status, and explicit remote push trigger.
   - *Event Log:* Chronological log of timestamped execution events.
6. **Execution History Sidebar:** Interactive list of historical executions with live polling during running executions.

### 17.4 Local Startup Commands

The Founder Local Interface can be launched locally on any developer machine:

```bash
# Recommended launcher (opens browser automatically at http://127.0.0.1:8765)
.venv\Scripts\python.exe scripts/run_founder_ui.py

# Specify custom port without auto-opening browser
.venv\Scripts\python.exe scripts/run_founder_ui.py --port 8765 --no-browser

# Alternatively via Uvicorn directly
.venv\Scripts\python.exe -m uvicorn jester_bridge.server:app --port 8765
```

---

## 18. Multi-Runtime & Multi-Account Architecture (TASK-0013)

TASK-0013 evolves the JESTER AI Bridge from a provider/API-oriented architecture into a provider-neutral, runtime-neutral AI orchestration layer capable of using multiple authenticated AI runtimes and accounts while preserving the Task Control Plane, security boundaries, Human Signoff, Context Engine, Persistent Execution History, Verification, and GitController.

```text
ROLE
  ↓ (Operational responsibility & required capabilities)
AGENT
  ↓ (Configured logical worker identity & declared capabilities)
PROVIDER
  ↓ (Vendor integration adapter: google, openai, anthropic, ollama)
RUNTIME
  ↓ (Execution engine: API, CLI, or Local daemon)
ACCOUNT / CREDENTIAL
  ↓ (Authenticated tenant/identity: account-a, account-b, local)
MODEL
    (Concrete checkpoint: gemini-2.5-pro, gpt-4o, qwen2.5:7b)
```

### 18.1 The 6-Tier Abstraction Hierarchy

1. **Role (`Role`):** Operational role (`architect`, `executor`, `reviewer`, `auditor`).
2. **Agent (`AgentProfile`):** Configured logical worker profile.
3. **Provider (`AgentProvider`):** Logical vendor integration (`google`, `openai`, `anthropic`, `ollama`).
4. **Runtime (`RuntimeEntry`):** Concrete execution mechanism (`api`, `cli`, `local`).
5. **Account Identity (`AccountIdentity`):** Tenant/identity reference (`account-a`, `account-b`, `local`) with isolated authentication references.
6. **Model:** Concrete checkpoint or checkpoint series.

### 18.2 Runtime Types & Authentication Mechanisms

The Bridge explicitly distinguishes three execution and authentication models:
- **API Runtime (`RuntimeType.API`):** Remote HTTP/REST or SDK calls authenticated via API keys (`AuthType.API_KEY`) or environment variables (`AuthType.ENV_VAR`).
- **CLI Runtime (`RuntimeType.CLI`):** Local CLI processes (`gemini`, `codex`, `claude`) authenticated via named CLI profiles (`AuthType.CLI_PROFILE`), user sessions (`AuthType.SESSION`), or system tokens.
- **Local Runtime (`RuntimeType.LOCAL`):** Self-hosted daemons (e.g. Ollama running on `http://127.0.0.1:11434`) requiring no credentials (`AuthType.NONE`).

### 18.3 Dynamic Multi-Account Catalog (Zero-Code Scaling)

Multi-account support is configuration/data-driven rather than hardcoded logic. The system does not employ conditional statements like `if account == "gemini_a": ... elif account == "gemini_b": ...`.
Instead, multiple accounts for a provider are registered dynamically in the `RuntimeRegistry`:
```python
registry.register_runtime(
    RuntimeEntry(
        runtime_id="gemini-cli-acc-a",
        provider_id="google",
        runtime_type=RuntimeType.CLI,
        account=AccountIdentity(
            account_id="account-a",
            label="Google AI Pro Account A",
            provider="google",
            auth_ref=AuthReference(auth_type=AuthType.CLI_PROFILE, profile_name="gemini-team-a"),
        ),
        model="gemini-2.5-pro",
        capabilities={"code_generation", "code_editing", "reasoning"},
        priority=10,
    )
)
```
Adding `account-c`, `account-d`, or future accounts requires only registry registration or configuration entry; zero orchestration code modifications are required.

### 18.4 Runtime Readiness & Availability States

Runtimes report dynamic readiness (`RuntimeReadiness`) across 8 standardized states:
- `READY`: Online and capable of accepting tasks.
- `UNAVAILABLE`: Temporarily or permanently unavailable.
- `AUTH_REQUIRED`: Missing credentials or expired session.
- `RATE_LIMITED`: Actively rate-limited.
- `QUOTA_EXHAUSTED`: Quota exhausted (e.g. daily token cap reached).
- `OFFLINE`: Daemon or service unreachable.
- `CAPABILITY_MISMATCH`: Does not satisfy task capability requirements.
- `ERROR`: Runtime error during preflight check.

### 18.5 Deterministic Routing & Fallback

The `RuntimeRouter` deterministically selects candidate runtimes by filtering:
1. Provider match (if requested).
2. Runtime type match (if requested).
3. Account ID match (if requested).
4. Capability subset match: `task.required_capabilities ⊆ runtime.capabilities`.
5. Readiness preflight: Evaluates `runtime.check_readiness()` in priority order.

When an account is unavailable (e.g. `QUOTA_EXHAUSTED`), the router records a `FallbackEvent` and seamlessly promotes the next highest-priority ready candidate (e.g. `account-b`). If all candidates fail, routing **fails closed** with an actionable, sanitized reason; silent mock fallback is strictly prohibited.

### 18.6 Generic Adapters

- **`CLIRuntimeAdapter` (`jester_bridge/adapters.py`):** Safely executes CLI tools with an executable allowlist (`{"gemini", "codex", "claude"}`), explicit argument vectors (never `shell=True`), timeout containment, and standardized stdout/stderr parsing.
- **`LocalRuntimeAdapter` (`jester_bridge/adapters.py`):** Interfaces with local Ollama instances (`http://127.0.0.1:11434`), checks daemon connectivity and model availability, and handles offline states cleanly.

### 18.7 Security Invariants & Redaction

- **No Raw Credentials:** `AuthReference` strictly rejects raw credentials or secret values matching API key patterns (`sk-...`, `AIza...`).
- **Context Isolation:** Secrets, tokens, and CLI sessions never enter `InvocationRequest.payload`, `ContextPackage`, `Task` specifications, or task reports.
- **Execution History:** Runtime IDs, account IDs, and routing reasons are persisted in `.jester/history.db` metadata; raw credentials and authentication tokens are never stored.

### 18.8 Founder UI & REST API Exposure

The Founder Local Interface exposes the active runtime registry and readiness via `GET /api/runtimes`, allowing operators to inspect available accounts, runtime types, models, priorities, and readiness statuses in real time.
