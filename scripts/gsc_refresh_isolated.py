import os
import html
from typing import Dict, List, Set, Tuple

TARGET_TEMPLATE = os.getenv("TARGET_TEMPLATE", "all").strip().lower()
REFRESH_SCOPE = os.getenv("REFRESH_SCOPE", "internal-links").strip().lower()
MAX_URLS = int(os.getenv("MAX_URLS_TO_REFRESH", "10"))
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"

TEMPLATE_PATHS: Dict[str, str] = {
    "a": "scam-check-now",
    "b": "scam-check-now-b",
    "c": "scam-check-now-c",
}

TARGET_PAGE_SPECS: List[Dict[str, str]] = [
    {"slug": "is-recruiter-email-from-unknown-company-legit-or-scam", "cluster": "job"},
    {"slug": "is-venmo-security-alert-email-legit-or-scam", "cluster": "security"},
    {"slug": "is-fedex-customs-charge-email-legit-or-scam", "cluster": "delivery"},
    {"slug": "is-amazon-refund-message-legit-or-scam", "cluster": "refund"},
    {"slug": "is-google-account-disabled-email-legit-or-scam", "cluster": "security"},
    {"slug": "is-fedex-package-reroute-email-legit-or-scam", "cluster": "delivery"},
    {"slug": "is-google-security-warning-email-legit-or-scam", "cluster": "security"},
    {"slug": "is-security-alert-message-legit-or-scam", "cluster": "security"},
    {"slug": "is-fedex-delivery-legit-or-scam", "cluster": "delivery"},
    {"slug": "is-apple-account-verification-email-legit-or-scam", "cluster": "security"},
]

TODAY_TARGET_SLUGS: List[str] = [item["slug"] for item in TARGET_PAGE_SPECS]
CLUSTER_BY_SLUG: Dict[str, str] = {item["slug"]: item["cluster"] for item in TARGET_PAGE_SPECS}

SPECIAL_REPLACEMENTS = {
    "usps": "USPS",
    "ups": "UPS",
    "fedex": "FedEx",
    "amazon": "Amazon",
    "google": "Google",
    "apple": "Apple",
    "id": "ID",
    "whatsapp": "WhatsApp",
    "telegram": "Telegram",
    "snapchat": "Snapchat",
    "venmo": "Venmo",
    "paypal": "PayPal",
    "zelle": "Zelle",
    "gmail": "Gmail",
    "tiktok": "TikTok",
    "ssn": "SSN",
}

STRIP_WORDS = {
    "is",
    "this",
    "a",
    "an",
    "the",
    "or",
    "and",
    "legit",
    "scam",
    "real",
    "fake",
}

LOWERCASE_LINK_WORDS = {"a", "an", "and", "or", "the", "from"}

TITLE_MAP = {
    "is-recruiter-email-from-unknown-company-legit-or-scam": "Recruiter Email From Unknown Company: Legit or Scam Warning Signs",
    "is-venmo-security-alert-email-legit-or-scam": "Venmo Security Alert Email: Legit or Scam Warning Signs",
    "is-fedex-customs-charge-email-legit-or-scam": "FedEx Customs Charge Email: Legit or Scam Warning Signs",
    "is-amazon-refund-message-legit-or-scam": "Amazon Refund Message: Legit or Scam Warning Signs",
    "is-google-account-disabled-email-legit-or-scam": "Google Account Disabled Email: Legit or Scam Warning Signs",
    "is-fedex-package-reroute-email-legit-or-scam": "FedEx Package Reroute Email: Legit or Scam Warning Signs",
    "is-google-security-warning-email-legit-or-scam": "Google Security Warning Email: Legit or Scam Warning Signs",
    "is-security-alert-message-legit-or-scam": "Security Alert Message: Legit or Scam Warning Signs",
    "is-fedex-delivery-legit-or-scam": "FedEx Delivery Message: Legit or Scam Warning Signs",
    "is-apple-account-verification-email-legit-or-scam": "Apple Account Verification Email: Legit or Scam Warning Signs",
}

DESCRIPTION_MAP = {
    "is-recruiter-email-from-unknown-company-legit-or-scam": "Got a recruiter email from an unknown company? Learn warning signs, fake hiring patterns, and what to do before replying or sharing personal information.",
    "is-venmo-security-alert-email-legit-or-scam": "Got a Venmo security alert email? Learn fake alert warning signs, phishing risks, and what to do before clicking or replying.",
    "is-fedex-customs-charge-email-legit-or-scam": "Got a FedEx customs charge email? Learn payment scam warning signs, fake shipping patterns, and what to do before paying.",
    "is-amazon-refund-message-legit-or-scam": "Got an Amazon refund message? Learn warning signs, fake refund link risks, and what to do before you click, reply, or send information.",
    "is-google-account-disabled-email-legit-or-scam": "Received a Google account disabled email? Learn warning signs of fake account alerts and how to verify safely.",
    "is-fedex-package-reroute-email-legit-or-scam": "Got a FedEx package reroute email? Learn scam warning signs, fake tracking risks, and what to do before clicking.",
    "is-google-security-warning-email-legit-or-scam": "Got a Google security warning email? Learn warning signs of phishing alerts and what to do before taking action.",
    "is-security-alert-message-legit-or-scam": "Received a security alert message? Learn how to spot fake alerts, suspicious links, and what to do next.",
    "is-fedex-delivery-legit-or-scam": "Got a FedEx delivery message? Learn scam signs, fake tracking links, and what to do before clicking.",
    "is-apple-account-verification-email-legit-or-scam": "Received an Apple account verification email? Learn warning signs, phishing risks, and what to check before clicking.",
}

CLUSTER_SUPPORT: Dict[str, List[str]] = {
    "job": [
        "is-recruiter-email-from-unknown-company-legit-or-scam",
        "is-security-alert-message-legit-or-scam",
        "is-google-account-disabled-email-legit-or-scam",
    ],
    "security": [
        "is-venmo-security-alert-email-legit-or-scam",
        "is-google-account-disabled-email-legit-or-scam",
        "is-google-security-warning-email-legit-or-scam",
        "is-security-alert-message-legit-or-scam",
        "is-apple-account-verification-email-legit-or-scam",
    ],
    "delivery": [
        "is-fedex-delivery-legit-or-scam",
        "is-fedex-customs-charge-email-legit-or-scam",
        "is-fedex-package-reroute-email-legit-or-scam",
    ],
    "refund": [
        "is-amazon-refund-message-legit-or-scam",
        "is-security-alert-message-legit-or-scam",
        "is-google-account-disabled-email-legit-or-scam",
    ],
}


def get_target_dirs() -> List[str]:
    if TARGET_TEMPLATE == "all":
        return [TEMPLATE_PATHS["a"], TEMPLATE_PATHS["b"], TEMPLATE_PATHS["c"]]
    if TARGET_TEMPLATE not in TEMPLATE_PATHS:
        raise ValueError(f"Invalid TARGET_TEMPLATE: {TARGET_TEMPLATE}")
    return [TEMPLATE_PATHS[TARGET_TEMPLATE]]


def get_target_slugs() -> List[str]:
    if MAX_URLS <= 0:
        raise ValueError(f"Invalid MAX_URLS_TO_REFRESH: {MAX_URLS}")
    return TODAY_TARGET_SLUGS[:MAX_URLS]


def is_allowed_seo_page(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return (
        normalized.startswith("scam-check-now/")
        or normalized.startswith("scam-check-now-b/")
        or normalized.startswith("scam-check-now-c/")
    ) and normalized.endswith("/index.html")


def template_key_from_path(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    for template_key, template_dir in TEMPLATE_PATHS.items():
        if normalized.startswith(f"{template_dir}/"):
            return template_key
    return None


def slug_from_path(path: str) -> str | None:
    normalized = path.replace("\\", "/").strip("/")
    parts = normalized.split("/")
    if len(parts) < 2:
        return None
    return parts[-2].strip() or None


def public_href(template_key: str, slug: str) -> str:
    return f"/{TEMPLATE_PATHS[template_key]}/{slug}/"


def repo_file_for(template_key: str, slug: str) -> str:
    return os.path.join(TEMPLATE_PATHS[template_key], slug, "index.html")


def page_exists(template_key: str, slug: str) -> bool:
    return os.path.exists(repo_file_for(template_key, slug))


def get_target_files() -> List[str]:
    files: List[str] = []
    seen: Set[str] = set()

    for base_dir in get_target_dirs():
        for slug in get_target_slugs():
            candidate = os.path.join(base_dir, slug, "index.html")
            normalized_candidate = candidate.replace("\\", "/")
            if (
                os.path.exists(candidate)
                and is_allowed_seo_page(candidate)
                and normalized_candidate not in seen
            ):
                files.append(candidate)
                seen.add(normalized_candidate)

    return files


def humanize_word(word: str) -> str:
    lower = word.lower()
    if lower in SPECIAL_REPLACEMENTS:
        return SPECIAL_REPLACEMENTS[lower]
    return lower.capitalize()


def slug_to_topic_phrase(slug: str) -> str:
    words = [w for w in slug.split("-") if w]
    cleaned = [humanize_word(w) for w in words if w.lower() not in STRIP_WORDS]
    if not cleaned:
        cleaned = [humanize_word(w) for w in words]
    return " ".join(cleaned).strip() or "Suspicious message"


def slug_to_question_label(slug: str) -> str:
    words = [w for w in slug.split("-") if w]
    rendered: List[str] = []

    for index, word in enumerate(words):
        lower = word.lower()
        if lower in SPECIAL_REPLACEMENTS:
            rendered.append(SPECIAL_REPLACEMENTS[lower])
        elif index == 0 and lower == "is":
            rendered.append("Is")
        elif lower in LOWERCASE_LINK_WORDS:
            rendered.append(lower)
        elif lower == "scam":
            rendered.append("Scam")
        else:
            rendered.append(lower.capitalize())

    label = " ".join(rendered).strip()
    if label.startswith("Is ") and not label.endswith("?"):
        label = f"{label}?"
    label = label.replace(" Legit Or Scam?", " Legit or a Scam?")
    label = label.replace(" Real Or Fake?", " Real or Fake?")
    label = label.replace(" Legit Or Scam", " Legit or a Scam")
    label = label.replace(" Real Or Fake", " Real or Fake")
    return label


def build_title(slug: str) -> str:
    return TITLE_MAP.get(slug, f"{slug_to_topic_phrase(slug)} Scam? Warning Signs and What to Do")


def build_description(slug: str) -> str:
    return DESCRIPTION_MAP.get(
        slug,
        f"Check whether {slug_to_topic_phrase(slug)} is a scam. Review warning signs, suspicious link risks, and what to do before acting.",
    )


def template_priority_for(current_template: str) -> List[str]:
    if current_template == "a":
        return ["a", "c", "b"]
    if current_template == "b":
        return ["b", "a", "c"]
    if current_template == "c":
        return ["c", "a", "b"]
    return ["a", "b", "c"]


def build_internal_link_targets(current_slug: str, current_template: str) -> List[Tuple[str, str]]:
    cluster = CLUSTER_BY_SLUG.get(current_slug)
    same_cluster = [slug for slug in CLUSTER_SUPPORT.get(cluster or "", []) if slug != current_slug]
    fallback_cluster = [slug for slug in TODAY_TARGET_SLUGS if slug not in same_cluster and slug != current_slug]

    ordered_slugs = same_cluster + fallback_cluster
    template_priority = template_priority_for(current_template)

    targets: List[Tuple[str, str]] = []
    seen_hrefs: Set[str] = set()

    for slug in ordered_slugs:
        for template_key in template_priority:
            if slug == current_slug and template_key == current_template:
                continue
            if not page_exists(template_key, slug):
                continue
            href = public_href(template_key, slug)
            if href in seen_hrefs:
                continue
            targets.append((template_key, slug))
            seen_hrefs.add(href)
            if len(targets) >= 10:
                return targets

    return targets


def build_link_items_html(targets: List[Tuple[str, str]]) -> str:
    items: List[str] = []
    for template_key, target_slug in targets:
        href = public_href(template_key, target_slug)
        label = slug_to_question_label(target_slug)
        items.append(
            f'<li><a href="{html.escape(href, quote=True)}">{html.escape(label)}</a></li>'
        )
    return "".join(items)


def replace_title(content: str, new_title: str) -> str:
    import re

    return re.sub(
        r"<title>.*?</title>",
        f"<title>{html.escape(new_title)}</title>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_meta_description(content: str, new_description: str) -> str:
    import re

    return re.sub(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\'].*?["\'][^>]*>',
        f'<meta name="description" content="{html.escape(new_description, quote=True)}">',
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_list_by_id(content: str, list_id: str, items_html: str) -> str:
    import re

    patterns = [
        rf'(<ul[^>]*id="{re.escape(list_id)}"[^>]*>)(.*?)(</ul>)',
        rf"(<ul[^>]*id='{re.escape(list_id)}'[^>]*>)(.*?)(</ul>)",
    ]

    updated = content
    for pattern in patterns:
        updated, count = re.subn(
            pattern,
            lambda match: f"{match.group(1)}{items_html}{match.group(3)}",
            updated,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if count:
            return updated
    return updated


def update_internal_links_only(content: str, slug: str, template_key: str) -> str:
    targets = build_internal_link_targets(slug, template_key)
    updated = replace_list_by_id(content, "relatedLinks", build_link_items_html(targets[:5]))
    updated = replace_list_by_id(updated, "moreLinks", build_link_items_html(targets[5:10]))
    return updated


def normalize_whitespace(content: str) -> str:
    import re

    return re.sub(r"\n{3,}", "\n\n", content).strip() + "\n"


def should_update_metadata_only() -> bool:
    return REFRESH_SCOPE == "metadata"


def should_update_internal_links_only() -> bool:
    return REFRESH_SCOPE == "internal-links"


def process_file(path: str) -> bool:
    if not is_allowed_seo_page(path):
        print(f"SKIPPED (not allowed): {path}")
        return False

    slug = slug_from_path(path)
    template_key = template_key_from_path(path)

    if not slug:
        print(f"SKIPPED (no slug): {path}")
        return False

    if not template_key:
        print(f"SKIPPED (no template): {path}")
        return False

    with open(path, "r", encoding="utf-8") as file:
        original = file.read()

    if should_update_metadata_only():
        updated = original
        updated = replace_title(updated, build_title(slug))
        updated = replace_meta_description(updated, build_description(slug))
        updated = normalize_whitespace(updated)
    elif should_update_internal_links_only():
        updated = update_internal_links_only(original, slug, template_key)
        updated = normalize_whitespace(updated)
    else:
        raise ValueError(f"Invalid REFRESH_SCOPE: {REFRESH_SCOPE}")

    if updated == original:
        print(f"NO CHANGE: {path}")
        return False

    print(f"UPDATED: {path}")

    if not DRY_RUN:
        with open(path, "w", encoding="utf-8") as file:
            file.write(updated)

    return True


def main() -> None:
    if REFRESH_SCOPE not in {"metadata", "internal-links"}:
        raise ValueError(f"Invalid REFRESH_SCOPE: {REFRESH_SCOPE}")

    target_files = get_target_files()

    if not target_files:
        print("No matching GSC target SEO pages found.")
        return

    print(f"TARGET_TEMPLATE={TARGET_TEMPLATE}")
    print(f"REFRESH_SCOPE={REFRESH_SCOPE}")
    print(f"MAX_URLS_TO_REFRESH={MAX_URLS}")
    print(f"DRY_RUN={DRY_RUN}")
    print(f"Processing {len(target_files)} exact GSC target SEO pages...")

    updated_count = 0
    for file_path in target_files:
        if process_file(file_path):
            updated_count += 1

    print(f"Updated {updated_count} file(s).")
    print("Done.")


if __name__ == "__main__":
    main()