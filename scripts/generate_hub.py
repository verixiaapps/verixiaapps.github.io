import os
import re
import html
from pathlib import Path
from typing import Dict, List, Tuple


HUB_FILE_PATH = os.getenv("HUB_FILE_PATH", "scam-check-now/hubs/all-scam-checks/index.html").strip()
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"

ROOT_FOLDERS: List[Tuple[str, str, str]] = [
    ("scam-check-now", "Template A Pages", "/scam-check-now/"),
    ("scam-check-now-b", "Template B Pages", "/scam-check-now-b/"),
    ("scam-check-now-c", "Template C Pages", "/scam-check-now-c/"),
]

AUTO_START = "<!-- AUTO_HUB_SECTIONS_START -->"
AUTO_END = "<!-- AUTO_HUB_SECTIONS_END -->"


def escape_text(text: str) -> str:
    return html.escape(text, quote=False)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def slug_to_title(slug: str) -> str:
    text = slug.strip().strip("/")
    if not text:
        return "Untitled Page"

    words = text.split("-")
    special = {
        "amazon": "Amazon",
        "apple": "Apple",
        "google": "Google",
        "gmail": "Gmail",
        "paypal": "PayPal",
        "venmo": "Venmo",
        "zelle": "Zelle",
        "cash": "Cash",
        "app": "App",
        "usps": "USPS",
        "ups": "UPS",
        "fedex": "FedEx",
        "dhl": "DHL",
        "irs": "IRS",
        "sms": "SMS",
        "otp": "OTP",
        "td": "TD",
        "pnc": "PNC",
        "us": "US",
        "binance": "Binance",
        "coinbase": "Coinbase",
        "crypto": "Crypto",
        "whatsapp": "WhatsApp",
        "linkedin": "LinkedIn",
        "facebook": "Facebook",
        "instagram": "Instagram",
        "tiktok": "TikTok",
        "discord": "Discord",
        "netflix": "Netflix",
        "spotify": "Spotify",
        "microsoft": "Microsoft",
        "robinhood": "Robinhood",
        "revolut": "Revolut",
        "citibank": "Citibank",
    }
    lower_words = {"a", "an", "and", "or", "the", "to", "for", "of", "in", "on", "from"}

    out: List[str] = []
    for i, word in enumerate(words):
        lower = word.lower()
        if lower in special:
            out.append(special[lower])
        elif i > 0 and lower in lower_words:
            out.append(lower)
        else:
            out.append(lower.capitalize())

    title = " ".join(out)

    replacements = [
        (" Or Scam ", " or Scam "),
        (" Or Fake ", " or Fake "),
        (" Real Or Fake", " Real or Fake"),
        (" Legit Or Scam", " Legit or Scam"),
        (" A Scam", " a Scam"),
    ]
    for old, new in replacements:
        title = title.replace(old, new)

    return title.strip()


def extract_slug_from_file(file_path: Path, root_folder: str) -> str:
    relative = normalize_path(str(file_path.relative_to(root_folder)))
    if not relative.endswith("/index.html"):
        raise ValueError(f"Unexpected page path: {file_path}")
    return relative[:-11].strip("/")


def extract_title_from_html(content: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", content, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def clean_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    title = html.unescape(title)
    return title


def choose_display_title(file_path: Path, slug: str) -> str:
    try:
        content = file_path.read_text(encoding="utf-8")
        html_title = clean_title(extract_title_from_html(content))
        if html_title:
            return html_title
    except Exception:
        pass

    return slug_to_title(slug)


def discover_pages(root_folder: str, url_prefix: str) -> List[Dict[str, str]]:
    folder = Path(root_folder)
    if not folder.exists():
        return []

    pages: List[Dict[str, str]] = []

    for file_path in sorted(folder.rglob("index.html")):
        normalized = normalize_path(str(file_path))

        if "/hubs/" in normalized:
            continue

        slug = extract_slug_from_file(file_path, root_folder)
        if not slug:
            continue

        href = f"{url_prefix}{slug}/"
        title = choose_display_title(file_path, slug)

        pages.append(
            {
                "title": title,
                "href": href,
                "slug": slug,
                "sort_key": slug.lower(),
            }
        )

    pages.sort(key=lambda x: x["sort_key"])
    return pages


def build_section_html(section_title: str, pages: List[Dict[str, str]], section_id: str) -> str:
    count_text = f"{len(pages)} page" if len(pages) == 1 else f"{len(pages)} pages"

    items = "\n".join(
        f'        <li><a href="{escape_text(page["href"])}">{escape_text(page["title"])}</a></li>'
        for page in pages
    )

    return f"""    <div class="link-section" id="{escape_text(section_id)}">
      <h3>{escape_text(section_title)} <span style="font-size:14px;color:#a7b7d3;font-weight:800;">({escape_text(count_text)})</span></h3>
      <ul class="related-links">
{items}
      </ul>
    </div>"""


def build_auto_sections() -> str:
    section_blocks: List[str] = []

    total_pages = 0
    for root_folder, label, url_prefix in ROOT_FOLDERS:
        pages = discover_pages(root_folder, url_prefix)
        total_pages += len(pages)
        section_id = f"auto-{root_folder.replace('/', '-').replace('_', '-')}"
        section_blocks.append(build_section_html(label, pages, section_id))

    summary_block = f"""    <div class="content-bridge">
      Browse all published scam check pages across Templates A, B, and C. This hub updates automatically and helps users find exact warning pages for suspicious emails, texts, payment alerts, delivery notices, recruiter messages, account warnings, and more.
      <div style="margin-top:10px;font-size:13px;color:#a7b7d3;font-weight:800;">Auto-indexed pages currently linked here: {total_pages}</div>
    </div>"""

    return "\n".join([summary_block] + section_blocks)


def replace_auto_section(content: str, new_inner_html: str) -> str:
    pattern = re.compile(
        rf"({re.escape(AUTO_START)})(.*)({re.escape(AUTO_END)})",
        flags=re.DOTALL,
    )
    replacement = f"{AUTO_START}\n{new_inner_html}\n    {AUTO_END}"
    updated, count = pattern.subn(replacement, content, count=1)

    if count == 0:
        raise ValueError(
            f"Hub file must contain markers:\n{AUTO_START}\n...\n{AUTO_END}"
        )

    return updated


def validate_hub_file_exists() -> Path:
    hub_path = Path(HUB_FILE_PATH)
    if not hub_path.exists():
        raise FileNotFoundError(f"Missing hub file: {HUB_FILE_PATH}")
    return hub_path


def process_hub() -> bool:
    hub_path = validate_hub_file_exists()
    original = hub_path.read_text(encoding="utf-8")
    auto_sections = build_auto_sections()
    updated = replace_auto_section(original, auto_sections)

    if updated == original:
        print("NO CHANGE: hub already up to date")
        return False

    print(f"UPDATED: {HUB_FILE_PATH}")

    if not DRY_RUN:
        hub_path.write_text(updated, encoding="utf-8", newline="")

    return True


def main() -> None:
    print(f"DRY_RUN={DRY_RUN}")
    print(f"HUB_FILE_PATH={HUB_FILE_PATH}")

    changed = process_hub()
    if changed:
        print("Hub refresh complete.")
    else:
        print("Hub refresh complete. Nothing changed.")


if __name__ == "__main__":
    main()