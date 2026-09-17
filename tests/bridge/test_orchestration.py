"""
Unit and Integration Tests for BridgeOrchestrator (Phase 2C-1).

Verifies:
- Architect stage resolution and task specification generation
- Executor stage execution and .jester task lifecycle integration
- Reviewer stage independent evaluation and verdict parsing
- Complete multi-agent pipeline: Architect (OpenAI) -> Executor (Google) -> Reviewer (OpenAI)
- Provider swappability across the orchestration layer
- Rework flow: Reviewer REWORK_REQUIRED -> Executor -> Reviewer PASS
- Max rework cycles threshold enforcement (blocks infinite retry loops)
- Invalid transition rejections (e.g. ARCHITECT -> REVIEWER, EXECUTOR -> COMPLETED)
- Mandatory human sign-off boundary (Reviewer PASS halts at AWAITING_HUMAN_SIGNOFF)
- Provider failure handling (halts pipeline cleanly)
- Capability preflight enforcement during orchestrated stages
- Zero leakage of provider-specific response objects across handoffs
"""
from unittest.mock import MagicMock
import pytest

from jester_bridge.contracts import (
    InvocationRequest,
    InvocationResult,
    InvocationStatus,
)
from jester_bridge.core import BridgeCore, CapabilityMismatchError
from jester_bridge.config import BridgeConfig
from jester_bridge.agent import AgentProfile
from jester_bridge.protocol import Task
from jester_bridge.roles import Role
from jester_bridge.testing import MockProviderA, MockProviderB
from jester_bridge.openai_provider import OpenAIProvider
from jester_bridge.google_provider import GoogleProvider
from jester_bridge.orchestration import (
    BridgeOrchestrator,
    OrchestrationStage,
    ReviewVerdict,
    ArchitectInput,
    InvalidTransitionError,
)


def _setup_multi_provider_core(
    arch_summary="Task specification created.",
    exec_summary="Code implementation completed.",
    rev_summary="Review verdict: PASS. All criteria met.",
):
    """Sets up BridgeCore with mocked OpenAI and Google providers."""
    # Mock OpenAI client
    mock_openai_resp = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = arch_summary
    mock_choice.finish_reason = "stop"
    mock_openai_resp.choices = [mock_choice]
    mock_openai_resp.model = "o3-mini"
    mock_openai_resp.id = "openai-arch-mock"
    mock_openai_resp.usage = MagicMock(prompt_tokens=40, completion_tokens=30, total_tokens=70)
    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.return_value = mock_openai_resp
    openai_provider = OpenAIProvider(api_key="mock-openai", client=mock_openai_client)

    # Mock Google client
    mock_google_http = MagicMock()
    mock_google_http.status_code = 200
    mock_google_http.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": exec_summary}]}}],
        "usageMetadata": {"promptTokenCount": 50, "candidatesTokenCount": 25, "totalTokenCount": 75},
    }
    mock_google_client = MagicMock()
    mock_google_client.post.return_value = mock_google_http
    google_provider = GoogleProvider(api_key="mock-google", client=mock_google_client)

    config = BridgeConfig(
        role_bindings={
            "architect": "chatgpt-lead",
            "executor": "gemini-dev",
            "reviewer": "chatgpt-critic",
        },
        agents={
            "chatgpt-lead": AgentProfile(
                id="chatgpt-lead",
                role="architect",
                provider="openai",
                model="o3-mini",
                capabilities={"planning", "reasoning", "repository_read"},
            ),
            "gemini-dev": AgentProfile(
                id="gemini-dev",
                role="executor",
                provider="google",
                model="gemini-2.5-pro",
                capabilities={"planning", "reasoning", "code_generation", "repository_read"},
            ),
            "chatgpt-critic": AgentProfile(
                id="chatgpt-critic",
                role="reviewer",
                provider="openai",
                model="gpt-4o",
                capabilities={"reasoning", "repository_read", "review"},
            ),
        },
    )

    core = BridgeCore(config=config, providers={"openai": openai_provider, "google": google_provider})
    return core, openai_provider, google_provider, mock_choice, mock_google_http


def test_orchestration_complete_pipeline_with_human_signoff():
    """
    Validates complete multi-agent pipeline:
    Architect (OpenAI) -> Executor (Google) -> Reviewer (OpenAI) -> Human Sign-off -> Completed.
    """
    core, openai_prov, google_prov, mock_openai_choice, _ = _setup_multi_provider_core()
    orchestrator = BridgeOrchestrator(core=core)

    initial_task = Task(id="TASK-PIPE-01", title="Pipeline Feature")
    session = orchestrator.create_session(task=initial_task)
    assert session.current_stage == OrchestrationStage.PENDING

    # 1. ARCHITECT STAGE
    arch_input = ArchitectInput(
        intent="Implement deterministic scoring function",
        target_task_id="TASK-PIPE-01",
    )
    session = orchestrator.run_architect_stage(session, arch_input)
    assert session.current_stage == OrchestrationStage.ARCHITECT
    assert session.architect_result is not None
    assert session.task.status == "inbox"
    assert session.task.role == Role.EXECUTOR.value

    # 2. EXECUTOR STAGE
    session = orchestrator.run_executor_stage(session)
    assert session.current_stage == OrchestrationStage.EXECUTOR
    assert session.executor_result is not None
    assert session.executor_result.status == InvocationStatus.SUCCESS
    assert session.task.status == "active"

    # 3. REVIEWER STAGE
    mock_openai_choice.message.content = "Review verdict: PASS. Code strictly satisfies acceptance criteria."
    session = orchestrator.run_reviewer_stage(session, verification_output="pytest passed: 10/10")
    # Crucial assertion: Reviewer PASS must halt at AWAITING_HUMAN_SIGNOFF!
    assert session.current_stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert session.review_result is not None
    assert session.review_result.verdict == ReviewVerdict.PASS
    assert session.task.status == "review"

    # 4. HUMAN SIGN-OFF
    session = orchestrator.approve_human_signoff(
        session, approver="lead-dev", notes="Verified independently. Approved for merge."
    )
    assert session.current_stage == OrchestrationStage.COMPLETED
    assert session.task.status == "completed"
    assert session.human_signoff_by == "lead-dev"


def test_orchestration_rework_flow():
    """
    Validates the rework flow:
    Executor -> Reviewer (REWORK_REQUIRED) -> Executor -> Reviewer (PASS) -> Awaiting Signoff.
    """
    core, openai_prov, google_prov, mock_openai_choice, _ = _setup_multi_provider_core()
    orchestrator = BridgeOrchestrator(core=core, max_rework_cycles=2)

    task = Task(
        id="TASK-REWORK-01",
        title="Rework Task",
        role=Role.EXECUTOR.value,
        required_capabilities={"code_generation", "reasoning"},
    )
    session = orchestrator.create_session(task=task)

    # Initial execution
    session = orchestrator.run_executor_stage(session)
    assert session.current_stage == OrchestrationStage.EXECUTOR

    # Reviewer requests rework
    mock_openai_choice.message.content = "Review verdict: REWORK_REQUIRED. Missing edge-case validation."
    session = orchestrator.run_reviewer_stage(session)
    assert session.current_stage == OrchestrationStage.REWORK_REQUIRED
    assert session.rework_count == 1
    assert session.review_result.verdict == ReviewVerdict.REWORK_REQUIRED

    # Re-execution (executor addresses rework feedback)
    session = orchestrator.run_executor_stage(session)
    assert session.current_stage == OrchestrationStage.EXECUTOR

    # Reviewer passes after rework
    mock_openai_choice.message.content = "Review verdict: PASS. Edge cases resolved."
    session = orchestrator.run_reviewer_stage(session)
    assert session.current_stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF
    assert session.review_result.verdict == ReviewVerdict.PASS


def test_orchestration_max_rework_exceeded_blocks_task():
    """
    Validates that exceeding max rework cycles marks session and task as BLOCKED,
    preventing infinite retry loops.
    """
    core, openai_prov, google_prov, mock_openai_choice, _ = _setup_multi_provider_core()
    orchestrator = BridgeOrchestrator(core=core, max_rework_cycles=1)  # Only 1 rework allowed

    task = Task(
        id="TASK-LIMIT-01",
        title="Limited Rework Task",
        role=Role.EXECUTOR.value,
        required_capabilities={"code_generation", "reasoning"},
    )
    session = orchestrator.create_session(task=task)

    # Cycle 1: Execute -> Rework
    session = orchestrator.run_executor_stage(session)
    mock_openai_choice.message.content = "Review: REWORK_REQUIRED (attempt 1)"
    session = orchestrator.run_reviewer_stage(session)
    assert session.current_stage == OrchestrationStage.REWORK_REQUIRED
    assert session.rework_count == 1

    # Cycle 2: Execute -> Rework again (exceeds threshold)
    session = orchestrator.run_executor_stage(session)
    mock_openai_choice.message.content = "Review: REWORK_REQUIRED (attempt 2)"
    session = orchestrator.run_reviewer_stage(session)

    # Exceeded max_rework_cycles=1 -> BLOCKED
    assert session.current_stage == OrchestrationStage.BLOCKED
    assert session.task.status == "blocked"
    assert "Exceeded maximum rework cycles" in (session.task.blocked_reason or "")


def test_orchestration_invalid_transitions():
    """Validates that unauthorized or illegal stage transitions are rejected."""
    core, _, _, _, _ = _setup_multi_provider_core()
    orchestrator = BridgeOrchestrator(core=core)

    task = Task(id="TASK-INVALID-01", title="Invalid Transition Test")
    session = orchestrator.create_session(task=task)

    # Illegal: Attempting REVIEWER directly from PENDING (skipping executor)
    with pytest.raises(InvalidTransitionError, match="Executor stage must complete"):
        orchestrator.run_reviewer_stage(session)

    # Illegal: Attempting human signoff approval from PENDING
    with pytest.raises(InvalidTransitionError, match="Cannot approve human signoff"):
        orchestrator.approve_human_signoff(session, approver="dev")


def test_orchestration_provider_swappability():
    """
    Acceptance Criteria Test:
    Proves that the entire orchestration pipeline works identically when providers are swapped:
    Pipeline A: Architect (OpenAI) -> Executor (Google) -> Reviewer (OpenAI)
    Pipeline B: Architect (Google) -> Executor (OpenAI) -> Reviewer (Google)
    With zero code changes in BridgeOrchestrator!
    """
    # 1. Setup mock providers
    from jester_bridge.testing import BaseMockProvider
    provider_openai = BaseMockProvider(provider_id="openai", default_summary="OpenAI summary")
    provider_google = BaseMockProvider(provider_id="google", default_summary="Google summary")

    # --- PIPELINE A ---
    config_a = BridgeConfig(
        role_bindings={"architect": "agent-oa", "executor": "agent-go", "reviewer": "agent-oa"},
        agents={
            "agent-oa": AgentProfile(id="agent-oa", role="architect", provider="openai", capabilities={"planning", "reasoning", "review", "code_generation"}),
            "agent-go": AgentProfile(id="agent-go", role="executor", provider="google", capabilities={"planning", "reasoning", "review", "code_generation"}),
        },
    )
    core_a = BridgeCore(config=config_a, providers={"openai": provider_openai, "google": provider_google})
    orchestrator_a = BridgeOrchestrator(core=core_a)

    task_a = Task(id="TASK-SWAP-A", title="Swap Task A", role="executor", required_capabilities={"code_generation", "reasoning"})
    session_a = orchestrator_a.create_session(task=task_a)
    session_a = orchestrator_a.run_architect_stage(session_a, ArchitectInput(intent="Decompose A"))
    assert session_a.architect_result.raw_result.provider == "openai"
    session_a = orchestrator_a.run_executor_stage(session_a)
    assert session_a.executor_result.raw_result.provider == "google"
    session_a = orchestrator_a.run_reviewer_stage(session_a)
    assert session_a.review_result.raw_result.provider == "openai"

    # --- PIPELINE B (SWAPPED ROLES) ---
    config_b = BridgeConfig(
        role_bindings={"architect": "agent-go", "executor": "agent-oa", "reviewer": "agent-go"},
        agents={
            "agent-oa": AgentProfile(id="agent-oa", role="executor", provider="openai", capabilities={"planning", "reasoning", "review", "code_generation"}),
            "agent-go": AgentProfile(id="agent-go", role="architect", provider="google", capabilities={"planning", "reasoning", "review", "code_generation"}),
        },
    )
    core_b = BridgeCore(config=config_b, providers={"openai": provider_openai, "google": provider_google})
    orchestrator_b = BridgeOrchestrator(core=core_b)

    task_b = Task(id="TASK-SWAP-B", title="Swap Task B", role="executor", required_capabilities={"code_generation", "reasoning"})
    session_b = orchestrator_b.create_session(task=task_b)
    session_b = orchestrator_b.run_architect_stage(session_b, ArchitectInput(intent="Decompose B"))
    assert session_b.architect_result.raw_result.provider == "google"  # Swapped to Google!
    session_b = orchestrator_b.run_executor_stage(session_b)
    assert session_b.executor_result.raw_result.provider == "openai"  # Swapped to OpenAI!
    session_b = orchestrator_b.run_reviewer_stage(session_b)
    assert session_b.review_result.raw_result.provider == "google"  # Swapped to Google!


def test_orchestration_provider_failure_halts_pipeline():
    """Validates that a provider execution failure marks stage FAILED and halts progression."""
    core, openai_prov, google_prov, _, mock_google_http = _setup_multi_provider_core()
    # Force executor provider failure (HTTP 500)
    mock_google_http.status_code = 500
    mock_google_http.text = "Internal Server Error"

    orchestrator = BridgeOrchestrator(core=core)
    task = Task(id="TASK-FAIL-01", title="Fail Task", role="executor", required_capabilities={"code_generation", "reasoning"})
    session = orchestrator.create_session(task=task)

    session = orchestrator.run_executor_stage(session)
    assert session.current_stage == OrchestrationStage.FAILED
    assert session.executor_result.status == InvocationStatus.FAILED

    # Attempting reviewer from FAILED must be rejected
    with pytest.raises(InvalidTransitionError):
        orchestrator.run_reviewer_stage(session)


def test_orchestration_capability_failure_halts():
    """Validates that a capability preflight failure raises CapabilityMismatchError and halts progression."""
    core, _, _, _, _ = _setup_multi_provider_core()
    orchestrator = BridgeOrchestrator(core=core)

    # Task requiring a capability not supported by gemini-dev (e.g. "quantum_computing")
    task = Task(
        id="TASK-UNSUPPORTED",
        title="Unsupported Capability Task",
        role="executor",
        required_capabilities={"quantum_computing"},
    )
    session = orchestrator.create_session(task=task)

    with pytest.raises(CapabilityMismatchError, match="quantum_computing"):
        orchestrator.run_executor_stage(session)


def test_orchestration_human_signoff_rejection():
    """Validates that human rejection transitions task back to REWORK_REQUIRED."""
    core, _, _, mock_openai_choice, _ = _setup_multi_provider_core()
    orchestrator = BridgeOrchestrator(core=core, max_rework_cycles=2)

    task = Task(id="TASK-REJECT-01", title="Human Rejection Test", role="executor", required_capabilities={"code_generation", "reasoning"})
    session = orchestrator.create_session(task=task)
    session = orchestrator.run_executor_stage(session)
    mock_openai_choice.message.content = "Review verdict: PASS."
    session = orchestrator.run_reviewer_stage(session)
    assert session.current_stage == OrchestrationStage.AWAITING_HUMAN_SIGNOFF

    # Human rejects the work
    session = orchestrator.reject_human_signoff(session, rejector="lead-dev", reason="Scope too broad.")
    assert session.current_stage == OrchestrationStage.REWORK_REQUIRED
    assert session.rework_count == 1
    assert "lead-dev" in (session.human_signoff_by or "")


def test_orchestration_no_provider_specific_data_leakage():
    """Verifies that all handoff contracts expose only normalized, provider-neutral fields."""
    core, _, _, _, _ = _setup_multi_provider_core()
    orchestrator = BridgeOrchestrator(core=core)

    task = Task(id="TASK-LEAK-01", title="Leak Test", role="executor", required_capabilities={"code_generation", "reasoning"})
    session = orchestrator.create_session(task=task)
    session = orchestrator.run_executor_stage(session)

    # Inspect ExecutorResult contract
    assert session.executor_result is not None
    assert not hasattr(session.executor_result, "choices")
    assert not hasattr(session.executor_result, "candidates")
    assert isinstance(session.executor_result.files_modified, list)
    assert isinstance(session.executor_result.summary, str)
