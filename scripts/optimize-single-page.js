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
  "PayPal Suspicious Login Email: Fake or Real? Warning Signs & What To Do";

const NEW_META =
  "Got a PayPal suspicious login email? Learn how to spot fake alerts, phishing links, and account takeover scams. See warning signs and how to verify safely.";

const NEW_INTRO = `<p>A PayPal suspicious login email can be real, but it is also one of the most common phishing scams used to steal account access and money. These messages often look like official PayPal alerts warning about unusual activity or login attempts. Before clicking any link or responding, verify the alert directly through the official PayPal app or website.</p>`;

const NEW_RELATED_LINKS = null;

const NEW_FAQ_JSONLD = `{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"Is a PayPal suspicious login email real?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Some PayPal login alerts are real, but many are phishing emails designed to steal your login details or money. Always verify the alert directly through the official PayPal app or website instead of clicking links in the email."
      }
    },
    {
      "@type":"Question",
      "name":"How do I verify a PayPal login alert?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Open the official PayPal app or type PayPal's website directly into your browser and check your account activity there. Real alerts will still make sense after independent verification."
      }
    },
    {
      "@type":"Question",
      "name":"What happens if I click a fake PayPal email?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Fake PayPal emails often lead to phishing pages that steal your login details, passwords, or verification codes. This can lead to account takeover, unauthorized payments, and linked bank or card fraud."
      }
    }
  ]
}`;

const NEW_VISIBLE_FAQ = `
    <div class="link-section" id="visibleFaqWrap">
      <h3>PayPal Suspicious Login Email FAQ</h3>

      <div class="content-body">
        <p><strong>Is a PayPal suspicious login email real or a scam?</strong><br>Some PayPal login alerts are real, but many are phishing emails designed to steal your login details or money. Always verify the alert through the official PayPal app or website.</p>

        <p><strong>What should I do if I get one?</strong><br>Do not click links in the email. Open PayPal directly and check your account activity. If nothing appears there, the message is likely a scam.</p>

        <p><strong>What happens if I clicked the link?</strong><br>You may have been sent to a fake login page. Change your password immediately, review recent account activity, and secure your account before any unauthorized access spreads.</p>
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

function replaceFaqJsonLd(html) {
  if (!NEW_FAQ_JSONLD) return html;

  return replaceWithCheck(
    html,
    /<script type="application\/ld\+json">[\s\S]*?"@type":"FAQPage"[\s\S]*?<\/script>/i,
    `<script type="application/ld+json">\n${NEW_FAQ_JSONLD}\n</script>`,
    "FAQ JSON-LD"
  );
}

function replaceIntro(html) {
  if (!NEW_INTRO) return html;

  const updated = html.replace(
    /(<div class="content-block"[^>]*>\s*)(<p>[\s\S]*?<\/p>)/i,
    `$1${NEW_INTRO}`
  );

  if (updated === html) {
    console.warn("No change for intro paragraph");
    return html;
  }

  console.log("Updated intro paragraph");
  return updated;
}

function fixBrokenStoryParagraph(html) {
  const updated = html.replace(
    /(<div class="content-block"[^>]*>[\s\S]*?<p>[\s\S]*?<\/p>\s*<h2>[\s\S]*?<\/h2>\s*<p>[\s\S]*?<\/p>\s*)(A message lands in your inbox[\s\S]*?)(\s*<p>That difference matters because)/i,
    (match, before, storyText, after) => {
      const story = storyText.trim();
      return `${before}<p>${story}</p>${after}`;
    }
  );

  if (updated === html) {
    console.warn("No change for broken story paragraph");
    return html;
  }

  console.log("Fixed broken story paragraph");
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

function upsertVisibleFaq(html) {
  if (!NEW_VISIBLE_FAQ) return html;

  if (html.includes('id="visibleFaqWrap"')) {
    const updatedExisting = html.replace(
      /<div class="link-section" id="visibleFaqWrap">[\s\S]*?<\/div>\s*(?=<div class="content-close">)/i,
      NEW_VISIBLE_FAQ
    );

    if (updatedExisting === html) {
      console.warn("No change for visible FAQ");
      return html;
    }

    console.log("Updated visible FAQ");
    return updatedExisting;
  }

  const updatedInserted = html.replace(
    /(\s*<div class="content-close">)/i,
    `${NEW_VISIBLE_FAQ}$1`
  );

  if (updatedInserted === html) {
    console.warn("No change for visible FAQ");
    return html;
  }

  console.log("Inserted visible FAQ");
  return updatedInserted;
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
updated = replaceFaqJsonLd(updated);
updated = replaceIntro(updated);
updated = fixBrokenStoryParagraph(updated);
updated = replaceRelatedLinks(updated);
updated = upsertVisibleFaq(updated);

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