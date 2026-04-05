import os
import re
import html
import json
from typing import List, Dict, Any

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

# Exact per-page SEO updates only: metadata + visible top-of-page content + matching JSON-LD
PAGE_SEO: Dict[str, Dict[str, str]] = {
    "scam-check-now/is-amazon-refund-message-legit-or-scam/index.html": {
        "title": "Is Amazon Refund Message Legit or a Scam? Warning Signs",
        "description": "Got an Amazon refund message? Learn the warning signs and how to check if it is legit or a scam before you click, reply, or share information.",
        "h1": "Is Amazon Refund Message Legit or a Scam?",
        "intro": "Got an Amazon refund message? Learn the warning signs and how to check if it is legit or a scam before you click, reply, send money, or share information.",
    },
    "scam-check-now/is-google-account-disabled-email-legit-or-scam/index.html": {
        "title": "Is Google Account Disabled Email Legit or a Scam? Warning Signs",
        "description": "Got a Google account disabled email? Learn the warning signs and how to check if it is legit or a scam before you click, log in, or reply.",
        "h1": "Is Google Account Disabled Email Legit or a Scam?",
        "intro": "Got a Google account disabled email? Learn the warning signs and how to check if it is legit or a scam before you click, log in, reply, or share information.",
    },
    "scam-check-now/is-fedex-customs-charge-email-legit-or-scam/index.html": {
        "title": "Is FedEx Customs Charge Email Legit or a Scam? Warning Signs",
        "description": "Got a FedEx customs charge email? Learn the warning signs and how to check if it is legit or a scam before you pay, click, or reply.",
        "h1": "Is FedEx Customs Charge Email Legit or a Scam?",
        "intro": "Got a FedEx customs charge email? Learn the warning signs and how to check if it is legit or a scam before you pay, click, reply, or share information.",
    },
    "scam-check-now/is-usps-tracking-text-legit-or-scam/index.html": {
        "title": "Is USPS Tracking Text Legit or a Scam? Warning Signs",
        "description": "Got a USPS tracking text? Learn the warning signs and how to check if it is legit or a scam before you click the tracking link or reply.",
        "h1": "Is USPS Tracking Text Legit or a Scam?",
        "intro": "Got a USPS tracking text? Learn the warning signs and how to check if it is legit or a scam before you click the tracking link, reply, or share information.",
    },
    "scam-check-now/is-recruiter-email-from-unknown-company-legit-or-scam/index.html": {
        "title": "Is Recruiter Email From Unknown Company Legit or a Scam? Warning Signs",
        "description": "Got a recruiter email from an unknown company? Learn the warning signs and how to check if it is legit or a scam before you reply or share information.",
        "h1": "Is Recruiter Email From Unknown Company Legit or a Scam?",
        "intro": "Got a recruiter email from an unknown company? Learn the warning signs and how to check if it is legit or a scam before you reply, click, or share information.",
    },
    "scam-check-now/is-venmo-security-alert-email-legit-or-scam/index.html": {
        "title": "Is Venmo Security Alert Email Legit or a Scam? Warning Signs",
        "description": "Got a Venmo security alert email? Learn the warning signs and how to check if it is legit or a scam before you click, log in, or reply.",
        "h1": "Is Venmo Security Alert Email Legit or a Scam?",
        "intro": "Got a Venmo security alert email? Learn the warning signs and how to check if it is legit or a scam before you click, log in, reply, or share information.",
    },
    "scam-check-now/is-whatsapp-unusual-login-email-legit-or-scam/index.html": {
        "title": "Is WhatsApp Unusual Login Email Legit or a Scam? Warning Signs",
        "description": "Got a WhatsApp unusual login email? Learn the warning signs and how to check if it is legit or a scam before you click, log in, or reply.",
        "h1": "Is WhatsApp Unusual Login Email Legit or a Scam?",
        "intro": "Got a WhatsApp unusual login email? Learn the warning signs and how to check if it is legit or a scam before you click, log in, reply, or share information.",
    },
    "scam-check-now/is-venmo-verification-code-text-real-or-fake/index.html": {
        "title": "Is Venmo Verification Code Text Real or Fake? Warning Signs",
        "description": "Got a Venmo verification code text? Learn the warning signs and how to check if it is real or fake before you share any code or take action.",
        "h1": "Is Venmo Verification Code Text Real or Fake?",
        "intro": "Got a Venmo verification code text? Learn the warning signs and how to check if it is real or fake before you share any code, click, or take action.",
    },
    "scam-check-now/is-security-alert-message-legit-or-scam/index.html": {
        "title": "Is Security Alert Message Legit or a Scam? Warning Signs",
        "description": "Got a security alert message? Learn the warning signs and how to check if it is legit or a scam before you click, reply, or share information.",
        "h1": "Is Security Alert Message Legit or a Scam?",
        "intro": "Got a security alert message? Learn the warning signs and how to check if it is legit or a scam before you click, reply, or share information.",
    },
}


def repo_path_to_url(path: str) -> str:
    normalized = path.replace("\\", "/")
    if not normalized.endswith("/index.html"):
        raise ValueError(f"Unexpected page path: {path}")
    return f"https://verixiaapps.com/{normalized[:-10]}/"


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


def replace_meta(content: str, key: str, value: str, attr: str = "name") -> str:
    escaped = html.escape(value, quote=True)
    patterns = [
        rf'(<meta[^>]*{attr}="{re.escape(key)}"[^>]*content=")([^"]*)(".*?>)',
        rf"(<meta[^>]*{attr}='{re.escape(key)}'[^>]*content=')([^']*)('.*?>)",
        rf'(<meta[^>]*content=")([^"]*)("[^>]*{attr}="{re.escape(key)}"[^>]*>)',
        rf"(<meta[^>]*content=')([^']*)('[^>]*{attr}='{re.escape(key)}'[^>]*>)",
    ]

    updated = content
    for pattern in patterns:
        updated, count = re.subn(
            pattern,
            rf"\g<1>{escaped}\g<3>",
            updated,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if count:
            return updated

    print(f"WARNING: meta {attr} '{key}' not found")
    return updated


def replace_first_h1(content: str, new_h1: str) -> str:
    updated, count = re.subn(
        r"(<h1[^>]*>)(.*?)(</h1>)",
        rf"\g<1>{html.escape(new_h1)}\g<3>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if count == 0:
        print("WARNING: <h1> not found")
    return updated


def replace_first_paragraph_after_h1(content: str, new_paragraph: str) -> str:
    updated, count = re.subn(
        r"(<h1[^>]*>.*?</h1>\s*<p[^>]*>)(.*?)(</p>)",
        rf"\g<1>{html.escape(new_paragraph)}\g<3>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if count == 0:
        print("WARNING: first paragraph after <h1> not found")
    return updated


def update_jsonld_object(obj: Any, seo: Dict[str, str], page_url: str) -> None:
    if isinstance(obj, list):
        for item in obj:
            update_jsonld_object(item, seo, page_url)
        return

    if not isinstance(obj, dict):
        return

    obj_type = obj.get("@type")
    obj_url = obj.get("url")
    obj_name = obj.get("name", "")

    if obj_type == "CollectionPage":
        obj["name"] = seo["title"]
        obj["description"] = seo["description"]

    elif obj_type == "BreadcrumbList":
        items = obj.get("itemListElement")
        if isinstance(items, list) and items:
            last_item = items[-1]
            if isinstance(last_item, dict):
                last_item["name"] = seo["h1"]

    elif obj_type == "ItemList" and isinstance(obj_name, str) and "Related Scam Checks" in obj_name:
        obj["name"] = f"{seo['h1']} Related Scam Checks"

    elif obj_url == page_url:
        if "name" in obj and isinstance(obj.get("name"), str):
            obj["name"] = seo["title"]
        if "description" in obj and isinstance(obj.get("description"), str):
            obj["description"] = seo["description"]

    for value in obj.values():
        update_jsonld_object(value, seo, page_url)


def replace_jsonld(content: str, seo: Dict[str, str], page_url: str) -> str:
    pattern = re.compile(
        r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
        flags=re.DOTALL | re.IGNORECASE,
    )

    def _repl(match: re.Match) -> str:
        open_tag, json_text, close_tag = match.groups()
        stripped = json_text.strip()
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            print("WARNING: JSON-LD parse failed")
            return match.group(0)

        update_jsonld_object(data, seo, page_url)
        new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return f"{open_tag}{new_json}{close_tag}"

    updated, count = pattern.subn(_repl, content)
    if count == 0:
        print("WARNING: JSON-LD script not found")
    return updated


def process_file(path: str) -> bool:
    if not os.path.exists(path):
        print(f"SKIPPED (missing): {path}")
        return False

    seo = PAGE_SEO.get(path)
    if not seo:
        print(f"SKIPPED (no SEO config): {path}")
        return False

    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    updated = original

    if REFRESH_SCOPE != "metadata":
        raise ValueError("Set REFRESH_SCOPE=metadata")

    updated = replace_title(updated, seo["title"])
    updated = replace_meta(updated, "description", seo["description"], "name")
    updated = replace_meta(updated, "og:title", seo["title"], "property")
    updated = replace_meta(updated, "og:description", seo["description"], "property")
    updated = replace_meta(updated, "twitter:title", seo["title"], "name")
    updated = replace_meta(updated, "twitter:description", seo["description"], "name")
    updated = replace_first_h1(updated, seo["h1"])
    updated = replace_first_paragraph_after_h1(updated, seo["intro"])
    updated = replace_jsonld(updated, seo, repo_path_to_url(path))

    if updated == original:
        print(f"NO CHANGE: {path}")
        return False

    print(f"UPDATED: {path}")

    if not DRY_RUN:
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)

    return True


def main() -> None:
    if REFRESH_SCOPE != "metadata":
        raise ValueError("Set REFRESH_SCOPE=metadata")

    if MAX_URLS <= 0:
        raise ValueError("Invalid MAX_URLS_TO_REFRESH")

    files = TARGET_FILES[:MAX_URLS]

    print(f"REFRESH_SCOPE={REFRESH_SCOPE}")
    print(f"DRY_RUN={DRY_RUN}")
    print(f"MAX_URLS_TO_REFRESH={MAX_URLS}")
    print(f"Processing {len(files)} exact repo-root SEO pages...")

    updated = 0
    for path in files:
        if process_file(path):
            updated += 1

    print(f"Updated {updated} file(s). Done.")


if __name__ == "__main__":
    main()