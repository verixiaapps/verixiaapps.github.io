import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.cluster_map import CLUSTERS

KEYWORDS_FILE = "data/generated_keywords.txt"
OUTPUT_DIR = "scam-check-now"
SITE = "https://verixiaapps.com"
MAX_LINKS_PER_HUB = 50

HUB_INTROS = {
    "amazon-scams": "Amazon scams often use fake account alerts, delivery issues, gift card requests, or security warnings to pressure people into clicking links, sharing details, or sending money.",
    "paypal-scams": "PayPal scams often use fake payment alerts, invoice tricks, account warnings, or refund messages to create urgency and push people into unsafe actions.",
    "zelle-scams": "Zelle scams often rely on fake payment issues, impersonation, reversal claims, or urgent transfer requests designed to get money sent quickly.",
    "cash-app-scams": "Cash App scams often involve fake payment notices, support impersonation, giveaway tricks, or refund pressure designed to move money fast.",
    "venmo-scams": "Venmo scams often use fake payments, accidental transfer stories, buyer-seller tricks, or impersonation to pressure fast action.",
    "facebook-scams": "Facebook scams often appear through Marketplace messages, fake buyer interest, account alerts, impersonation, or suspicious links.",
    "instagram-scams": "Instagram scams often use impersonation, fake brand outreach, phishing links, account warnings, or suspicious investment messages.",
    "tiktok-scams": "TikTok scams often use fake promotions, impersonation, suspicious links, phishing messages, or payment tricks.",
    "whatsapp-scams": "WhatsApp scams often involve impersonation, unknown numbers, fake support, urgent payment requests, or suspicious links.",
    "telegram-scams": "Telegram scams often involve fake investments, impersonation, suspicious groups, phishing links, or urgent payment requests.",
    "snapchat-scams": "Snapchat scams often use impersonation, fake account alerts, suspicious links, or pressure to send money or information.",
    "discord-scams": "Discord scams often use fake Nitro offers, suspicious downloads, impersonation, phishing links, or account takeover tricks.",
    "crypto-scams": "Crypto scams often use fake investment promises, wallet connection tricks, phishing links, impersonation, and urgent transfer requests.",
    "package-delivery-scams": "Package delivery scams often use fake USPS, FedEx, UPS, or delivery alerts to push clicks, payments, or personal information.",
    "bank-scams": "Bank scams often use fake fraud alerts, account lock messages, payment issues, or impersonation to pressure immediate action.",
    "job-scams": "Job scams often use fake recruiters, remote job offers, interview messages, or payment requests to steal money or personal information.",
    "investment-scams": "Investment scams often promise fast returns, urgent opportunities, insider tips, or guaranteed profits to pressure risky decisions.",
    "loan-scams": "Loan scams often use fake approvals, upfront fees, urgent verification requests, or suspicious lenders to steal money or information.",
    "credit-scams": "Credit scams often involve fake repair offers, urgent account notices, phishing attempts, or requests for sensitive personal details.",
    "romance-scams": "Romance scams often build trust first, then create emotional pressure for money, gifts, account access, or private information.",
    "gift-card-scams": "Gift card scams often use urgent payment pressure, impersonation, fake support, or fake emergencies because gift cards are hard to recover.",
    "urgent-payment-scams": "Urgent payment scams rely on speed, pressure, fear, and limited verification time to get money sent before the target stops to check.",
    "government-scams": "Government scams often impersonate the IRS, Social Security, tax agencies, or benefits programs to scare people into acting quickly.",
    "unknown-number-scams": "Unknown number scams often begin with unexpected texts or calls designed to spark curiosity, urgency, or a quick reply.",
    "verification-code-scams": "Verification code scams often try to trick people into sharing one-time codes, security codes, or login approvals.",
    "phishing-scams": "Phishing scams often use fake login pages, email warnings, security alerts, or account verification requests to steal credentials."
}

HUB_TITLES = {
    "amazon-scams": "Amazon Scams: Warning Signs, Related Checks & What To Do",
    "paypal-scams": "PayPal Scams: Warning Signs, Related Checks & What To Do",
    "zelle-scams": "Zelle Scams: Warning Signs, Related Checks & What To Do",
    "cash-app-scams": "Cash App Scams: Warning Signs, Related Checks & What To Do",
    "venmo-scams": "Venmo Scams: Warning Signs, Related Checks & What To Do",
    "facebook-scams": "Facebook Scams: Warning Signs, Related Checks & What To Do",
    "instagram-scams": "Instagram Scams: Warning Signs, Related Checks & What To Do",
    "tiktok-scams": "TikTok Scams: Warning Signs, Related Checks & What To Do",
    "whatsapp-scams": "WhatsApp Scams: Warning Signs, Related Checks & What To Do",
    "telegram-scams": "Telegram Scams: Warning Signs, Related Checks & What To Do",
    "snapchat-scams": "Snapchat Scams: Warning Signs, Related Checks & What To Do",
    "discord-scams": "Discord Scams: Warning Signs, Related Checks & What To Do",
    "crypto-scams": "Crypto Scams: Warning Signs, Related Checks & What To Do",
    "package-delivery-scams": "Package Delivery Scams: Warning Signs, Related Checks & What To Do",
    "bank-scams": "Bank Scams: Warning Signs, Related Checks & What To Do",
    "job-scams": "Job Scams: Warning Signs, Related Checks & What To Do",
    "investment-scams": "Investment Scams: Warning Signs, Related Checks & What To Do",
    "loan-scams": "Loan Scams: Warning Signs, Related Checks & What To Do",
    "credit-scams": "Credit Scams: Warning Signs, Related Checks & What To Do",
    "romance-scams": "Romance Scams: Warning Signs, Related Checks & What To Do",
    "gift-card-scams": "Gift Card Scams: Warning Signs, Related Checks & What To Do",
    "urgent-payment-scams": "Urgent Payment Scams: Warning Signs, Related Checks & What To Do",
    "government-scams": "Government Scams: Warning Signs, Related Checks & What To Do",
    "unknown-number-scams": "Unknown Number Scams: Warning Signs, Related Checks & What To Do",
    "verification-code-scams": "Verification Code Scams: Warning Signs, Related Checks & What To Do",
    "phishing-scams": "Phishing Scams: Warning Signs, Related Checks & What To Do"
}


def normalize_keyword(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def title_case(text):
    return " ".join(word.capitalize() for word in str(text).split())


def escape_html(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        return []

    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        keywords = [normalize_keyword(line) for line in f if line.strip()]

    return list(dict.fromkeys(keywords))


def slugify(text):
    text = normalize_keyword(text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def page_exists(slug):
    return os.path.exists(os.path.join(OUTPUT_DIR, slug, "index.html"))


def matches_cluster(keyword, match_terms):
    keyword_norm = normalize_keyword(keyword)
    for term in match_terms:
        term_norm = normalize_keyword(term)
        if term_norm and term_norm in keyword_norm:
            return True
    return False


def score_keyword(keyword, hub_terms):
    kw = normalize_keyword(keyword)
    score = 0

    for term in hub_terms:
        term_norm = normalize_keyword(term)
        if term_norm and term_norm in kw:
            score += 2

    if "scam" in kw:
        score += 1

    if "email" in kw or "text" in kw:
        score += 1

    if "message" in kw or "link" in kw:
        score += 1

    if kw.startswith("is ") or kw.startswith("is this "):
        score += 1

    return (-score, len(kw), kw)


def build_related_links(cluster_keywords):
    links = []
    seen = set()

    for keyword in cluster_keywords:
        slug = slugify(keyword)
        if not slug or slug in seen or not page_exists(slug):
            continue

        seen.add(slug)
        anchor = f"{title_case(keyword)} Scam Check"
        links.append(
            f'<li><a href="/scam-check-now/{slug}/">{escape_html(anchor)}</a></li>'
        )

    return "\n".join(links)


def build_hub_html(hub_slug, hub_title, intro, links_html):
    canonical = build_canonical(hub_slug)
    description = intro

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape_html(hub_title)}</title>
<meta name="description" content="{escape_html(description)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{escape_html(canonical)}">
<style>
:root{{
--bg-top:#eef4ff;
--bg-bottom:#ffffff;
--ink:#1f2937;
--ink-strong:#0f172a;
--muted:#667085;
--line:#e2e8f0;
--line-soft:#edf2f7;
--blue:#2563eb;
--blue-soft:#eff6ff;
--blue-line:#bfdbfe;
--shadow-xl:0 30px 80px rgba(15,23,42,.10);
}}
*{{box-sizing:border-box;}}
body{{
font-family:system-ui,-apple-system,Arial,sans-serif;
background:
radial-gradient(circle at top center, rgba(79,125,243,.12), transparent 30%),
radial-gradient(circle at 20% 8%, rgba(37,99,235,.06), transparent 20%),
linear-gradient(180deg,var(--bg-top) 0%,var(--bg-bottom) 100%);
margin:0;
padding:32px 0;
color:var(--ink);
line-height:1.65;
}}
.page-shell{{
max-width:860px;
margin:0 auto;
padding:0 14px;
}}
.content-section{{
max-width:780px;
margin:auto;
background:rgba(255,255,255,.96);
padding:22px;
padding-bottom:36px;
border-radius:30px;
box-shadow:var(--shadow-xl);
border:1px solid rgba(226,232,240,.95);
}}
h1,h2{{
margin:0 0 14px;
color:var(--ink-strong);
line-height:1.08;
letter-spacing:-.035em;
font-weight:900;
}}
h1{{font-size:40px;}}
h2{{font-size:28px;margin-top:30px;}}
p, li{{
font-size:18px;
color:#334155;
}}
ul{{
margin:0;
padding-left:22px;
}}
li{{margin-bottom:10px;}}
a{{
color:#2563eb;
text-decoration:none;
font-weight:700;
}}
a:hover{{text-decoration:underline;}}
.info-box{{
margin:0 0 24px;
padding:18px;
border-radius:20px;
background:#f8fafc;
border:1px solid var(--line-soft);
font-size:15px;
color:#334155;
font-weight:800;
line-height:1.6;
}}
.link-box{{
margin-top:22px;
padding:18px;
border-radius:20px;
background:var(--blue-soft);
border:1px solid var(--blue-line);
}}
@media (max-width:640px){{
h1{{font-size:30px;}}
h2{{font-size:24px;}}
p,li{{font-size:16px;}}
.content-section{{padding:18px;border-radius:24px;}}
}}
</style>
</head>
<body>
<div class="page-shell">
<section class="content-section">
<div class="info-box">This hub groups together related scam checks so you can review warning signs, compare patterns, and quickly navigate to the most relevant pages.</div>

<h1>{escape_html(hub_title)}</h1>

<p>{escape_html(intro)}</p>
<p>These scam patterns often change in wording, format, and delivery method, but the underlying tactics usually stay the same: urgency, impersonation, suspicious links, fake support, payment pressure, or requests for sensitive information.</p>
<p>Use the related scam checks below to review specific variations, compare warning signs, and understand what to do next before you click, reply, send money, or share anything.</p>

<h2>Common Warning Signs</h2>
<ul>
<li>Urgent language designed to stop you from verifying independently</li>
<li>Suspicious links, fake websites, or messages that do not match the official source</li>
<li>Requests for money, codes, passwords, or personal information</li>
<li>Pressure to act immediately before checking the situation yourself</li>
</ul>

<h2>Related Scam Checks</h2>
<div class="link-box">
<ul>
{links_html}
</ul>
</div>

<h2>What To Do</h2>
<p>If something looks off, do not rely on the message itself. Go to the official website, app, or verified support channel directly and confirm the situation there before taking action.</p>
</section>
</div>
</body>
</html>
"""


def save_hub(slug, html):
    folder = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "index.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    keywords = load_keywords()
    if not keywords:
        print("No generated keywords found.")
        return

    built_count = 0

    for hub_slug, match_terms in CLUSTERS.items():
        matched = [kw for kw in keywords if matches_cluster(kw, match_terms)]

        if not matched:
            print(f"Skipped hub: {hub_slug} (no matching generated keywords)")
            continue

        matched = sorted(
            dict.fromkeys(matched),
            key=lambda k: score_keyword(k, match_terms)
        )[:MAX_LINKS_PER_HUB]

        links_html = build_related_links(matched)

        if not links_html.strip():
            print(f"Skipped hub: {hub_slug} (no existing linked pages)")
            continue

        hub_title = HUB_TITLES.get(hub_slug, title_case(hub_slug.replace("-", " ")))
        intro = HUB_INTROS.get(
            hub_slug,
            "This page groups together related scam checks so you can review warning signs, compare patterns, and navigate related pages more easily."
        )

        html = build_hub_html(hub_slug, hub_title, intro, links_html)
        save_hub(hub_slug, html)

        built_count += 1
        print(f"Built hub: {hub_slug}")

    print(f"Done. Built {built_count} hub pages.")


if __name__ == "__main__":
    main()