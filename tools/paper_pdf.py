import os
import requests


def download_pdf(
    pdf_url: str,
    filename: str,
    referer_url: str | None = None,
) -> str | None:

    os.makedirs("data/papers", exist_ok=True)

    save_path = os.path.join(
        "data",
        "papers",
        filename,
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "application/pdf,text/html,"
            "application/xhtml+xml;q=0.9,*/*;q=0.8"
        ),
    }

    try:
        session = requests.Session()

        # 先访问论文页面，获取 cookie
        if referer_url:
            session.get(
                referer_url,
                headers=headers,
                timeout=30,
            )

            headers["Referer"] = referer_url

        response = session.get(
            pdf_url,
            headers=headers,
            timeout=30,
            allow_redirects=True,
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        )

        if "pdf" not in content_type.lower():
            print(
                "返回内容不是 PDF:",
                content_type,
            )
            return None

        with open(save_path, "wb") as f:
            f.write(response.content)

        return save_path

    except Exception as e:
        print("PDF 下载失败：", e)
        return None