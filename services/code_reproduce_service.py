"""Workflow service for the bounded code-reproduction MVP."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from services.sandbox_service import DockerSandboxRunner


_GITHUB_URL = re.compile(
    r"https://github\.com/[^\s)>,]+",
    flags=re.IGNORECASE,
)
_TRAILING_PUNCTUATION = ".,;:!?)]}"


def _find_repository(task: str, repository: str | None) -> str | None:
    candidate = repository or (_GITHUB_URL.search(task or "") or [None])[0]
    if not candidate:
        return None
    candidate = candidate.rstrip(_TRAILING_PUNCTUATION).rstrip("/")
    parsed = urlparse(candidate)
    parts = [part for part in parsed.path.split("/") if part]
    if (
        parsed.scheme.lower() != "https"
        or parsed.netloc.lower() != "github.com"
        or len(parts) != 2
        or not all(parts)
    ):
        return None
    return candidate


def _missing_repository_result() -> dict[str, Any]:
    return {
        "status": "failed",
        "repository": None,
        "project_type": None,
        "steps": [],
        "executed_command": None,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "duration_seconds": 0.0,
        "error": "A valid GitHub repository URL is required for code reproduction.",
        "summary": "No valid GitHub repository URL was provided.",
    }


async def run_code_reproduce(
    task: str,
    repository: str | None = None,
    sandbox=None,
) -> dict[str, Any]:
    """Run one repository smoke test through the sandbox boundary."""

    repository_url = _find_repository(task, repository)
    if not repository_url:
        return _missing_repository_result()

    runner = sandbox or DockerSandboxRunner()
    return await runner.run_repository_smoke_test(repository_url)
