from typing import Literal
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate


class RouteDecision(BaseModel):
    route: Literal["direct_answer", "paper_search","local_rag","planner"]
    reason: str


def create_router(model):
    prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        你是科研助手的路由器。

        你只能选择以下个路由之一：

        1. direct_answer
        用户询问普通知识、概念解释，不需要查询论文。

        2. local_rag
        用户询问科研方法、实验结果、论文内容，
        并且适合从本地论文知识库中查找证据后回答。

        3. paper_search
        用户明确要求查找、搜索、推荐论文，
        例如“找几篇论文”“最新有哪些研究”“推荐相关文献”。
        
        4. planner
        用户的任务需要多个连续步骤才能完成，
        例如：
        “找3篇论文，并比较它们的方法、数据集和优缺点”
        “查找相关研究，再总结目前存在的问题和未来趋势”

        只选择最合适的一个路由。
        """
    ),
    ("human", "{question}")])

    return prompt | model.with_structured_output(RouteDecision,method="function_calling")