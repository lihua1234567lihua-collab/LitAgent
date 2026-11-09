'''执行结果校验，检查论文数量、年份、重复性，以及阅读、推理、代码复现等步骤的结果'''
from __future__ import annotations

import re
from typing import Any


_ID_FIELDS = ("doi", "openalex_id", "paper_id", "id")


def _extract_count(step_goal: str) -> int | None:
    patterns = [
        r"(?:at least|minimum of|至少|不少于)\s*(\d+)",
        r"(?:top|find|select|choose|找|筛选|选择)\s*(\d+)",
        r"\b(\d+)\s+(?:papers|articles|studies)\b",
        r"(\d+)\s*篇",
    ]

    for pattern in patterns:
        match = re.search(pattern, step_goal, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))

    return None


def _extract_year_range(step_goal: str) -> tuple[int | None, int | None]:
    match = re.search(
        r"(20\d{2})\s*(?:-|–|—|至|到)\s*(20\d{2})",
        step_goal,
        flags=re.IGNORECASE,
    )
    if match:
        return int(match.group(1)), int(match.group(2))

    match = re.search(
        r"(?:after|since|from|自|从)\s*(20\d{2})",
        step_goal,
        flags=re.IGNORECASE,
    )
    if match:
        return int(match.group(1)), None

    match = re.search(
        r"(?:before|until|之前|不晚于)\s*(20\d{2})",
        step_goal,
        flags=re.IGNORECASE,
    )
    if match:
        return None, int(match.group(1))

    match = re.search(r"(?<!\d)(20\d{2})(?!\d)", step_goal)
    if match:
        year = int(match.group(1))
        return year, year

    return None, None


def _paper_year(paper: dict[str, Any]) -> int | None:
    for key in ("publication_year", "year"):
        value = paper.get(key)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass

    for key in ("publication_date", "date"):
        value = str(paper.get(key) or "")
        match = re.search(r"(20\d{2})", value)
        if match:
            return int(match.group(1))

    return None


def _paper_identity(paper: dict[str, Any]) -> str | None:
    for key in _ID_FIELDS:
        value = str(paper.get(key) or "").strip().lower()
        if value:
            return f"{key}:{value}"

    title = re.sub(r"\s+", " ", str(paper.get("title") or "").strip())
    return f"title:{title.lower()}" if title else None


def _has_identifier(paper: dict[str, Any]) -> bool:
    return any(str(paper.get(key) or "").strip() for key in _ID_FIELDS)


def _result(
    passed: bool,
    reason: str,
    failed_constraints: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "passed": passed,
        "source": "deterministic",
        "reason": reason,
        "failed_constraints": failed_constraints,
    }


def validate_paper_read(
    step_goal: str,
    paper_contents: dict[str, dict[str, Any]],
    paper_analyses: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Validate that paper content and structured analyses are ready."""

    failures: list[dict[str, Any]] = []

    if not paper_contents:
        failures.append({"type": "paper_content", "reason": "missing"})

    for key, content in paper_contents.items():
        if content.get("status") != "ready":
            failures.append(
                {
                    "type": "paper_content",
                    "paper": key,
                    "reason": "not_ready",
                }
            )
        if not str(content.get("content") or "").strip():
            failures.append(
                {
                    "type": "paper_content",
                    "paper": key,
                    "reason": "empty",
                }
            )
        if not str(paper_analyses.get(key, {}).get("analysis") or "").strip():
            failures.append(
                {
                    "type": "paper_analysis",
                    "paper": key,
                    "reason": "missing",
                }
            )

    if failures:
        return _result(False, "paper_read validation failed", failures)

    return _result(
        True,
        f"paper_read completed for {len(paper_contents)} papers",
        [],
    )


def validate_reasoning(
    step_goal: str,
    result: str,
) -> dict[str, Any]:
    """Validate that the reasoning node produced a non-empty result."""

    if not str(result or "").strip():
        return _result(
            False,
            "reasoning result is empty",
            [{"type": "reasoning_result", "reason": "empty"}],
        )

    return _result(True, "reasoning result is ready", [])


def validate_code_reproduce(
    step_goal: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    """Validate the structured result returned by the sandbox workflow."""

    if not isinstance(result, dict):
        return _result(
            False,
            "code reproduction result is invalid",
            [{"type": "code_reproduce_result", "reason": "invalid"}],
        )

    status = str(result.get("status") or "").strip().lower()
    exit_code = result.get("exit_code")
    if status != "success" or exit_code not in (None, 0):
        return _result(
            False,
            "code reproduction did not succeed",
            [
                {
                    "type": "code_reproduce_status",
                    "status": status or None,
                    "exit_code": exit_code,
                }
            ],
        )

    return _result(True, "code reproduction succeeded", [])


def validate_paper_search(
    step_goal: str,
    search_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate explicit paper-search constraints without calling an LLM."""

    if not search_results:
        return _result(
            False,
            "搜索结果为空。",
            [{"type": "non_empty_results", "actual": 0}],
        )

    failures: list[dict[str, Any]] = []
    valid_papers: list[dict[str, Any]] = []

    for index, paper in enumerate(search_results):
        if not str(paper.get("title") or "").strip():
            failures.append(
                {
                    "type": "required_field",
                    "index": index,
                    "field": "title",
                }
            )
            continue

        if not _has_identifier(paper):
            failures.append(
                {
                    "type": "required_field",
                    "index": index,
                    "field": "paper_identifier",
                }
            )
            continue

        valid_papers.append(paper)

    seen: set[str] = set()
    unique_papers: list[dict[str, Any]] = []
    duplicate_count = 0

    for paper in valid_papers:
        identity = _paper_identity(paper)
        if identity in seen:
            duplicate_count += 1
            continue

        if identity:
            seen.add(identity)

        unique_papers.append(paper)

    if duplicate_count:
        failures.append(
            {
                "type": "duplicate_papers",
                "count": duplicate_count,
            }
        )

    required_count = _extract_count(step_goal)
    actual_count = len(unique_papers)

    if required_count is not None and actual_count < required_count:
        failures.append(
            {
                "type": "paper_count",
                "required": required_count,
                "actual": actual_count,
            }
        )

    min_year, max_year = _extract_year_range(step_goal)

    if min_year is not None or max_year is not None:
        for paper in unique_papers:
            year = _paper_year(paper)

            if year is None:
                failures.append(
                    {
                        "type": "paper_year",
                        "title": paper.get("title"),
                        "reason": "missing",
                    }
                )
                continue

            if min_year is not None and year < min_year:
                failures.append(
                    {
                        "type": "paper_year",
                        "title": paper.get("title"),
                        "year": year,
                        "minimum": min_year,
                    }
                )

            if max_year is not None and year > max_year:
                failures.append(
                    {
                        "type": "paper_year",
                        "title": paper.get("title"),
                        "year": year,
                        "maximum": max_year,
                    }
                )

    if failures:
        return _result(
            False,
            "；".join(item["type"] for item in failures),
            failures,
        )

    return _result(
        True,
        f"确定性条件满足，共 {actual_count} 篇唯一论文。",
        [],
    )
