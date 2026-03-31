import os
import re
import sys
import json
from collections import Counter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from data.cluster_map import CLUSTERS

KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "generated_keywords.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "scam-check-now-b")
SITE = "https://verixiaapps.com"

MAX_LINKS_PER_HUB = 50
TOP_SCAM_TYPES_COUNT = 8
MAX_RELATED_TOPICS = 10
MAX_FAQS = 4
MAX_COMMON_SITUATIONS = 5
MAX_COMPARISON_POINTS = 4
MAX_PATTERN_EXAMPLES = 4
REPORT_PATH = os.path.join(OUTPUT_DIR, "_hub_build_report.json")
def compact_spaces(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def normalize_keyword(text):
    return compact_spaces(str(text).lower())


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", normalize_keyword(text)).strip("-")


def keyword_tokens(text):
    return set(normalize_keyword(text).replace("-", " ").split())


def normalize_term_tokens(text):
    return set(normalize_keyword(text).replace("-", " ").split())
    def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        return []

    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return list(dict.fromkeys(normalize_keyword(line) for line in f if line.strip()))


def matches_cluster(keyword, match_terms):
    kw_norm = normalize_keyword(keyword)
    kw_tokens = keyword_tokens(keyword)
    kw_joined = f" {kw_norm.replace('-', ' ')} "

    for term in match_terms:
        term_norm = normalize_keyword(term)
        term_tokens = normalize_term_tokens(term)
        term_joined = f" {term_norm.replace('-', ' ')} "

        if term_tokens and term_tokens.issubset(kw_tokens):
            return True
        if term_joined.strip() and term_joined in kw_joined:
            return True

    return False
    def score_keyword(keyword, hub_terms):
    kw = normalize_keyword(keyword)
    kw_tokens = keyword_tokens(kw)
    score = 0

    if "scam" in kw_tokens:
        score += 4
    if "legit" in kw_tokens:
        score += 4
    if "review" in kw_tokens:
        score += 3
    if "warning" in kw_tokens or "risk" in kw_tokens:
        score += 3
    if {"email", "text", "message"} & kw_tokens:
        score += 2
    if {"link", "login", "verification"} & kw_tokens:
        score += 2
    if kw.startswith("is ") or kw.startswith("is this "):
        score += 1

    return (-score, len(kw), kw)
    def build_related_link_items(cluster_keywords):
    items = []
    seen = set()

    for keyword in cluster_keywords:
        slug = slugify(keyword)
        if not slug or slug in seen:
            continue

        seen.add(slug)
        label = keyword.title()
        anchor = label if label.lower().endswith("scam") else f"{label} Scam Check"

        items.append({
            "slug": slug,
            "title": label,
            "href": f"/scam-check-now-b/{slug}/",
            "anchor": anchor,
        })

    return items
    def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    keywords = load_keywords()
    built_count = 0

    for hub_slug, match_terms in CLUSTERS.items():
        matched = [kw for kw in keywords if matches_cluster(kw, match_terms)]
        matched = sorted(matched, key=lambda k: score_keyword(k, match_terms))[:MAX_LINKS_PER_HUB]

        link_items = build_related_link_items(matched)

        print(f"Built hub: {hub_slug} (matched: {len(matched)}, links: {len(link_items)})")
        built_count += 1

    print("\n--- HUB BUILD COMPLETE ---")
    print(f"Hubs built: {built_count}")


if __name__ == "__main__":
    main()