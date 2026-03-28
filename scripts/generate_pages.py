import os
import re
from html import escape
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
    "irs", "social", "verification", "phishing", "login", "account",
    "delivery", "package", "recruiter", "refund", "payment", "wallet"
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
    "facebook marketplace": "Facebook Marketplace",
    "instagram": "Instagram",
    "telegram": "Telegram",
    "snapchat": "Snapchat",
    "discord": "Discord",
    "crypto": "Crypto",
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "bank": "Bank",
    "bank of america": "Bank of America",
    "chase": "Chase",
    "wells fargo": "Wells Fargo",
    "social security": "Social Security",
    "google": "Google",
    "apple": "Apple",
    "microsoft": "Microsoft",
    "steam": "Steam",
    "walmart": "Walmart",
    "target": "Target",
    "two factor": "Two-Factor",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "vs", "with"
}


def slugify(text):
    text = normalize_keyword(text)
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
    text = normalize_keyword(text)
    if not text:
        return ""

    words = text.split()
    titled = []

    for i, word in enumerate(words):
        if i > 0 and word in SMALL_WORDS:
            titled.append(word)
        else:
            titled.append(word.capitalize())

    return apply_brand_case(" ".join(titled))


def keyword_tokens(text):
    return set(clean_base_keyword(text).split())


def keyword_cluster_tokens(text):
    return {token for token in keyword_tokens(text) if token in CLUSTER_TERMS}


def keyword_root(text):
    base = clean_base_keyword(text)
    return base.split()[0] if base else ""


def is_guidance_style_keyword(keyword):
    kw = normalize_keyword(keyword)
    return (
        kw.startswith("how to ")
        or kw.startswith("what to do")
        or kw.startswith("what happens")
        or kw.startswith("why ")
        or kw.startswith("when ")
        or kw.startswith("where ")
        or kw.startswith("who ")
        or kw.startswith("check ")
        or kw.startswith("report ")
    )


def is_question_style_keyword(keyword):
    kw = normalize_keyword(keyword)
    return kw.startswith(("is ", "can ", "did ", "should ", "was ", "could ", "would ", "do ", "does "))


def readable_keyword(text):
    base = display_keyword(text)
    return title_case(base) if base else ""


def load_keywords():
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return list(dict.fromkeys([normalize_keyword(k) for k in f if k.strip()]))


def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()


def build_title(keyword):
    raw = normalize_keyword(keyword)
    readable = readable_keyword(keyword)

    if not raw:
        return "Is This a Scam? Warning Signs, Safety Tips & What To Do"

    if is_guidance_style_keyword(raw):
        return f"{title_case(raw)} | Warning Signs, Safety Tips & What To Do"

    if raw.startswith("did i get scammed"):
        return f"{title_case(raw)}? Signs, Risks & What To Do Next"

    if raw.startswith("is this "):
        return f"{title_case(raw)}? Warning Signs, Risks & What To Do"

    if raw.startswith("is ") and " legit" in raw:
        cleaned = re.sub(r"\s+legit\b", "", raw).strip()
        return f"{title_case(cleaned)} Legit or a Scam? Warning Signs & What To Do"

    if is_question_style_keyword(raw):
        return f"{title_case(raw)}? Warning Signs, Risks & What To Know"

    return f"Is {readable} a Scam? Warning Signs, Risks & What To Do"


def build_description(keyword):
    raw = normalize_keyword(keyword)
    clean_kw = display_keyword(keyword)
    readable = readable_keyword(keyword)

    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        return (
            f"Learn the warning signs, scam risk signals, and safest next steps for {readable}. "
            f"Check suspicious messages, emails, links, and offers before you click, reply, or send money."
        )

    return (
        f"Is {readable} a scam or legit? Review warning signs, risk signals, and what to do next. "
        f"Check suspicious {clean_kw} messages, emails, texts, links, and offers."
    )


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def build_related_label(keyword):
    raw = normalize_keyword(keyword)
    readable = readable_keyword(keyword)

    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        return title_case(raw)

    return f"Is {readable} a Scam?"


def get_related_pages(current_page, all_pages, limit=RELATED_LINKS_COUNT):
    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_tokens = keyword_tokens(current_keyword)
    current_cluster = keyword_cluster_tokens(current_keyword)
    current_root = keyword_root(current_keyword)
    current_base = clean_base_keyword(current_keyword)

    valid_pages = [
        p for p in all_pages
        if p["slug"] != current_slug
        and p["slug"] not in PROTECTED_SLUGS
        and clean_base_keyword(p["keyword"]) != current_base
    ]

    def relevance_score(page):
        other_keyword = page["keyword"]
        other_tokens = keyword_tokens(other_keyword)
        other_cluster = keyword_cluster_tokens(other_keyword)
        other_root = keyword_root(other_keyword)
        other_base = clean_base_keyword(other_keyword)

        same_root = 1 if current_root and other_root == current_root else 0
        shared_cluster = len(current_cluster & other_cluster)
        shared_tokens = len(current_tokens & other_tokens)
        exact_base_penalty = 1 if other_base == current_base else 0
        length_diff = abs(len(other_tokens) - len(current_tokens))

        return (
            -exact_base_penalty,
            -same_root,
            -shared_cluster,
            -shared_tokens,
            length_diff,
            other_keyword,
        )

    ranked_pages = sorted(valid_pages, key=relevance_score)

    selected = []
    used_slugs = set()
    used_bases = set()

    for page in ranked_pages:
        base = clean_base_keyword(page["keyword"])
        if page["slug"] in used_slugs or base in used_bases:
            continue
        selected.append(page)
        used_slugs.add(page["slug"])
        used_bases.add(base)
        if len(selected) == limit:
            break

    if len(selected) < limit:
        for page in valid_pages:
            base = clean_base_keyword(page["keyword"])
            if page["slug"] in used_slugs or base in used_bases:
                continue
            selected.append(page)
            used_slugs.add(page["slug"])
            used_bases.add(base)
            if len(selected) == limit:
                break

    return selected


def build_page(keyword, template, all_pages):
    slug = slugify(keyword)
    keyword_display = display_keyword(keyword)

    try:
        content = generate_content(keyword_display)
    except Exception:
        readable = readable_keyword(keyword_display)
        content = (
            f"<p>{readable} scams are commonly used to trick people into sending money or sharing sensitive information. "
            f"If you receive a message related to {escape(keyword_display)}, avoid clicking unknown links, do not send payments, "
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
        f'<li><a href="/scam-check-now/{r["slug"]}/">{escape(build_related_label(r["keyword"]))}</a></li>'
        for r in related_pages
    )

    html = template
    html = html.replace("{{TITLE}}", escape(title))
    html = html.replace("{{DESCRIPTION}}", escape(description))
    html = html.replace("{{KEYWORD}}", escape(keyword_display))
    html = html.replace("{{AI_CONTENT}}", content)
    html = html.replace("{{RELATED_LINKS}}", related_links)
    html = html.replace("{{CANONICAL_URL}}", escape(canonical))

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