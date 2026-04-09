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

# Exact repo-root path only for the page being optimized right now
TARGET_FILES: List[str] = [
    "scam-check-now-b/is-td-bank-fraud-alert-email-legit-or-scam/index.html",
]

# Exact per-page SEO updates only for this page:
# metadata + visible top-of-page content + matching JSON-LD + long SEO body + FAQ
PAGE_SEO: Dict[str, Dict[str, Any]] = {
    "scam-check-now-b/is-td-bank-fraud-alert-email-legit-or-scam/index.html": {
        "title": "Is TD Bank Fraud Alert Email Legit or a Scam? Real or Fake Warning Signs",
        "description": "Got a TD Bank fraud alert email? Learn how to tell if it is legit or a scam, what phishing red flags to watch for, and what to do before you click, sign in, reply, or share information.",
        "h1": "Is TD Bank Fraud Alert Email Legit or a Scam?",
        "intro": "Got a TD Bank fraud alert email? Some fraud alerts are real, but scammers also send fake TD Bank security notices to steal your login details, verification codes, or personal information. Learn the warning signs and how to check if it is legit or fake before you click, sign in, reply, or share anything.",
        "body_html": """
<div class="content-block" data-context="banking" data-mode="comparison">
<p>A TD Bank fraud alert email can be legitimate, but it is also a common phishing theme used by scammers. The safest way to judge it is not by how official the email looks, but by whether the alert still makes sense after you verify it directly through your TD Bank account, app, or official support channels.</p>

<h2>How Real And Fake TD Bank Fraud Alerts Usually Differ</h2>
<p>A legitimate TD Bank fraud alert usually points you back to your real account activity and can be confirmed independently through the official TD Bank website or mobile app. A scam version often tries to keep you inside the email itself by pushing you to click a link, call a number in the message, or share information before you verify anything on your own.</p>

<p>Scammers know that banking alerts create immediate fear. A fake TD Bank fraud email may claim your account has suspicious activity, a locked card, an unusual login, or a transfer that needs urgent review. The goal is to make you act quickly before you slow down and confirm whether the alert is actually connected to your account.</p>

<p>Many fake TD Bank fraud alert emails look polished. They may include the TD logo, account-related wording, security language, and a button that appears to lead to a login page. Some even include phone numbers or instructions that sound professional. But a convincing design does not make the message real. What matters is whether the email matches real account activity and whether the action path stays inside official TD Bank channels.</p>

<p>Phishing versions often push one urgent next step. That may be logging in through a link, verifying your identity by email, sending a one-time code, or calling a supposed fraud department listed in the message. In some cases, the scam continues across text messages or phone calls after the email is opened, making the whole situation feel even more believable.</p>

<p>If you interact with a fake TD Bank fraud alert email, the risks can be serious. Clicking a phishing link can lead to a fake sign-in page designed to capture your credentials. Replying with personal details or verification codes can help scammers take over your account. Even calling a fake support number may expose sensitive banking information that can later be used for fraud or identity theft.</p>

<p>That is why independent verification matters so much. A real TD Bank fraud alert should still make sense when you ignore the email link and instead check your account through the official site, official app, or a trusted phone number you found yourself. A scam version usually falls apart the moment you stop relying on the message itself.</p>
</div>

<h2>Signs This Might Be A Scam</h2>
<ul>
<li>Unexpected TD Bank fraud alerts that arrive without matching account activity</li>
<li>Links that push you to sign in or verify information directly from the email</li>
<li>Requests for passwords, one-time codes, card details, or personal information</li>
<li>Urgent wording about locked access, suspicious transfers, or immediate account review</li>
<li>Phone numbers, reply instructions, or websites that do not clearly match official TD Bank channels</li>
</ul>

<h2>How To Respond Safely</h2>
<p>A careful verification step can stop most TD Bank phishing scams before any damage happens.</p>
<p>If you receive a TD Bank fraud alert email, do not click links or trust contact details inside the message right away. Open the official TD Bank app, visit the official website directly, or use a trusted support number you look up yourself. If the alert is real, it should still appear through those official channels. If it is fake, checking independently can keep you from handing over access, codes, or personal information to a scammer.</p>
""".strip(),
        "faq_entities": [
            {
                "@type": "Question",
                "name": "Can a TD Bank fraud alert email be real?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes, some TD Bank fraud alert emails can be legitimate, but scammers also imitate them. The safest step is to verify the alert directly through the official TD Bank website, mobile app, or a trusted support number you find yourself."
                },
            },
            {
                "@type": "Question",
                "name": "How can I tell if a TD Bank fraud alert email is a scam?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Watch for urgent pressure, links that push you to log in immediately, requests for passwords or one-time codes, and contact details that only appear inside the email. A real alert should still make sense when you verify it independently through official TD Bank channels."
                },
            },
            {
                "@type": "Question",
                "name": "What should I do if I clicked a fake TD Bank fraud alert email?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Stop entering information, close the page, and check your TD Bank account through the official app or website. If you entered login details or codes, change your credentials right away and contact TD Bank through an official support channel you looked up independently."
                },
            },
        ],
    },
}

REQUIRED_SEO_KEYS = ("title", "description", "h1", "intro", "body_html", "faq_entities")


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

        missing = [key for key in REQUIRED_SEO_KEYS if not seo.get(key)]
        if missing:
            raise ValueError(f"Missing SEO fields for {path}: {', '.join(missing)}")

        if not isinstance(seo["faq_entities"], list) or not seo["faq_entities"]:
            raise ValueError(f"faq_entities must be a non-empty list for {path}")


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


def replace_seo_content_block(content: str, new_inner_html: str) -> str:
    open_pattern = re.compile(
        r'<div\b(?=[^>]*\bid=["\']seoContent["\'])[^>]*>',
        flags=re.IGNORECASE,
    )
    open_match = open_pattern.search(content)
    if not open_match:
        print("WARNING: seoContent block not found")
        return content

    start_open = open_match.start()
    end_open = open_match.end()

    tag_pattern = re.compile(r'</?div\b[^>]*>', flags=re.IGNORECASE)
    depth = 1
    search_pos = end_open
    close_end = None

    while True:
        tag_match = tag_pattern.search(content, search_pos)
        if not tag_match:
            break

        tag_text = tag_match.group(0)
        if tag_text.lower().startswith("</div"):
            depth -= 1
            if depth == 0:
                close_end = tag_match.end()
                break
        else:
            depth += 1

        search_pos = tag_match.end()

    if close_end is None:
        print("WARNING: seoContent closing </div> not found")
        return content

    original_block = content[start_open:close_end]

    opening_tag = content[start_open:end_open]
    new_block = f"{opening_tag}{new_inner_html}</div>"

    if original_block == new_block:
        return content

    return content[:start_open] + new_block + content[close_end:]


def update_jsonld_object(obj: Any, seo: Dict[str, Any], page_url: str) -> None:
    if isinstance(obj, list):
        for item in obj:
            update_jsonld_object(item, seo, page_url)
        return

    if not isinstance(obj, dict):
        return

    obj_type = obj.get("@type")
    obj_url = obj.get("url")
    obj_name = obj.get("name", "")

    if obj_type in {"CollectionPage", "WebPage"}:
        obj["name"] = seo["title"]
        obj["description"] = seo["description"]
        if obj.get("url") == page_url or obj_type == "WebPage":
            obj["url"] = page_url

    elif obj_type == "FAQPage":
        obj["mainEntity"] = seo["faq_entities"]

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


def replace_jsonld(content: str, seo: Dict[str, Any], page_url: str) -> str:
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
    updated = replace_seo_content_block(updated, seo["body_html"])
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
    print(f"Processing {len(files)} exact repo-root SEO page(s)...")

    updated_count = 0
    for path in files:
        if process_file(path):
            updated_count += 1

    print(f"Updated {updated_count} file(s). Done.")


if __name__ == "__main__":
    main()