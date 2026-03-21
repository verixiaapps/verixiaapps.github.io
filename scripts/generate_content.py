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


# -----------------------------
# CLEANING + STRUCTURE
# -----------------------------
def strip_markdown_artifacts(text: str) -> str:
    text = text.strip()

    # remove code fences
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # remove markdown headings
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)

    # normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # convert markdown bullets into plain lines so they do not become junk paragraphs
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    # remove excess blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    cleaned = []

    for p in paragraphs:
        p = p.replace("\n", " ")
        p = re.sub(r"[ \t]+", " ", p).strip()

        # skip obvious junk lines
        if not p:
            continue
        if len(p) < 30:
            continue
        if p.lower() in {"key signals", "recommended action", "common warning signs", "what should you do?"}:
            continue

        cleaned.append(p)

    return cleaned


def clean_text(text: str) -> str:
    text = strip_markdown_artifacts(text)
    paragraphs = split_paragraphs(text)
    return "\n".join(f"<p>{p}</p>" for p in paragraphs)


def is_usable_content(html: str) -> bool:
    paragraph_count = html.count("<p>")
    return paragraph_count >= MIN_PARAGRAPHS


def enforce_structure(keyword: str, content: str) -> str:
    keyword_title = title_case(display_keyword(keyword))

    return f"""
<div class="content-block">
{content}
</div>

<h2>Common Warning Signs</h2>
<ul>
<li>Unexpected messages asking for money, codes, or personal information</li>
<li>Pressure to act quickly before you can verify the message</li>
<li>Links, websites, or senders that do not fully match the official source</li>
<li>Requests for payment by crypto, gift card, wire transfer, or other hard-to-reverse methods</li>
</ul>

<h2>What Should You Do?</h2>
<p>If you received something related to {keyword_title}, slow down before clicking, replying, or paying. Verify through the official website, app, or company contact information instead of using the message itself.</p>
""".strip()


def fallback_content(keyword: str) -> str:
    keyword_title = title_case(display_keyword(keyword))

    return f"""
<p>{keyword_title} messages are often designed to feel real at first glance. They may mention a payment issue, account problem, security alert, delivery update, job offer, or urgent request that pushes you to act before you stop and verify what you are seeing.</p>

<p>Many of these scams work by creating pressure. The message may tell you to click a link immediately, confirm personal details, send money, connect a wallet, or respond before a deadline. That urgency is often meant to stop you from checking whether the sender, website, or offer is legitimate.</p>

<p>Scammers also change the format depending on the situation. The same scam can show up as a text, email, job message, customer support alert, website pop-up, or payment request. The wording may change, but the goal is usually the same: get access to your money, account, or personal information.</p>

<h2>Common Warning Signs</h2>
<ul>
<li>Unexpected requests for money, codes, or personal information</li>
<li>Urgent language that pushes immediate action</li>
<li>Suspicious links, senders, or websites that are hard to verify</li>
<li>Payment requests through crypto, gift cards, or wire transfer</li>
</ul>

<h2>What Should You Do?</h2>
<p>Do not click links, send money, or share information until you verify the message through an official source. If something feels rushed, mismatched, or hard to confirm, treat it cautiously until you can verify it independently.</p>
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