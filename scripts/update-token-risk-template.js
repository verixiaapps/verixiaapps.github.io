const fs = require("fs");
const path = require("path");

const TEMPLATE_PATH = path.join(
  process.cwd(),
  "token-risk-template",
  "token-risk-template-a.html"
);

function assertFileExists(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Template file not found: ${filePath}`);
  }
}

function replaceAllExact(source, oldValue, newValue) {
  if (!oldValue || oldValue === newValue) return source;
  if (!source.includes(oldValue)) return source;
  return source.split(oldValue).join(newValue);
}

function replaceAllRegex(source, regex, newValue) {
  return source.replace(regex, newValue);
}

function ensureContains(source, needle, label) {
  if (!source.includes(needle)) {
    throw new Error(`Expected content missing after update: ${label}`);
  }
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
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
          return {
            start: startIndex,
            end: i + 1,
          };
        }
      }
    }

    prev = char;
  }

  throw new Error(`Could not find function end for: ${functionName}`);
}

function replaceFunction(source, functionName, replacement) {
  const existingRange = findFunctionRange(source, functionName);

  if (!existingRange) {
    throw new Error(`Could not find function: ${functionName}`);
  }

  return (
    source.slice(0, existingRange.start) +
    replacement +
    source.slice(existingRange.end)
  );
}

function insertBeforeFunction(source, functionName, blockToInsert) {
  if (source.includes(blockToInsert)) return source;

  const existingRange = findFunctionRange(source, functionName);

  if (!existingRange) {
    throw new Error(`Could not find insertion point before function: ${functionName}`);
  }

  return (
    source.slice(0, existingRange.start) +
    blockToInsert +
    "\n\n" +
    source.slice(existingRange.start)
  );
}

function updateStaticCopy(html) {
  let output = html;

  const exactReplacements = [
    ['<span>Scam Check Now</span>', '<span>Token Risk</span>'],
    ['<div class="hero-badge">Live scam checking</div>', '<div class="hero-badge">Live token analysis</div>'],
    ['<div class="hero-badge">Shareable warning page</div>', '<div class="hero-badge">Liquidity-aware checks</div>'],
    ['<div class="hero-badge">Built for repeat use</div>', '<div class="hero-badge">Built for repeat use</div>'],
    ['<div class="hero-trust-chip">Check before you click</div>', '<div class="hero-trust-chip">Check before you buy</div>'],
    ['<div class="hero-trust-chip">Check before you reply</div>', '<div class="hero-trust-chip">Check before you swap</div>'],
    ['<div class="hero-trust-chip">Check before you send money</div>', '<div class="hero-trust-chip">Check before you connect</div>'],
    ['<div class="system-badge">Example scam pattern for reference</div>', '<div class="system-badge">Example token risk snapshot for reference</div>'],
    ['<div class="preview-badge" id="previewBadge">🔴 Example Risk Pattern</div>', '<div class="preview-badge" id="previewBadge">🔴 Example Token Risk</div>'],
    ['<div class="preview-score" id="previewScore">Risk Example</div>', '<div class="preview-score" id="previewScore">Liquidity Confidence</div>'],
    ['<div class="preview-domain" id="previewDomain">Example suspicious message</div>', '<div class="preview-domain" id="previewDomain">Example token snapshot</div>'],
    ['<div class="preview-sub" id="previewSub">Common signals found in similar scams</div>', '<div class="preview-sub" id="previewSub">Common risk signals found in similar tokens</div>'],
    ['<div class="input-help">Examples: delivery text, PayPal alert, crypto message, job offer, account warning</div>', '<div class="input-help">Example: ERC-20, Solana, Base, or other supported token contract address</div>'],
    ['<button class="check" onclick="check()">🔍 Check Scam Risk</button>', '<button class="check" onclick="checkToken()">🔍 Check Token Risk</button>'],
    ['<div class="note">No signup required • 1 free check • Results in seconds</div>', '<div class="note">No signup required • 1 free token check • Results in seconds</div>'],
    ['<div class="note">Get a clear risk level, key red flags, and what to do next</div>', '<div class="note">Get a clear risk level, liquidity confidence, token metrics, and what to do next</div>'],
    ['<h4>Check suspicious messages anytime</h4>', '<h4>Check token risk anytime</h4>'],
    ['Scam attempts often do not happen once. Use the app to check the next message before you click, reply, or send money.', 'Risky tokens move fast. Use the app to review the next token before you buy, swap, or connect your wallet.'],
    ['<h3>Don’t Miss the Next Scam</h3>', '<h3>Don’t Miss the Next Risky Token</h3>'],
    ['Most scam attempts do not happen once. If you are seeing suspicious messages, links, or requests, more may follow. Check each one before it costs you.', 'Risky tokens do not appear once. If you are checking launches, trending coins, or fast-moving pairs, more will follow. Check each one before it costs you.'],
    ['Built for ongoing protection against scams, phishing, impersonation, and risky payment requests', 'Built for ongoing token risk review across liquidity, volume, volatility, and market behavior'],
    ['Unlimited scam checks • Cancel anytime', 'Unlimited token checks • Cancel anytime'],
    ['Weekly Protection', 'Weekly Access'],
    ['Monthly Protection', 'Monthly Access'],
    ['Yearly Protection', 'Yearly Access'],
    ['<h3 id="relatedHeading">Check Similar Messages</h3>', '<h3 id="relatedHeading">Check Similar Tokens</h3>'],
    ['<h3 id="moreLinksHeading">More Scam Checks</h3>', '<h3 id="moreLinksHeading">More Token Risk Checks</h3>'],
    ['Messages like this are one of the most common ways people lose money, share codes, or hand over access without realizing it. When something feels off, pause and verify it through official sources before taking action.', 'Tokens like this can move fast and punish bad decisions quickly. When something feels off, pause and review liquidity, volume, pair age, and broader trust signals before taking action.'],
    ['Scam Check Now © 2026 • Scam detection and risk analysis tool', 'Token Risk © 2026 • Token risk analysis tool'],
    ['Unlimited scam checks are active with this account', 'Unlimited token checks are active with this account'],
    ['Unlock unlimited scam checks instantly', 'Unlock unlimited token checks instantly'],
    ['Continue with your selected plan below.', 'Continue with your selected plan below.'],
    ['🔓 Unlock Unlimited Checks', '🔓 Unlock Unlimited Token Checks']
  ];

  for (const [oldValue, newValue] of exactReplacements) {
    output = replaceAllExact(output, oldValue, newValue);
  }

  output = replaceAllRegex(
    output,
    /<textarea id="text"[^>]*><\/textarea>/g,
    '<input id="tokenAddress" placeholder="Paste token contract address">'
  );

  output = replaceAllRegex(
    output,
    /"name":"How can I tell if something is a scam\?"/g,
    `"name":"How can I tell if a crypto token is risky?"`
  );

  output = replaceAllRegex(
    output,
    /Look for urgency, requests for money or codes, suspicious links, and messages that pressure you to act quickly\. Always verify through official sources\./g,
    `Look for low liquidity, abnormal volume spikes, extreme price changes, and very new pairs. Always verify the token before buying, swapping, or connecting.`
  );

  output = replaceAllRegex(
    output,
    /"name":"What should I do if I clicked a suspicious link\?"/g,
    `"name":"What does liquidity confidence mean?"`
  );

  output = replaceAllRegex(
    output,
    /Avoid entering any information, close the page, run a security check on your device, and change important passwords if needed\./g,
    `Liquidity confidence is a simple signal based on liquidity relative to trading activity. Weak liquidity can make exits, slippage, and sharp breakdowns more dangerous.`
  );

  output = replaceAllRegex(
    output,
    /"name":"Are scam messages common\?"/g,
    `"name":"Can a token still be risky even if it has volume?"`
  );

  output = replaceAllRegex(
    output,
    /Yes, scam messages are increasingly common across email, text, social media, and messaging apps\. They often impersonate trusted companies or people\./g,
    `Yes. Volume alone does not make a token safe. Thin liquidity, unstable price behavior, and weak trust signals can still create high risk.`
  );

  output = replaceAllRegex(
    output,
    /<div class="preview-signal"><span class="preview-signal-icon">⚠️<\/span><span>Suspicious domain mismatch<\/span><\/div>\s*<div class="preview-signal"><span class="preview-signal-icon">⚠️<\/span><span>Urgent language detected<\/span><\/div>\s*<div class="preview-signal"><span class="preview-signal-icon">⚠️<\/span><span>Payment request via gift card<\/span><\/div>/g,
    `<div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>Low liquidity versus trading activity</span></div>
        <div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>Very new pair or unstable price action</span></div>
        <div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>Mixed trust signals across token metrics</span></div>`
  );

  return output;
}

const CHECK_TOKEN_FUNCTION = `async function checkToken() {
  const tokenAddress = document.getElementById("tokenAddress").value.trim();
  const emailEl = document.getElementById("email");
  const email = emailEl ? emailEl.value.trim().toLowerCase() : "";
  const subscribed = isBrowserSubscribed();
  const result = document.getElementById("result");

  if (!tokenAddress) {
    result.innerHTML = \`
      <div class="result-card unknown">
        <div class="result-top">
          <div class="risk unknown">⚪ Paste Token Address</div>
          <div class="result-chip">Awaiting Input</div>
        </div>
        <div class="result-summary">Paste a token contract address to check liquidity, market signals, and token risk before you act.</div>
      </div>
    \`;
    result.style.display = "block";
    return;
  }

  result.style.display = "block";
  result.innerHTML = \`
    <div class="result-card unknown">
      <div class="result-top">
        <div class="risk unknown">⚪ Analyzing...</div>
        <div class="result-chip">Token Scan In Progress</div>
      </div>
      <div class="result-summary">Checking liquidity, volume, price behavior, and broader token risk signals.</div>
    </div>
  \`;

  try {
    const response = await fetch(API + "/token-risk", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tokenAddress, email, subscribed })
    });

    const data = await response.json();

    if (data.limit) {
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
    showUpgrade();
  } catch (e) {
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

const FORMATTER_BLOCK = `function formatCompactMetricValue(label, value) {
  if (value === null || value === undefined || value === "") return "N/A";

  if (typeof value === "number") {
    if (label === "Price Change 24h") {
      const rounded = Math.round(value * 100) / 100;
      return \`\${rounded}%\`;
    }

    if (label === "Price USD") {
      if (value >= 1) return \`$\${value.toLocaleString(undefined, { maximumFractionDigits: 6 })}\`;
      return \`$\${value.toFixed(8).replace(/0+$/, "").replace(/\\.$/, "")}\`;
    }

    if (["Liquidity", "Volume 24h", "Market Cap", "FDV"].includes(label)) {
      return \`$\${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}\`;
    }

    return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }

  return String(value);
}

function formatTokenMetrics(metrics) {
  const rows = [
    ["Liquidity", metrics?.liquidityUsd],
    ["Volume 24h", metrics?.volume24h],
    ["Price Change 24h", metrics?.priceChange24h],
    ["Price USD", metrics?.priceUsd],
    ["Market Cap", metrics?.marketCap],
    ["FDV", metrics?.fdv],
    ["Pair Age", metrics?.pairAge],
    ["Chain", metrics?.chainId],
    ["DEX", metrics?.dexId]
  ];

  return rows.map(([label, value]) => \`
    <li class="signal-item">
      <span class="signal-icon">•</span>
      <span><strong>\${escapeHtml(label)}:</strong> \${escapeHtml(formatCompactMetricValue(label, value))}</span>
    </li>
  \`).join("");
}

function formatTokenList(items, emptyText) {
  const safeItems = Array.isArray(items) ? items.filter(Boolean) : [];

  if (!safeItems.length) {
    return \`<li class="signal-item"><span class="signal-icon">•</span><span>\${escapeHtml(emptyText)}</span></li>\`;
  }

  return safeItems.map(item => \`
    <li class="signal-item">
      <span class="signal-icon">•</span>
      <span>\${escapeHtml(String(item))}</span>
    </li>
  \`).join("");
}

function formatTokenResult(data) {
  const analysis = data.analysis || {};
  const riskRaw = String(analysis.riskLevel || "unknown").toLowerCase();
  const safeRiskClass = cardClassForRisk(riskRaw);
  const tokenData = data.tokenData || {};
  const tokenMetrics = data.tokenMetrics || {};
  const liquidityConfidence = data.liquidityConfidence || "Unknown";
  const pairFound = data.pairFound !== false;

  const titleBits = [];
  if (tokenData.symbol) titleBits.push(tokenData.symbol);
  if (tokenData.name && tokenData.name !== tokenData.symbol) titleBits.push(tokenData.name);

  const assetTitle = titleBits.length ? titleBits.join(" • ") : "Token Risk Review";
  const continuationLine = !pairFound
    ? '<div class="result-continuation">No live Dexscreener pair was found for this token, so treat it cautiously until you verify the contract and market structure.</div>'
    : "";

  return \`
  <div class="result-card \${safeRiskClass}">
    <div class="result-top">
      <div class="risk \${safeRiskClass}">\${iconForRisk(safeRiskClass)} \${safeRiskClass === "unknown" ? "Risk Level: REVIEW" : "Risk Level: " + String(analysis.riskLevel || "Review").toUpperCase()}</div>
      <div class="result-chip">Liquidity Confidence: \${escapeHtml(String(liquidityConfidence))}</div>
    </div>

    <div class="result-summary"><strong>\${escapeHtml(assetTitle)}</strong>\${tokenData.address ? "<br>" + escapeHtml(String(tokenData.address)) : ""}</div>
    \${continuationLine}

    <div class="section">
      <div class="section-title">Summary</div>
      <div class="action-box">\${escapeHtml(String(analysis.summary || "No summary available."))}</div>
    </div>

    <div class="section">
      <div class="section-title">Token Metrics</div>
      <ul class="signal-list">
        \${formatTokenMetrics(tokenMetrics)}
      </ul>
    </div>

    <div class="section">
      <div class="section-title">Key Signals</div>
      <ul class="signal-list">
        \${formatTokenList(analysis.keySignals, "No key signals available.")}
      </ul>
    </div>

    <div class="section">
      <div class="section-title">Concerning Indicators</div>
      <ul class="signal-list">
        \${formatTokenList(
          analysis.concerningIndicators,
          pairFound ? "No major concerning indicators were returned." : "No live pair data was found for this token."
        )}
      </ul>
    </div>

    <div class="section">
      <div class="section-title">Legitimate Elements</div>
      <ul class="signal-list">
        \${formatTokenList(analysis.legitimateElements, "No strong positive elements were returned.")}
      </ul>
    </div>

    <div class="section">
      <div class="section-title">Recommended Actions</div>
      <ul class="signal-list">
        \${formatTokenList(analysis.recommendations, "Verify the token before interacting.")}
      </ul>
    </div>

    <div class="result-payline">\${escapeHtml(String(analysis.finalTake || "Proceed carefully and verify the token before taking action."))}</div>

    <div class="result-actions">
      <button class="check result-cta" onclick="scrollToTopCheck()">🔁 Want to check another token? Paste it now</button>
    </div>
  </div>
  \`;
}`;

const SCROLL_TO_TOP_CHECK_FUNCTION = `function scrollToTopCheck() {
  const tokenInput = document.getElementById("tokenAddress");
  if (!tokenInput) return;
  window.scrollTo({ top: 0, behavior: "smooth" });
  setTimeout(() => tokenInput.focus(), 300);
}`;

const BUILD_HERO_TITLE_FUNCTION = `function buildHeroTitle(keywordRaw) {
  const cleanTitle = displayCleanKeyword(keywordRaw);
  if (!cleanTitle) {
    return "Check Token Risk Before You Buy, Swap, or Connect";
  }
  return \`\${cleanTitle}: Token Risk Check, Warning Signs & What To Know\`;
}`;

const BUILD_HERO_SUBHEADING_FUNCTION = `function buildHeroSubheading(keywordRaw) {
  const readableKeyword = displayKeyword(cleanKeywordForSentence(keywordRaw) || cleanKeywordBase(keywordRaw) || keywordRaw);
  if (!readableKeyword) {
    return "Paste a token address below to review liquidity confidence, market behavior, and broader token risk signals before you act.";
  }
  return \`Use the checker below to review \${readableKeyword} with liquidity, volume, pair-age, and token-risk context before you buy, swap, or connect.\`;
}`;

const BUILD_CONTENT_HEADING_FUNCTION = `function buildContentHeading(keywordRaw) {
  const cleanTitle = displayCleanKeyword(keywordRaw);
  if (!cleanTitle) {
    return "How To Review Token Risk Before You Interact";
  }
  return \`\${cleanTitle}: What To Review Before You Buy, Swap, or Connect\`;
}`;

const BUILD_CONTENT_BRIDGE_FUNCTION = `function buildContentBridge(keywordRaw) {
  const cleanTitle = displayKeyword(cleanKeywordForSentence(keywordRaw) || cleanKeywordBase(keywordRaw) || keywordRaw);
  if (!cleanTitle) {
    return "Use the checker above to review token liquidity, trading activity, pair age, and broader risk signals before you take action.";
  }
  return \`If you are looking at \${cleanTitle} right now, use the checker above to review liquidity, trading activity, pair age, and broader token-risk signals before you buy, swap, or connect.\`;
}`;

const BUILD_RECOGNITION_ITEMS_FUNCTION = `function buildRecognitionItems(keywordRaw) {
  const lower = normalizeKeyword(keywordRaw || "").toLowerCase();

  if (containsAny(lower, ["memecoin", "meme", "pump", "moon"])) {
    return [
      ["What people notice first", "Fast hype, sharp price moves, and heavy attention before trust is established."],
      ["What matters most", "Liquidity, pair age, and whether volume looks supported by the pool."],
      ["Why it feels tempting", "Momentum can make weak setups look stronger than they really are."],
      ["What makes it risky", "Thin liquidity and unstable trading behavior can punish late entries fast."]
    ];
  }

  if (containsAny(lower, ["solana", "eth", "ethereum", "base", "token", "coin", "crypto"])) {
    return [
      ["What people notice first", "A fast-moving token with volume, price action, and visible market interest."],
      ["What matters most", "Liquidity support, pair age, and whether activity looks stable or overheated."],
      ["Why it feels believable", "Momentum and branding can make a token look safer than its market structure suggests."],
      ["What makes it risky", "Weak liquidity, extreme moves, and unstable pair behavior can increase downside fast."]
    ];
  }

  return [
    ["What people notice first", "A token that looks active enough to buy without a deeper check."],
    ["What matters most", "Liquidity, volume, pair age, and broader market behavior."],
    ["Why it feels believable", "Price action and attention can create confidence before trust is earned."],
    ["What makes it risky", "A weak market structure can break down quickly once pressure hits the pool."]
  ];
}`;

const APPLY_PREVIEW_CARD_FUNCTION = `function applyPreviewCard() {
  const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
  const cleanTitle = displayCleanKeyword(keywordRaw) || "Example Token";
  const lower = keywordRaw.toLowerCase();

  const previewDomain = document.getElementById("previewDomain");
  const previewSub = document.getElementById("previewSub");
  const previewBadge = document.getElementById("previewBadge");
  const previewScore = document.getElementById("previewScore");
  const previewScoreFill = document.getElementById("previewScoreFill");
  const previewSignals = document.getElementById("previewSignals");

  if (!previewDomain || !previewSub || !previewBadge || !previewScore || !previewScoreFill || !previewSignals) {
    return;
  }

  let riskLabel = "Example Token Risk";
  let trustScore = "Liquidity Confidence";
  let fillWidth = "34%";
  let sub = "Common risk signals found in similar token setups";
  let signals = [
    "Liquidity may be weak relative to trading activity",
    "Pair age may be too new for confidence",
    "Price behavior may be unstable"
  ];

  if (containsAny(lower, ["meme", "memecoin", "pump", "moon"])) {
    riskLabel = "Example Meme Token Risk";
    fillWidth = "22%";
    signals = [
      "Fast hype without stable support",
      "Volume may outpace liquidity",
      "Sharp reversals can hit fast"
    ];
  } else if (containsAny(lower, ["solana", "eth", "ethereum", "base", "token", "coin", "crypto"])) {
    riskLabel = "Example Token Snapshot";
    fillWidth = "40%";
    signals = [
      "Liquidity versus volume matters",
      "Pair age affects confidence",
      "Stable structure matters more than hype"
    ];
  }

  previewBadge.textContent = \`🔴 \${riskLabel}\`;
  previewScore.textContent = trustScore;
  previewScoreFill.style.width = fillWidth;
  previewDomain.textContent = cleanTitle;
  previewSub.textContent = sub;
  previewSignals.innerHTML = signals.map(signal =>
    \`<div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>\${escapeHtml(signal)}</span></div>\`
  ).join("");
}`;

const APPLY_INTENT_TO_CHECKER_FUNCTION = `function applyIntentToChecker() {
  const tokenInput = document.getElementById("tokenAddress");
  const inputHelp = document.querySelector(".input-help");

  if (!tokenInput || !inputHelp) return;

  tokenInput.placeholder = "Paste token contract address";
  inputHelp.textContent = "Example: ERC-20, Solana, Base, or other supported token contract address";
}`;

const BUILD_SEO_CARD_TITLES_FUNCTION = `function buildSeoCardTitles(keywordRaw) {
  const lower = normalizeKeyword(keywordRaw || "").toLowerCase();

  if (containsAny(lower, ["meme", "memecoin", "pump", "moon"])) {
    return [
      ["🪙", "What this token setup often looks like"],
      ["💧", "Why liquidity matters first"],
      ["📈", "Where hype can hide risk"],
      ["⚠️", "What can happen if the structure is weak"]
    ];
  }

  return [
    ["🪙", "What this token often looks like"],
    ["💧", "Why liquidity and volume matter"],
    ["📊", "How the market structure should be read"],
    ["⚠️", "What can happen when risk is ignored"]
  ];
}`;

const PATCH_ANALYZE_LIMIT_AUTO_OPEN_FUNCTION = `function patchAnalyzeLimitAutoOpen() {
  if (!window.fetch || window.__SCAM_CHECK_FETCH_PATCHED__) return;
  window.__SCAM_CHECK_FETCH_PATCHED__ = true;

  const originalFetch = window.fetch.bind(window);

  window.fetch = async function (input, init) {
    let requestUrl = "";
    let isTokenRiskRequest = false;
    let parsedBody = null;

    try {
      requestUrl = typeof input === "string" ? input : (input && input.url ? input.url : "");
      isTokenRiskRequest = !!requestUrl && requestUrl.indexOf("/token-risk") !== -1;

      if (isTokenRiskRequest && init && typeof init.body === "string") {
        try {
          parsedBody = JSON.parse(init.body);
        } catch (e) {
          parsedBody = null;
        }

        if (parsedBody && typeof parsedBody === "object") {
          const enteredEmail = normalizeEmail(parsedBody.email || getEnteredEmail());
          const storedEmail = getStoredVerifiedEmail();
          const shouldSendSubscribed =
            !!enteredEmail &&
            !!storedEmail &&
            enteredEmail === storedEmail &&
            isBrowserSubscribed();

          parsedBody.email = enteredEmail;
          parsedBody.subscribed = shouldSendSubscribed;
          init = Object.assign({}, init, { body: JSON.stringify(parsedBody) });
        }
      }
    } catch (e) {}

    const response = await originalFetch(input, init);

    try {
      if (isTokenRiskRequest) {
        const requestEmail = normalizeEmail((parsedBody && parsedBody.email) || getEnteredEmail());

        response.clone().json().then(function (data) {
          const backendConfirmedSubscribed = !!(
            data &&
            (
              data.subscribed === true ||
              data.activeSubscription === true ||
              data.hasSubscription === true ||
              data.unlimited === true
            )
          );

          if (backendConfirmedSubscribed) {
            markBrowserSubscribed(true);

            if (requestEmail) {
              setStoredVerifiedEmail(requestEmail);
            } else if (data && data.email) {
              setStoredVerifiedEmail(data.email);
            }

            syncPostPurchaseMessage();
            hideLegacyUpgradeUI();
            return;
          }

          syncPostPurchaseMessage();

          if (data && data.limit === true) {
            setTimeout(function () {
              hideLegacyUpgradeUI();
              if (!shouldSuppressUpgrade() && window.openEmbeddedUpgrade) {
                window.openEmbeddedUpgrade("monthly");
              }
            }, 0);
          }
        }).catch(function () {});
      }
    } catch (e) {}

    return response;
  };
}`;

function main() {
  assertFileExists(TEMPLATE_PATH);

  let html = fs.readFileSync(TEMPLATE_PATH, "utf8");

  html = updateStaticCopy(html);

  html = replaceFunction(html, "check", CHECK_TOKEN_FUNCTION);
  html = replaceFunction(html, "scrollToTopCheck", SCROLL_TO_TOP_CHECK_FUNCTION);
  html = replaceFunction(html, "buildHeroTitle", BUILD_HERO_TITLE_FUNCTION);
  html = replaceFunction(html, "buildHeroSubheading", BUILD_HERO_SUBHEADING_FUNCTION);
  html = replaceFunction(html, "buildContentHeading", BUILD_CONTENT_HEADING_FUNCTION);
  html = replaceFunction(html, "buildContentBridge", BUILD_CONTENT_BRIDGE_FUNCTION);
  html = replaceFunction(html, "buildRecognitionItems", BUILD_RECOGNITION_ITEMS_FUNCTION);
  html = replaceFunction(html, "applyPreviewCard", APPLY_PREVIEW_CARD_FUNCTION);
  html = replaceFunction(html, "applyIntentToChecker", APPLY_INTENT_TO_CHECKER_FUNCTION);
  html = replaceFunction(html, "buildSeoCardTitles", BUILD_SEO_CARD_TITLES_FUNCTION);
  html = replaceFunction(html, "patchAnalyzeLimitAutoOpen", PATCH_ANALYZE_LIMIT_AUTO_OPEN_FUNCTION);

  if (!html.includes("function formatTokenResult(data)")) {
    html = insertBeforeFunction(html, "showUpgrade", FORMATTER_BLOCK);
  }

  ensureContains(html, "Token Risk", "Token Risk branding");
  ensureContains(html, 'id="tokenAddress"', "token address input");
  ensureContains(html, 'onclick="checkToken()"', "token check button hook");
  ensureContains(html, 'fetch(API + "/token-risk"', "token risk endpoint");
  ensureContains(html, 'requestUrl.indexOf("/token-risk") !== -1', "token risk fetch watcher");
  ensureContains(html, "function formatTokenResult(data)", "token result formatter");
  ensureContains(html, "async function checkToken()", "token check function");
  ensureContains(html, "Liquidity Confidence", "liquidity confidence UI");
  ensureContains(html, 'id="email"', "subscriber email field preserved");
  ensureContains(html, 'const API_BASE = "https://awake-integrity-production-faa0.up.railway.app";', "Railway API base preserved");
  ensureContains(html, 'const STRIPE_PUBLISHABLE_KEY = "pk_live_', "Stripe publishable key preserved");
  ensureContains(html, 'create-embedded-subscription', "embedded checkout endpoint preserved");
  ensureContains(html, 'create-checkout', "hosted checkout endpoint preserved");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");
  console.log(\`Updated \${TEMPLATE_PATH}\`);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}