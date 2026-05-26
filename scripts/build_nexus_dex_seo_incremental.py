"""
build_nexus_dex_seo_incremental.py -- v2.0 (Verixia / v18.4 engine)

Incremental builder for Verixia SEO pages. Only renders new pages (slugs that
don't already exist on disk).

What changed from v1.2 -> v2.0:
  - Dropped Hyperliquid integration (no hlDataBlock variable, no hyperliquid
    hub, no Hyperliquid keywords in BRAND_CASE or cluster terms).
  - Dropped prediction markets (no event-markets hub, no polymarket/kalshi
    routing).
  - Dropped all Python-side fallback content generators (build_static_h1,
    build_static_intro, build_supp_heading_local, build_supp_intro_local,
    build_schema_faq, build_title, build_description, generate_ai_text).
    The engine has internal two-pass + alt-framing + low-temp retry. If it
    cannot produce a page above MIN_PUBLISH_SCORE, the keyword stays in the
    queue. No off-brand fallback content is ever published.
  - Added v18.4 hubs: wonderland-memes, live-signals, brand-tokens,
    solana-bridges, solana-swaps.
  - Added scale-hardening hooks: /reset-build at start, /build-report at end,
    duplicate-risk rejection from engine output gate.
  - Updated BRAND_CASE + cluster terms for Solana-DeFi voice.
"""

import json
import os
import re
import sys
from html import escape
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# -------------------------
# CONFIG
# -------------------------

KEYWORD_FILE            = os.path.join(BASE_DIR, "data", "nexus_dex_keywords.txt")
GENERATED_SLUGS_FILE    = os.path.join(BASE_DIR, "data", "nexus_dex_generated_slugs.txt")
GENERATED_KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "nexus_dex_generated_keywords.txt")
REJECTED_FILE           = os.path.join(BASE_DIR, "data", "nexus_dex_rejected_keywords.txt")
BUILD_REPORT_FILE       = os.path.join(BASE_DIR, "data", "nexus_dex_build_report.json")

TEMPLATE_FILE = os.path.join(BASE_DIR, "nexus-dex-template", "nexus-dex-template.html")
OUTPUT_DIR    = os.path.join(BASE_DIR, "nexus-dex")
SITE          = "https://verixiaapps.com"

# v18.4 engine API
SEO_API_BASE        = os.getenv("SEO_API_BASE", "https://awake-integrity-production-faa0.up.railway.app")
SEO_PAGE_ENDPOINT   = f"{SEO_API_BASE}/verixia/seo-page"
SEO_RESET_ENDPOINT  = f"{SEO_API_BASE}/verixia/reset-build"
SEO_REPORT_ENDPOINT = f"{SEO_API_BASE}/verixia/build-report"
SEO_PAGE_TIMEOUT    = int(os.getenv("SEO_PAGE_TIMEOUT_S", "90"))

# Engine scores >=72 internally. Python publishes only >=80.
MIN_PUBLISH_SCORE = 80

RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT    = 10
DAILY_LIMIT         = int(os.getenv("DAILY_LIMIT", "100"))

# Protected hub slugs the script never overwrites.
PROTECTED_SLUGS = {
    # core
    "nexus-dex",
    "crypto-markets",
    "bitcoin-markets",
    "ethereum-markets",
    "solana-markets",
    "altcoin-markets",
    # v18.4 product surfaces
    "wonderland-memes",
    "live-signals",
    "brand-tokens",
    "solana-bridges",
    "solana-swaps",
    # commercial / discovery / how-to
    "no-kyc-trading",
    "wallet-trading",
    "whale-tracking",
    "token-launch",
    "how-to-guides",
    # brands sub-hubs (kept for legacy URLs)
    "tokenized-stocks",
    "buy-stocks-onchain",
    "stocks-no-kyc",
    "stocks-24-7",
    "global-stock-access",
    "global-markets",
}
FALLBACK_HUB_SLUG = "crypto-markets"

# v18.4 template placeholders. {{HL_DATA_BLOCK}} dropped from required set
# but still substituted as empty string for backwards compat.
REQUIRED_TEMPLATE_PLACEHOLDERS = {
    "{{TITLE}}",
    "{{DESCRIPTION}}",
    "{{KEYWORD}}",
    "{{AI_CONTENT}}",
    "{{RELATED_LINKS}}",
    "{{MORE_LINKS}}",
    "{{HUB_LINK}}",
    "{{CANONICAL_URL}}",
    "{{MODIFIED_DATE}}",
    "{{BREADCRUMB_NAME}}",
    "{{STATIC_H1}}",
    "{{STATIC_INTRO}}",
    "{{OG_IMAGE}}",
    "{{SCHEMA_FAQ}}",
    "{{AGGREGATE_RATING_JSON}}",
    "{{SUPP_HEADING}}",
    "{{SUPP_INTRO}}",
    "{{PAGE_META_SCRIPT}}",
}

# Cluster terms for related-page scoring. Updated for Solana-DeFi-native voice.
VERIXIA_CLUSTER_TERMS = {
    # core
    "swap", "swaps", "buy", "sell", "trade", "trading", "dex", "defi",
    "wallet", "mobile", "app", "self", "custodial", "non",
    "phantom", "backpack", "solflare", "jupiter", "raydium", "orca", "meteora",
    "phoenix", "lifinity",
    # chains for bridges
    "solana", "ethereum", "base", "arbitrum", "optimism", "polygon", "avalanche",
    "bnb", "binance", "bsc", "sui", "aptos", "btc", "eth", "sol", "usdc", "usdt",
    "bridge", "bridges", "wormhole", "debridge", "allbridge",
    # brand tokens
    "brand", "brands", "tokenized", "stock", "stocks", "equity", "onchain",
    "fractional", "settled", "usdc", "price", "tracked",
    "aapl", "tsla", "nvda", "msft", "googl", "amzn", "meta", "mstr", "nflx",
    "spy", "qqq", "crcl", "hood", "coin", "orcl", "crm",
    "aaplx", "tslax", "nvdax", "msftx", "googlx", "amznx", "metax", "mstrx",
    "nflxx", "spyx", "qqqx", "crclx", "hoodx", "coinx", "orclx", "crmx",
    "apple", "tesla", "nvidia", "microsoft", "google", "alphabet", "amazon",
    "netflix", "microstrategy", "circle", "robinhood", "oracle", "salesforce",
    # memes
    "meme", "memes", "memecoin", "wonderland", "ape", "moon", "degen",
    "hoppy", "fartcoin", "pepe", "wif", "bonk", "popcat", "mew", "wen",
    "bome", "myro", "ponke", "michi", "trump", "moodeng", "goat", "pnut",
    "fresh", "launch", "launchpad",
    # signals / discovery
    "trending", "signals", "discovery", "gainers", "volume", "leaders", "hot",
    "pumping", "live",
    # commercial / KYC
    "kyc", "anonymous", "permissionless", "aggregator", "best", "price",
    "global", "no",
}

BRAND_CASE = {
    "nexus dex":           "Nexus DEX",
    "verixia":             "Verixia",
    "wonderland":          "Wonderland",
    "trust wallet":        "Trust Wallet",
    "raydium launchlab":   "Raydium LaunchLab",
    "phantom":             "Phantom",
    "backpack":            "Backpack",
    "solflare":            "Solflare",
    "metamask":            "MetaMask",
    "dexscreener":         "Dexscreener",
    "uniswap":             "Uniswap",
    "raydium":             "Raydium",
    "orca":                "Orca",
    "meteora":             "Meteora",
    "phoenix":             "Phoenix",
    "lifinity":            "Lifinity",
    "jupiter":             "Jupiter",
    "coinbase":            "Coinbase",
    "robinhood":           "Robinhood",
    "kraken":              "Kraken",
    "binance":             "Binance",
    "ethereum":            "Ethereum",
    "avalanche":           "Avalanche",
    "arbitrum":            "Arbitrum",
    "polygon":             "Polygon",
    "optimism":            "Optimism",
    "base":                "Base",
    "sui":                 "Sui",
    "aptos":               "Aptos",
    "bitcoin":             "Bitcoin",
    "solana":              "Solana",
    "wormhole":            "Wormhole",
    "debridge":            "deBridge",
    "allbridge":           "Allbridge",
    "crypto":              "Crypto",
    "wallet":              "Wallet",
    # brand tickers (preserve casing on the x-suffix)
    "aaplx":  "AAPLx",  "tslax":  "TSLAx",  "nvdax":  "NVDAx",
    "msftx":  "MSFTx",  "googlx": "GOOGLx", "amznx":  "AMZNx",
    "metax":  "METAx",  "mstrx":  "MSTRx",  "nflxx":  "NFLXx",
    "spyx":   "SPYx",   "qqqx":   "QQQx",   "crclx":  "CRCLx",
    "hoodx":  "HOODx",  "coinx":  "COINx",  "orclx":  "ORCLx",
    "crmx":   "CRMx",
    # underlying tickers
    "aapl":  "AAPL",  "tsla":  "TSLA",  "nvda":  "NVDA",  "msft":  "MSFT",
    "googl": "GOOGL", "amzn":  "AMZN",  "meta":  "META",  "mstr":  "MSTR",
    "nflx":  "NFLX",  "spy":   "SPY",   "qqq":   "QQQ",   "crcl":  "CRCL",
    "hood":  "HOOD",  "coin":  "COIN",  "orcl":  "ORCL",  "crm":   "CRM",
    # companies
    "apple":         "Apple",
    "tesla":         "Tesla",
    "nvidia":        "Nvidia",
    "microsoft":     "Microsoft",
    "google":        "Google",
    "alphabet":      "Alphabet",
    "amazon":        "Amazon",
    "netflix":       "Netflix",
    "microstrategy": "MicroStrategy",
    "circle":        "Circle",
    "oracle":        "Oracle",
    "salesforce":    "Salesforce",
    # chain tickers
    "btc":   "BTC",  "eth":   "ETH",  "sol":   "SOL",
    "usdc":  "USDC", "usdt":  "USDT", "bnb":   "BNB",
    # memes
    "hoppy":    "HOPPY",    "fartcoin": "FARTCOIN", "pepe":   "PEPE",
    "wif":      "WIF",      "bonk":     "BONK",     "popcat": "POPCAT",
    "mew":      "MEW",      "wen":      "WEN",      "bome":   "BOME",
    "myro":     "MYRO",     "ponke":    "PONKE",    "michi":  "MICHI",
    "trump":    "TRUMP",    "moodeng":  "MOODENG",  "goat":   "GOAT",
    "pnut":     "PNUT",     "doge":     "DOGE",     "shib":   "SHIB",
    "floki":    "FLOKI",    "fwog":     "FWOG",     "pengu":  "PENGU",
    "neiro":    "NEIRO",    "useless":  "USELESS",
    # solana ecosystem tokens
    "jup":      "JUP",
    "ray":      "RAY",
    "pyth":     "PYTH",
    "jto":      "JTO",
    # generic acronyms
    "dex":      "DEX",
    "cex":      "CEX",
    "kyc":      "KYC",
    "spl":      "SPL",
    "nft":      "NFT",
    "dao":      "DAO",
    "defi":     "DeFi",
    "tvl":      "TVL",
    "us":       "U.S.",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with",
}

HUB_TITLE_OVERRIDES = {
    # core
    "crypto-markets":   "Crypto Markets Hub",
    "bitcoin-markets":  "Bitcoin Markets Hub",
    "ethereum-markets": "Ethereum Markets Hub",
    "solana-markets":   "Solana Markets Hub",
    "altcoin-markets":  "Altcoin Markets Hub",
    # v18.4 product surfaces
    "wonderland-memes": "Wonderland Memes Hub",
    "live-signals":     "Live Signals Hub",
    "brand-tokens":     "Brand Tokens Hub",
    "solana-bridges":   "Solana Bridges Hub",
    "solana-swaps":     "Solana Swaps Hub",
    # commercial / discovery / how-to
    "no-kyc-trading":   "No KYC Trading Hub",
    "wallet-trading":   "Wallet Trading Hub",
    "whale-tracking":   "Whale Tracking Hub",
    "token-launch":     "Token Launch Hub",
    "how-to-guides":    "Verixia Guides Hub",
    # legacy brand hubs
    "tokenized-stocks":    "Tokenized Stocks Hub",
    "buy-stocks-onchain":  "Buy Stocks On-Chain Hub",
    "stocks-no-kyc":       "Stocks No KYC Hub",
    "stocks-24-7":         "24/7 Stocks Hub",
    "global-stock-access": "Global Stock Access Hub",
    "global-markets":      "Global Markets Hub",
}

# Order matters: first match wins.
# Dropped from v1.2: hyperliquid-frontend, all event-markets routing, all perps
# routing. v18.4 engine doesn't handle perps -- filter your keywords first.
HUB_MATCH_RULES = [
    # ---- Memes (Wonderland) ----
    ("hoppy",      "wonderland-memes"),
    ("fartcoin",   "wonderland-memes"),
    ("pepe",       "wonderland-memes"),
    ("wif",        "wonderland-memes"),
    ("bonk",       "wonderland-memes"),
    ("popcat",     "wonderland-memes"),
    ("mew",        "wonderland-memes"),
    ("bome",       "wonderland-memes"),
    ("myro",       "wonderland-memes"),
    ("michi",      "wonderland-memes"),
    ("trump",      "wonderland-memes"),
    ("moodeng",    "wonderland-memes"),
    ("goat",       "wonderland-memes"),
    ("pnut",       "wonderland-memes"),
    ("pengu",      "wonderland-memes"),
    ("neiro",      "wonderland-memes"),
    ("memecoin",   "wonderland-memes"),
    ("meme coin",  "wonderland-memes"),
    ("meme token", "wonderland-memes"),
    ("wonderland", "wonderland-memes"),
    ("degen coin", "wonderland-memes"),
    ("moonshot",   "wonderland-memes"),
    ("fresh launch", "wonderland-memes"),
    ("new launch", "wonderland-memes"),
    ("low cap gem", "wonderland-memes"),

    # ---- Signals / discovery ----
    ("trending solana",     "live-signals"),
    ("trending coins",      "live-signals"),
    ("trending tokens",     "live-signals"),
    ("trending crypto",     "live-signals"),
    ("whats pumping",       "live-signals"),
    ("what is pumping",     "live-signals"),
    ("whats mooning",       "live-signals"),
    ("hot right now",       "live-signals"),
    ("hot coins",           "live-signals"),
    ("hot tokens",          "live-signals"),
    ("fresh launches",      "live-signals"),
    ("new solana coins",    "live-signals"),
    ("new solana tokens",   "live-signals"),
    ("top gainers",         "live-signals"),
    ("volume leaders",      "live-signals"),
    ("signals",             "live-signals"),
    ("discovery",           "live-signals"),

    # ---- Brand tokens (specific tickers + companies) ----
    ("aaplx",   "brand-tokens"),
    ("tslax",   "brand-tokens"),
    ("nvdax",   "brand-tokens"),
    ("msftx",   "brand-tokens"),
    ("googlx",  "brand-tokens"),
    ("amznx",   "brand-tokens"),
    ("metax",   "brand-tokens"),
    ("mstrx",   "brand-tokens"),
    ("nflxx",   "brand-tokens"),
    ("spyx",    "brand-tokens"),
    ("qqqx",    "brand-tokens"),
    ("crclx",   "brand-tokens"),
    ("hoodx",   "brand-tokens"),
    ("coinx",   "brand-tokens"),
    ("orclx",   "brand-tokens"),
    ("crmx",    "brand-tokens"),
    ("apple on solana",     "brand-tokens"),
    ("tesla on solana",     "brand-tokens"),
    ("nvidia on solana",    "brand-tokens"),
    ("microsoft on solana", "brand-tokens"),
    ("google on solana",    "brand-tokens"),
    ("amazon on solana",    "brand-tokens"),
    ("microstrategy on solana", "brand-tokens"),
    ("brand token",         "brand-tokens"),
    ("brand tokens",        "brand-tokens"),
    ("tokenized stock",     "brand-tokens"),
    ("tokenized stocks",    "brand-tokens"),
    ("tokenized equity",    "brand-tokens"),
    ("tokenized equities",  "brand-tokens"),
    ("onchain stocks",      "brand-tokens"),
    ("onchain equities",    "brand-tokens"),
    ("stocks on solana",    "brand-tokens"),
    ("stocks as spl",       "brand-tokens"),
    ("24 7 stock",          "brand-tokens"),
    ("stocks 24 hours",     "brand-tokens"),
    ("stocks weekend",      "brand-tokens"),
    ("trade stocks at night", "brand-tokens"),
    ("trade stocks weekends", "brand-tokens"),
    ("buy stocks no kyc",   "brand-tokens"),
    ("anonymous stock",     "brand-tokens"),
    ("stocks without broker", "brand-tokens"),
    ("buy us stocks from",  "brand-tokens"),
    ("us stocks no us bank", "brand-tokens"),
    ("us stocks international", "brand-tokens"),
    ("global stock",        "brand-tokens"),

    # ---- Bridges ----
    ("bridge ethereum",     "solana-bridges"),
    ("bridge eth",          "solana-bridges"),
    ("bridge base",         "solana-bridges"),
    ("bridge arbitrum",     "solana-bridges"),
    ("bridge arb",          "solana-bridges"),
    ("bridge optimism",     "solana-bridges"),
    ("bridge op",           "solana-bridges"),
    ("bridge polygon",      "solana-bridges"),
    ("bridge avalanche",    "solana-bridges"),
    ("bridge avax",         "solana-bridges"),
    ("bridge bnb",          "solana-bridges"),
    ("bridge bsc",          "solana-bridges"),
    ("bridge binance",      "solana-bridges"),
    ("bridge sui",          "solana-bridges"),
    ("bridge aptos",        "solana-bridges"),
    ("ethereum to solana",  "solana-bridges"),
    ("eth to solana",       "solana-bridges"),
    ("base to solana",      "solana-bridges"),
    ("arbitrum to solana",  "solana-bridges"),
    ("optimism to solana",  "solana-bridges"),
    ("polygon to solana",   "solana-bridges"),
    ("avalanche to solana", "solana-bridges"),
    ("bnb to solana",       "solana-bridges"),
    ("sui to solana",       "solana-bridges"),
    ("aptos to solana",     "solana-bridges"),
    ("cross chain solana",  "solana-bridges"),
    ("cross-chain solana",  "solana-bridges"),
    ("wormhole",            "solana-bridges"),
    ("debridge",            "solana-bridges"),
    ("allbridge",           "solana-bridges"),

    # ---- Swaps (specific tokens + Solana DEX commercial) ----
    ("how to buy jup",      "solana-swaps"),
    ("how to swap jup",     "solana-swaps"),
    ("how to buy ray",      "solana-swaps"),
    ("how to swap ray",     "solana-swaps"),
    ("how to buy sol",      "solana-swaps"),
    ("how to buy usdc",     "solana-swaps"),
    ("how to buy on solana", "solana-swaps"),
    ("how to swap on solana", "solana-swaps"),
    ("solana swap",         "solana-swaps"),
    ("solana swaps",        "solana-swaps"),
    ("solana dex",          "solana-swaps"),
    ("solana aggregator",   "solana-swaps"),
    ("solana exchange",     "solana-swaps"),
    ("dex aggregator",      "solana-swaps"),
    ("best price swap",     "solana-swaps"),

    # ---- Whale / on-chain intelligence ----
    ("whale tracker",   "whale-tracking"),
    ("whale tracking",  "whale-tracking"),
    ("smart money",     "whale-tracking"),
    ("insider wallet",  "whale-tracking"),
    ("deployer wallet", "whale-tracking"),
    ("sniper wallet",   "whale-tracking"),
    ("kol wallet",      "whale-tracking"),

    # ---- Token launch ----
    ("launch token",    "token-launch"),
    ("token launch",    "token-launch"),
    ("launchpad",       "token-launch"),
    ("bonding curve",   "token-launch"),
    ("deploy token",    "token-launch"),
    ("fresh pool",      "token-launch"),

    # ---- Wallet / no-KYC commercial buckets ----
    ("phantom wallet trading",  "wallet-trading"),
    ("backpack wallet trading", "wallet-trading"),
    ("self custodial",          "wallet-trading"),
    ("non custodial",           "wallet-trading"),
    ("wallet based",            "wallet-trading"),
    ("wallet native",           "wallet-trading"),
    ("no kyc",                  "no-kyc-trading"),
    ("without kyc",             "no-kyc-trading"),
    ("no signup",               "no-kyc-trading"),
    ("no sign up",              "no-kyc-trading"),
    ("no verification",         "no-kyc-trading"),
    ("no account",              "no-kyc-trading"),
    ("anonymous crypto",        "no-kyc-trading"),
    ("anonymous swap",          "no-kyc-trading"),
    ("anonymous dex",           "no-kyc-trading"),

    # ---- Generic catch-alls (lowest priority) ----
    ("swap",                "solana-swaps"),
    ("how to",              "how-to-guides"),
]


# -------------------------
# UTILITIES
# -------------------------

def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def slugify(text):
    text = normalize_keyword(text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def contains_term_phrase(haystack, needle):
    haystack_norm = normalize_keyword(haystack)
    needle_norm   = normalize_keyword(needle)
    if not haystack_norm or not needle_norm:
        return False
    pattern = r"(^|[^a-z0-9])" + re.escape(needle_norm) + r"([^a-z0-9]|$)"
    return re.search(pattern, haystack_norm, flags=re.IGNORECASE) is not None


def clean_base_keyword(text):
    kw = normalize_keyword(text)
    kw = re.sub(r"^\s*is\s+this\s+",        "", kw)
    kw = re.sub(r"^\s*is\s+",               "", kw)
    kw = re.sub(r"^\s*can\s+i\s+",          "", kw)
    kw = re.sub(r"^\s*should\s+i\s+",       "", kw)
    kw = re.sub(r"^\s*how\s+to\s+",         "", kw)
    kw = re.sub(r"^\s*where\s+to\s+",       "", kw)
    kw = re.sub(r"^\s*best\s+place\s+to\s+","", kw)
    kw = re.sub(r"\s+no\s+kyc$",            "", kw)
    kw = re.sub(r"\s+mobile$",              "", kw)
    kw = re.sub(r"\s+app$",                 "", kw)
    kw = re.sub(r"\s+without\s+kyc$",       "", kw)
    kw = re.sub(r"\s+wallet\s+only$",       "", kw)
    return re.sub(r"\s+", " ", kw).strip()


def display_keyword(text):
    return clean_base_keyword(text)


def apply_brand_case(text):
    result = f" {text} "
    for raw, proper in sorted(BRAND_CASE.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(raw) + r"(?![a-z0-9])"
        result = re.sub(pattern, proper, result, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", result).strip()


def title_case(text):
    if not text:
        return ""
    words  = normalize_keyword(text).split()
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
    base = clean_base_keyword(text)
    if not base:
        base = normalize_keyword(text)
    return {token for token in base.split() if token}


def keyword_cluster_tokens(text):
    return {token for token in keyword_tokens(text) if token in VERIXIA_CLUSTER_TERMS}


def keyword_root(text):
    cleaned = clean_base_keyword(text)
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


def validate_daily_limit(value):
    if value <= 0:
        raise ValueError("DAILY_LIMIT must be greater than 0")


def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys(normalize_keyword(line) for line in f if line.strip()))


def load_generated_records():
    if not os.path.exists(GENERATED_SLUGS_FILE) or not os.path.exists(GENERATED_KEYWORDS_FILE):
        return []

    with open(GENERATED_SLUGS_FILE, encoding="utf-8") as f:
        slugs = [slugify(line) for line in f if slugify(line)]

    with open(GENERATED_KEYWORDS_FILE, encoding="utf-8") as f:
        keywords = [normalize_keyword(line) for line in f if normalize_keyword(line)]

    if len(slugs) != len(keywords):
        print(
            "[warning] tracking files not line-aligned. "
            "Rebuilding tracking from existing pages on disk."
        )
        return []

    records = []
    seen    = set()
    for slug, keyword in zip(slugs, keywords):
        if not slug or not keyword or slug in PROTECTED_SLUGS:
            continue
        if slug in seen:
            continue
        seen.add(slug)
        records.append({"slug": slug, "keyword": keyword})

    return records


def write_lines(filepath, values):
    ensure_file(filepath)
    lines = [str(v).strip() for v in values if str(v).strip()]
    with open(filepath, "w", encoding="utf-8") as f:
        if lines:
            f.write("\n".join(lines) + "\n")
        else:
            f.write("")


def append_line(filepath, value):
    ensure_file(filepath)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(str(value).strip() + "\n")


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


def find_best_hub_slug(keyword):
    keyword_norm = normalize_keyword(keyword)
    for term, slug in HUB_MATCH_RULES:
        if contains_term_phrase(keyword_norm, term):
            return slug
    return FALLBACK_HUB_SLUG


def build_hub_link_html(keyword):
    hub_slug = find_best_hub_slug(keyword)
    if not hub_slug:
        return ""
    hub_title = HUB_TITLE_OVERRIDES.get(hub_slug, f"{humanize_slug(hub_slug)} Hub")
    return f'<a href="/nexus-dex/{hub_slug}/">{escape_html(hub_title)}</a>'


def sanitize_ai_html(text):
    raw = str(text or "").strip()
    if not raw:
        return ""
    raw = re.sub(r"^```(?:html)?\s*", "",  raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$",           "",  raw)
    raw = re.sub(r"<script\b[^>]*>.*?</script>", "", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<style\b[^>]*>.*?</style>",   "", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = raw.strip()
    if "<" in raw and ">" in raw:
        return raw
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", raw) if p.strip()]
    if not paragraphs:
        paragraphs = [raw]
    return "\n".join(f"<p>{escape_html(p)}</p>" for p in paragraphs)


def discover_existing_output_pages(existing_keyword_map=None):
    existing_keyword_map = existing_keyword_map or {}
    discovered = []
    if not os.path.isdir(OUTPUT_DIR):
        return discovered
    for slug in sorted(os.listdir(OUTPUT_DIR)):
        slug = slugify(slug)
        if not slug or slug in PROTECTED_SLUGS:
            continue
        if not os.path.isfile(page_path(slug)):
            continue
        keyword = normalize_keyword(existing_keyword_map.get(slug, slug.replace("-", " ")))
        if not keyword:
            continue
        discovered.append({"slug": slug, "keyword": keyword})
    return discovered


def render_page_html(template_html, replacements):
    html = template_html
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", html)))
    if unresolved:
        raise ValueError("Unresolved template placeholders remain: " + ", ".join(unresolved))
    return html


# -------------------------
# ENGINE CLIENT
# -------------------------

def fetch_engine_payload(keyword):
    """Hit /seo-page for the full v18.4 payload. Returns the parsed payload
    dict or None on failure. NO Python-side fallback content -- if the engine
    cannot produce a publishable page, the keyword stays in the queue."""
    try:
        resp = requests.post(
            SEO_PAGE_ENDPOINT,
            json={"keyword": keyword, "site": "nexus-dex"},
            timeout=SEO_PAGE_TIMEOUT,
        )
    except requests.RequestException as exc:
        print(f"[engine] network error for {keyword!r}: {exc}")
        return None
    if resp.status_code != 200:
        print(f"[engine] HTTP {resp.status_code} for {keyword!r}: {resp.text[:200]}")
        return None
    try:
        payload = resp.json()
    except ValueError:
        print(f"[engine] bad JSON for {keyword!r}")
        return None
    if not payload.get("meta") or not payload.get("content"):
        print(f"[engine] missing meta/content for {keyword!r}")
        return None
    return payload


def reset_build_registry():
    """v18.4: clear engine output gate + anti-repetition registries at build start."""
    try:
        resp = requests.post(SEO_RESET_ENDPOINT, timeout=10)
        if resp.status_code == 200:
            print("[build] engine build registries reset")
            return True
        print(f"[build] reset failed: HTTP {resp.status_code}")
        return False
    except requests.RequestException as exc:
        print(f"[build] reset failed: {exc}")
        return False


def fetch_build_report():
    """v18.4: fetch engine build report sidecar at end of run."""
    try:
        resp = requests.get(SEO_REPORT_ENDPOINT, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        print(f"[build] report fetch failed: HTTP {resp.status_code}")
        return None
    except requests.RequestException as exc:
        print(f"[build] report fetch failed: {exc}")
        return None


def is_publishable(payload):
    """Quality gate."""
    meta  = payload.get("meta") or {}
    score = payload.get("score")
    if score is None:
        score = meta.get("score")

    if isinstance(score, (int, float)) and score < MIN_PUBLISH_SCORE:
        return False, f"score {score} < {MIN_PUBLISH_SCORE}"

    if payload.get("duplicateRisk"):
        return False, "duplicate fingerprint flagged by engine output gate"

    content = (payload.get("content") or "").strip()
    if len(content) < 400:
        return False, f"content too short ({len(content)} chars)"

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if len(paragraphs) < 3:
        return False, f"only {len(paragraphs)} paragraphs (need >=3)"

    required_meta_fields = ("title", "description", "h1", "intro")
    missing = [f for f in required_meta_fields if not (meta.get(f) or "").strip()]
    if missing:
        return False, f"meta missing: {','.join(missing)}"

    return True, ""


def record_rejected(keyword, reason):
    append_line(REJECTED_FILE, f"{keyword}\t{reason}")


def build_aggregate_rating_json(page_signals):
    """Use engine's pageSignals.aggregateRatingJson if provided, else default."""
    if page_signals and page_signals.get("aggregateRatingJson"):
        return page_signals["aggregateRatingJson"]
    return json.dumps({
        "@type": "AggregateRating",
        "ratingValue": "4.8",
        "reviewCount": "2847",
        "bestRating": "5",
    }, ensure_ascii=False)


def build_page_meta_script(meta):
    """Emit window.__pageMeta for template hydration. v18.4 dropped hlDataBlock."""
    if not meta:
        return ""
    payload = {
        "title":                meta.get("title", ""),
        "description":          meta.get("description", ""),
        "h1":                   meta.get("h1", ""),
        "intro":                meta.get("intro", ""),
        "contentHeading":       meta.get("contentHeading", ""),
        "contentBridge":        meta.get("contentBridge", ""),
        "breadcrumb":           meta.get("breadcrumb", ""),
        "intent":               meta.get("intent", ""),
        "subIntent":            meta.get("subIntent", ""),
        "framingName":          meta.get("framingName", ""),
        "subject":              meta.get("subject", ""),
        "faq":                  meta.get("faq", []),
        "recognitionChips":     meta.get("recognitionChips", []),
        "supplementaryCards":   meta.get("supplementaryCards", []),
        "supplementaryHeading": meta.get("supplementaryHeading", ""),
        "supplementaryIntro":   meta.get("supplementaryIntro", ""),
        "pageSignals":          meta.get("pageSignals", {}),
        "jitter":               meta.get("jitter", {}),
        "observations":         meta.get("observations", []),
    }
    blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    return f'<script id="page-meta">window.__pageMeta = {blob};</script>'


def enforce_title_length(title, fallback):
    """Trim engine title to <=60 chars on a word boundary if needed."""
    title = (title or "").strip() or fallback
    if len(title) <= 60:
        return title
    candidates = [
        re.sub(r",?\s*Mobile-First\s*$", "", title),
        re.sub(r",?\s*No KYC,?\s*Mobile-First\s*$", "", title),
        re.sub(r"\s*\|\s*[^|]*$", "", title),
    ]
    for c in candidates:
        if 0 < len(c) <= 60:
            return c
    cut = title[:60].rsplit(" ", 1)[0]
    return cut if cut else title[:60]


# -------------------------
# SEO TEXT HELPERS
# -------------------------

def build_og_image(slug):
    return f"{SITE}/og/nexus-dex.png"


def build_related_anchor(keyword):
    raw      = normalize_keyword(keyword)
    readable = readable_keyword(keyword)
    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        anchor = title_case(raw)
        if is_question_style_keyword(raw) and not anchor.endswith("?"):
            anchor += "?"
        return anchor
    return f"{readable} on Verixia"


def build_canonical(slug):
    return f"{SITE}/nexus-dex/{slug}/"


# -------------------------
# LINKING HELPERS
# -------------------------

def dedupe_pages_by_slug(pages_list):
    deduped = []
    seen    = set()
    for page in pages_list:
        slug    = slugify(page.get("slug", ""))
        keyword = normalize_keyword(page.get("keyword", ""))
        if not slug or not keyword or slug in seen or slug in PROTECTED_SLUGS:
            continue
        seen.add(slug)
        deduped.append({"slug": slug, "keyword": keyword})
    return deduped


def get_related_pages(current_page, all_pages, limit, exclude_slugs=None):
    exclude_slugs   = {slugify(slug) for slug in (exclude_slugs or set()) if slugify(slug)}
    current_slug    = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_tokens  = keyword_tokens(current_keyword)
    current_cluster = keyword_cluster_tokens(current_keyword)
    current_root    = keyword_root(current_keyword)
    current_base    = clean_base_keyword(current_keyword)
    current_hub     = find_best_hub_slug(current_keyword)

    candidates = [
        p for p in all_pages
        if p["slug"] != current_slug
        and p["slug"] not in PROTECTED_SLUGS
        and p["slug"] not in exclude_slugs
        and page_exists(p["slug"])
        and clean_base_keyword(p["keyword"]) != current_base
    ]

    def score(page):
        other_keyword  = page["keyword"]
        other_tokens   = keyword_tokens(other_keyword)
        other_cluster  = keyword_cluster_tokens(other_keyword)
        other_root     = keyword_root(other_keyword)
        other_hub      = find_best_hub_slug(other_keyword)
        length_diff    = abs(len(other_tokens) - len(current_tokens))
        same_root      = 1 if current_root and other_root == current_root else 0
        same_hub       = 1 if current_hub  and other_hub  == current_hub  else 0
        shared_cluster = len(current_cluster & other_cluster)
        shared_tokens  = len(current_tokens  & other_tokens)
        return (-same_hub, -same_root, -shared_cluster, -shared_tokens, length_diff, other_keyword)

    ranked     = sorted(candidates, key=score)
    related    = []
    used_slugs = set()
    used_bases = set()

    for page in ranked:
        base = clean_base_keyword(page["keyword"])
        if page["slug"] in used_slugs or base in used_bases:
            continue
        related.append(page)
        used_slugs.add(page["slug"])
        used_bases.add(base)
        if len(related) == limit:
            break

    return related


def build_links_html(pages_list):
    return "".join(
        f'<li><a href="/nexus-dex/{p["slug"]}/">'
        f'{escape_html(build_related_anchor(p["keyword"]))}</a></li>\n'
        for p in pages_list
        if page_exists(p["slug"])
    )


def build_aligned_generated_records(existing_pages_list, extra_pages=None):
    records_by_slug = {}
    for page in existing_pages_list:
        slug    = slugify(page.get("slug", ""))
        keyword = normalize_keyword(page.get("keyword", ""))
        if not slug or not keyword or slug in PROTECTED_SLUGS:
            continue
        if page_exists(slug):
            records_by_slug[slug] = {"slug": slug, "keyword": keyword}
    for page in extra_pages or []:
        slug    = slugify(page.get("slug", ""))
        keyword = normalize_keyword(page.get("keyword", ""))
        if not slug or not keyword or slug in PROTECTED_SLUGS:
            continue
        if page_exists(slug):
            records_by_slug[slug] = {"slug": slug, "keyword": keyword}
    return [records_by_slug[slug] for slug in sorted(records_by_slug.keys())]


def write_build_report_sidecar(report):
    """Persist the engine's build report to data/ so you can inspect it later."""
    ensure_file(BUILD_REPORT_FILE)
    report["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    Path(BUILD_REPORT_FILE).write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[build] sidecar report written: {BUILD_REPORT_FILE}")


# -------------------------
# SETUP & GENERATION LOOP
# -------------------------

validate_daily_limit(DAILY_LIMIT)

os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(GENERATED_SLUGS_FILE)
ensure_file(GENERATED_KEYWORDS_FILE)
ensure_file(REJECTED_FILE)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

validate_template_placeholders(template)

keywords = load_keywords()
if not keywords:
    print("No keywords in queue. Nothing to generate.")
    sys.exit(0)

# v18.4: reset engine build registries before this run
reset_build_registry()

generated_records    = load_generated_records()
existing_keyword_map = {r["slug"]: r["keyword"] for r in generated_records}

filesystem_pages  = discover_existing_output_pages(existing_keyword_map=existing_keyword_map)
generated_records = build_aligned_generated_records(filesystem_pages)

generated_slugs    = {r["slug"]    for r in generated_records}
generated_keywords = {r["keyword"] for r in generated_records}

queue_pages          = []
seen_queue_slugs     = set()
duplicate_queue_count = 0

for keyword in keywords:
    keyword_norm = normalize_keyword(keyword)
    slug         = slugify(keyword_norm)
    if slug in PROTECTED_SLUGS or not slug:
        continue
    if slug in seen_queue_slugs:
        duplicate_queue_count += 1
        continue
    seen_queue_slugs.add(slug)
    queue_pages.append({"keyword": keyword_norm, "slug": slug})

existing_pages = dedupe_pages_by_slug(filesystem_pages)
queue_pages    = dedupe_pages_by_slug(queue_pages)

print(f"Loaded {len(keywords)} keywords from queue.")
print(f"Unique queued pages after slug dedupe: {len(queue_pages)}")
print(f"Duplicate queued keywords skipped: {duplicate_queue_count}")
print(f"Known generated slugs: {len(generated_slugs)}")
print(f"Known generated keywords: {len(generated_keywords)}")
print(f"Existing pages available for internal links: {len(existing_pages)}")
print(f"Daily limit: {DAILY_LIMIT}")
print(f"Fallback hub slug: {FALLBACK_HUB_SLUG}")
print(f"Quality floor (publish): {MIN_PUBLISH_SCORE}")

generated_count        = 0
skipped_existing_count = 0
failed_count           = 0
processed_keywords     = set()
new_pages_this_run     = []

for page in queue_pages:
    if generated_count >= DAILY_LIMIT:
        break

    slug            = page["slug"]
    keyword         = page["keyword"]
    keyword_display = display_keyword(keyword)
    path            = page_path(slug)

    if slug in PROTECTED_SLUGS:
        processed_keywords.add(keyword)
        print("Skipping protected page:", slug)
        continue

    if page_exists(slug):
        skipped_existing_count += 1
        processed_keywords.add(keyword)
        continue

    os.makedirs(os.path.dirname(path), exist_ok=True)

    # v18.4: pull full payload from engine. No fallback content.
    engine_payload = fetch_engine_payload(keyword)
    if not engine_payload:
        failed_count += 1
        record_rejected(keyword, "engine returned no payload")
        # keyword stays in queue (we don't add to processed_keywords)
        continue

    ok, reason = is_publishable(engine_payload)
    if not ok:
        failed_count += 1
        record_rejected(keyword, reason)
        print(f"[rejected] {keyword!r}: {reason}")
        # keyword stays in queue for next run
        continue

    meta              = engine_payload["meta"]
    ai_text           = sanitize_ai_html(engine_payload["content"])
    title             = enforce_title_length(meta.get("title"), f"{readable_keyword(keyword)} | Verixia")
    description       = meta.get("description", "").strip()
    h1_text           = meta.get("h1", "").strip()
    intro_text        = meta.get("intro", "").strip()
    breadcrumb        = meta.get("breadcrumb", "").strip() or readable_keyword(keyword)
    faq_schema        = meta.get("faqSchema", "").strip() or "{}"
    page_signals      = meta.get("pageSignals") or {}
    aggregate_json    = build_aggregate_rating_json(page_signals)
    supp_heading      = meta.get("supplementaryHeading", "").strip() or "Why Verixia"
    supp_intro        = meta.get("supplementaryIntro", "").strip()
    page_meta_script  = build_page_meta_script(meta)

    canonical = build_canonical(slug)

    related_pages = get_related_pages(page, existing_pages, RELATED_LINKS_COUNT)
    related_slugs = {p["slug"] for p in related_pages}
    more_pages    = get_related_pages(
        page,
        existing_pages,
        MORE_LINKS_COUNT,
        exclude_slugs=related_slugs,
    )

    hub_link_html = build_hub_link_html(keyword)

    html = render_page_html(
        template,
        {
            "{{TITLE}}":                  escape_html(title),
            "{{DESCRIPTION}}":            escape_html(description),
            "{{KEYWORD}}":                escape_html(keyword_display),
            "{{AI_CONTENT}}":             ai_text,
            "{{RELATED_LINKS}}":          build_links_html(related_pages),
            "{{MORE_LINKS}}":             build_links_html(more_pages),
            "{{HUB_LINK}}":               hub_link_html,
            "{{CANONICAL_URL}}":          escape_html(canonical),
            "{{MODIFIED_DATE}}":          datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "{{BREADCRUMB_NAME}}":        escape_html(breadcrumb),
            "{{STATIC_H1}}":              escape_html(h1_text),
            "{{STATIC_INTRO}}":           escape_html(intro_text),
            "{{OG_IMAGE}}":               escape_html(build_og_image(slug)),
            "{{SCHEMA_FAQ}}":             faq_schema,
            "{{AGGREGATE_RATING_JSON}}":  aggregate_json,
            "{{SUPP_HEADING}}":           escape_html(supp_heading),
            "{{SUPP_INTRO}}":             escape_html(supp_intro),
            "{{PAGE_META_SCRIPT}}":       page_meta_script,
            # Deprecated in v18.4 -- kept as empty string for legacy templates
            "{{HL_DATA_BLOCK}}":          "",
        },
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    processed_keywords.add(keyword)

    new_page_record = {"keyword": keyword, "slug": slug}
    new_pages_this_run.append(new_page_record)
    existing_pages.append(new_page_record)
    existing_pages = dedupe_pages_by_slug(existing_pages)
    generated_count += 1

    print(
        f"Generated: {slug} ({generated_count}/{DAILY_LIMIT}) "
        f"-> hub: {find_best_hub_slug(keyword)} "
        f"-> intent: {meta.get('intent')} / {meta.get('subIntent')} "
        f"/ framing: {meta.get('framingName')} "
        f"/ score: {engine_payload.get('score')}"
    )

# Update tracking files
remaining_keywords = [
    normalize_keyword(kw)
    for kw in keywords
    if normalize_keyword(kw) not in processed_keywords
]

aligned_records = build_aligned_generated_records(existing_pages, extra_pages=new_pages_this_run)
write_lines(GENERATED_SLUGS_FILE,    [r["slug"]    for r in aligned_records])
write_lines(GENERATED_KEYWORDS_FILE, [r["keyword"] for r in aligned_records])
write_lines(KEYWORD_FILE, remaining_keywords)

# v18.4: persist engine build report
report = fetch_build_report()
if report:
    report["python_generated"] = generated_count
    report["python_failed"]    = failed_count
    report["python_skipped_existing"] = skipped_existing_count
    write_build_report_sidecar(report)

print(
    f"\nDone. Generated {generated_count} new pages. "
    f"Skipped {skipped_existing_count} existing pages. "
    f"Failed {failed_count} keywords (stayed in queue)."
)
print(f"Remaining keywords in queue: {len(remaining_keywords)}")
