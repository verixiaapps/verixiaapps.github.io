import os

SEED_FILE = "data/seed_keywords.txt"
PATTERN_FILE = "data/patterns.txt"
OUTPUT_FILE = "data/keywords.txt"

MAX_KEYWORDS = 5000
MIN_WORDS = 2
MAX_WORDS = 12

BANNED_SUBSTRINGS = [
    "scam legit",
    "legit scam",
    "safe scam",
    "scam safe",
    "is is ",
    "is this is ",
    "how to spot how to spot",
    "legit or legit",
    "scam or scam",
    "safe or safe",
    "real or real",
    "fake or fake",
]

LOW_VALUE_EXACT = {
    "scam",
    "legit",
    "safe",
    "real",
    "fake",
    "message",
    "email",
    "text",
    "link",
    "website",
    "notification",
}

HIGH_INTENT_MARKERS = [
    " scam",
    " legit",
    " safe",
    " real",
    " fake",
    " phishing",
    " suspicious",
    " dangerous",
    " report ",
    " verify ",
    " trust ",
    " click ",
    " reply ",
    " open ",
    " respond ",
    " what happens ",
    " why did ",
    " who sent ",
    " asking for money",
    " asking for code",
    " urgent action",
    " account is locked",
]

QUESTION_STARTERS = (
    "is ",
    "is this ",
    "did ",
    "was ",
    "should ",
    "what ",
    "why ",
    "who ",
    "how ",
    "check ",
    "report ",
    "got ",
    "just ",
    "anyone ",
    "this ",
)

BAD_PREFIXES = (
    "is is ",
    "is this is ",
    "how to how to ",
)

BAD_DOUBLE_PATTERNS = [
    (" scam", " scam"),
    (" legit", " legit"),
    (" safe", " safe"),
    (" real", " real"),
    (" fake", " fake"),
]


def clean_phrase(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def load_lines(path: str):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        return [clean_phrase(line) for line in f if clean_phrase(line)]


def word_count(text: str) -> int:
    return len(text.split())


def has_duplicate_adjacent_words(text: str) -> bool:
    words = text.split()
    return any(words[i] == words[i + 1] for i in range(len(words) - 1))


def contains_high_intent_marker(text: str) -> bool:
    padded = f" {text} "
    return any(marker in padded for marker in HIGH_INTENT_MARKERS)


def has_bad_double_patterns(text: str) -> bool:
    padded = f" {text} "
    for left, right in BAD_DOUBLE_PATTERNS:
        if padded.count(left) > 1 or padded.count(right) > 1:
            return True
    return False


def is_valid_seed(seed: str) -> bool:
    if not seed:
        return False
    if len(seed) < 2:
        return False
    if "{" in seed or "}" in seed:
        return False
    if seed in LOW_VALUE_EXACT:
        return False
    if word_count(seed) > 8:
        return False
    if has_duplicate_adjacent_words(seed):
        return False
    return True


def is_valid_phrase(phrase: str) -> bool:
    if not phrase:
        return False

    phrase = clean_phrase(phrase)

    if len(phrase) < 5:
        return False
    if "{" in phrase or "}" in phrase:
        return False
    if has_duplicate_adjacent_words(phrase):
        return False
    if word_count(phrase) < MIN_WORDS or word_count(phrase) > MAX_WORDS:
        return False
    if phrase in LOW_VALUE_EXACT:
        return False
    if any(bad in phrase for bad in BANNED_SUBSTRINGS):
        return False
    if any(phrase.startswith(bad) for bad in BAD_PREFIXES):
        return False
    if has_bad_double_patterns(phrase):
        return False

    # Reject phrases that are too bare / low intent
    if not contains_high_intent_marker(phrase) and not phrase.startswith(QUESTION_STARTERS):
        return False

    # Common malformed endings
    if phrase.endswith((" is", " a", " an", " the", " or", " and", " to", " for", " from", " with")):
        return False

    return True


def quality_score(phrase: str):
    phrase = clean_phrase(phrase)
    count = word_count(phrase)

    starts_is_this = phrase.startswith("is this ")
    starts_is = phrase.startswith("is ")
    starts_how = phrase.startswith("how ")
    starts_should = phrase.startswith("should ")
    starts_what = phrase.startswith("what ")
    starts_why = phrase.startswith("why ")
    starts_report = phrase.startswith("report ")
    starts_check = phrase.startswith("check ")

    has_scam = " scam" in f" {phrase}"
    has_legit = " legit" in f" {phrase}"
    has_safe = " safe" in f" {phrase}"
    has_real = " real" in f" {phrase}"
    has_fake = " fake" in f" {phrase}"
    has_channel = any(
        token in f" {phrase} "
        for token in [
            " message ",
            " email ",
            " text ",
            " link ",
            " website ",
            " notification ",
            " whatsapp ",
            " telegram ",
        ]
    )
    has_action = any(
        token in f" {phrase} "
        for token in [
            " click ",
            " reply ",
            " open ",
            " respond ",
            " trust ",
            " verify ",
            " report ",
        ]
    )
    has_post_action = any(
        token in f" {phrase} "
        for token in [
            " what now",
            " what happens",
            " what do i do",
            " did i get",
            " got a ",
            " just received ",
        ]
    )

    # Lower tuple sorts first
    return (
        0 if has_scam else 1,
        0 if has_legit else 1,
        0 if has_safe else 1,
        0 if has_real or has_fake else 1,
        0 if has_channel else 1,
        0 if has_action else 1,
        0 if has_post_action else 1,
        0 if starts_is_this else 1,
        0 if starts_is else 1,
        0 if starts_should else 1,
        0 if starts_what else 1,
        0 if starts_why else 1,
        0 if starts_how else 1,
        0 if starts_check else 1,
        0 if starts_report else 1,
        abs(count - 5),
        len(phrase),
        phrase,
    )


def dedupe_preserve_best(phrases):
    best = {}

    for phrase in phrases:
        phrase = clean_phrase(phrase)
        if not is_valid_phrase(phrase):
            continue

        key = phrase
        current = best.get(key)
        if current is None or quality_score(phrase) < quality_score(current):
            best[key] = phrase

    return list(best.values())


def main():
    os.makedirs("data", exist_ok=True)

    seeds = [seed for seed in load_lines(SEED_FILE) if is_valid_seed(seed)]
    patterns = load_lines(PATTERN_FILE)

    if not seeds:
        print(f"No usable seed keywords found in {SEED_FILE}")
        return

    if not patterns:
        print(f"No patterns found in {PATTERN_FILE}")
        return

    keywords = []

    # Patterns-first generation only.
    # The patterns file already contains the strong intent shapes,
    # so we do not do blunt prefix/suffix mutation here.
    for seed in seeds:
        for pattern in patterns:
            if "{keyword}" not in pattern:
                continue

            phrase = clean_phrase(pattern.replace("{keyword}", seed))
            if is_valid_phrase(phrase):
                keywords.append(phrase)

    keywords = dedupe_preserve_best(keywords)
    keywords = sorted(keywords, key=quality_score)
    keywords = keywords[:MAX_KEYWORDS]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for kw in keywords:
            f.write(kw + "\n")

    print(f"Seeds loaded: {len(seeds)}")
    print(f"Patterns loaded: {len(patterns)}")
    print(f"Generated {len(keywords)} keywords")


if __name__ == "__main__":
    main()