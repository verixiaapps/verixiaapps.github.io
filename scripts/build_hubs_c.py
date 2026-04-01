Use this version:

import os
from collections import defaultdict

# PATH SETUP (works locally + in GH Actions)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "generated_keywords_c.txt")
SLUGS_FILE = os.path.join(BASE_DIR, "data", "generated_slugs_c.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "scam-check-now-c", "hubs")

SITE = "https://verixiaapps.com"
PAGE_PREFIX = "/scam-check-now-c"
HUB_PREFIX = "/scam-check-now-c/hubs"

MAX_LINKS_PER_HUB = 120

# HUB DEFINITIONS
HUB_RULES = {
    "job-scams": ["job", "hiring", "recruiter", "interview", "offer", "onboarding"],
    "crypto-scams": ["crypto", "bitcoin", "wallet", "ethereum", "eth", "nft", "airdrop", "token"],
    "email-scams": ["email", "mail", "inbox"],
    "text-scams": ["text", "sms", "message"],
    "brand-scams": ["paypal", "amazon", "apple", "google", "bank", "venmo", "zelle", "cash app"],
    "payment-scams": ["payment", "invoice", "transfer", "fee"],
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


# LOAD DATA (paired keywords + slugs)
with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
    keywords = [clean_text(x) for x in f.readlines() if x.strip()]

with open(SLUGS_FILE, "r", encoding="utf-8") as f:
    slugs = [clean_text(x) for x in f.readlines() if x.strip()]

if len(keywords) != len(slugs):
    raise ValueError("generated_keywords_c.txt and generated_slugs_c.txt count mismatch")

pairs = list(zip(keywords, slugs))

# GROUP INTO HUBS
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

# CREATE OUTPUT DIR
os.makedirs(OUTPUT_DIR, exist_ok=True)

# BUILD HUB PAGES
for hub_name, items in hubs.items():
    seen = set()
    deduped = []

    for kw, slug in items:
        if slug not in seen:
            seen.add(slug)
            deduped.append((kw, slug))

    deduped = deduped[:MAX_LINKS_PER_HUB]

    links_html = ""
    for kw, slug in deduped:
        url = f"{SITE}{PAGE_PREFIX}/{slug}/"
        links_html += f'<li><a href="{url}">{safe_html(kw)}</a></li>\n'

    title_text = hub_name.replace("-", " ").title()
    desc_text = title_text.lower()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{safe_html(title_text)} | Scam Check</title>
<meta name="description" content="Check {safe_html(desc_text)} messages, links, and offers. Identify scam risks before you click, reply, or send money.">
<link rel="canonical" href="{SITE}{HUB_PREFIX}/{hub_name}/">
<meta name="robots" content="index,follow">
</head>

<body style="font-family:Arial;padding:40px;max-width:900px;margin:auto;">

<h1>{safe_html(title_text)}</h1>

<p>
This page groups common {safe_html(desc_text)} patterns, messages, and scams.
Use it to quickly find similar cases, compare warning signs, and check suspicious messages before taking action.
</p>

<ul>
{links_html}
</ul>

</body>
</html>
"""

    hub_path = os.path.join(OUTPUT_DIR, hub_name)
    os.makedirs(hub_path, exist_ok=True)

    with open(os.path.join(hub_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

print("Hubs built successfully.")