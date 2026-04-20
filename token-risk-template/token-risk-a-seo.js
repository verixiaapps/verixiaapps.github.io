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
      .replace(/[–—]/g, "-")
      .trim();
  }

  function stripLeadingQuestionPrefixes(text) {
    return String(text || "")
      .replace(/^\s*is\s+/i, "")
      .replace(/^\s*can\s+i\s+trust\s+/i, "")
      .replace(/^\s*did\s+i\s+get\s+scammed\s+(?:by|on|with)\s+/i, "")
      .replace(/^\s*is\s+this\s+/i, "")
      .replace(/^\s*should\s+i\s+buy\s+/i, "")
      .replace(/^\s*can\s+i\s+buy\s+/i, "")
      .trim();
  }

  function stripTrailingQuestionSuffixes(text) {
    return String(text || "")
      .replace(/\s+a\s+scam$/i, "")
      .replace(/\s+or\s+legit$/i, "")
      .replace(/\s+or\s+scam$/i, "")
      .replace(/\s+legit$/i, "")
      .replace(/\s+real$/i, "")
      .replace(/\s+safe$/i, "")
      .replace(/\s+scam$/i, "")
      .replace(/\s+a$/i, "")
      .trim();
  }

  function cleanKeywordBase(keyword) {
    let text = normalizeKeyword(keyword);
    text = stripLeadingQuestionPrefixes(text);
    text = stripTrailingQuestionSuffixes(text);
    return text.replace(/\s+/g, " ").trim();
  }

  function cleanKeywordForSentence(keyword) {
    return cleanKeywordBase(keyword)
      .replace(/\btoken\b/gi, "")
      .replace(/\bcoin\b/gi, "")
      .replace(/\bcontract\b/gi, "")
      .replace(/\baddress\b/gi, "")
      .replace(/\bpair\b/gi, "")
      .replace(/\bchart\b/gi, "")
      .replace(/\bdexscreener\b/gi, "")
      .replace(/\bwebsite\b/gi, "")
      .replace(/\bproject\b/gi, "")
      .replace(/\blaunch\b/gi, "")
      .replace(/\bpresale\b/gi, "")
      .replace(/\bairdrop\b/gi, "")
      .replace(/\bscam\b/gi, "")
      .replace(/\bscams\b/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function displayKeyword(str) {
    const text = normalizeKeyword(str);
    if (!text) return "";
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  function displayCleanKeyword(str) {
    return displayKeyword(cleanKeywordBase(str));
  }

  function containsAny(text, phrases) {
    return phrases.some((phrase) => text.includes(phrase));
  }

  function isGuidanceStyleKeyword(lower) {
    return (
      lower.startsWith("how to ") ||
      lower.startsWith("what to do after ") ||
      lower.startsWith("how to recover after ") ||
      lower.startsWith("how to avoid ") ||
      lower.startsWith("what happens after ") ||
      lower.startsWith("what is ") ||
      lower.startsWith("why ") ||
      lower.startsWith("when ") ||
      lower.startsWith("where ") ||
      lower.startsWith("who ")
    );
  }

  function isQuestionStyleKeyword(lower) {
    return (
      lower.startsWith("is ") ||
      lower.startsWith("can ") ||
      lower.startsWith("should ") ||
      lower.startsWith("could ") ||
      lower.startsWith("would ") ||
      lower.startsWith("do ") ||
      lower.startsWith("does ") ||
      lower.startsWith("did ")
    );
  }

  function chooseBridgeIntro(baseKeyword) {
    const readable = displayKeyword(baseKeyword || "token setup");
    const variants = [
      `If this ${readable} just showed up,`,
      `If you're unsure about this ${readable},`,
      `If you're looking at this ${readable} right now,`
    ];
    const index = String(baseKeyword || "").length % variants.length;
    return variants[index];
  }

  function buildHeroTitle(keywordRaw) {
    const raw = normalizeKeyword(keywordRaw);
    const lower = raw.toLowerCase();
    const cleanTitle = displayCleanKeyword(keywordRaw);
    const readableTitle = displayKeyword(raw);

    if (!raw) {
      return "Token Risk Checker: Review Contract, Liquidity, and Warning Signs";
    }

    if (isGuidanceStyleKeyword(lower)) {
      return `${readableTitle}: Token Warning Signs, Risks & What To Check`;
    }

    if (lower.startsWith("did i get scammed")) {
      return `${readableTitle}? Token Risks, Warning Signs & What To Do Next`;
    }

    if (lower.startsWith("can ") || lower.startsWith("should ") || lower.startsWith("is this ")) {
      return `${readableTitle}? Token Risks, Warning Signs & What To Know`;
    }

    if (lower.startsWith("is ") && lower.includes(" safe")) {
      const withoutSafe = raw.replace(/\s+safe\b/i, "").trim();
      return `${displayKeyword(withoutSafe)} Safe or Risky? What To Check Before Buying`;
    }

    if (lower.startsWith("is ") && lower.includes(" legit")) {
      const withoutLegit = raw.replace(/\s+legit\b/i, "").trim();
      return `${displayKeyword(withoutLegit)} Legit or Risky? Token Warning Signs & What To Check`;
    }

    if (isQuestionStyleKeyword(lower)) {
      return `${readableTitle}? Token Risks, Warning Signs & What To Know`;
    }

    return `${cleanTitle} Token Risk Check: Contract, Liquidity & Holder Warning Signs`;
  }

  function buildHeroSubheading(keywordRaw) {
    const raw = normalizeKeyword(keywordRaw);
    const lower = raw.toLowerCase();
    const readableKeyword = displayKeyword(cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw);

    if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
      return "Use the checker below to review token contracts, project pages, Dexscreener links, liquidity claims, and suspicious token promotions before you buy or approve.";
    }

    return `Projects related to ${readableKeyword} can hide wallet concentration, contract risks, liquidity risk, or hype-driven traps. Paste the token details below before you buy, approve, or bridge.`;
  }

  function buildContentHeading(keywordRaw) {
    const raw = normalizeKeyword(keywordRaw);
    const lower = raw.toLowerCase();
    const readableTitle = displayKeyword(raw);
    const cleanTitle = displayCleanKeyword(keywordRaw);

    if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
      return readableTitle;
    }

    return `What ${cleanTitle} Token Risk Patterns Often Look Like`;
  }

  function buildContentBridge(keywordRaw) {
    const raw = normalizeKeyword(keywordRaw);
    const lower = raw.toLowerCase();
    const cleanSentenceKeyword = cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw;

    if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
      return "Use the checker above to review token contracts, project pages, Dexscreener links, and suspicious claims before you buy, approve, or bridge.";
    }

    return `${chooseBridgeIntro(cleanSentenceKeyword)} use the checker above before you buy, approve, bridge, or trust the pitch. Tokens like this often look normal at first and only become obviously risky after money is already in.`;
  }

  function buildRecognitionItems(keywordRaw) {
    const lower = normalizeKeyword(keywordRaw || "").toLowerCase();

    if (containsAny(lower, ["meme", "memecoin", "pump", "moon", "100x"])) {
      return [
        ["What people notice first", "Fast price movement, viral posts, screenshots, and social pressure to buy before the next leg up."],
        ["What bad actors want", "Liquidity from rushed buyers before the token setup, wallet concentration, and exit risk are fully understood."],
        ["Why it feels believable", "The energy looks organic because meme runs often move fast even when the setup underneath is weak."],
        ["What makes it risky", "Hype can hide concentrated wallets, weak liquidity, insider advantage, or a fast collapse once attention shifts."]
      ];
    }

    if (containsAny(lower, ["presale", "fair launch", "launch", "airdrop"])) {
      return [
        ["What people notice first", "A countdown, whitelist promise, early access push, or launch thread that makes speed feel necessary."],
        ["What bad actors want", "Funds or trust before the token setup, contract permissions, and distribution model are fully visible."],
        ["Why it feels believable", "Early access always sounds attractive because people fear missing the first move."],
        ["What makes it risky", "The most important details often stay vague until after buyers commit or approvals are already granted."]
      ];
    }

    if (containsAny(lower, ["solana", "eth", "ethereum", "bsc", "base", "arb", "avalanche"])) {
      return [
        ["What people notice first", "A chain-specific token page, trending pair, or social thread that makes the setup feel established quickly."],
        ["What bad actors want", "A buy, approval, or trust decision before liquidity, holder spread, and contract controls are checked."],
        ["Why it feels believable", "The token borrows familiar chain language, dashboards, and charts that make it look more mature than it is."],
        ["What makes it risky", "Contract behavior and wallet concentration can matter far more than branding or a short-term chart move."]
      ];
    }

    if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
      return [
        ["What people notice first", "A token page or pitch that looks normal until the money decision starts feeling urgent."],
        ["What bad actors want", "One buy, one approval, one bridge, or one rushed trust decision before real review happens."],
        ["Why it feels believable", "Crypto projects often reuse familiar dashboards, token language, and social proof that feel convincing fast."],
        ["What makes it risky", "The page is useful when you need to compare what you saw against a common token risk pattern before acting."]
      ];
    }

    return [
      ["What people notice first", "A chart, contract, or token page that looks promising before the deeper setup has been checked."],
      ["What bad actors want", "A fast buy, an approval, or confidence before the contract, liquidity, and wallets are fully understood."],
      ["Why it feels believable", "The project can look polished because branding and hype are easier to build than a trustworthy token setup."],
      ["What makes it risky", "The real danger often shows up after people commit, not before."]
    ];
  }

  function renderRecognitionChips() {
    const wrap = document.getElementById("contentRecognition");
    if (!wrap) return;

    const items = buildRecognitionItems(RAW_KEYWORD || "");
    wrap.innerHTML = items
      .map((item) => `
        <div class="recognition-chip">
          <span class="recognition-label">${escapeHtml(item[0])}</span>
          <span class="recognition-copy">${escapeHtml(item[1])}</span>
        </div>
      `)
      .join("");
  }

  function applyPreviewCard() {
    const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
    const cleanTitle = displayCleanKeyword(keywordRaw) || "Risky Token Setup";
    const lower = keywordRaw.toLowerCase();

    const previewDomain = document.getElementById("previewDomain");
    const previewSub = document.getElementById("previewSub");
    const previewBadge = document.getElementById("previewBadge");
    const previewScore = document.getElementById("previewScore");
    const previewScoreFill = document.getElementById("previewScoreFill");
    const previewSignals = document.getElementById("previewSignals");

    if (!previewDomain || !previewSub || !previewBadge || !previewScore || !previewScoreFill || !previewSignals) {
      return;
    }

    let riskLabel = "Example Token Risk";
    let trustScore = "Risk Example";
    let fillWidth = "18%";
    let sub = "Common warning signs found in similar token launches";
    let signals = [
      "Liquidity setup looks unclear",
      "Holder concentration may be high",
      "Trading permissions may create risk"
    ];

    if (containsAny(lower, ["meme", "memecoin", "pump", "moon", "100x"])) {
      signals = [
        "Hype may be ahead of fundamentals",
        "Wallet concentration could matter more than the chart",
        "Fast reversals are common when attention drops"
      ];
    } else if (containsAny(lower, ["presale", "launch", "airdrop", "fair launch"])) {
      signals = [
        "Early access pressure can hide weak details",
        "Token distribution may be unclear",
        "Liquidity and ownership setup should be verified"
      ];
    } else if (containsAny(lower, ["contract", "address", "token", "coin", "pair"])) {
      signals = [
        "Contract permissions may matter",
        "Liquidity and holder spread should be reviewed",
        "Project claims may not match on-chain reality"
      ];
    } else if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
      riskLabel = "Token Risk Check";
      trustScore = "Pattern Review";
      fillWidth = "34%";
      signals = [
        "Review contract, liquidity, and holders",
        "Verify claims outside the promo thread",
        "Do not buy or approve before checking"
      ];
    }

    previewBadge.textContent = `🔴 ${riskLabel}`;
    previewScore.textContent = trustScore;
    previewScoreFill.style.width = fillWidth;
    previewDomain.textContent = cleanTitle;
    previewSub.textContent = sub;
    previewSignals.innerHTML = signals
      .map((signal) => `
        <div class="preview-signal">
          <span class="preview-signal-icon">⚠️</span>
          <span>${escapeHtml(signal)}</span>
        </div>
      `)
      .join("");
  }

  function applyIntentToChecker() {
    const tokenInput = document.getElementById("tokenAddress");
    const inputHelp = document.querySelector(".input-help");

    if (!tokenInput || !inputHelp) return;

    tokenInput.placeholder = "Paste token contract address";
    inputHelp.textContent = "Example: ERC-20, Solana, Base, or other supported token contract address";
  }

  function splitSeoParagraphsFromHtml(seoContent) {
    const html = String(seoContent.innerHTML || "").trim();
    if (!html) return [];

    const parser = document.createElement("div");
    parser.innerHTML = html;

    let paragraphs = Array.from(parser.querySelectorAll("p"))
      .map((p) => p.textContent.trim())
      .filter(Boolean);

    if (paragraphs.length) return paragraphs;

    paragraphs = parser.innerHTML
      .replace(/<br\s*\/?>/gi, "\n")
      .replace(/<\/div>/gi, "\n\n")
      .replace(/<\/section>/gi, "\n\n")
      .replace(/<[^>]+>/g, "")
      .split(/\n\s*\n/)
      .map((p) => p.replace(/\s+/g, " ").trim())
      .filter(Boolean);

    return paragraphs;
  }

  function buildSeoCardTitles(keywordRaw) {
    const lower = normalizeKeyword(keywordRaw || "").toLowerCase();

    if (containsAny(lower, ["meme", "memecoin", "pump", "moon", "100x"])) {
      return [
        ["🚀", "Why this setup pulls buyers in"],
        ["🧱", "What usually looks weaker underneath"],
        ["⚠️", "Where the trap starts tightening"],
        ["🔍", "What to verify before acting"]
      ];
    }

    if (containsAny(lower, ["presale", "launch", "airdrop", "fair launch"])) {
      return [
        ["🪂", "Why the launch pitch works"],
        ["🧱", "What buyers often fail to review"],
        ["⚠️", "Where urgency gets expensive"],
        ["🔍", "What to confirm before committing"]
      ];
    }

    if (containsAny(lower, ["contract", "address", "token", "coin", "pair"])) {
      return [
        ["🧾", "What the setup suggests at first glance"],
        ["🧱", "What needs a closer look"],
        ["⚠️", "Where token risk can stay hidden"],
        ["🔍", "What to confirm before acting"]
      ];
    }

    return [
      ["👀", "What stands out first"],
      ["🧱", "What deserves a deeper check"],
      ["⚠️", "Where people get caught"],
      ["🔍", "What to verify next"]
    ];
  }

  function renderSeoContentCards(groups) {
    const seoContent = document.getElementById("seoContent");
    if (!seoContent) return;

    if (!groups.length) {
      seoContent.innerHTML = "";
      return;
    }

    const titles = buildSeoCardTitles(RAW_KEYWORD || "");

    seoContent.innerHTML = `
      <div class="story-stack">
        ${groups
          .map((group) => {
            const titleIndex = group && typeof group.titleIndex === "number" ? group.titleIndex : 0;
            const items = Array.isArray(group && group.items) ? group.items : [];
            const title = titles[titleIndex] || ["•", "More to know"];

            return `
              <article class="story-card${titleIndex === 0 ? " lead" : ""}">
                <div class="story-card-title">
                  <span class="story-card-title-icon">${title[0]}</span>
                  <span>${title[1]}</span>
                </div>
                <ul class="story-card-list">
                  ${items.map((item) => `<li class="story-card-item">${escapeHtml(item)}</li>`).join("")}
                </ul>
              </article>
            `;
          })
          .join("")}
      </div>
    `;
  }

  function stripSeoFiller(text) {
    return String(text || "")
      .replace(/\b(it is important to note that|it is worth noting that|in many cases|in some cases|in a lot of cases)\b/gi, "")
      .replace(/\b(this is because|the reason for this is that)\b/gi, "because")
      .replace(/\b(as always|of course|basically|simply put|put simply)\b/gi, "")
      .replace(/\b(when it comes to this|at the end of the day)\b/gi, "")
      .replace(/\bkeep in mind that\b/gi, "")
      .replace(/\bmake sure to\b/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function normalizeSeoSentence(sentence) {
    return stripSeoFiller(sentence)
      .replace(/^[-•]\s*/, "")
      .replace(/\s+/g, " ")
      .replace(/\s+([,.;!?])/g, "$1")
      .replace(/\.{2,}/g, ".")
      .trim();
  }

  function breakParagraphIntoSentences(paragraph) {
    return String(paragraph || "")
      .replace(/\s+/g, " ")
      .split(/(?<=[.!?])\s+/)
      .map(normalizeSeoSentence)
      .filter(Boolean);
  }

  function isTooGenericSentence(sentence) {
    const lower = String(sentence || "").toLowerCase().trim();
    if (!lower) return true;
    if (lower.length < 24) return true;

    const genericStarts = [
      "this means",
      "this can mean",
      "this is why",
      "this is because",
      "it is important",
      "it is worth",
      "in many cases",
      "in some cases",
      "there are many",
      "one thing to remember",
      "generally speaking",
      "in general"
    ];

    return genericStarts.some((start) => lower.startsWith(start));
  }

  function containsKeywordLeak(sentence) {
    const keyword = String(RAW_KEYWORD || "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();

    if (!keyword) return false;

    const lower = String(sentence || "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();

    if (!lower || !lower.includes(keyword)) return false;

    const cleanKeyword = keyword.replace(/[^a-z0-9]+/g, " ").trim();
    const cleanSentence = lower.replace(/[^a-z0-9]+/g, " ").trim();

    if (cleanSentence === cleanKeyword) return false;
    if (cleanSentence.startsWith(cleanKeyword + " ")) return true;
    if (cleanSentence.includes(" " + cleanKeyword + " ")) return true;

    return lower.length > keyword.length + 18;
  }

  function detectTokenTheme(keywordRaw, paragraphs) {
    const lower = normalizeKeyword(keywordRaw || "").toLowerCase();
    const combined = `${lower} ${(paragraphs || []).join(" ").toLowerCase()}`;

    if (containsAny(combined, ["meme", "memecoin", "pump", "moon", "100x"])) return "meme";
    if (containsAny(combined, ["presale", "launch", "airdrop", "fair launch", "whitelist"])) return "launch";
    if (containsAny(combined, ["solana", "ethereum", "eth", "bsc", "base", "arb", "avalanche"])) return "chain";
    return "generic";
  }

  function buildSourceMaterial(paragraphs) {
    return Array.isArray(paragraphs) ? paragraphs : [];
  }

  function compressTokenBullet(text, theme, cardIndex) {
    let value = String(text || "")
      .replace(/\s+/g, " ")
      .replace(/^[\-•]\s*/, "")
      .trim();

    if (!value) return "";

    value = stripSeoFiller(value)
      .replace(/\bthis means\b/gi, "")
      .replace(/\bthis can mean\b/gi, "")
      .replace(/\bthis matters because\b/gi, "")
      .replace(/\bit is important to\b/gi, "")
      .replace(/\bit is worth noting that\b/gi, "")
      .replace(/\bin many cases\b/gi, "")
      .replace(/\bin some cases\b/gi, "")
      .replace(/\btokens can\b/gi, "")
      .replace(/\ba token can\b/gi, "")
      .replace(/\bprojects can\b/gi, "")
      .replace(/\bthere is a risk that\b/gi, "")
      .replace(/\bthis token\b/gi, "The setup")
      .replace(/\bthe token\b/gi, "The setup")
      .replace(/\bthe project\b/gi, "The setup")
      .replace(/\busers\b/gi, "buyers")
      .replace(/\s+/g, " ")
      .trim();

    value = value
      .replace(/^because\s+/i, "")
      .replace(/^and\s+/i, "")
      .replace(/^but\s+/i, "")
      .replace(/^so\s+/i, "")
      .replace(/^while\s+/i, "")
      .replace(/^if\s+/i, "")
      .replace(/^when\s+/i, "")
      .replace(/^there are\s+/i, "")
      .replace(/^there is\s+/i, "")
      .trim();

    if (!value) return "";

    value = value.charAt(0).toUpperCase() + value.slice(1);

    const rewrites = [
      {
        test: /(urgent|urgency|rush|fomo|pressure|countdown|whitelist|early access)/i,
        value: "Urgency shows up before the setup is fully verified."
      },
      {
        test: /(liquidity|pool|lp|locked)/i,
        value: "Liquidity can look fine until exits matter more than entries."
      },
      {
        test: /(holder|holders|wallet|wallets|distribution|concentration)/i,
        value: "Holder concentration can change the risk fast once momentum fades."
      },
      {
        test: /(sell|selling|exit|honeypot|swap|approve|approval|permissions)/i,
        value: "Buying may feel easier than selling once the contract starts limiting exits."
      },
      {
        test: /(price|volume|chart|pump|moon|spike|trend)/i,
        value: "Fast chart movement can hide weak structure underneath."
      },
      {
        test: /(social|viral|telegram|x post|thread|community|influencer|hype)/i,
        value: "Social proof can feel stronger than the underlying proof."
      },
      {
        test: /(contract|mint|owner|ownership|blacklist|tax|function)/i,
        value: "Contract controls matter more than branding once money is committed."
      }
    ];

    for (const rule of rewrites) {
      if (rule.test.test(value)) {
        value = rule.value;
        break;
      }
    }

    if (theme === "meme" && /social proof/i.test(value)) {
      value = "Hype can outrun the actual strength of the setup.";
    }

    if (theme === "launch" && /urgency/i.test(value)) {
      value = "Launch pressure can push buyers in before the important details are visible.";
    }

    value = value
      .replace(/[,:;]\s*$/, "")
      .replace(/\.{2,}/g, ".")
      .trim();

    if (!value) return "";

    const maxLen = cardIndex === 3 ? 92 : 88;
    if (value.length > maxLen) {
      value = value.slice(0, maxLen).replace(/[,:;\s]+[^\s]*$/, "").trim();
    }

    value = value.replace(/[,:;\s]+$/g, "").trim();

    if (!/[.!?]$/.test(value)) {
      value += ".";
    }

    return value;
  }

  function buildCardBulletPool(paragraphs, theme) {
    const sourceMaterial = buildSourceMaterial(paragraphs);

    const candidateLines = sourceMaterial
      .flatMap(breakParagraphIntoSentences)
      .map(normalizeSeoSentence)
      .filter(Boolean)
      .filter((s) => !containsKeywordLeak(s))
      .filter((s) => !isTooGenericSentence(s))
      .map((s) => compressTokenBullet(s, theme, 1))
      .filter(Boolean);

    const seen = new Set();
    const unique = [];

    for (const line of candidateLines) {
      const key = line.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
      if (!key || seen.has(key)) continue;
      seen.add(key);
      unique.push(line);
    }

    return unique;
  }

  function buildSeoCardGroups(paragraphs) {
    const theme = detectTokenTheme(RAW_KEYWORD || "", paragraphs);
    const bulletPool = buildCardBulletPool(paragraphs, theme);

    if (!bulletPool.length) {
      return [];
    }

    const cards = [
      { titleIndex: 0, items: [] },
      { titleIndex: 1, items: [] },
      { titleIndex: 2, items: [] },
      { titleIndex: 3, items: [] }
    ];

    const globalSeen = new Set();
    const overflow = [];

    function keyFor(text) {
      return String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
    }

    function pushBullet(cardIndex, text) {
      const cleaned = compressTokenBullet(text, theme, cardIndex);
      const key = keyFor(cleaned);

      if (!cleaned || !key) return false;
      if (globalSeen.has(key)) return false;
      if (!cards[cardIndex] || cards[cardIndex].items.length >= 4) return false;

      globalSeen.add(key);
      cards[cardIndex].items.push(cleaned);
      return true;
    }

    function classifyCardIndex(text) {
      const lower = String(text || "").toLowerCase();

      if (/(check|verify|confirm|review|look for|watch for|make sure)/i.test(lower)) {
        return 3;
      }

      if (/(urgent|urgency|rush|fomo|pressure|countdown|whitelist|early access|viral|hype|social|thread|telegram|x post|community|influencer)/i.test(lower)) {
        return 0;
      }

      if (/(liquidity|pool|lp|locked|holder|holders|wallet|wallets|distribution|concentration|contract|mint|owner|ownership|blacklist|tax|function)/i.test(lower)) {
        return 1;
      }

      if (/(sell|selling|exit|honeypot|swap|approve|approval|permissions|price|volume|chart|pump|moon|spike|trend)/i.test(lower)) {
        return 2;
      }

      return 2;
    }

    for (const line of bulletPool) {
      const targetIndex = classifyCardIndex(line);
      if (!pushBullet(targetIndex, line)) {
        const cleaned = compressTokenBullet(line, theme, targetIndex);
        const key = keyFor(cleaned);
        if (cleaned && key && !globalSeen.has(key)) {
          overflow.push(line);
        }
      }
    }

    for (const line of overflow) {
      const nextCard = cards
        .filter((card) => card.items.length < 4)
        .sort((a, b) => a.items.length - b.items.length)[0];

      if (!nextCard) break;
      pushBullet(nextCard.titleIndex, line);
    }

    return cards
      .filter((card) => card.items.length > 0)
      .map((card) => ({
        titleIndex: card.titleIndex,
        items: card.items.slice(0, 4)
      }));
  }

  function cleanSeoContent() {
    const seoContent = document.getElementById("seoContent");
    if (!seoContent) return;

    seoContent.innerHTML = seoContent.innerHTML
      .replace(/\*\*/g, "")
      .replace(/<p>\s*<\/p>/g, "")
      .trim();

    const paragraphs = splitSeoParagraphsFromHtml(seoContent)
      .map((p) => stripSeoFiller(p))
      .map((p) => p.replace(/\s+/g, " ").trim())
      .filter(Boolean);

    const groups = buildSeoCardGroups(paragraphs);

    if (!groups.length) {
      seoContent.innerHTML = "";
      return;
    }

    renderSeoContentCards(groups);
  }

  function cleanRelatedLinks() {
    const relatedLinks = document.getElementById("relatedLinks");
    const relatedHeading = document.getElementById("relatedHeading");
    if (!relatedLinks || !relatedHeading) return;

    relatedLinks.innerHTML = relatedLinks.innerHTML.replace(/\*\*/g, "").trim();

    const links = relatedLinks.querySelectorAll("li a");
    if (links.length === 0) {
      relatedLinks.style.display = "none";
      relatedHeading.style.display = "none";
    }
  }

  function cleanMoreLinks() {
    const moreLinksWrap = document.getElementById("moreLinksWrap");
    const moreLinks = document.getElementById("moreLinks");
    const moreLinksHeading = document.getElementById("moreLinksHeading");

    if (!moreLinksWrap || !moreLinks || !moreLinksHeading) return;

    moreLinks.innerHTML = moreLinks.innerHTML.replace(/\*\*/g, "").trim();

    const links = moreLinks.querySelectorAll("li a");
    if (links.length === 0) {
      moreLinksWrap.style.display = "none";
      moreLinksHeading.style.display = "none";
    }
  }

  function setKeywordHeadings() {
    const keywordRaw = (RAW_KEYWORD || "this token").trim();

    const heroKeyword = document.getElementById("heroKeyword");
    const heroSubheading = document.getElementById("heroSubheading");
    const contentHeading = document.getElementById("contentHeading");
    const contentBridge = document.getElementById("contentBridge");

    if (heroKeyword) heroKeyword.textContent = buildHeroTitle(keywordRaw);
    if (heroSubheading) heroSubheading.textContent = buildHeroSubheading(keywordRaw);
    if (contentHeading) contentHeading.textContent = buildContentHeading(keywordRaw);
    if (contentBridge) contentBridge.textContent = buildContentBridge(keywordRaw);
  }

  function init() {
    setKeywordHeadings();
    applyPreviewCard();
    applyIntentToChecker();
    cleanSeoContent();
    cleanRelatedLinks();
    cleanMoreLinks();
    renderRecognitionChips();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  return {
    init
  };
})();