import os
import re
import random
from datetime import datetime

KEYWORD_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"
CONTENT_DIR = "data/content"

OUTPUT_DIR = "scam-check-now"

SITE = "https://verixiaapps.github.io"

ALL_PAGES_FILE = f"{OUTPUT_DIR}/all-pages.html"
SITEMAP_FILE = f"{OUTPUT_DIR}/sitemap.xml"


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip("-")


# ensure folders exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CONTENT_DIR, exist_ok=True)


with open(TEMPLATE_FILE) as f:
    template = f.read()

with open(KEYWORD_FILE) as f:
    keywords = [k.strip() for k in f.readlines() if k.strip()]


pages = []

for kw in keywords:
    slug = slugify(kw)
    pages.append({
        "keyword": kw,
        "slug": slug
    })


generated = []


for page in pages:

    slug = page["slug"]
    keyword = page["keyword"]

    filename = f"{slug}.html"
    path = f"{OUTPUT_DIR}/{filename}"

    title = keyword.title() + " | Scam Check Now"

    description = f"{keyword.title()} tool. Check suspicious messages, emails, links or job offers for scam risk."

    # AI CONTENT
    content_path = f"{CONTENT_DIR}/{slug}.txt"

    if os.path.exists(content_path):
        with open(content_path) as f:
            ai_text = f.read()
    else:
        ai_text = ""

    # RELATED LINKS
    related_candidates = [p for p in pages if p["slug"] != slug]

    related_pages = random.sample(
        related_candidates,
        min(5, len(related_candidates))
    )

    links = ""

    for r in related_pages:
        links += f'<li><a href="/scam-check-now/{r["slug"]}.html">{r["keyword"].title()}</a></li>\n'


    html = template

    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links)

    with open(path, "w") as f:
        f.write(html)

    generated.append(filename)

    print("generated:", filename)


# BUILD ALL-PAGES HUB

links = ""

for page in pages:
    slug = page["slug"]
    title = page["keyword"].title()
    links += f'<div><a href="/scam-check-now/{slug}.html">{title}</a></div>\n'


all_pages_html = f"""
<!DOCTYPE html>
<html>

<head>
<title>Scam Check Pages</title>
<meta name="robots" content="index, follow">
</head>

<body>

<h1>Scam Check Pages</h1>

{links}

</body>

</html>
"""

with open(ALL_PAGES_FILE, "w") as f:
    f.write(all_pages_html)

print("updated all-pages.html")


# BUILD SITEMAP

today = datetime.utcnow().strftime("%Y-%m-%d")

sitemap_links = ""

for page in pages:
    slug = page["slug"]

    sitemap_links += f"""
<url>
<loc>{SITE}/scam-check-now/{slug}.html</loc>
<lastmod>{today}</lastmod>
</url>
"""

sitemap_xml = f"""
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

{sitemap_links}

</urlset>
"""

with open(SITEMAP_FILE, "w") as f:
    f.write(sitemap_xml)

print("updated sitemap.xml")