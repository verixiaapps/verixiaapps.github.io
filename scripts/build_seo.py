import os
import re
import random
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
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip("-")


def build_title(keyword):
    kw = keyword.lower().strip()
    if kw.endswith(" scam"):
        kw = kw.replace(" scam", "")
    return f"Is {kw.title()} a Scam? (Real Check & Warning Signs)"


def build_description(keyword):
    return (
        f"Is {keyword.title()} a scam or legit? Check warning signs, real risks, "
        f"and what to do next. Free AI scam checker for {keyword}."
    )


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def load_keywords():
    with open(KEYWORD_FILE, encoding="utf-8") as f:
        return list(dict.fromkeys([k.strip().lower() for k in f if k.strip()]))


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
<h2>Is {keyword.title()} a Scam?</h2>
<p>{keyword.title()} scams often involve requests for money, personal information, or urgent action.
Avoid clicking unknown links or sending funds. Always verify through official sources.</p>
"""

    # Related links (exclude itself + protected)
    related_candidates = [
        p for p in pages
        if p["slug"] != slug and p["slug"] not in PROTECTED_SLUGS
    ]

    random.shuffle(related_candidates)
    related_pages = related_candidates[:RELATED_LINKS_COUNT]

    links_html = "".join([
        f'<li><a href="/scam-check-now/{r["slug"]}/">Is {r["keyword"].title()} a Scam?</a></li>\n'
        for r in related_pages
    ])

    # Fill template
    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links_html)
    html = html.replace("{{CANONICAL_URL}}", canonical)

    # 🔥 ALWAYS overwrite (this is the key change)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Generated:", slug)