import os
import re
import sys
from html import escape

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from generate_content import generate_content
from data.cluster_map import CLUSTERS

# -----------------------------
# CONFIG
# -----------------------------
KEYWORD_FILE = os.path.join(BASE_DIR, "data", "keywords.txt")
GENERATED_SLUGS_FILE = os.path.join(BASE_DIR, "data", "generated_slugs.txt")
GENERATED_KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "generated_keywords.txt")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "seo-template.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "scam-check-now")
SITE = "https://verixiaapps.com"

RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT = 10
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "100"))

PROTECTED_SLUGS = {"is-this-a-scam"}

CLUSTER_TERMS = {
    "amazon", "paypal", "zelle", "cash", "venmo", "facebook", "instagram",
    "tiktok", "whatsapp", "telegram", "snapchat", "discord", "crypto",
    "bitcoin", "ethereum", "usps", "fedex", "ups", "bank", "chase",
    "wells", "america", "job", "loan", "credit", "romance", "gift",
    "irs", "social", "verification", "phishing", "login", "account",
    "delivery", "package", "recruiter", "refund", "payment", "wallet",
    "support", "number", "caller", "security", "alert"
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


# -----------------------------
# UTILITIES
# -----------------------------
def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def slugify(text):
    text = normalize_keyword(text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


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


def readable_keyword(text):
    base = display_keyword(text)
    return title_case(base) if base else ""


def keyword_tokens(text):
    return set(clean_base_keyword(text).split())


def keyword_cluster_tokens(text):
    return {token for token in keyword_tokens(text) if token in CLUSTER_TERMS}


def keyword_root(text):
    base = clean_base_keyword(text)
    return base.split()[0] if base else ""


def escape_html(text):
    return escape(str(text), quote=True)


def page_path(slug):
    return os.path.join(OUTPUT_DIR, slug, "index.html")


def page_exists(slug):
    return os.path.exists(page_path(slug))


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


# -----------------------------
# SEO TEXT HELPERS
# -----------------------------
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


def build_related_anchor(keyword):
    raw = normalize_keyword(keyword)
    readable = readable_keyword(keyword)

    if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
        if raw.startswith("is ") and " legit" in raw:
            cleaned = re.sub(r"\s+legit\b", "", raw).strip()
            return f"{title_case(cleaned)} Legit or a Scam?"
        if raw.startswith("did i get scammed") or raw.startswith("what happens after ") or raw.startswith("almost "):
            return title_case(raw) + "?"
        return title_case(raw)

    return f"Is {readable} a Scam?"


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def fallback_ai_text(keyword):
    readable = readable_keyword(keyword)
    keyword_display = display_keyword(keyword)
    return (
        f"<p>{readable} scams often involve impersonation, urgency, or requests for money and sensitive information.</p>"
        f"<p>Common warning signs include unexpected messages, pressure to act quickly, suspicious links, and unusual payment requests.</p>"
        f"<p>If you receive something related to {escape_html(keyword_display)}, avoid clicking links, replying, or sending money until you verify it through official sources.</p>"
    )


# -----------------------------
# FILE LOADERS
# -----------------------------
def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys(normalize_keyword(k) for k in f if k.strip()))


def load_generated_slugs():
    if not os.path.exists(GENERATED_SLUGS_FILE):
        return set()
    with open(GENERATED_SLUGS_FILE, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def load_generated_keywords():
    if not os.path.exists(GENERATED_KEYWORDS_FILE):
        return set()
    with open(GENERATED_KEYWORDS_FILE, encoding="utf-8") as f:
        return {normalize_keyword(line) for line in f if line.strip()}


def append_line_if_missing(filepath, value):
    value = value.strip()
    if not value:
        return

    existing = set()
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            existing = {line.strip() for line in f if line.strip()}

    if value not in existing:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(value + "\n")


# -----------------------------
# LINKING HELPERS
# -----------------------------
def dedupe_pages_by_slug(pages_list):
    deduped = []
    seen = set()

    for page in pages_list:
        slug = page["slug"]
        if not slug or slug in seen or slug in PROTECTED_SLUGS:
            continue
        seen.add(slug)
        deduped.append(page)

    return deduped


def get_related_pages(current_page, all_pages, limit, exclude_slugs=None):
    exclude_slugs = set(exclude_slugs or set())

    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_tokens = keyword_tokens(current_keyword)
    current_cluster = keyword_cluster_tokens(current_keyword)
    current_root = keyword_root(current_keyword)
    current_base = clean_base_keyword(current_keyword)

    candidates = [
        p for p in all_pages
        if p["slug"] != current_slug
        and p["slug"] not in PROTECTED_SLUGS
        and p["slug"] not in exclude_slugs
        and page_exists(p["slug"])
        and clean_base_keyword(p["keyword"]) != current_base
    ]

    def score(page):
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
            other_keyword
        )

    ranked = sorted(candidates, key=score)

    related = []
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


def find_best_hub_slug(keyword):
    keyword_norm = normalize_keyword(keyword)

    best_hub_slug = None
    best_score = 0

    for hub_slug, match_terms in CLUSTERS.items():
        score = 0
        for term in match_terms:
            term_norm = normalize_keyword(term)
            if term_norm and term_norm in keyword_norm:
                score += 1

        if score > best_score:
            best_score = score
            best_hub_slug = hub_slug

    return best_hub_slug


def build_hub_link_html(keyword):
    hub_slug = find_best_hub_slug(keyword)
    if not hub_slug or not page_exists(hub_slug):
        return ""

    hub_title = title_case(hub_slug.replace("-", " "))
    return (
        f'<a class="hub-link-card" href="/scam-check-now/{hub_slug}/">'
        f'<span class="hub-link-label">Scam Hub</span>'
        f'<span class="hub-link-title">Browse the {escape_html(hub_title)} Hub</span>'
        f'</a>'
    )


def build_links_html(pages_list):
    return "".join(
        f'<li><a href="/scam-check-now/{p["slug"]}/">{escape_html(build_related_anchor(p["keyword"]))}</a></li>\n'
        for p in pages_list
        if page_exists(p["slug"])
    )


# -----------------------------
# SETUP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

for required_file in [GENERATED_SLUGS_FILE, GENERATED_KEYWORDS_FILE]:
    if not os.path.exists(required_file):
        open(required_file, "a", encoding="utf-8").close()

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

keywords = load_keywords()
generated_slugs = load_generated_slugs()
generated_keywords = load_generated_keywords()

seen_queue_slugs = set()
queue_pages = []
duplicate_queue_count = 0

for k in keywords:
    slug = slugify(k)
    if slug in PROTECTED_SLUGS:
        continue
    if slug in seen_queue_slugs:
        duplicate_queue_count += 1
        continue
    seen_queue_slugs.add(slug)
    queue_pages.append({"keyword": k, "slug": slug})

existing_pages = []
existing_seen_slugs = set()

for keyword in generated_keywords:
    slug = slugify(keyword)
    if slug in PROTECTED_SLUGS or slug in existing_seen_slugs:
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
queue_pages = dedupe_pages_by_slug(queue_pages)

print(f"Loaded {len(keywords)} keywords from queue.")
print(f"Unique queued pages after slug dedupe: {len(queue_pages)}")
print(f"Duplicate queued keywords skipped: {duplicate_queue_count}")
print(f"Known generated slugs: {len(generated_slugs)}")
print(f"Known generated keywords: {len(generated_keywords)}")
print(f"Existing pages available for internal links: {len(existing_pages)}")
print(f"Daily limit: {DAILY_LIMIT}")


# -----------------------------
# GENERATE PAGES (INCREMENTAL ONLY)
# -----------------------------
generated_count = 0
skipped_existing_count = 0
skipped_known_slug_count = 0
skipped_known_keyword_count = 0
built_keywords = []

for page in queue_pages:
    if generated_count >= DAILY_LIMIT:
        break

    slug = page["slug"]
    keyword = page["keyword"]
    keyword_display = display_keyword(keyword)

    if slug in PROTECTED_SLUGS:
        print("Skipping protected page:", slug)
        continue

    if keyword in generated_keywords:
        skipped_known_keyword_count += 1
        built_keywords.append(keyword)
        continue

    if slug in generated_slugs:
        skipped_known_slug_count += 1
        built_keywords.append(keyword)
        continue

    path = page_path(slug)

    if page_exists(slug):
        skipped_existing_count += 1
        append_line_if_missing(GENERATED_SLUGS_FILE, slug)
        append_line_if_missing(GENERATED_KEYWORDS_FILE, keyword)
        generated_slugs.add(slug)
        generated_keywords.add(keyword)
        built_keywords.append(keyword)
        continue

    os.makedirs(os.path.dirname(path), exist_ok=True)

    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    try:
        ai_text = generate_content(keyword_display)
    except Exception as e:
        print("AI generation failed for", keyword, ":", e)
        ai_text = fallback_ai_text(keyword)

    link_source_pages = dedupe_pages_by_slug(existing_pages + queue_pages)

    related_pages = get_related_pages(page, link_source_pages, RELATED_LINKS_COUNT)
    related_slugs = {p["slug"] for p in related_pages}

    more_pages = get_related_pages(
        page,
        link_source_pages,
        MORE_LINKS_COUNT,
        exclude_slugs=related_slugs
    )

    links_html = build_links_html(related_pages)
    more_links_html = build_links_html(more_pages)
    hub_link_html = build_hub_link_html(keyword)

    html = template
    html = html.replace("{{TITLE}}", escape_html(title))
    html = html.replace("{{DESCRIPTION}}", escape_html(description))
    html = html.replace("{{KEYWORD}}", escape_html(keyword_display))
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links_html)
    html = html.replace("{{MORE_LINKS}}", more_links_html)
    html = html.replace("{{HUB_LINK}}", hub_link_html)
    html = html.replace("{{CANONICAL_URL}}", escape_html(canonical))

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    append_line_if_missing(GENERATED_SLUGS_FILE, slug)
    append_line_if_missing(GENERATED_KEYWORDS_FILE, keyword)
    generated_slugs.add(slug)
    generated_keywords.add(keyword)
    built_keywords.append(keyword)

    existing_pages.append({"keyword": keyword, "slug": slug})
    existing_pages = dedupe_pages_by_slug(existing_pages)

    generated_count += 1
    print(f"Generated: {slug} ({generated_count}/{DAILY_LIMIT})")

# rewrite queue with only leftovers
built_keyword_set = set(built_keywords)
remaining_keywords = [k for k in keywords if k not in built_keyword_set]

with open(KEYWORD_FILE, "w", encoding="utf-8") as f:
    for k in remaining_keywords:
        f.write(k + "\n")

print(
    f"Done. Generated {generated_count} new pages. "
    f"Skipped {skipped_existing_count} existing pages, "
    f"{skipped_known_slug_count} known slugs, "
    f"{skipped_known_keyword_count} known keywords."
)
print(f"Remaining keywords in queue: {len(remaining_keywords)}")