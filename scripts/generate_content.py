"""
generate_content.py — clean passthrough

Calls the Railway /seo-content endpoint and returns the engine's output unchanged.

What this version does:
  - Normalizes the keyword
  - Tries up to two prompt variants (the original keyword, then a question-form fallback)
  - Sends each to the Railway API with a generous timeout
  - Strips code fences and stray markdown/HTML headings the engine sometimes emits
  - Wraps any plain-text paragraphs in <p> tags so the template can split them into cards
  - Returns the result. No Python intro paragraphs. No scenario paragraphs. No
    context-detail paragraphs. No hardcoded warning bullet lists. No action
    blocks. The engine's writing is the whole output.

What this version does NOT do:
  - No enforce_structure() wrapping
  - No CONTEXT_EXAMPLES filler ("Messages like a suspicious link often arrive...")
  - No MODE_INTROS, CONTENT_MODES, ACTION_SECTION_TITLES, WARNING_SECTION_TITLES
  - No mixing of Python-built paragraphs with engine paragraphs

The result: the four paragraphs the template renders as the four story cards
all come from the engine, which is the high-quality writing you want on the page.
"""

import logging
import re
import sys
from html import unescape

import requests

# -----------------------------
# CONFIG
# -----------------------------
RAILWAY_API = "https://awake-integrity-production-faa0.up.railway.app"
TIMEOUT = 180

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

NON_RETRYABLE_ERROR_MARKERS = (
    "exceeded your current quota",
    "insufficient_quota",
    "billing",
    "quota",
    "invalid_api_key",
    "incorrect api key",
    "authentication",
    "unauthorized",
)


# -----------------------------
# HELPERS
# -----------------------------
def normalize_keyword(text: str) -> str:
    """Trim, collapse whitespace, lowercase."""
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def build_payload_variants(raw_keyword: str):
    """
    Try the raw keyword first. If the keyword doesn't already start with 'is',
    try a question-form fallback as a second attempt. Two attempts max.
    """
    variants = [raw_keyword]
    if raw_keyword and not raw_keyword.startswith("is "):
        # Build a simple question-form variant for the retry attempt
        cleaned = re.sub(r"\s+a\s+scam$", "", raw_keyword).strip()
        cleaned = re.sub(r"\s+scam$", "", cleaned).strip()
        if cleaned:
            question = f"is {cleaned} a scam"
            if question != raw_keyword and question not in variants:
                variants.append(question)
    return variants[:2]


def safe_json(response: requests.Response):
    """Parse JSON; raise ValueError with a short snippet on failure."""
    try:
        return response.json()
    except ValueError as e:
        snippet = response.text[:200].replace("\n", " ").strip()
        raise ValueError(f"Invalid JSON response: {snippet}") from e


def error_is_non_retryable(exc: Exception) -> bool:
    """Quota, billing, and auth errors should not be retried."""
    message = str(exc).lower()
    return any(marker in message for marker in NON_RETRYABLE_ERROR_MARKERS)


# -----------------------------
# CONTENT SANITIZATION
# -----------------------------
def strip_code_fences(text: str) -> str:
    """Remove triple-backtick blocks the model sometimes wraps output in."""
    return re.sub(r"```[a-z]*\s*", "", text, flags=re.IGNORECASE).replace("```", "")


def strip_markdown_headings(text: str) -> str:
    """Drop any leading markdown heading lines."""
    return re.sub(r"^\s*#{1,6}\s*.*$", "", text, flags=re.MULTILINE)


def strip_html_headings(text: str) -> str:
    """Drop any <h1>..<h6> blocks the model might emit."""
    return re.sub(
        r"<h[1-6][^>]*>.*?</h[1-6]>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )


def has_paragraph_tags(text: str) -> bool:
    return bool(re.search(r"<p\b", text, flags=re.IGNORECASE))


def wrap_plain_paragraphs(text: str) -> str:
    """
    If the engine returned plain-text paragraphs separated by blank lines,
    wrap each in <p>...</p> so the template's renderer can find them.
    If the engine already returned <p> tags, leave them alone.
    """
    if has_paragraph_tags(text):
        return text.strip()

    # Split on blank lines and wrap each block.
    blocks = [b.strip() for b in re.split(r"\n\s*\n+", text) if b.strip()]
    if not blocks:
        return text.strip()
    return "\n".join(f"<p>{unescape(b)}</p>" for b in blocks)


def normalize_engine_output(raw: str) -> str:
    """
    Run all the cleanup steps in order. The engine's content is preserved
    exactly — only formatting noise is removed.
    """
    if not raw:
        return ""
    text = strip_code_fences(raw)
    text = strip_markdown_headings(text)
    text = strip_html_headings(text)
    text = text.strip()
    if not text:
        return ""
    return wrap_plain_paragraphs(text)


# -----------------------------
# MAIN
# -----------------------------
def generate_content(keyword: str) -> str:
    """
    Returns the engine's content for the keyword, lightly sanitized and ready
    to be dropped into the template's {{AI_CONTENT}} slot.
    """
    raw_keyword = normalize_keyword(keyword)
    if not raw_keyword:
        raise ValueError("Empty keyword after normalization")

    logging.info("Generating content for: %s", raw_keyword)

    payload_variants = build_payload_variants(raw_keyword)
    last_error = None

    for prompt_keyword in payload_variants:
        try:
            res = requests.post(
                f"{RAILWAY_API}/seo-content",
                json={"keyword": prompt_keyword},
                timeout=TIMEOUT,
            )
            res.raise_for_status()
            data = safe_json(res)
            raw = str(data.get("content", "")).strip()

            if not raw:
                last_error = ValueError(
                    f"Empty content for prompt: {prompt_keyword}"
                )
                logging.warning(
                    "Engine returned empty content for %s using prompt '%s'",
                    raw_keyword,
                    prompt_keyword,
                )
                continue

            cleaned = normalize_engine_output(raw)
            if not cleaned:
                last_error = ValueError(
                    f"Content became empty after sanitization for prompt: {prompt_keyword}"
                )
                logging.warning(
                    "Engine output sanitized away for %s using prompt '%s'",
                    raw_keyword,
                    prompt_keyword,
                )
                continue

            # Log a quick quality check so we can confirm the engine output is
            # actually flowing through.
            paragraph_count = len(re.findall(r"<p\b", cleaned, flags=re.IGNORECASE))
            word_count = len(re.findall(r"\b\w+\b", re.sub(r"<[^>]+>", " ", cleaned)))
            logging.info(
                "Engine output OK for '%s': %s paragraphs, %s words",
                raw_keyword,
                paragraph_count,
                word_count,
            )

            return cleaned

        except Exception as e:
            last_error = e
            logging.warning(
                "Engine call failed for %s using prompt '%s': %s",
                raw_keyword,
                prompt_keyword,
                e,
            )
            if error_is_non_retryable(e):
                raise ValueError(
                    f"Content generation failed for '{raw_keyword}': {e}"
                ) from e

    raise ValueError(
        f"Content generation failed for '{raw_keyword}': {last_error}"
    )


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "amazon scam"
    print(generate_content(kw))
