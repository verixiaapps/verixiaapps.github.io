import os
import json
from collections import defaultdict

# CONFIG
INPUT_FILE = "keywords.json"   # your keyword list
OUTPUT_DIR = "scam-check-now-c/hubs"
BASE_URL = "https://verixiaapps.com/check"

MAX_LINKS_PER_HUB = 120

# HUB DEFINITIONS
HUB_RULES = {
    "job-scams": ["job", "hiring", "recruiter", "interview", "offer"],
    "crypto-scams": ["crypto", "bitcoin", "wallet", "eth", "nft", "airdrop"],
    "email-scams": ["email", "mail", "inbox"],
    "text-scams": ["text", "sms", "message"],
    "brand-scams": ["paypal", "amazon", "apple", "google", "bank"],
    "payment-scams": ["payment", "invoice", "transfer", "fee"],
}

# LOAD KEYWORDS
with open(INPUT_FILE, "r") as f:
    keywords = json.load(f)

# GROUP KEYWORDS INTO HUBS
hubs = defaultdict(list)

for kw in keywords:
    lower = kw.lower()

    matched = False
    for hub, rules in HUB_RULES.items():
        if any(r in lower for r in rules):
            hubs[hub].append(kw)
            matched = True
            break

    if not matched:
        hubs["general-scams"].append(kw)

# CREATE OUTPUT DIR
os.makedirs(OUTPUT_DIR, exist_ok=True)

# BUILD HUB PAGES
for hub_name, kw_list in hubs.items():
    kw_list = kw_list[:MAX_LINKS_PER_HUB]

    links_html = ""
    for kw in kw_list:
        slug = kw.lower().replace(" ", "-")
        url = f"{BASE_URL}/{slug}/"
        links_html += f'<li><a href="{url}">{kw}</a></li>\n'

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{hub_name.replace("-", " ").title()} | Scam Check</title>
<meta name="description" content="Check {hub_name.replace('-', ' ')} messages, links, and offers. Identify scam risks before you click, reply, or send money.">
<link rel="canonical" href="{BASE_URL}/hubs/{hub_name}/">
</head>

<body style="font-family:Arial;padding:40px;max-width:900px;margin:auto;">

<h1>{hub_name.replace("-", " ").title()}</h1>

<p>
This page groups common {hub_name.replace("-", " ")} patterns, messages, and scams.
Use it to quickly find similar cases, compare warning signs, and check suspicious messages before taking action.
</p>

<ul>
{links_html}
</ul>

</body>
</html>
"""

    # SAVE FILE
    hub_path = os.path.join(OUTPUT_DIR, hub_name)
    os.makedirs(hub_path, exist_ok=True)

    with open(os.path.join(hub_path, "index.html"), "w") as f:
        f.write(html)

print("Hubs built successfully.")