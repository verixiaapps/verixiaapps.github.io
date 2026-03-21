import requests
import sys
import logging
import re

# -----------------------------
# CONFIG
# -----------------------------
RAILWAY_API = "https://awake-integrity-production-faa0.up.railway.app"
TIMEOUT = 60  # seconds
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
    "If you received something related to {keyword}, slow down before clicking, replying, or paying. Verify through the official website, app, or company contact information instead of using the message itself.",
    "Before you respond to anything related to {keyword}, pause and verify it through an official source you find yourself. Do not rely on the message, caller, or link that contacted you.",
    "If this appears to involve {keyword}, do not click links, send money, or share details until you confirm the situation through the official website, app, or customer support channel.",
]

FALLBACK_PARAGRAPH_SETS = [
    [
        "{keyword} messages are often designed to feel real at first glance. They may mention a payment issue, account problem, security alert, delivery update, job offer, or urgent request that pushes you to act before you stop and verify what you are seeing.",
        "Many of these scams work by creating pressure. The message may tell you to click a link immediately, confirm personal details, send money, connect a wallet, or respond before a deadline. That urgency is often meant to stop you from checking whether the sender, website, or offer is legitimate.",
        "Scammers also change the format depending on the situation. The same scam can show up as a text, email, job message, customer support alert, website pop-up, or payment request. The wording may change, but the goal is usually the same: get access to your money, account, or personal information.",
    ],
    [
        "A {keyword} message can look routine at first, especially if it mentions an account issue, payment problem, verification request, or delivery update. The goal is usually to make the message feel familiar enough that you respond before stopping to question it.",
        "These scams often create urgency fast. You may be told something is locked, delayed, suspended, rejected, or at risk unless you act right away. That pressure is meant to reduce the chance that you independently verify the sender or website.",
        "The same basic scam can appear in different formats depending on the target. It may arrive as a text, email, direct message, support alert, pop-up, or fake website. Even when the wording changes, the message usually pushes you toward the same result: sharing information, clicking a risky link, or sending money.",
    ],
    [
        "Messages related to {keyword} often work because they sound specific. They may reference a payment, account notice, security issue, order problem, support request, or other situation that makes the message feel immediately relevant.",
        "A common pattern is speed and pressure. Instead of giving you time to think, the message may demand fast action, claim there is a deadline, or suggest something will go wrong if you do not respond immediately. That urgency is part of the scam.",
        "Scammers also adapt the format to what feels most believable. You might see the same basic trick in a text, email, fake website, job message, customer support conversation, or payment request. The format changes, but the objective stays the same: get you to trust the message before you verify it.",
    ],
]


# -----------------------------
# KEYWORD HELPERS
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
    if count <= 0:
        return 0
    return sum(ord(char) for char in normalize_keyword(keyword)) % count


# -----------------------------
# CLEANING + STRUCTURE
# -----------------------------
def strip_markdown_artifacts(text: str) -> str:
    text = text.strip()

    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    cleaned = []

    skip_lines = {
        "key signals",
        "recommended action",
        "common warning signs",
        "what should you do?",
        "red flags to watch for",
        "signs this might be a scam",
        "what to do next",
        "how to respond safely",
    }

    for p in paragraphs:
        p = p.replace("\n", " ")
        p = re.sub(r"[ \t]+", " ", p).strip()

        if not p:
            continue
        if len(p) < 30:
            continue
        if p.lower() in skip_lines:
            continue

        cleaned.append(p)

    return cleaned


def clean_text(text: str) -> str:
    text = strip_markdown_artifacts(text)
    paragraphs = split_paragraphs(text)
    return "\n".join(f"<p>{p}</p>" for p in paragraphs)


def is_usable_content(html: str) -> bool:
    return html.count("<p>") >= MIN_PARAGRAPHS


def enforce_structure(keyword: str, content: str) -> str:
    keyword_title = title_case(display_keyword(keyword))
    idx = variant_index(keyword, len(WARNING_SECTION_TITLES))

    warning_title = WARNING_SECTION_TITLES[idx]
    action_title = ACTION_SECTION_TITLES[idx]
    warning_bullets = WARNING_BULLET_SETS[idx]
    action_paragraph = ACTION_PARAGRAPHS[idx].format(keyword=keyword_title)

    bullet_html = "\n".join(f"<li>{item}</li>" for item in warning_bullets)

    return f"""
<div class="content-block">
{content}
</div>

<h2>{warning_title}</h2>
<ul>
{bullet_html}
</ul>

<h2>{action_title}</h2>
<p>{action_paragraph}</p>
""".strip()


def fallback_content(keyword: str) -> str:
    keyword_title = title_case(display_keyword(keyword))
    idx = variant_index(keyword, len(FALLBACK_PARAGRAPH_SETS))

    paragraphs = "\n\n".join(
        f"<p>{paragraph.format(keyword=keyword_title)}</p>"
        for paragraph in FALLBACK_PARAGRAPH_SETS[idx]
    )

    warning_title = WARNING_SECTION_TITLES[idx]
    action_title = ACTION_SECTION_TITLES[idx]
    warning_bullets = WARNING_BULLET_SETS[idx]
    action_paragraph = ACTION_PARAGRAPHS[idx].format(keyword=keyword_title)

    bullet_html = "\n".join(f"<li>{item}</li>" for item in warning_bullets)

    return f"""
{paragraphs}

<h2>{warning_title}</h2>
<ul>
{bullet_html}
</ul>

<h2>{action_title}</h2>
<p>{action_paragraph}</p>
""".strip()


# -----------------------------
# MAIN GENERATION
# -----------------------------
def generate_content(keyword: str) -> str:
    keyword = keyword.strip()
    if not keyword:
        raise ValueError("Keyword cannot be empty")

    payload = {"keyword": keyword}
    logging.info("Generating SEO content for: '%s'", keyword)

    try:
        response = requests.post(
            f"{RAILWAY_API}/seo-content",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        raw_text = str(data.get("content", "")).strip()
        if not raw_text:
            raise ValueError("Empty content from API")

        cleaned = clean_text(raw_text)
        if not is_usable_content(cleaned):
            raise ValueError("Content did not meet minimum quality threshold")

        final_content = enforce_structure(keyword, cleaned)
        logging.info("Content generated successfully for '%s'", keyword)
        return final_content

    except requests.RequestException as e:
        logging.warning("Request failed for '%s': %s", keyword, e)
        return fallback_content(keyword)
    except Exception as e:
        logging.warning("Falling back for '%s' due to: %s", keyword, e)
        return fallback_content(keyword)


# -----------------------------
# SCRIPT ENTRY
# -----------------------------
if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else "amazon scam"

    try:
        content = generate_content(keyword)
        print(content)
    except Exception as e:
        logging.error("Fatal error: %s", e)
        sys.exit(1)