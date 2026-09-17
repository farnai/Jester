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
