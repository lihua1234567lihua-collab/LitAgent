def build_search_query(model, user_query: str) -> str:
    prompt = f"""
        Extract concise English academic search keywords from the user request.

        Requirements:
        - Keep the research topic, object, method, and data type.
        - Translate Chinese into English.
        - Return only one keyword phrase.
        - Do not return a question.
        - Do not add punctuation or explanation.

User request:
{user_query}
"""
    response = model.invoke(prompt)
    return response.content.strip().rstrip("?.。？")