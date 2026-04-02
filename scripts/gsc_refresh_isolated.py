import os
import re
from typing import List, Optional, Set

TARGET_TEMPLATE = os.getenv("TARGET_TEMPLATE", "all").strip().lower()
MAX_URLS = int(os.getenv("MAX_URLS_TO_REFRESH", "1"))
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"

TEMPLATE_PATHS = {
    "a": "scam-check-now",
    "b": "scam-check-now-b",
    "c": "scam-check-now-c",
}

TODAY_TARGET_SLUGS = [
    "is-amazon-refund-message-legit-or-scam",
    "is-google-account-disabled-email-legit-or-scam",
    "is-fedex-customs-charge-email-legit-or-scam",
    "is-venmo-verification-code-text-real-or-fake",
    "is-bank-debit-card-suspension-email-legit-or-scam",
    "is-whatsapp-unusual-login-email-legit-or-scam",
    "is-telegram-suspicious-activity-message-legit-or-scam",
    "is-usps-tracking-text-legit-or-scam",
    "is-venmo-security-alert-email-legit-or-scam",
    "is-bank-account-closure-email-legit-or-scam",
    "is-apple-account-verification-email-legit-or-scam",
    "snapchat-scams",
    "is-fedex-delivery-legit-or-scam",
    "is-security-alert-message-legit-or-scam",
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

TITLE_MAP = {
    "is-amazon-refund-message-legit-or-scam": "Amazon Refund Message Scam? Warning Signs and What to Do",
    "is-google-account-disabled-email-legit-or-scam": "Google Account Disabled Email Scam? How to Spot the Warning Signs",
    "is-fedex-customs-charge-email-legit-or-scam": "FedEx Customs Charge Email Scam? What to Check First",
    "is-venmo-verification-code-text-real-or-fake": "Venmo Verification Code Text Scam? Real or Fake Warning Signs",
    "is-bank-debit-card-suspension-email-legit-or-scam": "Bank Debit Card Suspension Email Scam? Warning Signs and What to Do",
    "is-whatsapp-unusual-login-email-legit-or-scam": "WhatsApp Unusual Login Email Scam? How to Check Safely",
    "is-telegram-suspicious-activity-message-legit-or-scam": "Telegram Suspicious Activity Message Scam? Warning Signs and What to Do",
    "is-usps-tracking-text-legit-or-scam": "USPS Tracking Text Scam? What to Check Before You Click",
    "is-venmo-security-alert-email-legit-or-scam": "Venmo Security Alert Email Scam? How to Spot the Warning Signs",
    "is-bank-account-closure-email-legit-or-scam": "Bank Account Closure Email Scam? Warning Signs and What to Do",
    "is-apple-account-verification-email-legit-or-scam": "Apple Account Verification Email Scam? How to Spot the Warning Signs",
    "snapchat-scams": "Snapchat Scams: Common Warning Signs and What to Do",
    "is-fedex-delivery-legit-or-scam": "FedEx Delivery Message Scam? What to Check First",
    "is-security-alert-message-legit-or-scam": "Security Alert Message Scam? Warning Signs and What to Do",
}

DESCRIPTION_MAP = {
    "is-amazon-refund-message-legit-or-scam": "Got an Amazon refund message? Learn the scam warning signs, suspicious link risks, and what to do before you click, reply, or send information.",
    "is-google-account-disabled-email-legit-or-scam": "Received a Google account disabled email? Learn the warning signs of fake account alerts and how to verify the message safely.",
    "is-fedex-customs-charge-email-legit-or-scam": "Got a FedEx customs charge email? Review the scam signs, payment risks, and what to do before clicking or paying anything.",
    "is-venmo-verification-code-text-real-or-fake": "Received a Venmo verification code text? Learn how to spot scam signs, fake urgency, and risky requests before taking action.",
    "is-bank-debit-card-suspension-email-legit-or-scam": "Received a bank debit card suspension email? Learn the common warning signs, suspicious link risks, and how to verify it safely.",
    "is-whatsapp-unusual-login-email-legit-or-scam": "Got a WhatsApp unusual login email? Review the scam warning signs and what to do before you click or share information.",
    "is-telegram-suspicious-activity-message-legit-or-scam": "Received a Telegram suspicious activity message? Learn the warning signs of fake security alerts and risky login links.",
    "is-usps-tracking-text-legit-or-scam": "Got a USPS tracking text? Review the scam warning signs, fake tracking link risks, and what to do before clicking.",
    "is-venmo-security-alert-email-legit-or-scam": "Received a Venmo security alert email? Learn the warning signs of fake account alerts and how to verify it safely.",
    "is-bank-account-closure-email-legit-or-scam": "Got a bank account closure email? Review the scam warning signs, suspicious link risks, and what to do before taking action.",
    "is-apple-account-verification-email-legit-or-scam": "Received an Apple account verification email? Learn the scam signs, suspicious link risks, and how to verify it safely.",
    "snapchat-scams": "Learn common Snapchat scam warning signs, fake account risks, and what to do before replying, clicking, or sharing information.",
    "is-fedex-delivery-legit-or-scam": "Got a FedEx delivery message? Review the scam signs, fake tracking link risks, and what to do before clicking.",
    "is-security-alert-message-legit-or-scam": "Received a security alert message? Learn the warning signs of fake alerts, suspicious links, and what to do next.",
}

ANSWER_SUMMARY_MAP = {
    "is-amazon-refund-message-legit-or-scam": "Use the checker below before you trust an Amazon refund message, click links, reply, or share personal information. Messages like this often use fake urgency and refund confusion to push fast decisions.",
    "is-google-account-disabled-email-legit-or-scam": "Use the checker below before you trust a Google account disabled email, click links, or enter account details. Messages like this often use fear and fake account warnings to trigger fast action.",
    "is-fedex-customs-charge-email-legit-or-scam": "Use the checker below before you trust a FedEx customs charge email, click a payment link, or send information. Messages like this often use delivery pressure and small-fee requests to push fast decisions.",
    "is-venmo-verification-code-text-real-or-fake": "Use the checker below before you trust a Venmo verification code text, share a code, or reply. Messages like this often use fake urgency and account access tricks to push fast decisions.",
    "is-bank-debit-card-suspension-email-legit-or-scam": "Use the checker below before you trust a bank debit card suspension email, click links, or enter account details. Messages like this often use fake account threats to pressure quick action.",
    "is-whatsapp-unusual-login-email-legit-or-scam": "Use the checker below before you trust a WhatsApp unusual login email, click links, or share account information. Messages like this often use fake security pressure to trigger fast decisions.",
    "is-telegram-suspicious-activity-message-legit-or-scam": "Use the checker below before you trust a Telegram suspicious activity message, click links, or enter login details. Messages like this often use fake security alerts to pressure quick action.",
    "is-usps-tracking-text-legit-or-scam": "Use the checker below before you trust a USPS tracking text, click a tracking link, or pay anything. Messages like this often use delivery urgency and fake tracking pages to push fast decisions.",
    "is-venmo-security-alert-email-legit-or-scam": "Use the checker below before you trust a Venmo security alert email, click links, or enter account information. Messages like this often use fake warnings and misleading details to push fast action.",
    "is-bank-account-closure-email-legit-or-scam": "Use the checker below before you trust a bank account closure email, click links, or share personal information. Messages like this often use fake urgency and account threats to push fast decisions.",
    "is-apple-account-verification-email-legit-or-scam": "Use the checker below before you trust an Apple account verification email, click links, or enter login details. Messages like this often use fake authority and misleading details to push fast action.",
    "snapchat-scams": "Use the checker below before you trust suspicious Snapchat messages, links, or account requests. Scams like this often rely on urgency, impersonation, and misleading details to push quick decisions.",
    "is-fedex-delivery-legit-or-scam": "Use the checker below before you trust a FedEx delivery message, click links, or send information. Messages like this often use fake shipping pressure and misleading tracking details to push quick action.",
    "is-security-alert-message-legit-or-scam": "Use the checker below before you trust a security alert message, click links, or enter account details. Messages like this often use fear and fake warnings to pressure fast decisions.",
}

CONTENT_BRIDGE_MAP = {
    "is-amazon-refund-message-legit-or-scam": "If you are unsure about an Amazon refund message, use the checker above before clicking links, replying, or sharing information. Pages like this help you spot refund scam warning signs early and avoid costly mistakes.",
    "is-google-account-disabled-email-legit-or-scam": "If you are unsure about a Google account disabled email, use the checker above before clicking links or entering login details. Pages like this help you slow down, verify safely, and avoid fake account alert scams.",
    "is-fedex-customs-charge-email-legit-or-scam": "If you are unsure about a FedEx customs charge email, use the checker above before clicking payment links or sending information. Pages like this help you spot delivery-payment scams before taking action.",
    "is-venmo-verification-code-text-real-or-fake": "If you are unsure about a Venmo verification code text, use the checker above before replying or sharing any code. Pages like this help you catch account access scams before they turn into a bigger problem.",
    "is-bank-debit-card-suspension-email-legit-or-scam": "If you are unsure about a bank debit card suspension email, use the checker above before clicking links or entering account details. Pages like this help you catch fake banking alerts before taking action.",
    "is-whatsapp-unusual-login-email-legit-or-scam": "If you are unsure about a WhatsApp unusual login email, use the checker above before clicking links or sharing information. Pages like this help you slow down and spot fake security alerts early.",
    "is-telegram-suspicious-activity-message-legit-or-scam": "If you are unsure about a Telegram suspicious activity message, use the checker above before clicking links or entering login details. Pages like this help you catch fake security messages before they cost you access.",
    "is-usps-tracking-text-legit-or-scam": "If you are unsure about a USPS tracking text, use the checker above before clicking links or paying anything. Pages like this help you spot fake delivery messages and risky tracking pages early.",
    "is-venmo-security-alert-email-legit-or-scam": "If you are unsure about a Venmo security alert email, use the checker above before clicking links or entering account details. Pages like this help you spot fake payment-app warnings before taking action.",
    "is-bank-account-closure-email-legit-or-scam": "If you are unsure about a bank account closure email, use the checker above before clicking links or sharing information. Pages like this help you catch fake banking alerts and avoid costly mistakes.",
    "is-apple-account-verification-email-legit-or-scam": "If you are unsure about an Apple account verification email, use the checker above before clicking links or entering login details. Pages like this help you catch fake account verification scams early.",
    "snapchat-scams": "If you are dealing with suspicious Snapchat messages or account requests, use the checker above before clicking links, replying, or sharing information. Pages like this help you spot common Snapchat scam patterns early.",
    "is-fedex-delivery-legit-or-scam": "If you are unsure about a FedEx delivery message, use the checker above before clicking links or sending information. Pages like this help you spot fake delivery messages before taking action.",
    "is-security-alert-message-legit-or-scam": "If you are unsure about a security alert message, use the checker above before clicking links or entering account details. Pages like this help you slow down, verify safely, and avoid fake alert scams.",
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
    allowed_prefixes = (
        "scam-check-now/",
        "scam-check-now-b/",
        "scam-check-now-c/",
    )
    return normalized.startswith(allowed_prefixes) and normalized.endswith("/index.html")


def slug_from_path(path: str) -> Optional[str]:
    normalized = path.replace("\\", "/").strip("/")
    parts = normalized.split("/")
    if len(parts) < 2:
        return None
    return parts[-2].strip() or None


def get_target_files() -> List[str]:
    files: List[str] = []
    seen: Set[str] = set()

    target_dirs = get_target_dirs()
    target_slugs = get_target_slugs()

    for base_dir in target_dirs:
        for slug in target_slugs:
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
    phrase = " ".join(cleaned).strip()
    return phrase or "Suspicious message"


def build_title(slug: str) -> str:
    return TITLE_MAP.get(slug, f"{slug_to_topic_phrase(slug)} Scam? Warning Signs and What to Do")


def build_description(slug: str) -> str:
    return DESCRIPTION_MAP.get(
        slug,
        f"Check whether {slug_to_topic_phrase(slug)} is a scam. Review warning signs, suspicious link risks, and what to do before acting.",
    )


def build_answer_summary(slug: str) -> str:
    return ANSWER_SUMMARY_MAP.get(
        slug,
        f"Use the checker below before you trust {slug_to_topic_phrase(slug).lower()}, click links, reply, send money, or share personal information.",
    )


def build_content_bridge(slug: str) -> str:
    return CONTENT_BRIDGE_MAP.get(
        slug,
        f"If you are unsure about {slug_to_topic_phrase(slug).lower()}, use the checker above before clicking links, replying, or sending information.",
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
        lambda match: f"{match.group(1)}{new_text}{match.group(3)}",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_content_bridge(content: str, new_text: str) -> str:
    return re.sub(
        r'(<div\s+id="contentBridge"\s+class="content-bridge">)(.*?)(</div>)',
        lambda match: f"{match.group(1)}{new_text}{match.group(3)}",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


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

    updated = original
    updated = replace_title(updated, build_title(slug))
    updated = replace_meta_description(updated, build_description(slug))
    updated = replace_answer_summary(updated, build_answer_summary(slug))
    updated = replace_content_bridge(updated, build_content_bridge(slug))

    if updated == original:
        print(f"NO CHANGE: {path}")
        return False

    print(f"UPDATED: {path}")

    if not DRY_RUN:
        with open(path, "w", encoding="utf-8") as file:
            file.write(updated)

    return True


def main() -> None:
    target_files = get_target_files()

    if not target_files:
        print("No matching GSC target SEO pages found.")
        return

    print(f"TARGET_TEMPLATE={TARGET_TEMPLATE}")
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