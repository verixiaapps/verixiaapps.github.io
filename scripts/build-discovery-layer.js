import fs from "fs";
import path from "path";
import https from "https";

const SITE_URL = (process.env.SITE_URL || "").replace(/\/+$/, "");
const SOURCE_SITEMAP_URL = process.env.SOURCE_SITEMAP_URL;
const SECONDARY_SITEMAP_URL = process.env.SECONDARY_SITEMAP_URL;
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
    ${links.map((item) => `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`).join("\n")}
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
      ${items.map((item) => `<li><a href="${htmlEscape(item.href)}">${htmlEscape(item.label)}</a></li>`).join("\n")}
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
${churnedUrls.map((u) => `  <url><loc>${escapeXml(u)}</loc><lastmod>${escapeXml(nowISO())}</lastmod></url>`).join("\n")}
</urlset>`;
}

async function main() {
  if (!SITE_URL) throw new Error("SITE_URL is required");
  if (!SOURCE_SITEMAP_URL) throw new Error("SOURCE_SITEMAP_URL is required");

  console.log("Fetching sitemaps...");

  const sitemapUrls = [SOURCE_SITEMAP_URL];
  if (SECONDARY_SITEMAP_URL) sitemapUrls.push(SECONDARY_SITEMAP_URL);

  let allEntries = [];

  for (const sitemapUrl of sitemapUrls) {
    try {
      console.log(`Fetching: ${sitemapUrl}`);
      const xml = await fetchText(sitemapUrl);
      const parsed = parseSitemapEntries(xml);
      allEntries.push(...parsed);
    } catch (err) {
      console.error(`Failed to fetch sitemap: ${sitemapUrl}`, err.message);
    }
  }

  const entries = uniqueByUrl(sortNewestFirst(allEntries));
  if (!entries.length) throw new Error("No URLs found in any sitemap");

  // rest unchanged
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});