'''负责和java通信'''
import httpx


KNOWLEDGE_BACKEND_URL = "http://localhost:8080"


async def get_paper_by_id(paper_id: int) -> dict:
    url = f"{KNOWLEDGE_BACKEND_URL}/papers/{paper_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

    
async def add_paper_to_topic(
    topic_id: int,
    doi: str,
    title: str,
    pdf_path: str | None = None,
) -> dict:

    url = f"{KNOWLEDGE_BACKEND_URL}/topics/{topic_id}/papers"

    payload = {
        "doi": doi,
        "title": title,
    }

    if pdf_path is not None:
        payload["pdfPath"] = pdf_path

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
        )

        response.raise_for_status()
        return response.json()

async def get_user_topics(user_id: int) -> list[dict]:

    url = f"{KNOWLEDGE_BACKEND_URL}/users/{user_id}/topics"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        response.raise_for_status()

        return response.json()

async def get_topic_papers(
    topic_id: int,
) -> list[dict]:

    url = f"{KNOWLEDGE_BACKEND_URL}/topicpaper/{topic_id}/papers"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        response.raise_for_status()

        return response.json()

async def get_user_papers(user_id: int) -> list[dict]:

    url = f"{KNOWLEDGE_BACKEND_URL}/users/{user_id}/papers"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        return response.json()