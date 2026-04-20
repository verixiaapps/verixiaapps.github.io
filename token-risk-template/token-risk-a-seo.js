const TOKEN_RISK_SEO = (() => {

  const config = window.TOKEN_RISK_CONFIG || {};

  const RAW_KEYWORD = config.rawKeyword || "";

  function escapeHtml(str) {

    return String(str || "")

      .replace(/&/g, "&amp;")

      .replace(/</g, "&lt;")

      .replace(/>/g, "&gt;")

      .replace(/"/g, "&quot;")

      .replace(/'/g, "&#39;");

  }

  function normalizeKeyword(str) {

    return String(str || "")

      .replace(/\s+/g, " ")

      .trim();

  }

  function displayKeyword(str) {

    const text = normalizeKeyword(str);

    if (!text) return "";

    return text.charAt(0).toUpperCase() + text.slice(1);

  }

  function cleanKeywordBase(keyword) {

    return normalizeKeyword(keyword)

      .replace(/^\s*(is|can|should|did)\s+/i, "")

      .replace(/\s+(scam|legit|safe|real)$/i, "")

      .trim();

  }

  function buildHeroTitle(keywordRaw) {

    const raw = normalizeKeyword(keywordRaw);

    if (!raw) return "Token Risk Checker";

    return `${displayKeyword(raw)} — Token Risk Check`;

  }

  function buildHeroSubheading() {

    return "Check token contracts, liquidity, and risk signals before you buy or approve.";

  }

  function buildContentHeading(keywordRaw) {

    return `What to know about ${displayKeyword(cleanKeywordBase(keywordRaw))}`;

  }

  function buildContentBridge() {

    return "Use the checker above before interacting with any token. Risk often shows up after money moves, not before.";

  }

  function splitSeoParagraphsFromHtml(seoContent) {

    const html = String(seoContent.innerHTML || "").trim();

    if (!html) return [];

    const div = document.createElement("div");

    div.innerHTML = html;

    return Array.from(div.querySelectorAll("p"))

      .map((p) => p.textContent.trim())

      .filter(Boolean);

  }

  function breakIntoSentences(paragraph) {

    return String(paragraph || "")

      .split(/(?<=[.!?])\s+/)

      .map((s) => s.trim())

      .filter(Boolean);

  }

  function isBadSentence(s) {

    const lower = s.toLowerCase();

    if (lower.length < 20) return true;

    const junk = [

      "it is important",

      "in many cases",

      "it is worth noting",

      "generally speaking"

    ];

    return junk.some(j => lower.startsWith(j));

  }

  function cleanSentence(s) {

    return s

      .replace(/\s+/g, " ")

      .replace(/\s+([,.!?])/g, "$1")

      .trim();

  }

  function buildBulletPool(paragraphs) {

    return paragraphs

      .flatMap(breakIntoSentences)

      .map(cleanSentence)

      .filter(Boolean)

      .filter(s => !isBadSentence(s));

  }

  function buildCards(paragraphs) {

    const bullets = buildBulletPool(paragraphs);

    if (!bullets.length) return [];

    const cards = [

      { title: "What stands out", items: [] },

      { title: "What to check", items: [] },

      { title: "Where risk builds", items: [] },

      { title: "Before you act", items: [] }

    ];

    bullets.forEach((b, i) => {

      const index = i % 4;

      if (cards[index].items.length < 4) {

        cards[index].items.push(b);

      }

    });

    return cards;

  }

  function renderCards(groups) {

    const seoContent = document.getElementById("seoContent");

    if (!seoContent) return;

    seoContent.innerHTML = `

      <div class="story-stack">

        ${groups.map(group => `

          <article class="story-card">

            <div class="story-card-title">${group.title}</div>

            <ul class="story-card-list">

              ${group.items.map(i => `<li>${escapeHtml(i)}</li>`).join("")}

            </ul>

          </article>

        `).join("")}

      </div>

    `;

  }

  function cleanSeoContent() {

    const seoContent = document.getElementById("seoContent");

    if (!seoContent) return;

    const paragraphs = splitSeoParagraphsFromHtml(seoContent);

    const groups = buildCards(paragraphs);

    if (!groups.length) {

      seoContent.innerHTML = "";

      return;

    }

    renderCards(groups);

  }

  function cleanLinks(id, headingId) {

    const wrap = document.getElementById(id);

    const heading = document.getElementById(headingId);

    if (!wrap || !heading) return;

    const links = wrap.querySelectorAll("a");

    if (!links.length) {

      wrap.style.display = "none";

      heading.style.display = "none";

    }

  }

  function setKeywordHeadings() {

    const keywordRaw = RAW_KEYWORD || "this token";

    document.getElementById("heroKeyword").textContent = buildHeroTitle(keywordRaw);

    document.getElementById("heroSubheading").textContent = buildHeroSubheading();

    document.getElementById("contentHeading").textContent = buildContentHeading(keywordRaw);

    document.getElementById("contentBridge").textContent = buildContentBridge();

  }

  function init() {

    setKeywordHeadings();

    cleanSeoContent();

    cleanLinks("relatedLinks", "relatedHeading");

    cleanLinks("moreLinks", "moreLinksHeading");

  }

  if (document.readyState === "loading") {

    document.addEventListener("DOMContentLoaded", init);

  } else {

    init();

  }

  return { init };

})();