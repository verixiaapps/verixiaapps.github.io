import os
import html
from typing import Dict, List, Set, Tuple

TARGET_TEMPLATE = os.getenv("TARGET_TEMPLATE", "a").strip().lower()
REFRESH_SCOPE = os.getenv("REFRESH_SCOPE", "internal-links").strip().lower()
MAX_URLS = int(os.getenv("MAX_URLS_TO_REFRESH", "10"))
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"

# ✅ EXACT repo-root paths only (no slugs, no guessing, no other folders)
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

def humanize_word(word: str) -> str:
    return SPECIAL_REPLACEMENTS.get(word.lower(), word.capitalize())

def slug_to_label(slug: str) -> str:
    words = slug.split("-")
    rendered = []
    for i, w in enumerate(words):
        lw = w.lower()
        if lw in SPECIAL_REPLACEMENTS:
            rendered.append(SPECIAL_REPLACEMENTS[lw])
        elif i == 0 and lw == "is":
            rendered.append("Is")
        elif lw in LOWERCASE_LINK_WORDS:
            rendered.append(lw)
        else:
            rendered.append(lw.capitalize())
    label = " ".join(rendered)
    if label.startswith("Is ") and not label.endswith("?"):
        label += "?"
    return label

def build_internal_links(current_path: str) -> List[str]:
    links = []
    seen: Set[str] = set()

    for path in TARGET_FILES:
        if path == current_path:
            continue
        if not os.path.exists(path):
            continue

        href = public_href_from_path(path)
        if href in seen:
            continue

        slug = slug_from_path(path)
        label = slug_to_label(slug)

        links.append(f'<li><a href="{html.escape(href)}">{html.escape(label)}</a></li>')
        seen.add(href)

        if len(links) >= 10:
            break

    return links

def replace_list_by_id(content: str, list_id: str, items_html: str) -> str:
    import re
    patterns = [
        rf'(<ul[^>]*id="{list_id}"[^>]*>)(.*?)(</ul>)',
        rf"(<ul[^>]*id='{list_id}'[^>]*>)(.*?)(</ul>)",
    ]
    updated = content
    for pattern in patterns:
        updated, count = re.subn(
            pattern,
            lambda m: f"{m.group(1)}{items_html}{m.group(3)}",
            updated,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if count:
            return updated
    return updated

def process_file(path: str) -> bool:
    if not os.path.exists(path):
        print(f"SKIPPED (missing): {path}")
        return False

    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    links = build_internal_links(path)
    related_html = "".join(links[:5])
    more_html = "".join(links[5:10])

    updated = replace_list_by_id(original, "relatedLinks", related_html)
    updated = replace_list_by_id(updated, "moreLinks", more_html)

    if updated == original:
        print(f"NO CHANGE: {path}")
        return False

    print(f"UPDATED: {path}")

    if not DRY_RUN:
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)

    return True

def main() -> None:
    if REFRESH_SCOPE != "internal-links":
        raise ValueError("Only internal-links supported in this version")

    print(f"REFRESH_SCOPE={REFRESH_SCOPE}")
    print(f"DRY_RUN={DRY_RUN}")
    print(f"Processing {len(TARGET_FILES)} exact repo-root SEO pages...")

    updated_count = 0
    for path in TARGET_FILES[:MAX_URLS]:
        if process_file(path):
            updated_count += 1

    print(f"Updated {updated_count} file(s). Done.")

if __name__ == "__main__":
    main()