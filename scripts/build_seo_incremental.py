Use this full replacement.

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
# UTILITIES
# -----------------------------
def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", normalize_keyword(text)).strip("-")


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
    text = normalize_keyword(text)
    if not text:
        return ""

    titled = []
    for i, word in enumerate(text.split()):
        titled.append(word if i > 0 and word in SMALL_WORDS else word.capitalize())

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


def ensure_file(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        with open(filepath, "a", encoding="utf-8"):
            pass


def normalize_line_set(values):
    return {str(v).strip() for v in values if str(v).strip()}


def write_lines(filepath, values):
    with open(filepath, "w", encoding="utf-8") as f:
        for value in sorted(normalize_line_set(values)):
            f.write(value + "\n")


def short_preview(text, length=220):
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    return value[:length]


def sanitize_rejected_reason(text):
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    return value.replace("|", "/")[:500]


def sanitize_ai_html(text):
    raw = str(text).strip()

    raw = re.sub(r"```(?:html)?", "", raw, flags=re.IGNORECASE)
    raw = raw.replace("```", "").strip()

    raw = re.sub(r"(?is)<!doctype.*?>", "", raw)
    raw = re.sub(r"(?is)<html\b[^>]*>", "", raw)
    raw = re.sub(r"(?is)</html>", "", raw)
    raw = re.sub(r"(?is)<head\b[^>]*>.*?</head>", "", raw)
    raw = re.sub(r"(?is)<body\b[^>]*>", "", raw)
    raw = re.sub(r"(?is)</body>", "", raw)
    raw = re.sub(r"(?is)<title\b[^>]*>.*?</title>", "", raw)
    raw = re.sub(r"(?is)<meta\b[^>]*>", "", raw)
    raw = re.sub(r"(?is)<script\b[^>]*>.*?</script>", "", raw)
    raw = re.sub(r"(?is)<style\b[^>]*>.*?</style>", "", raw)
    raw = re.sub(r"(?is)<h1\b[^>]*>.*?</h1>", "", raw)

    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


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


def is_usable_ai_text(text, keyword_display=""):
    if not text:
        return False

    raw = sanitize_ai_html(text)
    lowered = raw.lower()
    text_only = re.sub(r"<[^>]+>", " ", raw)
    text_only = re.sub(r"\s+", " ", text_only).strip().lower()

    if len(raw) < 260:
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
        "content policy",
        "i do not have enough information",
        "i don't have enough information",
        "placeholder",
        "insert",
        "example content",
    }
    if any(marker in lowered for marker in weak_markers):
        return False

    if "<p>" not in lowered:
        return False

    if "<h2" not in lowered and "<ul" not in lowered and raw.count("\n") < 2:
        return False

    if len(text_only) < 200:
        return False

    if keyword_display:
        keyword_words = [w for w in re.findall(r"[a-z0-9]+", normalize_keyword(keyword_display)) if len(w) > 2]
        if keyword_words:
            hits = sum(1 for word in keyword_words if word in text_only)
            if hits == 0:
                return False

    return True


def validate_template(template_text):
    missing = sorted(tag for tag in REQUIRED_TEMPLATE_TAGS if tag not in template_text)
    if missing:
        raise ValueError(f"Template missing required placeholders: {', '.join(missing)}")


# -----------------------------
# REJECT TRACKING
# -----------------------------
def parse_rejected_line(line):
    value = line.strip()
    if not value:
        return None

    parts = [part.strip() for part in value.split("|")]

    if not parts or not parts[0]:
        return None

    keyword = normalize_keyword(parts[0])
    attempts = 1
    reason = ""

    if len(parts) >= 2:
        if parts[1].isdigit():
            attempts = max(1, int(parts[1]))
            if len(parts) >= 3:
                reason = " | ".join(parts[2:]).strip()
        else:
            attempts = 1
            reason = " | ".join(parts[1:]).strip()

    return keyword, attempts, reason


def load_rejected_state():
    state = {}
    if not os.path.exists(REJECTED_KEYWORDS_FILE):
        return state

    with open(REJECTED_KEYWORDS_FILE, encoding="utf-8") as f:
        for line in f:
            parsed = parse_rejected_line(line)
            if not parsed:
                continue

            keyword, attempts, reason = parsed
            existing = state.get(keyword)

            if not existing or attempts >= existing["attempts"]:
                state[keyword] = {
                    "attempts": attempts,
                    "reason": reason,
                }

    return state


def save_rejected_state(state):
    with open(REJECTED_KEYWORDS_FILE, "w", encoding="utf-8") as f:
        for keyword in sorted(state.keys()):
            attempts = int(state[keyword].get("attempts", 1))
            reason = sanitize_rejected_reason(state[keyword].get("reason", ""))
            if reason:
                f.write(f"{keyword} | {attempts} | {reason}\n")
            else:
                f.write(f"{keyword} | {attempts}\n")


# -----------------------------
# AI GENERATION
# -----------------------------
def build_retry_prompt(keyword, keyword_display):
    raw = normalize_keyword(keyword)
    readable = readable_keyword(keyword)
    display = readable or keyword_display or raw

    return f"""
Write a scam-check SEO content section for the search query: "{display}".

Requirements:
- Output HTML only
- Do not include <html>, <head>, <body>, or <h1>
- Write 4 to 6 short sections using <h2> and <p>
- Make it specific to the query, not generic filler
- Cover scam warning signs, why people search this query, when it may be legitimate, and what to do next
- Mention realistic scam patterns like phishing, fake login pages, spoofed support, urgent payment requests, fake verification, suspicious links, or impersonation when relevant
- Keep tone clear, trustworthy, and practical
- Do not mention being an AI
- Do not refuse
- Do not include placeholders
- Avoid repeating the exact keyword unnaturally

Target query: {display}
Original keyword: {raw}
""".strip()


def generate_ai_text(keyword, keyword_display):
    raw_keyword = normalize_keyword(keyword)
    clean_keyword = normalize_keyword(keyword_display)

    attempts = []
    if raw_keyword:
        attempts.append(("primary", raw_keyword))
    attempts.append(("structured", build_retry_prompt(keyword, keyword_display)))

    seen = set()
    ordered_attempts = []
    for label, prompt in attempts:
        prompt_norm = normalize_keyword(prompt)
        if prompt_norm and prompt_norm not in seen:
            seen.add(prompt_norm)
            ordered_attempts.append((label, prompt))

    last_error = None

    for label, prompt in ordered_attempts:
        try:
            ai_text = generate_content(prompt)
            ai_text = sanitize_ai_html(ai_text)

            if is_usable_ai_text(ai_text, keyword_display=keyword_display):
                return ai_text

            preview = short_preview(ai_text)
            last_error = f"rejected {label} attempt for '{clean_keyword or raw_keyword}' | preview: {preview}"
            print(f"[reject] {last_error}")

        except Exception as e:
            last_error = f"{label} attempt failed for '{clean_keyword or raw_keyword}': {e}"
            print(f"[error] {last_error}")

    raise ValueError(last_error or "AI generation failed")


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


# -----------------------------
# HUB HELPERS
# -----------------------------
def get_cluster_lookup():
    lookup = {}
    for hub_slug, match_terms in CLUSTERS.items():
        normalized_terms = []
        for term in match_terms:
            term_norm = normalize_keyword(term)
            if term_norm:
                normalized_terms.append(term_norm)
        lookup[hub_slug] = normalized_terms
    return lookup


CLUSTER_LOOKUP = get_cluster_lookup()


def ensure_fallback_hub_exists():
    if FALLBACK_HUB_SLUG not in CLUSTER_LOOKUP:
        CLUSTER_LOOKUP[FALLBACK_HUB_SLUG] = ["scam", "legit", "safe", "real or fake"]


def best_hub_title(hub_slug):
    if hub_slug == FALLBACK_HUB_SLUG:
        return "General Scams"

    label = hub_slug.replace("-", " ")
    label = re.sub(r"\bscams\b", "", label).strip()
    return title_case(label) if label else "General Scams"


def score_hub_match(keyword, hub_slug, match_terms):
    keyword_norm = normalize_keyword(keyword)
    keyword_clean = clean_base_keyword(keyword)
    keyword_word_set = set(re.findall(r"[a-z0-9]+", keyword_clean))
    keyword_joined = f" {keyword_clean} "

    score = 0

    for term in match_terms:
        term_norm = normalize_keyword(term)
        if not term_norm:
            continue

        term_words = set(re.findall(r"[a-z0-9]+", term_norm))
        exact_phrase = f" {term_norm} "

        if exact_phrase in keyword_joined:
            score += 12 + len(term_words)
        elif term_words and term_words.issubset(keyword_word_set):
            score += 8 + len(term_words)
        elif term_norm in keyword_norm:
            score += 5

    root = keyword_root(keyword)
    if root and root in hub_slug:
        score += 3

    if hub_slug == FALLBACK_HUB_SLUG:
        generic_hits = sum(1 for token in keyword_word_set if token in GENERAL_FALLBACK_TERMS)
        score += min(generic_hits, 4)

    return score


def find_best_hub_slug(keyword):
    ensure_fallback_hub_exists()

    best_hub_slug = FALLBACK_HUB_SLUG
    best_score = -1

    for hub_slug, match_terms in CLUSTER_LOOKUP.items():
        score = score_hub_match(keyword, hub_slug, match_terms)
        if score > best_score:
            best_score = score
            best_hub_slug = hub_slug

    return best_hub_slug or FALLBACK_HUB_SLUG


def build_hub_link_html(keyword):
    hub_slug = find_best_hub_slug(keyword)
    hub_title = best_hub_title(hub_slug)

    return (
        f'<a class="hub-link-card" href="/scam-check-now/{hub_slug}/">'
        f'<span class="hub-link-label">Scam Hub</span>'
        f'<span class="hub-link-title">Browse the {escape_html(hub_title)} Hub</span>'
        f'</a>'
    )


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
# SETUP
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
        ai_text = generate_ai_text(keyword, keyword_display)
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