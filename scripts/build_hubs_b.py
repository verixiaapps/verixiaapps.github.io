import os
from collections import defaultdict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "generated_keywords_b.txt")
SLUGS_FILE = os.path.join(BASE_DIR, "data", "generated_slugs_b.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "scam-check-now-b", "hubs")

SITE = "https://verixiaapps.com"
PAGE_PREFIX = "/scam-check-now-b"
HUB_PREFIX = "/scam-check-now-b/hubs"

MAX_LINKS_PER_HUB = 80

HUB_RULES = {
    "job-scams": ["job", "hiring", "recruiter", "interview", "offer", "onboarding"],
    "crypto-scams": ["crypto", "bitcoin", "wallet", "ethereum", "eth", "nft", "airdrop", "token"],
    "email-scams": ["email", "mail", "inbox"],
    "text-scams": ["text", "sms", "message"],
    "brand-scams": ["paypal", "amazon", "apple", "google", "bank", "venmo", "zelle", "cash app"],
    "payment-scams": ["payment", "invoice", "transfer", "fee", "refund"],
}

HUB_INTROS = {
    "job-scams": "Job scams often use fake recruiters, interview requests, remote work promises, and onboarding pressure to push people toward fees, personal information, or rushed next steps before anything is verified.",
    "crypto-scams": "Crypto scams often use fake investment claims, wallet pressure, airdrops, support impersonation, and urgent transfer requests to trigger risky actions before the target slows down.",
    "email-scams": "Email scams often rely on fake account alerts, invoice tricks, phishing links, impersonation, and urgent warnings to push clicks, logins, replies, or payments.",
    "text-scams": "Text scams often create urgency fast through delivery issues, account warnings, payment requests, unknown numbers, or suspicious links that try to push quick action.",
    "brand-scams": "Brand scams often copy familiar names, logos, account alerts, refund notices, and support language to build trust before moving the target toward a link, payment, or login step.",
    "payment-scams": "Payment scams often use fake invoices, transfer pressure, refund stories, fees, or account issues to push people into sending money before they verify the situation independently.",
    "general-scams": "General scam patterns often show the same core behavior: urgency, impersonation, suspicious links, pressure, and requests for money or information before independent verification.",
}

HUB_SUBHEADS = {
    "job-scams": "Review job-related scam patterns, compare similar pages, and check suspicious recruiter messages before you reply, apply, or share personal details.",
    "crypto-scams": "Review crypto scam patterns, compare related checks, and slow down before you connect a wallet, approve anything, or send funds.",
    "email-scams": "Review suspicious email patterns, compare related checks, and inspect messages before you click links, log in, or reply.",
    "text-scams": "Review suspicious text patterns, compare similar scam pages, and check risky SMS messages before you tap, call back, or send money.",
    "brand-scams": "Review brand impersonation patterns, compare related scam checks, and verify suspicious alerts before you trust the message.",
    "payment-scams": "Review payment scam patterns, compare related checks, and verify suspicious requests before you transfer money or approve charges.",
    "general-scams": "Review common scam patterns, compare related scam checks, and verify suspicious messages before you click, reply, or send money.",
}

SECTION_KICKERS = {
    "job-scams": "Hiring risk hub",
    "crypto-scams": "Crypto risk hub",
    "email-scams": "Email risk hub",
    "text-scams": "Text risk hub",
    "brand-scams": "Brand risk hub",
    "payment-scams": "Payment risk hub",
    "general-scams": "Scam category hub",
}

BADGES = {
    "job-scams": ["Job scam hub", "Recruiter checks", "Built for repeat use"],
    "crypto-scams": ["Crypto scam hub", "Wallet safety", "Built for repeat use"],
    "email-scams": ["Email scam hub", "Phishing checks", "Built for repeat use"],
    "text-scams": ["Text scam hub", "SMS warning page", "Built for repeat use"],
    "brand-scams": ["Brand scam hub", "Impersonation checks", "Built for repeat use"],
    "payment-scams": ["Payment scam hub", "Transfer warning page", "Built for repeat use"],
    "general-scams": ["Scam category hub", "Internal linking support", "Built for repeat use"],
}

HUB_WARNINGS = {
    "job-scams": [
        "Offers that move unusually fast with little screening or verification",
        "Requests for money, equipment purchases, or personal details too early",
        "Pressure to leave trusted platforms and continue on private apps",
    ],
    "crypto-scams": [
        "Urgent wallet actions, transfer requests, or support messages",
        "Promises of recovery, guaranteed gains, or exclusive token access",
        "Requests for seed phrases, approvals, or private account details",
    ],
    "email-scams": [
        "Unexpected account alerts, urgent warnings, or fake invoice notices",
        "Links that push fast login steps before independent verification",
        "Messages that look official but contain mismatched sender details",
    ],
    "text-scams": [
        "Unexpected messages with urgent links, payment requests, or warnings",
        "Unknown numbers trying to create panic, curiosity, or fast replies",
        "Texts that push you to act before opening the official app or site yourself",
    ],
    "brand-scams": [
        "Messages that copy trusted brands but pressure quick action",
        "Fake support, refunds, delivery alerts, or account notices",
        "Links or instructions that do not match the official brand workflow",
    ],
    "payment-scams": [
        "Unexpected invoice, refund, fee, or transfer pressure",
        "Messages that make account or payment problems feel urgent",
        "Requests to send money before checking the real account directly",
    ],
    "general-scams": [
        "Urgency before proof",
        "Suspicious links or fake support paths",
        "Requests for money, codes, logins, or personal details",
    ],
}

HUB_STEPS = {
    "job-scams": [
        "Verify the company and recruiter independently.",
        "Do not pay for equipment, onboarding, or background checks upfront.",
        "Slow down if the offer feels unusually fast or too easy.",
    ],
    "crypto-scams": [
        "Check the project, wallet request, and domain independently.",
        "Never share seed phrases, private keys, or recovery codes.",
        "Pause before approving transfers, wallet connections, or support requests.",
    ],
    "email-scams": [
        "Open the official website or app directly instead of using message links.",
        "Check whether the alert exists in your real account.",
        "Do not reply or log in through suspicious email instructions.",
    ],
    "text-scams": [
        "Do not tap the link right away.",
        "Open the official app or site yourself and verify the claim there.",
        "Ignore pressure to reply, call back, or pay immediately.",
    ],
    "brand-scams": [
        "Verify inside the real brand website or app first.",
        "Do not trust message-only support numbers or login paths.",
        "Compare the message details to the official account activity.",
    ],
    "payment-scams": [
        "Check the real payment account or bank directly.",
        "Do not trust screenshots, refund stories, or urgent reversal claims alone.",
        "Verify before sending money, approving charges, or sharing details.",
    ],
    "general-scams": [
        "Pause before you click, reply, or send money.",
        "Go to the official site or app yourself instead of using message links.",
        "Verify independently before sharing anything sensitive.",
    ],
}


def clean_text(s):
    return str(s).strip()


def safe_html(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def pretty_title(hub_name):
    return hub_name.replace("-", " ").title()


def build_links_html(items):
    blocks = []

    for kw, slug in items:
        url = f"{SITE}{PAGE_PREFIX}/{slug}/"
        blocks.append(
            f"""
<li class="hub-link-item">
  <a class="hub-link" href="{url}">
    <span class="hub-link-title">{safe_html(kw)}</span>
    <span class="hub-link-arrow">↗</span>
  </a>
</li>
""".strip()
        )

    return "\n".join(blocks)


def build_badges_html(hub_name):
    badges = BADGES.get(hub_name, BADGES["general-scams"])
    return "\n".join(f'<div class="hero-badge">{safe_html(badge)}</div>' for badge in badges)


def build_warning_items_html(hub_name):
    items = HUB_WARNINGS.get(hub_name, HUB_WARNINGS["general-scams"])
    return "\n".join(f"<li>{safe_html(item)}</li>" for item in items)


def build_step_items_html(hub_name):
    items = HUB_STEPS.get(hub_name, HUB_STEPS["general-scams"])
    return "\n".join(f"<li>{safe_html(item)}</li>" for item in items)


def build_hub_html(hub_name, items):
    title_text = pretty_title(hub_name)
    desc_text = title_text.lower()
    intro = HUB_INTROS.get(hub_name, HUB_INTROS["general-scams"])
    subhead = HUB_SUBHEADS.get(hub_name, HUB_SUBHEADS["general-scams"])
    kicker = SECTION_KICKERS.get(hub_name, SECTION_KICKERS["general-scams"])
    badge_html = build_badges_html(hub_name)
    links_html = build_links_html(items)
    warning_items_html = build_warning_items_html(hub_name)
    step_items_html = build_step_items_html(hub_name)
    page_count = len(items)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe_html(title_text)} | Scam Check Now</title>
<meta name="description" content="Check {safe_html(desc_text)} messages, links, and offers. Identify scam risks before you click, reply, or send money.">
<link rel="canonical" href="{SITE}{HUB_PREFIX}/{hub_name}/">
<meta name="robots" content="index,follow">
<meta property="og:title" content="{safe_html(title_text)} | Scam Check Now">
<meta property="og:description" content="Check {safe_html(desc_text)} messages, links, and offers. Identify scam risks before you click, reply, or send money.">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}{HUB_PREFIX}/{hub_name}/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{safe_html(title_text)} | Scam Check Now">
<meta name="twitter:description" content="Check {safe_html(desc_text)} messages, links, and offers. Identify scam risks before you click, reply, or send money.">

<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"CollectionPage",
  "name":"{safe_html(title_text)}",
  "description":"Check {safe_html(desc_text)} messages, links, and offers. Identify scam risks before you click, reply, or send money.",
  "url":"{SITE}{HUB_PREFIX}/{hub_name}/"
}}
</script>

<style>
:root{{
--bg:#07111f;
--bg-2:#0c1728;
--bg-3:#12203a;
--surface:rgba(255,255,255,.06);
--surface-2:rgba(255,255,255,.08);
--card:#101c33;
--ink:#e8f0ff;
--ink-strong:#ffffff;
--muted:#9eb0cf;
--line:rgba(148,163,184,.20);
--cyan:#22d3ee;
--cyan-2:#06b6d4;
--violet:#8b5cf6;
--emerald:#10b981;
--shadow-xl:0 32px 90px rgba(2,6,23,.42);
--shadow-lg:0 20px 54px rgba(2,6,23,.30);
--shadow-md:0 12px 30px rgba(2,6,23,.22);
--shadow-sm:0 8px 20px rgba(2,6,23,.16);
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
line-height:1.7;
background:
radial-gradient(circle at 14% 8%, rgba(34,211,238,.16), transparent 22%),
radial-gradient(circle at 84% 0%, rgba(139,92,246,.20), transparent 28%),
radial-gradient(circle at 50% 100%, rgba(16,185,129,.08), transparent 24%),
linear-gradient(180deg,#06101b 0%, #0a1324 34%, #0e1830 100%);
}}

a{{
color:#8be9ff;
text-decoration:none;
}}

a:hover{{
text-decoration:underline;
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
background:rgba(10,18,35,.68);
border:1px solid rgba(255,255,255,.10);
backdrop-filter:blur(14px);
box-shadow:var(--shadow-sm);
text-decoration:none;
}}

.logo:hover{{
text-decoration:none;
}}

.logo-dot{{
width:10px;
height:10px;
border-radius:50%;
background:linear-gradient(180deg,var(--cyan) 0%,var(--violet) 100%);
box-shadow:0 0 0 4px rgba(139,92,246,.14);
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
border:1px solid rgba(255,255,255,.12);
white-space:nowrap;
background:linear-gradient(180deg,rgba(255,255,255,.14) 0%,rgba(255,255,255,.08) 100%);
backdrop-filter:blur(10px);
box-shadow:var(--shadow-sm);
}}

.app-top:hover{{
text-decoration:none;
}}

.checker-top{{
pointer-events:auto;
padding:11px 15px;
font-size:14px;
border-radius:16px;
font-weight:900;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
white-space:nowrap;
box-shadow:0 16px 34px rgba(34,211,238,.16);
}}

.checker-top:hover{{
text-decoration:none;
}}

.page-shell{{
max-width:980px;
margin:0 auto;
padding:0 14px 40px;
}}

.hero{{
position:relative;
padding:18px 8px 22px;
max-width:980px;
margin:0 auto 14px;
text-align:center;
}}

.hero-badge-row{{
display:flex;
flex-wrap:wrap;
justify-content:center;
gap:10px;
margin-bottom:14px;
}}

.hero-badge{{
display:inline-flex;
align-items:center;
justify-content:center;
gap:8px;
padding:9px 13px;
border-radius:999px;
font-size:13px;
font-weight:900;
color:#dbeafe;
background:rgba(255,255,255,.08);
border:1px solid rgba(255,255,255,.10);
backdrop-filter:blur(10px);
}}

.hero h1{{
margin:0;
font-size:48px;
line-height:1.02;
letter-spacing:-.05em;
font-weight:950;
color:var(--ink-strong);
text-wrap:balance;
}}

.hero p{{
margin:14px auto 0;
max-width:780px;
font-size:19px;
color:#c7d5eb;
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
color:#dce8fb;
background:rgba(255,255,255,.06);
border:1px solid rgba(255,255,255,.10);
box-shadow:var(--shadow-sm);
}}

.content-section{{
max-width:860px;
margin:auto;
padding:22px;
border-radius:30px;
position:relative;
overflow:hidden;
border:1px solid rgba(255,255,255,.10);
background:
linear-gradient(180deg, rgba(17,28,51,.94) 0%, rgba(11,19,36,.98) 100%);
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
background:radial-gradient(circle, rgba(34,211,238,.14), transparent 65%);
pointer-events:none;
}}

.content-section > *{{
position:relative;
z-index:1;
}}

.breadcrumbs{{
margin:0 0 16px;
font-size:13px;
font-weight:900;
color:#98adcf;
line-height:1.6;
}}

.breadcrumbs a{{
color:#9fdcf4;
font-weight:900;
}}

.hero-panel,
.info-box,
.warning-card,
.steps-card,
.link-card,
.meta-strip{{
background:linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
border:1px solid rgba(255,255,255,.10);
border-radius:24px;
box-shadow:var(--shadow-md);
}}

.hero-panel{{
padding:22px;
margin:0 0 18px;
background:
linear-gradient(135deg, rgba(34,211,238,.12) 0%, rgba(139,92,246,.12) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.05) 100%);
}}

.hero-panel-kicker{{
font-size:12px;
font-weight:900;
letter-spacing:.08em;
text-transform:uppercase;
color:#8be9ff;
margin-bottom:8px;
}}

.hero-panel h2{{
margin:0 0 8px;
font-size:30px;
line-height:1.08;
letter-spacing:-.03em;
color:#fff;
}}

.hero-panel p{{
margin:10px 0 0;
font-size:15px;
font-weight:800;
color:#d8e5f8;
line-height:1.75;
}}

.info-box{{
margin:0 0 22px;
padding:18px;
font-size:15px;
color:#d6e3f7;
font-weight:800;
line-height:1.7;
}}

.grid-two{{
display:grid;
grid-template-columns:repeat(2,minmax(0,1fr));
gap:16px;
margin:0 0 22px;
}}

.warning-card,
.steps-card,
.link-card{{
padding:20px;
}}

.warning-card{{
background:
linear-gradient(135deg, rgba(239,68,68,.10) 0%, rgba(139,92,246,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.steps-card{{
background:
linear-gradient(135deg, rgba(16,185,129,.10) 0%, rgba(34,211,238,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.link-card{{
background:
linear-gradient(135deg, rgba(59,130,246,.10) 0%, rgba(139,92,246,.10) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

h1,h2,h3{{
margin:0 0 14px;
color:#fff;
line-height:1.08;
letter-spacing:-.035em;
font-weight:900;
text-wrap:balance;
}}

h2{{font-size:30px;}}
h3{{font-size:22px;}}
p, li{{
font-size:17px;
color:#d7e4f8;
}}

p{{
margin:0 0 16px;
}}

ul{{
margin:0;
padding-left:22px;
}}

li{{
margin-bottom:10px;
}}

.hub-links{{
list-style:none;
padding:0;
margin:18px 0 0;
display:grid;
gap:12px;
}}

.hub-link-item{{
margin:0;
}}

.hub-link{{
display:flex;
align-items:center;
justify-content:space-between;
gap:14px;
padding:16px 18px;
border-radius:18px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
box-shadow:var(--shadow-sm);
font-weight:900;
color:#e8f4ff;
}}

.hub-link:hover{{
text-decoration:none;
transform:translateY(-1px);
background:rgba(255,255,255,.07);
}}

.hub-link-title{{
display:block;
line-height:1.5;
}}

.hub-link-arrow{{
flex:0 0 auto;
font-size:16px;
color:#8be9ff;
}}

.meta-strip{{
margin:22px 0 0;
padding:16px 18px;
font-size:14px;
font-weight:900;
color:#d8e5f8;
line-height:1.7;
}}

@media (max-width:640px){{
body{{padding-top:84px;}}
.top-bar{{padding:10px 10px;}}
.top-actions{{gap:8px;margin-right:0;}}
.logo{{font-size:13px;margin-left:2px;padding:9px 12px;}}
.app-top{{font-size:13px;padding:8px 10px;}}
.checker-top{{font-size:13px;padding:8px 10px;margin-right:0;}}
.page-shell{{padding:0 12px 34px;}}
.hero{{padding:14px 6px 18px;}}
.hero h1{{font-size:34px;}}
.hero p{{margin-top:10px;font-size:17px;}}
.content-section{{padding:18px;border-radius:24px;}}
.hero-panel h2{{font-size:24px;}}
h2{{font-size:24px;}}
h3{{font-size:20px;}}
p{{font-size:16px;}}
.grid-two{{grid-template-columns:1fr;}}
.hub-link{{padding:14px 15px;}}
}}
</style>
</head>
<body>

<div class="top-bar">
  <a class="logo" href="{SITE}/check">
    <span class="logo-dot"></span>
    <span>Scam Check Now</span>
  </a>
  <div class="top-actions">
    <a class="app-top" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">📱 Get App</a>
    <a class="checker-top" href="{SITE}/check">Check Scam</a>
  </div>
</div>

<div class="page-shell">

  <div class="hero">
    <div class="hero-badge-row">
      {badge_html}
    </div>

    <h1>{safe_html(title_text)}</h1>
    <p>{safe_html(subhead)}</p>

    <div class="hero-trust">
      <div class="hero-trust-chip">Check before you click</div>
      <div class="hero-trust-chip">Check before you reply</div>
      <div class="hero-trust-chip">Check before you send money</div>
    </div>
  </div>

  <main class="content-section">
    <div class="breadcrumbs">
      <a href="{SITE}/check">Scam Check Now</a> / <a href="{SITE}{HUB_PREFIX}/">B Hubs</a> / <span>{safe_html(title_text)}</span>
    </div>

    <div class="hero-panel">
      <div class="hero-panel-kicker">{safe_html(kicker)}</div>
      <h2>Compare scam patterns faster</h2>
      <p>{safe_html(intro)}</p>
    </div>

    <div class="info-box">
      This hub groups similar pages together so people can scan patterns faster, compare suspicious messages, and verify risky situations before they click, reply, log in, or send money.
    </div>

    <div class="grid-two">
      <section class="warning-card" aria-labelledby="warning-signs-heading">
        <h2 id="warning-signs-heading">Common Warning Signs</h2>
        <ul>
          {warning_items_html}
        </ul>
      </section>

      <section class="steps-card" aria-labelledby="what-to-do-heading">
        <h2 id="what-to-do-heading">What To Do</h2>
        <ul>
          {step_items_html}
        </ul>
      </section>
    </div>

    <section class="link-card" aria-labelledby="related-checks-heading">
      <h2 id="related-checks-heading">Related Scam Checks</h2>
      <p>This hub currently links to {page_count} related pages in this category so you can compare patterns, wording, and warning signs before taking action.</p>

      <ul class="hub-links">
        {links_html}
      </ul>
    </section>

    <div class="meta-strip">
      Review scam patterns, compare warning signs, and use the linked pages above to investigate the most relevant variations in this category.
    </div>
  </main>
</div>
</body>
</html>
"""


with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
    keywords = [clean_text(x) for x in f.readlines() if x.strip()]

with open(SLUGS_FILE, "r", encoding="utf-8") as f:
    slugs = [clean_text(x) for x in f.readlines() if x.strip()]

if len(keywords) != len(slugs):
    raise ValueError("generated_keywords_b.txt and generated_slugs_b.txt count mismatch")

pairs = list(zip(keywords, slugs))

hubs = defaultdict(list)

for kw, slug in pairs:
    lower = kw.lower()
    matched = False

    for hub, rules in HUB_RULES.items():
        if any(r in lower for r in rules):
            hubs[hub].append((kw, slug))
            matched = True
            break

    if not matched:
        hubs["general-scams"].append((kw, slug))

os.makedirs(OUTPUT_DIR, exist_ok=True)

for hub_name, items in hubs.items():
    seen = set()
    deduped = []

    for kw, slug in items:
        if slug not in seen:
            seen.add(slug)
            deduped.append((kw, slug))

    deduped = deduped[:MAX_LINKS_PER_HUB]

    html = build_hub_html(hub_name, deduped)

    hub_path = os.path.join(OUTPUT_DIR, hub_name)
    os.makedirs(hub_path, exist_ok=True)

    with open(os.path.join(hub_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

print("B hubs built successfully.")