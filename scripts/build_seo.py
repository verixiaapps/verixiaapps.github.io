import os
import re
from collections import defaultdict
from generate_content import generate_content

# -----------------------------
# CONFIG
# -----------------------------
KEYWORD_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"
OUTPUT_DIR = "scam-check-now"
SITE = "https://verixiaapps.com"
RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT = 8

PROTECTED_SLUGS = {"is-this-a-scam"}

CLUSTER_TERMS = {
    "amazon", "paypal", "zelle", "cash", "venmo", "facebook", "instagram",
    "tiktok", "whatsapp", "telegram", "snapchat", "discord", "crypto",
    "bitcoin", "ethereum", "usps", "fedex", "ups", "bank", "chase",
    "wells", "america", "job", "loan", "credit", "romance", "gift",
    "irs", "social", "verification", "phishing", "login", "account"
}

HUB_SLUG_MAP = {
    "amazon": "amazon-scams",
    "paypal": "paypal-scams",
    "zelle": "zelle-scams",
    "cash": "cash-app-scams",
    "venmo": "venmo-scams",
    "facebook": "facebook-scams",
    "instagram": "instagram-scams",
    "tiktok": "tiktok-scams",
    "whatsapp": "whatsapp-scams",
    "telegram": "telegram-scams",
    "snapchat": "snapchat-scams",
    "discord": "discord-scams",
    "crypto": "crypto-scams",
    "bitcoin": "crypto-scams",
    "ethereum": "crypto-scams",
    "usps": "package-delivery-scams",
    "fedex": "package-delivery-scams",
    "ups": "package-delivery-scams",
    "bank": "bank-scams",
    "chase": "bank-scams",
    "wells": "bank-scams",
    "job": "job-scams",
    "loan": "loan-scams",
    "credit": "credit-scams",
    "romance": "romance-scams",
    "gift": "gift-card-scams",
    "irs": "government-scams",
    "social": "government-scams",
    "verification": "verification-code-scams",
    "phishing": "phishing-scams",
    "login": "phishing-scams",
    "account": "phishing-scams",
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

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with"
}

HIGH_INTENT_TERMS = {
    "scam", "legit", "safe", "review", "warning", "risk", "phishing",
    "verification", "refund", "payment", "invoice", "login", "alert",
    "email", "text", "message", "job", "offer", "support", "transfer"
}

LOW_VALUE_SINGLE_TERMS = {
    "scam", "message", "email", "text", "alert", "warning", "request",
    "offer", "payment", "login", "verification"
}

TITLE_PATTERNS = (
    "Is {kw} a Scam or Legit? (Full 2026 Check)",
    "{kw} Scam? Warning Signs, Risks & What to Do",
    "Is {kw} Safe? Scam Check + Red Flags",
    "{kw} Review: Scam or Legit? (Updated 2026)",
)

DESCRIPTION_PATTERNS = (
    "Think {kw} might be a scam? Check warning signs, real risks, and what to do next. Free instant scam check.",
    "Is {kw} legit or a scam? Review red flags, scam patterns, and safe next steps with our free AI scam checker.",
    "Check whether {kw} looks suspicious. See common scam signs, real risks, and what to do before you click or reply.",
    "Worried about {kw}? Learn the warning signs, risk signals, and safest next steps with a free scam check.",
)

fallback_count = 0
deduped_keywords_count = 0
skipped_duplicate_keywords_count = 0
skipped_weak_keywords_count = 0


# -----------------------------
# UTILITIES
# -----------------------------
def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def slugify(text):
    text = normalize_keyword(text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def stable_index(text, count):
    if count <= 0:
        return 0
    return sum(ord(c) for c in normalize_keyword(text)) % count


def clean_base_keyword(text):
    kw = normalize_keyword(text)

    # Remove common question wrappers / duplicate phrasing
    kw = re.sub(r"^\s*is\s+", "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+", "", kw)
    kw = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+(?:by|on|with)\s+", "", kw)
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


def build_title(keyword):
    kw = title_case(display_keyword(keyword))
    pattern = TITLE_PATTERNS[stable_index(keyword, len(TITLE_PATTERNS))]
    return pattern.format(kw=kw)


def build_description(keyword):
    clean_kw = title_case(display_keyword(keyword))
    pattern = DESCRIPTION_PATTERNS[stable_index(keyword, len(DESCRIPTION_PATTERNS))]
    return pattern.format(kw=clean_kw)


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def load_keywords():
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys([normalize_keyword(k) for k in f if k.strip()]))


def keyword_tokens(text):
    return set(canonical_keyword(text).split())


def keyword_cluster_tokens(text):
    return {token for token in keyword_tokens(text) if token in CLUSTER_TERMS}


def keyword_root(text):
    cleaned = canonical_keyword(text)
    return cleaned.split()[0] if cleaned else ""


def get_hub_slug(keyword):
    root = keyword_root(keyword)
    return HUB_SLUG_MAP.get(root, "")


def build_hub_link_html(keyword):
    hub_slug = get_hub_slug(keyword)
    if not hub_slug:
        return ""

    root = keyword_root(keyword)
    hub_label = title_case(root.replace("-", " "))
    if not hub_label:
        hub_label = "Scam"

    hub_title_map = {
        "amazon": "Amazon Scam Hub",
        "paypal": "PayPal Scam Hub",
        "zelle": "Zelle Scam Hub",
        "cash": "Cash App Scam Hub",
        "venmo": "Venmo Scam Hub",
        "facebook": "Facebook Scam Hub",
        "instagram": "Instagram Scam Hub",
        "tiktok": "TikTok Scam Hub",
        "whatsapp": "WhatsApp Scam Hub",
        "telegram": "Telegram Scam Hub",
        "snapchat": "Snapchat Scam Hub",
        "discord": "Discord Scam Hub",
        "crypto": "Crypto Scam Hub",
        "bitcoin": "Crypto Scam Hub",
        "ethereum": "Crypto Scam Hub",
        "usps": "Package Delivery Scam Hub",
        "fedex": "Package Delivery Scam Hub",
        "ups": "Package Delivery Scam Hub",
        "bank": "Bank Scam Hub",
        "chase": "Bank Scam Hub",
        "wells": "Bank Scam Hub",
        "job": "Job Scam Hub",
        "loan": "Loan Scam Hub",
        "credit": "Credit Scam Hub",
        "romance": "Romance Scam Hub",
        "gift": "Gift Card Scam Hub",
        "irs": "Government Scam Hub",
        "social": "Government Scam Hub",
        "verification": "Verification Code Scam Hub",
        "phishing": "Phishing Scam Hub",
        "login": "Phishing Scam Hub",
        "account": "Phishing Scam Hub",
    }

    hub_title = hub_title_map.get(root, f"{hub_label} Scam Hub")

    return (
        f'<a class="hub-link-card" href="/scam-check-now/{hub_slug}/">'
        f'<span class="hub-link-label">Related scam category</span>'
        f'<span class="hub-link-title">{hub_title}</span>'
        f'</a>'
    )


def is_weak_keyword(keyword):
    tokens = canonical_keyword(keyword).split()
    if len(tokens) < 2:
        return True

    if len(tokens) == 2 and all(token in LOW_VALUE_SINGLE_TERMS for token in tokens):
        return True

    if not any(token in HIGH_INTENT_TERMS or token in CLUSTER_TERMS for token in tokens):
        return True

    return False


def keyword_quality_score(keyword):
    kw = normalize_keyword(keyword)
    score = 0

    if kw.endswith(" scam"):
        score += 20
    if " scam " in f" {kw} ":
        score += 10
    if "legit" in kw:
        score += 9
    if "review" in kw:
        score += 7
    if "safe" in kw:
        score += 6
    if any(term in kw for term in ["warning", "risk", "phishing", "verification", "refund", "payment", "invoice", "login", "alert"]):
        score += 6

    if " or legit" in kw:
        score -= 6
    if kw.startswith("is "):
        score -= 8
    if kw.startswith("can i trust "):
        score -= 10
    if kw.startswith("did i get scammed "):
        score -= 12
    if kw.startswith("this "):
        score -= 4

    score -= len(kw) / 100.0
    return score


def choose_canonical_keyword(keywords_for_same_intent):
    return sorted(
        keywords_for_same_intent,
        key=lambda k: (-keyword_quality_score(k), len(k), k)
    )[0]


def dedupe_keywords(raw_keywords):
    global deduped_keywords_count, skipped_duplicate_keywords_count, skipped_weak_keywords_count

    groups = defaultdict(list)
    for keyword in raw_keywords:
        groups[canonical_keyword(keyword)].append(keyword)

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
    current_cluster_tokens = keyword_cluster_tokens(current_keyword)
    current_root = keyword_root(current_keyword)
    current_hub_slug = get_hub_slug(current_keyword)

    candidates = [
        p for p in all_pages
        if p["slug"] != current_slug and p["slug"] not in PROTECTED_SLUGS
    ]

    def score(page):
        other_keyword = page["keyword"]
        other_tokens = keyword_tokens(other_keyword)
        other_cluster_tokens = keyword_cluster_tokens(other_keyword)
        other_root = keyword_root(other_keyword)
        other_hub_slug = get_hub_slug(other_keyword)

        same_hub = 1 if current_hub_slug and other_hub_slug == current_hub_slug else 0
        same_root = 1 if other_root == current_root and current_root else 0
        shared_cluster = len(current_cluster_tokens & other_cluster_tokens)
        shared_tokens = len(current_tokens & other_tokens)
        length_diff = abs(len(other_keyword.split()) - len(current_keyword.split()))

        return (
            -same_hub,
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


def get_more_links(current_page, all_pages, limit):
    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_hub_slug = get_hub_slug(current_keyword)

    if current_hub_slug:
        same_hub_pages = [
            p for p in all_pages
            if p["slug"] != current_slug and get_hub_slug(p["keyword"]) == current_hub_slug
        ]
    else:
        same_hub_pages = []

    fallback_pages = [
        p for p in all_pages
        if p["slug"] != current_slug and p not in same_hub_pages
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

    if "is is " in title.lower():
        errors.append("title contains 'Is Is'")

    if " a a " in title.lower():
        errors.append("title contains duplicated article")

    if not canonical.endswith(f"/{slug}/"):
        errors.append("canonical mismatch")

    if len(related_pages) == 0:
        errors.append("no related pages")

    if len(title) < 35 or len(title) > 72:
        errors.append("title length out of target range")

    if len(description) < 110 or len(description) > 165:
        errors.append("description length out of target range")

    return errors


# -----------------------------
# SETUP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

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

    folder = f"{OUTPUT_DIR}/{slug}"
    path = f"{folder}/index.html"
    os.makedirs(folder, exist_ok=True)

    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    try:
        ai_text = generate_content(keyword_display)
    except Exception as e:
        fallback_count += 1
        print("AI generation failed for", keyword, ":", e)
        ai_text = f"""
<p>{title_case(keyword_display)} scams often involve requests for money, personal information, or urgent action. Avoid clicking unknown links or sending funds. Always verify through official sources.</p>
<p>Scammers often create urgency, impersonate trusted brands, or ask you to confirm account details before you have time to stop and check what is happening.</p>
<p>The safest move is to verify independently through the official website or app before replying, logging in, sending money, or sharing personal information.</p>
""".strip()

    related_pages = get_related_pages(page, pages, RELATED_LINKS_COUNT)
    more_links_pages = get_more_links(page, pages, MORE_LINKS_COUNT)
    hub_link_html = build_hub_link_html(keyword)

    validation_errors = validate_page_output(slug, title, description, canonical, related_pages)
    if validation_errors:
        validation_error_count += 1
        print("Validation warning for", slug, ":", "; ".join(validation_errors))

    links_html = "".join(
        f'<li><a href="/scam-check-now/{r["slug"]}/">Is {title_case(display_keyword(r["keyword"]))} a Scam?</a></li>\n'
        for r in related_pages
    )

    more_links_html = "".join(
        f'<li><a href="/scam-check-now/{r["slug"]}/">{title_case(display_keyword(r["keyword"]))} Scam Check</a></li>\n'
        for r in more_links_pages
    )

    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword_display)
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links_html)
    html = html.replace("{{CANONICAL_URL}}", canonical)
    html = html.replace("{{HUB_LINK}}", hub_link_html)
    html = html.replace("{{MORE_LINKS}}", more_links_html)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        generated_count += 1
        print("Generated:", slug)
    except Exception as e:
        error_count += 1
        print("Error writing page for", slug, ":", e)

print("\n--- SEO BUILD REPORT ---")
print("Raw keywords loaded:", len(raw_keywords))
print("Canonical keywords used:", len(keywords))
print("Duplicate / fragmented keywords removed:", deduped_keywords_count)
print("Duplicate slug groups skipped:", skipped_duplicate_keywords_count)
print("Weak / low-value keywords skipped:", skipped_weak_keywords_count)
print("Pages generated:", generated_count)
print("Fallback content used:", fallback_count)
print("Validation warnings:", validation_error_count)
print("Write errors:", error_count)