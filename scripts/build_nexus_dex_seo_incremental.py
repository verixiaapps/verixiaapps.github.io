import os
import re
import sys
import subprocess
from html import escape

BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from generate_nexus_dex_content import generate_nexus_dex_content

# -----------------------------
# CONFIG
# -----------------------------
KEYWORD_FILE            = os.path.join(BASE_DIR, "data", "nexus_dex_keywords.txt")
GENERATED_SLUGS_FILE    = os.path.join(BASE_DIR, "data", "nexus_dex_generated_slugs.txt")
GENERATED_KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "nexus_dex_generated_keywords.txt")
REJECTED_KEYWORDS_FILE  = os.path.join(BASE_DIR, "data", "nexus_dex_rejected_keywords.txt")

TEMPLATE_FILE = os.path.join(BASE_DIR, "nexus-dex-template", "nexus-dex-template.html")
OUTPUT_DIR    = os.path.join(BASE_DIR, "nexus-dex")
SITE          = "https://verixiaapps.com"

RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT    = 10
DAILY_LIMIT         = int(os.getenv("DAILY_LIMIT", "100"))
COMMIT_EVERY        = int(os.getenv("COMMIT_EVERY", "30"))
RESUME              = os.getenv("RESUME", "true").lower() == "true"

PROTECTED_SLUGS = {
    "nexus-dex",
    "crypto-markets",
    "bitcoin-markets",
    "ethereum-markets",
    "solana-markets",
    "altcoin-markets",
    "hyperliquid-frontend",
    "global-markets",
    "tokenized-stocks",
    "buy-stocks-onchain",
    "stocks-no-kyc",
    "stocks-24-7",
    "global-stock-access",
    "solana-swap",
    "buy-token",
    "no-kyc-trading",
    "whale-tracking",
    "token-launch",
    "wallet-trading",
    "how-to-guides",
    "wonderland-memes",
    "live-signals",
    "brand-tokens",
    "solana-bridges",
    "solana-swaps",
}
FALLBACK_HUB_SLUG = "crypto-markets"

REQUIRED_TEMPLATE_PLACEHOLDERS = {
    "{{TITLE}}",
    "{{DESCRIPTION}}",
    "{{KEYWORD}}",
    "{{AI_CONTENT}}",
    "{{RELATED_LINKS}}",
    "{{MORE_LINKS}}",
    "{{HUB_LINK}}",
    "{{CANONICAL_URL}}",
}

NEXUS_DEX_CLUSTER_TERMS = {
    "perps", "perp", "perpetual", "leverage", "leveraged", "long", "short",
    "hedge", "amplify", "swap", "buy", "sell", "trade", "trading", "dex",
    "cex", "kyc", "wallet", "mobile", "app", "self", "custodial", "non",
    "phantom", "backpack", "solflare", "metamask", "jupiter", "raydium",
    "orca", "drift", "hyperliquid", "kamino", "whale", "smart", "money",
    "insider", "deployer", "sniper", "kol", "cohort", "holder", "concentration",
    "launch", "launchpad", "bonding", "curve", "graduate", "fair", "stealth",
    "solana", "ethereum", "bitcoin", "btc", "eth", "sol", "usdc", "usdt",
    "base", "bsc", "arbitrum", "polygon", "spl", "memecoin", "altcoin",
    "shitcoin", "microcap", "pump", "fun",
    "xstocks", "xstock", "tokenized", "stocks", "stock", "equity", "equities",
    "onchain", "fractional", "brokerage", "broker", "backed",
    "aapl", "tsla", "nvda", "msft", "googl", "amzn", "meta", "mstr", "nflx",
    "amd", "coin", "hood", "crcl", "spy", "qqq", "gld",
    "aaplx", "tslax", "nvdax", "msftx", "googlx", "amznx", "metax", "mstrx",
    "nflxx", "spyx", "qqqx", "crclx",
    "wonderland", "meme", "memes", "ape", "moon", "degen",
    "hoppy", "fartcoin", "popcat", "wif", "bonk", "mew", "wen",
    "bome", "myro", "ponke", "michi", "trump", "moodeng", "goat", "pnut",
    "fresh", "trending", "signals", "discovery", "gainers", "volume", "leaders",
    "hot", "pumping", "live",
    "bridge", "bridges", "wormhole", "debridge", "allbridge",
    "anonymous", "permissionless", "aggregator", "best", "price", "global", "no",
}

BRAND_CASE = {
    "nexus dex": "Nexus DEX",
    "verixia": "Verixia",
    "binance smart chain": "Binance Smart Chain",
    "trust wallet": "Trust Wallet",
    "raydium launchlab": "Raydium LaunchLab",
    "pump fun": "Pump Fun",
    "backed finance": "Backed Finance",
    "hyperliquid": "Hyperliquid",
    "wonderland": "Wonderland",
    "metamask": "MetaMask",
    "dexscreener": "Dexscreener",
    "pancakeswap": "PancakeSwap",
    "uniswap": "Uniswap",
    "raydium": "Raydium",
    "coinbase": "Coinbase",
    "robinhood": "Robinhood",
    "kalshi": "Kalshi",
    "kraken": "Kraken",
    "bybit": "Bybit",
    "kamino": "Kamino",
    "ethereum": "Ethereum",
    "avalanche": "Avalanche",
    "arbitrum": "Arbitrum",
    "polygon": "Polygon",
    "optimism": "Optimism",
    "phantom": "Phantom",
    "backpack": "Backpack",
    "solflare": "Solflare",
    "bitcoin": "Bitcoin",
    "solana": "Solana",
    "binance": "Binance",
    "jupiter": "Jupiter",
    "meteora": "Meteora",
    "phoenix": "Phoenix",
    "lifinity": "Lifinity",
    "orca": "Orca",
    "drift": "Drift",
    "wormhole": "Wormhole",
    "debridge": "deBridge",
    "allbridge": "Allbridge",
    "crypto": "Crypto",
    "market": "Market",
    "wallet": "Wallet",
    "xstocks": "xStocks",
    "xstock": "xStock",
    "aaplx": "AAPLx",
    "tslax": "TSLAx",
    "nvdax": "NVDAx",
    "msftx": "MSFTx",
    "googlx": "GOOGLx",
    "amznx": "AMZNx",
    "metax": "METAx",
    "mstrx": "MSTRx",
    "nflxx": "NFLXx",
    "spyx": "SPYx",
    "qqqx": "QQQx",
    "crclx": "CRCLx",
    "hoodx": "HOODx",
    "coinx": "COINx",
    "orclx": "ORCLx",
    "crmx": "CRMx",
    "aapl": "AAPL",
    "tsla": "TSLA",
    "nvda": "NVDA",
    "msft": "MSFT",
    "googl": "GOOGL",
    "amzn": "AMZN",
    "meta": "META",
    "mstr": "MSTR",
    "nflx": "NFLX",
    "amd": "AMD",
    "coin": "COIN",
    "hood": "HOOD",
    "crcl": "CRCL",
    "orcl": "ORCL",
    "crm": "CRM",
    "spy": "SPY",
    "qqq": "QQQ",
    "gld": "GLD",
    "apple": "Apple",
    "tesla": "Tesla",
    "nvidia": "Nvidia",
    "microsoft": "Microsoft",
    "google": "Google",
    "alphabet": "Alphabet",
    "amazon": "Amazon",
    "netflix": "Netflix",
    "microstrategy": "MicroStrategy",
    "circle": "Circle",
    "oracle": "Oracle",
    "salesforce": "Salesforce",
    "fdv": "FDV",
    "bsc": "BSC",
    "eth": "ETH",
    "btc": "BTC",
    "sol": "SOL",
    "usdc": "USDC",
    "usdt": "USDT",
    "bnb": "BNB",
    "base": "Base",
    "blast": "Blast",
    "sui": "Sui",
    "aptos": "Aptos",
    "ton": "TON",
    "trx": "TRX",
    "tron": "Tron",
    "bonk": "BONK",
    "wif": "WIF",
    "pepe": "PEPE",
    "doge": "DOGE",
    "shib": "SHIB",
    "trump": "TRUMP",
    "popcat": "POPCAT",
    "hoppy": "HOPPY",
    "fartcoin": "FARTCOIN",
    "moodeng": "MOODENG",
    "pnut": "PNUT",
    "goat": "GOAT",
    "mew": "MEW",
    "wen": "WEN",
    "bome": "BOME",
    "myro": "MYRO",
    "ponke": "PONKE",
    "michi": "MICHI",
    "floki": "FLOKI",
    "fwog": "FWOG",
    "pengu": "PENGU",
    "neiro": "NEIRO",
    "useless": "USELESS",
    "jup": "JUP",
    "ray": "RAY",
    "pyth": "PYTH",
    "jto": "JTO",
    "hype": "HYPE",
    "spx": "SPX",
    "ai16z": "ai16z",
    "griffain": "GRIFFAIN",
    "chillguy": "CHILLGUY",
    "zerebro": "ZEREBRO",
    "dex": "DEX",
    "cex": "CEX",
    "kyc": "KYC",
    "spl": "SPL",
    "nft": "NFT",
    "dao": "DAO",
    "defi": "DeFi",
    "tvl": "TVL",
    "evm": "EVM",
    "etf": "ETF",
    "rwa": "RWA",
    "fomc": "FOMC",
    "cpi": "CPI",
    "gdp": "GDP",
    "nfl": "NFL",
    "nba": "NBA",
    "ufc": "UFC",
    "us": "U.S.",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with",
}

HUB_TITLE_OVERRIDES = {
    "crypto-markets": "Crypto Markets Hub",
    "bitcoin-markets": "Bitcoin Markets Hub",
    "ethereum-markets": "Ethereum Markets Hub",
    "solana-markets": "SOL Markets Hub",
    "altcoin-markets": "Altcoin Markets Hub",
    "hyperliquid-frontend": "Hyperliquid Frontend Hub",
    "global-markets": "Global Markets Hub",
    "tokenized-stocks": "Tokenized Stocks Hub",
    "buy-stocks-onchain": "Buy Stocks On-Chain Hub",
    "stocks-no-kyc": "Stocks No KYC Hub",
    "stocks-24-7": "24/7 Stocks Hub",
    "global-stock-access": "Global Stock Access Hub",
    "solana-swap": "Solana Swap Hub",
    "buy-token": "Buy Token Hub",
    "no-kyc-trading": "No KYC Trading Hub",
    "whale-tracking": "Whale Tracking Hub",
    "token-launch": "Token Launch Hub",
    "wallet-trading": "Wallet Trading Hub",
    "how-to-guides": "Nexus DEX Guides Hub",
    "wonderland-memes": "Wonderland Memes Hub",
    "live-signals": "Live Signals Hub",
    "brand-tokens": "Brand Tokens Hub",
    "solana-bridges": "Solana Bridges Hub",
    "solana-swaps": "Solana Swaps Hub",
}

# Order matters: most specific first
HUB_MATCH_RULES = [
    ("hyperliquid", "hyperliquid-frontend"),

    # xStocks / brand tokens
    ("xstocks", "global-markets"),
    ("xstock", "global-markets"),
    ("backed finance", "global-markets"),
    ("aaplx", "global-markets"),
    ("tslax", "global-markets"),
    ("nvdax", "global-markets"),
    ("spyx", "global-markets"),
    ("qqqx", "global-markets"),

    ("buy us stocks from", "global-stock-access"),
    ("us stocks no us bank", "global-stock-access"),
    ("us stocks for non residents", "global-stock-access"),
    ("us stocks international", "global-stock-access"),
    ("global stock", "global-stock-access"),
    ("international stock", "global-stock-access"),

    ("24 7 stock", "stocks-24-7"),
    ("stocks 24 hours", "stocks-24-7"),
    ("stocks weekend", "stocks-24-7"),
    ("trade stocks at night", "stocks-24-7"),
    ("trade stocks weekends", "stocks-24-7"),
    ("trade stocks holidays", "stocks-24-7"),
    ("stocks never close", "stocks-24-7"),
    ("always open stock", "stocks-24-7"),
    ("stocks after hours", "stocks-24-7"),

    ("buy stocks no kyc", "stocks-no-kyc"),
    ("trade stocks no kyc", "stocks-no-kyc"),
    ("stock trading no verification", "stocks-no-kyc"),
    ("stock trading no signup", "stocks-no-kyc"),
    ("stocks no id", "stocks-no-kyc"),
    ("stocks no account", "stocks-no-kyc"),
    ("anonymous stock trading", "stocks-no-kyc"),
    ("stocks without broker", "stocks-no-kyc"),
    ("stocks without robinhood", "stocks-no-kyc"),
    ("stocks without etrade", "stocks-no-kyc"),

    ("buy apple stock", "buy-stocks-onchain"),
    ("buy aapl", "buy-stocks-onchain"),
    ("buy tesla stock", "buy-stocks-onchain"),
    ("buy tsla", "buy-stocks-onchain"),
    ("buy nvidia stock", "buy-stocks-onchain"),
    ("buy nvda", "buy-stocks-onchain"),
    ("buy microsoft stock", "buy-stocks-onchain"),
    ("buy msft", "buy-stocks-onchain"),
    ("buy google stock", "buy-stocks-onchain"),
    ("buy googl", "buy-stocks-onchain"),
    ("buy meta stock", "buy-stocks-onchain"),
    ("buy amazon stock", "buy-stocks-onchain"),
    ("buy amzn", "buy-stocks-onchain"),
    ("buy mstr", "buy-stocks-onchain"),
    ("buy microstrategy", "buy-stocks-onchain"),
    ("buy spy", "buy-stocks-onchain"),
    ("buy qqq", "buy-stocks-onchain"),
    ("buy netflix stock", "buy-stocks-onchain"),
    ("buy nflx", "buy-stocks-onchain"),
    ("buy coinbase stock", "buy-stocks-onchain"),
    ("buy robinhood stock", "buy-stocks-onchain"),
    ("buy circle stock", "buy-stocks-onchain"),
    ("buy crcl", "buy-stocks-onchain"),

    ("tokenized stocks", "tokenized-stocks"),
    ("tokenized equity", "tokenized-stocks"),
    ("onchain stocks", "tokenized-stocks"),
    ("onchain equities", "tokenized-stocks"),
    ("stocks on solana", "tokenized-stocks"),
    ("stocks on blockchain", "tokenized-stocks"),
    ("stocks as spl tokens", "tokenized-stocks"),
    ("buy stocks with crypto", "tokenized-stocks"),
    ("buy stocks with usdc", "tokenized-stocks"),
    ("buy stocks with sol", "tokenized-stocks"),

    # Perps
    ("btc perps", "bitcoin-markets"),
    ("bitcoin perps", "bitcoin-markets"),
    ("bitcoin futures", "bitcoin-markets"),
    ("bitcoin perpetual", "bitcoin-markets"),
    ("eth perps", "ethereum-markets"),
    ("ethereum perps", "ethereum-markets"),
    ("ethereum futures", "ethereum-markets"),
    ("ethereum perpetual", "ethereum-markets"),
    ("sol perps", "solana-markets"),
    ("solana perps", "solana-markets"),
    ("sol perpetual", "solana-markets"),
    ("memecoin perps", "altcoin-markets"),
    ("altcoin perps", "altcoin-markets"),
    ("wif perps", "altcoin-markets"),
    ("bonk perps", "altcoin-markets"),
    ("pepe perps", "altcoin-markets"),
    ("doge perps", "altcoin-markets"),
    ("hype perps", "altcoin-markets"),

    # Whale
    ("whale tracker", "whale-tracking"),
    ("smart money", "whale-tracking"),
    ("insider", "whale-tracking"),
    ("deployer", "whale-tracking"),
    ("sniper", "whale-tracking"),
    ("kol wallet", "whale-tracking"),

    # Launch
    ("launch token", "token-launch"),
    ("token launch", "token-launch"),
    ("launchpad", "token-launch"),
    ("bonding curve", "token-launch"),
    ("deploy token", "token-launch"),

    # Swap
    ("solana swap", "solana-swap"),
    ("solana dex", "solana-swap"),
    ("dex aggregator", "solana-swap"),
    ("best price swap", "solana-swap"),
    ("swap", "solana-swap"),

    # Buy token
    ("buy bonk", "buy-token"),
    ("buy wif", "buy-token"),
    ("buy pepe", "buy-token"),
    ("buy trump", "buy-token"),
    ("buy memecoin", "buy-token"),
    ("buy spl", "buy-token"),
    ("buy ", "buy-token"),

    # Wallet
    ("phantom wallet trading", "wallet-trading"),
    ("backpack wallet trading", "wallet-trading"),
    ("self custodial", "wallet-trading"),
    ("non custodial", "wallet-trading"),
    ("wallet based", "wallet-trading"),

    # No KYC
    ("no kyc", "no-kyc-trading"),
    ("without kyc", "no-kyc-trading"),
    ("no signup", "no-kyc-trading"),
    ("no verification", "no-kyc-trading"),

    # Perps fallback
    ("perps", "crypto-markets"),
    ("perpetual", "crypto-markets"),
    ("leverage", "crypto-markets"),

    ("how to", "how-to-guides"),
]

LOW_VALUE_SINGLE_TERMS = {
    "trade", "swap", "buy", "sell", "mobile", "wallet", "app", "dex",
    "perp", "perps", "leverage", "no", "from", "with", "on", "for",
}

HIGH_INTENT_TERMS = {
    "perps", "perp", "perpetual", "leverage", "leveraged", "long", "short",
    "hedge", "kyc", "wallet", "mobile", "phantom", "backpack", "solflare",
    "hyperliquid", "whale", "smart", "money", "insider", "deployer", "sniper",
    "kol", "launch", "launchpad", "bonding", "deploy", "swap", "buy", "sell",
    "trade", "custodial",
    "xstocks", "xstock", "tokenized", "stocks", "stock", "equity", "equities",
    "aapl", "tsla", "nvda", "msft", "googl", "amzn", "meta", "mstr", "spy", "qqq",
    "aaplx", "tslax", "nvdax", "spyx", "qqqx",
    "wonderland", "meme", "memes", "hoppy", "fartcoin", "popcat",
    "bridge", "bridges", "trending", "signals", "fresh",
}


# -----------------------------
# UTILITIES
# -----------------------------
def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def slugify(text):
    text = normalize_keyword(text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def contains_term_phrase(haystack, needle):
    haystack_norm = normalize_keyword(haystack)
    needle_norm = normalize_keyword(needle)
    if not haystack_norm or not needle_norm:
        return False
    pattern = r"(^|[^a-z0-9])" + re.escape(needle_norm) + r"([^a-z0-9]|$)"
    return re.search(pattern, haystack_norm, flags=re.IGNORECASE) is not None


def clean_base_keyword(text):
    kw = normalize_keyword(text)
    kw = re.sub(r"^\s*is\s+this\s+", "", kw)
    kw = re.sub(r"^\s*is\s+", "", kw)
    kw = re.sub(r"^\s*can\s+i\s+", "", kw)
    kw = re.sub(r"^\s*should\s+i\s+", "", kw)
    kw = re.sub(r"^\s*how\s+to\s+", "", kw)
    kw = re.sub(r"^\s*where\s+to\s+", "", kw)
    kw = re.sub(r"^\s*best\s+place\s+to\s+", "", kw)
    kw = re.sub(r"\s+no\s+kyc$", "", kw)
    kw = re.sub(r"\s+mobile$", "", kw)
    kw = re.sub(r"\s+app$", "", kw)
    kw = re.sub(r"\s+without\s+kyc$", "", kw)
    return re.sub(r"\s+", " ", kw).strip()


def display_keyword(text):
    return clean_base_keyword(text)


def canonical_keyword(text):
    clean_kw = clean_base_keyword(text)
    return clean_kw if clean_kw else normalize_keyword(text)


def canonical_slug(text):
    return slugify(canonical_keyword(text))


def apply_brand_case(text):
    result = f" {text} "
    for raw, proper in sorted(BRAND_CASE.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(raw) + r"(?![a-z0-9])"
        result = re.sub(pattern, proper, result, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", result).strip()


def title_case(text):
    if not text:
        return ""
    words = normalize_keyword(text).split()
    titled = []
    for i, word in enumerate(words):
        if i > 0 and word in SMALL_WORDS:
            titled.append(word)
        else:
            titled.append(word.capitalize())
    return apply_brand_case(" ".join(titled))


def readable_keyword(text):
    base = display_keyword(text)
    return title_case(base) if base else ""


def keyword_tokens(text):
    return set(canonical_keyword(text).split())


def keyword_cluster_tokens(text):
    return {token for token in keyword_tokens(text) if token in NEXUS_DEX_CLUSTER_TERMS}


def keyword_root(text):
    cleaned = canonical_keyword(text)
    return cleaned.split()[0] if cleaned else ""


def escape_html(text):
    return escape(str(text), quote=True)


def is_guidance_style_keyword(keyword):
    kw = normalize_keyword(keyword)
    return (
        kw.startswith("how to ")
        or kw.startswith("what is ")
        or kw.startswith("what does ")
        or kw.startswith("why ")
        or kw.startswith("when ")
        or kw.startswith("where ")
        or kw.startswith("best ")
        or kw.startswith("top ")
        or kw.startswith("cheapest ")
    )


def is_question_style_keyword(keyword):
    kw = normalize_keyword(keyword)
    return kw.startswith(("is ", "can ", "should ", "what ", "why ", "when ", "where "))


def ensure_file(filepath):
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists(filepath):
        with open(filepath, "a", encoding="utf-8"):
            pass


def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []
    seen = set()
    ordered = []
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        for line in f:
            keyword = normalize_keyword(line)
            if not keyword or keyword in seen:
                continue
            seen.add(keyword)
            ordered.append(keyword)
    return ordered


def load_generated_slugs():
    if not os.path.exists(GENERATED_SLUGS_FILE):
        return set()
    with open(GENERATED_SLUGS_FILE, encoding="utf-8") as f:
        return {slugify(line) for line in f if slugify(line)}


def load_generated_keywords():
    if not os.path.exists(GENERATED_KEYWORDS_FILE):
        return set()
    with open(GENERATED_KEYWORDS_FILE, encoding="utf-8") as f:
        return {normalize_keyword(line) for line in f if normalize_keyword(line)}


def write_lines(filepath, values):
    ensure_file(filepath)
    lines = [str(v).strip() for v in values if str(v).strip()]
    with open(filepath, "w", encoding="utf-8") as f:
        if lines:
            f.write("\n".join(lines) + "\n")
        else:
            f.write("")


def page_path(slug):
    return os.path.join(OUTPUT_DIR, slug, "index.html")


def page_exists(slug):
    return os.path.exists(page_path(slug))


def humanize_slug(slug):
    return title_case(slug.replace("-", " "))


def validate_template_placeholders(template_html):
    missing = [p for p in REQUIRED_TEMPLATE_PLACEHOLDERS if p not in template_html]
    if missing:
        raise ValueError("Template is missing required placeholders: " + ", ".join(sorted(missing)))


def load_template():
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(f"Missing template file: {TEMPLATE_FILE}")
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        template = f.read()
    validate_template_placeholders(template)
    return template


def find_best_hub_slug(keyword):
    keyword_norm = normalize_keyword(keyword)
    for term, slug in HUB_MATCH_RULES:
        if contains_term_phrase(keyword_norm, term):
            return slug
    return FALLBACK_HUB_SLUG


def build_hub_link_html(keyword):
    hub_slug = find_best_hub_slug(keyword)
    hub_title = HUB_TITLE_OVERRIDES.get(hub_slug, f"{humanize_slug(hub_slug)} Hub")
    return f'<a href="/nexus-dex/{hub_slug}/">{escape_html(hub_title)}</a>'


def sanitize_ai_html(text):
    raw = str(text or "").strip()
    if not raw:
        return ""
    raw = re.sub(r"^```(?:html)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    raw = re.sub(r"<script\b[^>]*>.*?</script>", "", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", "", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = raw.strip()
    if "<" in raw and ">" in raw:
        return raw
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", raw) if p.strip()]
    if not paragraphs:
        paragraphs = [raw]
    return "\n".join(f"<p>{escape_html(p)}</p>" for p in paragraphs)


# -----------------------------
# QUALITY FILTERS (from legacy v1)
# -----------------------------
def is_weak_keyword(keyword):
    tokens = canonical_keyword(keyword).split()
    if len(tokens) < 2:
        return True
    if len(tokens) == 2 and all(token in LOW_VALUE_SINGLE_TERMS for token in tokens):
        return True
    if not any(token in HIGH_INTENT_TERMS or token in NEXUS_DEX_CLUSTER_TERMS for token in tokens):
        return True
    return False


def keyword_quality_score(keyword):
    kw = normalize_keyword(keyword)
    score = 0
    if "nexus dex" in kw or "verixia" in kw:
        score += 12
    if "perps" in kw or "perpetual" in kw:
        score += 10
    if "leverage" in kw or "leveraged" in kw:
        score += 8
    if "hyperliquid" in kw:
        score += 10
    if "no kyc" in kw or "without kyc" in kw or "no signup" in kw:
        score += 10
    if "self custodial" in kw or "non custodial" in kw or "wallet based" in kw:
        score += 8
    if "xstocks" in kw or "xstock" in kw or "tokenized stock" in kw or "tokenized equity" in kw or "brand token" in kw:
        score += 10
    if "stocks on solana" in kw or "onchain stocks" in kw or "stocks as spl" in kw:
        score += 8
    if "24 7 stock" in kw or "stocks 24 hours" in kw or "stocks weekend" in kw:
        score += 7
    if any(tok in kw for tok in ["aapl", "tsla", "nvda", "msft", "googl", "amzn", "spy", "qqq", "mstr"]):
        score += 6
    if any(term in kw for term in ["btc", "bitcoin", "eth", "ethereum", "sol", "solana"]):
        score += 6
    if any(term in kw for term in ["wif", "bonk", "pepe", "doge", "hype", "popcat", "trump", "fartcoin", "hoppy"]):
        score += 7
    if any(term in kw for term in ["swap", "buy", "trade", "short", "long", "hedge"]):
        score += 5
    if any(term in kw for term in ["phantom", "backpack", "solflare", "wallet"]):
        score += 6
    if "mobile" in kw or "app" in kw:
        score += 4
    if "whale" in kw or "smart money" in kw or "insider" in kw or "deployer" in kw:
        score += 7
    if "launch" in kw or "launchpad" in kw or "bonding curve" in kw:
        score += 6
    if "bridge" in kw or "wormhole" in kw or "debridge" in kw:
        score += 6
    if "trending" in kw or "signals" in kw or "fresh launch" in kw:
        score += 5
    if kw.startswith("is "):
        score -= 4
    if kw.startswith("can i "):
        score -= 4
    score -= len(kw) / 100.0
    return score


def choose_canonical_keyword(keywords_for_same_intent):
    return sorted(
        keywords_for_same_intent,
        key=lambda k: (-keyword_quality_score(k), len(k), k)
    )[0]


def dedupe_keywords(raw_keywords):
    groups = {}
    for keyword in raw_keywords:
        key = canonical_keyword(keyword)
        groups.setdefault(key, []).append(keyword)

    canonical_keywords = []
    seen_slugs = set()
    skipped_weak = 0
    skipped_dup = 0
    deduped = 0

    for _, group in groups.items():
        chosen = choose_canonical_keyword(group)
        chosen_slug = canonical_slug(chosen)

        if chosen_slug in PROTECTED_SLUGS or not chosen_slug:
            continue
        if is_weak_keyword(chosen):
            skipped_weak += len(group)
            continue
        if chosen_slug in seen_slugs:
            skipped_dup += len(group)
            continue

        canonical_keywords.append(chosen)
        seen_slugs.add(chosen_slug)
        if len(group) > 1:
            deduped += len(group) - 1

    return canonical_keywords, deduped, skipped_dup, skipped_weak


def validate_page_output(slug, title, description, canonical, related_pages):
    errors = []
    if not slug:
        errors.append("empty slug")
    if not canonical.endswith(f"/{slug}/"):
        errors.append("canonical mismatch")
    if len(related_pages) == 0:
        errors.append("no related pages")
    if len(title) < 35 or len(title) > 78:
        errors.append("title length out of target range")
    if len(description) < 110 or len(description) > 170:
        errors.append("description length out of target range")
    return errors


def is_usable_ai_text(text):
    if not text:
        return False
    raw = str(text).strip()
    lowered = raw.lower()
    if len(raw) < 350:
        return False
    weak_markers = {
        "lorem ipsum",
        "as an ai",
        "here are some paragraphs",
        "let me know if you want",
        "i can't help with that",
        "i cannot help with that",
        "i am sorry",
        "cannot assist",
        "can't assist",
        "content policy",
    }
    if any(marker in lowered for marker in weak_markers):
        return False
    paragraph_like = (
        "<p>" in lowered
        or "</p>" in lowered
        or "\n\n" in raw
        or raw.count("\n") >= 3
    )
    return paragraph_like


def append_rejected_keyword(keyword, reason):
    ensure_file(REJECTED_KEYWORDS_FILE)
    entry = f"{normalize_keyword(keyword)} | {str(reason).strip()}"

    existing = set()
    with open(REJECTED_KEYWORDS_FILE, "r", encoding="utf-8") as f:
        existing = {line.strip() for line in f if line.strip()}

    if entry not in existing:
        with open(REJECTED_KEYWORDS_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")


# -----------------------------
# GIT CHECKPOINT
# -----------------------------
def get_remaining_keywords(raw_keywords, processed_keywords):
    """Compute remaining keywords by excluding already-processed ones."""
    return [kw for kw in raw_keywords if normalize_keyword(kw) not in processed_keywords]


def git_checkpoint(generated_count, new_generated_keywords, new_generated_slugs, raw_keywords, processed_keywords):
    sorted_keywords = sorted(new_generated_keywords, key=slugify)
    write_lines(GENERATED_KEYWORDS_FILE, sorted_keywords)
    write_lines(GENERATED_SLUGS_FILE, [slugify(k) for k in sorted_keywords])
    write_lines(KEYWORD_FILE, get_remaining_keywords(raw_keywords, processed_keywords))

    try:
        subprocess.run(["git", "add", "-A"], check=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if result.returncode == 0:
            print(f"[checkpoint] No changes to commit at {generated_count} pages.")
            return

        subprocess.run(
            ["git", "commit", "-m", f"Nexus DEX progress checkpoint: {generated_count} pages"],
            check=True
        )
        subprocess.run(["git", "fetch", "origin", "main"], check=True)
        subprocess.run(
            ["git", "push", "--force-with-lease", "origin", "HEAD:main"],
            check=True
        )
        print(f"[checkpoint] Committed and pushed at {generated_count} pages.")
    except subprocess.CalledProcessError as e:
        print(f"[checkpoint] Git error at {generated_count} pages: {e}")


# -----------------------------
# AI GENERATION (retry across prompt variants)
# -----------------------------
def generate_ai_text(keyword, keyword_display):
    attempts = []
    raw_keyword = normalize_keyword(keyword)
    clean_keyword = normalize_keyword(keyword_display)
    readable = readable_keyword(keyword_display)

    if raw_keyword:
        attempts.append(raw_keyword)
    if clean_keyword and clean_keyword != raw_keyword:
        attempts.append(clean_keyword)
    if readable:
        attempts.append(readable)
    if clean_keyword:
        attempts.append(f"{clean_keyword} nexus dex")
    if clean_keyword and not contains_term_phrase(raw_keyword, "kyc"):
        attempts.append(f"{clean_keyword} no kyc")
    if clean_keyword and not contains_term_phrase(raw_keyword, "wallet"):
        attempts.append(f"{clean_keyword} from wallet")

    seen = set()
    ordered_attempts = []
    for item in attempts:
        item_norm = normalize_keyword(item)
        if item_norm and item_norm not in seen:
            seen.add(item_norm)
            ordered_attempts.append(item)

    last_error = None
    for attempt in ordered_attempts:
        try:
            raw_ai = generate_nexus_dex_content(attempt)
            ai_text = sanitize_ai_html(raw_ai)
            if is_usable_ai_text(ai_text):
                return ai_text
            last_error = f"thin or malformed output for prompt: {attempt}"
        except Exception as e:
            last_error = str(e)
            print(f"[error] AI generation failed for '{attempt}': {e}")

    raise ValueError(last_error or "AI generation failed")


# -----------------------------
# SEO TEXT HELPERS
# -----------------------------
def build_title(keyword):
    raw = normalize_keyword(keyword)
    readable = readable_keyword(keyword)
    if not raw:
        return "Nexus DEX | Self-Custodial Perps, Swaps & Tokenized Stocks"
    if is_guidance_style_keyword(raw):
        return f"{title_case(raw)} | Nexus DEX Wallet Guide"
    if raw.startswith("is this "):
        return f"{title_case(raw)}? Self-Custodial Trading on Nexus DEX"
    if raw.startswith("should i buy "):
        cleaned = re.sub(r"^should i buy\s+", "", raw).strip()
        return f"Should I Buy {title_case(cleaned)}? Nexus DEX Best Price No KYC"
    if raw.startswith("can i "):
        return f"{title_case(raw)}? Nexus DEX Wallet-Based No KYC Trading"
    if is_question_style_keyword(raw):
        return f"{title_case(raw)}? Nexus DEX Self-Custodial Trading"
    return f"{readable} | Nexus DEX | Self-Custodial, No KYC, Mobile-First"


def build_description(keyword):
    raw = normalize_keyword(keyword)
    readable = readable_keyword(keyword)
    clean_kw = display_keyword(keyword)
    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        return (
            f"Use Nexus DEX for {readable}. Self-custodial perps, swaps, and tokenized stocks "
            f"from your Solana wallet with no KYC, no signup, and mobile-first access."
        )
    return (
        f"{readable} on Nexus DEX. Self-custodial trading from your wallet with best-price routing, "
        f"no KYC, and mobile-first access. Trade {clean_kw} without a centralized exchange."
    )


def build_related_anchor(keyword):
    raw = normalize_keyword(keyword)
    readable = readable_keyword(keyword)
    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        anchor = title_case(raw)
        if is_question_style_keyword(raw) and not anchor.endswith("?"):
            anchor += "?"
        return anchor
    return f"{readable} on Nexus DEX"


def build_canonical(slug):
    return f"{SITE}/nexus-dex/{slug}/"


# -----------------------------
# LINKING HELPERS
# -----------------------------
def dedupe_pages_by_slug(pages_list):
    deduped = []
    seen = set()
    for page in pages_list:
        slug = page["slug"]
        if not slug or slug in seen or slug in PROTECTED_SLUGS:
            continue
        seen.add(slug)
        deduped.append(page)
    return deduped


def get_related_pages(current_page, all_pages, limit, exclude_slugs=None):
    exclude_slugs = set(exclude_slugs or set())
    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_tokens = keyword_tokens(current_keyword)
    current_cluster = keyword_cluster_tokens(current_keyword)
    current_root = keyword_root(current_keyword)
    current_hub = find_best_hub_slug(current_keyword)

    candidates = [
        p for p in all_pages
        if p["slug"] != current_slug
        and p["slug"] not in PROTECTED_SLUGS
        and p["slug"] not in exclude_slugs
        and page_exists(p["slug"])
    ]

    def score(page):
        other_keyword = page["keyword"]
        other_tokens = keyword_tokens(other_keyword)
        other_cluster = keyword_cluster_tokens(other_keyword)
        other_root = keyword_root(other_keyword)
        other_hub = find_best_hub_slug(other_keyword)
        length_diff = abs(len(other_keyword.split()) - len(current_keyword.split()))
        same_hub = 1 if current_hub and other_hub == current_hub else 0
        same_root = 1 if current_root and other_root == current_root else 0
        shared_cluster = len(current_cluster & other_cluster)
        shared_tokens = len(current_tokens & other_tokens)
        return (-same_hub, -same_root, -shared_cluster, -shared_tokens, length_diff, other_keyword)

    ranked = sorted(candidates, key=score)
    related = []
    used_slugs = set()

    for page in ranked:
        if page["slug"] in used_slugs:
            continue
        related.append(page)
        used_slugs.add(page["slug"])
        if len(related) == limit:
            break

    return related


def get_more_links(current_page, all_pages, limit, exclude_slugs=None):
    exclude_slugs = set(exclude_slugs or set())
    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_hub = find_best_hub_slug(current_keyword)

    same_hub_pages = []
    if current_hub:
        same_hub_pages = [
            p for p in all_pages
            if p["slug"] != current_slug
            and p["slug"] not in exclude_slugs
            and p["slug"] not in PROTECTED_SLUGS
            and page_exists(p["slug"])
            and find_best_hub_slug(p["keyword"]) == current_hub
        ]

    fallback_pages = [
        p for p in all_pages
        if p["slug"] != current_slug
        and p["slug"] not in exclude_slugs
        and p["slug"] not in PROTECTED_SLUGS
        and page_exists(p["slug"])
        and p not in same_hub_pages
    ]

    selected = []
    used_slugs = set()

    for page in same_hub_pages + fallback_pages:
        if page["slug"] in used_slugs:
            continue
        selected.append(page)
        used_slugs.add(page["slug"])
        if len(selected) == limit:
            break

    return selected


def build_links_html(pages_list):
    return "".join(
        f'<li><a href="/nexus-dex/{p["slug"]}/">{escape_html(build_related_anchor(p["keyword"]))}</a></li>\n'
        for p in pages_list
        if page_exists(p["slug"])
    )


# -----------------------------
# SETUP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(GENERATED_SLUGS_FILE)
ensure_file(GENERATED_KEYWORDS_FILE)
ensure_file(REJECTED_KEYWORDS_FILE)

template = load_template()
raw_keywords = load_keywords()

if not raw_keywords:
    print("No keywords in queue. Nothing to generate.")
    sys.exit(0)

# Legacy v1 dedupe + quality filter
keywords, deduped_count, skipped_dup_count, skipped_weak_count = dedupe_keywords(raw_keywords)

generated_slugs = load_generated_slugs()
generated_keywords = load_generated_keywords()

# Build queue from deduped/quality-filtered keywords
queue_pages = []
seen_queue_slugs = set()
for keyword in keywords:
    slug = canonical_slug(keyword)
    if not slug or slug in PROTECTED_SLUGS or slug in seen_queue_slugs:
        continue
    seen_queue_slugs.add(slug)
    queue_pages.append({"keyword": keyword, "slug": slug})

# Existing pages = pages already on disk (used for internal links)
existing_pages = []
existing_seen_slugs = set()

for keyword in generated_keywords:
    slug = slugify(keyword)
    if slug in PROTECTED_SLUGS or slug in existing_seen_slugs or not slug:
        continue
    if page_exists(slug):
        existing_pages.append({"keyword": keyword, "slug": slug})
        existing_seen_slugs.add(slug)

for page in queue_pages:
    if page["slug"] in existing_seen_slugs:
        continue
    if page_exists(page["slug"]):
        existing_pages.append(page)
        existing_seen_slugs.add(page["slug"])

existing_pages = dedupe_pages_by_slug(existing_pages)
queue_pages = dedupe_pages_by_slug(queue_pages)

print(f"Loaded {len(raw_keywords)} raw keywords from queue.")
print(f"Canonical keywords after dedupe/quality filter: {len(keywords)}")
print(f"Duplicate / fragmented keywords removed: {deduped_count}")
print(f"Duplicate slug groups skipped: {skipped_dup_count}")
print(f"Weak / low-value keywords skipped: {skipped_weak_count}")
print(f"Known generated slugs: {len(generated_slugs)}")
print(f"Known generated keywords: {len(generated_keywords)}")
print(f"Existing pages available for internal links: {len(existing_pages)}")
print(f"Daily limit: {DAILY_LIMIT}")
print(f"Commit every: {COMMIT_EVERY}")
print(f"Resume mode: {RESUME}")


# -----------------------------
# GENERATE PAGES
# -----------------------------
generated_count = 0
skipped_existing_count = 0
ai_failure_count = 0
validation_error_count = 0
# FIX: use a set to track processed keywords; never filter the full list in the loop
processed_keywords = set()
new_generated_slugs = set(generated_slugs)
new_generated_keywords = set(generated_keywords)

for page in queue_pages:
    if generated_count >= DAILY_LIMIT:
        break

    slug = page["slug"]
    keyword = page["keyword"]
    keyword_norm = normalize_keyword(keyword)
    keyword_display = display_keyword(keyword)
    path = page_path(slug)

    if slug in PROTECTED_SLUGS:
        processed_keywords.add(keyword_norm)
        print("Skipping protected page:", slug)
        continue

    if page_exists(slug) and RESUME:
        skipped_existing_count += 1
        new_generated_slugs.add(slug)
        new_generated_keywords.add(keyword)
        processed_keywords.add(keyword_norm)
        continue

    os.makedirs(os.path.dirname(path), exist_ok=True)
    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    try:
        ai_text = generate_ai_text(keyword, keyword_display)
    except Exception as e:
        ai_failure_count += 1
        append_rejected_keyword(keyword, e)
        print(f"AI generation rejected for {keyword}: {e}")
        continue

    related_pages = get_related_pages(page, existing_pages, RELATED_LINKS_COUNT)
    related_slugs = {p["slug"] for p in related_pages}
    more_pages = get_more_links(
        page,
        existing_pages,
        MORE_LINKS_COUNT,
        exclude_slugs=related_slugs,
    )

    hub_link_html = build_hub_link_html(keyword)

    validation_errors = validate_page_output(slug, title, description, canonical, related_pages)
    if validation_errors:
        validation_error_count += 1
        print(f"Validation warning for {slug}: {'; '.join(validation_errors)}")

    html = template
    html = html.replace("{{TITLE}}",         escape_html(title))
    html = html.replace("{{DESCRIPTION}}",   escape_html(description))
    html = html.replace("{{KEYWORD}}",       escape_html(keyword_display))
    html = html.replace("{{AI_CONTENT}}",    ai_text)
    html = html.replace("{{RELATED_LINKS}}", build_links_html(related_pages))
    html = html.replace("{{MORE_LINKS}}",    build_links_html(more_pages))
    html = html.replace("{{HUB_LINK}}",      hub_link_html)
    html = html.replace("{{CANONICAL_URL}}", escape_html(canonical))

    # Tolerant unresolved-placeholder strip
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", html)))
    if unresolved:
        print(f"[warn] stripping unresolved template placeholders: {', '.join(unresolved)}")
        for token in unresolved:
            html = html.replace(token, "")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    new_generated_slugs.add(slug)
    new_generated_keywords.add(keyword)
    processed_keywords.add(keyword_norm)

    existing_pages.append({"keyword": keyword, "slug": slug})
    existing_pages = dedupe_pages_by_slug(existing_pages)
    generated_count += 1

    print(
        f"Generated: {slug} ({generated_count}/{DAILY_LIMIT}) "
        f"-> hub: {find_best_hub_slug(keyword)}"
    )

    if generated_count % COMMIT_EVERY == 0:
        git_checkpoint(generated_count, new_generated_keywords, new_generated_slugs, raw_keywords, processed_keywords)

# Final checkpoint
git_checkpoint(generated_count, new_generated_keywords, new_generated_slugs, raw_keywords, processed_keywords)

remaining_count = len(get_remaining_keywords(raw_keywords, processed_keywords))

print(f"\n--- NEXUS DEX SEO BUILD REPORT ---")
print(f"Raw keywords loaded: {len(raw_keywords)}")
print(f"Canonical keywords used: {len(keywords)}")
print(f"Duplicate / fragmented keywords removed: {deduped_count}")
print(f"Duplicate slug groups skipped: {skipped_dup_count}")
print(f"Weak / low-value keywords skipped: {skipped_weak_count}")
print(f"Pages generated: {generated_count}")
print(f"Pages skipped (already on disk): {skipped_existing_count}")
print(f"AI generations rejected: {ai_failure_count}")
print(f"Validation warnings: {validation_error_count}")
print(f"Remaining keywords in queue: {remaining_count}")
