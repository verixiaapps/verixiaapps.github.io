import os
import re
import sys
import logging
from typing import List, Dict, Tuple, Optional

import requests

# -------------------------
# CONFIG
# -------------------------

TOKEN_RISK_API = os.getenv(
    "TOKEN_RISK_API",
    "https://awake-integrity-production-faa0.up.railway.app",
).rstrip("/")

TOKEN_RISK_ENDPOINT = os.getenv("TOKEN_RISK_ENDPOINT", "/seo-content")
TIMEOUT             = int(os.getenv("TOKEN_RISK_TIMEOUT", "180"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

NON_RETRYABLE_ERROR_MARKERS = (
    "exceeded your current quota",
    "insufficient_quota",
    "billing",
    "quota",
    "429",
    "rate limit",
    "rate_limit",
    "invalid_api_key",
    "incorrect api key",
    "authentication",
    "unauthorized",
    "forbidden",
)

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with",
}

BRAND_CASE = {
    "binance smart chain": "Binance Smart Chain",
    "market cap":          "Market Cap",
    "pair age":            "Pair Age",
    "price action":        "Price Action",
    "price change":        "Price Change",
    "trust wallet":        "Trust Wallet",
    "pool depth":          "Pool Depth",
    "token risk hub":      "Token Risk Hub",
    "token risk":          "Token Risk",
    "metamask":            "MetaMask",
    "dexscreener":         "Dexscreener",
    "pancakeswap":         "PancakeSwap",
    "uniswap":             "Uniswap",
    "raydium":             "Raydium",
    "coinbase":            "Coinbase",
    "ethereum":            "Ethereum",
    "avalanche":           "Avalanche",
    "arbitrum":            "Arbitrum",
    "polygon":             "Polygon",
    "phantom":             "Phantom",
    "bitcoin":             "Bitcoin",
    "solana":              "Solana",
    "binance":             "Binance",
    "jupiter":             "Jupiter",
    "liquidity":           "Liquidity",
    "volume":              "Volume",
    "buyers":              "Buyers",
    "sellers":             "Sellers",
    "slippage":            "Slippage",
    "crypto":              "Crypto",
    "token":               "Token",
    "market":              "Market",
    "fdv":                 "FDV",
    "bsc":                 "BSC",
    "eth":                 "ETH",
    "ton":                 "TON",
    "trx":                 "TRX",
    "tron":                "Tron",
    "base":                "Base",
    "blast":               "Blast",
    "sui":                 "Sui",
    "cto":                 "CTO",
}

CHAIN_HINTS = (
    "solana", "ethereum", "eth", "base", "bsc", "arbitrum", "polygon",
    "avalanche", "blast", "sui", "ton", "tron", "bitcoin",
)

METRIC_HINTS = (
    "liquidity", "volume", "pair age", "pool depth", "slippage", "fdv",
    "market cap", "buyers", "sellers", "price action", "price change",
)

BUY_INTENT_HINTS = (
    "should i buy", "worth buying", "good investment", "safe to buy",
    "buy now", "entry", "buy",
)

SAFETY_HINTS = (
    "safe", "legit", "risky", "rug pull", "rug", "honeypot", "scam",
    "sell lock", "sell locked",
)

WEAK_MARKERS = (
    "lorem ipsum",
    "as an ai",
    "here are some paragraphs",
    "let me know if you want",
    "i can't help with that",
    "i cannot help with that",
    "i'm sorry",
    "i am sorry",
    "cannot assist",
    "can't assist",
    "content policy",
    "policy",
)

# -------------------------
# HELPERS
# -------------------------

def normalize_keyword(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip().lower())


def contains_term_phrase(haystack: str, needle: str) -> bool:
    haystack_norm = normalize_keyword(haystack)
    needle_norm   = normalize_keyword(needle)
    if not haystack_norm or not needle_norm:
        return False
    pattern = r"(^|[^a-z0-9])" + re.escape(needle_norm) + r"([^a-z0-9]|$)"
    return re.search(pattern, haystack_norm, flags=re.IGNORECASE) is not None


def clean_base_keyword(text: str) -> str:
    kw = normalize_keyword(text)
    kw = re.sub(r"^\s*is\s+this\s+",      "", kw)
    kw = re.sub(r"^\s*is\s+",             "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+","", kw)
    kw = re.sub(r"^\s*should\s+i\s+buy\s+","", kw)
    kw = re.sub(r"^\s*check\s+",          "", kw)
    kw = re.sub(r"\s+safe$",              "", kw)
    kw = re.sub(r"\s+legit$",             "", kw)
    kw = re.sub(r"\s+risky$",             "", kw)
    kw = re.sub(r"\s+real$",              "", kw)
    kw = re.sub(r"\s+scam$",              "", kw)
    return re.sub(r"\s+", " ", kw).strip()


def display_keyword(text: str) -> str:
    return clean_base_keyword(text)


def apply_brand_case(text: str) -> str:
    result = f" {text} "
    for raw, proper in sorted(BRAND_CASE.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(raw) + r"(?![a-z0-9])"
        result  = re.sub(pattern, proper, result, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", result).strip()


def title_case(text: str) -> str:
    text = normalize_keyword(text)
    if not text:
        return ""
    words  = text.split()
    titled: List[str] = []
    for i, word in enumerate(words):
        titled.append(word if i > 0 and word in SMALL_WORDS else word.capitalize())
    return apply_brand_case(" ".join(titled))


def variant_index(keyword: str, count: int) -> int:
    return sum(ord(c) for c in normalize_keyword(keyword)) % count if count else 0


def safe_json(response: requests.Response) -> Dict:
    try:
        return response.json()
    except ValueError as e:
        snippet = response.text[:200].replace("\n", " ").strip()
        raise ValueError(f"Invalid JSON response: {snippet}") from e


def error_is_non_retryable(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(marker in message for marker in NON_RETRYABLE_ERROR_MARKERS)


def dedupe_preserve_order(items: List[str]) -> List[str]:
    seen   = set()
    result: List[str] = []
    for item in items:
        key = normalize_keyword(item)
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def clean_text(text: str) -> str:
    text = str(text or "")
    text = re.sub(r"```(?:html)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```",          "", text)
    text = re.sub(r"<script\b[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b[^>]*>.*?</style>",   "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def strip_all_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def is_usable_ai_text(text: str) -> bool:
    if not text:
        return False
    raw     = str(text).strip()
    lowered = raw.lower()
    if len(raw) < 280:
        return False
    if any(marker in lowered for marker in WEAK_MARKERS):
        return False
    paragraph_like = (
        "<p>"  in lowered
        or "</p>" in lowered
        or "<ul>" in lowered
        or raw.count("\n") >= 3
    )
    return paragraph_like


def normalize_ai_html(text: str) -> str:
    raw = clean_text(text)
    if not raw:
        return ""
    raw = re.sub(
        r"</?(html|body|main|section|article|header|footer|aside)[^>]*>",
        "", raw, flags=re.IGNORECASE,
    )
    raw = re.sub(r"<div[^>]*>",  "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"</div>",      "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", "", raw, flags=re.IGNORECASE | re.DOTALL)

    allowed_tag_names = {"strong", "em", "b", "i", "code", "p", "ul", "ol", "li", "blockquote"}

    def rebuild_allowed_tag(match: re.Match) -> str:
        slash = match.group(1)
        tag   = match.group(2).lower()
        return f"<{slash}{tag}>" if tag in allowed_tag_names else ""

    raw = re.sub(r"<(/?)([a-z0-9]+)(?:\s[^>]*)?>", rebuild_allowed_tag, raw, flags=re.IGNORECASE)
    raw = re.sub(r"\n{3,}", "\n\n", raw).strip()

    if re.search(r"</?(p|ul|ol|li|blockquote)\b", raw, flags=re.IGNORECASE):
        return raw

    plain = strip_all_tags(raw)
    plain = re.sub(r"\s+", " ", plain).strip()
    if not plain:
        return ""

    parts = [part.strip() for part in re.split(r"\n\s*\n+", plain) if part.strip()]
    if not parts:
        parts = [plain]
    return "\n".join(f"<p>{part}</p>" for part in parts)


def trim_redundant_ai_html(html: str, raw_keyword: str) -> str:
    if not html:
        return ""

    blocks = re.findall(
        r"<p>.*?</p>|<ul>.*?</ul>|<ol>.*?</ol>|<blockquote>.*?</blockquote>",
        html, flags=re.I | re.S,
    )
    if not blocks:
        blocks = [html]

    keyword_norm  = normalize_keyword(raw_keyword)
    keyword_clean = re.sub(r"[^a-z0-9]+", " ", keyword_norm).strip()

    kept: List[str] = []
    seen_text       = set()

    for block in blocks:
        plain       = strip_all_tags(block)
        plain       = re.sub(r"\s+", " ", plain).strip()
        plain_lower = plain.lower()

        if not plain or len(plain) < 35:
            continue
        if any(marker in plain_lower for marker in WEAK_MARKERS):
            continue

        normalized_plain = re.sub(r"[^a-z0-9]+", " ", plain_lower).strip()
        if normalized_plain in seen_text:
            continue

        if keyword_clean:
            if normalized_plain.count(keyword_clean) > 2:
                continue

        seen_text.add(normalized_plain)
        kept.append(block.strip())

    if not kept:
        return html
    if len(kept) > 4:
        kept = kept[:4]
    return "\n".join(kept)


def build_payload_variants(raw_keyword: str, display_kw: str) -> List[str]:
    readable = title_case(display_kw)
    variants = dedupe_preserve_order([
        raw_keyword,
        display_kw,
        readable,
        f"{display_kw} token risk"     if display_kw else "",
        f"is {display_kw} safe"        if display_kw and not raw_keyword.startswith("is ") else "",
        f"should i buy {display_kw}"   if display_kw and not contains_term_phrase(raw_keyword, "buy") else "",
        f"{display_kw} liquidity risk" if display_kw and not contains_term_phrase(raw_keyword, "liquidity") else "",
    ])
    return variants[:6]


# -------------------------
# API CALL
# -------------------------

def fetch_ai(prompt_keyword: str) -> str:
    response = requests.post(
        f"{TOKEN_RISK_API}{TOKEN_RISK_ENDPOINT}",
        json={"keyword": prompt_keyword, "type": "token-risk"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = safe_json(response)
    return str(data.get("content", "")).strip()


# -------------------------
# MAIN GENERATOR
# -------------------------

def generate_token_content(keyword: str) -> str:
    raw_keyword = normalize_keyword(keyword)
    display_kw  = display_keyword(raw_keyword)

    if not display_kw:
        raise ValueError("Empty keyword after normalization")

    logging.info("Generating token content for: %s", raw_keyword)

    payload_variants = build_payload_variants(raw_keyword, display_kw)
    last_error: Optional[Exception] = None

    for prompt_keyword in payload_variants:
        try:
            raw = fetch_ai(prompt_keyword)

            if not raw:
                last_error = ValueError(f"Empty content for prompt: {prompt_keyword}")
                logging.warning(
                    "Token AI generation returned empty content for %s using prompt '%s'",
                    raw_keyword, prompt_keyword,
                )
                continue

            if not is_usable_ai_text(raw):
                last_error = ValueError(f"Thin or malformed output for prompt: {prompt_keyword}")
                logging.warning(
                    "Token AI generation returned thin content for %s using prompt '%s'",
                    raw_keyword, prompt_keyword,
                )
                continue

            final_content = normalize_ai_html(raw)
            final_content = trim_redundant_ai_html(final_content, raw_keyword)

            if not final_content:
                last_error = ValueError(f"Sanitized content became empty for prompt: {prompt_keyword}")
                logging.warning(
                    "Token AI content became empty after sanitation for %s using prompt '%s'",
                    raw_keyword, prompt_keyword,
                )
                continue

            # Return the SEO engine output directly.
            # enforce_structure() was removed -- it wrapped clean content in <h2>/<ul>/<div>
            # which broke the template's paragraph parser and story card system.
            # The SEO engine already validates: 4 paragraphs, word counts, no lists, no HTML.
            return final_content

        except Exception as e:
            last_error = e
            logging.warning(
                "Token AI generation failed for %s using prompt '%s': %s",
                raw_keyword, prompt_keyword, e,
            )
            if error_is_non_retryable(e):
                raise ValueError(
                    f"Token AI generation failed for '{raw_keyword}': {e}"
                ) from e

    raise ValueError(f"Token AI generation failed for '{raw_keyword}': {last_error}")


if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else "should i buy this solana token"
    print(generate_token_content(keyword))
 