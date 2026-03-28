import os
import re
from generate_content import generate_content

KEYWORDS_FILE = "data/keywords.txt"
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


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def clean_base_keyword(text):
    kw = normalize_keyword(text)

    kw = re.sub(r"^\s*is\s+", "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+", "", kw)
    kw = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+(?:by|on|with)\s+", "", kw)
    kw = re.sub(r"^\s*this\s+", "this ", kw)

    kw = re.sub(r"\s+a\s+scam$", "", kw)
    kw = re.sub(r"\s+or\s+legit$", "", kw)
    kw = re.sub(r"\s+or\s+scam$", "", kw)
    kw = re.sub(r"\s+legit$", "", kw)
    kw = re.sub(r"\s+real$", "", kw)
    kw = re.sub(r"\s+safe$", "", kw)
    kw = re.sub(r"\s+scam$", "", kw)

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
    words = normalize_keyword(text).split()
    titled = [word.capitalize() for word in words]
    return apply_brand_case(" ".join(titled))


def keyword_tokens(text):
    return set(clean_base_keyword(text).split())


def keyword_cluster_tokens(text):
    return {token for token in keyword_tokens(text) if token in CLUSTER_TERMS}


def load_keywords():
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return list(dict.fromkeys([normalize_keyword(k) for k in f if k.strip()]))


def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()


def build_title(keyword):
    kw = title_case(display_keyword(keyword))
    return f"Is {kw} a Scam? (Real Check & Warning Signs)"


def build_description(keyword):
    clean_kw = display_keyword(keyword)
    keyword_title = title_case(clean_kw)
    return (
        f"Is {keyword_title} a scam or legit? Check real risk signals, warning signs, "
        f"and what to do next. Free AI scam checker for {clean_kw} messages, emails, or links."
    )


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def get_related_pages(current_page, all_pages, limit=RELATED_LINKS_COUNT):
    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_tokens = keyword_tokens(current_keyword)
    current_cluster = keyword_cluster_tokens(current_keyword)
    current_root = clean_base_keyword(current_keyword).split()[0] if clean_base_keyword(current_keyword) else ""

    valid_pages = [
        p for p in all_pages
        if p["slug"] != current_slug and p["slug"] not in PROTECTED_SLUGS
    ]

    def relevance_score(page):
        other_keyword = page["keyword"]
        other_tokens = keyword_tokens(other_keyword)
        other_cluster = keyword_cluster_tokens(other_keyword)
        other_root = clean_base_keyword(other_keyword).split()[0] if clean_base_keyword(other_keyword) else ""

        same_root = 1 if other_root == current_root and current_root else 0
        shared_cluster = len(current_cluster & other_cluster)
        shared_tokens = len(current_tokens & other_tokens)
        length_diff = abs(len(clean_base_keyword(other_keyword).split()) - len(clean_base_keyword(current_keyword).split()))

        return (-same_root, -shared_cluster, -shared_tokens, length_diff, other_keyword)

    ranked_pages = sorted(valid_pages, key=relevance_score)

    selected = []
    used_slugs = set()

    for page in ranked_pages:
        if page["slug"] in used_slugs:
            continue
        selected.append(page)
        used_slugs.add(page["slug"])
        if len(selected) == limit:
            break

    if len(selected) < limit:
        for page in valid_pages:
            if page["slug"] in used_slugs:
                continue
            selected.append(page)
            used_slugs.add(page["slug"])
            if len(selected) == limit:
                break

    return selected


def build_page(keyword, template, all_pages):
    slug = slugify(keyword)
    keyword_display = display_keyword(keyword)

    try:
        content = generate_content(keyword_display)
    except Exception:
        readable = title_case(keyword_display)
        content = (
            f"<p>{readable} scams are commonly used to trick people into sending money or sharing sensitive information. "
            f"If you receive a message related to {keyword_display}, avoid clicking unknown links, do not send payments, "
            f"and verify the source through official channels.</p>"
            f"<p>Scammers often create urgency, impersonate trusted brands, or ask you to confirm account details before you have time to stop and check what is happening.</p>"
            f"<p>The safest move is to verify independently through the official website or app before replying, logging in, sending money, or sharing personal information.</p>"
        )

    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    current_page = {"keyword": keyword, "slug": slug}
    related_pages = get_related_pages(current_page, all_pages, RELATED_LINKS_COUNT)

    related_links = "\n".join(
        f'<li><a href="/scam-check-now/{r["slug"]}/">Is {title_case(display_keyword(r["keyword"]))} a Scam?</a></li>'
        for r in related_pages
    )

    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword_display)
    html = html.replace("{{AI_CONTENT}}", content)
    html = html.replace("{{RELATED_LINKS}}", related_links)
    html = html.replace("{{CANONICAL_URL}}", canonical)

    return slug, html


def save_page(slug, html):
    folder = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "index.html")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    keywords = load_keywords()
    template = load_template()

    all_pages = [
        {"keyword": k, "slug": slugify(k)}
        for k in keywords
        if slugify(k) not in PROTECTED_SLUGS
    ]

    for keyword in keywords:
        slug = slugify(keyword)

        if slug in PROTECTED_SLUGS:
            print(f"skipped protected page: {keyword}")
            continue

        try:
            slug, html = build_page(keyword, template, all_pages)
            save_page(slug, html)
            print(f"generated page for: {keyword}")
        except Exception as e:
            print(f"error generating page for: {keyword}")
            print(e)


if __name__ == "__main__":
    main()