 const fs = require("fs");
const path = require("path");

const TARGET_PAGE = process.env.TARGET_PAGE;
const DRY_RUN = String(process.env.DRY_RUN).toLowerCase() === "true";

if (!TARGET_PAGE) {
  console.error("Missing TARGET_PAGE env");
  process.exit(1);
}

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
// CUSTOMIZE PER PAGE (YOU/ME EDIT THIS PART ONLY)
// -----------------------------
const NEW_TITLE = null; // example: "Is Amazon Refund Email Legit or Scam? Warning Signs"
const NEW_META = null;  // example: "Got an Amazon refund email? Learn warning signs and how to check if it's real or a scam."

const NEW_INTRO = null; // example: "<p>...</p>"

const NEW_RELATED_LINKS = null;
// example:
// [
//   { href: "/scam-check-now/page-1/", text: "Page 1" },
//   { href: "/scam-check-now/page-2/", text: "Page 2" }
// ]

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

function replaceTitle(html) {
  if (!NEW_TITLE) return html;

  return html.replace(
    /<title\b[^>]*>.*?<\/title>/i,
    `<title>${NEW_TITLE}</title>`
  );
}

function replaceMetaDescription(html) {
  if (!NEW_META) return html;

  return html.replace(
    /<meta\s+name=["']description["']\s+content=["'][^"']*["']\s*\/?>/i,
    `<meta name="description" content="${NEW_META}">`
  );
}

function replaceIntro(html) {
  if (!NEW_INTRO) return html;

  // replace first <p> inside content-block
  return html.replace(
    /(<div class="content-block"[^>]*>)([\s\S]*?)(<p>[\s\S]*?<\/p>)/i,
    (match, start, middle, firstP) => {
      return `${start}${middle}${NEW_INTRO}`;
    }
  );
}

function replaceRelatedLinks(html) {
  if (!NEW_RELATED_LINKS) return html;

  const listHTML = NEW_RELATED_LINKS.map(
    (l) => `<li><a href="${l.href}">${l.text}</a></li>`
  ).join("\n");

  return html.replace(
    /<ul id="relatedLinks">[\s\S]*?<\/ul>/i,
    `<ul id="relatedLinks">\n${listHTML}\n</ul>`
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
updated = replaceIntro(updated);
updated = replaceRelatedLinks(updated);

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