import requests
import sys
import logging
import re
from html import unescape

# -----------------------------
# CONFIG
# -----------------------------
RAILWAY_API = "https://awake-integrity-production-faa0.up.railway.app"
TIMEOUT = 60

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

WARNING_SECTION_TITLES = [
    "Common Warning Signs",
    "Red Flags To Watch For",
    "Signs This Might Be A Scam",
]

ACTION_SECTION_TITLES = [
    "What Should You Do?",
    "What To Do Next",
    "How To Respond Safely",
]

ACTION_SECTION_INTROS = [
    "The safest next step is to verify everything outside the message itself.",
    "Before you click, reply, or pay, confirm the situation through an official source you trust.",
    "A careful verification step can stop most scams before any damage happens.",
]

CONTENT_MODES = [
    "direct",
    "scenario",
    "warning",
    "comparison",
    "breakdown",
]

GENERIC_WARNING_BULLET_SETS = [
    [
        "Unexpected messages asking for money, codes, or personal information",
        "Pressure to act quickly before you can verify the message",
        "Links, websites, or senders that do not fully match the official source",
        "Requests for payment by crypto, gift card, wire transfer, or other hard-to-reverse methods",
    ],
    [
        "A sudden message that creates urgency without clear proof",
        "Requests to click a link, log in, or confirm sensitive details",
        "Sender names, websites, or contact details that do not fully match",
        "Payment instructions that are hard to reverse or verify",
    ],
    [
        "Warnings or alerts that push you to act before checking",
        "Requests for verification codes, personal details, or payment",
        "Suspicious links, fake support pages, or mismatched domains",
        "Pressure to move off trusted platforms or official apps",
    ],
]

CONTEXT_WARNING_BULLETS = {
    "payment": [
        [
            "Messages about account limits, refunds, transfers, or suspicious charges that push you to act immediately",
            "Requests to confirm card details, bank credentials, payment information, or one-time codes",
            "Links that lead to login pages, payment pages, or support pages that do not fully match the official brand",
            "Pressure to send money through wire transfer, Zelle, gift cards, crypto, or other hard-to-reverse methods",
        ],
        [
            "Unexpected payment alerts that create urgency before you can verify the issue",
            "Requests to sign in, confirm ownership, or unlock an account through a message link",
            "Customer support language that feels generic, mismatched, or slightly off-brand",
            "Refund or payment instructions that bypass the official app or website",
        ],
        [
            "Security warnings, refunds, or payment problems that arrive without context",
            "Requests for login details, card information, or verification codes",
            "Fake support pages, spoofed domains, or copied brand layouts",
            "Instructions to move money quickly before checking the account directly",
        ],
    ],
    "job": [
        [
            "A job offer that arrives quickly with little screening or no normal hiring process",
            "Promises of easy pay, remote work, or fast approval without clear role details",
            "Requests for personal details, application fees, equipment payments, or bank information early in the process",
            "Pressure to move the conversation to text, WhatsApp, Telegram, or another unofficial channel",
        ],
        [
            "Recruiters who avoid normal interview steps or provide vague company details",
            "Pay, benefits, or work terms that seem unusually generous for the role",
            "Requests to pay upfront for training, software, background checks, or equipment",
            "Messages that push you off trusted job platforms too quickly",
        ],
        [
            "A hiring message that feels rushed, generic, or overly enthusiastic",
            "Requests for identity documents, account details, or payment before real onboarding",
            "Contact details that do not fully match the claimed company",
            "Instructions to continue through unofficial messaging apps instead of normal hiring channels",
        ],
    ],
    "crypto": [
        [
            "Messages promising guaranteed returns, recovery help, or urgent wallet action",
            "Requests to connect a wallet, approve a transaction, or share seed phrase details",
            "Support or investment messages that push you to move funds quickly",
            "Websites, apps, or tokens that look real at first but do not match the official project",
        ],
        [
            "Investment claims that sound low-risk, exclusive, or time-sensitive",
            "Requests to verify a wallet, unlock funds, or fix a transfer through a link",
            "Fake support accounts contacting you first instead of responding through official channels",
            "Pressure to send crypto before you can independently verify the opportunity",
        ],
        [
            "Recovery, airdrop, staking, or support messages designed to create urgency",
            "Requests for wallet access, private details, or transaction approval",
            "Impersonation of known exchanges, wallets, or crypto communities",
            "Promises of returns or account fixes that depend on quick payment or connection",
        ],
    ],
    "delivery": [
        [
            "Delivery messages about failed drop-off, address problems, customs fees, or tracking issues",
            "Links asking you to confirm shipping details or pay a small fee before redelivery",
            "Sender names or tracking pages that do not fully match the official carrier",
            "Messages that arrive unexpectedly when you are not actively expecting a package",
        ],
        [
            "Urgent delivery alerts that push you to click before checking the carrier directly",
            "Requests to update an address, confirm identity, or pay a handling charge",
            "Tracking links that use unusual domains or shortened URLs",
            "Package issues that appear vague and do not reference a real order you recognize",
        ],
        [
            "Texts or emails claiming a package problem without enough shipment detail",
            "Small fee requests designed to get payment information quickly",
            "Spoofed delivery pages that copy USPS, FedEx, UPS, or shipping layouts",
            "Pressure to act right away instead of checking tracking in the official app or site",
        ],
    ],
    "account-security": [
        [
            "Unexpected security alerts claiming your account is locked, suspended, or under review",
            "Requests to enter login details, reset a password, or share a verification code",
            "Links to sign-in pages that do not fully match the official website or app",
            "Support messages that create urgency before you can check the account yourself",
        ],
        [
            "Password reset or login alerts you did not trigger",
            "Messages asking for one-time codes, two-factor details, or identity confirmation",
            "Email addresses, domains, or support pages that look close but not exact",
            "Pressure to secure the account by following the link in the message",
        ],
        [
            "Warnings about unusual activity that push you to act immediately",
            "Requests to verify your identity through message links or unofficial pages",
            "Copied branding used to imitate real support teams or account alerts",
            "Attempts to capture login details or verification codes before you verify the source",
        ],
    ],
    "government": [
        [
            "Messages about taxes, benefits, or government payments that create urgency without clear proof",
            "Requests for personal details, account information, or fees to release money or fix a problem",
            "Threats involving penalties, suspension, arrest, or benefit loss unless you respond quickly",
            "Payment demands through gift cards, wire transfers, crypto, or unofficial channels",
        ],
        [
            "Unexpected notices about refunds, benefits, or account issues that pressure you to act fast",
            "Requests to confirm identity or payment details through a link in the message",
            "Language that sounds official but does not match how real agencies normally communicate",
            "Instructions to pay or verify through channels outside official government websites",
        ],
        [
            "Tax or benefits messages designed to trigger panic or urgency",
            "Requests for Social Security numbers, banking details, or fees before verification",
            "Fake websites or contact details that imitate official agencies",
            "Pressure to respond immediately instead of checking directly with the real agency",
        ],
    ],
    "unknown-number": [
        [
            "Calls or messages from numbers you do not recognize that quickly ask for information or money",
            "Texts that create urgency, curiosity, or confusion before giving enough detail",
            "Links, callbacks, or follow-up requests tied to a number with no trusted context",
            "Attempts to move the conversation toward payment, codes, or personal details",
        ],
        [
            "Unexpected messages from unknown or spoofed numbers with vague but urgent claims",
            "Requests to confirm identity, click a link, or continue the conversation elsewhere",
            "Call-back pressure, wrong-number tactics, or messages that feel oddly generic",
            "A number that does not match the claimed company, person, or service",
        ],
        [
            "Texts or calls that rely on surprise before offering proof",
            "Requests for money, verification codes, or personal information from an unfamiliar contact",
            "Links or callback numbers that you cannot independently verify",
            "Pressure to keep responding before you confirm who is actually contacting you",
        ],
    ],
    "phishing": [
        [
            "Emails or texts designed to copy a trusted brand, platform, or service",
            "Links that lead to login pages, support pages, or account alerts that look real at first glance",
            "Requests for passwords, verification codes, account access, or payment details",
            "Urgent language pushing you to fix a problem before you verify the source",
        ],
        [
            "A message that imitates a company update, security warning, or support response",
            "Requests to sign in, confirm identity, or reset an account through a link",
            "Domains, reply addresses, or page layouts that are close to the original but not exact",
            "Pressure to act before checking the official website or app directly",
        ],
        [
            "Spoofed messages that use fear, urgency, or account warnings",
            "Fake login pages built to capture credentials or verification codes",
            "Branding that looks familiar but contains small mismatches",
            "Links or downloads intended to steal information or redirect you to a fraudulent page",
        ],
    ],
}

ACTION_PARAGRAPHS_BY_CONTEXT = {
    "payment": [
        "If this involves {keyword}, do not use the message link to sign in, confirm a transfer, or send money. Open the official app or website yourself and check the account there first.",
        "Before you respond to anything related to {keyword}, verify the account, payment issue, or support claim inside the official platform you trust.",
        "If {keyword} appears in a payment or account message, avoid sending money or sharing codes until you confirm the request through the official app, website, or phone number.",
    ],
    "job": [
        "If this involves {keyword}, verify the employer, recruiter, and job listing independently before sharing personal details or paying anything.",
        "Before you continue with anything related to {keyword}, confirm the company website, recruiter email domain, and hiring process through trusted sources you find yourself.",
        "If {keyword} appears in a job message, avoid fees, gift cards, equipment payments, or unofficial chat apps until you verify the role directly with the employer.",
    ],
    "crypto": [
        "If this involves {keyword}, do not connect a wallet, approve a transaction, or send crypto until you verify the project, platform, or support account through official channels.",
        "Before you take any action related to {keyword}, double-check the website, support contact, and wallet request yourself instead of trusting the message alone.",
        "If {keyword} appears in a crypto message, avoid moving funds or sharing wallet-related information until you confirm the situation through the real exchange, wallet, or project site.",
    ],
    "delivery": [
        "If this involves {keyword}, do not pay a fee or confirm details through the message link. Check tracking directly on the official carrier website or app instead.",
        "Before you respond to anything related to {keyword}, verify the shipment independently using the real USPS, FedEx, UPS, or merchant tracking page.",
        "If {keyword} appears in a delivery alert, avoid entering payment or address details until you confirm the package issue through the official carrier.",
    ],
    "account-security": [
        "If this involves {keyword}, do not enter your password or verification code through a message link. Open the official website or app yourself and check the account there.",
        "Before you act on anything related to {keyword}, verify the login alert, reset request, or account warning directly inside the real service.",
        "If {keyword} appears in a security message, avoid sharing codes or credentials until you confirm the alert through the official platform.",
    ],
    "government": [
        "If this involves {keyword}, do not pay, click, or share personal information through the message. Verify the notice directly through the official agency website or phone number.",
        "Before you respond to anything related to {keyword}, confirm the claim through the real IRS, Social Security, or government benefits portal you access yourself.",
        "If {keyword} appears in a government-related message, avoid urgent payments or identity sharing until you verify the notice independently.",
    ],
    "unknown-number": [
        "If this involves {keyword}, avoid replying, clicking, or calling back until you can confirm who contacted you and why.",
        "Before you respond to anything related to {keyword}, verify the sender or caller through an official source instead of the message itself.",
        "If {keyword} appears in an unexpected call or text, do not share personal information, money, or verification codes until you know exactly who is contacting you.",
    ],
    "phishing": [
        "If this involves {keyword}, do not use the link in the message to sign in or verify anything. Go to the official website or app directly instead.",
        "Before you respond to anything related to {keyword}, inspect the sender, domain, and page carefully and verify through the real service yourself.",
        "If {keyword} appears in a suspicious email or text, avoid downloads, logins, and code sharing until you confirm the source independently.",
    ],
    "general": [
        "If you received something related to {keyword}, slow down before clicking, replying, or paying. Always verify through the official website or app instead of using the message itself.",
        "Before you respond to anything related to {keyword}, pause and verify it through a trusted source you find yourself.",
        "If this involves {keyword}, avoid clicking links or sending money until you confirm it through the official platform.",
    ],
}

CONTEXT_EXAMPLES = {
    "payment": [
        "a PayPal refund email",
        "a bank fraud alert text",
        "an Amazon payment warning",
        "a Zelle transfer problem message",
    ],
    "job": [
        "a recruiter email",
        "a remote job offer",
        "an interview request text",
        "an onboarding payment request",
    ],
    "crypto": [
        "a wallet verification request",
        "a crypto recovery message",
        "an exchange support DM",
        "an airdrop or token claim link",
    ],
    "delivery": [
        "a USPS tracking text",
        "a FedEx delivery alert",
        "a UPS missed package message",
        "a customs fee link",
    ],
    "account-security": [
        "a login alert email",
        "a password reset message",
        "an account locked warning",
        "a two-factor code request",
    ],
    "government": [
        "an IRS warning",
        "a Social Security notice",
        "a tax refund message",
        "a benefits verification request",
    ],
    "unknown-number": [
        "a random text from an unknown number",
        "a strange callback request",
        "a spoofed-number voicemail",
        "an unexpected unknown caller message",
    ],
    "phishing": [
        "a fake login page",
        "a suspicious sign-in link",
        "a phishing email",
        "a copied account warning",
    ],
    "general": [
        "a suspicious message",
        "an unexpected email",
        "a strange text",
        "a suspicious link",
    ],
}

MODE_INTROS = {
    "direct": [
        "The main question is whether the message or request can be trusted.",
        "The safest way to evaluate it is to slow down and separate the claim from the pressure around it.",
        "Most scam checks start with the same question: does the situation hold up when you verify it independently?",
    ],
    "scenario": [
        "A common pattern starts when someone receives something that looks routine at first glance.",
        "Many people only realize the risk after the message creates just enough urgency to interrupt normal checking.",
        "This usually becomes dangerous when the message feels familiar enough to trust and urgent enough to rush.",
    ],
    "warning": [
        "This type of scam usually works by stacking multiple warning signs instead of relying on just one obvious red flag.",
        "The strongest clue is often not one detail, but the combination of pressure, impersonation, and verification shortcuts.",
        "What makes these scams effective is that the message often looks ordinary until you isolate the warning signs one by one.",
    ],
    "comparison": [
        "A legitimate version and a scam version of the same message often look similar on the surface but behave very differently once you verify them.",
        "The difference usually comes down to whether the sender is asking you to trust the message itself or verify the claim independently.",
        "A real notice usually survives independent verification, while a scam version usually depends on speed, pressure, or a fake link.",
    ],
    "breakdown": [
        "The easiest way to understand the risk is to break down how this scam usually unfolds step by step.",
        "Most versions follow a similar sequence: attention, urgency, action request, and then pressure before verification.",
        "When you map the scam flow instead of focusing only on the wording, the pattern becomes much easier to spot.",
    ],
}

BRAND_CASE = {
    "paypal": "PayPal",
    "whatsapp": "WhatsApp",
    "cash app": "Cash App",
    "tiktok": "TikTok",
    "icloud": "iCloud",
    "irs": "IRS",
    "usps": "USPS",
    "ups": "UPS",
    "fedex": "FedEx",
    "sms": "SMS",
    "otp": "OTP",
    "2fa": "2FA",
    "dm": "DM",
    "nft": "NFT",
    "ceo": "CEO",
    "binance": "Binance",
    "coinbase": "Coinbase",
    "metamask": "MetaMask",
    "trust wallet": "Trust Wallet",
    "google play": "Google Play",
    "zelle": "Zelle",
    "venmo": "Venmo",
    "amazon": "Amazon",
    "facebook": "Facebook",
    "facebook marketplace": "Facebook Marketplace",
    "instagram": "Instagram",
    "telegram": "Telegram",
    "snapchat": "Snapchat",
    "discord": "Discord",
    "crypto": "Crypto",
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "bank": "Bank",
    "bank of america": "Bank of America",
    "chase": "Chase",
    "wells fargo": "Wells Fargo",
    "social security": "Social Security",
    "google": "Google",
    "apple": "Apple",
    "microsoft": "Microsoft",
    "steam": "Steam",
    "walmart": "Walmart",
    "target": "Target",
    "two factor": "Two-Factor",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "vs", "with"
}

# -----------------------------
# HELPERS
# -----------------------------
def normalize_keyword(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip().lower())


def clean_base_keyword(text: str) -> str:
    kw = normalize_keyword(text)

    kw = re.sub(r"^\s*is\s+", "", kw)
    kw = re.sub(r"^\s*can\s+i\s+trust\s+", "", kw)
    kw = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+by\s+", "", kw)
    kw = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+on\s+", "", kw)
    kw = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+with\s+", "", kw)
    kw = re.sub(r"^\s*this\s+", "this ", kw)

    kw = re.sub(r"\s+a\s+scam$", "", kw)
    kw = re.sub(r"\s+or\s+legit$", "", kw)
    kw = re.sub(r"\s+or\s+scam$", "", kw)
    kw = re.sub(r"\s+legit$", "", kw)
    kw = re.sub(r"\s+real$", "", kw)
    kw = re.sub(r"\s+safe$", "", kw)
    kw = re.sub(r"\s+scam$", "", kw)

    kw = re.sub(r"\s+a$", "", kw)
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
    titled = []

    for i, word in enumerate(words):
        titled.append(word if i > 0 and word in SMALL_WORDS else word.capitalize())

    return apply_brand_case(" ".join(titled))


def variant_index(keyword: str, count: int) -> int:
    return sum(ord(c) for c in normalize_keyword(keyword)) % count if count else 0


def choose_mode(keyword: str) -> str:
    idx = variant_index(keyword, len(CONTENT_MODES))
    return CONTENT_MODES[idx]


def context_example(context: str, keyword: str) -> str:
    examples = CONTEXT_EXAMPLES.get(context, CONTEXT_EXAMPLES["general"])
    idx = variant_index(keyword, len(examples))
    return examples[idx]


def mode_intro_sentence(mode: str, keyword: str) -> str:
    options = MODE_INTROS.get(mode, MODE_INTROS["direct"])
    idx = variant_index(keyword + mode, len(options))
    return options[idx]


def strip_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</li\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>", "- ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def dedupe_preserve_order(items):
    seen = set()
    result = []
    for item in items:
        key = normalize_keyword(item)
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def safe_json(response: requests.Response):
    try:
        return response.json()
    except ValueError as e:
        snippet = response.text[:200].replace("\n", " ").strip()
        raise ValueError(f"Invalid JSON response: {snippet}") from e


def clean_text(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", "", text, flags=re.IGNORECASE | re.DOTALL)
    return text.strip()


# -----------------------------
# INTENT / CONTEXT
# -----------------------------
def detect_intent(keyword: str) -> str:
    kw = normalize_keyword(keyword)

    if kw.startswith(("is ", "can ", "did ", "should ", "was ")):
        return "question"
    if kw.startswith("how to ") or kw.startswith("what to do") or kw.startswith("check "):
        return "action"
    if kw.startswith(("i clicked ", "i replied ", "i opened ")):
        return "post-action"
    return "entity"


def detect_context(keyword: str) -> str:
    kw = normalize_keyword(keyword)

    if any(x in kw for x in [
        "verification code", "two factor", "security code", "login", "account verification",
        "password reset", "account suspended", "account locked", "unusual activity",
        "security alert", "verification email", "login alert", "password reset email",
        "support team", "customer support", "account support"
    ]):
        return "account-security"

    if any(x in kw for x in ["phishing", "fake website", "suspicious link", "malicious link"]):
        return "phishing"

    if any(x in kw for x in ["amazon", "paypal", "bank", "zelle", "venmo", "cash app", "cash-app", "wire transfer", "bank transfer", "payment request", "refund notice", "invoice"]):
        return "payment"

    if any(x in kw for x in ["job", "hiring", "offer", "recruiter", "interview", "onboarding", "work from home", "remote job"]):
        return "job"

    if any(x in kw for x in ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft", "trading platform", "crypto payment"]):
        return "crypto"

    if any(x in kw for x in ["usps", "fedex", "ups", "delivery", "package", "parcel", "shipment", "tracking number", "missed delivery"]):
        return "delivery"

    if any(x in kw for x in ["irs", "tax refund", "social security", "government benefits", "government"]):
        return "government"

    if any(x in kw for x in ["unknown number", "random text", "unknown caller", "blocked number", "spoofed number", "phone call", "voicemail"]):
        return "unknown-number"

    return "general"


# -----------------------------
# SMART INTRO
# -----------------------------
def intro_paragraph(raw_keyword: str, display_kw: str, mode: str) -> str:
    keyword_title = title_case(display_kw)
    intent = detect_intent(raw_keyword)
    context = detect_context(raw_keyword)
    example = context_example(context, raw_keyword)
    mode_sentence = mode_intro_sentence(mode, raw_keyword)

    if intent == "post-action":
        return (
            f"<p>If you already interacted with something related to {keyword_title}, the most important step is to slow down and verify what happened before taking any further action. {mode_sentence} Many scams rely on panic after a click, reply, login, or payment, so a calm check can help limit damage and keep you from taking the next risky step.</p>"
        )

    if intent == "question":
        if context == "job":
            return (
                f"<p>{keyword_title} is a common question when something like {example} feels too fast, too vague, or too good to be true. {mode_sentence} In many cases, the answer comes down to whether the sender, company, pay, and hiring process can be verified independently.</p>"
            )
        if context == "delivery":
            return (
                f"<p>{keyword_title} is a common question when something like {example} looks urgent but feels slightly off. {mode_sentence} The safest way to judge it is to ignore the message link and verify the shipment directly through the real carrier or merchant.</p>"
            )
        if context == "crypto":
            return (
                f"<p>{keyword_title} is a common question when something like {example} creates urgency around crypto. {mode_sentence} These scams often depend on speed, trust, and technical confusion to push people into approving actions too quickly.</p>"
            )
        if context == "account-security":
            return (
                f"<p>{keyword_title} is a common question when something like {example} appears without context. {mode_sentence} These messages often look routine, but they may be designed to capture your credentials or verification codes before you check the real account yourself.</p>"
            )
        return (
            f"<p>{keyword_title} is a common question when something like {example} feels suspicious. {mode_sentence} In many cases, the answer comes down to warning signs like urgency, unusual payment requests, suspicious links, or pressure to act before you can verify what is happening.</p>"
        )

    if intent == "action":
        return (
            f"<p>If you are trying to handle {keyword_title}, move carefully. {mode_sentence} Scams often work by pushing people to react fast, so taking a moment to verify the source can help you avoid clicking, replying, paying, or sharing information too soon.</p>"
        )

    if context == "job":
        return (
            f"<p>{keyword_title} scams often look like ordinary recruiter outreach, remote job offers, interview requests, or onboarding messages at first glance, including things like {example}. {mode_sentence} The real goal is usually to collect personal information, push you into paying upfront, or move you into an unofficial hiring process before you can verify the employer.</p>"
        )

    if context == "delivery":
        return (
            f"<p>{keyword_title} scams often arrive as normal-looking package alerts, tracking problems, or delivery updates, such as {example}. {mode_sentence} They are designed to feel routine, but the real objective is often to get you to click a link, enter details, or pay a small fee before you verify whether the shipment issue is real.</p>"
        )

    if context == "crypto":
        return (
            f"<p>{keyword_title} scams are built to look credible to people already thinking about exchanges, wallets, investments, or account recovery, including requests like {example}. {mode_sentence} They often create urgency around access, profit, or security so you act before carefully verifying the request.</p>"
        )

    if context == "account-security":
        return (
            f"<p>{keyword_title} scams are designed to imitate normal account activity like login alerts, verification requests, password resets, or support messages, including things like {example}. {mode_sentence} The real goal is often to capture credentials, one-time codes, or identity details before you check the official account directly.</p>"
        )

    return (
        f"<p>{keyword_title} scams are designed to look believable at first glance. Messages like {example} often arrive as ordinary alerts, emails, or requests. {mode_sentence} The real goal is to create pressure and get you to act before you stop to verify the details.</p>"
    )


# -----------------------------
# SCENARIO
# -----------------------------
def scenario_paragraph(raw_keyword: str, display_kw: str, mode: str) -> str:
    keyword_title = title_case(display_kw)
    context = detect_context(raw_keyword)
    example = context_example(context, raw_keyword)

    if mode == "comparison":
        if context == "delivery":
            return (
                f"<p>A legitimate delivery notice usually appears in the real carrier app or on the official tracking page, while a scam version often starts with something like {example} and pushes you toward a message link, a small fee, or a rushed address update.</p>"
            )
        if context == "payment":
            return (
                f"<p>A real payment alert usually survives independent checking inside the official app, while a scam version often starts with something like {example} and pressures you to sign in, approve a change, or call a fake support line before you verify anything yourself.</p>"
            )
        if context == "job":
            return (
                f"<p>A real hiring process usually includes a verifiable company, consistent recruiter identity, and normal interview steps, while a scam version often starts with something like {example} and rushes toward personal data, fees, or off-platform contact.</p>"
            )
        return (
            f"<p>A legitimate version of this kind of message usually holds up when you verify it independently, while a scam version often starts with something like {example} and then depends on urgency, fear, or confusion to keep you inside the message itself.</p>"
        )

    if mode == "breakdown":
        if context == "crypto":
            return (
                f"<p>A common {keyword_title} flow starts with attention from something like {example}, moves into urgency about access, recovery, or profit, and then ends with a request to connect a wallet, approve a transaction, or trust an unofficial support contact.</p>"
            )
        if context == "account-security":
            return (
                f"<p>A common {keyword_title} flow starts with something like {example}, creates urgency around account access, and then tries to move you onto a fake page or into sharing codes before you check the real service yourself.</p>"
            )
        return (
            f"<p>A common {keyword_title} flow starts with something like {example}, builds trust with familiar wording, and then introduces urgency or a request for action before you can verify the situation independently.</p>"
        )

    if context == "payment":
        return (
            f"<p>A common {keyword_title} scenario starts with something like {example}, or with a message about an account issue, payment problem, suspicious login, refund, charge, or urgent verification request. The goal is often to make you click a link, sign in on a fake page, confirm personal details, or send money before you realize the message is not legitimate.</p>"
        )

    if context == "job":
        return (
            f"<p>A typical {keyword_title} case may involve something like {example}, a job offer that feels unusually fast, easy, or high-paying, or a request for personal details, upfront fees, equipment payments, identity documents, or pressure to move the conversation off a trusted platform.</p>"
        )

    if context == "crypto":
        return (
            f"<p>Many {keyword_title} scams involve things like {example}, fake investment opportunities, support impersonation, wallet connections, account recovery offers, staking claims, or promises of guaranteed returns. The real objective is often to get access to your funds, wallet, login, or transaction approvals.</p>"
        )

    if context == "delivery":
        return (
            f"<p>A common {keyword_title} message claims there is a shipping problem, missed delivery, address issue, customs fee, or tracking error, often through something like {example}. These messages usually try to push you into clicking a link or paying a small amount before you verify whether the delivery issue is real.</p>"
        )

    if context == "account-security":
        return (
            f"<p>In many {keyword_title} cases, the message starts with something like {example} and claims there was unusual activity, a login issue, an account lock, or a password problem that needs immediate attention. The scam works by making the warning feel routine enough to trust and urgent enough to stop you from checking the real account first.</p>"
        )

    if context == "government":
        return (
            f"<p>A common {keyword_title} scenario uses fear, urgency, or the promise of money to get a fast response, often through something like {example}. It may mention taxes, benefits, refunds, penalties, identity confirmation, or account issues, but the real goal is often to capture personal details or pressure you into payment before you verify the claim independently.</p>"
        )

    if context == "unknown-number":
        return (
            f"<p>A common {keyword_title} situation begins with something like {example}. The message may stay vague at first, then quickly move toward links, callbacks, money, codes, or personal information once it gets your attention.</p>"
        )

    if context == "phishing":
        return (
            f"<p>Many {keyword_title} scams imitate a real company, account warning, delivery notice, support message, or security alert, often through something like {example}. The message is usually designed to get you onto a fake page where your login details, payment information, or verification codes can be captured.</p>"
        )

    return (
        f"<p>In many {keyword_title} situations, the message is written to build trust and urgency at the same time. Something like {example} may sound routine, but it is often trying to get quick access to your information, money, or account before you can slow down and verify it.</p>"
    )


# -----------------------------
# STRUCTURE HELPERS
# -----------------------------
def get_warning_bullets(context: str, idx: int):
    if context in CONTEXT_WARNING_BULLETS:
        return CONTEXT_WARNING_BULLETS[context][idx]
    return GENERIC_WARNING_BULLET_SETS[idx]


def get_action_paragraph(context: str, idx: int, keyword_title: str):
    paragraphs = ACTION_PARAGRAPHS_BY_CONTEXT.get(context, ACTION_PARAGRAPHS_BY_CONTEXT["general"])
    return paragraphs[idx].format(keyword=keyword_title)


def context_detail_paragraph(raw_keyword: str, display_kw: str, mode: str) -> str:
    keyword_title = title_case(display_kw)
    context = detect_context(raw_keyword)
    example = context_example(context, raw_keyword)

    if mode == "warning":
        return (
            f"<p>The strongest clue is usually not one isolated detail. With {keyword_title}, the risk often becomes clearer when something like {example} is combined with urgency, a shortcut to payment or login, and pressure to trust the message instead of verifying outside it.</p>"
        )

    if mode == "comparison":
        return (
            f"<p>That difference matters because a real notice related to {keyword_title} should still make sense after you verify it through the official site, app, support channel, or account portal. A scam version usually becomes weaker the moment you stop relying on the message itself.</p>"
        )

    if mode == "breakdown":
        return (
            f"<p>This is why step-by-step checking matters. Once a message related to {keyword_title} moves from attention to urgency to action, the safest move is to interrupt that sequence and confirm the claim independently before the scam reaches the point of payment, login, or code theft.</p>"
        )

    if context == "payment":
        return (
            f"<p>Payment-related scams connected to {keyword_title} often try to replace a normal account check with a message-based shortcut. Instead of trusting the alert itself, the safer move is to open the real app or site yourself and confirm whether any payment issue actually exists, especially when something like {example} is involved.</p>"
        )
    if context == "job":
        return (
            f"<p>Job-related scams connected to {keyword_title} often break normal hiring patterns. Real employers usually have a verifiable company presence, a clear role, and a consistent interview process, while scam messages often stay vague until they ask for money, documents, or account details, especially after something like {example} appears.</p>"
        )
    if context == "crypto":
        return (
            f"<p>Crypto-related scams connected to {keyword_title} often succeed by making risky actions feel routine. A message may talk about support, recovery, verification, or returns, but the safest habit is to independently confirm the platform, domain, and wallet action before doing anything irreversible, especially if it begins with something like {example}.</p>"
        )
    if context == "delivery":
        return (
            f"<p>Delivery-related scams connected to {keyword_title} usually work because the request seems small and ordinary. Even a minor fee or simple address update can be enough to collect payment information or redirect you to a fake page, which is why independent tracking checks matter when something like {example} appears.</p>"
        )
    if context == "account-security":
        return (
            f"<p>Account-security scams connected to {keyword_title} are effective because the warning often sounds familiar. A fake alert may mention a password reset, unusual login, or account problem, but the safest response is always to open the real service directly rather than rely on the message link, especially if it begins with something like {example}.</p>"
        )
    if context == "government":
        return (
            f"<p>Government-related scams connected to {keyword_title} often use the appearance of authority to push fast decisions. That is why it is important to verify any claim directly through the official agency website or number instead of trusting the message on its own, especially when something like {example} is used to create urgency.</p>"
        )
    if context == "unknown-number":
        return (
            f"<p>Unknown-number scams connected to {keyword_title} often begin with very little detail because the first goal is simply to get a response. Once a person replies, scammers may shift the conversation toward links, payment requests, verification codes, or impersonation tactics, especially after something like {example} gets your attention.</p>"
        )
    if context == "phishing":
        return (
            f"<p>Phishing-related scams connected to {keyword_title} often depend on visual familiarity. The message, sender name, or page may look close enough to the real thing that the safest move is to ignore the embedded link and navigate to the official site on your own, especially when something like {example} is used to build trust.</p>"
        )

    return (
        f"<p>Scams connected to {keyword_title} often work because they combine ordinary wording with pressure. That mix can make a message feel routine enough to trust and urgent enough to act on before independently checking the details, especially when something like {example} is used as the starting point.</p>"
    )


# -----------------------------
# STRUCTURE
# -----------------------------
def enforce_structure(raw_keyword: str, display_kw: str, content: str) -> str:
    keyword_title = title_case(display_kw)
    context = detect_context(raw_keyword)
    mode = choose_mode(raw_keyword)
    idx = variant_index(display_kw + mode, len(WARNING_SECTION_TITLES))

    intro = intro_paragraph(raw_keyword, display_kw, mode)
    scenario = scenario_paragraph(raw_keyword, display_kw, mode)
    detail = context_detail_paragraph(raw_keyword, display_kw, mode)

    warning_title = WARNING_SECTION_TITLES[idx]
    action_title = ACTION_SECTION_TITLES[idx]
    action_intro = ACTION_SECTION_INTROS[idx]
    bullets = get_warning_bullets(context, idx)
    action = get_action_paragraph(context, idx, keyword_title)

    bullet_html = "\n".join(f"<li>{b}</li>" for b in bullets)

    if mode == "comparison":
        middle_heading = "How Legitimate And Scam Versions Usually Differ"
    elif mode == "breakdown":
        middle_heading = "How This Scam Pattern Usually Unfolds"
    elif mode == "warning":
        middle_heading = "Why The Warning Signs Matter"
    elif mode == "scenario":
        middle_heading = "How This Situation Usually Plays Out"
    else:
        middle_heading = "What This Scam Pattern Usually Looks Like"

    return f"""
<div class="content-block" data-context="{context}" data-mode="{mode}">
{intro}
<h2>{middle_heading}</h2>
{scenario}
{content}
{detail}
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
# MAIN
# -----------------------------
def generate_content(keyword: str) -> str:
    raw_keyword = normalize_keyword(keyword)
    display_kw = display_keyword(raw_keyword)

    if not display_kw:
        raise ValueError("Empty keyword after normalization")

    logging.info("Generating content for: %s", raw_keyword)

    payload_variants = dedupe_preserve_order([
        raw_keyword,
        display_kw,
        title_case(display_kw),
        f"is {display_kw} a scam" if display_kw and not raw_keyword.startswith("is ") else raw_keyword,
        f"{display_kw} legit or scam" if display_kw and "legit" not in raw_keyword and "scam" not in raw_keyword else raw_keyword,
    ])

    last_error = None

    for prompt_keyword in payload_variants:
        try:
            res = requests.post(
                f"{RAILWAY_API}/seo-content",
                json={"keyword": prompt_keyword},
                timeout=TIMEOUT
            )
            res.raise_for_status()

            data = safe_json(res)
            raw = str(data.get("content", "")).strip()

            if not raw:
                last_error = ValueError(f"Empty content for prompt: {prompt_keyword}")
                continue

            cleaned = clean_text(raw)
            final_content = cleaned if cleaned else raw

            return enforce_structure(raw_keyword, display_kw, final_content)

        except Exception as e:
            last_error = e
            logging.warning("AI generation failed for %s using prompt '%s': %s", raw_keyword, prompt_keyword, e)

    raise ValueError(f"AI generation failed for '{raw_keyword}': {last_error}")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    keyword = sys.argv[1] if len(sys.argv) > 1 else "amazon scam"
    print(generate_content(keyword))