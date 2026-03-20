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
RELATED_LINKS_COUNT = 5

# 🔒 PROTECTED PAGES (DO NOT GENERATE / OVERWRITE)
PROTECTED_SLUGS = {"is-this-a-scam"}


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


def get_related_pages(current_page, all_pages, limit):
    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_tokens = keyword_tokens(current_keyword)

    candidates = [
        p for p in all_pages
        if p["slug"] != current_slug and p["slug"] not in PROTECTED_SLUGS
    ]

    def score(page):
        other_tokens = keyword_tokens(page["keyword"])
        shared = len(current_tokens & other_tokens)
        same_root = 1 if current_keyword.split()[0] == page["keyword"].split()[0] else 0
        length_diff = abs(len(page["keyword"]) - len(current_keyword))
        return (-same_root, -shared, length_diff, page["keyword"])

    ranked = sorted(candidates, key=score)

    if ranked:
        return ranked[:limit]

    # emergency fallback so there is always at least something if any page exists
    fallback = [
        p for p in all_pages
        if p["slug"] not in PROTECTED_SLUGS and p["slug"] != current_slug
    ]
    return fallback[:limit]


# -----------------------------
# SETUP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

keywords = load_keywords()
pages = [{"keyword": k, "slug": slugify(k)} for k in keywords]


# -----------------------------
# GENERATE PAGES (ALWAYS REBUILD)
# -----------------------------
for page in pages:
    slug = page["slug"]
    keyword = page["keyword"]
    keyword_display = display_keyword(keyword)

    # 🔒 Never touch protected page
    if slug in PROTECTED_SLUGS:
        print("Skipping protected page:", slug)
        continue

    folder = f"{OUTPUT_DIR}/{slug}"
    path = f"{folder}/index.html"
    os.makedirs(folder, exist_ok=True)

    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    # Generate AI content
    try:
        ai_text = generate_content(keyword)
    except Exception as e:
        print("AI generation failed for", keyword, ":", e)
        ai_text = f"""
<p>{title_case(display_keyword(keyword))} scams often involve requests for money, personal information, or urgent action. Avoid clicking unknown links or sending funds. Always verify through official sources.</p>
"""

    # Related links (always internal, always regenerated)
    related_pages = get_related_pages(page, pages, RELATED_LINKS_COUNT)

    links_html = "".join([
        f'<li><a href="/scam-check-now/{r["slug"]}/">Is {title_case(display_keyword(r["keyword"]))} a Scam?</a></li>\n'
        for r in related_pages
    ])

    # Final fallback so the template never gets an empty related-links section
    if not links_html:
        links_html = '<li><a href="/scam-check-now/is-this-a-scam/">Check Another Scam Message</a></li>\n'

    # Fill template
    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword_display)
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links_html)
    html = html.replace("{{CANONICAL_URL}}", canonical)

    # 🔥 ALWAYS overwrite
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Generated:", slug)