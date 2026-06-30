#!/usr/bin/env python3
"""
generate_token_content.py -- v13.1

Builds Verixia token-risk and DEX-aggregator SEO pages from the keyword queue.

v13.1 (CURRENT):
  - Added per-keyword endpoint routing. Token-risk keywords now POST to
    /token-risk-page (backed by riskEngine.js v18.5). DEX-aggregator and
    DeFi-perps keywords keep using /seo-page (backed by tokenriskseoengine.js).
  - select_engine_endpoint() picks the right URL using the existing
    HUB_MATCH_RULES, so routing follows the same taxonomy as hub selection.
  - No other behavior changed. Templates, slugs, related links, generated
    tracking files all work the same.

v13.0 (preserved):
  - Title, description, H1, hero intro, content H2, content bridge, FAQ,
    schema, threat banner, recognition chips, and story card titles all come
    from the Node SEO engine's `buildPageMeta(keyword)` -- single source of
    truth.
  - Python no longer reimplements intent detection, subject extraction, or
    keyword cleaning. Those live in the engine.

v13.0.1 patch (preserved):
  - `generate_token_content(keyword)` compatibility shim returns just the
    content body string from the page payload for legacy callers.
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

# Repo layout: this script lives at BASE_DIR/scripts/generate_token_content.py
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths preserved verbatim from v12 -- do not change without coordinating
# with cron / Railway / deploy pipeline.
KEYWORDS_FILE        = BASE_DIR / "data" / "token_keywords.txt"
GENERATED_SLUGS_FILE = BASE_DIR / "data" / "token_generated_slugs.txt"
GENERATED_KW_FILE    = BASE_DIR / "data" / "token_generated_keywords.txt"

TEMPLATE_RISK_PATH   = BASE_DIR / "token-risk-template" / "token-risk-template-a.html"
TEMPLATE_DEX_PATH    = BASE_DIR / "token-risk-template" / "dex-aggregator-template.html"
TEMPLATE_DEFI_PATH   = BASE_DIR / "token-risk-template" / "defi-general-template-a.html"

OUTPUT_DIR_RISK      = BASE_DIR / "token-risk"
OUTPUT_DIR_DEX       = BASE_DIR / "dex"
OUTPUT_DIR_DEFI      = BASE_DIR / "defi"

SITE_URL             = "https://verixiaapps.com"
SEO_API_BASE         = "https://awake-integrity-production-faa0.up.railway.app"

# Two engine endpoints (v13.1):
#   /seo-page         -> tokenriskseoengine.js  (LEGACY -- dex + defi-general)
#   /token-risk-page  -> riskEngine.js v18.5    (NEW    -- token-risk only)
SEO_PAGE_ENDPOINT             = f"{SEO_API_BASE}/seo-page"
SEO_TOKEN_RISK_PAGE_ENDPOINT  = f"{SEO_API_BASE}/token-risk-page"
SEO_PAGE_TIMEOUT_S            = 45  # engine worst case is now ~25s per pass

DAILY_LIMIT          = 8

OG_IMAGE             = f"{SITE_URL}/og-default.png"
TWITTER_HANDLE       = "@verixiaapps"

# =========================================================================
# HUB SYSTEM (preserved -- depends on your taxonomy)
# =========================================================================

HUB_MATCH_RULES = [
    # Order matters: first match wins.
    # (regex pattern, hub_slug, hub_title_override_key)
    (r"\bhoneypot\b",                        "honeypot-tokens",       "honeypot"),
    (r"\brug\s*pull|rugpull|\brug\b",        "rug-pull-detection",    "rug_pull"),
    (r"\bscam|fraud|fake|phish",             "scam-token-detection",  "scam"),
    (r"\bsolana\b.*\bswap\b|\bswap\b.*\bsolana\b|\bspl\b.*\bswap\b",
                                              "solana-dex-aggregator", "swap"),
    (r"\bperp(s|etual)|funding\s+rate|liquidation|leverage",
                                              "defi-perpetuals",       "perps"),
    (r"\bdex\s+aggregator|swap\s+aggregator|best\s+price\s+swap",
                                              "solana-dex-aggregator", "aggregator"),
    (r"\bmeme\s+coin",                       "meme-coin-risk",        "meme"),
    (r"\bnew\s+token|token\s+launch|presale",
                                              "new-token-risk",        "new_token"),
    (r"\bholder|concentration|whale",        "holder-concentration",  "holders"),
    (r"\blp\s+lock|liquidity\s+lock|locked\s+liquidity",
                                              "liquidity-lock",        "lp_lock"),
    (r"\bcontract|smart\s+contract|renounce|mint(able|\s+authority)|freeze|blacklist",
                                              "contract-risk",         "contract"),
]

HUB_TITLE_OVERRIDES = {
    "honeypot":   "Honeypot Token Detection Hub",
    "rug_pull":   "Rug Pull Detection Hub",
    "scam":       "Scam Token Detection Hub",
    "swap":       "Solana DEX Aggregator",
    "perps":      "DeFi Perpetuals Hub",
    "aggregator": "Solana DEX Aggregator",
    "meme":       "Meme Coin Risk Hub",
    "new_token":  "New Token Risk Hub",
    "holders":    "Holder Concentration Hub",
    "lp_lock":    "Liquidity Lock Status Hub",
    "contract":   "Contract Risk Hub",
}

# Hub slugs that should NOT route to the new /token-risk-page endpoint.
# These keep using the legacy /seo-page endpoint because they produce
# templates (dex-aggregator, defi-general) that the legacy engine handles.
NON_TOKEN_RISK_HUBS = {"solana-dex-aggregator", "defi-perpetuals"}

DEFAULT_HUB_SLUG  = "token-risk"
DEFAULT_HUB_TITLE = "Token Risk Checker"

def select_hub(keyword: str) -> tuple[str, str]:
    """Return (hub_slug, hub_title) for the keyword based on hub rules."""
    lower = keyword.lower()
    for pattern, hub_slug, override_key in HUB_MATCH_RULES:
        if re.search(pattern, lower):
            title = HUB_TITLE_OVERRIDES.get(override_key, DEFAULT_HUB_TITLE)
            return hub_slug, title
    return DEFAULT_HUB_SLUG, DEFAULT_HUB_TITLE

def select_engine_endpoint(keyword: str) -> str:
    """Pick the engine endpoint URL for `keyword`.

    Token-risk keywords route to /token-risk-page (riskEngine.js v18.5).
    DEX-aggregator and DeFi-perps keywords route to /seo-page
    (tokenriskseoengine.js -- legacy). Everything else defaults to the
    new token-risk endpoint, matching the default hub.
    """
    hub_slug, _ = select_hub(keyword)
    if hub_slug in NON_TOKEN_RISK_HUBS:
        return SEO_PAGE_ENDPOINT
    return SEO_TOKEN_RISK_PAGE_ENDPOINT

# =========================================================================
# SLUG MANAGEMENT
# =========================================================================

_SLUG_INVALID = re.compile(r"[^a-z0-9\-]+")
_SLUG_DASHES  = re.compile(r"-{2,}")

def slugify(keyword: str) -> str:
    """Generate URL-safe slug from a keyword. Same logic as v12."""
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
    POST the appropriate engine endpoint for `keyword`. Returns:
      {
        keyword, content, templateType,
        meta: { title, description, h1, intro, contentHeading, contentBridge,
                breadcrumb, faq, faqSchema, threatBanner, recognitionChips,
                storyCardTitles, intent, shape, subject, subjects },
        hlData, hlDataBlock
      }
    Returns None on hard failure (network, 5xx, malformed response).
    """
    endpoint = select_engine_endpoint(keyword)

    try:
        resp = requests.post(
            endpoint,
            json={"keyword": keyword},
            timeout=SEO_PAGE_TIMEOUT_S,
        )
    except requests.RequestException as exc:
        print(f"[seo-page] Network error at {endpoint} for {keyword!r}: {exc}", file=sys.stderr)
        return None

    if resp.status_code != 200:
        print(f"[seo-page] HTTP {resp.status_code} at {endpoint} for {keyword!r}: {resp.text[:200]}", file=sys.stderr)
        return None

    try:
        payload = resp.json()
    except ValueError:
        print(f"[seo-page] Bad JSON at {endpoint} for {keyword!r}", file=sys.stderr)
        return None

    # Minimum field check
    if not payload.get("content") or not payload.get("meta"):
        print(f"[seo-page] Missing content/meta at {endpoint} for {keyword!r}", file=sys.stderr)
        return None

    return payload

# =========================================================================
# COMPATIBILITY SHIM
# =========================================================================
#
# Legacy callers (e.g. build_token_seo_incremental.py) import
# `generate_token_content` and expect a plain string of body content for a
# given keyword. The new architecture fetches a full payload from the Node
# endpoint, so this shim extracts and returns just the `content` field.
# Returns "" on failure -- callers already handle empty strings.

def generate_token_content(keyword: str) -> str:
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
        "shib": "SHIB", "lp": "LP", "dex": "DEX", "cex": "CEX", "nft": "NFT",
        "ai": "AI", "dao": "DAO", "defi": "DeFi", "tvl": "TVL", "kyc": "KYC",
        "lst": "LST", "lrt": "LRT", "rwa": "RWA", "ico": "ICO", "ido": "IDO",
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
        href = f"/{hub_slug}/{slug}/"
        items.append(f'<a class="related-link" href="{href}">{title}</a>')
    return "\n".join(items)

# =========================================================================
# TEMPLATE RENDERING
# =========================================================================

def load_template(template_type: str) -> str:
    """Load template HTML based on type (risk, dex, or defi-general)."""
    if template_type == "dex":
        path = TEMPLATE_DEX_PATH
    elif template_type == "defi-general":
        path = TEMPLATE_DEFI_PATH
    else:
        path = TEMPLATE_RISK_PATH
    if not path.exists():
        raise FileNotFoundError(f"Template missing: {path}")
    return path.read_text(encoding="utf-8")

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
    """Render the 4-paragraph engine content as HTML paragraphs."""
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

    canonical = f"{SITE_URL}/{hub_slug}/{slug}/"
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

        # Hero / content (server-rendered; template JS now respects these)
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
        "{{HUB_LINK_HREF}}":       f"/{hub_slug}/",
        "{{HUB_LINK_TEXT}}":       html_escape(hub_title),
        "{{RELATED_LINKS}}":       related_html,
        "{{LINKS_HTML}}":          related_html,

        # Generation timestamp
        "{{GENERATED_AT}}":        datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    rendered = template_html
    # Fill the live data panel placeholders ({{LIVE_*}}, {{ROBOTS}}) from the
    # engine's enrichmentData. Safe to call even if engine returned no data —
    # the helper falls back to '—' values and noindex's the page.
    merge_live_fields(substitutions, payload)

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

def write_page(template_type: str, slug: str, hub_slug: str, html: str) -> Path:
    """Write the rendered HTML to the correct output directory."""
    if template_type == "dex":
        output_dir = OUTPUT_DIR_DEX / slug
    elif template_type == "defi-general":
        output_dir = OUTPUT_DIR_DEFI / slug
    else:
        # Token risk pages: respect the hub slug if it differs from default
        output_dir = OUTPUT_DIR_RISK / slug
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
    endpoint = select_engine_endpoint(keyword)
    print(f"[build]    endpoint: {endpoint}")
    payload = fetch_seo_page(keyword)
    if not payload:
        print(f"[build] FAILED: could not fetch payload for {keyword!r}")
        return False

    template_type = payload.get("templateType", "risk")
    meta          = payload["meta"]

    slug = slugify(keyword)
    if not slug:
        print(f"[build] FAILED: empty slug for {keyword!r}")
        return False

    hub_slug, hub_title = select_hub(keyword)
    related     = get_related_pages(slug, hub_slug, limit=4)
    related_html = build_links_html(related, hub_slug)

    template_html = load_template(template_type)
    rendered = render_page(
        template_html=template_html,
        keyword=keyword,
        payload=payload,
        slug=slug,
        hub_slug=hub_slug,
        hub_title=hub_title,
        related_html=related_html,
    )

    output_file = write_page(template_type, slug, hub_slug, rendered)
    record_generated(slug, keyword, hub_slug)
    extras = []
    if payload.get("dataMode"):    extras.append(f"mode={payload['dataMode']}")
    if payload.get("score"):       extras.append(f"score={payload['score']}")
    extras_str = f" ({', '.join(extras)})" if extras else ""
    print(f"[build] OK -> {output_file} (intent={meta.get('intent')}, shape={meta.get('shape')}){extras_str}")
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
    parser = argparse.ArgumentParser(description="Build Verixia SEO pages from keyword queue.")
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
# ROUTE_SNIPPETS -- already in server.js as of v13.1
# =========================================================================
#
# /seo-page          -> tokenriskseoengine.js (legacy, dex + defi-general)
# /token-risk-page   -> riskEngine.js v18.5   (token-risk template only)
#
# Routing decision lives in select_engine_endpoint() above. The legacy
# /seo-page route handles solana-dex-aggregator and defi-perpetuals hubs;
# everything else goes to /token-risk-page.
# =========================================================================

# =========================================================================
# v13.2 PATCH -- Live data panel + noindex gate
# =========================================================================
#
# Surfaces the DexScreener numbers the engine fetches (which currently only
# exist inside the AI prompt) as visible HTML, fills the new {{LIVE_*}}
# placeholders in token-risk-template-a.html, and noindex's pages where
# enrichment data was unavailable.
#
# Call merge_live_fields(replacements, engine_result) just before applying
# replacements to the template string.
# =========================================================================
from datetime import datetime, timezone


def _fmt_usd(n):
    """48210 -> '$48,210'; 1840000 -> '$1.84M'."""
    if n is None:
        return "—"
    try:
        v = float(n)
    except (TypeError, ValueError):
        return "—"
    if v >= 1_000_000_000:
        return f"${v / 1_000_000_000:.2f}B"
    if v >= 1_000_000:
        return f"${v / 1_000_000:.2f}M"
    if v >= 1_000:
        return f"${v:,.0f}"
    return f"${v:.2f}"


def _fmt_pct(n):
    if n is None:
        return "—"
    try:
        return f"{float(n):.1f}%"
    except (TypeError, ValueError):
        return "—"


def _fmt_age(days):
    if days is None:
        return "—"
    try:
        d = int(days)
    except (TypeError, ValueError):
        return "—"
    if d < 1:
        return "< 1 day"
    if d == 1:
        return "1 day"
    if d < 30:
        return f"{d} days"
    if d < 365:
        return f"{d // 30} mo"
    return f"{d // 365}y {(d % 365) // 30}mo"


def _ago(fetched_at_iso):
    """'14 sec ago' / '3 min ago' / '2 hr ago' from an ISO timestamp."""
    if not fetched_at_iso:
        return "just now"
    try:
        t = datetime.fromisoformat(str(fetched_at_iso).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return "just now"
    delta = (datetime.now(timezone.utc) - t).total_seconds()
    if delta < 60:
        return f"{int(delta)} sec ago"
    if delta < 3600:
        return f"{int(delta // 60)} min ago"
    if delta < 86400:
        return f"{int(delta // 3600)} hr ago"
    return f"{int(delta // 86400)} d ago"


def _tier(value, good_above=None, warn_above=None, bad_above=None,
          good_below=None, warn_below=None, bad_below=None):
    """Returns CSS class: 'good' / 'warn' / 'bad' / ''."""
    if value is None:
        return ""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return ""
    if bad_above is not None and v >= bad_above:
        return "bad"
    if warn_above is not None and v >= warn_above:
        return "warn"
    if good_above is not None and v >= good_above:
        return "good"
    if bad_below is not None and v <= bad_below:
        return "bad"
    if warn_below is not None and v <= warn_below:
        return "warn"
    if good_below is not None and v <= good_below:
        return "good"
    return ""


def _live_panel_empty():
    """Fallback when enrichment unavailable. Page will also be noindex'd."""
    return {
        "{{LIVE_FETCHED_AGO}}":     "—",
        "{{LIVE_FETCHED_UTC}}":     "—",
        "{{POOL_DEPTH_USD}}":       "—",
        "{{POOL_TIER}}":            "",
        "{{MARKET_CAP_USD}}":       "—",
        "{{VOLUME_24H_USD}}":       "—",
        "{{VOLUME_TIER}}":          "",
        "{{PAIR_AGE}}":             "—",
        "{{AGE_TIER}}":             "",
        "{{HOLDER_CONCENTRATION}}": "—",
        "{{HOLDER_TIER}}":          "",
        "{{LP_LOCK_STATUS}}":       "—",
        "{{LP_TIER}}":              "",
        "{{REFERENCE_CONTEXT}}":    "Live data unavailable",
    }


def build_live_panel_fields(enrichment):
    """Map engine enrichmentData -> template {{LIVE_*}} placeholders.

    Accepts the same enrichmentData shape produced by resolveKeywordEnrichment
    in riskEngine.js. Safe to call with None.
    """
    if not enrichment:
        return _live_panel_empty()

    data = enrichment.get("data") or {}
    tier = enrichment.get("tier") or data.get("tier") or "none"
    fetched_at = data.get("fetchedAt") or data.get("fetched_at")

    if tier == "token":
        pool       = data.get("poolDepthUsd")
        volume     = data.get("volume24hUsd")
        age_days   = data.get("ageDays")
        holders    = data.get("topHolderPct")  # 0-100
        lp_locked  = data.get("lpLocked")  # bool

        lp_status = "Locked" if lp_locked else "Unlocked"
        lp_class  = "good" if lp_locked else "bad"

        ref_line = (
            f"Sample reference: {data.get('refSampleSize', '—')} top-liquidity tokens "
            f"&middot; median pool {_fmt_usd(data.get('refMedianPoolUsd'))} "
            f"&middot; median pair age {_fmt_age(data.get('refMedianAgeDays'))}"
        )

        return {
            "{{LIVE_FETCHED_AGO}}":     _ago(fetched_at),
            "{{LIVE_FETCHED_UTC}}":     (str(fetched_at) or "")[:16].replace("T", " ") + " UTC",
            "{{POOL_DEPTH_USD}}":       _fmt_usd(pool),
            "{{POOL_TIER}}":            _tier(pool, good_above=100_000, warn_below=50_000, bad_below=10_000),
            "{{MARKET_CAP_USD}}":       _fmt_usd(data.get("marketCapUsd")),
            "{{VOLUME_24H_USD}}":       _fmt_usd(volume),
            "{{VOLUME_TIER}}":          _tier(volume, good_above=100_000, warn_below=20_000, bad_below=5_000),
            "{{PAIR_AGE}}":             _fmt_age(age_days),
            "{{AGE_TIER}}":             _tier(age_days, good_above=90, warn_below=14, bad_below=3),
            "{{HOLDER_CONCENTRATION}}": _fmt_pct(holders),
            "{{HOLDER_TIER}}":          _tier(holders, bad_above=60, warn_above=40, good_below=25),
            "{{LP_LOCK_STATUS}}":       lp_status,
            "{{LP_TIER}}":              lp_class,
            "{{REFERENCE_CONTEXT}}":    ref_line,
        }

    if tier in ("category", "anchor"):
        sample = data.get("sampleSize") or "—"
        cat = data.get("category", "top-liquidity")
        return {
            "{{LIVE_FETCHED_AGO}}":     _ago(fetched_at),
            "{{LIVE_FETCHED_UTC}}":     (str(fetched_at) or "")[:16].replace("T", " ") + " UTC",
            "{{POOL_DEPTH_USD}}":       _fmt_usd(data.get("medianPoolDepthUsd")) + " (median)",
            "{{POOL_TIER}}":            "",
            "{{MARKET_CAP_USD}}":       _fmt_usd(data.get("medianMarketCapUsd")) + " (median)",
            "{{VOLUME_24H_USD}}":       _fmt_usd(data.get("medianVolume24hUsd")) + " (median)",
            "{{VOLUME_TIER}}":          "",
            "{{PAIR_AGE}}":             _fmt_age(data.get("medianAgeDays")) + " (median)",
            "{{AGE_TIER}}":             "",
            "{{HOLDER_CONCENTRATION}}": "Category view",
            "{{HOLDER_TIER}}":          "",
            "{{LP_LOCK_STATUS}}":       "Category view",
            "{{LP_TIER}}":              "",
            "{{REFERENCE_CONTEXT}}":    f"Reference set: {sample} top-liquidity tokens in {cat} category",
        }

    return _live_panel_empty()


def merge_live_fields(replacements, engine_result):
    """Merge live-panel fields into the replacements dict and set robots meta.

    Call this just before the template string is .replace()d with replacements.
    The template's <meta name="robots"> needs to be {{ROBOTS}} for the
    noindex gate to take effect (see comment at bottom of file).

    Noindex policy (conservative):
      - tier == "none" (engine fetched and got nothing) -> noindex,follow
      - enrichment field absent entirely (engine doesn't pass it through yet)
        -> default index. The live panel shows '—' placeholders until the
        engine begins exposing enrichmentData. Existing pages keep indexing.
      - tier == "token"/"category"/"anchor" -> index (real data present)
    """
    if not isinstance(engine_result, dict):
        engine_result = {}

    enrichment = (
        engine_result.get("enrichmentData")
        or engine_result.get("meta", {}).get("enrichmentData")
    )
    replacements.update(build_live_panel_fields(enrichment))

    # Only noindex on an EXPLICIT tier=none signal. Missing field = default index.
    if enrichment and enrichment.get("tier") == "none":
        replacements["{{ROBOTS}}"] = "noindex,follow"
    else:
        replacements["{{ROBOTS}}"] = (
            "index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1"
        )

    return replacements


# =========================================================================
# REQUIRED TEMPLATE EDIT FOR THE NOINDEX GATE TO WORK
# =========================================================================
# In token-risk-template-a.html, change:
#     <meta name="robots" content="index,follow,max-snippet:-1,...">
# to:
#     <meta name="robots" content="{{ROBOTS}}">
#
# (The new placeholder is filled by merge_live_fields() above.)
# =========================================================================
 