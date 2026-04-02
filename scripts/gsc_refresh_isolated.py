import os
import re
from typing import List, Optional

TARGET_TEMPLATE = os.getenv("TARGET_TEMPLATE", "all").strip().lower()
MAX_URLS = int(os.getenv("MAX_URLS_TO_REFRESH", "100"))
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"

TEMPLATE_PATHS = {
    "a": "scam-check-now",
    "b": "scam-check-now-b",
    "c": "scam-check-now-c",
}

ALLOWED_FIELDS = (
    "title",
    "meta_description",
    "answer_summary",
    "content_bridge",
)

QUERY_TERMS_TO_STRIP = {
    "is",
    "this",
    "a",
    "an",
    "the",
    "message",
    "messages",
    "email",
    "emails",
    "text",
    "texts",
    "notification",
    "notifications",
    "alert",
    "alerts",
    "real",
    "fake",
    "legit",
    "scam",
    "safe",
    "or",
    "and",
    "can",
    "i",
    "trust",
    "did",
    "get",
    "scammed",
    "by",
    "on",
    "with",
}

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
    "crypto": "crypto",
    "bank": "bank",
    "account": "account",
    "verification": "verification",
    "security": "security",
    "refund": "refund",
    "delivery": "delivery",
    "tracking": "tracking",
    "customs": "customs",
    "charge": "charge",
    "disabled": "disabled",
    "login": "login",
    "unusual": "unusual",
    "activity": "activity",
}


def get_target_dirs() -> List[str]:
    if TARGET_TEMPLATE == "all":
        return [TEMPLATE_PATHS["a"], TEMPLATE_PATHS["b"], TEMPLATE_PATHS["c"]]

    if TARGET_TEMPLATE not in TEMPLATE_PATHS:
        raise ValueError(f"Invalid TARGET_TEMPLATE: {TARGET_TEMPLATE}")

    return [TEMPLATE_PATHS[TARGET_TEMPLATE]]


def get_index_files(folder: str) -> List[str]:
    files: List[str] = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            if filename == "index.html":
                files.append(os.path.join(root, filename))
    return sorted(files)


def is_allowed_seo_page(path: str) -> bool:
    normalized = path.replace("\\", "/")
    allowed_prefixes = (
        "scam-check-now/",
        "scam-check-now-b/",
        "scam-check-now-c/",
    )
    if not normalized.endswith("/index.html"):
        return False
    return normalized.startswith(allowed_prefixes)


def slug_from_path(path: str) -> Optional[str]:
    normalized = path.replace("\\", "/").strip("/")
    parts = normalized.split("/")
    if len(parts) < 2:
        return None
    slug = parts[-2].strip()
    if not slug:
        return None
    return slug


def humanize_word(word: str) -> str:
    lower = word.lower()
    if lower in SPECIAL_REPLACEMENTS:
        return SPECIAL_REPLACEMENTS[lower]
    return lower.capitalize()


def slug_to_display_phrase(slug: str) -> str:
    words = [w for w in slug.strip().split("-") if w]
    cleaned_words = []
    for word in words:
        if word.lower() in QUERY_TERMS_TO_STRIP:
            continue
        cleaned_words.append(humanize_word(word))

    if not cleaned_words:
        cleaned_words = [humanize_word(w) for w in words if w]

    return " ".join(cleaned_words).strip()


def slug_to_topic_phrase(slug: str) -> str:
    phrase = slug_to_display_phrase(slug)
    if not phrase:
        return "Suspicious message"
    return phrase


def build_title(slug: str) -> str:
    topic = slug_to_topic_phrase(slug)

    if any(term in slug for term in ("refund",)):
        return f"Is {topic} a Scam? Warning Signs and What to Do"

    if any(term in slug for term in ("tracking", "delivery", "customs", "charge")):
        return f"Is {topic} Legit or a Scam? What to Check First"

    if any(term in slug for term in ("verification", "security", "login", "disabled", "account")):
        return f"Is {topic} a Scam? How to Spot the Warning Signs"

    return f"Is {topic} a Scam? Warning Signs and What to Do"


def build_description(slug: str) -> str:
    topic = slug_to_topic_phrase(slug)

    if any(term in slug for term in ("refund",)):
        return (
            f"Got a {topic}? Learn the common scam warning signs, fake link risks, "
            f"and what to do before clicking, replying, or sending information."
        )

    if any(term in slug for term in ("tracking", "delivery", "customs", "charge")):
        return (
            f"Received a {topic}? Review the scam signs, payment risks, and what to do "
            f"before clicking a tracking link or paying anything."
        )

    if any(term in slug for term in ("verification", "security", "login", "disabled", "account")):
        return (
            f"Received a {topic}? Learn the warning signs of fake account alerts, "
            f"suspicious links, and how to verify the message safely."
        )

    return (
        f"Check whether {topic} is a scam. Review warning signs, suspicious link risks, "
        f"and what to do before you click, reply, or send money."
    )


def build_answer_summary(slug: str) -> str:
    topic = slug_to_topic_phrase(slug)
    return (
        f"Use the checker below before you trust {topic.lower()}, click links, reply, "
        f"send money, or share personal information. Messages like this often use urgency, "
        f"fake authority, and misleading details to push fast decisions."
    )


def build_content_bridge(slug: str) -> str:
    topic = slug_to_topic_phrase(slug)
    return (
        f"If you are unsure about {topic.lower()}, use the checker above before clicking links, "
        f"replying, sending money, or sharing personal information. Pages like this help you slow down, "
        f"spot warning signs, and avoid costly mistakes before taking action."
    )


def replace_title(content: str, new_title: str) -> str:
    return re.sub(
        r"<title>.*?</title>",
        f"<title>{new_title}</title>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_meta_description(content: str, new_description: str) -> str:
    return re.sub(
        r'<meta\s+name="description"\s+content=".*?">',
        f'<meta name="description" content="{new_description}">',
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_answer_summary(content: str, new_text: str) -> str:
    return re.sub(
        r'(<p\s+id="answerSummary">)(.*?)(</p>)',
        rf"\1{new_text}\3",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_content_bridge(content: str, new_text: str) -> str:
    return re.sub(
        r'(<div\s+id="contentBridge"\s+class="content-bridge">)(.*?)(</div>)',
        rf"\1{new_text}\3",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def process_file(path: str) -> None:
    if not is_allowed_seo_page(path):
        print(f"SKIPPED (not allowed): {path}")
        return

    slug = slug_from_path(path)
    if not slug:
        print(f"SKIPPED (no slug): {path}")
        return

    with open(path, "r", encoding="utf-8") as file:
        original = file.read()

    updated = original

    new_title = build_title(slug)
    new_description = build_description(slug)
    new_answer_summary = build_answer_summary(slug)
    new_content_bridge = build_content_bridge(slug)

    updated = replace_title(updated, new_title)
    updated = replace_meta_description(updated, new_description)
    updated = replace_answer_summary(updated, new_answer_summary)
    updated = replace_content_bridge(updated, new_content_bridge)

    if updated != original:
        print(f"UPDATED: {path}")
        if not DRY_RUN:
            with open(path, "w", encoding="utf-8") as file:
                file.write(updated)
    else:
        print(f"NO CHANGE: {path}")


def main() -> None:
    if MAX_URLS <= 0:
        raise ValueError(f"Invalid MAX_URLS_TO_REFRESH: {MAX_URLS}")

    target_dirs = get_target_dirs()

    all_files: List[str] = []
    for directory in target_dirs:
        if os.path.exists(directory):
            all_files.extend(get_index_files(directory))

    all_files = [path for path in all_files if is_allowed_seo_page(path)]

    if not all_files:
        print("No allowed SEO page index.html files found.")
        return

    selected_files = all_files[:MAX_URLS]

    print(f"TARGET_TEMPLATE={TARGET_TEMPLATE}")
    print(f"DRY_RUN={DRY_RUN}")
    print(f"Processing {len(selected_files)} SEO page files...")

    for file_path in selected_files:
        process_file(file_path)

    print("Done.")


if __name__ == "__main__":
    main()