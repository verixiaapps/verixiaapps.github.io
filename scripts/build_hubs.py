import os
import re
import sys
import json
from collections import Counter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from data.cluster_map import CLUSTERS

KEYWORDS_FILE = os.path.join(BASE_DIR, "data", "generated_keywords.txt")
OUTPUT_DIR = os.path.join(BASE_DIR, "scam-check-now")
SITE = "https://verixiaapps.com"

MAX_LINKS_PER_HUB = 50
TOP_SCAM_TYPES_COUNT = 8
MAX_RELATED_TOPICS = 10
MAX_FAQS = 4
MAX_COMMON_SITUATIONS = 5
MAX_COMPARISON_POINTS = 4
MAX_PATTERN_EXAMPLES = 4
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
    "amazon-scams": "Amazon scams often use fake account alerts, delivery issues, gift card requests, refunds, or security warnings to pressure people into clicking links, sharing details, or sending money before they verify anything independently.",
    "paypal-scams": "PayPal scams often use fake payment alerts, invoice tricks, account warnings, or refund messages to create urgency and push people into unsafe actions before they check the real account.",
    "zelle-scams": "Zelle scams often rely on fake payment issues, impersonation, reversal claims, or urgent transfer requests designed to get money sent quickly before the target confirms the situation through the bank.",
    "cash-app-scams": "Cash App scams often involve fake payment notices, support impersonation, giveaway tricks, or refund pressure designed to move money fast before the target slows down.",
    "venmo-scams": "Venmo scams often use fake payments, accidental transfer stories, buyer-seller tricks, or impersonation to pressure fast action before independent verification.",
    "facebook-scams": "Facebook scams often appear through Marketplace messages, fake buyer interest, account alerts, impersonation, or suspicious links that try to move people off-platform or into unsafe actions.",
    "instagram-scams": "Instagram scams often use impersonation, fake brand outreach, phishing links, account warnings, or suspicious investment messages to build trust before asking for action.",
    "tiktok-scams": "TikTok scams often use fake promotions, impersonation, suspicious links, phishing messages, or payment tricks that depend on speed and familiarity.",
    "whatsapp-scams": "WhatsApp scams often involve impersonation, unknown numbers, fake support, urgent payment requests, or suspicious links that rely on quick replies and off-platform trust.",
    "telegram-scams": "Telegram scams often involve fake investments, impersonation, suspicious groups, phishing links, or urgent payment requests that pressure people to act before verifying.",
    "snapchat-scams": "Snapchat scams often use impersonation, fake account alerts, suspicious links, or pressure to send money or information before the target confirms who is really behind the message.",
    "discord-scams": "Discord scams often use fake Nitro offers, suspicious downloads, impersonation, phishing links, or account takeover tricks designed to capture credentials or trigger unsafe clicks.",
    "crypto-scams": "Crypto scams often use fake investment promises, wallet connection tricks, phishing links, impersonation, recovery claims, and urgent transfer requests to move funds before the target verifies anything.",
    "package-delivery-scams": "Package delivery scams often use fake USPS, FedEx, UPS, or delivery alerts to push clicks, payments, or personal information through messages that look routine at first glance.",
    "bank-scams": "Bank scams often use fake fraud alerts, account lock messages, payment issues, suspicious charge warnings, or impersonation to pressure immediate action before the target checks the real account.",
    "job-scams": "Job scams often use fake recruiters, remote job offers, interview messages, onboarding pressure, or payment requests to steal money or personal information during what looks like a normal hiring process.",
    "investment-scams": "Investment scams often promise fast returns, urgent opportunities, insider tips, or guaranteed profits to pressure risky decisions before independent verification.",
    "loan-scams": "Loan scams often use fake approvals, upfront fees, urgent verification requests, or suspicious lenders to steal money or personal information from people already under financial pressure.",
    "credit-scams": "Credit scams often involve fake repair offers, urgent account notices, phishing attempts, or requests for sensitive personal details that are framed as routine financial steps.",
    "romance-scams": "Romance scams often build trust first, then create emotional pressure for money, gifts, account access, or private information once the target feels invested in the relationship.",
    "gift-card-scams": "Gift card scams often use urgent payment pressure, impersonation, fake support, or fake emergencies because gift cards are hard to recover once the codes are shared.",
    "urgent-payment-scams": "Urgent payment scams rely on speed, pressure, fear, and limited verification time to get money sent before the target stops to check who is really making the request.",
    "government-scams": "Government scams often impersonate the IRS, Social Security, tax agencies, or benefits programs to scare people into acting quickly before they verify the notice through an official source.",
    "unknown-number-scams": "Unknown number scams often begin with unexpected texts or calls designed to spark curiosity, urgency, or a quick reply before the scammer reveals the real request.",
    "verification-code-scams": "Verification code scams often try to trick people into sharing one-time codes, security codes, or login approvals that can be used to access accounts or reset credentials.",
    "account-security-scams": "Account security scams often use fake login alerts, password resets, account lock messages, or verification warnings to push people toward fake pages or code sharing before they check the real service.",
    "phishing-scams": "Phishing scams often use fake login pages, email warnings, security alerts, or account verification requests to steal credentials, payment information, or recovery details.",
    "general-scams": "General scam patterns often show the same core behavior: urgency, impersonation, pressure, suspicious links, requests for money, and attempts to stop independent verification."
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
    "account-security-scams": "Account Security Scams: Warning Signs, Related Checks & What To Do",
    "phishing-scams": "Phishing Scams: Warning Signs, Related Checks & What To Do",
    "general-scams": "Scam Warning Signs: Related Checks & What To Do",
}

HUB_META_DESCRIPTIONS = {
    "amazon-scams": "Review common Amazon scam patterns, warning signs, and related scam checks. Learn what fake Amazon alerts, refunds, account notices, and delivery scams often look like.",
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
    "crypto-scams": "Explore common crypto scam patterns, fake investments, wallet tricks, phishing links, recovery pressure, and urgent transfer requests. Review related crypto scam checks.",
    "package-delivery-scams": "Review common package delivery scam patterns, fake USPS, UPS, and FedEx alerts, suspicious links, and payment requests. Compare related scam checks.",
    "bank-scams": "Explore common bank scam patterns, fake fraud alerts, account lock notices, payment issues, suspicious charges, and impersonation tactics. Review related bank scam checks.",
    "job-scams": "Review common job scam patterns, fake recruiters, interview messages, remote job offers, and payment requests. Compare related job scam checks.",
    "investment-scams": "Explore common investment scam patterns, fake returns, urgent opportunities, guaranteed profits, and pressure tactics. Review related scam checks.",
    "loan-scams": "Review common loan scam patterns, fake approvals, urgent verification requests, suspicious lenders, and upfront fee tricks. Compare related scam checks.",
    "credit-scams": "Explore common credit scam patterns, fake repair offers, urgent notices, phishing attempts, and sensitive data requests. Review related scam checks.",
    "romance-scams": "Review common romance scam patterns, emotional manipulation, gift requests, money pressure, and trust-building tactics. Compare related scam checks.",
    "gift-card-scams": "Explore common gift card scam patterns, fake emergencies, urgent payment pressure, impersonation, and support tricks. Review related scam checks.",
    "urgent-payment-scams": "Review common urgent payment scam patterns, fear tactics, time pressure, refund claims, and fast-transfer requests. Compare related urgent payment scam checks.",
    "government-scams": "Explore common government scam patterns, IRS threats, Social Security impersonation, tax scams, and benefits fraud. Review related scam checks.",
    "unknown-number-scams": "Review common unknown number scam patterns, suspicious texts, unexpected calls, curiosity hooks, and fast-reply traps. Compare related scam checks.",
    "verification-code-scams": "Explore common verification code scam patterns, one-time code theft, login approval tricks, and account access scams. Review related scam checks.",
    "account-security-scams": "Review common account security scam patterns, fake login alerts, password reset warnings, account lock notices, and verification requests. Compare related scam checks.",
    "phishing-scams": "Review common phishing scam patterns, fake login pages, account alerts, email warnings, and credential theft attempts. Compare related scam checks.",
    "general-scams": "Review broad scam warning signs, suspicious message patterns, and related scam checks. Learn what to look for before you click, reply, send money, or share information.",
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
    "crypto-scams": [
        "Fake investment promises, suspicious wallet requests, phishing links, or support impersonation",
        "Urgent transfer instructions designed to move funds before you verify the situation",
        "Messages that promise guaranteed returns, recoveries, or exclusive opportunities",
        "Requests for wallet access, seed phrases, or approvals that should never be shared",
    ],
    "job-scams": [
        "Fake recruiter outreach, remote job offers, interview requests, or onboarding messages",
        "Pressure to move quickly, share personal details, or pay for equipment or verification",
        "Offers that seem unusually fast, easy, or high-paying without normal screening",
        "Requests that move off trusted platforms before legitimacy is confirmed",
    ],
    "phishing-scams": [
        "Fake login pages, account alerts, security warnings, or verification requests",
        "Links that imitate trusted brands but lead to credential theft pages",
        "Urgent wording designed to keep you from verifying the sender independently",
        "Requests for passwords, codes, or login details outside official channels",
    ],
    "account-security-scams": [
        "Unexpected login alerts, password reset warnings, or account lock messages",
        "Requests to share one-time codes, credentials, or identity details through the message itself",
        "Links to sign-in pages that look close to the real service but are not exact",
        "Pressure to act immediately before checking the official account directly",
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
    "account-security-scams": [
        ("What does an account security scam usually look like?", "It often looks like a login alert, password reset, account lock, or verification warning that pushes you toward a link or code-sharing step before you verify the real account."),
        ("How should you verify an account security alert?", "Open the official website or app yourself, sign in directly there, and check whether the alert appears inside your real account activity or notifications."),
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
    "account-security-scams": [
        "Open the official website or app directly instead of using the message link.",
        "Check the real account activity, security notifications, and login history there first.",
        "Do not share one-time codes, passwords, or recovery details unless you initiated the request yourself.",
    ],
}

HUB_HOW_IT_WORKS = {
    "amazon-scams": "These scams usually mimic normal Amazon trust signals first, then introduce urgency around account access, deliveries, refunds, or gift cards so the target reacts before verifying.",
    "paypal-scams": "These scams often look believable because they use payment language, invoice formatting, and refund urgency to make the target feel they need to act immediately.",
    "zelle-scams": "These scams work by creating confusion around payment status, reversals, business account claims, or buyer-seller pressure so the victim sends money before checking carefully.",
    "crypto-scams": "These scams usually rely on urgency, technical confusion, fake authority, and irreversible transfers to push victims into wallet approvals or direct payments.",
    "job-scams": "These scams typically start with excitement and speed, then shift into requests for money, sensitive data, or off-platform communication before legitimacy is established.",
    "account-security-scams": "These scams usually start with a familiar-looking warning, then push the target toward a fake login, code-sharing request, or urgent security step before the real account is checked directly.",
}

HUB_TARGETING = {
    "amazon-scams": "They often target online shoppers, delivery recipients, and people used to seeing frequent account or shipping notifications.",
    "paypal-scams": "They often target buyers, sellers, freelancers, and anyone who regularly receives payment alerts or invoices.",
    "zelle-scams": "They often target marketplace buyers and sellers, people sending peer payments, and anyone under time pressure during a transaction.",
    "crypto-scams": "They often target newer crypto users, people seeking fast gains, and anyone under pressure to recover funds or act on a supposedly exclusive opportunity.",
    "job-scams": "They often target job seekers who are moving quickly, applying broadly, or hoping for remote work and fast hiring.",
    "account-security-scams": "They often target people who already use the impersonated service regularly and are used to receiving security, login, or account notifications.",
}

INTRO_FALLBACK = (
    "This hub groups together related scam checks so you can review warning signs, compare patterns, and understand how scam variations often work."
)

META_FALLBACK = (
    "Review related scam checks, compare warning signs, and learn what to do next before you click, reply, send money, or share information."
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

GENERIC_COMPARISON_POINTS = [
    (
        "A legitimate version usually survives independent verification.",
        "A scam version usually depends on the message itself and becomes weaker once you check the official site or app directly."
    ),
    (
        "A legitimate notice usually uses established support, account, or order flows.",
        "A scam version usually pushes you toward a shortcut like a message link, callback number, urgent payment step, or code request."
    ),
    (
        "A legitimate warning usually still makes sense after you slow down.",
        "A scam version usually depends on urgency, fear, or confusion to stop you from checking carefully."
    ),
]

HUB_COMPARISON_POINTS = {
    "amazon-scams": [
        (
            "A real Amazon notice usually appears alongside matching order, refund, or account details inside the official Amazon account.",
            "A scam version usually depends on a link, gift card demand, rushed refund claim, or message-only instruction."
        ),
        (
            "A real Amazon delivery or account issue can be checked through the official app or website directly.",
            "A scam version usually tries to keep you inside the email or text instead of letting you verify independently."
        ),
    ],
    "paypal-scams": [
        (
            "A real PayPal alert should match actual activity inside your PayPal account.",
            "A scam version usually depends on panic around invoices, refunds, or suspicious payments before you check the real account."
        ),
        (
            "A real PayPal issue can be reviewed through the official app or website.",
            "A scam version usually pushes you toward a link, a fake support number, or an urgent login step."
        ),
    ],
    "crypto-scams": [
        (
            "A legitimate crypto action should still make sense after you independently verify the project, wallet, exchange, or support channel.",
            "A scam version usually depends on urgency, impersonation, or technical confusion to push you into approval or transfer steps."
        ),
        (
            "A legitimate crypto request should never require you to share seed phrases or private access details.",
            "A scam version often tries to normalize exactly those unsafe requests."
        ),
    ],
    "job-scams": [
        (
            "A real hiring process usually includes a verifiable company, consistent recruiter identity, and normal interview steps.",
            "A scam version usually rushes toward fees, sensitive documents, or off-platform communication."
        ),
        (
            "A real job opportunity can usually be checked through the employer website or a known recruiter identity.",
            "A scam version usually becomes vague or evasive once you ask to verify the company independently."
        ),
    ],
    "account-security-scams": [
        (
            "A real security alert should still make sense when you open the official website or app directly.",
            "A scam version usually depends on the message link, code request, or urgency before you verify the real account."
        ),
        (
            "A real security step should follow familiar account recovery or login flows.",
            "A scam version usually introduces a fake page, unusual code-sharing step, or support shortcut."
        ),
    ],
}

GENERIC_PATTERN_EXAMPLES = [
    "A message that creates urgency before it provides enough real detail.",
    "A link or support path that asks you to trust the message instead of verifying outside it.",
    "A request for payment, login, codes, or personal information before independent confirmation.",
    "A familiar-looking notice that becomes less believable the moment you slow down and check carefully.",
]

HUB_PATTERN_EXAMPLES = {
    "amazon-scams": [
        "A fake order, refund, or delivery notice that tries to move you into a payment or login step.",
        "A message that uses Amazon branding to create urgency around an account or package issue.",
        "A gift card or refund story that only makes sense inside the message itself.",
    ],
    "paypal-scams": [
        "A fake invoice or suspicious payment alert that pressures you to log in immediately.",
        "A refund or support message that tries to push you toward a fake page or support number.",
        "An urgent payment issue that does not match real activity once you check PayPal directly.",
    ],
    "crypto-scams": [
        "A wallet verification, recovery, or support request that depends on urgency and technical confusion.",
        "An investment or token claim that promises upside before independent proof exists.",
        "A fake support contact that tries to normalize approvals, transfers, or wallet access steps.",
    ],
    "job-scams": [
        "A recruiter or hiring message that moves unusually fast and skips normal screening.",
        "A job offer that starts sounding expensive once fees, equipment, or identity requests appear.",
        "An off-platform hiring conversation that becomes vague the moment independent verification is requested.",
    ],
    "account-security-scams": [
        "A login, password reset, or account lock warning that depends on a message link.",
        "A security alert that feels familiar until it asks for a code, password, or unusual identity step.",
        "A copied account warning that weakens once you open the real service directly.",
    ],
}

COMMON_SITUATION_TEMPLATES = {
    "payment": [
        "A fake refund, invoice, or payment problem creates urgency before you can review the real account.",
        "The message tries to turn a routine account check into a rushed login, transfer, or support action.",
        "The sender pushes you toward a link, callback, or payment step instead of the official platform.",
    ],
    "job": [
        "The conversation moves faster than a normal hiring process and starts asking for money or sensitive details.",
        "The offer sounds attractive on the surface, but the verification path gets weaker as you look closer.",
        "The recruiter, company, or role becomes harder to confirm once the message pushes you off trusted channels.",
    ],
    "crypto": [
        "The request becomes risky the moment it asks for wallet approval, recovery details, or urgent transfers.",
        "A technical-looking message uses urgency to stop careful verification of the domain, project, or support account.",
        "The promise sounds strong, but the independent proof stays weak while the action request gets stronger.",
    ],
    "delivery": [
        "A small delivery issue is used to justify a link click, address update, or payment request.",
        "The message feels routine because shipping alerts are common, but the verification path is unusually weak.",
        "The notice depends on urgency around a package rather than on details you can confirm independently.",
    ],
    "account-security": [
        "A familiar-looking security warning creates enough panic to push a fast login or code-sharing step.",
        "The message imitates a normal account protection flow but depends on a link or shortcut to control the next step.",
        "The alert sounds routine until you compare it to the real service and notice the mismatch.",
    ],
    "government": [
        "Authority and urgency are combined to pressure a fast response before official verification happens.",
        "The message uses a benefits, tax, or identity issue to create panic and shorten your decision time.",
        "The request sounds formal, but the pressure and payment path do not match how real agencies operate.",
    ],
    "unknown-number": [
        "The first goal is simply to get a reply, then the real pressure appears once engagement starts.",
        "A vague but urgent message creates curiosity before moving toward links, calls, or payment pressure.",
        "The lack of clear context is intentional because it gives the scammer room to shape the conversation after you respond.",
    ],
    "phishing": [
        "The message depends on visual familiarity and speed rather than on independent proof.",
        "A trusted-looking link or page is meant to keep you from opening the real site yourself.",
        "The message becomes weaker the moment you ignore the link and navigate independently.",
    ],
    "general": [
        "The pressure usually appears before the proof does.",
        "The message tries to keep you inside its own version of reality instead of letting you verify outside it.",
        "A familiar-looking format is used to lower suspicion before the real request appears.",
    ],
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


def page_path(slug):
    return os.path.join(OUTPUT_DIR, slug, "index.html")


def page_exists(slug):
    return os.path.exists(page_path(slug))


def iter_match_terms(match_terms):
    if isinstance(match_terms, str):
        return [match_terms]
    if isinstance(match_terms, dict):
        values = []
        for value in match_terms.values():
            if isinstance(value, (list, tuple, set)):
                values.extend(str(v) for v in value if str(v).strip())
            elif str(value).strip():
                values.append(str(value))
        return values
    if isinstance(match_terms, (list, tuple, set)):
        return [str(term) for term in match_terms if str(term).strip()]
    return [str(match_terms)] if str(match_terms).strip() else []


def load_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        return []

    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return list(dict.fromkeys(normalize_keyword(line) for line in f if line.strip()))


def matches_cluster(keyword, match_terms):
    kw_norm = normalize_keyword(keyword)
    kw_tokens = keyword_tokens(keyword)
    kw_joined = f" {kw_norm.replace('-', ' ')} "

    for term in iter_match_terms(match_terms):
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

    for term in iter_match_terms(hub_terms):
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
        anchor = label if label.lower().endswith("scam") else f"{label} Scam Check"
        items.append({
            "slug": slug,
            "title": label,
            "href": f"/scam-check-now/{slug}/",
            "anchor": anchor,
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
        [normalize_keyword(term).replace("-", " ") for term in iter_match_terms(hub_terms) if normalize_keyword(term)],
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
<p>These are the scam themes and repeated search patterns showing up most often across the child pages in this hub.</p>
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

    for term in iter_match_terms(match_terms):
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
<p>These terms help define the category and show the types of signals, brands, channels, and scam angles this hub is built around.</p>
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
<p>These are the safest verification moves to make before you click, reply, pay, log in, or share anything sensitive.</p>
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
    if count == 0:
        return (
            f"<p>This hub is active, but it does not have related scam check pages linked yet. "
            f"As more pages are generated in the {escape_html(hub_title)} category, they should be linked here automatically.</p>"
        )

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
    for term in iter_match_terms(hub_terms):
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


def detect_hub_context(hub_slug, hub_terms):
    combined = f"{hub_slug} {' '.join(iter_match_terms(hub_terms))}".lower()

    if any(x in combined for x in ["amazon", "paypal", "bank", "zelle", "venmo", "cash app", "refund", "invoice", "payment"]):
        return "payment"
    if any(x in combined for x in ["job", "recruiter", "interview", "onboarding", "employment", "remote job"]):
        return "job"
    if any(x in combined for x in ["crypto", "wallet", "bitcoin", "ethereum", "airdrop", "nft", "seed phrase"]):
        return "crypto"
    if any(x in combined for x in ["delivery", "usps", "fedex", "ups", "shipment", "tracking", "parcel", "package"]):
        return "delivery"
    if any(x in combined for x in ["account security", "verification code", "password reset", "login", "account locked", "security alert"]):
        return "account-security"
    if any(x in combined for x in ["irs", "tax", "social security", "government", "benefits"]):
        return "government"
    if any(x in combined for x in ["unknown number", "unknown caller", "blocked number", "spoofed number", "voicemail"]):
        return "unknown-number"
    if "phishing" in combined:
        return "phishing"
    return "general"


def build_dynamic_keyword_summary_html(matched_keywords, hub_terms):
    if not matched_keywords:
        fallback = (
            "This hub is active based on the cluster mapping for this category. "
            "As generated pages accumulate here, this section will reflect the most common entities, delivery channels, and pressure patterns people are searching for."
        )
        return f"""
<section aria-labelledby="keyword-patterns-heading">
<h2 id="keyword-patterns-heading">What People Are Seeing In This Scam Category</h2>
<p>{escape_html(fallback)}</p>
</section>
""".strip()

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
    if not matched_keywords:
        return ""

    insights = get_hub_keyword_insights(matched_keywords, hub_terms)
    entities = insights["top_entities"][:8]

    if not entities:
        return ""

    items_html = "\n".join(f"<li>{escape_html(item)}</li>" for item in entities)

    return f"""
<section aria-labelledby="entity-focus-heading">
<h2 id="entity-focus-heading">Common Brands, Platforms, Or Entities Mentioned</h2>
<p>These are the names, platforms, brands, or recognizable contexts that show up most often in related search patterns across this hub.</p>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_cluster_specific_intro_html(intro, matched_keywords, hub_terms):
    if not matched_keywords:
        return f"""
<section aria-labelledby="hub-intro-heading">
<h2 id="hub-intro-heading" style="position:absolute;left:-9999px;">Hub Introduction</h2>
<p>{escape_html(intro)}</p>
<p>This hub is being maintained from the cluster definitions, even if the related child pages are not all present yet.</p>
</section>
""".strip()

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
    if not matched_keywords:
        return "related scam signals, scam warning signs, and category-level verification patterns"

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


def build_common_situations_html(hub_slug, matched_keywords, hub_terms):
    context = detect_hub_context(hub_slug, hub_terms)
    base_points = list(COMMON_SITUATION_TEMPLATES.get(context, COMMON_SITUATION_TEMPLATES["general"]))
    examples = HUB_PATTERN_EXAMPLES.get(hub_slug, [])
    combined = dedupe_preserve_order(base_points + examples)

    if not combined:
        return ""

    items_html = "\n".join(
        f"<li>{escape_html(item)}</li>"
        for item in combined[:MAX_COMMON_SITUATIONS]
    )

    return f"""
<section aria-labelledby="common-situations-heading">
<h2 id="common-situations-heading">Common Situations In This Category</h2>
<p>These are recurring situations and message patterns that often show up across the related pages in this hub.</p>
<ul>
{items_html}
</ul>
</section>
""".strip()


def build_comparison_html(hub_slug):
    pairs = HUB_COMPARISON_POINTS.get(hub_slug, GENERIC_COMPARISON_POINTS)
    if not pairs:
        return ""

    blocks = []
    for legit, scam in pairs[:MAX_COMPARISON_POINTS]:
        blocks.append(
            f"""
<div class="comparison-item">
  <div class="comparison-col legit">
    <h3>Legitimate Version</h3>
    <p>{escape_html(legit)}</p>
  </div>
  <div class="comparison-col scam">
    <h3>Scam Version</h3>
    <p>{escape_html(scam)}</p>
  </div>
</div>
""".strip()
        )

    return f"""
<section aria-labelledby="comparison-heading">
<h2 id="comparison-heading">How Legitimate And Scam Versions Usually Differ</h2>
<p>One of the safest ways to evaluate these messages is to compare how a real version behaves versus how a scam version usually tries to control the next step.</p>
{''.join(blocks)}
</section>
""".strip()


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


def validate_hub_output(hub_slug, hub_title, description, canonical, matched_keywords, link_items, html):
    errors = []

    if not hub_slug:
        errors.append("empty hub slug")
    if not hub_title.strip():
        errors.append("empty title")
    if len(description) < 110 or len(description) > 165:
        errors.append("description length out of target range")
    if not canonical.endswith(f"/{hub_slug}/"):
        errors.append("canonical mismatch")
    if html.count("<h2") < 8:
        errors.append("insufficient section depth")
    if len(html) < 8000:
        errors.append("page html too thin")
    if "<main" not in html:
        errors.append("missing main landmark")
    if "application/ld+json" not in html:
        errors.append("missing schema")
    if "og:title" not in html or "twitter:title" not in html:
        errors.append("missing social metadata")
    if not link_items:
        errors.append("no linked child pages")
    if matched_keywords and len(link_items) == 0:
        errors.append("matched keywords exist but no child pages were found on disk")

    return errors


def dedupe_preserve_order(items):
    seen = set()
    output = []

    for item in items:
        key = compact_spaces(str(item).lower())
        if key and key not in seen:
            seen.add(key)
            output.append(item)

    return output


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
    common_situations_html = build_common_situations_html(hub_slug, matched_keywords, hub_terms)
    comparison_html = build_comparison_html(hub_slug)

    jump_links = []
    sections = []

    if top_scam_types_html:
        jump_links.append('<a href="#variations-heading">Variations</a>')
        sections.append(f"""
<div class="section-card">
{top_scam_types_html}
</div>
""".strip())

    if common_situations_html:
        jump_links.append('<a href="#common-situations-heading">Situations</a>')
        sections.append(f"""
<div class="section-card">
{common_situations_html}
</div>
""".strip())

    jump_links.append('<a href="#keyword-patterns-heading">What People See</a>')
    sections.append(f"""
<div class="section-card">
{dynamic_keyword_summary_html}
</div>
""".strip())

    if comparison_html:
        jump_links.append('<a href="#comparison-heading">Real vs Scam</a>')
        sections.append(f"""
<div class="section-card">
{comparison_html}
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
<section class="section-card warning-surface" aria-labelledby="warning-signs-heading">
<h2 id="warning-signs-heading">Common Warning Signs</h2>
<p>These are the risk signals that repeatedly show up across this category and should make you slow down before you act.</p>
<ul>
{warning_signs_html}
</ul>
</section>
""".strip())

    jump_links.append('<a href="#verify-heading">Verify Safely</a>')
    sections.append(f"""
<div class="section-card verify-surface">
{verify_steps_html}
</div>
""".strip())

    jump_links.append('<a href="#related-checks-heading">Related Checks</a>')
    sections.append(f"""
<section class="section-card link-surface" aria-labelledby="related-checks-heading">
<h2 id="related-checks-heading">Related Scam Checks</h2>
{link_summary_html}
<div class="link-box">
{"<ul>" + links_html + "</ul>" if link_items else "<p>No linked child pages are available yet for this hub.</p>"}
</div>
</section>
""".strip())

    sections.append("""
<section class="section-card closing-surface" aria-labelledby="what-to-do-heading">
<h2 id="what-to-do-heading">What To Do</h2>
<p>If something looks off, do not rely on the message itself. Go to the official website, app, or verified support channel directly and confirm the situation there before taking action.</p>
<p>If money, codes, credentials, or wallet access are involved, slowing down is often the safest move. Independent verification matters more than anything the suspicious message claims.</p>
</section>
""".strip())

    jump_links.append('<a href="#faq-heading">FAQ</a>')
    sections.append(f"""
<div class="section-card faq-surface">
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
--bg:#07111f;
--bg-2:#0c1728;
--bg-3:#12203a;
--surface:rgba(255,255,255,.06);
--surface-2:rgba(255,255,255,.08);
--surface-3:rgba(255,255,255,.04);
--card:#101c33;
--card-2:#162541;
--ink:#e8f0ff;
--ink-strong:#ffffff;
--ink-dark:#132033;
--muted:#9eb0cf;
--muted-2:#7e93b5;
--line:rgba(148,163,184,.20);
--line-2:rgba(255,255,255,.10);
--cyan:#22d3ee;
--cyan-2:#06b6d4;
--blue:#3b82f6;
--blue-2:#2563eb;
--violet:#8b5cf6;
--violet-2:#7c3aed;
--emerald:#10b981;
--emerald-2:#059669;
--amber:#f59e0b;
--red:#ef4444;
--green-soft:rgba(16,185,129,.12);
--green-line:rgba(16,185,129,.26);
--red-soft:rgba(239,68,68,.10);
--red-line:rgba(239,68,68,.22);
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

.info-box,
.hero-panel,
.tool-cta-card,
.section-card,
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
margin:0 0 20px;
padding:18px;
font-size:15px;
color:#d6e3f7;
font-weight:800;
line-height:1.7;
}}

h1,h2,h3{{
margin:0 0 14px;
color:#fff;
line-height:1.08;
letter-spacing:-.035em;
font-weight:900;
text-wrap:balance;
}}

h1{{font-size:42px;}}
h2{{font-size:30px;margin-top:0;}}
h3{{font-size:22px;margin-top:0;}}

p, li{{
font-size:17px;
color:#d7e4f8;
}}

p{{
margin:0 0 16px;
}}

ul,ol{{
margin:0;
padding-left:22px;
}}

li{{
margin-bottom:10px;
}}

li::marker{{
color:#8be9ff;
}}

.jump-links{{
display:flex;
flex-wrap:wrap;
gap:10px;
margin:0 0 22px;
}}

.jump-links a{{
display:inline-flex;
align-items:center;
justify-content:center;
padding:10px 13px;
border-radius:999px;
font-size:13px;
font-weight:900;
color:#dbeafe;
background:rgba(255,255,255,.06);
border:1px solid rgba(255,255,255,.10);
box-shadow:var(--shadow-sm);
}}

.jump-links a:hover{{
text-decoration:none;
transform:translateY(-1px);
}}

.tool-cta-card{{
margin:0 0 24px;
padding:24px;
text-align:center;
background:
linear-gradient(135deg, rgba(34,211,238,.10) 0%, rgba(139,92,246,.10) 100%),
linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.04) 100%);
}}

.tool-cta-card h3{{
margin:0 0 8px;
font-size:28px;
}}

.tool-cta-card p{{
margin:0 auto 14px;
max-width:620px;
font-size:15px;
line-height:1.7;
color:#c8d6ec;
font-weight:700;
}}

.tool-cta-button{{
display:block;
width:100%;
text-decoration:none;
text-align:center;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
font-weight:900;
padding:16px;
border-radius:18px;
box-shadow:0 18px 40px rgba(34,211,238,.20);
font-size:17px;
letter-spacing:.2px;
}}

.tool-cta-button:hover{{
text-decoration:none;
transform:translateY(-1px);
box-shadow:0 22px 44px rgba(34,211,238,.24);
}}

.tool-cta-note{{
margin-top:12px;
font-size:13px;
color:#9fb0cc;
font-weight:900;
}}

.section-card{{
padding:20px;
}}

.section-card p:last-child,
.section-card ul:last-child,
.section-card ol:last-child{{
margin-bottom:0;
}}

.warning-surface{{
background:
linear-gradient(135deg, rgba(239,68,68,.10) 0%, rgba(139,92,246,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.verify-surface{{
background:
linear-gradient(135deg, rgba(16,185,129,.10) 0%, rgba(34,211,238,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.link-surface{{
background:
linear-gradient(135deg, rgba(59,130,246,.10) 0%, rgba(139,92,246,.10) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.closing-surface{{
background:
linear-gradient(135deg, rgba(16,185,129,.08) 0%, rgba(139,92,246,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.faq-surface{{
background:
linear-gradient(135deg, rgba(139,92,246,.10) 0%, rgba(34,211,238,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}}

.link-box{{
margin-top:16px;
padding:18px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
}}

.link-box ul{{
padding-left:20px;
}}

.link-box li{{
margin-bottom:12px;
}}

.link-box a{{
color:#8be9ff;
font-weight:900;
}}

.meta-strip{{
margin:22px 0 0;
padding:16px 18px;
font-size:14px;
font-weight:900;
color:#d8e5f8;
line-height:1.7;
}}

.section-divider{{
height:1px;
background:linear-gradient(90deg, transparent, rgba(139,92,246,.45), rgba(34,211,238,.45), transparent);
margin:28px 0;
}}

.faq-item + .faq-item{{
margin-top:12px;
padding-top:12px;
border-top:1px solid rgba(255,255,255,.10);
}}

.faq-item h3{{
font-size:20px;
margin-bottom:8px;
}}

.comparison-item{{
display:grid;
grid-template-columns:1fr 1fr;
gap:14px;
margin-top:14px;
}}

.comparison-col{{
padding:16px;
border-radius:18px;
border:1px solid rgba(255,255,255,.10);
background:rgba(255,255,255,.04);
}}

.comparison-col.legit{{
background:var(--green-soft);
border-color:var(--green-line);
}}

.comparison-col.scam{{
background:var(--red-soft);
border-color:var(--red-line);
}}

.comparison-col h3{{
font-size:18px;
margin-bottom:8px;
}}

.comparison-col p:last-child{{
margin-bottom:0;
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
h1{{font-size:32px;}}
h2{{font-size:24px;}}
h3{{font-size:20px;}}
p,li{{font-size:16px;}}
.jump-links{{gap:8px;}}
.jump-links a{{font-size:13px;padding:9px 11px;}}
.comparison-item{{grid-template-columns:1fr;}}
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
      <div class="hero-badge">Scam category hub</div>
      <div class="hero-badge">Premium internal linking</div>
      <div class="hero-badge">Built for repeat use</div>
    </div>

    <h1>{escape_html(hub_title)}</h1>
    <p>Review warning signs, compare related scam checks, and understand how this pattern usually works before you click, reply, send money, or share information.</p>

    <div class="hero-trust">
      <div class="hero-trust-chip">Check before you click</div>
      <div class="hero-trust-chip">Check before you reply</div>
      <div class="hero-trust-chip">Check before you send money</div>
    </div>
  </div>

  <main class="content-section">
    <div class="breadcrumbs">
      <a href="{SITE}/check">Scam Check Now</a> / <a href="{SITE}/scam-check-now/">Scam Check Hubs</a> / <span>{escape_html(hub_title)}</span>
    </div>

    <div class="hero-panel">
      <div class="hero-panel-kicker">Category hub</div>
      <h2>Compare scam patterns faster</h2>
      <p>This hub groups together related scam checks so you can review warning signs, compare patterns, and quickly navigate to the most relevant pages in this category.</p>
    </div>

    <div class="info-box">
      These scam patterns often change in wording, format, brand references, and delivery method, but the underlying tactics usually stay the same: urgency, impersonation, suspicious links, fake support, payment pressure, or requests for sensitive information.
    </div>

    {cluster_specific_intro_html}
    <p>Use the related scam checks below to review specific variations, compare warning signs, and understand what to do next before you click, reply, send money, or share anything sensitive.</p>

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

    validation_warning_count = 0
    built_count = 0
    validation_details = []

    for hub_slug, raw_match_terms in CLUSTERS.items():
        match_terms = iter_match_terms(raw_match_terms)
        matched = [kw for kw in keywords if matches_cluster(kw, match_terms)] if keywords else []

        matched = dedupe_cluster_keywords(matched)
        matched = sorted(matched, key=lambda k: score_keyword(k, match_terms))[:MAX_LINKS_PER_HUB]

        link_items = build_related_link_items(matched)

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
        )

        if validation_errors:
            validation_warning_count += 1
            validation_details.append({
                "hub_slug": hub_slug,
                "matched_keywords": len(matched),
                "linked_pages": len(link_items),
                "errors": validation_errors,
            })
            print(f"Validation warning for {hub_slug}: {'; '.join(validation_errors)}")

        save_hub(hub_slug, html)
        built_count += 1
        print(f"Built hub: {hub_slug} (matched keywords: {len(matched)}, linked pages: {len(link_items)})")

    report = {
        "keywords_loaded": len(keywords),
        "hubs_built": built_count,
        "validation_warnings": validation_warning_count,
        "validation_details": validation_details,
    }
    save_report(report)

    print("\n--- HUB BUILD REPORT ---")
    print(f"Keywords loaded: {len(keywords)}")
    print(f"Hubs built: {built_count}")
    print(f"Validation warnings: {validation_warning_count}")
    print(f"Saved report: {REPORT_PATH}")


if __name__ == "__main__":
    main()