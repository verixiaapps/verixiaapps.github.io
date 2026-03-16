import os
import re
from generate_content import generate_content

KEYWORDS_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"
OUTPUT_DIR = "scam-check-now"


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


def build_page(keyword, template):

    slug = slugify(keyword)

    content = generate_content(keyword)

    title = keyword.title()

    html = template.replace("{{TITLE}}", title)
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{CONTENT}}", content)

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

    for keyword in keywords:

        slug = slugify(keyword)

        page_path = os.path.join(OUTPUT_DIR, slug, "index.html")

        if os.path.exists(page_path):
            print("skip existing", keyword)
            continue

        try:

            slug, html = build_page(keyword, template)

            save_page(slug, html)

            print("generated page for", keyword)

        except Exception as e:

            print("error generating page for", keyword)
            print(e)


if __name__ == "__main__":
    main()