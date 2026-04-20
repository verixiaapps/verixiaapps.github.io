import os
import re
from collections import Counter
SEED_FILE = "data/token_seed_keywords.txt"
PATTERN_FILE = "data/token_patterns.txt"
OUTPUT_FILE = "data/token_keywords.txt"
MAX_KEYWORDS = 5000
MIN_WORDS = 2
MAX_WORDS = 12
BANNED_SUBSTRINGS = [
    "token token",
    "coin coin",
    "buy buy",
    "safe safe",
    "legit legit",
    "risky risky",
    "rug rug",
    "honeypot honeypot",
    "is is ",
    "is this is ",
    "should i buy should i buy",
    "token risk token risk",
    "safe or safe",
    "legit or legit",
    "risky or risky",
]
LOW_VALUE_EXACT = {
    "token",
    "coin",
    "crypto",
    "buy",
    "safe",
    "legit",
    "risky",
    "rug",
    "honeypot",
    "liquidity",
    "volume",
    "fdv",
    "market cap",
    "pair age",
    "price",
    "chart",
    "token risk",
}
HIGH_INTENT_MARKERS = [
    "token risk",
    "safe",
    "legit",
    "risky",
    "rug",
    "rug pull",
    "honeypot",
    "should i buy",
    "buy now",
    "worth buying",
    "good investment",
    "safe to buy",
    "liquidity",
    "volume",
    "pair age",
    "fdv",
    "market cap",
    "buyers",
    "sellers",
    "slippage",
    "price action",
    "price change",
    "entry",
    "exit",
]
QUESTION_STARTERS = (
    "is ",
    "is this ",
    "should ",
    "what ",
    "why ",
    "when ",
    "where ",
    "how ",
    "check ",
    "can ",
)
BAD_PREFIXES = (
    "is is ",
    "is this is ",
    "should i buy should i buy ",
    "how to how to ",
)
STRONG_SIGNAL_TERMS = {
    "token risk",
    "safe",
    "legit",
    "risky",
    "rug",
    "rug pull",
    "honeypot",
    "buy",
    "entry",
    "exit",
    "liquidity",
    "volume",
    "pair age",
    "fdv",
    "market cap",
    "buyers",
    "sellers",
    "slippage",
    "price action",
    "price change",
    "solana",
    "ethereum",
    "eth",
    "base",
    "bsc",
    "arbitrum",
    "polygon",
    "avalanche",
    "blast",
    "sui",
    "ton",
    "tron",
    "bitcoin",
}
CHAIN_TERMS = {
    "solana",
    "ethereum",
    "eth",
    "base",
    "bsc",
    "arbitrum",
    "polygon",
    "avalanche",
    "blast",
    "sui",
    "ton",
    "tron",
    "bitcoin",
}
METRIC_TERMS = {
    "liquidity",
    "volume",
    "pair age",
    "fdv",
    "market cap",
    "buyers",
    "sellers",
    "slippage",
    "price action",
    "price change",
}
BUY_TERMS = {
    "should i buy",
    "buy now",
    "worth buying",
    "good investment",
    "safe to buy",
    "entry",
    "exit",
}
SAFETY_TERMS = {
    "safe",
    "legit",
    "risky",
    "rug",
    "rug pull",
    "honeypot",
}
STOPWORDS = {
    "is",
    "this",
    "a",
    "an",
    "the",
    "to",
    "for",
    "of",
    "and",
    "or",
    "with",
    "on",
    "in",
    "can",
    "should",
    "what",
    "why",
    "when",
    "where",
    "how",
    "i",
    "now",
}
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
def contains_term_phrase(text: str, needle: str) -> bool:
    return re.search(rf"(^|[^a-z0-9]){re.escape(needle)}([^a-z0-9]|$)", text) is not None
def contains_high_intent_marker(text: str) -> bool:
    return any(contains_term_phrase(text, marker) for marker in HIGH_INTENT_MARKERS)
def has_bad_double_patterns(text: str) -> bool:
    words = text.split()
    if len(words) < 4:
        return False
    bigrams = [" ".join(words[i:i + 2]) for i in range(len(words) - 1)]
    bigram_counts = Counter(bigrams)
    for bigram, count in bigram_counts.items():
        if count > 1 and bigram not in {"of the", "in the", "to the"}:
            return True
    return False
def has_excessive_repeated_terms(text: str) -> bool:
    words = text.split()
    meaningful = [w for w in words if w not in STOPWORDS]
    if not meaningful:
        return True
    counts = Counter(meaningful)
    max_count = max(counts.values())
    if max_count >= 3:
        return True
    repeated_unique = sum(1 for count in counts.values() if count > 1)
    if repeated_unique >= 2:
        return True
    return False
def has_signal_term(text: str) -> bool:
    return any(contains_term_phrase(text, term) for term in STRONG_SIGNAL_TERMS)
def phrase_signature(text: str) -> str:
    words = text.split()
    normalized = []
    for word in words:
        if word in STOPWORDS:
            continue
        normalized.append(word)
    return " ".join(normalized)
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
    if has_excessive_repeated_terms(seed):
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
    if not re.search(r"[a-z]", phrase):
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
    if has_excessive_repeated_terms(phrase):
        return False
    if not contains_high_intent_marker(phrase) and not phrase.startswith(QUESTION_STARTERS):
        return False
    if not has_signal_term(phrase):
        return False
    if phrase.endswith((" is", " a", " an", " the", " or", " and", " to", " for", " from", " with")):
        return False
    return True
def quality_score(phrase: str):
    phrase = clean_phrase(phrase)
    count = word_count(phrase)
    starts_is_this = phrase.startswith("is this ")
    starts_is = phrase.startswith("is ")
    starts_should = phrase.startswith("should ")
    starts_what = phrase.startswith("what ")
    starts_why = phrase.startswith("why ")
    starts_how = phrase.startswith("how ")
    starts_check = phrase.startswith("check ")
    starts_can = phrase.startswith("can ")
    has_token_risk = contains_term_phrase(phrase, "token risk")
    has_buy = any(contains_term_phrase(phrase, term) for term in BUY_TERMS)
    has_safety = any(contains_term_phrase(phrase, term) for term in SAFETY_TERMS)
    has_honeypot = contains_term_phrase(phrase, "honeypot")
    has_rug = contains_term_phrase(phrase, "rug") or contains_term_phrase(phrase, "rug pull")
    has_metrics = any(contains_term_phrase(phrase, term) for term in METRIC_TERMS)
    has_chain = any(contains_term_phrase(phrase, term) for term in CHAIN_TERMS)
    has_trade_terms = any(contains_term_phrase(phrase, term) for term in {"entry", "exit", "swap", "buy"})
    signature_len = len(phrase_signature(phrase).split())
    return (
        0 if has_buy else 1,
        0 if has_safety else 1,
        0 if has_honeypot or has_rug else 1,
        0 if has_metrics else 1,
        0 if has_chain else 1,
        0 if has_token_risk else 1,
        0 if has_trade_terms else 1,
        0 if starts_should else 1,
        0 if starts_is_this else 1,
        0 if starts_is else 1,
        0 if starts_what else 1,
        0 if starts_why else 1,
        0 if starts_how else 1,
        0 if starts_check else 1,
        0 if starts_can else 1,
        abs(count - 5),
        abs(signature_len - 4),
        len(phrase),
        phrase,
    )
def choose_best_phrase(phrases):
    return sorted(phrases, key=quality_score)[0]
def dedupe_preserve_best(phrases):
    exact_best = {}
    signature_groups = {}
    for phrase in phrases:
        phrase = clean_phrase(phrase)
        if not is_valid_phrase(phrase):
            continue
        current = exact_best.get(phrase)
        if current is None or quality_score(phrase) < quality_score(current):
            exact_best[phrase] = phrase
    for phrase in exact_best.values():
        signature = phrase_signature(phrase)
        if not signature:
            continue
        signature_groups.setdefault(signature, []).append(phrase)
    best_phrases = []
    for group in signature_groups.values():
        best_phrases.append(choose_best_phrase(group))
    return best_phrases
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
    print(f"Generated {len(keywords)} token risk keywords")
if __name__ == "__main__":
    main()