"""Multi-paper orchestration for the paper-read graph node."""

import json
from pathlib import Path
from typing import Any, Callable

from services.fulltext_resolver import (
    _safe_pdf_stem,
    resolve_paper_content,
)
from tools.paper_reader import read_paper


def _paper_key(paper: dict[str, Any]) -> str:
    return str(
        paper.get("openalex_id")
        or paper.get("doi")
        or paper.get("title")
        or "unknown-paper"
    )


def _response_text(response: Any) -> str:
    content = getattr(response, "content", response)
    return str(content).strip()


async def prepare_paper_read(
    selected_papers: list[dict[str, Any]] | None = None,
    task: str = "",
    model=None,
    paper_contents: dict[str, dict[str, Any]] | None = None,
    paper_analyses: dict[str, dict[str, Any]] | None = None,
    thread_id: str = "current-thread",
    workspace_dir: str | Path | None = None,
    paper_reader: Callable[[dict], dict] | None = None,
    resolver: Callable[..., Any] | None = None,
    *,
    state: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prepare all paper content and analyses required by one graph step."""

    if state is not None:
        selected_papers = state.get("selected_papers", [])
        paper_contents = state.get("paper_contents")
        paper_analyses = state.get("paper_analyses")
    thread_id = (config or {}).get("configurable", {}).get("thread_id", thread_id)
    selected_papers = selected_papers or []
    contents = dict(paper_contents or {})
    analyses = dict(paper_analyses or {})
    missing: list[dict[str, Any]] = []
    reader = paper_reader or read_paper
    resolve = resolver or resolve_paper_content
    workspace = Path(workspace_dir or Path("data") / "workspace" / thread_id)
    workspace.mkdir(parents=True, exist_ok=True)

    for paper in selected_papers:
        key = _paper_key(paper)
        if contents.get(key, {}).get("status") == "ready":
            continue

        paper_data = {**paper, **reader(paper)}
        resolved = await resolve(
            paper=paper_data,
            task=task,
            model=model,
            workspace_dir=workspace,
        )
        if resolved.get("status") == "need_fulltext":
            missing.append(
                {
                    "title": paper.get("title"),
                    "doi": paper.get("doi"),
                    "openalex_id": paper.get("openalex_id"),
                    "paper_id": paper_data.get("paper_id"),
                    "source": paper_data.get("source") or paper_data.get("searcher"),
                    "pdf_target_path": str(
                        workspace / f"{_safe_pdf_stem(paper.get('title'))}.pdf"
                    ),
                }
            )
        else:
            contents[key] = resolved

    for paper in selected_papers:
        key = _paper_key(paper)
        if key in analyses:
            continue
        content = contents.get(key, {}).get("content")
        if not content:
            continue
        prompt = f"""
Extract the method, dataset, results, advantages, and limitations from this
paper content. Use only the supplied content and return a concise structured
analysis.

Paper:
{json.dumps(contents[key], ensure_ascii=False)}
"""
        analyses[key] = {
            "task": "method, dataset, results, advantages, limitations",
            "analysis": _response_text(model.invoke(prompt)),
        }

    return {
        "paper_contents": contents,
        "paper_analyses": analyses,
        "missing": missing,
        "summary": f"Read {len(contents)} papers and cached reusable analyses.",
    }
