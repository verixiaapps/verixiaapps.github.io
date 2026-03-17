import requests
import sys
import logging

# -----------------------------
# CONFIG
# -----------------------------
RAILWAY_API = "https://awake-integrity-production-faa0.up.railway.app"
TIMEOUT = 60  # seconds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -----------------------------
# FUNCTIONS
# -----------------------------
def generate_content(keyword: str) -> str:
    """
    Generate SEO-optimized content for a given keyword using Railway API.

    Args:
        keyword (str): Keyword for which to generate content

    Returns:
        str: Generated content
    """
    if not keyword.strip():
        raise ValueError("Keyword cannot be empty")

    payload = {"keyword": keyword.strip()}

    logging.info(f"Requesting SEO content for keyword: '{keyword}'")

    try:
        response = requests.post(
            f"{RAILWAY_API}/seo-content",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        raise RuntimeError("Failed to fetch SEO content from Railway API") from e

    data = response.json()
    text = data.get("content", "").strip()

    if not text:
        logging.error(f"No content returned for keyword '{keyword}'")
        raise RuntimeError("Empty content returned from Railway API")

    logging.info(f"Successfully generated content for '{keyword}'")
    return text

# -----------------------------
# SCRIPT ENTRY
# -----------------------------
if __name__ == "__main__":
    # Accept keyword from CLI if provided, else use sample
    keyword = sys.argv[1] if len(sys.argv) > 1 else "amazon scam"

    try:
        content = generate_content(keyword)
        print(content)
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        sys.exit(1)