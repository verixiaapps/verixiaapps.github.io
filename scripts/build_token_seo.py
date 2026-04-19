import os
import re
from html import escape

from generate_token_content import generate_token_content

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

rejected_count = 0
deduped_keywords_count = 0
skipped_duplicate_keywords_count = 0
skipped_weak_keywords_count = 0
ai_failure_count = 0


# -----------------------------
# UTILITIES
# -----------------------------
def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


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


def build_title(keyword):
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


def build_description(keyword):
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


def validate_template_placeholders(template_html):
    missing = [placeholder for placeholder in REQUIRED_TEMPLATE_PLACEHOLDERS if placeholder not in template_html]
    if missing:
        raise ValueError("Template is missing required placeholders: " + ", ".join(sorted(missing)))


def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys(normalize_keyword(k) for k in f if k.strip()))


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
    return "token-risk-hub"


def build_hub_link_html(keyword):
    hub_slug = find_best_hub_slug(keyword)
    hub_title = HUB_TITLE_OVERRIDES.get(hub_slug, f"{title_case(hub_slug.replace('-', ' '))} Hub")
    return f'<a href="/token-risk/{hub_slug}/">{escape_html(hub_title)}</a>'


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
    seen = set()

    for _, group in groups.items():
        chosen = choose_canonical_keyword(group)
        chosen_slug = canonical_slug(chosen)

        if chosen_slug in PROTECTED_SLUGS:
            continue

        if is_weak_keyword(chosen):
            skipped_weak_keywords_count += len(group)
            continue

        if chosen_slug in seen:
            skipped_duplicate_keywords_count += len(group)
            continue

        canonical_keywords.append(chosen)
        seen.add(chosen_slug)

        if len(group) > 1:
            deduped_keywords_count += len(group) - 1

    return canonical_keywords


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

    return f"{readable} Token Risk"


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
        "i’m sorry",
        "i am sorry",
        "cannot assist",
        "can't assist",
        "policy",
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


def generate_ai_text(keyword, keyword_display):
    attempts = []
    raw_keyword = normalize_keyword(keyword)
    clean_keyword = normalize_keyword(keyword_display)

    if raw_keyword:
        attempts.append(raw_keyword)

    if clean_keyword and clean_keyword != raw_keyword:
        attempts.append(clean_keyword)

    readable = readable_keyword(keyword_display)
    if readable:
        attempts.append(readable)

    if clean_keyword:
        attempts.append(f"{clean_keyword} token risk")

    if clean_keyword and not raw_keyword.startswith("is "):
        attempts.append(f"is {clean_keyword} safe")

    if clean_keyword and not contains_term_phrase(raw_keyword, "buy"):
        attempts.append(f"should i buy {clean_keyword}")

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
            ai_text = generate_token_content(attempt)
            if is_usable_ai_text(ai_text):
                return ai_text
            last_error = f"thin or malformed output for prompt: {attempt}"
        except Exception as e:
            last_error = str(e)

    raise ValueError(last_error or "AI generation failed")


# -----------------------------
# SETUP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(REJECTED_KEYWORDS_FILE)

template = load_template()
raw_keywords = load_keywords()
keywords = dedupe_keywords(raw_keywords)

pages = [
    {"keyword": k, "slug": canonical_slug(k)}
    for k in keywords
    if canonical_slug(k) not in PROTECTED_SLUGS
]


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

    folder = os.path.join(OUTPUT_DIR, slug)
    path = os.path.join(folder, "index.html")
    os.makedirs(folder, exist_ok=True)

    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    try:
        ai_text = generate_ai_text(keyword, keyword_display)
    except Exception as e:
        ai_failure_count += 1
        append_rejected_keyword(keyword, e)
        print("AI generation rejected for", keyword, ":", e)
        continue

    related_pages = get_related_pages(page, pages, RELATED_LINKS_COUNT)
    related_slugs = {p["slug"] for p in related_pages}

    more_links_pages = get_more_links(
        page,
        pages,
        MORE_LINKS_COUNT,
        exclude_slugs=related_slugs,
    )

    hub_link_html = build_hub_link_html(keyword)

    validation_errors = validate_page_output(slug, title, description, canonical, related_pages)
    if validation_errors:
        validation_error_count += 1
        print("Validation warning for", slug, ":", "; ".join(validation_errors))

    links_html = "".join(
        f'<li><a href="/token-risk/{r["slug"]}/">{escape_html(build_related_anchor(r["keyword"]))}</a></li>\n'
        for r in related_pages
    )

    more_links_html = "".join(
        f'<li><a href="/token-risk/{r["slug"]}/">{escape_html(build_related_anchor(r["keyword"]))}</a></li>\n'
        for r in more_links_pages
    )

    html = template
    html = html.replace("{{TITLE}}", escape_html(title))
    html = html.replace("{{DESCRIPTION}}", escape_html(description))
    html = html.replace("{{KEYWORD}}", escape_html(keyword_display))
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links_html)
    html = html.replace("{{MORE_LINKS}}", more_links_html)
    html = html.replace("{{HUB_LINK}}", hub_link_html)
    html = html.replace("{{CANONICAL_URL}}", escape_html(canonical))

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        generated_count += 1
        print("Generated:", slug)
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
print("AI generations rejected:", ai_failure_count)
print("Rejected keywords logged:", rejected_count)
print("Validation warnings:", validation_error_count)
print("Write errors:", error_count)