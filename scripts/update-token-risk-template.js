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

function replaceAllRegex(source, regex, newValue) {
  return source.replace(regex, newValue);
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

  html = replaceAllRegex(
    html,
    /<textarea[^>]*id="text"[^>]*><\/textarea>/g,
    '<input id="tokenAddress" type="text" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" placeholder="Paste token contract address">'
  );

  const TOKEN_RISK_POLISH_STYLE = `
:root{
  --bg:#05070d;
  --bg-2:#070b14;
  --bg-3:#0b1220;
  --bg-4:#0f1728;

  --surface:rgba(255,255,255,.04);
  --surface-2:rgba(255,255,255,.055);
  --surface-3:rgba(255,255,255,.075);

  --card:#0d1422;
  --card-2:#111a2b;
  --card-3:#162235;

  --ink:#edf3ff;
  --ink-strong:#ffffff;
  --ink-dark:#111827;
  --muted:#9cadc8;
  --muted-2:#8292ad;

  --line:rgba(255,255,255,.08);
  --line-2:rgba(255,255,255,.06);
  --line-3:rgba(255,255,255,.11);

  --cyan:#8cb8ff;
  --cyan-2:#6d98ff;
  --blue:#668eff;
  --blue-2:#4d77f2;
  --violet:#8d84f7;
  --violet-2:#7267eb;
  --emerald:#31c48d;
  --emerald-2:#1ea672;
  --amber:#f3ab34;
  --red:#ff744f;
  --red-2:#f45d35;

  --shadow-xl:0 28px 80px rgba(0,0,0,.42);
  --shadow-lg:0 20px 54px rgba(0,0,0,.34);
  --shadow-md:0 14px 34px rgba(0,0,0,.26);
  --shadow-sm:0 10px 22px rgba(0,0,0,.18);
  --shadow-xs:0 6px 14px rgba(0,0,0,.12);

  --radius-xl:28px;
  --radius-lg:22px;
  --radius-md:18px;
  --radius-sm:14px;
}

body{
  background:
    radial-gradient(circle at 15% 0%, rgba(118,146,255,.10), transparent 25%),
    radial-gradient(circle at 88% 0%, rgba(141,132,247,.08), transparent 26%),
    linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 30%, var(--bg-3) 68%, var(--bg-4) 100%);
}

.container,
.content-section{
  border:1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(13,20,34,.96) 0%, rgba(9,14,24,.985) 100%);
  box-shadow:var(--shadow-xl);
}

.preview-card,
.tool-shell,
.app-link-card,
.upgrade,
.inline-info-card{
  border:1px solid var(--line);
  box-shadow:var(--shadow-md);
}

.preview-card{
  background:
    linear-gradient(180deg, rgba(255,255,255,.05) 0%, rgba(255,255,255,.025) 100%);
}

.tool-shell{
  background:
    linear-gradient(180deg, rgba(255,255,255,.045) 0%, rgba(255,255,255,.025) 100%);
  border-color:var(--line);
}

.app-link-card{
  background:
    linear-gradient(180deg, rgba(255,255,255,.04) 0%, rgba(255,255,255,.02) 100%);
}

.inline-info-card,
.content-bridge,
.content-close,
.story-card,
.recognition-chip{
  border:1px solid var(--line);
  box-shadow:none;
}

.content-bridge,
.content-close{
  background:rgba(255,255,255,.035);
}

.story-card{
  background:
    linear-gradient(180deg, rgba(255,255,255,.045) 0%, rgba(255,255,255,.025) 100%);
}

.story-card.lead{
  background:
    linear-gradient(180deg, rgba(116,132,235,.14) 0%, rgba(255,255,255,.03) 100%);
  border-color:rgba(141,132,247,.22);
}

textarea,
input{
  border:1px solid rgba(255,255,255,.10);
  background:rgba(7,12,21,.9);
  box-shadow:none;
}

textarea:focus,
input:focus{
  border-color:rgba(109,152,255,.55);
  box-shadow:0 0 0 4px rgba(109,152,255,.10);
  background:rgba(8,14,24,.96);
}

.check,
.plan,
.plan.secondary,
.plan.tertiary,
.upgrade-top,
.app-link-button{
  box-shadow:0 14px 30px rgba(0,0,0,.22);
}

.hero-badge,
.hero-trust-chip,
.logo,
.app-top,
.preview-score{
  border:1px solid var(--line);
}

#email{
  margin-top:14px;
  background:rgba(255,255,255,.035);
  border-color:rgba(255,255,255,.08);
}

#email::placeholder{
  color:#8a9ab5;
}

.note{
  color:#93a4bf;
}

.success{
  color:#8df0b9;
}

#result{
  margin-top:24px;
}
`;

  const TOKEN_RISK_ANALYSIS_STYLE = `
.token-analysis-wrap{
  margin-top:24px;
  color:#eef3ff;
}
.token-analysis-card{
  background:
    linear-gradient(180deg, rgba(14,20,32,.98) 0%, rgba(10,15,24,.99) 100%);
  border-radius:26px;
  padding:24px 20px 22px;
  color:#eef3ff;
  box-shadow:0 24px 64px rgba(0,0,0,.34);
  border:1px solid rgba(255,255,255,.08);
}
.token-meta-line{
  margin:-4px 0 18px;
  font-size:13px;
  line-height:1.5;
  color:rgba(255,255,255,.52);
  word-break:break-word;
}
.token-risk-pill{
  display:inline-flex;
  align-items:center;
  gap:10px;
  padding:13px 17px;
  border-radius:18px;
  font-weight:900;
  font-size:17px;
  margin-bottom:16px;
  border:1px solid rgba(255,255,255,.12);
  letter-spacing:.01em;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.04);
}
.token-risk-pill.high{
  color:#ff8a67;
  border-color:rgba(255,116,79,.42);
  background:rgba(255,116,79,.10);
}
.token-risk-pill.medium{
  color:#ffc15d;
  border-color:rgba(243,171,52,.36);
  background:rgba(243,171,52,.10);
}
.token-risk-pill.low{
  color:#5ee0a5;
  border-color:rgba(49,196,141,.32);
  background:rgba(49,196,141,.10);
}
.token-risk-pill.unknown{
  color:#d5dbea;
  border-color:rgba(255,255,255,.14);
  background:rgba(255,255,255,.05);
}
.token-metric-stack{
  display:grid;
  gap:10px;
  margin:0 0 24px;
}
.token-metric-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
  padding:16px 18px;
  border-radius:18px;
  background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.06);
}
.token-metric-label{
  font-size:14px;
  font-weight:700;
  color:rgba(255,255,255,.60);
}
.token-metric-value{
  font-size:16px;
  font-weight:900;
  color:#f8fbff;
  text-align:right;
}
.token-metric-value.positive{ color:#5ee0a5; }
.token-metric-value.negative{ color:#ff8a67; }

.token-section{
  margin-top:18px;
  padding-top:18px;
  border-top:1px solid rgba(255,255,255,.07);
}
.token-section:first-of-type{
  margin-top:0;
}
.token-section-title{
  font-size:12px;
  font-weight:900;
  letter-spacing:.10em;
  text-transform:uppercase;
  margin-bottom:12px;
  color:rgba(255,255,255,.66);
}
.token-section-title.red{ color:#ff8a67; }
.token-section-title.green{ color:#5ee0a5; }

.token-summary-text{
  font-size:15px;
  line-height:1.68;
  color:rgba(255,255,255,.84);
}

.token-list{
  list-style:none;
  padding:0;
  margin:0;
  display:grid;
  gap:10px;
}
.token-list-item{
  position:relative;
  padding:12px 14px 12px 16px;
  border-radius:16px;
  background:rgba(255,255,255,.035);
  border:1px solid rgba(255,255,255,.06);
  font-size:14px;
  line-height:1.58;
  color:rgba(255,255,255,.84);
}
.token-list-item::before{
  content:"";
  position:absolute;
  left:0;
  top:12px;
  bottom:12px;
  width:3px;
  border-radius:999px;
  background:rgba(255,255,255,.14);
}
.token-section-title.red + .token-list .token-list-item::before{
  background:rgba(255,116,79,.80);
}
.token-section-title.green + .token-list .token-list-item::before{
  background:rgba(49,196,141,.78);
}

.token-key-grid{
  display:grid;
  gap:10px;
}
.token-key-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:16px;
  align-items:start;
  padding:12px 14px;
  border-radius:16px;
  background:rgba(255,255,255,.035);
  border:1px solid rgba(255,255,255,.06);
}
.token-key-main{
  font-size:14px;
  line-height:1.5;
  color:rgba(255,255,255,.72);
}
.token-key-main strong{
  font-weight:900;
  color:#f5f8ff;
}
.token-key-value{
  font-size:14px;
  line-height:1.2;
  font-weight:900;
  color:#f8fbff;
  text-align:right;
  white-space:nowrap;
}
.token-key-value.low{ color:#ff8a67; }
.token-key-value.medium{ color:#ffc15d; }
.token-key-value.high{ color:#5ee0a5; }
.token-key-sub{
  margin-top:5px;
  font-size:12px;
  line-height:1.55;
  color:rgba(255,255,255,.45);
}

.token-final-take{
  font-size:16px;
  line-height:1.6;
  font-weight:900;
}
.token-final-take.high{ color:#ff8a67; }
.token-final-take.medium{ color:#ffc15d; }
.token-final-take.low{ color:#5ee0a5; }
.token-final-take.unknown{ color:#e7edf9; }

@media (max-width:640px){
  .token-analysis-card{
    padding:20px 16px 18px;
    border-radius:22px;
  }
  .token-risk-pill{
    font-size:16px;
    padding:12px 15px;
    border-radius:16px;
    margin-bottom:14px;
  }
  .token-meta-line{
    margin-bottom:14px;
    font-size:12px;
  }
  .token-metric-stack,
  .token-key-grid,
  .token-list{
    gap:9px;
  }
  .token-metric-row,
  .token-key-row,
  .token-list-item{
    padding:12px 13px;
    border-radius:14px;
  }
  .token-metric-label,
  .token-key-main,
  .token-key-value,
  .token-summary-text,
  .token-list-item,
  .token-final-take{
    font-size:14px;
  }
  .token-key-sub{
    font-size:12px;
  }
}
`;

  const APPLY_INTENT_TO_CHECKER_FUNCTION = `function applyIntentToChecker() {
  const tokenInput = document.getElementById("tokenAddress");
  const inputHelp = document.querySelector(".input-help");

  if (!tokenInput || !inputHelp) return;

  tokenInput.placeholder = "Paste token contract address";
  inputHelp.textContent = "Example: ERC-20, Solana, Base, or other supported token contract address";
}`;

  const SPLIT_SEO_PARAGRAPHS_FROM_HTML_FUNCTION = `function splitSeoParagraphsFromHtml(seoContent) {
  const html = String(seoContent.innerHTML || "").trim();
  if (!html) return [];

  const parser = document.createElement("div");
  parser.innerHTML = html;

  let paragraphs = Array.from(parser.querySelectorAll("p"))
    .map(p => p.textContent.trim())
    .filter(Boolean);

  if (paragraphs.length) return paragraphs;

  paragraphs = parser.innerHTML
    .replace(/<br\\s*\\/?>/gi, "\\n")
    .replace(/<\\/div>/gi, "\\n\\n")
    .replace(/<\\/section>/gi, "\\n\\n")
    .replace(/<[^>]+>/g, "")
    .split(/\\n\\s*\\n/)
    .map(p => p.replace(/\\s+/g, " ").trim())
    .filter(Boolean);

  return paragraphs;
}`;

  const BUILD_SEO_CARD_TITLES_FUNCTION = `function buildSeoCardTitles(keywordRaw) {
  const lower = normalizeKeyword(keywordRaw || "").toLowerCase();

  if (containsAny(lower, ["meme", "memecoin", "pump", "moon", "100x"])) {
    return [
      ["🚀", "What this meme token setup often looks like"],
      ["⏱️", "Where the urgency becomes the trap"],
      ["🔁", "How the same pattern appears in different launches"],
      ["💥", "What can happen after the buy-in"]
    ];
  }

  if (containsAny(lower, ["presale", "launch", "airdrop", "fair launch"])) {
    return [
      ["🪂", "What this launch setup often looks like"],
      ["⏱️", "Where the pressure gets dangerous"],
      ["🔁", "How the story changes across different versions"],
      ["💥", "What happens after funds or trust are committed"]
    ];
  }

  if (containsAny(lower, ["contract", "address", "token", "coin", "pair"])) {
    return [
      ["🧾", "What this token setup often looks like"],
      ["⏱️", "Where the risk starts hiding behind momentum"],
      ["🔁", "How the same contract risk appears in different forms"],
      ["💥", "What can happen after the wrong buy or approval"]
    ];
  }

  return [
    ["👀", "What this usually looks like"],
    ["⏱️", "Where the pressure starts"],
    ["🔁", "How the pattern changes"],
    ["💥", "What can happen next"]
  ];
}`;

  const RENDER_SEO_CONTENT_CARDS_FUNCTION = `function renderSeoContentCards(paragraphs) {
  const seoContent = document.getElementById("seoContent");
  if (!seoContent) return;

  if (!paragraphs.length) {
    seoContent.innerHTML = "";
    return;
  }

  const titles = buildSeoCardTitles(RAW_KEYWORD || "");

  seoContent.innerHTML = \`
    <div class="story-stack">
      \${paragraphs.map((paragraph, index) => \`
        <article class="story-card\${index === 0 ? " lead" : ""}">
          <div class="story-card-title">
            <span class="story-card-title-icon">\${titles[index] ? titles[index][0] : "•"}</span>
            <span>\${titles[index] ? titles[index][1] : "More to know"}</span>
          </div>
          <p>\${escapeHtml(paragraph)}</p>
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
    .map(p => p.replace(/\\s+/g, " ").trim())
    .filter(Boolean)
    .slice(0, 4);

  renderSeoContentCards(paragraphs);
}`;

  const SCROLL_TO_TOP_CHECK_FUNCTION = `function scrollToTopCheck() {
  const tokenInput = document.getElementById("tokenAddress");
  if (!tokenInput) return;
  window.scrollTo({ top: 0, behavior: "smooth" });
  setTimeout(() => tokenInput.focus(), 300);
}`;

  const CHECK_FUNCTION = `async function check() {
  const tokenAddress = document.getElementById("tokenAddress")?.value.trim();
  const email = document.getElementById("email")?.value.trim().toLowerCase() || "";
  const subscribed = isBrowserSubscribed();
  const result = document.getElementById("result");

  if (!tokenAddress) {
    result.style.display = "block";
    result.innerHTML = \`
      <div class="result-card unknown">
        <div class="result-top">
          <div class="risk unknown">⚪ Paste Token Address</div>
          <div class="result-chip">Awaiting Input</div>
        </div>
        <div class="result-summary">Paste a token contract address to review liquidity confidence, market behavior, and token risk before you act.</div>
      </div>
    \`;
    return;
  }

  result.style.display = "block";
  result.innerHTML = \`
    <div class="result-card unknown">
      <div class="result-top">
        <div class="risk unknown">⚪ Analyzing...</div>
        <div class="result-chip">Token Scan In Progress</div>
      </div>
      <div class="result-summary">Checking liquidity, volume, price behavior, pair age, and broader token risk signals.</div>
    </div>
  \`;

  try {
    const res = await fetch(API + "/analyze-token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tokenAddress, email, subscribed })
    });

    const data = await res.json();

    if (data && data.limit) {
      result.innerHTML = \`
        <div class="result-card medium">
          <div class="result-top">
            <div class="risk medium">🟠 Free Check Used</div>
            <div class="result-chip">Upgrade Available</div>
          </div>
          <div class="result-summary">Unlock unlimited access so you can check the next token before you buy, swap, or connect.</div>
        </div>
      \`;
      showUpgrade();
      return;
    }

    result.innerHTML = formatTokenResult(data || {});
  } catch {
    result.innerHTML = \`
      <div class="result-card unknown">
        <div class="result-top">
          <div class="risk unknown">⚪ Unable To Analyze</div>
          <div class="result-chip">Try Again</div>
        </div>
        <div class="result-summary">We could not analyze this token right now. Please try again in a moment.</div>
      </div>
    \`;
  }
}`;

  const COMPACT_MONEY_FUNCTION = `function compactMoney(value) {
  if (value === null || value === undefined || value === "") return "N/A";
  const num = Number(value);
  if (!Number.isFinite(num)) return "N/A";

  if (Math.abs(num) >= 1000000000) return \`$\${(num / 1000000000).toFixed(2)}B\`;
  if (Math.abs(num) >= 1000000) return \`$\${(num / 1000000).toFixed(2)}M\`;
  if (Math.abs(num) >= 1000) return \`$\${(num / 1000).toFixed(2)}K\`;
  return \`$\${num.toLocaleString(undefined, { maximumFractionDigits: 2 })}\`;
}`;

  const COMPACT_PERCENT_FUNCTION = `function compactPercent(value) {
  if (value === null || value === undefined || value === "") return "N/A";
  const num = Number(value);
  if (!Number.isFinite(num)) return "N/A";
  return \`\${num >= 0 ? "+" : ""}\${num.toFixed(2)}%\`;
}`;

  const ESCAPE_MAYBE_FUNCTION = `function escapeMaybe(value) {
  return escapeHtml(String(value == null ? "" : value));
}`;

  const NORMALIZE_RISK_CLASS_FUNCTION = `function normalizeRiskClass(value) {
  const lower = String(value || "").toLowerCase();
  if (lower === "high") return "high";
  if (lower === "medium") return "medium";
  if (lower === "low") return "low";
  return "unknown";
}`;

  const NORMALIZE_LIQUIDITY_CLASS_FUNCTION = `function normalizeLiquidityClass(value) {
  const lower = String(value || "").toLowerCase();
  if (lower === "high") return "high";
  if (lower === "medium") return "medium";
  if (lower === "low") return "low";
  return "unknown";
}`;

  const RISK_PILL_LABEL_FUNCTION = `function riskPillLabel(value) {
  const lower = normalizeRiskClass(value);
  if (lower === "high") return "Risk: High";
  if (lower === "medium") return "Risk: Medium";
  if (lower === "low") return "Risk: Low";
  return "Risk: Review";
}`;

  const LIQUIDITY_SUBTEXT_FUNCTION = `function liquiditySubtext(value) {
  const lower = String(value || "").toLowerCase();
  if (lower === "high") return "Stronger liquidity relative to activity.";
  if (lower === "medium") return "Moderate liquidity support relative to activity.";
  if (lower === "low") return "Low liquidity relative to volume — higher rug risk.";
  return "Liquidity support is unclear.";
}`;

  const METRIC_ROW_FUNCTION = `function metricRow(label, formattedValue, extraClass) {
  const cls = extraClass ? \`token-metric-value \${extraClass}\` : "token-metric-value";
  return \`
    <div class="token-metric-row">
      <div class="token-metric-label">\${escapeMaybe(label)}</div>
      <div class="\${cls}">\${escapeMaybe(formattedValue || "N/A")}</div>
    </div>
  \`;
}`;

  const FORMAT_SIMPLE_BULLET_LIST_FUNCTION = `function formatSimpleBulletList(items, fallbackText) {
  const safe = Array.isArray(items)
    ? items.map(item => String(item || "").trim()).filter(Boolean)
    : [];

  const rows = safe.length ? safe : [fallbackText];

  return rows.map(item => \`<li class="token-list-item">\${escapeMaybe(item)}</li>\`).join("");
}`;

  const BUILD_KEY_SIGNAL_ROWS_FUNCTION = `function buildKeySignalRows(data) {
  const metrics = data.tokenMetrics || {};
  const liquidityConfidence = data.liquidityConfidence || "Unknown";
  const lcClass = normalizeLiquidityClass(liquidityConfidence);

  const priceChange = Number(metrics.priceChange24h);
  const priceClass = Number.isFinite(priceChange)
    ? (priceChange > 0 ? "high" : priceChange < 0 ? "low" : "")
    : "";

  return \`
    <div class="token-key-row">
      <div>
        <div class="token-key-main"><strong>Liquidity Confidence:</strong> <span class="token-key-value \${lcClass}" style="display:inline;white-space:normal;">\${escapeMaybe(String(liquidityConfidence).toUpperCase())}</span></div>
        <div class="token-key-sub">\${escapeMaybe(liquiditySubtext(liquidityConfidence))}</div>
      </div>
      <div></div>
    </div>

    <div class="token-key-row">
      <div class="token-key-main">Volume Behavior</div>
      <div class="token-key-value">\${escapeMaybe(compactMoney(metrics.volume24h))}</div>
    </div>

    <div class="token-key-row">
      <div class="token-key-main">Price Behavior</div>
      <div class="token-key-value \${priceClass}">\${escapeMaybe(compactPercent(metrics.priceChange24h))}</div>
    </div>

    <div class="token-key-row">
      <div class="token-key-main">Pair Age</div>
      <div class="token-key-value">\${escapeMaybe(metrics.pairAge || "N/A")}</div>
    </div>

    <div class="token-key-row">
      <div class="token-key-main">FDV</div>
      <div class="token-key-value">\${escapeMaybe(compactMoney(metrics.fdv))}</div>
    </div>
  \`;
}`;

  const FORMAT_TOKEN_RESULT_FUNCTION = `function formatTokenResult(data) {
  const analysis = data.analysis || {};
  const metrics = data.tokenMetrics || {};
  const tokenData = data.tokenData || {};
  const pairFound = data.pairFound !== false;
  const riskClass = normalizeRiskClass(analysis.riskLevel);
  const displayTitle = tokenData.symbol || tokenData.name || "Token Risk Review";

  const metaParts = [];
  if (tokenData.name && tokenData.symbol && tokenData.name !== tokenData.symbol) {
    metaParts.push(tokenData.name);
  }
  if (tokenData.address) {
    metaParts.push(tokenData.address);
  }
  if (!pairFound) {
    metaParts.push("No live Dex pair found");
  }

  const priceChangeNumber = Number(metrics.priceChange24h);
  const priceChangeClass = Number.isFinite(priceChangeNumber)
    ? (priceChangeNumber >= 0 ? "positive" : "negative")
    : "";

  return \`
    <div class="token-analysis-wrap">
      <div class="token-analysis-card">
        <div class="token-risk-pill \${riskClass}">
          <span>🛡️</span>
          <span>\${escapeMaybe(riskPillLabel(analysis.riskLevel))}</span>
        </div>

        <div class="token-meta-line">
          \${escapeMaybe(displayTitle)}\${metaParts.length ? " • " + escapeMaybe(metaParts.join(" • ")) : ""}
        </div>

        <div class="token-metric-stack">
          \${metricRow("Liquidity USD", compactMoney(metrics.liquidityUsd))}
          \${metricRow("Volume 24h", compactMoney(metrics.volume24h))}
          \${metricRow("Price change 24h", compactPercent(metrics.priceChange24h), priceChangeClass)}
          \${metricRow("Pair age", metrics.pairAge || "N/A")}
          \${metricRow("FDV", compactMoney(metrics.fdv))}
        </div>

        <div class="token-section">
          <div class="token-section-title">Summary</div>
          <div class="token-summary-text">\${escapeMaybe(analysis.summary || "No summary available.")}</div>
        </div>

        <div class="token-section">
          <div class="token-section-title">Key Signals</div>
          <div class="token-key-grid">
            \${buildKeySignalRows(data)}
          </div>
        </div>

        <div class="token-section">
          <div class="token-section-title red">Red Flags</div>
          <ul class="token-list">
            \${formatSimpleBulletList(
              analysis.concerningIndicators,
              pairFound ? "No major concerning indicators were returned." : "No live pair data was found for this token."
            )}
          </ul>
        </div>

        <div class="token-section">
          <div class="token-section-title green">Safe Signals</div>
          <ul class="token-list">
            \${formatSimpleBulletList(
              analysis.legitimateElements,
              "No strong positive trust signals were returned."
            )}
          </ul>
        </div>

        <div class="token-section">
          <div class="token-section-title">Final Take</div>
          <div class="token-final-take \${riskClass}">\${escapeMaybe(analysis.finalTake || "Proceed carefully.")}</div>
        </div>

        <div class="token-section">
          <div class="token-section-title">What To Watch</div>
          <ul class="token-list">
            \${formatSimpleBulletList(
              analysis.recommendations,
              "Verify the token before interacting."
            )}
          </ul>
        </div>
      </div>
    </div>
  \`;
}`;

  html = upsertStyleBlock(html, "token-risk-polish-style", TOKEN_RISK_POLISH_STYLE);
  html = upsertStyleBlock(html, "token-risk-analysis-style", TOKEN_RISK_ANALYSIS_STYLE);

  html = upsertFunction(html, "applyIntentToChecker", APPLY_INTENT_TO_CHECKER_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "splitSeoParagraphsFromHtml", SPLIT_SEO_PARAGRAPHS_FROM_HTML_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "buildSeoCardTitles", BUILD_SEO_CARD_TITLES_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "renderSeoContentCards", RENDER_SEO_CONTENT_CARDS_FUNCTION, "cleanSeoContent");
  html = upsertFunction(html, "cleanSeoContent", CLEAN_SEO_CONTENT_FUNCTION, "cleanRelatedLinks");
  html = upsertFunction(html, "scrollToTopCheck", SCROLL_TO_TOP_CHECK_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "check", CHECK_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "compactMoney", COMPACT_MONEY_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "compactPercent", COMPACT_PERCENT_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "escapeMaybe", ESCAPE_MAYBE_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "normalizeRiskClass", NORMALIZE_RISK_CLASS_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "normalizeLiquidityClass", NORMALIZE_LIQUIDITY_CLASS_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "riskPillLabel", RISK_PILL_LABEL_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "liquiditySubtext", LIQUIDITY_SUBTEXT_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "metricRow", METRIC_ROW_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "formatSimpleBulletList", FORMAT_SIMPLE_BULLET_LIST_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "buildKeySignalRows", BUILD_KEY_SIGNAL_ROWS_FUNCTION, "showUpgrade");
  html = upsertFunction(html, "formatTokenResult", FORMAT_TOKEN_RESULT_FUNCTION, "showUpgrade");

  ensureContains(html, 'id="tokenAddress"', "token input");
  ensureContains(html, 'fetch(API + "/analyze-token"', "token risk endpoint");
  ensureContains(html, "function formatTokenResult(data)", "token formatter");
  ensureContains(html, "function cleanSeoContent()", "seo content cleanup");
  ensureContains(html, "function renderSeoContentCards(paragraphs)", "seo card renderer");
  ensureContains(html, "Liquidity Confidence", "liquidity confidence");
  ensureContains(html, "What To Watch", "what to watch");
  ensureContains(html, 'JSON.stringify({ tokenAddress, email, subscribed })', "token request payload");
  ensureContains(html, 'style id="token-risk-analysis-style"', "token analysis style block");
  ensureContains(html, 'style id="token-risk-polish-style"', "token polish style block");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");
  console.log(`Template updated: ${TEMPLATE_PATH}`);
}

main();