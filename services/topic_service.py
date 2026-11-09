from tools.knowledge_backend_client import get_user_topics


async def resolve_topic_id(
    user_id: int,
    topic_name: str,
) -> int:

    topics = await get_user_topics(user_id)

    for topic in topics:
        if topic["name"].lower() == topic_name.lower():
            return topic["id"]

    raise ValueError(f"Topic not found: {topic_name}")

async def resolve_topic_from_query(
    user_id: int,
    user_query: str,
) -> int | None:

    topics = await get_user_topics(user_id)

    matched = [
        topic for topic in topics
        if topic.get("name")
        and topic["name"].strip().casefold() in user_query.casefold()
    ]

    if len(matched) > 1:
        raise ValueError("Multiple topics matched")

    if not matched:
        return None

    return matched[0]["id"]