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

const NEW_SEO_CONTENT = `
<div id="seoContent" class="content-body"><div class="content-block" data-context="bank-security" data-mode="comparison">
<p>A TD Bank fraud alert email can look convincing because scammers copy the same words people expect to see in a real bank warning. The message usually says there was suspicious activity, an unusual login, a blocked transfer, or a security hold that needs immediate attention. The risk is that the email tries to pull you into a fake login page or push you into calling a fake support number before you verify anything through your real account.</p>

<p>The most common scam version creates urgency first. It says your account is at risk, your card was flagged, or your access will be restricted unless you act now. A button like review activity, secure account, or verify identity then sends you to a page designed to look like TD Bank. Once there, the goal is usually to steal your username, password, one time code, card details, or other account information.</p>

<p>A real TD Bank alert should still make sense when you check it independently in the official TD Bank app or by going directly to the official website yourself. A scam version gets weaker the moment you stop relying on the email. That is one of the clearest differences. If the warning only works when you trust the email itself, the situation is not safe enough to treat as real.</p>

<p>Another common pattern is a fake support workflow. Instead of only asking you to log in, the email may tell you to call a number immediately to stop fraud. The person who answers may pretend to be TD Bank and ask for account details, verification codes, card numbers, or approval of a transaction you do not understand. This is designed to create panic and rush you past basic verification.</p>

<p>If you receive a TD Bank fraud alert email, do not click the link inside the message and do not call the number listed in the email. Open the official TD Bank app yourself or type the official site into your browser manually and check for alerts there. If you already clicked or entered information, change your password right away, review recent activity, and contact TD Bank through an official support channel you found independently.</p>

<p>The safest way to think about these emails is simple. A real bank warning can be verified outside the message. A scam depends on getting you to trust the message, the link, or the caller before you slow down. Treat any unexpected TD Bank fraud alert email as suspicious until you confirm it directly through the official app, website, or verified bank contact information.</p>
</div></div>
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

function replaceSeoContent(html) {
  if (!NEW_SEO_CONTENT) return html;

  const updated = html.replace(
    /<div id="seoContent" class="content-body">[\s\S]*?<\/div>\s*(?=<div class="link-section")/i,
    `${NEW_SEO_CONTENT}\n\n    `
  );

  if (updated === html) {
    console.warn("No change for seo content");
    return html;
  }

  console.log("Updated seo content");
  return updated;
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
updated = replaceWebPageJsonLd(updated);
updated = upsertFaqJsonLd(updated);
updated = replaceSeoContent(updated);
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