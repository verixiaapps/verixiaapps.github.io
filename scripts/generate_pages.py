import os
import re
import random
from generate_content import generate_content

KEYWORDS_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"
OUTPUT_DIR = "scam-check-now"
SITE = "https://verixiaapps.com"


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip("-")


def load_keywords():
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return [k.strip() for k in f if k.strip()]


def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()


def build_title(keyword):
    kw = keyword.lower().strip()
    if kw.endswith(" scam"):
        kw = kw.replace(" scam", "")
    return f"Is {kw.title()} a Scam? | Scam Check Now"


def build_description(keyword):
    return f"Is {keyword.title()} a scam? Use this free AI scam checker to analyze suspicious messages, emails, links, or job offers related to {keyword}."


def build_page(keyword, template, all_pages):
    slug = slugify(keyword)

    # Generate AI content with fallback
    try:
        content = generate_content(keyword)
    except:
        content = f"{keyword.title()} scams often involve messages requesting payment, personal information, or urgent action. If you receive a suspicious message related to {keyword}, verify the sender and avoid clicking unknown links or sending money."

    title = build_title(keyword)
    description = build_description(keyword)

    # Select related links
    related_candidates = [p for p in all_pages if p["slug"] != slug]
    related_pages = random.sample(related_candidates, min(5, len(related_candidates)))
    related_links = "\n".join(
        f'<li><a href="/scam-check-now/{r["slug"]}/">{r["keyword"].title()}</a></li>' for r in related_pages
    )

    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{AI_CONTENT}}", content)
    html = html.replace("{{RELATED_LINKS}}", related_links)

    return slug, html


def save_page(slug, html):
    folder = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, "index.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    keywords = load_keywords()
    template = load_template()

    # Prepare all pages for related links
    all_pages = [{"keyword": k, "slug": slugify(k)} for k in keywords]

    for keyword in keywords:
        slug = slugify(keyword)
        page_path = os.path.join(OUTPUT_DIR, slug, "index.html")

        if os.path.exists(page_path):
            print(f"skipped existing page: {keyword}")
            continue

        try:
            slug, html = build_page(keyword, template, all_pages)
            save_page(slug, html)
            print(f"generated page for: {keyword}")
        except Exception as e:
            print(f"error generating page for: {keyword}")
            print(e)


if __name__ == "__main__":
    main()