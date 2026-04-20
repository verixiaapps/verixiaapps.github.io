const TOKEN_RISK_APP = (() => {

  const config = window.TOKEN_RISK_CONFIG || {};

  const API = config.apiBase || "";

  const RAW_KEYWORD = config.rawKeyword || "";

  const BROWSER_SUB_KEY = config.browserSubKey || "token_risk_browser_subscribed";

  function isBrowserSubscribed() {

    return localStorage.getItem(BROWSER_SUB_KEY) === "true";

  }

  function escapeHtml(str) {

    return String(str || "")

      .replace(/&/g, "&amp;")

      .replace(/</g, "&lt;")

      .replace(/>/g, "&gt;")

      .replace(/"/g, "&quot;")

      .replace(/'/g, "&#39;");

  }

  function summaryForRisk(riskClass) {

    if (riskClass === "high") {

      return "This token or project shows multiple risk signals. Treat it as unsafe until you verify the contract, holder setup, liquidity, and project claims directly.";

    }

    if (riskClass === "medium") {

      return "This token shows warning signs. Be cautious and verify the contract, trading setup, wallet concentration, and project claims before you buy or approve anything.";

    }

    if (riskClass === "low") {

      return "This token shows fewer obvious warning signs, but you should still verify contract permissions, liquidity setup, wallet concentration, and project claims before taking action.";

    }

    return "We could not determine a clear token risk level. Treat it cautiously and verify the contract, project claims, and trading setup before doing anything else.";

  }

  function paylineForRisk(riskClass) {

    if (riskClass === "high") {

      return "People get trapped by risky token setups every day. If the next contract or launch looks similar, guessing wrong could cost real money fast.";

    }

    if (riskClass === "medium") {

      return "Suspicious launches often do not stop at one. If you are looking at one risky token today, you may see another tomorrow. Check the next one before you buy.";

    }

    if (riskClass === "low") {

      return "Even lower-risk tokens can become dangerous later if liquidity changes, wallet concentration matters more than expected, or project behavior shifts.";

    }

    return "When the token risk is unclear, the safest move is to pause, verify this one carefully, and treat the next similar setup with caution too.";

  }

  function cardClassForRisk(risk) {

    if (risk === "high") return "high";

    if (risk === "medium") return "medium";

    if (risk === "low") return "low";

    return "unknown";

  }

  function iconForRisk(risk) {

    if (risk === "high") return "🔴";

    if (risk === "medium") return "🟠";

    if (risk === "low") return "🟢";

    return "⚪";

  }

  function signalIconForRisk(risk) {

    if (risk === "high") return "⚠️";

    if (risk === "medium") return "⚠️";

    if (risk === "low") return "✔️";

    return "•";

  }

  function chipByRisk(risk) {

    if (risk === "high") return "Pattern Match: Strong";

    if (risk === "medium") return "Pattern Match: Moderate";

    if (risk === "low") return "Pattern Match: Lower Risk";

    return "Pattern Match: Review Needed";

  }

  function scrollToTopCheck() {

    const tokenInput = document.getElementById("tokenAddress");

    if (!tokenInput) return;

    window.scrollTo({ top: 0, behavior: "smooth" });

    setTimeout(() => tokenInput.focus(), 300);

  }

  function getShareUrl() {

    return window.location.href;

  }

  function getShareText() {

    return "This token may be risky. Check it before you buy, approve, or bridge:";

  }

  function getWarningMessage() {

    return `This token may be risky.

Check it before you buy, approve, or bridge:

${getShareUrl()}`;

  }

  function showShareStatus(message) {

    const status = document.getElementById("shareStatus");

    if (!status) return;

    status.textContent = message;

    clearTimeout(showShareStatus.timeoutId);

    showShareStatus.timeoutId = setTimeout(() => {

      status.textContent = "";

    }, 2200);

  }

  function fallbackCopy(value, successMessage) {

    const input = document.createElement("textarea");

    input.value = value;

    input.setAttribute("readonly", "");

    input.style.position = "absolute";

    input.style.left = "-9999px";

    document.body.appendChild(input);

    input.select();

    input.setSelectionRange(0, 99999);

    document.execCommand("copy");

    document.body.removeChild(input);

    showShareStatus(successMessage);

  }

  function copyWarningMessage() {

    const message = getWarningMessage();

    if (navigator.clipboard && navigator.clipboard.writeText) {

      navigator.clipboard.writeText(message).then(() => {

        showShareStatus("Warning copied.");

      }).catch(() => {

        fallbackCopy(message, "Warning copied.");

      });

      return;

    }

    fallbackCopy(message, "Warning copied.");

  }

  function copyLink() {

    const url = getShareUrl();

    if (navigator.clipboard && navigator.clipboard.writeText) {

      navigator.clipboard.writeText(url).then(() => {

        showShareStatus("Link copied.");

      }).catch(() => {

        fallbackCopy(url, "Link copied.");

      });

      return;

    }

    fallbackCopy(url, "Link copied.");

  }

  function shareNative() {

    const shareData = {

      title: document.title,

      text: getShareText(),

      url: getShareUrl()

    };

    if (navigator.share) {

      navigator.share(shareData).catch(() => {});

      return;

    }

    copyWarningMessage();

  }

  function shareX() {

    const text = encodeURIComponent(getShareText());

    const url = encodeURIComponent(getShareUrl());

    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, "_blank", "noopener,noreferrer");

  }

  function compactMoney(value) {

    if (value === null || value === undefined || value === "") return "N/A";

    const num = Number(value);

    if (!Number.isFinite(num)) return "N/A";

    if (Math.abs(num) >= 1000000000) return `$${(num / 1000000000).toFixed(2)}B`;

    if (Math.abs(num) >= 1000000) return `$${(num / 1000000).toFixed(2)}M`;

    if (Math.abs(num) >= 1000) return `$${(num / 1000).toFixed(2)}K`;

    return `$${num.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;

  }

  function compactPercent(value) {

    if (value === null || value === undefined || value === "") return "N/A";

    const num = Number(value);

    if (!Number.isFinite(num)) return "N/A";

    return `${num >= 0 ? "+" : ""}${num.toFixed(2)}%`;

  }

  function escapeMaybe(value) {

    return escapeHtml(String(value == null ? "" : value));

  }

  function normalizeRiskClass(value) {

    const lower = String(value || "").toLowerCase();

    if (lower === "high") return "high";

    if (lower === "medium") return "medium";

    if (lower === "low") return "low";

    return "unknown";

  }

  function normalizeLiquidityClass(value) {

    const lower = String(value || "").toLowerCase();

    if (lower === "high") return "high";

    if (lower === "medium") return "medium";

    if (lower === "low") return "low";

    return "unknown";

  }

  function riskPillLabel(value) {

    const lower = normalizeRiskClass(value);

    if (lower === "high") return "Risk: High";

    if (lower === "medium") return "Risk: Medium";

    if (lower === "low") return "Risk: Low";

    return "Risk: Review";

  }

  function liquiditySubtext(value) {

    const lower = String(value || "").toLowerCase();

    if (lower === "high") return "Stronger liquidity relative to activity.";

    if (lower === "medium") return "Moderate liquidity support relative to activity.";

    if (lower === "low") return "Low liquidity relative to volume — higher rug risk.";

    return "Liquidity support is unclear.";

  }

  function metricRow(label, formattedValue, extraClass) {

    const cls = extraClass ? `token-metric-value ${extraClass}` : "token-metric-value";

    return `

      <div class="token-metric-row">

        <div class="token-metric-label">${escapeMaybe(label)}</div>

        <div class="${cls}">${escapeMaybe(formattedValue || "N/A")}</div>

      </div>

    `;

  }

  function formatSimpleBulletList(items, fallbackText) {

    const safe = Array.isArray(items)

      ? items.map(item => String(item || "").trim()).filter(Boolean)

      : [];

    const rows = safe.length ? safe : [fallbackText];

    return rows.map(item => `<li class="token-list-item">${escapeMaybe(item)}</li>`).join("");

  }

  function buildKeySignalRows(data) {

    const metrics = data.tokenMetrics || {};

    const liquidityConfidence = data.liquidityConfidence || "Unknown";

    const lcClass = normalizeLiquidityClass(liquidityConfidence);

    const priceChange = Number(metrics.priceChange24h);

    const priceClass = Number.isFinite(priceChange)

      ? (priceChange > 0 ? "high" : priceChange < 0 ? "low" : "")

      : "";

    return `

      <div class="token-key-row">

        <div>

          <div class="token-key-main"><strong>Liquidity Confidence:</strong> <span class="token-key-value ${lcClass}" style="display:inline;white-space:normal;">${escapeMaybe(String(liquidityConfidence).toUpperCase())}</span></div>

          <div class="token-key-sub">${escapeMaybe(liquiditySubtext(liquidityConfidence))}</div>

        </div>

        <div></div>

      </div>

      <div class="token-key-row">

        <div class="token-key-main">Volume Behavior</div>

        <div class="token-key-value">${escapeMaybe(compactMoney(metrics.volume24h))}</div>

      </div>

      <div class="token-key-row">

        <div class="token-key-main">Price Behavior</div>

        <div class="token-key-value ${priceClass}">${escapeMaybe(compactPercent(metrics.priceChange24h))}</div>

      </div>

      <div class="token-key-row">

        <div class="token-key-main">Pair Age</div>

        <div class="token-key-value">${escapeMaybe(metrics.pairAge || "N/A")}</div>

      </div>

      <div class="token-key-row">

        <div class="token-key-main">FDV</div>

        <div class="token-key-value">${escapeMaybe(compactMoney(metrics.fdv))}</div>

      </div>

    `;

  }

  function formatResult(raw) {

    const lines = String(raw || "").split("\n").map(l => l.trim()).filter(Boolean);

    let risk = "";

    let signals = [];

    let actions = [];

    let mode = "";

    lines.forEach(line => {

      const lower = line.toLowerCase();

      if (lower.includes("risk level")) {

        risk = line.split(":").slice(1).join(":").trim();

        return;

      }

      if (lower.includes("key signals")) {

        mode = "signals";

        return;

      }

      if (lower.includes("recommended action")) {

        mode = "actions";

        return;

      }

      if (line.startsWith("-")) {

        const cleaned = line.replace(/^-+\s*/, "");

        if (mode === "signals") signals.push(cleaned);

        if (mode === "actions") actions.push(cleaned);

      }

    });

    const riskClass = (risk || "review").trim().toLowerCase();

    const safeRiskClass = cardClassForRisk(riskClass);

    const signalIcon = signalIconForRisk(safeRiskClass);

    const continuationLine = safeRiskClass !== "low"

      ? `<div class="result-continuation">If this token setup reached you once, similar ones may already be in your feed. Risky launches often repeat the same pattern across many buyers.</div>`

      : "";

    if (signals.length === 0) {

      signals = ["Review the contract, liquidity setup, holder concentration, project claims, and any unusual trading behavior before taking action."];

    }

    if (actions.length === 0) {

      actions = ["Do not buy, approve, or bridge until you verify the contract, liquidity, holders, and project claims directly through reliable sources."];

    }

    return `

      <div class="result-card ${safeRiskClass}">

        <div class="result-top">

          <div class="risk ${safeRiskClass}">${iconForRisk(safeRiskClass)} ${safeRiskClass === "unknown" ? "Risk Level: REVIEW" : "Risk Level: " + safeRiskClass.toUpperCase()}</div>

          <div class="result-chip">${chipByRisk(safeRiskClass)}</div>

        </div>

        <div class="result-summary">${escapeHtml(summaryForRisk(safeRiskClass))}</div>

        ${continuationLine}

        <div class="section">

          <div class="section-title">Detected Signals</div>

          <ul class="signal-list">

            ${signals.map(s => `<li class="signal-item"><span class="signal-icon">${signalIcon}</span><span>${escapeHtml(s)}</span></li>`).join("")}

          </ul>

        </div>

        <div class="section">

          <div class="section-title">Recommended Actions</div>

          <div class="action-box">${escapeHtml(actions[0])}</div>

        </div>

        <div class="result-payline">${escapeHtml(paylineForRisk(safeRiskClass))}</div>

        <div class="result-actions">

          <button class="check result-cta" type="button" onclick="scrollToTopCheck()">🔁 Need to check another token? Scan it now</button>

          <div class="share-wrap">

            <div class="share-alert">⚠️ Risky tokens often spread through the same circles quickly</div>

            <div class="share-copy">Know someone who could see this same token, contract, or promo thread? Send this warning before they buy, approve, or bridge.</div>

            <div class="share-grid">

              <button type="button" class="share-btn primary" onclick="copyWarningMessage()">⚠️ Copy Warning</button>

              <button type="button" class="share-btn dark" onclick="shareNative()">📤 Share</button>

              <button type="button" class="share-btn light" onclick="shareX()">𝕏 Share to X</button>

              <button type="button" class="share-btn light" onclick="copyLink()">🔗 Copy Link</button>

            </div>

            <div class="share-status" id="shareStatus" aria-live="polite"></div>

          </div>

        </div>

      </div>

    `;

  }

  function formatTokenResult(data) {

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

    return `

      <div class="token-analysis-wrap">

        <div class="token-analysis-card">

          <div class="token-risk-pill ${riskClass}">

            <span>🛡️</span>

            <span>${escapeMaybe(riskPillLabel(analysis.riskLevel))}</span>

          </div>

          <div class="token-meta-line">

            ${escapeMaybe(displayTitle)}${metaParts.length ? " • " + escapeMaybe(metaParts.join(" • ")) : ""}

          </div>

          <div class="token-metric-stack">

            ${metricRow("Liquidity USD", compactMoney(metrics.liquidityUsd))}

            ${metricRow("Volume 24h", compactMoney(metrics.volume24h))}

            ${metricRow("Price change 24h", compactPercent(metrics.priceChange24h), priceChangeClass)}

            ${metricRow("Pair age", metrics.pairAge || "N/A")}

            ${metricRow("FDV", compactMoney(metrics.fdv))}

          </div>

          <div class="token-section">

            <div class="token-section-title">Summary</div>

            <div class="token-summary-text">${escapeMaybe(analysis.summary || "No summary available.")}</div>

          </div>

          <div class="token-section">

            <div class="token-section-title">Key Signals</div>

            <div class="token-key-grid">

              ${buildKeySignalRows(data)}

            </div>

          </div>

          <div class="token-section">

            <div class="token-section-title red">Red Flags</div>

            <ul class="token-list">

              ${formatSimpleBulletList(

                analysis.concerningIndicators,

                pairFound ? "No major concerning indicators were returned." : "No live pair data was found for this token."

              )}

            </ul>

          </