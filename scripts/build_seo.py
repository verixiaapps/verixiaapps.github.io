import os
import re
import random
from datetime import datetime
from generate_content import generate_content

# -----------------------------
# CONFIGURATION
# -----------------------------
KEYWORD_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"
OUTPUT_DIR = "scam-check-now"
SITE = "https://verixiaapps.com"
ALL_PAGES_FILE = f"{OUTPUT_DIR}/all-pages.html"
SITEMAP_FILE = f"{OUTPUT_DIR}/sitemap.xml"
RELATED_LINKS_COUNT = 5

# 🔒 PROTECTED SLUGS (DO NOT TOUCH)
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

# 🚫 Filter out protected slugs EARLY
pages = [
    {"keyword": k, "slug": slugify(k)}
    for k in keywords
    if slugify(k) not in PROTECTED_SLUGS
]

# -----------------------------
# GENERATE PAGES
# -----------------------------
generated = []

for page in pages:
    slug = page["slug"]
    keyword = page["keyword"]

    # 🔒 Double protection (never touch it)
    if slug in PROTECTED_SLUGS:
        print("Skipping protected page:", slug)
        continue

    folder = f"{OUTPUT_DIR}/{slug}"
    path = f"{folder}/index.html"
    os.makedirs(folder, exist_ok=True)

    if os.path.exists(path):
        print("Skipping existing page:", slug)
        continue

    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    try:
        ai_text = generate_content(keyword)
    except Exception as e:
        print("AI generation failed for", keyword, ":", e)
        ai_text = f"""
<h2>Is {keyword.title()} a Scam?</h2>
<p>{keyword.title()} scams often involve messages requesting payment, personal information, or urgent action. 
Avoid clicking unknown links or sending money. Always verify through official sources.</p>
"""

    # Internal linking (exclude protected pages automatically)
    related_candidates = [p for p in pages if p["slug"] != slug]
    random.shuffle(related_candidates)
    related_pages = related_candidates[:RELATED_LINKS_COUNT]

    links_html = "".join([
        f'<li><a href="/scam-check-now/{r["slug"]}/">Is {r["keyword"].title()} a Scam?</a></li>\n'
        for r in related_pages
    ])

    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links_html)
    html = html.replace("{{CANONICAL_URL}}", canonical)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    generated.append(slug)
    print("Generated:", slug)

# -----------------------------
# ALL-PAGES LIST
# -----------------------------
all_links = "".join([
    f'<div><a href="/scam-check-now/{p["slug"]}/">{p["keyword"].title()}</a></div>\n'
    for p in pages
])

all_pages_html = f"""
<!DOCTYPE html>
<html>
<head>
<title>All Scam Pages</title>
<meta name="robots" content="noindex, follow">
</head>
<body>
<h1>All Scam Check Pages</h1>
{all_links}
</body>
</html>
"""

with open(ALL_PAGES_FILE, "w", encoding="utf-8") as f:
    f.write(all_pages_html)

print("Updated all-pages.html")

# -----------------------------
# SITEMAP (protected pages excluded)
# -----------------------------
today = datetime.utcnow().strftime("%Y-%m-%d")

sitemap_links = "".join([
    f"""
<url>
  <loc>{SITE}/scam-check-now/{p['slug']}/</loc>
  <lastmod>{today}</lastmod>
</url>
"""
    for p in pages
])

sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_links}
</urlset>
"""

with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
    f.write(sitemap_xml)

print("Updated sitemap.xml")