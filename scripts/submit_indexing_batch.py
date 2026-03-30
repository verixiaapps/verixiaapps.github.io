import os
from urllib.request import Request, urlopen

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

BATCH_URLS_FILE = os.path.join(BASE_DIR, "seo-indexing", "batch_urls.txt")
SUBMITTED_URLS_FILE = os.path.join(BASE_DIR, "seo-indexing", "submitted_urls.txt")


def read_lines(filepath: str) -> list[str]:
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def append_lines(filepath: str, lines: list[str]) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    existing = set(read_lines(filepath))

    with open(filepath, "a", encoding="utf-8") as f:
        for line in lines:
            if line not in existing:
                f.write(line + "\n")


def ping_url(url: str) -> None:
    try:
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )
        urlopen(req, timeout=10).read()
        print(f"Pinged: {url}")
    except Exception as e:
        print(f"Failed: {url} | {e}")


def main() -> None:
    batch_urls = read_lines(BATCH_URLS_FILE)

    if not batch_urls:
        print("No URLs in batch.")
        return

    print(f"Submitting {len(batch_urls)} URLs...")

    for url in batch_urls:
        ping_url(url)

    append_lines(SUBMITTED_URLS_FILE, batch_urls)

    print(f"Added {len(batch_urls)} URLs to submitted list.")


if __name__ == "__main__":
    main()