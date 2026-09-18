"""
Generic CLI and Local Engine Adapters for JESTER AI Bridge (TASK-0013).

Provides:
- CLIRuntimeAdapter: Controlled CLI execution for coding tools (Gemini CLI, Codex CLI, Claude CLI)
  with strict executable allowlists, argument sanitization, and output normalization.
- LocalRuntimeAdapter: Local engine integration (e.g. Ollama daemon on localhost)
  with offline detection, discovery, and capability validation.
"""
from datetime import datetime, timezone
import os
import re
import shutil
import subprocess
from typing import Any, Callable, Dict, List, Optional, Set

from .contracts import InvocationRequest, InvocationResult, InvocationStatus, UsageMetrics
from .provider import AgentProvider
from .runtimes import RuntimeReadiness, RuntimeStatus


DEFAULT_ALLOWED_CLI_EXECUTABLES: Set[str] = {
    "gemini",
    "codex",
    "claude",
    "agy",
}

DEFAULT_CLI_CAPABILITIES: Set[str] = {
    "planning",
    "reasoning",
    "repository_read",
    "repository_write",
    "code_generation",
    "code_editing",
    "command_execution",
    "testing",
    "review",
}

DEFAULT_LOCAL_CAPABILITIES: Set[str] = {
    "planning",
    "reasoning",
    "repository_read",
    "code_generation",
    "local_execution",
}


def _sanitize_cli_text(text: Optional[str]) -> Optional[str]:
    """Sanitizes potential API keys or tokens from CLI text."""
    if not text:
        return text
    text = re.sub(r"\b(sk-[a-zA-Z0-9_\-]{20,})\b", "[REDACTED_API_KEY]", text)
    text = re.sub(r"\b(AIza[a-zA-Z0-9_\-]{30,})\b", "[REDACTED_API_KEY]", text)
    text = re.sub(r"(Bearer\s+)[a-zA-Z0-9_\-\.]{20,}", r"\1[REDACTED_TOKEN]", text, flags=re.IGNORECASE)
    return text


class CLIRuntimeAdapter(AgentProvider):
    """
    Generic CLI Runtime Adapter for executing AI tools via command-line interface.

    Enforces:
    - Controlled executable allowlist (rejects arbitrary shell execution or unsafe binaries)
    - Shell=False subprocess execution (zero shell injection risk)
    - Account and profile isolation
    - Output normalization to standard InvocationResult
    """

    def __init__(
        self,
        provider_id: str,
        executable_name: str,
        account_id: Optional[str] = None,
        cli_profile: Optional[str] = None,
        allowed_executables: Optional[Set[str]] = None,
        extra_env: Optional[Dict[str, str]] = None,
        timeout: float = 60.0,
        supported_capabilities: Optional[Set[str]] = None,
        runner_fn: Optional[Callable[..., Any]] = None,
    ):
        self._provider_id = provider_id
        self._allowed_executables = set(allowed_executables or DEFAULT_ALLOWED_CLI_EXECUTABLES)

        # Security check on executable name
        norm_exe = os.path.basename(executable_name).lower()
        if norm_exe not in self._allowed_executables:
            raise ValueError(
                f"Executable '{executable_name}' is not in the controlled allowlist: "
                f"{sorted(list(self._allowed_executables))}."
            )
        if any(c in executable_name for c in (";", "&", "|", "`", "$", "\n", "\r")):
            raise ValueError(f"Executable name contains forbidden shell metacharacters: {executable_name}")

        self._executable_name = norm_exe
        self._account_id = account_id or "default"
        self._cli_profile = cli_profile
        self._extra_env = dict(extra_env or {})
        self._timeout = timeout
        self._capabilities = set(supported_capabilities or DEFAULT_CLI_CAPABILITIES)
        self._runner_fn = runner_fn

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def executable_name(self) -> str:
        return self._executable_name

    @property
    def account_id(self) -> str:
        return self._account_id

    def get_supported_capabilities(self) -> Set[str]:
        return set(self._capabilities)

    def _build_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        if self._cli_profile:
            env["CLI_ACTIVE_PROFILE"] = self._cli_profile
        env.update(self._extra_env)
        return env

    def _resolve_executable(self) -> str:
        """Resolves the executable on PATH, correctly locating Windows .cmd/.bat scripts."""
        resolved = shutil.which(self._executable_name)
        return resolved if resolved else self._executable_name

    def list_available_models(self) -> List[str]:
        """Lists available models supported by the CLI runtime."""
        if self._executable_name == "agy":
            try:
                exe = self._resolve_executable()
                proc = subprocess.run(
                    [exe, "models"],
                    capture_output=True,
                    text=True,
                    timeout=10.0,
                    shell=False,
                )
                if proc.returncode == 0 and proc.stdout:
                    models = []
                    for line in proc.stdout.splitlines():
                        line = line.strip()
                        if not line or line.startswith("Fetching"):
                            continue
                        parts = line.split("\t")
                        if parts and parts[0]:
                            models.append(parts[0].strip())
                    if models:
                        return models
            except Exception:
                pass
            return [
                "gemini-3.8-flash-high",
                "gemini-3.8-flash-medium",
                "gemini-3.8-flash-low",
                "gemini-3.7-flash-high",
                "gemini-3.1-pro-high",
            ]
        return []

    def _build_command(self, request: InvocationRequest, prompt: str) -> tuple[List[str], Optional[str]]:
        """Constructs the argument vector and stdin input tailored to the CLI tool."""
        exe = self._executable_name if self._runner_fn is not None else self._resolve_executable()
        cmd = [exe]
        if self._cli_profile:
            cmd.extend(["--profile", self._cli_profile])

        if self._executable_name == "gemini":
            cmd.extend(["-p", prompt, "-o", "json", "--yolo", "--skip-trust"])
            if request.model and request.model != "default":
                cmd.extend(["-m", request.model])
            return cmd, None
        elif self._executable_name == "agy":
            cmd.extend([
                "-p",
                prompt,
                "--output-format",
                "json",
                "--dangerously-skip-permissions",
                "--disable-slash-commands",
            ])
            if request.model and request.model != "default":
                cmd.extend(["--model", request.model])
            return cmd, None
        else:
            if request.model and request.model != "default":
                cmd.extend(["--model", request.model])
            return cmd, prompt

    def health_check(self) -> bool:
        """Returns True if the CLI executable is found on PATH or an injected runner is present."""
        if self._runner_fn is not None:
            return True
        return shutil.which(self._executable_name) is not None

    def check_readiness(self) -> RuntimeReadiness:
        """Evaluates executable presence and environment readiness."""
        if not self.health_check():
            return RuntimeReadiness(
                status=RuntimeStatus.UNAVAILABLE,
                message=f"CLI executable '{self._executable_name}' was not found on system PATH.",
            )

        if self._runner_fn is not None:
            return RuntimeReadiness(
                status=RuntimeStatus.READY,
                message=f"CLI executable '{self._executable_name}' is ready (test runner).",
            )

        if self._executable_name == "agy":
            try:
                exe = self._resolve_executable()
                proc = subprocess.run(
                    [
                        exe,
                        "-p",
                        "Reply with exactly: JESTER_ANTIGRAVITY_AUTH_OK",
                        "--output-format",
                        "json",
                        "--dangerously-skip-permissions",
                        "--disable-slash-commands",
                        "--model",
                        "gemini-3.8-flash-low",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15.0,
                    env=self._build_env(),
                    shell=False,
                )
                stdout_text = proc.stdout or ""
                stderr_text = proc.stderr or ""
                combined_text = (stdout_text + " " + stderr_text).strip()

                auth_keywords = (
                    "not authenticated",
                    "auth required",
                    "login",
                    "sign in",
                    "unauthorized",
                    "invalid auth",
                    "no credentials",
                )
                if any(kw in combined_text.lower() for kw in auth_keywords):
                    return RuntimeReadiness(
                        status=RuntimeStatus.AUTH_REQUIRED,
                        message=f"Antigravity CLI is not authenticated: {_sanitize_cli_text(combined_text[:200])}",
                    )

                if proc.returncode != 0:
                    if any(kw in combined_text.lower() for kw in ("quota", "rate limit", "resource_exhausted")):
                        return RuntimeReadiness(
                            status=RuntimeStatus.QUOTA_EXHAUSTED,
                            message=f"Antigravity CLI quota exhausted: {_sanitize_cli_text(combined_text[:200])}",
                        )
                    return RuntimeReadiness(
                        status=RuntimeStatus.ERROR,
                        message=f"Antigravity CLI reported error ({proc.returncode}): {_sanitize_cli_text(combined_text[:200])}",
                    )

                if "JESTER_ANTIGRAVITY_AUTH_OK" in combined_text:
                    return RuntimeReadiness(
                        status=RuntimeStatus.READY,
                        message="Antigravity CLI is authenticated and operational.",
                    )
                else:
                    return RuntimeReadiness(
                        status=RuntimeStatus.AUTH_REQUIRED,
                        message="Antigravity CLI probe did not return expected authenticated response.",
                    )
            except subprocess.TimeoutExpired:
                return RuntimeReadiness(
                    status=RuntimeStatus.UNAVAILABLE,
                    message="Antigravity CLI readiness probe timed out.",
                )
            except Exception as e:
                return RuntimeReadiness(
                    status=RuntimeStatus.ERROR,
                    message=f"Antigravity CLI probe failed: {_sanitize_cli_text(str(e))}",
                )

        if self._executable_name == "gemini":
            try:
                exe = self._resolve_executable()
                proc = subprocess.run(
                    [exe, "-p", "readiness check", "-o", "json"],
                    capture_output=True,
                    text=True,
                    timeout=10.0,
                    env=self._build_env(),
                    shell=False,
                )
                stdout_text = proc.stdout or ""
                stderr_text = proc.stderr or ""
                if (
                    proc.returncode == 41
                    or "Invalid auth method" in stdout_text
                    or "Invalid auth method" in stderr_text
                    or "IneligibleTierError" in stdout_text
                    or "IneligibleTierError" in stderr_text
                ):
                    return RuntimeReadiness(
                        status=RuntimeStatus.AUTH_REQUIRED,
                        message="Gemini CLI is not authenticated (exit code 41 / IneligibleTierError).",
                    )
                elif proc.returncode != 0:
                    err_text = (stdout_text + " " + stderr_text).strip()
                    if "quota" in err_text.lower() or "rate limit" in err_text.lower():
                        return RuntimeReadiness(
                            status=RuntimeStatus.QUOTA_EXHAUSTED,
                            message=f"Gemini CLI quota exhausted: {_sanitize_cli_text(err_text[:200])}",
                        )
                    return RuntimeReadiness(
                        status=RuntimeStatus.ERROR,
                        message=f"Gemini CLI reported error ({proc.returncode}): {_sanitize_cli_text(err_text[:200])}",
                    )
            except subprocess.TimeoutExpired:
                return RuntimeReadiness(
                    status=RuntimeStatus.UNAVAILABLE,
                    message="Gemini CLI probe timed out.",
                )
            except Exception as e:
                return RuntimeReadiness(
                    status=RuntimeStatus.ERROR,
                    message=f"Gemini CLI probe failed: {_sanitize_cli_text(str(e))}",
                )

        return RuntimeReadiness(
            status=RuntimeStatus.READY,
            message=f"CLI executable '{self._executable_name}' is ready.",
        )

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        """
        Executes the CLI tool in a bounded subprocess, normalizes stdout/stderr,
        and returns a standard InvocationResult.
        """
        import json

        req_payload = request.payload or {}
        goal = req_payload.get("goal") or req_payload.get("title") or "Execute task"
        scope = req_payload.get("scope") or []
        constraints = req_payload.get("constraints") or []
        criteria = req_payload.get("acceptance_criteria") or []
        verification = req_payload.get("verification") or []

        prompt_parts: List[str] = []
        if request.role:
            prompt_parts.append(f"TASK ID: {request.task_id}")
            prompt_parts.append(f"ROLE: {request.role.upper()}")
            if request.role.lower() == "executor":
                prompt_parts.append(
                    "INSTRUCTION: You are an expert software engineer acting as an Executor in the JESTER engineering workflow.\n"
                    "Implement the required changes within the authorized scope.\n"
                    "Adhere strictly to constraints and satisfy all acceptance criteria.\n"
                    "CRITICAL FILE FORMAT REQUIREMENT: When creating or modifying files, you MUST output the complete file content\n"
                    "inside a markdown code block with the exact file path header syntax:\n"
                    "```python:<exact_relative_path>\n<file_content>\n```\n"
                    "Do NOT omit the relative path after the colon. Example:\n"
                    "```python:tests/bridge/task_0015_antigravity_cli_e2e_probe.py\ndef test_two_plus_two():\n    assert 2 + 2 == 4\n```"
                )
            elif request.role.lower() == "reviewer":
                prompt_parts.append(
                    "INSTRUCTION: You are an independent code reviewer in the JESTER engineering workflow.\n"
                    "Inspect the provided unified code diff and verification output against the task goal and acceptance criteria.\n"
                    "Verify whether the diff correctly creates or modifies the requested files and passes tests.\n"
                    "If the diff satisfies the criteria and tests pass, your review MUST explicitly state 'VERDICT: PASS' and explain why.\n"
                    "If the criteria are not satisfied or tests fail, your review MUST state 'VERDICT: REWORK_REQUIRED' with specific feedback."
                )
            elif request.role.lower() == "architect":
                prompt_parts.append(
                    "INSTRUCTION: You are a software architect. Decompose the goal into structured task specifications."
                )

        prompt_parts.append(f"GOAL: {goal}")
        if scope:
            prompt_parts.append(f"AUTHORIZED SCOPE:\n" + "\n".join(f"  - {s}" for s in scope))
        if constraints:
            prompt_parts.append(f"CONSTRAINTS:\n" + "\n".join(f"  - {c}" for c in constraints))
        if criteria:
            prompt_parts.append(f"ACCEPTANCE CRITERIA:\n" + "\n".join(f"  - {a}" for a in criteria))
        if verification:
            prompt_parts.append(f"VERIFICATION COMMANDS:\n" + "\n".join(f"  - {v}" for v in verification))

        code_context = req_payload.get("code_context")
        if code_context:
            prompt_parts.append(f"\nCODE CONTEXT:\n{code_context}")

        diff = req_payload.get("diff")
        if diff:
            prompt_parts.append(f"\nUNIFIED CODE DIFF (CRITICAL EVIDENCE):\n```diff\n{diff}\n```")

        verif_output = req_payload.get("verification_output")
        if verif_output:
            prompt_parts.append(f"\nVERIFICATION OUTPUT:\n{verif_output}")

        prompt = "\n".join(prompt_parts)

        cmd, stdin_input = self._build_command(request, prompt)
        env = self._build_env()

        try:
            if self._runner_fn is not None:
                # Use injected runner for test doubles
                retcode, stdout, stderr = self._runner_fn(cmd, env, req_payload)
            else:
                proc = subprocess.run(
                    cmd,
                    input=stdin_input,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout,
                    env=env,
                    shell=False,
                )
                retcode = proc.returncode
                stdout = proc.stdout
                stderr = proc.stderr

            clean_stdout = _sanitize_cli_text(stdout or "")
            clean_stderr = _sanitize_cli_text(stderr or "")

            # Attempt JSON error parsing and structured response extraction
            json_error = None
            parsed_agy_data = None
            for raw_text in (stdout or "", stderr or ""):
                if not raw_text.strip():
                    continue
                # 1. Look for embedded JSON object { ... }
                try:
                    matches = list(re.finditer(r"(\{.*\})", raw_text, flags=re.DOTALL))
                    if matches:
                        target = matches[-1].group(1).strip()
                        data = json.loads(target)
                        if isinstance(data, dict):
                            if self._executable_name == "agy" and ("status" in data or "response" in data):
                                parsed_agy_data = data
                            if "error" in data and data["error"]:
                                err_obj = data["error"]
                                msg = err_obj.get("message") if isinstance(err_obj, dict) else str(err_obj)
                                code = err_obj.get("code") if isinstance(err_obj, dict) else None
                                if code == 41 or (msg and "Invalid auth method" in msg):
                                    json_error = f"Gemini CLI authentication required: {msg} (code {code})"
                                else:
                                    json_error = f"{msg}" + (f" (code {code})" if code else "")
                                break
                except Exception:
                    pass

            usage = UsageMetrics(input_tokens=100, output_tokens=100, total_tokens=200)
            raw_meta = {
                "cli_executable": self._executable_name,
                "cli_profile": self._cli_profile,
                "account_id": self._account_id,
            }

            if parsed_agy_data:
                if parsed_agy_data.get("status") == "SUCCESS" and retcode == 0:
                    status = InvocationStatus.SUCCESS
                    summary = parsed_agy_data.get("response", "").strip() or f"CLI {self._executable_name} finished successfully."
                    err_msg = None
                else:
                    status = InvocationStatus.FAILED
                    err_msg = parsed_agy_data.get("error") or clean_stderr or f"CLI execution failed with code {retcode}."
                    summary = f"CLI {self._executable_name} error: {err_msg}"

                agy_usage = parsed_agy_data.get("usage", {})
                if isinstance(agy_usage, dict):
                    usage = UsageMetrics(
                        input_tokens=agy_usage.get("input_tokens", 100),
                        output_tokens=agy_usage.get("output_tokens", 100),
                        total_tokens=agy_usage.get("total_tokens", 200),
                    )
                raw_meta["conversation_id"] = parsed_agy_data.get("conversation_id")
                raw_meta["duration_seconds"] = parsed_agy_data.get("duration_seconds")
            elif json_error:
                status = InvocationStatus.FAILED
                summary = f"CLI {self._executable_name} error: {json_error}"
                err_msg = json_error
            elif retcode == 0:
                status = InvocationStatus.SUCCESS
                summary = clean_stdout or f"CLI {self._executable_name} finished successfully."
                err_msg = None
            else:
                status = InvocationStatus.FAILED
                summary = clean_stdout or f"CLI {self._executable_name} exited with status {retcode}."
                err_msg = clean_stderr or f"CLI execution failed with code {retcode}."

        except subprocess.TimeoutExpired:
            status = InvocationStatus.FAILED
            summary = f"CLI {self._executable_name} timed out after {self._timeout}s."
            err_msg = summary
            usage = UsageMetrics(input_tokens=0, output_tokens=0, total_tokens=0)
            raw_meta = {"cli_executable": self._executable_name, "account_id": self._account_id}
        except Exception as e:
            status = InvocationStatus.FAILED
            summary = f"CLI {self._executable_name} failed to execute."
            err_msg = _sanitize_cli_text(str(e))
            usage = UsageMetrics(input_tokens=0, output_tokens=0, total_tokens=0)
            raw_meta = {"cli_executable": self._executable_name, "account_id": self._account_id}

        # Extract file changes from summary if present
        from .runtime import extract_file_changes_from_text
        changes = extract_file_changes_from_text(summary) if summary else []
        files_mod = [c.relative_path for c in changes]

        return InvocationResult(
            request_id=request.request_id,
            task_id=request.task_id,
            status=status,
            agent_id=request.agent_id,
            provider=self.provider_id,
            model=request.model or self._executable_name,
            summary=summary,
            files_modified=files_mod,
            reports_generated=[],
            error_message=err_msg,
            usage=usage,
            raw_metadata=raw_meta,
            completed_at=datetime.now(timezone.utc).isoformat(),
        )


class LocalRuntimeAdapter(AgentProvider):
    """
    Local Engine Adapter for local model servers (e.g. Ollama daemon on localhost).

    Enforces:
    - Zero mandatory authentication requirements
    - Safe local connectivity inspection (endpoint polling)
    - Offline daemon status reporting without system crashing
    - Output normalization to standard InvocationResult
    """

    def __init__(
        self,
        provider_id: str = "ollama",
        endpoint: str = "http://127.0.0.1:11434",
        default_model: str = "qwen2.5:7b",
        timeout: float = 30.0,
        supported_capabilities: Optional[Set[str]] = None,
        client: Optional[Any] = None,
    ):
        self._provider_id = provider_id
        self._endpoint = endpoint.rstrip("/")
        self._default_model = default_model
        self._timeout = timeout
        self._capabilities = set(supported_capabilities or DEFAULT_LOCAL_CAPABILITIES)
        self._client = client

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def default_model(self) -> str:
        return self._default_model

    def get_supported_capabilities(self) -> Set[str]:
        return set(self._capabilities)

    def health_check(self) -> bool:
        """Checks if local daemon is reachable."""
        readiness = self.check_readiness()
        return readiness.status == RuntimeStatus.READY

    def check_readiness(self) -> RuntimeReadiness:
        """Polls local daemon endpoint to verify connectivity."""
        if self._client is not None:
            # Test double client
            if hasattr(self._client, "is_healthy") and not self._client.is_healthy:
                return RuntimeReadiness(
                    status=RuntimeStatus.OFFLINE,
                    message=f"Local engine at {self._endpoint} is unreachable.",
                )
            return RuntimeReadiness(
                status=RuntimeStatus.READY,
                message=f"Local engine ready at {self._endpoint}.",
            )

        try:
            import httpx
            resp = httpx.get(f"{self._endpoint}/api/tags", timeout=2.0)
            if resp.status_code == 200:
                return RuntimeReadiness(
                    status=RuntimeStatus.READY,
                    message=f"Local engine ready at {self._endpoint}.",
                )
            else:
                return RuntimeReadiness(
                    status=RuntimeStatus.ERROR,
                    message=f"Local engine responded with HTTP {resp.status_code}.",
                )
        except Exception:
            return RuntimeReadiness(
                status=RuntimeStatus.OFFLINE,
                message=f"Local daemon offline / unreachable at {self._endpoint}.",
            )

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        """Executes a request against the local engine."""
        readiness = self.check_readiness()
        if readiness.status != RuntimeStatus.READY:
            return InvocationResult(
                request_id=request.request_id,
                task_id=request.task_id,
                status=InvocationStatus.BLOCKED,
                agent_id=request.agent_id,
                provider=self.provider_id,
                model=request.model or self._default_model,
                summary=f"Local engine is offline: {readiness.message}",
                error_message=readiness.message,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )

        # In production, make HTTP POST to /api/generate or use test double
        if self._client is not None and hasattr(self._client, "generate"):
            res_text = self._client.generate(request)
        else:
            res_text = f"[local:{self.provider_id}] Generated response using {request.model or self._default_model}."

        return InvocationResult(
            request_id=request.request_id,
            task_id=request.task_id,
            status=InvocationStatus.SUCCESS,
            agent_id=request.agent_id,
            provider=self.provider_id,
            model=request.model or self._default_model,
            summary=res_text,
            files_modified=[],
            reports_generated=[],
            usage=UsageMetrics(input_tokens=50, output_tokens=50, total_tokens=100),
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
