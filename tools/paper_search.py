import httpx
from langchain.tools import tool


OPENALEX_URL = "https://api.openalex.org/works"


@tool
def search_papers(
    query: str,
    top_k: int = 5,
    start_year: int | None = None,
    end_year: int | None = None,
) -> list[dict]:
    """
    从 OpenAlex 检索真实学术论文。

    Args:
        query: 论文检索主题，例如
               "LiDAR tree crown segmentation"
        top_k: 返回论文数量，默认 5 篇。

    Returns:
        真实论文的标题、作者、年份、期刊、DOI 等信息。
    """

    # 防止 Agent 一次请求太多结果
    top_k = max(1, min(top_k, 10))
    params = {
        "search": query,
        "per_page": top_k,
    }

    filters = []

    if start_year is not None:
        filters.append(f"from_publication_date:{start_year}-01-01")

    if end_year is not None:
        filters.append(f"to_publication_date:{end_year}-12-31")

    if filters:
        params["filter"] = ",".join(filters)

    response = httpx.get(
        OPENALEX_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()


    papers = []

    for item in data.get("results", []):

        # -------------------------
        # 作者
        # -------------------------

        authors = []

        for authorship in item.get(
            "authorships",
            [],
        ):
            author = authorship.get(
                "author",
                {},
            )

            name = author.get(
                "display_name"
            )

            if name:
                authors.append(name)

        # 作者太多时不要全部塞给 LLM
        if len(authors) > 5:
            authors = authors[:5] + ["et al."]


        # -------------------------
        # 期刊 / 会议
        # -------------------------

        primary_location = (
            item.get("primary_location")
            or {}
        )

        source = (
            primary_location.get("source")
            or {}
        )

        source_name = source.get(
            "display_name"
        )


        # -------------------------
        # Open Access
        # -------------------------

        open_access = (
            item.get("open_access")
            or {}
        )


        # -------------------------
        # 整理结果
        # -------------------------
        best_oa_location = item.get("best_oa_location") or {}

        paper_url = (
            primary_location.get("landing_page_url")
            or item.get("doi")
            or item.get("id")
        )

        pdf_url = best_oa_location.get("pdf_url")

        oa_url = (
            best_oa_location.get("landing_page_url")
            or open_access.get("oa_url")
        )
        
        paper = {
            "title": item.get("title"),
            "year": item.get(
                "publication_year"
            ),
            "authors": authors,
            "source": source_name,
            "doi": item.get("doi"),
            "cited_by_count": item.get(
                "cited_by_count",
                0,
            ),
            "is_open_access": open_access.get(
                "is_oa"
            ),
            "openalex_id": item.get("id"),
            "paper_url": paper_url,
            "pdf_url": pdf_url,
            "oa_url": oa_url,
        }

        papers.append(paper)

    return papers