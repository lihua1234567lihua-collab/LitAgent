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
        best_oa_location = data.get("best_oa_location") or {}
        pdf_url = best_oa_location.get("pdf_url")
        landing_page_url = best_oa_location.get("landing_page_url")
        return {
            "title": data.get("title"),
            "doi": data.get("doi"),
            "year": data.get("publication_year"),
            "abstract": abstract,
            "openalex_id": openalex_id,
            "pdf_url":pdf_url,
        }

    except Exception as e:
        return {
            "title": paper.get("title"),
            "doi": paper.get("doi"),
            "openalex_id": openalex_id,
            "error": str(e),
        }
def abstract_is_sufficient(
    abstract: str,
    user_query: str,
    model,
) -> bool:
    """
    判断摘要是否足以完成当前任务。
    先做硬判断，再让 LLM 判断语义是否充分。
    """

    # 1. 摘要为空
    if not abstract:
        return False

    # 2. 摘要过短
    if len(abstract.strip()) < 300:
        return False

    # 3. 让 LLM 判断摘要内容是否足够回答当前问题
    prompt = f"""
你需要判断一篇论文的摘要，是否包含足够的信息来完成当前任务。

当前任务：
{user_query}

论文摘要：
{abstract}

判断标准：
- 如果仅根据这个摘要，就能够较可靠地完成当前任务，返回 sufficient
- 如果摘要缺少完成任务所需的关键信息，返回 insufficient
- 不要根据常识补充摘要中没有的信息
- 不要解释

只能返回：

sufficient
insufficient
"""

    response = model.invoke(prompt)

    decision = response.content.strip().lower()

    if decision == "sufficient":
        return True

    return False