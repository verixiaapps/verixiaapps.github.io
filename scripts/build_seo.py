import os
import re
import random
from datetime import datetime
from generate_content import generate_content


KEYWORD_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"

OUTPUT_DIR = "scam-check-now"

SITE = "https://verixiaapps.com"

ALL_PAGES_FILE = f"{OUTPUT_DIR}/all-pages.html"
SITEMAP_FILE = f"{OUTPUT_DIR}/sitemap.xml"


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip("-")


def build_title(keyword):

    kw = keyword.lower().strip()

    # If keyword already contains "scam", remove it for cleaner titles
    if kw.endswith(" scam"):
        brand = kw.replace(" scam", "")
        return f"Is {brand.title()} a Scam? | Scam Check Now"

    return f"Is {kw.title()} a Scam? | Scam Check Now"


os.makedirs(OUTPUT_DIR, exist_ok=True)


with open(TEMPLATE_FILE, encoding="utf-8") as f:
    template = f.read()

with open(KEYWORD_FILE, encoding="utf-8") as f:
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

    folder = f"{OUTPUT_DIR}/{slug}"
    path = f"{folder}/index.html"

    os.makedirs(folder, exist_ok=True)

    if os.path.exists(path):
        print("skipping existing page:", slug)
        continue

    title = build_title(keyword)

    description = f"Is {keyword.title()} a scam? Use this free AI scam checker to analyze suspicious messages, emails, links, or job offers related to {keyword}."

    try:
        ai_text = generate_content(keyword)
    except:
        ai_text = f"{keyword.title()} scams often involve messages requesting payment, personal information, or urgent action. If you receive a suspicious message related to {keyword}, verify the sender and avoid clicking unknown links or sending money."

    related_candidates = [p for p in pages if p["slug"] != slug]

    related_pages = random.sample(
        related_candidates,
        min(5, len(related_candidates))
    )

    links = ""

    for r in related_pages:
        links += f'<li><a href="/scam-check-now/{r["slug"]}/">{r["keyword"].title()}</a></li>\n'


    html = template

    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{AI_CONTENT}}", ai_text)
    html = html.replace("{{RELATED_LINKS}}", links)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    generated.append(slug)

    print("generated:", slug)


links = ""

for page in pages:
    slug = page["slug"]
    title = page["keyword"].title()
    links += f'<div><a href="/scam-check-now/{slug}/">{title}</a></div>\n'


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


with open(ALL_PAGES_FILE, "w", encoding="utf-8") as f:
    f.write(all_pages_html)

print("updated all-pages.html")


today = datetime.utcnow().strftime("%Y-%m-%d")

sitemap_links = ""

for page in pages:

    slug = page["slug"]

    sitemap_links += f"""
<url>
<loc>{SITE}/scam-check-now/{slug}/</loc>
<lastmod>{today}</lastmod>
</url>
"""


sitemap_xml = f"""
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

{sitemap_links}

</urlset>
"""


with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
    f.write(sitemap_xml)

print("updated sitemap.xml")