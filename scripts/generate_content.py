import requests
import sys
import logging
import re

# -----------------------------
# CONFIG
# -----------------------------
RAILWAY_API = "https://awake-integrity-production-faa0.up.railway.app"
TIMEOUT = 60  # seconds

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
def clean_text(text: str) -> str:
    text = text.strip()

    # remove markdown headings like ### ####
    text = re.sub(r'#{1,6}\s*', '', text)

    # normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # split into paragraphs on blank lines
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # collapse single-line breaks and extra spaces inside each paragraph
    cleaned_paragraphs = []
    for p in paragraphs:
        p = p.replace("\n", " ")
        p = re.sub(r'[ \t]+', ' ', p).strip()
        if p:
            cleaned_paragraphs.append(f"<p>{p}</p>")

    return "\n".join(cleaned_paragraphs)


def enforce_structure(keyword: str, content: str) -> str:
    """
    Keeps structure consistent and renders AI output as real HTML paragraphs.
    """

    keyword_display = display_keyword(keyword)
    keyword_title = title_case(keyword_display)

    return f"""
<div class="content-block">
{content}
</div>

<h2>Common Warning Signs</h2>
<ul>
<li>Unexpected messages asking for money or personal information</li>
<li>Urgent pressure to act quickly</li>
<li>Suspicious links or unfamiliar senders</li>
<li>Requests for payment via gift cards, crypto, or wire transfer</li>
</ul>

<h2>What Should You Do?</h2>
<p>If you receive a message related to {keyword_title}, do not click links or send money. Verify directly through official sources and report suspicious activity.</p>
"""


def fallback_content(keyword: str) -> str:
    keyword_display = display_keyword(keyword)
    keyword_title = title_case(keyword_display)

    return f"""
<p>{keyword_title} scams are commonly used to trick people into sending money or sharing sensitive information. Scammers often impersonate trusted brands or create urgency.</p>

<h2>Common Warning Signs</h2>
<ul>
<li>Requests for payment or personal information</li>
<li>Messages that create urgency or fear</li>
<li>Unknown links or suspicious senders</li>
</ul>

<h2>What Should You Do?</h2>
<p>Avoid clicking links, do not send money, and verify through official sources before taking any action.</p>
"""


# -----------------------------
# MAIN GENERATION
# -----------------------------
def generate_content(keyword: str) -> str:
    if not keyword.strip():
        raise ValueError("Keyword cannot be empty")

    payload = {"keyword": keyword.strip()}
    logging.info(f"Generating SEO content for: '{keyword}'")

    try:
        response = requests.post(
            f"{RAILWAY_API}/seo-content",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        raw_text = data.get("content", "").strip()

        if not raw_text:
            raise ValueError("Empty content from API")

        cleaned = clean_text(raw_text)

        # enforce structure for SEO consistency
        final_content = enforce_structure(keyword, cleaned)

        logging.info(f"Content generated successfully for '{keyword}'")
        return final_content

    except Exception as e:
        logging.warning(f"Falling back for '{keyword}' due to: {e}")
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
        logging.error(f"Fatal error: {e}")
        sys.exit(1)