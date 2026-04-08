const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();

const TARGET_DIRS = [
  "scam-check-now",
  "scam-check-now-b",
  "scam-check-now-c"
];

const START_MARKER = "<!-- SCAM_CHECK_EMBEDDED_UPGRADE_START -->";
const END_MARKER = "<!-- SCAM_CHECK_EMBEDDED_UPGRADE_END -->";

const BROWSER_SNIPPET = String.raw`(function () {
  if (window.__SCAM_CHECK_EMBEDDED_UPGRADE__) return;
  window.__SCAM_CHECK_EMBEDDED_UPGRADE__ = true;

  const API_BASE = "https://awake-integrity-production-faa0.up.railway.app";
  const STRIPE_PUBLISHABLE_KEY = "pk_live_51T83ANJjMzyHDzeQlrggekWLypSX5CUd01DW8gCqjo32KnKrDsdDtg61CbbrJUzMF82T4z5INGWROuLMlIfp1zKE00oMYmW08Y";
  const ADS_ID = "AW-17956428385";
  const ADS_SEND_TO = "AW-17956428385/dE43CO04_IUcEOGopfJC";
  const BROWSER_SUB_KEY = "scam_check_browser_subscribed";
  const VERIFIED_SUB_EMAIL_KEY = "scam_check_verified_subscriber_email";

  const PRICES = {
    weekly: "price_1T8KOTJjMzyHDzeQDDg1A2TF",
    monthly: "price_1T8KOUJjMzyHDzeQxaqPFOSB",
    yearly: "price_1T8KOQJjMzyHDzeQfcU1C1MQ"
  };

  let stripe = null;
  let checkoutInstance = null;
  let selectedPlanKey = "monthly";
  let isInitializingCheckout = false;
  let stripeScriptPromise = null;
  let legacyUpgradeObserver = null;

  let wrapper;
  let buttonRow;
  let button;
  let checkoutCard;
  let compactRow;
  let compactText;
  let changePlanBtn;
  let planRow;
  let weeklyBtn;
  let monthlyBtn;
  let yearlyBtn;
  let helper;
  let checkoutContainer;
  let status;
  let closeBtn;

  function normalizeEmail(value) {
    return String(value || "").trim().toLowerCase();
  }

  function getEmailInput() {
    return document.getElementById("email");
  }

  function getEnteredEmail() {
    const input = getEmailInput();
    return input ? normalizeEmail(input.value) : "";
  }

  function getStoredVerifiedEmail() {
    return normalizeEmail(localStorage.getItem(VERIFIED_SUB_EMAIL_KEY) || "");
  }

  function setStoredVerifiedEmail(email) {
    const normalized = normalizeEmail(email);
    if (normalized) {
      localStorage.setItem(VERIFIED_SUB_EMAIL_KEY, normalized);
    }
  }

  function isBrowserSubscribed() {
    return localStorage.getItem(BROWSER_SUB_KEY) === "true";
  }

  function markBrowserSubscribed(value) {
    if (value) {
      localStorage.setItem(BROWSER_SUB_KEY, "true");
    } else {
      localStorage.removeItem(BROWSER_SUB_KEY);
    }
  }

  function isVerifiedSubscriberForCurrentUser() {
    const storedEmail = getStoredVerifiedEmail();
    const enteredEmail = getEnteredEmail();

    if (!isBrowserSubscribed()) return false;
    if (!storedEmail) return false;
    if (!enteredEmail) return false;

    return enteredEmail === storedEmail;
  }

  function shouldSuppressUpgrade() {
    return isVerifiedSubscriberForCurrentUser();
  }

  function syncPostPurchaseMessage() {
    const postPurchase = document.getElementById("postPurchase");
    if (!postPurchase) return;

    postPurchase.textContent = "✅ Unlimited scam checks are active with this account";
    postPurchase.style.display = shouldSuppressUpgrade() ? "block" : "none";
  }

  function setStatus(text) {
    if (status) status.textContent = text || "";
  }

  function injectLegacyUpgradeKillCSS() {
    if (document.getElementById("scam-check-hide-legacy-upgrade")) return;

    const style = document.createElement("style");
    style.id = "scam-check-hide-legacy-upgrade";
    style.textContent = \`
      #upgrade {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
        opacity: 0 !important;
        max-height: 0 !important;
        min-height: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        border: 0 !important;
      }
    \`;
    document.head.appendChild(style);
  }

  function hideLegacyUpgradeUI() {
    const oldUpgrade = document.getElementById("upgrade");
    if (oldUpgrade) {
      oldUpgrade.style.setProperty("display", "none", "important");
      oldUpgrade.style.setProperty("visibility", "hidden", "important");
      oldUpgrade.style.setProperty("pointer-events", "none", "important");
      oldUpgrade.style.setProperty("opacity", "0", "important");
      oldUpgrade.style.setProperty("max-height", "0", "important");
      oldUpgrade.style.setProperty("min-height", "0", "important");
      oldUpgrade.style.setProperty("height", "0", "important");
      oldUpgrade.style.setProperty("overflow", "hidden", "important");
      oldUpgrade.style.setProperty("margin", "0", "important");
      oldUpgrade.style.setProperty("padding", "0", "important");
      oldUpgrade.style.setProperty("border", "0", "important");
      oldUpgrade.setAttribute("hidden", "");
      oldUpgrade.setAttribute("aria-hidden", "true");
    }
  }

  function watchLegacyUpgradeUI() {
    if (legacyUpgradeObserver) return;

    legacyUpgradeObserver = new MutationObserver(function () {
      hideLegacyUpgradeUI();
    });

    legacyUpgradeObserver.observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["style", "class"]
    });
  }

  function ensureAdsScript() {
    if (document.querySelector('script[src*="googletagmanager.com/gtag/js?id=' + ADS_ID + '"]')) {
      return;
    }
    const s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + ADS_ID;
    document.head.appendChild(s);
  }

  function ensureGtag() {
    ensureAdsScript();
    window.dataLayer = window.dataLayer || [];
    if (!window.gtag) {
      window.gtag = function () { window.dataLayer.push(arguments); };
    }
    try {
      window.gtag("js", new Date());
      window.gtag("config", ADS_ID);
    } catch (e) {}
  }

  function handleReturnState() {
    ensureGtag();

    const params = new URLSearchParams(window.location.search);
    const hasConversion = params.get("conversion") === "1";
    const hasSubscribed = params.get("subscribed") === "true";

    if (hasConversion && !sessionStorage.getItem("ads_conversion")) {
      try {
        window.gtag("event", "conversion", {
          send_to: ADS_SEND_TO,
          value: 10.0,
          currency: "USD"
        });
        sessionStorage.setItem("ads_conversion", "1");
      } catch (e) {}
    }

    if (hasSubscribed) {
      markBrowserSubscribed(true);
    }

    syncPostPurchaseMessage();

    if (hasConversion || hasSubscribed) {
      try {
        window.history.replaceState({}, document.title, window.location.pathname);
      } catch (e) {}
    }
  }

  function patchTopUpgradeButton() {
    const topBtn = document.querySelector(".upgrade-top");
    if (!topBtn) return;
    topBtn.setAttribute("type", "button");
    topBtn.removeAttribute("onclick");
    topBtn.onclick = function (e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      if (shouldSuppressUpgrade()) {
        hideLegacyUpgradeUI();
        return false;
      }
      hideLegacyUpgradeUI();
      if (window.openEmbeddedUpgrade) {
        window.openEmbeddedUpgrade("monthly");
      }
      return false;
    };
  }

  function patchHostedCheckoutFallback() {
    window.checkout = async function (priceId) {
      if (shouldSuppressUpgrade()) {
        hideLegacyUpgradeUI();
        return;
      }

      const pageUrl = window.location.origin + window.location.pathname;

      try {
        const response = await fetch(API_BASE + "/create-checkout", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            priceId,
            email: null,
            successUrl: pageUrl + "?subscribed=true&conversion=1",
            cancelUrl: pageUrl
          })
        });

        const data = await response.json();

        if (data && data.url) {
          window.location = data.url;
        } else {
          alert("Checkout failed. Please try again.");
        }
      } catch (e) {
        alert("Checkout failed. Please try again.");
      }
    };
  }

  function patchShowUpgrade() {
    window.showUpgrade = function () {
      hideLegacyUpgradeUI();
      return;
    };
  }

  function patchAnalyzeLimitAutoOpen() {
    if (!window.fetch || window.__SCAM_CHECK_FETCH_PATCHED__) return;
    window.__SCAM_CHECK_FETCH_PATCHED__ = true;

    const originalFetch = window.fetch.bind(window);

    window.fetch = async function (input, init) {
      let requestUrl = "";
      let isAnalyzeRequest = false;
      let parsedBody = null;

      try {
        requestUrl = typeof input === "string" ? input : (input && input.url ? input.url : "");
        isAnalyzeRequest = !!requestUrl && requestUrl.indexOf("/analyze") !== -1;

        if (isAnalyzeRequest && init && typeof init.body === "string") {
          try {
            parsedBody = JSON.parse(init.body);
          } catch (e) {
            parsedBody = null;
          }

          if (parsedBody && typeof parsedBody === "object") {
            const enteredEmail = normalizeEmail(parsedBody.email || getEnteredEmail());
            parsedBody.email = enteredEmail;

            if (Object.prototype.hasOwnProperty.call(parsedBody, "subscribed")) {
              delete parsedBody.subscribed;
            }

            init = Object.assign({}, init, { body: JSON.stringify(parsedBody) });
          }
        }
      } catch (e) {}

      const response = await originalFetch(input, init);

      try {
        if (isAnalyzeRequest) {
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
                if (window.openEmbeddedUpgrade) {
                  window.openEmbeddedUpgrade("monthly");
                }
              }, 0);
            }
          }).catch(function () {});
        }
      } catch (e) {}

      return response;
    };
  }

  function patchLegacyButtons() {
    const buttons = Array.from(document.querySelectorAll('button[onclick], .upgrade-top'));
    buttons.forEach(function (btn) {
      const onclickText = (btn.getAttribute("onclick") || "").trim();
      const text = (btn.textContent || "").toLowerCase().trim();

      if (onclickText === "showUpgrade()" || text.includes("upgrade")) {
        btn.removeAttribute("onclick");
        btn.onclick = function (e) {
          if (e) {
            e.preventDefault();
            e.stopPropagation();
          }

          if (shouldSuppressUpgrade()) {
            hideLegacyUpgradeUI();
            return false;
          }

          hideLegacyUpgradeUI();
          if (window.openEmbeddedUpgrade) {
            window.openEmbeddedUpgrade("monthly");
          }
          return false;
        };
      }
    });
  }

  function patchSubscriberEmailField() {
    const input = getEmailInput();
    if (!input || input.__SCAM_CHECK_EMAIL_PATCHED__) return;

    input.__SCAM_CHECK_EMAIL_PATCHED__ = true;
    input.addEventListener("input", function () {
      syncPostPurchaseMessage();
      hideLegacyUpgradeUI();
    });
  }

  function ensureStripeScript() {
    if (window.Stripe) return Promise.resolve();

    if (stripeScriptPromise) return stripeScriptPromise;

    stripeScriptPromise = new Promise(function (resolve, reject) {
      const existing = document.querySelector('script[src="https://js.stripe.com/v3/"]');
      if (existing) {
        if (window.Stripe) {
          resolve();
          return;
        }
        existing.addEventListener("load", function () { resolve(); }, { once: true });
        existing.addEventListener("error", function () { reject(new Error("Stripe failed to load.")); }, { once: true });
        return;
      }

      const s = document.createElement("script");
      s.src = "https://js.stripe.com/v3/";
      s.async = true;
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error("Stripe failed to load.")); };
      document.body.appendChild(s);
    });

    return stripeScriptPromise;
  }

  function getPlanButtonByKey(key) {
    return { weekly: weeklyBtn, monthly: monthlyBtn, yearly: yearlyBtn }[key] || monthlyBtn;
  }

  function updateCompactSummary(key) {
    const btn = getPlanButtonByKey(key);
    if (!btn || !compactText) return;
    compactText.innerHTML =
      '<div style="font-size:12px;color:#d4e0f2;font-weight:700;">Selected plan</div>' +
      '<div style="margin-top:2px;">' + btn.dataset.planLabel + ' • ' + btn.dataset.planSubLabel + '</div>';
  }

  function setActivePlan(key) {
    [weeklyBtn, monthlyBtn, yearlyBtn].forEach(function (btn) {
      if (!btn) return;
      const isActive = btn.dataset.planKey === key;
      btn.dataset.active = isActive ? "true" : "false";
      btn.style.background = isActive
        ? "linear-gradient(135deg, rgba(134,121,247,.25) 0%, rgba(44,198,232,.22) 100%)"
        : "rgba(255,255,255,.05)";
      btn.style.borderColor = isActive
        ? "rgba(102,217,239,.55)"
        : "rgba(255,255,255,.12)";
      btn.style.boxShadow = isActive
        ? "0 0 0 1px rgba(102,217,239,.20) inset"
        : "none";
      btn.style.transform = "translateY(0)";
    });

    updateCompactSummary(key);
  }

  function showPlanSelector() {
    if (!compactRow || !planRow || !helper) return;
    compactRow.style.display = "none";
    planRow.style.display = "grid";
    helper.style.display = "block";
  }

  function showCompactSelector() {
    if (!compactRow || !planRow || !helper) return;
    compactRow.style.display = "flex";
    planRow.style.display = "none";
    helper.style.display = "none";
  }

  async function destroyEmbeddedCheckout() {
    if (checkoutInstance && typeof checkoutInstance.destroy === "function") {
      try {
        await checkoutInstance.destroy();
      } catch (e) {}
    }

    checkoutInstance = null;

    if (checkoutContainer) {
      checkoutContainer.innerHTML = "";
      checkoutContainer.style.display = "none";
      checkoutContainer.style.minHeight = "0";
      checkoutContainer.style.paddingBottom = "0";
    }
  }

  async function openCheckoutForPlan(planKey) {
    if (shouldSuppressUpgrade()) {
      hideLegacyUpgradeUI();
      return;
    }
    if (isInitializingCheckout) return;
    if (!PRICES[planKey]) return;

    isInitializingCheckout = true;
    selectedPlanKey = planKey;
    setActivePlan(planKey);
    showCompactSelector();
    helper.textContent = "Loading secure checkout...";
    setStatus("");
    checkoutContainer.style.display = "block";
    checkoutContainer.style.minHeight = "360px";
    checkoutContainer.innerHTML = "";

    try {
      await ensureStripeScript();

      if (!window.Stripe) {
        throw new Error("Stripe failed to load.");
      }

      if (!stripe) {
        stripe = Stripe(STRIPE_PUBLISHABLE_KEY);
      }

      await destroyEmbeddedCheckout();

      checkoutContainer.style.display = "block";
      checkoutContainer.style.minHeight = "520px";
      checkoutContainer.style.paddingBottom = "24px";

      const fetchClientSecret = async function () {
        const res = await fetch(API_BASE + "/create-embedded-subscription", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            priceId: PRICES[planKey],
            returnUrl: window.location.origin + window.location.pathname + "?subscribed=true&conversion=1"
          })
        });

        const data = await res.json();

        if (!res.ok || !data || !data.clientSecret) {
          throw new Error((data && data.error) || "No clientSecret");
        }

        return data.clientSecret;
      };

      checkoutInstance = await stripe.createEmbeddedCheckoutPage({
        fetchClientSecret: fetchClientSecret
      });

      checkoutInstance.mount("#embedded-checkout-mount");
      helper.textContent = "Complete payment below.";
    } catch (e) {
      console.error("Embedded checkout error:", e);
      await destroyEmbeddedCheckout();
      showPlanSelector();
      helper.textContent = "Select a plan to load secure checkout.";
      checkoutContainer.innerHTML = "Unable to load checkout.";
      checkoutContainer.style.display = "block";
      checkoutContainer.style.minHeight = "100px";
      setStatus("Please try again.");
    } finally {
      isInitializingCheckout = false;
    }
  }

  async function openSelectorInternal() {
    if (!checkoutCard || !buttonRow) return;

    if (shouldSuppressUpgrade()) {
      hideLegacyUpgradeUI();
      return;
    }

    hideLegacyUpgradeUI();
    await destroyEmbeddedCheckout();
    buttonRow.style.display = "none";
    checkoutCard.style.display = "block";
    setActivePlan(selectedPlanKey);
    showPlanSelector();
    helper.textContent = "Select a plan to load secure checkout.";
    setStatus("");
  }

  async function closeCheckoutInternal() {
    await destroyEmbeddedCheckout();
    checkoutCard.style.display = "none";
    buttonRow.style.display = shouldSuppressUpgrade() ? "none" : "flex";
    helper.textContent = "Select a plan to load secure checkout.";
    setStatus("");
    showPlanSelector();
  }

  function makePlanButton(label, sublabel, key) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.dataset.planKey = key;
    btn.dataset.planLabel = label;
    btn.dataset.planSubLabel = sublabel;
    btn.style.padding = "12px 10px";
    btn.style.borderRadius = "14px";
    btn.style.border = "1px solid rgba(255,255,255,.12)";
    btn.style.background = "rgba(255,255,255,.05)";
    btn.style.color = "#fff";
    btn.style.cursor = "pointer";
    btn.style.textAlign = "left";
    btn.style.minHeight = "72px";
    btn.style.boxShadow = "none";
    btn.style.transition = "transform .15s ease, border-color .15s ease, background .15s ease";

    const top = document.createElement("div");
    top.textContent = label;
    top.style.fontSize = "14px";
    top.style.fontWeight = "900";
    top.style.lineHeight = "1.2";

    const bottom = document.createElement("div");
    bottom.textContent = sublabel;
    bottom.style.fontSize = "12px";
    bottom.style.color = "#d4e0f2";
    bottom.style.marginTop = "5px";
    bottom.style.lineHeight = "1.3";

    btn.appendChild(top);
    btn.appendChild(bottom);

    btn.addEventListener("mouseenter", function () {
      if (btn.dataset.active !== "true") {
        btn.style.transform = "translateY(-1px)";
      }
    });

    btn.addEventListener("mouseleave", function () {
      btn.style.transform = "translateY(0)";
    });

    return btn;
  }

  function buildEmbeddedUI() {
    if (document.getElementById("embedded-toggle-wrapper")) return;

    wrapper = document.createElement("div");
    wrapper.id = "embedded-toggle-wrapper";
    wrapper.style.maxWidth = "820px";
    wrapper.style.margin = "12px auto 16px";
    wrapper.style.padding = "0 12px";
    wrapper.style.boxSizing = "border-box";

    buttonRow = document.createElement("div");
    buttonRow.style.display = shouldSuppressUpgrade() ? "none" : "flex";
    buttonRow.style.justifyContent = "flex-start";

    button = document.createElement("button");
    button.type = "button";
    button.innerText = "🔓 Unlock Unlimited Checks";
    button.style.padding = "10px 14px";
    button.style.borderRadius = "999px";
    button.style.fontWeight = "900";
    button.style.fontSize = "14px";
    button.style.background = "linear-gradient(135deg,#8679f7,#2cc6e8)";
    button.style.color = "#fff";
    button.style.border = "none";
    button.style.cursor = "pointer";
    button.style.boxShadow = "0 10px 24px rgba(44,198,232,.18)";
    buttonRow.appendChild(button);

    checkoutCard = document.createElement("div");
    checkoutCard.style.display = "none";
    checkoutCard.style.marginTop = "12px";
    checkoutCard.style.background = "linear-gradient(180deg, rgba(18,31,57,.92) 0%, rgba(11,20,39,.97) 100%)";
    checkoutCard.style.border = "1px solid rgba(255,255,255,.10)";
    checkoutCard.style.borderRadius = "22px";
    checkoutCard.style.padding = "16px";
    checkoutCard.style.boxShadow = "0 22px 56px rgba(2,6,23,.28)";
    checkoutCard.style.color = "#fff";

    const title = document.createElement("div");
    title.textContent = "Unlock unlimited scam checks instantly";
    title.style.fontSize = "22px";
    title.style.fontWeight = "900";
    title.style.marginBottom = "6px";

    const sub = document.createElement("div");
    sub.textContent = "Continue with your selected plan below.";
    sub.style.fontSize = "14px";
    sub.style.color = "#d4e0f2";
    sub.style.marginBottom = "12px";

    compactRow = document.createElement("div");
    compactRow.style.display = "none";
    compactRow.style.alignItems = "center";
    compactRow.style.justifyContent = "space-between";
    compactRow.style.gap = "10px";
    compactRow.style.marginBottom = "12px";
    compactRow.style.padding = "10px 12px";
    compactRow.style.borderRadius = "14px";
    compactRow.style.background = "rgba(255,255,255,.05)";
    compactRow.style.border = "1px solid rgba(255,255,255,.10)";

    compactText = document.createElement("div");
    compactText.style.fontSize = "13px";
    compactText.style.lineHeight = "1.35";
    compactText.style.color = "#fff";
    compactText.style.fontWeight = "800";

    changePlanBtn = document.createElement("button");
    changePlanBtn.type = "button";
    changePlanBtn.textContent = "Change";
    changePlanBtn.style.padding = "8px 12px";
    changePlanBtn.style.borderRadius = "999px";
    changePlanBtn.style.border = "1px solid rgba(255,255,255,.14)";
    changePlanBtn.style.background = "rgba(255,255,255,.06)";
    changePlanBtn.style.color = "#fff";
    changePlanBtn.style.fontWeight = "800";
    changePlanBtn.style.cursor = "pointer";
    changePlanBtn.style.flex = "0 0 auto";

    compactRow.appendChild(compactText);
    compactRow.appendChild(changePlanBtn);

    planRow = document.createElement("div");
    planRow.style.display = "grid";
    planRow.style.gridTemplateColumns = "repeat(3, minmax(0,1fr))";
    planRow.style.gap = "10px";
    planRow.style.marginBottom = "12px";

    weeklyBtn = makePlanButton("Weekly", "$3.99 / week", "weekly");
    monthlyBtn = makePlanButton("Monthly", "$11.99 / month", "monthly");
    yearlyBtn = makePlanButton("Yearly", "$39.99 / year", "yearly");

    planRow.appendChild(weeklyBtn);
    planRow.appendChild(monthlyBtn);
    planRow.appendChild(yearlyBtn);

    helper = document.createElement("div");
    helper.textContent = "Select a plan to load secure checkout.";
    helper.style.fontSize = "13px";
    helper.style.color = "#d4e0f2";
    helper.style.marginBottom = "10px";
    helper.style.lineHeight = "1.45";

    checkoutContainer = document.createElement("div");
    checkoutContainer.id = "embedded-checkout-mount";
    checkoutContainer.style.minHeight = "0";
    checkoutContainer.style.borderRadius = "16px";
    checkoutContainer.style.overflow = "hidden";
    checkoutContainer.style.display = "none";

    status = document.createElement("div");
    status.style.marginTop = "10px";
    status.style.fontSize = "13px";
    status.style.lineHeight = "1.45";
    status.style.color = "#d4e2f5";

    closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.textContent = "Close";
    closeBtn.style.marginTop = "12px";
    closeBtn.style.padding = "10px 14px";
    closeBtn.style.borderRadius = "12px";
    closeBtn.style.border = "1px solid rgba(255,255,255,.14)";
    closeBtn.style.background = "rgba(255,255,255,.06)";
    closeBtn.style.color = "#fff";
    closeBtn.style.fontWeight = "800";
    closeBtn.style.cursor = "pointer";

    checkoutCard.appendChild(title);
    checkoutCard.appendChild(sub);
    checkoutCard.appendChild(compactRow);
    checkoutCard.appendChild(planRow);
    checkoutCard.appendChild(helper);
    checkoutCard.appendChild(checkoutContainer);
    checkoutCard.appendChild(status);
    checkoutCard.appendChild(closeBtn);

    wrapper.appendChild(buttonRow);
    wrapper.appendChild(checkoutCard);

    const target = document.querySelector(".container");
    if (target) {
      const toolShell = target.querySelector(".tool-shell") || document.querySelector(".tool-shell");
      if (toolShell) {
        target.insertBefore(wrapper, toolShell);
      } else {
        target.insertBefore(wrapper, target.firstChild);
      }
    } else {
      document.body.insertBefore(wrapper, document.body.firstChild);
    }

    button.addEventListener("click", function () {
      if (shouldSuppressUpgrade()) {
        hideLegacyUpgradeUI();
        return;
      }
      window.openEmbeddedUpgrade("monthly");
    });

    weeklyBtn.addEventListener("click", function () {
      openCheckoutForPlan("weekly");
    });

    monthlyBtn.addEventListener("click", function () {
      openCheckoutForPlan("monthly");
    });

    yearlyBtn.addEventListener("click", function () {
      openCheckoutForPlan("yearly");
    });

    closeBtn.addEventListener("click", function () {
      closeCheckoutInternal();
    });

    changePlanBtn.addEventListener("click", async function () {
      await destroyEmbeddedCheckout();
      showPlanSelector();
      helper.textContent = "Select a plan to load secure checkout.";
      setStatus("");
      setActivePlan(selectedPlanKey);
    });

    if (window.innerWidth <= 640) {
      planRow.style.gridTemplateColumns = "1fr";
      compactRow.style.flexDirection = "column";
      compactRow.style.alignItems = "stretch";
    }

    setActivePlan(selectedPlanKey);
  }

  window.openSelector = async function () {
    if (shouldSuppressUpgrade()) {
      hideLegacyUpgradeUI();
      return;
    }

    await openSelectorInternal();

    setTimeout(function () {
      const el = document.getElementById("embedded-toggle-wrapper");
      if (el) {
        try {
          el.scrollIntoView({ behavior: "smooth", block: "start" });
        } catch (e) {}
      }
    }, 120);
  };

  window.openEmbeddedUpgrade = async function (planKey) {
    if (shouldSuppressUpgrade()) {
      hideLegacyUpgradeUI();
      return;
    }

    await openSelectorInternal();

    setTimeout(function () {
      const el = document.getElementById("embedded-toggle-wrapper");
      if (el) {
        try {
          el.scrollIntoView({ behavior: "smooth", block: "start" });
        } catch (e) {}
      }
    }, 120);

    if (planKey && PRICES[planKey]) {
      openCheckoutForPlan(planKey);
    }
  };

  function init() {
    injectLegacyUpgradeKillCSS();
    hideLegacyUpgradeUI();
    watchLegacyUpgradeUI();
    handleReturnState();
    patchTopUpgradeButton();
    patchHostedCheckoutFallback();
    patchShowUpgrade();
    patchAnalyzeLimitAutoOpen();
    patchLegacyButtons();
    patchSubscriberEmailField();
    buildEmbeddedUI();
    syncPostPurchaseMessage();

    setTimeout(function () {
      hideLegacyUpgradeUI();
      patchLegacyButtons();
      patchSubscriberEmailField();
      syncPostPurchaseMessage();
    }, 0);

    setTimeout(function () {
      hideLegacyUpgradeUI();
      patchLegacyButtons();
      patchSubscriberEmailField();
      syncPostPurchaseMessage();
    }, 150);
  }

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();`;

function walk(dir, results = []) {
  if (!fs.existsSync(dir)) return results;

  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      walk(fullPath, results);
      continue;
    }

    if (entry.isFile() && entry.name === "index.html") {
      results.push(fullPath);
    }
  }

  return results;
}

function upsertManagedBlock(html) {
  const managedBlock = `${START_MARKER}
<script>
${BROWSER_SNIPPET}
</script>
${END_MARKER}`;

  const managedRegex = new RegExp(
    `${escapeRegex(START_MARKER)}[\\s\\S]*?${escapeRegex(END_MARKER)}`,
    "g"
  );

  if (managedRegex.test(html)) {
    return html.replace(managedRegex, managedBlock);
  }

  if (html.includes("</body>")) {
    return html.replace("</body>", `${managedBlock}\n</body>`);
  }

  return `${html}\n${managedBlock}\n`;
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function main() {
  const targetFiles = TARGET_DIRS.flatMap((dir) => walk(path.join(ROOT, dir)));

  if (!targetFiles.length) {
    console.log("No index.html files found in target directories.");
    process.exit(0);
  }

  let updatedCount = 0;

  for (const filePath of targetFiles) {
    const original = fs.readFileSync(filePath, "utf8");
    const updated = upsertManagedBlock(original);

    if (updated !== original) {
      fs.writeFileSync(filePath, updated, "utf8");
      updatedCount += 1;
      console.log(`Updated: ${path.relative(ROOT, filePath)}`);
    } else {
      console.log(`No change: ${path.relative(ROOT, filePath)}`);
    }
  }

  console.log(`Done. Updated ${updatedCount} file(s).`);
}

main();