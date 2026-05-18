import json
import os
import re
import sys
from html import escape
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from generate_token_content import generate_token_content

# -------------------------
# CONFIG
# -------------------------

KEYWORD_FILE           = os.path.join(BASE_DIR, "data", "token_keywords.txt")
GENERATED_SLUGS_FILE   = os.path.join(BASE_DIR, "data", "token_generated_slugs.txt")
GENERATED_KEYWORDS_FILE= os.path.join(BASE_DIR, "data", "token_generated_keywords.txt")
TEMPLATE_FILE          = os.path.join(BASE_DIR, "token-risk-template", "token-risk-template-a.html")
OUTPUT_DIR             = os.path.join(BASE_DIR, "token-risk")
SITE                   = "https://verixiaapps.com"

RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT    = 10
DAILY_LIMIT         = int(os.getenv("DAILY_LIMIT", "100"))

PROTECTED_SLUGS  = {"token-risk", "token-risk-hub"}
FALLBACK_HUB_SLUG = "token-risk-hub"

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
}

TOKEN_CLUSTER_TERMS = {
    "token", "coin", "crypto", "meme", "memecoin", "pump", "moon", "degen",
    "microcap", "shitcoin", "moonshot", "fair", "launch", "stealth", "cto",
    "solana", "ethereum", "eth", "base", "bsc", "arbitrum", "polygon",
    "avalanche", "blast", "sui", "ton", "tron", "bitcoin", "liquidity",
    "volume", "pair", "fdv", "market", "cap", "buyers", "sellers", "pool",
    "slippage", "chart", "candles", "price", "change", "swap", "buy",
    "entry", "exit", "rug", "honeypot", "safe", "legit", "risk",
}

BRAND_CASE = {
    "binance smart chain": "Binance Smart Chain",
    "market cap":          "Market Cap",
    "pair age":            "Pair Age",
    "price action":        "Price Action",
    "price change":        "Price Change",
    "trust wallet":        "Trust Wallet",
    "pool depth":          "Pool Depth",
    "token risk hub":      "Token Risk Hub",
    "token risk":          "Token Risk",
    "metamask":            "MetaMask",
    "dexscreener":         "Dexscreener",
    "pancakeswap":         "PancakeSwap",
    "uniswap":             "Uniswap",
    "raydium":             "Raydium",
    "coinbase":            "Coinbase",
    "ethereum":            "Ethereum",
    "avalanche":           "Avalanche",
    "arbitrum":            "Arbitrum",
    "polygon":             "Polygon",
    "phantom":             "Phantom",
    "bitcoin":             "Bitcoin",
    "solana":              "Solana",
    "binance":             "Binance",
    "jupiter":             "Jupiter",
    "liquidity":           "Liquidity",
    "volume":              "Volume",
    "buyers":              "Buyers",
    "sellers":             "Sellers",
    "slippage":            "Slippage",
    "crypto":              "Crypto",
    "token":               "Token",
    "market":              "Market",
    "fdv":                 "FDV",
    "bsc":                 "BSC",
    "eth":                 "ETH",
    "ton":                 "TON",
    "trx":                 "TRX",
    "tron":                "Tron",
    "base":                "Base",
    "blast":               "Blast",
    "sui":                 "Sui",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with",
}

HUB_TITLE_OVERRIDES = {
    "meme-token-risk":     "Meme Token Risk Hub",
    "solana-token-risk":   "Solana Token Risk Hub",
    "ethereum-token-risk": "Ethereum Token Risk Hub",
    "base-token-risk":     "Base Token Risk Hub",
    "bsc-token-risk":      "BSC Token Risk Hub",
    "arbitrum-token-risk": "Arbitrum Token Risk Hub",
    "token-metrics-risk":  "Token Metrics Risk Hub",
    "buy-intent-risk":     "Buy Intent Risk Hub",
    "token-safety-check":  "Token Safety Check Hub",
    "token-risk-hub":      "Token Risk Hub",
}

# Ordered from most specific to most general.
HUB_MATCH_RULES = [
    ("meme coin",      "meme-token-risk"),
    ("memecoin",       "meme-token-risk"),
    ("meme token",     "meme-token-risk"),
    ("shitcoin",       "meme-token-risk"),
    ("microcap",       "meme-token-risk"),
    ("moonshot",       "meme-token-risk"),
    ("degen",          "meme-token-risk"),
    ("pump",           "meme-token-risk"),
    ("moon",           "meme-token-risk"),
    ("should i buy",   "buy-intent-risk"),
    ("worth buying",   "buy-intent-risk"),
    ("good investment","buy-intent-risk"),
    ("safe to buy",    "buy-intent-risk"),
    ("buy now",        "buy-intent-risk"),
    ("entry",          "buy-intent-risk"),
    ("buy",            "buy-intent-risk"),
    ("liquidity",      "token-metrics-risk"),
    ("volume",         "token-metrics-risk"),
    ("pair age",       "token-metrics-risk"),
    ("pool depth",     "token-metrics-risk"),
    ("slippage",       "token-metrics-risk"),
    ("fdv",            "token-metrics-risk"),
    ("market cap",     "token-metrics-risk"),
    ("buyers",         "token-metrics-risk"),
    ("sellers",        "token-metrics-risk"),
    ("solana",         "solana-token-risk"),
    ("ethereum",       "ethereum-token-risk"),
    ("eth",            "ethereum-token-risk"),
    ("base",           "base-token-risk"),
    ("bsc",            "bsc-token-risk"),
    ("arbitrum",       "arbitrum-token-risk"),
    ("safe",           "token-safety-check"),
    ("legit",          "token-safety-check"),
    ("risky",          "token-safety-check"),
    ("rug pull",       "token-safety-check"),
    ("rug",            "token-safety-check"),
    ("honeypot",       "token-safety-check"),
    ("token risk",     "token-risk-hub"),
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
    kw = re.sub(r"^\s*is\s+this\s+",     "", kw)
    kw = re.sub(r"^\s*is\s+",            "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+","", kw)
    kw = re.sub(r"^\s*should\s+i\s+buy\s+","", kw)
    kw = re.sub(r"^\s*check\s+",         "", kw)
    kw = re.sub(r"\s+safe\s+to\s+buy\b", "", kw)
    kw = re.sub(r"\s+to\s+buy\b",        "", kw)
    kw = re.sub(r"\s+to\s+trade\b",      "", kw)
    kw = re.sub(r"\s+safe$",             "", kw)
    kw = re.sub(r"\s+legit$",            "", kw)
    kw = re.sub(r"\s+risky$",            "", kw)
    kw = re.sub(r"\s+real$",             "", kw)
    kw = re.sub(r"\s+scam$",             "", kw)
    kw = re.sub(r"\s+warning$",          "", kw)
    kw = re.sub(r"\s+alert$",            "", kw)
    kw = re.sub(r"\s+danger$",           "", kw)
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
    return {token for token in keyword_tokens(text) if token in TOKEN_CLUSTER_TERMS}


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
        or kw.startswith("check ")
    )


def is_question_style_keyword(keyword):
    kw = normalize_keyword(keyword)
    return kw.startswith(("is ", "can ", "should ", "what ", "why ", "when ", "where "))


def clean_keyword_for_title(text):
    kw = normalize_keyword(text)
    kw = re.sub(r"^\s*is\s+this\s+",       "", kw)
    kw = re.sub(r"^\s*is\s+",              "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+", "", kw)
    kw = re.sub(r"^\s*should\s+i\s+buy\s+","", kw)
    kw = re.sub(r"^\s*what\s+is\s+a?\s*",  "", kw)
    kw = re.sub(r"^\s*how\s+to\s+",        "", kw)
    kw = re.sub(r"^\s*check\s+",           "", kw)
    noise = [
        r"\btoken\b", r"\bcoin\b", r"\bcrypto\b",
        r"\brisk\b", r"\bsafe\b", r"\blegit\b",
        r"\bscam\b", r"\bhoneypot\b", r"\brug\s*pull\b",
        r"\bcheck\b", r"\bchecker\b", r"\breview\b",
        r"\bwarning\b", r"\balert\b", r"\bdanger\b",
        r"\bbefore\s+buy(ing)?\b", r"\bbefore\s+invest(ing)?\b", r"\bbefore\s+you\s+buy\b",
        r"\bto\s+buy\b", r"\bto\s+trade\b", r"\bfor\s+sale\b",
        r"\bis\b", r"\bthis\b", r"\bwhat\b", r"\bhow\b",
        r"\bthe\b", r"\ba\b",
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
        r"\bi\b", r"\bmy\b", r"\byou(r)?\b",
        r"\bcan\b", r"\bshould\b", r"\bwill\b", r"\bwould\b",
        r"\binvest(ing|ment|or)?\b", r"\btrad(e|ing|er)?\b",
        r"\bmarket(s)?\b", r"\bguide\b", r"\btip(s)?\b",
        r"\bare\b", r"\bof\b", r"\bin\b", r"\bon\b",
        r"\bvs\b", r"\bversus\b",
        r"\bbuy(ing)?\b", r"\bsell(ing)?\b",
        r"\bsafety\b", r"\bsign(s)?\b", r"\brisks?\b",
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
        raw   = normalize_keyword(keyword)
        if not raw:
            return "Token Risk Check -- On-Chain Analysis"
        subject = extract_subject(keyword)
        s     = title_case(subject) if subject and len(subject) > 2 else ""
        lower = raw.lower()
        if "honeypot" in lower:
            return f"Honeypot Token Check -- {s or 'Solana + EVM'}"
        if "rug pull" in lower or "rug-pull" in lower or "rugpull" in lower:
            return f"Rug Pull Token Check -- {s or 'Solana + EVM'}"
        if any(t in lower for t in ["scam", "fake", "fraud", "phish"]):
            return f"Scam Token Check -- {'Is ' + s + ' Legitimate?' if s else 'Verify Before Buying'}"
        if any(t in lower for t in ["safe", "legit", "real", "trust"]):
            s_safe = s if s and s not in ["Trust","Safe","Real","Legit"] else "This Token"
            return f"Token Risk Check -- Is {s_safe} Safe?"
        if any(t in lower for t in ["risk", "risky", "danger", "warning"]):
            return f"{s or 'Token'} Risk -- On-Chain Safety Check"
        if any(t in lower for t in ["how", "what", "why", "explain", "does", "work", "guide", "tutorial"]):
            return f"On-Chain Guide -- {s + ' Risk Analysis' if s else 'Token Risk Analysis'}"
        if any(t in lower for t in ["vs", "versus", "compare", "difference", "between"]):
            return f"{s + ' -- Token Risk Comparison' if s else 'Token Risk Comparison -- Solana + EVM'}"
        if any(t in lower for t in ["better", "best", "top", "choose", "pick"]):
            s_best = s if s and s not in ["Best","Top"] else ""
            return f"Best {s_best}? On-Chain Risk Comparison" if s_best else "Token Risk Comparison -- Solana + EVM"
        if any(t in lower for t in ["price", "worth", "pump", "moon", "prediction", "forecast"]):
            return f"{'Is ' + s + ' Worth Buying? On-Chain Risk Check' if s else 'Token Risk Check -- Price + On-Chain Signals'}"
        if any(t in lower for t in ["buy", "invest", "should", "portfolio", "entry"]):
            return f"{'Should I Buy ' + s + '? Token Risk Check' if s else 'Token Risk Check -- Before You Buy'}"
        if s:
            return f"Is {s} Safe? Token Risk Check"
        soft = soft_extract(keyword)
        if soft and len(soft) > 2:
            return f"{title_case(soft)} -- Token Risk Check"
        return "Token Risk Check -- On-Chain Analysis"
    except Exception:
        return "Token Risk Check -- On-Chain Analysis"


def build_static_intro(keyword):
    lower = normalize_keyword(keyword).lower()
    if "honeypot" in lower:
        return (
            "Check whether this token blocks selling at the contract level. "
            "Honeypot tokens look identical to legitimate tokens on price charts until you try to exit."
        )
    if "rug pull" in lower or "rug-pull" in lower or "rugpull" in lower:
        return (
            "Review the liquidity lock status, holder concentration, and contract permissions "
            "before committing to a position."
        )
    if "scam" in lower or "fake" in lower:
        return (
            "Verify the contract structure, on-chain trading history, and developer wallet activity "
            "before buying in."
        )
    return (
        "Paste any contract address for an instant on-chain risk assessment -- "
        "honeypot detection, liquidity analysis, holder concentration, and contract permissions."
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
            "[warning] token_generated_slugs.txt and token_generated_keywords.txt are not "
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
    return f'<a href="/token-risk/{hub_slug}/">{escape_html(hub_title)}</a>'


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
# SEO TEXT HELPERS
# -------------------------

def build_og_image(slug):
    return "https://verixiaapps.com/og/token-risk.png"


def build_schema_faq(keyword):
    lower = normalize_keyword(keyword).lower()

    base_items = [
        (
            "How does the token risk checker work?",
            "Paste the token contract address into the checker. The tool reads the smart contract "
            "directly to identify structural risk signals -- minting permissions, freeze authority, "
            "blacklisting functions, sell restrictions -- then reviews the liquidity pool depth, LP "
            "lock status, and top holder wallet percentages. Results return in seconds with a risk "
            "level and specific signals detected.",
        ),
        (
            "Is the check free?",
            "The first check is free with no account required. Unlimited checks are available from "
            "$3.99 per week. Subscribe with any email address and cancel anytime from your account.",
        ),
        (
            "What chains are supported?",
            "The checker supports Solana SPL tokens and EVM tokens across Ethereum, Base, Arbitrum, "
            "BNB Chain, Polygon, and Avalanche. Paste the full contract address -- for Solana tokens "
            "this is the token mint address, for EVM tokens it is the 0x contract address.",
        ),
    ]

    if "honeypot" in lower:
        intent_item = (
            "What is a honeypot token?",
            "A honeypot token is a smart contract that allows purchases but blocks selling. The "
            "restriction is encoded into the transfer function -- a require() statement that causes "
            "sell transactions to revert for non-whitelisted wallets. Honeypots can look identical "
            "to legitimate tokens on price charts because buy transactions execute normally while "
            "only sell attempts fail.",
        )
    elif "rug pull" in lower or "rug-pull" in lower or "rugpull" in lower or "rug" in lower:
        intent_item = (
            "What is a rug pull in crypto?",
            "A rug pull happens when token developers or large holders remove all liquidity from the "
            "trading pool after attracting enough buyers. Liquidity removal collapses the token price "
            "instantly -- often 99% or more. The risk is visible before it happens: unlocked LP tokens, "
            "thin pools relative to market cap, and anonymous developer wallets are the main on-chain "
            "signals.",
        )
    elif any(t in lower for t in ["liquidity", " pool ", " lp "]):
        intent_item = (
            "What does liquidity lock status mean?",
            "Liquidity lock status indicates whether LP tokens are locked in a time-lock contract. "
            "Unlocked LP tokens mean the developer can remove all liquidity at any time, instantly "
            "collapsing the token price. Check the lock duration and the percentage of LP tokens "
            "that are locked.",
        )
    else:
        intent_item = (
            "What is holder concentration and why does it matter?",
            "Holder concentration measures what percentage of a token's supply is held by the largest "
            "wallets. When five wallets hold 60% or more of supply, a coordinated exit can move the "
            "market faster than other buyers can absorb. The checker surfaces top wallet percentages "
            "alongside pool depth to give a complete picture of exit risk.",
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
        return "Token Risk Checker | Liquidity, Volume, Pair Age & Risk Signals"
    if is_guidance_style_keyword(raw):
        return f"{title_case(raw)} | Token Risk, Liquidity & Warning Signs"
    if raw.startswith("is this "):
        return f"{title_case(raw)}? Token Risk, Liquidity & What To Know"
    if raw.startswith("is ") and contains_term_phrase(raw, "safe"):
        cleaned = re.sub(r"\s+safe\b", "", raw).strip()
        return f"Is {title_case(cleaned)} Safe? Token Risk, Liquidity & Warning Signs"
    if raw.startswith("should i buy "):
        cleaned = re.sub(r"^should i buy\s+", "", raw).strip()
        return f"Should I Buy {title_case(cleaned)}? Token Risk & Warning Signs"
    if is_question_style_keyword(raw):
        return f"{title_case(raw)}? Token Risk, Liquidity & What To Know"
    return f"{readable} Token Risk | Liquidity, Volume, Pair Age & Warning Signs"


def build_description(keyword):
    raw      = normalize_keyword(keyword)
    readable = readable_keyword(keyword)
    clean_kw = display_keyword(keyword)
    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        return (
            f"Review token risk signals for {readable}, including liquidity, volume, pair age, "
            f"price action, and broader market-structure warning signs before you buy or swap."
        )
    return (
        f"Check {readable} token risk with liquidity, volume, pair age, price action, and "
        f"market-structure signals. Review {clean_kw} risk before you buy, swap, or connect."
    )


def build_related_anchor(keyword):
    raw      = normalize_keyword(keyword)
    readable = readable_keyword(keyword)
    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        anchor = title_case(raw)
        if is_question_style_keyword(raw) and not anchor.endswith("?"):
            anchor += "?"
        return anchor
    return f"{readable} Token Risk"


def build_canonical(slug):
    return f"{SITE}/token-risk/{slug}/"


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
        f'<li><a href="/token-risk/{p["slug"]}/">'
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
    raw_keyword = normalize_keyword(keyword)
    results = []

    for _ in range(2):
        try:
            ai_text = sanitize_ai_html(generate_token_content(raw_keyword))
            if ai_text:
                results.append(ai_text)
        except Exception as e:
            print(f"[warn] AI call failed for '{raw_keyword}': {e}")

    if not results:
        return ""

    return max(results, key=len)


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

generated_count        = 0
skipped_existing_count = 0
skipped_no_content     = 0
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
    title       = build_title(keyword)
    description = build_description(keyword)
    canonical   = build_canonical(slug)

    ai_text = generate_ai_text(keyword, keyword_display)
    if not ai_text:
        skipped_no_content += 1
        print(f"[skipped] No AI content produced for: {keyword}")
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
    html = render_page_html(
        template,
        {
            "{{TITLE}}":             escape_html(title),
            "{{DESCRIPTION}}":       escape_html(description),
            "{{KEYWORD}}":           escape_html(keyword_display),
            "{{AI_CONTENT}}":        ai_text,
            "{{RELATED_LINKS}}":     build_links_html(related_pages),
            "{{MORE_LINKS}}":        build_links_html(more_pages),
            "{{HUB_LINK}}":          hub_link_html,
            "{{CANONICAL_URL}}":     escape_html(canonical),
            "{{MODIFIED_DATE}}":     datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "{{BREADCRUMB_NAME}}":   escape_html(title_case(keyword_display) or readable_keyword(keyword)),
            "{{STATIC_H1}}":         escape_html(build_static_h1(keyword)),
            "{{STATIC_INTRO}}":      escape_html(build_static_intro(keyword)),
            "{{OG_IMAGE}}":          escape_html(build_og_image(slug)),
            "{{HL_DATA_BLOCK}}":     "",
            "{{PAGE_META_SCRIPT}}":  "",
            "{{SCHEMA_FAQ}}":        build_schema_faq(keyword),
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
        f"-> hub: {find_best_hub_slug(keyword)}"
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
    f"Skipped {skipped_existing_count} existing. "
    f"Skipped {skipped_no_content} with no AI content."
)
print(f"Remaining keywords in queue: {len(remaining_keywords)}")
