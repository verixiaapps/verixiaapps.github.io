const fs = require("fs");
const path = require("path");

const SITE_ROOT = "https://verixiaapps.com";
const ROOT_DIR = "scam-check-now";

const TARGET_URLS = (process.env.TARGET_URLS || "")
  .split(",")
  .map(s => s.trim())
  .filter(Boolean);

const OPTIMIZE_TITLE = String(process.env.OPTIMIZE_TITLE) === "true";
const OPTIMIZE_META = String(process.env.OPTIMIZE_META) === "true";
const OPTIMIZE_INTRO = String(process.env.OPTIMIZE_INTRO) === "true";
const OPTIMIZE_LINKS = String(process.env.OPTIMIZE_LINKS) === "true";
const DRY_RUN = String(process.env.DRY_RUN) === "true";

const SPECIAL_REPLACEMENTS = {
  usps: "USPS",
  ups: "UPS",
  fedex: "FedEx",
  dhl: "DHL",
  td: "TD",
  bank: "Bank",
  paypal: "PayPal",
  venmo: "Venmo",
  zelle: "Zelle",
  whatsapp: "WhatsApp",
  telegram: "Telegram",
  snapchat: "Snapchat",
  instagram: "Instagram",
  facebook: "Facebook",
  google: "Google",
  apple: "Apple",
  amazon: "Amazon",
  recruiter: "Recruiter",
  interview: "Interview",
  login: "Login",
  fraud: "Fraud",
};

const STOP_WORDS = new Set([
  "is", "this", "that", "a", "an", "the", "or", "and", "real", "fake", "legit", "scam"
]);

function normalizeUrlToRelative(urlOrPath) {
  let value = String(urlOrPath || "").trim();

  if (!value) return "";

  if (value.startsWith(SITE_ROOT)) {
    value = value.slice(SITE_ROOT.length);
  }

  if (!value.startsWith("/")) {
    value = "/" + value;
  }

  return value.replace(/\/+$/, "") + "/";
}

function isAllowedTarget(relativeUrl) {
  return relativeUrl.startsWith(`/${ROOT_DIR}/`);
}

function relativeUrlToFilePath(relativeUrl) {
  const clean = relativeUrl.replace(/^\/+/, "").replace(/\/+$/, "");
  return path.join(clean, "index.html");
}

function fileExists(filePath) {
  return fs.existsSync(filePath) && fs.statSync(filePath).isFile();
}

function readFile(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function writeFile(filePath, content) {
  fs.writeFileSync(filePath, content, "utf8");
}

function extractSlugFromRelativeUrl(relativeUrl) {
  const clean = relativeUrl.replace(/^\/+/, "").replace(/\/+$/, "");
  const parts = clean.split("/");
  return parts[parts.length - 1] || "";
}

function humanizeWord(word) {
  const lower = word.toLowerCase();
  if (SPECIAL_REPLACEMENTS[lower]) return SPECIAL_REPLACEMENTS[lower];
  if (lower.length <= 2) return lower.toUpperCase();
  return lower.charAt(0).toUpperCase() + lower.slice(1);
}

function slugToReadableTopic(slug) {
  const words = slug
    .split("-")
    .map(w => w.trim())
    .filter(Boolean);

  return words.map(humanizeWord).join(" ");
}

function slugToCoreTopic(slug) {
  const words = slug
    .split("-")
    .map(w => w.trim().toLowerCase())
    .filter(Boolean)
    .filter(w => !STOP_WORDS.has(w));

  return words.map(humanizeWord).join(" ");
}

function buildTitle(slug) {
  const raw = slugToReadableTopic(slug);
  const core = slugToCoreTopic(slug) || raw;

  if (/fraud-alert/.test(slug)) {
    return `${core}? Don’t Click Until You Check This`;
  }

  if (/recruiter|interview|job/.test(slug)) {
    return `${core}? Real Recruiter or Scam Warning`;
  }

  if (/login|verification|account/.test(slug)) {
    return `${core}? Real or Fake Security Alert`;
  }

  if (/whatsapp|telegram|snapchat|instagram/.test(slug)) {
    return `${core}: Scam Signs and What to Do`;
  }

  if (/fedex|ups|usps|delivery|package|reroute/.test(slug)) {
    return `${core}? Delivery Scam Warning Signs`;
  }

  return `${raw}? Real or Scam Warning Signs`;
}

function buildMetaDescription(slug) {
  const raw = slugToReadableTopic(slug);
  const core = slugToCoreTopic(slug) || raw;

  if (/fraud-alert/.test(slug)) {
    return `Got a ${core.toLowerCase()} message? Learn the red flags, how to verify it safely, and what to do before you click or respond.`;
  }

  if (/recruiter|interview|job/.test(slug)) {
    return `Received a ${core.toLowerCase()} message? Learn the warning signs of fake recruiters, suspicious interview requests, and how to verify it safely.`;
  }

  if (/login|verification|account/.test(slug)) {
    return `Got a ${core.toLowerCase()} email or text? Check the red flags, common scam patterns, and safest next steps before you enter any information.`;
  }

  if (/whatsapp|telegram|snapchat|instagram/.test(slug)) {
    return `Worried about ${core.toLowerCase()} scams? Learn common warning signs, how these scams work, and what to do if you already replied.`;
  }

  if (/fedex|ups|usps|delivery|package|reroute/.test(slug)) {
    return `Got a ${core.toLowerCase()} message? See the common delivery scam signs, what is safe to click, and how to verify the message.`;
  }

  return `Learn whether ${raw.toLowerCase()} is real or a scam, the biggest warning signs, and the safest next step before clicking or replying.`;
}

function buildIntroHtml(slug) {
  const raw = slugToReadableTopic(slug);
  const core = slugToCoreTopic(slug) || raw;

  if (/fraud-alert/.test(slug)) {
    return `
<p>If you got a ${core} message, pause before you click anything. Scam messages often copy the language and urgency of real fraud alerts to pressure you into reacting fast.</p>
<p>The safest move is to verify the alert directly through the company’s official app, website, or phone number you look up yourself — not the link or number inside the message.</p>
`;
  }

  if (/recruiter|interview|job/.test(slug)) {
    return `
<p>If you received a ${core} message, do not assume it is real just because it sounds professional. Fake recruiter scams often promise jobs, interviews, or fast hiring to collect personal details or push victims into fake payments.</p>
<p>Check for pressure, vague company details, off-platform contact requests, and any demand for money, gift cards, or sensitive information early in the conversation.</p>
`;
  }

  if (/login|verification|account/.test(slug)) {
    return `
<p>If you got a ${core} alert, be careful before entering your password or verification code. Account-security scams often create urgency and fear so people act before checking the sender or destination page.</p>
<p>The safest path is to open the official app or website yourself and check your account there instead of using the link in the message.</p>
`;
  }

  if (/whatsapp|telegram|snapchat|instagram/.test(slug)) {
    return `
<p>${raw} can take many forms, including fake support messages, impersonation, romance scams, crypto pitches, and requests for verification codes. The exact wording changes, but the goal is usually the same: get access, money, or trust quickly.</p>
<p>Look for urgency, strange links, requests to move the conversation, and anything asking for codes, payments, or sensitive personal details.</p>
`;
  }

  if (/fedex|ups|usps|delivery|package|reroute/.test(slug)) {
    return `
<p>If you got a ${core} message, slow down before clicking. Delivery scams often use package issues, rerouting, customs fees, or missed-delivery warnings to make the message feel urgent and believable.</p>
<p>Before you interact with it, verify the shipment through the official delivery site or app using tracking information you already trust.</p>
`;
  }

  return `
<p>If you got a ${raw} message, it is smart to verify it before clicking or replying. Many scams are designed to look routine, urgent, and believable at first glance.</p>
<p>Below are the key warning signs, what to check, and the safest next steps if you are unsure whether the message is real.</p>
`;
}

function walk(dir, callback) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, callback);
    } else {
      callback(full);
    }
  }
}

function extractAllSeoPages() {
  const pages = [];

  if (!fs.existsSync(ROOT_DIR)) return pages;

  walk(ROOT_DIR, filePath => {
    if (filePath.endsWith("index.html")) {
      const relative = "/" + filePath.replace(/\\/g, "/").replace(/\/index\.html$/, "/");
      pages.push(relative);
    }
  });

  return pages;
}

function getRelatedPages(currentRelativeUrl, limit = 10) {
  const currentSlug = extractSlugFromRelativeUrl(currentRelativeUrl);
  const currentTerms = new Set(
    currentSlug
      .split("-")
      .map(x => x.toLowerCase())
      .filter(x => x && !STOP_WORDS.has(x))
  );

  const allPages = extractAllSeoPages().filter(p => p !== currentRelativeUrl);

  const scored = allPages.map(page => {
    const slug = extractSlugFromRelativeUrl(page);
    const terms = slug.split("-").map(x => x.toLowerCase()).filter(Boolean);
    let score = 0;

    for (const t of terms) {
      if (currentTerms.has(t)) score += 2;
    }

    if (/bank|paypal|venmo|zelle|login|verification|account/.test(currentSlug) && /bank|paypal|venmo|zelle|login|verification|account/.test(slug)) {
      score += 2;
    }

    if (/fedex|ups|usps|delivery|package|reroute/.test(currentSlug) && /fedex|ups|usps|delivery|package|reroute/.test(slug)) {
      score += 2;
    }

    if (/recruiter|interview|job/.test(currentSlug) && /recruiter|interview|job/.test(slug)) {
      score += 2;
    }

    if (/whatsapp|telegram|snapchat|instagram/.test(currentSlug) && /whatsapp|telegram|snapchat|instagram/.test(slug)) {
      score += 2;
    }

    return { page, score };
  });

  return scored
    .sort((a, b) => b.score - a.score || a.page.localeCompare(b.page))
    .slice(0, limit)
    .map(x => x.page);
}

function buildLinksHtml(relativeUrls) {
  return relativeUrls.map(url => {
    const slug = extractSlugFromRelativeUrl(url);
    const label = slugToReadableTopic(slug);
    return `<li><a href="${url}">${label}</a></li>`;
  }).join("\n");
}

function replaceTitle(html, newTitle) {
  if (/<title>[\s\S]*?<\/title>/i.test(html)) {
    return html.replace(/<title>[\s\S]*?<\/title>/i, `<title>${escapeHtml(newTitle)}</title>`);
  }

  return html.replace(/<head>/i, `<head>\n<title>${escapeHtml(newTitle)}</title>`);
}

function replaceMetaDescription(html, description) {
  const tag = `<meta name="description" content="${escapeHtmlAttr(description)}">`;

  if (/<meta\s+name=["']description["'][^>]*>/i.test(html)) {
    return html.replace(/<meta\s+name=["']description["'][^>]*>/i, tag);
  }

  return html.replace(/<head>/i, `<head>\n${tag}`);
}

function replaceIntro(html, introHtml) {
  if (/<section[^>]*id=["']seo-intro["'][\s\S]*?<\/section>/i.test(html)) {
    return html.replace(
      /<section[^>]*id=["']seo-intro["'][\s\S]*?<\/section>/i,
      `<section id="seo-intro">\n${introHtml.trim()}\n</section>`
    );
  }

  if (/<main[^>]*>/i.test(html)) {
    return html.replace(
      /<main[^>]*>/i,
      match => `${match}\n<section id="seo-intro">\n${introHtml.trim()}\n</section>`
    );
  }

  return html;
}

function replaceRelatedLinks(html, linksHtml) {
  if (/<ul[^>]*id=["']relatedLinks["'][\s\S]*?<\/ul>/i.test(html)) {
    return html.replace(
      /<ul[^>]*id=["']relatedLinks["'][\s\S]*?<\/ul>/i,
      `<ul id="relatedLinks">\n${linksHtml}\n</ul>`
    );
  }

  if (/<\/main>/i.test(html)) {
    return html.replace(
      /<\/main>/i,
      `<section>\n<h2>Related scam checks</h2>\n<ul id="relatedLinks">\n${linksHtml}\n</ul>\n</section>\n</main>`
    );
  }

  return html;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function escapeHtmlAttr(text) {
  return escapeHtml(text).replace(/"/g, "&quot;");
}

function optimizeOne(relativeUrl) {
  if (!isAllowedTarget(relativeUrl)) {
    console.log(`Skipping non-A URL: ${relativeUrl}`);
    return;
  }

  const filePath = relativeUrlToFilePath(relativeUrl);

  if (!fileExists(filePath)) {
    console.log(`Skipping missing file: ${filePath}`);
    return;
  }

  const slug = extractSlugFromRelativeUrl(relativeUrl);
  let html = readFile(filePath);
  const original = html;

  if (OPTIMIZE_TITLE) {
    html = replaceTitle(html, buildTitle(slug));
  }

  if (OPTIMIZE_META) {
    html = replaceMetaDescription(html, buildMetaDescription(slug));
  }

  if (OPTIMIZE_INTRO) {
    html = replaceIntro(html, buildIntroHtml(slug));
  }

  if (OPTIMIZE_LINKS) {
    const related = getRelatedPages(relativeUrl, 10);
    html = replaceRelatedLinks(html, buildLinksHtml(related));
  }

  if (html !== original) {
    console.log(`Updated: ${filePath}`);
    if (!DRY_RUN) {
      writeFile(filePath, html);
    }
  } else {
    console.log(`No changes: ${filePath}`);
  }
}

function main() {
  if (!TARGET_URLS.length) {
    console.error("No target URLs provided.");
    process.exit(1);
  }

  const normalized = TARGET_URLS
    .map(normalizeUrlToRelative)
    .filter(Boolean);

  console.log("Target URLs:");
  for (const url of normalized) {
    console.log(`- ${url}`);
  }

  for (const relativeUrl of normalized) {
    optimizeOne(relativeUrl);
  }

  console.log(DRY_RUN ? "Dry run complete." : "Optimization complete.");
}

main();