const fs = require("fs");

const path = require("path");

const TEMPLATE_PATH = process.env.TEMPLATE_PATH

  ? path.join(process.cwd(), process.env.TEMPLATE_PATH)

  : path.join(process.cwd(), "token-risk-template", "token-risk-template-a.html");

function assertFileExists(filePath) {

  if (!fs.existsSync(filePath)) {

    throw new Error(`Template file not found: ${filePath}`);

  }

}

function ensureContains(source, needle, label) {

  if (!source.includes(needle)) {

    throw new Error(`Missing: ${label}`);

  }

}

function escapeRegex(value) {

  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

}

function findFunctionRange(source, functionName) {

  const escapedName = escapeRegex(functionName);

  const startRegex = new RegExp(`(?:async\\s+)?function\\s+${escapedName}\\s*\\(`);

  const startMatch = startRegex.exec(source);

  if (!startMatch) return null;

  const startIndex = startMatch.index;

  const braceStart = source.indexOf("{", startIndex);

  if (braceStart === -1) {

    throw new Error(`Could not find function body start for: ${functionName}`);

  }

  let depth = 0;

  let inSingle = false;

  let inDouble = false;

  let inTemplate = false;

  let inLineComment = false;

  let inBlockComment = false;

  let prev = "";

  for (let i = braceStart; i < source.length; i++) {

    const char = source[i];

    const next = source[i + 1];

    if (inLineComment) {

      if (char === "\n") inLineComment = false;

      prev = char;

      continue;

    }

    if (inBlockComment) {

      if (prev === "*" && char === "/") inBlockComment = false;

      prev = char;

      continue;

    }

    if (!inSingle && !inDouble && !inTemplate) {

      if (char === "/" && next === "/") {

        inLineComment = true;

        prev = char;

        continue;

      }

      if (char === "/" && next === "*") {

        inBlockComment = true;

        prev = char;

        continue;

      }

    }

    if (!inDouble && !inTemplate && char === "'" && prev !== "\\") {

      inSingle = !inSingle;

      prev = char;

      continue;

    }

    if (!inSingle && !inTemplate && char === `"` && prev !== "\\") {

      inDouble = !inDouble;

      prev = char;

      continue;

    }

    if (!inSingle && !inDouble && char === "`" && prev !== "\\") {

      inTemplate = !inTemplate;

      prev = char;

      continue;

    }

    if (!inSingle && !inDouble && !inTemplate) {

      if (char === "{") depth++;

      if (char === "}") {

        depth--;

        if (depth === 0) {

          return { start: startIndex, end: i + 1 };

        }

      }

    }

    prev = char;

  }

  throw new Error(`Could not find function end for: ${functionName}`);

}

function upsertFunction(source, functionName, replacement, insertBeforeName) {

  const range = findFunctionRange(source, functionName);

  if (range) {

    return source.slice(0, range.start) + replacement + source.slice(range.end);

  }

  const insertRange = findFunctionRange(source, insertBeforeName);

  if (!insertRange) {

    throw new Error(`Function not found for insertion: ${insertBeforeName}`);

  }

  return (

    source.slice(0, insertRange.start) +

    replacement +

    "\n\n" +

    source.slice(insertRange.start)

  );

}

function upsertStyleBlock(source, styleId, css, insertBeforeTag = "</head>") {

  const block = `<style id="${styleId}">\n${css}\n</style>`;

  const regex = new RegExp(

    `<style[^>]*id=["']${escapeRegex(styleId)}["'][^>]*>[\\s\\S]*?<\\/style>`,

    "i"

  );

  if (regex.test(source)) {

    return source.replace(regex, block);

  }

  const insertIndex = source.indexOf(insertBeforeTag);

  if (insertIndex === -1) {

    throw new Error(`Insertion tag not found for style block: ${insertBeforeTag}`);

  }

  return source.slice(0, insertIndex) + block + "\n" + source.slice(insertIndex);

}

function extractFunctionNames(bundle) {

  const names = [];

  const regex = /(?:async\\s+)?function\\s+([A-Za-z0-9_$]+)\\s*\\(/g;

  let match;

  while ((match = regex.exec(bundle))) {

    names.push(match[1]);

  }

  return names;

}

function upsertFunctionBundle(source, bundle, insertBeforeName) {

  let nextSource = source;

  const names = extractFunctionNames(bundle);

  if (!names.length) {

    throw new Error("No functions found in bundle.");

  }

  for (let i = names.length - 1; i >= 0; i--) {

    const name = names[i];

    const range = findFunctionRange(bundle, name);

    if (!range) {

      throw new Error(`Could not isolate bundled function: ${name}`);

    }

    const fnSource = bundle.slice(range.start, range.end).trim();

    nextSource = upsertFunction(nextSource, name, fnSource, insertBeforeName);

  }

  return nextSource;

}

function main() {

  assertFileExists(TEMPLATE_PATH);

  let html = fs.readFileSync(TEMPLATE_PATH, "utf8");

  const TOKEN_RISK_POLISH_STYLE = `

#seoContent .story-stack{

  display:grid;

  gap:12px;

  margin-top:6px;

}

#seoContent .story-card{

  position:relative;

  overflow:hidden;

  border:1px solid rgba(255,255,255,.08);

  border-radius:20px;

  padding:16px 16px 14px;

  background:linear-gradient(180deg, rgba(255,255,255,.05) 0%, rgba(255,255,255,.02) 100%);

  box-shadow:0 10px 28px rgba(0,0,0,.16);

  transition:all .2s ease;

}

#seoContent .story-card:hover{

  transform:translateY(-2px);

  box-shadow:0 14px 34px rgba(0,0,0,.22);

}

#seoContent .story-card::before{

  content:"";

  position:absolute;

  top:0; left:0; right:0;

  height:1px;

  background:linear-gradient(90deg, rgba(159,203,255,.28), rgba(255,255,255,0));

}

#seoContent .story-card.lead{

  border-color:rgba(135,146,255,.34);

  background:linear-gradient(180deg, rgba(108,126,255,.18) 0%, rgba(255,255,255,.03) 100%);

}

#seoContent .story-card-title{

  display:flex;

  align-items:center;

  gap:10px;

  margin-bottom:10px;

  font-size:11px;

  letter-spacing:.18em;

  text-transform:uppercase;

  font-weight:800;

  color:#9fcbff;

}

#seoContent .story-card-list{

  list-style:none;

  padding:0;

  margin:0;

  display:grid;

  gap:8px;

}

#seoContent .story-card-item{

  position:relative;

  padding-left:14px;

  margin:0;

  font-size:14px;

  line-height:1.4;

  color:#e5eefc;

  font-weight:800;

}

#seoContent .story-card-item::before{

  content:"";

  position:absolute;

  left:0;

  top:.7em;

  width:6px;

  height:6px;

  border-radius:50%;

  background:rgba(159,203,255,.95);

  box-shadow:0 0 0 4px rgba(159,203,255,.10);

  transform:translateY(-50%);

}

`;

  const FINAL_POLISH_OVERRIDE = `function finalPolishLine(text, cardIndex) {

  let value = String(text || "")

    .replace(/\\s+/g, " ")

    .replace(/[,:;]+$/g, "")

    .trim();

  if (!value) return "";

  value = trimBulletHard(value, cardIndex === 3 ? 10 : 11);

  if (!value) return "";

  return value.charAt(0).toUpperCase() + value.slice(1);

}`;

  const LIMIT_CARD_ITEMS = `function buildSeoCardGroups(paragraphs) {

  const theme = detectTokenTheme(RAW_KEYWORD || "", paragraphs);

  const bulletPool = buildCardBulletPool(paragraphs, theme);

  const fallbackMap = buildDefaultTokenFallbacks(theme);

  const cards = [

    { titleIndex: 0, items: [], seenBuckets: new Set() },

    { titleIndex: 1, items: [], seenBuckets: new Set() },

    { titleIndex: 2, items: [], seenBuckets: new Set() },

    { titleIndex: 3, items: [], seenBuckets: new Set() }

  ];

  const globalSeen = new Set();

  function pushBullet(cardIndex, bullet) {

    if (!cards[cardIndex]) return false;

    const sourceText = typeof bullet === "string"

      ? bullet

      : (bullet.original || bullet.text || "");

    const themeName = typeof bullet === "string"

      ? classifyTokenBulletTheme(sourceText)

      : (bullet.theme || classifyTokenBulletTheme(sourceText));

    const bucket = typeof bullet === "string"

      ? bulletBucketKey(sourceText, themeName, cardIndex)

      : (bullet.bucket || bulletBucketKey(sourceText, themeName, cardIndex));

    const text = compressTokenBullet(sourceText, theme, cardIndex);

    const normalized = normalizeTokenBulletKey(text);

    if (!text || !normalized) return false;

    if (globalSeen.has(normalized)) return false;

    if (cards[cardIndex].seenBuckets.has(bucket)) return false;

    if (cards[cardIndex].items.length >= 3) return false;

    globalSeen.add(normalized);

    cards[cardIndex].seenBuckets.add(bucket);

    cards[cardIndex].items.push(text);

    return true;

  }

  for (const bullet of bulletPool) {

    pushBullet(bullet.cardIndex, bullet);

  }

  for (let i = 0; i < cards.length; i++) {

    const fallbacks = fallbackMap[i] || [];

    for (const fallback of fallbacks) {

      if (cards[i].items.length >= 2) break;

      pushBullet(i, fallback);

    }

  }

  return cards

    .map(card => ({

      titleIndex: card.titleIndex,

      items: card.items.slice(0, 3)

    }))

    .filter(card => card.items.length > 0);

}`;

  html = upsertStyleBlock(html, "token-risk-polish-style", TOKEN_RISK_POLISH_STYLE);

  html = upsertFunction(html, "finalPolishLine", FINAL_POLISH_OVERRIDE, "compressTokenBullet");

  html = upsertFunction(html, "buildSeoCardGroups", LIMIT_CARD_ITEMS, "renderSeoContentCards");

  ensureContains(html, "story-card", "card styling");

  ensureContains(html, "finalPolishLine", "bullet tightening");

  ensureContains(html, "buildSeoCardGroups", "card limiter");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");

  console.log("Refined.");

}

main();