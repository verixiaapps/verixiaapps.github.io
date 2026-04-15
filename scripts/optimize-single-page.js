const fs = require("fs");
const path = require("path");

// ✅ EXACT PAGE TARGETED
const TARGET_PAGE = "scam-check-now/is-td-bank-fraud-alert-email-legit-or-scam/index.html";
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
  "TD Bank Fraud Alert Email Scam? How to Tell if It Is Real or Fake";

const NEW_META =
  "Got a TD Bank fraud alert email? Learn the warning signs, fake login tricks, and what to do before you click a link, enter your password, or reply.";

const NEW_RAW_KEYWORD = "TD Bank fraud alert email";

const NEW_TOP_BLOCK = `
  <div class="page-shell-top-block" id="freshnessBlock" style="max-width:940px;margin:18px auto 20px;padding:0 14px;">
    <div class="inline-info-card" style="margin-top:0;">
      <div style="font-size:13px;font-weight:900;color:#9cecff;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">
        Updated April 2026
      </div>
      <div style="font-size:15px;font-weight:800;line-height:1.6;color:#e6f0ff;">
        Users are still receiving TD Bank fraud alert emails claiming:
      </div>
      <ul style="margin:10px 0 0 18px;color:#d7e4f8;font-weight:800;line-height:1.6;">
        <li>“Suspicious activity detected”</li>
        <li>“Verify your account immediately”</li>
        <li>“Unusual login attempt”</li>
      </ul>
      <div style="margin-top:10px;font-size:14px;font-weight:800;color:#d7e4f8;line-height:1.6;">
        These messages often link to fake TD Bank login pages or fake support numbers designed to steal your login details or verification codes.
      </div>
    </div>
  </div>
`;

const NEW_EXAMPLE_CARD = `
    <div class="story-card" id="realExamplesCard">
      <div class="story-card-title">
        <span class="story-card-title-icon">📩</span>
        <span>Real TD Bank Fraud Email Examples</span>
      </div>
      <p>Reports show people receiving emails with subject lines like “TD Bank: Suspicious activity detected,” “Action required: verify your account,” or “Unusual login attempt.” These messages often reference a large transaction, a locked account, or a security issue that needs immediate attention.</p>
      <p style="margin-top:14px;">Most versions include buttons such as “Secure Account,” “Verify Identity,” or “Review Activity.” These links can lead to fake TD Bank login pages designed to capture usernames, passwords, and one-time verification codes.</p>
      <p style="margin-top:14px;">Some variations also include a phone number labeled as a fraud department or security team. Calling it can connect you to scammers who ask for login details, verification codes, or card information under pressure.</p>
      <div style="margin-top:14px;font-size:14px;font-weight:800;color:#d7e4f8;line-height:1.6;">If the message only feels real when you follow the link or call the number inside it, that is a strong warning sign. A legitimate alert should still be verifiable directly through the official TD Bank app or website.</div>
    </div>
`;

const NEW_RELATED_LINKS = [
  {
    href: "/scam-check-now/is-td-bank-account-access-alert-email-legit-or-scam/",
    text: "Is TD Bank Account Access Alert Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-banking-alert-email-legit-or-scam/",
    text: "Is TD Bank Banking Alert Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-sign-in-alert-email-legit-or-scam/",
    text: "Is TD Bank Sign In Alert Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-unusual-login-email-legit-or-scam/",
    text: "Is TD Bank Unusual Login Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-fraud-department-email-legit-or-scam/",
    text: "Is TD Bank Fraud Department Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-secure-message-email-legit-or-scam/",
    text: "Is TD Bank Secure Message Email Legit or a Scam?"
  }
];

const NEW_MORE_LINKS = [
  {
    href: "/scam-check-now/is-td-bank-fraud-investigation-email-legit-or-scam/",
    text: "Is TD Bank Fraud Investigation Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-account-verification-email-legit-or-scam/",
    text: "Is TD Bank Account Verification Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-account-review-email-legit-or-scam/",
    text: "Is TD Bank Account Review Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-payment-verification-email-legit-or-scam/",
    text: "Is TD Bank Payment Verification Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-suspicious-transfer-email-legit-or-scam/",
    text: "Is TD Bank Suspicious Transfer Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-td-bank-card-security-alert-text-legit-or-scam/",
    text: "Is TD Bank Card Security Alert Text Legit or a Scam?"
  }
];

const NEW_FAQ_JSONLD = `{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"Is a TD Bank fraud alert email always a scam?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"No. Banks can send real fraud alerts, but scammers also copy the same type of warning. The safest approach is to verify the alert independently in the official TD Bank app or by using official contact details, not the link or number inside the email."
      }
    },
    {
      "@type":"Question",
      "name":"How can I tell if a TD Bank fraud alert email is fake?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Common warning signs include urgent pressure, suspicious links, fake support phone numbers, requests for login details or verification codes, and messages that only make sense if you trust the email itself. A real alert should still be verifiable outside the message."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I clicked a TD Bank fraud alert email?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"If you clicked the link or entered information, change your password immediately, review account activity, and contact TD Bank through an official channel you found independently. If you shared sensitive details or codes, treat it as urgent and secure the account right away."
      }
    }
  ]
}`;

const NEW_VISIBLE_FAQ = `
    <div class="link-section" id="visibleFaqWrap">
      <h3>TD Bank Fraud Alert Email FAQ</h3>
      <div class="content-body">
        <p><strong>Is a TD Bank fraud alert email always a scam?</strong><br>No. Banks can send real fraud alerts, but scammers also copy the same type of warning. The safest approach is to verify the alert independently in the official TD Bank app or by using official contact details, not the link or number inside the email.</p>
        <p><strong>How can I tell if a TD Bank fraud alert email is fake?</strong><br>Common warning signs include urgent pressure, suspicious links, fake support phone numbers, requests for login details or verification codes, and messages that only make sense if you trust the email itself. A real alert should still be verifiable outside the message.</p>
        <p><strong>What should I do if I clicked a TD Bank fraud alert email?</strong><br>If you clicked the link or entered information, change your password immediately, review account activity, and contact TD Bank through an official channel you found independently. If you shared sensitive details or codes, treat it as urgent and secure the account right away.</p>
      </div>
    </div>
`;

const NEW_HUB_LINK = `
    <div class="inline-info-card" id="hubLinkWrap">
      <a href="/scam-check-now/bank-scams/">Bank Scam Hub</a>
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
    `${safeName}__${timestamp()}.html`
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
          /"name":"([^"\\]|\\.)*"/i,
          `"name":"${escapeJsonString(NEW_TITLE)}"`
        );
      }

      if (NEW_META) {
        next = next.replace(
          /"description":"([^"\\]|\\.)*"/i,
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

function replaceBankSeoCardTitles(html) {
  const updated = html.replace(
    /if\s*\(containsAny\(lower,\s*\["bank",\s*"paypal",\s*"venmo",\s*"zelle",\s*"cash app",\s*"amazon",\s*"refund",\s*"payment"\]\)\)\s*\{\s*return\s*\[\s*\["💳",\s*"What this account or payment setup often looks like"\],\s*\["⏱️",\s*"Where the panic starts doing the work"\],\s*\["🔁",\s*"How the account warning changes across versions"\],\s*\["💥",\s*"What happens after a login, code, or payment mistake"\]\s*\];\s*\}/i,
    `if (containsAny(lower, ["bank", "paypal", "venmo", "zelle", "cash app", "amazon", "refund", "payment"])) {
    return [
      ["💳", "What this account or payment setup often looks like"],
      ["⏱️", "Where the panic starts doing the work"],
      ["🔁", "How the account warning changes across versions"],
      ["💥", "What happens after a login, code, or payment mistake"],
      ["•", "What to do next"],
      ["•", "Key safety rule"]
    ];
  }`
  );

  if (updated === html) {
    console.warn("No change for bank seo card titles");
    return html;
  }

  console.log("Updated bank seo card titles");
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
updated = replaceBankSeoCardTitles(updated);
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