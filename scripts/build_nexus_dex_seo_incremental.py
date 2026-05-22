import json
import os
import re
import sys
from html import escape
from datetime import datetime, timezone

import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from generate_nexus_dex_content import generate_nexus_dex_content

# -------------------------
# CONFIG
# -------------------------

KEYWORD_FILE           = os.path.join(BASE_DIR, "data", "nexus_dex_keywords.txt")
GENERATED_SLUGS_FILE   = os.path.join(BASE_DIR, "data", "nexus_dex_generated_slugs.txt")
GENERATED_KEYWORDS_FILE= os.path.join(BASE_DIR, "data", "nexus_dex_generated_keywords.txt")
TEMPLATE_FILE          = os.path.join(BASE_DIR, "nexus-dex-template", "nexus-dex-template.html")
OUTPUT_DIR             = os.path.join(BASE_DIR, "nexus-dex")
SITE                   = "https://verixiaapps.com"

# v1.1: engine API for full meta payload (pageSignals, supplementaryHeading/Intro, etc.)
SEO_API_BASE      = os.getenv("SEO_API_BASE", "https://awake-integrity-production-faa0.up.railway.app")
SEO_PAGE_ENDPOINT = f"{SEO_API_BASE}/seo-page"
SEO_PAGE_TIMEOUT  = int(os.getenv("SEO_PAGE_TIMEOUT_S", "90"))

RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT    = 10
DAILY_LIMIT         = int(os.getenv("DAILY_LIMIT", "100"))

PROTECTED_SLUGS = {
    "nexus-dex",
    "perps-trading",
    "bitcoin-perps",
    "ethereum-perps",
    "solana-perps",
    "altcoin-perps",
    "hyperliquid-frontend",
    "xstocks-trading",
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
}
FALLBACK_HUB_SLUG = "perps-trading"

# v1.1: required placeholders updated to include the 3 new v16.2 ones.
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
    "{{HL_DATA_BLOCK}}",
    "{{SCHEMA_FAQ}}",
    "{{AGGREGATE_RATING_JSON}}",
    "{{SUPP_HEADING}}",
    "{{SUPP_INTRO}}",
    "{{PAGE_META_SCRIPT}}",
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
}

BRAND_CASE = {
    "nexus dex":           "Nexus DEX",
    "binance smart chain": "Binance Smart Chain",
    "trust wallet":        "Trust Wallet",
    "raydium launchlab":   "Raydium LaunchLab",
    "pump fun":            "Pump Fun",
    "backed finance":      "Backed Finance",
    "hyperliquid":         "Hyperliquid",
    "metamask":            "MetaMask",
    "dexscreener":         "Dexscreener",
    "pancakeswap":         "PancakeSwap",
    "uniswap":             "Uniswap",
    "raydium":             "Raydium",
    "coinbase":            "Coinbase",
    "robinhood":           "Robinhood",
    "kalshi":              "Kalshi",
    "kraken":              "Kraken",
    "bybit":               "Bybit",
    "kamino":              "Kamino",
    "ethereum":            "Ethereum",
    "avalanche":           "Avalanche",
    "arbitrum":            "Arbitrum",
    "polygon":             "Polygon",
    "phantom":             "Phantom",
    "backpack":            "Backpack",
    "solflare":            "Solflare",
    "bitcoin":             "Bitcoin",
    "solana":              "Solana",
    "binance":             "Binance",
    "jupiter":             "Jupiter",
    "orca":                "Orca",
    "drift":               "Drift",
    "crypto":              "Crypto",
    "market":              "Market",
    "wallet":              "Wallet",
    "xstocks":             "xStocks",
    "xstock":              "xStock",
    "aaplx":               "AAPLx",
    "tslax":               "TSLAx",
    "nvdax":               "NVDAx",
    "msftx":               "MSFTx",
    "googlx":              "GOOGLx",
    "amznx":               "AMZNx",
    "metax":               "METAx",
    "mstrx":               "MSTRx",
    "nflxx":               "NFLXx",
    "spyx":                "SPYx",
    "qqqx":                "QQQx",
    "crclx":               "CRCLx",
    "aapl":                "AAPL",
    "tsla":                "TSLA",
    "nvda":                "NVDA",
    "msft":                "MSFT",
    "googl":               "GOOGL",
    "amzn":                "AMZN",
    "mstr":                "MSTR",
    "nflx":                "NFLX",
    "amd":                 "AMD",
    "coin":                "COIN",
    "hood":                "HOOD",
    "crcl":                "CRCL",
    "spy":                 "SPY",
    "qqq":                 "QQQ",
    "gld":                 "GLD",
    "fdv":                 "FDV",
    "bsc":                 "BSC",
    "eth":                 "ETH",
    "btc":                 "BTC",
    "sol":                 "SOL",
    "usdc":                "USDC",
    "usdt":                "USDT",
    "bnb":                 "BNB",
    "base":                "Base",
    "blast":               "Blast",
    "sui":                 "Sui",
    "ton":                 "TON",
    "trx":                 "TRX",
    "tron":                "Tron",
    "bonk":                "BONK",
    "wif":                 "WIF",
    "pepe":                "PEPE",
    "doge":                "DOGE",
    "shib":                "SHIB",
    "trump":               "TRUMP",
    "popcat":              "POPCAT",
    "jup":                 "JUP",
    "ray":                 "RAY",
    "pyth":                "PYTH",
    "jto":                 "JTO",
    "hype":                "HYPE",
    "spx":                 "SPX",
    "ai16z":               "ai16z",
    "fartcoin":            "FARTCOIN",
    "moodeng":             "MOODENG",
    "pnut":                "PNUT",
    "goat":                "GOAT",
    "griffain":            "GRIFFAIN",
    "chillguy":            "CHILLGUY",
    "zerebro":             "ZEREBRO",
    "dex":                 "DEX",
    "cex":                 "CEX",
    "kyc":                 "KYC",
    "spl":                 "SPL",
    "nft":                 "NFT",
    "dao":                 "DAO",
    "evm":                 "EVM",
    "etf":                 "ETF",
    "rwa":                 "RWA",
    "fomc":                "FOMC",
    "cpi":                 "CPI",
    "gdp":                 "GDP",
    "nfl":                 "NFL",
    "nba":                 "NBA",
    "ufc":                 "UFC",
    "us":                  "U.S.",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with",
}

HUB_TITLE_OVERRIDES = {
    "perps-trading":         "Perps Trading Hub",
    "bitcoin-perps":         "Bitcoin Perps Hub",
    "ethereum-perps":        "Ethereum Perps Hub",
    "solana-perps":          "SOL Perps Hub",
    "altcoin-perps":         "Altcoin Perps Hub",
    "hyperliquid-frontend":  "Hyperliquid Frontend Hub",
    "xstocks-trading":       "xStocks Trading Hub",
    "tokenized-stocks":      "Tokenized Stocks Hub",
    "buy-stocks-onchain":    "Buy Stocks On-Chain Hub",
    "stocks-no-kyc":         "Stocks No KYC Hub",
    "stocks-24-7":           "24/7 Stocks Hub",
    "global-stock-access":   "Global Stock Access Hub",
    "solana-swap":           "Solana Swap Hub",
    "buy-token":             "Buy Token Hub",
    "no-kyc-trading":        "No KYC Trading Hub",
    "whale-tracking":        "Whale Tracking Hub",
    "token-launch":          "Token Launch Hub",
    "wallet-trading":        "Wallet Trading Hub",
    "how-to-guides":         "Nexus DEX Guides Hub",
}

HUB_MATCH_RULES = [
    ("hyperliquid",         "hyperliquid-frontend"),
    ("xstocks",              "xstocks-trading"),
    ("xstock",               "xstocks-trading"),
    ("backed finance",       "xstocks-trading"),
    ("aaplx",                "xstocks-trading"),
    ("tslax",                "xstocks-trading"),
    ("nvdax",                "xstocks-trading"),
    ("spyx",                 "xstocks-trading"),
    ("qqqx",                 "xstocks-trading"),
    ("buy us stocks from",   "global-stock-access"),
    ("us stocks no us bank", "global-stock-access"),
    ("us stocks for non residents", "global-stock-access"),
    ("us stocks international", "global-stock-access"),
    ("global stock",         "global-stock-access"),
    ("international stock",  "global-stock-access"),
    ("24 7 stock",           "stocks-24-7"),
    ("stocks 24 hours",      "stocks-24-7"),
    ("stocks weekend",       "stocks-24-7"),
    ("trade stocks at night", "stocks-24-7"),
    ("trade stocks weekends", "stocks-24-7"),
    ("trade stocks holidays", "stocks-24-7"),
    ("stocks never close",   "stocks-24-7"),
    ("always open stock",    "stocks-24-7"),
    ("stocks after hours",   "stocks-24-7"),
    ("buy stocks no kyc",    "stocks-no-kyc"),
    ("trade stocks no kyc",  "stocks-no-kyc"),
    ("stock trading no verification", "stocks-no-kyc"),
    ("stock trading no signup", "stocks-no-kyc"),
    ("stocks no id",         "stocks-no-kyc"),
    ("stocks no account",    "stocks-no-kyc"),
    ("anonymous stock trading", "stocks-no-kyc"),
    ("stocks without broker", "stocks-no-kyc"),
    ("stocks without robinhood", "stocks-no-kyc"),
    ("stocks without etrade", "stocks-no-kyc"),
    ("buy apple stock",      "buy-stocks-onchain"),
    ("buy aapl",             "buy-stocks-onchain"),
    ("buy tesla stock",      "buy-stocks-onchain"),
    ("buy tsla",             "buy-stocks-onchain"),
    ("buy nvidia stock",     "buy-stocks-onchain"),
    ("buy nvda",             "buy-stocks-onchain"),
    ("buy microsoft stock",  "buy-stocks-onchain"),
    ("buy msft",             "buy-stocks-onchain"),
    ("buy google stock",     "buy-stocks-onchain"),
    ("buy googl",            "buy-stocks-onchain"),
    ("buy meta stock",       "buy-stocks-onchain"),
    ("buy amazon stock",     "buy-stocks-onchain"),
    ("buy amzn",             "buy-stocks-onchain"),
    ("buy mstr",             "buy-stocks-onchain"),
    ("buy microstrategy",    "buy-stocks-onchain"),
    ("buy spy",              "buy-stocks-onchain"),
    ("buy qqq",              "buy-stocks-onchain"),
    ("buy netflix stock",    "buy-stocks-onchain"),
    ("buy nflx",             "buy-stocks-onchain"),
    ("buy coinbase stock",   "buy-stocks-onchain"),
    ("buy robinhood stock",  "buy-stocks-onchain"),
    ("buy circle stock",     "buy-stocks-onchain"),
    ("buy crcl",             "buy-stocks-onchain"),
    ("tokenized stocks",     "tokenized-stocks"),
    ("tokenized equity",     "tokenized-stocks"),
    ("onchain stocks",       "tokenized-stocks"),
    ("onchain equities",     "tokenized-stocks"),
    ("stocks on solana",     "tokenized-stocks"),
    ("stocks on blockchain", "tokenized-stocks"),
    ("stocks as spl tokens", "tokenized-stocks"),
    ("buy stocks with crypto", "tokenized-stocks"),
    ("buy stocks with usdc", "tokenized-stocks"),
    ("buy stocks with sol",  "tokenized-stocks"),
    ("btc perps",           "bitcoin-perps"),
    ("bitcoin perps",       "bitcoin-perps"),
    ("bitcoin futures",     "bitcoin-perps"),
    ("bitcoin perpetual",   "bitcoin-perps"),
    ("eth perps",           "ethereum-perps"),
    ("ethereum perps",      "ethereum-perps"),
    ("ethereum futures",    "ethereum-perps"),
    ("ethereum perpetual",  "ethereum-perps"),
    ("sol perps",           "solana-perps"),
    ("solana perps",        "solana-perps"),
    ("sol perpetual",       "solana-perps"),
    ("memecoin perps",      "altcoin-perps"),
    ("altcoin perps",       "altcoin-perps"),
    ("wif perps",           "altcoin-perps"),
    ("bonk perps",          "altcoin-perps"),
    ("pepe perps",          "altcoin-perps"),
    ("doge perps",          "altcoin-perps"),
    ("hype perps",          "altcoin-perps"),
    ("whale tracker",       "whale-tracking"),
    ("smart money",         "whale-tracking"),
    ("insider",             "whale-tracking"),
    ("deployer",            "whale-tracking"),
    ("sniper",              "whale-tracking"),
    ("kol wallet",          "whale-tracking"),
    ("launch token",        "token-launch"),
    ("token launch",        "token-launch"),
    ("launchpad",           "token-launch"),
    ("bonding curve",       "token-launch"),
    ("deploy token",        "token-launch"),
    ("solana swap",         "solana-swap"),
    ("solana dex",          "solana-swap"),
    ("dex aggregator",      "solana-swap"),
    ("best price swap",     "solana-swap"),
    ("swap",                "solana-swap"),
    ("buy bonk",            "buy-token"),
    ("buy wif",             "buy-token"),
    ("buy pepe",            "buy-token"),
    ("buy trump",           "buy-token"),
    ("buy memecoin",        "buy-token"),
    ("buy spl",             "buy-token"),
    ("buy ",                "buy-token"),
    ("phantom wallet trading",  "wallet-trading"),
    ("backpack wallet trading", "wallet-trading"),
    ("self custodial",      "wallet-trading"),
    ("non custodial",       "wallet-trading"),
    ("wallet based",        "wallet-trading"),
    ("no kyc",              "no-kyc-trading"),
    ("without kyc",         "no-kyc-trading"),
    ("no signup",           "no-kyc-trading"),
    ("no verification",     "no-kyc-trading"),
    ("perps",               "perps-trading"),
    ("perpetual",           "perps-trading"),
    ("leverage",            "perps-trading"),
    ("how to",              "how-to-guides"),
]

# -------------------------
# UTILITIES (unchanged from v1.0)
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
    return {token for token in keyword_tokens(text) if token in NEXUS_DEX_CLUSTER_TERMS}


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


def clean_keyword_for_title(text):
    kw = normalize_keyword(text)
    kw = re.sub(r"^\s*is\s+this\s+",        "", kw)
    kw = re.sub(r"^\s*is\s+",               "", kw)
    kw = re.sub(r"^\s*can\s+i\s+",          "", kw)
    kw = re.sub(r"^\s*should\s+i\s+",       "", kw)
    kw = re.sub(r"^\s*what\s+is\s+a?\s*",   "", kw)
    kw = re.sub(r"^\s*how\s+to\s+",         "", kw)
    kw = re.sub(r"^\s*where\s+to\s+",       "", kw)
    kw = re.sub(r"^\s*best\s+place\s+to\s+","", kw)
    noise = [
        r"\bperps?\b", r"\bperpetual\b", r"\bleverage\b", r"\bleveraged\b",
        r"\bswap\b", r"\bbuy\b", r"\bsell\b", r"\btrade\b", r"\btrading\b",
        r"\bdex\b", r"\bwallet\b", r"\bmobile\b", r"\bapp\b",
        r"\bno\s+kyc\b", r"\bwithout\s+kyc\b", r"\bno\s+signup\b",
        r"\bno\s+verification\b", r"\bwallet\s+only\b",
        r"\bfrom\s+solana\b", r"\bon\s+solana\b", r"\bin\s+solana\b",
        r"\bfrom\s+wallet\b", r"\bfrom\s+phantom\b", r"\bfrom\s+backpack\b",
        r"\bself\s+custodial\b", r"\bnon\s+custodial\b",
        r"\bis\b", r"\bthis\b", r"\bwhat\b", r"\bhow\b",
        r"\bthe\b", r"\ba\b", r"\bcan\b", r"\bi\b",
    ]
    for pattern in noise:
        kw = re.sub(pattern, "", kw, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", kw).strip()


def extract_subject(keyword):
    kw = clean_keyword_for_title(keyword)
    extra_noise = [
        r"\bgood\b", r"\bbad\b", r"\bworth\b",
        r"\bprice(s)?\b", r"\btoday\b", r"\bnow\b", r"\btomorrow\b",
        r"\bfees?\b", r"\bsignal(s)?\b", r"\bexplain(ed)?\b",
        r"\bwork(s|ing)?\b", r"\bdoes\b", r"\bdo\b",
        r"\bmy\b", r"\byou(r)?\b",
        r"\bshould\b", r"\bwill\b", r"\bwould\b",
        r"\binvest(ing|ment|or)?\b", r"\btrader\b",
        r"\bmarket(s)?\b", r"\bguide\b", r"\btip(s)?\b",
        r"\bare\b", r"\bof\b", r"\bin\b", r"\bon\b",
        r"\bvs\b", r"\bversus\b",
        r"\bbuy(ing)?\b", r"\bsell(ing)?\b",
        r"\bsign(s)?\b", r"\brisks?\b",
        r"\bsurviv(e|al|ing)?\b", r"\breward(s)?\b",
        r"\b\d{4}\b",
    ]
    for pattern in extra_noise:
        kw = re.sub(pattern, "", kw, flags=re.IGNORECASE)
    words = [w for w in re.sub(r"\s+", " ", kw).strip().split(" ") if len(w) > 2]
    return " ".join(words[:3])


def soft_extract(keyword):
    stop = {
        "is","a","an","the","and","or","but","for","with","from","this","that","these","those",
        "was","are","be","been","to","of","in","on","at","by","as","if","it","its","do","did",
        "has","have","had","not","no","so","up","out","than","then","when","where","who",
        "why","how","what","will","would","could","should","can","may","might",
    }
    words = [w for w in normalize_keyword(keyword).split() if len(w) > 1 and w not in stop]
    return " ".join(words[:3])


def build_static_h1(keyword):
    try:
        raw = normalize_keyword(keyword)
        if not raw:
            return "Nexus DEX -- Self-Custodial Trading From Your Wallet"
        subject = extract_subject(keyword)
        s = title_case(subject) if subject and len(subject) > 2 else ""
        lower = raw.lower()

        if "hyperliquid" in lower:
            return f"Trade Hyperliquid From Solana -- {s or 'Wallet-Based, No MetaMask'}"
        if "xstocks" in lower or "xstock" in lower or "tokenized stock" in lower or "tokenized equity" in lower:
            return f"xStocks on Solana -- {s or 'AAPL, TSLA, NVDA From Your Wallet'}"
        if any(t in lower for t in ["aaplx","tslax","nvdax","spyx","qqqx","mstrx","metax","amznx","googlx","msftx","nflxx","crclx"]):
            return f"Tokenized Stocks -- {s or 'On-Chain Equity From Your Wallet'}"
        if ("stocks" in lower or "stock" in lower) and ("solana" in lower or "onchain" in lower or "spl" in lower):
            return f"Stocks on Solana -- {s or 'Tokenized Equities From Your Wallet'}"
        if ("stocks" in lower or "stock" in lower) and ("no kyc" in lower or "without kyc" in lower or "no signup" in lower or "no account" in lower):
            return f"Stocks No KYC -- {s or 'Buy U.S. Equities From Your Wallet'}"
        if ("stocks" in lower or "stock" in lower) and ("24" in lower or "weekend" in lower or "after hours" in lower or "holiday" in lower or "night" in lower):
            return f"Trade Stocks 24/7 -- {s or 'On-Chain, Never Close'}"
        if ("stocks" in lower or "stock" in lower) and ("from europe" in lower or "from asia" in lower or "from india" in lower or "international" in lower or "non resident" in lower):
            return f"Global U.S. Stocks Access -- {s or 'No Broker, No Bank, Wallet-Only'}"
        if "whale" in lower or "smart money" in lower or "insider" in lower or "deployer" in lower or "sniper" in lower:
            return f"Whale & Smart-Money Tracking -- {s or 'Real-Time On-Chain'}"
        if "launch" in lower or "launchpad" in lower or "bonding curve" in lower:
            return f"Token Launch -- {s or 'From Your Wallet, No KYC'}"
        if any(t in lower for t in ["perps", "perp", "perpetual", "leverage", "leveraged", "long", "short", "hedge"]):
            return f"Perps Trading -- {s or 'Wallet-Based, No KYC, Mobile-First'}"
        if "swap" in lower or "dex aggregator" in lower or "best price" in lower:
            return f"Solana DEX Swap -- {s or 'Best Price, No KYC, Mobile'}"
        if lower.startswith("buy ") or " buy " in lower:
            return f"Buy on Solana -- {s or 'From Your Wallet, No KYC'}"
        if "no kyc" in lower or "without kyc" in lower or "no signup" in lower:
            return f"No-KYC Trading -- {s or 'Wallet-Based, Mobile-First'}"
        if "wallet" in lower or "self custodial" in lower or "non custodial" in lower:
            return f"Wallet-Based Trading -- {s or 'Self-Custodial, On-Chain'}"
        if any(t in lower for t in ["how", "what", "why", "guide", "tutorial"]):
            return f"Nexus DEX Guide -- {s + ' Walkthrough' if s else 'Self-Custodial Trading'}"
        if any(t in lower for t in ["vs", "versus", "compare", "difference", "between"]):
            return f"{s + ' -- Nexus DEX Comparison' if s else 'Nexus DEX vs Centralized Exchanges'}"
        if any(t in lower for t in ["better", "best", "top", "choose", "pick", "cheapest"]):
            return f"Best {s}? Nexus DEX Wallet-Based Trading" if s else "Best DEX -- Nexus DEX Self-Custodial Trading"
        if s:
            return f"{s} on Nexus DEX -- Wallet-Based, No KYC"
        soft = soft_extract(keyword)
        if soft and len(soft) > 2:
            return f"{title_case(soft)} -- Nexus DEX Wallet-Based Trading"
        return "Nexus DEX -- Self-Custodial Trading From Your Wallet"
    except Exception:
        return "Nexus DEX -- Self-Custodial Trading From Your Wallet"


def build_static_intro(keyword):
    lower = normalize_keyword(keyword).lower()
    if "hyperliquid" in lower:
        return (
            "Trade Hyperliquid markets directly from a Solana wallet without bridging to Arbitrum or "
            "installing MetaMask. Mobile-first access using Phantom, Backpack, or Solflare."
        )
    if "xstocks" in lower or "xstock" in lower or "tokenized stock" in lower or "tokenized equity" in lower:
        return (
            "Trade tokenized U.S. stocks like AAPLx, TSLAx, NVDAx, and SPYx directly from a Solana "
            "wallet. Each xStock is backed 1:1 by the real share in regulated custody, trades 24/7, "
            "and is fully composable across Solana DeFi -- no brokerage account and no KYC at the protocol level."
        )
    if ("stocks" in lower or "stock" in lower) and ("no kyc" in lower or "without kyc" in lower or "no signup" in lower or "no account" in lower):
        return (
            "Buy U.S. stocks with no KYC, no broker signup, and no ID upload. Tokenized xStocks on "
            "Solana trade as SPL tokens directly from Phantom, Backpack, or Solflare. Your wallet is your account."
        )
    if ("stocks" in lower or "stock" in lower) and ("24" in lower or "weekend" in lower or "after hours" in lower or "holiday" in lower or "night" in lower):
        return (
            "Tokenized U.S. stocks on Solana trade 24/7 -- nights, weekends, and holidays. Buy or sell "
            "AAPLx, TSLAx, NVDAx, SPYx, and QQQx outside U.S. market hours directly from your wallet."
        )
    if ("stocks" in lower or "stock" in lower) and ("from europe" in lower or "from asia" in lower or "from india" in lower or "international" in lower or "non resident" in lower):
        return (
            "Non-U.S. users can buy AAPL, TSLA, NVDA, SPY exposure via xStocks on Solana from anywhere "
            "in the world. No U.S. bank account, no brokerage, no KYC at the protocol level -- just a Solana wallet funded with USDC."
        )
    if "stocks" in lower or "stock" in lower:
        return (
            "Trade tokenized stocks on Solana from your wallet. Apple, Tesla, Nvidia, S&P 500, and "
            "more as SPL tokens with 24/7 trading, fractional positions, and full DeFi composability."
        )
    if "whale" in lower or "smart money" in lower or "insider" in lower:
        return (
            "Track Solana whales, smart money, memecoin insiders, deployer clusters, and KOL wallets "
            "in real time. See who is accumulating before the chart moves."
        )
    if "launch" in lower or "launchpad" in lower or "bonding curve" in lower:
        return (
            "Launch a Solana token from your wallet without code, KYC, or upfront fees. Deploy via "
            "bonding curve and graduate to Raydium liquidity automatically."
        )
    if any(t in lower for t in ["perps", "perp", "perpetual", "leverage", "leveraged"]):
        return (
            "Long or short crypto with leverage directly from your Solana wallet. No KYC, no signup, "
            "no centralized account. Connect Phantom, Backpack, or Solflare and trade in seconds."
        )
    if "swap" in lower or "dex aggregator" in lower:
        return (
            "Swap any Solana token with best-price routing across Jupiter, Raydium, and Orca. "
            "Connect your wallet, paste a token address, and trade with low slippage."
        )
    if lower.startswith("buy ") or " buy " in lower:
        return (
            "Buy any Solana token directly from your wallet -- memecoins, AI tokens, new launches. "
            "Best-price aggregation with no signup and no centralized exchange listing required."
        )
    return (
        "Self-custodial trading from your Solana wallet -- perps, swaps, and tokenized stocks in "
        "one interface. No KYC, no signup, no centralized custody. Every trade settles on-chain."
    )


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
            "[warning] nexus_dex_generated_slugs.txt and nexus_dex_generated_keywords.txt are not "
            "line-aligned. Rebuilding tracking from existing pages on disk."
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


def write_lines(filepath, values, preserve_input=True):
    ensure_file(filepath)
    if preserve_input:
        lines = [str(v).strip()  for v in values if str(v).strip()]
    else:
        lines = [str(v).rstrip() for v in values if str(v).strip()]
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
    return "\n".join(f"<p>{escape_html(paragraph)}</p>" for paragraph in paragraphs)


def discover_existing_output_pages(existing_keyword_map=None):
    existing_keyword_map = existing_keyword_map or {}
    discovered = []
    if not os.path.isdir(OUTPUT_DIR):
        return discovered
    for slug in sorted(os.listdir(OUTPUT_DIR)):
        slug = slugify(slug)
        if not slug or slug in PROTECTED_SLUGS:
            continue
        index_path = page_path(slug)
        if not os.path.isfile(index_path):
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
# v1.1: ENGINE PAYLOAD FETCH
# -------------------------

def fetch_engine_payload(keyword):
    """v1.1: hit /seo-page for the full engine meta (pageSignals, supplementary*).
    Returns the parsed payload dict or None on failure. The caller falls back to
    local-only rendering when this returns None.
    """
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
    if not payload.get("meta"):
        print(f"[engine] missing meta for {keyword!r}")
        return None
    return payload


def build_aggregate_rating_json(page_signals):
    """v1.1: produce the inline AggregateRating object that the FinancialService
    and SoftwareApplication schemas inline via {{AGGREGATE_RATING_JSON}}.

    The engine's pageSignals.aggregateRatingJson already includes @type, so we
    can use it directly. Falls back to a deterministic 4.8/2500 default if the
    engine didn't supply signals (older engine versions or fetch failure).
    """
    if page_signals and page_signals.get("aggregateRatingJson"):
        return page_signals["aggregateRatingJson"]
    rating_value = (page_signals or {}).get("ratingValue", 4.8)
    review_count = (page_signals or {}).get("reviewCount", 2500)
    return json.dumps({
        "@type": "AggregateRating",
        "ratingValue": f"{float(rating_value):.1f}",
        "reviewCount": str(int(review_count)),
        "bestRating": "5",
    }, ensure_ascii=False)


def build_page_meta_script(meta, hl_data_block=""):
    """v1.1: emit window.__pageMeta with the full engine payload (pageSignals,
    supplementaryHeading/Intro, recognition chips, story titles, FAQ, etc).
    Used by the template's hydration JS.
    """
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
        "shape":                meta.get("shape", ""),
        "subject":              meta.get("subject", ""),
        "faq":                  meta.get("faq", []),
        "threatBanner":         meta.get("threatBanner"),
        "recognitionChips":     meta.get("recognitionChips", []),
        "storyCardTitles":      meta.get("storyCardTitles", []),
        "supplementaryCards":   meta.get("supplementaryCards", []),
        "supplementaryHeading": meta.get("supplementaryHeading", ""),
        "supplementaryIntro":   meta.get("supplementaryIntro", ""),
        "pageSignals":          meta.get("pageSignals", {}),
        "author":               meta.get("author", {}),
        "hlDataBlock":          hl_data_block or "",
    }
    blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    return f'<script id="page-meta">window.__pageMeta = {blob};</script>'


# -------------------------
# SEO TEXT HELPERS
# -------------------------

def build_og_image(slug):
    return "https://verixiaapps.com/og/nexus-dex.png"


def build_schema_faq(keyword):
    lower = normalize_keyword(keyword).lower()

    base_items = [
        (
            "Do I need to sign up or complete KYC?",
            "No. Nexus DEX is fully self-custodial. Connect a Solana wallet (Phantom, Backpack, or "
            "Solflare), sign a transaction, and trade. There is no signup, no identity verification, "
            "no document upload, and no centralized account.",
        ),
        (
            "Which wallets are supported?",
            "Phantom, Backpack, Solflare, and other major Solana wallets work with Nexus DEX. You sign "
            "each trade from your wallet and funds stay in your wallet between trades. The platform "
            "never holds your funds.",
        ),
        (
            "How does pricing work compared to centralized exchanges?",
            "Spot swaps and tokenized stock trades route through Jupiter, Raydium, and Orca for best "
            "price. Perps settle on-chain at posted market prices. There are no platform deposit fees, "
            "no withdrawal fees, and no minimum balances.",
        ),
    ]

    if "hyperliquid" in lower:
        intent_item = (
            "Can I trade Hyperliquid from a Solana wallet?",
            "Yes. Nexus DEX provides a wallet-based interface to Hyperliquid markets that connects "
            "from a Solana wallet like Phantom or Backpack. There is no need to bridge to Arbitrum or "
            "install MetaMask. Your trades route to Hyperliquid liquidity from your existing wallet.",
        )
    elif "xstocks" in lower or "xstock" in lower or "tokenized stock" in lower or "tokenized equity" in lower or any(t in lower for t in ["aaplx","tslax","nvdax","spyx","qqqx"]):
        intent_item = (
            "What are xStocks and how do they work?",
            "xStocks are tokenized 1:1 representations of real U.S. stocks and ETFs (AAPLx for Apple, "
            "TSLAx for Tesla, NVDAx for Nvidia, SPYx for the S&P 500, etc.) issued by Backed Finance "
            "and now part of Kraken. Each token is backed by the underlying share held in regulated "
            "Swiss custody, trades 24/7 as an SPL token on Solana, and is fully composable across DeFi.",
        )
    elif ("stocks" in lower or "stock" in lower) and ("no kyc" in lower or "without kyc" in lower or "no signup" in lower or "no account" in lower):
        intent_item = (
            "Can I really buy U.S. stocks without KYC?",
            "Yes. xStocks on Solana are SPL tokens, so there is no brokerage account, no SSN, and no "
            "ID upload at the protocol level. Connect Phantom, Backpack, or Solflare, fund with USDC, "
            "and buy AAPLx, TSLAx, NVDAx, SPYx, or QQQx. Availability and tax rules still depend on your jurisdiction.",
        )
    elif ("stocks" in lower or "stock" in lower) and ("24" in lower or "weekend" in lower or "after hours" in lower or "holiday" in lower or "night" in lower):
        intent_item = (
            "Can I really trade stocks 24/7?",
            "Yes. xStocks trade around the clock on Solana DEXes. You can buy or sell AAPLx, TSLAx, "
            "NVDAx, SPYx, and QQQx on weekends, after U.S. market hours, and on holidays. Liquidity "
            "may be thinner outside market hours, but the markets never fully close.",
        )
    elif ("stocks" in lower or "stock" in lower) and ("from europe" in lower or "from asia" in lower or "from india" in lower or "international" in lower or "non resident" in lower):
        intent_item = (
            "Can non-U.S. users buy U.S. stocks here?",
            "Yes. xStocks are designed so users outside the U.S. can get exposure to AAPL, TSLA, NVDA, "
            "SPY, and other equities without a U.S. brokerage or U.S. bank account. Just a Solana "
            "wallet funded with USDC. Local tax and regulatory rules still apply.",
        )
    elif ("stocks" in lower or "stock" in lower):
        intent_item = (
            "How do tokenized stocks work?",
            "Tokenized stocks like xStocks live on Solana as SPL tokens, each backed 1:1 by the real "
            "underlying share in regulated custody. They trade 24/7, support fractional positions, "
            "and can be LP'd on Raydium or used as collateral on Kamino just like any other SPL token.",
        )
    elif "whale" in lower or "smart money" in lower or "insider" in lower or "deployer" in lower:
        intent_item = (
            "What counts as smart money or a whale?",
            "Wallets with consistent profitable trades, early entries on tokens that pumped, deployer "
            "clusters with track records, and KOL wallets. Nexus DEX surfaces these wallets and their "
            "current positions so you can follow accumulation patterns in real time.",
        )
    elif "launch" in lower or "launchpad" in lower or "bonding curve" in lower:
        intent_item = (
            "How does the Solana token launch work?",
            "The launchpad is no-code. You name the token, set basic parameters, and deploy from your "
            "wallet. A bonding curve handles early trading. Once the token hits the graduation "
            "threshold, liquidity migrates automatically to a Raydium pool.",
        )
    elif any(t in lower for t in ["perps", "perp", "perpetual", "leverage"]):
        intent_item = (
            "How does perps trading work without KYC?",
            "Perps positions on Nexus DEX are collateralized by USDC in your Solana wallet. You sign "
            "the position from your wallet, the position opens against an on-chain perpetual futures "
            "market, and PnL settles back to your wallet. No off-chain account is needed.",
        )
    elif "swap" in lower or "buy" in lower:
        intent_item = (
            "How does best-price routing work?",
            "Nexus DEX queries Jupiter, Raydium, and Orca for the best price on your trade. The "
            "selected route is executed in a single transaction signed from your wallet. You get the "
            "best available price across all three aggregators without checking each one manually.",
        )
    else:
        intent_item = (
            "Why use Nexus DEX over a centralized exchange?",
            "Self-custody, no KYC, no signup, and on-chain settlement for every trade. Funds stay in "
            "your wallet between positions, the platform cannot freeze or restrict your account, and "
            "every position is verifiable on-chain.",
        )

    all_items = [intent_item] + base_items
    schema = {
        "@context": "https://schema.org",
        "@type":    "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name":  q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in all_items
        ],
    }
    return json.dumps(schema, ensure_ascii=False)


def build_title(keyword):
    raw      = normalize_keyword(keyword)
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
    raw      = normalize_keyword(keyword)
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
    raw      = normalize_keyword(keyword)
    readable = readable_keyword(keyword)
    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        anchor = title_case(raw)
        if is_question_style_keyword(raw) and not anchor.endswith("?"):
            anchor += "?"
        return anchor
    return f"{readable} on Nexus DEX"


def build_canonical(slug):
    return f"{SITE}/nexus-dex/{slug}/"


# -------------------------
# v1.1: SUPP HEADING + INTRO FALLBACKS
# -------------------------
# Used when engine fetch fails. The engine's per-intent versions are richer
# but these keep the build green if Railway is unreachable.

def build_supp_heading_local(keyword):
    lower = normalize_keyword(keyword).lower()
    if any(t in lower for t in ["xstocks", "xstock", "tokenized stock", "stocks on solana"]):
        return "Why xStocks on Solana are different"
    if any(t in lower for t in ["perps", "perp", "perpetual", "leverage", "long", "short"]):
        return "Why DeFi perps run differently from a CEX"
    if any(t in lower for t in ["swap", "dex", "aggregator", "routing"]):
        return "Why Solana DeFi swaps run differently"
    if any(t in lower for t in ["whale", "smart money", "insider", "deployer"]):
        return "Why on-chain whale tracking beats price-only signals"
    return "Why Solana DeFi is different"


def build_supp_intro_local(keyword):
    lower = normalize_keyword(keyword).lower()
    if any(t in lower for t in ["xstocks", "xstock", "tokenized stock", "stocks on solana"]):
        return (
            "xStocks behave like any other SPL token once they land in the wallet. Three things "
            "change versus a traditional brokerage: settlement, hours, and composability. Each is "
            "mechanical, observable, and reflected in how the position behaves on-chain."
        )
    if any(t in lower for t in ["perps", "perp", "perpetual", "leverage"]):
        return (
            "The product runs as a responsive web DEX, not a native app. Connect a Solana wallet "
            "directly from your browser; positions, margin, and PnL all settle on-chain against the "
            "underlying protocol. The structural differences from a CEX: no platform custody, no "
            "account, no email."
        )
    if any(t in lower for t in ["swap", "dex", "aggregator", "routing"]):
        return (
            "A direct swap on one DEX applies full price impact to the trade size. An aggregator "
            "splits the order across the pools with the deepest active liquidity right now. The "
            "three structural differences that matter on Solana: fees, block time, and how the same "
            "wallet that holds your tokens also signs the trade."
        )
    return (
        "DeFi on Solana removes the account, the email, and the KYC step. What replaces them: a "
        "wallet you control, smart contracts that execute trades directly, and on-chain settlement "
        "in sub-second blocks. The three structural differences that matter day-to-day: fees, "
        "custody, and execution speed."
    )


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


# -------------------------
# AI GENERATION
# -------------------------

def generate_ai_text(keyword, keyword_display):
    raw_keyword   = normalize_keyword(keyword)
    clean_keyword = normalize_keyword(keyword_display)
    readable      = readable_keyword(keyword_display)

    attempts = [
        raw_keyword,
        clean_keyword,
        readable,
        f"{clean_keyword} nexus dex" if clean_keyword else "",
        f"{clean_keyword} no kyc" if clean_keyword and not contains_term_phrase(raw_keyword, "kyc") else "",
        f"{clean_keyword} from wallet" if clean_keyword and not contains_term_phrase(raw_keyword, "wallet") else "",
    ]

    seen       = set()
    last_error = None

    for prompt in attempts:
        prompt_norm = normalize_keyword(prompt)
        if not prompt_norm or prompt_norm in seen:
            continue
        seen.add(prompt_norm)
        try:
            ai_text = sanitize_ai_html(generate_nexus_dex_content(prompt))
            if ai_text:
                return ai_text
        except Exception as e:
            last_error = e
            print(f"[error] AI generation failed for '{prompt}': {e}")

    if last_error:
        raise ValueError(f"AI generation failed for all prompts: {last_error}")
    raise ValueError("AI generation failed for all prompts")


# -------------------------
# SETUP & GENERATION LOOP
# -------------------------

validate_daily_limit(DAILY_LIMIT)

os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(GENERATED_SLUGS_FILE)
ensure_file(GENERATED_KEYWORDS_FILE)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

validate_template_placeholders(template)

keywords = load_keywords()
if not keywords:
    print("No keywords in queue. Nothing to generate.")
    sys.exit(0)

generated_records    = load_generated_records()
existing_keyword_map = {record["slug"]: record["keyword"] for record in generated_records}

filesystem_pages  = discover_existing_output_pages(existing_keyword_map=existing_keyword_map)
generated_records = build_aligned_generated_records(filesystem_pages)

generated_slugs    = {record["slug"]    for record in generated_records}
generated_keywords = {record["keyword"] for record in generated_records}

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

generated_count      = 0
skipped_existing_count = 0
failed_count         = 0
processed_keywords   = set()
new_pages_this_run   = []

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

    # v1.1: pull full meta from engine
    engine_payload = fetch_engine_payload(keyword)
    meta           = (engine_payload or {}).get("meta") or {}
    hl_block       = (engine_payload or {}).get("hlDataBlock") or ""
    ai_text_engine = (engine_payload or {}).get("content") or ""

    # v1.2: prefer engine values for title/h1/desc/intro/breadcrumb when available.
    # The engine knows the keyword's intent + sub-intent and produces tighter,
    # more on-topic copy than the local Python static functions.
    engine_title       = meta.get("title", "").strip()
    engine_description = meta.get("description", "").strip()
    engine_h1          = meta.get("h1", "").strip()
    engine_intro       = meta.get("intro", "").strip()
    engine_breadcrumb  = meta.get("breadcrumb", "").strip()
    engine_faq_schema  = meta.get("faqSchema", "").strip()

    title       = engine_title       or build_title(keyword)
    description = engine_description or build_description(keyword)
    h1_text     = engine_h1          or build_static_h1(keyword)
    intro_text  = engine_intro       or build_static_intro(keyword)
    breadcrumb  = engine_breadcrumb  or (title_case(keyword_display) or readable_keyword(keyword))
    faq_schema  = engine_faq_schema  or build_schema_faq(keyword)

    # v1.2: cap title at 60 chars. Engine usually under, but if Python fallback
    # produced a longer one, trim the suffix variants ("Mobile-First" first).
    if len(title) > 60:
        trimmed = re.sub(r",?\s*Mobile-First\s*$", "", title)
        if len(trimmed) <= 60:
            title = trimmed
        else:
            trimmed = re.sub(r",?\s*No KYC,?\s*Mobile-First\s*$", "", title)
            if len(trimmed) <= 60:
                title = trimmed
            else:
                # Last resort: hard cut at 60 on a word boundary
                cut = title[:60].rsplit(" ", 1)[0]
                title = cut if cut else title[:60]

    canonical = build_canonical(slug)

    # If engine returned content, use it; else fall back to legacy AI fetch
    if ai_text_engine:
        ai_text = sanitize_ai_html(ai_text_engine)
    else:
        try:
            ai_text = generate_ai_text(keyword, keyword_display)
        except Exception as e:
            failed_count += 1
            print(f"[failed] {keyword} -> {e}")
            continue

    # v1.1: derive the new placeholders. Engine values when available,
    # local fallbacks otherwise -- so the build never fails on a network blip.
    page_signals      = meta.get("pageSignals") or {}
    aggregate_json    = build_aggregate_rating_json(page_signals)
    supp_heading      = meta.get("supplementaryHeading") or build_supp_heading_local(keyword)
    supp_intro        = meta.get("supplementaryIntro")   or build_supp_intro_local(keyword)
    page_meta_script  = build_page_meta_script(meta, hl_block)

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
            "{{HL_DATA_BLOCK}}":          hl_block,
            "{{PAGE_META_SCRIPT}}":       page_meta_script,
            "{{SCHEMA_FAQ}}":             faq_schema,
            # v1.1: new placeholders
            "{{AGGREGATE_RATING_JSON}}":  aggregate_json,
            "{{SUPP_HEADING}}":           escape_html(supp_heading),
            "{{SUPP_INTRO}}":             escape_html(supp_intro),
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
        f"-> meta: {'engine' if meta else 'local-fallback'}"
    )

remaining_keywords = []
for keyword in keywords:
    keyword_norm = normalize_keyword(keyword)
    if keyword_norm not in processed_keywords:
        remaining_keywords.append(keyword_norm)

aligned_records = build_aligned_generated_records(existing_pages, extra_pages=new_pages_this_run)
write_lines(GENERATED_SLUGS_FILE,    [record["slug"]    for record in aligned_records])
write_lines(GENERATED_KEYWORDS_FILE, [record["keyword"] for record in aligned_records])
write_lines(KEYWORD_FILE, remaining_keywords)

print(
    f"Done. Generated {generated_count} new pages. "
    f"Skipped {skipped_existing_count} existing pages. "
    f"Failed {failed_count} keywords."
)
print(f"Remaining keywords in queue: {len(remaining_keywords)}")
