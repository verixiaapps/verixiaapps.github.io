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
  gap:12px;
  margin-top:8px;
}
#seoContent .story-card{
  position:relative;
  overflow:hidden;
  border:1px solid rgba(255,255,255,.08);
  border-radius:20px;
  padding:16px 16px 14px;
  background:
    linear-gradient(180deg, rgba(255,255,255,.055) 0%, rgba(255,255,255,.022) 100%);
  box-shadow:0 10px 28px rgba(0,0,0,.16);
  transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease, background .18s ease;
}
#seoContent .story-card:hover{
  transform:translateY(-2px);
  box-shadow:0 14px 34px rgba(0,0,0,.22);
  border-color:rgba(159,203,255,.16);
}
#seoContent .story-card::before{
  content:"";
  position:absolute;
  top:0;
  left:0;
  right:0;
  height:1px;
  background:linear-gradient(90deg, rgba(159,203,255,.28), rgba(255,255,255,0));
}
#seoContent .story-card.lead{
  border-color:rgba(135,146,255,.34);
  background:
    linear-gradient(180deg, rgba(108,126,255,.19) 0%, rgba(255,255,255,.032) 100%);
  box-shadow:0 14px 34px rgba(0,0,0,.18);
}
#seoContent .story-card-title{
  display:flex;
  align-items:center;
  gap:10px;
  margin-bottom:10px;
  font-size:11px;
  letter-spacing:.18em;
  text-transform:uppercase;
  font-weight:850;
  color:#9fcbff;
}
#seoContent .story-card-title-icon{
  opacity:.95;
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
  line-height:1.38;
  color:#e8f0fc;
  font-weight:800;
  letter-spacing:-.01em;
}
#seoContent .story-card-item::before{
  content:"";
  position:absolute;
  left:0;
  top:.68em;
  width:6px;
  height:6px;
  border-radius:50%;
  background:rgba(159,203,255,.96);
  box-shadow:0 0 0 4px rgba(159,203,255,.10);
  transform:translateY(-50%);
}
#seoContent .story-card.lead .story-card-item::before{
  background:rgba(194,201,255,.98);
  box-shadow:0 0 0 4px rgba(167,177,255,.12);
}
@media (max-width:640px){
  #seoContent .story-stack{
    gap:10px;
    margin-top:6px;
  }
  #seoContent .story-card{
    padding:15px 15px 14px;
    border-radius:18px;
    transition:none;
  }
  #seoContent .story-card:hover{
    transform:none;
    box-shadow:0 10px 28px rgba(0,0,0,.16);
  }
  #seoContent .story-card-list{
    gap:8px;
  }
  #seoContent .story-card-item{
    font-size:14px;
    line-height:1.36;
    padding-left:14px;
  }
}
`;

  const FINAL_POLISH_OVERRIDE = `function finalPolishLine(text, cardIndex) {
  let value = String(text || "")
    .replace(/\\s+/g, " ")
    .replace(/[,:;]+$/g, "")
    .replace(/^and\\s+/i, "")
    .replace(/^but\\s+/i, "")
    .replace(/^so\\s+/i, "")
    .trim();

  if (!value) return "";

  value = trimBulletHard(value, cardIndex === 3 ? 10 : 11);

  if (!value) return "";

  value = value
    .replace(/\\bthe setup\\s+can\\s+/i, "The setup can ")
    .replace(/\\bthe setup\\s+usually\\s+/i, "The setup usually ")
    .replace(/\\s+/g, " ")
    .trim();

  if (!value) return "";

  return value.charAt(0).toUpperCase() + value.slice(1);
}`;

  const COMPRESS_TOKEN_BULLET_OVERRIDE = `function compressTokenBullet(text, theme, cardIndex) {
  const cleaned = cleanRewriteInput(stripSeoFiller(String(text || "")));
  if (!cleaned) return "";

  const bulletTheme = classifyTokenBulletTheme(cleaned);
  const resolvedCard = typeof cardIndex === "number" ? cardIndex : classifyCardIndex(cleaned, bulletTheme);
  const rewritten = buildMeaningRewrite(cleaned, bulletTheme || theme, resolvedCard) || cleaned;

  let value = finalPolishLine(rewritten, resolvedCard);

  if (!value) return "";

  value = value
    .replace(/\\bSurface confidence can hide weak structure\\./i, "Surface confidence can hide weak structure.")
    .replace(/\\bWeak structure breaks long before the story does\\./i, "Weak structure breaks before the story does.")
    .replace(/\\bExecution risk usually appears after entry\\./i, "Execution risk often appears after entry.")
    .replace(/\\bSlow down and verify the setup\\./i, "Slow down and verify the setup.")
    .trim();

  return value;
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

  const RENDER_SEO_CONTENT_CARDS_OVERRIDE = `function renderSeoContentCards(groups) {
  const seoContent = document.getElementById("seoContent");
  if (!seoContent) return;

  if (!groups.length) {
    seoContent.innerHTML = "";
    return;
  }

  const titles = buildSeoCardTitles(RAW_KEYWORD || "");

  seoContent.innerHTML = \`
    <div class="story-stack">
      \${groups.map((group) => {
        const titleIndex = group && typeof group.titleIndex === "number" ? group.titleIndex : 0;
        const items = Array.isArray(group && group.items) ? group.items.slice(0, 3) : [];
        const title = titles[titleIndex] || ["•", "More to know"];

        return \`
          <article class="story-card\${titleIndex === 0 ? " lead" : ""}">
            <div class="story-card-title">
              <span class="story-card-title-icon">\${title[0]}</span>
              <span>\${title[1]}</span>
            </div>
            <ul class="story-card-list">
              \${items.map(item => \`<li class="story-card-item">\${escapeHtml(item)}</li>\`).join("")}
            </ul>
          </article>
        \`;
      }).join("")}
    </div>
  \`;
}`;

  const APPLY_PREVIEW_CARD_OVERRIDE = `function applyPreviewCard() {
  const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
  const lower = keywordRaw.toLowerCase();
  const label = makeReadableCopyLabel(keywordRaw) || "Token Setup";

  const previewDomain = document.getElementById("previewDomain");
  const previewSub = document.getElementById("previewSub");
  const previewBadge = document.getElementById("previewBadge");
  const previewScore = document.getElementById("previewScore");
  const previewScoreFill = document.getElementById("previewScoreFill");
  const previewSignals = document.getElementById("previewSignals");

  if (!previewDomain || !previewSub || !previewBadge || !previewScore || !previewScoreFill || !previewSignals) {
    return;
  }

  let badge = "🔴 Example Token Risk";
  let score = "Pattern Review";
  let fillWidth = "24%";
  let sub = "Common structural warnings seen in risky token setups.";

  if (/(cannot sell|can't sell|honeypot|sell)/i.test(lower)) {
    badge = "🔴 Sell Lock Pattern";
    score = "Exit Risk: High";
    fillWidth = "14%";
    sub = "The entry can look normal right before exits break.";
  } else if (/(presale|fair launch|launch|airdrop)/i.test(lower)) {
    badge = "🔴 Launch Risk Pattern";
    score = "Review Pressure";
    fillWidth = "20%";
    sub = "Launch hype often arrives before real structure gets tested.";
  } else if (/(meme|memecoin|pump|moon|100x)/i.test(lower)) {
    badge = "🔴 Hype Pattern";
    score = "Noise vs Structure";
    fillWidth = "18%";
    sub = "Momentum can look strong while the setup underneath stays weak.";
  } else if (/(contract|address|pair|dexscreener)/i.test(lower)) {
    badge = "🔴 Structure Review";
    score = "Control Check";
    fillWidth = "22%";
    sub = "Surface data does not prove a safe contract or safe exit path.";
  }

  previewBadge.textContent = badge;
  previewScore.textContent = score;
  previewScoreFill.style.width = fillWidth;
  previewDomain.textContent = label;
  previewSub.textContent = sub;

  previewSignals.innerHTML = buildPreviewSignals(keywordRaw)
    .slice(0, 3)
    .map(signal => \`<div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>\${escapeHtml(signal)}</span></div>\`)
    .join("");
}`;

  html = upsertStyleBlock(html, "token-risk-polish-style", TOKEN_RISK_POLISH_STYLE);
  html = upsertFunction(html, "finalPolishLine", FINAL_POLISH_OVERRIDE, "compressTokenBullet");
  html = upsertFunction(html, "compressTokenBullet", COMPRESS_TOKEN_BULLET_OVERRIDE, "buildCardBulletPool");
  html = upsertFunction(html, "buildSeoCardGroups", LIMIT_CARD_ITEMS, "renderSeoContentCards");
  html = upsertFunction(html, "renderSeoContentCards", RENDER_SEO_CONTENT_CARDS_OVERRIDE, "cleanSeoContent");
  html = upsertFunction(html, "applyPreviewCard", APPLY_PREVIEW_CARD_OVERRIDE, "applyIntentToChecker");

  ensureContains(html, 'style id="token-risk-polish-style"', "polish style block");
  ensureContains(html, "function finalPolishLine(", "bullet tightening");
  ensureContains(html, "function compressTokenBullet(", "bullet compression override");
  ensureContains(html, "function buildSeoCardGroups(", "card limiter");
  ensureContains(html, "function renderSeoContentCards(", "card render override");
  ensureContains(html, "function applyPreviewCard(", "preview tighten override");
  ensureContains(html, "items.length >= 3", "3-item hard limit");
  ensureContains(html, "items.slice(0, 3)", "3-item output limit");
  ensureContains(html, "slice(0, 3)", "preview signal limit");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");
  console.log("Additional premium card refinements applied.");
}

main();