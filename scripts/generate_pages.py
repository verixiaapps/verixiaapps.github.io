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


def normalize_keyword(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def display_keyword(text):
    kw = normalize_keyword(text)
    if kw.endswith(" scam"):
        kw = kw[:-5].strip()
    return kw


def title_case(text):
    return " ".join(word.capitalize() for word in text.split())


def load_keywords():
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return list(dict.fromkeys([normalize_keyword(k) for k in f if k.strip()]))


def load_template():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()


def build_title(keyword):
    kw = title_case(display_keyword(keyword))
    return f"Is {kw} a Scam? (Real Check & Warning Signs)"


def build_description(keyword):
    keyword_title = title_case(normalize_keyword(keyword))
    return (
        f"Is {keyword_title} a scam or legit? Check real risk signals, warning signs, "
        f"and what to do next. Free AI scam checker for {normalize_keyword(keyword)} messages, emails, or links."
    )


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def build_page(keyword, template, all_pages):
    slug = slugify(keyword)
    keyword_display = display_keyword(keyword)

    try:
        content = generate_content(keyword)
    except Exception:
        content = (
            f"<p>{title_case(normalize_keyword(keyword))} scams are commonly used to trick people into sending money or sharing sensitive information. "
            f"If you receive a message related to {normalize_keyword(keyword)}, avoid clicking unknown links, do not send payments, "
            f"and verify the source through official channels. Scammers often create urgency or impersonate trusted brands.</p>"
        )

    title = build_title(keyword)
    description = build_description(keyword)
    canonical = build_canonical(slug)

    related_candidates = [p for p in all_pages if p["slug"] != slug]
    random.shuffle(related_candidates)
    related_pages = related_candidates[:5]

    related_links = "\n".join(
        f'<li><a href="/scam-check-now/{r["slug"]}/">Is {title_case(display_keyword(r["keyword"]))} a Scam?</a></li>'
        for r in related_pages
    )

    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{KEYWORD}}", keyword_display)
    html = html.replace("{{AI_CONTENT}}", content)
    html = html.replace("{{RELATED_LINKS}}", related_links)
    html = html.replace("{{CANONICAL_URL}}", canonical)

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