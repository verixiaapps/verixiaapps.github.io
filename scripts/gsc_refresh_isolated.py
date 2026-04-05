import os
import re
import html
import json
from typing import List, Dict, Any


def parse_positive_int(value: str, default: int) -> int:
    try:
        parsed = int(str(value).strip())
        if parsed <= 0:
            return default
        return parsed
    except (TypeError, ValueError):
        return default


REFRESH_SCOPE = os.getenv("REFRESH_SCOPE", "metadata").strip().lower()
MAX_URLS = parse_positive_int(os.getenv("MAX_URLS_TO_REFRESH", "10"), 10)
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

REQUIRED_SEO_KEYS = ("title", "description", "h1", "intro")


def repo_path_to_url(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    if not normalized.endswith("/index.html"):
        raise ValueError(f"Unexpected page path: {path}")
    return f"https://verixiaapps.com/{normalized[:-10]}/"


def escape_text(text: str) -> str:
    return html.escape(text, quote=False)


def escape_attr(text: str) -> str:
    return html.escape(text, quote=True)


def validate_config() -> None:
    if REFRESH_SCOPE != "metadata":
        raise ValueError("Set REFRESH_SCOPE=metadata")

    if MAX_URLS <= 0:
        raise ValueError("Invalid MAX_URLS_TO_REFRESH")

    seen = set()
    for path in TARGET_FILES:
        if path in seen:
            raise ValueError(f"Duplicate target file: {path}")
        seen.add(path)

        if path not in PAGE_SEO:
            raise ValueError(f"Missing PAGE_SEO entry for target file: {path}")

        if not path.endswith("/index.html"):
            raise ValueError(f"Unexpected target file path: {path}")

    for path, seo in PAGE_SEO.items():
        if not path.endswith("/index.html"):
            raise ValueError(f"Unexpected PAGE_SEO path: {path}")

        missing = [key for key in REQUIRED_SEO_KEYS if not str(seo.get(key, "")).strip()]
        if missing:
            raise ValueError(f"Missing SEO fields for {path}: {', '.join(missing)}")


def replace_title(content: str, new_title: str) -> str:
    updated, count = re.subn(
        r"(<title\b[^>]*>)(.*?)(</title>)",
        rf"\g<1>{escape_text(new_title)}\g<3>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if count == 0:
        print("WARNING: <title> not found")
    return updated


def parse_tag_attributes(tag: str) -> Dict[str, str]:
    attrs: Dict[str, str] = {}
    for match in re.finditer(
        r'([^\s=<>"\'/]+)\s*=\s*("([^"]*)"|\'([^\']*)\')',
        tag,
        flags=re.DOTALL,
    ):
        name = match.group(1).lower()
        value = match.group(3) if match.group(3) is not None else (match.group(4) or "")
        attrs[name] = value
    return attrs


def rebuild_meta_tag(original_tag: str, new_attrs: Dict[str, str]) -> str:
    if not re.match(r"<meta\b", original_tag, flags=re.IGNORECASE):
        return original_tag

    ordered_names: List[str] = []
    seen = set()

    for match in re.finditer(
        r'([^\s=<>"\'/]+)\s*=\s*("([^"]*)"|\'([^\']*)\')',
        original_tag,
        flags=re.DOTALL,
    ):
        name = match.group(1)
        lower_name = name.lower()
        if lower_name not in seen:
            ordered_names.append(lower_name)
            seen.add(lower_name)

    for name in new_attrs.keys():
        if name not in seen:
            ordered_names.append(name)
            seen.add(name)

    parts = ["<meta"]
    for name in ordered_names:
        if name in new_attrs:
            parts.append(f'{name}="{escape_attr(new_attrs[name])}"')

    closing = " />" if re.search(r"/\s*>$", original_tag) else ">"
    return " ".join(parts) + closing


def replace_meta(content: str, key: str, value: str, attr: str = "name") -> str:
    attr = attr.lower()
    key_lower = key.lower()
    meta_pattern = re.compile(r"<meta\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)

    match_to_replace = None
    for match in meta_pattern.finditer(content):
        tag = match.group(0)
        attrs = parse_tag_attributes(tag)
        if attrs.get(attr, "").lower() == key_lower:
            match_to_replace = match
            break

    if match_to_replace is None:
        print(f"WARNING: meta {attr} '{key}' not found")
        return content

    original_tag = match_to_replace.group(0)
    attrs = parse_tag_attributes(original_tag)
    attrs["content"] = value
    new_tag = rebuild_meta_tag(original_tag, attrs)

    return content[: match_to_replace.start()] + new_tag + content[match_to_replace.end() :]


def replace_first_h1(content: str, new_h1: str) -> str:
    updated, count = re.subn(
        r"(<h1\b[^>]*>)(.*?)(</h1>)",
        rf"\g<1>{escape_text(new_h1)}\g<3>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if count == 0:
        print("WARNING: <h1> not found")
    return updated


def replace_first_paragraph_after_h1(content: str, new_paragraph: str) -> str:
    pattern = re.compile(
        r"(<h1\b[^>]*>.*?</h1>)(?P<gap>(?:\s|<!--.*?-->)*)(<p\b[^>]*>)(.*?)(</p>)",
        flags=re.DOTALL | re.IGNORECASE,
    )
    updated, count = pattern.subn(
        rf"\1\g<gap>\3{escape_text(new_paragraph)}\5",
        content,
        count=1,
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
            for item in items:
                if not isinstance(item, dict):
                    continue
                item_ref = item.get("item")
                if isinstance(item_ref, str) and item_ref == page_url:
                    item["name"] = seo["h1"]

            last_item = items[-1]
            if isinstance(last_item, dict):
                last_item["name"] = seo["h1"]

    elif obj_type == "ItemList" and isinstance(obj_name, str) and "Related Scam Checks" in obj_name:
        obj["name"] = f"{seo['h1']} Related Scam Checks"

    elif obj_url == page_url:
        if isinstance(obj.get("name"), str):
            obj["name"] = seo["title"]
        if isinstance(obj.get("description"), str):
            obj["description"] = seo["description"]

    for value in obj.values():
        update_jsonld_object(value, seo, page_url)


def replace_jsonld(content: str, seo: Dict[str, str], page_url: str) -> str:
    pattern = re.compile(
        r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
        flags=re.DOTALL | re.IGNORECASE,
    )

    found_any = False

    def _repl(match: re.Match) -> str:
        nonlocal found_any
        found_any = True

        open_tag, json_text, close_tag = match.groups()
        stripped = json_text.strip()

        if not stripped:
            print("WARNING: JSON-LD script empty")
            return match.group(0)

        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            print("WARNING: JSON-LD parse failed")
            return match.group(0)

        update_jsonld_object(data, seo, page_url)
        new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return f"{open_tag}{new_json}{close_tag}"

    updated = pattern.sub(_repl, content)

    if not found_any:
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
    page_url = repo_path_to_url(path)

    updated = replace_title(updated, seo["title"])
    updated = replace_meta(updated, "description", seo["description"], "name")
    updated = replace_meta(updated, "og:title", seo["title"], "property")
    updated = replace_meta(updated, "og:description", seo["description"], "property")
    updated = replace_meta(updated, "twitter:title", seo["title"], "name")
    updated = replace_meta(updated, "twitter:description", seo["description"], "name")
    updated = replace_first_h1(updated, seo["h1"])
    updated = replace_first_paragraph_after_h1(updated, seo["intro"])
    updated = replace_jsonld(updated, seo, page_url)

    if updated == original:
        print(f"NO CHANGE: {path}")
        return False

    print(f"UPDATED: {path}")

    if not DRY_RUN:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(updated)

    return True


def main() -> None:
    validate_config()

    files = TARGET_FILES[: min(MAX_URLS, len(TARGET_FILES))]

    print(f"REFRESH_SCOPE={REFRESH_SCOPE}")
    print(f"DRY_RUN={DRY_RUN}")
    print(f"MAX_URLS_TO_REFRESH={MAX_URLS}")
    print(f"Processing {len(files)} exact repo-root SEO pages...")

    updated_count = 0
    for path in files:
        if process_file(path):
            updated_count += 1

    print(f"Updated {updated_count} file(s). Done.")


if __name__ == "__main__":
    main()