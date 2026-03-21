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
    kw = title_case(display_keyword(keyword))
    return f"Is {kw} a Scam? (Real Check & Warning Signs)"


def build_description(keyword):
    keyword_title = title_case(normalize_keyword(keyword))
    return (
        f"Is {keyword_title} a scam or legit? Check warning signs, real risks, "
        f"and what to do next. Free AI scam checker for {normalize_keyword(keyword)}."
    )


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def load_keywords():
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys([normalize_keyword(k) for k in f if k.strip()]))


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
        ai_text = generate_content(keyword)
    except Exception as e:
        print("AI generation failed for", keyword, ":", e)
        ai_text = f"""
<p>{title_case(display_keyword(keyword))} scams often involve requests for money, personal information, or urgent action. Avoid clicking unknown links or sending funds. Always verify through official sources.</p>
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