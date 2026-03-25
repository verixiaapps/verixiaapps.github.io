import requests
import sys
import logging
import re

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

# -----------------------------
# INTENT DETECTION (🔥 NEW)
# -----------------------------
def detect_intent(keyword: str) -> str:
    kw = keyword.lower()

    if kw.startswith("is ") or kw.startswith("can ") or kw.startswith("did "):
        return "question"
    if "how to" in kw or "what to do" in kw:
        return "action"
    return "entity"


def detect_context(keyword: str) -> str:
    kw = keyword.lower()

    if any(x in kw for x in ["amazon", "paypal", "bank", "zelle", "venmo"]):
        return "payment"
    if any(x in kw for x in ["job", "hiring", "offer"]):
        return "job"
    if any(x in kw for x in ["crypto", "bitcoin", "ethereum"]):
        return "crypto"
    if any(x in kw for x in ["usps", "fedex", "ups", "delivery"]):
        return "delivery"

    return "general"


# -----------------------------
# SMART INTRO (🔥 BIG SEO WIN)
# -----------------------------
def intro_paragraph(keyword: str) -> str:
    keyword_title = title_case(display_keyword(keyword))
    intent = detect_intent(keyword)

    if intent == "question":
        return f"<p>{keyword_title} is a question many people ask when something feels off. In most cases, the answer depends on warning signs like urgency, suspicious links, or unusual requests.</p>"

    if intent == "action":
        return f"<p>If you're trying to handle {keyword_title}, it's important to move carefully. Scams often rely on quick reactions, so taking a moment to verify details can prevent mistakes.</p>"

    return f"<p>{keyword_title} scams are designed to look believable at first glance. They often appear as normal messages, alerts, or requests, but are meant to push you into acting quickly.</p>"


# -----------------------------
# SCENARIO (context aware)
# -----------------------------
def scenario_paragraph(keyword: str) -> str:
    keyword_title = title_case(display_keyword(keyword))
    context = detect_context(keyword)

    if context == "payment":
        return f"<p>A common {keyword_title} scenario involves a message about a payment issue or account problem. You may be asked to log in, confirm details, or send money to resolve it.</p>"

    if context == "job":
        return f"<p>A typical {keyword_title} case includes a job offer that feels unusually fast or high-paying. It may request personal details, fees, or moving off-platform.</p>"

    if context == "crypto":
        return f"<p>Many {keyword_title} scams involve fake investments, wallet connections, or promises of guaranteed returns designed to get access to your funds.</p>"

    if context == "delivery":
        return f"<p>A common {keyword_title} message claims there is a delivery issue and asks you to click a link or pay a small fee.</p>"

    return f"<p>In many {keyword_title} situations, the message is designed to create urgency and trust at the same time.</p>"


# -----------------------------
# HELPERS
# -----------------------------
def normalize_keyword(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def display_keyword(text: str) -> str:
    kw = normalize_keyword(text)
    if kw.endswith(" scam"):
        kw = kw[:-5].strip()
    return kw


def title_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


def variant_index(keyword: str, count: int) -> int:
    return sum(ord(c) for c in keyword) % count if count else 0


# -----------------------------
# CLEANING
# -----------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)

    paragraphs = [
        p.strip()
        for p in text.split("\n\n")
        if len(p.strip()) > 40
    ]

    return "\n".join(f"<p>{p}</p>" for p in paragraphs[:4])


def is_usable_content(html: str) -> bool:
    return html.count("<p>") >= MIN_PARAGRAPHS


# -----------------------------
# STRUCTURE
# -----------------------------
def enforce_structure(keyword: str, content: str) -> str:
    keyword_title = title_case(display_keyword(keyword))
    idx = variant_index(keyword, len(WARNING_SECTION_TITLES))

    intro = intro_paragraph(keyword)
    scenario = scenario_paragraph(keyword)

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


def fallback_content(keyword: str) -> str:
    keyword_title = title_case(display_keyword(keyword))
    idx = variant_index(keyword, len(WARNING_BULLET_SETS))

    intro = intro_paragraph(keyword)
    scenario = scenario_paragraph(keyword)

    bullets = WARNING_BULLET_SETS[idx]
    action = ACTION_PARAGRAPHS[idx].format(keyword=keyword_title)

    bullet_html = "\n".join(f"<li>{b}</li>" for b in bullets)

    return f"""
{intro}
{scenario}

<p>{keyword_title} scams often rely on urgency and impersonation.</p>
<p>They may appear as normal messages, emails, or websites.</p>
<p>Always verify independently before taking action.</p>

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
    keyword = keyword.strip()
    logging.info("Generating content for: %s", keyword)

    try:
        res = requests.post(
            f"{RAILWAY_API}/seo-content",
            json={"keyword": keyword},
            timeout=TIMEOUT
        )
        res.raise_for_status()

        raw = str(res.json().get("content", "")).strip()
        if not raw:
            raise ValueError("Empty content")

        cleaned = clean_text(raw)

        if not is_usable_content(cleaned):
            raise ValueError("Low quality")

        return enforce_structure(keyword, cleaned)

    except Exception as e:
        logging.warning("Fallback for %s: %s", keyword, e)
        return fallback_content(keyword)


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else "amazon scam"
    print(generate_content(keyword))