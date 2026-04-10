(function () {
  if (window.__SCAM_CHECK_RUNTIME__) return;
  window.__SCAM_CHECK_RUNTIME__ = true;

  /* =========================
     SAFE HELPERS
  ========================= */

  function safe(fn) {
    try { fn(); } catch (e) {}
  }

  function normalize(str) {
    return String(str || "").replace(/\s+/g, " ").trim();
  }

  function lower(str) {
    return normalize(str).toLowerCase();
  }

  function cleanBase(keyword) {
    let t = normalize(keyword)
      .replace(/^\s*is\s+/i, "")
      .replace(/\s+(scam|legit|real|fake)\s*$/i, "")
      .trim();
    return t;
  }

  function cleanSentence(keyword) {
    return cleanBase(keyword)
      .replace(/\b(message|email|text|link|website|alert|request|offer|scam)s?\b/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function display(str) {
    str = normalize(str);
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
  }

  /* =========================
     INTENT DETECTION
  ========================= */

  function detectIntent(keyword) {
    const k = lower(keyword);

    if (k.startsWith("did i get scammed")) return "post-scam";
    if (k.startsWith("how to") || k.startsWith("what to do")) return "guidance";
    if (k.startsWith("is ") && k.includes(" legit")) return "legit-check";
    if (k.startsWith("is ")) return "scam-check";

    return "default";
  }

  /* =========================
     CONTENT VARIANTS (IMPROVED)
  ========================= */

  function variantA(keyword) {
    const readable = display(keyword);
    const clean = cleanSentence(keyword) || cleanBase(keyword) || keyword;

    return `
<div class="content-block">
<p>${readable} usually shows up when something feels slightly off. Most scam messages are designed to look routine at first, then shift toward urgency or action.</p>

<h2>Is ${clean} a Scam or Legitimate?</h2>
<p>Situations like ${clean} are commonly used in scam campaigns that rely on timing and familiarity. The message often looks normal, but is designed to move you toward clicking a link, logging in, or sending money before verifying.</p>

<h3>Typical Risk Pattern</h3>
<ul>
<li>Unexpected message tied to an account, delivery, or payment</li>
<li>Subtle urgency or “last chance” language</li>
<li>Link or action that bypasses normal app flow</li>
<li>Request for login, code, or payment</li>
</ul>

<h3>How To Check Safely</h3>
<p>Do not use the message itself to verify. Open the official app or website directly and check if the request is real. If nothing matches, the message is very likely part of a scam pattern.</p>
</div>
`;
  }

  function variantB(keyword) {
    const readable = display(keyword);
    const clean = cleanSentence(keyword) || cleanBase(keyword) || keyword;

    return `
<div class="content-block">
<p>${readable} often follows a repeatable scam pattern. It is rarely just one message. Instead, it is part of a sequence designed to build trust and create urgency.</p>

<h2>How ${clean} Messages Work</h2>
<p>The message usually starts with something believable like a delivery, account issue, or payment alert. It then introduces pressure, pushing you to act before checking.</p>

<p>Once engaged, it leads to one of three outcomes: clicking a link, entering information, or sending money.</p>

<h3>Why It Feels Real</h3>
<p>These messages often align with real-world timing. If you recently made a purchase or expected communication, the message feels legitimate.</p>

<h3>What To Watch For</h3>
<ul>
<li>Messages that look official but feel slightly off</li>
<li>Links that redirect outside the platform</li>
<li>Requests that skip normal verification steps</li>
<li>Pressure to act immediately</li>
</ul>

<h3>Safer Approach</h3>
<p>Pause and verify outside the message. Use the official app or website directly. This removes the pressure and exposes fake requests.</p>
</div>
`;
  }

  function variantC(keyword) {
    const readable = display(keyword);
    const clean = cleanSentence(keyword) || cleanBase(keyword) || keyword;

    return `
<div class="content-block">
<p>If you are dealing with ${readable}, the safest move is to slow down. Scam messages depend on speed and reaction.</p>

<h2>What To Do About ${clean}</h2>
<p>Do not click anything immediately. Even legitimate-looking messages should be verified independently before taking action.</p>

<h3>Immediate Safety Steps</h3>
<ul>
<li>Avoid clicking links in the message</li>
<li>Do not enter login or payment details</li>
<li>Check the official app or website manually</li>
<li>Wait before taking action</li>
</ul>

<h3>If You Already Interacted</h3>
<p>Secure your account immediately. Change passwords, review activity, and contact the official service if needed.</p>

<h3>Why This Matters</h3>
<p>Messages like ${clean} are often repeated across many targets. Even if one seems harmless, follow-up attempts may be more aggressive.</p>
</div>
`;
  }

  function getVariant(keyword) {
    const slug = lower(keyword).replace(/\s+/g, "-");
    let hash = 0;
    for (let i = 0; i < slug.length; i++) {
      hash = ((hash << 5) - hash) + slug.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash) % 3;
  }

  /* =========================
     MAIN OVERRIDE
  ========================= */

  function overrideSeoContent() {
    const el = document.getElementById("seoContent");
    if (!el) return;

    if (el.dataset.runtimeInjected === "true") return;
    el.dataset.runtimeInjected = "true";

    const keyword = normalize(window.RAW_KEYWORD || "");

    if (!keyword) return;

    const v = getVariant(keyword);

    let html = "";
    if (v === 0) html = variantA(keyword);
    else if (v === 1) html = variantB(keyword);
    else html = variantC(keyword);

    el.innerHTML = html;
  }

  /* =========================
     INIT (NON-DESTRUCTIVE)
  ========================= */

  function init() {
    safe(overrideSeoContent);
  }

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();