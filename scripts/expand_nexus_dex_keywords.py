import os
import re
from collections import Counter

SEED_FILE = "data/nexus_dex_seed_keywords.txt"
PATTERN_FILE = "data/nexus_dex_patterns.txt"
OUTPUT_FILE = "data/nexus_dex_keywords.txt"
MAX_KEYWORDS = 5000
MIN_WORDS = 2
MAX_WORDS = 12

BANNED_SUBSTRINGS = [
    "perps perps",
    "perp perp",
    "perpetual perpetual",
    "swap swap",
    "buy buy",
    "sell sell",
    "trade trade",
    "wallet wallet",
    "leverage leverage",
    "long long",
    "short short",
    "is is ",
    "no no ",
    "no kyc no kyc",
    "kyc kyc",
    "nexus dex nexus dex",
    "hyperliquid hyperliquid",
    "xstocks xstocks",
    "stocks stocks",
    "stock stock",
    "tokenized tokenized",
    "whale whale",
    "launch launch",
    "self custodial self custodial",
    "non custodial non custodial",
    "wallet based wallet based",
    "perps trading perps trading",
    "wallet trading wallet trading",
    "swap on swap",
    "buy on buy",
    "from wallet from wallet",
    "on nexus dex on nexus dex",
]

LOW_VALUE_EXACT = {
    "perps",
    "perp",
    "perpetual",
    "swap",
    "buy",
    "sell",
    "trade",
    "trading",
    "wallet",
    "mobile",
    "app",
    "dex",
    "cex",
    "kyc",
    "leverage",
    "long",
    "short",
    "hedge",
    "stock",
    "stocks",
    "equity",
    "equities",
    "xstocks",
    "xstock",
    "tokenized",
    "whale",
    "launch",
    "no kyc",
    "nexus dex",
    "perps trading",
    "wallet trading",
    "self custodial",
    "non custodial",
}

HIGH_INTENT_MARKERS = [
    "perps",
    "perp",
    "perpetual",
    "leverage",
    "leveraged",
    "long",
    "short",
    "hedge",
    "no kyc",
    "without kyc",
    "no signup",
    "no verification",
    "self custodial",
    "non custodial",
    "wallet based",
    "mobile",
    "phantom",
    "backpack",
    "solflare",
    "hyperliquid",
    "whale",
    "smart money",
    "insider",
    "deployer",
    "sniper",
    "launch",
    "launchpad",
    "bonding curve",
    "swap",
    "buy",
    "trade",
    "dex aggregator",
    "best price",
    "nexus dex",
    # xStocks / tokenized stocks
    "xstocks",
    "xstock",
    "tokenized stock",
    "tokenized stocks",
    "tokenized equity",
    "tokenized equities",
    "onchain stocks",
    "stocks on solana",
    "stocks as spl",
    "buy stocks",
    "trade stocks",
    "stocks no kyc",
    "stocks without",
    "stocks 24",
    "stocks weekend",
    "stocks after hours",
    "us stocks",
    "aapl",
    "tsla",
    "nvda",
    "msft",
    "googl",
    "amzn",
    "mstr",
    "spy",
    "qqq",
    "aaplx",
    "tslax",
    "nvdax",
    "spyx",
    "qqqx",
    "backed finance",
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
    "can i can i ",
)

STRONG_SIGNAL_TERMS = {
    "perps",
    "perp",
    "perpetual",
    "leverage",
    "leveraged",
    "long",
    "short",
    "hedge",
    "no kyc",
    "without kyc",
    "no signup",
    "self custodial",
    "non custodial",
    "wallet based",
    "phantom",
    "backpack",
    "solflare",
    "hyperliquid",
    "whale",
    "smart money",
    "insider",
    "deployer",
    "sniper",
    "launch",
    "launchpad",
    "bonding curve",
    "swap",
    "buy",
    "trade",
    "dex",
    "solana",
    "ethereum",
    "eth",
    "sol",
    "btc",
    "bitcoin",
    "bonk",
    "wif",
    "pepe",
    "doge",
    "hype",
    "popcat",
    "trump",
    "jup",
    "ray",
    "spx",
    "fartcoin",
    # xStocks tickers + concepts
    "xstocks",
    "xstock",
    "tokenized",
    "stocks",
    "stock",
    "equity",
    "equities",
    "onchain",
    "aapl",
    "tsla",
    "nvda",
    "msft",
    "googl",
    "amzn",
    "meta",
    "mstr",
    "spy",
    "qqq",
    "nflx",
    "coin",
    "hood",
    "crcl",
    "aaplx",
    "tslax",
    "nvdax",
    "spyx",
    "qqqx",
}

CHAIN_TERMS = {
    "solana",
    "ethereum",
    "eth",
    "sol",
    "bitcoin",
    "btc",
    "arbitrum",
    "polygon",
    "base",
    "bsc",
    "avalanche",
    "blast",
    "sui",
    "ton",
    "tron",
}

METRIC_TERMS = {
    "no kyc",
    "without kyc",
    "no signup",
    "self custodial",
    "non custodial",
    "wallet based",
    "mobile",
    "best price",
    "dex aggregator",
    "on chain",
    "wallet only",
    "from wallet",
    "24 7",
    "fractional",
    "1:1 backed",
}

BUY_TERMS = {
    "swap",
    "buy",
    "sell",
    "trade",
    "long",
    "short",
    "hedge",
    "leverage",
    "open position",
    "close position",
    "lp",
    "borrow",
    "collateral",
}

SAFETY_TERMS = {
    "no kyc",
    "without kyc",
    "no signup",
    "no verification",
    "self custodial",
    "non custodial",
    "wallet based",
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
        if count > 1 and bigram not in {"of the", "in the", "to the", "on the", "from the"}:
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
    if phrase.endswith((" is", " a", " an", " the", " or", " and", " to", " for", " from", " with", " on", " in")):
        return False
    return True


def quality_score(phrase: str):
    phrase = clean_phrase(phrase)
    count = word_count(phrase)

    starts_is_this = phrase.startswith("is this ")
    starts_is      = phrase.startswith("is ")
    starts_should  = phrase.startswith("should ")
    starts_what    = phrase.startswith("what ")
    starts_why     = phrase.startswith("why ")
    starts_how     = phrase.startswith("how ")
    starts_check   = phrase.startswith("check ")
    starts_can     = phrase.startswith("can ")

    has_action       = any(contains_term_phrase(phrase, term) for term in BUY_TERMS)
    has_custody      = any(contains_term_phrase(phrase, term) for term in SAFETY_TERMS)
    has_no_kyc       = contains_term_phrase(phrase, "no kyc") or contains_term_phrase(phrase, "without kyc")
    has_perps        = contains_term_phrase(phrase, "perps") or contains_term_phrase(phrase, "perpetual")
    has_xstocks      = (
        contains_term_phrase(phrase, "xstocks")
        or contains_term_phrase(phrase, "xstock")
        or contains_term_phrase(phrase, "tokenized stock")
        or contains_term_phrase(phrase, "tokenized stocks")
        or contains_term_phrase(phrase, "tokenized equity")
        or contains_term_phrase(phrase, "stocks on solana")
        or contains_term_phrase(phrase, "onchain stocks")
        or any(contains_term_phrase(phrase, t) for t in ["aaplx", "tslax", "nvdax", "spyx", "qqqx"])
    )
    has_hyperliquid  = contains_term_phrase(phrase, "hyperliquid")
    has_whale        = contains_term_phrase(phrase, "whale") or contains_term_phrase(phrase, "smart money") or contains_term_phrase(phrase, "insider")
    has_launch       = contains_term_phrase(phrase, "launch") or contains_term_phrase(phrase, "launchpad")
    has_feature      = any(contains_term_phrase(phrase, term) for term in METRIC_TERMS)
    has_chain        = any(contains_term_phrase(phrase, term) for term in CHAIN_TERMS)
    has_venue        = any(contains_term_phrase(phrase, term) for term in {"swap", "dex", "perps", "hyperliquid", "xstocks", "kamino", "raydium"})

    signature_len = len(phrase_signature(phrase).split())

    return (
        0 if has_action else 1,
        0 if has_custody else 1,
        0 if has_no_kyc else 1,
        0 if has_perps or has_xstocks or has_hyperliquid else 1,
        0 if has_whale or has_launch else 1,
        0 if has_feature else 1,
        0 if has_chain else 1,
        0 if has_venue else 1,
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
    print(f"Generated {len(keywords)} nexus dex keywords")


if __name__ == "__main__":
    main()
