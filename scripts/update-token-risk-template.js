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

function main() {
  assertFileExists(TEMPLATE_PATH);

  let html = fs.readFileSync(TEMPLATE_PATH, "utf8");

  html = replaceAllRegex(
    html,
    /<textarea[^>]*id="text"[^>]*><\/textarea>/g,
    '<input id="tokenAddress" type="text" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" placeholder="Paste token contract address">'
  );

  const APPLY_INTENT_TO_CHECKER_FUNCTION = `function applyIntentToChecker() {
  const tokenInput = document.getElementById("tokenAddress");
  const inputHelp = document.querySelector(".input-help");

  if (!tokenInput || !inputHelp) return;

  tokenInput.placeholder = "Paste token contract address";
  inputHelp.textContent = "Example: ERC-20, Solana, Base, or other supported token contract address";
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
    const res = await fetch(API + "/token-risk", {
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

  html = upsertFunction(html, "applyIntentToChecker", APPLY_INTENT_TO_CHECKER_FUNCTION, "showUpgrade");
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
  ensureContains(html, 'fetch(API + "/token-risk"', "token risk endpoint");
  ensureContains(html, "function formatTokenResult(data)", "token formatter");
  ensureContains(html, "Liquidity Confidence", "liquidity confidence");
  ensureContains(html, "What To Watch", "what to watch");
  ensureContains(html, 'JSON.stringify({ tokenAddress, email, subscribed })', "token request payload");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");
  console.log(`Template updated: ${TEMPLATE_PATH}`);
}

main();