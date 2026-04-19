const fs = require("fs");

const path = require("path");

const TEMPLATE_PATH = process.env.TEMPLATE_PATH

  ? path.join(process.cwd(), process.env.TEMPLATE_PATH)

  : path.join(process.cwd(), "token-risk-template", "token-risk-template-a.html");

function assertFileExists(filePath) {

  if (!fs.existsSync(filePath)) {

    throw new Error(`Template file not found: ${filePath}`);

  }

}

function replaceAllRegex(source, regex, newValue) {

  return source.replace(regex, newValue);

}

function ensureContains(source, needle, label) {

  if (!source.includes(needle)) {

    throw new Error(`Missing: ${label}`);

  }

}

function escapeRegex(value) {

  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

}

function findFunctionRange(source, functionName) {

  const escapedName = escapeRegex(functionName);

  const startRegex = new RegExp(`(?:async\\s+)?function\\s+${escapedName}\\s*\\(`);

  const startMatch = startRegex.exec(source);

  if (!startMatch) return null;

  const startIndex = startMatch.index;

  const braceStart = source.indexOf("{", startIndex);

  if (braceStart === -1) {

    throw new Error(`Could not find function body start for: ${functionName}`);

  }

  let depth = 0;

  let inSingle = false;

  let inDouble = false;

  let inTemplate = false;

  let inLineComment = false;

  let inBlockComment = false;

  let prev = "";

  for (let i = braceStart; i < source.length; i++) {

    const char = source[i];

    const next = source[i + 1];

    if (inLineComment) {

      if (char === "\n") inLineComment = false;

      prev = char;

      continue;

    }

    if (inBlockComment) {

      if (prev === "*" && char === "/") inBlockComment = false;

      prev = char;

      continue;

    }

    if (!inSingle && !inDouble && !inTemplate) {

      if (char === "/" && next === "/") {

        inLineComment = true;

        prev = char;

        continue;

      }

      if (char === "/" && next === "*") {

        inBlockComment = true;

        prev = char;

        continue;

      }

    }

    if (!inDouble && !inTemplate && char === "'" && prev !== "\\") {

      inSingle = !inSingle;

      prev = char;

      continue;

    }

    if (!inSingle && !inTemplate && char === `"` && prev !== "\\") {

      inDouble = !inDouble;

      prev = char;

      continue;

    }

    if (!inSingle && !inDouble && char === "`" && prev !== "\\") {

      inTemplate = !inTemplate;

      prev = char;

      continue;

    }

    if (!inSingle && !inDouble && !inTemplate) {

      if (char === "{") depth++;

      if (char === "}") {

        depth--;

        if (depth === 0) {

          return { start: startIndex, end: i + 1 };

        }

      }

    }

    prev = char;

  }

  throw new Error(`Could not find function end for: ${functionName}`);

}

function upsertFunction(source, functionName, replacement, insertBeforeName) {

  const range = findFunctionRange(source, functionName);

  if (range) {

    return source.slice(0, range.start) + replacement + source.slice(range.end);

  }

  const insertRange = findFunctionRange(source, insertBeforeName);

  if (!insertRange) {

    throw new Error(`Function not found for insertion: ${insertBeforeName}`);

  }

  return (

    source.slice(0, insertRange.start) +

    replacement +

    "\n\n" +

    source.slice(insertRange.start)

  );

}

function upsertStyleBlock(source, styleId, css, insertBeforeTag = "</head>") {

  const block = `<style id="${styleId}">\n${css}\n</style>`;

  const regex = new RegExp(

    `<style[^>]*id=["']${escapeRegex(styleId)}["'][^>]*>[\\s\\S]*?<\\/style>`,

    "i"

  );

  if (regex.test(source)) {

    return source.replace(regex, block);

  }

  const insertIndex = source.indexOf(insertBeforeTag);

  if (insertIndex === -1) {

    throw new Error(`Insertion tag not found for style block: ${insertBeforeTag}`);

  }

  return source.slice(0, insertIndex) + block + "\n" + source.slice(insertIndex);

}

function main() {

  assertFileExists(TEMPLATE_PATH);

  let html = fs.readFileSync(TEMPLATE_PATH, "utf8");

  html = replaceAllRegex(

    html,

    /<textarea[^>]*id="text"[^>]*><\/textarea>/g,

    '<input id="tokenAddress" type="text" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" placeholder="Paste token contract address">'

  );

  const TOKEN_RISK_POLISH_STYLE = `

:root{

  --bg:#04070f;

  --bg-2:#07101a;

  --bg-3:#0b1626;

  --bg-4:#0f1d31;

  --surface:rgba(255,255,255,.035);

  --surface-2:rgba(255,255,255,.05);

  --surface-3:rgba(255,255,255,.075);

  --card:#0d1524;

  --card-2:#101b2d;

  --card-3:#152238;

  --ink:#edf4ff;

  --ink-strong:#ffffff;

  --ink-dark:#111827;

  --muted:#9caed0;

  --muted-2:#8395b6;

  --line:rgba(255,255,255,.08);

  --line-2:rgba(255,255,255,.06);

  --line-3:rgba(255,255,255,.12);

  --cyan:#82b7ff;

  --cyan-2:#5f94ff;

  --blue:#668dff;

  --blue-2:#4f74ed;

  --violet:#8d82f6;

  --violet-2:#7168e8;

  --emerald:#2fc48d;

  --emerald-2:#1ea875;

  --amber:#f1ac3d;

  --red:#ff7659;

  --red-2:#ef6047;

  --shadow-xl:0 30px 80px rgba(0,0,0,.42);

  --shadow-lg:0 22px 56px rgba(0,0,0,.34);

  --shadow-md:0 14px 34px rgba(0,0,0,.24);

  --shadow-sm:0 10px 22px rgba(0,0,0,.18);

  --shadow-xs:0 6px 14px rgba(0,0,0,.12);

  --radius-xl:28px;

  --radius-lg:22px;

  --radius-md:18px;

  --radius-sm:14px;

}

body{

  background:

    radial-gradient(circle at 16% 0%, rgba(97,141,255,.12), transparent 24%),

    radial-gradient(circle at 86% 0%, rgba(141,130,246,.09), transparent 28%),

    radial-gradient(circle at 50% 100%, rgba(47,196,141,.04), transparent 30%),

    linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 30%, var(--bg-3) 68%, var(--bg-4) 100%);

}

.logo,

.app-top{

  background:rgba(9,16,28,.72);

  border-color:rgba(255,255,255,.10);

  box-shadow:0 10px 24px rgba(0,0,0,.16);

}

.logo-dot{

  box-shadow:0 0 0 4px rgba(95,148,255,.12);

}

.hero{

  padding-bottom:28px;

}

.hero h1{

  max-width:860px;

  margin-left:auto;

  margin-right:auto;

  text-shadow:0 10px 26px rgba(0,0,0,.14);

}

.hero p{

  max-width:740px;

  color:#c6d4ea;

}

.hero-badge{

  background:rgba(255,255,255,.055);

  color:#dde9fb;

  border-color:rgba(255,255,255,.09);

  box-shadow:none;

}

.hero-trust-chip{

  background:rgba(255,255,255,.04);

  color:#dbe7fb;

  border-color:rgba(255,255,255,.08);

  box-shadow:none;

}

.container,

.content-section{

  border:1px solid var(--line);

  background:

    linear-gradient(180deg, rgba(13,20,34,.965) 0%, rgba(9,14,24,.987) 100%);

  box-shadow:var(--shadow-xl);

}

.container::before,

.content-section::before{

  background:radial-gradient(circle, rgba(95,148,255,.12), transparent 66%);

}

.container::after,

.content-section::after{

  background:radial-gradient(circle, rgba(141,130,246,.09), transparent 68%);

}

.preview-card,

.tool-shell,

.app-link-card,

.upgrade,

.inline-info-card{

  border:1px solid var(--line);

  box-shadow:var(--shadow-md);

}

.preview-card{

  background:

    linear-gradient(180deg, rgba(255,255,255,.055) 0%, rgba(255,255,255,.025) 100%);

}

.preview-badge{

  box-shadow:0 10px 20px rgba(185,75,95,.12);

}

.preview-score{

  background:rgba(255,255,255,.05);

  color:#ecf2ff;

}

.preview-domain{

  color:#ffffff;

}

.preview-sub{

  color:#ccdaee;

}

.preview-signal{

  background:rgba(255,255,255,.045);

  border:1px solid rgba(255,255,255,.07);

  color:#f6dfe3;

}

.tool-shell{

  background:

    linear-gradient(180deg, rgba(255,255,255,.045) 0%, rgba(255,255,255,.02) 100%);

  border-color:var(--line);

}

textarea,

input{

  border:1px solid rgba(255,255,255,.10);

  background:rgba(7,12,21,.92);

  box-shadow:none;

}

textarea:focus,

input:focus{

  border-color:rgba(95,148,255,.58);

  box-shadow:0 0 0 4px rgba(95,148,255,.10);

  background:rgba(8,14,24,.97);

}

.check,

.plan,

.plan.secondary,

.plan.tertiary,

.upgrade-top,

.app-link-button{

  box-shadow:0 14px 30px rgba(0,0,0,.20);

}

.check{

  background:linear-gradient(135deg,#7b79f5 0%, #4e85ff 52%, #31c48d 100%);

}

.upgrade-top{

  background:linear-gradient(135deg,#817cf4 0%, #4c84ff 52%, #2fc08a 100%);

}

.app-link-button{

  background:linear-gradient(135deg,#4d73eb 0%, #31c48d 100%);

}

.app-link-card{

  background:

    linear-gradient(180deg, rgba(255,255,255,.04) 0%, rgba(255,255,255,.02) 100%);

}

.inline-info-card,

.content-bridge,

.content-close,

.story-card,

.recognition-chip{

  border:1px solid var(--line);

  box-shadow:none;

}

.inline-info-card{

  background:

    linear-gradient(180deg, rgba(255,255,255,.04) 0%, rgba(255,255,255,.02) 100%);

}

.content-bridge,

.content-close{

  background:rgba(255,255,255,.03);

}

.content-section h2{

  font-size:38px;

  letter-spacing:-.036em;

}

.content-section h3{

  letter-spacing:-.03em;

}

.recognition-chip{

  border-radius:20px;

  background:

    linear-gradient(180deg, rgba(255,255,255,.045) 0%, rgba(255,255,255,.02) 100%);

}

.recognition-label{

  color:#96c9ff;

}

.recognition-copy{

  color:#e7effd;

}

.story-stack{

  display:grid;

  gap:14px;

}

.story-card{

  border-radius:20px;

  background:

    linear-gradient(180deg, rgba(255,255,255,.045) 0%, rgba(255,255,255,.02) 100%);

}

.story-card.lead{

  background:

    linear-gradient(180deg, rgba(116,132,235,.16) 0%, rgba(255,255,255,.025) 100%);

  border-color:rgba(141,132,247,.24);

}

.story-card-title{

  color:#9ccbff;

}

.story-card p{

  margin:0;

  font-size:16px;

  line-height:1.72;

  color:#dde8fa;

}

.link-section{

  border-top:1px solid rgba(255,255,255,.07);

}

.related-links a{

  color:#9fd1ff;

}

.note{

  color:#94a7c5;

}

.success{

  color:#8ce9b6;

}

#email{

  margin-top:14px;

  background:rgba(255,255,255,.03);

  border-color:rgba(255,255,255,.08);

}

#email::placeholder{

  color:#8899b7;

}

#result{

  margin-top:24px;

}

.footer{

  color:#93a6c5;

}

.footer a{

  color:#9fd1ff;

}

@media (max-width:640px){

  .content-section h2{font-size:30px;}

  .story-card p{font-size:15px;line-height:1.68;}

  .recognition-chip{border-radius:16px;}

}

`;

  const SPLIT_SEO_PARAGRAPHS_FROM_HTML_FUNCTION = `function splitSeoParagraphsFromHtml(seoContent) {

  const html = String(seoContent.innerHTML || "").trim();

  if (!html) return [];

  const parser = document.createElement("div");

  parser.innerHTML = html;

  let paragraphs = Array.from(parser.querySelectorAll("p"))

    .map(p => p.textContent.trim())

    .filter(Boolean);

  if (paragraphs.length) return paragraphs;

  paragraphs = parser.innerHTML

    .replace(/<br\\s*\\/?>/gi, "\\n")

    .replace(/<\\/div>/gi, "\\n\\n")

    .replace(/<\\/section>/gi, "\\n\\n")

    .replace(/<[^>]+>/g, "")

    .split(/\\n\\s*\\n/)

    .map(p => p.replace(/\\s+/g, " ").trim())

    .filter(Boolean);

  return paragraphs;

}`;

  const STRIP_SEO_FILLER_FUNCTION = `function stripSeoFiller(text) {

  return String(text || "")

    .replace(/\\b(it is important to note that|it is worth noting that|in many cases|in some cases|in a lot of cases)\\b/gi, "")

    .replace(/\\b(this is because|the reason for this is that)\\b/gi, "because")

    .replace(/\\b(as always|of course|basically|simply put|put simply)\\b/gi, "")

    .replace(/\\b(when it comes to this|at the end of the day)\\b/gi, "")

    .replace(/\\bkeep in mind that\\b/gi, "")

    .replace(/\\bmake sure to\\b/gi, "")

    .replace(/\\s+/g, " ")

    .trim();

}`;

  const NORMALIZE_SEO_SENTENCE_FUNCTION = `function normalizeSeoSentence(sentence) {

  return stripSeoFiller(sentence)

    .replace(/^[-•]\\s*/, "")

    .replace(/\\s+/g, " ")

    .replace(/\\s+([,.;!?])/g, "$1")

    .replace(/\\.{2,}/g, ".")

    .trim();

}`;

  const BREAK_PARAGRAPH_INTO_SENTENCES_FUNCTION = `function breakParagraphIntoSentences(paragraph) {

  return String(paragraph || "")

    .replace(/\\s+/g, " ")

    .split(/(?<=[.!?])\\s+/)

    .map(normalizeSeoSentence)

    .filter(Boolean);

}`;

  const IS_TOO_GENERIC_SENTENCE_FUNCTION = `function isTooGenericSentence(sentence) {

  const lower = String(sentence || "").toLowerCase();

  if (!lower) return true;

  if (lower.length < 36) return true;

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

    "one thing to remember"

  ];

  return genericStarts.some(start => lower.startsWith(start));

}`;

  const BUILD_SEO_CARD_GROUPS_FUNCTION = `function buildSeoCardGroups(paragraphs) {

  const sentences = paragraphs

    .flatMap(breakParagraphIntoSentences)

    .map(normalizeSeoSentence)

    .filter(Boolean)

    .filter(sentence => !isTooGenericSentence(sentence));

  const deduped = [];

  const seen = new Set();

  for (const sentence of sentences) {

    const key = sentence.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

    if (!key || seen.has(key)) continue;

    seen.add(key);

    deduped.push(sentence);

  }

  const grouped = [];

  let current = [];

  for (const sentence of deduped) {

    const currentText = current.join(" ");

    const projected = (currentText ? currentText + " " : "") + sentence;

    if (current.length >= 2 || projected.length > 250) {

      if (current.length) grouped.push(current.join(" "));

      current = [sentence];

      continue;

    }

    current.push(sentence);

  }

  if (current.length) grouped.push(current.join(" "));

  return grouped

    .map(group => group.replace(/\\s+/g, " ").trim())

    .filter(Boolean)

    .slice(0, 4);

}`;

  const BUILD_SEO_CARD_TITLES_FUNCTION = `function buildSeoCardTitles(keywordRaw) {

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

}`;

  const RENDER_SEO_CONTENT_CARDS_FUNCTION = `function renderSeoContentCards(groups) {

  const seoContent = document.getElementById("seoContent");

  if (!seoContent) return;

  if (!groups.length) {

    seoContent.innerHTML = "";

    return;

  }

  const titles = buildSeoCardTitles(RAW_KEYWORD || "");

  seoContent.innerHTML = \`

    <div class="story-stack">

      \${groups.map((group, index) => \`

        <article class="story-card\${index === 0 ? " lead" : ""}">

          <div class="story-card-title">

            <span class="story-card-title-icon">\${titles[index] ? titles[index][0] : "•"}</span>

            <span>\${titles[index] ? titles[index][1] : "More to know"}</span>

          </div>

          <p>\${escapeHtml(group)}</p>

        </article>

      \`).join("")}

    </div>

  \`;

}`;

  const CLEAN_SEO_CONTENT_FUNCTION = `function cleanSeoContent() {

  const seoContent = document.getElementById("seoContent");

  if (!seoContent) return;

  seoContent.innerHTML = seoContent.innerHTML

    .replace(/\\*\\*/g, "")

    .replace(/<p>\\s*<\\/p>/g, "")

    .trim();

  const paragraphs = splitSeoParagraphsFromHtml(seoContent)

    .map(p => stripSeoFiller(p))

    .map(p => p.replace(/\\s+/g, " ").trim())

    .filter(Boolean);

  const groups = buildSeoCardGroups(paragraphs);

  renderSeoContentCards(groups);

}`;

  html = upsertStyleBlock(html, "token-risk-polish-style", TOKEN_RISK_POLISH_STYLE);

  html = upsertFunction(

    html,

    "splitSeoParagraphsFromHtml",

    SPLIT_SEO_PARAGRAPHS_FROM_HTML_FUNCTION,

    "cleanSeoContent"

  );

  html = upsertFunction(

    html,

    "stripSeoFiller",

    STRIP_SEO_FILLER_FUNCTION,

    "cleanSeoContent"

  );

  html = upsertFunction(

    html,

    "normalizeSeoSentence",

    NORMALIZE_SEO_SENTENCE_FUNCTION,

    "cleanSeoContent"

  );

  html = upsertFunction(

    html,

    "breakParagraphIntoSentences",

    BREAK_PARAGRAPH_INTO_SENTENCES_FUNCTION,

    "cleanSeoContent"

  );

  html = upsertFunction(

    html,

    "isTooGenericSentence",

    IS_TOO_GENERIC_SENTENCE_FUNCTION,

    "cleanSeoContent"

  );

  html = upsertFunction(

    html,

    "buildSeoCardGroups",

    BUILD_SEO_CARD_GROUPS_FUNCTION,

    "cleanSeoContent"

  );

  html = upsertFunction(

    html,

    "buildSeoCardTitles",

    BUILD_SEO_CARD_TITLES_FUNCTION,

    "cleanSeoContent"

  );

  html = upsertFunction(

    html,

    "renderSeoContentCards",

    RENDER_SEO_CONTENT_CARDS_FUNCTION,

    "cleanSeoContent"

  );

  html = upsertFunction(

    html,

    "cleanSeoContent",

    CLEAN_SEO_CONTENT_FUNCTION,

    "cleanRelatedLinks"

  );

  ensureContains(html, 'id="tokenAddress"', "token input");

  ensureContains(html, "function splitSeoParagraphsFromHtml(seoContent)", "seo paragraph splitter");

  ensureContains(html, "function stripSeoFiller(text)", "seo filler stripper");

  ensureContains(html, "function buildSeoCardGroups(paragraphs)", "seo card grouping");

  ensureContains(html, "function buildSeoCardTitles(keywordRaw)", "seo card titles");

  ensureContains(html, "function renderSeoContentCards(groups)", "seo card renderer");

  ensureContains(html, "function cleanSeoContent()", "seo content cleanup");

  ensureContains(html, 'style id="token-risk-polish-style"', "token polish style block");

  ensureContains(html, 'fetch(API + "/analyze-token"', "checker endpoint preserved");

  ensureContains(html, "function formatTokenResult(data)", "checker formatter preserved");

  ensureContains(html, 'style id="token-risk-analysis-style"', "checker analysis style preserved");

  fs.writeFileSync(TEMPLATE_PATH, html, "utf8");

  console.log(`Template updated: ${TEMPLATE_PATH}`);

}

main();