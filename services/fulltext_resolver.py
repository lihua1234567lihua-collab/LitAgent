def abstract_is_sufficient(
    abstract: str,
    task: str,
    model,
) -> bool:
    """
    判断摘要是否足以完成当前任务。
    """

    if not abstract:
        return False

    if len(abstract.strip()) < 300:
        return False

    prompt = f"""
判断下面这篇论文的摘要是否足以完成当前任务。

当前任务：
{task}

摘要：
{abstract}

规则：
- 如果只根据摘要就能较可靠地完成任务，返回 sufficient
- 如果缺少关键方法、数据集、实验结果、局限性等信息，返回 insufficient
- 不允许根据常识补充摘要中没有的信息
- 不要解释

只能返回：
sufficient
insufficient
"""

    response = model.invoke(prompt)

    decision = response.content.strip().lower()

    return decision == "sufficient"


def resolve_paper_content(
    paper: dict,
    task: str,
    model,
) -> dict:
    """
    决定当前任务应该使用摘要还是进一步获取全文。
    """

    abstract = paper.get("abstract", "")

    if abstract_is_sufficient(
        abstract,
        task,
        model,
    ):
        return {
            "paper": paper,
            "task": task,
            "content_type": "abstract",
            "content": abstract,
            "pdf_path": None,
            "status": "ready",
        }

    return {
        "paper": paper,
        "task": task,
        "content_type": None,
        "content": None,
        "pdf_path": None,
        "status": "need_fulltext",
    }