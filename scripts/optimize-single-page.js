const fs = require("fs");
const path = require("path");

// ✅ EXACT PAGE TARGETED
const TARGET_PAGE = "scam-check-now/is-wells-fargo-payment-declined-email-legit-or-scam/index.html";
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
  "Wells Fargo Payment Declined Email Scam? How to Tell if It's Real or Fake";

const NEW_META =
  "Got a Wells Fargo payment declined email? Learn the warning signs, fake sender tricks, phishing links, and urgent account language scammers use before you click.";

const NEW_SEO_CONTENT = `
<div id="seoContent" class="content-body"><div class="content-block" data-context="account-security" data-mode="comparison">
<p>A Wells Fargo payment declined email can sometimes be real, but it is also a common phishing setup used to steal login details, verification codes, and payment information. If you received one, the safest move is to stop inside the message and check your account directly in the official Wells Fargo app or by typing the Wells Fargo website into your browser yourself. If the alert only works when you stay inside the email, treat it like a scam until proven otherwise.</p>

<p>If you want a fast check, look for the biggest red flags first. A fake Wells Fargo payment declined email often pushes you to click a button to update billing information, verify your account, or fix a payment issue immediately. It may warn that your account will be restricted, locked, or unable to process payments unless you act fast. If you cannot confirm the same issue inside your real Wells Fargo account, assume the message is unsafe.</p>

<p>Most scam versions start by looking routine. The subject line may say things like "Payment Declined," "Action Required," "Billing Issue Detected," or "Your Payment Could Not Be Processed," and the email often copies Wells Fargo branding, colors, and layout closely enough to feel legitimate. It may include a logo, a warning banner, and a button that looks like a normal account action, which is exactly why people click too quickly.</p>

<p>The strongest warning sign is usually the pressure. Scam emails often say your account may be restricted, your payment failed, or your access will be limited unless you fix the issue immediately. That urgency is what does most of the work. A real Wells Fargo alert can be checked safely by opening the official app or signing in manually, while a phishing email depends on keeping you inside its own link path.</p>

<p>Another major signal is the sender and link mismatch. You might see a display name like "Wells Fargo Alerts," but the real sender address or reply-to field points somewhere unrelated. The link may also look correct at first glance while leading to a domain that is slightly altered, misspelled, or completely unrelated to Wells Fargo. Those small differences are often the clearest proof that the email is fake.</p>

<p>If you clicked the link or entered your login, password, or verification code, act quickly. Go directly to the real Wells Fargo website or app, change your password, review recent account activity, and secure any linked cards or accounts. Attackers can move fast once they get access, which is why you should never try to fix a Wells Fargo account problem from inside a suspicious email.</p>
</div></div>
`;

const NEW_RELATED_LINKS = [
  {
    href: "/scam-check-now/is-wells-fargo-account-locked-email-legit-or-scam/",
    text: "Is Wells Fargo Account Locked Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-wells-fargo-fraud-alert-email-legit-or-scam/",
    text: "Is Wells Fargo Fraud Alert Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-wells-fargo-login-alert-email-legit-or-scam/",
    text: "Is Wells Fargo Login Alert Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-wells-fargo-password-reset-email-legit-or-scam/",
    text: "Is Wells Fargo Password Reset Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-wells-fargo-suspicious-activity-email-legit-or-scam/",
    text: "Is Wells Fargo Suspicious Activity Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-wells-fargo-transfer-alert-email-legit-or-scam/",
    text: "Is Wells Fargo Transfer Alert Email Legit or a Scam?"
  }
];

const NEW_MORE_LINKS = [
  {
    href: "/scam-check-now/is-wells-fargo-security-alert-message-legit-or-scam/",
    text: "Is Wells Fargo Security Alert Message Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-wells-fargo-verification-code-text-legit-or-scam/",
    text: "Is Wells Fargo Verification Code Text Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-bank-payment-declined-email-legit-or-scam/",
    text: "Is Bank Payment Declined Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-chase-payment-declined-email-legit-or-scam/",
    text: "Is Chase Payment Declined Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-bank-of-america-payment-declined-email-legit-or-scam/",
    text: "Is Bank of America Payment Declined Email Legit or a Scam?"
  },
  {
    href: "/scam-check-now/is-citizens-bank-payment-declined-email-legit-or-scam/",
    text: "Is Citizens Bank Payment Declined Email Legit or a Scam?"
  }
];

const NEW_FAQ_JSONLD = `{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"Is a Wells Fargo payment declined email always fake?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"No. Some Wells Fargo payment alerts are real, but many are phishing emails designed to steal login details, codes, or payment information. The safest way to check is to ignore the email links and verify the alert directly in the official Wells Fargo app or website."
      }
    },
    {
      "@type":"Question",
      "name":"How can I tell if a Wells Fargo payment declined email is fake?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Check the full sender address, reply-to address, and link destination instead of relying on the display name alone. Scam emails often use addresses and domains that look similar to Wells Fargo but are not official."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I clicked a fake Wells Fargo payment declined email?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Go directly to the official Wells Fargo site or app, change your password, review account activity, and secure any linked cards or accounts immediately. If you entered login details or a verification code, treat it as urgent."
      }
    }
  ]
}`;

const NEW_VISIBLE_FAQ = `
    <div class="link-section" id="visibleFaqWrap">
      <h3>Wells Fargo Payment Declined Email FAQ</h3>
      <div class="content-body">
        <p><strong>Is a Wells Fargo payment declined email always fake?</strong><br>No. Some Wells Fargo payment alerts are real, but many are phishing emails designed to steal login details, codes, or payment information. The safest way to check is to ignore the email links and verify the alert directly in the official Wells Fargo app or website.</p>
        <p><strong>How can I tell if a Wells Fargo payment declined email is fake?</strong><br>Check the full sender address, reply-to address, and link destination instead of relying on the display name alone. Scam emails often use addresses and domains that look similar to Wells Fargo but are not official.</p>
        <p><strong>What should I do if I clicked a fake Wells Fargo payment declined email?</strong><br>Go directly to the official Wells Fargo site or app, change your password, review account activity, and secure any linked cards or accounts immediately. If you entered login details or a verification code, treat it as urgent.</p>
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