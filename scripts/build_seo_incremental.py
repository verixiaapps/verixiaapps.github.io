import os
import re
import sys
import subprocess
from html import escape

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
   sys.path.append(BASE_DIR)

from generate_content import generate_content
from data.cluster_map import CLUSTERS

# -----------------------------
# CONFIG
# -----------------------------
KEYWORD_FILE = os.path.join(BASE_DIR, "data", "keywords.txt")
GENERATED_SLUGS_FILE = os.path.join(BASE_DIR, "data", "generated_slugs.txt")
GENERATED_KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "generated_keywords.txt")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "seo-template.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "scam-check-now")
SITE = "https://verixiaapps.com"

RELATED_LINKS_COUNT = 6
MORE_LINKS_COUNT = 10
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "100"))
COMMIT_EVERY = int(os.getenv("COMMIT_EVERY", "30"))
RESUME = os.getenv("RESUME", "true").lower() == "true"
RUN_MODE = os.getenv("RUN_MODE", "generate")

PROTECTED_SLUGS = {"is-this-a-scam"}
FALLBACK_HUB_SLUG = "general-scams"

CLUSTER_TERMS = {
   "amazon", "paypal", "zelle", "cash", "venmo", "facebook", "instagram",
   "tiktok", "whatsapp", "telegram", "snapchat", "discord", "crypto",
   "bitcoin", "ethereum", "usps", "fedex", "ups", "bank", "chase",
   "wells", "america", "job", "loan", "credit", "romance", "gift",
   "irs", "social", "verification", "phishing", "login", "account",
   "delivery", "package", "recruiter", "refund", "payment", "wallet",
   "support", "number", "caller", "security", "alert"
}

BRAND_CASE = {
   "facebook marketplace": "Facebook Marketplace",
   "bank of america": "Bank of America",
   "wells fargo": "Wells Fargo",
   "social security": "Social Security",
   "trust wallet": "Trust Wallet",
   "google play": "Google Play",
   "cash app": "Cash App",
   "two factor": "Two-Factor",
   "metamask": "MetaMask",
   "coinbase": "Coinbase",
   "whatsapp": "WhatsApp",
   "instagram": "Instagram",
   "snapchat": "Snapchat",
   "telegram": "Telegram",
   "microsoft": "Microsoft",
   "binance": "Binance",
   "facebook": "Facebook",
   "ethereum": "Ethereum",
   "discord": "Discord",
   "bitcoin": "Bitcoin",
   "walmart": "Walmart",
   "paypal": "PayPal",
   "tiktok": "TikTok",
   "venmo": "Venmo",
   "amazon": "Amazon",
   "google": "Google",
   "apple": "Apple",
   "target": "Target",
   "crypto": "Crypto",
   "chase": "Chase",
   "steam": "Steam",
   "zelle": "Zelle",
   "fedex": "FedEx",
   "usps": "USPS",
   "bank": "Bank",
   "irs": "IRS",
   "ups": "UPS",
   "sms": "SMS",
   "otp": "OTP",
   "2fa": "2FA",
   "nft": "NFT",
   "ceo": "CEO",
   "dm": "DM",
   "icloud": "iCloud",
}

SMALL_WORDS = {
   "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
   "or", "the", "to", "vs", "with"
}

HUB_TITLE_OVERRIDES = {
   "amazon-scams": "Amazon Scam Hub",
   "paypal-scams": "PayPal Scam Hub",
   "zelle-scams": "Zelle Scam Hub",
   "cash-app-scams": "Cash App Scam Hub",
   "venmo-scams": "Venmo Scam Hub",
   "facebook-scams": "Facebook Scam Hub",
   "instagram-scams": "Instagram Scam Hub",
   "tiktok-scams": "TikTok Scam Hub",
   "whatsapp-scams": "WhatsApp Scam Hub",
   "telegram-scams": "Telegram Scam Hub",
   "snapchat-scams": "Snapchat Scam Hub",
   "discord-scams": "Discord Scam Hub",
   "crypto-scams": "Crypto Scam Hub",
   "package-delivery-scams": "Package Delivery Scam Hub",
   "bank-scams": "Bank Scam Hub",
   "job-scams": "Job Scam Hub",
   "loan-scams": "Loan Scam Hub",
   "credit-scams": "Credit Scam Hub",
   "romance-scams": "Romance Scam Hub",
   "gift-card-scams": "Gift Card Scam Hub",
   "government-scams": "Government Scam Hub",
   "verification-code-scams": "Verification Code Scam Hub",
   "account-security-scams": "Account Security Scam Hub",
   "phishing-scams": "Phishing Scam Hub",
   "general-scams": "Scam Hub",
}

# -----------------------------
# UTILITIES
# -----------------------------
def normalize_keyword(text):
   return re.sub(r"\s+", " ", str(text).strip().lower())


def slugify(text):
   text = normalize_keyword(text)
   text = re.sub(r"[^a-z0-9]+", "-", text)
   return text.strip("-")


def clean_base_keyword(text):
   """
   Light cleaner: just normalize whitespace and strip punctuation/emojis.
   Intent detection happens in build_title — we DON'T strip content words here,
   because keywords like "common delivery scam" or "examples of a debt collection scam"
   are legitimate searches that need to stay intact.
   """
   kw = normalize_keyword(text)
   # Strip emojis/non-ASCII
   kw = re.sub(r"[^\x00-\x7f]", " ", kw)
   # Strip punctuation except hyphens/word chars
   kw = re.sub(r"[^\w\s-]", " ", kw)
   kw = re.sub(r"\s+", " ", kw).strip()
   return kw


def display_keyword(text):
   return clean_base_keyword(text)


def apply_brand_case(text):
   result = f" {text} "
   for raw, proper in sorted(BRAND_CASE.items(), key=lambda x: len(x[0]), reverse=True):
       pattern = r"(?<![a-z0-9])" + re.escape(raw) + r"(?![a-z0-9])"
       result = re.sub(pattern, proper, result, flags=re.IGNORECASE)
   return re.sub(r"\s+", " ", result).strip()


def title_case(text):
   if not text:
       return ""

   words = normalize_keyword(text).split()
   titled = []

   for i, word in enumerate(words):
       if i > 0 and word in SMALL_WORDS:
           titled.append(word)
       else:
           titled.append(word.capitalize())

   return apply_brand_case(" ".join(titled))


def readable_keyword(text):
   base = display_keyword(text)
   return title_case(base) if base else ""


def keyword_tokens(text):
   base = clean_base_keyword(text)
   if not base:
       base = normalize_keyword(text)
   return set(token for token in base.split() if token)


def keyword_cluster_tokens(text):
   return {token for token in keyword_tokens(text) if token in CLUSTER_TERMS}


def keyword_root(text):
   cleaned = clean_base_keyword(text)
   return cleaned.split()[0] if cleaned else ""


def escape_html(text):
   return escape(str(text), quote=True)


def is_guidance_style_keyword(keyword):
   kw = normalize_keyword(keyword)
   return (
       kw.startswith("how to ")
       or kw.startswith("what to do")
       or kw.startswith("what happens")
       or kw.startswith("why ")
       or kw.startswith("when ")
       or kw.startswith("where ")
       or kw.startswith("who ")
       or kw.startswith("check ")
       or kw.startswith("report ")
   )


def is_question_style_keyword(keyword):
   kw = normalize_keyword(keyword)
   return kw.startswith(("is ", "can ", "did ", "should ", "was ", "could ", "would ", "do ", "does "))


def ensure_file(filepath):
   folder = os.path.dirname(filepath)
   if folder:
       os.makedirs(folder, exist_ok=True)
   if not os.path.exists(filepath):
       with open(filepath, "a", encoding="utf-8"):
           pass


def load_keywords():
   if not os.path.exists(KEYWORD_FILE):
       return []
   with open(KEYWORD_FILE, encoding="utf-8") as f:
       return list(dict.fromkeys(normalize_keyword(line) for line in f if line.strip()))


def load_generated_slugs():
   if not os.path.exists(GENERATED_SLUGS_FILE):
       return set()
   with open(GENERATED_SLUGS_FILE, encoding="utf-8") as f:
       return {slugify(line) for line in f if slugify(line)}


def load_generated_keywords():
   if not os.path.exists(GENERATED_KEYWORDS_FILE):
       return set()
   with open(GENERATED_KEYWORDS_FILE, encoding="utf-8") as f:
       return {normalize_keyword(line) for line in f if normalize_keyword(line)}


def write_lines(filepath, values, preserve_input=True):
   ensure_file(filepath)

   if preserve_input:
       lines = [str(v).strip() for v in values if str(v).strip()]
   else:
       lines = [str(v).rstrip() for v in values if str(v).strip()]

   with open(filepath, "w", encoding="utf-8") as f:
       if lines:
           f.write("\n".join(lines) + "\n")
       else:
           f.write("")


def page_path(slug):
   return os.path.join(OUTPUT_DIR, slug, "index.html")


def page_exists(slug):
   return os.path.exists(page_path(slug))


def humanize_slug(slug):
   return title_case(slug.replace("-", " "))


def _extract_slug_from_cluster_value(value):
   if isinstance(value, str):
       value = value.strip().strip("/")
       if not value:
           return ""
       if value.startswith("http://") or value.startswith("https://"):
           parts = [part for part in value.split("/") if part]
           return parts[-1] if parts else ""
       return value.split("/")[-1]

   if isinstance(value, dict):
       for key in ("slug", "hub_slug", "url", "path"):
           candidate = value.get(key)
           extracted = _extract_slug_from_cluster_value(candidate)
           if extracted:
               return extracted

   return ""


def find_best_hub_slug(keyword):
   keyword_norm = normalize_keyword(keyword)
   base = clean_base_keyword(keyword_norm)
   tokens = set(base.split()) if base else set()

   if isinstance(CLUSTERS, dict):
       for cluster_key, cluster_value in CLUSTERS.items():
           cluster_tokens = set(normalize_keyword(cluster_key).replace("-", " ").split())
           if cluster_tokens and cluster_tokens & tokens:
               extracted = _extract_slug_from_cluster_value(cluster_value)
               if extracted:
                   return extracted

           if isinstance(cluster_value, dict):
               for field in ("keywords", "terms", "aliases", "tokens"):
                   raw_terms = cluster_value.get(field, [])
                   if isinstance(raw_terms, (list, tuple, set)):
                       normalized_terms = {normalize_keyword(term) for term in raw_terms}
                       if keyword_norm in normalized_terms or base in normalized_terms:
                           extracted = _extract_slug_from_cluster_value(cluster_value)
                           if extracted:
                               return extracted

   ordered_fallbacks = [
       ("facebook marketplace", "facebook-scams"),
       ("bank of america", "bank-scams"),
       ("wells fargo", "bank-scams"),
       ("social security", "government-scams"),
       ("trust wallet", "crypto-scams"),
       ("google play", "phishing-scams"),
       ("cash app", "cash-app-scams"),
       ("metamask", "crypto-scams"),
       ("coinbase", "crypto-scams"),
       ("whatsapp", "whatsapp-scams"),
       ("instagram", "instagram-scams"),
       ("snapchat", "snapchat-scams"),
       ("telegram", "telegram-scams"),
       ("facebook", "facebook-scams"),
       ("ethereum", "crypto-scams"),
       ("discord", "discord-scams"),
       ("bitcoin", "crypto-scams"),
       ("paypal", "paypal-scams"),
       ("tiktok", "tiktok-scams"),
       ("venmo", "venmo-scams"),
       ("amazon", "amazon-scams"),
       ("crypto", "crypto-scams"),
       ("zelle", "zelle-scams"),
       ("fedex", "package-delivery-scams"),
       ("usps", "package-delivery-scams"),
       ("ups", "package-delivery-scams"),
       ("chase", "bank-scams"),
       ("bank", "bank-scams"),
       ("irs", "government-scams"),
       ("job", "job-scams"),
       ("loan", "loan-scams"),
       ("credit", "credit-scams"),
       ("romance", "romance-scams"),
       ("gift", "gift-card-scams"),
       ("verification", "verification-code-scams"),
       ("phishing", "phishing-scams"),
       ("login", "account-security-scams"),
       ("account", "account-security-scams"),
       ("delivery", "package-delivery-scams"),
       ("package", "package-delivery-scams"),
   ]

   haystack = f" {keyword_norm} "
   for term, slug in ordered_fallbacks:
       if f" {term} " in haystack:
           return slug

   return FALLBACK_HUB_SLUG


def build_hub_link_html(keyword):
   hub_slug = find_best_hub_slug(keyword)
   if not hub_slug:
       return ""

   hub_title = HUB_TITLE_OVERRIDES.get(hub_slug, f"{humanize_slug(hub_slug)} Hub")

   return f'<a href="/scam-check-now/{hub_slug}/">{escape_html(hub_title)}</a>'


def sanitize_ai_html(text):
   raw = str(text or "").strip()
   if not raw:
       return ""

   raw = re.sub(r"^```(?:html)?\s*", "", raw, flags=re.IGNORECASE)
   raw = re.sub(r"\s*```$", "", raw)
   raw = re.sub(r"<script\b[^>]*>.*?</script>", "", raw, flags=re.IGNORECASE | re.DOTALL)
   raw = re.sub(r"<style\b[^>]*>.*?</style>", "", raw, flags=re.IGNORECASE | re.DOTALL)
   raw = raw.strip()

   if "<" in raw and ">" in raw:
       return raw

   paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", raw) if p.strip()]
   if not paragraphs:
       paragraphs = [raw]

   return "\n".join(f"<p>{escape_html(paragraph)}</p>" for paragraph in paragraphs)


# -----------------------------
# GIT CHECKPOINT
# -----------------------------
def git_checkpoint(generated_count, new_generated_keywords, new_generated_slugs, remaining_keywords):
   """Write tracking files and commit+push progress to origin."""
   sorted_keywords = sorted(new_generated_keywords, key=slugify)
   write_lines(GENERATED_KEYWORDS_FILE, sorted_keywords)
   write_lines(GENERATED_SLUGS_FILE, [slugify(k) for k in sorted_keywords])
   write_lines(KEYWORD_FILE, remaining_keywords)

   try:
       subprocess.run(["git", "add", "-A"], check=True)
       result = subprocess.run(
           ["git", "diff", "--cached", "--quiet"],
           capture_output=True
       )
       if result.returncode == 0:
           print(f"[checkpoint] No changes to commit at {generated_count} pages.")
           return

       subprocess.run(
           ["git", "commit", "-m", f"Progress checkpoint: {generated_count} pages generated"],
           check=True
       )
       subprocess.run(["git", "fetch", "origin", "main"], check=True)
       subprocess.run(
           ["git", "push", "--force-with-lease", "origin", "HEAD:main"],
           check=True
       )
       print(f"[checkpoint] Committed and pushed at {generated_count} pages.")
   except subprocess.CalledProcessError as e:
       print(f"[checkpoint] Git error at {generated_count} pages: {e}")


# -----------------------------
# AI GENERATION
# -----------------------------
def generate_ai_text(keyword, keyword_display):
   raw_keyword = normalize_keyword(keyword)
   clean_keyword = normalize_keyword(keyword_display)
   readable = readable_keyword(keyword_display)

   attempts = [
       raw_keyword,
       clean_keyword,
       readable,
       f"is {clean_keyword} a scam" if clean_keyword and not raw_keyword.startswith("is ") else "",
       f"{clean_keyword} legit or scam" if clean_keyword and "legit" not in raw_keyword and "scam" not in raw_keyword else "",
   ]

   seen = set()
   last_error = None

   for prompt in attempts:
       prompt_norm = normalize_keyword(prompt)
       if not prompt_norm or prompt_norm in seen:
           continue
       seen.add(prompt_norm)

       try:
           ai_text = sanitize_ai_html(generate_content(prompt))
           if ai_text:
               return ai_text
       except Exception as e:
           last_error = e
           print(f"[error] AI generation failed for '{prompt}': {e}")

   if last_error:
       raise ValueError(f"AI generation failed for all prompts: {last_error}")
   raise ValueError("AI generation failed for all prompts")


# -----------------------------
# SEO TEXT HELPERS
# -----------------------------
def build_title(keyword):
   """
   Match search intent and build a varied title. Each pattern has multiple
   title shapes; a hash of the keyword picks which one — same keyword always
   gets the same title, but adjacent keywords get visibly different titles.
   This prevents Google from flagging templated/duplicate titles across thousands of pages.
   """
   raw = normalize_keyword(keyword)
   if not raw:
       raise ValueError("empty keyword")

   def cap(text):
       return title_case(text.strip()) if text else ""

   # Deterministic variant picker — same keyword always picks same index
   def pick(variants):
       h = 0
       for ch in raw:
           h = (h * 31 + ord(ch)) & 0xFFFFFFFF
       return variants[h % len(variants)]

   # ---- INTENT PATTERNS (most specific first) ----

   # "examples of (a/an) X scam"
   m = (re.match(r"^examples?\s+of\s+(?:a|an)\s+(.+?)\s+scam$", raw)
        or re.match(r"^examples?\s+of\s+(.+?)\s+scam$", raw))
   if m:
       s = cap(m.group(1))
       return pick([
           f"{s} Scam Examples: Real Cases You Should Know",
           f"Real {s} Scam Examples and How They Work",
           f"{s} Scams Explained: Examples and Tactics",
           f"Common {s} Scam Examples Reported in 2025",
           f"{s} Scam Cases: How They Trick Victims",
           f"Real Stories: {s} Scams People Encountered",
           f"{s} Scam Playbook: Examples From Real Reports",
           f"Inside a {s} Scam: Examples and How They Unfold",
           f"{s} Scams in the Wild: Examples and Patterns",
           f"What a {s} Scam Looks Like: Real Examples",
           f"Anatomy of a {s} Scam: Walkthroughs and Cases",
           f"Examples of {s} Scams That Caught People Off Guard",
           f"{s} Scam Tactics: Real-World Examples",
           f"Documented {s} Scams: Cases and How They Worked",
           f"How {s} Scams Play Out: Real Examples",
           f"{s} Scam Reports: Examples From Recent Victims",
           f"Case Files: {s} Scam Examples You Should See",
           f"{s} Scams Up Close: Real Examples Reviewed",
           f"Examples of {s} Scams Targeting People in 2025",
           f"{s} Scam Stories That Show the Pattern",
           f"Look at Real {s} Scams Before You Get Caught",
           f"{s} Scam Snapshots: Examples From Real Cases",
       ])

   # "how to avoid (a/an) X scam"
   m = (re.match(r"^how\s+to\s+avoid\s+(?:a|an)\s+(.+?)\s+scam$", raw)
        or re.match(r"^how\s+to\s+avoid\s+(.+?)\s+scam$", raw))
   if m:
       s = cap(m.group(1))
       return pick([
           f"How to Avoid a {s} Scam in 2025",
           f"How to Spot and Avoid a {s} Scam",
           f"Protecting Yourself From {s} Scams",
           f"{s} Scams: How to Stay Safe",
           f"Avoid Getting Scammed by Fake {s} Offers",
           f"Steering Clear of {s} Scams: A Simple Guide",
           f"How to Outsmart a {s} Scam",
           f"Don't Fall for a {s} Scam — Here's How",
           f"{s} Scams: Practical Ways to Protect Yourself",
           f"Stay Ahead of {s} Scams With These Tips",
           f"Smart Habits That Keep You Safe From {s} Scams",
           f"Why People Fall for {s} Scams and How to Avoid It",
           f"Avoiding {s} Scams: What Actually Works",
           f"A No-Nonsense Guide to Avoiding {s} Scams",
           f"{s} Scam Defense: Steps That Make a Difference",
           f"Beat the {s} Scam Before It Beats You",
           f"How to Recognize and Walk Away From a {s} Scam",
           f"Your Quick Guide to Dodging {s} Scams",
           f"What to Do Before You Get Hit by a {s} Scam",
           f"Sidestepping {s} Scams: A Reader's Guide",
           f"Practical Protection Against {s} Scams",
           f"{s} Scam Survival Guide for 2025",
       ])

   # "how to check if (a/an) X is a scam"
   m = (re.match(r"^how\s+to\s+check\s+if\s+(?:a|an)\s+(.+?)\s+is\s+a\s+scam$", raw)
        or re.match(r"^how\s+to\s+check\s+if\s+(.+?)\s+is\s+a\s+scam$", raw))
   if m:
       s = cap(m.group(1))
       return pick([
           f"How to Check if a {s} Is a Scam",
           f"Is That {s} Real or a Scam? Here's How to Tell",
           f"Verify Before You Trust: Checking if {s} Is Legit",
           f"How to Tell if a {s} Is Legit or a Scam",
           f"Spotting a Fake {s}: Verification Steps",
           f"Quick Ways to Verify a {s} Before You Trust It",
           f"Is {s} Legit? A Verification Walkthrough",
           f"Don't Trust That {s} Yet — How to Check First",
           f"Smart Checks for {s} Before You Engage",
           f"Verifying a {s}: What to Look For",
           f"Background Checks: Is That {s} the Real Thing?",
           f"How to Investigate a {s} Before You Trust It",
           f"Checking a {s}'s Legitimacy in Minutes",
           f"Is a {s} Trustworthy? Try These Checks",
           f"Read the Signs: Is a {s} Real or Fake?",
           f"Confirming a {s} Is Real Before You Commit",
           f"Vetting a {s}: A Practical Checklist",
           f"How to Sanity-Check a {s} Before You Pay",
           f"Does That {s} Pass the Smell Test? Find Out",
           f"Tell Real From Fake: Checking a {s}",
           f"Verification Steps for a {s} You Were Sent",
       ])

   # "how to tell if X is a scam"
   m = re.match(r"^how\s+to\s+tell\s+if\s+(?:a|an)?\s*(.+?)\s+is\s+a\s+scam$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"How to Tell if {s} Is a Scam",
           f"Is {s} Legit? How to Tell the Difference",
           f"{s} Scam or Real Deal? How to Decide",
           f"Telling Real {s} From a Scam",
           f"Quick Ways to Tell if {s} Is a Scam",
           f"Real or Rip-Off? Spotting a {s} Scam",
           f"Read Between the Lines: Is {s} Legit?",
           f"How to Figure Out if {s} Is a Scam",
           f"Decoding {s}: Real or Scam?",
           f"Is {s} Genuine? Here's How to Tell",
           f"Sussing Out a {s} Scam Before It's Too Late",
           f"Spot the Difference: Real {s} vs. a Scam",
           f"What Sets a Real {s} Apart From a Scam",
           f"How People Tell {s} Scams From the Real Thing",
           f"Telltale Signs: Is {s} a Scam?",
           f"Cutting Through the Confusion: Is {s} a Scam?",
           f"How to Read a {s} Before You Trust It",
           f"Reality Check: Is {s} a Scam?",
           f"A Closer Look: Is {s} Legit or a Scam?",
           f"Honest Take: How to Tell if {s} Is a Scam",
       ])

   # "common X scam(s)"
   m = re.match(r"^common\s+(.+?)\s+scams?$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"Common {s} Scams to Watch Out For",
           f"The Most Common {s} Scams in 2025",
           f"{s} Scams That Are Trending This Year",
           f"Frequent {s} Scams and How They Operate",
           f"Top {s} Scams People Are Falling For",
           f"Everyday {s} Scams You Should Know",
           f"{s} Scams Going Around Right Now",
           f"Popular {s} Scams and Their Tactics",
           f"Familiar {s} Scams That Keep Working",
           f"{s} Scams Reported Across the U.S.",
           f"The {s} Scams Showing Up Everywhere",
           f"{s} Scams You'll Probably See This Year",
           f"Widespread {s} Scams: What to Know",
           f"{s} Scams That Are Costing People Money",
           f"Recurring {s} Scams and Their Patterns",
           f"{s} Scams You'll Want to Recognize",
           f"What {s} Scams Look Like in 2025",
           f"{s} Scam Variations You Should Spot",
           f"A Rundown of Common {s} Scams",
           f"{s} Scams in Heavy Rotation Right Now",
           f"{s} Scams Making the Rounds",
           f"Familiar Faces: Common {s} Scams Explained",
       ])

   # "typical/popular/new/recent/latest/top X scam(s)"
   m = re.match(r"^(typical|popular|new|recent|latest|top)\s+(.+?)\s+scams?$", raw)
   if m:
       q = m.group(1).capitalize()
       s = cap(m.group(2))
       return pick([
           f"{q} {s} Scams You Should Know About",
           f"{q} {s} Scams Reported in 2025",
           f"{q} {s} Scam Trends and How to Avoid Them",
           f"Watch Out for These {q} {s} Scams",
           f"{q} {s} Scams: A Closer Look",
           f"{q} {s} Scams Making Headlines",
           f"What's Behind the {q} {s} Scams",
           f"Breaking Down {q} {s} Scams",
           f"{q} {s} Scams Hitting Inboxes and Phones",
           f"{q} {s} Scam Wave: What to Know",
           f"{q} {s} Scams Showing Up Online",
           f"Why {q} {s} Scams Keep Working",
           f"{q} {s} Scam Patterns Worth Knowing",
           f"A Look at {q} {s} Scams in 2025",
           f"{q} {s} Scams: Tactics and Defense",
           f"{q} {s} Scams Spreading Right Now",
       ])

   # "is X legit" / "is X legit or scam"
   m = re.match(r"^is\s+(.+?)\s+legit(?:\s+or\s+(?:a\s+)?scam)?$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"Is {s} Legit or a Scam?",
           f"{s}: Legit Service or Scam?",
           f"Is {s} Real or a Scam? An Honest Look",
           f"{s} Reviewed: Legit or Should You Avoid It?",
           f"Should You Trust {s}? Legit Check",
           f"{s}: Real Company or Red Flag?",
           f"Is {s} Worth Trusting? A Quick Review",
           f"{s} — Genuine or a Scam? Read Before You Sign Up",
           f"Honest Take: Is {s} Legit?",
           f"Is {s} Trustworthy? Here's What to Check",
           f"{s} Under the Microscope: Legit or Not?",
           f"Can You Trust {s}? Reality Check",
           f"{s}: Verified or a Possible Scam?",
           f"Reader Question: Is {s} Legit?",
           f"Is {s} the Real Thing? An Honest Review",
           f"{s} Deep Dive: Legit or Risky?",
           f"{s} on Trial: Legit Service or Scam?",
           f"Verifying {s}: What the Evidence Says",
           f"Is {s} a Safe Bet or a Scam?",
           f"{s} Reviewed in Plain English",
           f"Is {s} Worth Your Money or a Trap?",
           f"{s}: Honest Legitimacy Check",
       ])

   # "is X a scam"
   m = re.match(r"^is\s+(.+?)\s+a\s+scam$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"Is {s} a Scam?",
           f"Is {s} a Scam or Legit?",
           f"{s} Scam or Real? Here's What to Know",
           f"Is {s} Safe or a Scam? Honest Review",
           f"{s}: Scam or Trustworthy? A Closer Look",
           f"Reality Check: Is {s} a Scam?",
           f"Is {s} the Real Deal or a Scam?",
           f"{s} Investigated: Scam or Legit?",
           f"Should You Worry About {s}? Honest Take",
           f"{s} on the Radar: Scam or Safe?",
           f"Is {s} a Setup? An Honest Look",
           f"{s} in 2025: Scam or Real?",
           f"Inside {s}: Scam, Legit, or Somewhere Between?",
           f"Is {s} Sketchy? Real Review",
           f"{s} Reviewed: Scam Risk Honestly Assessed",
           f"What's Going on With {s}? Scam Check",
           f"Is {s} Worth Trusting? Honest Answer",
           f"{s}: Red Flags, Real Reports, and the Truth",
           f"Honest Verdict: Is {s} a Scam?",
           f"Is {s} Trying to Scam You? Here's What to Know",
           f"{s} Walk-Through: Scam or Genuine?",
           f"Quick Read: Is {s} a Scam?",
       ])

   # "is this a scam" alone
   if raw == "is this a scam":
       return pick([
           "Is This a Scam? How to Check Before You Click",
           "How to Tell if Something Is a Scam",
           "Is This a Scam? A Quick Guide to Checking",
           "Spotting a Scam: What to Look For Before You Act",
           "Is This a Scam? Read the Signals First",
           "Scam or Not? How to Tell in a Minute",
           "Is This a Scam? An Honest Self-Check",
           "Suspicious Message or Page? How to Decide",
           "Is This a Scam? Five Things to Look At",
           "How to Tell if You're Being Scammed",
           "Is This Legit? A Practical Scam Check",
           "Quick Read: Is This a Scam?",
       ])

   # "is this X" (anything else)
   m = re.match(r"^is\s+this\s+(.+)$", raw)
   if m:
       rest = re.sub(r"\s+a\s+scam$", "", m.group(1).strip()).strip()
       if rest:
           s = cap(rest)
           return pick([
               f"Is This {s}? How to Tell if It's Real",
               f"Is This {s} Legit or Fake?",
               f"Got This {s}? Here's How to Check",
               f"Is This {s} a Scam? Quick Verification Tips",
               f"Is This {s} Real? Here's What to Look For",
               f"Suspicious {s}? How to Verify",
               f"Read This Before You Trust That {s}",
               f"Is That {s} the Real Thing?",
               f"Quick Check: Is This {s} a Scam?",
               f"How to Tell if a {s} Like This Is Legit",
               f"This {s}: Real or a Red Flag?",
               f"Got a {s} Like This? How to Decide",
           ])
       return "Is This a Scam? How to Check Before You Click"

   # "did i get scammed by/on/with/from X"
   m = re.match(r"^did\s+i\s+get\s+scammed\s+(?:by|on|with|from)\s+(.+)$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"Did I Get Scammed by {s}? Signs to Look For",
           f"Scammed by {s}? What to Do Next",
           f"Think You Were Scammed by {s}? Here's How to Tell",
           f"Recovering From a {s} Scam: Your Next Steps",
           f"After a {s} Scam: What Comes Next",
           f"Scammed by {s}? A Recovery Walkthrough",
           f"What to Do if You Were Scammed by {s}",
           f"Lost Money to {s}? Here's What to Try",
           f"Scam Recovery: Steps After a {s} Incident",
           f"After Getting Scammed by {s}: A Practical Guide",
           f"Hit by a {s} Scam? Here's the Path Forward",
           f"Did {s} Scam You? Read This Next",
           f"Caught in a {s} Scam? Steps to Take Today",
           f"{s} Scam Aftermath: What You Can Still Do",
       ])

   # "check if X is a scam"
   m = re.match(r"^check\s+if\s+(.+?)\s+is\s+a\s+scam$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"Is {s} a Scam? Verify Before You Trust",
           f"Checking if {s} Is Legit or a Scam",
           f"Is {s} Safe? How to Check",
           f"Run a Scam Check on {s} in Minutes",
           f"Is {s} Real? Quick Verification",
           f"{s} Scam Check: A Practical Walkthrough",
           f"How People Vet {s} Before Trusting It",
           f"Does {s} Pass a Scam Check?",
       ])

   # "X scam check"
   m = re.match(r"^(.+?)\s+scam\s+check$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"{s} Scam Check: Verify Before You Trust",
           f"Is {s} Legit? Run a Quick Scam Check",
           f"{s} Legitimacy Check: What to Verify First",
           f"Vetting {s}: A Scam Check Walkthrough",
           f"{s} Scam Check Guide for 2025",
           f"Quick Scam Check for {s}",
           f"{s} on the Radar: Run This Scam Check",
           f"Don't Trust {s} Yet — Scam Check Steps",
       ])

   # "X scam reviews"
   m = re.match(r"^(.+?)\s+scam\s+reviews?$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"{s} Scam Reviews: What Users Are Reporting",
           f"{s} Reviews and Scam Reports",
           f"Real {s} Reviews: Legit or a Scam?",
           f"{s} Reviewed: Real Reports From Users",
           f"User Reviews on {s}: Scam Signals to Know",
           f"What People Are Saying About {s}",
           f"{s} Reputation Check: Reviews and Reports",
           f"Reading the Room: {s} Reviews and Risks",
       ])

   # "X legit check"
   m = re.match(r"^(.+?)\s+legit\s+check$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"{s} Legit Check: Verify Before You Commit",
           f"Is {s} Legit? Quick Verification Guide",
           f"{s} Trust Check: What to Look At First",
           f"Vetting {s}: A Legit Check That Works",
           f"{s} Authenticity Check for 2025",
           f"Reading the Signs: Is {s} Legit?",
           f"{s} Background Check Before You Engage",
           f"Verify {s}: A Legit Check Walkthrough",
       ])

   # Question-form: what/why/when/where/who/how — BEFORE bare "X scam"
   if re.match(r"^(what|why|when|where|who|how)\s+", raw):
       q = cap(raw)
       return pick([
           f"{q}? A Plain-Language Answer",
           f"{q}? Everything You Need to Know",
           f"{q}? Here's What Actually Happens",
           f"{q}? Real Examples and Practical Tips",
           f"{q}? Read This First",
           f"{q}? An Honest, Useful Answer",
           f"{q}? A Clear Walkthrough",
           f"{q}? Quick Guide With Real Examples",
           f"{q}? The Facts in Plain English",
           f"{q}? Practical Answers You Can Use",
           f"{q}? A Reader's Guide",
           f"{q}? Straight Talk on the Topic",
       ])

   # bare "X scam(s)"
   m = re.match(r"^(.+?)\s+scams?$", raw)
   if m:
       s = cap(m.group(1))
       return pick([
           f"Is {s} a Scam? What to Watch For",
           f"{s} Scams Explained",
           f"{s} Scam Warning: How to Protect Yourself",
           f"{s} Scam Alert: Spotting the Red Flags",
           f"All About {s} Scams: Tactics and Defense",
           f"{s} Scams in 2025: What to Know",
           f"Inside {s} Scams: How They Actually Work",
           f"A Quick Guide to {s} Scams",
           f"{s} Scams Decoded",
           f"{s} Scams Up Close",
           f"The Reality of {s} Scams Today",
           f"{s} Scams: Patterns and Protection",
           f"Behind {s} Scams: What's Really Going On",
           f"{s} Scam Field Guide",
           f"{s} Scams Without the Jargon",
           f"Understanding {s} Scams in Plain English",
           f"{s} Scam Brief: Tactics and Tells",
           f"{s} Scam Anatomy: Step by Step",
           f"The {s} Scam Landscape in 2025",
           f"{s} Scams: What's Working and What to Avoid",
           f"{s} Scam Snapshot",
           f"{s} Scam Files",
       ])

   # ---- FALLBACK: no pattern matched ----
   q = cap(raw)
   return pick([
       f"{q}: What You Should Know",
       f"{q} Explained",
       f"About {q}: A Quick Guide",
       f"{q}: An Honest Look",
       f"{q}: Plain-Language Overview",
       f"{q}: A Reader's Guide",
       f"{q}: Key Things to Know",
       f"{q}: Straight Talk",
       f"{q}: What People Are Asking",
       f"{q}: A Closer Look",
   ])


def build_description(keyword):
   raw = normalize_keyword(keyword)
   readable = readable_keyword(keyword)

   def pick(variants):
       h = 0
       for ch in raw:
           h = (h * 31 + ord(ch)) & 0xFFFFFFFF
       return variants[h % len(variants)]

   if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
       return pick([
           f"Learn how {readable} works, what to look out for, and how to stay safe before you click, reply, or pay.",
           f"A practical guide to {readable} — red flags, real examples, and what to do if you spot one.",
           f"Everything you need to know about {readable}: how it works, who is targeted, and how to protect yourself.",
           f"{readable} explained in plain language, with examples and simple steps to avoid getting caught.",
           f"What {readable} looks like in real life, and the simple checks that keep you from being a victim.",
           f"A reader-friendly look at {readable}: tactics, warning signs, and what to do next.",
           f"Read this before you act on anything related to {readable} — clear examples and steps that work.",
           f"How {readable} actually plays out, and how to stay one step ahead of it.",
           f"{readable} broken down: what to recognize, what to ignore, and what to verify.",
           f"Plain-English coverage of {readable} with real scenarios and practical safety steps.",
           f"What you should know about {readable} — written for normal people, not security experts.",
           f"A no-fluff guide to {readable}: how it works, who falls for it, how to avoid it.",
           f"Real talk about {readable}: what's actually happening and how to handle it.",
           f"A short, honest guide to {readable} — examples, tells, and next steps.",
           f"{readable} from the ground up: how it begins, how it ends, how to stop it.",
       ])

   return pick([
       f"Is {readable} legit, or should you be worried? Here is what to check before you trust it or send money.",
       f"Real reports, red flags, and verification steps for {readable}. Find out what to look for before you act.",
       f"A closer look at {readable}: how it works, common tactics, and how to tell legit from a scam.",
       f"{readable}: what people are reporting, how to spot fakes, and what to do if you have already engaged.",
       f"Honest review of {readable} — what is real, what is a red flag, and how to protect yourself.",
       f"Everything you should know about {readable} before you engage, in plain English.",
       f"A practical look at {readable}: tactics, tells, and what makes it different from the real thing.",
       f"{readable} reviewed without the jargon — what works, what doesn't, what to watch.",
       f"What's behind {readable}: real reports, common patterns, and how to verify before you trust it.",
       f"Read this before you trust {readable}. A clear, useful walkthrough of what to check.",
       f"{readable}: the honest take on whether it's legit, sketchy, or somewhere in between.",
       f"A quick, useful guide to {readable} for anyone who isn't sure what they're looking at.",
       f"How to think about {readable} when you're not sure what to trust.",
       f"Cut through the noise on {readable} — what's actually going on and how to react.",
       f"Real-world coverage of {readable}: what to expect, what to verify, what to skip.",
   ])


def build_related_anchor(keyword):
   raw = normalize_keyword(keyword)
   readable = readable_keyword(keyword)

   if is_guidance_style_keyword(raw) or is_question_style_keyword(raw):
       if raw.startswith("is ") and " legit" in raw:
           cleaned = re.sub(r"\s+legit\b", "", raw).strip()
           return f"{title_case(cleaned)} Legit or a Scam?"
       if raw.startswith("did i get scammed") or raw.startswith("what happens after ") or raw.startswith("almost "):
           return title_case(raw) + "?"
       return title_case(raw)

   return f"Is {readable} a Scam?"


def build_canonical(slug):
   return f"{SITE}/scam-check-now/{slug}/"


# -----------------------------
# LINKING HELPERS
# -----------------------------
def dedupe_pages_by_slug(pages_list):
   deduped = []
   seen = set()

   for page in pages_list:
       slug = page["slug"]
       if not slug or slug in seen or slug in PROTECTED_SLUGS:
           continue
       seen.add(slug)
       deduped.append(page)

   return deduped


def get_related_pages(current_page, all_pages, limit, exclude_slugs=None):
   exclude_slugs = set(exclude_slugs or set())
   current_slug = current_page["slug"]
   current_keyword = current_page["keyword"]
   current_tokens = keyword_tokens(current_keyword)
   current_cluster = keyword_cluster_tokens(current_keyword)
   current_root = keyword_root(current_keyword)
   current_base = clean_base_keyword(current_keyword)
   current_hub = find_best_hub_slug(current_keyword)

   candidates = [
       p for p in all_pages
       if p["slug"] != current_slug
       and p["slug"] not in PROTECTED_SLUGS
       and p["slug"] not in exclude_slugs
       and page_exists(p["slug"])
       and clean_base_keyword(p["keyword"]) != current_base
   ]

   def score(page):
       other_keyword = page["keyword"]
       other_tokens = keyword_tokens(other_keyword)
       other_cluster = keyword_cluster_tokens(other_keyword)
       other_root = keyword_root(other_keyword)
       other_hub = find_best_hub_slug(other_keyword)
       length_diff = abs(len(other_tokens) - len(current_tokens))
       same_root = 1 if current_root and other_root == current_root else 0
       same_hub = 1 if current_hub and other_hub == current_hub else 0
       shared_cluster = len(current_cluster & other_cluster)
       shared_tokens = len(current_tokens & other_tokens)

       return (
           -same_hub,
           -same_root,
           -shared_cluster,
           -shared_tokens,
           length_diff,
           other_keyword,
       )

   ranked = sorted(candidates, key=score)
   related = []
   used_slugs = set()
   used_bases = set()

   for page in ranked:
       base = clean_base_keyword(page["keyword"])
       if page["slug"] in used_slugs or base in used_bases:
           continue
       related.append(page)
       used_slugs.add(page["slug"])
       used_bases.add(base)
       if len(related) == limit:
           break

   return related


def build_links_html(pages_list):
   return "".join(
       f'<li><a href="/scam-check-now/{p["slug"]}/">{escape_html(build_related_anchor(p["keyword"]))}</a></li>\n'
       for p in pages_list
       if page_exists(p["slug"])
   )


# -----------------------------
# SETUP & GENERATION LOOP
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
ensure_file(GENERATED_SLUGS_FILE)
ensure_file(GENERATED_KEYWORDS_FILE)

with open(TEMPLATE_FILE, encoding="utf-8") as f:
   template = f.read()

keywords = load_keywords()
if not keywords:
   print("No keywords in queue. Nothing to generate.")
   sys.exit(0)

generated_slugs = load_generated_slugs()
generated_keywords = load_generated_keywords()

queue_pages = []
seen_queue_slugs = set()
duplicate_queue_count = 0

for keyword in keywords:
   keyword_norm = normalize_keyword(keyword)
   slug = slugify(keyword_norm)

   if slug in PROTECTED_SLUGS or not slug:
       continue
   if slug in seen_queue_slugs:
       duplicate_queue_count += 1
       continue

   seen_queue_slugs.add(slug)
   queue_pages.append({"keyword": keyword_norm, "slug": slug})

existing_pages = []
existing_seen_slugs = set()

for keyword in generated_keywords:
   slug = slugify(keyword)
   if slug in PROTECTED_SLUGS or slug in existing_seen_slugs or not slug:
       continue
   if page_exists(slug):
       existing_pages.append({"keyword": keyword, "slug": slug})
       existing_seen_slugs.add(slug)

for page in queue_pages:
   if page["slug"] in existing_seen_slugs:
       continue
   if page_exists(page["slug"]):
       existing_pages.append(page)
       existing_seen_slugs.add(page["slug"])

existing_pages = dedupe_pages_by_slug(existing_pages)
queue_pages = dedupe_pages_by_slug(queue_pages)

print(f"Loaded {len(keywords)} keywords from queue.")
print(f"Unique queued pages after slug dedupe: {len(queue_pages)}")
print(f"Duplicate queued keywords skipped: {duplicate_queue_count}")
print(f"Known generated slugs: {len(generated_slugs)}")
print(f"Known generated keywords: {len(generated_keywords)}")
print(f"Existing pages available for internal links: {len(existing_pages)}")
print(f"Daily limit: {DAILY_LIMIT}")
print(f"Commit every: {COMMIT_EVERY}")
print(f"Resume mode: {RESUME}")
print(f"Run mode: {RUN_MODE}")
print(f"Fallback hub slug: {FALLBACK_HUB_SLUG}")

generated_count = 0
skipped_existing_count = 0
failed_count = 0
processed_keywords = set()
new_generated_slugs = set(generated_slugs)
new_generated_keywords = set(generated_keywords)

# Build remaining_keywords as a mutable list we update on each checkpoint
remaining_keywords = [normalize_keyword(kw) for kw in keywords]

for page in queue_pages:
   if generated_count >= DAILY_LIMIT:
       break

   slug = page["slug"]
   keyword = page["keyword"]
   keyword_display = display_keyword(keyword)
   path = page_path(slug)

   if slug in PROTECTED_SLUGS:
       processed_keywords.add(keyword)
       remaining_keywords = [kw for kw in remaining_keywords if kw != keyword]
       print("Skipping protected page:", slug)
       continue

   # Skip existing pages unless the user explicitly turned resume off.
   # When RESUME is false, we re-generate even if the file already exists
   # (useful for rebuild_wipe + resume=false, or forced regens).
   if page_exists(slug) and RESUME:
       skipped_existing_count += 1
       new_generated_slugs.add(slug)
       new_generated_keywords.add(keyword)
       processed_keywords.add(keyword)
       remaining_keywords = [kw for kw in remaining_keywords if kw != keyword]
       continue

   os.makedirs(os.path.dirname(path), exist_ok=True)
   title = build_title(keyword)
   description = build_description(keyword)
   canonical = build_canonical(slug)

   try:
       ai_text = generate_ai_text(keyword, keyword_display)
   except Exception as e:
       failed_count += 1
       print(f"[failed] {keyword} -> {e}")
       continue

   related_pages = get_related_pages(page, existing_pages, RELATED_LINKS_COUNT)
   related_slugs = {p["slug"] for p in related_pages}
   more_pages = get_related_pages(
       page,
       existing_pages,
       MORE_LINKS_COUNT,
       exclude_slugs=related_slugs,
   )

   hub_link_html = build_hub_link_html(keyword)
   html = template
   html = html.replace("{{TITLE}}", escape_html(title))
   html = html.replace("{{DESCRIPTION}}", escape_html(description))
   html = html.replace("{{KEYWORD}}", escape_html(keyword_display))
   html = html.replace("{{AI_CONTENT}}", ai_text)
   html = html.replace("{{RELATED_LINKS}}", build_links_html(related_pages))
   html = html.replace("{{MORE_LINKS}}", build_links_html(more_pages))
   html = html.replace("{{HUB_LINK}}", hub_link_html)
   html = html.replace("{{CANONICAL_URL}}", escape_html(canonical))

   with open(path, "w", encoding="utf-8") as f:
       f.write(html)

   new_generated_slugs.add(slug)
   new_generated_keywords.add(keyword)
   processed_keywords.add(keyword)
   remaining_keywords = [kw for kw in remaining_keywords if kw != keyword]

   existing_pages.append({"keyword": keyword, "slug": slug})
   existing_pages = dedupe_pages_by_slug(existing_pages)
   generated_count += 1

   print(
       f"Generated: {slug} ({generated_count}/{DAILY_LIMIT}) "
       f"-> hub: {find_best_hub_slug(keyword)}"
   )

   # ---- CHECKPOINT EVERY N PAGES ----
   if generated_count % COMMIT_EVERY == 0:
       git_checkpoint(generated_count, new_generated_keywords, new_generated_slugs, remaining_keywords)

# Final write + commit for whatever remains after the last checkpoint
git_checkpoint(generated_count, new_generated_keywords, new_generated_slugs, remaining_keywords)

print(
   f"Done. Generated {generated_count} new pages. "
   f"Skipped {skipped_existing_count} existing pages. "
   f"Failed {failed_count} keywords."
)
print(f"Remaining keywords in queue: {len(remaining_keywords)}")
