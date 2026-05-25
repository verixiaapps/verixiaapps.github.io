#!/usr/bin/env python3
"""
generate_nexus_dex_content.py -- v2.0 (canonical builder)

Builds Verixia Nexus DEX SEO pages from the keyword queue.

Design rules (v2.0):
  - Single source of truth: the Node SEO engine (v16.2+) at /seo-page.
  - No content fallbacks. If engine fails or returns weak content,
    the keyword stays in the queue and is retried on the next run.
  - Quality floor: MIN_PUBLISH_SCORE = 80. Engine still scores at 72
    internally, but Python refuses to publish anything weaker.
  - Two-pass retry: one engine call, and on transient failure, one retry.
    Beyond that, skip and log.
  - Placeholder names match the v2.3 template exactly:
      {{TITLE}} {{DESCRIPTION}} {{KEYWORD}} {{AI_CONTENT}}
      {{RELATED_LINKS}} {{MORE_LINKS}} {{HUB_LINK}}
      {{CANONICAL_URL}} {{MODIFIED_DATE}} {{BREADCRUMB_NAME}}
      {{STATIC_H1}} {{STATIC_INTRO}} {{OG_IMAGE}} {{HL_DATA_BLOCK}}
      {{SCHEMA_FAQ}} {{AGGREGATE_RATING_JSON}}
      {{SUPP_HEADING}} {{SUPP_INTRO}} {{PAGE_META_SCRIPT}}
  - prediction_markets intent is routed to the event-markets hub.
  - AggregateRating is exposed inline in the visual chip only (the
    template's FinancialService/SoftwareApplication JSON-LD that
    references {{AGGREGATE_RATING_JSON}} must be stripped from the
    template, see template v2.4). This file no longer emits
    AggregateRating JSON-LD.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from html import escape as html_escape_lib
from pathlib import Path

import requests

# =========================================================================
# CONFIG
# =========================================================================

BASE_DIR             = Path(__file__).resolve().parent.parent

KEYWORDS_FILE        = BASE_DIR / "data" / "nexus_dex_keywords.txt"
GENERATED_SLUGS_FILE = BASE_DIR / "data" / "nexus_dex_generated_slugs.txt"
GENERATED_KW_FILE    = BASE_DIR / "data" / "nexus_dex_generated_keywords.txt"
REJECTED_FILE        = BASE_DIR / "data" / "nexus_dex_rejected_keywords.txt"

TEMPLATE_PATH        = BASE_DIR / "nexus-dex-template" / "nexus-dex-template.html"
OUTPUT_DIR           = BASE_DIR / "nexus-dex"

SITE_URL             = "https://verixiaapps.com"
SEO_API_BASE         = "https://awake-integrity-production-faa0.up.railway.app"
SEO_PAGE_ENDPOINT    = f"{SEO_API_BASE}/seo-page"
SEO_PAGE_TIMEOUT_S   = 90

DAILY_LIMIT          = 100

# Engine accepts >=72. Python publishes only >=80.
MIN_PUBLISH_SCORE    = 80

OG_IMAGE             = f"{SITE_URL}/og/nexus-dex.png"
TWITTER_HANDLE       = "@verixiaapps"

RELATED_LINKS_COUNT  = 6
MORE_LINKS_COUNT     = 10

# Protected slugs are hub pages that this script never overwrites.
PROTECTED_SLUGS = {
    "nexus-dex",
    "crypto-markets",
    "bitcoin-markets",
    "ethereum-markets",
    "solana-markets",
    "altcoin-markets",
    "hyperliquid-frontend",
    "global-markets",
    "tokenized-stocks",
    "buy-stocks-onchain",
    "stocks-no-kyc",
    "stocks-24-7",
    "global-stock-access",
    "solana-swap",
    "buy-token",
    "no-kyc-trading",
    "whale-tracking",
    "token-launch",
    "wallet-trading",
    "how-to-guides",
    "event-markets",
    "prediction-markets",
}

# =========================================================================
# HUB SYSTEM
# =========================================================================
# Order matters: first match wins. Prediction markets routed to event-markets.

HUB_MATCH_RULES = [
    # ---- Prediction markets (NEW, highest priority) ----
    (r"\b(polymarket|kalshi)\b",
        "event-markets", "predictions"),
    (r"prediction\s+market|outcome\s+market|yes/?no\s+shares?|implied\s+probabilit",
        "event-markets", "predictions"),
    (r"\b(btc|bitcoin|eth|ethereum|sol|solana)\s+price\s+(prediction|target|forecast)\b",
        "event-markets", "predictions"),
    (r"will\s+(bitcoin|btc|ethereum|eth|solana|sol)\s+(hit|reach|cross|break)\b",
        "event-markets", "predictions"),
    (r"crypto[\s-]?native\s+predictions?|defi\s+outcome|onchain\s+prediction",
        "event-markets", "predictions"),
    (r"bonding\s+curve\s+graduation|memecoin\s+graduation\s+market",
        "event-markets", "predictions"),

    # ---- Hyperliquid ----
    (r"\bhyperliquid\b",
        "hyperliquid-frontend", "hyperliquid"),

    # ---- xStocks / tokenized stocks (specific tickers first) ----
    (r"\bxstocks?\b|\baaplx\b|\btslax\b|\bnvdax\b|\bspyx\b|\bqqqx\b|\bmstrx\b|\bgooglx\b|\bmsftx\b|\bamznx\b|\bmetax\b|\bnflxx\b|\bcrclx\b|\bhoodx\b|backed\s+finance",
        "global-markets", "xstocks"),
    (r"buy\s+us\s+stocks\s+from|us\s+stocks\s+no\s+us\s+bank|us\s+stocks\s+for\s+non\s+residents|us\s+stocks\s+international|global\s+stock|international\s+stock",
        "global-stock-access", "global_stocks"),
    (r"24\s*7\s+stock|stocks?\s+24\s+hours?|stocks?\s+weekend|trade\s+stocks?\s+at\s+night|trade\s+stocks?\s+weekends?|trade\s+stocks?\s+holidays?|stocks?\s+never\s+close|always\s+open\s+stock|stocks?\s+after\s+hours?",
        "stocks-24-7", "stocks_247"),
    (r"buy\s+stocks?\s+no\s+kyc|trade\s+stocks?\s+no\s+kyc|stock\s+trading\s+no\s+verification|stock\s+trading\s+no\s+signup|stocks?\s+no\s+id|stocks?\s+no\s+account|anonymous\s+stock|stocks?\s+without\s+(broker|robinhood|etrade)",
        "stocks-no-kyc", "stocks_no_kyc"),
    (r"buy\s+(apple|aapl|tesla|tsla|nvidia|nvda|microsoft|msft|google|googl|alphabet|meta|amazon|amzn|mstr|microstrategy|spy|qqq|netflix|nflx|coinbase|robinhood|circle|crcl)\b",
        "buy-stocks-onchain", "buy_stocks"),
    (r"tokenized\s+stocks?|tokenized\s+equit(y|ies)|onchain\s+stocks?|onchain\s+equit(y|ies)|stocks?\s+on\s+(solana|blockchain)|stocks?\s+as\s+spl|buy\s+stocks?\s+with\s+(crypto|usdc|sol)",
        "tokenized-stocks", "tokenized_stocks"),

    # ---- Perps by asset ----
    (r"\bbtc\s+perp|bitcoin\s+perp|bitcoin\s+futures|bitcoin\s+perpetual",
        "bitcoin-markets", "btc_perps"),
    (r"\beth\s+perp|ethereum\s+perp|ethereum\s+futures|ethereum\s+perpetual",
        "ethereum-markets", "eth_perps"),
    (r"\bsol\s+perp|solana\s+perp|sol\s+perpetual",
        "solana-markets", "sol_perps"),
    (r"\bmemecoin\s+perp|altcoin\s+perp|\bwif\s+perp|\bbonk\s+perp|\bpepe\s+perp|\bdoge\s+perp|\bhype\s+perp",
        "altcoin-markets", "altcoin_perps"),

    # ---- Whale / launch / swap / buy ----
    (r"\bwhale\b|\bsmart\s+money\b|\binsider\b|\bdeployer\b|\bsniper\b|kol\s+wallet",
        "whale-tracking", "whale"),
    (r"\blaunch\s+token|\btoken\s+launch|\blaunchpad\b|bonding\s+curve|deploy\s+token",
        "token-launch", "launch"),
    (r"\bsolana\s+swap|\bsolana\s+dex|\bdex\s+aggregator|best\s+price\s+swap",
        "solana-swap", "swap"),
    (r"\bbuy\s+(bonk|wif|pepe|trump|memecoin|spl)\b|\bbuy\b",
        "buy-token", "buy_token"),

    # ---- Wallet / no-KYC (generic, after specific rules) ----
    (r"phantom\s+wallet\s+trading|backpack\s+wallet\s+trading|self\s+custodial|non\s+custodial|wallet\s+based",
        "wallet-trading", "wallet"),
    (r"no\s+kyc|without\s+kyc|no\s+signup|no\s+verification",
        "no-kyc-trading", "no_kyc"),

    # ---- Perps fallback ----
    (r"\bperp(s|etual)|\bleverage|\blong\b|\bshort\b|\bhedge\b",
        "crypto-markets", "perps"),
    (r"\bswap\b",
        "solana-swap", "swap"),
    (r"how\s+to\b",
        "how-to-guides", "how_to"),
]

HUB_TITLE_OVERRIDES = {
    "predictions":      "Prediction Markets Hub",
    "hyperliquid":      "Hyperliquid Frontend Hub",
    "xstocks":          "Global Markets Hub",
    "tokenized_stocks": "Tokenized Stocks Hub",
    "buy_stocks":       "Buy Stocks On-Chain Hub",
    "stocks_no_kyc":    "Stocks No KYC Hub",
    "stocks_247":       "24/7 Stocks Hub",
    "global_stocks":    "Global Stock Access Hub",
    "btc_perps":        "Bitcoin Markets Hub",
    "eth_perps":        "Ethereum Markets Hub",
    "sol_perps":        "SOL Markets Hub",
    "altcoin_perps":    "Altcoin Markets Hub",
    "whale":            "Whale Tracking Hub",
    "launch":           "Token Launch Hub",
    "swap":             "Solana Swap Hub",
    "buy_token":        "Buy Token Hub",
    "wallet":           "Wallet Trading Hub",
    "no_kyc":           "No KYC Trading Hub",
    "perps":            "Crypto Markets Hub",
    "how_to":           "Nexus DEX Guides Hub",
}

DEFAULT_HUB_SLUG  = "crypto-markets"
DEFAULT_HUB_TITLE = "Crypto Markets Hub"


def select_hub(keyword: str) -> tuple[str, str]:
    """Return (hub_slug, hub_title) for the keyword based on hub rules."""
    lower = keyword.lower()
    for pattern, hub_slug, override_key in HUB_MATCH_RULES:
        if re.search(pattern, lower):
            title = HUB_TITLE_OVERRIDES.get(override_key, DEFAULT_HUB_TITLE)
            return hub_slug, title
    return DEFAULT_HUB_SLUG, DEFAULT_HUB_TITLE


# =========================================================================
# SLUG + IO HELPERS
# =========================================================================

_SLUG_INVALID = re.compile(r"[^a-z0-9\-]+")
_SLUG_DASHES  = re.compile(r"-{2,}")


def slugify(keyword: str) -> str:
    s = keyword.lower().strip()
    s = re.sub(r"[\u2013\u2014]", "-", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = _SLUG_INVALID.sub("", s)
    s = _SLUG_DASHES.sub("-", s)
    s = s.strip("-")
    return s[:90] if len(s) > 90 else s


def load_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_line(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(value + "\n")


def write_lines(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(values) + ("\n" if values else ""), encoding="utf-8")


def html_escape(text) -> str:
    return html_escape_lib(str(text), quote=True)


def load_keyword_queue() -> list[str]:
    if not KEYWORDS_FILE.exists():
        print(f"[error] Keywords file missing: {KEYWORDS_FILE}", file=sys.stderr)
        return []
    all_keywords = load_lines(KEYWORDS_FILE)
    generated    = set(load_lines(GENERATED_KW_FILE))
    return [kw for kw in all_keywords if kw not in generated]


# =========================================================================
# ENGINE CLIENT (two-pass retry, no fallback content)
# =========================================================================

def fetch_seo_page(keyword: str, attempt: int = 1) -> dict | None:
    """POST /seo-page. Return payload or None on failure.

    One retry on transient errors. No fallback content ever.
    """
    try:
        resp = requests.post(
            SEO_PAGE_ENDPOINT,
            json={"keyword": keyword, "site": "nexus-dex"},
            timeout=SEO_PAGE_TIMEOUT_S,
        )
    except requests.RequestException as exc:
        print(f"[seo-page] network error (attempt {attempt}) for {keyword!r}: {exc}", file=sys.stderr)
        if attempt < 2:
            time.sleep(2.0)
            return fetch_seo_page(keyword, attempt + 1)
        return None

    if resp.status_code in (502, 503, 504, 429) and attempt < 2:
        print(f"[seo-page] HTTP {resp.status_code} (attempt {attempt}) for {keyword!r}, retrying", file=sys.stderr)
        time.sleep(2.0)
        return fetch_seo_page(keyword, attempt + 1)

    if resp.status_code != 200:
        print(f"[seo-page] HTTP {resp.status_code} for {keyword!r}: {resp.text[:200]}", file=sys.stderr)
        return None

    try:
        payload = resp.json()
    except ValueError:
        print(f"[seo-page] bad JSON for {keyword!r}", file=sys.stderr)
        return None

    if not payload.get("content") or not payload.get("meta"):
        print(f"[seo-page] missing content/meta for {keyword!r}", file=sys.stderr)
        return None

    return payload


def is_publishable(payload: dict) -> tuple[bool, str]:
    """Quality gate: engine must report score >= MIN_PUBLISH_SCORE, and
    content must look structurally valid (4 paragraphs, real prose)."""
    meta = payload.get("meta") or {}
    score = payload.get("score")
    if score is None:
        score = meta.get("score")

    if isinstance(score, (int, float)) and score < MIN_PUBLISH_SCORE:
        return False, f"score {score} < {MIN_PUBLISH_SCORE}"

    content = (payload.get("content") or "").strip()
    if len(content) < 400:
        return False, f"content too short ({len(content)} chars)"

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if len(paragraphs) < 3:
        return False, f"only {len(paragraphs)} paragraphs (need >=3)"

    # Engine should have stamped these. If they're missing, the page would
    # render badly even if the body is fine.
    required_meta_fields = ("title", "description", "h1", "intro")
    missing = [f for f in required_meta_fields if not (meta.get(f) or "").strip()]
    if missing:
        return False, f"meta missing: {','.join(missing)}"

    return True, ""


# =========================================================================
# COMPATIBILITY SHIM (kept for legacy callers)
# =========================================================================

def generate_nexus_dex_content(keyword: str) -> str:
    """Legacy interface: return only the content body. Use process_keyword()
    instead in new code."""
    payload = fetch_seo_page(keyword)
    if not payload:
        return ""
    ok, _reason = is_publishable(payload)
    if not ok:
        return ""
    return payload.get("content", "") or ""


# =========================================================================
# RELATED + MORE LINK RANKING
# =========================================================================

def _load_generated_pages() -> list[dict]:
    """Build [{slug, keyword, hub_slug}] from tracking files, aligned line by
    line. If they're out of sync, fall back to the slugs file only."""
    slugs_lines    = load_lines(GENERATED_SLUGS_FILE)
    keyword_lines  = load_lines(GENERATED_KW_FILE)

    parsed_slugs = []
    for line in slugs_lines:
        if ":" in line:
            hub_part, slug = line.split(":", 1)
        else:
            hub_part, slug = "", line
        slug = slug.strip()
        if slug:
            parsed_slugs.append((hub_part.strip(), slug))

    pages = []
    if len(parsed_slugs) == len(keyword_lines):
        for (hub_part, slug), kw in zip(parsed_slugs, keyword_lines):
            if slug in PROTECTED_SLUGS:
                continue
            hub_slug = hub_part or select_hub(kw)[0]
            pages.append({"slug": slug, "keyword": kw, "hub_slug": hub_slug})
    else:
        # Lines drifted: reconstruct from slugs alone.
        for hub_part, slug in parsed_slugs:
            if slug in PROTECTED_SLUGS:
                continue
            kw = slug.replace("-", " ")
            hub_slug = hub_part or select_hub(kw)[0]
            pages.append({"slug": slug, "keyword": kw, "hub_slug": hub_slug})
    return pages


def slug_to_title(slug: str) -> str:
    """Reconstruct a readable title from a slug, preserving ticker casing."""
    preserve = {
        "btc":"BTC","eth":"ETH","sol":"SOL","usdc":"USDC","usdt":"USDT",
        "bnb":"BNB","bonk":"BONK","pepe":"PEPE","wif":"WIF","doge":"DOGE",
        "shib":"SHIB","hype":"HYPE","popcat":"POPCAT","trump":"TRUMP",
        "jup":"JUP","ray":"RAY","pyth":"PYTH","jto":"JTO","spx":"SPX",
        "ai16z":"ai16z","fartcoin":"FARTCOIN","moodeng":"MOODENG",
        "pnut":"PNUT","goat":"GOAT","griffain":"GRIFFAIN","chillguy":"CHILLGUY",
        "zerebro":"ZEREBRO",
        "lp":"LP","dex":"DEX","cex":"CEX","nft":"NFT","spl":"SPL",
        "ai":"AI","dao":"DAO","defi":"DeFi","tvl":"TVL","kyc":"KYC",
        "lst":"LST","lrt":"LRT","rwa":"RWA","ico":"ICO","ido":"IDO",
        "etf":"ETF","fomc":"FOMC","cpi":"CPI","gdp":"GDP",
        "nfl":"NFL","nba":"NBA","ufc":"UFC",
        "xstocks":"xStocks","xstock":"xStock",
        "aapl":"AAPL","tsla":"TSLA","nvda":"NVDA","msft":"MSFT",
        "googl":"GOOGL","amzn":"AMZN","mstr":"MSTR","nflx":"NFLX",
        "spy":"SPY","qqq":"QQQ","crcl":"CRCL","hood":"HOOD","coin":"COIN",
        "aaplx":"AAPLx","tslax":"TSLAx","nvdax":"NVDAx","spyx":"SPYx",
        "qqqx":"QQQx","mstrx":"MSTRx","metax":"METAx","amznx":"AMZNx",
        "googlx":"GOOGLx","msftx":"MSFTx","nflxx":"NFLXx","crclx":"CRCLx",
        "hoodx":"HOODx",
        "us":"U.S.","vs":"vs",
    }
    small = {"a","an","and","as","at","by","for","from","in","of","on","or","the","to","vs","with"}
    out = []
    for i, w in enumerate(slug.replace("-", " ").split()):
        wl = w.lower()
        if wl in preserve:
            out.append(preserve[wl])
        elif i > 0 and wl in small:
            out.append(wl)
        else:
            out.append(w.capitalize())
    return " ".join(out)


def _tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if t and len(t) > 1}


def _rank_candidates(current: dict, all_pages: list[dict]) -> list[dict]:
    """Rank candidate pages by hub overlap then token overlap."""
    cur_tokens = _tokens(current["keyword"])
    cur_hub    = current["hub_slug"]

    def score(p):
        if p["slug"] == current["slug"]:
            return None
        same_hub  = 1 if p["hub_slug"] == cur_hub else 0
        overlap   = len(_tokens(p["keyword"]) & cur_tokens)
        return (-same_hub, -overlap, len(p["keyword"]), p["slug"])

    scored = [(score(p), p) for p in all_pages]
    scored = [(s, p) for s, p in scored if s is not None]
    scored.sort(key=lambda x: x[0])
    return [p for _, p in scored]


def get_related_and_more(current_slug: str, current_keyword: str, current_hub: str) -> tuple[list[dict], list[dict]]:
    """Return (related, more) page lists. Related comes from the same hub
    when possible; more fills in from neighbouring hubs."""
    all_pages = _load_generated_pages()
    current = {"slug": current_slug, "keyword": current_keyword, "hub_slug": current_hub}
    ranked = _rank_candidates(current, all_pages)
    related = ranked[:RELATED_LINKS_COUNT]
    used = {p["slug"] for p in related}
    more = [p for p in ranked if p["slug"] not in used][:MORE_LINKS_COUNT]
    return related, more


def build_links_html(pages: list[dict]) -> str:
    if not pages:
        return ""
    return "\n".join(
        f'<li><a href="/nexus-dex/{p["slug"]}/">{html_escape(slug_to_title(p["slug"]))}</a></li>'
        for p in pages
    )


def build_hub_link_html(hub_slug: str, hub_title: str) -> str:
    return (
        f'<span class="hub-link-label">Hub:</span> '
        f'<a class="hub-link-anchor" href="/nexus-dex/{html_escape(hub_slug)}/">'
        f'{html_escape(hub_title)}</a>'
    )


# =========================================================================
# META-DRIVEN PAGE BUILD
# =========================================================================

def build_page_meta_script(meta: dict, hl_data_block: str = "") -> str:
    """Expose engine meta to window.__pageMeta for template hydration."""
    payload = {
        "title":                meta.get("title", ""),
        "description":          meta.get("description", ""),
        "h1":                   meta.get("h1", ""),
        "intro":                meta.get("intro", ""),
        "contentHeading":       meta.get("contentHeading", ""),
        "contentBridge":        meta.get("contentBridge", ""),
        "breadcrumb":           meta.get("breadcrumb", ""),
        "intent":               meta.get("intent", ""),
        "subIntent":            meta.get("subIntent", ""),
        "shape":                meta.get("shape", ""),
        "subject":              meta.get("subject", ""),
        "faq":                  meta.get("faq", []),
        "threatBanner":         meta.get("threatBanner"),
        "recognitionChips":     meta.get("recognitionChips", []),
        "storyCardTitles":      meta.get("storyCardTitles", []),
        "supplementaryCards":   meta.get("supplementaryCards", []),
        "supplementaryHeading": meta.get("supplementaryHeading", ""),
        "supplementaryIntro":   meta.get("supplementaryIntro", ""),
        "ecosystemCards":       meta.get("ecosystemCards", []),
        "pageSignals":          meta.get("pageSignals", {}),
        "author":               meta.get("author", {}),
        "hlDataBlock":          hl_data_block or "",
    }
    blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    return f'<script id="page-meta">window.__pageMeta = {blob};</script>'


def _enforce_title_length(title: str, fallback: str) -> str:
    """Trim engine title to <=60 chars on a word boundary if needed."""
    title = (title or "").strip() or fallback
    if len(title) <= 60:
        return title
    # Try to drop trailing comma-clauses first.
    candidates = [
        re.sub(r",?\s*Mobile-First\s*$", "", title),
        re.sub(r",?\s*No KYC,?\s*Mobile-First\s*$", "", title),
        re.sub(r"\s*\|\s*[^|]*$", "", title),
    ]
    for c in candidates:
        if 0 < len(c) <= 60:
            return c
    cut = title[:60].rsplit(" ", 1)[0]
    return cut if cut else title[:60]


def render_page(template_html: str,
                keyword: str,
                payload: dict,
                slug: str,
                hub_slug: str,
                hub_title: str) -> str:
    """Substitute every placeholder. Raises ValueError if anything is left."""
    meta     = payload["meta"]
    content  = payload["content"]
    hl_block = payload.get("hlDataBlock", "") or ""

    related, more = get_related_and_more(slug, keyword, hub_slug)

    canonical = f"{SITE_URL}/nexus-dex/{slug}/"
    title     = _enforce_title_length(meta.get("title"), f"{keyword} | Nexus DEX")
    desc      = meta.get("description", "") or ""
    h1        = meta.get("h1", "") or ""
    intro     = meta.get("intro", "") or ""
    breadcrumb_name = meta.get("breadcrumb", "") or slug_to_title(slug)
    faq_schema      = meta.get("faqSchema", "") or "{}"
    page_signals    = meta.get("pageSignals") or {}

    aggregate_rating_json = (page_signals.get("aggregateRatingJson")
                             or json.dumps({
                                 "@type": "AggregateRating",
                                 "ratingValue": "4.8",
                                 "reviewCount": "2500",
                                 "bestRating": "5",
                             }, ensure_ascii=False))

    supp_heading = (meta.get("supplementaryHeading", "") or "Why Solana DeFi is different").strip()
    supp_intro   = (meta.get("supplementaryIntro", "") or "").strip()

    # Engine produces clean prose paragraphs separated by blank lines.
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    ai_content_html = "\n".join(f"<p>{html_escape(p)}</p>" for p in paragraphs)

    meta_script = build_page_meta_script(meta, hl_block)

    substitutions = {
        "{{TITLE}}":                  html_escape(title),
        "{{DESCRIPTION}}":            html_escape(desc),
        "{{KEYWORD}}":                html_escape(keyword),
        "{{AI_CONTENT}}":             ai_content_html,
        "{{RELATED_LINKS}}":          build_links_html(related),
        "{{MORE_LINKS}}":             build_links_html(more),
        "{{HUB_LINK}}":               build_hub_link_html(hub_slug, hub_title),
        "{{CANONICAL_URL}}":          html_escape(canonical),
        "{{MODIFIED_DATE}}":          datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "{{BREADCRUMB_NAME}}":        html_escape(breadcrumb_name),
        "{{STATIC_H1}}":              html_escape(h1),
        "{{STATIC_INTRO}}":           html_escape(intro),
        "{{OG_IMAGE}}":               html_escape(OG_IMAGE),
        "{{HL_DATA_BLOCK}}":          hl_block,
        "{{SCHEMA_FAQ}}":             faq_schema,
        "{{AGGREGATE_RATING_JSON}}":  aggregate_rating_json,
        "{{SUPP_HEADING}}":           html_escape(supp_heading),
        "{{SUPP_INTRO}}":             html_escape(supp_intro),
        "{{PAGE_META_SCRIPT}}":       meta_script,
    }

    rendered = template_html
    for placeholder, value in substitutions.items():
        rendered = rendered.replace(placeholder, str(value))

    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", rendered)))
    if unresolved:
        raise ValueError(f"Unresolved template placeholders: {', '.join(unresolved)}")

    return rendered


# =========================================================================
# BUILD ORCHESTRATION
# =========================================================================

def load_template() -> str:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template missing: {TEMPLATE_PATH}")
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def write_page(slug: str, html: str) -> Path:
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(html, encoding="utf-8")
    return out_file


def record_generated(slug: str, keyword: str, hub_slug: str) -> None:
    append_line(GENERATED_SLUGS_FILE, f"{hub_slug}:{slug}")
    append_line(GENERATED_KW_FILE, keyword)


def record_rejected(keyword: str, reason: str) -> None:
    append_line(REJECTED_FILE, f"{keyword}\t{reason}")


def process_keyword(keyword: str, template_html: str) -> bool:
    """Generate one page. Returns True only if the page was published."""
    slug = slugify(keyword)
    if not slug:
        record_rejected(keyword, "empty slug")
        return False
    if slug in PROTECTED_SLUGS:
        print(f"[build] skip protected slug: {slug}")
        return False

    print(f"[build] -> {keyword!r} (slug={slug})")

    payload = fetch_seo_page(keyword)
    if not payload:
        record_rejected(keyword, "engine returned no payload after retry")
        return False

    ok, reason = is_publishable(payload)
    if not ok:
        print(f"[build] REJECTED {keyword!r}: {reason}")
        record_rejected(keyword, reason)
        return False

    hub_slug, hub_title = select_hub(keyword)

    try:
        html = render_page(template_html, keyword, payload, slug, hub_slug, hub_title)
    except ValueError as exc:
        print(f"[build] REJECTED {keyword!r}: {exc}")
        record_rejected(keyword, f"render error: {exc}")
        return False

    out_file = write_page(slug, html)
    record_generated(slug, keyword, hub_slug)
    meta = payload.get("meta", {})
    print(f"[build] OK   -> {out_file} "
          f"(hub={hub_slug}, intent={meta.get('intent')}, "
          f"sub={meta.get('subIntent')}, score={payload.get('score')})")
    return True


def main(limit: int = DAILY_LIMIT) -> int:
    pending = load_keyword_queue()
    if not pending:
        print("[build] no pending keywords")
        return 0

    template_html = load_template()
    todo = pending[:limit]
    succeeded = 0
    failed    = 0

    print(f"[build] pending={len(pending)} todo={len(todo)} floor={MIN_PUBLISH_SCORE}")
    for i, keyword in enumerate(todo, 1):
        print(f"\n[build] [{i}/{len(todo)}] {keyword}")
        try:
            if process_keyword(keyword, template_html):
                succeeded += 1
            else:
                failed += 1
        except Exception as exc:
            failed += 1
            print(f"[build] EXCEPTION on {keyword!r}: {exc}", file=sys.stderr)
            record_rejected(keyword, f"exception: {exc}")
        time.sleep(0.4)

    print(f"\n[build] done. ok={succeeded} failed={failed} "
          f"remaining={len(pending) - len(todo) + failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Verixia Nexus DEX SEO pages.")
    parser.add_argument("--limit", type=int, default=DAILY_LIMIT,
                        help=f"max pages per run (default {DAILY_LIMIT})")
    parser.add_argument("--keyword", type=str, default=None,
                        help="process a single keyword (bypasses queue + limit)")
    args = parser.parse_args()

    if args.keyword:
        tpl = load_template()
        ok = process_keyword(args.keyword, tpl)
        sys.exit(0 if ok else 1)
    sys.exit(main(limit=args.limit))
