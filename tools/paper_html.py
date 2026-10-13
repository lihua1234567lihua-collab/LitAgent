import requests


def fetch_paper_html(
    landing_page_url: str,
) -> str | None:

    if not landing_page_url:
        return None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            landing_page_url,
            headers=headers,
            timeout=30,
        )

        print("HTML status:", response.status_code)
        print(
            "HTML content-type:",
            response.headers.get("Content-Type"),
        )

        response.raise_for_status()

        return response.text

    except Exception as e:
        print("HTML ��ȡʧ�ܣ�", e)
        return None