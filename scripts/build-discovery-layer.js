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

function decodeXml(value) {
  return String(value)
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, "&");
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

function sortNewestFirst(entries) {
  return [...entries].sort((a, b) => {
    const aTime = toTimestamp(a.lastmod);
    const bTime = toTimestamp(b.lastmod);

    if (aTime !== bTime) return bTime - aTime;
    return b.url.localeCompare(a.url);
  });
}

function toTimestamp(value) {
  if (!value) return 0;
  const t = Date.parse(value);
  return Number.isNaN(t) ? 0 : t;
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
        "x ",
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

function groupByTopics(entries) {
  const grouped = new Map();

  for (const entry of entries) {
    const topics = inferTopics(entry.url);

    for (const topic of topics) {
      if (!grouped.has(topic.slug)) {
        grouped.set(topic.slug, {
          slug: topic.slug,
          title: topic.title,
          entries: [],
        });
      }
      grouped.get(topic.slug).entries.push(entry);
    }
  }

  return [...grouped.values()]
    .map((group) => ({
      ...group,
      entries: uniqueByUrl(sortNewestFirst(group.entries)),
    }))
    .sort((a, b) => b.entries.length - a.entries.length || a.title.localeCompare(b.title));
}

function pageShell({ title, intro = "", items = [], extraSections = [] }) {
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
    ${extraSections.join("\n")}
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
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
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

function joinSiteUrl(relativePath) {
  return `${SITE_URL}/${relativePath.replace(/^\/+/, "")}`;
}

async function main() {
  if (!SITE_URL) {
    throw new Error("SITE_URL is required");
  }

  if (!SOURCE_SITEMAP_URL) {
    throw new Error("SOURCE_SITEMAP_URL is required");
  }

  console.log("Fetching main sitemap...");
  const xml = await fetchText(SOURCE_SITEMAP_URL);

  const entries = uniqueByUrl(sortNewestFirst(parseSitemapEntries(xml)));

  if (!entries.length) {
    throw new Error("No URLs found in sitemap");
  }

  const latestEntries = entries.slice(0, MAX_LATEST);
  const todayEntries = filterToday(entries).slice(0, MAX_TODAY);
  const weekEntries = filterThisWeek(entries).slice(0, MAX_WEEK);
  const htmlEntries = entries.slice(0, MAX_HTML);
  const feedEntries = entries.slice(0, MAX_FEED);

  const topicGroups = groupByTopics(entries).filter((group) => group.entries.length > 0);
  const topTopicGroups = topicGroups.slice(0, 10);

  writeFile(
    path.join(DISCOVERY_DIR, "latest/index.html"),
    pageShell({
      title: "Latest Pages",
      intro: "Newest URLs discovered from the main sitemap.",
      items: entriesToListItems(latestEntries),
    })
  );

  writeFile(
    path.join(DISCOVERY_DIR, "today/index.html"),
    pageShell({
      title: `Pages Added ${todayString()}`,
      intro: "URLs with today's lastmod date from the main sitemap.",
      items: entriesToListItems(todayEntries),
    })
  );

  writeFile(
    path.join(DISCOVERY_DIR, "this-week/index.html"),
    pageShell({
      title: "Pages This Week",
      intro: "URLs updated in the last 7 days from the main sitemap.",
      items: entriesToListItems(weekEntries),
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

  const clusterIndexItems = topTopicGroups.map((group) => ({
    href: joinSiteUrl(`discovery/clusters/${group.slug}/`),
    label: `${group.title} (${group.entries.length})`,
  }));

  writeFile(
    path.join(DISCOVERY_DIR, "clusters/index.html"),
    pageShell({
      title: "Discovery Clusters",
      intro: "Topic-organized discovery pages built from sitemap URL patterns.",
      items: clusterIndexItems,
    })
  );

  for (const group of topTopicGroups) {
    writeFile(
      path.join(DISCOVERY_DIR, `clusters/${group.slug}/index.html`),
      pageShell({
        title: group.title,
        intro: `Topic cluster generated from sitemap URLs: ${group.title}.`,
        items: entriesToListItems(group.entries.slice(0, 250)),
      })
    );
  }

  const discoveryUrls = [
    joinSiteUrl("discovery/latest/"),
    joinSiteUrl("discovery/today/"),
    joinSiteUrl("discovery/this-week/"),
    joinSiteUrl("discovery/html-sitemap/"),
    joinSiteUrl("discovery/feeds/latest.xml"),
    joinSiteUrl("discovery/clusters/"),
    ...topTopicGroups.map((group) => joinSiteUrl(`discovery/clusters/${group.slug}/`)),
  ];

  writeFile(DISCOVERY_SITEMAP_PATH, buildXmlSitemap(discoveryUrls));

  console.log("Discovery layer built successfully.");
  console.log(`Total source URLs: ${entries.length}`);
  console.log(`Cluster pages created: ${topTopicGroups.length}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});