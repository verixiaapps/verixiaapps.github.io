import os
import re
from generate_content import generate_content

# -----------------------------
# CONFIG
# -----------------------------
KEYWORD_FILE = "data/keywords.txt"
GENERATED_SLUGS_FILE = "data/generated_slugs.txt"
GENERATED_KEYWORDS_FILE = "data/generated_keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"
OUTPUT_DIR = "scam-check-now"
SITE = "https://verixiaapps.com"
RELATED_LINKS_COUNT = 6
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "100"))

PROTECTED_SLUGS = {"is-this-a-scam"}

CLUSTER_TERMS = {
    "amazon", "paypal", "zelle", "cash", "venmo", "facebook", "instagram",
    "tiktok", "whatsapp", "telegram", "snapchat", "discord", "crypto",
    "bitcoin", "ethereum", "usps", "fedex", "ups", "bank", "chase",
    "wells", "america", "job", "loan", "credit", "romance", "gift",
    "irs", "social", "verification", "phishing", "login", "account"
}


# -----------------------------
# UTILITIES
# -----------------------------
def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def normalize_keyword(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def display_keyword(text):
    kw = normalize_keyword(text)
    if kw.endswith(" scam"):
        kw = kw[:-5].strip()
    return kw


def title_case(text):
    return " ".join(word.capitalize() for word in text.split())


def build_title(keyword):
    kw_raw = normalize_keyword(keyword)
    kw_display = title_case(display_keyword(keyword))

    if kw_raw.startswith("how to "):
        return f"{title_case(kw_raw)}: Safety Tips, Warning Signs & What To Do"

    if kw_raw.startswith("what to do after "):
        return f"{title_case(kw_raw)}: Recovery Steps & What To Do Next"

    if kw_raw.startswith("how to recover after "):
        return f"{title_case(kw_raw)}: What To Do Next"

    if kw_raw.startswith("how to secure "):
        return f"{title_case(kw_raw)}: Safety Steps & What To Do Next"

    if kw_raw.startswith("how to block "):
        return f"{title_case(kw_raw)}: Protection Tips & Warning Signs"

    if kw_raw.startswith("how to avoid "):
        return f"{title_case(kw_raw)}: Warning Signs & Safety Tips"

    if kw_raw.startswith("did i get scammed"):
        return f"{title_case(kw_raw)}? Signs, Risks & What To Do Next"

    if kw_raw.startswith("can scammers"):
        return f"{title_case(kw_raw)}? Risks, Warning Signs & What To Do"

    if kw_raw.startswith("can someone"):
        return f"{title_case(kw_raw)}? Risks, Warning Signs & What To Do"

    if kw_raw.startswith("almost "):
        return f"{title_case(kw_raw)}? Warning Signs & Safety Steps"

    if kw_raw.startswith("is ") and " legit" in kw_raw:
        clean = title_case(kw_raw.replace(" legit", ""))
        return f"{clean} Legit or a Scam? Warning Signs & What To Do"

    if kw_raw.startswith("is this "):
        return f"{title_case(kw_raw)}? Check Warning Signs & What To Do"

    if kw_raw.startswith("is "):
        return f"{title_case(kw_raw)}? Warning Signs & What To Do"

    if kw_raw.startswith("what happens after "):
        return f"{title_case(kw_raw)}? Risks, Warning Signs & Next Steps"

    return f"Is {kw_display} a Scam? Warning Signs & What To Do"


def build_description(keyword):
    kw_raw = normalize_keyword(keyword)
    kw_display = title_case(display_keyword(keyword))

    if kw_raw.startswith("how to "):
        return (
            f"Learn {kw_raw} with practical safety tips, warning signs, and what to do next. "
            f"Use our free AI scam checker for suspicious messages, emails, and links."
        )

    if kw_raw.startswith("what to do after "):
        return (
            f"Learn {kw_raw}, the warning signs to watch for, and the next steps to protect yourself. "
            f"Use our free AI scam checker for suspicious messages, emails, and links."
        )

    if kw_raw.startswith("did i get scammed"):
        return (
            f"Find out {kw_raw}, review warning signs, understand the risks, and see what to do next. "
            f"Use our free AI scam checker for suspicious messages, emails, and links."
        )

    if kw_raw.startswith("can scammers") or kw_raw.startswith("can someone"):
        return (
            f"Find out {kw_raw}, review the risks and warning signs, and see what steps to take next. "
            f"Use our free AI scam checker for suspicious messages, emails, and links."
        )

    if kw_raw.startswith("almost "):
        return (
            f"Find out whether it is safe, review warning signs, and learn what steps to take next. "
            f"Use our free AI scam checker for suspicious messages, emails, and links."
        )

    if kw_raw.startswith("is ") and " legit" in kw_raw:
        clean = kw_raw.replace(" legit", "")
        return (
            f"Is {clean} legit or a scam? Review warning signs, real risks, and what to do next. "
            f"Use our free AI scam checker for suspicious messages, emails, and links."
        )

    if kw_raw.startswith("is this "):
        return (
            f"Check whether this looks like a scam, review warning signs, real risks, and what to do next. "
            f"Use our free AI scam checker for suspicious messages, emails, and links."
        )

    if kw_raw.startswith("is "):
        return (
            f"Is {kw_display} a scam? Review warning signs, real risks, and what to do next. "
            f"Use our free AI scam checker for suspicious messages, emails, and links."
        )

    if kw_raw.startswith("what happens after "):
        return (
            f"Learn what happens next, the risks to watch for, and what steps to take after a phishing or scam event. "
            f"Use our free AI scam checker for suspicious messages, emails, and links."
        )

    return (
        f"Is {kw_display} a scam or legit? Check warning signs, real risks, and what to do next. "
        f"Use our free AI scam checker for suspicious messages, emails, and links."
    )


def build_related_anchor(keyword):
    kw_raw = normalize_keyword(keyword)
    kw_display = title_case(display_keyword(keyword))

    if kw_raw.startswith("how to "):
        return title_case(kw_raw)

    if kw_raw.startswith("what to do after "):
        return title_case(kw_raw)

    if kw_raw.startswith("how to recover after "):
        return title_case(kw_raw)

    if kw_raw.startswith("how to secure "):
        return title_case(kw_raw)

    if kw_raw.startswith("how to block "):
        return title_case(kw_raw)

    if kw_raw.startswith("how to avoid "):
        return title_case(kw_raw)

    if kw_raw.startswith("did i get scammed"):
        return title_case(kw_raw) + "?"

    if kw_raw.startswith("can scammers"):
        return title_case(kw_raw) + "?"

    if kw_raw.startswith("can someone"):
        return title_case(kw_raw) + "?"

    if kw_raw.startswith("almost "):
        return title_case(kw_raw) + "?"

    if kw_raw.startswith("is ") and " legit" in kw_raw:
        clean = title_case(kw_raw.replace(" legit", ""))
        return f"{clean} Legit or a Scam?"

    if kw_raw.startswith("is this "):
        return title_case(kw_raw) + "?"

    if kw_raw.startswith("is "):
        return title_case(kw_raw) + "?"

    if kw_raw.startswith("what happens after "):
        return title_case(kw_raw) + "?"

    return f"Is {kw_display} a Scam?"


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys([normalize_keyword(k) for k in f if k.strip()]))


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


def keyword_tokens(text):
    return set(normalize_keyword(text).split())


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


def page_exists(slug):
    path = os.path.join(OUTPUT_DIR, slug, "index.html")
    return os.path.exists(path)


def fallback_ai_text(keyword):
    kw = title_case(display_keyword(keyword))
    return f"""
<p>{kw} scams often involve impersonation, urgency, or requests for money and sensitive information.</p>
<p>Common warning signs include unexpected messages, pressure to act quickly, suspicious links, and unusual payment requests.</p>
<p>If you are unsure, avoid clicking links, replying, or sending money until you verify through official sources.</p>
""".strip()


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

# keep queue unique by slug too
seen_queue_slugs = set()
pages = []
duplicate_queue_count = 0

for k in keywords:
    slug = slugify(k)
    if slug in PROTECTED_SLUGS:
        continue
    if slug in seen_queue_slugs:
        duplicate_queue_count += 1
        continue
    seen_queue_slugs.add(slug)
    pages.append({"keyword": k, "slug": slug})

print(f"Loaded {len(keywords)} keywords from queue.")
print(f"Unique queued pages after slug dedupe: {len(pages)}")
print(f"Duplicate queued keywords skipped: {duplicate_queue_count}")
print(f"Known generated slugs: {len(generated_slugs)}")
print(f"Known generated keywords: {len(generated_keywords)}")
print(f"Daily limit: {DAILY_LIMIT}")


# -----------------------------
# GENERATE PAGES (INCREMENTAL ONLY)
# -----------------------------
generated_count = 0
skipped_existing_count = 0
skipped_known_slug_count = 0
skipped_known_keyword_count = 0
built_keywords = []

for page in pages:
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

    folder = os.path.join(OUTPUT_DIR, slug)
    path = os.path.join(folder, "index.html")

    if page_exists(slug):
        skipped_existing_count += 1
        append_line_if_missing(GENERATED_SLUGS_FILE, slug)
        append_line_if_missing(GENERATED_KEYWORDS_FILE, keyword)
        generated_slugs.add(slug)
        generated_keywords.add(keyword)
        built_keywords.append(keyword)
        continue

    os.makedirs(folder, exist_ok=True)

    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    try:
        ai_text = generate_content(keyword)
    except Exception as e:
        print("AI generation failed for", keyword, ":", e)
        ai_text = fallback_ai_text(keyword)

    related_pages = get_related_pages(page, pages, RELATED_LINKS_COUNT)

    links_html = "".join(
        f'<li><a href="/scam-check-now/{r["slug"]}/">{build_related_anchor(r["keyword"])}</a></li>\n'
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

    append_line_if_missing(GENERATED_SLUGS_FILE, slug)
    append_line_if_missing(GENERATED_KEYWORDS_FILE, keyword)
    generated_slugs.add(slug)
    generated_keywords.add(keyword)
    built_keywords.append(keyword)

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