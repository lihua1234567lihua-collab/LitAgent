from tools.paper_html import fetch_paper_html


url = "https://www.mdpi.com/1999-4907/12/2/131"

html = fetch_paper_html(url)

if html:
    print("HTML 长度:", len(html))