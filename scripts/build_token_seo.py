import os
import re
import json
from html import escape
from pathlib import Path

from generate_token_content import generate_token_content, merge_live_fields

# -----------------------------
# CONFIG
# -----------------------------
KEYWORD_FILE = "data/token_keywords.txt"
REJECTED_KEYWORDS_FILE = "data/token_rejected_keywords.txt"
TEMPLATE_FILE = "token-risk-template/token-risk-template-a.html"
OUTPUT_DIR = "token-risk"
SITE = "https://verixiaapps.com"

RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT = 10

PROTECTED_SLUGS = {"token-risk", "token-risk-hub"}

# Required placeholders (page won't build if any are missing)
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

# Optional placeholders — engine provides values; template uses them if present.
# Missing optional placeholders are silently skipped (no template edit needed today).
OPTIONAL_TEMPLATE_PLACEHOLDERS = {
    "{{H1}}",
    "{{INTRO}}",
    "{{CONTENT_HEADING}}",
    "{{CONTENT_BRIDGE}}",
    "{{BREADCRUMB}}",
    "{{THREAT_BANNER}}",
    "{{CONTRACT_BREAKDOWN}}",
    "{{FAQ}}",
    "{{FAQ_SCHEMA}}",
    "{{SUBJECT_DISPLAY}}",
    "{{SUBJECT_TYPE}}",
    "{{SUB_INTENT}}",
    "{{CANONICAL_PAIR_ADDRESS}}",
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
    "market cap": "Market Cap",
    "pair age": "Pair Age",
    "price action": "Price Action",
    "price change": "Price Change",
    "trust wallet": "Trust Wallet",
    "pool depth": "Pool Depth",
    "token risk hub": "Token Risk Hub",
    "token risk": "Token Risk",
    "metamask": "MetaMask",
    "dexscreener": "Dexscreener",
    "pancakeswap": "PancakeSwap",
    "uniswap": "Uniswap",
    "raydium": "Raydium",
    "coinbase": "Coinbase",
    "ethereum": "Ethereum",
    "avalanche": "Avalanche",
    "arbitrum": "Arbitrum",
    "polygon": "Polygon",
    "phantom": "Phantom",
    "bitcoin": "Bitcoin",
    "solana": "Solana",
    "binance": "Binance",
    "jupiter": "Jupiter",
    "liquidity": "Liquidity",
    "volume": "Volume",
    "buyers": "Buyers",
    "sellers": "Sellers",
    "slippage": "Slippage",
    "crypto": "Crypto",
    "token": "Token",
    "market": "Market",
    "fdv": "FDV",
    "bsc": "BSC",
    "eth": "ETH",
    "ton": "TON",
    "trx": "TRX",
    "tron": "Tron",
    "base": "Base",
    "blast": "Blast",
    "sui": "Sui",
    "cto": "CTO",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with",
}

HUB_TITLE_OVERRIDES = {
    "meme-token-risk": "Meme Token Risk Hub",
    "solana-token-risk": "Solana Token Risk Hub",
    "ethereum-token-risk": "Ethereum Token Risk Hub",
    "base-token-risk": "Base Token Risk Hub",
    "bsc-token-risk": "BSC Token Risk Hub",
    "arbitrum-token-risk": "Arbitrum Token Risk Hub",
    "token-metrics-risk": "Token Metrics Risk Hub",
    "buy-intent-risk": "Buy Intent Risk Hub",
    "token-safety-check": "Token Safety Check Hub",
    "token-risk-hub": "Token Risk Hub",
}

HUB_MATCH_RULES = [
    ("meme coin", "meme-token-risk"),
    ("memecoin", "meme-token-risk"),
    ("meme token", "meme-token-risk"),
    ("shitcoin", "meme-token-risk"),
    ("microcap", "meme-token-risk"),
    ("moonshot", "meme-token-risk"),
    ("degen", "meme-token-risk"),
    ("pump", "meme-token-risk"),
    ("moon", "meme-token-risk"),
    ("should i buy", "buy-intent-risk"),
    ("worth buying", "buy-intent-risk"),
    ("good investment", "buy-intent-risk"),
    ("safe to buy", "buy-intent-risk"),
    ("buy now", "buy-intent-risk"),
    ("entry", "buy-intent-risk"),
    ("buy", "buy-intent-risk"),
    ("liquidity", "token-metrics-risk"),
    ("volume", "token-metrics-risk"),
    ("pair age", "token-metrics-risk"),
    ("pool depth", "token-metrics-risk"),
    ("slippage", "token-metrics-risk"),
    ("fdv", "token-metrics-risk"),
    ("market cap", "token-metrics-risk"),
    ("buyers", "token-metrics-risk"),
    ("sellers", "token-metrics-risk"),
    ("solana", "solana-token-risk"),
    ("ethereum", "ethereum-token-risk"),
    ("eth", "ethereum-token-risk"),
    ("base", "base-token-risk"),
    ("bsc", "bsc-token-risk"),
    ("arbitrum", "arbitrum-token-risk"),
    ("safe", "token-safety-check"),
    ("legit", "token-safety-check"),
    ("risky", "token-safety-check"),
    ("rug pull", "token-safety-check"),
    ("rug", "token-safety-check"),
    ("honeypot", "token-safety-check"),
    ("token risk", "token-risk-hub"),
]

LOW_VALUE_SINGLE_TERMS = {
    "token", "coin", "crypto", "market", "risk", "safe", "legit", "buy",
    "entry", "volume", "liquidity", "price",
}

HIGH_INTENT_TERMS = {
    "safe", "legit", "risky", "rug", "honeypot", "buy", "entry",
    "liquidity", "volume", "pair", "fdv", "market", "cap", "buyers",
    "sellers", "slippage", "price", "chart", "token", "risk",
}

# Length targets for validation (engine output should land in range)
TITLE_MIN = 35
TITLE_MAX = 78
DESCRIPTION_MIN = 110
DESCRIPTION_MAX = 170

rejected_count = 0
deduped_keywords_count = 0
skipped_duplicate_keywords_count = 0
skipped_weak_keywords_count = 0
ai_failure_count = 0
engine_meta_used_count = 0
python_meta_fallback_count = 0


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
    kw = re.sub(r"^\s*can\s+i\s+trust\s+", "", kw)
    kw = re.sub(r"^\s*should\s+i\s+buy\s+", "", kw)
    kw = re.sub(r"^\s*check\s+", "", kw)

    kw = re.sub(r"\s+safe$", "", kw)
    kw = re.sub(r"\s+legit$", "", kw)
    kw = re.sub(r"\s+risky$", "", kw)
    kw = re.sub(r"\s+real$", "", kw)
    kw = re.sub(r"\s+scam$", "", kw)

    # Prevents " Token Risk" suffix doubling in build_related_anchor
    kw = re.sub(r"\s+token\s+risk$", "", kw)
    kw = re.sub(r"\s+risk$", "", kw)

    kw = re.sub(r"\s+", " ", kw).strip()
    return kw


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
    return {token for token in keyword_tokens(text) if token in TOKEN_CLUSTER_TERMS}


def keyword_root(text):
    cleaned = canonical_keyword(text)
    return cleaned.split()[0] if cleaned else ""


def escape_html(text):
    return escape(str(text), quote=True)


# -----------------------------
# PYTHON-SIDE FALLBACK META BUILDERS
# Only used when the engine returns no meta (rare; defensive).
# Preserves prior behavior verbatim.
# -----------------------------
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


def build_title_python(keyword):
    raw = normalize_keyword(keyword)
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


def build_description_python(keyword):
    raw = normalize_keyword(keyword)
    readable = readable_keyword(keyword)
    clean_kw = display_keyword(keyword)

    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        return (
            f"Review token risk signals for {readable}, including liquidity, volume, pair age, "
            f"price action, and broader market-structure warning signs before you buy or swap."
        )

    return (
        f"Check {readable} token risk with liquidity, volume, pair age, price action, and market-structure signals. "
        f"Review {clean_kw} risk before you buy, swap, or connect."
    )


def build_canonical(slug):
    return f"{SITE}/token-risk/{slug}/"


# -----------------------------
# TEMPLATE / KEYWORDS
# -----------------------------
def validate_template_placeholders(template_html):
    missing = [
        placeholder for placeholder in REQUIRED_TEMPLATE_PLACEHOLDERS
        if placeholder not in template_html
    ]
    if missing:
        raise ValueError("Template is missing required placeholders: " + ", ".join(sorted(missing)))


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


def load_template():
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(f"Missing template file: {TEMPLATE_FILE}")
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        template = f.read()
    validate_template_placeholders(template)
    return template


# -----------------------------
# HUB ROUTING (Python-side; engine doesn't do this)
# -----------------------------
def find_best_hub_slug(keyword):
    keyword_norm = normalize_keyword(keyword)
    for term, slug in HUB_MATCH_RULES:
        if contains_term_phrase(keyword_norm, term):
            return slug
    return "token-risk-hub"


def build_hub_link_html(keyword):
    hub_slug = find_best_hub_slug(keyword)
    hub_title = HUB_TITLE_OVERRIDES.get(hub_slug, f"{title_case(hub_slug.replace('-', ' '))} Hub")
    return f'<a href="/token-risk/{hub_slug}/">{escape_html(hub_title)}</a>'


# -----------------------------
# DEDUP / QUALITY GATE
# -----------------------------
def is_weak_keyword(keyword):
    tokens = canonical_keyword(keyword).split()

    if len(tokens) < 2:
        return True

    if len(tokens) == 2 and all(token in LOW_VALUE_SINGLE_TERMS for token in tokens):
        return True

    if not any(token in HIGH_INTENT_TERMS or token in TOKEN_CLUSTER_TERMS for token in tokens):
        return True

    return False


def keyword_quality_score(keyword):
    kw = normalize_keyword(keyword)
    score = 0

    if "token risk" in kw:
        score += 10
    if "should i buy" in kw:
        score += 10
    if "safe" in kw:
        score += 8
    if "legit" in kw:
        score += 8
    if "risky" in kw:
        score += 8
    if "rug" in kw or "honeypot" in kw:
        score += 9
    if any(term in kw for term in ["liquidity", "volume", "pair age", "fdv", "market cap", "buyers", "sellers", "slippage"]):
        score += 7
    if any(term in kw for term in ["solana", "ethereum", "base", "bsc", "arbitrum", "bitcoin"]):
        score += 5

    if kw.startswith("is "):
        score -= 4
    if kw.startswith("can i trust "):
        score -= 6

    score -= len(kw) / 100.0
    return score


def choose_canonical_keyword(keywords_for_same_intent):
    return sorted(
        keywords_for_same_intent,
        key=lambda k: (-keyword_quality_score(k), len(k), k)
    )[0]


def dedupe_keywords(raw_keywords):
    global deduped_keywords_count, skipped_duplicate_keywords_count, skipped_weak_keywords_count

    groups = {}
    for keyword in raw_keywords:
        key = canonical_keyword(keyword)
        groups.setdefault(key, []).append(keyword)

    canonical_keywords = []
    seen_slugs = set()

    for _, group in groups.items():
        chosen = choose_canonical_keyword(group)
        chosen_slug = canonical_slug(chosen)

        if chosen_slug in PROTECTED_SLUGS:
            continue

        if is_weak_keyword(chosen):
            skipped_weak_keywords_count += len(group)
            continue

        if chosen_slug in seen_slugs:
            skipped_duplicate_keywords_count += len(group)
            continue

        canonical_keywords.append(chosen)
        seen_slugs.add(chosen_slug)

        if len(group) > 1:
            deduped_keywords_count += len(group) - 1

    return canonical_keywords


# -----------------------------
# RELATED / MORE LINKS (Python-side; engine doesn't do these either)
# -----------------------------
def get_related_pages(current_page, all_pages, limit):
    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_tokens = keyword_tokens(current_keyword)
    current_cluster = keyword_cluster_tokens(current_keyword)
    current_root = keyword_root(current_keyword)
    current_hub = find_best_hub_slug(current_keyword)

    candidates = [
        p for p in all_pages
        if p["slug"] != current_slug and p["slug"] not in PROTECTED_SLUGS
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

        return (
            -same_hub,
            -same_root,
            -shared_cluster,
            -shared_tokens,
            length_diff,
            other_keyword,
        )

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

    if len(related) < limit:
        for page in candidates:
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
            and find_best_hub_slug(p["keyword"]) == current_hub
        ]

    fallback_pages = [
        p for p in all_pages
        if p["slug"] != current_slug
        and p["slug"] not in exclude_slugs
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


# -----------------------------
# VALIDATION + FILE HELPERS
# -----------------------------
def validate_page_output(slug, title, description, canonical, related_pages):
    errors = []

    if not slug:
        errors.append("empty slug")
    if not canonical.endswith(f"/{slug}/"):
        errors.append("canonical mismatch")
    if len(related_pages) == 0:
        errors.append("no related pages")
    if len(title) < TITLE_MIN or len(title) > TITLE_MAX:
        errors.append(f"title length out of target range ({len(title)} chars)")
    if len(description) < DESCRIPTION_MIN or len(description) > DESCRIPTION_MAX:
        errors.append(f"description length out of target range ({len(description)} chars)")

    return errors


def ensure_file(filepath):
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists(filepath):
        with open(filepath, "a", encoding="utf-8"):
            pass


def append_rejected_keyword(keyword, reason):
    global rejected_count

    ensure_file(REJECTED_KEYWORDS_FILE)
    entry = f"{normalize_keyword(keyword)} | {str(reason).strip()}"

    existing = set()
    with open(REJECTED_KEYWORDS_FILE, "r", encoding="utf-8") as f:
        existing = {line.strip() for line in f if line.strip()}

    if entry not in existing:
        with open(REJECTED_KEYWORDS_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        rejected_count += 1


def build_related_anchor(keyword):
    raw = normalize_keyword(keyword)
    readable = readable_keyword(keyword)

    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        anchor = title_case(raw)
        if is_question_style_keyword(raw) and not anchor.endswith("?"):
            anchor += "?"
        return anchor

    # If the readable phrase already contains "risk", don't append "Token Risk"
    # again — this is what produced "Coin Risk Scanner Token Risk" on live pages.
    if re.search(r"\brisk\b", readable, flags=re.IGNORECASE):
        return readable

    return f"{readable} Token Risk"


# -----------------------------
# CONTENT HANDLING (engine output)
# -----------------------------
def is_usable_ai_text(text):
    """Light check on the engine's content. Engine has its own validator + no-failure
    contract, so this is just a defensive belt-and-suspenders before write."""
    if not text:
        return False
    raw = str(text).strip()
    if len(raw) < 250:
        return False

    lowered = raw.lower()
    weak_markers = {
        "lorem ipsum",
        "as an ai",
        "let me know if you want",
        "i can't help with that",
        "i cannot help with that",
        "i am sorry",
        "i'm sorry",
        "cannot assist",
        "can't assist",
    }
    if any(marker in lowered for marker in weak_markers):
        return False
    return True


def wrap_paragraphs(text):
    """Engine returns plain paragraphs separated by blank lines. Wrap in <p> tags."""
    text = str(text or "").strip()
    if not text:
        return ""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "\n".join(f"<p>{escape_html(p)}</p>" for p in paragraphs)


def call_engine(keyword):
    """Single call into the new risk engine via generate_token_content.
    Expected return shape: dict with `content` (str) and `meta` (dict).

    Backward-compat: if generate_token_content returns a plain string,
    treat it as content-only and fall back to Python-side meta builders.

    enrichmentData (DexScreener tier + data) is preserved if present so the
    live-data panel placeholders can be filled downstream.
    """
    result = generate_token_content(keyword)

    if isinstance(result, dict):
        return {
            "content":        result.get("content") or "",
            "meta":           result.get("meta") or {},
            # Preserve enrichment for the live-data panel. May live at top level
            # or inside meta depending on engine wrapper version.
            "enrichmentData": result.get("enrichmentData")
                              or (result.get("meta") or {}).get("enrichmentData"),
            "liveToken":      result.get("liveToken")
                              or (result.get("meta") or {}).get("liveToken"),
        }

    # Legacy shape (string only)
    return {"content": str(result or ""), "meta": {}, "enrichmentData": None, "liveToken": None}


# -----------------------------
# THREAT BANNER / CONTRACT BREAKDOWN RENDERERS
# (only injected when the template has the matching placeholder)
# -----------------------------
def render_threat_banner(meta):
    banner = meta.get("threatBanner") if meta else None
    if not banner:
        return ""
    tier = escape_html(banner.get("tier", "info"))
    icon = escape_html(banner.get("icon", "i"))
    title = escape_html(banner.get("title", ""))
    copy = escape_html(banner.get("copy", ""))
    if not title:
        return ""
    return (
        f'<div class="vx-threat vx-threat--{tier}">'
        f'<span class="vx-threat-icon">{icon}</span>'
        f'<div><strong>{title}</strong><p>{copy}</p></div>'
        f'</div>'
    )


def render_contract_breakdown(meta):
    """Inline the engine's contract-breakdown HTML if present.
    The engine puts this in meta.contractBreakdownHtml when canonical pair
    contract data is available."""
    if not meta:
        return ""
    inline = meta.get("contractBreakdownHtml") or ""
    return str(inline)


def render_faq(meta):
    faq = meta.get("faq") if meta else None
    if not faq:
        return ""
    items = []
    for i, item in enumerate(faq):
        q = escape_html(item.get("q", ""))
        a = escape_html(item.get("a", ""))
        if not q or not a:
            continue
        open_attr = " open" if i == 0 else ""
        items.append(
            f'<details class="vx-faq-item"{open_attr}>'
            f'<summary class="vx-faq-q">{q}</summary>'
            f'<div class="vx-faq-a"><p>{a}</p></div>'
            f'</details>'
        )
    if not items:
        return ""
    return '<section class="vx-faq"><div class="vx-faq-list">' + "\n".join(items) + '</div></section>'


def render_faq_schema(meta):
    schema = meta.get("faqSchema") if meta else None
    if not schema:
        return ""
    return f'<script type="application/ld+json">{schema}</script>'


# -----------------------------
# SETUP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(REJECTED_KEYWORDS_FILE)

template = load_template()
raw_keywords = load_keywords()
keywords = dedupe_keywords(raw_keywords)

pages = []
seen_page_slugs = set()

for keyword in keywords:
    slug = canonical_slug(keyword)
    if not slug or slug in PROTECTED_SLUGS or slug in seen_page_slugs:
        continue
    pages.append({"keyword": keyword, "slug": slug})
    seen_page_slugs.add(slug)


# -----------------------------
# GENERATE PAGES (ALWAYS REBUILD)
# -----------------------------
generated_count = 0
error_count = 0
validation_error_count = 0

for page in pages:
    slug = page["slug"]
    keyword = page["keyword"]
    keyword_display = display_keyword(keyword)

    if slug in PROTECTED_SLUGS:
        print("Skipping protected page:", slug)
        continue

    folder = Path(OUTPUT_DIR) / slug
    path = folder / "index.html"
    folder.mkdir(parents=True, exist_ok=True)

    # 1. Call the risk engine (single call -- no retry loop; engine has no-failure contract)
    try:
        engine_result = call_engine(keyword)
        ai_text = engine_result["content"]
        engine_meta = engine_result["meta"] or {}
    except Exception as e:
        ai_failure_count += 1
        append_rejected_keyword(keyword, e)
        print("Risk engine call failed for", keyword, ":", e)
        continue

    if not is_usable_ai_text(ai_text):
        ai_failure_count += 1
        append_rejected_keyword(keyword, "engine returned thin/unusable content")
        print("Engine content unusable for", keyword)
        continue

    # 2. Meta: prefer engine output; fall back to Python builders if missing
    if engine_meta.get("title"):
        title = engine_meta["title"]
        engine_meta_used_count += 1
    else:
        title = build_title_python(keyword)
        python_meta_fallback_count += 1

    if engine_meta.get("description"):
        description = engine_meta["description"]
    else:
        description = build_description_python(keyword)

    h1 = engine_meta.get("h1") or readable_keyword(keyword) or keyword_display
    intro = engine_meta.get("intro") or ""
    content_heading = engine_meta.get("contentHeading") or ""
    content_bridge = engine_meta.get("contentBridge") or ""
    breadcrumb = engine_meta.get("breadcrumb") or readable_keyword(keyword)
    subject_display = engine_meta.get("subjectDisplay") or keyword_display
    subject_type = engine_meta.get("subjectType") or "generic"
    sub_intent = engine_meta.get("subIntent") or "general"
    canonical_pair = engine_meta.get("canonicalPair") or {}
    canonical_pair_address = canonical_pair.get("address") or ""

    canonical = build_canonical(slug)

    # 3. Related + more links + hub (Python-side; engine doesn't own these)
    related_pages = get_related_pages(page, pages, RELATED_LINKS_COUNT)
    related_slugs = {p["slug"] for p in related_pages}
    more_links_pages = get_more_links(page, pages, MORE_LINKS_COUNT, exclude_slugs=related_slugs)
    hub_link_html = build_hub_link_html(keyword)

    # 4. Validate
    validation_errors = validate_page_output(slug, title, description, canonical, related_pages)
    if validation_errors:
        validation_error_count += 1
        print("Validation warning for", slug, ":", "; ".join(validation_errors))

    # 5. Render link blocks
    links_html = "".join(
        f'<li><a href="/token-risk/{r["slug"]}/">{escape_html(build_related_anchor(r["keyword"]))}</a></li>\n'
        for r in related_pages
    )
    more_links_html = "".join(
        f'<li><a href="/token-risk/{r["slug"]}/">{escape_html(build_related_anchor(r["keyword"]))}</a></li>\n'
        for r in more_links_pages
    )

    # 6. Render content + engine-driven optional blocks
    ai_content_html = wrap_paragraphs(ai_text)
    threat_banner_html = render_threat_banner(engine_meta)
    contract_breakdown_html = render_contract_breakdown(engine_meta)
    faq_html = render_faq(engine_meta)
    faq_schema_html = render_faq_schema(engine_meta)

    # 7. Apply to template
    html = template
    # Required placeholders
    html = html.replace("{{TITLE}}", escape_html(title))
    html = html.replace("{{DESCRIPTION}}", escape_html(description))
    html = html.replace("{{KEYWORD}}", escape_html(keyword_display))
    html = html.replace("{{AI_CONTENT}}", ai_content_html)
    html = html.replace("{{RELATED_LINKS}}", links_html)
    html = html.replace("{{MORE_LINKS}}", more_links_html)
    html = html.replace("{{HUB_LINK}}", hub_link_html)
    html = html.replace("{{CANONICAL_URL}}", escape_html(canonical))

    # Optional placeholders (no-op if not in template)
    html = html.replace("{{H1}}", escape_html(h1))
    html = html.replace("{{INTRO}}", escape_html(intro))
    html = html.replace("{{CONTENT_HEADING}}", escape_html(content_heading))
    html = html.replace("{{CONTENT_BRIDGE}}", escape_html(content_bridge))
    html = html.replace("{{BREADCRUMB}}", escape_html(breadcrumb))
    html = html.replace("{{THREAT_BANNER}}", threat_banner_html)
    html = html.replace("{{CONTRACT_BREAKDOWN}}", contract_breakdown_html)
    html = html.replace("{{FAQ}}", faq_html)
    html = html.replace("{{FAQ_SCHEMA}}", faq_schema_html)
    html = html.replace("{{SUBJECT_DISPLAY}}", escape_html(subject_display))
    html = html.replace("{{SUBJECT_TYPE}}", escape_html(subject_type))
    html = html.replace("{{SUB_INTENT}}", escape_html(sub_intent))
    html = html.replace("{{CANONICAL_PAIR_ADDRESS}}", escape_html(canonical_pair_address))

    # Live data panel + robots gate. merge_live_fields fills {{LIVE_*}}
    # placeholders from enrichmentData (or '—' if absent) and sets {{ROBOTS}}
    # to noindex,follow only on explicit tier=none, default index otherwise.
    live_replacements = {}
    merge_live_fields(live_replacements, engine_result)
    for placeholder, value in live_replacements.items():
        html = html.replace(placeholder, str(value))

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        generated_count += 1
        print("Generated:", slug, "  (subjectType=", subject_type, "subIntent=", sub_intent + ")")
    except Exception as e:
        error_count += 1
        print("Error writing page for", slug, ":", e)

print("\n--- TOKEN RISK SEO BUILD REPORT ---")
print("Raw keywords loaded:", len(raw_keywords))
print("Canonical keywords used:", len(keywords))
print("Duplicate / fragmented keywords removed:", deduped_keywords_count)
print("Duplicate slug groups skipped:", skipped_duplicate_keywords_count)
print("Weak / low-value keywords skipped:", skipped_weak_keywords_count)
print("Pages generated:", generated_count)
print("Engine meta used:", engine_meta_used_count)
print("Python meta fallback used:", python_meta_fallback_count)
print("AI generations rejected:", ai_failure_count)
print("Rejected keywords logged:", rejected_count)
print("Validation warnings:", validation_error_count)
print("Write errors:", error_count)
