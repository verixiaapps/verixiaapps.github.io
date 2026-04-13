import os
from typing import List

MASTER_DIR = os.getenv("MASTER_DIR", "data/used_keywords_master")
MASTER_FILE = os.getenv("MASTER_FILE", os.path.join(MASTER_DIR, "used_keywords_master.txt"))

SOURCE_FILES = [
    os.getenv("SOURCE_A", "data/generated_keywords.txt"),
    os.getenv("SOURCE_B", "data/generated_keywords_b.txt"),
    os.getenv("SOURCE_C", "data/generated_keywords_c.txt"),
]


def normalize_keyword(keyword: str) -> str:
    return " ".join(str(keyword).lower().split())


def read_keywords(path: str) -> List[str]:
    if not os.path.exists(path):
        print(f"Missing source file: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f]

    return [line for line in lines if line]


def dedupe_preserve_order(keywords: List[str]) -> List[str]:
    seen = set()
    output = []

    for keyword in keywords:
        normalized = normalize_keyword(keyword)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        output.append(keyword)

    return output


def main() -> None:
    print("Building used keywords master file...")

    all_keywords: List[str] = []
    total_raw = 0

    for source in SOURCE_FILES:
        keywords = read_keywords(source)
        total_raw += len(keywords)
        print(f"{source}: {len(keywords)} keywords")
        all_keywords.extend(keywords)

    unique_keywords = dedupe_preserve_order(all_keywords)
    duplicate_count = total_raw - len(unique_keywords)

    os.makedirs(MASTER_DIR, exist_ok=True)

    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        for keyword in unique_keywords:
            f.write(keyword + "\n")

    print(f"\nTotal raw keywords: {total_raw}")
    print(f"Total unique keywords: {len(unique_keywords)}")
    print(f"Duplicates removed: {duplicate_count}")
    print(f"Saved to: {MASTER_FILE}")
    print("Done.")


if __name__ == "__main__":
    main()