"""Real sandbox execution for bounded repository smoke tests."""

from __future__ import annotations

import asyncio
import re
import shutil
import textwrap
import time
import uuid
from typing import Any


_MAX_LOG_CHARS = 8192
_STEP_MARKER = re.compile(
    r"__LITAGENT_STEP__([^|]+)\|([^|]+)\|(\d+)"
)
_STATUS_MARKER = re.compile(r"__LITAGENT_STATUS__([a-z_]+)")
_PROJECT_MARKER = re.compile(r"__LITAGENT_PROJECT__([a-z_]+)")


def _bounded(text: str, limit: int = _MAX_LOG_CHARS) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    suffix = "\n...[truncated]"
    return text[: limit - len(suffix)] + suffix


def _empty_result(repository: str) -> dict[str, Any]:
    return {
        "status": "failed",
        "repository": repository,
        "project_type": None,
        "steps": [],
        "executed_command": None,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "duration_seconds": 0.0,
        "summary": "Repository smoke test did not run.",
    }


async def _run_process(
    command: list[str],
    *,
    timeout_seconds: float,
) -> tuple[int | None, str, str, bool]:
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout_seconds,
        )
    except asyncio.TimeoutError:
        process.kill()
        stdout, stderr = await process.communicate()
        return (
            process.returncode,
            stdout.decode(errors="replace"),
            stderr.decode(errors="replace"),
            True,
        )

    return (
        process.returncode,
        stdout.decode(errors="replace"),
        stderr.decode(errors="replace"),
        False,
    )


class DockerSandboxRunner:
    """Run one conservative repository smoke test in a Docker container."""

    def __init__(
        self,
        image: str = "python:3.12-slim",
        timeout_seconds: int = 120,
        network_enabled: bool = True,
        cpu_limit: str = "2",
        memory_limit: str = "2g",
    ) -> None:
        self.image = image
        self.timeout_seconds = timeout_seconds
        self.network_enabled = network_enabled
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit

    async def _check_runtime(self, docker: str) -> str | None:
        exit_code, _, stderr, timed_out = await _run_process(
            [docker, "info", "--format", "{{.ServerVersion}}"],
            timeout_seconds=10,
        )
        if timed_out or exit_code != 0:
            detail = stderr.strip() or "Docker daemon is unavailable."
            return f"Docker runtime is not available: {detail}"
        return None

    async def run_repository_smoke_test(self, repository: str) -> dict[str, Any]:
        result = _empty_result(repository)
        docker = shutil.which("docker")
        if not docker:
            result.update(
                {
                    "status": "sandbox_unavailable",
                    "error": "Docker runtime is not available.",
                    "summary": "Docker executable is not available.",
                }
            )
            return result

        runtime_error = await self._check_runtime(docker)
        if runtime_error:
            result.update(
                {
                    "status": "sandbox_unavailable",
                    "error": runtime_error,
                    "summary": "Docker daemon is not available.",
                }
            )
            return result

        script = textwrap.dedent(
            """
            set -u
            REPO_DIR=/workspace/repo

            run_step() {
                name="$1"
                description="$2"
                shift 2
                "$@"
                code=$?
                printf '__LITAGENT_STEP__%s|%s|%s\\n' "$name" "$description" "$code"
                return "$code"
            }

            if ! command -v git >/dev/null 2>&1; then
                if ! run_step bootstrap 'apt-get update && apt-get install git' \
                    sh -c 'apt-get update && apt-get install -y --no-install-recommends git'; then
                    printf '__LITAGENT_STATUS__failed\\n'
                    exit 20
                fi
            fi

            if ! run_step clone 'git clone --depth 1' \
                git clone --depth 1 "$REPOSITORY" "$REPO_DIR"; then
                printf '__LITAGENT_STATUS__failed\\n'
                exit 21
            fi

            if ! run_step inspect 'find repository files' \
                sh -c 'find "$1" -maxdepth 2 -type f | sort | head -n 80' sh "$REPO_DIR"; then
                printf '__LITAGENT_STATUS__failed\\n'
                exit 22
            fi

            if [ -f "$REPO_DIR/pyproject.toml" ] || \
               [ -f "$REPO_DIR/requirements.txt" ] || \
               [ -f "$REPO_DIR/setup.py" ] || \
               find "$REPO_DIR" -maxdepth 2 -type f -name '*.py' | grep -q .; then
                printf '__LITAGENT_PROJECT__python\\n'
            else
                printf '__LITAGENT_PROJECT__unknown\\n'
                printf '__LITAGENT_STATUS__unsupported_project_type\\n'
                exit 0
            fi

            if ! run_step environment 'python -m venv /workspace/venv' \
                python -m venv /workspace/venv; then
                printf '__LITAGENT_STATUS__failed\\n'
                exit 23
            fi

            if [ -f "$REPO_DIR/requirements.txt" ]; then
                if ! run_step dependencies 'python -m pip install -r requirements.txt' \
                    sh -c 'cd "$1" && . /workspace/venv/bin/activate && python -m pip install --no-cache-dir -r requirements.txt' sh "$REPO_DIR"; then
                    printf '__LITAGENT_STATUS__failed\\n'
                    exit 24
                fi
            elif [ -f "$REPO_DIR/pyproject.toml" ] || [ -f "$REPO_DIR/setup.py" ]; then
                if ! run_step dependencies 'python -m pip install -e .' \
                    sh -c 'cd "$1" && . /workspace/venv/bin/activate && python -m pip install --no-cache-dir -e .' sh "$REPO_DIR"; then
                    printf '__LITAGENT_STATUS__failed\\n'
                    exit 25
                fi
            fi

            TEST_FILE=$(find "$REPO_DIR" -maxdepth 3 -type f \
                \\( -name 'test_*.py' -o -name '*_test.py' \\) | sort | head -n 1)
            if [ -n "$TEST_FILE" ]; then
                if ! run_step test_dependencies 'python -m pip install pytest' \
                    sh -c '. /workspace/venv/bin/activate && python -m pip install --no-cache-dir pytest' ; then
                    printf '__LITAGENT_STATUS__failed\\n'
                    exit 26
                fi
                if run_step smoke 'python -m pytest -q <first-test-file>' \
                    sh -c 'cd "$1" && . /workspace/venv/bin/activate && python -m pytest -q "$2"' sh "$REPO_DIR" "$TEST_FILE"; then
                    printf '__LITAGENT_STATUS__success\\n'
                    exit 0
                fi
                printf '__LITAGENT_STATUS__failed\\n'
                exit 27
            fi

            printf '__LITAGENT_STATUS__inspection_only\\n'
            exit 0
            """
        ).strip()

        network = "bridge" if self.network_enabled else "none"
        container_name = f"litagent-code-reproduce-{uuid.uuid4().hex[:12]}"
        command = [
            docker,
            "run",
            "--rm",
            "--name",
            container_name,
            f"--network={network}",
            f"--cpus={self.cpu_limit}",
            f"--memory={self.memory_limit}",
            "--pids-limit=256",
            "--security-opt",
            "no-new-privileges",
            "--tmpfs",
            "/tmp:rw,nosuid,size=256m",
            "-e",
            f"REPOSITORY={repository}",
            self.image,
            "sh",
            "-c",
            script,
        ]
        started = time.monotonic()
        exit_code, stdout, stderr, timed_out = await _run_process(
            command,
            timeout_seconds=self.timeout_seconds,
        )
        duration = round(time.monotonic() - started, 3)
        result["duration_seconds"] = duration
        result["exit_code"] = exit_code
        result["stdout"] = _bounded(stdout)
        result["stderr"] = _bounded(stderr)
        result["steps"] = [
            {
                "name": match.group(1),
                "command": match.group(2),
                "exit_code": int(match.group(3)),
            }
            for match in _STEP_MARKER.finditer(stdout)
        ]
        project_match = _PROJECT_MARKER.search(stdout)
        result["project_type"] = (
            project_match.group(1) if project_match else None
        )
        if result["steps"]:
            result["executed_command"] = result["steps"][-1]["command"]

        if timed_out:
            await _run_process(
                [docker, "rm", "-f", container_name],
                timeout_seconds=10,
            )
            result["status"] = "timeout"
            result["error"] = "Sandbox execution exceeded its timeout."
            result["summary"] = "Repository smoke test timed out."
            return result

        status_match = _STATUS_MARKER.search(stdout)
        status = status_match.group(1) if status_match else None
        if not status:
            daemon_error = stderr.lower()
            if exit_code == 125 and (
                "daemon" in daemon_error or "connect" in daemon_error
            ):
                status = "sandbox_unavailable"
                result["error"] = _bounded(stderr.strip())
            else:
                status = "failed"
        result["status"] = status
        summaries = {
            "success": "Repository smoke test passed.",
            "failed": "Repository smoke test failed.",
            "unsupported_project_type": "Repository is not a supported Python project.",
            "inspection_only": "Python project inspected; no safe test entrypoint was found.",
            "sandbox_unavailable": "Docker container could not be started.",
        }
        result["summary"] = summaries.get(status, "Repository smoke test completed.")
        return result
