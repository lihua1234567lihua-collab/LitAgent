'''意图识别与分流：判断用户需要普通回答、论文搜索还是本地RAG等'''
from typing import Literal
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder


class RouteDecision(BaseModel):
    route: Literal["direct_answer", "paper_search","local_rag","planner"]
    paper_scope: Literal[
        "current_paper",
        "topic",
        "user_library",
        "none"
    ] = "none"

    reason: str


def create_router(model):
    '''意图识别与分流：判断用户需要普通回答、论文搜索还是本地RAG等'''
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            你是 LitAgent 科研助手的智能路由器。

            你的任务是结合用户当前问题和对话历史，
            同时判断：
            1. route：用户需要执行什么任务。
            2. paper_scope：用户希望查询哪部分论文。

            【一、任务路由 route】

            direct_answer：
            用户询问普通概念、技术原理或通用知识，
            不需要查询论文。

            local_rag：
            用户希望查询、分析、总结或比较已有论文，
            包括已上传、已收藏或 Topic 中的论文。

            paper_search：
            用户明确要求从外部搜索、查找或推荐新论文。

            planner：
            用户任务需要多个连续步骤才能完成，
            例如搜索新论文、阅读全文并分析研究局限。

            【二、论文检索范围 paper_scope】

            current_paper：
            用户正在讨论某一篇具体论文。
            包括：
            - 明确询问刚上传的论文。
            - 延续上文，继续讨论同一篇论文。
            - 使用“它”“这篇论文”等指代，且根据历史能确定对象。

            topic：
            用户明确要求查询某个 Topic 下的论文集合。

            user_library：
            用户希望查询整个个人论文库，
            或对多篇已收藏论文进行综合分析。

            none：
            当前任务不涉及本地论文检索范围，
            例如普通知识问答或外部论文搜索。

            【三、上下文判断规则】

            1. 必须结合当前问题和对话历史理解用户意图。
            2. 如果用户正在连续讨论同一篇论文，
            即使当前问题没有重复论文标题，
            也应该判断为 current_paper。
            3. 不要仅通过固定关键词判断检索范围。
            4. 如果用户明确切换研究对象或查询范围，
            以当前问题为准。
            5. 如果用户要求分析整个论文库，
            不要因为历史中讨论过某篇论文，
            就继续使用 current_paper。
            6. 如果无法确定当前问题指向哪篇具体论文，
            不要强行判断为 current_paper。
            7. 不要推测或生成论文 ID。
            8. 论文 ID 由后续程序根据会话状态确定。

            【四、判断示例】

            用户：帮我分析刚刚上传的论文。
            route = local_rag
            paper_scope = current_paper

            历史：用户正在讨论一篇红树林碳储量论文。
            用户：那作者具体采用了什么方法？
            route = local_rag
            paper_scope = current_paper

            历史：用户正在讨论一篇论文。
            用户：总结我收藏的所有论文。
            route = local_rag
            paper_scope = user_library

            用户：分析 LiDAR Topic 下的研究局限。
            route = local_rag
            paper_scope = topic

            用户：搜索最近两年的树冠分割论文。
            route = paper_search
            paper_scope = none

            用户：什么是 Transformer？
            route = direct_answer
            paper_scope = none

            【五、输出要求】

            严格按照 RouteDecision 结构化输出。
            route 和 paper_scope 必须分别判断。
            reason 简要说明判断依据。
            """
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    return prompt | model.with_structured_output(RouteDecision,method="function_calling")##llm返回结构化的route类型
    return prompt | model.with_structured_output(RouteDecision,method="function_calling")##llm返回结构化的route类型