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
RELATED_LINKS_COUNT = 5  # number of internal links per page

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
        brand = kw.replace(" scam", "")
        return f"Is {brand.title()} a Scam? | Scam Check Now"
    return f"Is {kw.title()} a Scam? | Scam Check Now"

def build_description(keyword):
    return f"Is {keyword.title()} a scam? Use this free AI scam checker to analyze messages, emails, links, or job offers related to {keyword}."

# -----------------------------
# SETUP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

with open(KEYWORD_FILE, encoding="utf-8") as f:
    keywords = [k.strip() for k in f.readlines() if k.strip()]

pages = [{"keyword": k, "slug": slugify(k)} for k in keywords]

# -----------------------------
# GENERATE PAGES
# -----------------------------
generated = []

for page in pages:
    slug = page["slug"]
    keyword = page["keyword"]

    folder = f"{OUTPUT_DIR}/{slug}"
    path = f"{folder}/index.html"
    os.makedirs(folder, exist_ok=True)

    if os.path.exists(path):
        print("Skipping existing page:", slug)
        continue

    title = build_title(keyword)
    description = build_description(keyword)

    # Generate AI content with fallback
    try:
        ai_text = generate_content(keyword)
        # Optional: break AI content into paragraphs for readability
        ai_text = "\n\n".join([p.strip() for p in ai_text.split("\n") if p.strip()])
    except Exception as e:
        print("AI generation failed for", keyword, ":", e)
        ai_text = f"{keyword.title()} scams often involve messages requesting payment, personal information, or urgent action. Verify senders and avoid unknown links or money requests."

    # Pick related links
    related_candidates = [p for p in pages if p["slug"] != slug]
    related_pages = random.sample(related_candidates, min(RELATED_LINKS_COUNT, len(related_candidates)))
    links_html = "".join([f'<li><a href="/scam-check-now/{r["slug"]}/">{r["keyword"].title()}</a></li>\n' for r in related_pages])

    # Fill template
    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links_html)

    # Write page
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    generated.append(slug)
    print("Generated:", slug)

# -----------------------------
# ALL-PAGES LIST
# -----------------------------
all_links = "".join([f'<div><a href="/scam-check-now/{p["slug"]}/">{p["keyword"].title()}</a></div>\n' for p in pages])
all_pages_html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Scam Check Pages</title>
<meta name="robots" content="index, follow">
</head>
<body>
<h1>Scam Check Pages</h1>
{all_links}
</body>
</html>
"""
with open(ALL_PAGES_FILE, "w", encoding="utf-8") as f:
    f.write(all_pages_html)
print("Updated all-pages.html")

# -----------------------------
# SITEMAP
# -----------------------------
today = datetime.utcnow().strftime("%Y-%m-%d")
sitemap_links = "".join([f"""
<url>
<loc>{SITE}/scam-check-now/{p['slug']}/</loc>
<lastmod>{today}</lastmod>
</url>
""" for p in pages])

sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_links}
</urlset>
"""

with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
    f.write(sitemap_xml)
print("Updated sitemap.xml")