Here is your revised file with ONLY the fix applied (6 most related, otherwise fill to 6):

import os
import re
from generate_content import generate_content

KEYWORDS_FILE = "data/keywords.txt"
TEMPLATE_FILE = "templates/seo-template.html"
OUTPUT_DIR = "scam-check-now"
SITE = "https://verixiaapps.com"
RELATED_LINKS_COUNT = 6

PROTECTED_SLUGS = {"is-this-a-scam"}


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
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


def keyword_tokens(text):
    return set(normalize_keyword(text).split())


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


def get_related_pages(current_page, all_pages, limit=RELATED_LINKS_COUNT):
    current_slug = current_page["slug"]
    current_keyword = current_page["keyword"]
    current_tokens = keyword_tokens(current_keyword)
    current_root = current_keyword.split()[0]

    valid_pages = [
        p for p in all_pages
        if p["slug"] != current_slug and p["slug"] not in PROTECTED_SLUGS
    ]

    def relevance_score(page):
        other_keyword = page["keyword"]
        other_tokens = keyword_tokens(other_keyword)
        same_root = 1 if other_keyword.split()[0] == current_root else 0
        shared_tokens = len(current_tokens & other_tokens)
        length_diff = abs(len(other_keyword) - len(current_keyword))
        return (-same_root, -shared_tokens, length_diff, other_keyword)

    ranked_pages = sorted(valid_pages, key=relevance_score)

    # take most related first
    selected = ranked_pages[:limit]

    # if not enough, fill with remaining pages
    if len(selected) < limit:
        for p in ranked_pages[limit:]:
            if p not in selected:
                selected.append(p)
            if len(selected) == limit:
                break

    return selected


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

    current_page = {"keyword": keyword, "slug": slug}
    related_pages = get_related_pages(current_page, all_pages, RELATED_LINKS_COUNT)

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

    all_pages = [
        {"keyword": k, "slug": slugify(k)}
        for k in keywords
        if slugify(k) not in PROTECTED_SLUGS
    ]

    for keyword in keywords:
        slug = slugify(keyword)

        if slug in PROTECTED_SLUGS:
            print(f"skipped protected page: {keyword}")
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