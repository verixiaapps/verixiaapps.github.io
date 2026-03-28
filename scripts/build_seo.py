import os
import re
from generate_content import generate_content

# -----------------------------
# CONFIG
# -----------------------------
KEYWORD_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"
OUTPUT_DIR = "scam-check-now"
SITE = "https://verixiaapps.com"
RELATED_LINKS_COUNT = 6

PROTECTED_SLUGS = {"is-this-a-scam"}

CLUSTER_TERMS = {
    "amazon", "paypal", "zelle", "cash", "venmo", "facebook", "instagram",
    "tiktok", "whatsapp", "telegram", "snapchat", "discord", "crypto",
    "bitcoin", "ethereum", "usps", "fedex", "ups", "bank", "chase",
    "wells", "america", "job", "loan", "credit", "romance", "gift",
    "irs", "social", "verification", "phishing", "login", "account"
}

BRAND_CASE = {
    "paypal": "PayPal",
    "whatsapp": "WhatsApp",
    "cash app": "Cash App",
    "tiktok": "TikTok",
    "icloud": "iCloud",
    "irs": "IRS",
    "usps": "USPS",
    "ups": "UPS",
    "fedex": "FedEx",
    "sms": "SMS",
    "otp": "OTP",
    "2fa": "2FA",
    "dm": "DM",
    "nft": "NFT",
    "ceo": "CEO",
    "binance": "Binance",
    "coinbase": "Coinbase",
    "metamask": "MetaMask",
    "trust wallet": "Trust Wallet",
    "google play": "Google Play",
    "cash": "Cash",
    "zelle": "Zelle",
    "venmo": "Venmo",
    "amazon": "Amazon",
    "facebook": "Facebook",
    "instagram": "Instagram",
    "telegram": "Telegram",
    "snapchat": "Snapchat",
    "discord": "Discord",
    "crypto": "Crypto",
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "bank": "Bank",
    "chase": "Chase",
    "wells fargo": "Wells Fargo",
    "social security": "Social Security",
    "google": "Google",
    "apple": "Apple",
    "microsoft": "Microsoft",
    "steam": "Steam",
    "walmart": "Walmart",
    "target": "Target",
}


# -----------------------------
# UTILITIES
# -----------------------------
def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def clean_base_keyword(text):
    kw = normalize_keyword(text)

    # Remove common question wrappers / duplicate phrasing
    kw = re.sub(r"^\s*is\s+", "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+", "", kw)
    kw = re.sub(r"^\s*this\s+", "this ", kw)
    kw = re.sub(r"\s+", " ", kw).strip()

    # Remove common trailing wrappers
    kw = re.sub(r"\s+a\s+scam$", "", kw)
    kw = re.sub(r"\s+scam$", "", kw)
    kw = re.sub(r"\s+legit$", "", kw)
    kw = re.sub(r"\s+or\s+legit$", "", kw)
    kw = re.sub(r"\s+or\s+scam$", "", kw)
    kw = re.sub(r"\s+real$", "", kw)
    kw = re.sub(r"\s+safe$", "", kw)

    # Clean common malformed leftovers
    kw = re.sub(r"\s+a$", "", kw)
    kw = re.sub(r"\s+", " ", kw).strip()

    return kw


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

    small_words = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "vs", "with"}
    words = text.split()
    titled = []

    for i, word in enumerate(words):
        lower = word.lower()
        if i > 0 and lower in small_words:
            titled.append(lower)
        else:
            titled.append(lower.capitalize())

    return apply_brand_case(" ".join(titled))


def build_title(keyword):
    kw = title_case(display_keyword(keyword))
    return f"Is {kw} a Scam? (Real Check & Warning Signs)"


def build_description(keyword):
    clean_kw = display_keyword(keyword)
    keyword_title = title_case(clean_kw)
    return (
        f"Is {keyword_title} a scam or legit? Check warning signs, real risks, "
        f"and what to do next. Free AI scam checker for {clean_kw}."
    )


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def load_keywords():
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys([normalize_keyword(k) for k in f if k.strip()]))


def keyword_tokens(text):
    return set(clean_base_keyword(text).split())


def keyword_cluster_tokens(text):
    return {token for token in keyword_tokens(text) if token in CLUSTER_TERMS}


def get_related_pages(current_page, all_pages, limit):
    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_tokens = keyword_tokens(current_keyword)
    current_cluster_tokens = keyword_cluster_tokens(current_keyword)
    current_root = current_keyword.split()[0]

    candidates = [
        p for p in all_pages
        if p["slug"] != current_slug and p["slug"] not in PROTECTED_SLUGS
    ]

    def score(page):
        other_keyword = page["keyword"]
        other_tokens = keyword_tokens(other_keyword)
        other_cluster_tokens = keyword_cluster_tokens(other_keyword)

        same_root = 1 if other_keyword.split()[0] == current_root else 0
        shared_cluster = len(current_cluster_tokens & other_cluster_tokens)
        shared_tokens = len(current_tokens & other_tokens)
        length_diff = abs(len(other_keyword.split()) - len(current_keyword.split()))

        return (
            -same_root,
            -shared_cluster,
            -shared_tokens,
            length_diff,
            other_keyword
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


# -----------------------------
# SETUP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

keywords = load_keywords()
pages = [
    {"keyword": k, "slug": slugify(k)}
    for k in keywords
    if slugify(k) not in PROTECTED_SLUGS
]


# -----------------------------
# GENERATE PAGES (ALWAYS REBUILD)
# -----------------------------
for page in pages:
    slug = page["slug"]
    keyword = page["keyword"]
    keyword_display = display_keyword(keyword)

    if slug in PROTECTED_SLUGS:
        print("Skipping protected page:", slug)
        continue

    folder = f"{OUTPUT_DIR}/{slug}"
    path = f"{folder}/index.html"
    os.makedirs(folder, exist_ok=True)

    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    try:
        ai_text = generate_content(keyword_display)
    except Exception as e:
        print("AI generation failed for", keyword, ":", e)
        ai_text = f"""
<p>{title_case(keyword_display)} scams often involve requests for money, personal information, or urgent action. Avoid clicking unknown links or sending funds. Always verify through official sources.</p>
""".strip()

    related_pages = get_related_pages(page, pages, RELATED_LINKS_COUNT)

    links_html = "".join(
        f'<li><a href="/scam-check-now/{r["slug"]}/">Is {title_case(display_keyword(r["keyword"]))} a Scam?</a></li>\n'
        for r in related_pages
    )

    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword_display)
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links_html)
    html = html.replace("{{CANONICAL_URL}}", canonical)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Generated:", slug)