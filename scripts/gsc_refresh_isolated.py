import os
import re
import html
import json
from typing import List, Dict, Any


def parse_positive_int(value: str, default: int) -> int:
    try:
        parsed = int(str(value).strip())
        if parsed <= 0:
            return default
        return parsed
    except (TypeError, ValueError):
        return default


REFRESH_SCOPE = os.getenv("REFRESH_SCOPE", "metadata").strip().lower()
MAX_URLS = parse_positive_int(os.getenv("MAX_URLS_TO_REFRESH", "10"), 10)
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"

TARGET_FILES: List[str] = [
    "scam-check-now/is-google-security-warning-email-legit-or-scam/index.html",
    "scam-check-now/paypal-suspicious-login-email-scam/index.html",
    "scam-check-now/is-google-account-disabled-email-legit-or-scam/index.html",
    "scam-check-now/is-apple-billing-update-email-legit-or-scam/index.html",
    "scam-check-now/is-recruiter-email-from-unknown-company-legit-or-scam/index.html",
]

PAGE_SEO: Dict[str, Dict[str, Any]] = {
    "scam-check-now/is-google-security-warning-email-legit-or-scam/index.html": {
        "title": "Is Google Security Warning Email Legit or a Scam? Real or Fake Warning Signs",
        "description": "Got a Google security warning email or Google Gmail security warning? Learn how to tell if it is legit or a scam, what phishing red flags to watch for, and what to do before you click, sign in, reply, or share information.",
        "h1": "Is Google Security Warning Email Legit or a Scam?",
        "intro": "Got a Google security warning email or Google Gmail security warning? Some account security alerts are real, but scammers also send fake security alert messages and fake Google warning emails to steal passwords, verification codes, or personal information. Learn the warning signs and how to check if it is legit or fake before you click, sign in, reply, or share anything.",
        "body_html": """
<div class="content-block" data-context="security" data-mode="comparison">
<p>A Google security warning email can be legitimate, but it is also a common phishing theme used by scammers. The safest way to judge it is not by how polished the email looks, but by whether the warning still makes sense after you verify it directly through your Google Account, Gmail settings, or official Google security pages. That is especially true if the message looks like a Google Gmail security warning or a general security alert message.</p>

<h2>How Real And Fake Google Security Warning Emails Usually Differ</h2>
<p>A legitimate Google security warning email usually reflects real account activity and can be confirmed independently through your Google Account, Gmail app, or official Google account security dashboard. A scam version often tries to keep you inside the email itself by pushing you to click a link, sign in immediately, or share information before you verify anything on your own.</p>

<p>Scammers use Google warning emails because account-security messages create immediate fear. A fake email may claim there was a suspicious login, unusual device activity, password reset attempt, or urgent problem with your Google account. Some fake messages are written more broadly as a security alert message, while others imitate a more specific Google Gmail security warning. The goal is the same: make you react quickly before you slow down and confirm whether the warning is actually real.</p>

<p>Many fake Google security emails look convincing. They may include Google branding, security wording, account-related details, and a button that appears to lead to a real sign-in page. Some even copy the style of genuine Google alerts very closely. But a polished design does not make the email trustworthy. What matters is whether the alert matches real account activity and whether the action path stays inside official Google channels.</p>

<p>A real Google alert should still make sense after you ignore the email itself and open your Google Account directly. If the message claims your Gmail account has a security issue, you should be able to confirm that inside your real account security settings without using the message link. A scam version often becomes weaker the moment you stop relying on the email.</p>

<p>Phishing versions often push one urgent next step. That may be clicking a sign-in link, confirming your identity by email, entering a one-time code, or reviewing an account issue through a page linked from the message. In some cases, the scam continues after the click with fake Google login screens meant to capture credentials.</p>

<p>If you interact with a fake Google security warning email, the risks can be serious. Clicking a phishing link can lead to a fake sign-in page designed to steal your password. Entering verification codes can help attackers bypass account protections. Replying with personal details can expose more information that scammers can later use for account takeover or identity theft.</p>

<p>That is why independent verification matters so much. A real Google security warning should still make sense when you ignore the email link and instead open your Google Account directly through the official website or app. A scam version usually falls apart the moment you stop relying on the message itself.</p>
</div>

<h2>Signs This Might Be A Scam</h2>
<ul>
<li>Unexpected Google security warnings or security alert messages that do not match any real account activity</li>
<li>Messages that claim to be a Google Gmail security warning but push you to sign in immediately from the email</li>
<li>Requests for passwords, verification codes, or personal information</li>
<li>Pressure about suspicious logins, locked access, or urgent account review</li>
<li>Sender details, reply instructions, or websites that do not clearly match official Google channels</li>
</ul>

<h2>How To Respond Safely</h2>
<p>A careful verification step can stop most Google phishing scams before any damage happens.</p>
<p>If you receive a Google security warning email, do not click links or trust contact details inside the message right away. Open your Google Account directly, review recent security activity through official Google pages, and change your password only through the real account dashboard if needed. If the warning is real, it should still appear there. If it is fake, checking independently can keep you from handing over access, codes, or personal information to a scammer.</p>
""".strip(),
        "faq_entities": [
            {
                "@type": "Question",
                "name": "Can a Google security warning email be real?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes, some Google security warning emails are legitimate, but scammers also imitate them. The safest step is to verify the warning directly through your Google Account, Gmail app, or official Google security pages."
                },
            },
            {
                "@type": "Question",
                "name": "What if the email looks like a Google Gmail security warning?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Even if it looks like a Google Gmail security warning, do not trust the email by itself. Open your Google Account directly and check recent security activity there. A real warning should still appear through official Google channels."
                },
            },
            {
                "@type": "Question",
                "name": "How can I tell if a Google security warning email is a scam?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Watch for urgent pressure, links that push you to sign in immediately, requests for passwords or verification codes, and sender details or websites that do not clearly match official Google channels. A real warning should still make sense when you verify it independently."
                },
            },
        ],
    },
    "scam-check-now/paypal-suspicious-login-email-scam/index.html": {
        "title": "PayPal Suspicious Login Email Scam? Real or Fake Warning Signs",
        "description": "Got a PayPal suspicious login email or PayPal security alert email? Learn how to tell if it is real or a scam, what phishing red flags to watch for, and what to do before you click, sign in, or share information.",
        "h1": "PayPal Suspicious Login Email Scam?",
        "intro": "Got a PayPal suspicious login email or PayPal security alert email? Some login alerts are real, but scammers also send fake PayPal warning emails to steal your password, payment details, or verification codes. Learn the warning signs and how to check if it is real or fake before you click, sign in, reply, or share anything.",
        "body_html": """
<div class="content-block" data-context="payment" data-mode="comparison">
<p>A PayPal suspicious login email can be legitimate, but it is also a common phishing tactic used by scammers. The safest way to judge it is not by how official the email looks, but by whether the alert still makes sense after you verify it directly through your PayPal account or official PayPal support channels.</p>

<h2>How Real And Fake PayPal Suspicious Login Emails Usually Differ</h2>
<p>A legitimate PayPal suspicious login email usually reflects real account activity and can be confirmed independently through your PayPal account, app, or official PayPal website. A scam version often tries to keep you inside the email itself by pushing you to click a link, sign in immediately, or confirm details before you verify anything on your own.</p>

<p>Scammers use PayPal login alerts because money-related account messages create immediate fear. A fake email may claim there was an unrecognized login, unusual device activity, account limitation, or security problem that needs urgent review. Some versions are written more like a PayPal security alert email, but the goal is the same: make you react quickly before you slow down and confirm whether the alert is actually real.</p>

<p>Many fake PayPal suspicious login emails look polished. They may include PayPal branding, account language, payment references, and buttons that appear to lead to a real sign-in page. Some even include case numbers, timestamps, or fake support instructions. But a convincing design does not make the message trustworthy. What matters is whether the alert matches real account activity and whether the action path stays inside official PayPal channels.</p>

<p>A real PayPal suspicious login alert should still hold up when you open PayPal directly through the official app or website. If the email says there was unusual account access, recent login or security activity should make sense there too. A scam version usually depends on you trusting the email itself instead of verifying independently.</p>

<p>Phishing versions often push one urgent next step. That may be clicking a sign-in link, confirming your identity by email, entering a one-time code, or reviewing account activity through a page linked from the message. In some cases, the scam continues after the click with fake PayPal login pages designed to capture credentials and payment information.</p>

<p>If you interact with a fake PayPal suspicious login email, the risks can be serious. Clicking a phishing link can lead to a fake sign-in page that steals your login details. Entering verification codes can help attackers bypass security protections. Sharing payment details or personal information can expose your account to fraud and identity theft.</p>

<p>That is why independent verification matters so much. A real PayPal suspicious login alert should still make sense when you ignore the email link and instead open your PayPal account directly through the official website or app. A scam version usually falls apart the moment you stop relying on the message itself.</p>
</div>

<h2>Signs This Might Be A Scam</h2>
<ul>
<li>Unexpected PayPal login alerts or PayPal security alert emails that do not match any real account activity</li>
<li>Links that push you to sign in or review a suspicious login directly from the email</li>
<li>Requests for passwords, one-time codes, card details, or personal information</li>
<li>Pressure about account limitation, unusual device access, or urgent review</li>
<li>Sender details, reply instructions, or websites that do not clearly match official PayPal channels</li>
</ul>

<h2>How To Respond Safely</h2>
<p>A careful verification step can stop most PayPal phishing scams before any damage happens.</p>
<p>If you receive a PayPal suspicious login email, do not click links or trust contact details inside the message right away. Open your PayPal account directly through the official site or app and review recent login or security activity there. If the alert is real, it should still appear through official channels. If it is fake, checking independently can keep you from handing over access, codes, or payment details to a scammer.</p>
""".strip(),
        "faq_entities": [
            {
                "@type": "Question",
                "name": "Can a PayPal suspicious login email be real?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes, some PayPal suspicious login emails are legitimate, but scammers also imitate them. The safest step is to verify the alert directly through your PayPal account or the official PayPal app or website."
                },
            },
            {
                "@type": "Question",
                "name": "Is a PayPal security alert email always a scam?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "No, some PayPal security alert emails are real, but you should never trust the email alone. Open PayPal directly through the official app or website and verify the alert there first."
                },
            },
            {
                "@type": "Question",
                "name": "What should I do if I clicked a fake PayPal suspicious login email?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Stop entering information, close the page, and check your PayPal account directly through the official site or app. If you entered login details or codes, change your password right away and review your account security and recent activity immediately."
                },
            },
        ],
    },
    "scam-check-now/is-google-account-disabled-email-legit-or-scam/index.html": {
        "title": "Is Google Account Disabled Email Legit or a Scam? Real or Fake Warning Signs",
        "description": "Got a Google account disabled email or Google account suspension email? Learn how to tell if it is legit or a scam, what phishing red flags to watch for, and what to do before you click, sign in, or share information.",
        "h1": "Is Google Account Disabled Email Legit or a Scam?",
        "intro": "Got a Google account disabled email or Google account suspension email? Some account notices are real, but scammers also send fake Google disabled-account emails to steal passwords, verification codes, or personal information. Learn the warning signs and how to check if it is legit or fake before you click, sign in, reply, or share anything.",
        "body_html": """
<div class="content-block" data-context="security" data-mode="comparison">
<p>A Google account disabled email can be legitimate, but it is also a common phishing theme used by scammers. The safest way to judge it is not by how serious the email sounds, but by whether the notice still makes sense after you verify it directly through your Google account or official Google support pages.</p>

<h2>How Real And Fake Google Account Disabled Emails Usually Differ</h2>
<p>A legitimate Google account disabled email usually reflects a real account issue and can be confirmed independently through your Google Account, Gmail app, or official Google recovery pages. A scam version often tries to keep you inside the email itself by pushing you to click a link, submit an appeal, or confirm details before you verify anything on your own.</p>

<p>Scammers use disabled-account warnings because account access messages create immediate panic. A fake email may claim your Google account was disabled, restricted, suspended, or flagged for policy or security issues. Some versions are framed more like a Google account suspension email, but the goal stays the same: make you react quickly before you slow down and confirm whether the notice is actually real.</p>

<p>Many fake Google account disabled emails look convincing. They may include Google branding, policy language, support wording, and buttons that appear to lead to a real recovery or appeal page. Some even mention deadlines, account review, or restored access after confirmation. But a polished design does not make the message trustworthy. What matters is whether the warning matches real account status and whether the action path stays inside official Google channels.</p>

<p>A real Google account disabled notice should still make sense when you ignore the email and open your Google account directly through the official site or app. If the email says your account was suspended or disabled, the problem should still be visible through official recovery or support routes. A fake version often depends on the message itself for credibility.</p>

<p>Phishing versions often push one urgent next step. That may be signing in through a link, submitting account details, entering a one-time code, or opening an appeal page linked from the email. In some cases, the scam continues after the click with fake login screens or recovery forms designed to capture credentials.</p>

<p>If you interact with a fake Google account disabled email, the risks can be serious. Clicking a phishing link can lead to a fake sign-in page that steals your password. Entering verification codes can help attackers bypass security protections. Sharing personal information can expose you to account takeover or identity theft.</p>

<p>That is why independent verification matters so much. A real Google account disabled notice should still make sense when you ignore the email link and instead open your Google account directly through the official site or app. A scam version usually falls apart the moment you stop relying on the message itself.</p>
</div>

<h2>Signs This Might Be A Scam</h2>
<ul>
<li>Unexpected Google disabled-account notices or Google account suspension emails that do not match your real account status</li>
<li>Links that push you to sign in, appeal, or verify information directly from the email</li>
<li>Requests for passwords, verification codes, or personal information</li>
<li>Pressure about deadlines, permanent loss of access, or urgent account review</li>
<li>Sender details, reply instructions, or websites that do not clearly match official Google channels</li>
</ul>

<h2>How To Respond Safely</h2>
<p>A careful verification step can stop most Google phishing scams before any damage happens.</p>
<p>If you receive a Google account disabled email, do not click links or trust contact details inside the message right away. Open your Google account directly, check account status through official Google pages, and use only real recovery or support routes if needed. If the notice is real, it should still appear there. If it is fake, checking independently can keep you from handing over access, codes, or personal information to a scammer.</p>
""".strip(),
        "faq_entities": [
            {
                "@type": "Question",
                "name": "Can a Google account disabled email be real?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes, some Google account disabled emails are legitimate, but scammers also imitate them. The safest step is to verify the notice directly through your Google account or official Google recovery and support pages."
                },
            },
            {
                "@type": "Question",
                "name": "What if the message says my Google account is suspended?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "If the message says your Google account is suspended or disabled, do not trust the email alone. Open your Google account directly and use official Google recovery or support pages to verify whether the issue is real."
                },
            },
            {
                "@type": "Question",
                "name": "What should I do if I clicked a fake Google account disabled email?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Stop entering information, close the page, and check your Google account directly through the official site or app. If you entered login details or codes, change your password right away and review your account security settings immediately."
                },
            },
        ],
    },
    "scam-check-now/is-apple-billing-update-email-legit-or-scam/index.html": {
        "title": "Is Apple Billing Update Email Legit or a Scam? Real or Fake Warning Signs",
        "description": "Got an Apple billing update email? Learn how to tell if it is legit or a scam, what phishing red flags to watch for, and what to do before you click, sign in, or update payment details.",
        "h1": "Is Apple Billing Update Email Legit or a Scam?",
        "intro": "Got an Apple billing update email? Some billing notices are real, but scammers also send fake Apple payment emails to steal your Apple ID login details, card information, or verification codes. Learn the warning signs and how to check if it is legit or fake before you click, sign in, update payment details, or share anything.",
        "body_html": """
<div class="content-block" data-context="payment" data-mode="comparison">
<p>An Apple billing update email can be legitimate, but it is also a common phishing tactic used by scammers. The safest way to judge it is not by how official the email looks, but by whether the billing issue still makes sense after you verify it directly through your Apple account or official Apple support channels.</p>

<h2>How Real And Fake Apple Billing Update Emails Usually Differ</h2>
<p>A legitimate Apple billing update email usually reflects a real payment or account issue and can be confirmed independently through your Apple ID settings, App Store account, or official Apple billing pages. A scam version often tries to keep you inside the email itself by pushing you to click a link, sign in immediately, or update payment details before you verify anything on your own.</p>

<p>Scammers use Apple billing warnings because payment-related messages create immediate concern. A fake email may claim your payment method failed, your subscription will be interrupted, your account has a billing issue, or your Apple services will be disabled unless you act quickly. The goal is to make you react before you slow down and confirm whether the issue is actually real.</p>

<p>Many fake Apple billing update emails look polished. They may include Apple branding, subscription wording, payment references, and buttons that appear to lead to a real billing page. Some even mention invoices, account review, or urgent verification. But a polished design does not make the message trustworthy. What matters is whether the billing issue matches real account activity and whether the action path stays inside official Apple channels.</p>

<p>A real Apple billing notice should still make sense after you ignore the email and open your Apple account directly. If there is a real payment problem, subscription issue, or failed billing method, you should be able to confirm it inside official Apple settings without using the message link. A scam version often depends on speed and message-based trust.</p>

<p>Phishing versions often push one urgent next step. That may be signing in through a link, updating payment details by email, entering a one-time code, or reviewing billing activity through a page linked from the message. In some cases, the scam continues after the click with fake Apple ID login pages designed to capture credentials and card details.</p>

<p>If you interact with a fake Apple billing update email, the risks can be serious. Clicking a phishing link can lead to a fake sign-in page that steals your Apple ID credentials. Entering card details can expose your payment information. Sharing verification codes can help attackers bypass security protections and gain access to your account.</p>

<p>That is why independent verification matters so much. A real Apple billing update notice should still make sense when you ignore the email link and instead open your Apple account directly through the official website or app settings. A scam version usually falls apart the moment you stop relying on the message itself.</p>
</div>

<h2>Signs This Might Be A Scam</h2>
<ul>
<li>Unexpected Apple billing notices that do not match any real payment issue in your account</li>
<li>Links that push you to sign in or update payment details directly from the email</li>
<li>Requests for passwords, one-time codes, card details, or personal information</li>
<li>Pressure about cancelled subscriptions, disabled services, or urgent account review</li>
<li>Sender details, reply instructions, or websites that do not clearly match official Apple channels</li>
</ul>

<h2>How To Respond Safely</h2>
<p>A careful verification step can stop most Apple phishing scams before any damage happens.</p>
<p>If you receive an Apple billing update email, do not click links or trust contact details inside the message right away. Open your Apple account directly, check billing and subscription details through official Apple settings, and update payment methods only through real Apple pages if needed. If the notice is real, it should still appear there. If it is fake, checking independently can keep you from handing over access, codes, or card details to a scammer.</p>
""".strip(),
        "faq_entities": [
            {
                "@type": "Question",
                "name": "Can an Apple billing update email be real?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes, some Apple billing update emails are legitimate, but scammers also imitate them. The safest step is to verify the notice directly through your Apple account, subscription settings, or official Apple billing pages."
                },
            },
            {
                "@type": "Question",
                "name": "How can I tell if an Apple billing update email is a scam?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Watch for urgent pressure, links that push you to sign in or update payment details immediately, requests for passwords or one-time codes, and sender details or websites that do not clearly match official Apple channels. A real notice should still make sense when you verify it independently."
                },
            },
            {
                "@type": "Question",
                "name": "What should I do if I clicked a fake Apple billing update email?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Stop entering information, close the page, and check your Apple account directly through the official site or account settings. If you entered login details, card information, or codes, change your password right away and review your account security immediately."
                },
            },
        ],
    },
    "scam-check-now/is-recruiter-email-from-unknown-company-legit-or-scam/index.html": {
        "title": "Is Recruiter Email From Unknown Company Legit or a Scam? Real or Fake Warning Signs",
        "description": "Got a recruiter email from an unknown company or a recruiter asking for money? Learn how to tell if it is legit or a scam, what red flags to watch for, and what to do before you reply, click, or share personal information.",
        "h1": "Is Recruiter Email From Unknown Company Legit or a Scam?",
        "intro": "Got a recruiter email from an unknown company or a recruiter asking for money? Some recruiting messages are legitimate, but scammers also send fake recruiter emails to steal personal information, push fake job offers, or collect payment details. Learn the warning signs and how to check if it is legit or fake before you reply, click, interview, or share anything.",
        "body_html": """
<div class="content-block" data-context="job" data-mode="comparison">
<p>A recruiter email from an unknown company can be legitimate, but it is also a common scam setup used by fraudsters. The safest way to judge it is not by how professional the email sounds, but by whether the recruiter, company, and job still make sense after you verify them independently through official sources.</p>

<h2>How Real And Fake Recruiter Emails Usually Differ</h2>
<p>A legitimate recruiter email usually points back to a real company, a verifiable recruiter identity, and a role that can be confirmed independently through the company website, LinkedIn, or other trusted channels. A scam version often tries to keep you inside the email itself by pushing you to reply quickly, move to another app, or share personal information before you verify anything on your own.</p>

<p>Scammers use recruiter emails because job opportunities create hope, urgency, and curiosity. A fake recruiter message may promise a high-paying role, remote flexibility, fast hiring, or immediate interview access. In many cases the scam becomes much clearer when the recruiter starts asking for money, background-check fees, equipment purchases, or payment details. The goal is to make you react quickly before you slow down and confirm whether the recruiter and company are actually real.</p>

<p>Many fake recruiter emails look polished. They may include a realistic signature, job description, company wording, and professional-sounding next steps. Some even copy real job postings or use names that sound like legitimate hiring staff. But a polished design does not make the message trustworthy. What matters is whether the recruiter identity, company, and job survive independent checking.</p>

<p>A real recruiter should still make sense after outside verification. You should be able to confirm the company, the recruiter, and the role through the official company website, LinkedIn, or another trusted source. A scam version often gets weaker the moment you stop relying on the email itself and start checking independently.</p>

<p>Scam versions often push one urgent next step. That may be replying with personal information, moving to Telegram or WhatsApp, paying for equipment, completing fake onboarding, or clicking a link to submit documents. If a recruiter is asking for money early in the process, that is a major red flag. In some cases, the scam continues after contact with fake interviews, fake offer letters, or direct payment requests.</p>

<p>If you interact with a fake recruiter email, the risks can be serious. Sharing your resume is usually not the main danger by itself, but sharing your address, date of birth, ID documents, banking details, or payment information can expose you to fraud or identity theft. In some scams, victims lose money through fake background check fees, equipment purchases, or payment-setup traps.</p>

<p>That is why independent verification matters so much. A real recruiter email should still make sense when you ignore the message alone and instead verify the recruiter, company, and role through official channels. A scam version usually becomes weaker the moment you stop relying on the email itself.</p>
</div>

<h2>Signs This Might Be A Scam</h2>
<ul>
<li>Recruiter emails from unknown companies with no clear company website or verifiable online presence</li>
<li>Pressure to reply fast, move to another app, or continue the process outside normal hiring channels</li>
<li>Requests for sensitive personal information before any real interview process</li>
<li>Promises of unusually high pay, fast hiring, or guaranteed remote work without screening</li>
<li>A recruiter asking for money, equipment purchases, banking details, or payment setup early in the process</li>
</ul>

<h2>How To Respond Safely</h2>
<p>A careful verification step can stop most recruiter scams before any damage happens.</p>
<p>If you receive a recruiter email from an unknown company, do not rely on the email alone. Look up the company independently, verify the recruiter on the company site or LinkedIn, and confirm the job exists through trusted sources before you reply or share personal details. If the opportunity is real, it should still hold up after that verification. If it is fake, checking independently can keep you from losing money or exposing your identity to a scammer.</p>
""".strip(),
        "faq_entities": [
            {
                "@type": "Question",
                "name": "Can a recruiter email from an unknown company be real?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes, some recruiter emails from lesser-known companies can be legitimate, but scammers also use fake recruiter messages. The safest step is to verify the recruiter, company, and job independently before you reply or share personal information."
                },
            },
            {
                "@type": "Question",
                "name": "Is a recruiter asking for money a scam?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "A recruiter asking for money early in the process is a major red flag. Real employers and recruiters do not usually ask candidates to pay fees for equipment, background checks, or onboarding before a legitimate hiring process is confirmed."
                },
            },
            {
                "@type": "Question",
                "name": "What should I do if I replied to a fake recruiter email?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Stop sharing more information, break off contact, and review what details you already provided. If you shared sensitive identity, financial, or login information, take steps right away to secure those accounts and watch for fraud."
                },
            },
        ],
    },
}

REQUIRED_SEO_KEYS = ("title", "description", "h1", "intro", "body_html", "faq_entities")


def repo_path_to_url(path: str) -> str:
    normalized = path.replace("\\", "/").strip()
    if not normalized.endswith("/index.html"):
        raise ValueError(f"Unexpected page path: {path}")
    return f"https://verixiaapps.com/{normalized[:-10]}/"


def escape_text(text: str) -> str:
    return html.escape(text, quote=False)


def escape_attr(text: str) -> str:
    return html.escape(text, quote=True)


def validate_config() -> None:
    if REFRESH_SCOPE != "metadata":
        raise ValueError("Set REFRESH_SCOPE=metadata")

    if MAX_URLS <= 0:
        raise ValueError("Invalid MAX_URLS_TO_REFRESH")

    seen = set()
    for path in TARGET_FILES:
        if path in seen:
            raise ValueError(f"Duplicate target file: {path}")
        seen.add(path)

        if path not in PAGE_SEO:
            raise ValueError(f"Missing PAGE_SEO entry for target file: {path}")

        if not path.endswith("/index.html"):
            raise ValueError(f"Unexpected target file path: {path}")

    for path, seo in PAGE_SEO.items():
        if not path.endswith("/index.html"):
            raise ValueError(f"Unexpected PAGE_SEO path: {path}")

        missing = [key for key in REQUIRED_SEO_KEYS if not seo.get(key)]
        if missing:
            raise ValueError(f"Missing SEO fields for {path}: {', '.join(missing)}")

        if not isinstance(seo["faq_entities"], list) or not seo["faq_entities"]:
            raise ValueError(f"faq_entities must be a non-empty list for {path}")


def replace_title(content: str, new_title: str) -> str:
    updated, count = re.subn(
        r"(<title\b[^>]*>)(.*?)(</title>)",
        rf"\g<1>{escape_text(new_title)}\g<3>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if count == 0:
        print("WARNING: <title> not found")
    return updated


def parse_tag_attributes(tag: str) -> Dict[str, str]:
    attrs: Dict[str, str] = {}
    for match in re.finditer(
        r'([^\s=<>"\'/]+)\s*=\s*("([^"]*)"|\'([^\']*)\')',
        tag,
        flags=re.DOTALL,
    ):
        name = match.group(1).lower()
        value = match.group(3) if match.group(3) is not None else (match.group(4) or "")
        attrs[name] = value
    return attrs


def rebuild_meta_tag(original_tag: str, new_attrs: Dict[str, str]) -> str:
    if not re.match(r"<meta\b", original_tag, flags=re.IGNORECASE):
        return original_tag

    ordered_names: List[str] = []
    seen = set()

    for match in re.finditer(
        r'([^\s=<>"\'/]+)\s*=\s*("([^"]*)"|\'([^\']*)\')',
        original_tag,
        flags=re.DOTALL,
    ):
        name = match.group(1)
        lower_name = name.lower()
        if lower_name not in seen:
            ordered_names.append(lower_name)
            seen.add(lower_name)

    for name in new_attrs.keys():
        if name not in seen:
            ordered_names.append(name)
            seen.add(name)

    parts = ["<meta"]
    for name in ordered_names:
        if name in new_attrs:
            parts.append(f'{name}="{escape_attr(new_attrs[name])}"')

    closing = " />" if re.search(r"/\s*>$", original_tag) else ">"
    return " ".join(parts) + closing


def replace_meta(content: str, key: str, value: str, attr: str = "name") -> str:
    attr = attr.lower()
    key_lower = key.lower()
    meta_pattern = re.compile(r"<meta\b[^>]*>", flags=re.IGNORECASE | re.DOTALL)

    match_to_replace = None
    for match in meta_pattern.finditer(content):
        tag = match.group(0)
        attrs = parse_tag_attributes(tag)
        if attrs.get(attr, "").lower() == key_lower:
            match_to_replace = match
            break

    if match_to_replace is None:
        print(f"WARNING: meta {attr} '{key}' not found")
        return content

    original_tag = match_to_replace.group(0)
    attrs = parse_tag_attributes(original_tag)
    attrs["content"] = value
    new_tag = rebuild_meta_tag(original_tag, attrs)

    return content[: match_to_replace.start()] + new_tag + content[match_to_replace.end() :]


def replace_first_h1(content: str, new_h1: str) -> str:
    updated, count = re.subn(
        r"(<h1\b[^>]*>)(.*?)(</h1>)",
        rf"\g<1>{escape_text(new_h1)}\g<3>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if count == 0:
        print("WARNING: <h1> not found")
    return updated


def replace_first_paragraph_after_h1(content: str, new_paragraph: str) -> str:
    pattern = re.compile(
        r"(<h1\b[^>]*>.*?</h1>)(?P<gap>(?:\s|<!--.*?-->)*)(<p\b[^>]*>)(.*?)(</p>)",
        flags=re.DOTALL | re.IGNORECASE,
    )
    updated, count = pattern.subn(
        rf"\1\g<gap>\3{escape_text(new_paragraph)}\5",
        content,
        count=1,
    )
    if count == 0:
        print("WARNING: first paragraph after <h1> not found")
    return updated


def replace_seo_content_block(content: str, new_inner_html: str) -> str:
    open_pattern = re.compile(
        r'<div\b(?=[^>]*\bid=["\']seoContent["\'])[^>]*>',
        flags=re.IGNORECASE,
    )
    open_match = open_pattern.search(content)
    if not open_match:
        print("WARNING: seoContent block not found")
        return content

    start_open = open_match.start()
    end_open = open_match.end()

    tag_pattern = re.compile(r'</?div\b[^>]*>', flags=re.IGNORECASE)
    depth = 1
    search_pos = end_open
    close_end = None

    while True:
        tag_match = tag_pattern.search(content, search_pos)
        if not tag_match:
            break

        tag_text = tag_match.group(0)
        if tag_text.lower().startswith("</div"):
            depth -= 1
            if depth == 0:
                close_end = tag_match.end()
                break
        else:
            depth += 1

        search_pos = tag_match.end()

    if close_end is None:
        print("WARNING: seoContent closing </div> not found")
        return content

    original_block = content[start_open:close_end]
    opening_tag = content[start_open:end_open]
    new_block = f"{opening_tag}{new_inner_html}</div>"

    if original_block == new_block:
        return content

    return content[:start_open] + new_block + content[close_end:]


def update_jsonld_object(obj: Any, seo: Dict[str, Any], page_url: str) -> None:
    if isinstance(obj, list):
        for item in obj:
            update_jsonld_object(item, seo, page_url)
        return

    if not isinstance(obj, dict):
        return

    obj_type = obj.get("@type")
    obj_url = obj.get("url")
    obj_name = obj.get("name", "")

    if obj_type in {"CollectionPage", "WebPage"}:
        obj["name"] = seo["title"]
        obj["description"] = seo["description"]
        if obj.get("url") == page_url or obj_type == "WebPage":
            obj["url"] = page_url

    elif obj_type == "FAQPage":
        obj["mainEntity"] = seo["faq_entities"]

    elif obj_type == "BreadcrumbList":
        items = obj.get("itemListElement")
        if isinstance(items, list) and items:
            for item in items:
                if not isinstance(item, dict):
                    continue
                item_ref = item.get("item")
                if isinstance(item_ref, str) and item_ref == page_url:
                    item["name"] = seo["h1"]

            last_item = items[-1]
            if isinstance(last_item, dict):
                last_item["name"] = seo["h1"]

    elif obj_type == "ItemList" and isinstance(obj_name, str) and "Related Scam Checks" in obj_name:
        obj["name"] = f"{seo['h1']} Related Scam Checks"

    elif obj_url == page_url:
        if isinstance(obj.get("name"), str):
            obj["name"] = seo["title"]
        if isinstance(obj.get("description"), str):
            obj["description"] = seo["description"]

    for value in obj.values():
        update_jsonld_object(value, seo, page_url)


def replace_jsonld(content: str, seo: Dict[str, Any], page_url: str) -> str:
    pattern = re.compile(
        r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
        flags=re.DOTALL | re.IGNORECASE,
    )

    found_any = False

    def _repl(match: re.Match) -> str:
        nonlocal found_any
        found_any = True

        open_tag, json_text, close_tag = match.groups()
        stripped = json_text.strip()

        if not stripped:
            print("WARNING: JSON-LD script empty")
            return match.group(0)

        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            print("WARNING: JSON-LD parse failed")
            return match.group(0)

        update_jsonld_object(data, seo, page_url)
        new_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return f"{open_tag}{new_json}{close_tag}"

    updated = pattern.sub(_repl, content)

    if not found_any:
        print("WARNING: JSON-LD script not found")

    return updated


def process_file(path: str) -> bool:
    if not os.path.exists(path):
        print(f"SKIPPED (missing): {path}")
        return False

    seo = PAGE_SEO.get(path)
    if not seo:
        print(f"SKIPPED (no SEO config): {path}")
        return False

    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    updated = original
    page_url = repo_path_to_url(path)

    updated = replace_title(updated, seo["title"])
    updated = replace_meta(updated, "description", seo["description"], "name")
    updated = replace_meta(updated, "og:title", seo["title"], "property")
    updated = replace_meta(updated, "og:description", seo["description"], "property")
    updated = replace_meta(updated, "twitter:title", seo["title"], "name")
    updated = replace_meta(updated, "twitter:description", seo["description"], "name")
    updated = replace_first_h1(updated, seo["h1"])
    updated = replace_first_paragraph_after_h1(updated, seo["intro"])
    updated = replace_seo_content_block(updated, seo["body_html"])
    updated = replace_jsonld(updated, seo, page_url)

    if updated == original:
        print(f"NO CHANGE: {path}")
        return False

    print(f"UPDATED: {path}")

    if not DRY_RUN:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(updated)

    return True


def main() -> None:
    validate_config()

    files = TARGET_FILES[: min(MAX_URLS, len(TARGET_FILES))]

    print(f"REFRESH_SCOPE={REFRESH_SCOPE}")
    print(f"DRY_RUN={DRY_RUN}")
    print(f"MAX_URLS_TO_REFRESH={MAX_URLS}")
    print(f"Processing {len(files)} exact repo-root SEO page(s)...")

    updated_count = 0
    for path in files:
        if process_file(path):
            updated_count += 1

    print(f"Updated {updated_count} file(s). Done.")


if __name__ == "__main__":
    main()