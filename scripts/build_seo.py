import os
import re
import random
from datetime import datetime

KEYWORD_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"

OUTPUT_DIR = "scam-check-now"

SITE = "https://verixiaapps.github.io"

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+','-',text)
    return text.strip("-")

template = open(TEMPLATE_FILE).read()

keywords = open(KEYWORD_FILE).read().splitlines()

pages = []

for kw in keywords:

    slug = slugify(kw)

    pages.append({
        "keyword": kw,
        "slug": slug
    })


for page in pages:

    title = page["keyword"].title() + " | Scam Check Now"

    description = f"{page['keyword'].title()} tool. Check suspicious messages, emails, links or job offers for scam risk."

    # pick random internal links

    related = random.sample(pages, min(5, len(pages)))

    links = ""

    for r in related:

        if r["slug"] != page["slug"]:

            links += f'<li><a href="/scam-check-now/{r["slug"]}.html">{r["keyword"].title()}</a></li>\n'


    html = template

    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", page["keyword"])
    html = html.replace("{{RELATED_LINKS}}", links)

    filename = f"{OUTPUT_DIR}/{page['slug']}.html"

    with open(filename,"w") as f:

        f.write(html)

    print("generated", filename)