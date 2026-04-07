// scripts/update-embedded-upgrade-templates.js
#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const DRY_RUN = String(process.env.DRY_RUN || "true").trim().toLowerCase() === "true";

const FRAGMENT_PATH = path.join(ROOT, "scripts", "fragments", "embedded-upgrade-script.html");
const TEMPLATE_FILES = [
  path.join(ROOT, "templates", "seo-template.html"),
  path.join(ROOT, "templates", "seo-template-b.html"),
  path.join(ROOT, "templates", "seo-template-c.html")
];

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exit(1);
}

function log(message) {
  console.log(message);
}

function exists(filePath) {
  try {
    fs.accessSync(filePath);
    return true;
  } catch {
    return false;
  }
}

function normalizeSlashes(value) {
  return String(value || "").replace(/\\/g, "/");
}

function loadFragment() {
  if (!exists(FRAGMENT_PATH)) {
    fail(`Missing fragment file: ${normalizeSlashes(path.relative(ROOT, FRAGMENT_PATH))}`);
  }

  const fragment = fs.readFileSync(FRAGMENT_PATH, "utf8").replace(/\r\n/g, "\n").trim();

  if (!fragment) {
    fail("Embedded upgrade fragment file is empty.");
  }

  if (!fragment.startsWith("<script>") || !fragment.endsWith("</script>")) {
    fail("Embedded upgrade fragment must contain exactly one full <script>...</script> block.");
  }

  return fragment;
}

function stripExistingEmbeddedUpgrade(content) {
  return content.replace(
    /\n*<script>\s*\(function\s*\(\)\s*\{\s*if\s*\(window\.__SCAM_CHECK_EMBEDDED_UPGRADE__\)\s*return;[\s\S]*?<\/script>\s*/i,
    "\n\n"
  );
}

function injectAtBottom(originalContent, fragment) {
  let content = originalContent.replace(/\r\n/g, "\n").trimEnd();
  content = stripExistingEmbeddedUpgrade(content).trimEnd();

  const bodyCloseIndex = content.toLowerCase().lastIndexOf("</body>");
  const htmlCloseIndex = content.toLowerCase().lastIndexOf("</html>");

  if (bodyCloseIndex === -1) {
    throw new Error("File is missing closing </body> tag.");
  }

  if (htmlCloseIndex === -1) {
    throw new Error("File is missing closing </html> tag.");
  }

  if (bodyCloseIndex > htmlCloseIndex) {
    throw new Error("Closing </body> appears after closing </html>.");
  }

  const beforeBodyClose = content.slice(0, bodyCloseIndex).trimEnd();
  const afterBodyClose = content.slice(bodyCloseIndex, htmlCloseIndex).trim();
  const htmlCloseTag = content.slice(htmlCloseIndex).trim();

  if (afterBodyClose.toLowerCase() !== "</body>") {
    throw new Error("Expected only </body> before </html>.");
  }

  return `${beforeBodyClose}\n\n</body>\n\n${fragment}\n\n${htmlCloseTag}\n`;
}

function main() {
  const fragment = loadFragment();

  log(`Dry run: ${DRY_RUN ? "true" : "false"}`);
  log(`Fragment: ${normalizeSlashes(path.relative(ROOT, FRAGMENT_PATH))}`);
  log(`Target templates: ${TEMPLATE_FILES.length}`);
  log("");

  let changedCount = 0;
  let unchangedCount = 0;
  const failedFiles = [];

  for (const absolutePath of TEMPLATE_FILES) {
    const relativePath = normalizeSlashes(path.relative(ROOT, absolutePath));

    try {
      if (!exists(absolutePath)) {
        throw new Error("Template file not found.");
      }

      const original = fs.readFileSync(absolutePath, "utf8");
      const updated = injectAtBottom(original, fragment);

      if (updated === original.replace(/\r\n/g, "\n")) {
        unchangedCount += 1;
        log(`UNCHANGED: ${relativePath}`);
        continue;
      }

      changedCount += 1;
      log(`${DRY_RUN ? "WOULD UPDATE" : "UPDATED"}: ${relativePath}`);

      if (!DRY_RUN) {
        fs.writeFileSync(absolutePath, updated, "utf8");
      }
    } catch (error) {
      failedFiles.push({ file: relativePath, error: error.message });
      log(`FAILED: ${relativePath} -> ${error.message}`);
    }
  }

  log("");
  log("Summary");
  log(`Changed: ${changedCount}`);
  log(`Unchanged: ${unchangedCount}`);
  log(`Failed: ${failedFiles.length}`);

  if (failedFiles.length) {
    log("");
    log("Failed files:");
    for (const item of failedFiles) {
      log(`- ${item.file}: ${item.error}`);
    }
    process.exit(1);
  }
}

main();