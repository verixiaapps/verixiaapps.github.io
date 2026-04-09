const fs = require("fs");
const path = require("path");

const rawInput = process.env.INPUT_URLS?.trim() || "";

if (!rawInput) {
  console.error("No URLs were provided.");
  process.exit(1);
}

const allowedRoots = new Set([
  "scam-check-now",
  "scam-check-now-b",
  "scam-check-now-c",
]);

const repoRoot = process.cwd();
const outputBlocks = [];
const errors = [];

const urls = rawInput
  .split(/\r?\n/)
  .map((line) => line.trim())
  .filter(Boolean);

function extractFilePath(url) {
  let parsed;

  try {
    parsed = new URL(url);
  } catch {
    throw new Error("Invalid URL");
  }

  if (!["http:", "https:"].includes(parsed.protocol)) {
    throw new Error("Invalid URL");
  }

  if (parsed.hostname.toLowerCase() !== "verixiaapps.com") {
    throw new Error("Must be verixiaapps.com");
  }

  const decodedPath = decodeURIComponent(parsed.pathname || "").trim();
  const normalizedPath = decodedPath.replace(/\/+/g, "/");
  const parts = normalizedPath
    .replace(/^\/|\/$/g, "")
    .split("/")
    .filter(Boolean);

  if (parts.length < 2) {
    throw new Error("Invalid path");
  }

  if (parts.some((part) => part === "." || part === "..")) {
    throw new Error("Path cannot contain . or ..");
  }

  if (!allowedRoots.has(parts[0])) {
    throw new Error("Not in allowed folders");
  }

  let fileParts;

  if (parts[parts.length - 1] === "index.html") {
    if (parts.length < 3) {
      throw new Error("Invalid index.html path");
    }
    fileParts = parts;
  } else {
    fileParts = [...parts, "index.html"];
  }

  const filePath = fileParts.join("/");
  const absolutePath = path.resolve(repoRoot, filePath);
  const allowedBase = path.resolve(repoRoot, parts[0]);

  if (!absolutePath.startsWith(allowedBase + path.sep)) {
    throw new Error("Resolved path escapes allowed folder");
  }

  return filePath;
}

for (const url of urls) {
  try {
    const filePath = extractFilePath(url);
    const absolutePath = path.resolve(repoRoot, filePath);

    if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) {
      throw new Error(`File not found: ${filePath}`);
    }

    const html = fs.readFileSync(absolutePath, "utf8").trim();

    const block = [
      "URL:",
      url,
      "",
      "FILE PATH:",
      filePath,
      "",
      "HTML:",
      html,
    ].join("\n");

    outputBlocks.push(block);
  } catch (error) {
    errors.push(`${url} -> ${error.message}`);
  }
}

const finalParts = [];

if (outputBlocks.length > 0) {
  finalParts.push(outputBlocks.join("\n==================================================\n\n"));
}

if (errors.length > 0) {
  finalParts.push(`ERRORS:\n${errors.join("\n")}`);
}

const finalOutput = finalParts.length > 0 ? `${finalParts.join("\n\n==================================================\n\n")}\n` : "";

fs.mkdirSync(path.join(repoRoot, "exports"), { recursive: true });
fs.writeFileSync(path.join(repoRoot, "exports", "page-html-export.txt"), finalOutput, "utf8");

console.log(finalOutput);

if (outputBlocks.length === 0) {
  process.exit(1);
}