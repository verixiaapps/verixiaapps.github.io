const TOKEN_RISK_UPGRADE = (() => {

  if (window.__TOKEN_RISK_EMBEDDED_UPGRADE__) {

    return window.TOKEN_RISK_UPGRADE || {};

  }

  window.__TOKEN_RISK_EMBEDDED_UPGRADE__ = true;

  const config = window.TOKEN_RISK_CONFIG || {};

  const API_BASE = config.apiBase || "";

  const STRIPE_PUBLISHABLE_KEY = config.stripePublishableKey || "";

  const BROWSER_SUB_KEY = config.browserSubKey || "token_risk_browser_subscribed";

  const VERIFIED_SUB_EMAIL_KEY = config.verifiedSubEmailKey || "token_risk_verified_subscriber_email";

  const PRICES = {

    weekly: config?.prices?.weekly || "",

    monthly: config?.prices?.monthly || "",

    yearly: config?.prices?.yearly || ""

  };

  let stripe = null;

  let checkoutInstance = null;

  let selectedPlanKey = PRICES.monthly ? "monthly" : (PRICES.weekly ? "weekly" : "yearly");

  let isInitializingCheckout = false;

  let stripeScriptPromise = null;

  let unlockBtn = null;

  function normalizeEmail(v) {

    return String(v || "").trim().toLowerCase();

  }

  function getEmailInput() {

    return document.getElementById("email");

  }

  function getEnteredEmail() {

    const el = getEmailInput();

    return el ? normalizeEmail(el.value) : "";

  }

  function getStoredVerifiedEmail() {

    try {

      return normalizeEmail(localStorage.getItem(VERIFIED_SUB_EMAIL_KEY));

    } catch {

      return "";

    }

  }

  function setStoredVerifiedEmail(email) {

    if (!email) return;

    try {

      localStorage.setItem(VERIFIED_SUB_EMAIL_KEY, normalizeEmail(email));

    } catch {}

  }

  function isBrowserSubscribed() {

    try {

      return localStorage.getItem(BROWSER_SUB_KEY) === "true";

    } catch {

      return false;

    }

  }

  function markBrowserSubscribed(v) {

    try {

      v

        ? localStorage.setItem(BROWSER_SUB_KEY, "true")

        : localStorage.removeItem(BROWSER_SUB_KEY);

    } catch {}

  }

  function shouldSuppressUpgrade() {

    const stored = getStoredVerifiedEmail();

    const entered = getEnteredEmail();

    return isBrowserSubscribed() && stored && entered && stored === entered;

  }

  function hideLegacyUpgradeUI() {

    const el = document.getElementById("upgrade");

    if (!el) return;

    el.style.display = "none";

    el.setAttribute("hidden", "");

  }

  function setLoadingState(isLoading) {

    if (!unlockBtn) return;

    unlockBtn.disabled = isLoading;

    unlockBtn.textContent = isLoading

      ? "Loading checkout..."

      : "🔓 Unlock Unlimited Checks";

    unlockBtn.style.opacity = isLoading ? "0.7" : "1";

  }

  function patchFetch() {

    if (!window.fetch || window.__FETCH_PATCHED__) return;

    window.__FETCH_PATCHED__ = true;

    const originalFetch = window.fetch.bind(window);

    window.fetch = async (input, init = {}) => {

      let isAnalyze = false;

      let bodyObj = null;

      try {

        const url = typeof input === "string" ? input : input?.url || "";

        isAnalyze = url.includes("/analyze-token");

        if (isAnalyze && init?.body && typeof init.body === "string") {

          try {

            bodyObj = JSON.parse(init.body);

          } catch {

            bodyObj = {};

          }

          const email = normalizeEmail(bodyObj.email || getEnteredEmail());

          const stored = getStoredVerifiedEmail();

          bodyObj.email = email;

          bodyObj.subscribed =

            !!email &&

            !!stored &&

            email === stored &&

            isBrowserSubscribed();

          init = {

            ...init,

            body: JSON.stringify(bodyObj)

          };

        }

      } catch {}

      const res = await originalFetch(input, init);

      if (isAnalyze) {

        res.clone().json().then(data => {

          const isSub =

            data?.subscribed ||

            data?.activeSubscription ||

            data?.hasSubscription ||

            data?.unlimited;

          if (isSub) {

            markBrowserSubscribed(true);

            const email = bodyObj?.email || data?.email;

            if (email) setStoredVerifiedEmail(email);

            hideLegacyUpgradeUI();

            return;

          }

          if (data?.limit && !shouldSuppressUpgrade()) {

            setTimeout(() => window.openEmbeddedUpgrade?.("monthly"), 0);

          }

        }).catch(() => {});

      }

      return res;

    };

  }

  function ensureStripe() {

    if (window.Stripe) return Promise.resolve();

    if (stripeScriptPromise) return stripeScriptPromise;

    stripeScriptPromise = new Promise((resolve, reject) => {

      const existing = document.querySelector('script[src="https://js.stripe.com/v3/"]');

      if (existing) {

        existing.onload = resolve;

        existing.onerror = reject;

        return;

      }

      const s = document.createElement("script");

      s.src = "https://js.stripe.com/v3/";

      s.async = true;

      s.onload = resolve;

      s.onerror = reject;

      document.body.appendChild(s);

    });

    return stripeScriptPromise;

  }

  async function openCheckout(planKey) {

    if (shouldSuppressUpgrade()) return;

    if (!API_BASE || !STRIPE_PUBLISHABLE_KEY) {

      console.error("Missing API_BASE or Stripe key");

      return;

    }

    if (!PRICES[planKey]) {

      console.error("Missing price ID for plan:", planKey);

      return;

    }

    if (isInitializingCheckout) return;

    isInitializingCheckout = true;

    setLoadingState(true);

    try {

      await ensureStripe();

      if (!window.Stripe) throw new Error("Stripe not available");

      if (!stripe) {

        stripe = Stripe(STRIPE_PUBLISHABLE_KEY);

      }

      if (checkoutInstance?.destroy) {

        await checkoutInstance.destroy();

      }

      const mount = document.getElementById("embedded-checkout-mount");

      if (!mount) {

        console.error("Checkout mount missing");

        alert("Unable to load checkout. Please refresh.");

        return;

      }

      const fetchClientSecret = async () => {

        const res = await fetch(API_BASE + "/create-embedded-subscription", {

          method: "POST",

          headers: { "Content-Type": "application/json" },

          body: JSON.stringify({

            priceId: PRICES[planKey],

            returnUrl:

              window.location.origin +

              window.location.pathname +

              "?subscribed=true"

          })

        });

        const data = await res.json();

        if (!data?.clientSecret) {

          throw new Error("No client secret returned");

        }

        return data.clientSecret;

      };

      checkoutInstance = await stripe.initEmbeddedCheckout({

        fetchClientSecret

      });

      checkoutInstance.mount("#embedded-checkout-mount");

    } catch (e) {

      console.error("Checkout error:", e);

      alert("Checkout failed. Please try again.");

    } finally {

      isInitializingCheckout = false;

      setLoadingState(false);

    }

  }

  function buildUI() {

    if (!API_BASE || !STRIPE_PUBLISHABLE_KEY) return;

    if (document.getElementById("embedded-toggle-wrapper")) return;

    const wrapper = document.createElement("div");

    wrapper.id = "embedded-toggle-wrapper";

    unlockBtn = document.createElement("button");

    unlockBtn.textContent = "🔓 Unlock Unlimited Checks";

    unlockBtn.onclick = () => window.openEmbeddedUpgrade("monthly");

    const mount = document.createElement("div");

    mount.id = "embedded-checkout-mount";

    mount.style.marginTop = "12px";

    wrapper.appendChild(unlockBtn);

    wrapper.appendChild(mount);

    document.body.prepend(wrapper);

  }

  window.openEmbeddedUpgrade = async (planKey = "monthly") => {

    if (shouldSuppressUpgrade()) return;

    await openCheckout(planKey);

  };

  function init() {

    hideLegacyUpgradeUI();

    patchFetch();

    buildUI();

  }

  if (document.readyState === "loading") {

    document.addEventListener("DOMContentLoaded", init);

  } else {

    init();

  }

  const api = { init };

  window.TOKEN_RISK_UPGRADE = api;

  return api;

})();