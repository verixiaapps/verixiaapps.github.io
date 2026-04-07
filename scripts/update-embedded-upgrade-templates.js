// scripts/update-embedded-upgrade-templates.js

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();

const FRAGMENT_PATH = path.join(ROOT, "scripts", "fragments", "embedded-upgrade-script.html");

const TEMPLATE_FILES = [
  path.join(ROOT, "templates", "seo-template.html"),
  path.join(ROOT, "templates", "seo-template-b.html"),
  path.join(ROOT, "templates", "seo-template-c.html")
];

function fail(msg) {
  console.error("ERROR:", msg);
  process.exit(1);
}

function loadFragment() {
  if (!fs.existsSync(FRAGMENT_PATH)) {
    fail("Missing fragment: " + FRAGMENT_PATH);
  }

  const content = fs.readFileSync(FRAGMENT_PATH, "utf8").trim();

  if (!content.startsWith("<script>") || !content.endsWith("</script>")) {
    fail("Fragment must be a full <script>...</script>");
  }

  return content;
}

function removeOldScript(html) {
  return html.replace(
    /<script>\s*\(function\s*\(\)\s*\{\s*if\s*\(window\.__SCAM_CHECK_EMBEDDED_UPGRADE__\)[\s\S]*?<\/script>/i,
    ""
  );
}

function injectScript(html, script) {
  const cleaned = removeOldScript(html).trim();

  if (!cleaned.includes("</body>")) {
    throw new Error("Missing </body>");
  }

  return cleaned.replace(
    /<\/body>/i,
    `\n\n${script}\n\n</body>`
  );
}

function run() {
  const script = loadFragment();

  let updated = 0;

  for (const file of TEMPLATE_FILES) {
    if (!fs.existsSync(file)) {
      console.log("Skip (missing):", file);
      continue;
    }

    const original = fs.readFileSync(file, "utf8");
    const next = injectScript(original, script);

    if (original !== next) {
      fs.writeFileSync(file, next, "utf8");
      console.log("UPDATED:", file);
      updated++;
    } else {
      console.log("UNCHANGED:", file);
    }
  }

  console.log("\nDone. Updated:", updated);
}

run();