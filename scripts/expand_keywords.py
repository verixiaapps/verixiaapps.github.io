import os
import itertools

SEED_FILE = "data/seed_keywords.txt"
PATTERN_FILE = "data/patterns.txt"
OUTPUT_FILE = "data/keywords.txt"

# optional modifiers to expand search intent
PREFIXES = [
    "",
    "is ",
    "is this ",
    "how to spot ",
]

SUFFIXES = [
    "",
    " scam",
    " legit",
]

MAX_KEYWORDS = 5000  # safety cap


def load_lines(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def clean_phrase(text):
    text = " ".join(text.split())  # remove extra spaces
    return text.strip()


def is_valid(phrase):
    # basic filters to avoid junk
    if len(phrase) < 5:
        return False
    if phrase.count("{") > 0:
        return False
    return True


def main():
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

    # base pattern expansion
    for seed in seeds:
        for pattern in patterns:
            phrase = pattern.replace("{keyword}", seed)
            phrase = clean_phrase(phrase)
            if is_valid(phrase):
                keywords.add(phrase)

    # intent expansion (adds more real search variations)
    expanded = set()

    for kw in keywords:
        for pre, suf in itertools.product(PREFIXES, SUFFIXES):
            phrase = clean_phrase(f"{pre}{kw}{suf}")
            if is_valid(phrase):
                expanded.add(phrase)

    keywords.update(expanded)

    # dedupe + sort
    keywords = sorted(list(keywords))

    # cap to avoid explosion
    keywords = keywords[:MAX_KEYWORDS]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for kw in keywords:
            f.write(kw + "\n")

    print(f"Generated {len(keywords)} keywords")


if __name__ == "__main__":
    main()