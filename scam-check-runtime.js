Here’s the stronger runtime version. It is tighter, more aggressive about removing soft/generic lower-page content, keeps the best narrative paragraphs, sharpens bridge copy and badges, cleans duplicate sections better, and avoids touching core template structure.

(function () {
  if (window.__SCAM_CHECK_RUNTIME__) return;
  window.__SCAM_CHECK_RUNTIME__ = true;

  function safe(fn) {
    try {
      fn();
    } catch (e) {}
  }

  function normalize(str) {
    return String(str || "")
      .replace(/\u00A0/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function textOf(node) {
    return normalize(node ? node.textContent : "");
  }

  function removeNode(node) {
    if (node && node.parentNode) {
      node.parentNode.removeChild(node);
    }
  }

  function wordCount(text) {
    return normalize(text).split(/\s+/).filter(Boolean).length;
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
      "how to respond safely",
      "how to stay safe",
      "how to protect yourself",
      "what are the red flags",
      "red flags",
      "warning signs",
      "what should you do",
      "how to check safely",
      "next steps",
      "final thoughts",
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
      "use the checker first if you want a fast risk review",
      "scammers often",
      "it is important to",
      "users should",
      "be cautious",
      "stay vigilant",
      "always verify",
      "protect yourself by",
      "the safest move is",
      "the best thing you can do",
      "one of the most common scams",
      "this kind of scam",
      "this type of scam",
      "there are many versions",
      "there are several versions",
      "the message may look legitimate",
      "the message may appear legitimate",
      "warning signs include",
      "red flags include",
      "common warning signs",
      "how to verify safely",
      "what to do next",
      "to stay safe",
      "through official channels",
      "through official sources",
      "contact the company directly",
    ];

    return weakPatterns.some(function (p) {
      return t.includes(p);
    });
  }

  function isSoftParagraph(text) {
    const t = normalize(text).toLowerCase();
    if (!t) return true;

    if (wordCount(t) < 35) return true;
    if (isWeakSeoParagraph(t)) return true;

    const softSignals = [
      "this is because",
      "this happens because",
      "this means you should",
      "that is why",
      "the goal is to",
      "the scam works by",
      "the message is designed to",
      "the sender wants you to",
      "one version",
      "another version",
      "in some cases",
      "at the end of the day",
      "the main thing",
    ];

    let softCount = 0;
    softSignals.forEach(function (phrase) {
      if (t.includes(phrase)) softCount++;
    });

    return softCount >= 2;
  }

  function getLargeParagraphs(container) {
    if (!container) return [];

    return Array.from(container.querySelectorAll("p"))
      .map(function (p) {
        return {
          node: p,
          text: normalize(p.textContent),
        };
      })
      .filter(function (item) {
        return wordCount(item.text) >= 35;
      });
  }

  function paragraphStrength(text) {
    const t = normalize(text).toLowerCase();
    if (!t) return -100;

    let score = 0;

    const strongSignals = [
      "subject line",
      "sender",
      "display name",
      "reply-to",
      "from address",
      "button",
      "link",
      "portal",
      "screen",
      "page",
      "prompt",
      "code",
      "form",
      "chat",
      "tracking",
      "invoice",
      "countdown",
      "domain",
      "logo",
      "browser tab",
      "address bar",
      "payment page",
      "login page",
      "support chat",
      "telegram",
      "whatsapp",
      "direct deposit",
      "offer letter",
      "seed phrase",
      "connect wallet",
      "redelivery",
      "customs",
      "fee",
      "refund",
      "verification",
    ];

    strongSignals.forEach(function (signal) {
      if (t.includes(signal)) score += 2;
    });

    if (/\$\d+(\.\d{2})?/.test(t)) score += 4;
    if (/\b\d{1,4}\b/.test(t)) score += 2;
    if (/you get|you open|you receive|you see|you land|you tap|a text|an email|a message|the message|the email|the page|the screen|it starts|it shows up/.test(t)) {
      score += 5;
    }
    if (/urgent|today|now|minutes|same day|expires|deadline|locked|suspended|frozen|warning/.test(t)) {
      score += 4;
    }
    if (/stolen|loss|identity theft|account takeover|fraud|money|charge|wallet drain|credentials|documents/.test(t)) {
      score += 4;
    }
    if (isSoftParagraph(t)) score -= 12;

    return score;
  }

  function pickBestNarrativeParagraphs(paragraphData) {
    if (!paragraphData.length) return [];

    const ranked = paragraphData
      .map(function (item, index) {
        return {
          index: index,
          text: item.text,
          score: paragraphStrength(item.text),
        };
      })
      .filter(function (item) {
        return !isSoftParagraph(item.text);
      });

    const chosen = ranked.length ? ranked : paragraphData.map(function (item, index) {
      return {
        index: index,
        text: item.text,
        score: paragraphStrength(item.text),
      };
    });

    return chosen
      .sort(function (a, b) {
        if (b.score !== a.score) return b.score - a.score;
        return a.index - b.index;
      })
      .slice(0, 4)
      .sort(function (a, b) {
        return a.index - b.index;
      })
      .map(function (item) {
        return item.text;
      });
  }

  function dedupeParagraphs(paragraphs) {
    const seen = new Set();

    return paragraphs.filter(function (text) {
      const key = normalize(text)
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, "")
        .slice(0, 180);

      if (!key) return false;
      if (seen.has(key)) return false;

      seen.add(key);
      return true;
    });
  }

  function buildCleanNarrativeCard(paragraphs) {
    const wrapper = document.createElement("div");
    wrapper.className = "section-card info-surface";

    paragraphs.forEach(function (text) {
      const p = document.createElement("p");
      p.textContent = text;
      wrapper.appendChild(p);
    });

    return wrapper;
  }

  function removeHeadingBlock(heading) {
    if (!heading) return;

    const parentCard = heading.closest(
      ".section-card, .tool-cta-card, .faq-surface, .warning-surface, .verify-surface, .steps-surface"
    );

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
    if (firstSectionCard) {
      const paragraphData = getLargeParagraphs(firstSectionCard);
      let finalParagraphs = pickBestNarrativeParagraphs(paragraphData);
      finalParagraphs = dedupeParagraphs(finalParagraphs).slice(0, 4);

      if (finalParagraphs.length >= 3) {
        const cleanCard = buildCleanNarrativeCard(finalParagraphs);
        firstSectionCard.replaceWith(cleanCard);
      }
    }

    Array.from(seoContent.querySelectorAll("h2, h3, h4")).forEach(function (heading) {
      if (isProbablyGenericHeading(textOf(heading))) {
        removeHeadingBlock(heading);
      }
    });

    Array.from(
      seoContent.querySelectorAll(
        ".tool-cta-card, .warning-surface, .verify-surface, .steps-surface, .faq-surface"
      )
    ).forEach(removeNode);

    Array.from(seoContent.querySelectorAll(".section-divider")).forEach(removeNode);

    Array.from(seoContent.querySelectorAll("p, li, h2, h3, h4")).forEach(function (node) {
      if (node.children.length === 0) {
        node.textContent = normalize(node.textContent);
      }

      const text = normalize(node.textContent);
      if (!text) {
        removeNode(node);
        return;
      }

      if (node.tagName === "P" && isWeakSeoParagraph(text)) {
        removeNode(node);
      }
    });
  }

  function tightenBridgeCopy() {
    const bridge = document.getElementById("contentBridge");
    if (!bridge) return;

    const text = normalize(bridge.textContent);
    const keyword = normalize(window.RAW_KEYWORD || "this message");

    if (!text || text.length > 165 || isWeakSeoParagraph(text)) {
      bridge.textContent = `If this ${keyword} just showed up, run it through the checker above before you click, reply, sign in, or send money.`;
    }
  }

  function tightenHeroBadges() {
    const badges = document.querySelectorAll(".hero-badge");
    if (!badges.length) return;

    const replacements = [
      "Check suspicious messages",
      "Instant scam review",
      "Built for repeat checks",
    ];

    badges.forEach(function (badge, index) {
      if (replacements[index]) {
        badge.textContent = replacements[index];
      }
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
      previewDomain.textContent =
        cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
    }
  }

  function dedupeLowerSections() {
    const contentSection = document.querySelector(".content-section");
    if (!contentSection) return;

    const headings = Array.from(contentSection.querySelectorAll("h2, h3"));
    const seen = new Set();

    headings.forEach(function (heading) {
      const key = normalize(heading.textContent).toLowerCase();
      if (!key) return;

      if (seen.has(key)) {
        const card = heading.closest(
          ".section-card, .tool-cta-card, .faq-surface, .warning-surface, .verify-surface, .steps-surface"
        );
        if (card) {
          removeNode(card);
        } else {
          removeHeadingBlock(heading);
        }
        return;
      }

      seen.add(key);
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