const fs = require("fs");
const path = require("path");

// ✅ EXACT PAGE TARGETED
const TARGET_PAGE = "scam-check-now/is-venmo-verification-code-text-real-or-fake/index.html";
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
  "Venmo Verification Code Text Scam? How to Tell if It's Real or Fake";

const NEW_META =
  "Got a Venmo verification code text you did not request? Learn the warning signs, account takeover tricks, and what to do before you share a code.";

const NEW_SEO_CONTENT = `
<div id="seoContent" class="content-body"><div class="content-block" data-context="account-security" data-mode="comparison">
<p>A Venmo verification code text can be real, but if you did not request it, the situation is often risky. In many cases, scammers trigger a login attempt on purpose so Venmo sends a legitimate code to your phone. The code itself may be real, but the scam is the attempt to get you to share it with someone else.</p>

<p>The most common pattern is simple. Someone tries to sign in to your Venmo account using your phone number or login details. Right after that, you receive a real verification code text. The attacker then contacts you pretending to be Venmo support, a buyer, or someone who claims they entered your number by mistake and asks you to send the code back. If you share it, they can get into your account.</p>

<p>That is why the safest rule is direct and simple: never share a Venmo verification code with anyone. Venmo will not ask you to read a code back over text, email, chat, or social media. Any person or message asking for that code is trying to bypass your account security.</p>

<p>Another warning sign is urgency. Scam versions often try to create panic by saying there is suspicious activity, a locked account, a payment problem, or an urgent verification issue. The goal is to make you react quickly instead of stopping to think about why you received a code you never requested in the first place.</p>

<p>If you got the code but did not share it, open the official Venmo app yourself and review your account activity. Change your password if anything looks off, and make sure your login information is still secure. If you did share the code, act immediately by changing your password, reviewing transfers, and securing any linked bank or card information.</p>

<p>The clearest way to think about this is that a verification code is meant only for the person signing in. The moment someone else wants that code, the message is no longer safe. Treat unexpected Venmo verification code texts as possible account takeover attempts until you verify everything directly in the official app.</p>
</div></div>
`;

const NEW_RELATED_LINKS = [
  {
    href: "/scam-check-now/is-venmo-payment-verification-text-legit-or-scam/",
    text: "Is Venmo Payment Verification Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-transaction-verification-text-legit-or-scam/",
    text: "Is Venmo Transaction Verification Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-account-verification-email-legit-or-scam/",
    text: "Is Venmo Account Verification Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-login-attempt-text-legit-or-scam/",
    text: "Is Venmo Login Attempt Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-security-code-message-legit-or-scam/",
    text: "Is Venmo Security Code Message Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-sign-in-alert-email-legit-or-scam/",
    text: "Is Venmo Sign In Alert Email Legit or a Scam?"
  }
];

const NEW_MORE_LINKS = [
  {
    href: "/scam-check-now/is-venmo-urgent-verification-message-legit-or-scam/",
    text: "Is Venmo Urgent Verification Message Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-login-from-new-device-email-legit-or-scam/",
    text: "Is Venmo Login from New Device Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-account-warning-text-legit-or-scam/",
    text: "Is Venmo Account Warning Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-suspicious-transfer-text-legit-or-scam/",
    text: "Is Venmo Suspicious Transfer Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-payment-request-from-unknown-legit-or-scam/",
    text: "Is Venmo Payment Request from Unknown Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-venmo-payment-alert-real-or-fake/",
    text: "Is Venmo Payment Alert Real or Fake?"
  }
];

const NEW_FAQ_JSONLD = `{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"Is a Venmo verification code text always a scam?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"No. The code itself can be a real Venmo security code, but if you did not request it, it often means someone is trying to access your account. The scam usually happens when someone asks you to share that code."
      }
    },
    {
      "@type":"Question",
      "name":"Why did I get a Venmo verification code text I did not request?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"This often happens when someone tries to log in to your Venmo account using your phone number or other account details. Venmo sends a real code, but the risky part is the login attempt behind it."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I shared a Venmo verification code?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Open the official Venmo app immediately, change your password, review recent account activity, and secure any linked bank or card information. If anything looks suspicious, treat it as urgent and lock down the account right away."
      }
    }
  ]
}`;

const NEW_VISIBLE_FAQ = `
    <div class="link-section" id="visibleFaqWrap">
      <h3>Venmo Verification Code Text FAQ</h3>
      <div class="content-body">
        <p><strong>Is a Venmo verification code text always a scam?</strong><br>No. The code itself can be a real Venmo security code, but if you did not request it, it often means someone is trying to access your account. The scam usually happens when someone asks you to share that code.</p>
        <p><strong>Why did I get a Venmo verification code text I did not request?</strong><br>This often happens when someone tries to log in to your Venmo account using your phone number or other account details. Venmo sends a real code, but the risky part is the login attempt behind it.</p>
        <p><strong>What should I do if I shared a Venmo verification code?</strong><br>Open the official Venmo app immediately, change your password, review recent account activity, and secure any linked bank or card information. If anything looks suspicious, treat it as urgent and lock down the account right away.</p>
      </div>
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
    /<meta\s+name=["']description["']\s+content=["'][^"']*["']\s*\/?>/i,
    `<meta name="description" content="${escapeHtmlAttr(NEW_META)}">`,
    "meta description"
  );
}

function replaceOgTitle(html) {
  if (!NEW_TITLE) return html;

  return replaceWithCheck(
    html,
    /<meta\s+property=["']og:title["']\s+content=["'][^"']*["']\s*\/?>/i,
    `<meta property="og:title" content="${escapeHtmlAttr(NEW_TITLE)}">`,
    "og:title"
  );
}

function replaceOgDescription(html) {
  if (!NEW_META) return html;

  return replaceWithCheck(
    html,
    /<meta\s+property=["']og:description["']\s+content=["'][^"']*["']\s*\/?>/i,
    `<meta property="og:description" content="${escapeHtmlAttr(NEW_META)}">`,
    "og:description"
  );
}

function replaceTwitterTitle(html) {
  if (!NEW_TITLE) return html;

  return replaceWithCheck(
    html,
    /<meta\s+name=["']twitter:title["']\s+content=["'][^"']*["']\s*\/?>/i,
    `<meta name="twitter:title" content="${escapeHtmlAttr(NEW_TITLE)}">`,
    "twitter:title"
  );
}

function replaceTwitterDescription(html) {
  if (!NEW_META) return html;

  return replaceWithCheck(
    html,
    /<meta\s+name=["']twitter:description["']\s+content=["'][^"']*["']\s*\/?>/i,
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