const fs = require("fs");
const path = require("path");

// ✅ EXACT PAGE TARGETED
const TARGET_PAGE = "scam-check-now/paypal-suspicious-login-email-scam/index.html";
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
  "PayPal Suspicious Login Email Scam? How to Tell if It's Real or Fake";

const NEW_META =
  "Got a PayPal suspicious login email? Learn the real warning signs, fake sender tricks, phishing links, and account lock language scammers use before you click.";

const NEW_SEO_CONTENT = `
<div id="seoContent" class="content-body"><div class="content-block" data-context="account-security" data-mode="comparison">
<p>A PayPal suspicious login email can be real, but it is also one of the most common phishing setups used to steal logins, verification codes, and money. If you received one, the safest move is to stop inside the message and verify the alert directly in the official PayPal app or by typing PayPal's website into your browser yourself. If the warning only works when you stay inside the email, treat it like a scam until proven otherwise.</p>

<p>If you want a fast check, look for the biggest red flags first. A suspicious PayPal login email often pushes a login button instead of telling you to check your account directly. It may warn that your account will be locked, restricted, or limited unless you act immediately. It may also ask for your password, one-time code, card details, or identity confirmation through the email flow. If you cannot confirm the same alert inside your real PayPal account, assume the message is unsafe.</p>

<p>A fake PayPal suspicious login email usually starts by looking routine. The subject line may say things like "Suspicious Login Detected," "Unusual Sign-In Attempt," or "Your Account Needs Attention," and the email often copies PayPal colors, logo placement, button styling, and generic account language closely enough to feel familiar. That surface-level polish is what gets people to lower their guard.</p>

<p>The strongest warning sign is usually not the branding. It is the pressure. Scam versions often tell you your account will be locked in a few hours, that unauthorized payments may already be pending, or that you must verify activity immediately through a button inside the email. That is the point where many people click too quickly. A real PayPal alert can be checked by opening the official app or signing in manually, while a phishing email depends on keeping you inside its own link path.</p>

<p>Many of these emails also reveal themselves through the sender and destination details. You may see a display name like "PayPal Security" while the actual sender address or reply-to field points somewhere unrelated, or the link preview leads to a domain that only looks PayPal-like at a glance. Common scam patterns include extra words, added hyphens, swapped letters, or a support-style domain that is not actually PayPal. That mismatch matters more than how professional the email looks.</p>

<p>If you clicked through and entered your login, password, or verification code on a fake page, act quickly. Go directly to the real PayPal site or app, change your password, review recent activity, and secure any linked cards or bank accounts. Attackers can move fast once they get access, which is why the safest rule is simple: never secure a PayPal account from inside a suspicious email. Verify the issue from the real PayPal app or website first, then act only from there.</p>
</div></div>
`;

const NEW_RELATED_LINKS = [
  {
    href: "/scam-check-now/is-paypal-suspicious-login-alert-email-legit-or-scam/",
    text: "Is PayPal Suspicious Login Alert Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-login-attempt-email-legit-or-scam/",
    text: "Is PayPal Login Attempt Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-unusual-login-email-legit-or-scam/",
    text: "Is PayPal Unusual Login Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-login-from-new-device-email-legit-or-scam/",
    text: "Is PayPal Login from New Device Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-suspicious-login-text-legit-or-scam/",
    text: "Is PayPal Suspicious Login Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-login-alert-text-legit-or-scam/",
    text: "Is PayPal Login Alert Text Legit or a Scam?"
  }
];

const NEW_MORE_LINKS = [
  {
    href: "/scam-check-now/is-paypal-unauthorized-login-text-legit-or-scam/",
    text: "Is PayPal Unauthorized Login Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-account-limited-email-legit-or-scam/",
    text: "Is PayPal Account Limited Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-account-locked-email-legit-or-scam/",
    text: "Is PayPal Account Locked Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-account-restriction-email-legit-or-scam/",
    text: "Is PayPal Account Restriction Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-account-suspension-email-legit-or-scam/",
    text: "Is PayPal Account Suspension Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-account-unlock-email-legit-or-scam/",
    text: "Is PayPal Account Unlock Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-account-verification-email-legit-or-scam/",
    text: "Is PayPal Account Verification Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-paypal-account-warning-email-legit-or-scam/",
    text: "Is PayPal Account Warning Email Legit or a Scam?"
  }
];

const NEW_FAQ_JSONLD = `{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"Is a PayPal suspicious login email always fake?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"No. Some PayPal login alerts are real, but many are phishing emails built to steal your login, code, or payment details. The safest way to tell is to ignore the email links and verify the alert directly in the official PayPal app or website."
      }
    },
    {
      "@type":"Question",
      "name":"How can I tell if a PayPal sender address is fake?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Check the full sender address, reply-to address, and link destination instead of relying on the display name alone. Scam emails often use addresses or domains that look similar to PayPal but are not actually PayPal."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I clicked a fake PayPal login email?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Go directly to the real PayPal site or app, change your password, review recent activity, and secure any linked cards or bank accounts. If you entered a one-time code or other sensitive details, treat it as urgent and lock down the account immediately."
      }
    }
  ]
}`;

const NEW_VISIBLE_FAQ = `
    <div class="link-section" id="visibleFaqWrap">
      <h3>PayPal Suspicious Login Email FAQ</h3>
      <div class="content-body">
        <p><strong>Is a PayPal suspicious login email always fake?</strong><br>No. Some PayPal login alerts are real, but many are phishing emails built to steal your login, code, or payment details. The safest way to tell is to ignore the email links and verify the alert directly in the official PayPal app or website.</p>
        <p><strong>How can I tell if a PayPal sender address is fake?</strong><br>Check the full sender address, reply-to address, and link destination instead of relying on the display name alone. Scam emails often use addresses or domains that look similar to PayPal but are not actually PayPal.</p>
        <p><strong>What should I do if I clicked a fake PayPal login email?</strong><br>Go directly to the real PayPal site or app, change your password, review recent activity, and secure any linked cards or bank accounts. If you entered a one-time code or other sensitive details, treat it as urgent and lock down the account immediately.</p>
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