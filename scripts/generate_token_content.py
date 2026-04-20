import os
import re
import sys
import logging
from typing import List, Dict, Tuple, Optional

import requests

# -----------------------------
# CONFIG
# -----------------------------
TOKEN_RISK_API = os.getenv(
    "TOKEN_RISK_API",
    "https://awake-integrity-production-faa0.up.railway.app",
).rstrip("/")

TOKEN_RISK_ENDPOINT = os.getenv("TOKEN_RISK_ENDPOINT", "/seo-content")
TIMEOUT = int(os.getenv("TOKEN_RISK_TIMEOUT", "180"))

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

CONTENT_MODES = [
    "risk-overview",
    "buy-decision",
    "metrics-breakdown",
    "safety-check",
    "scenario",
]

SECTION_TITLES = {
    "risk-overview": "What This Token Risk Pattern Usually Looks Like",
    "buy-decision": "How To Think About The Buy Decision",
    "metrics-breakdown": "Which Token Metrics Usually Matter Most",
    "safety-check": "How To Judge Whether The Setup Looks Safer Or Riskier",
    "scenario": "How This Token Situation Usually Plays Out",
}

WARNING_SECTION_TITLES = [
    "Common Token Risk Warning Signs",
    "Red Flags To Watch Before Buying",
    "Signs The Setup May Be Weak Or Risky",
]

ACTION_SECTION_TITLES = [
    "What To Do Before You Buy Or Swap",
    "How To Check The Token More Safely",
    "Safer Next Steps",
]

ACTION_SECTION_INTROS = [
    "The safest move is to verify the setup outside hype, chat pressure, or screenshots.",
    "Before you buy, swap, or connect a wallet, slow down and check the token independently.",
    "A careful token check can prevent a rushed entry into a weak or manipulated setup.",
]

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with",
}

BRAND_CASE = {
    "binance smart chain": "Binance Smart Chain",
    "market cap": "Market Cap",
    "pair age": "Pair Age",
    "price action": "Price Action",
    "price change": "Price Change",
    "trust wallet": "Trust Wallet",
    "pool depth": "Pool Depth",
    "token risk hub": "Token Risk Hub",
    "token risk": "Token Risk",
    "metamask": "MetaMask",
    "dexscreener": "Dexscreener",
    "pancakeswap": "PancakeSwap",
    "uniswap": "Uniswap",
    "raydium": "Raydium",
    "coinbase": "Coinbase",
    "ethereum": "Ethereum",
    "avalanche": "Avalanche",
    "arbitrum": "Arbitrum",
    "polygon": "Polygon",
    "phantom": "Phantom",
    "bitcoin": "Bitcoin",
    "solana": "Solana",
    "binance": "Binance",
    "jupiter": "Jupiter",
    "liquidity": "Liquidity",
    "volume": "Volume",
    "buyers": "Buyers",
    "sellers": "Sellers",
    "slippage": "Slippage",
    "crypto": "Crypto",
    "token": "Token",
    "market": "Market",
    "fdv": "FDV",
    "bsc": "BSC",
    "eth": "ETH",
    "ton": "TON",
    "trx": "TRX",
    "tron": "Tron",
    "base": "Base",
    "blast": "Blast",
    "sui": "Sui",
    "cto": "CTO",
}

CHAIN_HINTS = (
    "solana",
    "ethereum",
    "eth",
    "base",
    "bsc",
    "arbitrum",
    "polygon",
    "avalanche",
    "blast",
    "sui",
    "ton",
    "tron",
    "bitcoin",
)

METRIC_HINTS = (
    "liquidity",
    "volume",
    "pair age",
    "pool depth",
    "slippage",
    "fdv",
    "market cap",
    "buyers",
    "sellers",
    "price action",
    "price change",
)

BUY_INTENT_HINTS = (
    "should i buy",
    "worth buying",
    "good investment",
    "safe to buy",
    "buy now",
    "entry",
    "buy",
)

SAFETY_HINTS = (
    "safe",
    "legit",
    "risky",
    "rug pull",
    "rug",
    "honeypot",
    "scam",
    "sell lock",
    "sell locked",
)

ALLOWED_INLINE_TAGS = ("strong", "em", "b", "i", "code")
ALLOWED_BLOCK_TAGS = ("p", "ul", "ol", "li", "blockquote")

RISK_WARNING_BULLETS = {
    "metrics": [
        [
            "Liquidity looks thin relative to the attention or price move being advertised",
            "Volume spikes look unstable, sudden, or disconnected from organic trading interest",
            "Pair Age is extremely new, which leaves less history to judge behavior",
            "Buyers, sellers, or price movement look one-sided in a way that may signal weak market structure",
        ],
        [
            "The token story sounds strong, but core market metrics stay weak or shallow",
            "Slippage, pool depth, or tradability look worse than the hype suggests",
            "Market Cap or FDV is being used aggressively while execution risk is still high",
            "The chart attracts attention before there is enough stable trading history",
        ],
        [
            "Key token metrics are being presented selectively instead of as a full risk picture",
            "Short-term momentum is being confused with durability or safety",
            "A few screenshots or calls are replacing direct market checks",
            "There is not enough clean on-chain or market context to justify confidence",
        ],
    ],
    "buy-intent": [
        [
            "Pressure to buy quickly before the setup is independently checked",
            "Hype around upside is much stronger than evidence around Liquidity, volume, or Pair Age",
            "People focus on potential gains while downplaying execution and exit risk",
            "The buy thesis depends more on excitement than on stable token structure",
        ],
        [
            "Fear of missing out is being used to rush an entry",
            "The token is framed as safe or early without enough real data behind that claim",
            "The market structure still looks fragile even though the story sounds strong",
            "Entry talk is happening before there is enough proof that the setup is durable",
        ],
        [
            "A fast chart move is being treated as validation of safety",
            "The setup may be easy to enter but much harder to exit cleanly",
            "The conversation is about upside first and risk second",
            "Independent verification is being replaced by social proof or urgency",
        ],
    ],
    "safety": [
        [
            "Claims that the token is safe, legit, or not a rug are not backed by strong market structure",
            "The trust narrative is stronger than the actual Liquidity, history, or trading behavior",
            "People are using reassurance language instead of objective token checks",
            "The setup still leaves major uncertainty around execution, exit, or sustainability",
        ],
        [
            "Safety language appears before there is enough history to support it",
            "The token may avoid obvious red flags while still carrying high structural risk",
            "The market looks thin, young, or unstable despite confident messaging",
            "The analysis depends on vibes, endorsements, or calls rather than direct checks",
        ],
        [
            "A token can avoid being an obvious scam and still be a poor or risky buy",
            "Low transparency, weak depth, or unstable behavior can matter even without a textbook rug pattern",
            "The setup may look fine at first glance but still break down under pressure",
            "The confidence level around the token may be higher than the evidence justifies",
        ],
    ],
    "chain": [
        [
            "The chain context is being used as a trust shortcut instead of checking the token itself",
            "A familiar ecosystem does not automatically make a specific token safer",
            "The token is borrowing credibility from the chain, wallet, or DEX brand",
            "Network familiarity may hide token-level execution risk",
        ],
        [
            "Being on a popular chain is being confused with having strong token structure",
            "Users may feel more comfortable because the tooling is familiar, not because the setup is safer",
            "The platform brand is clear, but the token risk still looks unresolved",
            "Chain identity alone is not enough to remove exit, liquidity, or durability concerns",
        ],
        [
            "The ecosystem is recognizable, but token-specific risk remains the real issue",
            "Users may overtrust the setup because the chain or DEX is familiar",
            "A token can still be weak even if the surrounding infrastructure is strong",
            "Chain reputation should support analysis, not replace it",
        ],
    ],
    "general": [
        [
            "Strong hype but weak proof around Liquidity, history, or trade quality",
            "Pressure to buy, swap, or ape in before the setup is independently checked",
            "Safety claims that are not matched by clean token metrics",
            "A token story that sounds stronger than the actual market structure",
        ],
        [
            "A fast-moving narrative built on excitement rather than strong token fundamentals",
            "Thin or unstable trading conditions underneath aggressive promotion",
            "Too much confidence around a token that still has limited proof",
            "Social pressure replacing direct checks of the chart, pool, and market behavior",
        ],
        [
            "A believable setup on the surface that becomes weaker when you slow down",
            "Not enough stable history to judge whether the move is durable",
            "Claims of safety or quality without enough supporting evidence",
            "A token that may be easy to enter emotionally but harder to justify analytically",
        ],
    ],
}

ACTION_PARAGRAPHS_BY_CONTEXT = {
    "metrics": [
        "If this involves {keyword}, check Liquidity, Volume, Pair Age, and the basic trade setup directly before treating the token as stronger than it is.",
        "Before buying or swapping {keyword}, verify whether the metrics support the narrative instead of relying on screenshots, calls, or hype threads.",
        "If {keyword} is being discussed through token metrics, focus on whether the market structure looks durable enough to support both entry and exit.",
    ],
    "buy-intent": [
        "If this involves {keyword}, do not let urgency make the decision for you. Check whether the token still looks attractive after the excitement is stripped away.",
        "Before buying {keyword}, make sure the setup still makes sense when you review Liquidity, history, and exit conditions independently.",
        "If {keyword} is being framed as a buy opportunity, treat that as the beginning of the analysis, not the conclusion.",
    ],
    "safety": [
        "If this involves {keyword}, do not treat reassurance language as proof. Check whether the token actually looks safer under direct review.",
        "Before trusting claims around {keyword}, verify the market structure, chart behavior, and token context yourself.",
        "If {keyword} is being described as safe or legit, test whether the evidence is strong enough to support that confidence.",
    ],
    "chain": [
        "If this involves {keyword}, separate chain familiarity from token quality. A known ecosystem still requires token-level verification.",
        "Before buying or swapping {keyword}, verify the token itself instead of assuming the chain or DEX environment makes it safe.",
        "If {keyword} is being discussed inside a familiar ecosystem, make sure the token still passes basic risk checks on its own merits.",
    ],
    "general": [
        "If this involves {keyword}, slow down before buying or swapping and check whether the token still looks strong once the noise is removed.",
        "Before acting on anything related to {keyword}, verify the token structure directly instead of trusting chat momentum or social proof.",
        "If {keyword} is attracting attention, treat that as a signal to investigate harder, not a reason to skip the risk check.",
    ],
}

CONTEXT_EXAMPLES = {
    "metrics": [
        "a token with thin liquidity",
        "a sudden volume spike",
        "a very new pair",
        "a chart that moves harder than the structure supports",
    ],
    "buy-intent": [
        "a should I buy this token post",
        "a fast entry setup",
        "a token being pushed as early",
        "a chart that looks tempting but still feels uncertain",
    ],
    "safety": [
        "a token being called safe",
        "a not a rug claim",
        "a legit token thread",
        "a reassurance-heavy token discussion",
    ],
    "chain": [
        "a Solana meme token",
        "a Base token setup",
        "an ETH token launch",
        "a BSC microcap being pushed as easy money",
    ],
    "general": [
        "a token with fast hype",
        "a risky-looking chart",
        "a new launch with limited history",
        "a token getting attention before it has much proof",
    ],
}

MODE_INTROS = {
    "risk-overview": [
        "The main question is whether the token setup looks stronger than the hype around it.",
        "The safest way to judge the token is to separate the story from the actual market structure.",
        "Most token risk checks come down to whether the setup still looks solid after the excitement is removed.",
    ],
    "buy-decision": [
        "A buy decision is usually weakest when it is rushed and strongest when it survives a slower second look.",
        "The real question is not whether the token can move, but whether the setup justifies taking the risk.",
        "Many weak entries happen when people confuse momentum with quality.",
    ],
    "metrics-breakdown": [
        "The cleanest token checks usually begin with structure, not emotion.",
        "Most token setups become clearer once you look at the actual metrics instead of the narrative alone.",
        "A few core market signals often tell you more than a long thread of opinions.",
    ],
    "safety-check": [
        "A token does not need to be an obvious scam to still be a weak or dangerous buy.",
        "The safety question is usually about structure, not reassurance.",
        "What matters most is whether the setup holds up under direct review, not whether people sound confident about it.",
    ],
    "scenario": [
        "A common token risk pattern starts with excitement and only later reveals the structural weakness underneath.",
        "Many risky token setups feel convincing early because attention arrives before proof does.",
        "This usually becomes dangerous when the chart, chat, and urgency all start reinforcing each other at once.",
    ],
}

WEAK_MARKERS = (
    "lorem ipsum",
    "as an ai",
    "here are some paragraphs",
    "let me know if you want",
    "i can't help with that",
    "i cannot help with that",
    "i’m sorry",
    "i am sorry",
    "cannot assist",
    "can't assist",
    "content policy",
    "policy",
)

GENERIC_PATTERNS = (
    "this is important",
    "it is important",
    "it is worth noting",
    "in many cases",
    "in some cases",
    "generally speaking",
    "at the end of the day",
    "when it comes to this",
)

# -----------------------------
# HELPERS
# -----------------------------
def normalize_keyword(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip().lower())


def contains_term_phrase(haystack: str, needle: str) -> bool:
    haystack_norm = normalize_keyword(haystack)
    needle_norm = normalize_keyword(needle)

    if not haystack_norm or not needle_norm:
        return False

    pattern = r"(^|[^a-z0-9])" + re.escape(needle_norm) + r"([^a-z0-9]|$)"
    return re.search(pattern, haystack_norm, flags=re.IGNORECASE) is not None


def clean_base_keyword(text: str) -> str:
    kw = normalize_keyword(text)

    kw = re.sub(r"^\s*is\s+this\s+", "", kw)
    kw = re.sub(r"^\s*is\s+", "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+", "", kw)
    kw = re.sub(r"^\s*should\s+i\s+buy\s+", "", kw)
    kw = re.sub(r"^\s*check\s+", "", kw)

    kw = re.sub(r"\s+safe$", "", kw)
    kw = re.sub(r"\s+legit$", "", kw)
    kw = re.sub(r"\s+risky$", "", kw)
    kw = re.sub(r"\s+real$", "", kw)
    kw = re.sub(r"\s+scam$", "", kw)

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
    titled: List[str] = []

    for i, word in enumerate(words):
        titled.append(word if i > 0 and word in SMALL_WORDS else word.capitalize())

    return apply_brand_case(" ".join(titled))


def variant_index(keyword: str, count: int) -> int:
    return sum(ord(c) for c in normalize_keyword(keyword)) % count if count else 0


def choose_mode(keyword: str) -> str:
    idx = variant_index(keyword, len(CONTENT_MODES))
    return CONTENT_MODES[idx]


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
    seen = set()
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
    text = re.sub(r"\s*```", "", text)
    text = re.sub(r"<script\b[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b[^>]*>.*?</style>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def strip_all_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def is_usable_ai_text(text: str) -> bool:
    if not text:
        return False

    raw = str(text).strip()
    lowered = raw.lower()

    if len(raw) < 280:
        return False

    if any(marker in lowered for marker in WEAK_MARKERS):
        return False

    paragraph_like = (
        "<p>" in lowered
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
        "",
        raw,
        flags=re.IGNORECASE,
    )
    raw = re.sub(r"<div[^>]*>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"</div>", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", "", raw, flags=re.IGNORECASE | re.DOTALL)

    allowed_tag_names = set(ALLOWED_INLINE_TAGS + ALLOWED_BLOCK_TAGS)
    tag_pattern = r"<(/?)([a-z0-9]+)(?:\s[^>]*)?>"

    def rebuild_allowed_tag(match: re.Match) -> str:
        slash = match.group(1)
        tag = match.group(2).lower()
        if tag in allowed_tag_names:
            return f"<{slash}{tag}>"
        return ""

    raw = re.sub(tag_pattern, rebuild_allowed_tag, raw, flags=re.IGNORECASE)
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


def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def trim_redundant_ai_html(html: str, raw_keyword: str) -> str:
    if not html:
        return ""

    blocks = re.findall(r"<p>.*?</p>|<ul>.*?</ul>|<ol>.*?</ol>|<blockquote>.*?</blockquote>", html, flags=re.I | re.S)
    if not blocks:
        blocks = [html]

    keyword_norm = normalize_keyword(raw_keyword)
    keyword_clean = re.sub(r"[^a-z0-9]+", " ", keyword_norm).strip()

    kept: List[str] = []
    seen_text = set()

    for block in blocks:
        plain = strip_all_tags(block)
        plain = re.sub(r"\s+", " ", plain).strip()
        plain_lower = plain.lower()

        if not plain or len(plain) < 35:
            continue
        if any(marker in plain_lower for marker in WEAK_MARKERS):
            continue
        if any(marker in plain_lower for marker in GENERIC_PATTERNS):
            continue

        normalized_plain = re.sub(r"[^a-z0-9]+", " ", plain_lower).strip()
        if normalized_plain in seen_text:
            continue

        if keyword_clean:
            keyword_mentions = normalized_plain.count(keyword_clean)
            if keyword_mentions > 2:
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
        f"{display_kw} token risk" if display_kw else "",
        f"is {display_kw} safe" if display_kw and not raw_keyword.startswith("is ") else "",
        f"should i buy {display_kw}" if display_kw and not contains_term_phrase(raw_keyword, "buy") else "",
        f"{display_kw} liquidity risk" if display_kw and not contains_term_phrase(raw_keyword, "liquidity") else "",
    ])
    return variants[:6]


# -----------------------------
# INTENT / CONTEXT
# -----------------------------
def detect_context(keyword: str) -> str:
    kw = normalize_keyword(keyword)
    scores = {
        "buy-intent": 0,
        "safety": 0,
        "metrics": 0,
        "chain": 0,
    }

    for term in BUY_INTENT_HINTS:
        if contains_term_phrase(kw, term):
            scores["buy-intent"] += 3 if " " in term else 1

    for term in SAFETY_HINTS:
        if contains_term_phrase(kw, term):
            scores["safety"] += 3 if " " in term else 1

    for term in METRIC_HINTS:
        if contains_term_phrase(kw, term):
            scores["metrics"] += 3 if " " in term else 2

    for term in CHAIN_HINTS:
        if contains_term_phrase(kw, term):
            scores["chain"] += 2

    if scores["metrics"] > 0 and scores["chain"] > 0:
        scores["metrics"] += 1

    if scores["buy-intent"] > 0 and scores["safety"] > 0:
        scores["buy-intent"] += 1

    priority = ("buy-intent", "safety", "metrics", "chain")
    best_context = "general"
    best_score = 0

    for context in priority:
        if scores[context] > best_score:
            best_context = context
            best_score = scores[context]

    return best_context if best_score > 0 else "general"


def context_example(context: str, keyword: str) -> str:
    examples = CONTEXT_EXAMPLES.get(context, CONTEXT_EXAMPLES["general"])
    idx = variant_index(keyword, len(examples))
    return examples[idx]


def mode_intro_sentence(mode: str, keyword: str) -> str:
    options = MODE_INTROS.get(mode, MODE_INTROS["risk-overview"])
    idx = variant_index(keyword + mode, len(options))
    return options[idx]


# -----------------------------
# CONTENT BUILDERS
# -----------------------------
def intro_paragraph(raw_keyword: str, display_kw: str, mode: str) -> str:
    keyword_title = title_case(display_kw)
    context = detect_context(raw_keyword)
    example = context_example(context, raw_keyword)
    mode_sentence = mode_intro_sentence(mode, raw_keyword)

    if context == "buy-intent":
        return (
            f"<p>{keyword_title} is usually a buy-decision question, not just a hype question. "
            f"{mode_sentence} A setup like {example} can look attractive early, but the safer move is to ask whether the token still looks strong after you check Liquidity, history, exit conditions, and overall structure directly.</p>"
        )

    if context == "metrics":
        return (
            f"<p>{keyword_title} is usually a token-structure question. "
            f"{mode_sentence} Something like {example} can matter much more than social excitement because weak metrics often show up before the broader market realizes the setup is fragile.</p>"
        )

    if context == "safety":
        return (
            f"<p>{keyword_title} is usually a safety-and-structure question. "
            f"{mode_sentence} A token can avoid obvious scam language and still carry meaningful risk if the market setup, Liquidity, or history does not support the confidence around it.</p>"
        )

    if context == "chain":
        return (
            f"<p>{keyword_title} often gets judged too quickly because the surrounding chain or DEX feels familiar. "
            f"{mode_sentence} Something like {example} may borrow trust from the ecosystem, but the real question is whether the token itself looks solid under direct review.</p>"
        )

    return (
        f"<p>{keyword_title} is usually best judged by structure, not excitement. "
        f"{mode_sentence} A setup like {example} may look interesting at first glance, but the safest move is to separate the token narrative from the actual risk signals before buying or swapping.</p>"
    )


def scenario_paragraph(raw_keyword: str, display_kw: str, mode: str) -> str:
    keyword_title = title_case(display_kw)
    example = context_example(detect_context(raw_keyword), raw_keyword)

    if mode == "buy-decision":
        return (
            f"<p>With {keyword_title}, the risky pattern is often the same: a chart or narrative creates enough excitement that people start asking whether they should buy before they have really checked the token. A setup like {example} can feel compelling, but good entries usually survive slower analysis while bad ones depend on urgency.</p>"
        )

    if mode == "metrics-breakdown":
        return (
            f"<p>With {keyword_title}, the cleanest read usually comes from looking at the market structure directly. A setup like {example} may be paired with hype, calls, or screenshots, but the more important question is whether the core metrics look deep, stable, and believable enough to support the move.</p>"
        )

    if mode == "safety-check":
        return (
            f"<p>With {keyword_title}, people often try to reduce the decision to a simple safe or risky label. A setup like {example} is usually more nuanced than that. The better question is whether the token looks strong enough to justify confidence, especially if conditions change after you enter.</p>"
        )

    if mode == "scenario":
        return (
            f"<p>A common {keyword_title} pattern starts when a token gets attention faster than it earns trust. Something like {example} draws people in, chat momentum builds, and then the decision becomes rushed. That is usually when weak structure matters most, because the market can look strong right up until it no longer does.</p>"
        )

    return (
        f"<p>In many {keyword_title} situations, the token story is easy to understand long before the risk is easy to understand. Something like {example} may sound manageable, but the quality of the setup usually depends on whether the underlying market structure still looks healthy once you stop relying on the narrative alone.</p>"
    )


def context_detail_paragraph(raw_keyword: str, display_kw: str, mode: str) -> str:
    keyword_title = title_case(display_kw)
    context = detect_context(raw_keyword)
    example = context_example(context, raw_keyword)

    if context == "buy-intent":
        return (
            f"<p>That matters because a token related to {keyword_title} may still move even if the setup is weak. The real issue is whether the trade is being justified by evidence or by urgency. When something like {example} is involved, it is safer to check whether the setup still looks attractive after the fear of missing out is removed.</p>"
        )

    if context == "metrics":
        return (
            f"<p>This is why token metrics matter so much for {keyword_title}. A setup like {example} may look fine in a screenshot or chat message, but direct checks of Liquidity, volume behavior, age, and trade quality often tell you whether the structure is actually stable enough to trust.</p>"
        )

    if context == "safety":
        return (
            f"<p>The key point for {keyword_title} is that safety language can easily outrun the evidence. A token being called safe, legit, or not a rug does not mean the setup is strong. When something like {example} is involved, the better habit is to ask whether the structure supports the confidence, not whether people sound confident.</p>"
        )

    if context == "chain":
        return (
            f"<p>This matters because chain familiarity can distort judgment around {keyword_title}. A setup like {example} may feel more trustworthy simply because the tooling is recognizable, but token-level risk still decides whether the trade looks durable, fragile, or difficult to exit cleanly.</p>"
        )

    if mode == "metrics-breakdown":
        return (
            f"<p>For {keyword_title}, that is why structure usually matters more than storytelling. The token may still attract attention, but the safer read comes from asking whether the metrics actually support the confidence level around the setup.</p>"
        )

    return (
        f"<p>With {keyword_title}, the safer approach is usually the same: slow down, verify the structure, and make sure the setup still makes sense without hype or pressure. That becomes even more important when something like {example} is being used to make the token sound more convincing than it may really be.</p>"
    )


def get_warning_bullets(context: str, idx: int) -> List[str]:
    if context in RISK_WARNING_BULLETS:
        return RISK_WARNING_BULLETS[context][idx]
    return RISK_WARNING_BULLETS["general"][idx]


def get_action_paragraph(context: str, idx: int, keyword_title: str) -> str:
    paragraphs = ACTION_PARAGRAPHS_BY_CONTEXT.get(context, ACTION_PARAGRAPHS_BY_CONTEXT["general"])
    return paragraphs[idx].format(keyword=keyword_title)


def build_metric_support_block(raw_keyword: str, display_kw: str) -> str:
    keyword_title = title_case(display_kw)
    context = detect_context(raw_keyword)

    if context == "metrics":
        return (
            f"<h2>How To Read The Metrics More Clearly</h2>"
            f"<p>For {keyword_title}, focus on whether Liquidity, Volume, Pair Age, FDV or Market Cap framing, and general trade quality all point in the same direction. The setup is usually stronger when the structure looks coherent instead of selectively impressive.</p>"
        )

    if context == "buy-intent":
        return (
            f"<h2>Why Buy Pressure Can Distort Token Risk</h2>"
            f"<p>For {keyword_title}, the danger is often not just the token itself but the pace of the decision. When buy pressure increases, people may ignore thin Liquidity, fragile charts, or weak depth because they are more focused on upside than on whether they can exit safely later.</p>"
        )

    if context == "safety":
        return (
            f"<h2>Why Safe And Risky Are Usually Not Binary</h2>"
            f"<p>For {keyword_title}, it helps to avoid overly simple labels. A token can avoid obvious scam patterns and still be too thin, too new, or too unstable to deserve high confidence. The better question is whether the setup looks strong enough for the claim being made.</p>"
        )

    if context == "chain":
        return (
            f"<h2>Why Chain Familiarity Is Not Enough</h2>"
            f"<p>For {keyword_title}, familiar infrastructure can make the token feel safer than it is. The real test is whether the token itself shows strong enough structure, history, and trading conditions to justify confidence independent of the chain brand.</p>"
        )

    return (
        f"<h2>Why Structure Matters More Than Narrative</h2>"
        f"<p>For {keyword_title}, a strong narrative can attract attention quickly, but structure usually decides whether the setup deserves trust. The safer move is to check whether the token still looks solid when you focus on the underlying market instead of the story around it.</p>"
    )


# -----------------------------
# STRUCTURE ENFORCER
# -----------------------------
def enforce_structure(raw_keyword: str, display_kw: str, content: str) -> str:
    keyword_title = title_case(display_kw)
    context = detect_context(raw_keyword)
    mode = choose_mode(raw_keyword)

    idx = variant_index(display_kw + mode, len(WARNING_SECTION_TITLES))
    middle_heading = SECTION_TITLES.get(mode, SECTION_TITLES["risk-overview"])
    warning_title = WARNING_SECTION_TITLES[idx]
    action_title = ACTION_SECTION_TITLES[idx]
    action_intro = ACTION_SECTION_INTROS[idx]
    bullets = get_warning_bullets(context, idx)
    action = get_action_paragraph(context, idx, keyword_title)

    bullet_html = "\n".join(f"<li>{b}</li>" for b in bullets)
    metric_block = build_metric_support_block(raw_keyword, display_kw)

    return f"""
<div class="content-block" data-context="{context}" data-mode="{mode}">
{intro_paragraph(raw_keyword, display_kw, mode)}
<h2>{middle_heading}</h2>
{scenario_paragraph(raw_keyword, display_kw, mode)}
{content}
{context_detail_paragraph(raw_keyword, display_kw, mode)}
{metric_block}
</div>
<h2>{warning_title}</h2>
<ul>
{bullet_html}
</ul>
<h2>{action_title}</h2>
<p>{action_intro}</p>
<p>{action}</p>
""".strip()


# -----------------------------
# API CALL
# -----------------------------
def fetch_ai(prompt_keyword: str) -> str:
    response = requests.post(
        f"{TOKEN_RISK_API}{TOKEN_RISK_ENDPOINT}",
        json={"keyword": prompt_keyword, "type": "token-risk"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = safe_json(response)
    return str(data.get("content", "")).strip()


# -----------------------------
# MAIN GENERATOR
# -----------------------------
def generate_token_content(keyword: str) -> str:
    raw_keyword = normalize_keyword(keyword)
    display_kw = display_keyword(raw_keyword)

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
                    raw_keyword,
                    prompt_keyword,
                )
                continue

            if not is_usable_ai_text(raw):
                last_error = ValueError(f"Thin or malformed output for prompt: {prompt_keyword}")
                logging.warning(
                    "Token AI generation returned thin content for %s using prompt '%s'",
                    raw_keyword,
                    prompt_keyword,
                )
                continue

            final_content = normalize_ai_html(raw)
            final_content = trim_redundant_ai_html(final_content, raw_keyword)

            if not final_content:
                last_error = ValueError(f"Sanitized content became empty for prompt: {prompt_keyword}")
                logging.warning(
                    "Token AI content became empty after sanitation for %s using prompt '%s'",
                    raw_keyword,
                    prompt_keyword,
                )
                continue

            return enforce_structure(raw_keyword, display_kw, final_content)

        except Exception as e:
            last_error = e
            logging.warning(
                "Token AI generation failed for %s using prompt '%s': %s",
                raw_keyword,
                prompt_keyword,
                e,
            )

            if error_is_non_retryable(e):
                raise ValueError(
                    f"Token AI generation failed for '{raw_keyword}': {e}"
                ) from e

    raise ValueError(f"Token AI generation failed for '{raw_keyword}': {last_error}")


if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else "should i buy this solana token"
    print(generate_token_content(keyword))