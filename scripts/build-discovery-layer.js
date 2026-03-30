import fs from "fs";
import path from "path";
import https from "https";

const SITE_URL = (process.env.SITE_URL || "").replace(/\/+$/, "");
const SOURCE_SITEMAP_URL = process.env.SOURCE_SITEMAP_URL;
const DISCOVERY_DIR = process.env.DISCOVERY_DIR || "discovery";
const DISCOVERY_SITEMAP_PATH = process.env.DISCOVERY_SITEMAP_PATH || "discovery-sitemap.xml";

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

function fetchText(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, (res) => {
        if (res.statusCode && res.statusCode >= 400) {
          reject(new Error(`Failed to fetch ${url} - status ${res.statusCode}`));
          return;
        }

        let data = "";
        res.on("data", (chunk) => {
          data += chunk;
        });
        res.on("end", () => resolve(data));
      })
      .on("error", reject);
  });
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
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
  return escapeXml(value);
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
  const urlBlocks = [...xml.matchAll(/<url>([\s\S]*?)<\/url>/g)];

  if (urlBlocks.length === 0) {
    const locMatches = [...xml.matchAll(/<loc>(.*?)<\/loc>/g)];
    return locMatches.map((m) => ({
      url: decodeXml(m[1].trim()),
      lastmod: null,
    }));
  }

  return urlBlocks
    .map((match) => {
      const block = match[1];
      const locMatch = block.match(/<loc>(.*?)<\/loc>/);
      if (!locMatch) return null;

      const lastmodMatch = block.match(/<lastmod>(.*?)<\/lastmod>/);

      return {
        url: decodeXml(locMatch[1].trim()),
        lastmod: lastmodMatch ? decodeXml(lastmodMatch[1].trim()) : null,
      };
    })
    .filter(Boolean);
}

function uniqueByUrl(entries) {
  const seen = new Set();
  const out = [];

  for (const entry of entries) {
    if (!entry || !entry.url) continue;
    if (seen.has(entry.url)) continue;
    seen.add(entry.url);
    out.push(entry);
  }

  return out;
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
    return b.url.localeCompare(a.url);
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
    return new URL(url).pathname.toLowerCase();
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
  return `${SITE_URL}/${relativePath.replace(/^\/+/, "")}`;
}

function slugify(value) {
  return String(value)
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "general";
}

function titleCaseFromSlug(slug) {
  return slug
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
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

function globalRelatedDiscoverySection() {
  const links = [
    { href: joinSiteUrl("discovery/latest/"), label: "Latest Pages" },
    { href: joinSiteUrl("discovery/today/"), label: "Today Pages" },
    { href: joinSiteUrl("discovery/this-week/"), label: "This Week" },
    { href: joinSiteUrl("discovery/html-sitemap/"), label: "HTML Sitemap" },
    { href: joinSiteUrl("discovery/clusters/"), label: "Discovery Clusters" },
    { href: joinSiteUrl("discovery/latest/platforms/"), label: "Latest By Platform" },
    { href: joinSiteUrl("discovery/today/topics/"), label: "Today By Topic" },
    { href: joinSiteUrl("discovery/runway/"), label: "Runway Pages" },
    { href: joinSiteUrl("discovery/hybrids/"), label: "Hybrid Discovery Pages" },
    { href: joinSiteUrl("discovery/random/"), label: "Random Discovery 1" },
    { href: joinSiteUrl("discovery/random-2/"), label: "Random Discovery 2" },
    { href: joinSiteUrl("discovery/random-3/"), label: "Random Discovery 3" },
    { href: joinSiteUrl("discovery/revisit/"), label: "Revisit Pages" },
  ];

  return `<section>
  <h2>Related Discovery Pages</h2>
  <ul>
    ${links
      .map(
        (item) =>
          `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`
      )
      .join("\n")}
  </ul>
</section>`;
}

function pageShell({ title, intro = "", items = [], extraSections = [] }) {
  const sections = [...extraSections, globalRelatedDiscoverySection()].filter(Boolean);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${htmlEscape(title)}</title>
</head>
<body>
  <main>
    <h1>${htmlEscape(title)}</h1>
    ${intro ? `<p>${htmlEscape(intro)}</p>` : ""}
    <ul>
      ${items
        .map(
          (item) =>
            `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`
        )
        .join("\n")}
    </ul>
    ${sections.join("\n")}
  </main>
</body>
</html>`;
}

function entriesToListItems(entries) {
  return entries.map((entry) => ({
    href: entry.url,
    label: entry.url,
  }));
}

function buildXmlSitemap(urls) {
  const churnedUrls = shuffle(uniqueStrings(urls));

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${churnedUrls
  .map(
    (u) => `  <url>
    <loc>${escapeXml(u)}</loc>
    <lastmod>${escapeXml(nowISO())}</lastmod>
  </url>`
  )
  .join("\n")}
</urlset>`;
}

function buildFeed(entries) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Latest URLs</title>
    <link>${escapeXml(SITE_URL)}</link>
    <description>Latest generated URLs</description>
    ${entries
      .map(
        (entry) => `    <item>
      <title>${escapeXml(entry.url)}</title>
      <link>${escapeXml(entry.url)}</link>
      <pubDate>${escapeXml(
        entry.lastmod ? new Date(entry.lastmod).toUTCString() : new Date().toUTCString()
      )}</pubDate>
    </item>`
      )
      .join("\n")}
  </channel>
</rss>`;
}

function inferTopics(url) {
  const pathname = getPathname(url);
  const normalized = pathname.replace(/[-_/]+/g, " ");

  const topics = [];

  const topicRules = [
    {
      slug: "payment-scams",
      title: "Payment Scams",
      keywords: [
        "zelle",
        "paypal",
        "venmo",
        "cash app",
        "cashapp",
        "apple pay",
        "google pay",
        "wire transfer",
        "bank transfer",
        "invoice",
        "payment",
        "refund",
        "chargeback",
        "billing",
      ],
    },
    {
      slug: "job-scams",
      title: "Job Scams",
      keywords: [
        "job",
        "career",
        "recruiter",
        "recruitment",
        "employment",
        "interview",
        "hiring",
        "offer letter",
        "remote work",
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
        "wallet",
        "metamask",
        "coinbase",
        "binance",
        "usdt",
        "solana",
        "token",
        "blockchain",
        "defi",
      ],
    },
    {
      slug: "website-scams",
      title: "Website Scams",
      keywords: [
        "website",
        "site",
        "domain",
        "store",
        "shop",
        "checkout",
        "web",
      ],
    },
    {
      slug: "email-scams",
      title: "Email Scams",
      keywords: [
        "email",
        "gmail",
        "outlook",
        "message",
        "mail",
        "inbox",
        "phishing email",
      ],
    },
    {
      slug: "text-scams",
      title: "Text Scams",
      keywords: [
        "text",
        "sms",
        "imessage",
        "message",
        "verification code",
        "otp",
        "2fa",
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
        "tiktok",
        "snapchat",
        "discord",
        "twitter",
        "social media",
      ],
    },
    {
      slug: "delivery-scams",
      title: "Delivery Scams",
      keywords: [
        "usps",
        "fedex",
        "ups",
        "delivery",
        "package",
        "shipment",
        "tracking",
      ],
    },
    {
      slug: "banking-scams",
      title: "Banking Scams",
      keywords: [
        "bank",
        "chase",
        "wells fargo",
        "bank of america",
        "citibank",
        "debit",
        "credit card",
        "account alert",
        "suspicious login",
      ],
    },
    {
      slug: "impersonation-scams",
      title: "Impersonation Scams",
      keywords: [
        "support",
        "customer service",
        "help desk",
        "impersonation",
        "pretending",
        "fake representative",
        "account team",
      ],
    },
  ];

  for (const rule of topicRules) {
    if (rule.keywords.some((keyword) => normalized.includes(keyword))) {
      topics.push({
        slug: rule.slug,
        title: rule.title,
      });
    }
  }

  if (topics.length === 0) {
    const segments = getPathSegments(url);
    if (segments.length > 0) {
      topics.push({
        slug: "general",
        title: "General",
      });
    }
  }

  return topics;
}

function inferPlatforms(url) {
  const pathname = getPathname(url);
  const normalized = pathname.replace(/[-_/]+/g, " ");
  const found = [];

  const platformRules = [
    { slug: "zelle", title: "Zelle", keywords: ["zelle"] },
    { slug: "paypal", title: "PayPal", keywords: ["paypal"] },
    { slug: "venmo", title: "Venmo", keywords: ["venmo"] },
    { slug: "cash-app", title: "Cash App", keywords: ["cash app", "cashapp"] },
    { slug: "whatsapp", title: "WhatsApp", keywords: ["whatsapp"] },
    { slug: "telegram", title: "Telegram", keywords: ["telegram"] },
    { slug: "tiktok", title: "TikTok", keywords: ["tiktok"] },
    { slug: "snapchat", title: "Snapchat", keywords: ["snapchat"] },
    { slug: "instagram", title: "Instagram", keywords: ["instagram"] },
    { slug: "facebook", title: "Facebook", keywords: ["facebook"] },
    { slug: "discord", title: "Discord", keywords: ["discord"] },
    { slug: "gmail", title: "Gmail", keywords: ["gmail"] },
    { slug: "outlook", title: "Outlook", keywords: ["outlook"] },
    { slug: "usps", title: "USPS", keywords: ["usps"] },
    { slug: "fedex", title: "FedEx", keywords: ["fedex"] },
    { slug: "ups", title: "UPS", keywords: ["ups"] },
    { slug: "coinbase", title: "Coinbase", keywords: ["coinbase"] },
    { slug: "binance", title: "Binance", keywords: ["binance"] },
    { slug: "metamask", title: "MetaMask", keywords: ["metamask"] },
    { slug: "apple-pay", title: "Apple Pay", keywords: ["apple pay"] },
    { slug: "google-pay", title: "Google Pay", keywords: ["google pay"] },
    { slug: "bank-of-america", title: "Bank of America", keywords: ["bank of america"] },
    { slug: "chase", title: "Chase", keywords: ["chase"] },
    { slug: "wells-fargo", title: "Wells Fargo", keywords: ["wells fargo"] },
  ];

  for (const rule of platformRules) {
    if (rule.keywords.some((keyword) => normalized.includes(keyword))) {
      found.push({
        slug: rule.slug,
        title: rule.title,
      });
    }
  }

  if (found.length > 0) {
    return found;
  }

  const segments = getPathSegments(url);
  if (segments.length >= 2) {
    const firstMeaningful = segments[1];
    if (firstMeaningful && !["scam-check-now", "discovery"].includes(firstMeaningful)) {
      return [
        {
          slug: slugify(firstMeaningful),
          title: titleCaseFromSlug(slugify(firstMeaningful)),
        },
      ];
    }
  }

  return [];
}

function groupEntries(entries, classifier) {
  const grouped = new Map();

  for (const entry of entries) {
    const labels = classifier(entry.url);
    for (const label of labels) {
      if (!grouped.has(label.slug)) {
        grouped.set(label.slug, {
          slug: label.slug,
          title: label.title,
          entries: [],
        });
      }
      grouped.get(label.slug).entries.push(entry);
    }
  }

  return [...grouped.values()]
    .map((group) => ({
      ...group,
      entries: uniqueByUrl(sortNewestFirst(group.entries)),
    }))
    .sort((a, b) => b.entries.length - a.entries.length || a.title.localeCompare(b.title));
}

function buildLinkedSection(title, basePath, groups) {
  const items = groups.map((group) => ({
    href: joinSiteUrl(`${basePath}/${group.slug}/`),
    label: `${group.title} (${group.entries.length})`,
  }));

  return `<section>
  <h2>${htmlEscape(title)}</h2>
  <ul>
    ${items
      .map(
        (item) =>
          `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`
      )
      .join("\n")}
  </ul>
</section>`;
}

function chunkEntries(entries, size, maxPages) {
  const pages = [];
  for (let i = 0; i < entries.length && pages.length < maxPages; i += size) {
    pages.push(entries.slice(i, i + size));
  }
  return pages;
}

function buildPaginationSection(title, basePath, pageCount) {
  if (pageCount <= 1) return "";
  const items = [];
  for (let i = 1; i <= pageCount; i += 1) {
    items.push({
      href: joinSiteUrl(`${basePath}/page-${i}/`),
      label: `Page ${i}`,
    });
  }

  return `<section>
  <h2>${htmlEscape(title)}</h2>
  <ul>
    ${items
      .map(
        (item) =>
          `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`
      )
      .join("\n")}
  </ul>
</section>`;
}

function findGroupBySlug(groups, slug) {
  return groups.find((group) => group.slug === slug) || null;
}

function buildCrossLinksForTopic(topicGroup, platformGroups) {
  const relatedPlatformLinks = platformGroups
    .filter((platformGroup) =>
      platformGroup.entries.some((entry) =>
        topicGroup.entries.some((topicEntry) => topicEntry.url === entry.url)
      )
    )
    .slice(0, 8)
    .map((group) => ({
      href: joinSiteUrl(`discovery/latest/${group.slug}/`),
      label: `${group.title} (${group.entries.length})`,
    }));

  if (!relatedPlatformLinks.length) return "";

  return `<section>
  <h2>Related Platforms</h2>
  <ul>
    ${relatedPlatformLinks
      .map(
        (item) =>
          `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`
      )
      .join("\n")}
  </ul>
</section>`;
}

function buildCrossLinksForPlatform(platformGroup, topicGroups) {
  const relatedTopicLinks = topicGroups
    .filter((topicGroup) =>
      topicGroup.entries.some((entry) =>
        platformGroup.entries.some((platformEntry) => platformEntry.url === entry.url)
      )
    )
    .slice(0, 8)
    .map((group) => ({
      href: joinSiteUrl(`discovery/clusters/${group.slug}/`),
      label: `${group.title} (${group.entries.length})`,
    }));

  if (!relatedTopicLinks.length) return "";

  return `<section>
  <h2>Related Topics</h2>
  <ul>
    ${relatedTopicLinks
      .map(
        (item) =>
          `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`
      )
      .join("\n")}
  </ul>
</section>`;
}

function buildHybridGroups(entries, topicGroups, platformGroups) {
  const hybrids = [];

  for (const topicGroup of topicGroups) {
    for (const platformGroup of platformGroups) {
      const sharedEntries = uniqueByUrl(
        sortNewestFirst(
          entries.filter(
            (entry) =>
              topicGroup.entries.some((t) => t.url === entry.url) &&
              platformGroup.entries.some((p) => p.url === entry.url)
          )
        )
      );

      if (!sharedEntries.length) continue;

      hybrids.push({
        topicSlug: topicGroup.slug,
        topicTitle: topicGroup.title,
        platformSlug: platformGroup.slug,
        platformTitle: platformGroup.title,
        slug: `${topicGroup.slug}/${platformGroup.slug}`,
        title: `${topicGroup.title} / ${platformGroup.title}`,
        entries: sharedEntries,
      });
    }
  }

  return hybrids
    .sort((a, b) => b.entries.length - a.entries.length || a.title.localeCompare(b.title))
    .slice(0, MAX_HYBRID_PAGES);
}

function buildRandomSection(title, baseFolder, entries) {
  writeFile(
    path.join(DISCOVERY_DIR, `${baseFolder}/index.html`),
    pageShell({
      title,
      intro: "Randomized crawl entry points built from the main sitemap.",
      items: entriesToListItems(entries),
      extraSections: [
        `<section>
  <h2>Why This Exists</h2>
  <p>These links rotate each run to create additional discovery paths for older and less frequently revisited URLs.</p>
</section>`,
      ],
    })
  );
}

async function main() {
  if (!SITE_URL) throw new Error("SITE_URL is required");
  if (!SOURCE_SITEMAP_URL) throw new Error("SOURCE_SITEMAP_URL is required");

  console.log("Fetching main sitemap...");
  const xml = await fetchText(SOURCE_SITEMAP_URL);

  const entries = uniqueByUrl(sortNewestFirst(parseSitemapEntries(xml)));
  if (!entries.length) throw new Error("No URLs found in sitemap");

  const latestEntries = entries.slice(0, MAX_LATEST);
  const todayEntries = filterToday(entries).slice(0, MAX_TODAY);
  const weekEntries = filterThisWeek(entries).slice(0, MAX_WEEK);
  const htmlEntries = entries.slice(0, MAX_HTML);
  const feedEntries = entries.slice(0, MAX_FEED);

  const topicGroupsAll = groupEntries(entries, inferTopics).filter((group) => group.entries.length > 0);
  const topicGroups = topicGroupsAll.slice(0, MAX_TOPIC_GROUPS);

  const platformGroupsAll = groupEntries(entries, inferPlatforms).filter((group) => group.entries.length > 0);
  const platformGroups = platformGroupsAll.slice(0, MAX_PLATFORM_GROUPS);

  const todayTopicGroups = groupEntries(filterToday(entries), inferTopics).filter((group) => group.entries.length > 0);
  const latestPlatformGroups = groupEntries(entries.slice(0, 1000), inferPlatforms).filter((group) => group.entries.length > 0);

  const runwayPages = chunkEntries(entries, RUNWAY_PAGE_SIZE, MAX_RUNWAY_PAGES);
  const paginatedLatestPages = chunkEntries(entries, PAGINATED_LATEST_PAGE_SIZE, MAX_PAGINATED_LATEST_PAGES);
  const paginatedTodayPages = chunkEntries(filterToday(entries), PAGINATED_TODAY_PAGE_SIZE, MAX_PAGINATED_TODAY_PAGES);

  const hybridGroups = buildHybridGroups(
    entries.slice(0, 2500),
    topicGroups,
    platformGroups
  );

  const randomEntries1 = pickRandomEntries(entries, RANDOM_PAGE_SIZE);
  const randomEntries2 = pickRandomEntries(entries, RANDOM_PAGE_SIZE);
  const randomEntries3 = pickRandomEntries(entries, RANDOM_PAGE_SIZE);

  const revisitPool = entries.slice(REVISIT_START_OFFSET, REVISIT_END_OFFSET);
  const revisitEntries = pickRandomEntries(revisitPool.length ? revisitPool : entries, REVISIT_PAGE_SIZE);

  writeFile(
    path.join(DISCOVERY_DIR, "latest/index.html"),
    pageShell({
      title: "Latest Pages",
      intro: "Newest URLs discovered from the main sitemap.",
      items: entriesToListItems(latestEntries),
      extraSections: [
        buildLinkedSection("Latest By Platform", "discovery/latest", latestPlatformGroups.slice(0, MAX_PLATFORM_GROUPS)),
        buildPaginationSection("Latest Pagination", "discovery/latest", paginatedLatestPages.length),
      ],
    })
  );

  writeFile(
    path.join(DISCOVERY_DIR, "today/index.html"),
    pageShell({
      title: `Pages Added ${todayString()}`,
      intro: "URLs with today's lastmod date from the main sitemap.",
      items: entriesToListItems(todayEntries),
      extraSections: [
        buildLinkedSection("Today By Topic", "discovery/today", todayTopicGroups.slice(0, MAX_TOPIC_GROUPS)),
        buildPaginationSection("Today Pagination", "discovery/today", paginatedTodayPages.length),
      ],
    })
  );

  writeFile(
    path.join(DISCOVERY_DIR, "this-week/index.html"),
    pageShell({
      title: "Pages This Week",
      intro: "URLs updated in the last 7 days from the main sitemap.",
      items: entriesToListItems(weekEntries),
      extraSections: [
        buildLinkedSection("Runway Pages", "discovery/runway", runwayPages.map((page, index) => ({
          slug: `page-${index + 1}`,
          title: `Runway Page ${index + 1}`,
          entries: page,
        }))),
      ],
    })
  );

  writeFile(
    path.join(DISCOVERY_DIR, "html-sitemap/index.html"),
    pageShell({
      title: "HTML Sitemap",
      intro: "Recently updated URLs from the main sitemap.",
      items: entriesToListItems(htmlEntries),
    })
  );

  writeFile(
    path.join(DISCOVERY_DIR, "feeds/latest.xml"),
    buildFeed(feedEntries)
  );

  writeFile(
    path.join(DISCOVERY_DIR, "clusters/index.html"),
    pageShell({
      title: "Discovery Clusters",
      intro: "Topic-organized discovery pages built from sitemap URL patterns.",
      items: topicGroups.map((group) => ({
        href: joinSiteUrl(`discovery/clusters/${group.slug}/`),
        label: `${group.title} (${group.entries.length})`,
      })),
      extraSections: [
        buildLinkedSection("Hybrid Discovery Pages", "discovery/hybrids", hybridGroups.map((group) => ({
          slug: group.slug,
          title: group.title,
          entries: group.entries,
        }))),
      ],
    })
  );

  for (const group of topicGroups) {
    writeFile(
      path.join(DISCOVERY_DIR, `clusters/${group.slug}/index.html`),
      pageShell({
        title: group.title,
        intro: `Topic cluster generated from sitemap URLs: ${group.title}.`,
        items: entriesToListItems(group.entries.slice(0, MAX_CLUSTER_PAGE_URLS)),
        extraSections: [
          buildCrossLinksForTopic(group, latestPlatformGroups),
        ],
      })
    );
  }

  writeFile(
    path.join(DISCOVERY_DIR, "today/topics/index.html"),
    pageShell({
      title: "Today By Topic",
      intro: "Today's freshest URLs grouped by topic.",
      items: todayTopicGroups.slice(0, MAX_TOPIC_GROUPS).map((group) => ({
        href: joinSiteUrl(`discovery/today/${group.slug}/`),
        label: `${group.title} (${group.entries.length})`,
      })),
    })
  );

  for (const group of todayTopicGroups.slice(0, MAX_TOPIC_GROUPS)) {
    writeFile(
      path.join(DISCOVERY_DIR, `today/${group.slug}/index.html`),
      pageShell({
        title: `${group.title} Today`,
        intro: `Today's URLs grouped under ${group.title}.`,
        items: entriesToListItems(group.entries.slice(0, MAX_TOPIC_PAGE_URLS)),
        extraSections: [
          buildCrossLinksForTopic(group, latestPlatformGroups),
        ],
      })
    );
  }

  writeFile(
    path.join(DISCOVERY_DIR, "latest/platforms/index.html"),
    pageShell({
      title: "Latest By Platform",
      intro: "Newest URLs grouped by platform-level patterns.",
      items: latestPlatformGroups.slice(0, MAX_PLATFORM_GROUPS).map((group) => ({
        href: joinSiteUrl(`discovery/latest/${group.slug}/`),
        label: `${group.title} (${group.entries.length})`,
      })),
    })
  );

  for (const group of latestPlatformGroups.slice(0, MAX_PLATFORM_GROUPS)) {
    writeFile(
      path.join(DISCOVERY_DIR, `latest/${group.slug}/index.html`),
      pageShell({
        title: `${group.title} Latest`,
        intro: `Newest URLs grouped under ${group.title}.`,
        items: entriesToListItems(group.entries.slice(0, MAX_PLATFORM_PAGE_URLS)),
        extraSections: [
          buildCrossLinksForPlatform(group, topicGroups),
        ],
      })
    );
  }

  for (let i = 0; i < paginatedLatestPages.length; i += 1) {
    const pageNumber = i + 1;
    writeFile(
      path.join(DISCOVERY_DIR, `latest/page-${pageNumber}/index.html`),
      pageShell({
        title: `Latest Page ${pageNumber}`,
        intro: `Paginated latest URLs page ${pageNumber}.`,
        items: entriesToListItems(paginatedLatestPages[i]),
        extraSections: [
          buildPaginationSection("More Latest Pages", "discovery/latest", paginatedLatestPages.length),
        ],
      })
    );
  }

  for (let i = 0; i < paginatedTodayPages.length; i += 1) {
    const pageNumber = i + 1;
    writeFile(
      path.join(DISCOVERY_DIR, `today/page-${pageNumber}/index.html`),
      pageShell({
        title: `Today Page ${pageNumber}`,
        intro: `Paginated today's URLs page ${pageNumber}.`,
        items: entriesToListItems(paginatedTodayPages[i]),
        extraSections: [
          buildPaginationSection("More Today Pages", "discovery/today", paginatedTodayPages.length),
        ],
      })
    );
  }

  writeFile(
    path.join(DISCOVERY_DIR, "runway/index.html"),
    pageShell({
      title: "Runway Pages",
      intro: "Sequential crawl lanes through the newest sitemap URLs.",
      items: runwayPages.map((page, index) => ({
        href: joinSiteUrl(`discovery/runway/page-${index + 1}/`),
        label: `Runway Page ${index + 1} (${page.length})`,
      })),
    })
  );

  for (let i = 0; i < runwayPages.length; i += 1) {
    const pageNumber = i + 1;
    const extraLinks = [];

    if (pageNumber > 1) {
      extraLinks.push({
        href: joinSiteUrl(`discovery/runway/page-${pageNumber - 1}/`),
        label: `Previous Runway Page ${pageNumber - 1}`,
      });
    }

    if (pageNumber < runwayPages.length) {
      extraLinks.push({
        href: joinSiteUrl(`discovery/runway/page-${pageNumber + 1}/`),
        label: `Next Runway Page ${pageNumber + 1}`,
      });
    }

    extraLinks.push({
      href: joinSiteUrl("discovery/latest/"),
      label: "Back to Latest Pages",
    });

    extraLinks.push({
      href: joinSiteUrl("discovery/clusters/"),
      label: "Back to Discovery Clusters",
    });

    writeFile(
      path.join(DISCOVERY_DIR, `runway/page-${pageNumber}/index.html`),
      pageShell({
        title: `Runway Page ${pageNumber}`,
        intro: `Sequential runway page ${pageNumber} for deeper crawl continuity.`,
        items: entriesToListItems(runwayPages[i]),
        extraSections: [
          `<section>
  <h2>Navigation</h2>
  <ul>
    ${extraLinks
      .map(
        (item) =>
          `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`
      )
      .join("\n")}
  </ul>
</section>`,
        ],
      })
    );
  }

  writeFile(
    path.join(DISCOVERY_DIR, "hybrids/index.html"),
    pageShell({
      title: "Hybrid Discovery Pages",
      intro: "Topic and platform combinations built from sitemap URL overlap.",
      items: hybridGroups.map((group) => ({
        href: joinSiteUrl(`discovery/hybrids/${group.slug}/`),
        label: `${group.title} (${group.entries.length})`,
      })),
    })
  );

  for (const group of hybridGroups) {
    const relatedTopic = findGroupBySlug(topicGroups, group.topicSlug);
    const relatedPlatform = findGroupBySlug(latestPlatformGroups, group.platformSlug) || findGroupBySlug(platformGroups, group.platformSlug);

    const extraSections = [];

    if (relatedTopic || relatedPlatform) {
      const links = [];
      if (relatedTopic) {
        links.push({
          href: joinSiteUrl(`discovery/clusters/${relatedTopic.slug}/`),
          label: `${relatedTopic.title} Cluster`,
        });
      }
      if (relatedPlatform) {
        links.push({
          href: joinSiteUrl(`discovery/latest/${relatedPlatform.slug}/`),
          label: `${relatedPlatform.title} Latest`,
        });
      }

      extraSections.push(`<section>
  <h2>Related Discovery Pages</h2>
  <ul>
    ${links
      .map(
        (item) =>
          `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`
      )
      .join("\n")}
  </ul>
</section>`);
    }

    writeFile(
      path.join(DISCOVERY_DIR, `hybrids/${group.slug}/index.html`),
      pageShell({
        title: group.title,
        intro: `Hybrid discovery page for ${group.title}.`,
        items: entriesToListItems(group.entries.slice(0, MAX_HYBRID_PAGE_URLS)),
        extraSections,
      })
    );
  }

  buildRandomSection("Random Discovery 1", "random", randomEntries1);
  buildRandomSection("Random Discovery 2", "random-2", randomEntries2);
  buildRandomSection("Random Discovery 3", "random-3", randomEntries3);

  writeFile(
    path.join(DISCOVERY_DIR, "revisit/index.html"),
    pageShell({
      title: "Revisit Pages",
      intro: "Previously published URLs re-surfaced for fresh crawl attention.",
      items: entriesToListItems(revisitEntries),
      extraSections: [
        `<section>
  <h2>Selection Window</h2>
  <p>This page intentionally draws from older URLs rather than the newest batch.</p>
</section>`,
      ],
    })
  );

  const discoveryUrls = [
    joinSiteUrl("discovery/latest/"),
    joinSiteUrl("discovery/today/"),
    joinSiteUrl("discovery/this-week/"),
    joinSiteUrl("discovery/html-sitemap/"),
    joinSiteUrl("discovery/feeds/latest.xml"),
    joinSiteUrl("discovery/clusters/"),
    joinSiteUrl("discovery/today/topics/"),
    joinSiteUrl("discovery/latest/platforms/"),
    joinSiteUrl("discovery/runway/"),
    joinSiteUrl("discovery/hybrids/"),
    joinSiteUrl("discovery/random/"),
    joinSiteUrl("discovery/random-2/"),
    joinSiteUrl("discovery/random-3/"),
    joinSiteUrl("discovery/revisit/"),
    ...topicGroups.map((group) => joinSiteUrl(`discovery/clusters/${group.slug}/`)),
    ...todayTopicGroups.slice(0, MAX_TOPIC_GROUPS).map((group) => joinSiteUrl(`discovery/today/${group.slug}/`)),
    ...latestPlatformGroups.slice(0, MAX_PLATFORM_GROUPS).map((group) => joinSiteUrl(`discovery/latest/${group.slug}/`)),
    ...runwayPages.map((_, index) => joinSiteUrl(`discovery/runway/page-${index + 1}/`)),
    ...paginatedLatestPages.map((_, index) => joinSiteUrl(`discovery/latest/page-${index + 1}/`)),
    ...paginatedTodayPages.map((_, index) => joinSiteUrl(`discovery/today/page-${index + 1}/`)),
    ...hybridGroups.map((group) => joinSiteUrl(`discovery/hybrids/${group.slug}/`)),
  ];

  writeFile(DISCOVERY_SITEMAP_PATH, buildXmlSitemap(discoveryUrls));

  console.log("Discovery layer built successfully.");
  console.log(`Total source URLs: ${entries.length}`);
  console.log(`Topic clusters created: ${topicGroups.length}`);
  console.log(`Today-by-topic pages created: ${todayTopicGroups.slice(0, MAX_TOPIC_GROUPS).length}`);
  console.log(`Latest-by-platform pages created: ${latestPlatformGroups.slice(0, MAX_PLATFORM_GROUPS).length}`);
  console.log(`Runway pages created: ${runwayPages.length}`);
  console.log(`Paginated latest pages created: ${paginatedLatestPages.length}`);
  console.log(`Paginated today pages created: ${paginatedTodayPages.length}`);
  console.log(`Hybrid pages created: ${hybridGroups.length}`);
  console.log(`Random pages created: 3`);
  console.log(`Revisit page created: 1`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});