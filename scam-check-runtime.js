(function () {
  if (window.__SCAM_CHECK_RUNTIME__) return;
  window.__SCAM_CHECK_RUNTIME__ = true;

  function safe(fn) {
    try { fn(); } catch (e) {}
  }

  function normalize(str) {
    return String(str || "")
      .replace(/\s+/g, " ")
      .replace(/\u00A0/g, " ")
      .trim();
  }

  function textOf(node) {
    return normalize(node ? node.textContent : "");
  }

  function removeNode(node) {
    if (node && node.parentNode) node.parentNode.removeChild(node);
  }

  function isProbablyGenericHeading(text) {
    const t = normalize(text).toLowerCase();
    return [
      "common warning signs",
      "how to verify safely",
      "what to do next",
      "frequently asked questions",
      "faq",
      "not sure if this is a scam?",
      "how legitimate and scam versions usually differ",
      "signs this might be a scam",
      "how to respond safely"
    ].includes(t);
  }

  function isWeakSeoParagraph(text) {
    const t = normalize(text).toLowerCase();
    if (!t) return true;

    const weakPatterns = [
      "scam attempts often rely on speed",
      "slowing down is one of the simplest ways",
      "do not use the message itself to verify",
      "open the official app or website directly",
      "independent verification matters more than anything",
      "if you have not clicked yet",
      "if you already clicked",
      "look for pressure",
      "open the official website or app yourself",
      "secure the affected account",
      "messages like this are one of the most common ways people lose money",
      "when something feels off",
      "pause and verify it through official sources",
      "these are the signals that should make you slow down",
      "use the checker first if you want a fast risk review"
    ];

    return weakPatterns.some((p) => t.includes(p));
  }

  function getLargeParagraphs(container) {
    if (!container) return [];

    return Array.from(container.querySelectorAll("p"))
      .map((p) => ({
        node: p,
        text: normalize(p.textContent)
      }))
      .filter((item) => item.text.split(/\s+/).length >= 35);
  }

  function buildCleanNarrativeCard(paragraphs) {
    const wrapper = document.createElement("div");
    wrapper.className = "section-card info-surface";

    paragraphs.forEach((text) => {
      const p = document.createElement("p");
      p.textContent = text;
      wrapper.appendChild(p);
    });

    return wrapper;
  }

  function tightenSeoContent() {
    const seoContent = document.getElementById("seoContent");
    if (!seoContent) return;
    if (seoContent.dataset.runtimeTightened === "true") return;
    seoContent.dataset.runtimeTightened = "true";

    seoContent.innerHTML = String(seoContent.innerHTML || "")
      .replace(/\*\*/g, "")
      .replace(/&nbsp;/gi, " ")
      .trim();

    const firstSectionCard = seoContent.querySelector(".section-card");
    if (!firstSectionCard) return;

    const paragraphData = getLargeParagraphs(firstSectionCard);

    const strongParagraphs = paragraphData
      .map((item) => item.text)
      .filter((text) => !isWeakSeoParagraph(text));

    let finalParagraphs = strongParagraphs.slice(0, 4);

    if (finalParagraphs.length < 3) {
      finalParagraphs = paragraphData.map((item) => item.text).slice(0, 4);
    }

    if (finalParagraphs.length >= 3) {
      const cleanCard = buildCleanNarrativeCard(finalParagraphs);
      firstSectionCard.replaceWith(cleanCard);
    }

    Array.from(seoContent.querySelectorAll("h2, h3, h4")).forEach((heading) => {
      if (isProbablyGenericHeading(textOf(heading))) {
        const parentCard = heading.closest(".section-card, .tool-cta-card, .faq-surface, .warning-surface, .verify-surface, .steps-surface");
        if (parentCard) {
          removeNode(parentCard);
          return;
        }

        let next = heading.nextElementSibling;
        while (next && !/^H[2-4]$/.test(next.tagName)) {
          const toRemove = next;
          next = next.nextElementSibling;
          removeNode(toRemove);
        }
        removeNode(heading);
      }
    });

    Array.from(seoContent.querySelectorAll(".tool-cta-card, .warning-surface, .verify-surface, .steps-surface, .faq-surface")).forEach(removeNode);

    Array.from(seoContent.querySelectorAll(".section-divider")).forEach(removeNode);

    Array.from(seoContent.querySelectorAll("p, li, h2, h3, h4")).forEach((node) => {
      if (node.children.length === 0) {
        node.textContent = normalize(node.textContent);
      }
      if (!normalize(node.textContent)) {
        removeNode(node);
      }
    });
  }

  function tightenBridgeCopy() {
    const bridge = document.getElementById("contentBridge");
    if (!bridge) return;

    const text = normalize(bridge.textContent);
    if (!text) return;

    if (text.length > 190) {
      const keyword = normalize(window.RAW_KEYWORD || "this message");
      bridge.textContent = `If this ${keyword} just showed up, use the checker above before you click, reply, or send money.`;
    }
  }

  function tightenHeroBadges() {
    const badges = document.querySelectorAll(".hero-badge");
    if (!badges.length) return;

    const replacements = [
      "Check suspicious messages",
      "Instant risk review",
      "Built for repeat use"
    ];

    badges.forEach((badge, index) => {
      if (replacements[index]) badge.textContent = replacements[index];
    });
  }

  function cleanPreviewTitle() {
    const previewDomain = document.getElementById("previewDomain");
    if (!previewDomain) return;

    const keyword = normalize(window.RAW_KEYWORD || "");
    if (!keyword) return;

    const cleaned = keyword
      .replace(/^\s*is\s+/i, "")
      .replace(/\s+(legit|scam|real|fake)\s*$/i, "")
      .replace(/\s+/g, " ")
      .trim();

    if (cleaned) {
      previewDomain.textContent = cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
    }
  }

  function dedupeLowerSections() {
    const contentSection = document.querySelector(".content-section");
    if (!contentSection) return;

    const headings = Array.from(contentSection.querySelectorAll("h2, h3"));
    let seen = new Set();

    headings.forEach((heading) => {
      const key = normalize(heading.textContent).toLowerCase();
      if (!key) return;

      if (seen.has(key)) {
        const card = heading.closest(".section-card, .tool-cta-card, .faq-surface, .warning-surface, .verify-surface, .steps-surface");
        if (card) removeNode(card);
      } else {
        seen.add(key);
      }
    });
  }

  function init() {
    safe(tightenHeroBadges);
    safe(cleanPreviewTitle);
    safe(tightenBridgeCopy);
    safe(tightenSeoContent);
    safe(dedupeLowerSections);
  }

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();