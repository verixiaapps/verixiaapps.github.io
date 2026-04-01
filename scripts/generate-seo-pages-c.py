import os
from datetime import datetime

BASE_DIR = "scam-check-now-c"
KEYWORD_FILE = "data/keywords_c.txt"
OUTPUT_LIMIT = 50  # pages per run

TEMPLATE_PATH = "templates/seo-template-c.html"


def load_keywords():
    if not os.path.exists(KEYWORD_FILE):
        return []

    with open(KEYWORD_FILE, "r", encoding="utf-8") as f:
        return [k.strip() for k in f.readlines() if k.strip()]


def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def slugify(text):
    return text.lower().replace(" ", "-").replace("/", "").strip()


def build_page(template, keyword):
    title = f"{keyword.title()} | Scam Check Now"
    description = f"Check if {keyword} is a scam. Identify warning signs, risk level, and what to do next."

    html = template
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{CANONICAL_URL}}", f"https://verixiaapps.com/check/{slugify(keyword)}/")
    html = html.replace("{{AI_CONTENT}}", f"{keyword} scams are increasing. Always verify before clicking links, sending money, or sharing information.")
    html = html.replace("{{RELATED_LINKS}}", "")
    html = html.replace("{{MORE_LINKS}}", "")

    return html


def save_page(slug, html):
    path = os.path.join(BASE_DIR, slug)
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def main():
    keywords = load_keywords()
    template = load_template()

    if not keywords:
        print("No keywords found.")
        return

    today = datetime.utcnow().strftime("%Y%m%d")

    count = 0

    for keyword in keywords:
        if count >= OUTPUT_LIMIT:
            break

        slug = slugify(keyword)
        html = build_page(template, keyword)
        save_page(slug, html)

        count += 1

    print(f"Generated {count} C pages.")


if __name__ == "__main__":
    main()