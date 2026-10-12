def rewrite_query(model, user_query: str) -> str:

    prompt = f"""
你是科研论文 RAG 的查询改写器。

请把用户问题改写成一个适合语义检索的英文问题。

要求：
1. 保留用户真正的提问意图，例如 how、what method、what algorithm。
2. 使用论文中常见的专业表达。
3. 如果存在常见同义术语，可以同时保留，例如：
   segmentation / delineation。
4. 删除“根据我的数据库”“帮我查一下”等无关表达。
5. 不回答问题。
6. 不要只输出几个关键词，要输出一句完整、明确的英文检索问题。

用户问题：
{user_query}
"""

    response = model.invoke([
        {
            "role": "user",
            "content": prompt,
        }
    ])

    return response.content.strip()