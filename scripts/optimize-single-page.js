const fs = require("fs");
const path = require("path");

// ✅ EXACT PAGE TARGETED
const TARGET_PAGE = "scam-check-now/is-fedex-customs-charge-email-legit-or-scam/index.html";
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
  "FedEx Customs Charge Email: Scam or Legit? Warning Signs & What To Do";

const NEW_META =
  "Got a FedEx customs charge email asking for payment? Learn the biggest warning signs, fake delivery fee tricks, and what to do before you click, enter payment details, or verify shipment information.";

const NEW_RAW_KEYWORD = "FedEx customs charge email";

const NEW_INSTANT_VERDICT_CARD = `
  <div class="page-shell-top-block" id="instantVerdictCardWrap" style="max-width:940px;margin:-6px auto 12px;padding:0 14px;">
    <div class="story-card lead" id="instantVerdictCard" style="margin:0;padding:20px 16px;text-align:center;">

      <div style="margin-bottom:10px;">
        <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0%25' stop-color='%23ffb36b'/><stop offset='100%25' stop-color='%23d97706'/></linearGradient></defs><circle cx='32' cy='32' r='30' fill='url(%23g)'/><path d='M32 14 L50 46 H14 Z' fill='white' opacity='0.96'/><rect x='29' y='24' width='6' height='12' rx='3' fill='%23d97706'/><circle cx='32' cy='41' r='3' fill='%23d97706'/></svg>" alt="Warning" style="width:56px;height:56px;">
      </div>

      <div style="font-size:18px;font-weight:900;color:#ffd39a;margin-bottom:6px;">
        Risk Level: Medium to High
      </div>

      <div style="font-size:15px;font-weight:800;color:#e6f0ff;margin-bottom:4px;">
        Likely fake delivery fee or customs payment request
      </div>

      <div style="font-size:15px;font-weight:900;color:#ffffff;">
        Do not click the payment link inside the message. Check the shipment only through the official FedEx site or app you open yourself.
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
        People are still receiving FedEx customs charge emails claiming:
      </div>
      <ul style="margin:10px 0 0 18px;color:#d7e4f8;font-weight:800;line-height:1.6;">
        <li>“Your package is being held at customs”</li>
        <li>“Pay a small fee to release delivery”</li>
        <li>“Complete payment now to avoid return or delay”</li>
      </ul>
      <div style="margin-top:10px;font-size:14px;font-weight:800;color:#d7e4f8;line-height:1.6;">
        These messages often lead to fake FedEx payment or tracking pages designed to steal card details, personal information, or account access.
      </div>
    </div>
  </div>
`;

const NEW_SEO_CONTENT = `
<div class="story-stack">
  <article class="story-card lead">
    <div class="story-card-title">
      <span class="story-card-title-icon">📦</span>
      <span>What this FedEx customs charge email often looks like</span>
    </div>
    <p>A FedEx customs charge email usually claims your package is delayed, held at customs, or waiting for a small payment before delivery can continue. The message is built to feel routine so you act fast before stopping to verify whether the shipment problem is real.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">⏱️</span>
      <span>Where the pressure starts</span>
    </div>
    <p>Most versions push urgency right away. They may warn that your shipment will be returned, cancelled, or delayed unless you pay immediately. That pressure is the point. Scammers want a fast click before you notice the sender, domain, or payment page does not fully add up.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">💳</span>
      <span>What scammers usually want</span>
    </div>
    <p>The goal is often payment information, personal details, or both. Fake FedEx customs pages may ask for a small release fee, billing details, address confirmation, or other information that can later be used for larger charges or fraud.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">🧭</span>
      <span>How to verify it safely</span>
    </div>
    <p>The safest check is simple: do not use the link inside the email. Open FedEx yourself, check the tracking number through the official site or app, and only trust delivery or customs information you verify independently.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">✅</span>
      <span>What to do next</span>
    </div>
    <p>If you have not clicked, stop there and verify the shipment through official channels before doing anything else. If you already clicked or entered payment details, treat it as urgent, monitor your card activity, and secure any information you shared.</p>
  </article>

  <article class="story-card">
    <div class="story-card-title">
      <span class="story-card-title-icon">⚠️</span>
      <span>Key safety rule</span>
    </div>
    <p>If the customs problem only feels real when you use the link inside the email, that is a strong warning sign. A real delivery issue should still be verifiable without relying on the message itself.</p>
  </article>
</div>
`;

const NEW_EXAMPLE_CARD = `
    <div class="story-card" id="realExamplesCard">
      <div class="story-card-title">
        <span class="story-card-title-icon">📩</span>
        <span>Common FedEx Customs Charge Email Examples</span>
      </div>
      <p>Reports show people receiving FedEx-style emails saying a package is on hold, a customs fee is due, or a small payment is needed before delivery can continue. These messages usually make the request sound routine and low-risk.</p>
      <p style="margin-top:14px;">Most versions include a payment button, tracking link, or fake support prompt telling you to release the shipment, confirm delivery details, or pay a customs charge immediately. These pages are often built to collect card details, personal information, or both.</p>
      <p style="margin-top:14px;">Some versions also create urgency by warning that the package will be returned, cancelled, or delayed within hours if you do not pay right away. Small fees are often used because they feel believable and easy to approve without much thought.</p>
      <div style="margin-top:14px;font-size:14px;font-weight:800;color:#d7e4f8;line-height:1.6;">If the delivery problem only feels legitimate when you use the payment link inside the email, that is a strong warning sign. A real shipment issue should still be verifiable directly through official FedEx tracking.</div>
    </div>
`;

const NEW_RELATED_LINKS = [
  {
    href: "/scam-check-now/is-ups-delivery-text-legit-or-scam/",
    text: "Is UPS Delivery Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-fedex-delivery-legit-or-scam/",
    text: "Is FedEx Delivery Message Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-tracking-text-legit-or-scam/",
    text: "Is USPS Tracking Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/package-delivery-scams/",
    text: "Package Delivery Scam Hub"
  },
  {
    href: "/scam-check-now/is-amazon-delivery-problem-email-legit-or-scam/",
    text: "Is Amazon Delivery Problem Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-missed-delivery-text-legit-or-scam/",
    text: "Is Missed Delivery Text Legit or a Scam?"
  }
];

const NEW_MORE_LINKS = [
  {
    href: "/scam-check-now/is-bank-account-closure-email-legit-or-scam/",
    text: "Is Bank Account Closure Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-security-alert-message-real-or-fake/",
    text: "Is PayPal Security Alert Message Real or Fake?"
  },
  {
    href: "/scam-check-now/is-amazon-refund-email-legit-or-scam/",
    text: "Is Amazon Refund Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-google-account-disabled-email-legit-or-scam/",
    text: "Is Google Account Disabled Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-background-check-email-asking-for-payment-legit-or-scam/",
    text: "Is Background Check Email Asking For Payment Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-apple-wallet-billing-email-legit-or-scam/",
    text: "Is Apple Wallet Billing Email Legit or a Scam?"
  }
];

const NEW_FAQ_JSONLD = `{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"Is a FedEx customs charge email always a scam?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"No. Customs or delivery fees can sometimes be real, but scammers frequently copy FedEx-style payment requests to steal card details or personal information. The safest approach is to verify any shipment issue directly through the official FedEx site or app, not through the link in the email."
      }
    },
    {
      "@type":"Question",
      "name":"How can I tell if a FedEx customs charge email is fake?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Common warning signs include urgent payment pressure, suspicious links, requests for card details, vague shipment information, and messages warning that the package will be returned unless you act immediately. A real delivery issue should still be verifiable outside the message itself."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I clicked a FedEx customs charge email?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"If you clicked the link or entered any details, treat it as urgent. Monitor your payment accounts, secure any information you shared, and verify the shipment only through the official FedEx site or app you opened yourself."
      }
    }
  ]
}`;

const NEW_VISIBLE_FAQ = `
    <div class="link-section" id="visibleFaqWrap">
      <h3>FedEx Customs Charge Email FAQ</h3>
      <div class="content-body">
        <p><strong>Is a FedEx customs charge email always a scam?</strong><br>No. Customs or delivery fees can sometimes be real, but scammers frequently copy FedEx-style payment requests to steal card details or personal information. The safest approach is to verify any shipment issue directly through the official FedEx site or app, not through the link in the email.</p>
        <p><strong>How can I tell if a FedEx customs charge email is fake?</strong><br>Common warning signs include urgent payment pressure, suspicious links, requests for card details, vague shipment information, and messages warning that the package will be returned unless you act immediately. A real delivery issue should still be verifiable outside the message itself.</p>
        <p><strong>What should I do if I clicked a FedEx customs charge email?</strong><br>If you clicked the link or entered any details, treat it as urgent. Monitor your payment accounts, secure any information you shared, and verify the shipment only through the official FedEx site or app you opened yourself.</p>
      </div>
    </div>
`;

const NEW_HUB_LINK = `
    <div class="inline-info-card" id="hubLinkWrap">
      <a href="/scam-check-now/package-delivery-scams/">Package Delivery Scam Hub</a>
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

  if (containsAny(lower, ["fedex", "delivery", "package", "shipment", "parcel", "customs"])) {
    riskLabel = "Example Risk Pattern";
    trustScore = "Delivery Risk Example";
    fillWidth = "24%";
    sub = "Common signals found in similar customs fee and delivery payment scams";
    signals = [
      "Urgent delivery or customs payment request",
      "Link may lead to a fake tracking or payment page",
      "Requests for card details or shipment verification"
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

function replaceFedexSeoCardTitles(html) {
  const updated = html.replace(
    /return \[\s*\["📦",\s*"What this delivery setup often looks like"\],\s*\["⏱️",\s*"Where the message pushes quick action"\],\s*\["🔁",\s*"How the carrier story changes across versions"\],\s*\["💥",\s*"What happens after the click or payment"\]\s*\];/i,
    `return [
      ["📦", "What this FedEx customs charge email often looks like"],
      ["⏱️", "Where the pressure starts"],
      ["💳", "What scammers usually want"],
      ["🧭", "How to verify it safely"],
      ["✅", "What to do next"],
      ["⚠️", "Key safety rule"]
    ];`
  );

  if (updated === html) {
    console.warn("No change for fedex seo card titles");
    return html;
  }

  console.log("Updated fedex seo card titles");
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
updated = replaceFedexSeoCardTitles(updated);
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