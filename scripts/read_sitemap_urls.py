import os
import re
from urllib.request import urlopen, Request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITEMAP_URL = "https://verixiaapps.com/sitemap.xml"
OUTPUT_FILE = os.path.join(BASE_DIR, "seo-indexing", "urls_to_ping.txt")


def fetch_sitemap(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    with urlopen(req, timeout=30) as response:
        content = response.read().decode("utf-8", errors="replace")
        if not content.strip():
            raise RuntimeError("Fetched sitemap is empty.")
        return content


def extract_urls(xml_text: str) -> list[str]:
    urls = re.findall(r"<loc>(.*?)</loc>", xml_text, flags=re.IGNORECASE | re.DOTALL)
    return [url.strip() for url in urls if url.strip()]


def save_urls(urls: list[str]) -> None:
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for url in urls:
            f.write(url + "\n")


def main() -> None:
    xml_text = fetch_sitemap(SITEMAP_URL)
    urls = extract_urls(xml_text)

    if not urls:
        raise RuntimeError("No URLs found in sitemap.")

    save_urls(urls)
    print(f"Saved {len(urls)} URLs to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()