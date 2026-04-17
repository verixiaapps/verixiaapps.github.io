const fs = require("fs");
const path = require("path");

const TARGET_FILE = path.join(
  process.cwd(),
  "path",
  "to",
  "the-file-you-want-to-update.html"
);

function assertFileExists(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Target file not found: ${filePath}`);
  }
}

function replaceExact(source, oldValue, newValue) {
  if (!oldValue || oldValue === newValue) return source;
  if (!source.includes(oldValue)) {
    throw new Error(`Exact text not found:\\n${oldValue}`);
  }
  return source.split(oldValue).join(newValue);
}

function replaceRegex(source, regex, newValue, label) {
  if (!regex.test(source)) {
    throw new Error(`Pattern not found: ${label}`);
  }
  return source.replace(regex, newValue);
}

function ensureContains(source, needle, label) {
  if (!source.includes(needle)) {
    throw new Error(`Expected content missing: ${label}`);
  }
}

function updateFileContents(source) {
  let output = source;

  // EXAMPLE EXACT REPLACEMENTS
  output = replaceExact(
    output,
    "Old text here",
    "New text here"
  );

  output = replaceExact(
    output,
    "Another old value",
    "Another new value"
  );

  // EXAMPLE REGEX REPLACEMENT
  output = replaceRegex(
    output,
    /Old pattern here/g,
    "New pattern here",
    "old pattern replacement"
  );

  // ADD MORE CHANGES HERE
  // output = replaceExact(output, "...", "...");
  // output = replaceRegex(output, /.../g, "...", "label");

  return output;
}

function main() {
  assertFileExists(TARGET_FILE);

  const original = fs.readFileSync(TARGET_FILE, "utf8");
  const updated = updateFileContents(original);

  if (updated === original) {
    console.log("No changes made.");
    return;
  }

  fs.writeFileSync(TARGET_FILE, updated, "utf8");

  ensureContains(updated, "New text here", "first replacement");
  ensureContains(updated, "Another new value", "second replacement");

  console.log(`Updated file: ${TARGET_FILE}`);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}