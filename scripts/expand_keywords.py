import os
import itertools

SEED_FILE = "data/seed_keywords.txt"
PATTERN_FILE = "data/patterns.txt"
OUTPUT_FILE = "data/keywords.txt"

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

MAX_KEYWORDS = 5000

STRONG_INTENT_MARKERS = [
    " scam",
    " legit",
    "is ",
    "is this ",
    "how to spot ",
]

BANNED_SUBSTRINGS = [
    "scam legit",
    "legit scam",
    "is is ",
    "is this is ",
    "how to spot how to spot",
]


def clean_phrase(text):
    return " ".join(text.strip().lower().split())


def load_lines(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        return [clean_phrase(line) for line in f if clean_phrase(line)]


def word_count(text):
    return len(text.split())


def has_duplicate_adjacent_words(text):
    words = text.split()
    return any(words[i] == words[i + 1] for i in range(len(words) - 1))


def contains_intent_marker(text):
    return any(marker in text for marker in STRONG_INTENT_MARKERS)


def is_valid(phrase):
    if not phrase:
        return False
    if len(phrase) < 5:
        return False
    if "{" in phrase or "}" in phrase:
        return False
    if has_duplicate_adjacent_words(phrase):
        return False
    if phrase.count(" scam") > 1:
        return False
    if phrase.count(" legit") > 1:
        return False
    if word_count(phrase) > 10:
        return False
    if any(bad in phrase for bad in BANNED_SUBSTRINGS):
        return False
    return True


def is_valid_combo(base_keyword, prefix, suffix):
    phrase = clean_phrase(f"{prefix}{base_keyword}{suffix}")

    if not is_valid(phrase):
        return False

    if prefix in {"is ", "is this "} and suffix == "":
        return False

    if prefix == "how to spot " and suffix != "":
        return False

    if prefix and contains_intent_marker(base_keyword):
        if (
            base_keyword.startswith("is ")
            or base_keyword.startswith("is this ")
            or base_keyword.startswith("how to spot ")
        ):
            return False

    if suffix == " scam" and " scam" in base_keyword:
        return False

    if suffix == " legit" and " legit" in base_keyword:
        return False

    if suffix == " legit" and " scam" in base_keyword:
        return False

    return True


def quality_score(phrase):
    count = word_count(phrase)

    starts_is_this = phrase.startswith("is this ")
    starts_is = phrase.startswith("is ")
    starts_how = phrase.startswith("how to spot ")
    has_scam = " scam" in f" {phrase}"
    has_legit = " legit" in f" {phrase}"

    return (
        0 if has_scam else 1,
        0 if starts_is_this else 1,
        0 if starts_is else 1,
        0 if has_legit else 1,
        1 if starts_how else 0,
        abs(count - 4),
        len(phrase),
        phrase,
    )


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

    for seed in seeds:
        for pattern in patterns:
            phrase = clean_phrase(pattern.replace("{keyword}", seed))
            if is_valid(phrase):
                keywords.add(phrase)

    expanded = set()

    for kw in keywords:
        for pre, suf in itertools.product(PREFIXES, SUFFIXES):
            if not is_valid_combo(kw, pre, suf):
                continue

            phrase = clean_phrase(f"{pre}{kw}{suf}")
            if is_valid(phrase):
                expanded.add(phrase)

    keywords.update(expanded)

    keywords = sorted(keywords, key=quality_score)
    keywords = keywords[:MAX_KEYWORDS]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for kw in keywords:
            f.write(kw + "\n")

    print(f"Generated {len(keywords)} keywords")


if __name__ == "__main__":
    main()