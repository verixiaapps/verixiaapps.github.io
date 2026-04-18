import os
import re
import html
from pathlib import Path
from typing import Dict, List
HUB_FILE_PATH = os.getenv("HUB_FILE_PATH", "token-risk/all/index.html").strip()
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"
ROOT_FOLDER = "token-risk"
URL_PREFIX = "/token-risk/"
AUTO_START = "<!-- AUTO_HUB_SECTIONS_START -->"
AUTO_END = "<!-- AUTO_HUB_SECTIONS_END -->"
EXCLUDED_SLUGS = {
    "",
    "all",
    "hub",
    "hubs",
}
EXCLUDED_PATH_PARTS = {
    "/all/",
    "/hub/",
    "/hubs/",
}
def escape_text(text: str) -> str:
    return html.escape(str(text), quote=False)
def normalize_path(path: str) -> str:
    return str(path).replace("\\", "/").strip()
def slug_to_title(slug: str) -> str:
    text = slug.strip().strip("/")
    if not text:
        return "Untitled Page"
    words = text.split("-")
    special = {
        "token": "Token",
        "risk": "Risk",
        "liquidity": "Liquidity",
        "volume": "Volume",
        "pair": "Pair",
        "age": "Age",
        "market": "Market",
        "cap": "Cap",
        "fdv": "FDV",
        "buyers": "Buyers",
        "sellers": "Sellers",
        "slippage": "Slippage",
        "price": "Price",
        "action": "Action",
        "change": "Change",
        "rug": "Rug",
        "honeypot": "Honeypot",
        "safe": "Safe",
        "legit": "Legit",
        "risky": "Risky",
        "buy": "Buy",
        "entry": "Entry",
        "exit": "Exit",
        "solana": "Solana",
        "ethereum": "Ethereum",
        "eth": "ETH",
        "base": "Base",
        "bsc": "BSC",
        "arbitrum": "Arbitrum",
        "polygon": "Polygon",
        "avalanche": "Avalanche",
        "blast": "Blast",
        "sui": "Sui",
        "ton": "TON",
        "tron": "Tron",
        "bitcoin": "Bitcoin",
        "crypto": "Crypto",
        "coin": "Coin",
        "meme": "Meme",
        "memecoin": "Memecoin",
        "dexscreener": "Dexscreener",
        "pancakeswap": "PancakeSwap",
        "uniswap": "Uniswap",
        "raydium": "Raydium",
        "jupiter": "Jupiter",
        "metamask": "MetaMask",
        "phantom": "Phantom",
        "trust": "Trust",
        "wallet": "Wallet",
        "cto": "CTO",
    }
    lower_words = {
        "a", "an", "and", "or", "the", "to", "for", "of", "in", "on", "from", "with", "vs"
    }
    out: List[str] = []
    for i, word in enumerate(words):
        lower = word.lower()
        if lower in special:
            out.append(special[lower])
        elif i > 0 and lower in lower_words:
            out.append(lower)
        else:
            out.append(lower.capitalize())
    return " ".join(out).strip()
def extract_slug_from_file(file_path: Path, root_folder: str) -> str:
    relative = normalize_path(str(file_path.relative_to(root_folder)))
    if relative == "index.html":
        return ""
    if not relative.endswith("/index.html"):
        raise ValueError(f"Unexpected page path: {file_path}")
    return relative[:-11].strip("/")
def extract_title_from_html(content: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", content, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()
def clean_title(title: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", title).strip())
def choose_display_title(file_path: Path, slug: str) -> str:
    try:
        content = file_path.read_text(encoding="utf-8")
        html_title = clean_title(extract_title_from_html(content))
        if html_title:
            return html_title
    except Exception:
        pass
    return slug_to_title(slug)
def normalize_url_prefix(url_prefix: str) -> str:
    prefix = "/" + url_prefix.strip("/") + "/"
    return prefix if prefix != "//" else "/"
def get_hub_slug_from_path(hub_path: Path) -> str:
    normalized = normalize_path(str(hub_path))
    if not normalized.endswith("/index.html") and normalized != "index.html":
        raise ValueError(f"HUB_FILE_PATH must point to an index.html file: {normalized}")
    relative = normalized[:-10].strip("/")
    return relative
def build_public_url(site_base: str, url_path: str) -> str:
    clean_path = url_path.strip("/")
    if not clean_path:
        return f"{site_base.rstrip('/')}/"
    return f"{site_base.rstrip('/')}/{clean_path}/"
def should_skip_slug(slug: str, normalized_path: str, hub_slug: str) -> bool:
    if not slug:
        return True
    slug_lower = slug.lower().strip("/")
    if slug_lower in EXCLUDED_SLUGS:
        return True
    if hub_slug and slug_lower == hub_slug.lower().strip("/"):
        return True
    if normalized_path.endswith("/token-risk/index.html"):
        return True
    for part in EXCLUDED_PATH_PARTS:
        if part in normalized_path:
            return True
    return False
def discover_pages(root_folder: str, url_prefix: str, hub_slug: str) -> List[Dict[str, str]]:
    folder = Path(root_folder)
    if not folder.exists():
        return []
    pages: List[Dict[str, str]] = []
    normalized_prefix = normalize_url_prefix(url_prefix)
    for file_path in sorted(folder.rglob("index.html")):
        if not file_path.is_file():
            continue
        normalized = normalize_path(str(file_path))
        try:
            slug = extract_slug_from_file(file_path, root_folder)
        except ValueError:
            continue
        if should_skip_slug(slug, normalized, hub_slug):
            continue
        href = f"{normalized_prefix}{slug}/"
        title = choose_display_title(file_path, slug)
        pages.append(
            {
                "title": title,
                "href": href,
                "slug": slug,
                "sort_key": slug.lower(),
            }
        )
    pages.sort(key=lambda x: x["sort_key"])
    return pages
def build_section_html(section_title: str, pages: List[Dict[str, str]], section_id: str) -> str:
    count_text = f"{len(pages)} page" if len(pages) == 1 else f"{len(pages)} pages"
    if pages:
        items = "\n".join(
            f'          <li><a href="{escape_text(page["href"])}">{escape_text(page["title"])}</a></li>'
            for page in pages
        )
    else:
        items = "          <li>No token risk pages found yet.</li>"
    return f"""      <div class="hub-section-card" id="{escape_text(section_id)}">
        <div class="hub-section-top">
          <div class="hub-section-kicker">Auto grouped section</div>
          <h3>{escape_text(section_title)}</h3>
          <div class="hub-count-pill">{escape_text(count_text)}</div>
        </div>
        <ul class="related-links">
{items}
        </ul>
      </div>"""
def build_auto_sections(hub_slug: str) -> str:
    pages = discover_pages(ROOT_FOLDER, URL_PREFIX, hub_slug)
    total_pages = len(pages)
    summary_block = f"""      <div class="content-bridge">
        <div class="bridge-kicker">Live token risk overview</div>
        This hub pulls in published token risk pages from the token-risk folder so visitors can browse liquidity, volume, FDV, pair age, rug, honeypot, safety, buy-intent, and chain-specific topics from one premium index page.
        <div class="hub-stats-row">
          <div class="hub-stat-card">
            <div class="hub-stat-label">Pages linked</div>
            <div class="hub-stat-value">{total_pages}</div>
          </div>
          <div class="hub-stat-card">
            <div class="hub-stat-label">Folder covered</div>
            <div class="hub-stat-value">1</div>
          </div>
          <div class="hub-stat-card">
            <div class="hub-stat-label">Refresh mode</div>
            <div class="hub-stat-value">Auto</div>
          </div>
        </div>
      </div>"""
    grid_open = '      <div class="hub-grid">'
    grid_close = "      </div>"
    section_block = build_section_html(
        section_title="Token Risk Pages",
        pages=pages,
        section_id="auto-token-risk-pages",
    )
    return "\n".join([summary_block, grid_open, section_block, grid_close])
def build_starter_hub_html(canonical_url: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>All Token Risk Pages | Token Risk</title>
<meta name="description" content="Browse all token risk pages. Review liquidity, volume, FDV, pair age, rug pull, honeypot, and token safety topics from one premium hub.">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{escape_text(canonical_url)}">
<meta property="og:title" content="All Token Risk Pages | Token Risk">
<meta property="og:description" content="Browse all token risk pages. Review liquidity, volume, FDV, pair age, rug pull, honeypot, and token safety topics from one premium hub.">
<meta property="og:type" content="website">
<meta property="og:url" content="{escape_text(canonical_url)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="All Token Risk Pages | Token Risk">
<meta name="twitter:description" content="Browse all token risk pages. Review liquidity, volume, FDV, pair age, rug pull, honeypot, and token safety topics from one premium hub.">
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"CollectionPage",
  "name":"All Token Risk Pages | Token Risk",
  "description":"Browse all token risk pages. Review liquidity, volume, FDV, pair age, rug pull, honeypot, and token safety topics from one premium hub.",
  "url":"{escape_text(canonical_url)}"
}}
</script>
<style>
:root{{
--bg:#06101b;
--bg-2:#0a1324;
--bg-3:#0f1b31;
--bg-4:#132341;
--surface:rgba(255,255,255,.05);
--surface-2:rgba(255,255,255,.07);
--surface-3:rgba(255,255,255,.10);
--ink:#e9f1ff;
--ink-strong:#ffffff;
--muted:#a7b7d3;
--cyan:#66d9ef;
--cyan-2:#28bfd9;
--violet:#8b78f2;
--emerald:#18b67f;
--shadow-xl:0 32px 90px rgba(2,6,23,.46);
--shadow-lg:0 22px 56px rgba(2,6,23,.34);
--shadow-md:0 14px 34px rgba(2,6,23,.24);
--shadow-sm:0 8px 20px rgba(2,6,23,.16);
--shadow-xs:0 4px 12px rgba(2,6,23,.10);
--radius-xl:30px;
--radius-lg:24px;
--radius-md:20px;
}}
*{{
box-sizing:border-box;
}}
html{{
-webkit-text-size-adjust:100%;
scroll-behavior:smooth;
}}
body{{
font-family:Inter,system-ui,-apple-system,Arial,sans-serif;
margin:0;
padding-top:90px;
color:var(--ink);
line-height:1.6;
background:
radial-gradient(circle at 14% 8%, rgba(102,217,239,.10), transparent 22%),
radial-gradient(circle at 84% 0%, rgba(139,120,242,.14), transparent 26%),
radial-gradient(circle at 50% 100%, rgba(24,182,127,.05), transparent 24%),
linear-gradient(180deg,var(--bg) 0%, var(--bg-2) 34%, var(--bg-3) 70%, var(--bg-4) 100%);
}}
a{{
color:#9cecff;
text-decoration:none;
}}
a:hover{{
text-decoration:none;
}}
@supports (padding:max(0px)) {{
  body{{
    padding-left:max(0px, env(safe-area-inset-left));
    padding-right:max(0px, env(safe-area-inset-right));
  }}
}}
.top-bar{{
position:fixed;
top:0;
left:0;
width:100%;
display:flex;
justify-content:space-between;
align-items:center;
padding:10px 16px;
z-index:1000;
pointer-events:none;
}}
.top-actions{{
pointer-events:auto;
display:flex;
align-items:center;
gap:10px;
margin-right:20px;
}}
.logo{{
pointer-events:auto;
display:inline-flex;
align-items:center;
gap:10px;
font-size:14px;
font-weight:900;
color:#eef6ff;
margin-left:8px;
padding:11px 15px;
border-radius:999px;
letter-spacing:-.01em;
background:rgba(10,18,35,.62);
border:1px solid rgba(255,255,255,.10);
backdrop-filter:blur(14px);
box-shadow:var(--shadow-sm);
text-decoration:none;
}}
.logo:hover{{
border-color:rgba(255,255,255,.16);
background:rgba(12,21,39,.72);
}}
.logo-dot{{
width:10px;
height:10px;
border-radius:50%;
background:linear-gradient(180deg,var(--cyan) 0%,var(--violet) 100%);
box-shadow:0 0 0 4px rgba(139,120,242,.12);
flex:0 0 10px;
}}
.app-top{{
display:inline-flex;
align-items:center;
justify-content:center;
padding:11px 14px;
font-size:14px;
border-radius:16px;
font-weight:900;
color:#fff;
border:1px solid rgba(255,255,255,.11);
white-space:nowrap;
background:linear-gradient(180deg,rgba(255,255,255,.12) 0%,rgba(255,255,255,.06) 100%);
backdrop-filter:blur(10px);
box-shadow:var(--shadow-xs);
transition:transform .18s ease, border-color .18s ease, background .18s ease, box-shadow .18s ease;
}}
.app-top:hover{{
transform:translateY(-1px);
border-color:rgba(255,255,255,.18);
background:linear-gradient(180deg,rgba(255,255,255,.16) 0%,rgba(255,255,255,.07) 100%);
box-shadow:0 10px 24px rgba(2,6,23,.22);
}}
.page-shell{{
max-width:1120px;
margin:0 auto;
padding:0 14px 40px;
}}
.hero{{
position:relative;
padding:18px 8px 24px;
max-width:980px;
margin:0 auto 14px;
text-align:center;
}}
.hero-badge-row{{
display:flex;
flex-wrap:wrap;
justify-content:center;
gap:10px;
margin-bottom:16px;
}}
.hero-badge{{
display:inline-flex;
align-items:center;
justify-content:center;
gap:8px;
padding:9px 13px;
border-radius:999px;
font-size:12px;
font-weight:900;
letter-spacing:.01em;
color:#d9e8ff;
background:rgba(255,255,255,.07);
border:1px solid rgba(255,255,255,.09);
backdrop-filter:blur(10px);
box-shadow:var(--shadow-xs);
}}
.hero h1{{
margin:0;
font-size:54px;
line-height:1.02;
letter-spacing:-.05em;
font-weight:950;
color:var(--ink-strong);
text-wrap:balance;
}}
.hero p{{
margin:14px auto 0;
max-width:820px;
font-size:19px;
color:#c8d7ec;
text-wrap:balance;
}}
.hero-trust{{
margin-top:18px;
display:flex;
flex-wrap:wrap;
justify-content:center;
gap:10px;
}}
.hero-trust-chip{{
display:inline-flex;
align-items:center;
justify-content:center;
padding:10px 14px;
border-radius:999px;
font-size:13px;
font-weight:900;
color:#dde9fb;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
box-shadow:var(--shadow-xs);
}}
.content-section{{
max-width:1080px;
margin:auto;
padding:24px;
border-radius:var(--radius-xl);
position:relative;
overflow:hidden;
border:1px solid rgba(255,255,255,.10);
background:
linear-gradient(180deg, rgba(17,28,51,.95) 0%, rgba(11,19,36,.985) 100%);
box-shadow:var(--shadow-xl);
}}
.content-section::before{{
content:"";
position:absolute;
top:-120px;
right:-90px;
width:260px;
height:260px;
border-radius:50%;
background:radial-gradient(circle, rgba(102,217,239,.11), transparent 65%);
pointer-events:none;
}}
.content-section::after{{
content:"";
position:absolute;
left:-80px;
bottom:-120px;
width:220px;
height:220px;
border-radius:50%;
background:radial-gradient(circle, rgba(139,120,242,.08), transparent 68%);
pointer-events:none;
}}
.content-section > *{{
position:relative;
z-index:1;
}}
.inline-info-card{{
margin:0 0 22px;
padding:20px;
border-radius:24px;
background:
linear-gradient(135deg, rgba(91,140,255,.10) 0%, rgba(139,120,242,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.06) 0%, rgba(255,255,255,.04) 100%);
border:1px solid rgba(255,255,255,.10);
box-shadow:var(--shadow-md);
}}
.content-section h2,
.content-section h3{{
margin:0 0 14px;
color:#fff;
line-height:1.08;
letter-spacing:-.035em;
font-weight:900;
text-wrap:balance;
}}
.content-section h2{{
font-size:40px;
}}
.content-section h3{{
font-size:28px;
margin:0;
}}
.content-bridge{{
margin:0 0 24px;
padding:22px;
border-radius:24px;
background:
linear-gradient(135deg, rgba(102,217,239,.08) 0%, rgba(139,120,242,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.045) 100%);
border:1px solid rgba(255,255,255,.10);
box-shadow:var(--shadow-md);
font-size:15px;
color:#d7e4f8;
font-weight:800;
line-height:1.72;
}}
.bridge-kicker{{
margin-bottom:8px;
font-size:12px;
font-weight:900;
letter-spacing:.08em;
text-transform:uppercase;
color:#99eaff;
}}
.hub-stats-row{{
display:grid;
grid-template-columns:repeat(3,minmax(0,1fr));
gap:12px;
margin-top:16px;
}}
.hub-stat-card{{
padding:16px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
box-shadow:var(--shadow-xs);
}}
.hub-stat-label{{
font-size:12px;
font-weight:900;
letter-spacing:.04em;
text-transform:uppercase;
color:#a7b7d3;
}}
.hub-stat-value{{
margin-top:6px;
font-size:28px;
font-weight:950;
line-height:1;
color:#ffffff;
}}
.hub-grid{{
display:grid;
grid-template-columns:repeat(1,minmax(0,1fr));
gap:18px;
margin-top:4px;
}}
.hub-section-card{{
padding:20px;
border-radius:24px;
background:
linear-gradient(180deg, rgba(255,255,255,.075) 0%, rgba(255,255,255,.04) 100%);
border:1px solid rgba(255,255,255,.10);
box-shadow:var(--shadow-md);
transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease, background .18s ease;
}}
.hub-section-card:hover{{
transform:translateY(-4px);
border-color:rgba(255,255,255,.18);
box-shadow:0 26px 60px rgba(2,6,23,.38);
background:
linear-gradient(180deg, rgba(255,255,255,.09) 0%, rgba(255,255,255,.045) 100%);
}}
.hub-section-top{{
margin-bottom:14px;
padding-bottom:12px;
border-bottom:1px solid rgba(255,255,255,.08);
}}
.hub-section-kicker{{
margin-bottom:8px;
font-size:11px;
font-weight:900;
letter-spacing:.08em;
text-transform:uppercase;
color:#9cecff;
}}
.hub-count-pill{{
display:inline-flex;
align-items:center;
justify-content:center;
padding:8px 12px;
border-radius:999px;
font-size:12px;
font-weight:900;
color:#dde9fb;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
box-shadow:var(--shadow-xs);
}}
.related-links{{
margin:0;
padding-left:20px;
padding-right:6px;
max-height:520px;
overflow:auto;
scrollbar-width:thin;
scrollbar-color:rgba(156,236,255,.28) transparent;
}}
.related-links::-webkit-scrollbar{{
width:8px;
}}
.related-links::-webkit-scrollbar-track{{
background:transparent;
}}
.related-links::-webkit-scrollbar-thumb{{
background:rgba(156,236,255,.22);
border-radius:999px;
}}
.related-links li{{
margin-bottom:12px;
}}
.related-links a{{
color:#9cecff;
font-weight:800;
line-height:1.5;
transition:color .18s ease, opacity .18s ease;
}}
.related-links a:hover{{
color:#ffffff;
opacity:.98;
}}
.content-close{{
margin-top:28px;
padding:20px;
border-radius:24px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
font-size:15px;
font-weight:800;
color:#d7e4f8;
line-height:1.72;
}}
.footer{{
text-align:center;
margin-top:72px;
padding:40px 20px;
color:#9fb0cc;
font-size:14px;
line-height:1.75;
text-wrap:balance;
}}
.footer a{{
color:#9cecff;
font-weight:700;
}}
@media (max-width:900px){{
.hub-stats-row{{grid-template-columns:1fr;}}
.related-links{{max-height:none;overflow:visible;padding-right:0;}}
}}
@media (max-width:640px){{
body{{padding-top:84px;}}
.hero{{padding:14px 6px 18px;}}
.hero h1{{font-size:34px;}}
.hero p{{margin-top:10px;font-size:17px;}}
.content-section{{margin-left:12px;margin-right:12px;padding:18px;border-radius:24px;}}
.top-bar{{padding:10px 10px;}}
.top-actions{{gap:8px;margin-right:0;}}
.logo{{font-size:13px;margin-left:2px;padding:9px 12px;}}
.app-top{{font-size:13px;padding:8px 10px;}}
.content-section h2{{font-size:30px;line-height:1.12;}}
.content-section h3{{font-size:24px;}}
.inline-info-card{{padding:14px 15px;}}
.content-close{{padding:15px;}}
.hub-section-card{{padding:16px;}}
.hub-stat-value{{font-size:24px;}}
}}
</style>
</head>
<body>
<div class="top-bar">
  <a class="logo" href="https://verixiaapps.com/token-risk/">
    <span class="logo-dot"></span>
    <span>Token Risk</span>
  </a>
  <div class="top-actions">
    <a class="app-top" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">📱 Get App</a>
  </div>
</div>
<div class="page-shell">
  <div class="hero">
    <div class="hero-badge-row">
      <div class="hero-badge">Premium token hub</div>
      <div class="hero-badge">Single-folder page discovery</div>
      <div class="hero-badge">Built for indexing and reuse</div>
    </div>
    <h1>Browse All Token Risk Pages</h1>
    <p>Explore token risk pages to find liquidity, volume, FDV, pair age, rug pull, honeypot, safety, buy-intent, and chain-specific topics faster.</p>
    <div class="hero-trust">
      <div class="hero-trust-chip">Find exact token pages</div>
      <div class="hero-trust-chip">Browse from one hub</div>
      <div class="hero-trust-chip">Updated automatically</div>
    </div>
  </div>
  <section class="content-section">
    <div class="inline-info-card">
      <h2 style="margin:0 0 8px;">Token Risk Hub</h2>
      <div style="font-size:15px;color:#d7e4f8;font-weight:800;line-height:1.68;">
        This page brings together published token risk pages from the token-risk folder so visitors can navigate across the full warning library from one clean premium location.
      </div>
    </div>
{AUTO_START}
{AUTO_END}
    <div class="content-close">
      Token setups often repeat the same underlying problems even when the narrative changes. This hub helps users quickly find exact token risk pages before they buy, swap, or trust a setup too quickly.
    </div>
  </section>
  <footer class="footer">
    <div>
      By using this website you agree to our
      <a href="https://verixiaapps.com/website-policies/scam-check/" target="_blank" rel="noopener noreferrer">Terms and Privacy Policy</a>.
    </div>
    <div style="margin-top:10px">
      Token Risk © 2026 • Token risk detection and analysis
    </div>
  </footer>
</div>
</body>
</html>
"""
def ensure_hub_parents_exist(hub_path: Path) -> None:
    parent = hub_path.parent
    if parent.exists():
        return
    if DRY_RUN:
        print(f"WOULD CREATE DIRECTORY: {parent}")
        return
    parent.mkdir(parents=True, exist_ok=True)
    print(f"CREATED DIRECTORY: {parent}")
def write_text_if_needed(path: Path, content: str) -> None:
    if DRY_RUN:
        print(f"WOULD WRITE FILE: {path}")
        return
    path.write_text(content, encoding="utf-8", newline="")
    print(f"WROTE FILE: {path}")
def load_or_build_hub_html(hub_path: Path, canonical_url: str) -> str:
    if hub_path.exists():
        return hub_path.read_text(encoding="utf-8")
    print(f"HUB FILE NOT FOUND, BUILDING STARTER SHELL: {hub_path}")
    return build_starter_hub_html(canonical_url)
def replace_auto_section(content: str, new_inner_html: str) -> str:
    pattern = re.compile(
        rf"({re.escape(AUTO_START)})(.*)({re.escape(AUTO_END)})",
        flags=re.DOTALL,
    )
    replacement = f"{AUTO_START}\n{new_inner_html}\n{AUTO_END}"
    updated, count = pattern.subn(replacement, content, count=1)
    if count == 0:
        raise ValueError(
            f"Hub file must contain markers:\n{AUTO_START}\n...\n{AUTO_END}"
        )
    return updated
def process_hub() -> bool:
    hub_path = Path(HUB_FILE_PATH)
    hub_slug = get_hub_slug_from_path(hub_path)
    canonical_url = build_public_url("https://verixiaapps.com", hub_slug)
    ensure_hub_parents_exist(hub_path)
    original = load_or_build_hub_html(hub_path, canonical_url)
    auto_sections = build_auto_sections(hub_slug)
    updated = replace_auto_section(original, auto_sections)
    if updated == original:
        print("NO CHANGE: hub already up to date")
        return False
    write_text_if_needed(hub_path, updated)
    print(f"UPDATED HUB CONTENT: {HUB_FILE_PATH}")
    return True
def main() -> None:
    print(f"DRY_RUN={DRY_RUN}")
    print(f"HUB_FILE_PATH={HUB_FILE_PATH}")
    changed = process_hub()
    if changed:
        print("Hub refresh complete.")
    else:
        print("Hub refresh complete. Nothing changed.")
if __name__ == "__main__":
    main()