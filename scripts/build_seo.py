import os
import re
from datetime import datetime

KEYWORD_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"

OUTPUT_DIR = "scam-check-now"

ALL_PAGES = f"{OUTPUT_DIR}/all-pages.html"
SITEMAP = f"{OUTPUT_DIR}/sitemap.xml"

SITE = "https://verixiaapps.github.io"


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+','-',text)
    return text.strip("-")


template = open(TEMPLATE_FILE).read()

keywords = open(KEYWORD_FILE).read().splitlines()

generated_pages = []

for kw in keywords:

    slug = slugify(kw)

    filename = f"{slug}.html"

    title = kw.title() + " | Scam Check Now"

    description = f"{kw.title()} tool. Check suspicious messages, emails, links and offers for scam risk using AI scam detection."

    page = template.replace("{{TITLE}}", title)
    page = page.replace("{{DESCRIPTION}}", description)
    page = page.replace("{{KEYWORD}}", kw)

    path = os.path.join(OUTPUT_DIR, filename)

    with open(path,"w") as f:
        f.write(page)

    generated_pages.append(filename)

    print("generated", filename)



# build all-pages.html

links = ""

for page in generated_pages:

    links += f'<div><a href="/scam-check-now/{page}">{page.replace("-"," ").replace(".html","").title()}</a></div>\n'


all_pages_html = f"""
<!DOCTYPE html>
<html>

<head>
<title>Scam Check Pages</title>
<meta name="robots" content="index, follow">
</head>

<body>

<h1>Scam Check Tools</h1>

{links}

</body>

</html>
"""

with open(ALL_PAGES,"w") as f:
    f.write(all_pages_html)

print("updated all-pages.html")



# build sitemap

sitemap_links = ""

today = datetime.utcnow().strftime("%Y-%m-%d")

for page in generated_pages:

    sitemap_links += f"""
<url>
<loc>{SITE}/scam-check-now/{page}</loc>
<lastmod>{today}</lastmod>
</url>
"""


sitemap_xml = f"""
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

{sitemap_links}

</urlset>
"""

with open(SITEMAP,"w") as f:
    f.write(sitemap_xml)

print("updated sitemap.xml")