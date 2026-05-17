#!/usr/bin/env python3
"""
generate_nexus_dex_content.py -- v1.0

Builds Verixia Nexus DEX SEO pages from the keyword queue.

Architecture (mirrors generate_token_content.py v13):
  - Title, description, H1, hero intro, content H2, content bridge, FAQ, schema,
    threat banner, recognition chips, and story card titles all come from the
    Node SEO engine's `buildPageMeta(keyword)` -- single source of truth.
  - Python does NOT reimplement intent detection, subject extraction, or
    keyword cleaning. Those live in the engine.
  - Expects the same POST /seo-page endpoint on the Node server that returns
    the full page payload (content + meta + hlData). If the engine needs to
    return Nexus-DEX-flavored content rather than token-risk content, either
    route by keyword on the engine side or point SEO_PAGE_ENDPOINT below at
    a separate Nexus-DEX-specific endpoint.

What stays in Python:
  - Keyword queue loading and slug management.
  - Hub link selection (HUB_MATCH_RULES, HUB_TITLE_OVERRIDES) -- depends on
    the Nexus DEX hub taxonomy, kept in Python.
  - Related-page linking via get_related_pages() + build_links_html().
  - Daily limit handling.
  - Output paths and file I/O.

Compatibility shim:
  - Exposes `generate_nexus_dex_content(keyword)` that returns just the content
    body string for legacy callers (build_nexus_dex_seo_incremental.py,
    build_nexus_dex_seo.py).
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# =========================================================================
# CONFIG
# =========================================================================

# Repo layout: this script lives at BASE_DIR/scripts/generate_nexus_dex_content.py
BASE_DIR = Path(__file__).resolve().parent.parent

KEYWORDS_FILE        = BASE_DIR / "data" / "nexus_dex_keywords.txt"
GENERATED_SLUGS_FILE = BASE_DIR / "data" / "nexus_dex_generated_slugs.txt"
GENERATED_KW_FILE    = BASE_DIR / "data" / "nexus_dex_generated_keywords.txt"

TEMPLATE_PATH        = BASE_DIR / "nexus-dex-template" / "nexus-dex-template.html"

OUTPUT_DIR           = BASE_DIR / "nexus-dex"

SITE_URL             = "https://verixiaapps.com"
SEO_API_BASE         = "https://awake-integrity-production-faa0.up.railway.app"
SEO_PAGE_ENDPOINT    = f"{SEO_API_BASE}/seo-page"
SEO_PAGE_TIMEOUT_S   = 90

DAILY_LIMIT          = 8

OG_IMAGE             = f"{SITE_URL}/og/nexus-dex.png"
TWITTER_HANDLE       = "@verixiaapps"

# =========================================================================
# HUB SYSTEM (mirrors nexus_dex_clusters.py taxonomy)
# =========================================================================

HUB_MATCH_RULES = [
    # Order matters: first match wins.
    # (regex pattern, hub_slug, hub_title_override_key)
    (r"\bhyperliquid\b",
        "hyperliquid-frontend", "hyperliquid"),
    (r"\bpolymarket\b",
        "polymarket-prediction", "polymarket"),
    (r"\bbtc\s+perp|bitcoin\s+perp|bitcoin\s+futures|bitcoin\s+perpetual",
        "bitcoin-perps", "btc_perps"),
    (r"\beth\s+perp|ethereum\s+perp|ethereum\s+futures|ethereum\s+perpetual",
        "ethereum-perps", "eth_perps"),
    (r"\bsol\s+perp|solana\s+perp|sol\s+perpetual",
        "solana-perps", "sol_perps"),
    (r"\bmemecoin\s+perp|altcoin\s+perp|\bwif\s+perp|\bbonk\s+perp|\bpepe\s+perp|\bdoge\s+perp|\bhype\s+perp",
        "altcoin-perps", "altcoin_perps"),
    (r"\bprediction\s+market|\bbet\s+on\b|\bodds\b|yes\s+or\s+no\s+market",
        "prediction-markets", "prediction"),
    (r"\bwhale\b|\bsmart\s+money\b|\binsider\b|\bdeployer\b|\bsniper\b|kol\s+wallet",
        "whale-tracking", "whale"),
    (r"\blaunch\s+token|\btoken\s+launch|\blaunchpad\b|bonding\s+curve|deploy\s+token",
        "token-launch", "launch"),
    (r"\bsolana\s+swap|\bsolana\s+dex|\bdex\s+aggregator|best\s+price\s+swap",
        "solana-swap", "swap"),
    (r"\bbuy\s+bonk|\bbuy\s+wif|\bbuy\s+pepe|\bbuy\s+trump|\bbuy\s+memecoin|\bbuy\s+spl|\bbuy\b",
        "buy-token", "buy_token"),
    (r"phantom\s+wallet\s+trading|backpack\s+wallet\s+trading|self\s+custodial|non\s+custodial|wallet\s+based",
        "wallet-trading", "wallet"),
    (r"no\s+kyc|without\s+kyc|no\s+signup|no\s+verification",
        "no-kyc-trading", "no_kyc"),
    (r"\bperp(s|etual)|\bleverage|\blong\b|\bshort\b|\bhedge\b",
        "perps-trading", "perps"),
    (r"\bswap\b",
        "solana-swap", "swap"),
    (r"how\s+to\b",
        "how-to-guides", "how_to"),
]

HUB_TITLE_OVERRIDES = {
    "hyperliquid":   "Hyperliquid Frontend Hub",
    "polymarket":    "Polymarket Hub",
    "btc_perps":     "Bitcoin Perps Hub",
    "eth_perps":     "Ethereum Perps Hub",
    "sol_perps":     "SOL Perps Hub",
    "altcoin_perps": "Altcoin Perps Hub",
    "prediction":    "Prediction Markets Hub",
    "whale":         "Whale Tracking Hub",
    "launch":        "Token Launch Hub",
    "swap":          "Solana Swap Hub",
    "buy_token":     "Buy Token Hub",
    "wallet":        "Wallet Trading Hub",
    "no_kyc":        "No KYC Trading Hub",
    "perps":         "Perps Trading Hub",
    "how_to":        "Nexus DEX Guides Hub",
}

DEFAULT_HUB_SLUG  = "nexus-dex"
DEFAULT_HUB_TITLE = "Nexus DEX"

def select_hub(keyword: str) -> tuple[str, str]:
    """Return (hub_slug, hub_title) for the keyword based on hub rules."""
    lower = keyword.lower()
    for pattern, hub_slug, override_key in HUB_MATCH_RULES:
        if re.search(pattern, lower):
            title = HUB_TITLE_OVERRIDES.get(override_key, DEFAULT_HUB_TITLE)
            return hub_slug, title
    return DEFAULT_HUB_SLUG, DEFAULT_HUB_TITLE

# =========================================================================
# SLUG MANAGEMENT
# =========================================================================

_SLUG_INVALID = re.compile(r"[^a-z0-9\-]+")
_SLUG_DASHES  = re.compile(r"-{2,}")

def slugify(keyword: str) -> str:
    """Generate URL-safe slug from a keyword."""
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

def load_keyword_queue() -> list[str]:
    """Load keywords from queue, deduped against generated tracking."""
    if not KEYWORDS_FILE.exists():
        print(f"[error] Keywords file missing: {KEYWORDS_FILE}", file=sys.stderr)
        return []
    all_keywords = load_lines(KEYWORDS_FILE)
    generated    = set(load_lines(GENERATED_KW_FILE))
    pending      = [kw for kw in all_keywords if kw not in generated]
    return pending

# =========================================================================
# ENGINE API CLIENT
# =========================================================================

def fetch_seo_page(keyword: str) -> dict | None:
    """
    POST /seo-page on the Node engine. Returns:
      {
        keyword, content, templateType,
        meta: { title, description, h1, intro, contentHeading, contentBridge,
                breadcrumb, faq, faqSchema, threatBanner, recognitionChips,
                storyCardTitles, intent, shape, subject, subjects },
        hlData, hlDataBlock
      }
    Returns None on hard failure (network, 5xx, malformed response).
    """
    try:
        resp = requests.post(
            SEO_PAGE_ENDPOINT,
            json={"keyword": keyword, "site": "nexus-dex"},
            timeout=SEO_PAGE_TIMEOUT_S,
        )
    except requests.RequestException as exc:
        print(f"[seo-page] Network error for {keyword!r}: {exc}", file=sys.stderr)
        return None

    if resp.status_code != 200:
        print(f"[seo-page] HTTP {resp.status_code} for {keyword!r}: {resp.text[:200]}", file=sys.stderr)
        return None

    try:
        payload = resp.json()
    except ValueError:
        print(f"[seo-page] Bad JSON for {keyword!r}", file=sys.stderr)
        return None

    # Minimum field check
    if not payload.get("content") or not payload.get("meta"):
        print(f"[seo-page] Missing content/meta for {keyword!r}", file=sys.stderr)
        return None

    return payload

# =========================================================================
# COMPATIBILITY SHIM
# =========================================================================
#
# Legacy callers (build_nexus_dex_seo_incremental.py, build_nexus_dex_seo.py)
# import `generate_nexus_dex_content` and expect a plain string of body
# content for a given keyword. The architecture fetches a full payload from
# the Node /seo-page endpoint, so this shim extracts and returns just the
# `content` field. Returns "" on failure -- callers already handle empty.

def generate_nexus_dex_content(keyword: str) -> str:
    """Compatibility shim: return just the content body string.

    Wraps fetch_seo_page() and returns payload["content"] (or "" on failure)
    so legacy importers keep working without changes.
    """
    payload = fetch_seo_page(keyword)
    if not payload:
        return ""
    return payload.get("content", "") or ""

# =========================================================================
# RELATED PAGES
# =========================================================================

def get_related_pages(current_slug: str, current_hub: str, limit: int = 4) -> list[tuple[str, str]]:
    """
    Returns up to `limit` (slug, title) pairs of previously-generated pages
    from the same hub (prioritised), then other hubs as fill-in.
    Title is reconstructed from the slug.
    """
    all_slugs = load_lines(GENERATED_SLUGS_FILE)
    same_hub  = []
    other_hub = []

    for line in all_slugs:
        # Format: <hub_slug>:<page_slug> if stored that way, else just <page_slug>
        if ":" in line:
            hub_part, slug = line.split(":", 1)
        else:
            hub_part, slug = DEFAULT_HUB_SLUG, line

        if slug == current_slug:
            continue

        title = slug_to_title(slug)
        if hub_part == current_hub:
            same_hub.append((slug, title, hub_part))
        else:
            other_hub.append((slug, title, hub_part))

    chosen = same_hub[:limit]
    if len(chosen) < limit:
        chosen += other_hub[: limit - len(chosen)]

    # Reverse so newest appears first (slugs are appended chronologically)
    chosen.reverse()
    return [(slug, title) for slug, title, _ in chosen[:limit]]

def slug_to_title(slug: str) -> str:
    """Reconstruct a readable title from a slug."""
    words = slug.replace("-", " ").split()
    preserve = {
        "btc": "BTC", "eth": "ETH", "sol": "SOL", "usdc": "USDC", "usdt": "USDT",
        "bnb": "BNB", "bonk": "BONK", "pepe": "PEPE", "wif": "WIF", "doge": "DOGE",
        "shib": "SHIB", "hype": "HYPE", "popcat": "POPCAT", "trump": "TRUMP",
        "jup": "JUP", "ray": "RAY", "pyth": "PYTH", "jto": "JTO", "spx": "SPX",
        "ai16z": "ai16z", "fartcoin": "FARTCOIN", "moodeng": "MOODENG",
        "pnut": "PNUT", "goat": "GOAT", "griffain": "GRIFFAIN", "chillguy": "CHILLGUY",
        "zerebro": "ZEREBRO",
        "lp": "LP", "dex": "DEX", "cex": "CEX", "nft": "NFT", "spl": "SPL",
        "ai": "AI", "dao": "DAO", "defi": "DeFi", "tvl": "TVL", "kyc": "KYC",
        "lst": "LST", "lrt": "LRT", "rwa": "RWA", "ico": "ICO", "ido": "IDO",
        "etf": "ETF", "fomc": "FOMC", "cpi": "CPI", "gdp": "GDP",
        "nfl": "NFL", "nba": "NBA", "ufc": "UFC",
        "vs": "vs",
    }
    out = []
    for w in words:
        if w in preserve:
            out.append(preserve[w])
        else:
            out.append(w.capitalize())
    return " ".join(out)

def build_links_html(related: list[tuple[str, str]], hub_slug: str) -> str:
    """Build the related-links HTML block."""
    if not related:
        return ""
    items = []
    for slug, title in related:
        href = f"/nexus-dex/{slug}/"
        items.append(f'<a class="related-link" href="{href}">{title}</a>')
    return "\n".join(items)

# =========================================================================
# TEMPLATE RENDERING
# =========================================================================

def load_template() -> str:
    """Load the Nexus DEX template HTML."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template missing: {TEMPLATE_PATH}")
    return TEMPLATE_PATH.read_text(encoding="utf-8")

def html_escape(text: str) -> str:
    """Minimal HTML escape for attribute / inline text contexts."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

def render_ai_content_html(content: str) -> str:
    """Render the engine content as HTML paragraphs."""
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    return "\n".join(f"<p>{html_escape(p)}</p>" for p in paragraphs)

def build_page_meta_script(meta: dict, hl_data_block: str = "") -> str:
    """
    Inject the engine's full meta object as window.__pageMeta. The template's
    JS reads this -- if present, it skips client-side regeneration of H1,
    intro, content heading, content bridge, FAQ, chips, and threat banner.
    """
    payload = {
        "title":            meta.get("title", ""),
        "description":      meta.get("description", ""),
        "h1":               meta.get("h1", ""),
        "intro":            meta.get("intro", ""),
        "contentHeading":   meta.get("contentHeading", ""),
        "contentBridge":    meta.get("contentBridge", ""),
        "breadcrumb":       meta.get("breadcrumb", ""),
        "intent":           meta.get("intent", ""),
        "shape":            meta.get("shape", ""),
        "subject":          meta.get("subject", ""),
        "faq":              meta.get("faq", []),
        "threatBanner":     meta.get("threatBanner"),
        "recognitionChips": meta.get("recognitionChips", []),
        "storyCardTitles":  meta.get("storyCardTitles", []),
        "hlDataBlock":      hl_data_block or "",
    }
    json_blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    # Escape closing script tags inside JSON to be safe
    safe_blob = json_blob.replace("</", "<\\/")
    return f'<script id="page-meta">window.__pageMeta = {safe_blob};</script>'

def render_page(template_html: str, keyword: str, payload: dict,
                slug: str, hub_slug: str, hub_title: str,
                related_html: str) -> str:
    """Replace all placeholders in the template with engine-supplied values."""
    meta = payload["meta"]
    content = payload["content"]
    hl_block = payload.get("hlDataBlock", "") or ""

    canonical = f"{SITE_URL}/nexus-dex/{slug}/"
    page_url  = canonical
    title     = meta.get("title", "")
    desc      = meta.get("description", "")
    h1        = meta.get("h1", "")
    intro     = meta.get("intro", "")
    content_heading = meta.get("contentHeading", "")
    content_bridge  = meta.get("contentBridge", "")
    breadcrumb_name = meta.get("breadcrumb", "")
    faq_schema      = meta.get("faqSchema", "")

    ai_content_html = render_ai_content_html(content)
    meta_script     = build_page_meta_script(meta, hl_block)

    substitutions = {
        # Standard meta
        "{{TITLE}}":               title,
        "{{DESCRIPTION}}":         desc,
        "{{KEYWORD}}":             keyword,
        "{{CANONICAL_URL}}":       canonical,
        "{{PAGE_URL}}":            page_url,
        "{{SITE_URL}}":            SITE_URL,

        # Open Graph / Twitter
        "{{OG_TITLE}}":            title,
        "{{OG_DESCRIPTION}}":      desc,
        "{{OG_URL}}":              page_url,
        "{{OG_IMAGE}}":            OG_IMAGE,
        "{{TWITTER_TITLE}}":       title,
        "{{TWITTER_DESCRIPTION}}": desc,
        "{{TWITTER_HANDLE}}":      TWITTER_HANDLE,

        # Hero / content (server-rendered; template JS respects these)
        "{{STATIC_H1}}":           html_escape(h1),
        "{{STATIC_INTRO}}":        html_escape(intro),
        "{{CONTENT_HEADING}}":     html_escape(content_heading),
        "{{CONTENT_BRIDGE}}":      html_escape(content_bridge),
        "{{BREADCRUMB_NAME}}":     html_escape(breadcrumb_name),

        # Body content
        "{{AI_CONTENT}}":          ai_content_html,
        "{{HL_DATA_BLOCK}}":       hl_block,

        # Schema + meta JSON for template JS
        "{{SCHEMA_FAQ}}":          faq_schema,
        "{{PAGE_META_SCRIPT}}":    meta_script,

        # Hub / related
        "{{HUB_SLUG}}":            hub_slug,
        "{{HUB_TITLE}}":           html_escape(hub_title),
        "{{HUB_LINK_HREF}}":       f"/nexus-dex/{hub_slug}/",
        "{{HUB_LINK_TEXT}}":       html_escape(hub_title),
        "{{RELATED_LINKS}}":       related_html,
        "{{LINKS_HTML}}":          related_html,

        # Generation timestamp
        "{{GENERATED_AT}}":        datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    rendered = template_html
    for placeholder, value in substitutions.items():
        rendered = rendered.replace(placeholder, str(value))

    # Insert page-meta script before </head> if {{PAGE_META_SCRIPT}} is not present
    if "{{PAGE_META_SCRIPT}}" not in template_html and "window.__pageMeta" not in rendered:
        if "</head>" in rendered:
            rendered = rendered.replace("</head>", f"{meta_script}\n</head>", 1)

    return rendered

# =========================================================================
# BUILD LOOP
# =========================================================================

def write_page(slug: str, html: str) -> Path:
    """Write the rendered HTML to the Nexus DEX output directory."""
    output_dir = OUTPUT_DIR / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "index.html"
    output_file.write_text(html, encoding="utf-8")
    return output_file

def record_generated(slug: str, keyword: str, hub_slug: str) -> None:
    """Mark a slug + keyword as generated so it doesn't rebuild."""
    append_line(GENERATED_SLUGS_FILE, f"{hub_slug}:{slug}")
    append_line(GENERATED_KW_FILE, keyword)

def process_keyword(keyword: str) -> bool:
    """Process a single keyword. Returns True on success, False otherwise."""
    print(f"[build] -> {keyword!r}")
    payload = fetch_seo_page(keyword)
    if not payload:
        print(f"[build] FAILED: could not fetch payload for {keyword!r}")
        return False

    meta = payload["meta"]

    slug = slugify(keyword)
    if not slug:
        print(f"[build] FAILED: empty slug for {keyword!r}")
        return False

    hub_slug, hub_title = select_hub(keyword)
    related     = get_related_pages(slug, hub_slug, limit=4)
    related_html = build_links_html(related, hub_slug)

    template_html = load_template()
    rendered = render_page(
        template_html=template_html,
        keyword=keyword,
        payload=payload,
        slug=slug,
        hub_slug=hub_slug,
        hub_title=hub_title,
        related_html=related_html,
    )

    output_file = write_page(slug, rendered)
    record_generated(slug, keyword, hub_slug)
    print(f"[build] OK -> {output_file} (intent={meta.get('intent')}, shape={meta.get('shape')})")
    return True

def main(limit: int = DAILY_LIMIT) -> int:
    """Build up to `limit` pages from the keyword queue."""
    pending = load_keyword_queue()
    if not pending:
        print("[build] No pending keywords.")
        return 0

    print(f"[build] Pending: {len(pending)} | Daily limit: {limit}")
    todo = pending[:limit]
    succeeded = 0
    failed    = 0

    for i, keyword in enumerate(todo, 1):
        print(f"\n[build] [{i}/{len(todo)}] {keyword}")
        try:
            ok = process_keyword(keyword)
            if ok:
                succeeded += 1
            else:
                failed += 1
        except Exception as exc:
            failed += 1
            print(f"[build] EXCEPTION on {keyword!r}: {exc}", file=sys.stderr)
        time.sleep(0.5)  # Tiny pause between calls

    print(f"\n[build] Done. Success: {succeeded} | Failed: {failed} | Skipped: {len(pending) - len(todo)}")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build Verixia Nexus DEX SEO pages from keyword queue.")
    parser.add_argument("--limit", type=int, default=DAILY_LIMIT,
                        help=f"Max pages per run (default {DAILY_LIMIT})")
    parser.add_argument("--keyword", type=str, default=None,
                        help="Process a single keyword (bypasses queue + daily limit)")
    args = parser.parse_args()

    if args.keyword:
        ok = process_keyword(args.keyword)
        sys.exit(0 if ok else 1)
    sys.exit(main(limit=args.limit))


# =========================================================================
# ROUTE_SNIPPET -- the Node server.js / index.js side
# =========================================================================
#
# This Python script POSTs {"keyword": "...", "site": "nexus-dex"} to the
# /seo-page endpoint. The "site" field lets the engine route to Nexus-DEX
# content generation (vs token-risk). If your engine doesn't yet handle the
# "site" field, either:
#
#   (a) update the engine to read req.body.site and switch system prompts,
#       OR
#   (b) point SEO_PAGE_ENDPOINT at a separate endpoint like /seo-page-nexus
#       and add a dedicated route on the Node side.
#
# Example route handler with site routing:
#
# import { generateSeoPagePayload } from "./seo_engine.js";
#
# app.post("/seo-page", async (req, res) => {
#   try {
#     const { keyword, site } = req.body || {};
#     if (!keyword) return res.status(400).json({ error: "keyword required" });
#     const payload = await generateSeoPagePayload(keyword, { site: site || "token-risk" });
#     res.json({ ...payload, templateType: "nexus-dex" });
#   } catch (err) {
#     console.error("[/seo-page]", err);
#     res.status(500).json({ error: err.message || "generation failed" });
#   }
# });
#
# =========================================================================
