"""Resolve the paper content required by one planner step.

The graph owns orchestration. This service owns the small content-resolution
policy: a user-provided PDF, a sufficient abstract, academic-mcp full text,
or a HITL request when none of those sources is available.
"""

from pathlib import Path
import re
import shutil
import subprocess

from tools.academic_mcp import read_paper as academic_read_paper


def abstract_is_sufficient(
    abstract: str,
    task: str,
    model,
) -> bool:
    """Return whether the abstract contains enough evidence for ``task``."""

    if not abstract or len(abstract.strip()) < 300:
        return False

    prompt = f"""
Determine whether the following paper abstract is sufficient to complete the
current task without inventing information.

Task:
{task}

Abstract:
{abstract}

Reply with exactly one word: sufficient or insufficient.
"""
    response = model.invoke(prompt)
    decision = getattr(response, "content", response)
    return str(decision).strip().lower() == "sufficient"


def _safe_pdf_stem(title: str | None) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", title or "paper")


def _candidate_pdf_paths(
    paper: dict,
    workspace_dir: str | Path | None,
) -> list[Path]:
    candidates: list[Path] = []
    for field in ("pdf_path", "local_pdf_path"):
        value = paper.get(field)
        if value:
            candidates.append(Path(value))

    if workspace_dir:
        candidates.append(
            Path(workspace_dir) / f"{_safe_pdf_stem(paper.get('title'))}.pdf"
        )

    return candidates


def _read_local_pdf_text(path: Path) -> str | None:
    """Read an existing PDF with the system's lightweight ``pdftotext`` tool."""

    executable = shutil.which("pdftotext")
    if not executable:
        return None

    try:
        result = subprocess.run(
            [executable, "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    text = result.stdout.strip()
    return text or None


def _resolve_local_pdf(
    paper: dict,
    workspace_dir: str | Path | None,
) -> tuple[str, str] | None:
    for path in _candidate_pdf_paths(paper, workspace_dir):
        if not path.is_file():
            continue
        content = _read_local_pdf_text(path)
        if content:
            return str(path), content
    return None


def _result(
    paper: dict,
    task: str,
    *,
    content_type: str | None,
    content: str | None,
    status: str,
    pdf_path: str | None = None,
    error: str | None = None,
) -> dict:
    value = {
        "paper": paper,
        "task": task,
        "content_type": content_type,
        "content": content,
        "status": status,
    }
    if pdf_path is not None:
        value["pdf_path"] = pdf_path
    if error is not None:
        value["error"] = error
    return value


async def resolve_paper_content(
    paper: dict,
    task: str,
    model,
    workspace_dir: str | Path | None = None,
) -> dict:
    """Resolve one paper without downloading or parsing a new PDF."""

    local_pdf = _resolve_local_pdf(paper, workspace_dir)
    if local_pdf:
        path, content = local_pdf
        return _result(
            paper,
            task,
            content_type="fulltext",
            content=content,
            status="ready",
            pdf_path=path,
        )

    abstract = paper.get("abstract") or ""
    if abstract_is_sufficient(abstract, task, model):
        return _result(
            paper,
            task,
            content_type="abstract",
            content=abstract,
            status="ready",
        )

    searcher = paper.get("source") or paper.get("searcher")
    paper_id = paper.get("paper_id")
    if not searcher or not paper_id:
        return _result(
            paper,
            task,
            content_type=None,
            content=None,
            status="need_fulltext",
            error=(
                "Missing academic-mcp identifiers: "
                f"source/searcher={searcher!r}, paper_id={paper_id!r}"
            ),
        )

    try:
        fulltext = await academic_read_paper(
            searcher=searcher,
            paper_id=paper_id,
        )
    except Exception as exc:
        return _result(
            paper,
            task,
            content_type=None,
            content=None,
            status="need_fulltext",
            error=str(exc),
        )

    return _result(
        paper,
        task,
        content_type="fulltext",
        content=fulltext,
        status="ready",
    )
