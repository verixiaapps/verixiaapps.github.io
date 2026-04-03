import json
import os
import re
import sys
from html import escape

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from generate_content import generate_content

# -----------------------------
# CONFIG
# -----------------------------
KEYWORD_FILE = os.path.join(BASE_DIR, "data", "keywords_b.txt")
GENERATED_SLUGS_FILE = os.path.join(BASE_DIR, "data", "generated_slugs_b.txt")
GENERATED_KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "generated_keywords_b.txt")
SLUG_TO_HUB_FILE = os.path.join(BASE_DIR, "data", "slug_to_hub_b.json")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "seo-template-b.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "scam-check-now-b")
HUBS_DIR = os.path.join(OUTPUT_DIR, "hubs")
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

DEFAULT_HUB_RULES = {
    "job-scams": ["job", "hiring", "recruiter", "interview", "offer", "onboarding"],
    "crypto-scams": ["crypto", "bitcoin", "wallet", "ethereum", "eth", "nft", "airdrop", "token"],
    "email-scams": ["email", "mail", "inbox"],
    "text-scams": ["text", "sms", "message"],
    "brand-scams": ["paypal", "amazon", "apple", "google", "bank", "venmo", "zelle", "cash app", "cash", "facebook", "instagram", "tiktok", "whatsapp", "telegram", "discord"],
    "payment-scams": ["payment", "invoice", "transfer", "fee", "refund", "charge", "billing"],
    "general-scams": [],
}

COMMON_HUB_WORDS = {"scam", "scams", "hub", "hubs"}


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
    base = clean_base_keyword(text)
    if not base:
        base = normalize_keyword(text)
    return {token for token in base.split() if token}


def keyword_cluster_tokens(text):
    return {token for token in keyword_tokens(text) if token in CLUSTER_TERMS}


def keyword_root(text):
    cleaned = clean_base_keyword(text)
    return cleaned.split()[0] if cleaned else ""


def escape_html(text):
    return escape(str(text), quote=True)


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


def ensure_file(filepath):
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists(filepath):
        with open(filepath, "a", encoding="utf-8"):
            pass


def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys(normalize_keyword(line) for line in f if line.strip()))


def load_generated_slugs():
    if not os.path.exists(GENERATED_SLUGS_FILE):
        return set()
    with open(GENERATED_SLUGS_FILE, encoding="utf-8") as f:
        return {slugify(line) for line in f if slugify(line)}


def load_generated_keywords():
    if not os.path.exists(GENERATED_KEYWORDS_FILE):
        return set()
    with open(GENERATED_KEYWORDS_FILE, encoding="utf-8") as f:
        return {normalize_keyword(line) for line in f if normalize_keyword(line)}


def load_slug_to_hub():
    if not os.path.exists(SLUG_TO_HUB_FILE):
        return {}
    with open(SLUG_TO_HUB_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return {slugify(k): str(v).strip() for k, v in data.items() if slugify(k) and str(v).strip()}


def load_available_hub_names(slug_to_hub):
    hub_names = set(DEFAULT_HUB_RULES.keys())

    for hub_name in slug_to_hub.values():
        hub_slug = slugify(hub_name)
        if hub_slug:
            hub_names.add(hub_slug)

    if os.path.isdir(HUBS_DIR):
        for name in os.listdir(HUBS_DIR):
            path = os.path.join(HUBS_DIR, name)
            if os.path.isdir(path):
                hub_slug = slugify(name)
                if hub_slug:
                    hub_names.add(hub_slug)

    return hub_names


def hub_name_tokens(hub_name):
    return {
        token
        for token in slugify(hub_name).split("-")
        if token and token not in COMMON_HUB_WORDS
    }


def infer_hub_name(keyword, available_hub_names):
    keyword_lower = normalize_keyword(keyword)
    tokens = keyword_tokens(keyword)

    candidate_hubs = set(available_hub_names or set()) | set(DEFAULT_HUB_RULES.keys())
    if not candidate_hubs:
        return ""

    best_hub = ""
    best_score = -1

    for hub_name in sorted(candidate_hubs):
        score = 0
        rules = DEFAULT_HUB_RULES.get(hub_name, [])

        for term in rules:
            term_norm = normalize_keyword(term)
            if not term_norm:
                continue
            pattern = r"(?<![a-z0-9])" + re.escape(term_norm) + r"(?![a-z0-9])"
            if re.search(pattern, keyword_lower):
                score += 3

        if score == 0:
            for token in hub_name_tokens(hub_name):
                if token in tokens:
                    score += 1

        if score > best_score:
            best_score = score
            best_hub = hub_name

    if best_score > 0:
        return best_hub

    if "general-scams" in candidate_hubs:
        return "general-scams"

    return ""


def write_lines(filepath, values, preserve_input=True):
    ensure_file(filepath)

    if preserve_input:
        lines = [str(v).strip() for v in values if str(v).strip()]
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


def load_output_pages_from_disk():
    pages = []
    seen = set()

    if not os.path.exists(OUTPUT_DIR):
        return pages

    for slug in sorted(os.listdir(OUTPUT_DIR)):
        folder = os.path.join(OUTPUT_DIR, slug)
        index_path = os.path.join(folder, "index.html")

        if not os.path.isdir(folder):
            continue
        if slug in PROTECTED_SLUGS or slug in seen or slug == "hubs" or not os.path.exists(index_path):
            continue

        seen.add(slug)
        pages.append({
            "keyword": slug.replace("-", " "),
            "slug": slug,
        })

    return pages


def merge_page_pools(*page_groups):
    merged = []
    seen = set()

    for group in page_groups:
        for page in group:
            slug = slugify(page.get("slug", ""))
            if not slug or slug in PROTECTED_SLUGS or slug == "hubs" or slug in seen:
                continue
            seen.add(slug)
            merged.append({
                "keyword": normalize_keyword(page.get("keyword", slug.replace("-", " "))),
                "slug": slug,
            })

    return merged


def sanitize_ai_html(text):
    raw = str(text or "").strip()
    if not raw:
        return ""

    raw = re.sub(r"^```(?:html)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    raw = re.sub(r"<script\b[^>]*>.*?</script>", "", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", "", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = raw.strip()

    if "<" in raw and ">" in raw:
        return raw

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", raw) if p.strip()]
    if not paragraphs:
        paragraphs = [raw]

    return "\n".join(f"<p>{escape_html(paragraph)}</p>" for paragraph in paragraphs)


# -----------------------------
# AI GENERATION
# -----------------------------
def generate_ai_text(keyword, keyword_display):
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

    seen = set()
    last_error = None

    for prompt in attempts:
        prompt_norm = normalize_keyword(prompt)
        if not prompt_norm or prompt_norm in seen:
            continue
        seen.add(prompt_norm)

        try:
            ai_text = sanitize_ai_html(generate_content(prompt))
            if ai_text:
                return ai_text
        except Exception as e:
            last_error = e
            print(f"[error] AI generation failed for '{prompt}': {e}")

    if last_error:
        raise ValueError(f"AI generation failed for all prompts: {last_error}")
    raise ValueError("AI generation failed for all prompts")


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
    return f"{SITE}/scam-check-now-b/{slug}/"


def pretty_hub_title(hub_name):
    return title_case(hub_name.replace("-", " "))


def build_hub_link_html(slug, keyword, slug_to_hub, available_hub_names):
    normalized_slug = slugify(slug)
    hub_name = slug_to_hub.get(normalized_slug, "").strip()

    if not hub_name:
        hub_name = infer_hub_name(keyword, available_hub_names)
        if hub_name:
            slug_to_hub[normalized_slug] = hub_name

    if not hub_name:
        return ""

    hub_title = pretty_hub_title(hub_name)
    hub_url = f"{SITE}/scam-check-now-b/hubs/{hub_name}/"
    return f'<a href="{escape_html(hub_url)}">{escape_html(hub_title)}</a>'


# -----------------------------
# LINKING HELPERS
# -----------------------------
def dedupe_pages_by_slug(pages_list):
    deduped = []
    seen = set()

    for page in pages_list:
        slug = slugify(page["slug"])
        if not slug or slug in seen or slug in PROTECTED_SLUGS or slug == "hubs":
            continue
        seen.add(slug)
        deduped.append({
            "keyword": normalize_keyword(page["keyword"]),
            "slug": slug,
        })

    return deduped


def get_related_pages(current_page, all_pages, limit, exclude_slugs=None):
    exclude_slugs = {slugify(s) for s in (exclude_slugs or set())}
    current_slug = slugify(current_page["slug"])
    current_keyword = current_page["keyword"]
    current_tokens = keyword_tokens(current_keyword)
    current_cluster = keyword_cluster_tokens(current_keyword)
    current_root = keyword_root(current_keyword)
    current_base = clean_base_keyword(current_keyword)

    candidates = [
        p for p in all_pages
        if slugify(p["slug"]) != current_slug
        and slugify(p["slug"]) not in PROTECTED_SLUGS
        and slugify(p["slug"]) not in exclude_slugs
        and page_exists(slugify(p["slug"]))
        and clean_base_keyword(p["keyword"]) != current_base
    ]

    def score(page):
        other_keyword = page["keyword"]
        other_tokens = keyword_tokens(other_keyword)
        other_cluster = keyword_cluster_tokens(other_keyword)
        other_root = keyword_root(other_keyword)
        length_diff = abs(len(other_tokens) - len(current_tokens))
        same_root = 1 if current_root and other_root == current_root else 0
        shared_cluster = len(current_cluster & other_cluster)
        shared_tokens = len(current_tokens & other_tokens)

        return (
            -same_root,
            -shared_cluster,
            -shared_tokens,
            length_diff,
            other_keyword,
        )

    ranked = sorted(candidates, key=score)
    related = []
    used_slugs = set()
    used_bases = set()

    for page in ranked:
        page_slug = slugify(page["slug"])
        base = clean_base_keyword(page["keyword"])
        if page_slug in used_slugs or base in used_bases:
            continue
        related.append(page)
        used_slugs.add(page_slug)
        used_bases.add(base)
        if len(related) == limit:
            break

    if len(related) < limit:
        fallback_candidates = sorted(
            [
                p for p in all_pages
                if slugify(p["slug"]) != current_slug
                and slugify(p["slug"]) not in PROTECTED_SLUGS
                and slugify(p["slug"]) not in exclude_slugs
                and slugify(p["slug"]) not in used_slugs
                and page_exists(slugify(p["slug"]))
            ],
            key=lambda p: slugify(p["slug"]),
        )

        for page in fallback_candidates:
            base = clean_base_keyword(page["keyword"])
            if base in used_bases:
                continue
            related.append(page)
            used_slugs.add(slugify(page["slug"]))
            used_bases.add(base)
            if len(related) == limit:
                break

    return related


def build_links_html(pages_list):
    return "".join(
        f'<li><a href="/scam-check-now-b/{slugify(p["slug"])}/">{escape_html(build_related_anchor(p["keyword"]))}</a></li>\n'
        for p in pages_list
        if page_exists(slugify(p["slug"]))
    )


# -----------------------------
# SETUP & GENERATION LOOP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(GENERATED_SLUGS_FILE)
ensure_file(GENERATED_KEYWORDS_FILE)
ensure_file(SLUG_TO_HUB_FILE)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

keywords = load_keywords()
if not keywords:
    print("No keywords in queue. Nothing to generate.")
    sys.exit(0)

generated_slugs = load_generated_slugs()
generated_keywords = load_generated_keywords()
slug_to_hub = load_slug_to_hub()
available_hub_names = load_available_hub_names(slug_to_hub)
disk_pages = load_output_pages_from_disk()

queue_pages = []
seen_queue_slugs = set()
duplicate_queue_count = 0

for keyword in keywords:
    keyword_norm = normalize_keyword(keyword)
    slug = slugify(keyword_norm)

    if slug in PROTECTED_SLUGS or not slug:
        continue
    if slug in seen_queue_slugs:
        duplicate_queue_count += 1
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
all_linkable_pages = merge_page_pools(existing_pages, disk_pages)

print(f"Loaded {len(keywords)} keywords from queue.")
print(f"Unique queued pages after slug dedupe: {len(queue_pages)}")
print(f"Duplicate queued keywords skipped: {duplicate_queue_count}")
print(f"Known generated slugs: {len(generated_slugs)}")
print(f"Known generated keywords: {len(generated_keywords)}")
print(f"Existing pages available for internal links: {len(all_linkable_pages)}")
print(f"Loaded slug-to-hub mappings: {len(slug_to_hub)}")
print(f"Available hub names: {len(available_hub_names)}")
print(f"Daily limit: {DAILY_LIMIT}")

generated_count = 0
skipped_existing_count = 0
failed_count = 0
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

        if slug not in slug_to_hub:
            inferred_hub = infer_hub_name(keyword, available_hub_names)
            if inferred_hub:
                slug_to_hub[slug] = inferred_hub

        continue

    os.makedirs(os.path.dirname(path), exist_ok=True)
    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    effective_hub_name = slug_to_hub.get(slug) or infer_hub_name(keyword, available_hub_names)
    if effective_hub_name:
        slug_to_hub[slug] = effective_hub_name
        available_hub_names.add(effective_hub_name)

    hub_link_html = build_hub_link_html(slug, keyword, slug_to_hub, available_hub_names)

    try:
        ai_text = generate_ai_text(keyword, keyword_display)
    except Exception as e:
        failed_count += 1
        print(f"[failed] {keyword} -> {e}")
        continue

    related_pages = get_related_pages(page, all_linkable_pages, RELATED_LINKS_COUNT)
    related_slugs = {p["slug"] for p in related_pages}

    more_pages = get_related_pages(
        page,
        all_linkable_pages,
        MORE_LINKS_COUNT,
        exclude_slugs=related_slugs,
    )

    html = template
    html = html.replace("{{TITLE}}", escape_html(title))
    html = html.replace("{{DESCRIPTION}}", escape_html(description))
    html = html.replace("{{KEYWORD}}", escape_html(keyword_display))
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", build_links_html(related_pages))
    html = html.replace("{{MORE_LINKS}}", build_links_html(more_pages))
    html = html.replace("{{CANONICAL_URL}}", escape_html(canonical))
    html = html.replace("{{HUB_LINK}}", hub_link_html)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    new_generated_slugs.add(slug)
    new_generated_keywords.add(keyword)
    processed_keywords.add(keyword)

    existing_pages.append({"keyword": keyword, "slug": slug})
    existing_pages = dedupe_pages_by_slug(existing_pages)
    all_linkable_pages = merge_page_pools(existing_pages, disk_pages, [page])

    generated_count += 1

    print(
        f"Generated: {slug} ({generated_count}/{DAILY_LIMIT}) "
        f"-> related: {len(related_pages)}, more: {len(more_pages)}, hub: {slug_to_hub.get(slug, 'none')}"
    )

remaining_keywords = []
for keyword in keywords:
    keyword_norm = normalize_keyword(keyword)
    if keyword_norm not in processed_keywords:
        remaining_keywords.append(keyword_norm)

write_lines(GENERATED_SLUGS_FILE, sorted(new_generated_slugs))
write_lines(GENERATED_KEYWORDS_FILE, sorted(new_generated_keywords))
write_lines(KEYWORD_FILE, remaining_keywords)

with open(SLUG_TO_HUB_FILE, "w", encoding="utf-8") as f:
    json.dump(slug_to_hub, f, indent=2, sort_keys=True)

print(
    f"Done. Generated {generated_count} new pages. "
    f"Skipped {skipped_existing_count} existing pages. "
    f"Failed {failed_count} keywords."
)
print(f"Remaining keywords in queue: {len(remaining_keywords)}")