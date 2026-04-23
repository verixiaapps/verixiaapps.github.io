const fs = require("fs");
const path = require("path");

// ✅ EXACT PAGE TARGETED
const TARGET_PAGE = "scam-check-now/is-telegram-suspicious-activity-message-legit-or-scam/index.html";
const DRY_RUN = String(process.env.DRY_RUN).toLowerCase() === "true";

if (!TARGET_PAGE.startsWith("scam-check-now/")) {
  console.error("Only A pages allowed (scam-check-now)");
  process.exit(1);
}

if (!fs.existsSync(TARGET_PAGE)) {
  console.error("File does not exist:", TARGET_PAGE);
  process.exit(1);
}

const BACKUP_DIR = "backup";

// -----------------------------
// ONE-PASS PAGE CUSTOMIZATION
// -----------------------------
const NEW_TITLE =
  'Telegram "Suspicious Activity" Message Scam? How to Tell if It Is Real or Fake';

const NEW_META =
  "Got a Telegram suspicious activity message? Learn the warning signs, fake verification link tricks, and what to do before you click, enter a code, or hand over account details.";

const NEW_RAW_KEYWORD = "Telegram suspicious activity message";

const NEW_INSTANT_VERDICT_CARD = `
  <div class="page-shell-top-block" id="instantVerdictCardWrap" style="max-width:940px;margin:-6px auto 12px;padding:0 14px;">
    <div class="story-card lead" id="instantVerdictCard" style="margin:0;padding:20px 16px;text-align:center;">

      <div style="margin-bottom:10px;">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0%25' stop-color='%23ff7b7b'/><stop offset='100%25' stop-color='%23d94b4b'/></linearGradient></defs><circle cx='32' cy='32' r='30' fill='url(%23g)'/><path d='M32 14 L50 46 H14 Z' fill='white' opacity='0.96'/><rect x='29' y='24' width='6' height='12' rx='3' fill='%23d94b4b'/><circle cx='32' cy='41' r='3' fill='%23d94b4b'/></svg>" alt="Warning" style="width:56px;height:56px;">
      </div>

      <div style="font-size:18px;font-weight:900;color:#ff9a9a;margin-bottom:6px;">
        Risk Level: High
      </div>

      <div style="font-size:15px;font-weight:800;color:#e6f0ff;margin-bottom:4px;">
        Likely fake security alert or account takeover attempt
      </div>

      <div style="font-size:15px;font-weight:900;color:#ffffff;">
        Do not click links or share login codes inside the message. Check your Telegram account only through the official app.
      </div>

    </div>
  </div>
`;

const NEW_TOP_BLOCK = `
  <div class="page-shell-top-block" id="freshnessBlock" style="max-width:940px;margin:18px auto 20px;padding:0 14px;">
    <div class="inline-info-card" style="margin-top:0;">
      <div style="font-size:13px;font-weight:900;color:#9cecff;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">
        Updated April 2026
      </div>
      <div style="font-size:15px;font-weight:800;line-height:1.6;color:#e6f0ff;">
        People are still receiving Telegram suspicious activity messages claiming:
      </div>
      <ul style="margin:10px 0 0 18px;color:#d7e4f8;font-weight:800;line-height:1.6;">
        <li>“Unusual login detected”</li>
        <li>“Verify your account immediately”</li>
        <li>“Your Telegram account may be suspended”</li>
      </ul>
      <div style="margin-top:10px;font-size:14px;font-weight:800;color:#d7e4f8;line-height:1.6;">
        These messages often lead to fake Telegram verification pages designed to steal phone numbers, login codes, or full account access.
      </div>
    </div>
  </div>
`;

const NEW_SEO_CONTENT = `
<div class="story-stack">
  <article class="story-card lead">
    <div class="story-card-title">
      <span class="story-card-title-icon">📱</span>
      <span>What this Telegram alert often looks like</span>
    </div>
    <p>A Telegram suspicious activity message usually claims there was an unusual login, a risky device, or a security problem tied to your account. The message is built to make you act fast before you slow down and verify whether anything is actually wrong inside the official Telegram app.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">⏱️</span>
      <span>Where the pressure starts</span>
    </div>
    <p>Most versions create urgency right away. They may warn that your account will be locked, suspended, or restricted unless you confirm activity immediately. That pressure is the point. Scammers want a fast click before you notice the sender, link, or wording does not fully add up.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">🔐</span>
      <span>What scammers usually want</span>
    </div>
    <p>The goal is often account takeover. Fake Telegram security pages may ask for your phone number, login code, password, or other recovery details. Once those details are handed over, the attacker can try to access your account, lock you out, or use your profile to target other people.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">🧭</span>
      <span>How to verify it safely</span>
    </div>
    <p>The safest check is simple: do not use the link inside the message. Open Telegram yourself, review your account and active sessions there, and only trust security information you verify directly inside the official app or official Telegram resources you opened on your own.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">✅</span>
      <span>What to do next</span>
    </div>
    <p>If you have not clicked, stop there and delete the message after checking your account through official channels. If you already clicked or shared any details, treat it as urgent, secure your Telegram account, review active sessions, and change connected credentials if needed.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">⚠️</span>
      <span>Key safety rule</span>
    </div>
    <p>If the message only feels real when you follow the link inside it, that is a strong warning sign. A real security issue should still be verifiable without using the message itself.</p>
  </article>
</div>
`;

const NEW_EXAMPLE_CARD = `
    <div class="story-card" id="realExamplesCard">
      <div class="story-card-title">
        <span class="story-card-title-icon">📩</span>
        <span>Common Telegram Suspicious Activity Message Examples</span>
      </div>
      <p>Reports show people receiving Telegram warnings that say “Suspicious activity detected,” “Unusual login attempt,” or “Immediate verification required.” These messages usually claim your account is at risk unless you act fast.</p>
      <p style="margin-top:14px;">Most versions include a link, button, or fake support prompt telling you to review activity, secure your account, or confirm your identity. These pages are often built to collect your phone number, login code, or other account recovery details.</p>
      <p style="margin-top:14px;">Some versions also pretend to come from Telegram support and create urgency by warning that your account will be locked, suspended, or compromised within minutes if you do not verify right away.</p>
      <div style="margin-top:14px;font-size:14px;font-weight:800;color:#d7e4f8;line-height:1.6;">If the message only feels legitimate when you use the link inside it, that is a strong warning sign. A real security concern should still be verifiable directly inside the official Telegram app.</div>
    </div>
`;

const NEW_RELATED_LINKS = [
  {
    href: "/scam-check-now/is-whatsapp-security-alert-legit-or-scam/",
    text: "Is WhatsApp Security Alert Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-google-security-alert-message-legit-or-scam/",
    text: "Is Google Security Alert Message Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-google-unusual-activity-message-legit-or-scam/",
    text: "Is Google Unusual Activity Message Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-instagram-account-suspended-message-legit-or-scam/",
    text: "Is Instagram Account Suspended Message Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-google-verification-code-message-legit-or-scam/",
    text: "Is Google Verification Code Message Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-telegram-message-from-unknown-user-legit-or-scam/",
    text: "Is Telegram Message From Unknown User Legit or a Scam?"
  }
];

const NEW_MORE_LINKS = [
  {
    href: "/scam-check-now/is-google-account-disabled-email-legit-or-scam/",
    text: "Is Google Account Disabled Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/google-account-suspension-email-scam/",
    text: "Is Google Account Suspension Email a Scam?"
  },
  {
    href: "/scam-check-now/is-instagram-security-alert-email-legit-or-scam/",
    text: "Is Instagram Security Alert Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-facebook-security-alert-email-legit-or-scam/",
    text: "Is Facebook Security Alert Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-apple-account-verification-email-legit-or-scam/",
    text: "Is Apple Account Verification Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-security-alert-message-real-or-fake/",
    text: "Is PayPal Security Alert Message Real or Fake?"
  }
];

const NEW_FAQ_JSONLD = `{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"Is a Telegram suspicious activity message always a scam?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"No. Security alerts can sometimes be real, but scammers frequently copy Telegram-style warnings to steal login codes or take over accounts. The safest approach is to verify any alert directly inside the official Telegram app, not through the link in the message."
      }
    },
    {
      "@type":"Question",
      "name":"How can I tell if a Telegram suspicious activity message is fake?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Common warning signs include urgent pressure, suspicious links, requests for login codes, fake support language, and messages warning that your account will be locked unless you act immediately. A real security issue should still be verifiable outside the message itself."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I clicked a Telegram suspicious activity message?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"If you clicked the link or entered any details, treat it as urgent. Secure your Telegram account, review active sessions, and change any connected credentials if needed. Use only the official Telegram app or official sources you opened yourself."
      }
    }
  ]
}`;

const NEW_VISIBLE_FAQ = `
    <div class="link-section" id="visibleFaqWrap">
      <h3>Telegram Suspicious Activity Message FAQ</h3>
      <div class="content-body">
        <p><strong>Is a Telegram suspicious activity message always a scam?</strong><br>No. Security alerts can sometimes be real, but scammers frequently copy Telegram-style warnings to steal login codes or take over accounts. The safest approach is to verify any alert directly inside the official Telegram app, not through the link in the message.</p>
        <p><strong>How can I tell if a Telegram suspicious activity message is fake?</strong><br>Common warning signs include urgent pressure, suspicious links, requests for login codes, fake support language, and messages warning that your account will be locked unless you act immediately. A real security issue should still be verifiable outside the message itself.</p>
        <p><strong>What should I do if I clicked a Telegram suspicious activity message?</strong><br>If you clicked the link or entered any details, treat it as urgent. Secure your Telegram account, review active sessions, and change any connected credentials if needed. Use only the official Telegram app or official sources you opened yourself.</p>
      </div>
    </div>
`;

const NEW_HUB_LINK = `
    <div class="inline-info-card" id="hubLinkWrap">
      <a href="/scam-check-now/telegram-scams/">Telegram Scam Hub</a>
    </div>
`;

// -----------------------------
// HELPERS
// -----------------------------
function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function ensureBackupDir() {
  if (!fs.existsSync(BACKUP_DIR)) {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
  }
}

function createBackup(originalContent) {
  ensureBackupDir();

  const safeName = TARGET_PAGE.replace(/\//g, "__");
  const backupPath = path.join(
    BACKUP_DIR,
    `${safeName}__${timestamp()}`
  );

  if (!DRY_RUN) {
    fs.writeFileSync(backupPath, originalContent, "utf8");
  }

  console.log("Backup created:", backupPath);
}

function escapeHtmlAttr(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function escapeJsonString(str) {
  return JSON.stringify(String(str)).slice(1, -1);
}

function replaceWithCheck(html, regex, replacement, label) {
  const updated = html.replace(regex, replacement);

  if (updated === html) {
    console.warn(`No change for ${label}`);
    return html;
  }

  console.log(`Updated ${label}`);
  return updated;
}

function replaceTitle(html) {
  if (!NEW_TITLE) return html;

  return replaceWithCheck(
    html,
    /<title\b[^>]*>[\s\S]*?<\/title>/i,
    `<title>${NEW_TITLE}</title>`,
    "title"
  );
}

function replaceMetaDescription(html) {
  if (!NEW_META) return html;

  return replaceWithCheck(
    html,
    /<meta\s+name=["']description["']\s+content=["'][^"]*["']\s*\/?>/i,
    `<meta name="description" content="${escapeHtmlAttr(NEW_META)}">`,
    "meta description"
  );
}

function replaceOgTitle(html) {
  if (!NEW_TITLE) return html;

  return replaceWithCheck(
    html,
    /<meta\s+property=["']og:title["']\s+content=["'][^"]*["']\s*\/?>/i,
    `<meta property="og:title" content="${escapeHtmlAttr(NEW_TITLE)}">`,
    "og:title"
  );
}

function replaceOgDescription(html) {
  if (!NEW_META) return html;

  return replaceWithCheck(
    html,
    /<meta\s+property=["']og:description["']\s+content=["'][^"]*["']\s*\/?>/i,
    `<meta property="og:description" content="${escapeHtmlAttr(NEW_META)}">`,
    "og:description"
  );
}

function replaceTwitterTitle(html) {
  if (!NEW_TITLE) return html;

  return replaceWithCheck(
    html,
    /<meta\s+name=["']twitter:title["']\s+content=["'][^"]*["']\s*\/?>/i,
    `<meta name="twitter:title" content="${escapeHtmlAttr(NEW_TITLE)}">`,
    "twitter:title"
  );
}

function replaceTwitterDescription(html) {
  if (!NEW_META) return html;

  return replaceWithCheck(
    html,
    /<meta\s+name=["']twitter:description["']\s+content=["'][^"]*["']\s*\/?>/i,
    `<meta name="twitter:description" content="${escapeHtmlAttr(NEW_META)}">`,
    "twitter:description"
  );
}

function replaceRawKeyword(html) {
  if (!NEW_RAW_KEYWORD) return html;

  return replaceWithCheck(
    html,
    /const\s+RAW_KEYWORD\s*=\s*"[^"]*";/i,
    `const RAW_KEYWORD = "${escapeHtmlAttr(NEW_RAW_KEYWORD)}";`,
    "RAW_KEYWORD"
  );
}

function replaceWebPageJsonLd(html) {
  if (!NEW_TITLE && !NEW_META) return html;

  const updated = html.replace(
    /<script type="application\/ld\+json">[\s\S]*?"@type":"WebPage"[\s\S]*?<\/script>/i,
    (block) => {
      let next = block;

      if (NEW_TITLE) {
        next = next.replace(
          /"name":"([^"\\\\]|\\\\.)*"/i,
          `"name":"${escapeJsonString(NEW_TITLE)}"`
        );
      }

      if (NEW_META) {
        next = next.replace(
          /"description":"([^"\\\\]|\\\\.)*"/i,
          `"description":"${escapeJsonString(NEW_META)}"`
        );
      }

      return next;
    }
  );

  if (updated === html) {
    console.warn("No change for WebPage JSON-LD");
    return html;
  }

  console.log("Updated WebPage JSON-LD");
  return updated;
}

function upsertFaqJsonLd(html) {
  if (!NEW_FAQ_JSONLD) return html;

  const faqScript = `<script type="application/ld+json">\n${NEW_FAQ_JSONLD}\n</script>`;

  if (/"@type":"FAQPage"/i.test(html) || /"@type"\s*:\s*"FAQPage"/i.test(html)) {
    const updated = html.replace(
      /<script type="application\/ld\+json">[\s\S]*?"@type"\s*:\s*"FAQPage"[\s\S]*?<\/script>|<script type="application\/ld\+json">[\s\S]*?"@type":"FAQPage"[\s\S]*?<\/script>/i,
      faqScript
    );

    if (updated === html) {
      console.warn("No change for FAQ JSON-LD");
      return html;
    }

    console.log("Updated FAQ JSON-LD");
    return updated;
  }

  const inserted = html.replace(/<\/head>/i, `${faqScript}\n</head>`);

  if (inserted === html) {
    console.warn("No change for FAQ JSON-LD");
    return html;
  }

  console.log("Inserted FAQ JSON-LD");
  return inserted;
}

function replaceFreshnessBlock(html) {
  if (!NEW_TOP_BLOCK) return html;

  if (html.includes('id="freshnessBlock"')) {
    const updatedExisting = html.replace(
      /<div class="page-shell-top-block" id="freshnessBlock"[\s\S]*?<\/div>\s*<\/div>\s*(?=<div class="container">|<div class="page-shell-top-block" id="instantVerdictCardWrap")/i,
      `${NEW_TOP_BLOCK}\n`
    );

    if (updatedExisting !== html) {
      console.log("Updated freshness block");
      return updatedExisting;
    }
  }

  const updated = html.replace(
    /(<\/div>\s*)(<div class="container">)/i,
    `$1\n${NEW_TOP_BLOCK}\n$2`
  );

  if (updated === html) {
    const fallback = html.replace(
      /<div class="container">/i,
      `${NEW_TOP_BLOCK}\n<div class="container">`
    );

    if (fallback === html) {
      console.warn("No change for freshness block");
      return html;
    }

    console.log("Inserted freshness block (fallback)");
    return fallback;
  }

  console.log("Inserted freshness block");
  return updated;
}

function insertInstantVerdictCard(html) {
  const startMarker = '<div class="page-shell-top-block" id="instantVerdictCardWrap"';

  if (html.includes(startMarker)) {
    const freshnessIndex = html.indexOf('<div class="page-shell-top-block" id="freshnessBlock"');
    const startIndex = html.indexOf(startMarker);

    if (startIndex !== -1 && freshnessIndex !== -1 && freshnessIndex > startIndex) {
      console.log("Replaced existing instant verdict card");
      return (
        html.slice(0, startIndex) +
        NEW_INSTANT_VERDICT_CARD +
        "\n" +
        html.slice(freshnessIndex)
      );
    }

    const updatedExisting = html.replace(
      /<div class="page-shell-top-block" id="instantVerdictCardWrap"[\s\S]*?<\/div>\s*<\/div>/i,
      NEW_INSTANT_VERDICT_CARD.trim()
    );

    if (updatedExisting !== html) {
      console.log("Updated instant verdict card");
      return updatedExisting;
    }
  }

  let updated = html.replace(
    /(<div class="page-shell-top-block" id="freshnessBlock")/i,
    `${NEW_INSTANT_VERDICT_CARD}\n$1`
  );

  if (updated !== html) {
    console.log("Inserted instant verdict card (before freshness)");
    return updated;
  }

  updated = html.replace(
    /(<div class="container">)/i,
    `$1\n${NEW_INSTANT_VERDICT_CARD}\n`
  );

  if (updated !== html) {
    console.log("Inserted instant verdict card (container fallback)");
    return updated;
  }

  console.warn("No change for instant verdict card");
  return html;
}

function replacePreviewSignals(html) {
  const replacement = `function applyPreviewCard() {
  const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
  const cleanTitle = displayCleanKeyword(keywordRaw) || "Suspicious Message";
  const lower = keywordRaw.toLowerCase();

  const previewDomain = document.getElementById("previewDomain");
  const previewSub = document.getElementById("previewSub");
  const previewBadge = document.getElementById("previewBadge");
  const previewScore = document.getElementById("previewScore");
  const previewScoreFill = document.getElementById("previewScoreFill");
  const previewSignals = document.getElementById("previewSignals");

  if (!previewDomain || !previewSub || !previewBadge || !previewScore || !previewScoreFill || !previewSignals) {
    return;
  }

  let riskLabel = "Example Risk Pattern";
  let trustScore = "Risk Example";
  let fillWidth = "18%";
  let sub = "Common signals found in similar scams";
  let signals = [
    "Suspicious domain mismatch",
    "Urgent language detected",
    "Payment request via gift card"
  ];

  if (containsAny(lower, ["telegram"])) {
    riskLabel = "Example Risk Pattern";
    trustScore = "Account Risk Example";
    fillWidth = "22%";
    sub = "Common signals found in similar Telegram account alert scams";
    signals = [
      "Fake login or verification link",
      "Pressure to act before account suspension",
      "Requests for phone number or login code"
    ];
  } else if (containsAny(lower, ["job", "recruiter", "interview", "hiring", "onboarding"])) {
    signals = [
      "Pressure to move quickly",
      "Requests for personal details or fees",
      "Offer appears unusually fast or high-paying"
    ];
  } else if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft"])) {
    signals = [
      "Urgent transfer or wallet request",
      "High-return or recovery promise",
      "Support or investment impersonation risk"
    ];
  } else if (containsAny(lower, ["delivery", "usps", "ups", "fedex", "package", "shipment", "parcel"])) {
    signals = [
      "Tracking or delivery pressure",
      "Link may lead to a fake page",
      "Small payment or verification request"
    ];
  } else if (containsAny(lower, ["bank", "paypal", "venmo", "zelle", "cash app", "amazon", "refund", "payment"])) {
    signals = [
      "Account or payment urgency",
      "Possible fake login or verification page",
      "Requests for money or sensitive details"
    ];
  } else if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    riskLabel = "Scam Risk Check";
    trustScore = "Pattern Review";
    fillWidth = "34%";
    signals = [
      "Review sender, links, and urgency",
      "Verify outside the original message",
      "Do not send money or codes until confirmed"
    ];
  }

  previewBadge.textContent = \`🔴 \${riskLabel}\`;
  previewScore.textContent = trustScore;
  previewScoreFill.style.width = fillWidth;
  previewDomain.textContent = cleanTitle;
  previewSub.textContent = sub;
  previewSignals.innerHTML = signals.map(signal =>
    \`<div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>\${escapeHtml(signal)}</span></div>\`
  ).join("");
}`;

  const updated = html.replace(
    /function applyPreviewCard\(\) \{[\s\S]*?\n\}/,
    replacement
  );

  if (updated === html) {
    console.warn("No change for preview signals");
    return html;
  }

  console.log("Updated preview signals");
  return updated;
}

function replaceTelegramSeoCardTitles(html) {
  const updated = html.replace(
    /return \[\s*\["📱",\s*"What this Telegram alert often looks like"\],\s*\["⏱️",\s*"Where the pressure starts"\],\s*\["🔁",\s*"How the account warning changes across versions"\],\s*\["💥",\s*"What happens after the click or code share"\],\s*\["•",\s*"What to do next"\],\s*\["•",\s*"Key safety rule"\]\s*\];/i,
    `return [
      ["📱", "What this Telegram alert often looks like"],
      ["⏱️", "Where the pressure starts"],
      ["🔐", "What scammers usually want"],
      ["🧭", "How to verify it safely"],
      ["✅", "What to do next"],
      ["⚠️", "Key safety rule"]
    ];`
  );

  if (updated === html) {
    console.warn("No change for telegram seo card titles");
    return html;
  }

  console.log("Updated telegram seo card titles");
  return updated;
}

function replaceSeoContent(html) {
  if (!NEW_SEO_CONTENT) return html;

  const updated = html.replace(
    /<div id="seoContent" class="content-body">[\s\S]*?<\/div>\s*\n\s*<div class="story-card" id="realExamplesCard">/i,
    `<div id="seoContent" class="content-body">${NEW_SEO_CONTENT}</div>

    <div class="story-card" id="realExamplesCard">`
  );

  if (updated === html) {
    console.warn("No change for seo content");
    return html;
  }

  console.log("Updated seo content");
  return updated;
}

function upsertExampleCard(html) {
  if (!NEW_EXAMPLE_CARD) return html;

  if (html.includes('id="realExamplesCard"')) {
    const updatedExisting = html.replace(
      /<div class="story-card" id="realExamplesCard">[\s\S]*?<\/div>\s*(?=<div class="link-section")/i,
      `${NEW_EXAMPLE_CARD}\n\n    `
    );

    if (updatedExisting === html) {
      console.warn("No change for example card");
      return html;
    }

    console.log("Updated example card");
    return updatedExisting;
  }

  const inserted = html.replace(
    /(\s*<div class="link-section">)/i,
    `\n${NEW_EXAMPLE_CARD}\n$1`
  );

  if (inserted === html) {
    console.warn("No change for example card");
    return html;
  }

  console.log("Inserted example card");
  return inserted;
}

function replaceRelatedLinks(html) {
  if (!NEW_RELATED_LINKS) return html;

  const listHTML = NEW_RELATED_LINKS
    .map((l) => `<li><a href="${l.href}">${l.text}</a></li>`)
    .join("\n");

  return replaceWithCheck(
    html,
    /<ul id="relatedLinks"[^>]*>[\s\S]*?<\/ul>/i,
    `<ul id="relatedLinks" class="related-links">\n${listHTML}\n</ul>`,
    "related links"
  );
}

function replaceMoreLinks(html) {
  if (!NEW_MORE_LINKS) return html;

  const listHTML = NEW_MORE_LINKS
    .map((l) => `<li><a href="${l.href}">${l.text}</a></li>`)
    .join("\n");

  return replaceWithCheck(
    html,
    /<ul id="moreLinks"[^>]*>[\s\S]*?<\/ul>/i,
    `<ul id="moreLinks" class="related-links">\n${listHTML}\n</ul>`,
    "more links"
  );
}

function replaceHubLink(html) {
  if (!NEW_HUB_LINK) return html;

  return replaceWithCheck(
    html,
    /<div class="inline-info-card" id="hubLinkWrap">[\s\S]*?<\/div>/i,
    NEW_HUB_LINK.trim(),
    "hub link"
  );
}

function upsertVisibleFaq(html) {
  if (!NEW_VISIBLE_FAQ) return html;

  if (html.includes('id="visibleFaqWrap"')) {
    const updatedExisting = html.replace(
      /<div class="link-section" id="visibleFaqWrap">[\s\S]*?<\/div>\s*(?=<div class="content-close">|<div class="link-section">)/i,
      NEW_VISIBLE_FAQ
    );

    if (updatedExisting === html) {
      console.warn("No change for visible FAQ");
      return html;
    }

    console.log("Updated visible FAQ");
    return updatedExisting;
  }

  const insertedBeforeClose = html.replace(
    /(\s*<div class="content-close">)/i,
    `\n${NEW_VISIBLE_FAQ}\n$1`
  );

  if (insertedBeforeClose === html) {
    console.warn("No change for visible FAQ");
    return html;
  }

  console.log("Inserted visible FAQ before closing section");
  return insertedBeforeClose;
}

function replaceEmailPlaceholder(html) {
  return replaceWithCheck(
    html,
    /<input id="email" placeholder="[^"]*">/i,
    `<input id="email" placeholder="Enter your subscription email">`,
    "email placeholder"
  );
}

function expandSeoCardLimit(html) {
  return replaceWithCheck(
    html,
    /\.slice\(0,\s*4\)/,
    `.slice(0, 6)`,
    "seo card limit"
  );
}

// -----------------------------
// MAIN
// -----------------------------
const original = fs.readFileSync(TARGET_PAGE, "utf8");

createBackup(original);

let updated = original;

updated = replaceTitle(updated);
updated = replaceMetaDescription(updated);
updated = replaceOgTitle(updated);
updated = replaceOgDescription(updated);
updated = replaceTwitterTitle(updated);
updated = replaceTwitterDescription(updated);
updated = replaceRawKeyword(updated);
updated = replaceWebPageJsonLd(updated);
updated = upsertFaqJsonLd(updated);
updated = replaceFreshnessBlock(updated);
updated = insertInstantVerdictCard(updated);
updated = replacePreviewSignals(updated);
updated = replaceTelegramSeoCardTitles(updated);
updated = replaceSeoContent(updated);
updated = upsertExampleCard(updated);
updated = replaceRelatedLinks(updated);
updated = replaceMoreLinks(updated);
updated = replaceHubLink(updated);
updated = upsertVisibleFaq(updated);
updated = replaceEmailPlaceholder(updated);
updated = expandSeoCardLimit(updated);

if (updated === original) {
  console.log("No changes made.");
  process.exit(0);
}

if (DRY_RUN) {
  console.log("DRY RUN - no file written");
  process.exit(0);
}

fs.writeFileSync(TARGET_PAGE, updated, "utf8");
console.log("Updated page:", TARGET_PAGE);