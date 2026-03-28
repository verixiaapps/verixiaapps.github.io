import os
import re
import sys
import json
from collections import Counter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.cluster_map import CLUSTERS

KEYWORDS_FILE = "data/generated_keywords.txt"
OUTPUT_DIR = "scam-check-now"
SITE = "https://verixiaapps.com"
MAX_LINKS_PER_HUB = 50
TOP_SCAM_TYPES_COUNT = 8
MIN_LINKS_TO_BUILD_HUB = 5
MAX_RELATED_TOPICS = 10
MAX_FAQS = 4
REPORT_PATH = os.path.join(OUTPUT_DIR, "_hub_build_report.json")

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
    "cash": "Cash",
    "zelle": "Zelle",
    "venmo": "Venmo",
    "amazon": "Amazon",
    "facebook": "Facebook",
    "instagram": "Instagram",
    "telegram": "Telegram",
    "snapchat": "Snapchat",
    "discord": "Discord",
    "crypto": "Crypto",
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "bank": "Bank",
    "chase": "Chase",
    "wells fargo": "Wells Fargo",
    "social security": "Social Security",
    "google": "Google",
    "apple": "Apple",
    "microsoft": "Microsoft",
    "steam": "Steam",
    "walmart": "Walmart",
    "target": "Target",
}

SMALL_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on",
    "or", "the", "to", "vs", "with"
}

STOPWORDS_FOR_VARIATIONS = {
    "is", "this", "a", "an", "the", "or", "and", "to", "for", "of", "in",
    "on", "by", "with", "from", "safe", "legit", "review", "warning", "risk",
    "scam", "scams", "message", "messages", "email", "emails", "text", "texts",
    "link", "links", "offer", "offers", "request", "requests", "alert", "alerts",
    "check", "full", "updated", "real", "common"
}

LOW_SIGNAL_VARIATION_WORDS = {
    "fake", "urgent", "suspicious", "random", "unknown", "new"
}

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
    "phishing-scams": "Phishing scams often use fake login pages, email warnings, security alerts, or account verification requests to steal credentials.",
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
    "phishing-scams": "Phishing Scams: Warning Signs, Related Checks & What To Do",
}

HUB_META_DESCRIPTIONS = {
    "amazon-scams": "Review common Amazon scam patterns, warning signs, and related scam checks. Learn what fake Amazon alerts, refunds, and delivery scams often look like.",
    "paypal-scams": "Review common PayPal scam patterns, fake invoices, payment alerts, and refund tricks. Compare related PayPal scam checks and warning signs.",
    "zelle-scams": "Explore common Zelle scam patterns, fake payment issues, reversal claims, and impersonation tricks. Review related Zelle scam checks and warning signs.",
    "cash-app-scams": "Review common Cash App scam patterns, fake payment notices, support impersonation, and refund tricks. Compare related Cash App scam checks.",
    "venmo-scams": "Explore common Venmo scam patterns, fake payments, accidental transfer stories, and impersonation tricks. Review related Venmo scam checks and warnings.",
    "facebook-scams": "Review common Facebook scam patterns, Marketplace tricks, fake buyer messages, phishing links, and impersonation attempts. Compare related scam checks.",
    "instagram-scams": "Explore common Instagram scam patterns, phishing links, impersonation, fake outreach, and account warning messages. Review related scam checks.",
    "tiktok-scams": "Review common TikTok scam patterns, phishing messages, fake promotions, suspicious links, and payment tricks. Compare related TikTok scam checks.",
    "whatsapp-scams": "Explore common WhatsApp scam patterns, impersonation, unknown numbers, fake support, and suspicious links. Review related WhatsApp scam checks.",
    "telegram-scams": "Review common Telegram scam patterns, fake investment groups, impersonation, phishing links, and payment pressure. Compare related Telegram scam checks.",
    "snapchat-scams": "Explore common Snapchat scam patterns, impersonation, fake alerts, suspicious links, and payment pressure. Review related Snapchat scam checks.",
    "discord-scams": "Review common Discord scam patterns, fake Nitro offers, phishing links, suspicious downloads, and takeover tricks. Compare related Discord scam checks.",
    "crypto-scams": "Explore common crypto scam patterns, fake investments, wallet tricks, phishing links, and urgent transfer requests. Review related crypto scam checks.",
    "package-delivery-scams": "Review common package delivery scam patterns, fake USPS, UPS, and FedEx alerts, suspicious links, and payment requests. Compare related scam checks.",
    "bank-scams": "Explore common bank scam patterns, fake fraud alerts, account lock notices, payment issues, and impersonation tactics. Review related bank scam checks.",
    "job-scams": "Review common job scam patterns, fake recruiters, interview messages, remote job offers, and payment requests. Compare related job scam checks.",
    "investment-scams": "Explore common investment scam patterns, fake returns, urgent opportunities, guaranteed profits, and pressure tactics. Review related scam checks.",
    "loan-scams": "Review common loan scam patterns, fake approvals, urgent verification requests, suspicious lenders, and upfront fee tricks. Compare related scam checks.",
    "credit-scams": "Explore common credit scam patterns, fake repair offers, urgent notices, phishing attempts, and sensitive data requests. Review related scam checks.",
    "romance-scams": "Review common romance scam patterns, emotional manipulation, gift requests, money pressure, and trust-building tactics. Compare related scam checks.",
    "gift-card-scams": "Explore common gift card scam patterns, fake emergencies, urgent payment pressure, impersonation, and support tricks. Review related scam checks.",
    "urgent-payment-scams": "Review common urgent payment scam patterns, fear tactics, time pressure, and fast-transfer requests. Compare related urgent payment scam checks.",
    "government-scams": "Explore common government scam patterns, IRS threats, Social Security impersonation, tax scams, and benefits fraud. Review related scam checks.",
    "unknown-number-scams": "Review common unknown number scam patterns, suspicious texts, unexpected calls, curiosity hooks, and fast-reply traps. Compare related scam checks.",
    "verification-code-scams": "Explore common verification code scam patterns, one-time code theft, login approval tricks, and account access scams. Review related scam checks.",
    "phishing-scams": "Review common phishing scam patterns, fake login pages, account alerts, email warnings, and credential theft attempts. Compare related scam checks.",
}

HUB_WARNING_BULLETS = {
    "amazon-scams": [
        "Fake Amazon account, order, refund, or delivery alerts designed to create urgency",
        "Links that lead to fake login pages or suspicious checkout and payment screens",
        "Gift card or payment requests that bypass normal Amazon account flows",
        "Messages that pressure you to act before verifying through the official Amazon site or app",
    ],
    "paypal-scams": [
        "Fake PayPal invoices, payment alerts, refund messages, or account warning emails",
        "Pressure to click a link and log in before verifying directly inside your PayPal account",
        "Requests to call fake support numbers or approve payments you did not expect",
        "Urgent wording designed to stop you from checking the official PayPal website or app first",
    ],
    "zelle-scams": [
        "Urgent transfer or payment issue claims that pressure you to send money quickly",
        "Fake reversal, refund, or business account stories designed to confuse the target",
        "Impersonation of banks, buyers, sellers, or support agents asking for immediate action",
        "Requests that move the conversation away from normal verification channels",
    ],
    "cash-app-scams": [
        "Fake payment notices, pending transfer stories, or support impersonation messages",
        "Pressure to issue refunds, send money back, or trust screenshots without verification",
        "Urgent payment instructions that bypass normal Cash App account review",
        "Messages that create confusion before you can verify the balance or activity directly",
    ],
    "venmo-scams": [
        "Fake payments, accidental transfer claims, or support impersonation messages",
        "Pressure to refund money or trust a screenshot instead of checking Venmo directly",
        "Buyer-seller stories designed to rush you into paying or sending money back",
        "Messages that push quick action before you verify the payment inside the real app",
    ],
    "facebook-scams": [
        "Marketplace buyer or seller messages that pressure payment, shipping, or identity sharing",
        "Fake account alerts, impersonation, or suspicious support-style messages",
        "Links that lead to fake login pages, phishing forms, or off-platform payment traps",
        "Urgency designed to keep the target from verifying directly inside Facebook",
    ],
    "instagram-scams": [
        "Phishing links, fake brand messages, impersonation attempts, or account warning alerts",
        "Suspicious outreach that pressures fast replies, verification, or money transfers",
        "Messages that try to move the conversation off-platform before trust is established",
        "Urgency designed to make you act before checking through the official Instagram app",
    ],
    "tiktok-scams": [
        "Fake promotion messages, account warnings, suspicious links, or impersonation attempts",
        "Urgent requests that push you to log in, verify, or pay outside normal TikTok flows",
        "Messages that sound official but do not come through trusted support channels",
        "Pressure designed to stop you from verifying the claim directly in the app",
    ],
    "whatsapp-scams": [
        "Unknown numbers, impersonation attempts, fake support, or payment pressure messages",
        "Suspicious links that lead to fake login pages, payment traps, or phishing forms",
        "Messages that create urgency, fear, or confusion to get a fast reply",
        "Requests for codes, money, or private information without proper verification",
    ],
    "telegram-scams": [
        "Fake investment groups, impersonation, suspicious links, or urgent payment requests",
        "Messages that promise easy profits or pressure you into moving funds quickly",
        "Fake admins or support accounts trying to build trust before making a request",
        "Links and messages designed to bypass careful verification",
    ],
    "snapchat-scams": [
        "Impersonation attempts, suspicious links, fake alerts, or payment pressure",
        "Messages that try to build trust fast and then ask for money or access",
        "Unexpected requests that move outside normal Snapchat activity",
        "Urgency designed to keep you from stopping to verify what is happening",
    ],
    "discord-scams": [
        "Fake Nitro offers, suspicious downloads, impersonation, or phishing links",
        "Messages that look official but push you outside trusted Discord flows",
        "Urgent account or support stories designed to create panic and fast action",
        "Requests that aim to steal credentials, downloads, or account access",
    ],
    "crypto-scams": [
        "Fake investment promises, suspicious wallet requests, phishing links, or support impersonation",
        "Urgent transfer instructions designed to move funds before you verify the situation",
        "Messages that promise guaranteed returns, recoveries, or exclusive opportunities",
        "Requests for wallet access, seed phrases, or approvals that should never be shared",
    ],
    "package-delivery-scams": [
        "Fake USPS, FedEx, or UPS alerts claiming delivery issues, customs fees, or address problems",
        "Suspicious links that lead to fake tracking pages, payment prompts, or phishing forms",
        "Urgency designed to push a quick click before you verify the delivery independently",
        "Requests for small payments or personal details tied to a fake shipping problem",
    ],
    "bank-scams": [
        "Fake fraud alerts, account lock messages, suspicious login warnings, or payment issues",
        "Pressure to verify through a link instead of the official bank website or app",
        "Impersonation of bank staff, fraud teams, or customer support representatives",
        "Urgency designed to stop you from calling the bank directly through a trusted number",
    ],
    "job-scams": [
        "Fake recruiter outreach, remote job offers, interview requests, or onboarding messages",
        "Pressure to move quickly, share personal details, or pay for equipment or verification",
        "Offers that seem unusually fast, easy, or high-paying without normal screening",
        "Requests that move off trusted platforms before legitimacy is confirmed",
    ],
    "investment-scams": [
        "Promises of guaranteed profits, insider opportunities, or urgent high-return offers",
        "Pressure to send money quickly before you can verify the person or platform",
        "Messages that sound sophisticated but avoid clear, independent proof",
        "Tactics that exploit greed, urgency, or fear of missing out",
    ],
    "loan-scams": [
        "Fake loan approvals, urgent verification requests, suspicious lenders, or upfront fees",
        "Pressure to pay before funds are released or legitimacy is confirmed",
        "Messages that request sensitive information too early in the process",
        "Urgency designed to bypass normal checks and independent verification",
    ],
    "credit-scams": [
        "Fake credit repair offers, urgent notices, phishing attempts, or account scare tactics",
        "Requests for sensitive details that should only be shared through trusted channels",
        "Messages that create pressure before you verify the sender independently",
        "Claims that sound official but do not match normal credit or lender processes",
    ],
    "romance-scams": [
        "Fast emotional bonding followed by requests for money, gifts, or account help",
        "Stories that create sympathy, urgency, or pressure before trust is properly earned",
        "Attempts to move conversations away from safer channels or normal verification",
        "Requests that escalate from emotional dependence into financial pressure",
    ],
    "gift-card-scams": [
        "Urgent payment pressure involving gift cards because they are hard to recover",
        "Impersonation of employers, family, support, or trusted companies asking for codes",
        "Emergency stories designed to stop you from checking independently",
        "Requests for gift card numbers or photos before legitimacy is confirmed",
    ],
    "urgent-payment-scams": [
        "Pressure to send money immediately before checking details independently",
        "Fear-based messages that reduce thinking time and increase emotional reaction",
        "Requests that bypass normal payment verification or business process",
        "Urgency designed to stop you from calling, checking, or confirming the story first",
    ],
    "government-scams": [
        "Impersonation of the IRS, Social Security, tax agencies, or benefits programs",
        "Threats, fear-based warnings, or fake deadlines designed to force fast action",
        "Requests for payments, codes, or private details outside normal official channels",
        "Urgency that discourages calling the real agency directly for verification",
    ],
    "unknown-number-scams": [
        "Unexpected calls or texts designed to create curiosity, urgency, or emotional reaction",
        "Vague stories that push you to reply before you understand what is happening",
        "Suspicious links or requests that arrive before any trust is established",
        "Pressure to continue the conversation without independent verification",
    ],
    "verification-code-scams": [
        "Requests for one-time codes, login approvals, or security verification details",
        "Messages that pretend the code is harmless when it could unlock an account",
        "Urgency designed to make you share a code before you stop to think",
        "Attempts to hide the real purpose of the code request",
    ],
    "phishing-scams": [
        "Fake login pages, account alerts, security warnings, or verification requests",
        "Links that imitate trusted brands but lead to credential theft pages",
        "Urgent wording designed to keep you from verifying the sender independently",
        "Requests for passwords, codes, or login details outside official channels",
    ],
}

HUB_FAQS = {
    "amazon-scams": [
        ("What does an Amazon scam usually look like?", "Amazon scams often appear as fake order problems, refund notices, account warnings, delivery issues, or gift card requests that create urgency."),
        ("How should you verify an Amazon message?", "Open the official Amazon app or website yourself and check your account there instead of using links, phone numbers, or instructions from the message."),
    ],
    "paypal-scams": [
        ("What does a PayPal scam usually look like?", "PayPal scams often show up as fake invoices, suspicious payment alerts, refund claims, or urgent account warning emails."),
        ("How should you verify a PayPal alert?", "Sign in through the real PayPal website or app directly and review your actual account activity before taking action."),
    ],
    "crypto-scams": [
        ("What makes crypto scams dangerous?", "Crypto scams often combine urgency, fake returns, impersonation, and wallet access requests, and many transfers are difficult or impossible to reverse."),
        ("What should you never share in a crypto scam situation?", "Never share your seed phrase, private keys, wallet approvals, or recovery codes with anyone."),
    ],
    "job-scams": [
        ("What are common job scam signs?", "Common job scam signs include fast offers, high pay with little screening, requests for fees or equipment purchases, and pressure to move off trusted platforms."),
        ("How do you verify a recruiter or job offer?", "Check the company site yourself, verify the recruiter identity independently, and avoid paying money or sharing sensitive data before legitimacy is confirmed."),
    ],
    "phishing-scams": [
        ("What is phishing?", "Phishing is a scam tactic that uses fake login pages, suspicious links, and urgent alerts to trick people into giving away account credentials or other sensitive information."),
        ("How do you avoid phishing?", "Do not click links from suspicious messages. Go directly to the official website or app yourself and verify the claim there."),
    ],
}

GENERIC_FAQS = [
    ("What are the biggest scam warning signs?", "The biggest scam warning signs are urgency, suspicious links, requests for money or codes, impersonation, and pressure to act before verifying independently."),
    ("What should you do if something seems suspicious?", "Do not rely on the message itself. Go to the official website, app, or verified support channel directly and confirm the situation there before taking action."),
]

HUB_VERIFY_STEPS = {
    "amazon-scams": [
        "Open the official Amazon app or website directly instead of using the message link.",
        "Check real orders, refunds, messages, and account notices inside your account.",
        "Ignore gift card, wire, or unusual payment requests that do not match normal Amazon flows.",
    ],
    "paypal-scams": [
        "Sign in to PayPal directly and review actual invoices, payments, and account notices.",
        "Do not call phone numbers or click links inside suspicious emails first.",
        "Verify whether the payment, invoice, or refund message appears in your real account.",
    ],
    "zelle-scams": [
        "Check your actual bank account and transfer history directly through your bank.",
        "Do not trust screenshots, overpayment stories, or urgent reversal claims.",
        "Confirm any payment issue through the real bank or app before sending anything.",
    ],
    "crypto-scams": [
        "Verify the domain, wallet request, and project identity independently.",
        "Never share seed phrases, private keys, or recovery codes.",
        "Slow down before approving wallet permissions, transfers, or support requests.",
    ],
    "job-scams": [
        "Verify the company website, recruiter identity, and real hiring process independently.",
        "Do not pay for equipment, onboarding, certification, or background checks upfront.",
        "Be cautious if the offer moves unusually fast or shifts to private channels too early.",
    ],
}

HUB_HOW_IT_WORKS = {
    "amazon-scams": "These scams usually mimic normal Amazon trust signals first, then introduce urgency around account access, deliveries, refunds, or gift cards so the target reacts before verifying.",
    "paypal-scams": "These scams often look believable because they use payment language, invoice formatting, and refund urgency to make the target feel they need to act immediately.",
    "zelle-scams": "These scams work by creating confusion around payment status, reversals, business account claims, or buyer-seller pressure so the victim sends money before checking carefully.",
    "crypto-scams": "These scams usually rely on urgency, technical confusion, fake authority, and irreversible transfers to push victims into wallet approvals or direct payments.",
    "job-scams": "These scams typically start with excitement and speed, then shift into requests for money, sensitive data, or off-platform communication before legitimacy is established.",
}

HUB_TARGETING = {
    "amazon-scams": "They often target online shoppers, delivery recipients, and people used to seeing frequent account or shipping notifications.",
    "paypal-scams": "They often target buyers, sellers, freelancers, and anyone who regularly receives payment alerts or invoices.",
    "zelle-scams": "They often target marketplace buyers and sellers, people sending peer payments, and anyone under time pressure during a transaction.",
    "crypto-scams": "They often target newer crypto users, people seeking fast gains, and anyone under pressure to recover funds or act on a supposedly exclusive opportunity.",
    "job-scams": "They often target job seekers who are moving quickly, applying broadly, or hoping for remote work and fast hiring.",
}

INTRO_FALLBACK = (
    "This page groups together related scam checks so you can review warning signs, "
    "compare patterns, and navigate related pages more easily."
)

META_FALLBACK = (
    "Review related scam checks, compare warning signs, and learn what to do next "
    "before you click, reply, send money, or share information."
)

GENERIC_ENTITY_WORDS = {
    "scam", "scams", "message", "messages", "email", "emails", "text", "texts",
    "link", "links", "offer", "offers", "request", "requests", "alert", "alerts",
    "review", "warning", "risk", "safe", "legit", "fake", "urgent", "updated",
    "common", "check", "real", "new", "random", "unknown", "what", "how",
    "why", "is", "this", "a", "an", "the", "for", "to", "from", "with",
    "account", "accounts", "support", "customer", "service", "team", "notice",
    "notices", "security", "verification", "login", "payment", "payments",
    "refund", "refunds", "delivery", "problem", "problems", "issue", "issues",
    "notification", "notifications", "center", "code", "codes", "access",
    "update", "updates", "official", "suspicious", "reply", "click", "money",
    "details", "information", "website", "websites", "page", "pages"
}

CHANNEL_HINTS = {
    "email": "email",
    "emails": "email",
    "text": "text",
    "texts": "text",
    "sms": "text",
    "message": "message",
    "messages": "message",
    "call": "call",
    "calls": "call",
    "phone": "call",
    "voicemail": "call",
    "link": "link",
    "links": "link",
    "website": "website",
    "websites": "website",
    "login": "login",
    "invoice": "invoice",
    "invoices": "invoice",
    "payment": "payment",
    "payments": "payment",
    "refund": "refund",
    "refunds": "refund",
    "delivery": "delivery",
    "package": "delivery",
    "packages": "delivery",
    "job": "job",
    "jobs": "job",
    "recruiter": "job",
    "recruiters": "job",
}

PRESSURE_HINTS = {
    "urgent": "urgency",
    "immediately": "urgency",
    "now": "urgency",
    "asap": "urgency",
    "verify": "verification pressure",
    "verification": "verification pressure",
    "login": "credential pressure",
    "password": "credential pressure",
    "code": "code theft",
    "codes": "code theft",
    "otp": "code theft",
    "2fa": "code theft",
    "gift": "gift card pressure",
    "card": "gift card pressure",
    "refund": "refund pressure",
    "invoice": "invoice pressure",
    "payment": "payment pressure",
    "bank": "bank impersonation",
    "paypal": "payment impersonation",
    "amazon": "brand impersonation",
    "irs": "government impersonation",
    "wallet": "wallet access pressure",
    "seed": "wallet access pressure",
}


def compact_spaces(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def normalize_keyword(text):
    return compact_spaces(str(text).lower())


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", normalize_keyword(text)).strip("-")


def keyword_tokens(text):
    return set(normalize_keyword(text).replace("-", " ").split())


def normalize_term_tokens(text):
    return set(normalize_keyword(text).replace("-", " ").split())


def apply_brand_case(text):
    result = f" {str(text)} "
    for raw, proper in sorted(BRAND_CASE.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(raw) + r"(?![a-z0-9])"
        result = re.sub(pattern, proper, result, flags=re.IGNORECASE)
    return compact_spaces(result)


def title_case(text):
    words = normalize_keyword(text).split()
    titled_words = []

    for i, word in enumerate(words):
        if i > 0 and word in SMALL_WORDS:
            titled_words.append(word)
        else:
            titled_words.append(word.capitalize())

    return apply_brand_case(" ".join(titled_words))


def escape_html(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def trim_meta_description(text, minimum=110, maximum=165):
    text = compact_spaces(text)
    if len(text) <= maximum:
        return text

    truncated = text[: maximum + 1]
    cut_points = [
        truncated.rfind(". "),
        truncated.rfind("; "),
        truncated.rfind(", "),
        truncated.rfind(" "),
    ]
    valid_cuts = [point for point in cut_points if point > minimum]

    if valid_cuts:
        cut = max(valid_cuts)
        text = truncated[:cut].rstrip(" ,;.")
    else:
        text = truncated[:maximum].rstrip(" ,;.")

    return text + "."


def build_canonical(slug):
    return f"{SITE}/scam-check-now/{slug}/"


def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        return []

    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return list(dict.fromkeys(normalize_keyword(line) for line in f if line.strip()))


def page_exists(slug):
    return os.path.exists(os.path.join(OUTPUT_DIR, slug, "index.html"))


def matches_cluster(keyword, match_terms):
    kw_norm = normalize_keyword(keyword)
    kw_tokens = keyword_tokens(keyword)
    kw_joined = f" {kw_norm.replace('-', ' ')} "

    for term in match_terms:
        term_norm = normalize_keyword(term)
        term_tokens = normalize_term_tokens(term)
        term_joined = f" {term_norm.replace('-', ' ')} "

        if term_tokens and term_tokens.issubset(kw_tokens):
            return True
        if term_joined.strip() and term_joined in kw_joined:
            return True

    return False


def score_keyword(keyword, hub_terms):
    kw = normalize_keyword(keyword)
    kw_tokens = keyword_tokens(kw)
    score = 0

    for term in hub_terms:
        term_tokens = normalize_term_tokens(term)
        if term_tokens and term_tokens.issubset(kw_tokens):
            score += 5

    if "scam" in kw_tokens:
        score += 4
    if "legit" in kw_tokens:
        score += 4
    if "review" in kw_tokens:
        score += 3
    if "warning" in kw_tokens or "risk" in kw_tokens:
        score += 3
    if {"email", "text", "message"} & kw_tokens:
        score += 2
    if {"link", "login", "verification"} & kw_tokens:
        score += 2
    if kw.startswith("is ") or kw.startswith("is this "):
        score += 1

    return (-score, len(kw), kw)


def dedupe_cluster_keywords(cluster_keywords):
    deduped = []
    seen_slugs = set()

    for keyword in cluster_keywords:
        slug = slugify(keyword)
        if slug and slug not in seen_slugs:
            deduped.append(keyword)
            seen_slugs.add(slug)

    return deduped


def clean_display_keyword(keyword):
    cleaned = normalize_keyword(keyword)
    cleaned = re.sub(r"^\s*is\s+", "", cleaned)
    cleaned = re.sub(r"^\s*can\s+i\s+trust\s+", "", cleaned)
    cleaned = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+(?:by|on|with)\s+", "", cleaned)
    cleaned = re.sub(r"\s+a\s+scam$", "", cleaned)
    cleaned = re.sub(r"\s+scam$", "", cleaned)
    cleaned = re.sub(r"\s+or\s+legit$", "", cleaned)
    cleaned = re.sub(r"\s+legit$", "", cleaned)
    cleaned = compact_spaces(cleaned)
    return title_case(cleaned)


def build_related_link_items(cluster_keywords):
    items = []
    seen = set()

    for keyword in cluster_keywords:
        slug = slugify(keyword)
        if not slug or slug in seen or not page_exists(slug):
            continue

        seen.add(slug)
        label = clean_display_keyword(keyword)
        items.append({
            "slug": slug,
            "title": label,
            "href": f"/scam-check-now/{slug}/",
            "anchor": f"{label} Scam Check",
        })

    return items


def build_related_links_html(link_items):
    return "\n".join(
        f'<li><a href="{escape_html(item["href"])}">{escape_html(item["anchor"])}</a></li>'
        for item in link_items
    )


def extract_variation_label(keyword, hub_terms):
    cleaned = normalize_keyword(keyword).replace("-", " ")
    cleaned = re.sub(r"^\s*is\s+", "", cleaned)
    cleaned = re.sub(r"^\s*can\s+i\s+trust\s+", "", cleaned)
    cleaned = re.sub(r"^\s*did\s+i\s+get\s+scammed\s+(?:by|on|with)\s+", "", cleaned)
    cleaned = re.sub(r"\s+a\s+scam$", "", cleaned)
    cleaned = re.sub(r"\s+scam$", "", cleaned)
    cleaned = re.sub(r"\s+or\s+legit$", "", cleaned)
    cleaned = re.sub(r"\s+legit$", "", cleaned)
    cleaned = compact_spaces(cleaned)

    removable_terms = sorted(
        [normalize_keyword(term).replace("-", " ") for term in hub_terms if normalize_keyword(term)],
        key=len,
        reverse=True,
    )

    for term in removable_terms:
        cleaned = re.sub(rf"\b{re.escape(term)}\b", " ", cleaned)

    original_words = cleaned.split()
    words = []

    for word in original_words:
        if word in STOPWORDS_FOR_VARIATIONS:
            continue
        if word in LOW_SIGNAL_VARIATION_WORDS and len(original_words) == 1:
            continue
        words.append(word)

    cleaned = compact_spaces(" ".join(words))

    if not cleaned or len(cleaned) < 3:
        return ""

    return title_case(cleaned)


def build_top_scam_types_html(cluster_keywords, hub_terms):
    counter = Counter()

    for keyword in cluster_keywords:
        label = extract_variation_label(keyword, hub_terms)
        if label:
            counter[label] += 1

    top_items = [label for label, _ in counter.most_common(TOP_SCAM_TYPES_COUNT)]
    if not top_items:
        return ""

    items_html = "\n".join(f"<li>{escape_html(item)}</li>" for item in top_items)

    return f"""
<section aria-labelledby="variations-heading">
<h2 id="variations-heading">Common Scam Variations In This Category</h2>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_warning_signs_html(hub_slug):
    bullets = HUB_WARNING_BULLETS.get(hub_slug, [
        "Urgent language designed to stop you from verifying independently",
        "Suspicious links, fake websites, or messages that do not match the official source",
        "Requests for money, codes, passwords, or personal information",
        "Pressure to act immediately before checking the situation yourself",
    ])
    return "\n".join(f"<li>{escape_html(bullet)}</li>" for bullet in bullets)


def build_related_topics_html(match_terms):
    cleaned_terms = []
    seen = set()

    for term in match_terms:
        label = title_case(str(term).replace("-", " "))
        key = normalize_keyword(label)
        if key and key not in seen:
            seen.add(key)
            cleaned_terms.append(label)

    if not cleaned_terms:
        return ""

    items_html = "\n".join(
        f"<li>{escape_html(item)}</li>"
        for item in cleaned_terms[:MAX_RELATED_TOPICS]
    )

    return f"""
<section aria-labelledby="related-topics-heading">
<h2 id="related-topics-heading">Related Scam Topics In This Hub</h2>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_verify_steps_html(hub_slug):
    steps = HUB_VERIFY_STEPS.get(hub_slug, [
        "Open the official website or app directly instead of using the message link.",
        "Check your real account, activity, notices, or support center there first.",
        "Do not send money, codes, passwords, or personal details until you verify independently.",
    ])

    items_html = "\n".join(f"<li>{escape_html(step)}</li>" for step in steps)

    return f"""
<section aria-labelledby="verify-heading">
<h2 id="verify-heading">How To Verify Safely</h2>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_how_it_works_html(hub_slug):
    text = HUB_HOW_IT_WORKS.get(
        hub_slug,
        "These scams usually create urgency first, then use impersonation, confusion, or fake authority to push the target into acting before verifying independently."
    )
    return f"""
<section aria-labelledby="how-it-works-heading">
<h2 id="how-it-works-heading">How These Scams Usually Work</h2>
<p>{escape_html(text)}</p>
</section>
""".strip()


def build_who_targeted_html(hub_slug):
    text = HUB_TARGETING.get(
        hub_slug,
        "These scams often target people who are busy, distracted, financially pressured, or already expecting a message related to the subject being impersonated."
    )
    return f"""
<section aria-labelledby="targeting-heading">
<h2 id="targeting-heading">Who These Scams Often Target</h2>
<p>{escape_html(text)}</p>
</section>
""".strip()


def get_faqs_for_hub(hub_slug):
    faqs = list(HUB_FAQS.get(hub_slug, []))
    if len(faqs) < 2:
        faqs.extend(GENERIC_FAQS[: max(0, 2 - len(faqs))])
    return faqs[:MAX_FAQS]


def build_faq_html(hub_slug):
    blocks = []

    for question, answer in get_faqs_for_hub(hub_slug):
        blocks.append(
            f'<div class="faq-item"><h3>{escape_html(question)}</h3><p>{escape_html(answer)}</p></div>'
        )

    return f"""
<section aria-labelledby="faq-heading">
<h2 id="faq-heading">Frequently Asked Questions</h2>
{''.join(blocks)}
</section>
""".strip()


def build_link_summary_html(link_items, hub_title):
    count = len(link_items)
    return (
        f"<p>This hub currently links to {count} related scam check pages so you can compare "
        f"patterns, wording, and tactics inside the {escape_html(hub_title)} category.</p>"
    )


def tokenize_for_analysis(text):
    return re.findall(r"[a-z0-9]+", normalize_keyword(text))


def natural_list(items, max_items=4):
    cleaned = [compact_spaces(str(x)) for x in items if compact_spaces(str(x))]
    cleaned = cleaned[:max_items]

    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"

    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def get_hub_keyword_insights(matched_keywords, hub_terms):
    channel_counter = Counter()
    pressure_counter = Counter()
    entity_counter = Counter()

    hub_term_tokens = set()
    for term in hub_terms:
        hub_term_tokens |= normalize_term_tokens(term)

    for keyword in matched_keywords:
        tokens = tokenize_for_analysis(keyword)

        for token in tokens:
            if token in CHANNEL_HINTS:
                channel_counter[CHANNEL_HINTS[token]] += 1

            if token in PRESSURE_HINTS:
                pressure_counter[PRESSURE_HINTS[token]] += 1

            if (
                token not in GENERIC_ENTITY_WORDS
                and token not in hub_term_tokens
                and len(token) > 2
                and not token.isdigit()
            ):
                entity_counter[token] += 1

    top_entities = [title_case(x) for x, _ in entity_counter.most_common(8)]
    top_channels = [x for x, _ in channel_counter.most_common(6)]
    top_pressures = [x for x, _ in pressure_counter.most_common(6)]

    return {
        "top_entities": top_entities,
        "top_channels": top_channels,
        "top_pressures": top_pressures,
    }


def build_dynamic_keyword_summary_html(matched_keywords, hub_terms):
    insights = get_hub_keyword_insights(matched_keywords, hub_terms)

    entities = natural_list(insights["top_entities"], 5)
    channels = natural_list([title_case(x) for x in insights["top_channels"]], 4)
    pressures = natural_list(insights["top_pressures"], 4)

    paragraphs = []

    if entities:
        paragraphs.append(
            f"Across the related pages in this hub, people frequently search about {escape_html(entities)}. "
            f"That suggests this category often overlaps with recognizable brands, entities, or scam contexts that users want to verify before clicking, replying, or sending money."
        )

    if channels:
        paragraphs.append(
            f"The keyword patterns in this hub also show that these scams often appear through {escape_html(channels)}. "
            f"That matters because the delivery channel usually shapes the scam tactic, the level of urgency, and the safest way to verify the situation independently."
        )

    if pressures:
        paragraphs.append(
            f"Another strong pattern across the matched searches is {escape_html(pressures)}. "
            f"That kind of pressure is common when scammers want fast action before the target has time to slow down, verify details, or notice inconsistencies."
        )

    if not paragraphs:
        paragraphs.append(
            "The matched searches in this hub show repeated intent around legitimacy checks, scam reviews, suspicious messages, and independent verification before taking action."
        )

    body = "\n".join(f"<p>{paragraph}</p>" for paragraph in paragraphs)

    return f"""
<section aria-labelledby="keyword-patterns-heading">
<h2 id="keyword-patterns-heading">What People Are Seeing In This Scam Category</h2>
{body}
</section>
""".strip()


def build_dynamic_entity_focus_html(matched_keywords, hub_terms):
    insights = get_hub_keyword_insights(matched_keywords, hub_terms)
    entities = insights["top_entities"][:8]

    if not entities:
        return ""

    items_html = "\n".join(f"<li>{escape_html(item)}</li>" for item in entities)

    return f"""
<section aria-labelledby="entity-focus-heading">
<h2 id="entity-focus-heading">Common Brands, Platforms, Or Entities Mentioned</h2>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_cluster_specific_intro_html(intro, matched_keywords, hub_terms):
    insights = get_hub_keyword_insights(matched_keywords, hub_terms)

    top_channels = natural_list([title_case(x) for x in insights["top_channels"]], 3)
    top_pressures = natural_list(insights["top_pressures"], 3)

    supporting = []

    if top_channels:
        supporting.append(
            f"In this category, suspicious activity often shows up through {escape_html(top_channels)}."
        )

    if top_pressures:
        supporting.append(
            f"Repeated search patterns also suggest that {escape_html(top_pressures)} shows up often in these variations."
        )

    supporting_html = "\n".join(f"<p>{sentence}</p>" for sentence in supporting)

    return f"""
<section aria-labelledby="hub-intro-heading">
<h2 id="hub-intro-heading" style="position:absolute;left:-9999px;">Hub Introduction</h2>
<p>{escape_html(intro)}</p>
{supporting_html}
</section>
""".strip()


def build_meta_keyword_support_text(matched_keywords, hub_terms):
    insights = get_hub_keyword_insights(matched_keywords, hub_terms)
    parts = []

    if insights["top_entities"]:
        parts.append(f"brands like {natural_list(insights['top_entities'], 4)}")
    if insights["top_channels"]:
        parts.append(f"channels like {natural_list([title_case(x) for x in insights['top_channels']], 4)}")
    if insights["top_pressures"]:
        parts.append(f"pressure patterns like {natural_list(insights['top_pressures'], 4)}")

    if not parts:
        return "related scam signals and verification patterns"

    return "; ".join(parts)


def build_schema(hub_slug, hub_title, description, intro, link_items, matched_keywords, hub_terms):
    canonical = build_canonical(hub_slug)
    faq_entities = [
        {
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": answer,
            },
        }
        for question, answer in get_faqs_for_hub(hub_slug)
    ]

    keyword_support = build_meta_keyword_support_text(matched_keywords, hub_terms)

    schema_objects = [
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": hub_title,
            "description": description,
            "url": canonical,
            "about": intro,
            "keywords": keyword_support,
            "mainEntity": {
                "@type": "ItemList",
                "name": f"{hub_title} Related Scam Checks",
                "numberOfItems": len(link_items),
            },
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Scam Check Now", "item": f"{SITE}/check"},
                {"@type": "ListItem", "position": 2, "name": "Scam Check Hubs", "item": f"{SITE}/scam-check-now/"},
                {"@type": "ListItem", "position": 3, "name": hub_title, "item": canonical},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"{hub_title} Related Scam Checks",
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "numberOfItems": len(link_items),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index + 1,
                    "url": f"{SITE}{item['href']}",
                    "name": item["anchor"],
                }
                for index, item in enumerate(link_items)
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_entities,
        },
    ]

    return json.dumps(schema_objects, ensure_ascii=False, separators=(",", ":"))


def validate_hub_output(hub_slug, hub_title, description, canonical, matched_keywords, link_items, html, intro, hub_terms):
    errors = []

    if not hub_slug:
        errors.append("empty hub slug")
    if not hub_title.strip():
        errors.append("empty title")
    if "scams scams" in hub_title.lower():
        errors.append("duplicated wording in title")
    if len(description) < 110 or len(description) > 165:
        errors.append("description length out of target range")
    if not canonical.endswith(f"/{hub_slug}/"):
        errors.append("canonical mismatch")
    if not matched_keywords:
        errors.append("no matched keywords")
    if len(link_items) < MIN_LINKS_TO_BUILD_HUB:
        errors.append("too few rendered links")
    if html.count("<h2") < 7:
        errors.append("insufficient section depth")
    if len(html) < 7000:
        errors.append("page html too thin")
    if "<main" not in html:
        errors.append("missing main landmark")
    if "application/ld+json" not in html:
        errors.append("missing schema")
    if "og:title" not in html or "twitter:title" not in html:
        errors.append("missing social metadata")
    if "What People Are Seeing In This Scam Category" not in html:
        errors.append("missing dynamic keyword summary")

    entity_count = len(get_hub_keyword_insights(matched_keywords, hub_terms)["top_entities"])
    if entity_count >= 4 and "Common Brands, Platforms, Or Entities Mentioned" not in html:
        errors.append("missing dynamic entity section")

    fallback_hits = 0
    if intro == INTRO_FALLBACK:
        fallback_hits += 1
    if description == trim_meta_description(META_FALLBACK):
        fallback_hits += 1
    if fallback_hits >= 2:
        errors.append("too much fallback copy")

    return errors


def build_hub_html(
    hub_slug,
    hub_title,
    description,
    intro,
    link_items,
    top_scam_types_html,
    warning_signs_html,
    related_topics_html,
    faq_html,
    matched_keywords,
    hub_terms,
):
    canonical = build_canonical(hub_slug)
    links_html = build_related_links_html(link_items)
    schema_json = build_schema(hub_slug, hub_title, description, intro, link_items, matched_keywords, hub_terms)
    how_it_works_html = build_how_it_works_html(hub_slug)
    who_targeted_html = build_who_targeted_html(hub_slug)
    verify_steps_html = build_verify_steps_html(hub_slug)
    link_summary_html = build_link_summary_html(link_items, hub_title)
    dynamic_keyword_summary_html = build_dynamic_keyword_summary_html(matched_keywords, hub_terms)
    dynamic_entity_focus_html = build_dynamic_entity_focus_html(matched_keywords, hub_terms)
    cluster_specific_intro_html = build_cluster_specific_intro_html(intro, matched_keywords, hub_terms)

    jump_links = []
    sections = []

    if top_scam_types_html:
        jump_links.append('<a href="#variations-heading">Variations</a>')
        sections.append(f"""
<div class="section-card">
{top_scam_types_html}
</div>
""".strip())

    jump_links.append('<a href="#keyword-patterns-heading">What People See</a>')
    sections.append(f"""
<div class="section-card">
{dynamic_keyword_summary_html}
</div>
""".strip())

    jump_links.append('<a href="#how-it-works-heading">How It Works</a>')
    sections.append(f"""
<div class="section-card">
{how_it_works_html}
</div>
""".strip())

    jump_links.append('<a href="#targeting-heading">Who Gets Targeted</a>')
    sections.append(f"""
<div class="section-card">
{who_targeted_html}
</div>
""".strip())

    if dynamic_entity_focus_html:
        jump_links.append('<a href="#entity-focus-heading">Entities</a>')
        sections.append(f"""
<div class="section-card">
{dynamic_entity_focus_html}
</div>
""".strip())

    if related_topics_html:
        jump_links.append('<a href="#related-topics-heading">Related Topics</a>')
        sections.append(f"""
<div class="section-card">
{related_topics_html}
</div>
""".strip())

    jump_links.append('<a href="#warning-signs-heading">Warning Signs</a>')
    sections.append(f"""
<section class="section-card" aria-labelledby="warning-signs-heading">
<h2 id="warning-signs-heading">Common Warning Signs</h2>
<ul>
{warning_signs_html}
</ul>
</section>
""".strip())

    jump_links.append('<a href="#verify-heading">Verify Safely</a>')
    sections.append(f"""
<div class="section-card">
{verify_steps_html}
</div>
""".strip())

    jump_links.append('<a href="#related-checks-heading">Related Checks</a>')
    sections.append(f"""
<section class="section-card" aria-labelledby="related-checks-heading">
<h2 id="related-checks-heading">Related Scam Checks</h2>
{link_summary_html}
<div class="link-box">
<ul>
{links_html}
</ul>
</div>
</section>
""".strip())

    sections.append("""
<section class="section-card" aria-labelledby="what-to-do-heading">
<h2 id="what-to-do-heading">What To Do</h2>
<p>If something looks off, do not rely on the message itself. Go to the official website, app, or verified support channel directly and confirm the situation there before taking action.</p>
<p>If money, codes, or credentials are involved, slowing down is often the safest move. Independent verification matters more than anything the suspicious message claims.</p>
</section>
""".strip())

    jump_links.append('<a href="#faq-heading">FAQ</a>')
    sections.append(f"""
<div class="section-card">
{faq_html}
</div>
""".strip())

    sections_html = "\n\n<div class=\"section-divider\"></div>\n\n".join(sections)
    jump_links_html = "\n  ".join(jump_links)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape_html(hub_title)}</title>
<meta name="description" content="{escape_html(description)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{escape_html(canonical)}">
<meta property="og:title" content="{escape_html(hub_title)}">
<meta property="og:description" content="{escape_html(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{escape_html(canonical)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape_html(hub_title)}">
<meta name="twitter:description" content="{escape_html(description)}">
<script type="application/ld+json">{schema_json}</script>
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
--navy:#1e293b;
--card:#ffffff;
--shadow-xl:0 30px 80px rgba(15,23,42,.10);
--shadow-md:0 12px 30px rgba(15,23,42,.07);
}}
*{{box-sizing:border-box;}}
html{{-webkit-text-size-adjust:100%;scroll-behavior:smooth;}}
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
max-width:920px;
margin:0 auto;
padding:0 14px;
}}
.content-section{{
max-width:800px;
margin:auto;
background:rgba(255,255,255,.97);
padding:24px;
padding-bottom:40px;
border-radius:30px;
box-shadow:var(--shadow-xl);
border:1px solid rgba(226,232,240,.95);
}}
h1,h2,h3{{
margin:0 0 14px;
color:var(--ink-strong);
line-height:1.08;
letter-spacing:-.035em;
font-weight:900;
}}
h1{{font-size:42px;}}
h2{{font-size:28px;margin-top:0;}}
h3{{font-size:22px;margin-top:20px;}}
p, li{{
font-size:18px;
color:#334155;
}}
ul,ol{{
margin:0;
padding-left:22px;
}}
li{{margin-bottom:10px;}}
a{{
color:var(--blue);
text-decoration:none;
font-weight:700;
}}
a:hover{{text-decoration:underline;}}
.breadcrumbs{{
margin:0 0 18px;
font-size:13px;
font-weight:800;
color:#64748b;
}}
.breadcrumbs a{{
color:#64748b;
text-decoration:none;
font-weight:800;
}}
.breadcrumbs a:hover{{text-decoration:underline;}}
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
.tool-cta-card{{
margin:0 0 24px;
padding:22px;
background:linear-gradient(180deg,#f8fbff 0%,#f3f8ff 100%);
border:1.5px solid #c7d2fe;
border-radius:22px;
text-align:center;
box-shadow:var(--shadow-md);
}}
.tool-cta-card h3{{
margin:0 0 8px;
font-size:24px;
}}
.tool-cta-card p{{
margin:0 0 14px;
font-size:15px;
line-height:1.6;
color:#4b5563;
}}
.tool-cta-note{{
margin-top:10px;
font-size:13px;
color:#6b7280;
font-weight:800;
}}
.tool-cta-button{{
display:block;
width:100%;
text-decoration:none;
text-align:center;
background:linear-gradient(180deg,#22324b 0%,var(--navy) 100%);
color:#fff;
font-weight:900;
padding:15px;
border-radius:16px;
box-shadow:0 14px 30px rgba(15,23,42,.12);
}}
.section-card{{
padding:20px;
background:var(--card);
border:1px solid var(--line-soft);
border-radius:22px;
box-shadow:0 8px 20px rgba(15,23,42,.03);
}}
.link-box{{
margin-top:16px;
padding:18px;
border-radius:20px;
background:var(--blue-soft);
border:1px solid var(--blue-line);
}}
.meta-strip{{
margin:22px 0 0;
padding:14px 16px;
border-radius:16px;
background:#f8fafc;
border:1px solid var(--line-soft);
font-size:14px;
font-weight:800;
color:#475569;
}}
.section-divider{{
height:1px;
background:linear-gradient(90deg, transparent, #dbeafe, transparent);
margin:28px 0;
}}
.faq-item + .faq-item{{
margin-top:8px;
padding-top:8px;
border-top:1px solid var(--line-soft);
}}
.jump-links{{
display:flex;
flex-wrap:wrap;
gap:10px;
margin:0 0 24px;
}}
.jump-links a{{
display:inline-block;
padding:10px 12px;
border-radius:999px;
background:#f8fafc;
border:1px solid var(--line-soft);
font-size:14px;
font-weight:800;
color:#334155;
}}
.jump-links a:hover{{
text-decoration:none;
background:#eff6ff;
border-color:#bfdbfe;
}}
@media (max-width:640px){{
h1{{font-size:30px;}}
h2{{font-size:24px;}}
h3{{font-size:20px;}}
p,li{{font-size:16px;}}
.content-section{{padding:18px;border-radius:24px;}}
.jump-links{{gap:8px;}}
.jump-links a{{font-size:13px;padding:9px 11px;}}
}}
</style>
</head>
<body>
<div class="page-shell">
<main class="content-section">
<div class="breadcrumbs">
  <a href="{SITE}/check">Scam Check Now</a> / <a href="{SITE}/scam-check-now/">Scam Check Hubs</a> / <span>{escape_html(hub_title)}</span>
</div>

<div class="info-box">This hub groups together related scam checks so you can review warning signs, compare patterns, and quickly navigate to the most relevant pages.</div>

<h1>{escape_html(hub_title)}</h1>

{cluster_specific_intro_html}
<p>These scam patterns often change in wording, format, and delivery method, but the underlying tactics usually stay the same: urgency, impersonation, suspicious links, fake support, payment pressure, or requests for sensitive information.</p>
<p>Use the related scam checks below to review specific variations, compare warning signs, and understand what to do next before you click, reply, send money, or share anything.</p>

<nav class="jump-links" aria-label="Page sections">
  {jump_links_html}
</nav>

<div class="tool-cta-card">
  <h3>Not sure if this is a scam?</h3>
  <p>Paste the suspicious message, email, website, or link into the scam checker and review the risk before you click, reply, or send money.</p>
  <a class="tool-cta-button" href="{SITE}/check">Check a Suspicious Message Now</a>
  <div class="tool-cta-note">No signup required • 1 free check • Takes seconds</div>
</div>

{sections_html}

<div class="meta-strip">
Compare scam patterns, review warning signs, and use the linked checks above to investigate the most relevant variations in this category.
</div>
</main>
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


def save_report(report):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    keywords = load_keywords()
    if not keywords:
        print("No generated keywords found.")
        return

    validation_warning_count = 0
    built_count = 0
    skipped_empty_count = 0
    skipped_no_links_count = 0
    validation_details = []

    for hub_slug, match_terms in CLUSTERS.items():
        matched = [kw for kw in keywords if matches_cluster(kw, match_terms)]

        if not matched:
            skipped_empty_count += 1
            print(f"Skipped hub: {hub_slug} (no matching generated keywords)")
            continue

        matched = dedupe_cluster_keywords(matched)
        matched = sorted(matched, key=lambda k: score_keyword(k, match_terms))[:MAX_LINKS_PER_HUB]

        link_items = build_related_link_items(matched)

        if len(link_items) < MIN_LINKS_TO_BUILD_HUB:
            skipped_no_links_count += 1
            print(f"Skipped hub: {hub_slug} (fewer than {MIN_LINKS_TO_BUILD_HUB} existing linked pages)")
            continue

        hub_title = HUB_TITLES.get(hub_slug, title_case(hub_slug.replace("-", " ")))
        intro = HUB_INTROS.get(hub_slug, INTRO_FALLBACK)
        description = trim_meta_description(HUB_META_DESCRIPTIONS.get(hub_slug, META_FALLBACK))
        canonical = build_canonical(hub_slug)

        top_scam_types_html = build_top_scam_types_html(matched, match_terms)
        warning_signs_html = build_warning_signs_html(hub_slug)
        related_topics_html = build_related_topics_html(match_terms)
        faq_html = build_faq_html(hub_slug)

        html = build_hub_html(
            hub_slug=hub_slug,
            hub_title=hub_title,
            description=description,
            intro=intro,
            link_items=link_items,
            top_scam_types_html=top_scam_types_html,
            warning_signs_html=warning_signs_html,
            related_topics_html=related_topics_html,
            faq_html=faq_html,
            matched_keywords=matched,
            hub_terms=match_terms,
        )

        validation_errors = validate_hub_output(
            hub_slug=hub_slug,
            hub_title=hub_title,
            description=description,
            canonical=canonical,
            matched_keywords=matched,
            link_items=link_items,
            html=html,
            intro=intro,
            hub_terms=match_terms,
        )

        if validation_errors:
            validation_warning_count += 1
            validation_details.append({
                "hub_slug": hub_slug,
                "errors": validation_errors,
            })
            print(f"Validation warning for {hub_slug}: {'; '.join(validation_errors)}")

        save_hub(hub_slug, html)
        built_count += 1
        print(f"Built hub: {hub_slug}")

    report = {
        "keywords_loaded": len(keywords),
        "hubs_built": built_count,
        "hubs_skipped_no_matches": skipped_empty_count,
        "hubs_skipped_insufficient_links": skipped_no_links_count,
        "validation_warnings": validation_warning_count,
        "validation_details": validation_details,
    }
    save_report(report)

    print("\n--- HUB BUILD REPORT ---")
    print(f"Keywords loaded: {len(keywords)}")
    print(f"Hubs built: {built_count}")
    print(f"Hubs skipped (no matches): {skipped_empty_count}")
    print(f"Hubs skipped (insufficient existing linked pages): {skipped_no_links_count}")
    print(f"Validation warnings: {validation_warning_count}")
    print(f"Saved report: {REPORT_PATH}")


if __name__ == "__main__":
    main()