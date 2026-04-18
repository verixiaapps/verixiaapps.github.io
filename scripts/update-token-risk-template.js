const fs = require("fs");
const path = require("path");

const TEMPLATE_PATH = process.env.TEMPLATE_PATH
  ? path.join(process.cwd(), process.env.TEMPLATE_PATH)
  : path.join(process.cwd(), "token-risk-template", "token-risk-template-a.html");
);

function assertFileExists(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Template file not found: ${filePath}`);
  }
}

function replaceAllExact(source, oldValue, newValue) {
  if (!source.includes(oldValue)) return source;
  return source.split(oldValue).join(newValue);
}

function replaceAllRegex(source, regex, newValue) {
  return source.replace(regex, newValue);
}

function ensureContains(source, needle, label) {
  if (!source.includes(needle)) {
    throw new Error(`Missing: ${label}`);
  }
}

function findFunctionRange(source, functionName) {
  const startRegex = new RegExp(`(?:async\\s+)?function\\s+${functionName}\\s*\\(`);
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
  let prev = "";

  for (let i = braceStart; i < source.length; i++) {
    const char = source[i];

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

  return source.slice(0, insertRange.start) + replacement + "\n\n" + source.slice(insertRange.start);
}

/* -------------------------
   STATIC COPY UPDATE
-------------------------- */

function updateStaticCopy(html) {
  let output = html;

  output = replaceAllExact(output, "Scam Check Now", "Token Risk");
  output = replaceAllExact(output, "Check Scam Risk", "Check Token Risk");

  output = replaceAllRegex(
    output,
    /<textarea[^>]*id="text"[^>]*><\/textarea>/g,
    '<input id="tokenAddress" type="text" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" placeholder="Paste token contract address">'
  );

  return output;
}

/* -------------------------
   STYLE
-------------------------- */

const STYLE_BLOCK = `<style id="token-risk-analysis-style">
.token-analysis-wrap{
  margin-top:22px;
  color:#f3f4f6;
}
.token-analysis-card{
  background:#000;
  border-radius:28px;
  padding:22px 18px 20px;
  color:#f3f4f6;
  box-shadow:0 16px 44px rgba(0,0,0,.35);
  border:1px solid rgba(255,255,255,.06);
}
.token-risk-pill{
  display:inline-flex;
  align-items:center;
  gap:10px;
  padding:14px 18px;
  border-radius:20px;
  font-weight:900;
  font-size:18px;
  margin-bottom:20px;
  border:2px solid rgba(255,255,255,.12);
}
.token-risk-pill.high{
  color:#ff5a00;
  border-color:#ff5a00;
  background:rgba(255,90,0,.12);
}
.token-risk-pill.medium{
  color:#ffb020;
  border-color:#ffb020;
  background:rgba(255,176,32,.12);
}
.token-risk-pill.low{
  color:#22c55e;
  border-color:#22c55e;
  background:rgba(34,197,94,.12);
}
.token-risk-pill.unknown{
  color:#d1d5db;
  border-color:rgba(255,255,255,.18);
  background:rgba(255,255,255,.06);
}
.token-metric-stack{
  display:grid;
  gap:14px;
  margin:0 0 28px;
}
.token-metric-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
  padding:22px 28px;
  border-radius:22px;
  background:linear-gradient(90deg,#141414 0%, #1a1a1a 100%);
}
.token-metric-label{
  font-size:18px;
  color:rgba(255,255,255,.62);
}
.token-metric-value{
  font-size:18px;
  font-weight:900;
  color:#f8fafc;
  text-align:right;
}
.token-metric-value.positive{ color:#23ff35; }
.token-metric-value.negative{ color:#ff5252; }
.token-section{
  margin-top:24px;
}
.token-section-title{
  font-size:20px;
  font-weight:950;
  color:#fff;
  text-transform:uppercase;
  margin-bottom:16px;
}
.token-section-title.red{ color:#ff2a1a; }
.token-section-title.green{ color:#23ff35; }
.token-summary-text{
  font-size:18px;
  line-height:1.6;
  color:rgba(255,255,255,.82);
}
.token-list{
  list-style:none;
  padding:0;
  margin:0;
  display:grid;
  gap:14px;
}
.token-list-item{
  font-size:18px;
  line-height:1.6;
  color:rgba(255,255,255,.82);
}
.token-list-item::before{
  content:"• ";
}
.token-key-grid{
  display:grid;
  gap:12px;
}
.token-key-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:16px;
  align-items:end;
}
.token-key-main{
  font-size:18px;
  line-height:1.4;
  color:rgba(255,255,255,.72);
}
.token-key-main strong{
  font-weight:500;
  color:rgba(255,255,255,.72);
}
.token-key-value{
  font-size:18px;
  line-height:1.2;
  font-weight:900;
  color:#f8fafc;
  text-align:right;
  white-space:nowrap;
}
.token-key-value.low{ color:#ff2a1a; }
.token-key-value.medium{ color:#ffb020; }
.token-key-value.high{ color:#23ff35; }
.token-key-sub{
  margin-top:4px;
  font-size:16px;
  line-height:1.45;
  font-style:italic;
  color:rgba(255,255,255,.42);
}
.token-final-take{
  font-size:20px;
  font-weight:900;
}
.token-final-take.high{ color:#ff5a00; }
.token-final-take.medium{ color:#ffb020; }
.token-final-take.low{ color:#23ff35; }
@media (max-width:640px){
  .token-analysis-card{
    padding:20px 16px 18px;
    border-radius:24px;
  }
  .token-risk-pill{
    font-size:17px;
    padding:13px 16px;
    border-radius:18px;
    margin-bottom:18px;
  }
  .token-metric-stack{
    gap:12px;
    margin-bottom:24px;
  }
  .token-metric-row{
    padding:18px 18px;
    border-radius:18px;
  }
  .token-metric-label,
  .token-metric-value,
  .token-key-main,
  .token-key-value,
  .token-summary-text,
  .token-list-item{
    font-size:16px;
  }
  .token-key-sub{
    font-size:15px;
  }
  .token-section-title{
    font-size:17px;
    margin-bottom:14px;
  }
  .token-final-take{
    font-size:17px;
  }
}
</style>`;

/* -------------------------
   CHECK FUNCTION
-------------------------- */

const CHECK_FUNCTION = `async function check() {
  const tokenAddress = document.getElementById("tokenAddress")?.value.trim();
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
    const res = await fetch(API + "/token-risk", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tokenAddress })
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

/* -------------------------
   FORMAT RESULT HELPERS
-------------------------- */

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

/* -------------------------
   MAIN
-------------------------- */

function main() {
  assertFileExists(TEMPLATE_PATH);

  let html = fs.readFileSync(TEMPLATE_PATH, "utf8");

  html = updateStaticCopy(html);

  if (!html.includes('id="token-risk-analysis-style"')) {
    html = replaceAllExact(html, "</head>", `${STYLE_BLOCK}\n</head>`);
  }

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

  ensureContains(html, "tokenAddress", "input");
  ensureContains(html, "/token-risk", "endpoint");
  ensureContains(html, "Liquidity Confidence", "liquidity confidence");
  ensureContains(html, 'id="token-risk-analysis-style"', "token analysis style");
  ensureContains(html, "function formatTokenResult(data)", "formatter");
  ensureContains(html, "What To Watch", "what to watch");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");
  console.log("Template updated");
}

main();