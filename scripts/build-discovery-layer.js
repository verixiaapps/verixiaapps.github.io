import fs from "fs";
import path from "path";
import https from "https";

const SITE_URL = (process.env.SITE_URL || "").replace(/\/+$/, "");
const SOURCE_SITEMAP_URL = process.env.SOURCE_SITEMAP_URL;

const DISCOVERY_DIR = process.env.DISCOVERY_DIR || "discovery";
const DISCOVERY_SITEMAP_PATH =
  process.env.DISCOVERY_SITEMAP_PATH || "discovery-sitemap.xml";

const MAX_LATEST = parseInt(process.env.MAX_LATEST_URLS || "100", 10);
const MAX_TODAY = parseInt(process.env.MAX_TODAY_URLS || "100", 10);
const MAX_WEEK = parseInt(process.env.MAX_THIS_WEEK_URLS || "700", 10);
const MAX_HTML = parseInt(process.env.MAX_HTML_SITEMAP_URLS || "500", 10);
const MAX_FEED = parseInt(process.env.MAX_FEED_URLS || "100", 10);

const MAX_CLUSTER_PAGE_URLS = 250;
const MAX_TOPIC_PAGE_URLS = 200;
const MAX_PLATFORM_PAGE_URLS = 150;
const MAX_TOPIC_GROUPS = 12;
const MAX_PLATFORM_GROUPS = 20;
const MAX_CLUSTER_GROUPS = 18;

const MIN_TOPIC_SIZE = 10;
const MIN_PLATFORM_SIZE = 8;
const MIN_CLUSTER_SIZE = 10;
const MIN_HYBRID_SIZE = 8;

const RUNWAY_PAGE_SIZE = 100;
const MAX_RUNWAY_PAGES = 10;

const PAGINATED_LATEST_PAGE_SIZE = 100;
const MAX_PAGINATED_LATEST_PAGES = 10;

const PAGINATED_TODAY_PAGE_SIZE = 100;
const MAX_PAGINATED_TODAY_PAGES = 5;

const MAX_HYBRID_PAGES = 30;
const MAX_HYBRID_PAGE_URLS = 120;

const RANDOM_PAGE_SIZE = 200;
const REVISIT_PAGE_SIZE = 300;
const REVISIT_START_OFFSET = 200;
const REVISIT_END_OFFSET = 1200;

const DISCOVERY_SEGMENT = String(DISCOVERY_DIR).replace(/^\/+|\/+$/g, "");

const STOPWORDS = new Set([
  "www",
  "http",
  "https",
  "html",
  "php",
  "com",
  "net",
  "org",
  "app",
  "apps",
  "page",
  "pages",
  "check",
  "checks",
  "scam",
  "scams",
  "warning",
  "warnings",
  "alert",
  "alerts",
  "message",
  "messages",
  "review",
  "risk",
  "analysis",
  "tool",
  "tools",
  "now",
  "guide",
  "tips",
  "what",
  "when",
  "why",
  "how",
  "with",
  "from",
  "into",
  "your",
  "this",
  "that",
  "have",
  "more",
  "less",
  "best",
  "new",
  "latest",
  "today",
  "week",
  "feed",
  "info",
  "help",
  "learn",
  "avoid",
  "about",
  "here",
  "there",
  "index",
  "home",
  "hub",
  "topic",
  "topics",
  "platform",
  "platforms",
  "cluster",
  "clusters",
  "hybrid",
  "hybrids",
  "random",
  "revisit",
  "runway",
  "all",
  "and",
  "for",
  "the",
  "you",
  "are",
  "can",
  "will",
  "was",
  "were",
  "been",
  "via",
  "use",
  "using",
  "look",
  "like",
  "over",
  "under",
  "before",
  "after",
  "during",
  "sign",
  "signs",
  "fake",
  "real",
  "safe",
  "official",
  "online",
  "site",
  "website",
  "web",
  "mail",
  "email",
  "text",
  "texts",
  "sms",
  "phone",
  "call",
  "calls",
  "link",
  "links",
  "customer",
  "support",
  "service",
  "services",
  "accounts",
]);

const TOPIC_DEFINITIONS = [
  {
    slug: "delivery-scams",
    title: "Delivery Scams",
    keywords: [
      "delivery",
      "package",
      "packages",
      "shipment",
      "shipments",
      "shipping",
      "tracking",
      "mail",
      "postal",
      "parcel",
      "usps",
      "ups",
      "fedex",
      "dhl",
      "post",
    ],
  },
  {
    slug: "payment-scams",
    title: "Payment Scams",
    keywords: [
      "payment",
      "payments",
      "invoice",
      "invoices",
      "charge",
      "charged",
      "billing",
      "bill",
      "refund",
      "refunds",
      "renewal",
      "renewals",
      "subscription",
      "subscriptions",
      "purchase",
      "purchases",
      "receipt",
      "receipts",
      "bank",
      "wire",
      "transfer",
      "zelle",
      "venmo",
      "cashapp",
      "cash-app",
      "paypal",
    ],
  },
  {
    slug: "account-alerts",
    title: "Account Alerts",
    keywords: [
      "account",
      "accounts",
      "login",
      "signin",
      "sign-in",
      "verify",
      "verification",
      "verified",
      "password",
      "reset",
      "reset-password",
      "security",
      "locked",
      "suspended",
      "suspension",
      "disabled",
      "confirm",
      "confirmed",
      "credential",
      "credentials",
      "access",
    ],
  },
  {
    slug: "job-scams",
    title: "Job Scams",
    keywords: [
      "job",
      "jobs",
      "hiring",
      "employment",
      "career",
      "careers",
      "recruiter",
      "recruiting",
      "interview",
      "remote",
      "work-from-home",
      "indeed",
      "offer-letter",
      "offer",
    ],
  },
  {
    slug: "crypto-scams",
    title: "Crypto Scams",
    keywords: [
      "crypto",
      "bitcoin",
      "btc",
      "ethereum",
      "eth",
      "usdt",
      "wallet",
      "wallets",
      "token",
      "tokens",
      "coin",
      "coins",
      "blockchain",
      "airdrop",
      "presale",
      "defi",
      "metamask",
      "solana",
    ],
  },
  {
    slug: "social-media-scams",
    title: "Social Media Scams",
    keywords: [
      "facebook",
      "instagram",
      "whatsapp",
      "telegram",
      "snapchat",
      "tiktok",
      "twitter",
      "x",
      "discord",
      "social",
      "dm",
      "direct-message",
    ],
  },
  {
    slug: "banking-scams",
    title: "Banking Scams",
    keywords: [
      "bank",
      "banking",
      "chase",
      "wellsfargo",
      "wells-fargo",
      "capitalone",
      "capital-one",
      "citi",
      "citibank",
      "boa",
      "bankofamerica",
      "credit-card",
      "debit-card",
      "fraud-department",
    ],
  },
  {
    slug: "shopping-scams",
    title: "Shopping Scams",
    keywords: [
      "amazon",
      "walmart",
      "ebay",
      "etsy",
      "shop",
      "shopify",
      "order",
      "orders",
      "seller",
      "buyer",
      "marketplace",
      "store",
      "receipt",
    ],
  },
  {
    slug: "government-and-toll-scams",
    title: "Government And Toll Scams",
    keywords: [
      "dmv",
      "irs",
      "government",
      "gov",
      "toll",
      "ezpass",
      "e-zpass",
      "fine",
      "fines",
      "citation",
      "tax",
      "taxes",
      "customs",
    ],
  },
  {
    slug: "tech-support-scams",
    title: "Tech Support Scams",
    keywords: [
      "microsoft",
      "apple",
      "icloud",
      "google",
      "gmail",
      "windows",
      "mac",
      "tech-support",
      "support",
      "device",
      "computer",
      "system",
      "virus",
      "malware",
    ],
  },
  {
    slug: "loan-and-finance-scams",
    title: "Loan And Finance Scams",
    keywords: [
      "loan",
      "loans",
      "credit",
      "lender",
      "lending",
      "advance",
      "advances",
      "payment-plan",
      "financing",
      "finance",
    ],
  },
  {
    slug: "romance-and-dating-scams",
    title: "Romance And Dating Scams",
    keywords: [
      "dating",
      "romance",
      "tinder",
      "bumble",
      "hinge",
      "match",
      "dating-app",
    ],
  },
];

const PLATFORM_DEFINITIONS = [
  { slug: "paypal", title: "PayPal", keywords: ["paypal"] },
  { slug: "amazon", title: "Amazon", keywords: ["amazon"] },
  { slug: "apple", title: "Apple", keywords: ["apple", "icloud", "itunes"] },
  { slug: "usps", title: "USPS", keywords: ["usps"] },
  { slug: "ups", title: "UPS", keywords: ["ups"] },
  { slug: "fedex", title: "FedEx", keywords: ["fedex", "fed-ex"] },
  { slug: "dhl", title: "DHL", keywords: ["dhl"] },
  { slug: "microsoft", title: "Microsoft", keywords: ["microsoft", "windows", "outlook", "office365"] },
  { slug: "google", title: "Google", keywords: ["google", "gmail", "googlepay", "gpay"] },
  { slug: "facebook", title: "Facebook", keywords: ["facebook", "meta"] },
  { slug: "instagram", title: "Instagram", keywords: ["instagram"] },
  { slug: "whatsapp", title: "WhatsApp", keywords: ["whatsapp"] },
  { slug: "telegram", title: "Telegram", keywords: ["telegram"] },
  { slug: "cash-app", title: "Cash App", keywords: ["cashapp", "cash-app"] },
  { slug: "venmo", title: "Venmo", keywords: ["venmo"] },
  { slug: "zelle", title: "Zelle", keywords: ["zelle"] },
  { slug: "chase", title: "Chase", keywords: ["chase"] },
  { slug: "walmart", title: "Walmart", keywords: ["walmart"] },
  { slug: "ebay", title: "eBay", keywords: ["ebay"] },
  { slug: "netflix", title: "Netflix", keywords: ["netflix"] },
];

const generatedPages = [];

function fetchText(url) {
  return new Promise((resolve, reject) => {
    https
      .get(
        url,
        {
          headers: {
            "User-Agent": "Mozilla/5.0 DiscoveryBuilder/1.0",
            Accept: "application/xml,text/xml,text/plain,*/*",
          },
        },
        (res) => {
          if (res.statusCode && res.statusCode >= 400) {
            reject(new Error(`Failed to fetch ${url} - status ${res.statusCode}`));
            return;
          }

          let data = "";
          res.on("data", (chunk) => {
            data += chunk;
          });
          res.on("end", () => resolve(data));
        }
      )
      .on("error", reject);
  });
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function removePath(targetPath) {
  if (!targetPath || !fs.existsSync(targetPath)) return;
  fs.rmSync(targetPath, { recursive: true, force: true });
}

function emptyDir(dir) {
  ensureDir(dir);
  for (const name of fs.readdirSync(dir)) {
    removePath(path.join(dir, name));
  }
}

function resetDiscoveryOutput() {
  emptyDir(DISCOVERY_DIR);

  const resolvedDiscoveryDir = path.resolve(DISCOVERY_DIR);
  const resolvedDiscoverySitemap = path.resolve(DISCOVERY_SITEMAP_PATH);

  if (
    resolvedDiscoverySitemap !== resolvedDiscoveryDir &&
    !resolvedDiscoverySitemap.startsWith(`${resolvedDiscoveryDir}${path.sep}`)
  ) {
    removePath(DISCOVERY_SITEMAP_PATH);
  }
}

function writeFile(filePath, content) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, content, "utf8");
}

function escapeXml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function htmlEscape(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function nowISO() {
  return new Date().toISOString();
}

function todayString() {
  return new Date().toISOString().slice(0, 10);
}

function startOfTodayUtc() {
  const d = new Date();
  d.setUTCHours(0, 0, 0, 0);
  return d;
}

function sevenDaysAgoUtc() {
  const d = startOfTodayUtc();
  d.setUTCDate(d.getUTCDate() - 6);
  return d;
}

function decodeXml(value) {
  return String(value)
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, "&");
}

function parseSitemapEntries(xml) {
  const urlBlocks = [...xml.matchAll(/<url\b[^>]*>([\s\S]*?)<\/url>/gi)];

  if (urlBlocks.length) {
    return urlBlocks
      .map((match) => {
        const block = match[1];
        const locMatch = block.match(/<loc\b[^>]*>([\s\S]*?)<\/loc>/i);
        if (!locMatch) return null;

        const lastmodMatch = block.match(/<lastmod\b[^>]*>([\s\S]*?)<\/lastmod>/i);

        return {
          url: decodeXml(locMatch[1].trim()),
          lastmod: lastmodMatch ? decodeXml(lastmodMatch[1].trim()) : null,
        };
      })
      .filter(Boolean);
  }

  const locMatches = [...xml.matchAll(/<loc\b[^>]*>([\s\S]*?)<\/loc>/gi)];
  return locMatches.map((match) => ({
    url: decodeXml(match[1].trim()),
    lastmod: null,
  }));
}

function parseSitemapIndexLocs(xml) {
  const sitemapBlocks = [...xml.matchAll(/<sitemap\b[^>]*>([\s\S]*?)<\/sitemap>/gi)];
  if (sitemapBlocks.length === 0) return [];

  return sitemapBlocks
    .map((match) => {
      const block = match[1];
      const locMatch = block.match(/<loc\b[^>]*>([\s\S]*?)<\/loc>/i);
      return locMatch ? decodeXml(locMatch[1].trim()) : null;
    })
    .filter(Boolean);
}

async function collectEntriesFromSitemap(url, visited = new Set()) {
  if (!url || visited.has(url)) return [];
  visited.add(url);

  const xml = await fetchText(url);

  if (/<sitemapindex[\s>]/i.test(xml)) {
    const childLocs = parseSitemapIndexLocs(xml);
    let all = [];
    for (const childUrl of childLocs) {
      try {
        const childEntries = await collectEntriesFromSitemap(childUrl, visited);
        all.push(...childEntries);
      } catch (err) {
        console.error(`Failed nested sitemap: ${childUrl}`, err.message);
      }
    }
    return all;
  }

  return parseSitemapEntries(xml);
}

function uniqueByUrl(entries) {
  const map = new Map();

  for (const entry of entries) {
    if (!entry || !entry.url) continue;
    const existing = map.get(entry.url);
    if (!existing) {
      map.set(entry.url, entry);
      continue;
    }

    const existingTime = toTimestamp(existing.lastmod);
    const nextTime = toTimestamp(entry.lastmod);
    if (nextTime > existingTime) {
      map.set(entry.url, entry);
    }
  }

  return [...map.values()];
}

function uniqueStrings(values) {
  return [...new Set(values.filter(Boolean))];
}

function toTimestamp(value) {
  if (!value) return 0;
  const t = Date.parse(value);
  return Number.isNaN(t) ? 0 : t;
}

function sortNewestFirst(entries) {
  return [...entries].sort((a, b) => {
    const aTime = toTimestamp(a.lastmod);
    const bTime = toTimestamp(b.lastmod);

    if (aTime !== bTime) return bTime - aTime;
    return a.url.localeCompare(b.url);
  });
}

function filterToday(entries) {
  const start = startOfTodayUtc().getTime();
  return entries.filter((entry) => toTimestamp(entry.lastmod) >= start);
}

function filterThisWeek(entries) {
  const start = sevenDaysAgoUtc().getTime();
  return entries.filter((entry) => toTimestamp(entry.lastmod) >= start);
}

function getPathname(url) {
  try {
    return decodeURIComponent(new URL(url).pathname.toLowerCase());
  } catch {
    return "";
  }
}

function getPathSegments(url) {
  return getPathname(url)
    .split("/")
    .filter(Boolean);
}

function joinSiteUrl(relativePath) {
  return `${SITE_URL}/${String(relativePath).replace(/^\/+/, "")}`;
}

function joinDiscoveryUrl(relativePath = "") {
  const pieces = [DISCOVERY_SEGMENT, String(relativePath || "").replace(/^\/+|\/+$/g, "")]
    .filter(Boolean)
    .join("/");
  return joinSiteUrl(`${pieces}/`);
}

function slugify(value) {
  return (
    String(value)
      .toLowerCase()
      .trim()
      .replace(/&/g, " and ")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "general"
  );
}

function titleCaseFromSlug(slug) {
  return String(slug)
    .split("-")
    .filter(Boolean)
    .map((part) => {
      if (part === "usps") return "USPS";
      if (part === "ups") return "UPS";
      if (part === "dhl") return "DHL";
      if (part === "dmv") return "DMV";
      if (part === "irs") return "IRS";
      if (part === "ebay") return "eBay";
      if (part === "x") return "X";
      return part.charAt(0).toUpperCase() + part.slice(1);
    })
    .join(" ");
}

function shuffle(values) {
  const arr = [...values];
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function pickRandomEntries(entries, count) {
  return shuffle(entries).slice(0, count);
}

function formatDisplayUrl(url) {
  return String(url)
    .replace(/^https?:\/\//, "")
    .replace(/\/+$/, "");
}

function normalizeText(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");
}

function tokenizeNormalized(value) {
  return normalizeText(value)
    .split(" ")
    .map((part) => part.trim())
    .filter(Boolean);
}

function tokenizeUrl(url) {
  const pathname = getPathname(url);
  return pathname
    .split(/[^a-z0-9]+/i)
    .map((part) => part.trim().toLowerCase())
    .filter((part) => {
      if (!part) return false;
      if (part.length < 3) return false;
      if (/^\d+$/.test(part)) return false;
      if (STOPWORDS.has(part)) return false;
      return true;
    });
}

function annotateEntry(entry) {
  const pathname = getPathname(entry.url);
  const segments = getPathSegments(entry.url);
  const tokens = uniqueStrings(tokenizeUrl(entry.url));
  const ts = toTimestamp(entry.lastmod);
  const normalized = normalizeText(`${pathname} ${tokens.join(" ")}`);
  const normalizedTokens = new Set(tokenizeNormalized(normalized));

  return {
    ...entry,
    pathname,
    segments,
    tokens,
    ts,
    normalized,
    normalizedTokens,
  };
}

function sanitizeEntries(entries) {
  const siteHost = (() => {
    try {
      return new URL(SITE_URL).host;
    } catch {
      return "";
    }
  })();

  return entries.filter((entry) => {
    try {
      const u = new URL(entry.url);
      const pathname = (u.pathname || "").toLowerCase();

      if (siteHost && u.host !== siteHost) return false;
      if (!pathname || pathname === "/") return false;
      if (pathname.includes(`/${DISCOVERY_SEGMENT.toLowerCase()}/`)) return false;
      if (pathname.endsWith(".xml")) return false;
      if (pathname.includes("/sitemap")) return false;

      return true;
    } catch {
      return false;
    }
  });
}

function formatEntryLabel(entry) {
  const usefulSegments = entry.segments.filter(
    (segment) =>
      !["check", "checks", DISCOVERY_SEGMENT.toLowerCase()].includes(segment.toLowerCase())
  );

  const tail = usefulSegments.slice(-3).map((segment) => titleCaseFromSlug(segment));
  const candidate = tail.join(" / ").trim();
  return candidate || formatDisplayUrl(entry.url);
}

function entriesToListItems(entries) {
  return entries.map((entry) => ({
    href: entry.url,
    label: formatEntryLabel(entry),
    sub: formatDisplayUrl(entry.url),
  }));
}

function linksToItems(links) {
  return links.map((link) => ({
    href: link.href,
    label: link.label,
    sub: link.sub || formatDisplayUrl(link.href),
  }));
}

function chunkEntries(entries, pageSize, maxPages) {
  const chunks = [];
  for (let i = 0; i < Math.min(maxPages, Math.ceil(entries.length / pageSize)); i += 1) {
    const slice = entries.slice(i * pageSize, (i + 1) * pageSize);
    if (!slice.length) break;
    chunks.push(slice);
  }
  return chunks;
}

function buildPagerSection(basePath, totalPages, currentPage, label) {
  if (totalPages <= 1) return "";

  const links = [];
  const start = Math.max(1, currentPage - 2);
  const end = Math.min(totalPages, currentPage + 2);

  for (let pageNum = start; pageNum <= end; pageNum += 1) {
    const href =
      pageNum === 1
        ? joinDiscoveryUrl(basePath)
        : joinDiscoveryUrl(`${basePath}/page-${pageNum}`);
    links.push({
      href,
      label: pageNum === 1 ? `${label} Page 1` : `${label} Page ${pageNum}`,
      sub: pageNum === currentPage ? "Current page" : "Browse more discovery URLs",
    });
  }

  return buildRelatedSection({
    title: `${label} pages`,
    intro: "Move deeper through paginated discovery pages without losing crawl depth.",
    links,
  });
}

function buildRelatedSection({ title, intro, links }) {
  if (!links || !links.length) return "";

  return `
    <div class="related-card">
      <div class="related-top">
        <h3>${htmlEscape(title)}</h3>
        <p>${htmlEscape(intro)}</p>
      </div>
      <ul class="related-grid">
        ${links
          .map(
            (item) => `
          <li>
            <a class="related-link" href="${htmlEscape(item.href)}">
              <span>
                <span class="related-label">${htmlEscape(item.label)}</span>
                <span class="related-sub">${htmlEscape(item.sub || formatDisplayUrl(item.href))}</span>
              </span>
              <span class="related-arrow">→</span>
            </a>
          </li>
        `
          )
          .join("\n")}
      </ul>
    </div>
  `;
}

function getPageMeta(title, kind = "generic") {
  if (kind === "hub") {
    return {
      badge: "Discovery hub",
      kicker: "Scam discovery engine",
      eyebrow: "Browse discovery surfaces",
      intro:
        "Use the discovery hub to move across recent scam check pages, grouped scam topics, platform collections, random discovery pages, and revisited older URLs that deserve fresh crawl attention.",
      statA: "Central access",
      statB: "Strong recirculation",
      statC: "Built for scale",
    };
  }

  if (kind === "latest") {
    return {
      badge: "Updated continuously",
      kicker: "Latest discovery",
      eyebrow: "Newest pages added",
      intro:
        "Browse the newest scam check pages discovered from your sitemap. This is the fastest way to see fresh suspicious message topics, account warning pages, delivery scam pages, and payment alert coverage in one place.",
      statA: "Newest additions",
      statB: "Fast discovery",
      statC: "Built for reuse",
    };
  }

  if (kind === "today") {
    return {
      badge: "Fresh today",
      kicker: "Today’s discovery",
      eyebrow: "New pages discovered today",
      intro:
        "See today’s newest scam check pages in one place. This page is built for fast discovery when suspicious messages, payment alerts, or fake delivery notices start appearing right now.",
      statA: "Today’s updates",
      statB: "Quick scan",
      statC: "High urgency",
    };
  }

  if (kind === "week") {
    return {
      badge: "This week",
      kicker: "Weekly discovery",
      eyebrow: "Recent pages from this week",
      intro:
        "Browse scam check pages discovered over the last week. This gives you a broader view of recent scam topics, warning patterns, and message types without having to dig through the sitemap manually.",
      statA: "7-day coverage",
      statB: "Broader view",
      statC: "Recent patterns",
    };
  }

  if (kind === "html") {
    return {
      badge: "Full browse view",
      kicker: "HTML sitemap",
      eyebrow: "Combined scam page directory",
      intro:
        "Use this HTML sitemap as a broad discovery page for scam check topics. It helps people move quickly through suspicious message pages, compare patterns, and reach a focused warning page faster.",
      statA: "Wide coverage",
      statB: "Search-friendly",
      statC: "Navigation hub",
    };
  }

  if (kind === "feed") {
    return {
      badge: "Fast feed",
      kicker: "Fresh scan feed",
      eyebrow: "Quick discovery feed",
      intro:
        "This fast discovery feed surfaces a tight set of fresh scam check pages for quick browsing, internal recirculation, and strong repeat visits.",
      statA: "Fast feed",
      statB: "Quick reuse",
      statC: "Fresh coverage",
    };
  }

  if (kind === "runway") {
    return {
      badge: "Runway pages",
      kicker: "Deeper discovery runway",
      eyebrow: "Paginated crawl runway",
      intro:
        "Runway pages push more scam check URLs into the discovery layer without bloating a single page. They are designed to deepen crawl paths while staying structured and indexable.",
      statA: "Deeper paths",
      statB: "Large coverage",
      statC: "Index support",
    };
  }

  if (kind === "random") {
    return {
      badge: "Discovery mix",
      kicker: "Random discovery",
      eyebrow: "Explore different scam patterns",
      intro:
        "Random discovery pages surface a shuffled mix of scam check URLs, creating alternate crawl paths and exposing overlooked suspicious message pages.",
      statA: "Mixed coverage",
      statB: "Extra crawl paths",
      statC: "Useful revisits",
    };
  }

  if (kind === "revisit") {
    return {
      badge: "Revisit older pages",
      kicker: "Resurfaced discovery",
      eyebrow: "Older pages worth recrawling",
      intro:
        "Revisit pages bring older scam check URLs back into the discovery layer so they can gain fresh internal links and more crawl attention.",
      statA: "Older URLs",
      statB: "Fresh links",
      statC: "Recrawl support",
    };
  }

  if (kind === "topics") {
    return {
      badge: "Topic discovery",
      kicker: "Grouped by scam topic",
      eyebrow: "Browse topic collections",
      intro:
        "These topic discovery pages organize scam check URLs by repeated themes like payment alerts, delivery scams, job scams, crypto risks, and account warnings.",
      statA: "Topic signals",
      statB: "Structured browsing",
      statC: "SEO support",
    };
  }

  if (kind === "topic-child") {
    return {
      badge: "Topic page",
      kicker: "Focused topic discovery",
      eyebrow: title,
      intro:
        "Browse a focused group of scam check URLs tied together by a repeated scam theme. This page helps people compare similar warning patterns fast.",
      statA: "Focused theme",
      statB: "Clear grouping",
      statC: "Related patterns",
    };
  }

  if (kind === "platforms") {
    return {
      badge: "Platform discovery",
      kicker: "Grouped by platform",
      eyebrow: "Browse platform collections",
      intro:
        "These platform discovery pages organize scam check URLs around the brands, services, and platforms that show up repeatedly in suspicious messages.",
      statA: "Brand grouping",
      statB: "Clear navigation",
      statC: "Repeat utility",
    };
  }

  if (kind === "platform-child") {
    return {
      badge: "Platform page",
      kicker: "Focused platform discovery",
      eyebrow: title,
      intro:
        "Browse scam check URLs tied to one specific platform or brand so people can quickly compare related warning pages and suspicious message patterns.",
      statA: "Brand focus",
      statB: "Relevant warnings",
      statC: "Higher intent",
    };
  }

  if (kind === "clusters") {
    return {
      badge: "Cluster discovery",
      kicker: "Grouped by repeated tokens",
      eyebrow: "Browse repeated pattern clusters",
      intro:
        "Cluster pages are built from repeated URL patterns and terms found across your sitemap. They help expose additional related discovery surfaces at scale.",
      statA: "Pattern grouping",
      statB: "Extra coverage",
      statC: "Scale support",
    };
  }

  if (kind === "cluster-child") {
    return {
      badge: "Cluster page",
      kicker: "Repeated pattern discovery",
      eyebrow: title,
      intro:
        "Browse scam check URLs connected by a repeated pattern discovered across your sitemap URLs. This creates additional structured internal links without editing the underlying pages.",
      statA: "Pattern signal",
      statB: "Additional paths",
      statC: "Discovery depth",
    };
  }

  if (kind === "hybrids") {
    return {
      badge: "Hybrid discovery",
      kicker: "Platform plus topic pages",
      eyebrow: "Browse hybrid collections",
      intro:
        "Hybrid pages combine a platform or brand with a repeated scam intent, creating high-intent discovery surfaces that often match how people search.",
      statA: "Higher intent",
      statB: "Combined signals",
      statC: "Strong entry points",
    };
  }

  if (kind === "hybrid-child") {
    return {
      badge: "Hybrid page",
      kicker: "Combined intent discovery",
      eyebrow: title,
      intro:
        "Browse a higher-intent set of scam check URLs that combine a platform with a repeated scam topic or action pattern.",
      statA: "Combined relevance",
      statB: "Focused set",
      statC: "Useful comparison",
    };
  }

  return {
    badge: "Discovery page",
    kicker: "Scam detection discovery",
    eyebrow: title,
    intro:
      "Use this discovery page to move through scam check topics quickly, compare suspicious message patterns, and reach a focused warning page before clicking links, replying, sending money, or sharing personal information.",
    statA: "Clear access",
    statB: "Structured navigation",
    statC: "Return visits",
  };
}

function globalRelatedDiscoverySection() {
  const links = [
    { href: joinDiscoveryUrl(""), label: "Discovery Hub" },
    { href: joinDiscoveryUrl("latest"), label: "Latest Pages" },
    { href: joinDiscoveryUrl("today"), label: "Today Pages" },
    { href: joinDiscoveryUrl("this-week"), label: "This Week" },
    { href: joinDiscoveryUrl("html-sitemap"), label: "HTML Sitemap" },
    { href: joinDiscoveryUrl("feed"), label: "Discovery Feed" },
    { href: joinDiscoveryUrl("clusters"), label: "Discovery Clusters" },
    { href: joinDiscoveryUrl("platforms"), label: "All Platforms" },
    { href: joinDiscoveryUrl("topics"), label: "All Topics" },
    { href: joinDiscoveryUrl("runway"), label: "Runway Pages" },
    { href: joinDiscoveryUrl("hybrids"), label: "Hybrid Discovery Pages" },
    { href: joinDiscoveryUrl("random"), label: "Random Discovery 1" },
    { href: joinDiscoveryUrl("random-2"), label: "Random Discovery 2" },
    { href: joinDiscoveryUrl("random-3"), label: "Random Discovery 3" },
    { href: joinDiscoveryUrl("revisit"), label: "Revisit Pages" },
  ];

  return buildRelatedSection({
    title: "Related discovery pages",
    intro:
      "Move through more scam discovery surfaces, recent pages, topic collections, platform groupings, and supporting navigation hubs.",
    links,
  });
}

function pageShell({
  title,
  canonicalUrl,
  intro = "",
  items = [],
  extraSections = [],
  kind = "generic",
}) {
  const meta = getPageMeta(title, kind);
  const sections = [...extraSections, globalRelatedDiscoverySection()].filter(Boolean);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>${htmlEscape(title)}</title>
  <meta name="description" content="${htmlEscape(intro || meta.intro)}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="${htmlEscape(canonicalUrl)}">

  <meta property="og:title" content="${htmlEscape(title)}">
  <meta property="og:description" content="${htmlEscape(intro || meta.intro)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="${htmlEscape(canonicalUrl)}">

  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="${htmlEscape(title)}">
  <meta name="twitter:description" content="${htmlEscape(intro || meta.intro)}">

  <style>
    :root{
      --bg:#07111f;
      --bg-2:#0c1728;
      --bg-3:#12203a;
      --surface:rgba(255,255,255,.06);
      --surface-2:rgba(255,255,255,.08);
      --card:#101c33;
      --ink:#e8f0ff;
      --ink-strong:#ffffff;
      --muted:#9eb0cf;
      --line:rgba(148,163,184,.20);
      --cyan:#22d3ee;
      --cyan-2:#06b6d4;
      --violet:#8b5cf6;
      --emerald:#10b981;
      --shadow-xl:0 32px 90px rgba(2,6,23,.42);
      --shadow-md:0 12px 30px rgba(2,6,23,.22);
      --shadow-sm:0 8px 20px rgba(2,6,23,.16);
    }

    *{box-sizing:border-box;}
    html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;}

    body{
      font-family:Inter,system-ui,-apple-system,Arial,sans-serif;
      margin:0;
      padding-top:90px;
      color:var(--ink);
      line-height:1.6;
      background:
        radial-gradient(circle at 14% 8%, rgba(34,211,238,.16), transparent 22%),
        radial-gradient(circle at 84% 0%, rgba(139,92,246,.20), transparent 28%),
        radial-gradient(circle at 50% 100%, rgba(16,185,129,.08), transparent 24%),
        linear-gradient(180deg,#06101b 0%, #0a1324 34%, #0e1830 100%);
    }

    a{color:#8be9ff;text-decoration:none;}
    a:hover{text-decoration:underline;}

    @supports (padding:max(0px)) {
      body{
        padding-left:max(0px, env(safe-area-inset-left));
        padding-right:max(0px, env(safe-area-inset-right));
      }
    }

    .top-bar{
      position:fixed;
      top:0;
      left:0;
      width:100%;
      display:flex;
      justify-content:space-between;
      align-items:center;
      padding:10px 16px;
      z-index:1000;
      pointer-events:none;
    }

    .top-actions{
      pointer-events:auto;
      display:flex;
      align-items:center;
      gap:10px;
      margin-right:20px;
    }

    .logo{
      pointer-events:auto;
      display:inline-flex;
      align-items:center;
      gap:10px;
      font-size:14px;
      font-weight:900;
      color:#eef6ff;
      margin-left:8px;
      padding:11px 15px;
      border-radius:999px;
      letter-spacing:-.01em;
      background:rgba(10,18,35,.68);
      border:1px solid rgba(255,255,255,.10);
      backdrop-filter:blur(14px);
      box-shadow:var(--shadow-sm);
      text-decoration:none;
    }

    .logo-dot{
      width:10px;
      height:10px;
      border-radius:50%;
      background:linear-gradient(180deg,var(--cyan) 0%,var(--violet) 100%);
      box-shadow:0 0 0 4px rgba(139,92,246,.14);
      flex:0 0 10px;
    }

    .app-top{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      padding:11px 14px;
      font-size:14px;
      border-radius:16px;
      font-weight:900;
      color:#fff;
      border:1px solid rgba(255,255,255,.12);
      white-space:nowrap;
      background:linear-gradient(180deg,rgba(255,255,255,.14) 0%,rgba(255,255,255,.08) 100%);
      backdrop-filter:blur(10px);
      box-shadow:var(--shadow-sm);
    }

    .upgrade-top{
      pointer-events:auto;
      display:inline-flex;
      align-items:center;
      justify-content:center;
      padding:11px 15px;
      font-size:14px;
      border-radius:16px;
      font-weight:900;
      background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
      color:#fff;
      white-space:nowrap;
      box-shadow:0 16px 34px rgba(34,211,238,.16);
      text-decoration:none;
    }

    .page-shell{
      max-width:980px;
      margin:0 auto;
      padding:0 14px 34px;
    }

    .hero{
      position:relative;
      padding:18px 8px 20px;
      max-width:980px;
      margin:0 auto 14px;
      text-align:center;
    }

    .hero-badge-row{
      display:flex;
      flex-wrap:wrap;
      justify-content:center;
      gap:10px;
      margin-bottom:14px;
    }

    .hero-badge{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      gap:8px;
      padding:9px 13px;
      border-radius:999px;
      font-size:13px;
      font-weight:900;
      color:#dbeafe;
      background:rgba(255,255,255,.08);
      border:1px solid rgba(255,255,255,.10);
      backdrop-filter:blur(10px);
    }

    .hero h1{
      margin:0;
      font-size:48px;
      line-height:1.02;
      letter-spacing:-.05em;
      font-weight:950;
      color:#fff;
      text-wrap:balance;
    }

    .hero p{
      margin:14px auto 0;
      max-width:760px;
      font-size:19px;
      color:#c7d5eb;
      text-wrap:balance;
    }

    .hero-trust{
      margin-top:18px;
      display:flex;
      flex-wrap:wrap;
      justify-content:center;
      gap:10px;
    }

    .hero-trust-chip{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      padding:10px 14px;
      border-radius:999px;
      font-size:13px;
      font-weight:900;
      color:#dce8fb;
      background:rgba(255,255,255,.06);
      border:1px solid rgba(255,255,255,.10);
      box-shadow:var(--shadow-sm);
    }

    .container{
      max-width:860px;
      margin:auto;
      padding:22px;
      border-radius:30px;
      position:relative;
      overflow:hidden;
      border:1px solid rgba(255,255,255,.10);
      background:
        linear-gradient(180deg, rgba(17,28,51,.94) 0%, rgba(11,19,36,.98) 100%);
      box-shadow:var(--shadow-xl);
    }

    .container::before{
      content:"";
      position:absolute;
      top:-120px;
      right:-90px;
      width:260px;
      height:260px;
      border-radius:50%;
      background:radial-gradient(circle, rgba(34,211,238,.14), transparent 65%);
      pointer-events:none;
    }

    .container > *{position:relative;z-index:1;}

    .intro-card,
    .stats-band,
    .links-card,
    .related-card,
    .footer-note{
      background:linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
      border:1px solid rgba(255,255,255,.10);
      border-radius:24px;
      box-shadow:var(--shadow-md);
    }

    .intro-card{
      padding:20px;
      background:
        linear-gradient(135deg, rgba(34,211,238,.12) 0%, rgba(139,92,246,.12) 100%),
        linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.05) 100%);
    }

    .intro-kicker{
      font-size:12px;
      font-weight:900;
      letter-spacing:.08em;
      text-transform:uppercase;
      color:#8be9ff;
      margin-bottom:8px;
    }

    .intro-card h2{
      margin:0;
      font-size:28px;
      line-height:1.08;
      letter-spacing:-.03em;
      color:#fff;
    }

    .intro-card p{
      margin:10px 0 0;
      font-size:15px;
      font-weight:800;
      color:#d8e5f8;
      line-height:1.7;
    }

    .stats-band{
      display:grid;
      grid-template-columns:repeat(3,minmax(0,1fr));
      gap:12px;
      padding:16px;
      margin-top:18px;
    }

    .stat-box{
      padding:14px;
      border-radius:18px;
      background:rgba(255,255,255,.05);
      border:1px solid rgba(255,255,255,.08);
    }

    .stat-label{
      font-size:12px;
      font-weight:900;
      letter-spacing:.08em;
      text-transform:uppercase;
      color:#8be9ff;
      margin-bottom:6px;
    }

    .stat-box p{
      margin:0;
      font-size:14px;
      font-weight:800;
      line-height:1.6;
      color:#d6e3f7;
    }

    .links-card{
      margin-top:18px;
      padding:22px;
      background:
        linear-gradient(135deg, rgba(34,211,238,.10) 0%, rgba(139,92,246,.10) 100%),
        linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.04) 100%);
    }

    .links-top{
      text-align:center;
      margin-bottom:16px;
    }

    .links-top h2{
      margin:0;
      font-size:30px;
      line-height:1.10;
      letter-spacing:-.04em;
      color:#fff;
    }

    .links-top p{
      margin:8px auto 0;
      max-width:680px;
      font-size:15px;
      color:#c8d6ec;
      font-weight:700;
      line-height:1.7;
    }

    .links-list{
      list-style:none;
      padding:0;
      margin:0;
      display:grid;
      gap:12px;
    }

    .links-list li{margin:0;}

    .link-item{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:16px;
      padding:16px 18px;
      border-radius:18px;
      background:rgba(255,255,255,.05);
      border:1px solid rgba(255,255,255,.09);
      transition:transform .15s ease, border-color .15s ease, background .15s ease;
      text-decoration:none;
    }

    .link-item:hover{
      transform:translateY(-1px);
      border-color:rgba(34,211,238,.35);
      background:rgba(255,255,255,.07);
      text-decoration:none;
    }

    .link-copy{min-width:0;}

    .link-title{
      display:block;
      font-size:15px;
      font-weight:900;
      line-height:1.4;
      color:#fff;
      margin-bottom:3px;
      word-break:break-word;
    }

    .link-sub{
      display:block;
      font-size:13px;
      line-height:1.58;
      font-weight:800;
      color:#bfd0ea;
      word-break:break-word;
    }

    .link-arrow{
      flex:0 0 auto;
      display:inline-flex;
      align-items:center;
      justify-content:center;
      width:34px;
      height:34px;
      border-radius:999px;
      background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
      color:#fff;
      font-size:16px;
      font-weight:900;
      box-shadow:0 12px 24px rgba(34,211,238,.16);
    }

    .related-card{
      margin-top:18px;
      padding:22px;
    }

    .related-top{
      text-align:center;
      margin-bottom:16px;
    }

    .related-top h3{
      margin:0;
      font-size:24px;
      line-height:1.12;
      letter-spacing:-.03em;
      color:#fff;
    }

    .related-top p{
      margin:8px auto 0;
      max-width:680px;
      font-size:14px;
      color:#c8d6ec;
      font-weight:700;
      line-height:1.68;
    }

    .related-grid{
      list-style:none;
      padding:0;
      margin:0;
      display:grid;
      grid-template-columns:repeat(2,minmax(0,1fr));
      gap:10px;
    }

    .related-grid li{margin:0;}

    .related-link{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:12px;
      padding:14px 15px;
      border-radius:18px;
      background:rgba(255,255,255,.05);
      border:1px solid rgba(255,255,255,.08);
      transition:transform .15s ease, border-color .15s ease, background .15s ease;
      text-decoration:none;
    }

    .related-link:hover{
      transform:translateY(-1px);
      border-color:rgba(34,211,238,.35);
      background:rgba(255,255,255,.07);
      text-decoration:none;
    }

    .related-label{
      display:block;
      font-size:14px;
      font-weight:900;
      color:#fff;
      line-height:1.45;
    }

    .related-sub{
      display:block;
      font-size:12px;
      font-weight:800;
      color:#bfd0ea;
      line-height:1.5;
      margin-top:3px;
      word-break:break-word;
    }

    .related-arrow{
      flex:0 0 auto;
      color:#8be9ff;
      font-size:15px;
      font-weight:900;
    }

    .footer-note{
      margin-top:18px;
      padding:18px;
      font-size:15px;
      font-weight:800;
      color:#d7e4f8;
      line-height:1.72;
      background:rgba(255,255,255,.05);
    }

    .footer{
      text-align:center;
      margin-top:72px;
      padding:40px 20px;
      color:#9fb0cc;
      font-size:14px;
      line-height:1.75;
      text-wrap:balance;
    }

    .footer a{
      color:#8be9ff;
      font-weight:700;
    }

    @media (max-width:640px){
      body{padding-top:84px;}
      .hero{padding:14px 6px 18px;}
      .hero h1{font-size:34px;}
      .hero p{margin-top:10px;font-size:17px;}
      .container{margin-left:12px;margin-right:12px;padding:18px;border-radius:24px;}
      .top-bar{padding:10px 10px;}
      .top-actions{gap:8px;margin-right:0;}
      .logo{font-size:13px;margin-left:2px;padding:9px 12px;}
      .app-top{font-size:13px;padding:8px 10px;}
      .upgrade-top{font-size:13px;padding:8px 10px;margin-right:0;}
      .intro-card h2{font-size:22px;}
      .links-top h2{font-size:24px;}
      .stats-band{grid-template-columns:1fr;}
      .related-grid{grid-template-columns:1fr;}
      .link-item{align-items:flex-start;}
    }
  </style>
</head>
<body>

  <div class="top-bar">
    <a class="logo" href="${htmlEscape(joinSiteUrl("check/"))}">
      <span class="logo-dot"></span>
      <span>Scam Check Now</span>
    </a>
    <div class="top-actions">
      <a class="app-top" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">📱 Get App</a>
      <a class="upgrade-top" href="${htmlEscape(joinSiteUrl("check/"))}">Run Check</a>
    </div>
  </div>

  <div class="page-shell">

    <div class="hero">
      <div class="hero-badge-row">
        <div class="hero-badge">${htmlEscape(meta.badge)}</div>
        <div class="hero-badge">Premium discovery pages</div>
        <div class="hero-badge">Built for repeat use</div>
      </div>

      <h1>${htmlEscape(title)}</h1>
      <p>${htmlEscape(intro || meta.intro)}</p>

      <div class="hero-trust">
        <div class="hero-trust-chip">Check before you click</div>
        <div class="hero-trust-chip">Check before you reply</div>
        <div class="hero-trust-chip">Check before you send money</div>
      </div>
    </div>

    <div class="container">
      <div class="intro-card">
        <div class="intro-kicker">${htmlEscape(meta.kicker)}</div>
        <h2>${htmlEscape(meta.eyebrow)}</h2>
        <p>${htmlEscape(meta.intro)}</p>
      </div>

      <div class="stats-band">
        <div class="stat-box">
          <div class="stat-label">${htmlEscape(meta.statA)}</div>
          <p>Structured discovery pages make it easier to browse suspicious topics without digging through clutter.</p>
        </div>
        <div class="stat-box">
          <div class="stat-label">${htmlEscape(meta.statB)}</div>
          <p>These pages are built to help people move faster from uncertainty to a focused scam check page.</p>
        </div>
        <div class="stat-box">
          <div class="stat-label">${htmlEscape(meta.statC)}</div>
          <p>Return visits matter here because suspicious messages, payment warnings, and fake alerts rarely happen once.</p>
        </div>
      </div>

      <div class="links-card">
        <div class="links-top">
          <h2>Browse scam check pages</h2>
          <p>Open a focused scam check page below to review suspicious messages, delivery alerts, account warnings, payment requests, crypto traps, and more.</p>
        </div>

        <ul class="links-list">
          ${items
            .map(
              (item) => `
            <li>
              <a class="link-item" href="${htmlEscape(item.href)}">
                <span class="link-copy">
                  <span class="link-title">${htmlEscape(item.label)}</span>
                  <span class="link-sub">${htmlEscape(item.sub || formatDisplayUrl(item.href))}</span>
                </span>
                <span class="link-arrow">→</span>
              </a>
            </li>
          `
            )
            .join("\n")}
        </ul>
      </div>

      ${sections.join("\n")}

      <div class="footer-note">
        These discovery pages are designed to help people navigate scam topics faster, compare patterns, and reach a focused warning page before clicking links, replying, sending money, or sharing personal information.
      </div>
    </div>

    <footer class="footer">
      <div>
        By using this website you agree to our
        <a href="${htmlEscape(joinSiteUrl("website-policies/scam-check/"))}" target="_blank" rel="noopener noreferrer">Terms and Privacy Policy</a>.
      </div>
      <div style="margin-top:10px">
        Scam Check Now © 2026 • Scam detection and risk analysis tool
      </div>
    </footer>

  </div>

</body>
</html>`;
}

function registerGeneratedPage(bucket, url, lastmod = nowISO()) {
  generatedPages.push({ bucket, url, lastmod });
}

function writeDiscoveryPage(
  relativePath,
  { title, intro, items, extraSections = [], kind = "generic" },
  bucket = "core"
) {
  const cleanRelative = String(relativePath || "").replace(/^\/+|\/+$/g, "");
  const filePath = cleanRelative
    ? path.join(DISCOVERY_DIR, cleanRelative, "index.html")
    : path.join(DISCOVERY_DIR, "index.html");

  const canonicalUrl = cleanRelative ? joinDiscoveryUrl(cleanRelative) : joinDiscoveryUrl("");
  const html = pageShell({
    title,
    canonicalUrl,
    intro,
    items,
    extraSections,
    kind,
  });

  writeFile(filePath, html);
  registerGeneratedPage(bucket, canonicalUrl);
}

function buildXmlSitemap(urlsWithDates) {
  const unique = [];
  const seen = new Set();

  for (const item of urlsWithDates) {
    if (!item || !item.url || seen.has(item.url)) continue;
    seen.add(item.url);
    unique.push(item);
  }

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${unique
  .map(
    (item) =>
      `  <url><loc>${escapeXml(item.url)}</loc><lastmod>${escapeXml(
        item.lastmod || nowISO()
      )}</lastmod></url>`
  )
  .join("\n")}
</urlset>`;
}

function buildSitemapIndexXml(sitemapUrls) {
  const unique = uniqueStrings(sitemapUrls);

  return `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${unique
  .map(
    (url) =>
      `  <sitemap><loc>${escapeXml(url)}</loc><lastmod>${escapeXml(nowISO())}</lastmod></sitemap>`
  )
  .join("\n")}
</sitemapindex>`;
}

function writeSegmentedDiscoverySitemaps() {
  const bucketFiles = {
    core: "core.xml",
    topics: "topics.xml",
    platforms: "platforms.xml",
    hybrids: "hybrids.xml",
    clusters: "clusters.xml",
    explore: "explore.xml",
  };

  const bucketUrls = {};

  for (const page of generatedPages) {
    const bucket = bucketFiles[page.bucket] ? page.bucket : "core";
    if (!bucketUrls[bucket]) bucketUrls[bucket] = [];
    bucketUrls[bucket].push({ url: page.url, lastmod: page.lastmod });
  }

  const sitemapIndexUrls = [];

  for (const [bucket, fileName] of Object.entries(bucketFiles)) {
    const entries = bucketUrls[bucket] || [];
    if (!entries.length) continue;

    const relativeXmlPath = path.posix.join(DISCOVERY_SEGMENT, "sitemaps", fileName);
    const localXmlPath = path.join(DISCOVERY_DIR, "sitemaps", fileName);
    writeFile(localXmlPath, buildXmlSitemap(entries));
    sitemapIndexUrls.push(joinSiteUrl(relativeXmlPath));
  }

  writeFile(DISCOVERY_SITEMAP_PATH, buildSitemapIndexXml(sitemapIndexUrls));
}

function buildGroupPageLinks(basePath, groups, maxItems = 24) {
  return groups.slice(0, maxItems).map((group) => ({
    href: joinDiscoveryUrl(`${basePath}/${group.slug}`),
    label: group.title,
    sub: `${group.entries.length} grouped URLs`,
  }));
}

function matchesKeyword(entry, keyword) {
  const parts = tokenizeNormalized(keyword);
  if (!parts.length) return false;
  return parts.every((part) => entry.normalizedTokens.has(part));
}

function matchDefinition(entry, definition) {
  return definition.keywords.some((keyword) => matchesKeyword(entry, keyword));
}

function buildPlatformGroups(entries) {
  return PLATFORM_DEFINITIONS.map((definition) => {
    const matched = entries.filter((entry) => matchDefinition(entry, definition));
    return {
      slug: definition.slug,
      title: definition.title,
      definition,
      entries: sortNewestFirst(uniqueByUrl(matched)).slice(0, MAX_PLATFORM_PAGE_URLS),
    };
  })
    .filter((group) => group.entries.length >= MIN_PLATFORM_SIZE)
    .sort((a, b) => b.entries.length - a.entries.length)
    .slice(0, MAX_PLATFORM_GROUPS);
}

function buildTopicGroups(entries) {
  return TOPIC_DEFINITIONS.map((definition) => {
    const matched = entries.filter((entry) => matchDefinition(entry, definition));
    return {
      slug: definition.slug,
      title: definition.title,
      definition,
      entries: sortNewestFirst(uniqueByUrl(matched)).slice(0, MAX_TOPIC_PAGE_URLS),
    };
  })
    .filter((group) => group.entries.length >= MIN_TOPIC_SIZE)
    .sort((a, b) => b.entries.length - a.entries.length)
    .slice(0, MAX_TOPIC_GROUPS);
}

function buildClusterGroups(entries) {
  const counts = new Map();

  for (const entry of entries) {
    for (const token of entry.tokens) {
      if (STOPWORDS.has(token)) continue;
      if (token.length < 4) continue;
      if (!counts.has(token)) counts.set(token, []);
      counts.get(token).push(entry);
    }
  }

  return [...counts.entries()]
    .map(([token, groupedEntries]) => ({
      slug: slugify(token),
      title: `${titleCaseFromSlug(token)} Cluster`,
      rawToken: token,
      entries: sortNewestFirst(uniqueByUrl(groupedEntries)).slice(0, MAX_CLUSTER_PAGE_URLS),
    }))
    .filter((group) => group.entries.length >= MIN_CLUSTER_SIZE)
    .filter((group) => !TOPIC_DEFINITIONS.some((d) => d.slug === group.slug))
    .filter((group) => !PLATFORM_DEFINITIONS.some((d) => d.slug === group.slug))
    .sort((a, b) => b.entries.length - a.entries.length)
    .slice(0, MAX_CLUSTER_GROUPS);
}

function buildHybridGroups(entries, platformGroups, topicGroups) {
  const hybrids = [];

  for (const platformGroup of platformGroups) {
    for (const topicGroup of topicGroups) {
      const intersection = sortNewestFirst(
        uniqueByUrl(
          entries.filter(
            (entry) =>
              matchDefinition(entry, platformGroup.definition) &&
              matchDefinition(entry, topicGroup.definition)
          )
        )
      ).slice(0, MAX_HYBRID_PAGE_URLS);

      if (intersection.length < MIN_HYBRID_SIZE) continue;

      hybrids.push({
        slug: `${platformGroup.slug}-${topicGroup.slug}`,
        title: `${platformGroup.title} ${topicGroup.title}`,
        entries: intersection,
        platformSlug: platformGroup.slug,
        topicSlug: topicGroup.slug,
      });
    }
  }

  return hybrids
    .sort((a, b) => b.entries.length - a.entries.length)
    .slice(0, MAX_HYBRID_PAGES);
}

function hasItems(items) {
  return Array.isArray(items) && items.length > 0;
}

function createFallbackIndexItems() {
  return linksToItems([
    { href: joinDiscoveryUrl("latest"), label: "Latest Pages", sub: "Newest discovery URLs" },
    { href: joinDiscoveryUrl("today"), label: "Today Pages", sub: "Fresh discovery URLs" },
    { href: joinDiscoveryUrl("this-week"), label: "This Week", sub: "Recent 7-day discovery view" },
    { href: joinDiscoveryUrl("html-sitemap"), label: "HTML Sitemap", sub: "Wide browse view" },
  ]);
}

async function main() {
  if (!SITE_URL) throw new Error("SITE_URL is required");
  if (!SOURCE_SITEMAP_URL) throw new Error("SOURCE_SITEMAP_URL is required");

  resetDiscoveryOutput();

  console.log("Fetching sitemap...");
  console.log(`Fetching: ${SOURCE_SITEMAP_URL}`);

  let allEntries = [];
  const visited = new Set();

  try {
    allEntries = await collectEntriesFromSitemap(SOURCE_SITEMAP_URL, visited);
  } catch (err) {
    console.error(`Failed to fetch sitemap: ${SOURCE_SITEMAP_URL}`, err.message);
    throw err;
  }

  let entries = sanitizeEntries(allEntries);
  entries = uniqueByUrl(entries).map(annotateEntry);
  entries = sortNewestFirst(entries);

  if (!entries.length) throw new Error("No valid URLs found in sitemap");

  const latestEntries = entries.slice(0, MAX_LATEST);
  const todayRaw = filterToday(entries);
  const weekRaw = filterThisWeek(entries);

  const todayEntries = (todayRaw.length ? todayRaw : entries).slice(0, MAX_TODAY);
  const weekEntries = (weekRaw.length ? weekRaw : entries).slice(0, MAX_WEEK);
  const htmlEntries = entries.slice(0, MAX_HTML);
  const feedEntries = entries.slice(0, MAX_FEED);

  const latestChunks = chunkEntries(entries, PAGINATED_LATEST_PAGE_SIZE, MAX_PAGINATED_LATEST_PAGES);
  const todayChunks = chunkEntries(
    todayRaw.length ? todayRaw : entries,
    PAGINATED_TODAY_PAGE_SIZE,
    MAX_PAGINATED_TODAY_PAGES
  );
  const runwayChunks = chunkEntries(entries, RUNWAY_PAGE_SIZE, MAX_RUNWAY_PAGES);

  const topicGroups = buildTopicGroups(entries);
  const platformGroups = buildPlatformGroups(entries);
  const clusterGroups = buildClusterGroups(entries);
  const hybridGroups = buildHybridGroups(entries, platformGroups, topicGroups);

  const todayTopicGroups = buildTopicGroups(todayRaw.length ? todayRaw : todayEntries);
  const latestPlatformGroups = buildPlatformGroups(latestEntries);

  writeDiscoveryPage(
    "",
    {
      title: "Scam Detection Discovery Hub",
      intro:
        "Central discovery page for recent scam check URLs, grouped topics, platform collections, random discovery surfaces, and revisit pages designed to support crawl depth and return visits.",
      items: linksToItems([
        { href: joinDiscoveryUrl("latest"), label: "Latest Pages", sub: "Newest discovery URLs" },
        { href: joinDiscoveryUrl("today"), label: "Today Pages", sub: "Fresh discovery URLs" },
        { href: joinDiscoveryUrl("this-week"), label: "This Week", sub: "Recent 7-day discovery view" },
        { href: joinDiscoveryUrl("html-sitemap"), label: "HTML Sitemap", sub: "Wide browse view" },
        { href: joinDiscoveryUrl("topics"), label: "All Topics", sub: "Grouped by scam theme" },
        { href: joinDiscoveryUrl("platforms"), label: "All Platforms", sub: "Grouped by brand or service" },
        { href: joinDiscoveryUrl("clusters"), label: "Discovery Clusters", sub: "Grouped by repeated URL patterns" },
        { href: joinDiscoveryUrl("hybrids"), label: "Hybrid Discovery Pages", sub: "Combined platform plus topic pages" },
        { href: joinDiscoveryUrl("runway"), label: "Runway Pages", sub: "Paginated crawl runway" },
        { href: joinDiscoveryUrl("random"), label: "Random Discovery 1", sub: "Shuffled alternate path" },
        { href: joinDiscoveryUrl("random-2"), label: "Random Discovery 2", sub: "More shuffled discovery" },
        { href: joinDiscoveryUrl("random-3"), label: "Random Discovery 3", sub: "Third random surface" },
        { href: joinDiscoveryUrl("revisit"), label: "Revisit Pages", sub: "Resurfaced older URLs" },
      ]),
      extraSections: [
        buildRelatedSection({
          title: "Discovery indexes",
          intro: "Use these grouped index pages to move through discovery types faster.",
          links: [
            { href: joinDiscoveryUrl("topics"), label: "Topic Index", sub: `${topicGroups.length} topic groups` },
            {
              href: joinDiscoveryUrl("platforms"),
              label: "Platform Index",
              sub: `${platformGroups.length} platform groups`,
            },
            {
              href: joinDiscoveryUrl("clusters"),
              label: "Cluster Index",
              sub: `${clusterGroups.length} cluster groups`,
            },
            {
              href: joinDiscoveryUrl("hybrids"),
              label: "Hybrid Index",
              sub: `${hybridGroups.length} hybrid pages`,
            },
          ],
        }),
      ],
      kind: "hub",
    },
    "core"
  );

  writeDiscoveryPage(
    "latest",
    {
      title: "Latest Pages",
      intro: "Newest URLs discovered from the sitemap.",
      items: entriesToListItems(latestEntries),
      extraSections: [
        buildPagerSection("latest", latestChunks.length, 1, "Latest"),
        buildRelatedSection({
          title: "Latest grouped views",
          intro: "Move from newest URLs into grouped discovery pages built from the same source set.",
          links: [
            {
              href: joinDiscoveryUrl("latest/platforms"),
              label: "Latest By Platform",
              sub: "Fresh platform groupings",
            },
            { href: joinDiscoveryUrl("topics"), label: "All Topics", sub: "Compare topic collections" },
            {
              href: joinDiscoveryUrl("platforms"),
              label: "All Platforms",
              sub: "Compare platform collections",
            },
            { href: joinDiscoveryUrl("runway"), label: "Runway Pages", sub: "Go deeper into newer URLs" },
          ],
        }),
      ],
      kind: "latest",
    },
    "core"
  );

  latestChunks.slice(1).forEach((chunk, index) => {
    const pageNumber = index + 2;
    writeDiscoveryPage(
      `latest/page-${pageNumber}`,
      {
        title: `Latest Pages - Page ${pageNumber}`,
        intro: "More recently discovered URLs from the sitemap.",
        items: entriesToListItems(chunk),
        extraSections: [buildPagerSection("latest", latestChunks.length, pageNumber, "Latest")],
        kind: "latest",
      },
      "core"
    );
  });

  writeDiscoveryPage(
    "today",
    {
      title: `Pages Added ${todayString()}`,
      intro: todayRaw.length
        ? "Today's URLs from the sitemap."
        : "Freshness timestamps were limited, so this page falls back to the newest available URLs.",
      items: entriesToListItems(todayEntries),
      extraSections: [
        buildPagerSection("today", todayChunks.length, 1, "Today"),
        buildRelatedSection({
          title: "Today grouped views",
          intro: "Move from fresh URLs into grouped topic and platform pages built from the freshest available set.",
          links: [
            { href: joinDiscoveryUrl("today/topics"), label: "Today By Topic", sub: "Fresh topic groupings" },
            { href: joinDiscoveryUrl("latest"), label: "Latest Pages", sub: "Newest overall URLs" },
            { href: joinDiscoveryUrl("this-week"), label: "This Week", sub: "Broader recent set" },
          ],
        }),
      ],
      kind: "today",
    },
    "core"
  );

  todayChunks.slice(1).forEach((chunk, index) => {
    const pageNumber = index + 2;
    writeDiscoveryPage(
      `today/page-${pageNumber}`,
      {
        title: `Pages Added ${todayString()} - Page ${pageNumber}`,
        intro: "More fresh discovery URLs from the newest available set.",
        items: entriesToListItems(chunk),
        extraSections: [buildPagerSection("today", todayChunks.length, pageNumber, "Today")],
        kind: "today",
      },
      "core"
    );
  });

  writeDiscoveryPage(
    "this-week",
    {
      title: "Pages This Week",
      intro: "Recent URLs from the sitemap over the last seven days.",
      items: entriesToListItems(weekEntries),
      extraSections: [
        buildRelatedSection({
          title: "Recent discovery paths",
          intro: "Expand from the weekly view into latest, today, and grouped discovery pages.",
          links: [
            { href: joinDiscoveryUrl("latest"), label: "Latest Pages", sub: "Newest overall view" },
            { href: joinDiscoveryUrl("today"), label: "Today Pages", sub: "Freshest day view" },
            { href: joinDiscoveryUrl("topics"), label: "Topic Index", sub: "Grouped by scam theme" },
            {
              href: joinDiscoveryUrl("platforms"),
              label: "Platform Index",
              sub: "Grouped by platform",
            },
          ],
        }),
      ],
      kind: "week",
    },
    "core"
  );

  writeDiscoveryPage(
    "html-sitemap",
    {
      title: "HTML Sitemap",
      intro: "Combined sitemap view.",
      items: entriesToListItems(htmlEntries),
      extraSections: [
        buildRelatedSection({
          title: "Broader discovery options",
          intro: "Use these pages to browse newer, grouped, or resurfaced URL sets.",
          links: [
            { href: joinDiscoveryUrl("feed"), label: "Discovery Feed", sub: "Fast recent scan" },
            { href: joinDiscoveryUrl("runway"), label: "Runway Pages", sub: "Paginated deep browse" },
            { href: joinDiscoveryUrl("revisit"), label: "Revisit Pages", sub: "Older URLs worth recrawling" },
          ],
        }),
      ],
      kind: "html",
    },
    "core"
  );

  writeDiscoveryPage(
    "feed",
    {
      title: "Discovery Feed",
      intro: "Fast moving discovery feed built from the freshest available scam check URLs.",
      items: entriesToListItems(feedEntries),
      extraSections: [
        buildRelatedSection({
          title: "Use the feed with",
          intro: "Pair the feed with wider pages and grouped discovery surfaces.",
          links: [
            { href: joinDiscoveryUrl("latest"), label: "Latest Pages", sub: "Newest overall set" },
            { href: joinDiscoveryUrl("today"), label: "Today Pages", sub: "Freshest day view" },
            { href: joinDiscoveryUrl("random"), label: "Random Discovery 1", sub: "Alternate crawl path" },
          ],
        }),
      ],
      kind: "feed",
    },
    "core"
  );

  if (runwayChunks.length) {
    writeDiscoveryPage(
      "runway",
      {
        title: "Runway Pages",
        intro: "Paginated runway pages created to push more scam check URLs into the discovery layer.",
        items: linksToItems(
          runwayChunks.map((chunk, index) => ({
            href:
              index === 0
                ? joinDiscoveryUrl("runway/page-1")
                : joinDiscoveryUrl(`runway/page-${index + 1}`),
            label: `Runway Page ${index + 1}`,
            sub: `${chunk.length} discovery URLs`,
          }))
        ),
        kind: "runway",
      },
      "explore"
    );

    runwayChunks.forEach((chunk, index) => {
      const pageNumber = index + 1;
      writeDiscoveryPage(
        `runway/page-${pageNumber}`,
        {
          title: `Runway Page ${pageNumber}`,
          intro: "Additional scam check URLs exposed through a deeper runway discovery path.",
          items: entriesToListItems(chunk),
          extraSections: [buildPagerSection("runway", runwayChunks.length, pageNumber, "Runway")],
          kind: "runway",
        },
        "explore"
      );
    });
  }

  const randomSets = [
    { path: "random", title: "Random Discovery 1" },
    { path: "random-2", title: "Random Discovery 2" },
    { path: "random-3", title: "Random Discovery 3" },
  ];

  randomSets.forEach((set, index) => {
    const items = entriesToListItems(pickRandomEntries(entries, RANDOM_PAGE_SIZE));
    if (!hasItems(items)) return;

    writeDiscoveryPage(
      set.path,
      {
        title: set.title,
        intro: "Shuffled discovery URLs for alternate crawl paths and broader internal recirculation.",
        items,
        extraSections: [
          buildRelatedSection({
            title: "More shuffled discovery",
            intro: "Move between random discovery pages and deeper resurfacing pages.",
            links: [
              { href: joinDiscoveryUrl("random"), label: "Random Discovery 1", sub: "Primary shuffled set" },
              {
                href: joinDiscoveryUrl("random-2"),
                label: "Random Discovery 2",
                sub: "Secondary shuffled set",
              },
              { href: joinDiscoveryUrl("random-3"), label: "Random Discovery 3", sub: "Third shuffled set" },
              { href: joinDiscoveryUrl("revisit"), label: "Revisit Pages", sub: "Older resurfaced URLs" },
            ].filter((_, linkIndex) => linkIndex !== index),
          }),
        ],
        kind: "random",
      },
      "explore"
    );
  });

  const revisitItems = entriesToListItems(
    entries.slice(REVISIT_START_OFFSET, REVISIT_END_OFFSET).slice(0, REVISIT_PAGE_SIZE)
  );
  if (hasItems(revisitItems)) {
    writeDiscoveryPage(
      "revisit",
      {
        title: "Revisit Pages",
        intro: "Resurfaced older URLs from deeper in your sitemap set.",
        items: revisitItems,
        extraSections: [
          buildRelatedSection({
            title: "Revisit with",
            intro: "Pair resurfaced URLs with fresh discovery pages to strengthen crawl loops.",
            links: [
              { href: joinDiscoveryUrl("latest"), label: "Latest Pages", sub: "Newest page set" },
              { href: joinDiscoveryUrl("random"), label: "Random Discovery 1", sub: "Alternate discovery path" },
              { href: joinDiscoveryUrl("runway"), label: "Runway Pages", sub: "Deeper paginated path" },
            ],
          }),
        ],
        kind: "revisit",
      },
      "explore"
    );
  }

  const topicIndexItems = linksToItems(buildGroupPageLinks("topics", topicGroups));
  writeDiscoveryPage(
    "topics",
    {
      title: "All Discovery Topics",
      intro: "Topic index built from repeated scam themes found across your sitemap URLs.",
      items: hasItems(topicIndexItems) ? topicIndexItems : createFallbackIndexItems(),
      extraSections: [
        buildRelatedSection({
          title: "Fresh topic surfaces",
          intro: "Use today and latest grouped views to enter topic pages from a freshness-first angle.",
          links: [
            {
              href: joinDiscoveryUrl("today/topics"),
              label: "Today By Topic",
              sub: `${todayTopicGroups.length} fresh topic groups`,
            },
            { href: joinDiscoveryUrl("latest"), label: "Latest Pages", sub: "Newest discovery URLs" },
          ],
        }),
      ],
      kind: "topics",
    },
    "topics"
  );

  topicGroups.forEach((group) => {
    if (group.entries.length < MIN_TOPIC_SIZE) return;

    writeDiscoveryPage(
      `topics/${group.slug}`,
      {
        title: group.title,
        intro: `Focused discovery page for ${group.title.toLowerCase()} built from repeated URL patterns across your sitemap.`,
        items: entriesToListItems(group.entries),
        extraSections: [
          buildRelatedSection({
            title: "More topic discovery",
            intro: "Compare related grouped discovery pages and freshness views.",
            links: [
              { href: joinDiscoveryUrl("topics"), label: "Topic Index", sub: "All topic pages" },
              { href: joinDiscoveryUrl("today/topics"), label: "Today By Topic", sub: "Fresh topic view" },
              { href: joinDiscoveryUrl("latest"), label: "Latest Pages", sub: "Newest overall pages" },
            ],
          }),
        ],
        kind: "topic-child",
      },
      "topics"
    );
  });

  const todayTopicIndexItems = linksToItems(buildGroupPageLinks("topics", todayTopicGroups));
  writeDiscoveryPage(
    "today/topics",
    {
      title: "Today By Topic",
      intro: "Fresh topic groupings built from the newest available discovery URLs.",
      items: hasItems(todayTopicIndexItems) ? todayTopicIndexItems : createFallbackIndexItems(),
      kind: "topics",
    },
    "topics"
  );

  const platformIndexItems = linksToItems(buildGroupPageLinks("platforms", platformGroups));
  writeDiscoveryPage(
    "platforms",
    {
      title: "All Discovery Platforms",
      intro: "Platform index built from repeated brands and services found across your sitemap URLs.",
      items: hasItems(platformIndexItems) ? platformIndexItems : createFallbackIndexItems(),
      extraSections: [
        buildRelatedSection({
          title: "Fresh platform surfaces",
          intro: "Use freshness-first grouped views to enter platform discovery pages from recent URL sets.",
          links: [
            {
              href: joinDiscoveryUrl("latest/platforms"),
              label: "Latest By Platform",
              sub: `${latestPlatformGroups.length} fresh platform groups`,
            },
            { href: joinDiscoveryUrl("latest"), label: "Latest Pages", sub: "Newest discovery URLs" },
          ],
        }),
      ],
      kind: "platforms",
    },
    "platforms"
  );

  platformGroups.forEach((group) => {
    if (group.entries.length < MIN_PLATFORM_SIZE) return;

    writeDiscoveryPage(
      `platforms/${group.slug}`,
      {
        title: `${group.title} Scam Checks`,
        intro: `Focused discovery page for ${group.title} scam check URLs and related suspicious message patterns.`,
        items: entriesToListItems(group.entries),
        extraSections: [
          buildRelatedSection({
            title: "More platform discovery",
            intro: "Compare related platform pages and broader grouped discovery hubs.",
            links: [
              { href: joinDiscoveryUrl("platforms"), label: "Platform Index", sub: "All platform pages" },
              {
                href: joinDiscoveryUrl("latest/platforms"),
                label: "Latest By Platform",
                sub: "Fresh platform groupings",
              },
              {
                href: joinDiscoveryUrl("hybrids"),
                label: "Hybrid Discovery Pages",
                sub: "Combined platform plus topic pages",
              },
            ],
          }),
        ],
        kind: "platform-child",
      },
      "platforms"
    );
  });

  const latestPlatformIndexItems = linksToItems(buildGroupPageLinks("platforms", latestPlatformGroups));
  writeDiscoveryPage(
    "latest/platforms",
    {
      title: "Latest By Platform",
      intro: "Fresh platform groupings based on the newest available discovery URLs.",
      items: hasItems(latestPlatformIndexItems) ? latestPlatformIndexItems : createFallbackIndexItems(),
      kind: "platforms",
    },
    "platforms"
  );

  const clusterIndexItems = linksToItems(
    clusterGroups.map((group) => ({
      href: joinDiscoveryUrl(`clusters/${group.slug}`),
      label: group.title,
      sub: `${group.entries.length} clustered URLs`,
    }))
  );
  writeDiscoveryPage(
    "clusters",
    {
      title: "Discovery Clusters",
      intro: "Cluster index built from repeated URL tokens discovered across your sitemap.",
      items: hasItems(clusterIndexItems) ? clusterIndexItems : createFallbackIndexItems(),
      kind: "clusters",
    },
    "clusters"
  );

  clusterGroups.forEach((group) => {
    if (group.entries.length < MIN_CLUSTER_SIZE) return;

    writeDiscoveryPage(
      `clusters/${group.slug}`,
      {
        title: group.title,
        intro: `Repeated pattern cluster page built from the token "${group.rawToken}" across your sitemap URLs.`,
        items: entriesToListItems(group.entries),
        extraSections: [
          buildRelatedSection({
            title: "More cluster discovery",
            intro: "Move from repeated token clusters into broader topic, platform, and hybrid pages.",
            links: [
              { href: joinDiscoveryUrl("clusters"), label: "Cluster Index", sub: "All cluster pages" },
              { href: joinDiscoveryUrl("topics"), label: "Topic Index", sub: "Thematic groupings" },
              { href: joinDiscoveryUrl("platforms"), label: "Platform Index", sub: "Brand groupings" },
            ],
          }),
        ],
        kind: "cluster-child",
      },
      "clusters"
    );
  });

  const hybridIndexItems = linksToItems(
    hybridGroups.map((group) => ({
      href: joinDiscoveryUrl(`hybrids/${group.slug}`),
      label: group.title,
      sub: `${group.entries.length} hybrid URLs`,
    }))
  );
  writeDiscoveryPage(
    "hybrids",
    {
      title: "Hybrid Discovery Pages",
      intro: "High-intent hybrid pages combining platforms with repeated scam topics.",
      items: hasItems(hybridIndexItems) ? hybridIndexItems : createFallbackIndexItems(),
      kind: "hybrids",
    },
    "hybrids"
  );

  hybridGroups.forEach((group) => {
    if (group.entries.length < MIN_HYBRID_SIZE) return;

    writeDiscoveryPage(
      `hybrids/${group.slug}`,
      {
        title: group.title,
        intro: `Focused hybrid discovery page combining ${group.platformSlug.replace(/-/g, " ")} with ${group.topicSlug.replace(/-/g, " ")} patterns.`,
        items: entriesToListItems(group.entries),
        extraSections: [
          buildRelatedSection({
            title: "More hybrid discovery",
            intro: "Use platform and topic indexes to move into adjacent high-intent discovery pages.",
            links: [
              { href: joinDiscoveryUrl("hybrids"), label: "Hybrid Index", sub: "All hybrid pages" },
              {
                href: joinDiscoveryUrl(`platforms/${group.platformSlug}`),
                label: `${titleCaseFromSlug(group.platformSlug)} Platform Page`,
                sub: "Platform-specific discovery",
              },
              {
                href: joinDiscoveryUrl(`topics/${group.topicSlug}`),
                label: `${titleCaseFromSlug(group.topicSlug)} Topic Page`,
                sub: "Topic-specific discovery",
              },
            ],
          }),
        ],
        kind: "hybrid-child",
      },
      "hybrids"
    );
  });

  writeSegmentedDiscoverySitemaps();

  console.log("Discovery layer built successfully.");
  console.log(`Total source URLs: ${entries.length}`);
  console.log(`Generated discovery pages: ${generatedPages.length}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});