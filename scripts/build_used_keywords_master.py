import os

MASTER_DIR = os.getenv("MASTER_DIR", "data/used_keywords_master")
MASTER_FILE = os.getenv("MASTER_FILE", "data/used_keywords_master/used_keywords_master.txt")

SOURCE_FILES = [
    os.getenv("SOURCE_A", "data/generated_keywords.txt"),
    os.getenv("SOURCE_B", "data/generated_keywords_b.txt"),
    os.getenv("SOURCE_C", "data/generated_keywords_c.txt"),
]


def read_keywords(path):
    if not os.path.exists(path):
        print(f"Missing source file: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    return [line for line in lines if line]


def normalize_keyword(kw: str) -> str:
    return " ".join(kw.lower().split())


def main():
    print("Building used keywords master file...")

    all_keywords = []
    seen = set()

    for source in SOURCE_FILES:
        keywords = read_keywords(source)
        print(f"{source}: {len(keywords)} keywords")

        for kw in keywords:
            normalized = normalize_keyword(kw)
            if normalized not in seen:
                seen.add(normalized)
                all_keywords.append(kw)

    os.makedirs(MASTER_DIR, exist_ok=True)

    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        for kw in all_keywords:
            f.write(kw + "\n")

    print(f"\nTotal unique keywords: {len(all_keywords)}")
    print(f"Saved to: {MASTER_FILE}")
    print("Done.")


if __name__ == "__main__":
    main()