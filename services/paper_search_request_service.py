from pydantic import BaseModel, Field


class PaperSearchRequest(BaseModel):
    query: str = Field(description="英文科研搜索关键词")
    top_k: int = Field(default=5, ge=1, le=10)
    start_year: int | None = None
    end_year: int | None = None


def build_search_request(model, user_query: str) -> PaperSearchRequest:
    """将用户的自然语言转换为结构化论文检索条件。"""

    structured_model = model.with_structured_output(
        PaperSearchRequest,
        method="function_calling",
    )

    prompt = f"""
        你是学术论文搜索条件解析器。

        请从用户输入中提取：
        1. query：简洁的英文科研关键词，保留研究对象、方法和数据类型。
        2. top_k：用户要求的论文数量，未指定则为 5。
        3. start_year：明确指定的起始年份，未指定则为 null。
        4. end_year：明确指定的结束年份，未指定则为 null。

        要求：
        - 不要将年份、论文数量加入 query。
        - 不要自行编造用户未指定的年份。
        - 如果用户要求超过 10 篇，当前单次检索最多设置为 10 篇。
        - 如果指定年份范围，start_year 不得大于 end_year。

        用户输入：
        {user_query}
        """

    return structured_model.invoke(prompt)