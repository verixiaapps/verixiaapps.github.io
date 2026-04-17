const fs = require("fs");
const path = require("path");

const TARGET_TEMPLATE_FILE =
  process.env.TARGET_TEMPLATE_FILE ||
  "token-risk-template/token-risk-template-a.html";

const DRY_RUN = String(process.env.DRY_RUN).toLowerCase() === "true";
const BACKUP_DIR = "backup";

if (!TARGET_TEMPLATE_FILE.startsWith("token-risk-template/")) {
  console.error("Only token-risk-template files are allowed.");
  process.exit(1);
}

if (!fs.existsSync(TARGET_TEMPLATE_FILE)) {
  console.error("File does not exist:", TARGET_TEMPLATE_FILE);
  process.exit(1);
}

// ------------------------------------
// TOKEN RISK PREMIUM SURFACE UPDATE
// CORE CODE / CHECKER FLOW STAYS INTACT
// ------------------------------------
const NEW_FAQ_JSONLD = `{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"How can I tell if a token might be risky?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Look for concentrated ownership, weak liquidity, suspicious contract behavior, aggressive hype, and pressure to buy or connect quickly. Always verify before acting."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do before buying or connecting to a token?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Review the token contract, liquidity setup, wallet permissions, ownership controls, and project credibility. Do not buy or connect until you understand the risks."
      }
    },
    {
      "@type":"Question",
      "name":"Can a token look legitimate and still be dangerous?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Yes. A token can appear active or popular while still carrying risks such as concentrated supply, liquidity problems, unsafe permissions, or contract patterns that expose buyers."
      }
    }
  ]
}`;

const NEW_HERO_BADGES = `
    <div class="hero-badge-row">
      <div class="hero-badge">Real-time token risk analysis</div>
      <div class="hero-badge">Premium contract warning page</div>
      <div class="hero-badge">Built for repeat checks</div>
    </div>
`;

const NEW_HERO_TRUST = `
    <div class="hero-trust">
      <div class="hero-trust-chip">Check before you buy</div>
      <div class="hero-trust-chip">Check before you connect</div>
      <div class="hero-trust-chip">Check before you approve</div>
    </div>
`;

const NEW_SYSTEM_BADGE = "Example token risk pattern for reference";

const NEW_PREVIEW_SIGNALS = `
        <div class="preview-signal"><span class="preview-signal-icon">🧬</span><span>Contract behavior needs review</span></div>
        <div class="preview-signal"><span class="preview-signal-icon">📉</span><span>Liquidity or holder risk may be present</span></div>
        <div class="preview-signal"><span class="preview-signal-icon">🧨</span><span>Buy or wallet pressure pattern detected</span></div>
`;

const NEW_TEXTAREA_PLACEHOLDER =
  "Paste the token name, contract address, project name, wallet prompt, or DEX link you're unsure about...";

const NEW_INPUT_HELP =
  "Examples: token contract, DEX pair, wallet approval prompt, token page, project name";

const NEW_CHECK_BUTTON = "🪙 Check Token Risk";

const NEW_TOOL_NOTE =
  "Get a clear risk level, token red flags, and what to do next";

const NEW_APP_CARD = `
    <div class="app-link-card">
      <h4>Check risky tokens anytime</h4>
      <p>Risky token setups do not happen once. Use the app to check the next token, wallet prompt, or approval request before you buy or connect.</p>
      <a class="app-link-button" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">Download the App</a>
    </div>
`;

const NEW_UPGRADE_H3 = "Don’t Miss the Next Risky Token";

const NEW_UPGRADE_COPY = `
      <div class="upgrade-copy">
        High-risk token setups do not show up once. If you are checking contracts, wallet prompts, or new assets, more may follow. Review each one before you buy, connect, or approve.
      </div>
`;

const NEW_UPGRADE_SUPPORT_1 = `
      <div style="margin-top:10px;font-size:13px;color:#d4e2f5;">
        Built for ongoing protection against risky tokens, unsafe contracts, wallet traps, and approval mistakes
      </div>
`;

const NEW_UPGRADE_SUPPORT_2 = `
      <div style="margin-top:8px;margin-bottom:10px;font-size:14px;color:#d4e2f5;">
        Unlimited token risk checks • Cancel anytime
      </div>
`;

const NEW_CONTENT_CLOSE = `
    <div class="content-close">
      Risk often spikes right before a rushed buy, wallet connection, or approval. If something feels off, pause and verify the token setup through trusted sources before taking action.
    </div>
`;

const NEW_RECOGNITION_BANK_BLOCK = `return [
      ["What people notice first", "A token pushing fast hype, sudden momentum, or easy upside before the fundamentals are clear."],
      ["What risky setups hide", "Weak liquidity, concentrated ownership, unsafe permissions, or contract behavior that puts buyers at risk."],
      ["Why it feels legitimate", "The branding, chart action, and community posts can make a risky token look more established than it really is."],
      ["Why this page helps", "It is built to surface token risk patterns quickly so you can slow down before you buy, connect, or approve."]
    ];`;

const NEW_RECOGNITION_CRYPTO_BLOCK = `return [
      ["What people notice first", "A token, contract, or wallet prompt that looks active, urgent, or easy to trust in the moment."],
      ["What risky setups hide", "Unsafe approvals, liquidity weakness, concentrated supply, or contract behavior that can hurt buyers fast."],
      ["Why it feels legitimate", "The page or project can look polished even when the real risk sits in ownership, permissions, or token structure."],
      ["Why this page helps", "It is built to highlight token risk signals before you buy, connect your wallet, or approve anything."]
    ];`;

const NEW_PREVIEW_CRYPTO_BLOCK = `signals = [
      "Contract behavior needs review",
      "Liquidity or holder risk may be present",
      "Buy or wallet pressure pattern detected"
    ];`;

const NEW_PREVIEW_FALLBACK_SIGNALS = `let signals = [
    "Contract behavior needs review",
    "Liquidity or holder risk may be present",
    "Buy or wallet pressure pattern detected"
  ];`;

const NEW_PREVIEW_BADGE = "🧨 Example Token Risk Pattern";
const NEW_PREVIEW_SCORE = "Token Risk Example";
const NEW_PREVIEW_DOMAIN = "Example risky token";
const NEW_PREVIEW_SUB = "Common signals found in similar token setups";

const NEW_APPLY_INTENT_CRYPTO = `
  if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft", "token", "contract", "dex", "solana"])) {
    textarea.placeholder = "Paste the token name, contract address, project name, wallet prompt, or DEX link you're unsure about...";
    inputHelp.textContent = "Examples: token contract, DEX pair, wallet approval prompt, token page, project name";
    return;
  }
`;

const NEW_BUILD_HERO_TITLE_CRYPTO = `if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft", "token", "contract", "dex", "solana"])) {
    return \`Is \${cleanTitle} Safe? Token Risk, Contract Warnings & What To Check\`;
  }`;

const NEW_BUILD_HERO_SUB_CRYPTO = `if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft", "token", "contract", "dex", "solana"])) {
    return \`Check \${readableKeyword} for token risk before you buy, connect your wallet, approve a transaction, or trust the setup.\`;
  }`;

const NEW_BUILD_CONTENT_HEADING_CRYPTO = `if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft", "token", "contract", "dex", "solana"])) {
    return \`What \${cleanTitle} Token Risk Often Looks Like\`;
  }`;

const NEW_BUILD_CONTENT_BRIDGE_CRYPTO = `if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft", "token", "contract", "dex", "solana"])) {
    return \`\${chooseBridgeIntro(cleanSentenceKeyword)} use the checker above before you buy, connect your wallet, approve anything, or trust the token setup. Risky tokens often look strongest right before someone acts too quickly.\`;
  }`;

const NEW_BUILD_SEO_CARD_TITLES_CRYPTO = `return [
      ["🧬", "What this token setup often looks like"],
      ["📉", "Where the risk starts showing"],
      ["🔐", "How the contract or wallet trap works"],
      ["🧨", "What can happen after you buy or approve"]
    ];`;

const NEW_CLEAN_SEO_SLICE = ".slice(0, 4)";

const NEW_SUMMARY_HIGH =
  "This token shows multiple high-risk indicators. Treat it as unsafe until you verify the contract, liquidity, ownership, and wallet permissions through trusted sources.";
const NEW_SUMMARY_MEDIUM =
  "This token shows warning signs. Be cautious and review the contract, wallet permissions, liquidity setup, and holder concentration before you buy or connect.";
const NEW_SUMMARY_LOW =
  "This token shows fewer obvious risk indicators, but you should still verify the contract, liquidity, ownership, and wallet permissions before taking action.";
const NEW_SUMMARY_UNKNOWN =
  "We could not determine a clear token risk level. Treat the setup cautiously and verify the contract and permissions before you buy, connect, or approve.";

const NEW_PAYLINE_HIGH =
  "People lose money on setups like this every day. If another token like this shows up tomorrow, acting too fast could cost you.";
const NEW_PAYLINE_MEDIUM =
  "Risky token setups often do not stop at one. If you are seeing one now, more may follow. Check the next one before you buy, connect, or approve.";
const NEW_PAYLINE_LOW =
  "Even lower-risk tokens can become expensive when later prompts ask for approvals, permissions, wallet access, or rushed buys.";
const NEW_PAYLINE_UNKNOWN =
  "When the risk is unclear, the safest move is to pause, verify the token setup, and treat the next similar token carefully too.";

const NEW_CHIP_HIGH = "Token Risk: Strong Match";
const NEW_CHIP_MEDIUM = "Token Risk: Moderate";
const NEW_CHIP_LOW = "Token Risk: Lower";
const NEW_CHIP_UNKNOWN = "Token Risk: Review Needed";

const NEW_SHARE_TEXT =
  "This token may be risky. Check it before you buy, connect, or approve:";
const NEW_WARNING_MESSAGE = `This token may be risky.
Check it before you buy, connect, or approve:
\${getShareUrl()}`;

const NEW_RESULT_EMPTY =
  "Paste a token name, contract address, wallet prompt, project page, or DEX link to check token risk before you act.";
const NEW_RESULT_LOADING =
  "Checking for token risk indicators, contract issues, liquidity concerns, wallet traps, and suspicious permission patterns.";

const NEW_LIMIT_CARD =
  "Unlock unlimited protection so you can check the next token, contract, wallet prompt, or approval request before it costs you.";

const NEW_ERROR_CARD =
  "We could not analyze this right now. Please try again in a moment.";

const NEW_RESULT_ACTION_FALLBACK =
  "Do not buy, do not connect your wallet, and do not approve anything until you verify the token contract, liquidity, and permissions through trusted sources.";

const NEW_RESULT_SIGNAL_FALLBACK =
  "Review the contract, wallet permissions, liquidity, holder concentration, and any pressure to buy or approve quickly.";

const NEW_RESULT_CONTINUATION =
  "If this token reached you once, similar high-risk setups may already be circulating. Risky token patterns often repeat across projects and communities.";

const NEW_RESULT_SECTION_SIGNALS = "Risk Indicators";
const NEW_RESULT_SECTION_ACTIONS = "Suggested Actions";
const NEW_RESULT_CTA = "🔁 Not sure about another token? Check it now";
const NEW_SHARE_ALERT = "⚠️ Risky token setups often spread fast";
const NEW_SHARE_COPY =
  "Know someone who could see this same token or wallet prompt? Send this warning before they buy, connect, or approve.";
const NEW_COPY_WARNING_BTN = "⚠️ Copy Warning";

const NEW_EMBEDDED_BUTTON = "🔓 Unlock Unlimited Token Checks";
const NEW_EMBEDDED_TITLE = "Unlock unlimited token checks instantly";
const NEW_POST_PURCHASE =
  "✅ Unlimited token checks are active with this account";

// ------------------------------------
// HELPERS
// ------------------------------------
function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function ensureBackupDir() {
  if (!fs.existsSync(BACKUP_DIR)) {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
  }
}

function createBackup(originalContent) {
  ensureBackupDir();

  const safeName = TARGET_TEMPLATE_FILE.replace(/\//g, "__");
  const backupPath = path.join(
    BACKUP_DIR,
    `${safeName}__${timestamp()}.html`
  );

  if (!DRY_RUN) {
    fs.writeFileSync(backupPath, originalContent, "utf8");
  }

  console.log("Backup created:", backupPath);
}

function replaceWithCheck(html, regex, replacement, label) {
  const updated = html.replace(regex, replacement);

  if (updated === html) {
    console.warn(`No change for ${label}`);
    return html;
  }

  console.log(`Updated ${label}`);
  return updated;
}

// ------------------------------------
// MAIN
// ------------------------------------
const original = fs.readFileSync(TARGET_TEMPLATE_FILE, "utf8");
createBackup(original);

let updated = original;

// premium accent colors, same structure
updated = replaceWithCheck(updated, /--cyan:#66d9ef;/, "--cyan:#39e7ff;", "cyan color");
updated = replaceWithCheck(updated, /--cyan-2:#28bfd9;/, "--cyan-2:#10cfe3;", "cyan-2 color");
updated = replaceWithCheck(updated, /--violet:#8b78f2;/, "--violet:#6f5af7;", "violet color");
updated = replaceWithCheck(updated, /--violet-2:#7460e8;/, "--violet-2:#5e49e2;", "violet-2 color");
updated = replaceWithCheck(updated, /--emerald:#18b67f;/, "--emerald:#00c48c;", "emerald color");
updated = replaceWithCheck(updated, /--emerald-2:#109466;/, "--emerald-2:#00a873;", "emerald-2 color");
updated = replaceWithCheck(updated, /--amber:#e7a93d;/, "--amber:#ffb020;", "amber color");
updated = replaceWithCheck(updated, /--red:#d96574;/, "--red:#ff4d57;", "red color");
updated = replaceWithCheck(updated, /--red-2:#b94b5f;/, "--red-2:#db3743;", "red-2 color");

// FAQ JSON-LD
updated = replaceWithCheck(
  updated,
  /<script type="application\/ld\+json">\s*\{\s*"@context":"https:\/\/schema\.org",\s*"@type":"FAQPage"[\s\S]*?<\/script>/i,
  `<script type="application/ld+json">
${NEW_FAQ_JSONLD}
</script>`,
  "FAQ JSON-LD"
);

// hero surface
updated = replaceWithCheck(
  updated,
  /<div class="hero-badge-row">[\s\S]*?<\/div>/i,
  NEW_HERO_BADGES.trim(),
  "hero badges"
);
updated = replaceWithCheck(
  updated,
  /<div class="hero-trust">[\s\S]*?<\/div>/i,
  NEW_HERO_TRUST.trim(),
  "hero trust chips"
);

// system badge + preview defaults
updated = replaceWithCheck(
  updated,
  /<div class="system-badge">[\s\S]*?<\/div>/i,
  `<div class="system-badge">${NEW_SYSTEM_BADGE}</div>`,
  "system badge"
);
updated = replaceWithCheck(
  updated,
  /<div class="preview-domain" id="previewDomain">[\s\S]*?<\/div>/i,
  `<div class="preview-domain" id="previewDomain">${NEW_PREVIEW_DOMAIN}</div>`,
  "preview domain"
);
updated = replaceWithCheck(
  updated,
  /<div class="preview-sub" id="previewSub">[\s\S]*?<\/div>/i,
  `<div class="preview-sub" id="previewSub">${NEW_PREVIEW_SUB}</div>`,
  "preview sub"
);
updated = replaceWithCheck(
  updated,
  /<div class="preview-signals" id="previewSignals">[\s\S]*?<\/div>\s*<\/div>/i,
  `<div class="preview-signals" id="previewSignals">
${NEW_PREVIEW_SIGNALS}
      </div>
    </div>`,
  "preview signals markup"
);

// checker card copy
updated = replaceWithCheck(
  updated,
  /<textarea id="text" placeholder="[^"]*"><\/textarea>/i,
  `<textarea id="text" placeholder="${NEW_TEXTAREA_PLACEHOLDER}"></textarea>`,
  "textarea placeholder"
);
updated = replaceWithCheck(
  updated,
  /<div class="input-help">[\s\S]*?<\/div>/i,
  `<div class="input-help">${NEW_INPUT_HELP}</div>`,
  "input help"
);
updated = replaceWithCheck(
  updated,
  /<button class="check" onclick="check\(\)">[\s\S]*?<\/button>/i,
  `<button class="check" onclick="check()">${NEW_CHECK_BUTTON}</button>`,
  "check button"
);
updated = replaceWithCheck(
  updated,
  /<div class="note">Get a clear risk level, key red flags, and what to do next<\/div>/i,
  `<div class="note">${NEW_TOOL_NOTE}</div>`,
  "tool note"
);

// app card
updated = replaceWithCheck(
  updated,
  /<div class="app-link-card">[\s\S]*?<\/div>\s*<div class="upgrade"/i,
  `${NEW_APP_CARD.trim()}

    <div class="upgrade"`,
  "app card"
);

// upgrade copy
updated = replaceWithCheck(
  updated,
  /<h3>Don’t Miss the Next Scam<\/h3>/i,
  `<h3>${NEW_UPGRADE_H3}</h3>`,
  "upgrade heading"
);
updated = replaceWithCheck(
  updated,
  /<div class="upgrade-copy">[\s\S]*?<\/div>/i,
  NEW_UPGRADE_COPY.trim(),
  "upgrade copy"
);
updated = replaceWithCheck(
  updated,
  /<div style="margin-top:10px;font-size:13px;color:#d4e2f5;">[\s\S]*?<\/div>/i,
  NEW_UPGRADE_SUPPORT_1.trim(),
  "upgrade support 1"
);
updated = replaceWithCheck(
  updated,
  /<div style="margin-top:8px;margin-bottom:10px;font-size:14px;color:#d4e2f5;">[\s\S]*?<\/div>/i,
  NEW_UPGRADE_SUPPORT_2.trim(),
  "upgrade support 2"
);

// content close
updated = replaceWithCheck(
  updated,
  /<div class="content-close">[\s\S]*?<\/div>\s*<\/section>/i,
  `${NEW_CONTENT_CLOSE.trim()}
  </section>`,
  "content close"
);

// JS surface transformations only
updated = replaceWithCheck(
  updated,
  /return \[\s*\["What people notice first", "A wallet prompt, support message, withdrawal issue, or token claim that looks urgent and easy to fix\."\],\s*\["What scammers want", "A connection approval, seed phrase, recovery detail, or fast transfer that cannot be reversed later\."\],\s*\["Why it feels believable", "The page copies exchange language, wallet prompts, support wording, and time pressure that feels technical\."\],\s*\["What makes it risky", "The first click often looks harmless until it turns into approvals, verification steps, or account access loss\."\]\s*\];/i,
  NEW_RECOGNITION_CRYPTO_BLOCK,
  "crypto recognition chips"
);
updated = replaceWithCheck(
  updated,
  /return \[\s*\["What people notice first", "A billing alert, refund notice, charge warning, verification code, or login issue that triggers panic fast\."\],\s*\["What scammers want", "A sign-in, card detail, payment confirmation, or one rushed response before you check the real account\."\],\s*\["Why it feels believable", "The message copies brand names, invoice language, account alerts, and payment wording people already trust\."\],\s*\["What makes it risky", "The fake step usually appears right when the message makes the account problem feel urgent or expensive\."\]\s*\];/i,
  NEW_RECOGNITION_BANK_BLOCK,
  "bank recognition chips"
);

updated = replaceWithCheck(
  updated,
  /let signals = \[\s*"Suspicious domain mismatch",\s*"Urgent language detected",\s*"Payment request via gift card"\s*\];/i,
  NEW_PREVIEW_FALLBACK_SIGNALS,
  "preview default signals block"
);
updated = replaceWithCheck(
  updated,
  /signals = \[\s*"Urgent transfer or wallet request",\s*"High-return or recovery promise",\s*"Support or investment impersonation risk"\s*\];/i,
  NEW_PREVIEW_CRYPTO_BLOCK,
  "preview crypto signals"
);
updated = replaceWithCheck(
  updated,
  /previewBadge\.textContent = `🔴 \$\{riskLabel\}`;/,
  `previewBadge.textContent = "${NEW_PREVIEW_BADGE}";`,
  "preview badge text"
);
updated = replaceWithCheck(
  updated,
  /previewScore\.textContent = trustScore;/,
  `previewScore.textContent = "${NEW_PREVIEW_SCORE}";`,
  "preview score text"
);
updated = replaceWithCheck(
  updated,
  /previewDomain\.textContent = cleanTitle;/,
  `previewDomain.textContent = cleanTitle || "${NEW_PREVIEW_DOMAIN}";`,
  "preview domain js"
);
updated = replaceWithCheck(
  updated,
  /previewSub\.textContent = sub;/,
  `previewSub.textContent = "${NEW_PREVIEW_SUB}";`,
  "preview sub js"
);

// add token-aware branches without altering core flow
updated = replaceWithCheck(
  updated,
  /if \(isGuidanceStyleKeyword\(lower\)\) \{\s*return `\$\{readableTitle\}: Safety Tips, Warning Signs & What To Do`;\s*\}/,
  `if (isGuidanceStyleKeyword(lower)) {
    return \`\${readableTitle}: Safety Tips, Warning Signs & What To Do\`;
  }

  ${NEW_BUILD_HERO_TITLE_CRYPTO}`,
  "hero title token branch"
);
updated = replaceWithCheck(
  updated,
  /if \(isGuidanceStyleKeyword\(lower\) \|\| isQuestionStyleKeyword\(lower\)\) \{\s*return "Use the checker below to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information\.";\s*\}/,
  `if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker below to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information.";
  }

  ${NEW_BUILD_HERO_SUB_CRYPTO}`,
  "hero sub token branch"
);
updated = replaceWithCheck(
  updated,
  /if \(isGuidanceStyleKeyword\(lower\) \|\| isQuestionStyleKeyword\(lower\) \|\| lower\.startsWith\("almost "\)\) \{\s*return readableTitle;\s*\}/,
  `if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower) || lower.startsWith("almost ")) {
    return readableTitle;
  }

  ${NEW_BUILD_CONTENT_HEADING_CRYPTO}`,
  "content heading token branch"
);
updated = replaceWithCheck(
  updated,
  /if \(isGuidanceStyleKeyword\(lower\) \|\| isQuestionStyleKeyword\(lower\)\) \{\s*return "Use the checker above to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information\.";\s*\}/,
  `if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker above to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information.";
  }

  ${NEW_BUILD_CONTENT_BRIDGE_CRYPTO}`,
  "content bridge token branch"
);

updated = replaceWithCheck(
  updated,
  /if \(containsAny\(lower, \["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft"\]\)\) \{\s*textarea\.placeholder = "Paste the crypto message, wallet request, token offer, or support message you're unsure about\.\.\.";\s*inputHelp\.textContent = "Examples: wallet connect message, token airdrop, exchange alert, support DM, recovery offer";\s*return;\s*\}/,
  NEW_APPLY_INTENT_CRYPTO.trim(),
  "apply intent crypto block"
);

updated = replaceWithCheck(
  updated,
  /return \[\s*\["🪙", "What this wallet or token setup often looks like"\],\s*\["⏱️", "Where the urgency gets dangerous"\],\s*\["🔁", "How the same trap appears in different forms"\],\s*\["💥", "What happens after the wrong approval or transfer"\]\s*\];/i,
  NEW_BUILD_SEO_CARD_TITLES_CRYPTO,
  "seo card titles crypto"
);

// keep 4 cards
updated = replaceWithCheck(
  updated,
  /\.slice\(0,\s*4\)/,
  NEW_CLEAN_SEO_SLICE,
  "seo slice limit"
);

// result / share / upgrade text
updated = replaceWithCheck(
  updated,
  /return "This message shows multiple scam signals\. Treat it as unsafe until you verify it directly through the official website, app, company, or platform\.";/,
  `return "${NEW_SUMMARY_HIGH}";`,
  "summary high"
);
updated = replaceWithCheck(
  updated,
  /return "This message shows warning signs\. Be cautious and verify the sender, offer, or website before you click, reply, send money, or share information\.";/,
  `return "${NEW_SUMMARY_MEDIUM}";`,
  "summary medium"
);
updated = replaceWithCheck(
  updated,
  /return "This message shows fewer obvious scam signals, but you should still verify anything involving links, payments, logins, or personal information before taking action\.";/,
  `return "${NEW_SUMMARY_LOW}";`,
  "summary low"
);
updated = replaceWithCheck(
  updated,
  /return "We could not determine a clear risk level\. Treat the message cautiously and verify it through official sources before you do anything else\.";/,
  `return "${NEW_SUMMARY_UNKNOWN}";`,
  "summary unknown"
);

updated = replaceWithCheck(
  updated,
  /return "People lose money from messages like this every day\. If another one shows up tomorrow, guessing wrong could cost you\.";/,
  `return "${NEW_PAYLINE_HIGH}";`,
  "payline high"
);
updated = replaceWithCheck(
  updated,
  /return "Suspicious messages often do not stop at one\. If you have seen one, more may follow\. Check the next one before you click, reply, or pay\.";/,
  `return "${NEW_PAYLINE_MEDIUM}";`,
  "payline medium"
);
updated = replaceWithCheck(
  updated,
  /return "Even lower-risk messages can become expensive when later versions ask for logins, payments, codes, or urgent action\.";/,
  `return "${NEW_PAYLINE_LOW}";`,
  "payline low"
);
updated = replaceWithCheck(
  updated,
  /return "When the risk is unclear, the safest move is to pause, verify this one, and treat the next similar message carefully too\.";/,
  `return "${NEW_PAYLINE_UNKNOWN}";`,
  "payline unknown"
);

updated = replaceWithCheck(
  updated,
  /if \(risk === "high"\) return "Pattern Match: Strong";/,
  `if (risk === "high") return "${NEW_CHIP_HIGH}";`,
  "chip high"
);
updated = replaceWithCheck(
  updated,
  /if \(risk === "medium"\) return "Pattern Match: Moderate";/,
  `if (risk === "medium") return "${NEW_CHIP_MEDIUM}";`,
  "chip medium"
);
updated = replaceWithCheck(
  updated,
  /if \(risk === "low"\) return "Pattern Match: Lower Risk";/,
  `if (risk === "low") return "${NEW_CHIP_LOW}";`,
  "chip low"
);
updated = replaceWithCheck(
  updated,
  /return "Pattern Match: Review Needed";/,
  `return "${NEW_CHIP_UNKNOWN}";`,
  "chip unknown"
);

updated = replaceWithCheck(
  updated,
  /return "

  /return "This message may be a scam\. Check it before you click, reply, or send money:";/,
  `return "${NEW_SHARE_TEXT}";`,
  "share text"
);
updated = replaceWithCheck(
  updated,
  /return `This message may be a scam\.\s*Check it before you click, reply, or send money:\s*\$\{getShareUrl$begin:math:text$$end:math:text$\}`;/,
  `return \`${NEW_WARNING_MESSAGE}\`;`,
  "warning message"
);

updated = replaceWithCheck(
  updated,
  /Paste a suspicious message, email, website, link, job offer, or investment pitch to check scam risk before you act\./,
  NEW_RESULT_EMPTY,
  "empty result text"
);
updated = replaceWithCheck(
  updated,
  /Checking for scam signals, risky patterns, payment traps, impersonation, and suspicious links\./,
  NEW_RESULT_LOADING,
  "loading result text"
);
updated = replaceWithCheck(
  updated,
  /Unlock unlimited protection so you can check the next suspicious message, link, or request before it costs you\./,
  NEW_LIMIT_CARD,
  "limit card text"
);
updated = replaceWithCheck(
  updated,
  /We could not analyze this right now\. Please try again in a moment\./,
  NEW_ERROR_CARD,
  "error result text"
);

updated = replaceWithCheck(
  updated,
  /signals = \["Review the sender, links, and any requests for money, urgency, or personal information\."\];/,
  `signals = ["${NEW_RESULT_SIGNAL_FALLBACK}"];`,
  "result signal fallback"
);
updated = replaceWithCheck(
  updated,
  /actions = \["Do not reply, do not click links, and verify directly through the official website, app, company, or platform before taking action\."\];/,
  `actions = ["${NEW_RESULT_ACTION_FALLBACK}"];`,
  "result action fallback"
);

updated = replaceWithCheck(
  updated,
  /<div class="result-continuation">If this reached you once, similar messages may already be on the way\. Scammers often repeat the same pattern across many people\.<\/div>/,
  `<div class="result-continuation">${NEW_RESULT_CONTINUATION}</div>`,
  "result continuation"
);
updated = replaceWithCheck(
  updated,
  /<div class="section-title">Detected Signals<\/div>/,
  `<div class="section-title">${NEW_RESULT_SECTION_SIGNALS}</div>`,
  "result signals title"
);
updated = replaceWithCheck(
  updated,
  /<div class="section-title">Recommended Actions<\/div>/,
  `<div class="section-title">${NEW_RESULT_SECTION_ACTIONS}</div>`,
  "result actions title"
);

updated = replaceWithCheck(
  updated,
  /🔁 Not sure about another message\? Check it now/,
  NEW_RESULT_CTA,
  "result cta"
);
updated = replaceWithCheck(
  updated,
  /⚠️ Messages like this are often sent in waves/,
  NEW_SHARE_ALERT,
  "share alert"
);
updated = replaceWithCheck(
  updated,
  /Know someone who could receive this same message\? Send this warning before they click, reply, or send money\./,
  NEW_SHARE_COPY,
  "share copy"
);
updated = replaceWithCheck(
  updated,
  /⚠️ Copy Warning/g,
  NEW_COPY_WARNING_BTN,
  "copy warning button"
);

// embedded upgrade wording only
updated = replaceWithCheck(
  updated,
  /postPurchase\.textContent = "✅ Unlimited scam checks are active with this account";/,
  `postPurchase.textContent = "${NEW_POST_PURCHASE}";`,
  "post purchase text"
);
updated = replaceWithCheck(
  updated,
  /button\.innerText = "🔓 Unlock Unlimited Checks";/,
  `button.innerText = "${NEW_EMBEDDED_BUTTON}";`,
  "embedded unlock button"
);
updated = replaceWithCheck(
  updated,
  /title\.textContent = "Unlock unlimited scam checks instantly";/,
  `title.textContent = "${NEW_EMBEDDED_TITLE}";`,
  "embedded title"
);

if (updated === original) {
  console.log("No changes made.");
  process.exit(0);
}

if (DRY_RUN) {
  console.log("DRY RUN - no file written");
  process.exit(0);
}

fs.writeFileSync(TARGET_TEMPLATE_FILE, updated, "utf8");
console.log("Updated token risk template:", TARGET_TEMPLATE_FILE);