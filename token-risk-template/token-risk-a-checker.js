const TOKEN_RISK_APP = (() => {
  const config = window.TOKEN_RISK_CONFIG || {};
  const API = config.apiBase || "";
  const BROWSER_SUB_KEY = config.browserSubKey || "token_risk_browser_subscribed";

  function isBrowserSubscribed() {
    try {
      return localStorage.getItem(BROWSER_SUB_KEY) === "true";
    } catch (_) {
      return false;
    }
  }

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function normalizeRiskClass(value) {
    const risk = String(value || "").toLowerCase().trim();
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
    if (risk === "low") return "✔️";
    if (risk === "unknown") return "•";
    return "⚠️";
  }

  function chipByRisk(risk) {
    if (risk === "high") return "Pattern Match: Strong";
    if (risk === "medium") return "Pattern Match: Moderate";
    if (risk === "low") return "Pattern Match: Lower Risk";
    return "Pattern Match: Review Needed";
  }

  function summaryForRisk(risk) {
    if (risk === "high") {
      return "This token shows multiple high-risk signals. Do not interact until contract behavior, liquidity, and ownership concentration are verified.";
    }
    if (risk === "medium") {
      return "This token shows warning signs. Review liquidity, wallet concentration, permissions, and trading behavior before taking action.";
    }
    if (risk === "low") {
      return "This token shows fewer immediate risk signals, but you should still verify contract behavior, liquidity, and concentration before interacting.";
    }
    return "We could not determine a clear risk level. Treat this token cautiously and verify contract behavior, liquidity, and ownership before acting.";
  }

  function paylineForRisk(risk) {
    if (risk === "high") {
      return "Risky tokens often look fine until liquidity changes, exits get harder, or concentration starts to matter. A wrong move can become expensive fast.";
    }
    if (risk === "medium") {
      return "Many questionable tokens do not fail immediately. The risk often appears later through liquidity shifts, contract behavior, or wallet concentration.";
    }
    if (risk === "low") {
      return "Even lower-risk tokens still need verification because liquidity, permissions, and concentration can change after launch.";
    }
    return "When the risk is unclear, the safest move is to pause and verify the token structure before you buy, approve, or interact.";
  }

  function compactMoney(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return "N/A";
    if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
    if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
    if (n >= 1e3) return `$${(n / 1e3).toFixed(2)}K`;
    return `$${n.toLocaleString()}`;
  }

  function compactPercent(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return "N/A";
    return `${n >= 0 ? "+" : ""}${n.toFixed(2)}%`;
  }

  function safeText(value, fallback) {
    const text = String(value || "").trim();
    return text || fallback;
  }

  function buildMetricSignals(metrics) {
    const signals = [];

    const liquidity = compactMoney(metrics.liquidityUsd);
    const volume24h = compactMoney(metrics.volume24h);
    const fdv = compactMoney(metrics.fdv);
    const pairAge = safeText(metrics.pairAge, "N/A");
    const price24h = compactPercent(metrics.priceChange24h);

    signals.push(`Liquidity: ${liquidity}`);
    signals.push(`Volume 24h: ${volume24h}`);
    signals.push(`Price 24h: ${price24h}`);
    signals.push(`Pair age: ${pairAge}`);
    signals.push(`FDV: ${fdv}`);

    return signals;
  }

  function normalizeList(items) {
    if (!Array.isArray(items)) return [];
    return items
      .map(item => String(item || "").trim())
      .filter(Boolean);
  }

  function formatTokenResult(data) {
    const analysis = data.analysis || {};
    const metrics = data.tokenMetrics || {};
    const tokenData = data.tokenData || {};
    const risk = normalizeRiskClass(analysis.riskLevel);

    const concerningIndicators = normalizeList(analysis.concerningIndicators);
    const legitimateElements = normalizeList(analysis.legitimateElements);
    const recommendations = normalizeList(analysis.recommendations);
    const metricSignals = buildMetricSignals(metrics);

    const tokenName = safeText(tokenData.symbol || tokenData.name, "Token");
    const finalTake = safeText(
      analysis.finalTake,
      "Proceed carefully and verify contract behavior, liquidity, and ownership before interacting."
    );

    const detectedSignals = concerningIndicators.length
      ? concerningIndicators
      : ["No strong negative signals were returned, but token structure should still be verified."];

    const positiveSignals = legitimateElements.length
      ? legitimateElements
      : ["No strong positive signals were returned."];

    const watchItems = recommendations.length
      ? recommendations
      : ["Verify contract permissions, liquidity conditions, and holder distribution before interacting."];

    const continuationLine = risk !== "low"
      ? `<div class="result-continuation">If this token looks attractive now, risk can still show up later through liquidity changes, concentration, permissions, or trading behavior.</div>`
      : "";

    return `
      <div class="result-card ${risk}">
        <div class="result-top">
          <div class="risk ${risk}">${iconForRisk(risk)} ${risk === "unknown" ? "Risk Level: REVIEW" : "Risk Level: " + risk.toUpperCase()}</div>
          <div class="result-chip">${chipByRisk(risk)}</div>
        </div>

        <div class="result-summary">${escapeHtml(summaryForRisk(risk))}</div>
        ${continuationLine}

        <div class="section">
          <div class="section-title">Token Overview</div>
          <ul class="signal-list">
            <li class="signal-item"><span class="signal-icon">🪙</span><span>${escapeHtml(`Token: ${tokenName}`)}</span></li>
            ${metricSignals.map(item => `
              <li class="signal-item"><span class="signal-icon">📊</span><span>${escapeHtml(item)}</span></li>
            `).join("")}
          </ul>
        </div>

        <div class="section">
          <div class="section-title">Key Risk Signals</div>
          <ul class="signal-list">
            ${detectedSignals.map(item => `
              <li class="signal-item"><span class="signal-icon">${signalIconForRisk(risk)}</span><span>${escapeHtml(item)}</span></li>
            `).join("")}
          </ul>
        </div>

        <div class="section">
          <div class="section-title">Positive Signals</div>
          <ul class="signal-list">
            ${positiveSignals.map(item => `
              <li class="signal-item"><span class="signal-icon">✔️</span><span>${escapeHtml(item)}</span></li>
            `).join("")}
          </ul>
        </div>

        <div class="section">
          <div class="section-title">What To Watch</div>
          <div class="action-box">${escapeHtml(watchItems[0])}</div>
        </div>

        <div class="section">
          <div class="section-title">Final Take</div>
          <div class="action-box">${escapeHtml(finalTake)}</div>
        </div>

        <div class="result-payline">${escapeHtml(paylineForRisk(risk))}</div>

        <div class="result-actions">
          <button class="check result-cta" onclick="scrollToTopCheck()">🔁 Check Another Token</button>
        </div>
      </div>
    `;
  }

  function renderState(title, summary, chip, riskClass) {
    const cls = riskClass || "unknown";
    return `
      <div class="result-card ${cls}">
        <div class="result-top">
          <div class="risk ${cls}">${escapeHtml(title)}</div>
          <div class="result-chip">${escapeHtml(chip)}</div>
        </div>
        <div class="result-summary">${escapeHtml(summary)}</div>
      </div>
    `;
  }

  function renderEmpty() {
    return renderState(
      "⚪ Paste Token Address",
      "Paste a token contract address to review token risk before you buy, approve, or interact.",
      "Awaiting Input",
      "unknown"
    );
  }

  function renderLoading() {
    return renderState(
      "⚪ Checking Token",
      "Analyzing liquidity, ownership concentration, trading behavior, and contract signals.",
      "Scan In Progress",
      "unknown"
    );
  }

  function renderLimit() {
    return renderState(
      "🟠 Free Check Used",
      "Unlock unlimited token checks so you can review the next contract before you buy, approve, or interact.",
      "Upgrade Available",
      "medium"
    );
  }

  function renderError(message) {
    return renderState(
      "⚪ Unable To Analyze",
      message || "We could not analyze this token right now. Please try again in a moment.",
      "Try Again",
      "unknown"
    );
  }

  async function parseJsonSafe(response) {
    try {
      return await response.json();
    } catch (_) {
      return null;
    }
  }

  async function check() {
    const tokenAddress = (document.getElementById("tokenAddress")?.value || "").trim();
    const email = (document.getElementById("email")?.value || "").trim().toLowerCase();
    const subscribed = isBrowserSubscribed();
    const result = document.getElementById("result");

    if (!result) return;

    result.style.display = "block";

    if (!API) {
      result.innerHTML = renderError("API missing.");
      return;
    }

    if (!tokenAddress) {
      result.innerHTML = renderEmpty();
      return;
    }

    result.innerHTML = renderLoading();

    try {
      const response = await fetch(`${API}/analyze-token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tokenAddress,
          email,
          subscribed
        })
      });

      const data = await parseJsonSafe(response);

      if (!response.ok) {
        result.innerHTML = renderError(data?.error || "The token could not be analyzed.");
        return;
      }

      if (data?.limit) {
        result.innerHTML = renderLimit();
        if (typeof window.showUpgrade === "function") {
          window.showUpgrade();
        }
        return;
      }

      if (data?.analysis) {
        result.innerHTML = formatTokenResult(data);
        if (typeof window.showUpgrade === "function") {
          window.showUpgrade();
        }
        return;
      }

      result.innerHTML = renderError("No analysis returned.");
    } catch (_) {
      result.innerHTML = renderError();
    }
  }

  function scrollToTopCheck() {
    const input = document.getElementById("tokenAddress");
    if (!input) return;

    window.scrollTo({ top: 0, behavior: "smooth" });
    setTimeout(() => input.focus(), 300);
  }

  function init() {
    const params = new URLSearchParams(window.location.search);
    const postPurchase = document.getElementById("postPurchase");

    if (params.get("subscribed") === "true") {
      try {
        localStorage.setItem(BROWSER_SUB_KEY, "true");
      } catch (_) {}
      if (postPurchase) {
        postPurchase.style.display = "block";
      }
      try {
        window.history.replaceState({}, document.title, window.location.pathname);
      } catch (_) {}
    }

    if (isBrowserSubscribed() && postPurchase) {
      postPurchase.style.display = "block";
    }
  }

  window.check = check;
  window.scrollToTopCheck = scrollToTopCheck;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  return { check };
})();