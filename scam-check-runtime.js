(function () {
  if (window.__SCAM_CHECK_RUNTIME__) return;
  window.__SCAM_CHECK_RUNTIME__ = true;

  function safe(fn) {
    try { fn(); } catch (e) {}
  }

  function normalize(str) {
    return String(str || "").replace(/\s+/g, " ").trim();
  }

  function cleanSeoContent() {
    const el = document.getElementById("seoContent");
    if (!el) return;

    if (el.dataset.runtimePolished === "true") return;
    el.dataset.runtimePolished = "true";

    el.innerHTML = String(el.innerHTML || "")
      .replace(/\*\*/g, "")
      .replace(/<p>\s*<\/p>/gi, "")
      .replace(/&nbsp;/gi, " ")
      .trim();

    const blocks = el.querySelectorAll("h1, h2, h3, h4, h5, h6, p, li");
    blocks.forEach(function (node) {
      if (node.children.length === 0) {
        node.textContent = normalize(node.textContent);
      }
    });

    const emptyBlocks = el.querySelectorAll("p, h1, h2, h3, h4, h5, h6, li");
    emptyBlocks.forEach(function (node) {
      if (!normalize(node.textContent)) {
        node.remove();
      }
    });
  }

  function init() {
    safe(cleanSeoContent);
  }

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();