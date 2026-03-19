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
# CLEANING + STRUCTURE
# -----------------------------
def clean_text(text: str) -> str:
    text = text.strip()

    # remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)

    # basic cleanup
    text = re.sub(r'[ \t]+', ' ', text)

    return text


def enforce_structure(keyword: str, content: str) -> str:
    """
    Ensures consistent SEO structure across all pages
    """

    keyword_title = keyword.title()

    return f"""
<h2>Is {keyword_title} a Scam?</h2>
<p>{content}</p>

<h2>Common Warning Signs</h2>
<ul>
<li>Unexpected messages asking for money or personal information</li>
<li>Urgent pressure to act quickly</li>
<li>Suspicious links or unfamiliar senders</li>
<li>Requests for payment via gift cards, crypto, or wire transfer</li>
</ul>

<h2>What Should You Do?</h2>
<p>If you receive a message related to {keyword}, do not click links or send money. Verify directly through official sources and report suspicious activity.</p>
"""


def fallback_content(keyword: str) -> str:
    keyword_title = keyword.title()

    return f"""
<h2>Is {keyword_title} a Scam?</h2>
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