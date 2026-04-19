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
  margin-top:6px;
}
#seoContent .story-card{
  position:relative;
  overflow:hidden;
  border:1px solid rgba(255,255,255,.08);
  border-radius:20px;
  padding:17px 17px 15px;
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
#seoContent .story-card-list{
  list-style:none;
  padding:0;
  margin:0;
  display:grid;
  gap:9px;
}
#seoContent .story-card-item{
  position:relative;
  padding-left:15px;
  margin:0;
  font-size:15px;
  line-height:1.58;
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
#seoContent .story-card.lead .story-card-item::before{
  background:rgba(194,201,255,.98);
  box-shadow:0 0 0 4px rgba(167,177,255,.12);
}
@media (max-width:640px){
  #seoContent .story-stack{ gap:10px; }
  #seoContent .story-card{ padding:15px 15px 14px; border-radius:18px; }
  #seoContent .story-card-list{ gap:8px; }
  #seoContent .story-card-item{
    font-size:14px;
    line-height:1.52;
    padding-left:14px;
  }
}
`;

  const COMPRESS_TOKEN_BULLET_FUNCTION = `function compressTokenBullet(text, theme, cardIndex) {
  let value = String(text || "")
    .replace(/\\s+/g, " ")
    .replace(/^[\\-•]\\s*/, "")
    .trim();

  if (!value) return "";

  value = stripSeoFiller(value)
    .replace(/\\bthis means\\b/gi, "")
    .replace(/\\bthis can mean\\b/gi, "")
    .replace(/\\bthis matters because\\b/gi, "")
    .replace(/\\bit is important to\\b/gi, "")
    .replace(/\\bit is worth noting that\\b/gi, "")
    .replace(/\\bin many cases\\b/gi, "")
    .replace(/\\bin some cases\\b/gi, "")
    .replace(/\\btokens can\\b/gi, "")
    .replace(/\\ba token can\\b/gi, "")
    .replace(/\\bprojects can\\b/gi, "")
    .replace(/\\bthere is a risk that\\b/gi, "")
    .replace(/\\bthis token\\b/gi, "The setup")
    .replace(/\\bthe token\\b/gi, "The setup")
    .replace(/\\bthe project\\b/gi, "The setup")
    .replace(/\\busers\\b/gi, "buyers")
    .replace(/\\s+/g, " ")
    .trim();

  value = value
    .replace(/^because\\s+/i, "")
    .replace(/^and\\s+/i, "")
    .replace(/^but\\s+/i, "")
    .replace(/^so\\s+/i, "")
    .replace(/^while\\s+/i, "")
    .replace(/^if\\s+/i, "")
    .replace(/^when\\s+/i, "")
    .replace(/^there are\\s+/i, "")
    .replace(/^there is\\s+/i, "")
    .trim();

  if (!value) return "";

  value = value.charAt(0).toUpperCase() + value.slice(1);

  const rewrites = [
    {
      test: /(urgent|urgency|rush|fomo|pressure|countdown|whitelist|early access)/i,
      value: "Urgency shows up before the setup is fully verified."
    },
    {
      test: /(liquidity|pool|lp|locked)/i,
      value: "Liquidity can look fine until exits matter more than entries."
    },
    {
      test: /(holder|holders|wallet|wallets|distribution|concentration)/i,
      value: "Holder concentration can change the risk fast once momentum fades."
    },
    {
      test: /(sell|selling|exit|honeypot|swap|approve|approval|permissions)/i,
      value: "Buying may feel easier than selling once the contract starts limiting exits."
    },
    {
      test: /(price|volume|chart|pump|moon|spike|trend)/i,
      value: "Fast chart movement can hide weak structure underneath."
    },
    {
      test: /(social|viral|telegram|x post|thread|community|influencer|hype)/i,
      value: "Social proof can feel stronger than the underlying proof."
    },
    {
      test: /(contract|mint|owner|ownership|blacklist|tax|function)/i,
      value: "Contract controls matter more than branding once money is committed."
    }
  ];

  for (const rule of rewrites) {
    if (rule.test.test(value)) {
      value = rule.value;
      break;
    }
  }

  value = value
    .replace(/[,:;]\\s*$/, "")
    .replace(/\\.{2,}/g, ".")
    .trim();

  if (!value) return "";

  const maxLen = cardIndex === 3 ? 92 : 88;
  if (value.length > maxLen) {
    value = value.slice(0, maxLen).replace(/[,:;\\s]+[^\\s]*$/, "").trim();
  }

  value = value.replace(/[,:;\\s]+$/g, "").trim();

  if (!/[.!?]$/.test(value)) {
    value += ".";
  }

  return value;
}`;

  const BUILD_CARD_BULLET_POOL_FUNCTION = `function buildCardBulletPool(paragraphs, theme) {
  const sourceMaterial = buildSourceMaterial(paragraphs);

  const candidateLines = sourceMaterial
    .flatMap(breakParagraphIntoSentences)
    .map(normalizeSeoSentence)
    .filter(Boolean)
    .filter(s => !containsKeywordLeak(s))
    .filter(s => !isTooGenericSentence(s))
    .map(s => compressTokenBullet(s, theme, 1))
    .filter(Boolean);

  const seen = new Set();
  const unique = [];

  for (const line of candidateLines) {
    const key = line.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    unique.push(line);
  }

  return unique;
}`;

  const BUILD_SEO_CARD_GROUPS_FUNCTION = `function buildSeoCardGroups(paragraphs) {
  const theme = detectTokenTheme(RAW_KEYWORD || "", paragraphs);
  const bulletPool = buildCardBulletPool(paragraphs, theme);

  if (!bulletPool.length) {
    return [];
  }

  const cards = [
    { titleIndex: 0, items: [] },
    { titleIndex: 1, items: [] },
    { titleIndex: 2, items: [] },
    { titleIndex: 3, items: [] }
  ];

  const globalSeen = new Set();
  const overflow = [];

  function keyFor(text) {
    return String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  }

  function pushBullet(cardIndex, text) {
    const cleaned = compressTokenBullet(text, theme, cardIndex);
    const key = keyFor(cleaned);

    if (!cleaned || !key) return false;
    if (globalSeen.has(key)) return false;
    if (!cards[cardIndex] || cards[cardIndex].items.length >= 4) return false;

    globalSeen.add(key);
    cards[cardIndex].items.push(cleaned);
    return true;
  }

  function classifyCardIndex(text) {
    const lower = String(text || "").toLowerCase();

    if (/(check|verify|confirm|review|look for|watch for|make sure)/i.test(lower)) {
      return 3;
    }

    if (/(urgent|urgency|rush|fomo|pressure|countdown|whitelist|early access|viral|hype|social|thread|telegram|x post|community|influencer)/i.test(lower)) {
      return 0;
    }

    if (/(liquidity|pool|lp|locked|holder|holders|wallet|wallets|distribution|concentration|contract|mint|owner|ownership|blacklist|tax|function)/i.test(lower)) {
      return 1;
    }

    if (/(sell|selling|exit|honeypot|swap|approve|approval|permissions|price|volume|chart|pump|moon|spike|trend)/i.test(lower)) {
      return 2;
    }

    return 2;
  }

  for (const line of bulletPool) {
    const targetIndex = classifyCardIndex(line);
    if (!pushBullet(targetIndex, line)) {
      const cleaned = compressTokenBullet(line, theme, targetIndex);
      const key = keyFor(cleaned);
      if (cleaned && key && !globalSeen.has(key)) {
        overflow.push(line);
      }
    }
  }

  for (const line of overflow) {
    const nextCard = cards
      .filter(card => card.items.length < 4)
      .sort((a, b) => a.items.length - b.items.length)[0];

    if (!nextCard) break;
    pushBullet(nextCard.titleIndex, line);
  }

  return cards
    .filter(card => card.items.length > 0)
    .map(card => ({
      titleIndex: card.titleIndex,
      items: card.items.slice(0, 4)
    }));
}`;

  const RENDER_SEO_CONTENT_CARDS_FUNCTION = `function renderSeoContentCards(groups) {
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
        const items = Array.isArray(group && group.items) ? group.items : (Array.isArray(group) ? group : []);
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

  html = upsertStyleBlock(html, "token-risk-polish-style", TOKEN_RISK_POLISH_STYLE);
  html = upsertFunction(html, "compressTokenBullet", COMPRESS_TOKEN_BULLET_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "buildCardBulletPool", BUILD_CARD_BULLET_POOL_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "buildSeoCardGroups", BUILD_SEO_CARD_GROUPS_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "renderSeoContentCards", RENDER_SEO_CONTENT_CARDS_FUNCTION, "cleanSeoContent");

  ensureContains(html, "compressTokenBullet", "bullet compressor");
  ensureContains(html, "buildCardBulletPool", "bullet pool builder");
  ensureContains(html, "buildSeoCardGroups", "seo card grouping");
  ensureContains(html, "renderSeoContentCards", "seo card renderer");
  ensureContains(html, 'style id="token-risk-polish-style"', "style block");
  ensureContains(html, "story-card-list", "bullet card list class");
  ensureContains(html, "story-card-item", "bullet card item class");
  ensureContains(html, "titleIndex", "title index preservation");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");
  console.log("Perfected.");
}

main();