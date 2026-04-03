import os
import html
from typing import List, Set

TARGET_TEMPLATE = os.getenv("TARGET_TEMPLATE", "all").strip().lower()
REFRESH_SCOPE = os.getenv("REFRESH_SCOPE", "internal-links").strip().lower()
MAX_URLS = int(os.getenv("MAX_URLS_TO_REFRESH", "10"))
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"

TEMPLATE_PATHS = {
    "a": "scam-check-now",
    "b": "scam-check-now-b",
    "c": "scam-check-now-c",
}

TODAY_TARGET_SLUGS = [
    "is-amazon-refund-message-legit-or-scam",
    "is-usps-tracking-text-legit-or-scam",
    "is-venmo-verification-code-text-real-or-fake",
    "is-security-alert-message-legit-or-scam",
    "snapchat-scams",
    "is-google-account-disabled-email-legit-or-scam",
    "is-apple-account-verification-email-legit-or-scam",
    "is-bank-account-closure-email-legit-or-scam",
    "is-fedex-delivery-legit-or-scam",
    "is-fedex-customs-charge-email-legit-or-scam",
]

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

LOWERCASE_LINK_WORDS = {"a", "an", "and", "or", "the"}

TITLE_MAP = {
    "is-amazon-refund-message-legit-or-scam": "Amazon Refund Email Scam? Real or Fake Warning Signs",
    "is-usps-tracking-text-legit-or-scam": "USPS Tracking Text Scam? Real or Fake Message Warning Signs",
    "is-venmo-verification-code-text-real-or-fake": "Venmo Verification Code Text Scam? Real or Fake Warning Signs",
    "is-security-alert-message-legit-or-scam": "Security Alert Message Scam? Real or Fake Warning Signs",
    "snapchat-scams": "Snapchat Scams: Real Examples, Warning Signs and What to Do",
    "is-google-account-disabled-email-legit-or-scam": "Google Account Disabled Email Scam? Real or Fake Warning Signs",
    "is-apple-account-verification-email-legit-or-scam": "Apple Account Verification Email Scam? Real or Fake Warning Signs",
    "is-bank-account-closure-email-legit-or-scam": "Bank Account Closure Email Scam? Real or Fake Warning Signs",
    "is-fedex-delivery-legit-or-scam": "FedEx Delivery Message Scam? Real or Fake Warning Signs",
    "is-fedex-customs-charge-email-legit-or-scam": "FedEx Customs Charge Email Scam? Real or Fake Warning Signs",
}

DESCRIPTION_MAP = {
    "is-amazon-refund-message-legit-or-scam": "Got an Amazon refund email or message? Learn scam warning signs, fake link risks, and what to do before you click, reply, or send information.",
    "is-usps-tracking-text-legit-or-scam": "Got a USPS tracking text? Learn scam warning signs, fake tracking link risks, and what to do before clicking.",
    "is-venmo-verification-code-text-real-or-fake": "Received a Venmo verification code text? Learn scam signs, fake urgency patterns, and what to do before taking action.",
    "is-security-alert-message-legit-or-scam": "Received a security alert message? Learn how to spot fake alerts, suspicious links, and what to do next.",
    "snapchat-scams": "Learn common Snapchat scam warning signs, fake account risks, and what to do before replying or clicking.",
    "is-google-account-disabled-email-legit-or-scam": "Received a Google account disabled email? Learn warning signs of fake alerts and how to verify safely.",
    "is-apple-account-verification-email-legit-or-scam": "Received an Apple account verification email? Learn scam signs and what to check before clicking.",
    "is-bank-account-closure-email-legit-or-scam": "Got a bank account closure email? Learn warning signs and what to do before taking action.",
    "is-fedex-delivery-legit-or-scam": "Got a FedEx delivery message? Learn scam signs, fake tracking links, and what to do before clicking.",
    "is-fedex-customs-charge-email-legit-or-scam": "Got a FedEx customs charge email? Learn scam warning signs, payment risks, and what to do before paying.",
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


def slug_from_path(path: str) -> str | None:
    normalized = path.replace("\\", "/").strip("/")
    parts = normalized.split("/")
    if len(parts) < 2:
        return None
    return parts[-2].strip() or None


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
    if slug == "snapchat-scams":
        return "Snapchat Scams"

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


def build_internal_link_targets(slug: str) -> List[str]:
    category_keywords = [part for part in slug.split("-") if part and part not in STRIP_WORDS]
    preferred: List[str] = []
    fallback: List[str] = []

    for candidate in TODAY_TARGET_SLUGS:
        if candidate == slug:
            continue
        if any(keyword in candidate for keyword in category_keywords[:3]):
            preferred.append(candidate)
        else:
            fallback.append(candidate)

    return (preferred + fallback)[:10]


def build_link_items_html(slugs: List[str]) -> str:
    items: List[str] = []
    for target_slug in slugs:
        href = f"/{target_slug}/"
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


def update_internal_links_only(content: str, slug: str) -> str:
    targets = build_internal_link_targets(slug)
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
    if not slug:
        print(f"SKIPPED (no slug): {path}")
        return False

    with open(path, "r", encoding="utf-8") as file:
        original = file.read()

    if should_update_metadata_only():
        updated = original
        updated = replace_title(updated, build_title(slug))
        updated = replace_meta_description(updated, build_description(slug))
        updated = normalize_whitespace(updated)
    elif should_update_internal_links_only():
        updated = update_internal_links_only(original, slug)
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