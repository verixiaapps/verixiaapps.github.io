#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();

const RUN_MODE = String(process.env.RUN_MODE || "single_page").trim();
const TARGET_FOLDER = String(process.env.TARGET_FOLDER || "scam-check-now").trim();
const PAGE_PATH = String(process.env.PAGE_PATH || "").trim();
const DRY_RUN = String(process.env.DRY_RUN || "true").trim().toLowerCase() === "true";

const ALLOWED_FOLDERS = ["scam-check-now", "scam-check-now-b", "scam-check-now-c"];
const FRAGMENT_PATH = path.join(ROOT, "scripts", "fragments", "embedded-upgrade-script.html");

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

function ensureAllowedFolder(folder) {
  if (!ALLOWED_FOLDERS.includes(folder)) {
    fail(`Invalid target folder: ${folder}. Allowed: ${ALLOWED_FOLDERS.join(", ")}`);
  }
}

function ensureSafeRelativePagePath(relativePath) {
  const normalized = normalizeSlashes(relativePath).replace(/^\/+/, "");

  if (!normalized) {
    fail("PAGE_PATH is required when RUN_MODE=single_page.");
  }

  if (normalized.includes("..")) {
    fail(`Unsafe PAGE_PATH: ${relativePath}`);
  }

  const matchedRoot = ALLOWED_FOLDERS.find(
    (folder) => normalized === folder || normalized.startsWith(`${folder}/`)
  );

  if (!matchedRoot) {
    fail(
      `PAGE_PATH must start with one of: ${ALLOWED_FOLDERS.join(", ")}. Received: ${relativePath}`
    );
  }

  if (!normalized.endsWith("/index.html")) {
    fail(`PAGE_PATH must point to an index.html file. Received: ${relativePath}`);
  }

  return normalized;
}

function walkIndexFiles(folderAbsolutePath) {
  const results = [];

  function walk(currentPath) {
    const entries = fs.readdirSync(currentPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(currentPath, entry.name);

      if (entry.isDirectory()) {
        walk(fullPath);
        continue;
      }

      if (entry.isFile() && entry.name === "index.html") {
        results.push(fullPath);
      }
    }
  }

  walk(folderAbsolutePath);
  return results.sort();
}

function loadFragment() {
  if (!exists(FRAGMENT_PATH)) {
    fail(`Missing fragment file: ${path.relative(ROOT, FRAGMENT_PATH)}`);
  }

  let fragment = fs.readFileSync(FRAGMENT_PATH, "utf8").replace(/\r\n/g, "\n").trim();

  if (!fragment) {
    fail("Embedded upgrade fragment file is empty.");
  }

  if (!fragment.startsWith("<script>") || !fragment.endsWith("</script>")) {
    fail("Embedded upgrade fragment must contain exactly one full <script>...</script> block.");
  }

  return fragment;
}

function getTargetFiles() {
  if (RUN_MODE === "single_page") {
    const safeRelativePath = ensureSafeRelativePagePath(PAGE_PATH);
    const absolutePath = path.join(ROOT, safeRelativePath);

    if (!exists(absolutePath)) {
      fail(`Single page file not found: ${safeRelativePath}`);
    }

    return [absolutePath];
  }

  if (RUN_MODE === "folder") {
    ensureAllowedFolder(TARGET_FOLDER);
    const folderAbsolutePath = path.join(ROOT, TARGET_FOLDER);

    if (!exists(folderAbsolutePath)) {
      fail(`Target folder not found: ${TARGET_FOLDER}`);
    }

    return walkIndexFiles(folderAbsolutePath);
  }

  if (RUN_MODE === "all") {
    return ALLOWED_FOLDERS.flatMap((folder) => {
      const folderAbsolutePath = path.join(ROOT, folder);
      if (!exists(folderAbsolutePath)) {
        log(`Skipping missing folder: ${folder}`);
        return [];
      }
      return walkIndexFiles(folderAbsolutePath);
    });
  }

  fail(`Invalid RUN_MODE: ${RUN_MODE}. Allowed: single_page, folder, all`);
}

function stripPreviousInjectedBlock(content) {
  let updated = content;

  updated = updated.replace(
    /\n*<script>\s*\(function\s*\(\)\s*\{\s*[\s\S]*?window\.__SCAM_CHECK_EMBEDDED_UPGRADE__[\s\S]*?<\/script>\s*(?=<\/html>\s*$)/i,
    "\n"
  );

  return updated;
}

function injectAtBottom(originalContent, fragment) {
  let content = originalContent.replace(/\r\n/g, "\n").trimEnd();

  content = stripPreviousInjectedBlock(content).trimEnd();

  const hasBodyClose = /<\/body>\s*<\/html>\s*$/i.test(content);
  if (!hasBodyClose) {
    throw new Error("File does not end with </body></html> in the expected order.");
  }

  content = content.replace(/<\/body>\s*<\/html>\s*$/i, "</body>");

  return `${content}\n\n${fragment}\n\n</html>\n`;
}

function main() {
  const fragment = loadFragment();
  const files = getTargetFiles();

  if (!files.length) {
    log("No matching index.html files found.");
    process.exit(0);
  }

  log(`Run mode: ${RUN_MODE}`);
  log(`Dry run: ${DRY_RUN ? "true" : "false"}`);
  log(`Fragment: ${path.relative(ROOT, FRAGMENT_PATH)}`);
  log(`Target files: ${files.length}`);
  log("");

  let changedCount = 0;
  let unchangedCount = 0;
  const changedFiles = [];
  const unchangedFiles = [];
  const failedFiles = [];

  for (const absolutePath of files) {
    const relativePath = normalizeSlashes(path.relative(ROOT, absolutePath));

    try {
      const original = fs.readFileSync(absolutePath, "utf8");
      const updated = injectAtBottom(original, fragment);

      if (updated === original.replace(/\r\n/g, "\n")) {
        unchangedCount += 1;
        unchangedFiles.push(relativePath);
        log(`UNCHANGED: ${relativePath}`);
        continue;
      }

      changedCount += 1;
      changedFiles.push(relativePath);
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

  if (changedFiles.length) {
    log("");
    log("Changed files:");
    for (const file of changedFiles) {
      log(`- ${file}`);
    }
  }

  if (unchangedFiles.length) {
    log("");
    log("Unchanged files:");
    for (const file of unchangedFiles) {
      log(`- ${file}`);
    }
  }

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