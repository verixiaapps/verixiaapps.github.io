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
REJECTED_KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "rejected_keywords.txt")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "seo-template.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "scam-check-now")
SITE = "https://verixiaapps.com"

RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT = 10
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "100"))
MAX_REJECT_ATTEMPTS = int(os.getenv("MAX_REJECT_ATTEMPTS", "2"))

PROTECTED_SLUGS = {"is-this-a-scam"}
FALLBACK_HUB_SLUG = "general-scams"

REQUIRED_TEMPLATE_TAGS = {
    "{{TITLE}}",
    "{{DESCRIPTION}}",
    "{{KEYWORD}}",
    "{{AI_CONTENT}}",
    "{{RELATED_LINKS}}",
    "{{MORE_LINKS}}",
    "{{HUB_LINK}}",
    "{{CANONICAL_URL}}",
}

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
    "facebook marketplace": "Facebook Marketplace",
    "bank of america": "Bank of America",
    "wells fargo": "Wells Fargo",
    "social security": "Social Security",
    "trust wallet": "Trust Wallet",
    "google play": "Google Play",
    "cash app": "Cash App",
    "two factor": "Two-Factor",
    "metamask": "MetaMask",
    "coinbase": "Coinbase",
    "whatsapp": "WhatsApp",
    "instagram": "Instagram",
    "snapchat": "Snapchat",
    "telegram": "Telegram",
    "microsoft": "Microsoft",
    "binance": "Binance",
    "facebook": "Facebook",
    "ethereum": "Ethereum",
    "discord": "Discord",
    "bitcoin": "Bitcoin",
    "walmart": "Walmart",
    "paypal": "PayPal",
    "tiktok": "TikTok",
    "venmo": "Venmo",
    "amazon": "Amazon",
    "google": "Google",
    "apple": "Apple",
    "target": "Target",
    "crypto": "Crypto",
    "chase": "Chase",
    "steam": "Steam",
    "zelle": "Zelle",
    "fedex": "FedEx",
    "usps": "USPS",
    "bank": "Bank",
    "irs": "IRS",
    "ups": "UPS",
    "sms": "SMS",
    "otp": "OTP",
    "2fa": "2FA",
    "nft": "NFT",
    "ceo": "CEO",
    "dm": "DM",
    "icloud": "iCloud",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with"
}

GENERAL_FALLBACK_TERMS = {
    "scam", "legit", "safe", "real", "fake", "message", "email", "text",
    "link", "website", "alert", "warning", "notification", "request",
    "offer", "phishing", "login", "account", "verify", "verification",
    "support", "money", "payment", "refund", "invoice", "code", "codes",
    "caller", "number", "contact", "suspicious", "unknown", "unexpected"
}

# -----------------------------
# AI GENERATION (300+ words)
# -----------------------------
def generate_ai_text(keyword, keyword_display, min_words=300):
    raw_keyword = normalize_keyword(keyword)
    clean_keyword = normalize_keyword(keyword_display)
    readable = readable_keyword(keyword_display)

    attempts = [
        raw_keyword,
        clean_keyword,
        readable,
        f"is {clean_keyword} a scam" if clean_keyword and not raw_keyword.startswith("is ") else "",
        f"{clean_keyword} legit or scam" if clean_keyword and "legit" not in raw_keyword and "scam" not in raw_keyword else "",
    ]

    for prompt in attempts:
        if not prompt:
            continue
        try:
            ai_text = sanitize_ai_html(generate_content(prompt))
            word_count = len(ai_text.split())
            retry_count = 0
            while word_count < min_words and retry_count < 2:
                ai_text = sanitize_ai_html(generate_content(prompt))
                word_count = len(ai_text.split())
                retry_count += 1
            if word_count >= min_words:
                return ai_text
            print(f"[warn] Generated text for '{prompt}' below {min_words} words ({word_count}).")
        except Exception as e:
            print(f"[error] AI generation failed for '{prompt}': {e}")

    raise ValueError(f"AI generation failed or below {min_words} words for all prompts")

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
    current_hub = find_best_hub_slug(current_keyword)

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
        other_hub = find_best_hub_slug(other_keyword)
        length_diff = abs(len(other_tokens) - len(current_tokens))
        same_root = 1 if current_root and other_root == current_root else 0
        same_hub = 1 if current_hub and other_hub == current_hub else 0
        shared_cluster = len(current_cluster & other_cluster)
        shared_tokens = len(current_tokens & other_tokens)
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
        f'<li><a href="/scam-check-now/{p["slug"]}/">{escape_html(build_related_anchor(p["keyword"]))}</a></li>\n'
        for p in pages_list
        if page_exists(p["slug"])
    )

# -----------------------------
# SETUP & GENERATION LOOP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(GENERATED_SLUGS_FILE)
ensure_file(GENERATED_KEYWORDS_FILE)
ensure_file(REJECTED_KEYWORDS_FILE)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

validate_template(template)

keywords = load_keywords()
if not keywords:
    print("No keywords in queue. Nothing to generate.")
    sys.exit(0)

generated_slugs = load_generated_slugs()
generated_keywords = load_generated_keywords()
rejected_state = load_rejected_state()

queue_pages = []
seen_queue_slugs = set()
duplicate_queue_count = 0
retry_limited_count = 0

for keyword in keywords:
    keyword_norm = normalize_keyword(keyword)
    slug = slugify(keyword_norm)
    if slug in PROTECTED_SLUGS or not slug:
        continue
    if slug in seen_queue_slugs:
        duplicate_queue_count += 1
        continue
    if rejected_state.get(keyword_norm, {}).get("attempts", 0) >= MAX_REJECT_ATTEMPTS:
        retry_limited_count += 1
        continue
    seen_queue_slugs.add(slug)
    queue_pages.append({"keyword": keyword_norm, "slug": slug})

existing_pages = []
existing_seen_slugs = set()

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
queue_pages = dedupe_pages_by_slug(queue_pages)

print(f"Loaded {len(keywords)} keywords from queue.")
print(f"Unique queued pages after slug dedupe: {len(queue_pages)}")
print(f"Duplicate queued keywords skipped: {duplicate_queue_count}")
print(f"Retry-limited keywords skipped: {retry_limited_count}")
print(f"Known generated slugs: {len(generated_slugs)}")
print(f"Known generated keywords: {len(generated_keywords)}")
print(f"Existing pages available for internal links: {len(existing_pages)}")
print(f"Daily limit: {DAILY_LIMIT}")
print(f"Max reject attempts: {MAX_REJECT_ATTEMPTS}")
print(f"Fallback hub slug: {FALLBACK_HUB_SLUG}")

generated_count = 0
skipped_existing_count = 0
rejected_count = 0
processed_keywords = set()
new_generated_slugs = set(generated_slugs)
new_generated_keywords = set(generated_keywords)

for page in queue_pages:
    if generated_count >= DAILY_LIMIT:
        break
    slug = page["slug"]
    keyword = page["keyword"]
    keyword_display = display_keyword(keyword)
    path = page_path(slug)
    if slug in PROTECTED_SLUGS:
        processed_keywords.add(keyword)
        print("Skipping protected page:", slug)
        continue
    if page_exists(slug):
        skipped_existing_count += 1
        new_generated_slugs.add(slug)
        new_generated_keywords.add(keyword)
        processed_keywords.add(keyword)
        continue
    os.makedirs(os.path.dirname(path), exist_ok=True)
    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)
    try:
        ai_text = generate_ai_text(keyword, keyword_display, min_words=300)
    except Exception as e:
        rejected_count += 1
        prior_attempts = rejected_state.get(keyword, {}).get("attempts", 0)
        rejected_state[keyword] = {
            "attempts": prior_attempts + 1,
            "reason": str(e),
        }
        processed_keywords.add(keyword)
        print(f"[reject-final] {keyword} -> {e}")
        continue
    related_pages = get_related_pages(page, existing_pages, RELATED_LINKS_COUNT)
    related_slugs = {p["slug"] for p in related_pages}
    more_pages = get_related_pages(
        page,
        existing_pages,
        MORE_LINKS_COUNT,
        exclude_slugs=related_slugs
    )
    hub_link_html = build_hub_link_html(keyword)
    html = template
    html = html.replace("{{TITLE}}", escape_html(title))
    html = html.replace("{{DESCRIPTION}}", escape_html(description))
    html = html.replace("{{KEYWORD}}", escape_html(keyword_display))
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", build_links_html(related_pages))
    html = html.replace("{{MORE_LINKS}}", build_links_html(more_pages))
    html = html.replace("{{HUB_LINK}}", hub_link_html)
    html = html.replace("{{CANONICAL_URL}}", escape_html(canonical))
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    new_generated_slugs.add(slug)
    new_generated_keywords.add(keyword)
    processed_keywords.add(keyword)
    if keyword in rejected_state:
        del rejected_state[keyword]
    existing_pages.append({"keyword": keyword, "slug": slug})
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

write_lines(GENERATED_SLUGS_FILE, new_generated_slugs)
write_lines(GENERATED_KEYWORDS_FILE, new_generated_keywords)
save_rejected_state(rejected_state)
write_lines(KEYWORD_FILE, remaining_keywords)

print(
    f"Done. Generated {generated_count} new pages. "
    f"Skipped {skipped_existing_count} existing pages. "
    f"Rejected {rejected_count} keywords."
)
print(f"Remaining keywords in queue: {len(remaining_keywords)}")