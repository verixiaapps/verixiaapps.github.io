import os

import re

import sys

import json

from collections import Counter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if BASE_DIR not in sys.path:

    sys.path.append(BASE_DIR)

from data.token_cluster_map import TOKEN_CLUSTERS

KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "token_keywords.txt")

OUTPUT_DIR = os.path.join(BASE_DIR, "token-risk")

SITE = "https://verixiaapps.com"

MAX_LINKS_PER_HUB = 50

REPORT_PATH = os.path.join(OUTPUT_DIR, "_token_hub_build_report.json")

# ✅ NEW: protect hubs + enforce valid child pages

PROTECTED_HUB_SLUGS = set(TOKEN_CLUSTERS.keys())

def compact_spaces(text):

    return re.sub(r"\s+", " ", str(text)).strip()

def normalize_keyword(text):

    return compact_spaces(str(text).lower())

def slugify(text):

    return re.sub(r"[^a-z0-9]+", "-", normalize_keyword(text)).strip("-")

def load_keywords():

    if not os.path.exists(KEYWORDS_FILE):

        return []

    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:

        return list(dict.fromkeys(normalize_keyword(line) for line in f if line.strip()))

def page_path(slug):

    return os.path.join(OUTPUT_DIR, slug, "index.html")

def page_exists(slug):

    return os.path.exists(page_path(slug))

def build_canonical(slug):

    return f"{SITE}/token-risk/{slug}/"

def trim_meta_description(text, minimum=110, maximum=165):

    text = compact_spaces(text)

    if len(text) <= maximum:

        return text

    truncated = text[: maximum]

    return truncated.rstrip(" ,;.") + "."

def title_case(text):

    return " ".join(word.capitalize() for word in text.split())

def escape_html(text):

    return (

        str(text)

        .replace("&", "&amp;")

        .replace('"', "&quot;")

        .replace("<", "&lt;")

        .replace(">", "&gt;")

    )

# -------------------------

# MATCHING + SCORING

# -------------------------

def matches_cluster(keyword, terms):

    kw = normalize_keyword(keyword)

    return any(term in kw for term in terms)

def score_keyword(keyword):

    return (len(keyword), keyword)

# -------------------------

# LINK BUILDER (FIXED)

# -------------------------

def build_related_link_items(cluster_keywords, valid_child_slugs):

    items = []

    seen = set()

    for keyword in cluster_keywords:

        slug = slugify(keyword)

        # ✅ FIXED: strict filtering

        if (

            not slug

            or slug in seen

            or slug in PROTECTED_HUB_SLUGS

            or slug not in valid_child_slugs

            or not page_exists(slug)

        ):

            continue

        seen.add(slug)

        label = title_case(keyword)

        items.append({

            "slug": slug,

            "href": f"/token-risk/{slug}/",

            "anchor": f"{label} Token Risk"

        })

    return items

# -------------------------

# HTML

# -------------------------

def build_hub_html(slug, title, description, links):

    canonical = build_canonical(slug)

    links_html = "\n".join(

        f'<li><a href="{escape_html(l["href"])}">{escape_html(l["anchor"])}</a></li>'

        for l in links

    )

    return f"""<!DOCTYPE html>

<html>

<head>

<title>{escape_html(title)}</title>

<meta name="description" content="{escape_html(description)}">

<link rel="canonical" href="{canonical}">

</head>

<body>

<h1>{escape_html(title)}</h1>

<p>Compare token risk patterns and warning signs before buying.</p>

<h2>Related Checks</h2>

<ul>

{links_html}

</ul>

</body>

</html>

"""

# -------------------------

# VALIDATION (LESS NOISE)

# -------------------------

def validate_hub(slug, description, html):

    errors = []

    if len(description) < 100:

        errors.append("weak description")

    if "<h1>" not in html:

        errors.append("missing h1")

    if "<ul>" not in html:

        errors.append("no links section")

    return errors

# -------------------------

# MAIN

# -------------------------

def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    keywords = load_keywords()

    # ✅ NEW: define valid child pages

    valid_child_slugs = {slugify(k) for k in keywords}

    valid_child_slugs -= PROTECTED_HUB_SLUGS

    built = 0

    warnings = []

    for hub_slug, terms in TOKEN_CLUSTERS.items():

        matched = [k for k in keywords if matches_cluster(k, terms)]

        matched = sorted(matched, key=score_keyword)[:MAX_LINKS_PER_HUB]

        link_items = build_related_link_items(matched, valid_child_slugs)

        # ✅ improved fallback title

        title = f"{title_case(hub_slug.replace('-', ' '))}: Warning Signs, Related Checks & What To Know"

        description = trim_meta_description(

            "Review token risk warning signs, patterns, and related checks before you buy, swap, or trust a token."

        )

        html = build_hub_html(hub_slug, title, description, link_items)

        errors = validate_hub(hub_slug, description, html)

        if errors:

            warnings.append({"hub": hub_slug, "errors": errors})

        folder = os.path.join(OUTPUT_DIR, hub_slug)

        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:

            f.write(html)

        built += 1

        print(f"Built {hub_slug} | links: {len(link_items)}")

    report = {

        "keywords": len(keywords),

        "built": built,

        "warnings": warnings

    }

    with open(REPORT_PATH, "w") as f:

        json.dump(report, f, indent=2)

    print("\nDONE")

    print(report)

if __name__ == "__main__":

    main()