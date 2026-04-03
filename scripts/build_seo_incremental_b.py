import json
import os
from generate_content import generate_content

BASE_DIR = "scam-check-now-c"
KEYWORD_FILE = "data/keywords_c.txt"
GENERATED_KEYWORDS_FILE = "data/generated_keywords_c.txt"
GENERATED_SLUGS_FILE = "data/generated_slugs_c.txt"
SLUG_TO_HUB_FILE = "data/slug_to_hub_c.json"

OUTPUT_LIMIT = int(os.getenv("PAGE_LIMIT", "50"))
REBUILD_ALL = os.getenv("REBUILD_ALL", "false").lower() == "true"

TEMPLATE_PATH = "templates/seo-template-c.html"
SITE = "https://verixiaapps.com"
URL_PREFIX = "/scam-check-now-c"
HUB_PREFIX = "/scam-check-now-c/hubs"

DEFAULT_HUB_RULES = {
    "job-scams": ["job", "hiring", "recruiter", "interview", "offer"],
    "crypto-scams": ["crypto", "bitcoin", "wallet", "ethereum", "nft"],
    "email-scams": ["email", "mail"],
    "text-scams": ["text", "sms", "message"],
    "brand-scams": ["paypal", "amazon", "apple", "google", "bank", "venmo", "zelle"],
    "payment-scams": ["payment", "gift", "card", "transfer", "refund"],
    "general-scams": [],
}


def load_file_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def save_file_lines(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if lines:
            f.write("\n".join(lines) + "\n")
        else:
            f.write("")


def append_file_line(path, line):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ensure_file_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("")


def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def load_slug_to_hub():
    if not os.path.exists(SLUG_TO_HUB_FILE):
        return {}
    with open(SLUG_TO_HUB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {str(k).strip(): str(v).strip() for k, v in data.items() if str(k).strip() and str(v).strip()}


def slugify(text):
    return (
        str(text).lower()
        .replace("'", "")
        .replace('"', "")
        .replace("/", "")
        .replace(":", "")
        .replace("?", "")
        .replace(",", "")
        .replace(".", "")
        .replace("&", " and ")
        .replace("  ", " ")
        .strip()
        .replace(" ", "-")
    )


def pretty_hub_title(hub_name):
    return hub_name.replace("-", " ").title()


def build_title(keyword):
    return f"{keyword.title()} | Scam Check Now"


def build_description(keyword):
    return f"Check if {keyword} is a scam. Identify warning signs, risk level, and what to do next."


def build_internal_links(existing_slugs, current_slug, limit=12):
    links = []
    used = set()

    for slug in existing_slugs:
        if slug == current_slug or slug in used or slug == "hubs":
            continue

        used.add(slug)
        text = slug.replace("-", " ")
        url = f"{URL_PREFIX}/{slug}/"
        links.append(f'<li><a href="{url}">{text.title()}</a></li>')

        if len(links) >= limit:
            break

    return "\n".join(links)


def infer_hub_name(keyword):
    keyword = keyword.lower()

    best = ""
    best_score = -1

    for hub, terms in DEFAULT_HUB_RULES.items():
        score = 0
        for term in terms:
            if term in keyword:
                score += 1

        if score > best_score:
            best_score = score
            best = hub

    if best_score > 0:
        return best

    return "general-scams"


def build_hub_link_html(slug, keyword, slug_to_hub):
    hub_name = slug_to_hub.get(slug)

    if not hub_name:
        hub_name = infer_hub_name(keyword)
        if hub_name:
            slug_to_hub[slug] = hub_name

    if not hub_name:
        return ""

    hub_title = pretty_hub_title(hub_name)
    hub_url = f"{SITE}{HUB_PREFIX}/{hub_name}/"
    return f'<a href="{hub_url}">{hub_title}</a>'


def build_page(template, keyword, ai_content, related_links, more_links, hub_link_html):
    slug = slugify(keyword)

    html = template
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{TITLE}}", build_title(keyword))
    html = html.replace("{{DESCRIPTION}}", build_description(keyword))
    html = html.replace("{{CANONICAL_URL}}", f"{SITE}{URL_PREFIX}/{slug}/")
    html = html.replace("{{AI_CONTENT}}", ai_content)
    html = html.replace("{{RELATED_LINKS}}", related_links)
    html = html.replace("{{MORE_LINKS}}", more_links)
    html = html.replace("{{HUB_LINK}}", hub_link_html)

    return html


def save_page(slug, html):
    path = os.path.join(BASE_DIR, slug)
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ensure_file_exists(GENERATED_KEYWORDS_FILE)
    ensure_file_exists(GENERATED_SLUGS_FILE)
    ensure_file_exists(SLUG_TO_HUB_FILE)

    keywords = load_file_lines(KEYWORD_FILE)
    template = load_template()
    slug_to_hub = load_slug_to_hub()

    if REBUILD_ALL:
        print("REBUILD_ALL=true -> resetting generated tracking files")
        save_file_lines(GENERATED_KEYWORDS_FILE, [])
        save_file_lines(GENERATED_SLUGS_FILE, [])

    generated_keywords = set(load_file_lines(GENERATED_KEYWORDS_FILE))
    generated_slugs = load_file_lines(GENERATED_SLUGS_FILE)

    if not keywords:
        print("No keywords found.")
        return

    count = 0
    remaining_keywords = []

    for keyword in keywords:
        if count >= OUTPUT_LIMIT:
            remaining_keywords.append(keyword)
            continue

        if not REBUILD_ALL and keyword in generated_keywords:
            continue

        slug = slugify(keyword)

        if not slug:
            continue

        if not REBUILD_ALL and slug in generated_slugs:
            continue

        try:
            print(f"Generating: {keyword}")

            related_links = build_internal_links(generated_slugs, slug, limit=10)
            more_links = build_internal_links(list(reversed(generated_slugs)), slug, limit=10)
            ai_content = generate_content(keyword)
            hub_link_html = build_hub_link_html(slug, keyword, slug_to_hub)

            html = build_page(
                template,
                keyword,
                ai_content,
                related_links,
                more_links,
                hub_link_html
            )

            save_page(slug, html)

            if keyword not in generated_keywords:
                append_file_line(GENERATED_KEYWORDS_FILE, keyword)
                generated_keywords.add(keyword)

            if slug not in generated_slugs:
                append_file_line(GENERATED_SLUGS_FILE, slug)
                generated_slugs.append(slug)

            count += 1

        except Exception as e:
            print(f"Failed: {keyword} -> {e}")
            remaining_keywords.append(keyword)

    save_file_lines(KEYWORD_FILE, remaining_keywords)

    with open(SLUG_TO_HUB_FILE, "w", encoding="utf-8") as f:
        json.dump(slug_to_hub, f, indent=2, sort_keys=True)

    print(f"Generated {count} C pages.")
    print(f"Loaded slug-to-hub mappings: {len(slug_to_hub)}")


if __name__ == "__main__":
    main()