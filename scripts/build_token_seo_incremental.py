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

KEYWORD_FILE            = os.path.join(BASE_DIR, "data", "token_keywords.txt")
GENERATED_SLUGS_FILE    = os.path.join(BASE_DIR, "data", "token_generated_slugs.txt")
GENERATED_KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "token_generated_keywords.txt")
TEMPLATE_FILE           = os.path.join(BASE_DIR, "token-risk-template", "token-risk-template-a.html")
OUTPUT_DIR              = os.path.join(BASE_DIR, "token-risk")
SITE                    = "https://verixiaapps.com"

RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT    = 10
DAILY_LIMIT         = int(os.getenv("DAILY_LIMIT", "100"))

PROTECTED_SLUGS   = {"token-risk", "token-risk-hub"}
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

HUB_MATCH_RULES = [
    ("meme coin",       "meme-token-risk"),
    ("memecoin",        "meme-token-risk"),
    ("meme token",      "meme-token-risk"),
    ("shitcoin",        "meme-token-risk"),
    ("microcap",        "meme-token-risk"),
    ("moonshot",        "meme-token-risk"),
    ("degen",           "meme-token-risk"),
    ("pump",            "meme-token-risk"),
    ("moon",            "meme-token-risk"),
    ("should i buy",    "buy-intent-risk"),
    ("worth buying",    "buy-intent-risk"),
    ("good investment", "buy-intent-risk"),
    ("safe to buy",     "buy-intent-risk"),
    ("buy now",         "buy-intent-risk"),
    ("entry",           "buy-intent-risk"),
    ("buy",             "buy-intent-risk"),
    ("liquidity",       "token-metrics-risk"),
    ("volume",          "token-metrics-risk"),
    ("pair age",        "token-metrics-risk"),
    ("pool depth",      "token-metrics-risk"),
    ("slippage",        "token-metrics-risk"),
    ("fdv",             "token-metrics-risk"),
    ("market cap",      "token-metrics-risk"),
    ("buyers",          "token-metrics-risk"),
    ("sellers",         "token-metrics-risk"),
    ("solana",          "solana-token-risk"),
    ("ethereum",        "ethereum-token-risk"),
    ("eth",             "ethereum-token-risk"),
    ("base",            "base-token-risk"),
    ("bsc",             "bsc-token-risk"),
    ("arbitrum",        "arbitrum-token-risk"),
    ("safe",            "token-safety-check"),
    ("legit",           "token-safety-check"),
    ("risky",           "token-safety-check"),
    ("rug pull",        "token-safety-check"),
    ("rug",             "token-safety-check"),
    ("honeypot",        "token-safety-check"),
    ("token risk",      "token-risk-hub"),
]

# Counters
engine_meta_used_count     = 0
python_meta_fallback_count = 0


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
    kw = re.sub(r"^\s*is\s+this\s+",       "", kw)
    kw = re.sub(r"^\s*is\s+",              "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+", "", kw)
    kw = re.sub(r"^\s*should\s+i\s+buy\s+","", kw)
    kw = re.sub(r"^\s*check\s+",           "", kw)
    kw = re.sub(r"\s+safe\s+to\s+buy\b",   "", kw)
    kw = re.sub(r"\s+to\s+buy\b",          "", kw)
    kw = re.sub(r"\s+to\s+trade\b",        "", kw)
    kw = re.sub(r"\s+safe$",               "", kw)
    kw = re.sub(r"\s+legit$",              "", kw)
    kw = re.sub(r"\s+risky$",              "", kw)
    kw = re.sub(r"\s+real$",               "", kw)
    kw = re.sub(r"\s+scam$",               "", kw)
    kw = re.sub(r"\s+warning$",            "", kw)
    kw = re.sub(r"\s+alert$",              "", kw)
    kw = re.sub(r"\s+danger$",             "", kw)
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
# PYTHON FALLBACK BUILDERS (used only when engine returns no meta)
# These are kept defensive -- engine should always provide meta now.
# Platform-trap aware: where possible, prefer minimal generic copy over
# regex-extracted "subjects" that might be platforms.
# -------------------------

def build_title_python_fallback(keyword):
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


def build_description_python_fallback(keyword):
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


def build_h1_python_fallback(keyword):
    """Minimal H1 fallback. No regex subject extraction -- avoids the platform bug."""
    raw = normalize_keyword(keyword)
    if not raw:
        return "Token Risk Check"
    lower = raw.lower()
    if "honeypot" in lower:
        return "Honeypot Token Check"
    if "rug" in lower:
        return "Rug Pull Risk Check"
    if "scam" in lower:
        return "Scam Token Check"
    return "Token Risk Check"


def build_intro_python_fallback(keyword):
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


def build_schema_faq_python_fallback(keyword):
    """Minimal FAQ schema fallback. Engine should always provide one."""
    items = [
        ("How does the token risk checker work?",
         "Paste the token contract address into the checker. The tool reads the smart contract "
         "directly to identify structural risk signals -- minting permissions, freeze authority, "
         "sell restrictions -- then reviews liquidity pool depth, LP lock status, and top holder "
         "wallet percentages. Results return in seconds."),
        ("Is the check free?",
         "The first check is free with no account required. Unlimited checks are available from "
         "$3.99 per week. Subscribe with any email address and cancel anytime."),
        ("What chains are supported?",
         "Solana SPL tokens and EVM tokens across Ethereum, Base, Arbitrum, BNB Chain, Polygon, "
         "and Avalanche. Paste the full contract address -- for Solana this is the token mint, "
         "for EVM it is the 0x contract address."),
    ]
    schema = {
        "@context":   "https://schema.org",
        "@type":      "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in items
        ],
    }
    return json.dumps(schema, ensure_ascii=False)


# -------------------------
# SEO TEXT HELPERS (Python-side, engine-independent)
# -------------------------

def build_og_image(slug):
    return "https://verixiaapps.com/og/token-risk.png"


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
# CONTENT HANDLING (engine output)
# -------------------------

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


def is_usable_ai_text(text):
    if not text:
        return False
    raw = str(text).strip()
    if len(raw) < 250:
        return False
    lowered = raw.lower()
    weak_markers = {
        "lorem ipsum", "as an ai", "i can't help with that", "i cannot help with that",
        "i am sorry", "i'm sorry", "cannot assist", "can't assist",
    }
    if any(marker in lowered for marker in weak_markers):
        return False
    return True


def call_engine(keyword):
    """Single call into the risk engine via generate_token_content.
    Expected return shape: dict with `content` (str) and `meta` (dict).
    Backward-compat: if a plain string is returned, treat as content-only."""
    result = generate_token_content(keyword)
    if isinstance(result, dict):
        return {
            "content": result.get("content") or "",
            "meta":    result.get("meta") or {},
        }
    return {"content": str(result or ""), "meta": {}}


# -------------------------
# HL_DATA_BLOCK + PAGE_META_SCRIPT RENDERERS
# -------------------------

def render_hl_data_block(meta):
    """Render a live-data block from canonical pair info + observations.
    Returns empty string when no canonical pair was resolved (category, concept,
    platform-context keywords). When present, gives the page a real-data anchor."""
    if not meta:
        return ""
    cp = meta.get("canonicalPair") or {}
    if not cp or not cp.get("address"):
        return ""

    rows = []
    if cp.get("symbol"):
        rows.append(("Ticker", str(cp["symbol"])))
    if cp.get("chain"):
        rows.append(("Chain", str(cp["chain"]).title()))
    if cp.get("dex"):
        rows.append(("Primary DEX", str(cp["dex"])))
    if cp.get("liquidityUsd"):
        rows.append(("Pool depth", str(cp["liquidityUsd"])))
    if cp.get("volume24h"):
        rows.append(("24h volume", str(cp["volume24h"])))
    if cp.get("marketCap"):
        rows.append(("Market cap", str(cp["marketCap"])))
    if cp.get("pairAge"):
        rows.append(("Pair age", str(cp["pairAge"])))

    contract = cp.get("contractData") or {}
    if contract.get("available"):
        if contract.get("splMintAuthorityRenounced") is True:
            rows.append(("Mint authority", "Renounced"))
        elif contract.get("splMintAuthorityRenounced") is False:
            rows.append(("Mint authority", "Active &mdash; deployer can mint"))
        if contract.get("splFreezeAuthorityRenounced") is True:
            rows.append(("Freeze authority", "Renounced"))
        elif contract.get("splFreezeAuthorityRenounced") is False:
            rows.append(("Freeze authority", "Active &mdash; deployer can freeze"))
        if contract.get("splTop10HoldersPct") is not None:
            rows.append(("Top 10 holders", f"{contract['splTop10HoldersPct']}%"))
        if contract.get("evmOwnerRenounced") is True:
            rows.append(("Contract owner", "Renounced (0x0)"))
        elif contract.get("evmOwnerRenounced") is False and contract.get("evmHasOwnerFunction") is True:
            rows.append(("Contract owner", "Active"))

    if not rows:
        return ""

    rows_html = "".join(
        f'<div class="vx-hl-row"><span class="vx-hl-label">{escape_html(label)}</span>'
        f'<span class="vx-hl-value">{value}</span></div>'
        for label, value in rows
    )
    addr = cp.get("address", "")
    addr_short = f"{addr[:6]}...{addr[-4:]}" if len(addr) > 14 else addr
    return (
        f'<section class="vx-hl-data" data-vx-canonical-address="{escape_html(addr)}">'
        f'<header class="vx-hl-header">'
        f'<span class="vx-hl-eyebrow">Live on-chain reads</span>'
        f'<span class="vx-hl-addr">{escape_html(addr_short)}</span>'
        f'</header>'
        f'<div class="vx-hl-rows">{rows_html}</div>'
        f'</section>'
    )


def render_page_meta_script(meta, keyword, slug):
    """Inject window.__pageMeta so the template's scanner widget can pick up
    subject/canonical context client-side. Mirrors the v16 page-meta pattern."""
    if not meta:
        return ""
    cp = meta.get("canonicalPair") or {}
    payload = {
        "keyword":          keyword,
        "slug":             slug,
        "intent":           "token_risk",
        "subIntent":        meta.get("subIntent") or "general",
        "subjectType":      meta.get("subjectType") or "generic",
        "subjectDisplay":   meta.get("subjectDisplay") or "",
        "ticker":           meta.get("ticker") or "",
        "platform":         meta.get("platform") or "",
        "category":         meta.get("category") or "",
        "concept":          meta.get("concept") or "",
        "canonicalAddress": cp.get("address") or "",
        "canonicalChain":   cp.get("chain") or "",
        "canonicalSymbol":  cp.get("symbol") or "",
    }
    json_payload = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return f'<script>window.__pageMeta = {json_payload};</script>'


# -------------------------
# SETUP + LOAD
# -------------------------

validate_daily_limit(DAILY_LIMIT)

os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(GENERATED_SLUGS_FILE)
ensure_file(GENERATED_KEYWORDS_FILE)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

validate_template_placeholders(template)

# Detect whether template includes the optional PAGE_META_SCRIPT placeholder
TEMPLATE_HAS_PAGE_META = "{{PAGE_META_SCRIPT}}" in template

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

print(f"Loaded {len(keywords)} keywords from queue.", flush=True)
print(f"Unique queued pages after slug dedupe: {len(queue_pages)}", flush=True)
print(f"Duplicate queued keywords skipped: {duplicate_queue_count}", flush=True)
print(f"Known generated slugs: {len(generated_slugs)}", flush=True)
print(f"Known generated keywords: {len(generated_keywords)}", flush=True)
print(f"Existing pages available for internal links: {len(existing_pages)}", flush=True)
print(f"Daily limit: {DAILY_LIMIT}", flush=True)
print(f"Fallback hub slug: {FALLBACK_HUB_SLUG}", flush=True)
print(f"Template has PAGE_META_SCRIPT: {TEMPLATE_HAS_PAGE_META}", flush=True)

generated_count        = 0
skipped_existing_count = 0
failed_count           = 0
processed_keywords     = set()
new_pages_this_run     = []

# -------------------------
# GENERATE LOOP
# -------------------------

for page in queue_pages:
    if generated_count >= DAILY_LIMIT:
        break

    slug            = page["slug"]
    keyword         = page["keyword"]
    keyword_display = display_keyword(keyword)
    path            = page_path(slug)

    if slug in PROTECTED_SLUGS:
        processed_keywords.add(keyword)
        print("Skipping protected page:", slug, flush=True)
        continue

    if page_exists(slug):
        skipped_existing_count += 1
        processed_keywords.add(keyword)
        continue

    os.makedirs(os.path.dirname(path), exist_ok=True)

    # 1. Single engine call -- no retry loop. Engine has no-failure contract.
    try:
        engine_result = call_engine(keyword)
        raw_content   = engine_result["content"]
        engine_meta   = engine_result["meta"] or {}
    except Exception as e:
        failed_count += 1
        print(f"[failed] {keyword} -> engine error: {e}", flush=True)
        continue

    if not is_usable_ai_text(raw_content):
        failed_count += 1
        print(f"[failed] {keyword} -> engine returned thin/unusable content", flush=True)
        continue

    ai_text = sanitize_ai_html(raw_content)
    if not ai_text:
        failed_count += 1
        print(f"[failed] {keyword} -> content sanitization produced empty string", flush=True)
        continue

    # 2. Meta: engine output preferred; fallback only when missing
    if engine_meta.get("title"):
        title = engine_meta["title"]
        engine_meta_used_count += 1
    else:
        title = build_title_python_fallback(keyword)
        python_meta_fallback_count += 1

    description    = engine_meta.get("description") or build_description_python_fallback(keyword)
    static_h1      = engine_meta.get("h1")          or build_h1_python_fallback(keyword)
    static_intro   = engine_meta.get("intro")       or build_intro_python_fallback(keyword)
    breadcrumb     = engine_meta.get("breadcrumb")  or (title_case(keyword_display) or readable_keyword(keyword))
    faq_schema     = engine_meta.get("faqSchema")   or build_schema_faq_python_fallback(keyword)
    canonical      = build_canonical(slug)
    hl_data_html   = render_hl_data_block(engine_meta)
    page_meta_html = render_page_meta_script(engine_meta, keyword, slug)

    # 3. Related + more links
    related_pages = get_related_pages(page, existing_pages, RELATED_LINKS_COUNT)
    related_slugs = {p["slug"] for p in related_pages}
    more_pages    = get_related_pages(
        page, existing_pages, MORE_LINKS_COUNT,
        exclude_slugs=related_slugs,
    )

    hub_link_html = build_hub_link_html(keyword)

    # 4. Render
    replacements = {
        "{{TITLE}}":           escape_html(title),
        "{{DESCRIPTION}}":     escape_html(description),
        "{{KEYWORD}}":         escape_html(keyword_display),
        "{{AI_CONTENT}}":      ai_text,
        "{{RELATED_LINKS}}":   build_links_html(related_pages),
        "{{MORE_LINKS}}":      build_links_html(more_pages),
        "{{HUB_LINK}}":        hub_link_html,
        "{{CANONICAL_URL}}":   escape_html(canonical),
        "{{MODIFIED_DATE}}":   datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "{{BREADCRUMB_NAME}}": escape_html(breadcrumb),
        "{{STATIC_H1}}":       escape_html(static_h1),
        "{{STATIC_INTRO}}":    escape_html(static_intro),
        "{{OG_IMAGE}}":        escape_html(build_og_image(slug)),
        "{{HL_DATA_BLOCK}}":   hl_data_html,
        "{{SCHEMA_FAQ}}":      faq_schema,
    }
    if TEMPLATE_HAS_PAGE_META:
        replacements["{{PAGE_META_SCRIPT}}"] = page_meta_html

    try:
        html = render_page_html(template, replacements)
    except Exception as e:
        failed_count += 1
        print(f"[failed] {keyword} -> render error: {e}", flush=True)
        continue

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    processed_keywords.add(keyword)

    new_page_record = {"keyword": keyword, "slug": slug}
    new_pages_this_run.append(new_page_record)
    existing_pages.append(new_page_record)
    existing_pages = dedupe_pages_by_slug(existing_pages)
    generated_count += 1

    subject_type = engine_meta.get("subjectType") or "generic"
    sub_intent   = engine_meta.get("subIntent")   or "general"
    print(
        f"Generated: {slug} ({generated_count}/{DAILY_LIMIT}) "
        f"-> hub: {find_best_hub_slug(keyword)}, subject: {subject_type}, subIntent: {sub_intent}",
        flush=True,
    )

# -------------------------
# WRITE-BACK
# -------------------------

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
    f"Failed {failed_count} keywords.",
    flush=True,
)
print(f"Engine meta used: {engine_meta_used_count}", flush=True)
print(f"Python meta fallback used: {python_meta_fallback_count}", flush=True)
print(f"Remaining keywords in queue: {len(remaining_keywords)}", flush=True)
