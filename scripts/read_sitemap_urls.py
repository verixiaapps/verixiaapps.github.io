import re
import sys
from urllib.request import urlopen, Request

SITEMAP_URL = "https://verixiaapps.com/sitemap.xml"


def fetch_sitemap(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    with urlopen(req, timeout=30) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise RuntimeError(f"Failed to fetch sitemap. HTTP status: {status}")

        content = response.read().decode("utf-8", errors="replace")
        if not content.strip():
            raise RuntimeError("Fetched sitemap is empty.")

        return content


def extract_urls(xml_text: str) -> list[str]:
    urls = re.findall(r"<loc>(.*?)</loc>", xml_text, flags=re.IGNORECASE | re.DOTALL)
    clean_urls = [url.strip() for url in urls if url.strip()]
    return clean_urls


def main() -> None:
    try:
        xml_text = fetch_sitemap(SITEMAP_URL)
        urls = extract_urls(xml_text)

        if not urls:
            raise RuntimeError("No URLs found in sitemap.")

        for url in urls:
            print(url)

        print(f"\nTotal URLs found: {len(urls)}", file=sys.stderr)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()