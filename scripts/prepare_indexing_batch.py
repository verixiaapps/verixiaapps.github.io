import json
import os
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

URLS_TO_PING_FILE = os.path.join(BASE_DIR, "seo-indexing", "urls_to_ping.txt")
SUBMITTED_URLS_FILE = os.path.join(BASE_DIR, "seo-indexing", "submitted_urls.txt")
BATCH_URLS_FILE = os.path.join(BASE_DIR, "seo-indexing", "batch_urls.txt")
LAST_RUN_FILE = os.path.join(BASE_DIR, "seo-indexing", "last_run.json")

BATCH_SIZE = int(os.getenv("INDEXING_BATCH_SIZE", "200"))


def ensure_parent_dir(filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)


def ensure_file(filepath: str, default_content: str = "") -> None:
    ensure_parent_dir(filepath)
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(default_content)


def read_lines(filepath: str) -> list[str]:
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    seen = set()
    deduped = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            deduped.append(line)

    return deduped


def write_lines(filepath: str, lines: list[str]) -> None:
    ensure_parent_dir(filepath)
    with open(filepath, "w", encoding="utf-8") as f:
        if lines:
            f.write("\n".join(lines) + "\n")
        else:
            f.write("")


def write_json(filepath: str, payload: dict) -> None:
    ensure_parent_dir(filepath)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> None:
    if BATCH_SIZE <= 0:
        raise RuntimeError(f"INDEXING_BATCH_SIZE must be greater than 0. Got: {BATCH_SIZE}")

    ensure_file(URLS_TO_PING_FILE)
    ensure_file(SUBMITTED_URLS_FILE)
    ensure_file(BATCH_URLS_FILE)
    ensure_file(LAST_RUN_FILE, "{}\n")

    all_urls = read_lines(URLS_TO_PING_FILE)
    submitted_urls = set(read_lines(SUBMITTED_URLS_FILE))

    remaining_urls = [url for url in all_urls if url not in submitted_urls]
    batch_urls = remaining_urls[:BATCH_SIZE]

    write_lines(BATCH_URLS_FILE, batch_urls)

    payload = {
        "timestamp_utc": utc_now_iso(),
        "batch_size_requested": BATCH_SIZE,
        "total_urls_in_sitemap_list": len(all_urls),
        "already_submitted_count": len(submitted_urls),
        "remaining_unsubmitted_count": len(remaining_urls),
        "batch_urls_count": len(batch_urls),
    }

    if batch_urls:
        payload["first_batch_url"] = batch_urls[0]
        payload["last_batch_url"] = batch_urls[-1]

    write_json(LAST_RUN_FILE, payload)

    print(f"Total URLs loaded: {len(all_urls)}")
    print(f"Already submitted: {len(submitted_urls)}")
    print(f"Remaining unsubmitted: {len(remaining_urls)}")
    print(f"Prepared batch count: {len(batch_urls)}")
    print(f"Batch file written to: {BATCH_URLS_FILE}")
    print(f"Run metadata written to: {LAST_RUN_FILE}")


if __name__ == "__main__":
    main()