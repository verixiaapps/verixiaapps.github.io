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

  function escapeMaybe(v) {
    return escapeHtml(v == null ? "" : String(v));
  }

  function normalizeRiskClass(v) {
    const x = String(v || "").toLowerCase().trim();
    if (x === "high") return "high";
    if (x === "medium") return "medium";
    if (x === "low") return "low";
    return "unknown";
  }

  function riskLabel(risk) {
    if (risk === "high") return "High Risk";
    if (risk === "medium") return "Moderate Risk";
    if (risk === "low") return "Lower Risk";
    return "Review";
  }

  function summaryForRisk(risk) {
    if (risk === "high") {
      return "Multiple high-risk signals detected. Do not interact until the contract, liquidity, and ownership structure are verified.";
    }
    if (risk === "medium") {
      return "Several warning signals detected. Review contract permissions, liquidity, and holder distribution before acting.";
    }
    if (risk === "low") {
      return "Fewer immediate risk signals detected, but verification is still required before interacting.";
    }
    return "Risk level unclear. Verify contract, liquidity, and ownership before taking action.";
  }

  function compactMoney(v) {
    const n = Number(v);
    if (!Number.isFinite(n)) return "N/A";
    if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
    if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
    if (n >= 1e3) return `$${(n / 1e3).toFixed(2)}K`;
    return `$${n.toLocaleString()}`;
  }

  function compactPercent(v) {
    const n = Number(v);
    if (!Number.isFinite(n)) return "N/A";
    return `${n >= 0 ? "+" : ""}${n.toFixed(2)}%`;
  }

  function metricRow(label, value, cls) {
    return `
      <div class="token-metric-row">
        <div class="token-metric-label">${label}</div>
        <div class="token-metric-value ${cls || ""}">${escapeMaybe(value)}</div>
      </div>
    `;
  }

  function listBlock(items, fallback) {
    const arr = Array.isArray(items)
      ? items.map(x => String(x || "").trim()).filter(Boolean)
      : [];

    const rows = arr.length ? arr : [fallback];

    return rows.map(x => `<li>${escapeMaybe(x)}</li>`).join("");
  }

  function formatTokenResult(data) {
    const a = data.analysis || {};
    const m = data.tokenMetrics || {};
    const t = data.tokenData || {};
    const risk = normalizeRiskClass(a.riskLevel);

    const priceChange = Number(m.priceChange24h);
    const priceCls = Number.isFinite(priceChange)
      ? priceChange >= 0 ? "positive" : "negative"
      : "";

    return `
      <div class="token-analysis-wrap">
        <div class="token-analysis-card">

          <div class="token-risk-pill ${risk}">
            ${riskLabel(risk)}
          </div>

          <div class="token-meta-line">
            ${escapeMaybe(t.symbol || t.name || "Token")}
          </div>

          <div class="token-summary-inline">
            ${escapeMaybe(summaryForRisk(risk))}
          </div>

          <div class="token-metric-stack">
            ${metricRow("Liquidity", compactMoney(m.liquidityUsd))}
            ${metricRow("Volume 24h", compactMoney(m.volume24h))}
            ${metricRow("Price 24h", compactPercent(m.priceChange24h), priceCls)}
            ${metricRow("Pair Age", m.pairAge || "N/A")}
            ${metricRow("FDV", compactMoney(m.fdv))}
          </div>

          <div class="token-section">
            <div class="token-section-title">Key Signals</div>
            <ul class="token-list">
              ${listBlock(
                a.concerningIndicators,
                "No strong negative signals were returned."
              )}
            </ul>
          </div>

          <div class="token-section">
            <div class="token-section-title">Positive Signals</div>
            <ul class="token-list">
              ${listBlock(
                a.legitimateElements,
                "No strong positive signals were returned."
              )}
            </ul>
          </div>

          <div class="token-section">
            <div class="token-section-title">What To Watch</div>
            <ul class="token-list">
              ${listBlock(
                a.recommendations,
                "Verify before interacting with this token."
              )}
            </ul>
          </div>

          <div class="token-section">
            <div class="token-section-title">Final Take</div>
            <div class="token-final-take ${risk}">
              ${escapeMaybe(a.finalTake || "Proceed carefully.")}
            </div>
          </div>

          <div class="token-cta-row">
            <button class="check result-cta" onclick="scrollToTopCheck()">Check Another Token</button>
          </div>

        </div>
      </div>
    `;
  }

  function renderState(title, sub, chip, cls) {
    return `
      <div class="result-card ${cls || "unknown"}">
        <div class="result-top">
          <div class="risk">${title}</div>
          <div class="result-chip">${chip}</div>
        </div>
        <div class="result-summary">${sub}</div>
      </div>
    `;
  }

  function renderEmpty() {
    return renderState(
      "Paste Token Address",
      "Enter a contract address to review token risk.",
      "Awaiting Input"
    );
  }

  function renderLoading() {
    return renderState(
      "Checking Token",
      "Analyzing liquidity, trading behavior, and contract signals.",
      "In Progress"
    );
  }

  function renderLimit() {
    return renderState(
      "Free Limit Reached",
      "Upgrade to continue checking tokens.",
      "Upgrade",
      "medium"
    );
  }

  function renderError(msg) {
    return renderState(
      "Unable To Analyze",
      msg || "Try again shortly.",
      "Error"
    );
  }

  async function parseJsonSafe(res) {
    try {
      return await res.json();
    } catch {
      return null;
    }
  }

  async function check() {
    const tokenAddress = (document.getElementById("tokenAddress")?.value || "").trim();
    const email = (document.getElementById("email")?.value || "").trim();
    const subscribed = isBrowserSubscribed();
    const result = document.getElementById("result");

    if (!result) return;

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
      const res = await fetch(`${API}/analyze-token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tokenAddress, email, subscribed })
      });

      const data = await parseJsonSafe(res);

      if (!res.ok) {
        result.innerHTML = renderError(data?.error);
        return;
      }

      if (data?.limit) {
        result.innerHTML = renderLimit();
        window.showUpgrade?.();
        return;
      }

      if (data?.analysis) {
        result.innerHTML = formatTokenResult(data);
        return;
      }

      result.innerHTML = renderError("No analysis returned.");
    } catch {
      result.innerHTML = renderError();
    }
  }

  function scrollToTopCheck() {
    const el = document.getElementById("tokenAddress");
    if (!el) return;
    window.scrollTo({ top: 0, behavior: "smooth" });
    setTimeout(() => el.focus(), 300);
  }

  function init() {
    const params = new URLSearchParams(window.location.search);
    const post = document.getElementById("postPurchase");

    if (params.get("subscribed") === "true") {
      try { localStorage.setItem(BROWSER_SUB_KEY, "true"); } catch {}
      if (post) post.style.display = "block";
    }

    if (isBrowserSubscribed() && post) {
      post.style.display = "block";
    }
  }

  window.check = check;
  window.scrollToTopCheck = scrollToTopCheck;

  document.readyState === "loading"
    ? document.addEventListener("DOMContentLoaded", init)
    : init();

  return { check };
})();