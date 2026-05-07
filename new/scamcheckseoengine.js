import fetch from "node-fetch";

// ============================================================================
// Scam Check SEO Engine -- v4.0
//
// What changed from v3:
//
// 1. LIVE WEB SEARCH: fetchLiveScamExamples() calls Brave Search API
//    (BRAVE_SEARCH_API_KEY env var) before generation. Real domains,
//    real sender addresses, real amounts extracted from search results
//    and injected as primary context. Falls back cleanly to static
//    scenarios when the key is not set -- zero breaking change.
//
// 2. PROMPT INJECTION: buildSystemPrompt and buildUserPrompt both accept
//    liveCtx. Live details appear as a confirmed-real layer on top of
//    the structural scenario texture. Model is instructed to use them
//    where they fit naturally -- not force them.
//
// 3. LIVE ANCHOR FIRST: when live details are available, buildUserPrompt
//    leads with a confirmed real detail as the first anchor before the
//    static scenario texture. Gives the model specific verifiable material
//    to open on rather than pre-loaded pattern strings.
// ============================================================================

// ============================================================================
// Config
// ============================================================================

const MODEL   = process.env.OPENAI_SEO_MODEL || "gpt-4.1-mini";
const API_URL = "https://api.openai.com/v1/chat/completions";
const TIMEOUT_MS  = Number(process.env.OPENAI_SEO_TIMEOUT_MS  || 28000);
const MAX_RETRIES = Number(process.env.OPENAI_SEO_MAX_RETRIES || 3);

const INITIAL_TEMPERATURES  = [0.45, 0.82];
const POLISH_SCORE_CEILING  = 88;
const POLISH_GAP_THRESHOLD  = 8;
const REWRITE_SCORE_THRESHOLD = 72;

const BRAVE_SEARCH_URL      = "https://api.search.brave.com/res/v1/web/search";
const BRAVE_SEARCH_TIMEOUT  = Number(process.env.BRAVE_SEARCH_TIMEOUT_MS || 7000);

// ============================================================================
// Utility
// ============================================================================

function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function normalizeWs(str) {
  return String(str || "").replace(/\r/g, "").replace(/[^\S\n]+/g, " ").trim();
}
function lower(str) { return normalizeWs(str).toLowerCase(); }
function wordCount(str) { return normalizeWs(str).split(/\s+/).filter(Boolean).length; }

function splitParagraphs(str) {
  return normalizeWs(str)
    .split(/\n\s*\n/)
    .map((p) => p.replace(/\n/g, " ").trim())
    .filter(Boolean);
}

function splitSentences(str) {
  return (String(str || "").match(/[^.!?]+[.!?]+|[^.!?]+$/g) || []).map((s) => s.trim());
}

function unique(arr) { return [...new Set(arr.filter(Boolean))]; }

function hasAny(text, terms) {
  const t = lower(text);
  return terms.some((term) => t.includes(lower(term)));
}

function shouldRetry(status) {
  return status === 408 || status === 409 || status === 425 || status === 429 || status >= 500;
}

// ============================================================================
// Keyword normalisation
// ============================================================================

function normalizeKeyword(kw) {
  return String(kw || "")
    .replace(/[\u2013\u2014]/g, "-")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

// ============================================================================
// Category classification
// ============================================================================

function classify(keyword) {
  const t = lower(keyword);

  // Score every category by term specificity.
  // Longer terms carry more diagnostic weight (e.g. "offer letter" >> "job").
  // This handles hybrid keywords like "Amazon crypto scam" or "PayPal verification code"
  // correctly -- the dominant signal wins rather than whichever category is checked first.
  function catScore(terms) {
    return terms.reduce((s, term) => {
      if (!t.includes(lower(term))) return s;
      return s + (term.length >= 11 ? 5 : term.length >= 8 ? 3 : term.length >= 5 ? 2 : 1);
    }, 0);
  }

  const scores = {
    job:          catScore(["offer letter","background check","remote job","work from home","human resources","linkedin recruiter","ziprecruiter","glassdoor","job offer","onboarding","recruiter","interview","hiring","employment","career","resume","application","salary"]),
    crypto:       catScore(["seed phrase","recovery phrase","wallet connect","wallet drain","smart contract","staking","airdrop","metamask","coinbase","binance","phantom","ledger","solana","ethereum","bitcoin","crypto","wallet","withdrawal","token","nft","blockchain","exchange","defi","trading","presale"]),
    delivery:     catScore(["missed delivery","delivery failed","customs fee","redelivery","shipment","tracking","package","parcel","carrier","postal","fedex","usps","ups","dhl","delivery"]),
    subscription: catScore(["auto-renew","auto renewal","annual fee","billing cycle","free trial","membership","subscription","renewal","cancel"]),
    verification: catScore(["authentication code","identity verification","account verification","phone verification","two-factor","2fa","one-time password","verification code","otp","confirm your identity","verify"]),
    impersonation:catScore(["social security","geek squad","tech support","microsoft support","apple support","best buy","government","federal","warrant","medicare","legal notice","police","court","utility","electric company","gas company","irs","fbi","fcc","ssa"]),
    account:      catScore(["account locked","account suspended","account alert","security alert","login alert","bank of america","wells fargo","td bank","cash app","zelle","venmo","paypal","amazon","netflix","spotify","facebook","instagram","refund","payment","billing","invoice","transaction","account","login","password","suspicious activity","charged"]),
  };

  const [[winner, winnerScore]] = Object.entries(scores).sort((a, b) => b[1] - a[1]);

  if (winnerScore > 0 && winner === "job") {
    return {
      type: "job", label: "job or recruiter scam",
      surface: "recruiter email, LinkedIn message, offer letter, or onboarding portal",
      cues: ["recruiter","interview","onboarding","offer letter","direct deposit",
             "background check","telegram","whatsapp","ssn","equipment","training fee",
             "resume","position","salary","hr","zelle","cash app"],
      proofHints: ["gmail.com","reply-to","offer letter","telegram","direct deposit",
                   "ssn","equipment reimbursement","background check","onboarding portal",
                   "routing number","zelle","cash app"],
      scenarioDetails: [
        "careers-hiring92@gmail.com, Deloitte logo in the signature, reply-to is dltte-hr@outlook.com - three different addresses on one email",
        "the offer letter PDF: correct fonts, correct spacing, company address field reads City, State - no street, no zip, nothing after the comma",
        "two messages on LinkedIn, then: all further communication needs to move to Telegram. The account was created six weeks ago.",
        "DocuSign envelope from docusign-hr@companyname-onboarding.net, direct deposit paperwork, three days before any call is scheduled",
        "Verified Hire Solutions Inc - the background check vendor named in the offer letter - zero results in any business registry, zero BBB listing",
        "equipment reimbursement form, routing number field, account number field, $500 laptop allowance, deposited before the start date",
        "companyname-hrportal.net - not the company's real domain - SSL certificate issued nine days ago",
        "training fee $150, fully refundable on first paycheck, send by Zelle or Cash App to a personal mobile number",
      ],
      consequenceCues: [
        "SSN and date of birth entered through the background check form, a credit line opened in that name four days later",
        "routing number collected in the direct deposit step, account drained by ACH pull",
        "$150 Zelle payment sent; the onboarding portal went offline the next morning",
      ],
    };
  }

  if (winnerScore > 0 && winner === "crypto") {
    return {
      type: "crypto", label: "crypto or wallet scam",
      surface: "wallet prompt, exchange alert, support chat, or token claim page",
      cues: ["wallet","seed phrase","connect","withdrawal","airdrop","token","exchange",
             "approval","recovery phrase","support chat","staking","claim","network fee",
             "gas fee","usdt","eth"],
      proofHints: ["connect wallet","seed phrase","support chat","countdown","approval",
                   "withdrawal hold","token claim","network fee","coinb4se-airdrop.io",
                   "metamask-support.net","unlimited spend","transaction hash"],
      scenarioDetails: [
        "support chat opens, first message from the agent: your wallet address, pasted in before you have typed anything",
        "withdrawal error banner: Your account requires re-verification, countdown from 9:00, funds return to sender when it hits zero",
        "Connect Wallet button on the airdrop page triggers a token approval for unlimited USDT spend - approval dialogue shows max in the amount field",
        "coinb4se-airdrop.io - the four substitutes for the a - every visual detail matches the real site until the address bar",
        "step three of identity verification: a field labeled Wallet Seed Backup, between two ordinary form fields",
        "staking rewards dashboard: pending balance $4,800, network fee $120 required before withdrawal, fee page accepts card only",
        "MetaMask popup: permission to spend unlimited USDT on behalf of a contract address not listed on any token registry",
        "coinbase-helpcenter.net: entering the recovery phrase will sync the account to upgraded servers, the agent says it takes under a minute",
      ],
      consequenceCues: [
        "entire wallet balance swept within 40 seconds of recovery phrase submission",
        "unlimited USDT approval signed, tokens drained across three transactions in the following 90 minutes",
        "$120 network fee paid by card; the staking balance never existed; support chat closed the moment payment confirmed",
      ],
    };
  }

  if (winnerScore > 0 && winner === "delivery") {
    return {
      type: "delivery", label: "delivery or shipping scam",
      surface: "SMS text, tracking page, carrier email, or customs notice",
      cues: ["tracking","package","delivery","redelivery","customs","fee","shipment",
             "address","parcel","carrier","reschedule","hold"],
      proofHints: ["tracking link","redelivery fee","customs release","tracking number",
                   "address confirmation","five-digit short code","tab title","usps-redelivery.net",
                   "dh1-customs.com","cvv","billing zip"],
      scenarioDetails: [
        "short code 92881, tracking link: usps-redelivery.net, registered eleven days ago",
        "carrier page: USPS eagle logo, correct scale - browser tab reads Parcel Notification Portal, URL shows usps-pkg-hold.info",
        "customs release fee page: $3.19, card number field, CVV field, billing zip, no tracking information until payment clears",
        "address confirmation form, step one: full name, phone number, date of birth - shipping label to review appears after",
        "dh1-customs.com - lowercase L replaced with a one - layout identical to real DHL portal, tab title is different",
        "card number entered, page refreshes: payment failed, please try another card - the first card has already been charged",
        "tracking number from the text: 1Z999AA10123456784 - no results on the actual UPS tracking page",
        "redelivery scheduling page: pick a two-hour window, then $2.50 to confirm the slot, payable by card only",
      ],
      consequenceCues: [
        "card number, CVV, and billing address captured on the $3.19 fee page; two additional charges appearing within 72 hours",
        "date of birth and phone number from the address step used in an account recovery attempt that afternoon",
        "second card entered after the false payment failure; both charged before the page went offline",
      ],
    };
  }

  if (winnerScore > 0 && winner === "subscription") {
    return {
      type: "subscription", label: "subscription or refund scam",
      surface: "billing email, renewal notice, refund confirmation, or support call",
      cues: ["subscription","renewal","refund","charge","cancel","billing","annual",
             "membership","invoice","auto-renew","anydesk","teamviewer","overpayment","dispute"],
      proofHints: ["invoice number","renewal date","cancellation line","refund amount",
                   "dispute phone number","anydesk","teamviewer","bank account number","overpayment",
                   "wire transfer","billing@subscriptionservices-support.com"],
      scenarioDetails: [
        "subject line: Your annual subscription has renewed - $129.99 sender: billing@subscriptionservices-support.com, reply-to: different address entirely",
        "invoice body: order number, renewal date six months ago, phone number if you did not authorize this charge",
        "agent: download AnyDesk to process the refund directly - download link goes to anydesk-refund-tool.com, not anydesk.com",
        "refund portal link in chat: bank account number field, routing number field, $129.99 returned in 3 to 5 business days",
        "agent: the system sent $1,299 by mistake, need the $1,169 difference back by wire transfer today",
        "cancellation confirmation from noreply@billing-confirm.net - different sender than the original invoice - $15 processing fee to finalize",
      ],
      consequenceCues: [
        "AnyDesk session recorded a full banking login; balance transferred within the hour",
        "bank account number and routing number submitted to the refund portal; ACH debit appeared two days later",
        "wire sent for the $1,169 overpayment difference before the original $129.99 charge was confirmed as fake",
      ],
    };
  }

  if (winnerScore > 0 && winner === "verification") {
    return {
      type: "verification", label: "verification or OTP scam",
      surface: "SMS code, verification screen, or two-factor prompt",
      cues: ["verification code","otp","one-time password","confirm","identity",
             "six-digit","sent to your phone","google voice","craigslist","two-factor","authentication"],
      proofHints: ["six-digit code","do not share","verification screen","google voice",
                   "google-account-verify.com","expires in","read back","craigslist","facebook marketplace"],
      scenarioDetails: [
        "SMS: Your verification code is 847291. Do not share this code with anyone. thirty seconds later, separate message: read it back to verify identity",
        "Craigslist buyer needs to confirm the seller is real - sends a Google Voice setup prompt to that phone number",
        "two-factor prompt at google-account-verify.com - not google.com - relaying the entered code to a live Google session in real time",
        "six-digit code entered, page redirects cleanly to the real site - attacker used the code before the redirect completed",
        "verification text from a number sharing the first three digits of the bank's real customer service line",
        "Facebook Marketplace buyer: share a code to confirm real identity before payment releases - the code is a Google Voice registration prompt",
      ],
      consequenceCues: [
        "Google Voice number registered to the attacker using the victim's phone number, used for further scams within the hour",
        "account access transferred the moment the code was entered; password reset completed before the victim closed the tab",
        "OTP used to authorize a bank transfer the victim never initiated; confirmation SMS arrived three minutes later",
      ],
    };
  }

  if (winnerScore > 0 && winner === "impersonation") {
    return {
      type: "impersonation", label: "impersonation or authority scam",
      surface: "phone call, voicemail, browser popup, or official-looking email",
      cues: ["irs","social security","warrant","arrest","federal","case number",
             "badge number","penalty","gift card","wire transfer","prepaid card","anydesk","popup","locked"],
      proofHints: ["badge number","case number","warrant number","gift card","wire transfer",
                   "caller id","google play","prepaid card","anydesk","browser locked","federal hold"],
      scenarioDetails: [
        "badge number 4471, case number SSA-2024-7732, Social Security number suspended due to suspicious activity across three states",
        "voicemail from 202-555-0143: federal warrant issued, address it within two hours before an officer is dispatched",
        "IRS email: government seal, case reference TIN-29847, 48-hour deadline, payment link goes to irs-tax-resolution.net",
        "agent: only safe payment method is Google Play gift cards - bank account is under federal review, any transfer would be flagged",
        "Microsoft support popup fills the browser: case ID MS-28847, callback number, computer disables in 15 minutes",
        "Social Security caller: number used in a rental car found with nineteen kilos of cocaine in Texas, new number issued for $200 processing fee",
      ],
      consequenceCues: [
        "six Google Play gift cards purchased, codes read over the phone, balance gone before the call ended",
        "wire transfer sent under case number SSA-2024-7732; the line disconnected immediately after confirmation",
        "AnyDesk session opened from the tech support popup; banking credentials captured while the agent ran a fake scan",
      ],
    };
  }

  if (winnerScore > 0 && winner === "account") {
    return {
      type: "account", label: "account, payment, or impersonation scam",
      surface: "security alert email, billing notice, login page, or payment failure SMS",
      cues: ["login","account","verification","code","refund","invoice","charge","billing",
             "alert","password","reply-to","sign-in","suspended","limited","unusual activity"],
      proofHints: ["amazon-security@hotmail.com","account-secure-login.net","netf1ix-payments.com",
                   "Confirm My Identity","order number","invoice amount","reply-to",
                   "security-noreply@apple-id-verify.com"],
      scenarioDetails: [
        "subject line: Your account has been limited - display name Amazon, from address amazon-security@hotmail.com, reply-to a third address entirely",
        "sign-in page: Amazon layout, correct fonts, correct button color, correct logo - address bar shows account-secure-login.net",
        "invoice: $139.99, Geek Squad Annual Protection, order number GS-2024-887342, phone number to dispute",
        "verification code SMS fires four seconds after fake login page submits - attacker already using the entered credentials on the real site",
        "button at the bottom: Confirm My Identity - card number field, billing zip, CVV, at amazon-id-verify.net",
        "billing@netf1ix-payments.com - the 1 replacing the l - account suspends in 24 hours, update card button, no Netflix branding at confirmation",
        "security-noreply@apple-id-verify.com, unrequested password reset, link resolves to appleid-account-recovery.net",
        "credentials entered, page spins 30 seconds, redirects cleanly to real Amazon - the clean redirect is the concealment",
      ],
      consequenceCues: [
        "credentials used within six minutes to place $340 in orders before the password was changed",
        "card number submitted through the Confirm My Identity form; charges for $89 and $210 within the hour",
        "password reset link used by the attacker before the victim clicked it; account locked on arrival",
      ],
    };
  }

  // General fallback -- no strong category signals
  return {
    type: "general", label: "suspicious message or scam",
    surface: "text message, email, website, or phone call",
    cues: ["message","email","text","link","page","button","alert","notice"],
    proofHints: ["subject line","reply-to address","button text","domain","from address",
                 "link destination","address bar"],
    scenarioDetails: [
      "display name: real company - from address: random domain, no connection to that brand",
      "button text: Continue Securely - destination URL: three characters off from the real site, rest of page copied exactly",
      "message references a specific action never taken - a login, a payment, a package - makes the alert feel personal",
      "page asks for credentials, redirects to real site within 30 seconds, closes the window of suspicion",
      "follow-up message 18 minutes later referencing the first, this time with a phone number for those who had trouble with the link",
      "subject line: Unusual sign-in activity detected - sender is security-alert@account-notifications.net, not the real company domain",
      "the link in the message resolves to a page that loads instantly with the correct logo, correct color, correct layout - the address bar is the only thing wrong",
      "form asks for full name, date of birth, last four digits of SSN - framed as identity verification before the account is restored",
    ],
    consequenceCues: [
      "credentials captured before the redirect, used to log in from a different IP within the same session",
      "card details entered on the payment form; three charges before the statement closed",
      "identity details submitted to a form backed by nothing, used in a credit application two weeks later",
    ],
  };
}

// ============================================================================
// Live scam context -- Brave Search API
// Fetches real, current scam details for the keyword.
// Falls back cleanly to null if BRAVE_SEARCH_API_KEY is not set.
// ============================================================================

async function safeFetch(url, options = {}, timeoutMs = 8000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  } finally {
    clearTimeout(id);
  }
}

async function fetchLiveScamExamples(keyword) {
  const apiKey = process.env.BRAVE_SEARCH_API_KEY;
  if (!apiKey) return null;

  const query = encodeURIComponent(`${keyword} scam real example report`);
  const data  = await safeFetch(
    `${BRAVE_SEARCH_URL}?q=${query}&count=5&search_lang=en&result_filter=web`,
    { headers: { "X-Subscription-Token": apiKey, Accept: "application/json" } },
    BRAVE_SEARCH_TIMEOUT
  );

  if (!data?.web?.results?.length) return null;

  const text = data.web.results
    .map((r) => `${r.title || ""} ${r.description || ""}`)
    .join(" ");

  // Extract real observable details from search snippets
  const domains = unique(
    (text.match(/\b[a-z0-9][a-z0-9-]{2,}\.(com|net|org|io|info|app|co)\b/gi) || [])
      .map((d) => d.toLowerCase())
      .filter((d) => !/\b(google|reddit|bbb|ftc|consumer|scamadviser|bing|yahoo|wikipedia|trustpilot)\b/.test(d))
      .slice(0, 4)
  );

  const amounts = unique(
    (text.match(/\$[\d,]+(?:\.\d{2})?/g) || []).slice(0, 3)
  );

  const emails = unique(
    (text.match(/\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b/gi) || [])
      .filter((e) => {
        const el = e.toLowerCase();
        return !/^(contact|info|support|help)@(google|microsoft|apple|amazon)\.(com)$/.test(el);
      })
      .slice(0, 3)
  );

  const PLATFORM_TERMS = ["telegram","whatsapp","zelle","cash app","venmo","anydesk",
                          "teamviewer","google play","apple gift card","wire transfer","google voice"];
  const platforms = PLATFORM_TERMS.filter((p) => text.toLowerCase().includes(p));

  // Only return context if we found at least one concrete specific
  if (!domains.length && !amounts.length && !emails.length) return null;

  return { domains, amounts, emails, platforms: unique(platforms) };
}

// ============================================================================
// Keyword signal extraction
// ============================================================================

function extractSignals(keyword) {
  const t       = lower(keyword);
  const surface = [], actions = [], money = [], timing = [];

  if (/\btext\b|sms|message/.test(t))                         surface.push("text message");
  if (/\bemail\b|e-mail/.test(t))                             surface.push("email");
  if (/\bcall\b|phone|voicemail/.test(t))                     surface.push("phone call");
  if (/\bwebsite\b|site\b|\bpage\b|\blink\b|\burl\b/.test(t)) surface.push("website or page");

  if (/refund/.test(t))                          { actions.push("claim or dispute a refund"); money.push("refund amount"); }
  if (/invoice|bill/.test(t))                    { actions.push("dispute an invoice charge"); money.push("invoice total"); }
  if (/verify|code|otp|2fa/.test(t))             { actions.push("enter a verification code"); timing.push("code expires in minutes"); }
  if (/login|sign.?in|password/.test(t))         actions.push("sign in to the account");
  if (/delivery|package|tracking/.test(t))        { actions.push("track or reschedule a package"); money.push("small redelivery fee"); }
  if (/job|recruiter|interview|hire/.test(t))     { actions.push("complete onboarding paperwork"); timing.push("start date deadline"); }
  if (/crypto|wallet|withdrawal|airdrop/.test(t)) { actions.push("connect wallet or claim tokens"); timing.push("countdown or withdrawal hold"); }
  if (/subscription|renew|cancel/.test(t))        { actions.push("call to dispute the charge"); money.push("annual renewal charge"); }
  if (/irs|government|warrant|social security/.test(t)) { actions.push("call back within the hour"); timing.push("two-hour window before enforcement"); }

  const BRANDS = ["amazon","apple","google","microsoft","paypal","venmo","zelle","cash app",
                  "usps","ups","fedex","dhl","coinbase","binance","metamask","netflix","spotify",
                  "facebook","instagram","whatsapp","telegram","td bank","chase","bank of america",
                  "wells fargo","solana","phantom","geek squad","norton","mcafee","irs","linkedin","indeed"];
  const brands = BRANDS.filter((b) => t.includes(b));

  return {
    surface: unique(surface), actions: unique(actions),
    money: unique(money), timing: unique(timing), brands: unique(brands),
  };
}

// ============================================================================
// Evidence type taxonomy
// ============================================================================

const EVIDENCE_TYPES = {
  sender:   ["from address","display name","reply-to","sender","short code","caller id","badge number"],
  domain:   ["domain","url","address bar","tab title","link resolves",".com",".net",".io",".info"],
  button:   ["button","button reads","button text","link text","verify now","confirm my identity"],
  amount:   ["$","fee","charge","invoice","refund","payment","total","balance"],
  formfield:["routing number","account number","ssn","cvv","billing zip","date of birth","card number","form field"],
  countdown:["countdown","timer","expires","minutes remaining","hits zero"],
  platform: ["telegram","whatsapp","zelle","cash app","anydesk","teamviewer","google voice","docusign"],
  wallet:   ["seed phrase","recovery phrase","connect wallet","approval","network fee","gas fee","token claim"],
  tracking: ["tracking number","tracking link","redelivery","customs","parcel"],
  invoice:  ["order number","case number","renewal date","invoice number"],
};

function detectEvidenceTypes(text) {
  const t     = lower(text);
  const found = new Set();
  for (const [type, signals] of Object.entries(EVIDENCE_TYPES)) {
    if (signals.some((s) => t.includes(s))) found.add(type);
  }
  return found;
}

function countNewEvidencePerParagraph(paragraphs) {
  const seen = new Set();
  return paragraphs.map((p) => {
    const types = detectEvidenceTypes(p);
    let newCount = 0;
    for (const tp of types) {
      if (!seen.has(tp)) { newCount++; seen.add(tp); }
    }
    return newCount;
  });
}

// ============================================================================
// Deterministic variation seeding
// ============================================================================

function keywordHash(keyword) {
  let h = 0;
  for (let i = 0; i < keyword.length; i++)
    h = (h * 31 + keyword.charCodeAt(i)) >>> 0;
  return h;
}

// ============================================================================
// Pass brief system
// ============================================================================

const ENTRY_POINTS = [
  (cat) => {
    const ex = cat.scenarioDetails.find((s) =>
      /gmail|reply-to|short code|caller|badge|from address|@/.test(s.toLowerCase())
    ) || cat.scenarioDetails[0];
    return (
      "For this piece, the opening detail is the sender or source -- " +
      "the actual from address, the short code it came from, whatever that detail is for this scenario. " +
      "Land on it in the first sentence and let the rest follow.\nReference: " + ex
    );
  },
  () =>
    "For this piece, open with a quoted phrase from the message or page in standard double quotes -- " +
    "the subject line, a button label, something the agent wrote, whatever fits. " +
    "The first sentence quotes it. Everything else unfolds from there.",
  (cat) => {
    const ex = cat.scenarioDetails.find((s) =>
      /\.(net|io|info|com)|address bar|tab title|url/.test(s.toLowerCase())
    ) || cat.scenarioDetails[1];
    return (
      "For this piece, the opening detail is the URL or domain -- " +
      "the actual address bar, where the link goes, what the tab says. " +
      "The specific domain, not a description of it.\nReference: " + ex
    );
  },
  (cat) => {
    const ex = cat.scenarioDetails.find((s) => /\$/.test(s)) || cat.scenarioDetails[2];
    return (
      "For this piece, open on a specific dollar amount -- " +
      "what it is and what it is supposedly for. The number first. Let the paragraph build from there.\nReference: " + ex
    );
  },
  () =>
    "For this piece, the opening detail is what the message asks someone to do -- " +
    "the button label, the phone number, the form, the code. " +
    "Name that action in the first sentence and follow where it leads.",
];

const COMPOSITION_SHAPES = [
  "Write this the way you'd describe something you're holding and turning over. " +
  "The first look, then what you notice when you go closer, then what's underneath that. " +
  "Let one paragraph be short -- some things only need a sentence or two. " +
  "Paragraphs don't need to hand off to each other.",
  "Four observations, each one standing on its own. Start on what you see first. " +
  "Each paragraph notices something the others didn't. " +
  "They don't build toward each other -- they just each earn their place. " +
  "One can be brief. Nothing needs to connect them.",
  "Four paragraphs, each one about something different. " +
  "Not four angles on the same thing -- four genuinely different observations. " +
  "They belong together but they don't need to prove it. " +
  "Some longer, one shorter. Let them sit next to each other without bridging.",
];

const ENDING_SHAPES = [
  "The last sentence lands on something specific that is already done -- a balance gone, a password taken, a form submitted. Past tense. No softening.",
  "The piece ends short. One sentence naming what was taken or changed. Past tense. That's it.",
  "The ending lands on the moment something became final -- the phrase entered, the transfer cleared, the code used. Name it and stop.",
  "What exists now that didn't before. A charge, a new account, a session from somewhere else. Stated simply. Already happened.",
  "The last sentence names the thing and what happened to it. One sentence. Done.",
];

function buildPassBrief(passIndex, keyword, cat) {
  const h        = keywordHash(keyword);
  const entryFn  = ENTRY_POINTS[(h + passIndex * 2) % ENTRY_POINTS.length];
  const shape    = COMPOSITION_SHAPES[passIndex % COMPOSITION_SHAPES.length];
  const ending   = ENDING_SHAPES[(h + passIndex) % ENDING_SHAPES.length];

  const total   = cat.scenarioDetails.length;
  const start   = (passIndex * 3) % total;
  const anchors = [
    cat.scenarioDetails[start % total],
    cat.scenarioDetails[(start + 1) % total],
    cat.scenarioDetails[(start + 2) % total],
  ].filter(Boolean).map((a) => "- " + a).join("\n");

  return { entryInstruction: entryFn(cat, keyword), shape, ending, anchors };
}

// ============================================================================
// Prompt construction
// ============================================================================

function buildSystemPrompt(keyword, liveCtx = null) {
  const cat = classify(keyword);
  const sig = extractSignals(keyword);

  const surfaceLine = sig.surface.length ? `Surface: ${sig.surface.join(", ")}` : `Surface: ${cat.surface}`;
  const brandLine   = sig.brands.length  ? `Brand or platform: ${sig.brands.join(", ")}` : "";
  const actionLine  = sig.actions.length ? `Action demanded: ${sig.actions.join("; ")}` : "";
  const moneyLine   = sig.money.length   ? `Money in play: ${sig.money.join(", ")}` : "";
  const timingLine  = sig.timing.length  ? `Timing pressure: ${sig.timing.join(", ")}` : "";
  const consequence = cat.consequenceCues[0] || "";

  const ex1  = cat.scenarioDetails[0] || "";
  const ex2  = cat.scenarioDetails[Math.floor(cat.scenarioDetails.length / 2)] || cat.scenarioDetails[1] || "";
  const reg1 = ex1.includes(" - ") ? ex1.split(" - ")[0].trim() : ex1.split(",")[0].trim();
  const reg2 = ex2.includes(" - ") ? ex2.split(" - ")[0].trim() : ex2.split(",")[0].trim();

  // Live details section -- injected when Brave Search returns specifics.
  // Placed after the register so the model treats them as confirmed real material.
  const liveSection = liveCtx
    ? `\nConfirmed real details for "${keyword}" -- use these where they fit naturally in the piece:\n` +
      (liveCtx.domains.length   ? `  Real domains seen: ${liveCtx.domains.join(", ")}\n`  : "") +
      (liveCtx.amounts.length   ? `  Amounts reported: ${liveCtx.amounts.join(", ")}\n`   : "") +
      (liveCtx.emails.length    ? `  Sender patterns: ${liveCtx.emails.join(", ")}\n`     : "") +
      (liveCtx.platforms.length ? `  Platforms used: ${liveCtx.platforms.join(", ")}\n`   : "")
    : "";

  return (
    "You write copy for a scam awareness page.\n\n" +
    "Someone just encountered something suspicious. " +
    "Write four paragraphs describing exactly what was there: " +
    "the address bar, the sender line, the button text, the form fields, the dollar amount, " +
    "what the agent wrote. Name each thing as you encounter it. " +
    "Don't explain what it means. Don't say what it was trying to do.\n\n" +
    "The four paragraphs don't need to be even. " +
    "One can be two sentences. One can carry more detail. " +
    "They don't need to hand off to each other -- " +
    "they just need to each show something the others didn't.\n\n" +
    "Put one quoted phrase in standard double quotes somewhere in the piece -- " +
    "a subject line, a button label, something from the message itself.\n\n" +
    "The last sentence names something that is already done. Past tense. Specific. Not a warning -- the outcome.\n\n" +
    "Never use: scammers often, this type of scam, be careful, stay safe, " +
    "red flags, fraudsters, cybercriminals, is designed to, the goal is to, " +
    "it is important to, users should.\n\n" +
    `Register -- sentences that belong in this kind of writing:\n  "${reg1}"\n  "${reg2}"\n` +
    liveSection + "\n" +
    surfaceLine + "\n" +
    (brandLine  ? brandLine  + "\n" : "") +
    (actionLine ? actionLine + "\n" : "") +
    (moneyLine  ? moneyLine  + "\n" : "") +
    (timingLine ? timingLine + "\n" : "") +
    "\nThe piece ends on: " + consequence + "\n\n" +
    "4 paragraphs. 600-850 words. Plain text. No headings. No bullets.\n" +
    "Output only the 4 paragraphs."
  );
}

function buildUserPrompt(keyword, passIndex, liveCtx = null) {
  const cat = classify(keyword);
  const sig = extractSignals(keyword);

  const contextLine   = sig.surface.length ? sig.surface.join(", ") : cat.surface;
  const brandContext  = sig.brands.length  ? `Brand: ${sig.brands.join(", ")}`  : "";
  const moneyContext  = sig.money.length   ? `Money: ${sig.money.join(", ")}`   : "";
  const timingContext = sig.timing.length  ? `Timing: ${sig.timing.join(", ")}` : "";
  const extras = [brandContext, moneyContext, timingContext].filter(Boolean).join(". ");

  const { entryInstruction, shape, ending, anchors } = buildPassBrief(passIndex, keyword, cat);
  const consequence = cat.consequenceCues[passIndex % cat.consequenceCues.length];

  // If live context is available, build the opening detail from real confirmed data.
  // Otherwise fall through to the static first anchor.
  let openingDetail;
  if (liveCtx && (liveCtx.domains.length || liveCtx.amounts.length || liveCtx.emails.length)) {
    const liveDetail = [
      liveCtx.domains.length ? `confirmed domain: ${liveCtx.domains[0]}` : null,
      liveCtx.amounts.length ? `amount reported: ${liveCtx.amounts[0]}`  : null,
      liveCtx.emails.length  ? `sender: ${liveCtx.emails[0]}`            : null,
    ].filter(Boolean).join(", ");

    openingDetail = `Confirmed real detail -- open on this:\n${liveDetail}`;
  } else {
    const firstAnchor = anchors.split("\n")[0].replace(/^-\s*/, "").trim();
    openingDetail = firstAnchor.split(" - ")[0].split(",")[0].trim();
  }

  // When live details are available, prepend as the lead anchor
  const anchorBlock = liveCtx && (liveCtx.domains.length || liveCtx.amounts.length || liveCtx.emails.length)
    ? `Confirmed real details to use:\n` +
      (liveCtx.domains.length ? `- ${liveCtx.domains[0]}\n` : "") +
      (liveCtx.amounts.length ? `- ${liveCtx.amounts[0]}\n` : "") +
      (liveCtx.emails.length  ? `- ${liveCtx.emails[0]}\n`  : "") +
      `\nAdditional scenario texture:\n${anchors}`
    : `Scenario texture to draw from:\n${anchors}`;

  return (
    `Write 4 paragraphs about: "${keyword}"\n` +
    `Surface: ${contextLine}` + (extras ? `. ${extras}.` : "") + "\n\n" +
    entryInstruction + "\n\n" +
    "The first paragraph opens on: " + openingDetail + "\n\n" +
    shape + "\n\n" +
    anchorBlock + "\n\n" +
    "Sentences can be short when the detail is simple. " +
    "Not every paragraph needs the same density or length. " +
    "One quoted phrase in standard double quotes somewhere in the piece.\n\n" +
    "The piece ends with: " + ending + "\n" +
    "Specific outcome: " + consequence + "\n\n" +
    "No advice. No generic language. Output only the 4 paragraphs."
  );
}

function buildRewritePrompt(keyword, content) {
  const cat       = classify(keyword);
  const h         = keywordHash(keyword);
  const ending    = ENDING_SHAPES[h % ENDING_SHAPES.length];
  const scenarios = cat.scenarioDetails.slice(0, 4).map((s) => "- " + s).join("\n");

  return (
    `Rewrite this for "${keyword}". 4 paragraphs.\n\n` +
    "Keep every specific detail that is already there -- " +
    "domains, amounts, sender addresses, button labels, quoted phrases. " +
    "Those are the piece's best material.\n\n" +
    "Read it once and find the one or two places where it loses the reader. " +
    "The most likely culprits: " +
    "an opening that sets up context instead of landing on something specific, " +
    "two paragraphs that cover the same kind of evidence in different words, " +
    "or a closing sentence that softens instead of stops. " +
    "Fix only what you find. Everything else stays.\n\n" +
    "Scenario texture:\n" + scenarios + "\n\n" +
    "The ending should feel like: " + ending + "\n\n" +
    "No advice. No generic language. Plain text.\n" +
    "Output only the 4 paragraphs.\n\n" +
    "Original:\n" + content
  );
}

function buildPolishPrompt(keyword, content) {
  const h      = keywordHash(keyword);
  const ending = ENDING_SHAPES[(h >> 2) % ENDING_SHAPES.length];

  return (
    `Polish this for "${keyword}". Sentence-level only -- don't move paragraphs.\n\n` +
    "One read-through. Find the sentence that sounds most constructed -- " +
    "the one that could appear in any scam article. " +
    "Replace it with whatever specific detail it sits closest to.\n\n" +
    "Check the first sentence of the piece. " +
    "If it reads as setup or context, cut to the most concrete thing in that paragraph.\n\n" +
    "If the last sentence hedges or implies rather than states: " + ending + "\n\n" +
    "If two paragraphs open with the same word, change one.\n\n" +
    "Keep every specific detail. Plain text.\n" +
    "Output only the 4 paragraphs.\n\n" +
    "Content:\n" + content
  );
}

// ============================================================================
// Scoring signals
// ============================================================================

const GENERIC_PHRASES = [
  "in today's digital age","scammers often","it is important to","users should",
  "these scams","one common tactic","another common tactic","the goal is to",
  "this type of scam","be careful","stay safe","stay vigilant","red flags include",
  "warning signs","it may appear as","this scam works by","protect yourself",
  "always verify","common scam","used to trick","designed to steal",
  "help you stay safe","the message is designed to","the scammer wants",
  "the scam relies on","this kind of scam","what to do next","in many cases",
  "bad actors","cybercriminals","fraudsters","be aware","watch out","think twice",
];

const EXPLAINER_PHRASES = [
  "is designed to","is meant to","works by","relies on","the goal is","the tactic is",
  "the message tries to","this is meant to","the scammer wants","the scam works",
  "the end goal","the purpose is",
];

const ADVICE_PHRASES = [
  "you should","do not click","never share","always check","be cautious","stay vigilant",
  "verify before","protect your","if you receive this","if you see this","remember to",
  "make sure to","the safest move","to stay safe","to protect yourself","avoid clicking",
  "do not respond",
];

const SCENE_TERMS = [
  "subject line","sender","display name","button","link","portal","screen","code","form",
  "chat","page","domain","logo","tracking","invoice","countdown","prompt","notice","alert",
  "field","timer","banner","address bar","reply-to","from address","tab title","login page",
  "sign-in page","short code","caller id","url bar","routing number","account number",
  "pdf","attachment","popup","browser","receipt","badge number","case number","order number",
];

const OBSERVED_DETAILS = [
  "display name","reply-to","subject line","button","countdown","timer","tracking page",
  "support chat","address bar","tab title","direct deposit","gift card","wire transfer",
  "telegram","whatsapp","connect wallet","offer letter","invoice","payment page","login page",
  "redelivery fee","from address","tracking number","verification code","sign-in page",
  "badge number","case number","routing number","anydesk","teamviewer","google voice",
  "seed phrase","recovery phrase","airdrop","approval","network fee","customs fee",
  "short code","google play","prepaid card","caller id","order number","billing zip",
  "cvv","card number","account number","onboarding portal","docusign","zelle","cash app",
  "two-factor","otp","six-digit",
];

function countMatches(text, terms) {
  const t = lower(text);
  return terms.filter((term) => t.includes(lower(term))).length;
}
function countGeneric(text)         { return countMatches(text, GENERIC_PHRASES); }
function countExplainers(text)      { return countMatches(text, EXPLAINER_PHRASES); }
function countAdvice(text)          { return countMatches(text, ADVICE_PHRASES); }
function countSceneTerms(text)      { return countMatches(text, SCENE_TERMS); }
function countObservedDetails(text) { return countMatches(text, OBSERVED_DETAILS); }

function countQuotedFragments(text) {
  return (String(text || "").match(/"[^"]{4,80}"/g) || []).length;
}
function countConcreteNumbers(text) {
  return (String(text || "").match(/\$[\d,]+(?:\.\d{2})?|\b\d{4,}\b/g) || []).length;
}
function countDomainSignals(text) {
  return (String(text || "").match(/\b[a-z0-9-]+\.(com|net|org|co|io|app|info|biz)\b/gi) || []).length;
}
function countEmailSignals(text) {
  return (String(text || "").match(/\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b/gi) || []).length;
}

function scoreHumanFeel(paragraphs) {
  let score = 0;
  const sentenceLengths = paragraphs
    .flatMap((p) => splitSentences(p).map((s) => wordCount(s)))
    .filter(Boolean);

  if (sentenceLengths.length >= 4) {
    const hasShort = sentenceLengths.some((n) => n <= 9);
    const hasLong  = sentenceLengths.some((n) => n >= 18);
    const avg      = sentenceLengths.reduce((a, b) => a + b, 0) / sentenceLengths.length;
    const variance = sentenceLengths.reduce((sum, n) => sum + Math.abs(n - avg), 0) / sentenceLengths.length;
    if (hasShort)            score += 8;
    if (hasShort && hasLong) score += 5;
    if (variance >= 5)       score += 4;
    if (avg < 7 || avg > 25) score -= 8;
  }

  if (paragraphs.length >= 3) {
    const wcs    = paragraphs.map((p) => wordCount(p));
    const spread = Math.max(...wcs) - Math.min(...wcs);
    if (spread >= 40) score += 6;
    if (spread >= 70) score += 4;
    if (wcs.some((w) => w <= 80)) score += 5;
    if (spread < 20) score -= 6;
  }

  const firstWords = paragraphs.map((p) =>
    lower(p).split(/\s+/)[0].replace(/[^a-z]/g, "")
  );
  const wordFreq = {};
  for (const w of firstWords) wordFreq[w] = (wordFreq[w] || 0) + 1;
  const maxRepeat = Math.max(...Object.values(wordFreq));
  if (maxRepeat >= 3)      score -= 10;
  else if (maxRepeat >= 2) score -= 4;
  else                     score += 4;

  return score;
}

function scoreEvidenceDiversity(paragraphs) {
  if (paragraphs.length < 2) return 0;
  const newPerParagraph = countNewEvidencePerParagraph(paragraphs);
  const totalNew   = newPerParagraph.reduce((a, b) => a + b, 0);
  const allHaveNew = newPerParagraph.every((n) => n >= 1);
  let s = 0;
  if (totalNew >= 4) s += 12;
  if (totalNew >= 6) s += 5;
  if (allHaveNew)    s += 8;
  if (newPerParagraph[2] === 0 || newPerParagraph[3] === 0) s -= 8;
  return s;
}

function hasDuplicateStarts(paragraphs) {
  const seen = new Set();
  for (const p of paragraphs) {
    const fp = lower(p).replace(/[^a-z0-9 ]/g, "").trim().slice(0, 55);
    if (!fp) continue;
    if (seen.has(fp)) return true;
    seen.add(fp);
  }
  return false;
}

// ============================================================================
// Scoring
// ============================================================================

function scoreContent(text, keyword) {
  const cat        = classify(keyword);
  const sig        = extractSignals(keyword);
  const content    = sanitize(text);
  const paragraphs = splitParagraphs(content);
  const t          = lower(content);
  let score        = 100;

  if (!content)                return 0;
  if (paragraphs.length !== 4) score -= 28;
  if (paragraphs.length < 2)   return clamp(score - 40, 0, 100);

  const total = wordCount(content);
  if (total < 480) score -= 14;
  if (total < 380) score -= 10;
  if (total > 920) score -= 5;

  score -= countGeneric(content)    * 6;
  score -= countExplainers(content) * 4;
  score -= countAdvice(content)     * 5;

  const observed = countObservedDetails(content);
  if (observed < 2)      score -= 22;
  else if (observed < 4) score -= 8;
  if (observed >= 5)     score += 10;
  if (observed >= 8)     score += 7;
  if (observed >= 11)    score += 5;

  const scene = countSceneTerms(content);
  if (scene < 3)   score -= 7;
  if (scene >= 6)  score += 5;
  if (scene >= 10) score += 4;

  const quoted = countQuotedFragments(content);
  if (quoted === 0) score -= 14;
  if (quoted >= 1)  score += 12;
  if (quoted >= 2)  score += 7;
  if (quoted >= 3)  score += 4;

  const numbers = countConcreteNumbers(content);
  if (numbers >= 1) score += 7;
  if (numbers >= 2) score += 5;
  if (numbers >= 3) score += 3;

  const domains = countDomainSignals(content);
  if (domains >= 1) score += 9;
  if (domains >= 2) score += 5;
  if (domains >= 3) score += 3;

  const emails = countEmailSignals(content);
  if (emails >= 1) score += 8;
  if (emails >= 2) score += 4;

  const proofDensity = quoted * 5 + numbers * 3 + domains * 5 + emails * 5 + Math.floor(observed / 2);
  if (proofDensity < 5)   score -= 10;
  if (proofDensity >= 12) score += 7;
  if (proofDensity >= 20) score += 5;
  if (proofDensity >= 28) score += 4;

  score += scoreHumanFeel(paragraphs);
  score += scoreEvidenceDiversity(paragraphs);
  if (hasDuplicateStarts(paragraphs)) score -= 6;

  const cueMatches = countMatches(content, cat.cues);
  if (cueMatches < 2)  score -= 7;
  if (cueMatches >= 4) score += 5;
  if (cueMatches >= 6) score += 3;

  const proofHintMatches = countMatches(content, cat.proofHints);
  if (proofHintMatches >= 2) score += 8;
  if (proofHintMatches >= 4) score += 5;
  if (proofHintMatches >= 6) score += 3;

  if (sig.brands.some((b) => t.includes(b)))                                       score += 5;
  if (sig.actions.some((a) => t.includes(lower(a.split(" ")[0]))))                 score += 3;
  if (sig.money.length && sig.money.some((m) => t.includes(lower(m.split(" ")[0]))))    score += 3;
  if (sig.timing.length && sig.timing.some((ti) => t.includes(lower(ti.split(" ")[0])))) score += 3;

  if (paragraphs[0]) {
    const fp = lower(paragraphs[0]);
    const hasSceneOpener =
      /^(you |a text|an email|a message|the message|the email|the page|the screen|the link|the button|the subject|the sender|the from|the reply|the tab|the address|the alert|the notice|the form|the prompt|the portal|the banner|the caller|the invoice|the pdf|the call|the popup|the domain|the url|the short|the badge|the case|the offer|the wallet|the approval|the countdown|the tracking|the customs|it landed|it arrived|it came|it shows|it opens|it reads|it says|it asks|"|a call|a popup|a banner|a recruiter|a verification|a withdrawal|a countdown|a short|subject line|short code|\$)/.test(fp);
    if (!hasSceneOpener) score -= 6;

    const p0proof = countObservedDetails(paragraphs[0]) + countDomainSignals(paragraphs[0]) * 2 +
      countEmailSignals(paragraphs[0]) * 2 + countQuotedFragments(paragraphs[0]) * 3 + countConcreteNumbers(paragraphs[0]);
    if (p0proof === 0) score -= 14;
    if (p0proof >= 3)  score += 8;
    if (p0proof >= 6)  score += 5;
  }

  for (let i = 0; i < paragraphs.length; i++) {
    const wc = wordCount(paragraphs[i]);
    if (wc < 60)  score -= 8;
    if (wc > 280) score -= 4;
    const pDetail = countObservedDetails(paragraphs[i]) + countDomainSignals(paragraphs[i]) + countEmailSignals(paragraphs[i]);
    if (pDetail === 0) score -= 7;
    if (pDetail >= 2)  score += 4;
    if (pDetail >= 4)  score += 3;
  }

  if (paragraphs[paragraphs.length - 1]) {
    const pLast = lower(paragraphs[paragraphs.length - 1]);
    if (/\bcould\b|\bmay\b|\bmight\b|be careful|if you|you should|to protect|to avoid/.test(pLast)) {
      score -= 10;
    }
    const lastProof = countConcreteNumbers(paragraphs[paragraphs.length - 1]) +
                      countDomainSignals(paragraphs[paragraphs.length - 1]) +
                      countEmailSignals(paragraphs[paragraphs.length - 1]) +
                      countObservedDetails(paragraphs[paragraphs.length - 1]);
    if (lastProof >= 2)      score += 6;
    else if (lastProof >= 1) score += 3;
  }

  if (t.includes(lower(keyword))) score += 3;
  return clamp(score, 0, 100);
}

// ============================================================================
// Sanitisation + Validation
// ============================================================================

function sanitize(text) {
  return String(text || "")
    .replace(/\r/g, "")
    .replace(/\u200B/g, "")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^[*-]\s+/gm, "")
    .replace(/^"+|"+$/g, "")
    .replace(/^'+|'+$/g, "")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim()
    .split(/\n\s*\n/)
    .map((p) =>
      p.replace(/\n/g, " ").replace(/\s+/g, " ").replace(/\s+([,.!?;:])/g, "$1").trim()
    )
    .filter(Boolean)
    .join("\n\n")
    .trim();
}

function isHardBroken(text) {
  const content = sanitize(text);
  if (!content) return true;
  if (/^#{1,6}\s/m.test(content)) return true;
  if (/<[a-z][a-z0-9]*[\s>]/i.test(content)) return true;
  return false;
}

function has4Paragraphs(text) {
  return splitParagraphs(sanitize(text)).length === 4;
}

// ============================================================================
// API call
// ============================================================================

async function fetchWithTimeout(url, options, timeoutMs) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try { return await fetch(url, { ...options, signal: controller.signal }); }
  finally { clearTimeout(id); }
}

async function callAPI({ systemPrompt, userPrompt, temperature }) {
  if (!process.env.OPENAI_API_KEY) throw new Error("OPENAI_API_KEY is not set.");

  let lastError = null;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const response = await fetchWithTimeout(
        API_URL,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
          body: JSON.stringify({
            model: MODEL, temperature,
            max_completion_tokens: 2000,
            messages: [
              { role: "system", content: systemPrompt },
              { role: "user",   content: userPrompt },
            ],
          }),
        },
        TIMEOUT_MS
      );

      const rawText = await response.text();
      let data = {};
      try { data = rawText ? JSON.parse(rawText) : {}; }
      catch { throw new Error(`API response was not valid JSON: ${rawText.slice(0, 200)}`); }

      if (!response.ok) {
        const err = new Error(data?.error?.message || `API request failed with status ${response.status}`);
        err.retryable = shouldRetry(response.status);
        throw err;
      }

      return sanitize(data.choices?.[0]?.message?.content || "");
    } catch (error) {
      lastError = error;
      const aborted   = error?.name === "AbortError";
      const retryable = aborted || error?.retryable === true;
      if (!retryable || attempt + 1 >= MAX_RETRIES) {
        if (aborted) throw new Error(`API request timed out after ${TIMEOUT_MS}ms`);
        throw error;
      }
      await sleep(600 * (attempt + 1));
    }
  }

  throw lastError || new Error("API request failed after retries");
}

// ============================================================================
// Generation pipeline
//
// v4: Brave Search fetch before generation when BRAVE_SEARCH_API_KEY is set.
// Live details injected as confirmed-real material in both system and user prompts.
// Falls back cleanly to static scenarios when key is absent.
//
// Third-pass logic (mutually exclusive):
//   REWRITE: fires when best score < 72. Structure needs a full rewrite.
//   POLISH:  fires when best score < 88 AND gap < 8. Both close, neither excellent.
//   Otherwise: one pass dominated or both excellent -- take the winner, no third call.
// ============================================================================

// Bonus applied when Brave Search live details actually appear in the generated content.
// The pass that uses confirmed real domains/amounts/emails ranks above an equally-structured
// pass that stayed with static scenario texture. Keeps candidate selection aligned with
// what matters most for E-E-A-T: real, verifiable, current specifics.
function scoreLiveContextUsage(content, liveCtx) {
  if (!liveCtx || !content) return 0;
  const t = lower(content);
  const details = [
    ...(liveCtx.domains || []),
    ...(liveCtx.amounts || []),
    ...(liveCtx.emails  || []),
  ];
  if (!details.length) return 0;
  const hits = details.filter((d) => t.includes(d.toLowerCase())).length;
  if (hits >= 3) return 14;
  if (hits >= 2) return 9;
  if (hits >= 1) return 5;
  return 0;
}

async function generateBestPass(keyword) {
  const kw = normalizeKeyword(keyword);

  // Fetch live scam examples -- runs in parallel with nothing else, resolves before prompts are built.
  // Falls back to null cleanly if BRAVE_SEARCH_API_KEY is absent.
  const liveCtx = await fetchLiveScamExamples(kw);

  const systemPrompt = buildSystemPrompt(kw, liveCtx);

  const rawPool = (
    await Promise.allSettled(
      INITIAL_TEMPERATURES.map((temp, i) =>
        callAPI({
          systemPrompt,
          userPrompt: buildUserPrompt(kw, i, liveCtx),
          temperature: temp,
        })
      )
    )
  )
    .filter((r) => {
      if (r.status === 'rejected') {
        console.error(`[SCAM] Parallel pass failed for "${kw}": ${r.reason?.message}`);
        return false;
      }
      return r.value && !isHardBroken(r.value);
    })
    .map((r) => sanitize(r.value));

  const scoredPool = rawPool
    .map((c) => ({ content: c, score: scoreContent(c, kw) + scoreLiveContextUsage(c, liveCtx) }))
    .sort((a, b) => b.score - a.score);

  let best = scoredPool[0] || null;

  if (best) {
    const secondScore = scoredPool[1]?.score ?? 0;
    const gap         = best.score - secondScore;
    const bestScore   = best.score;

    // Rewrite: structure genuinely weak
    if (bestScore < REWRITE_SCORE_THRESHOLD && has4Paragraphs(best.content)) {
      try {
        const rewritten = await callAPI({
          systemPrompt,
          userPrompt: buildRewritePrompt(kw, best.content),
          temperature: 0.55,
        });
        if (rewritten && !isHardBroken(rewritten) && has4Paragraphs(rewritten)) {
          const rewrittenScore = scoreContent(rewritten, kw);
          if (rewrittenScore >= bestScore - 2) {
            best = { content: sanitize(rewritten), score: rewrittenScore };
          }
        }
      } catch (err) {
        console.error(`[SEO] Rewrite failed for "${kw}": ${err.message}`);
      }
    }
    // Polish: both passes close, neither excellent
    else if (bestScore < POLISH_SCORE_CEILING && gap < POLISH_GAP_THRESHOLD && has4Paragraphs(best.content)) {
      try {
        const polished = await callAPI({
          systemPrompt,
          userPrompt: buildPolishPrompt(kw, best.content),
          temperature: 0.44,
        });
        if (polished && !isHardBroken(polished) && has4Paragraphs(polished)) {
          const polishedScore = scoreContent(polished, kw);
          if (polishedScore >= bestScore - 2) {
            best = { content: sanitize(polished), score: polishedScore };
          }
        }
      } catch (err) {
        console.error(`[SEO] Polish failed for "${kw}": ${err.message}`);
      }
    }
  }

  if (best) return best.content;
  throw new Error(`SEO generation failed for "${kw}" -- all API calls failed`);
}

// ============================================================================
// Template field builder
// ============================================================================

function buildTemplateFields(content) {
  const paragraphs = splitParagraphs(content);
  return {
    AI_HOOK:    paragraphs[0] || "",
    AI_BODY_1:  paragraphs[1] || "",
    AI_BODY_2:  "",
    AI_SUBHEAD: "What to Watch For",
    AI_BODY_3:  paragraphs[2] || "",
    AI_LIST:    "",
    AI_CLOSE:   paragraphs[3] || "",
  };
}

// ============================================================================
// Public API
// ============================================================================

async function generateSeoTemplateFields(keyword) {
  const content = await generateBestPass(keyword);
  return buildTemplateFields(content);
}

export { normalizeKeyword, generateBestPass, generateSeoTemplateFields, buildTemplateFields };
