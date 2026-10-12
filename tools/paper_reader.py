import json
from urllib.request import urlopen


def _restore_abstract(inverted_index: dict | None) -> str:
    """
    OpenAlex 的摘要不是普通字符串，
    而是 inverted index，需要恢复成正常文本。
    """
    if not inverted_index:
        return ""

    words = []

    for word, positions in inverted_index.items():
        for position in positions:
            words.append((position, word))

    words.sort(key=lambda x: x[0])

    return " ".join(word for _, word in words)


def read_paper(paper: dict) -> dict:
    """
    根据 paper_search 返回的论文信息，
    从 OpenAlex 获取更详细的论文信息和摘要。
    """

    openalex_id = paper.get("openalex_id")

    if not openalex_id:
        return {
            "title": paper.get("title"),
            "error": "缺少 openalex_id",
        }

    work_id = openalex_id.rstrip("/").split("/")[-1]

    api_url = f"https://api.openalex.org/works/{work_id}"

    try:
        with urlopen(api_url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        abstract = _restore_abstract(
            data.get("abstract_inverted_index")
        )

        return {
            "title": data.get("title"),
            "doi": data.get("doi"),
            "year": data.get("publication_year"),
            "abstract": abstract,
            "openalex_id": openalex_id,
        }

    except Exception as e:
        return {
            "title": paper.get("title"),
            "doi": paper.get("doi"),
            "openalex_id": openalex_id,
            "error": str(e),
        }