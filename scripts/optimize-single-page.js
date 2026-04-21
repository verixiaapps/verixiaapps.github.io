const fs = require("fs");
const path = require("path");

// ✅ EXACT PAGE TARGETED
const TARGET_PAGE = "scam-check-now/is-usps-package-delay-email-legit-or-scam/index.html";
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
  'USPS "Package Delay" Email Scam? How to Tell if It Is Real or Fake';

const NEW_META =
  'Got a USPS package delay email? Learn the warning signs, fake tracking link tricks, and what to do before you click, pay a fee, or enter your delivery details.';

const NEW_RAW_KEYWORD = "USPS package delay email";

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
        Likely fake delivery delay alert or phishing email
      </div>

      <div style="font-size:15px;font-weight:900;color:#ffffff;">
        Do not click links or pay any fee inside the message. Verify tracking only through the official USPS website or app.
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
        People are still receiving USPS package delay emails and messages claiming:
      </div>
      <ul style="margin:10px 0 0 18px;color:#d7e4f8;font-weight:800;line-height:1.6;">
        <li>“Your package has been delayed”</li>
        <li>“Action required to avoid return to sender”</li>
        <li>“Confirm address or pay a redelivery fee”</li>
      </ul>
      <div style="margin-top:10px;font-size:14px;font-weight:800;color:#d7e4f8;line-height:1.6;">
        These messages often lead to fake USPS tracking pages or payment screens designed to steal card details, addresses, or personal information.
      </div>
    </div>
  </div>
`;

const NEW_EXAMPLE_CARD = `
    <div class="story-card" id="realExamplesCard">
      <div class="story-card-title">
        <span class="story-card-title-icon">📩</span>
        <span>Common USPS Package Delay Email Examples</span>
      </div>
      <p>Reports show people receiving emails with subject lines like “USPS Package Delay,” “Delivery Delayed – Action Required,” or “Shipment On Hold.” These messages often claim there is a tracking issue, delivery delay, address problem, or missed shipment step that needs urgent action.</p>
      <p style="margin-top:14px;">Most versions include buttons such as “Track Package,” “Confirm Delivery,” or “Resolve Delay.” These links can lead to fake USPS pages designed to capture payment details, home addresses, and other personal information.</p>
      <p style="margin-top:14px;">Some versions also request a small redelivery, customs, or handling fee before the package can continue moving. The amount is usually small enough to feel believable but is only there to collect your card details.</p>
      <div style="margin-top:14px;font-size:14px;font-weight:800;color:#d7e4f8;line-height:1.6;">If the email only feels legitimate when you use the link inside it, that is a strong warning sign. A real delivery delay should still be verifiable directly through the official USPS website or app.</div>
    </div>
`;

const NEW_RELATED_LINKS = [
  {
    href: "/scam-check-now/is-usps-package-held-email-legit-or-scam/",
    text: "Is USPS Package Held Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-address-verification-email-legit-or-scam/",
    text: "Is USPS Address Verification Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-customs-fee-email-legit-or-scam/",
    text: "Is USPS Customs Fee Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-delivery-alert-email-legit-or-scam/",
    text: "Is USPS Delivery Alert Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-delivery-confirmation-email-legit-or-scam/",
    text: "Is USPS Delivery Confirmation Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-delivery-notification-email-legit-or-scam/",
    text: "Is USPS Delivery Notification Email Legit or a Scam?"
  }
];

const NEW_MORE_LINKS = [
  {
    href: "/scam-check-now/is-usps-failed-shipment-email-legit-or-scam/",
    text: "Is USPS Failed Shipment Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-delivery-attempt-notice-legit-or-scam/",
    text: "Is USPS Delivery Attempt Notice Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-delivery-failed-message-legit-or-scam/",
    text: "Is USPS Delivery Failed Message Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-delivery-failed-text-legit-or-scam/",
    text: "Is USPS Delivery Failed Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-usps-missed-delivery-text-legit-or-scam/",
    text: "Is USPS Missed Delivery Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/usps-delivery-text-scam/",
    text: "Is USPS Delivery Text a Scam?"
  }
];

const NEW_FAQ_JSONLD = `{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"Is a USPS package delay email always a scam?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"No. Delivery delays can be real, but scammers frequently copy USPS-style alerts to create urgency and collect payment or personal details. The safest approach is to verify the shipment independently through the official USPS website or app, not through the link inside the message."
      }
    },
    {
      "@type":"Question",
      "name":"How can I tell if a USPS package delay email is fake?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Common warning signs include urgent pressure, requests for a small fee, suspicious links, strange sender domains, and messages asking you to confirm address or payment details. A real delivery issue should still be verifiable outside the email."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I clicked a USPS package delay email?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"If you clicked the link or entered information, treat it as urgent. Review your card activity, secure any affected accounts, and verify your shipment directly through USPS using an official source you opened yourself."
      }
    }
  ]
}`;

const NEW_VISIBLE_FAQ = `
    <div class="link-section" id="visibleFaqWrap">
      <h3>USPS Package Delay Email FAQ</h3>
      <div class="content-body">
        <p><strong>Is a USPS package delay email always a scam?</strong><br>No. Delivery delays can be real, but scammers frequently copy USPS-style alerts to create urgency and collect payment or personal details. The safest approach is to verify the shipment independently through the official USPS website or app, not through the link inside the message.</p>
        <p><strong>How can I tell if a USPS package delay email is fake?</strong><br>Common warning signs include urgent pressure, requests for a small fee, suspicious links, strange sender domains, and messages asking you to confirm address or payment details. A real delivery issue should still be verifiable outside the email.</p>
        <p><strong>What should I do if I clicked a USPS package delay email?</strong><br>If you clicked the link or entered information, treat it as urgent. Review your card activity, secure any affected accounts, and verify your shipment directly through USPS using an official source you opened yourself.</p>
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

function insertTopFreshnessBlock(html) {
  if (!NEW_TOP_BLOCK) return html;

  if (html.includes('id="freshnessBlock"')) {
    console.log("Freshness block already exists");
    return html;
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
      console.warn("No change for top freshness block");
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

function replaceDeliverySeoCardTitles(html) {
  const updated = html.replace(
    /if\s*\(containsAny\(lower,\s*\["delivery",\s*"usps",\s*"ups",\s*"fedex",\s*"package",\s*"shipment",\s*"parcel"\]\)\)\s*\{\s*return\s*\[\s*\["📦",\s*"What this delivery setup often looks like"\],\s*\["⏱️",\s*"Where the message pushes quick action"\],\s*\["🔁",\s*"How the carrier story changes across versions"\],\s*\["💥",\s*"What happens after the click or payment"\]\s*\];\s*\}/i,
    `if (containsAny(lower, ["delivery", "usps", "ups", "fedex", "package", "shipment", "parcel"])) {
    return [
      ["📦", "What this delivery setup often looks like"],
      ["⏱️", "Where the message pushes quick action"],
      ["🔁", "How the carrier story changes across versions"],
      ["💥", "What happens after the click or payment"],
      ["•", "What to do next"],
      ["•", "Key safety rule"]
    ];
  }`
  );

  if (updated === html) {
    console.warn("No change for delivery seo card titles");
    return html;
  }

  console.log("Updated delivery seo card titles");
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
updated = insertTopFreshnessBlock(updated);
updated = insertInstantVerdictCard(updated);
updated = replaceDeliverySeoCardTitles(updated);
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