import os
import re
import html
from typing import List, Set, Dict

REFRESH_SCOPE = os.getenv("REFRESH_SCOPE", "metadata").strip().lower()
MAX_URLS = int(os.getenv("MAX_URLS_TO_REFRESH", "10"))
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"

# Exact repo-root paths only
TARGET_FILES: List[str] = [
    "scam-check-now/is-amazon-refund-message-legit-or-scam/index.html",
    "scam-check-now/is-google-account-disabled-email-legit-or-scam/index.html",
    "scam-check-now/is-fedex-customs-charge-email-legit-or-scam/index.html",
    "scam-check-now/is-usps-tracking-text-legit-or-scam/index.html",
    "scam-check-now/is-recruiter-email-from-unknown-company-legit-or-scam/index.html",
    "scam-check-now/is-venmo-security-alert-email-legit-or-scam/index.html",
    "scam-check-now/is-whatsapp-unusual-login-email-legit-or-scam/index.html",
    "scam-check-now/is-venmo-verification-code-text-real-or-fake/index.html",
    "scam-check-now/is-security-alert-message-legit-or-scam/index.html",
]

PAGE_METADATA: Dict[str, Dict[str, str]] = {
    "scam-check-now/is-amazon-refund-message-legit-or-scam/index.html": {
        "title": "Is Amazon Refund Message Legit or a Scam? Warning Signs",
        "description": "Got an Amazon refund message? Learn the warning signs and how to check if it is legit or a scam before you click, reply, or share information.",
    },
    "scam-check-now/is-google-account-disabled-email-legit-or-scam/index.html": {
        "title": "Is Google Account Disabled Email Legit or a Scam? Warning Signs",
        "description": "Got a Google account disabled email? Learn the warning signs and how to check if it is legit or a scam before you click, log in, or reply.",
    },
    "scam-check-now/is-fedex-customs-charge-email-legit-or-scam/index.html": {
        "title": "Is FedEx Customs Charge Email Legit or a Scam? Warning Signs",
        "description": "Got a FedEx customs charge email? Learn the warning signs and how to check if it is legit or a scam before you pay, click, or reply.",
    },
    "scam-check-now/is-usps-tracking-text-legit-or-scam/index.html": {
        "title": "Is USPS Tracking Text Legit or a Scam? Warning Signs",
        "description": "Got a USPS tracking text? Learn the warning signs and how to check if it is legit or a scam before you click the tracking link or reply.",
    },
    "scam-check-now/is-recruiter-email-from-unknown-company-legit-or-scam/index.html": {
        "title": "Is Recruiter Email From Unknown Company Legit or a Scam? Warning Signs",
        "description": "Got a recruiter email from an unknown company? Learn the warning signs and how to check if it is legit or a scam before you reply or share information.",
    },
    "scam-check-now/is-venmo-security-alert-email-legit-or-scam/index.html": {
        "title": "Is Venmo Security Alert Email Legit or a Scam? Warning Signs",
        "description": "Got a Venmo security alert email? Learn the warning signs and how to check if it is legit or a scam before you click, log in, or reply.",
    },
    "scam-check-now/is-whatsapp-unusual-login-email-legit-or-scam/index.html": {
        "title": "Is WhatsApp Unusual Login Email Legit or a Scam? Warning Signs",
        "description": "Got a WhatsApp unusual login email? Learn the warning signs and how to check if it is legit or a scam before you click, log in, or reply.",
    },
    "scam-check-now/is-venmo-verification-code-text-real-or-fake/index.html": {
        "title": "Is Venmo Verification Code Text Real or Fake? Warning Signs",
        "description": "Got a Venmo verification code text? Learn the warning signs and how to check if it is real or fake before you share any code or take action.",
    },
    "scam-check-now/is-security-alert-message-legit-or-scam/index.html": {
        "title": "Is Security Alert Message Legit or a Scam? Warning Signs",
        "description": "Got a security alert message? Learn the warning signs and how to check if it is legit or a scam before you click, reply, or share information.",
    },
}

SPECIAL_REPLACEMENTS = {
    "usps": "USPS",
    "ups": "UPS",
    "fedex": "FedEx",
    "amazon": "Amazon",
    "google": "Google",
    "apple": "Apple",
    "whatsapp": "WhatsApp",
    "telegram": "Telegram",
    "snapchat": "Snapchat",
    "venmo": "Venmo",
    "paypal": "PayPal",
    "zelle": "Zelle",
}

LOWERCASE_LINK_WORDS = {"a", "an", "and", "or", "the", "from"}


def slug_from_path(path: str) -> str:
    return path.replace("\\", "/").split("/")[-2]


def public_href_from_path(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    return f"/{parts[0]}/{parts[1]}/"


def slug_to_label(slug: str) -> str:
    words = slug.split("-")
    rendered: List[str] = []

    for index, word in enumerate(words):
        lower = word.lower()
        if lower in SPECIAL_REPLACEMENTS:
            rendered.append(SPECIAL_REPLACEMENTS[lower])
        elif index == 0 and lower == "is":
            rendered.append("Is")
        elif lower in LOWERCASE_LINK_WORDS:
            rendered.append(lower)
        else:
            rendered.append(lower.capitalize())

    label = " ".join(rendered).strip()
    if label.startswith("Is ") and not label.endswith("?"):
        label += "?"
    label = label.replace(" Legit Or Scam?", " Legit or a Scam?")
    label = label.replace(" Real Or Fake?", " Real or Fake?")
    label = label.replace(" Legit Or Scam", " Legit or a Scam")
    label = label.replace(" Real Or Fake", " Real or Fake")
    return label


def build_internal_links(current_path: str) -> List[str]:
    links: List[str] = []
    seen: Set[str] = set()

    for path in TARGET_FILES[:MAX_URLS]:
        if path == current_path:
            continue
        if not os.path.exists(path):
            continue

        href = public_href_from_path(path)
        if href in seen:
            continue

        slug = slug_from_path(path)
        label = slug_to_label(slug)

        links.append(f'<li><a href="{html.escape(href, quote=True)}">{html.escape(label)}</a></li>')
        seen.add(href)

        if len(links) >= 10:
            break

    return links


def replace_list_by_id(content: str, list_id: str, items_html: str) -> str:
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

    print(f"WARNING: list id '{list_id}' not found")
    return updated


def replace_title(content: str, new_title: str) -> str:
    updated, count = re.subn(
        r"<title>.*?</title>",
        f"<title>{html.escape(new_title)}</title>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if count == 0:
        print("WARNING: <title> not found")
    return updated


def replace_meta_by_name(content: str, name: str, value: str) -> str:
    escaped_value = html.escape(value, quote=True)
    patterns = [
        rf'(<meta[^>]*name="{re.escape(name)}"[^>]*content=")([^"]*)(".*?>)',
        rf"(<meta[^>]*name='{re.escape(name)}'[^>]*content=')([^']*)('.*?>)",
        rf'(<meta[^>]*content=")([^"]*)("[^>]*name="{re.escape(name)}"[^>]*>)',
        rf"(<meta[^>]*content=')([^']*)('[^>]*name='{re.escape(name)}'[^>]*>)",
    ]

    updated = content
    for pattern in patterns:
        updated, count = re.subn(
            pattern,
            rf"\g<1>{escaped_value}\g<3>",
            updated,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if count:
            return updated

    print(f"WARNING: meta name '{name}' not found")
    return updated


def replace_meta_by_property(content: str, prop: str, value: str) -> str:
    escaped_value = html.escape(value, quote=True)
    patterns = [
        rf'(<meta[^>]*property="{re.escape(prop)}"[^>]*content=")([^"]*)(".*?>)',
        rf"(<meta[^>]*property='{re.escape(prop)}'[^>]*content=')([^']*)('.*?>)",
        rf'(<meta[^>]*content=")([^"]*)("[^>]*property="{re.escape(prop)}"[^>]*>)',
        rf"(<meta[^>]*content=')([^']*)('[^>]*property='{re.escape(prop)}'[^>]*>)",
    ]

    updated = content
    for pattern in patterns:
        updated, count = re.subn(
            pattern,
            rf"\g<1>{escaped_value}\g<3>",
            updated,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if count:
            return updated

    print(f"WARNING: meta property '{prop}' not found")
    return updated


def process_file(path: str) -> bool:
    if not os.path.exists(path):
        print(f"SKIPPED (missing): {path}")
        return False

    with open(path, "r", encoding="utf-8") as file:
        original = file.read()

    updated = original

    if REFRESH_SCOPE == "internal-links":
        links = build_internal_links(path)
        related_html = "".join(links[:5])
        more_html = "".join(links[5:10])

        updated = replace_list_by_id(updated, "relatedLinks", related_html)
        updated = replace_list_by_id(updated, "moreLinks", more_html)

    elif REFRESH_SCOPE == "metadata":
        meta = PAGE_METADATA.get(path)
        if not meta:
            print(f"SKIPPED (no metadata configured): {path}")
            return False

        title = meta["title"]
        description = meta["description"]

        updated = replace_title(updated, title)
        updated = replace_meta_by_name(updated, "description", description)
        updated = replace_meta_by_property(updated, "og:title", title)
        updated = replace_meta_by_property(updated, "og:description", description)
        updated = replace_meta_by_name(updated, "twitter:title", title)
        updated = replace_meta_by_name(updated, "twitter:description", description)

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
    if REFRESH_SCOPE not in {"internal-links", "metadata"}:
        raise ValueError(f"Invalid REFRESH_SCOPE: {REFRESH_SCOPE}")

    if MAX_URLS <= 0:
        raise ValueError(f"Invalid MAX_URLS_TO_REFRESH: {MAX_URLS}")

    target_files = TARGET_FILES[:MAX_URLS]

    print(f"REFRESH_SCOPE={REFRESH_SCOPE}")
    print(f"DRY_RUN={DRY_RUN}")
    print(f"MAX_URLS_TO_REFRESH={MAX_URLS}")
    print(f"Processing {len(target_files)} exact repo-root SEO pages...")

    updated_count = 0
    for path in target_files:
        if process_file(path):
            updated_count += 1

    print(f"Updated {updated_count} file(s). Done.")


if __name__ == "__main__":
    main()