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
  const startRegex = new RegExp(`(?:async\\s+)?function\s+${escapedName}\\s*\\(`);
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
  const regex = /(?:async\\s+)?function\s+([A-Za-z0-9_$]+)\s*\(/g;
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
  line-height:1.42;
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
    line-height:1.4;
    padding-left:14px;
  }
}
`;

  const PAGE_COPY_TOOLS_FUNCTION = `function sanitizeKeywordForCopy(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw || "");
  const lowered = raw.toLowerCase();

  let value = cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw;

  value = value
    .replace(/\\bi bought\\b/gi, "")
    .replace(/\\bnow i\\b/gi, "")
    .replace(/\\bcannot sell\\b/gi, "sell lock")
    .replace(/\\bcan't sell\\b/gi, "sell lock")
    .replace(/\\bi got scammed by\\b/gi, "")
    .replace(/\\bdid i get scammed by\\b/gi, "")
    .replace(/^\\s*is\\s+/i, "")
    .replace(/^\\s*is this\\s+/i, "")
    .replace(/^\\s*should i buy\\s+/i, "")
    .replace(/^\\s*can i trust\\s+/i, "")
    .replace(/\\btoken risk check\\b/gi, "")
    .replace(/\\btoken risk\\b/gi, "")
    .replace(/\\bwarning signs\\b/gi, "")
    .replace(/\\brisks\\b/gi, "")
    .replace(/\\bwhat to know\\b/gi, "")
    .replace(/\\bwhat to check\\b/gi, "")
    .replace(/\\s+/g, " ")
    .trim();

  if (!value) {
    if (/(cannot sell|can't sell|honeypot|sell)/i.test(lowered)) return "sell lock";
    if (/(presale|fair launch|launch|airdrop)/i.test(lowered)) return "token launch";
    if (/(meme|memecoin|pump|moon|100x)/i.test(lowered)) return "meme token";
    if (/(contract|address|pair|dexscreener)/i.test(lowered)) return "token setup";
    return "this token";
  }

  return value;
}

function makeReadableCopyLabel(keywordRaw) {
  const cleaned = sanitizeKeywordForCopy(keywordRaw);
  const label = displayKeyword(cleaned || "this token");
  return label.length > 42 ? label.slice(0, 42).replace(/\\s+[^\\s]*$/, "").trim() : label;
}

function trimCopySentence(text, maxWords) {
  const words = String(text || "")
    .replace(/[.!?]+$/g, "")
    .trim()
    .split(/\\s+/)
    .filter(Boolean);

  if (!words.length) return "";

  const clipped = words.slice(0, maxWords).join(" ").replace(/[,:;\\-]+$/g, "").trim();
  return clipped ? clipped + "." : "";
}

function buildPreviewSignals(keywordRaw) {
  const lower = normalizeKeyword(keywordRaw || "").toLowerCase();

  if (/(cannot sell|can't sell|honeypot|sell)/i.test(lower)) {
    return [
      "The buy can work before exits fail.",
      "Sell pressure reveals the real trap.",
      "Approval prompts can worsen the damage."
    ];
  }

  if (/(meme|memecoin|pump|moon|100x)/i.test(lower)) {
    return [
      "Virality can outrun real due diligence.",
      "Few wallets can control the move.",
      "Price strength can disappear on first exits."
    ];
  }

  if (/(presale|fair launch|launch|airdrop)/i.test(lower)) {
    return [
      "Launch hype shrinks review time.",
      "Distribution details stay vague too often.",
      "Liquidity setup matters more than promises."
    ];
  }

  if (/(contract|address|pair|dexscreener)/i.test(lower)) {
    return [
      "Contract control matters more than branding.",
      "Liquidity quality decides exit risk.",
      "Holder concentration can crush the chart."
    ];
  }

  return [
    "Hype can hide weak structure.",
    "Liquidity decides how exits feel.",
    "Top wallets can control too much supply."
  ];
}`;

  const BUILD_HERO_TITLE_FUNCTION = `function buildHeroTitle(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const label = makeReadableCopyLabel(raw);

  if (!raw) {
    return "Check Token Risk Before You Buy";
  }

  if (/(cannot sell|can't sell|honeypot|sell)/i.test(lower)) {
    return \`\${label}: Sell Lock Warning Signs\`;
  }

  if (/(presale|fair launch|launch|airdrop)/i.test(lower)) {
    return \`\${label}: Launch Risk Warning Signs\`;
  }

  if (/(meme|memecoin|pump|moon|100x)/i.test(lower)) {
    return \`\${label}: Hype vs Real Risk\`;
  }

  if (isGuidanceStyleKeyword(lower)) {
    return \`\${displayKeyword(raw)}: What Actually Matters\`;
  }

  if (isQuestionStyleKeyword(lower)) {
    return \`\${displayKeyword(raw)}? Check the Structure First\`;
  }

  return \`\${label}: Token Risk Warning Signs\`;
}`;

  const BUILD_HERO_SUBHEADING_FUNCTION = `function buildHeroSubheading(keywordRaw) {
  const lower = normalizeKeyword(keywordRaw || "").toLowerCase();

  if (/(cannot sell|can't sell|honeypot|sell)/i.test(lower)) {
    return "Use the checker below to review exit risk, approvals, liquidity, and contract control before you touch the token again.";
  }

  if (/(presale|fair launch|launch|airdrop)/i.test(lower)) {
    return "Use the checker below to review contract control, liquidity, holder spread, and launch risk before you buy into the story.";
  }

  if (/(meme|memecoin|pump|moon|100x)/i.test(lower)) {
    return "Use the checker below to separate meme hype from real structure before you buy, approve, or chase the chart.";
  }

  if (/(contract|address|pair|dexscreener)/i.test(lower)) {
    return "Use the checker below to review contract control, liquidity quality, holder concentration, and execution risk before you act.";
  }

  return "Use the checker below to review contract control, liquidity, holder concentration, and exit risk before you buy or approve anything.";
}`;

  const BUILD_CONTENT_HEADING_FUNCTION = `function buildContentHeading(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const label = makeReadableCopyLabel(raw);

  if (!raw) return "What Usually Matters Most";

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return displayKeyword(raw);
  }

  if (/(cannot sell|can't sell|honeypot|sell)/i.test(lower)) {
    return \`Why \${label} Often Turns Ugly\`;
  }

  if (/(presale|fair launch|launch|airdrop)/i.test(lower)) {
    return \`What To Watch In \${label}\`;
  }

  if (/(meme|memecoin|pump|moon|100x)/i.test(lower)) {
    return \`What Usually Breaks Under \${label}\`;
  }

  return \`What Usually Matters In \${label}\`;
}`;

  const BUILD_CONTENT_BRIDGE_FUNCTION = `function buildContentBridge(keywordRaw) {
  const lower = normalizeKeyword(keywordRaw || "").toLowerCase();

  if (/(cannot sell|can't sell|honeypot|sell)/i.test(lower)) {
    return "When exits feel blocked, the problem is usually structural, not cosmetic. Check the contract, approvals, liquidity, and holder control before doing anything else.";
  }

  if (/(presale|fair launch|launch|airdrop)/i.test(lower)) {
    return "Fresh launches look exciting before the real structure is tested. Check ownership, liquidity, distribution, and sell conditions before trusting the pitch.";
  }

  if (/(meme|memecoin|pump|moon|100x)/i.test(lower)) {
    return "Hype moves faster than due diligence. Check the structure before you trust the chart, the crowd, or the marketing.";
  }

  if (/(contract|address|pair|dexscreener)/i.test(lower)) {
    return "A clean page or trending pair does not prove a safe setup. Check control, liquidity, holder spread, and exit behavior first.";
  }

  return "The dangerous part usually sits underneath the branding. Check the structure before you trust the story, the chart, or the crowd.";
}`;

  const BUILD_RECOGNITION_ITEMS_FUNCTION = `function buildRecognitionItems(keywordRaw) {
  const lower = normalizeKeyword(keywordRaw || "").toLowerCase();

  if (/(cannot sell|can't sell|honeypot|sell)/i.test(lower)) {
    return [
      ["What people notice first", "The token buys normally, then selling starts failing when it matters."],
      ["What bad actors want", "Entry first, panic later, and approvals signed before the trap is obvious."],
      ["Why it feels believable", "The chart and branding still look normal right up to the exit problem."],
      ["What actually matters", "Sell behavior, contract control, liquidity depth, and approval risk."]
    ];
  }

  if (/(presale|fair launch|launch|airdrop)/i.test(lower)) {
    return [
      ["What people notice first", "Countdowns, whitelists, early access, and pressure to move fast."],
      ["What bad actors want", "Committed buyers before ownership, liquidity, and distribution get real scrutiny."],
      ["Why it feels believable", "Fresh launches always sell speed, upside, and fear of missing out."],
      ["What actually matters", "Who controls the token, who holds the supply, and how exits work."]
    ];
  }

  if (/(meme|memecoin|pump|moon|100x)/i.test(lower)) {
    return [
      ["What people notice first", "Viral posts, green candles, screenshots, and crowd energy."],
      ["What bad actors want", "Buy pressure before anyone checks wallets, liquidity, or control functions."],
      ["Why it feels believable", "Real meme runs exist, so weak setups borrow the same visual cues."],
      ["What actually matters", "Liquidity quality, wallet concentration, and what happens when momentum stalls."]
    ];
  }

  if (/(contract|address|pair|dexscreener)/i.test(lower)) {
    return [
      ["What people notice first", "A chart, pair page, or contract link that looks clean enough."],
      ["What bad actors want", "Trust built from surface signals instead of actual structure."],
      ["Why it feels believable", "Crypto users often mistake visible data for verified safety."],
      ["What actually matters", "Liquidity, ownership control, holder spread, and exit behavior."]
    ];
  }

  return [
    ["What people notice first", "A clean page, a moving chart, or hype that feels convincing."],
    ["What bad actors want", "Trust before the contract and wallet structure get real scrutiny."],
    ["Why it feels believable", "Weak setups often look polished right before they fail."],
    ["What actually matters", "Liquidity, holders, contract control, and how exits actually work."]
  ];
}`;

  const APPLY_PREVIEW_CARD_FUNCTION = `function applyPreviewCard() {
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
    .map(signal => \`<div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>\${escapeHtml(signal)}</span></div>\`)
    .join("");
}`;

  const EXTRACT_SEO_SOURCE_BLOCKS_FUNCTION = `function extractSeoSourceBlocks(seoContent) {
  if (!seoContent) return [];

  const parser = document.createElement("div");
  parser.innerHTML = String(seoContent.innerHTML || "").trim();

  const rawNodes = Array.from(
    parser.querySelectorAll("p, li, h2, h3, h4, h5, blockquote")
  );

  const blocks = rawNodes
    .map(node => String(node.textContent || "").replace(/\\s+/g, " ").trim())
    .filter(Boolean)
    .filter(text => text.length >= 18)
    .filter(text => !/^check similar tokens$/i.test(text))
    .filter(text => !/^more token risk checks$/i.test(text))
    .filter(text => !/^token risk hub$/i.test(text));

  if (blocks.length) {
    return blocks;
  }

  return String(parser.textContent || "")
    .replace(/\\s+/g, " ")
    .split(/(?<=[.!?])\\s+/)
    .map(part => part.trim())
    .filter(Boolean)
    .filter(text => text.length >= 18);
}`;

  const TOKEN_BULLET_TOOLS_FUNCTION = `function normalizeTokenBulletKey(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function trimBulletHard(text, maxWords) {
  const words = String(text || "")
    .replace(/[.!?]+$/g, "")
    .trim()
    .split(/\\s+/)
    .filter(Boolean);

  if (!words.length) return "";

  const clipped = words.slice(0, maxWords).join(" ").trim();
  const safe = clipped
    .replace(/[,:;\\-]+$/g, "")
    .replace(/\\s+/g, " ")
    .trim();

  return safe ? safe + "." : "";
}

function cleanRewriteInput(text) {
  return String(text || "")
    .replace(/\\*\\*/g, "")
    .replace(/^[\\-•]\\s*/, "")
    .replace(/\\bthis means\\b/gi, "")
    .replace(/\\bthis can mean\\b/gi, "")
    .replace(/\\bthis usually means\\b/gi, "")
    .replace(/\\bit is important to note that\\b/gi, "")
    .replace(/\\bit is worth noting that\\b/gi, "")
    .replace(/\\bin many cases\\b/gi, "")
    .replace(/\\bin some cases\\b/gi, "")
    .replace(/\\bin most cases\\b/gi, "")
    .replace(/\\ba common pattern starts when\\b/gi, "")
    .replace(/\\bthe safer move is to\\b/gi, "")
    .replace(/\\bthe safest move is to\\b/gi, "")
    .replace(/\\bwhat this page helps with\\b/gi, "")
    .replace(/\\bthis page helps\\b/gi, "")
    .replace(/\\bthis token\\b/gi, "The setup")
    .replace(/\\bthe token\\b/gi, "The setup")
    .replace(/\\bthe project\\b/gi, "The setup")
    .replace(/\\busers\\b/gi, "buyers")
    .replace(/\\s+/g, " ")
    .trim();
}

function classifyTokenBulletTheme(text) {
  const lower = String(text || "").toLowerCase();

  if (/(check|verify|confirm|review|avoid|watch|pause|compare|inspect|read contract|check holder|check liquidity|before buying|before you buy|before acting)/i.test(lower)) {
    return "actions";
  }

  if (/(liquidity|pool|lp|locked|lock|unlock|drained|drain|remove liquidity|thin liquidity)/i.test(lower)) {
    return "liquidity";
  }

  if (/(holder|holders|wallet|wallets|whale|distribution|concentration|top wallet|top holder|few wallets)/i.test(lower)) {
    return "holders";
  }

  if (/(sell|selling|exit|honeypot|cannot sell|can't sell|blocked sell|swap fails|approval|approve|tax|slippage|volume spike|dump|exit liquidity)/i.test(lower)) {
    return "execution";
  }

  if (/(contract|owner|ownership|mint|blacklist|pause trading|freeze|admin|function|renounced|proxy|upgradeable|control)/i.test(lower)) {
    return "contract";
  }

  if (/(hype|viral|telegram|community|influencer|trend|pump|moon|fomo|urgent|urgency|pressure|countdown|whitelist|social|shill|promo|x post|thread)/i.test(lower)) {
    return "hype";
  }

  return "generic";
}

function classifyCardIndex(text, theme) {
  const resolvedTheme = theme || classifyTokenBulletTheme(text);

  if (resolvedTheme === "actions") return 3;
  if (resolvedTheme === "hype") return 0;
  if (resolvedTheme === "liquidity" || resolvedTheme === "holders" || resolvedTheme === "contract") return 1;
  if (resolvedTheme === "execution") return 2;
  return 2;
}

function bulletBucketKey(text, theme, cardIndex) {
  const lower = String(text || "").toLowerCase();

  if (cardIndex === 0) {
    if (/(fomo|urgent|countdown|rush|pressure|now|fast)/.test(lower)) return "hype-urgency";
    if (/(viral|social|telegram|x post|thread|community|influencer|promo)/.test(lower)) return "hype-social";
    if (/(price|pump|moon|spike|trend|attention)/.test(lower)) return "hype-price";
    if (/(launch|presale|airdrop|fair launch)/.test(lower)) return "hype-launch";
    return "hype-general";
  }

  if (cardIndex === 1) {
    if (/(remove liquidity|drain liquidity|rug pull|unlocked liquidity)/.test(lower)) return "structure-liquidity-rug";
    if (/(thin liquidity|low liquidity|shallow liquidity)/.test(lower)) return "structure-liquidity-thin";
    if (theme === "liquidity") return "structure-liquidity";
    if (/(top wallet|top holder|few wallets|concentration|distribution)/.test(lower)) return "structure-holders-concentration";
    if (theme === "holders") return "structure-holders";
    if (/(mint|blacklist|freeze|pause|owner|admin|proxy|upgradeable|permissions|control)/.test(lower)) return "structure-contract-control";
    if (theme === "contract") return "structure-contract";
    return "structure-general";
  }

  if (cardIndex === 2) {
    if (/(cannot sell|can't sell|honeypot|blocked sell|sell fails|exit)/.test(lower)) return "execution-sell";
    if (/(approval|approve|wallet connect|permission|allowance)/.test(lower)) return "execution-approval";
    if (/(tax|slippage)/.test(lower)) return "execution-tax";
    if (/(dump|crash|collapse|exit wave)/.test(lower)) return "execution-dump";
    if (/(price|chart|trend|volume|spike)/.test(lower)) return "execution-chart";
    return "execution-general";
  }

  if (cardIndex === 3) {
    if (/(contract|owner|mint|blacklist|pause|freeze|admin|proxy|permissions)/.test(lower)) return "action-contract";
    if (/(liquidity|lp|pool|locked|unlock|drain)/.test(lower)) return "action-liquidity";
    if (/(holder|wallet|distribution|concentration)/.test(lower)) return "action-holders";
    if (/(approve|approval|wallet connect|allowance|seed phrase|recovery)/.test(lower)) return "action-approval";
    if (/(sell|honeypot|exit|slippage|tax)/.test(lower)) return "action-exit";
    return "action-general";
  }

  return "general";
}

function buildDefaultTokenFallbacks(theme) {
  const lowerTheme = String(theme || "").toLowerCase();

  const common = {
    0: [
      "Hype lands before proof.",
      "Urgency replaces real review.",
      "The chart sells the story.",
      "Social noise masks weak setup."
    ],
    1: [
      "Liquidity decides how exits feel.",
      "Few wallets can control too much.",
      "Contract permissions can wreck the trade.",
      "Structure matters more than branding."
    ],
    2: [
      "Easy buys do not guarantee easy exits.",
      "Sell friction usually shows up late.",
      "Price action can flip hard.",
      "Execution risk hides inside momentum."
    ],
    3: [
      "Check contract control first.",
      "Check holder spread next.",
      "Check liquidity before trusting the chart.",
      "Pause before approving anything."
    ]
  };

  if (/(meme|memecoin|pump|moon|100x)/.test(lowerTheme)) {
    common[0] = [
      "Meme hype attracts buyers fast.",
      "Virality hides weak structure.",
      "Fast pumps create fake confidence.",
      "Community noise can outrun proof."
    ];
  }

  if (/(presale|launch|airdrop|fair launch)/.test(lowerTheme)) {
    common[0] = [
      "Launch hype compresses review time.",
      "Early access pressure distorts judgment.",
      "Countdowns exist to rush buyers.",
      "Fresh launches deserve extra skepticism."
    ];
  }

  if (/(cannot sell|cant sell|honeypot|sell)/.test(lowerTheme)) {
    common[2] = [
      "The buy works before the trap does.",
      "Sell friction shows up after entry.",
      "Blocked exits kill the trade.",
      "Execution risk matters more than hype."
    ];
  }

  return common;
}

function normalizeMeaningText(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9\\s]/g, " ")
    .replace(/\\s+/g, " ")
    .trim();
}

function sentenceHasAny(text, patterns) {
  return patterns.some(pattern => pattern.test(text));
}

function buildSentenceMeaning(text) {
  const lower = normalizeMeaningText(text);

  return {
    lower,
    urgency: sentenceHasAny(lower, [/\\burgent\\b/, /\\burgency\\b/, /\\brush\\b/, /\\bfomo\\b/, /\\bpressure\\b/, /\\bcountdown\\b/, /\\bwhitelist\\b/, /\\bearly access\\b/]),
    social: sentenceHasAny(lower, [/\\bviral\\b/, /\\btelegram\\b/, /\\bx post\\b/, /\\bthread\\b/, /\\bcommunity\\b/, /\\binfluencer\\b/, /\\bsocial\\b/, /\\bshill\\b/, /\\bpromo\\b/]),
    chart: sentenceHasAny(lower, [/\\bprice\\b/, /\\bpump\\b/, /\\bmoon\\b/, /\\bspike\\b/, /\\btrend\\b/, /\\battention\\b/, /\\bchart\\b/, /\\bvolume\\b/]),
    lockedLiquidity: sentenceHasAny(lower, [/\\blocked liquidity\\b/, /\\bliquidity locked\\b/, /\\blocked lp\\b/]),
    thinLiquidity: sentenceHasAny(lower, [/\\bthin liquidity\\b/, /\\blow liquidity\\b/, /\\bsmall pool\\b/, /\\bshallow liquidity\\b/]),
    unlockedLiquidity: sentenceHasAny(lower, [/\\bunlocked liquidity\\b/, /\\bliquidity unlocked\\b/, /\\bremove liquidity\\b/, /\\bdrain liquidity\\b/, /\\brug pull\\b/]),
    concentration: sentenceHasAny(lower, [/\\bholder concentration\\b/, /\\bwallet concentration\\b/, /\\bconcentration\\b/, /\\bfew wallets\\b/, /\\btop wallet\\b/, /\\btop holder\\b/, /\\bwhale\\b/, /\\bdistribution\\b/]),
    mint: sentenceHasAny(lower, [/\\bmint\\b/, /\\bminting\\b/, /\\bcreate supply\\b/, /\\bnew supply\\b/]),
    blacklist: sentenceHasAny(lower, [/\\bblacklist\\b/, /\\bfreeze\\b/, /\\bpause trading\\b/, /\\bpause\\b/, /\\bblock wallets\\b/]),
    ownership: sentenceHasAny(lower, [/\\bowner\\b/, /\\bownership\\b/, /\\badmin\\b/, /\\bproxy\\b/, /\\bupgradeable\\b/, /\\bcontrol\\b/, /\\brenounced\\b/, /\\bfunction\\b/, /\\bpermissions\\b/]),
    approvals: sentenceHasAny(lower, [/\\bapproval\\b/, /\\bapprove\\b/, /\\bwallet connect\\b/, /\\bpermission\\b/, /\\ballowance\\b/]),
    sellBlock: sentenceHasAny(lower, [/\\bcannot sell\\b/, /\\bcan t sell\\b/, /\\bblocked sell\\b/, /\\bsell fails\\b/, /\\bhoneypot\\b/]),
    slippage: sentenceHasAny(lower, [/\\bslippage\\b/, /\\bhigh tax\\b/, /\\btax\\b/]),
    dump: sentenceHasAny(lower, [/\\bdump\\b/, /\\bcrash\\b/, /\\bcollapse\\b/, /\\bexit wave\\b/]),
    launch: sentenceHasAny(lower, [/\\bpresale\\b/, /\\bfair launch\\b/, /\\blaunch\\b/, /\\bairdrop\\b/]),
    confidence: sentenceHasAny(lower, [/\\blooks safe\\b/, /\\bseems safe\\b/, /\\blooks legit\\b/, /\\btrust\\b/, /\\bconfidence\\b/, /\\bproof\\b/])
  };
}

function buildMeaningRewrite(text, theme, cardIndex) {
  const meaning = buildSentenceMeaning(text);
  const lower = meaning.lower;

  if (cardIndex === 0) {
    if (meaning.urgency && meaning.launch) return "Launch pressure usually lands before the proof does.";
    if (meaning.urgency) return "Urgency usually shows up before proof.";
    if (meaning.social && meaning.chart) return "Crowd hype and chart heat can hide weak structure.";
    if (meaning.social) return "Crowd noise can outrun real diligence.";
    if (meaning.chart && /\\bpump\\b|\\bspike\\b|\\bmoon\\b/.test(lower)) return "A pump can hide weak guts.";
    if (meaning.chart) return "The chart can sell a bad setup.";
    if (meaning.launch) return "Launch excitement can bury obvious risk.";
    return "Surface confidence can hide weak structure.";
  }

  if (cardIndex === 1) {
    if (meaning.unlockedLiquidity) return "Unsecured liquidity keeps the rug live.";
    if (meaning.thinLiquidity) return "Thin liquidity makes exits ugly fast.";
    if (meaning.lockedLiquidity) return "A liquidity lock does not fix bad structure.";
    if (meaning.concentration && meaning.chart) return "Too few wallets can steer the whole chart.";
    if (meaning.concentration) return "Too few wallets can own the move.";
    if (meaning.mint) return "Mint control can wreck supply discipline.";
    if (meaning.blacklist) return "Blacklist power kills buyer trust fast.";
    if (meaning.ownership && meaning.approvals) return "Admin control plus wallet approvals is a bad mix.";
    if (meaning.ownership) return "Admin control matters more than branding.";
    if (theme === "liquidity") return "Liquidity quality decides how exits feel.";
    if (theme === "holders") return "Wallet concentration can crush the chart.";
    if (theme === "contract") return "Contract control sets the real risk.";
    return "Weak structure breaks long before the story does.";
  }

  if (cardIndex === 2) {
    if (meaning.sellBlock && meaning.approvals) return "The buy and approval can work before exits fail.";
    if (meaning.sellBlock) return "Entry can work before exits break.";
    if (meaning.approvals) return "The approval can be the real trap.";
    if (meaning.slippage && meaning.chart) return "Taxes and slippage can wreck a strong-looking chart.";
    if (meaning.slippage) return "Taxes and slippage can trap late buyers.";
    if (meaning.dump) return "The chart can snap once exits start.";
    if (meaning.chart) return "Momentum usually dies at the exit test.";
    return "Execution risk usually appears after entry.";
  }

  if (cardIndex === 3) {
    if (meaning.ownership || meaning.mint || meaning.blacklist) return "Check contract permissions first.";
    if (meaning.unlockedLiquidity || meaning.thinLiquidity || meaning.lockedLiquidity) return "Verify the liquidity setup first.";
    if (meaning.concentration) return "Check top-wallet concentration next.";
    if (meaning.approvals) return "Do not sign under pressure.";
    if (meaning.sellBlock || meaning.slippage) return "Test the exit path before trusting it.";
    return "Slow down and verify the setup.";
  }

  return "";
}

function scoreMeaningSpecificity(text) {
  const meaning = buildSentenceMeaning(text);
  let score = 0;

  if (meaning.urgency) score += 2;
  if (meaning.social) score += 2;
  if (meaning.chart) score += 1;
  if (meaning.lockedLiquidity) score += 3;
  if (meaning.thinLiquidity) score += 3;
  if (meaning.unlockedLiquidity) score += 4;
  if (meaning.concentration) score += 3;
  if (meaning.mint) score += 4;
  if (meaning.blacklist) score += 4;
  if (meaning.ownership) score += 3;
  if (meaning.approvals) score += 3;
  if (meaning.sellBlock) score += 4;
  if (meaning.slippage) score += 2;
  if (meaning.dump) score += 2;
  if (meaning.launch) score += 2;
  if (meaning.confidence) score += 1;

  return score;
}

function finalPolishLine(text, cardIndex) {
  let value = String(text || "")
    .replace(/\\s+/g, " ")
    .replace(/[,:;]+$/g, "")
    .trim();

  if (!value) return "";

  value = trimBulletHard(value, cardIndex === 3 ? 12 : 13);

  if (!value) return "";

  return value.charAt(0).toUpperCase() + value.slice(1);
}`;

  const COMPRESS_TOKEN_BULLET_FUNCTION = `function compressTokenBullet(text, theme, cardIndex) {
  const cleaned = cleanRewriteInput(stripSeoFiller(String(text || "")));
  if (!cleaned) return "";

  const bulletTheme = classifyTokenBulletTheme(cleaned);
  const resolvedCard = typeof cardIndex === "number" ? cardIndex : classifyCardIndex(cleaned, bulletTheme);

  const rewritten = buildMeaningRewrite(cleaned, bulletTheme || theme, resolvedCard) || cleaned;
  return finalPolishLine(rewritten, resolvedCard);
}`;

  const BUILD_CARD_BULLET_POOL_FUNCTION = `function buildCardBulletPool(paragraphs, theme) {
  const sourceMaterial = Array.isArray(paragraphs) ? paragraphs : [];
  const sentencePool = sourceMaterial
    .flatMap(block => {
      const normalizedBlock = String(block || "").replace(/\\s+/g, " ").trim();
      if (!normalizedBlock) return [];
      const parts = normalizedBlock
        .split(/(?<=[.!?])\\s+/)
        .map(part => normalizeSeoSentence(part))
        .filter(Boolean);
      return parts.length ? parts : [normalizedBlock];
    })
    .map(s => normalizeSeoSentence(s))
    .filter(Boolean)
    .filter(s => s.length >= 18)
    .filter(s => !containsKeywordLeak(s))
    .filter(s => !isTooGenericSentence(s))
    .filter(s => !/^what people notice first$/i.test(s))
    .filter(s => !/^what bad actors want$/i.test(s))
    .filter(s => !/^why it feels believable$/i.test(s))
    .filter(s => !/^why this page helps$/i.test(s))
    .filter(s => !/^how this token situation usually plays out$/i.test(s))
    .filter(s => !/^why structure matters more than narrative$/i.test(s))
    .filter(s => !/^signs the setup may be weak or risky$/i.test(s))
    .filter(s => !/^safer next steps$/i.test(s));

  const candidates = sentencePool.map(sentence => {
    const rawTheme = classifyTokenBulletTheme(sentence);
    const cardIndex = classifyCardIndex(sentence, rawTheme);
    const compressed = compressTokenBullet(sentence, theme, cardIndex);
    const key = normalizeTokenBulletKey(compressed);
    const bucket = bulletBucketKey(sentence, rawTheme, cardIndex);
    const specificity = scoreMeaningSpecificity(sentence);

    return {
      original: sentence,
      text: compressed,
      theme: rawTheme,
      cardIndex,
      bucket,
      key,
      specificity,
      length: sentence.length
    };
  });

  const seen = new Set();
  const unique = [];

  candidates
    .filter(item => item.text && item.key)
    .sort((a, b) => {
      if (b.specificity !== a.specificity) return b.specificity - a.specificity;
      return b.length - a.length;
    })
    .forEach(item => {
      if (seen.has(item.key)) return;
      seen.add(item.key);
      unique.push(item);
    });

  return unique.sort((a, b) => {
    if (a.cardIndex !== b.cardIndex) return a.cardIndex - b.cardIndex;
    if (b.specificity !== a.specificity) return b.specificity - a.specificity;
    return b.length - a.length;
  });
}`;

  const BUILD_SEO_CARD_GROUPS_FUNCTION = `function buildSeoCardGroups(paragraphs) {
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
    if (cards[cardIndex].items.length >= 4) return false;

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
      if (cards[i].items.length >= 3) break;
      pushBullet(i, fallback);
    }
  }

  return cards
    .map(card => ({
      titleIndex: card.titleIndex,
      items: card.items.slice(0, 4)
    }))
    .filter(card => card.items.length > 0);
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
        const items = Array.isArray(group && group.items) ? group.items : [];
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

  const CLEAN_SEO_CONTENT_FUNCTION = `function cleanSeoContent() {
  const seoContent = document.getElementById("seoContent");
  if (!seoContent) return;

  seoContent.innerHTML = String(seoContent.innerHTML || "")
    .replace(/\\*\\*/g, "")
    .replace(/<p>\\s*<\\/p>/g, "")
    .trim();

  const blocks = extractSeoSourceBlocks(seoContent)
    .map(text => stripSeoFiller(text))
    .map(text => text.replace(/\\s+/g, " ").trim())
    .filter(Boolean)
    .filter(text => text.length >= 18);

  const groups = buildSeoCardGroups(blocks);

  if (!groups.length) {
    seoContent.innerHTML = "";
    return;
  }

  renderSeoContentCards(groups);
}`;

  html = upsertStyleBlock(html, "token-risk-polish-style", TOKEN_RISK_POLISH_STYLE);

  html = upsertFunctionBundle(html, PAGE_COPY_TOOLS_FUNCTION, "buildHeroTitle");
  html = upsertFunction(html, "buildHeroTitle", BUILD_HERO_TITLE_FUNCTION, "buildHeroSubheading");
  html = upsertFunction(html, "buildHeroSubheading", BUILD_HERO_SUBHEADING_FUNCTION, "buildContentHeading");
  html = upsertFunction(html, "buildContentHeading", BUILD_CONTENT_HEADING_FUNCTION, "buildContentBridge");
  html = upsertFunction(html, "buildContentBridge", BUILD_CONTENT_BRIDGE_FUNCTION, "setKeywordHeadings");
  html = upsertFunction(html, "buildRecognitionItems", BUILD_RECOGNITION_ITEMS_FUNCTION, "renderRecognitionChips");
  html = upsertFunction(html, "applyPreviewCard", APPLY_PREVIEW_CARD_FUNCTION, "applyIntentToChecker");

  html = upsertFunction(html, "extractSeoSourceBlocks", EXTRACT_SEO_SOURCE_BLOCKS_FUNCTION, "cleanSeoContent");
  html = upsertFunctionBundle(html, TOKEN_BULLET_TOOLS_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "compressTokenBullet", COMPRESS_TOKEN_BULLET_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "buildCardBulletPool", BUILD_CARD_BULLET_POOL_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "buildSeoCardGroups", BUILD_SEO_CARD_GROUPS_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "renderSeoContentCards", RENDER_SEO_CONTENT_CARDS_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "cleanSeoContent", CLEAN_SEO_CONTENT_FUNCTION, "cleanRelatedLinks");

  ensureContains(html, 'style id="token-risk-polish-style"', "style block");
  ensureContains(html, "sanitizeKeywordForCopy", "page copy sanitizer");
  ensureContains(html, "makeReadableCopyLabel", "page copy labeler");
  ensureContains(html, "buildPreviewSignals", "preview signal builder");
  ensureContains(html, "buildHeroTitle", "hero title override");
  ensureContains(html, "buildHeroSubheading", "hero subheading override");
  ensureContains(html, "buildContentHeading", "content heading override");
  ensureContains(html, "buildContentBridge", "content bridge override");
  ensureContains(html, "buildRecognitionItems", "recognition copy override");
  ensureContains(html, "applyPreviewCard", "preview card override");
  ensureContains(html, "extractSeoSourceBlocks", "seo source extractor");
  ensureContains(html, "normalizeTokenBulletKey", "bullet key normalizer");
  ensureContains(html, "trimBulletHard", "hard bullet trimmer");
  ensureContains(html, "cleanRewriteInput", "rewrite input cleaner");
  ensureContains(html, "classifyTokenBulletTheme", "bullet theme classifier");
  ensureContains(html, "classifyCardIndex", "card classifier");
  ensureContains(html, "bulletBucketKey", "bucket deduper");
  ensureContains(html, "buildDefaultTokenFallbacks", "fallback map");
  ensureContains(html, "normalizeMeaningText", "meaning normalizer");
  ensureContains(html, "sentenceHasAny", "pattern matcher");
  ensureContains(html, "buildSentenceMeaning", "meaning extractor");
  ensureContains(html, "buildMeaningRewrite", "meaning rewrite");
  ensureContains(html, "scoreMeaningSpecificity", "specificity scorer");
  ensureContains(html, "finalPolishLine", "final bullet polisher");
  ensureContains(html, "compressTokenBullet", "bullet compressor");
  ensureContains(html, "buildCardBulletPool", "bullet pool builder");
  ensureContains(html, "buildSeoCardGroups", "seo card grouping");
  ensureContains(html, "renderSeoContentCards", "seo card renderer");
  ensureContains(html, "cleanSeoContent", "seo cleaner");
  ensureContains(html, "story-card-list", "bullet card list class");
  ensureContains(html, "story-card-item", "bullet card item class");
  ensureContains(html, "titleIndex", "title index preservation");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");
  console.log("Perfected.");
}

main(); 