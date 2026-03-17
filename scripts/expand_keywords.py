import os

SEED_FILE = "data/seed_keywords.txt"
PATTERN_FILE = "data/patterns.txt"
OUTPUT_FILE = "data/keywords.txt"


def load_lines(path):
    """Load non-empty lines from a file, lowercase and stripped."""
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def main():
    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)

    seeds = load_lines(SEED_FILE)
    patterns = load_lines(PATTERN_FILE)

    if not seeds:
        print(f"No seed keywords found in {SEED_FILE}")
        return

    if not patterns:
        print(f"No patterns found in {PATTERN_FILE}")
        return

    keywords = set()

    for seed in seeds:
        for pattern in patterns:
            phrase = pattern.replace("{keyword}", seed).strip().lower()
            keywords.add(phrase)

    keywords = sorted(keywords)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for kw in keywords:
            f.write(kw + "\n")

    print(f"Generated {len(keywords)} keywords")


if __name__ == "__main__":
    main()