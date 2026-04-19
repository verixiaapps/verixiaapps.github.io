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

function main() {
  assertFileExists(TEMPLATE_PATH);

  let html = fs.readFileSync(TEMPLATE_PATH, "utf8");

  const TOKEN_RISK_POLISH_STYLE = `
#seoContent .story-stack{
  display:grid;
  gap:14px;
  margin-top:10px;
}
#seoContent .story-card{
  position:relative;
  overflow:hidden;
  border:1px solid rgba(255,255,255,.08);
  border-radius:20px;
  padding:18px 18px 16px;
  background:linear-gradient(180deg, rgba(255,255,255,.045) 0%, rgba(255,255,255,.02) 100%);
  box-shadow:0 12px 30px rgba(0,0,0,.14);
}
#seoContent .story-card::before{
  content:"";
  position:absolute;
  top:0; left:0; right:0;
  height:1px;
  background:linear-gradient(90deg, rgba(159,203,255,.24), rgba(255,255,255,0));
}
#seoContent .story-card.lead{
  border-color:rgba(135,146,255,.28);
  background:linear-gradient(180deg, rgba(108,126,255,.16) 0%, rgba(255,255,255,.03) 100%);
  box-shadow:0 16px 36px rgba(0,0,0,.18);
}
#seoContent .story-card-title{
  display:flex;
  align-items:center;
  gap:10px;
  margin-bottom:10px;
  font-size:12px;
  letter-spacing:.18em;
  text-transform:uppercase;
  font-weight:800;
  color:#9fcbff;
}
#seoContent .story-card p{
  margin:0;
  font-size:16px;
  line-height:1.72;
  color:#e5eefc;
}
`;

  const BUILD_SEO_CARD_GROUPS_FUNCTION = `function buildSeoCardGroups(paragraphs) {
  const theme = detectTokenTheme(RAW_KEYWORD || "", paragraphs);
  const sourceMaterial = buildSourceMaterial(paragraphs);

  const candidates = sourceMaterial
    .map(normalizeSeoSentence)
    .filter(Boolean)
    .filter(s => !containsKeywordLeak(s))
    .filter(s => !isTooGenericSentence(s))
    .map(s => ({ text: s, score: scoreTokenSentence(s) }))
    .sort((a, b) => b.score - a.score);

  const ranked = [];
  const seen = new Set();

  for (const item of candidates) {
    const key = item.text.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    ranked.push(item.text);
  }

  const material = ranked.length
    ? ranked
    : sourceMaterial.length
      ? sourceMaterial
      : [String(RAW_KEYWORD || "token risk")];

  const cards = [];
  const cardSeen = new Set();

  function tryPush(text) {
    const cleaned = String(text || "").replace(/\\s+/g, " ").trim();
    const key = cleaned.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
    if (!key || cardSeen.has(key)) return false;
    cardSeen.add(key);
    cards.push(cleaned);
    return true;
  }

  for (let i = 0; i < 4; i++) {
    const primary = getSourceTextForCard(material, i);
    if (tryPush(rewriteTokenSentence(primary, theme, i))) continue;

    const reversed = getSourceTextForCard(material.slice().reverse(), i);
    if (tryPush(rewriteTokenSentence(reversed, theme, i))) continue;

    tryPush(rewriteTokenSentence(material.join(" "), theme, i));
  }

  const hardFallbacks = [
    "Price movement alone is not enough to trust a token, because structure matters more than momentum once money is on the line.",
    "The strongest token checks focus on whether buying, selling, and swapping all work normally without hidden friction or weak support.",
    "When liquidity is thin or ownership is concentrated, fast chart movement can create a false sense of safety that disappears on exit.",
    "Verify contract behavior, liquidity support, holder distribution, and exit conditions before treating the token as lower risk."
  ];

  for (const f of hardFallbacks) {
    if (cards.length >= 4) break;
    tryPush(f);
  }

  return cards.slice(0, 4);
}`;

  html = upsertStyleBlock(html, "token-risk-polish-style", TOKEN_RISK_POLISH_STYLE);
  html = upsertFunction(html, "buildSeoCardGroups", BUILD_SEO_CARD_GROUPS_FUNCTION, "cleanSeoContent");

  ensureContains(html, "buildSeoCardGroups", "seo card grouping");
  ensureContains(html, 'style id="token-risk-polish-style"', "style block");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");
  console.log("Perfected.");
}

main();