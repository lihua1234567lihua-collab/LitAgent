# Code Reproduce MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a safe `code_reproduce` capability that runs a minimal GitHub repository smoke test inside a real Docker sandbox and returns bounded structured results without changing existing research workflows.

**Architecture:** `services/sandbox_service.py` owns Docker availability checks, resource limits, container execution, timeout handling, and bounded logs. `services/code_reproduce_service.py` extracts and validates an explicit GitHub URL, invokes the sandbox, and normalizes the result. `agent/graph.py` only registers the capability, dispatches a short node, and stores the structured result in the existing `step_results` state.

**Tech Stack:** Python async subprocess API for the Docker CLI, Docker container isolation, LangGraph node/edge registration, existing `ResearchState` and checkpoint flow, `unittest`/pytest.

## Global Constraints

- Only implement repository smoke testing; do not train models, download large datasets/models, use GPUs, auto-fix repositories, run long experiments, or reproduce paper metrics.
- Use a real Docker isolation boundary; never substitute `subprocess + tempfile` for sandboxing.
- Do not mount the host project/home, expose the Docker socket, use privileged mode, install Docker, or modify the host Python environment.
- Clone with `--depth 1`; allow network only through the explicit `network_enabled` option.
- If Docker or its daemon is unavailable, return `sandbox_unavailable` as structured data and do not crash the Graph.
- Run the first lightweight test file only when tests are discoverable; otherwise return `inspection_only` and never execute arbitrary README shell commands.
- Keep stdout/stderr bounded before placing results in `ResearchState`.
- Preserve existing Router, Planner, Executor, RAG, paper search/read, HITL, checkpoint, API, and State semantics except for adding the new capability route.
- Do not commit or push changes.

---

### Task 1: Add the Docker sandbox runner

**Files:**
- Create: `services/sandbox_service.py`
- Test: `tests/test_code_reproduce.py`

**Interfaces:**
- Produces `SandboxRunner.run_repository_smoke_test(repository: str) -> dict[str, Any]` as an async interface.
- The default implementation is `DockerSandboxRunner`; it returns statuses `success`, `failed`, `timeout`, `sandbox_unavailable`, `unsupported_project_type`, or `inspection_only`.

- [ ] **Step 1: Write failing tests for Docker-unavailable and bounded result contracts**

```python
async def test_docker_unavailable_is_structured(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    result = await DockerSandboxRunner().run_repository_smoke_test(
        "https://github.com/example/project"
    )
    assert result["status"] == "sandbox_unavailable"
    assert "Docker" in result["error"]

async def test_fake_runner_result_preserves_steps_and_logs():
    result = await FakeSandbox().run_repository_smoke_test(
        "https://github.com/example/project"
    )
    assert result["status"] == "success"
    assert result["steps"][0]["name"] == "clone"
    assert len(result["stdout"]) <= 8192
```

- [ ] **Step 2: Run the focused tests and verify they fail because the service does not exist**

Run: `uv run --no-sync python -m pytest tests/test_code_reproduce.py -v`

Expected: collection or import failure for `services.sandbox_service`.

- [ ] **Step 3: Implement the minimal Docker runner**

Implement `DockerSandboxRunner` with these exact behaviors:

```python
class DockerSandboxRunner:
    def __init__(
        self,
        image: str = "python:3.12-slim",
        timeout_seconds: int = 120,
        network_enabled: bool = True,
        cpu_limit: str = "2",
        memory_limit: str = "2g",
    ):
        ...

    async def run_repository_smoke_test(self, repository: str) -> dict[str, Any]:
        ...
```

Validate the Docker executable with `shutil.which("docker")`, then validate the daemon with `docker info`. Return `sandbox_unavailable` on either failure. Run one `docker run --rm` command with `--network=bridge` or `--network=none`, `--cpus`, `--memory`, `--pids-limit`, and `--security-opt no-new-privileges`; do not add volumes, privileged flags, or Docker socket mounts. The container script must clone with `git clone --depth 1`, inspect only shallow file structure, identify Python markers, install dependencies only in the container, and run only the first discovered test file through `python -m pytest -q`. If no test exists, emit `inspection_only`. Parse step markers into `steps`, capture `executed_command`, `exit_code`, `duration_seconds`, `stdout`, `stderr`, and `summary`, truncating both logs to 8192 characters. Wrap process communication in `asyncio.wait_for`; kill the process on timeout and return `timeout`.

- [ ] **Step 4: Run the focused sandbox tests**

Run: `uv run --no-sync python -m pytest tests/test_code_reproduce.py -v`

Expected: PASS for the unavailable-runtime and result-contract tests without requiring Docker or network access.

---

### Task 2: Add the code-reproduce service

**Files:**
- Create: `services/code_reproduce_service.py`
- Test: `tests/test_code_reproduce.py`

**Interfaces:**
- Produces `async def run_code_reproduce(task: str, repository: str | None = None, sandbox=None) -> dict[str, Any]`.
- It accepts an injected fake runner for tests and defaults to `DockerSandboxRunner`.

- [ ] **Step 1: Write failing tests for URL extraction, success, failure, and timeout normalization**

```python
async def test_code_reproduce_calls_injected_sandbox():
    sandbox = FakeSandbox()
    result = await run_code_reproduce(
        "Please smoke test https://github.com/example/project",
        sandbox=sandbox,
    )
    assert sandbox.repositories == ["https://github.com/example/project"]
    assert result["status"] == "success"

async def test_code_reproduce_without_github_url_does_not_start_sandbox():
    sandbox = FakeSandbox()
    result = await run_code_reproduce("reproduce the code", sandbox=sandbox)
    assert result["status"] == "failed"
    assert sandbox.repositories == []
    assert "GitHub" in result["error"]
```

- [ ] **Step 2: Run focused tests and verify the new service tests fail**

Run: `uv run --no-sync python -m pytest tests/test_code_reproduce.py -v`

Expected: import or missing-function failures for `services.code_reproduce_service`.

- [ ] **Step 3: Implement URL validation and service normalization**

Accept an explicit `repository` argument or the first `https://github.com/<owner>/<repo>` URL in `task`; reject missing URLs and non-GitHub URLs with a structured `failed` result. Strip trailing punctuation and preserve the repository URL in the result. Await the injected runner and return its structured result unchanged except for adding a concise `summary` when absent. Do not download, parse, or execute anything in this service.

- [ ] **Step 4: Run focused service tests**

Run: `uv run --no-sync python -m pytest tests/test_code_reproduce.py -v`

Expected: PASS for URL extraction, injected-runner success, missing URL, `sandbox_unavailable`, repository failure with stderr, and timeout result preservation.

---

### Task 3: Register the capability in the Graph and add integration coverage

**Files:**
- Modify: `agent/graph.py`
- Modify: `tests/test_graph_refactor.py`
- Test: `tests/test_code_reproduce.py`

**Interfaces:**
- Add `code_reproduce` to the existing action set and action routing map.
- Add a short `code_reproduce_node` that obtains the current step, calls `run_code_reproduce`, serializes the bounded structured result into the existing `step_results`, and calls `_step_update`.

- [ ] **Step 1: Write failing Graph integration tests**

Cover these assertions:

```python
async def test_executor_routes_code_reproduce_and_advances_once():
    # Fake planner/executor responses select code_reproduce.
    # Patch agent.graph.run_code_reproduce with an async fake.
    # Assert one call, current_step == 1, and structured status in step_results.

async def test_code_reproduce_failure_does_not_loop_or_crash():
    # Return sandbox_unavailable or failed from the fake service.
    # Assert Graph completes the step once and does not re-enter executor forever.
```

- [ ] **Step 2: Run the new integration tests and verify they fail before Graph registration**

Run: `uv run --no-sync python -m pytest tests/test_code_reproduce.py tests/test_graph_refactor.py -v`

Expected: failure because `code_reproduce` is not yet in `ACTIONS` or the node map.

- [ ] **Step 3: Add the minimal Graph integration**

Import `run_code_reproduce`, add `"code_reproduce"` to `ACTIONS`, add one short async node, register it in `create_node_handlers`, and map it in `action_route`/the capability edges. Extend only the planner/executor prompt capability lists enough for a plan step to name `code_reproduce`; do not change Router behavior or any existing node. Serialize the service result with `json.dumps(..., ensure_ascii=False)` before passing it as the existing `_step_update` result so no new State field is required. The node must not access Docker, Git, pip, or filesystem details directly.

- [ ] **Step 4: Run all required verification**

Run:

```text
uv run --no-sync python -m pytest tests/test_code_reproduce.py -v
uv run --no-sync python -m pytest tests/test_graph_refactor.py -v
uv run --no-sync python -m pytest -v
uv run --no-sync python -m compileall agent services tools api
git diff --check
```

Expected: all existing and new tests pass, compileall succeeds, and no whitespace errors are reported. Also manually invoke the default runner in an environment without an available Docker daemon and verify it returns `sandbox_unavailable` without raising into the Graph.

---

## Self-review checklist

- Existing paper search/read, RAG, HITL, checkpoint, and FastAPI paths are untouched except for normal Graph registration imports/maps.
- No host project or home directory is mounted into the container.
- No arbitrary README shell command is executed.
- No result log larger than 8192 characters enters `step_results`.
- Every sandbox failure mode is a structured result, and the Graph advances exactly once for the capability step.
- No commit or push is performed.
