import json
from urllib.request import urlopen


def _restore_abstract(inverted_index: dict | None) -> str:
    """Restore an OpenAlex inverted abstract index to normal text."""

    if not inverted_index:
        return ""

    words = []
    for word, positions in inverted_index.items():
        for position in positions:
            words.append((position, word))

    words.sort(key=lambda item: item[0])
    return " ".join(word for _, word in words)


def _preserve_identity(paper: dict, result: dict) -> dict:
    """Keep identifiers supplied by non-OpenAlex search providers."""

    for field in ("source", "searcher", "paper_id", "doi", "title"):
        if paper.get(field) is not None and result.get(field) is None:
            result[field] = paper[field]
    return result


def fetch_paper_metadata(paper: dict) -> dict:
    """Fetch paper metadata and abstract from OpenAlex."""

    openalex_id = paper.get("openalex_id")
    if not openalex_id:
        return _preserve_identity(paper, {
            "title": paper.get("title"),
            "error": "missing openalex_id",
        })

    work_id = openalex_id.rstrip("/").split("/")[-1]
    api_url = f"https://api.openalex.org/works/{work_id}"

    try:
        with urlopen(api_url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        abstract = _restore_abstract(data.get("abstract_inverted_index"))
        best_oa_location = data.get("best_oa_location") or {}
        return _preserve_identity(paper, {
            "title": data.get("title"),
            "doi": data.get("doi"),
            "year": data.get("publication_year"),
            "abstract": abstract,
            "openalex_id": openalex_id,
            "pdf_url": best_oa_location.get("pdf_url"),
        })
    except Exception as exc:
        return _preserve_identity(paper, {
            "title": paper.get("title"),
            "doi": paper.get("doi"),
            "openalex_id": openalex_id,
            "error": str(exc),
        })
