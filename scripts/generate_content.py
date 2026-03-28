import requests
import sys
import logging
import re
from html import unescape

# -----------------------------
# CONFIG
# -----------------------------
RAILWAY_API = "https://awake-integrity-production-faa0.up.railway.app"
TIMEOUT = 60
MIN_PARAGRAPHS = 3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

WARNING_SECTION_TITLES = [
    "Common Warning Signs",
    "Red Flags To Watch For",
    "Signs This Might Be A Scam",
]

ACTION_SECTION_TITLES = [
    "What Should You Do?",
    "What To Do Next",
    "How To Respond Safely",
]

WARNING_BULLET_SETS = [
    [
        "Unexpected messages asking for money, codes, or personal information",
        "Pressure to act quickly before you can verify the message",
        "Links, websites, or senders that do not fully match the official source",
        "Requests for payment by crypto, gift card, wire transfer, or other hard-to-reverse methods",
    ],
    [
        "A sudden message that creates urgency without clear proof",
        "Requests to click a link, log in, or confirm sensitive details",
        "Sender names, websites, or contact details that do not fully match",
        "Payment instructions that are hard to reverse or verify",
    ],
    [
        "Warnings or alerts that push you to act before checking",
        "Requests for verification codes, personal details, or payment",
        "Suspicious links, fake support pages, or mismatched domains",
        "Pressure to move off trusted platforms or official apps",
    ],
]

ACTION_PARAGRAPHS = [
    "If you received something related to {keyword}, slow down before clicking, replying, or paying. Always verify through the official website or app instead of using the message itself.",
    "Before you respond to anything related to {keyword}, pause and verify it through a trusted source you find yourself.",
    "If this involves {keyword}, avoid clicking links or sending money until you confirm it through the official platform.",
]

BRAND_CASE = {
    "paypal": "PayPal",
    "whatsapp": "WhatsApp",
    "cash app": "Cash App",
    "tiktok": "TikTok",
    "icloud": "iCloud",
    "irs": "IRS",
    "usps": "USPS",
    "ups": "UPS",
    "fedex": "FedEx",
    "sms": "SMS",
    "otp": "OTP",
    "2fa": "2FA",
    "dm": "DM",
    "nft": "NFT",
    "ceo": "CEO",
    "binance": "Binance",
    "coinbase": "Coinbase",
    "metamask": "MetaMask",
    "trust wallet": "Trust Wallet",
    "google play": "Google Play",
    "zelle": "Zelle",
    "venmo": "Venmo",
    "amazon": "Amazon",
    "facebook": "Facebook",
    "instagram": "Instagram",
    "telegram": "Telegram",
    "snapchat": "Snapchat",
    "discord": "Discord",
    "crypto": "Crypto",
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "bank": "Bank",
    "chase": "Chase",
    "wells fargo": "Wells Fargo",
    "social security": "Social Security",
    "google": "Google",
    "apple": "Apple",
    "microsoft": "Microsoft",
    "steam": "Steam",
    "walmart": "Walmart",
    "target": "Target",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "vs", "with"
}


# -----------------------------
# HELPERS
# -----------------------------
def normalize_keyword(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip().lower())


def clean_base_keyword(text: str) -> str:
    kw = normalize_keyword(text)

    # Remove common leading wrappers that break phrasing
    kw = re.sub(r"^\s*is\s+", "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+", "", kw)
    kw = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+by\s+", "", kw)
    kw = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+on\s+", "", kw)
    kw = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+with\s+", "", kw)
    kw = re.sub(r"^\s*this\s+", "this ", kw)

    # Remove common trailing wrappers
    kw = re.sub(r"\s+a\s+scam$", "", kw)
    kw = re.sub(r"\s+or\s+legit$", "", kw)
    kw = re.sub(r"\s+or\s+scam$", "", kw)
    kw = re.sub(r"\s+legit$", "", kw)
    kw = re.sub(r"\s+real$", "", kw)
    kw = re.sub(r"\s+safe$", "", kw)
    kw = re.sub(r"\s+scam$", "", kw)

    # Clean malformed leftovers
    kw = re.sub(r"\s+a$", "", kw)
    kw = re.sub(r"\s+", " ", kw).strip()

    return kw


def display_keyword(text: str) -> str:
    return clean_base_keyword(text)


def apply_brand_case(text: str) -> str:
    result = f" {text} "
    for raw, proper in sorted(BRAND_CASE.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(raw) + r"(?![a-z0-9])"
        result = re.sub(pattern, proper, result, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", result).strip()


def title_case(text: str) -> str:
    text = normalize_keyword(text)
    if not text:
        return ""

    words = text.split()
    titled = []

    for i, word in enumerate(words):
        if i > 0 and word in SMALL_WORDS:
            titled.append(word)
        else:
            titled.append(word.capitalize())

    return apply_brand_case(" ".join(titled))


def variant_index(keyword: str, count: int) -> int:
    return sum(ord(c) for c in normalize_keyword(keyword)) % count if count else 0


def strip_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</li\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>", "- ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


# -----------------------------
# INTENT DETECTION
# -----------------------------
def detect_intent(keyword: str) -> str:
    kw = normalize_keyword(keyword)

    if kw.startswith(("is ", "can ", "did ")):
        return "question"
    if kw.startswith("how to ") or kw.startswith("what to do"):
        return "action"
    return "entity"


def detect_context(keyword: str) -> str:
    kw = normalize_keyword(keyword)

    if any(x in kw for x in ["amazon", "paypal", "bank", "zelle", "venmo", "cash app", "cash-app"]):
        return "payment"
    if any(x in kw for x in ["job", "hiring", "offer", "recruiter", "interview", "onboarding"]):
        return "job"
    if any(x in kw for x in ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft"]):
        return "crypto"
    if any(x in kw for x in ["usps", "fedex", "ups", "delivery", "package", "parcel", "shipment"]):
        return "delivery"

    return "general"


# -----------------------------
# SMART INTRO
# -----------------------------
def intro_paragraph(raw_keyword: str, display_kw: str) -> str:
    keyword_title = title_case(display_kw)
    intent = detect_intent(raw_keyword)

    if intent == "question":
        return (
            f"<p>{keyword_title} is a common question when a message, email, text, link, "
            f"or request feels suspicious. In many cases, the answer comes down to warning "
            f"signs like urgency, unusual payment requests, suspicious links, or pressure "
            f"to act before you can verify what is happening.</p>"
        )

    if intent == "action":
        return (
            f"<p>If you are trying to handle {keyword_title}, move carefully. Scams often "
            f"work by pushing people to react fast, so taking a moment to verify the source "
            f"can help you avoid clicking, replying, paying, or sharing information too soon.</p>"
        )

    return (
        f"<p>{keyword_title} scams are designed to look believable at first glance. They often "
        f"arrive as ordinary messages, alerts, emails, or requests, but the real goal is to "
        f"create pressure and get you to act before you stop to verify the details.</p>"
    )


# -----------------------------
# SCENARIO
# -----------------------------
def scenario_paragraph(raw_keyword: str, display_kw: str) -> str:
    keyword_title = title_case(display_kw)
    context = detect_context(raw_keyword)

    if context == "payment":
        return (
            f"<p>A common {keyword_title} scenario starts with a message about an account issue, "
            f"payment problem, suspicious login, refund, or urgent verification request. The goal "
            f"is often to make you click a link, sign in on a fake page, confirm personal details, "
            f"or send money before you realize the message is not legitimate.</p>"
        )

    if context == "job":
        return (
            f"<p>A typical {keyword_title} case may involve a job offer that feels unusually fast, "
            f"easy, or high-paying. It can also involve requests for personal details, upfront fees, "
            f"equipment payments, or pressure to move the conversation off a trusted platform.</p>"
        )

    if context == "crypto":
        return (
            f"<p>Many {keyword_title} scams involve fake investment opportunities, support impersonation, "
            f"wallet connections, recovery offers, or promises of guaranteed returns. The real objective "
            f"is often to get access to your funds, wallet, or account credentials.</p>"
        )

    if context == "delivery":
        return (
            f"<p>A common {keyword_title} message claims there is a shipping problem, missed delivery, "
            f"address issue, customs fee, or tracking error. These messages usually try to push you into "
            f"clicking a link or paying a small amount before you verify whether the delivery issue is real.</p>"
        )

    return (
        f"<p>In many {keyword_title} situations, the message is written to build trust and urgency at the "
        f"same time. It may sound routine, but it is often trying to get quick access to your information, "
        f"money, or account before you can slow down and verify it.</p>"
    )


# -----------------------------
# CLEANING
# -----------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"<h1[^>]*>.*?</h1>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<h2[^>]*>.*?</h2>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<h3[^>]*>.*?</h3>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = text.strip()

    cleaned = []

    if "<p" in text.lower():
        paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", text, flags=re.IGNORECASE | re.DOTALL)
        for p in paragraphs:
            p = strip_html(p)
            if len(p) > 40:
                cleaned.append(f"<p>{p}</p>")
        if cleaned:
            return "\n".join(cleaned[:4])

    plain_text = strip_html(text)
    paragraphs = [
        re.sub(r"\s+", " ", p).strip()
        for p in re.split(r"\n\s*\n|(?<=[.!?])\s{2,}", plain_text)
        if len(re.sub(r"\s+", " ", p).strip()) > 40
    ]

    return "\n".join(f"<p>{p}</p>" for p in paragraphs[:4])


def is_usable_content(html: str) -> bool:
    return html.count("<p>") >= MIN_PARAGRAPHS


# -----------------------------
# STRUCTURE
# -----------------------------
def enforce_structure(raw_keyword: str, display_kw: str, content: str) -> str:
    keyword_title = title_case(display_kw)
    idx = variant_index(display_kw, len(WARNING_SECTION_TITLES))

    intro = intro_paragraph(raw_keyword, display_kw)
    scenario = scenario_paragraph(raw_keyword, display_kw)

    warning_title = WARNING_SECTION_TITLES[idx]
    action_title = ACTION_SECTION_TITLES[idx]
    bullets = WARNING_BULLET_SETS[idx]
    action = ACTION_PARAGRAPHS[idx].format(keyword=keyword_title)

    bullet_html = "\n".join(f"<li>{b}</li>" for b in bullets)

    return f"""
<div class="content-block">
{intro}
{scenario}
{content}
</div>

<h2>{warning_title}</h2>
<ul>
{bullet_html}
</ul>

<h2>{action_title}</h2>
<p>{action}</p>
""".strip()


def fallback_content(raw_keyword: str, display_kw: str) -> str:
    keyword_title = title_case(display_kw)
    idx = variant_index(display_kw, len(WARNING_BULLET_SETS))

    intro = intro_paragraph(raw_keyword, display_kw)
    scenario = scenario_paragraph(raw_keyword, display_kw)

    bullets = WARNING_BULLET_SETS[idx]
    action = ACTION_PARAGRAPHS[idx].format(keyword=keyword_title)

    bullet_html = "\n".join(f"<li>{b}</li>" for b in bullets)

    return f"""
{intro}
{scenario}

<p>{keyword_title} scams often rely on urgency, impersonation, and requests that push you to act before you verify what is happening.</p>
<p>They may arrive through a text, email, website, social message, phone call, or payment request that looks routine at first.</p>
<p>The safest move is to verify everything independently before clicking, replying, sending money, or sharing personal details.</p>

<h2>{WARNING_SECTION_TITLES[idx]}</h2>
<ul>
{bullet_html}
</ul>

<h2>{ACTION_SECTION_TITLES[idx]}</h2>
<p>{action}</p>
""".strip()


# -----------------------------
# MAIN
# -----------------------------
def generate_content(keyword: str) -> str:
    raw_keyword = normalize_keyword(keyword)
    display_kw = display_keyword(raw_keyword)

    logging.info("Generating content for: %s", display_kw)

    try:
        res = requests.post(
            f"{RAILWAY_API}/seo-content",
            json={"keyword": display_kw},
            timeout=TIMEOUT
        )
        res.raise_for_status()

        raw = str(res.json().get("content", "")).strip()
        if not raw:
            raise ValueError("Empty content")

        cleaned = clean_text(raw)

        if not is_usable_content(cleaned):
            raise ValueError("Low quality")

        return enforce_structure(raw_keyword, display_kw, cleaned)

    except Exception as e:
        logging.warning("Fallback for %s: %s", display_kw, e)
        return fallback_content(raw_keyword, display_kw)


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else "amazon scam"
    print(generate_content(keyword))