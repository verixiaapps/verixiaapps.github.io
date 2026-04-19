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
  top:0;
  left:0;
  right:0;
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
  line-height:1.2;
  letter-spacing:.18em;
  text-transform:uppercase;
  font-weight:800;
  color:#9fcbff;
}

#seoContent .story-card-title-icon{
  font-size:14px;
  line-height:1;
}

#seoContent .story-card p{
  margin:0;
  font-size:16px;
  line-height:1.72;
  color:#e5eefc;
}

@media (max-width:640px){
  #seoContent .story-card{
    padding:16px 16px 15px;
    border-radius:18px;
  }

  #seoContent .story-card p{
    font-size:15px;
    line-height:1.68;
  }
}
`;

  const SPLIT_SEO_PARAGRAPHS_FROM_HTML_FUNCTION = `function splitSeoParagraphsFromHtml(seoContent) {
  const html = String(seoContent.innerHTML || "").trim();
  if (!html) return [];

  const parser = document.createElement("div");
  parser.innerHTML = html;

  let paragraphs = Array.from(parser.querySelectorAll("p, li"))
    .map(node => node.textContent.trim())
    .filter(Boolean);

  if (paragraphs.length) return paragraphs;

  return parser.innerHTML
    .replace(/<br\\s*\\/?>/gi, "\\n")
    .replace(/<\\/p>/gi, "\\n\\n")
    .replace(/<\\/div>/gi, "\\n\\n")
    .replace(/<\\/section>/gi, "\\n\\n")
    .replace(/<li>/gi, "\\n• ")
    .replace(/<\\/li>/gi, "")
    .replace(/<[^>]+>/g, "")
    .split(/\\n\\s*\\n|\\n(?=•)/)
    .map(p => p.replace(/\\s+/g, " ").trim())
    .filter(Boolean);
}`;

  const STRIP_SEO_FILLER_FUNCTION = `function stripSeoFiller(text) {
  return String(text || "")
    .replace(/\\*\\*/g, "")
    .replace(/\\b(it is important to note that|it is worth noting that|in many cases|in some cases|in a lot of cases|generally speaking|in general)\\b/gi, "")
    .replace(/\\b(this is because|the reason for this is that)\\b/gi, "because")
    .replace(/\\b(as always|of course|basically|simply put|put simply|at the end of the day|when it comes to this)\\b/gi, "")
    .replace(/\\b(keep in mind that|make sure to|it can be helpful to|it helps to)\\b/gi, "")
    .replace(/\\b(looks legit|seems legit)\\b/gi, "looks safer than it may be")
    .replace(/\\s+/g, " ")
    .replace(/\\s+([,.;!?])/g, "$1")
    .trim();
}`;

  const NORMALIZE_SEO_SENTENCE_FUNCTION = `function normalizeSeoSentence(sentence) {
  return stripSeoFiller(sentence)
    .replace(/^[-•]\\s*/, "")
    .replace(/^[,:;]+\\s*/, "")
    .replace(/\\.{2,}/g, ".")
    .replace(/\\s+/g, " ")
    .trim();
}`;

  const BREAK_PARAGRAPH_INTO_SENTENCES_FUNCTION = `function breakParagraphIntoSentences(paragraph) {
  return String(paragraph || "")
    .replace(/\\s+/g, " ")
    .split(/(?<=[.!?])\\s+/)
    .map(normalizeSeoSentence)
    .filter(Boolean);
}`;

  const CONTAINS_KEYWORD_LEAK_FUNCTION = `function containsKeywordLeak(sentence) {
  const keyword = String(RAW_KEYWORD || "")
    .toLowerCase()
    .replace(/\\s+/g, " ")
    .trim();

  if (!keyword) return false;

  const lower = String(sentence || "")
    .toLowerCase()
    .replace(/\\s+/g, " ")
    .trim();

  if (!lower || !lower.includes(keyword)) return false;

  const cleanKeyword = keyword.replace(/[^a-z0-9]+/g, " ").trim();
  const cleanSentence = lower.replace(/[^a-z0-9]+/g, " ").trim();

  if (!cleanKeyword || cleanSentence === cleanKeyword) return false;
  if (cleanSentence.startsWith(cleanKeyword + " ")) return true;
  if (cleanSentence.includes(" " + cleanKeyword + " ")) return true;

  return lower.length > keyword.length + 18;
}`;

  const IS_TOO_GENERIC_SENTENCE_FUNCTION = `function isTooGenericSentence(sentence) {
  const lower = String(sentence || "").toLowerCase().trim();

  if (!lower) return true;
  if (lower.length < 28) return true;

  const genericStarts = [
    "this means",
    "this can mean",
    "this is why",
    "this is because",
    "it is important",
    "it is worth",
    "there are many",
    "one thing to remember",
    "in many cases",
    "in some cases",
    "generally speaking",
    "in general"
  ];

  const genericPhrases = [
    "what stands out first",
    "what deserves a deeper check",
    "where people get caught",
    "what to verify next",
    "looks normal until",
    "feels believable",
    "narrative alone",
    "structure supports",
    "social excitement",
    "setup looks stronger"
  ];

  if (genericStarts.some(start => lower.startsWith(start))) return true;
  if (genericPhrases.some(phrase => lower.includes(phrase))) return true;

  return false;
}`;

  const DETECT_TOKEN_THEME_FUNCTION = `function detectTokenTheme(keywordRaw, paragraphs) {
  const haystack = [String(keywordRaw || ""), ...(paragraphs || [])]
    .join(" ")
    .toLowerCase();

  if (/honeypot|can't sell|cant sell|cannot sell|sell blocked|sell tax|swap fails|can't swap|cant swap/.test(haystack)) {
    return "honeypot";
  }

  if (/liquidity|thin liquidity|low liquidity|market depth|slippage/.test(haystack)) {
    return "liquidity";
  }

  if (/holder|holders|wallet|wallets|distribution|concentration|top wallet/.test(haystack)) {
    return "holders";
  }

  if (/approval|approve|permission|allowance|spender/.test(haystack)) {
    return "approvals";
  }

  if (/presale|launch|airdrop|fair launch|new token|fresh launch/.test(haystack)) {
    return "launch";
  }

  return "token";
}`;

  const SCORE_TOKEN_SENTENCE_FUNCTION = `function scoreTokenSentence(sentence) {
  const lower = String(sentence || "").toLowerCase();
  let score = 0;

  const strongSignals = [
    "liquidity","holder","holders","wallet","wallets","distribution","concentration",
    "volume","slippage","exit","sell","swap","buy","contract","permission",
    "approval","honeypot","market depth","trading","pair","bridge","market cap",
    "locked","unlocked","tax"
  ];

  const dangerSignals = [
    "risk","warning","red flag","collapse","fails","thin","drain","rug","dump",
    "stuck","blocked","freeze","unsafe","danger"
  ];

  const actionSignals = [
    "check","review","verify","confirm","watch","treat","avoid","compare"
  ];

  strongSignals.forEach(signal => {
    if (lower.includes(signal)) score += 2;
  });

  dangerSignals.forEach(signal => {
    if (lower.includes(signal)) score += 2;
  });

  actionSignals.forEach(signal => {
    if (lower.includes(signal)) score += 1;
  });

  if (lower.length >= 70) score += 1;
  if (lower.length >= 110) score += 1;
  if (/\\d/.test(lower)) score += 1;
  if (/(before|when|if)\\b/.test(lower)) score += 1;

  return score;
}`;

  const BUILD_SOURCE_MATERIAL_FUNCTION = `function buildSourceMaterial(paragraphs) {
  const directSentences = paragraphs
    .flatMap(breakParagraphIntoSentences)
    .map(normalizeSeoSentence)
    .filter(Boolean);

  const paragraphUnits = paragraphs
    .map(normalizeSeoSentence)
    .filter(Boolean);

  const fragments = [];
  const seen = new Set();

  function pushUnique(text) {
    const cleaned = normalizeSeoSentence(text);
    const key = cleaned.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
    if (!cleaned || !key || seen.has(key)) return;
    seen.add(key);
    fragments.push(cleaned);
  }

  directSentences.forEach(pushUnique);
  paragraphUnits.forEach(pushUnique);

  if (!fragments.length) {
    const joined = paragraphUnits.join(" ").trim();
    if (joined) pushUnique(joined);
  }

  return fragments;
}`;

  const GET_SOURCE_TEXT_FOR_CARD_FUNCTION = `function getSourceTextForCard(material, index) {
  if (!material.length) return "";
  if (material[index]) return material[index];

  const joined = material.join(" ").trim();
  if (!joined) return material[index % material.length];

  if (index === 0) return material[0];
  if (index === 1) return material[Math.min(1, material.length - 1)] || joined;
  if (index === 2) return joined;
  if (index === 3) {
    return material.length > 1
      ? material.slice().reverse().join(" ")
      : joined;
  }

  return joined;
}`;

  const REWRITE_TOKEN_SENTENCE_FUNCTION = `function rewriteTokenSentence(sourceText, theme, index) {
  const text = normalizeSeoSentence(sourceText);
  const lower = text.toLowerCase();

  const mentionsLiquidity = /liquidity|slippage|market depth|volume|pair/.test(lower);
  const mentionsHolders = /holder|holders|wallet|wallets|distribution|concentration|top wallet/.test(lower);
  const mentionsContract = /contract|permission|approval|allowance|spender|tax/.test(lower);
  const mentionsSell = /sell|swap|exit|blocked|stuck|fails|cannot sell|can't sell|cant sell/.test(lower);
  const mentionsLaunch = /launch|presale|airdrop|fresh launch|new token/.test(lower);

  if (theme === "liquidity") {
    if (index === 0) {
      return "Low liquidity can make a token look active while still leaving weak market depth and unreliable exits once selling starts.";
    }
    if (index === 1) {
      return "When liquidity stays thin, even modest selling can create sharp slippage, unstable pricing, or exits that feel worse than the chart suggests.";
    }
    if (index === 2) {
      return mentionsHolders
        ? "Liquidity looks even weaker when too few wallets control supply, because concentrated ownership can break support faster under pressure."
        : "Compare liquidity, volume, and trading depth together, because fast price movement alone can hide a fragile setup.";
    }
    return mentionsContract
      ? "Thin liquidity becomes more dangerous when contract controls are unclear, so verify both exit conditions and token permissions before acting."
      : "Verify real liquidity support and market depth before treating the token as easier to buy or safer to exit.";
  }

  if (theme === "honeypot") {
    if (index === 0) {
      return "A token can feel easy to buy while contract behavior quietly makes selling harder, more expensive, or impossible once funds are in.";
    }
    if (index === 1) {
      return mentionsContract
        ? "That makes contract permissions more important than hype, because the real test is whether the token behaves normally when you try to exit."
        : "Exit risk matters more than entry momentum, because the real test is whether selling and swapping still work without hidden friction.";
    }
    if (index === 2) {
      return mentionsSell
        ? "If selling stalls, fails, or behaves differently than buying, treat the setup as a serious risk even when the chart still looks active."
        : "Watch for tokens where buying feels smooth but exit behavior is inconsistent, because that gap is often where traders get trapped.";
    }
    return "Review sell behavior, swap outcomes, and contract controls before assuming the token is tradable in both directions.";
  }

  if (theme === "holders") {
    if (index === 0) {
      return "A token can show activity while still depending on a small number of wallets that control too much supply or too much exit pressure.";
    }
    if (index === 1) {
      return "Heavy holder concentration raises the chance of sudden dumps, weaker support, and price action that does not reflect broad demand.";
    }
    if (index === 2) {
      return mentionsLiquidity
        ? "Holder concentration becomes even riskier when liquidity is thin, because a few wallets can move price faster than most buyers expect."
        : "Check top-wallet distribution before trusting momentum, because concentrated ownership can distort both support and exit conditions.";
    }
    return "Verify how supply is distributed across wallets before treating short-term price movement as proof of token strength.";
  }

  if (theme === "approvals") {
    if (index === 0) {
      return "Approval risk is easy to miss because the interface can look normal while the contract still asks for wallet access that deserves a closer review.";
    }
    if (index === 1) {
      return "Before signing, verify what the approval allows, whether permissions can be abused, and whether contract behavior matches the token’s pitch.";
    }
    if (index === 2) {
      return mentionsContract
        ? "A token does not need to drain funds directly to be dangerous, because unclear permissions and contract controls can still create fast exposure."
        : "Risk increases when approvals are broad but the token’s behavior is not transparent, especially if contract rules are hard to verify.";
    }
    return "Review approval scope, spender permissions, and contract behavior before giving the token access to your wallet.";
  }

  if (theme === "launch") {
    if (index === 0) {
      return "Early launch excitement can hide weak liquidity, concentrated holders, or contract risks that only become obvious after buyers are already in.";
    }
    if (index === 1) {
      return "A new token deserves extra caution when urgency is high, because early volume does not always mean the setup is stable or easy to exit.";
    }
    if (index === 2) {
      return mentionsLiquidity || mentionsHolders || mentionsContract
        ? "Launch momentum matters less than structure, so check liquidity, wallet distribution, and contract behavior before trusting the first wave of demand."
        : "Fast early attention can create false confidence, especially when token structure has not been verified beyond the initial chart move.";
    }
    return "Verify launch structure, token distribution, and exit conditions before committing funds on early momentum alone.";
  }

  if (index === 0) {
    return mentionsLiquidity
      ? "Liquidity deserves more attention than the chart, because weak depth can turn normal-looking activity into difficult exits very quickly."
      : "Price movement alone is not enough to trust a token, because structure matters more than momentum once money is on the line.";
  }

  if (index === 1) {
    return mentionsHolders
      ? "Holder distribution affects real risk more than short-term excitement, because concentrated ownership can change support and sell pressure fast."
      : "The strongest token checks focus on whether buying, selling, and swapping all work normally without hidden friction or weak support.";
  }

  if (index === 2) {
    return mentionsContract || mentionsSell
      ? "Contract behavior should confirm what the page promises, because unclear permissions or weak exit behavior can matter more than price action."
      : "When liquidity is thin or ownership is concentrated, fast chart movement can create a false sense of safety that disappears on exit.";
  }

  return "Verify contract behavior, liquidity support, holder distribution, and exit conditions before treating the token as lower risk.";
}`;

  const BUILD_SEO_CARD_GROUPS_FUNCTION = `function buildSeoCardGroups(paragraphs) {
  const theme = detectTokenTheme(RAW_KEYWORD || "", paragraphs);
  const sourceMaterial = buildSourceMaterial(paragraphs);

  const candidates = sourceMaterial
    .map(normalizeSeoSentence)
    .filter(Boolean)
    .filter(sentence => !containsKeywordLeak(sentence))
    .filter(sentence => !isTooGenericSentence(sentence))
    .map(sentence => ({
      text: sentence,
      score: scoreTokenSentence(sentence)
    }))
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
      : paragraphs.map(normalizeSeoSentence).filter(Boolean);

  if (!material.length) return [];

  const cards = [];
  const cardSeen = new Set();

  for (let i = 0; i < 4; i++) {
    const source = getSourceTextForCard(material, i);
    const rewritten = rewriteTokenSentence(source, theme, i)
      .replace(/\\s+/g, " ")
      .trim();

    let finalText = rewritten;
    let key = finalText.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

    if (!key || cardSeen.has(key)) {
      const alternateSource = getSourceTextForCard(material.slice().reverse(), i);
      finalText = rewriteTokenSentence(alternateSource, theme, i)
        .replace(/\\s+/g, " ")
        .trim();
      key = finalText.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
    }

    if (!key || cardSeen.has(key)) {
      finalText = rewriteTokenSentence(material.join(" "), theme, i)
        .replace(/\\s+/g, " ")
        .trim();
      key = finalText.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
    }

    if (!key || cardSeen.has(key)) continue;

    cardSeen.add(key);
    cards.push(finalText);
  }

  return cards.slice(0, 4);
}`;

  const BUILD_SEO_CARD_TITLES_FUNCTION = `function buildSeoCardTitles(keywordRaw, paragraphs) {
  const theme = detectTokenTheme(keywordRaw, paragraphs);

  if (theme === "liquidity") {
    return [
      ["💧", "Why liquidity can look safer than it is"],
      ["📉", "What starts breaking first"],
      ["⚠️", "Where exits become the real risk"],
      ["🔍", "What to verify before buying"]
    ];
  }

  if (theme === "honeypot") {
    return [
      ["🚪", "Why entry can look easier than exit"],
      ["🧾", "What the contract may be controlling"],
      ["⚠️", "Where traders get trapped"],
      ["🔍", "What to confirm before acting"]
    ];
  }

  if (theme === "holders") {
    return [
      ["👥", "Why distribution matters more than hype"],
      ["🧱", "What concentration can break"],
      ["⚠️", "Where sell pressure shows up"],
      ["🔍", "What to verify before trusting momentum"]
    ];
  }

  if (theme === "approvals") {
    return [
      ["🔐", "Why approvals deserve a closer look"],
      ["🧾", "What the contract may still control"],
      ["⚠️", "Where wallet risk starts"],
      ["🔍", "What to verify before signing"]
    ];
  }

  if (theme === "launch") {
    return [
      ["🚀", "Why early momentum can mislead"],
      ["🧱", "What buyers often fail to review"],
      ["⚠️", "Where launch risk gets expensive"],
      ["🔍", "What to confirm before committing"]
    ];
  }

  return [
    ["🧾", "What the token setup shows"],
    ["🧱", "What needs verification"],
    ["⚠️", "Where the risk appears"],
    ["🔍", "What to check before acting"]
  ];
}`;

  const RENDER_SEO_CONTENT_CARDS_FUNCTION = `function renderSeoContentCards(groups, paragraphs) {
  const seoContent = document.getElementById("seoContent");
  if (!seoContent) return;

  if (!groups.length) {
    seoContent.innerHTML = "";
    return;
  }

  const titles = buildSeoCardTitles(RAW_KEYWORD || "", paragraphs || []);

  seoContent.innerHTML = \`
    <div class="story-stack">
      \${groups.map((group, index) => \`
        <article class="story-card\${index === 0 ? " lead" : ""}">
          <div class="story-card-title">
            <span class="story-card-title-icon">\${titles[index][0]}</span>
            <span>\${titles[index][1]}</span>
          </div>
          <p>\${escapeHtml(group)}</p>
        </article>
      \`).join("")}
    </div>
  \`;
}`;

  const CLEAN_SEO_CONTENT_FUNCTION = `function cleanSeoContent() {
  const seoContent = document.getElementById("seoContent");
  if (!seoContent) return;

  seoContent.innerHTML = seoContent.innerHTML
    .replace(/\\*\\*/g, "")
    .replace(/<p>\\s*<\\/p>/g, "")
    .trim();

  const paragraphs = splitSeoParagraphsFromHtml(seoContent)
    .map(stripSeoFiller)
    .map(p => p.replace(/\\s+/g, " ").trim())
    .filter(Boolean);

  const groups = buildSeoCardGroups(paragraphs);
  renderSeoContentCards(groups, paragraphs);
}`;

  html = upsertStyleBlock(html, "token-risk-polish-style", TOKEN_RISK_POLISH_STYLE);

  html = upsertFunction(
    html,
    "splitSeoParagraphsFromHtml",
    SPLIT_SEO_PARAGRAPHS_FROM_HTML_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "stripSeoFiller",
    STRIP_SEO_FILLER_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "normalizeSeoSentence",
    NORMALIZE_SEO_SENTENCE_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "breakParagraphIntoSentences",
    BREAK_PARAGRAPH_INTO_SENTENCES_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "containsKeywordLeak",
    CONTAINS_KEYWORD_LEAK_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "isTooGenericSentence",
    IS_TOO_GENERIC_SENTENCE_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "detectTokenTheme",
    DETECT_TOKEN_THEME_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "scoreTokenSentence",
    SCORE_TOKEN_SENTENCE_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "buildSourceMaterial",
    BUILD_SOURCE_MATERIAL_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "getSourceTextForCard",
    GET_SOURCE_TEXT_FOR_CARD_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "rewriteTokenSentence",
    REWRITE_TOKEN_SENTENCE_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "buildSeoCardGroups",
    BUILD_SEO_CARD_GROUPS_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "buildSeoCardTitles",
    BUILD_SEO_CARD_TITLES_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "renderSeoContentCards",
    RENDER_SEO_CONTENT_CARDS_FUNCTION,
    "cleanSeoContent"
  );

  html = upsertFunction(
    html,
    "cleanSeoContent",
    CLEAN_SEO_CONTENT_FUNCTION,
    "cleanRelatedLinks"
  );

  ensureContains(html, "function splitSeoParagraphsFromHtml(seoContent)", "seo paragraph splitter");
  ensureContains(html, "function stripSeoFiller(text)", "seo filler stripper");
  ensureContains(html, "function normalizeSeoSentence(sentence)", "seo sentence normalizer");
  ensureContains(html, "function breakParagraphIntoSentences(paragraph)", "seo sentence splitter");
  ensureContains(html, "function containsKeywordLeak(sentence)", "keyword leak filter");
  ensureContains(html, "function isTooGenericSentence(sentence)", "generic sentence filter");
  ensureContains(html, "function detectTokenTheme(keywordRaw, paragraphs)", "theme detector");
  ensureContains(html, "function scoreTokenSentence(sentence)", "sentence scorer");
  ensureContains(html, "function buildSourceMaterial(paragraphs)", "source material builder");
  ensureContains(html, "function getSourceTextForCard(material, index)", "card source selector");
  ensureContains(html, "function rewriteTokenSentence(sourceText, theme, index)", "sentence rewriter");
  ensureContains(html, "function buildSeoCardGroups(paragraphs)", "seo card grouping");
  ensureContains(html, "function buildSeoCardTitles(keywordRaw, paragraphs)", "seo card titles");
  ensureContains(html, "function renderSeoContentCards(groups, paragraphs)", "seo card renderer");
  ensureContains(html, "function cleanSeoContent()", "seo content cleanup");
  ensureContains(html, 'style id="token-risk-polish-style"', "token polish style block");

  ensureContains(html, 'fetch(API + "/analyze-token"', "checker endpoint preserved");
  ensureContains(html, "function formatTokenResult(data)", "checker formatter preserved");
  ensureContains(html, 'style id="token-risk-analysis-style"', "checker analysis style preserved");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");
  console.log(`Template updated: ${TEMPLATE_PATH}`);
}

main();