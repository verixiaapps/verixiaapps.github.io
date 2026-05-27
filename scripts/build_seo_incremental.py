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
REJECTED_FILE           = os.path.join(BASE_DIR, "data", "nexus_dex_rejected_keywords.txt")

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
    "wonderland-memes",
    "live-signals",
    "brand-tokens",
    "solana-bridges",
    "solana-swaps",
    "no-kyc-trading",
    "wallet-trading",
    "whale-tracking",
    "token-launch",
    "how-to-guides",
    "tokenized-stocks",
    "buy-stocks-onchain",
    "stocks-no-kyc",
    "stocks-24-7",
    "global-stock-access",
    "global-markets",
}
FALLBACK_HUB_SLUG = "crypto-markets"

CLUSTER_TERMS = {
    "swap", "swaps", "buy", "sell", "trade", "trading", "dex", "defi",
    "wallet", "mobile", "app", "self", "custodial", "non",
    "phantom", "backpack", "solflare", "jupiter", "raydium", "orca", "meteora",
    "phoenix", "lifinity",
    "solana", "ethereum", "base", "arbitrum", "optimism", "polygon", "avalanche",
    "bnb", "binance", "bsc", "sui", "aptos", "btc", "eth", "sol", "usdc", "usdt",
    "bridge", "bridges", "wormhole", "debridge", "allbridge",
    "brand", "brands", "tokenized", "stock", "stocks", "equity", "onchain",
    "fractional", "settled", "price", "tracked",
    "aapl", "tsla", "nvda", "msft", "googl", "amzn", "meta", "mstr", "nflx",
    "spy", "qqq", "crcl", "hood", "coin", "orcl", "crm",
    "aaplx", "tslax", "nvdax", "msftx", "googlx", "amznx", "metax", "mstrx",
    "nflxx", "spyx", "qqqx", "crclx", "hoodx", "coinx", "orclx", "crmx",
    "apple", "tesla", "nvidia", "microsoft", "google", "alphabet", "amazon",
    "netflix", "microstrategy", "circle", "robinhood", "oracle", "salesforce",
    "meme", "memes", "memecoin", "wonderland", "ape", "moon", "degen",
    "hoppy", "fartcoin", "pepe", "wif", "bonk", "popcat", "mew", "wen",
    "bome", "myro", "ponke", "michi", "trump", "moodeng", "goat", "pnut",
    "fresh", "launch", "launchpad",
    "trending", "signals", "discovery", "gainers", "volume", "leaders", "hot",
    "pumping", "live",
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
    "aaplx":  "AAPLx",  "tslax":  "TSLAx",  "nvdax":  "NVDAx",
    "msftx":  "MSFTx",  "googlx": "GOOGLx", "amznx":  "AMZNx",
    "metax":  "METAx",  "mstrx":  "MSTRx",  "nflxx":  "NFLXx",
    "spyx":   "SPYx",   "qqqx":   "QQQx",   "crclx":  "CRCLx",
    "hoodx":  "HOODx",  "coinx":  "COINx",  "orclx":  "ORCLx",
    "crmx":   "CRMx",
    "aapl":  "AAPL",  "tsla":  "TSLA",  "nvda":  "NVDA",  "msft":  "MSFT",
    "googl": "GOOGL", "amzn":  "AMZN",  "meta":  "META",  "mstr":  "MSTR",
    "nflx":  "NFLX",  "spy":   "SPY",   "qqq":   "QQQ",   "crcl":  "CRCL",
    "hood":  "HOOD",  "coin":  "COIN",  "orcl":  "ORCL",  "crm":   "CRM",
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
    "btc":   "BTC",  "eth":   "ETH",  "sol":   "SOL",
    "usdc":  "USDC", "usdt":  "USDT", "bnb":   "BNB",
    "hoppy":    "HOPPY",    "fartcoin": "FARTCOIN", "pepe":   "PEPE",
    "wif":      "WIF",      "bonk":     "BONK",     "popcat": "POPCAT",
    "mew":      "MEW",      "wen":      "WEN",      "bome":   "BOME",
    "myro":     "MYRO",     "ponke":    "PONKE",    "michi":  "MICHI",
    "trump":    "TRUMP",    "moodeng":  "MOODENG",  "goat":   "GOAT",
    "pnut":     "PNUT",     "doge":     "DOGE",     "shib":   "SHIB",
    "floki":    "FLOKI",    "fwog":     "FWOG",     "pengu":  "PENGU",
    "neiro":    "NEIRO",    "useless":  "USELESS",
    "jup":      "JUP",
    "ray":      "RAY",
    "pyth":     "PYTH",
    "jto":      "JTO",
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
    "crypto-markets":   "Crypto Markets Hub",
    "bitcoin-markets":  "Bitcoin Markets Hub",
    "ethereum-markets": "Ethereum Markets Hub",
    "solana-markets":   "Solana Markets Hub",
    "altcoin-markets":  "Altcoin Markets Hub",
    "wonderland-memes": "Wonderland Memes Hub",
    "live-signals":     "Live Signals Hub",
    "brand-tokens":     "Brand Tokens Hub",
    "solana-bridges":   "Solana Bridges Hub",
    "solana-swaps":     "Solana Swaps Hub",
    "no-kyc-trading":   "No KYC Trading Hub",
    "wallet-trading":   "Wallet Trading Hub",
    "whale-tracking":   "Whale Tracking Hub",
    "token-launch":     "Token Launch Hub",
    "how-to-guides":    "Verixia Guides Hub",
    "tokenized-stocks":    "Tokenized Stocks Hub",
    "buy-stocks-onchain":  "Buy Stocks On-Chain Hub",
    "stocks-no-kyc":       "Stocks No KYC Hub",
    "stocks-24-7":         "24/7 Stocks Hub",
    "global-stock-access": "Global Stock Access Hub",
    "global-markets":      "Global Markets Hub",
}

HUB_MATCH_RULES = [
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
    ("buy stocks no kyc",   "brand-tokens"),
    ("anonymous stock",     "brand-tokens"),
    ("stocks without broker", "brand-tokens"),
    ("buy us stocks from",  "brand-tokens"),
    ("global stock",        "brand-tokens"),

    ("bridge ethereum",     "solana-bridges"),
    ("bridge eth",          "solana-bridges"),
    ("bridge base",         "solana-bridges"),
    ("bridge arbitrum",     "solana-bridges"),
    ("bridge optimism",     "solana-bridges"),
    ("bridge polygon",      "solana-bridges"),
    ("bridge avalanche",    "solana-bridges"),
    ("bridge bnb",          "solana-bridges"),
    ("bridge bsc",          "solana-bridges"),
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
    ("wormhole",            "solana-bridges"),
    ("debridge",            "solana-bridges"),
    ("allbridge",           "solana-bridges"),

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

    ("whale tracker",   "whale-tracking"),
    ("whale tracking",  "whale-tracking"),
    ("smart money",     "whale-tracking"),
    ("insider wallet",  "whale-tracking"),
    ("deployer wallet", "whale-tracking"),
    ("sniper wallet",   "whale-tracking"),
    ("kol wallet",      "whale-tracking"),

    ("launch token",    "token-launch"),
    ("token launch",    "token-launch"),
    ("launchpad",       "token-launch"),
    ("bonding curve",   "token-launch"),
    ("deploy token",    "token-launch"),
    ("fresh pool",      "token-launch"),

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

    ("swap",                "solana-swaps"),
    ("how to",              "how-to-guides"),
]


# -----------------------------
# UTILITIES (mirrors working scam-check builder)
# -----------------------------
def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def slugify(text):
    text = normalize_keyword(text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


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
    return {token for token in keyword_tokens(text) if token in CLUSTER_TERMS}


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


def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys(normalize_keyword(line) for line in f if line.strip()))


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


def contains_term_phrase(haystack, needle):
    haystack_norm = normalize_keyword(haystack)
    needle_norm   = normalize_keyword(needle)
    if not haystack_norm or not needle_norm:
        return False
    pattern = r"(^|[^a-z0-9])" + re.escape(needle_norm) + r"([^a-z0-9]|$)"
    return re.search(pattern, haystack_norm, flags=re.IGNORECASE) is not None


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
# GIT CHECKPOINT (mirrors scam-check pattern)
# -----------------------------
def git_checkpoint(generated_count, new_generated_keywords, new_generated_slugs, remaining_keywords):
    """Write tracking files and commit+push progress to origin."""
    sorted_keywords = sorted(new_generated_keywords, key=slugify)
    write_lines(GENERATED_KEYWORDS_FILE, sorted_keywords)
    write_lines(GENERATED_SLUGS_FILE, [slugify(k) for k in sorted_keywords])
    write_lines(KEYWORD_FILE, remaining_keywords)

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
# AI GENERATION (mirrors scam-check retry pattern)
# -----------------------------
def generate_ai_text(keyword, keyword_display):
    raw_keyword   = normalize_keyword(keyword)
    clean_keyword = normalize_keyword(keyword_display)
    readable      = readable_keyword(keyword_display)

    attempts = [
        raw_keyword,
        clean_keyword,
        readable,
        f"{clean_keyword} nexus dex" if clean_keyword else "",
        f"{clean_keyword} no kyc" if clean_keyword and "kyc" not in raw_keyword else "",
        f"{clean_keyword} from wallet" if clean_keyword and "wallet" not in raw_keyword else "",
    ]

    seen = set()
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


# -----------------------------
# SEO TEXT HELPERS
# -----------------------------
def build_title(keyword):
    raw      = normalize_keyword(keyword)
    readable = readable_keyword(keyword)

    if not raw:
        return "Verixia | Solana DeFi - Swaps, Bridges, Brands, Memes"
    if is_guidance_style_keyword(raw):
        return f"{title_case(raw)} | Verixia - Solana DeFi"
    if is_question_style_keyword(raw):
        return f"{title_case(raw)}? Verixia - No KYC, Wallet-Native"
    return f"{readable} | Verixia - No KYC, Non-Custodial on Solana"


def build_description(keyword):
    readable = readable_keyword(keyword)
    clean_kw = display_keyword(keyword)
    return (
        f"{readable} on Verixia. Non-custodial swap on Solana with Jupiter routing. "
        f"No KYC, no accounts, no limits. Trade {clean_kw} from your wallet."
    )


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


# -----------------------------
# LINKING HELPERS
# -----------------------------
def dedupe_pages_by_slug(pages_list):
    deduped = []
    seen    = set()
    for page in pages_list:
        slug = page["slug"]
        if not slug or slug in seen or slug in PROTECTED_SLUGS:
            continue
        seen.add(slug)
        deduped.append(page)
    return deduped


def get_related_pages(current_page, all_pages, limit, exclude_slugs=None):
    exclude_slugs   = set(exclude_slugs or set())
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
        f'<li><a href="/nexus-dex/{p["slug"]}/">{escape_html(build_related_anchor(p["keyword"]))}</a></li>\n'
        for p in pages_list
        if page_exists(p["slug"])
    )


# -----------------------------
# SETUP & GENERATION LOOP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(GENERATED_SLUGS_FILE)
ensure_file(GENERATED_KEYWORDS_FILE)
ensure_file(REJECTED_FILE)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

keywords = load_keywords()
if not keywords:
    print("No keywords in queue. Nothing to generate.")
    sys.exit(0)

generated_slugs    = load_generated_slugs()
generated_keywords = load_generated_keywords()

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

existing_pages       = []
existing_seen_slugs  = set()

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
queue_pages    = dedupe_pages_by_slug(queue_pages)

print(f"Loaded {len(keywords)} keywords from queue.")
print(f"Unique queued pages after slug dedupe: {len(queue_pages)}")
print(f"Duplicate queued keywords skipped: {duplicate_queue_count}")
print(f"Known generated slugs: {len(generated_slugs)}")
print(f"Known generated keywords: {len(generated_keywords)}")
print(f"Existing pages available for internal links: {len(existing_pages)}")
print(f"Daily limit: {DAILY_LIMIT}")
print(f"Commit every: {COMMIT_EVERY}")
print(f"Resume mode: {RESUME}")
print(f"Fallback hub slug: {FALLBACK_HUB_SLUG}")

generated_count          = 0
skipped_existing_count   = 0
failed_count             = 0
processed_keywords       = set()
new_generated_slugs      = set(generated_slugs)
new_generated_keywords   = set(generated_keywords)

remaining_keywords = [normalize_keyword(kw) for kw in keywords]

for page in queue_pages:
    if generated_count >= DAILY_LIMIT:
        break

    slug            = page["slug"]
    keyword         = page["keyword"]
    keyword_display = display_keyword(keyword)
    path            = page_path(slug)

    if slug in PROTECTED_SLUGS:
        processed_keywords.add(keyword)
        remaining_keywords = [kw for kw in remaining_keywords if kw != keyword]
        print("Skipping protected page:", slug)
        continue

    if page_exists(slug) and RESUME:
        skipped_existing_count += 1
        new_generated_slugs.add(slug)
        new_generated_keywords.add(keyword)
        processed_keywords.add(keyword)
        remaining_keywords = [kw for kw in remaining_keywords if kw != keyword]
        continue

    os.makedirs(os.path.dirname(path), exist_ok=True)
    title       = build_title(keyword)
    description = build_description(keyword)
    canonical   = build_canonical(slug)

    try:
        ai_text = generate_ai_text(keyword, keyword_display)
    except Exception as e:
        failed_count += 1
        print(f"[failed] {keyword} -> {e}")
        append_line(REJECTED_FILE, f"{keyword}\t{e}")
        continue

    related_pages = get_related_pages(page, existing_pages, RELATED_LINKS_COUNT)
    related_slugs = {p["slug"] for p in related_pages}
    more_pages    = get_related_pages(
        page,
        existing_pages,
        MORE_LINKS_COUNT,
        exclude_slugs=related_slugs,
    )

    hub_link_html = build_hub_link_html(keyword)
    html = template
    html = html.replace("{{TITLE}}",         escape_html(title))
    html = html.replace("{{DESCRIPTION}}",   escape_html(description))
    html = html.replace("{{KEYWORD}}",       escape_html(keyword_display))
    html = html.replace("{{AI_CONTENT}}",    ai_text)
    html = html.replace("{{RELATED_LINKS}}", build_links_html(related_pages))
    html = html.replace("{{MORE_LINKS}}",    build_links_html(more_pages))
    html = html.replace("{{HUB_LINK}}",      hub_link_html)
    html = html.replace("{{CANONICAL_URL}}", escape_html(canonical))

    # Strip any other unresolved {{TOKEN}} placeholders so the page still
    # writes cleanly even if the template adds new placeholders later.
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", html)))
    if unresolved:
        print(f"[warn] stripping unresolved template placeholders: {', '.join(unresolved)}")
        for token in unresolved:
            html = html.replace(token, "")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    new_generated_slugs.add(slug)
    new_generated_keywords.add(keyword)
    processed_keywords.add(keyword)
    remaining_keywords = [kw for kw in remaining_keywords if kw != keyword]

    existing_pages.append({"keyword": keyword, "slug": slug})
    existing_pages = dedupe_pages_by_slug(existing_pages)
    generated_count += 1

    print(
        f"Generated: {slug} ({generated_count}/{DAILY_LIMIT}) "
        f"-> hub: {find_best_hub_slug(keyword)}"
    )

    if generated_count % COMMIT_EVERY == 0:
        git_checkpoint(generated_count, new_generated_keywords, new_generated_slugs, remaining_keywords)

# Final checkpoint
git_checkpoint(generated_count, new_generated_keywords, new_generated_slugs, remaining_keywords)

print(
    f"\nDone. Generated {generated_count} new pages. "
    f"Skipped {skipped_existing_count} existing pages. "
    f"Failed {failed_count} keywords."
)
print(f"Remaining keywords in queue: {len(remaining_keywords)}")
