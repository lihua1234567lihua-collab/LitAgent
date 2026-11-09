"""Resolve the paper content required by one planner step.

The graph owns orchestration. This service owns the small content-resolution
policy: a user-provided PDF, a sufficient abstract, academic-mcp full text,
or a HITL request when none of those sources is available.
"""

from pathlib import Path
import re
import shutil
import subprocess
from tools.pdf_parser import extract_pdf_text



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

def _resolve_local_pdf(
    paper: dict,
    workspace_dir: str | Path | None,
) -> tuple[str, str] | None:
    for path in _candidate_pdf_paths(paper, workspace_dir):
        if not path.is_file():
            continue
        content = extract_pdf_text(path)
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
    model=None,
    workspace_dir: str | Path | None = None,
) -> dict:
    """只解析本地已有的 PDF，不自动联网获取全文。"""

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

    return _result(
        paper,
        task,
        content_type=None,
        content=None,
        status="need_fulltext",
        error="本地没有可用的 PDF，请用户上传全文。",
    )