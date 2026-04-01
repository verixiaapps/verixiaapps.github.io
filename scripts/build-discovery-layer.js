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

function canonicalForDiscoveryTitle(title) {
  if (title.startsWith("Pages Added ")) return joinSiteUrl("discovery/today/");
  if (title === "Latest Pages") return joinSiteUrl("discovery/latest/");
  if (title === "Pages This Week") return joinSiteUrl("discovery/this-week/");
  if (title === "HTML Sitemap") return joinSiteUrl("discovery/html-sitemap/");
  return joinSiteUrl("discovery/");
}

function formatDisplayUrl(url) {
  return String(url)
    .replace(/^https?:\/\//, "")
    .replace(/\/+$/, "");
}

function getPageMeta(title) {
  if (title === "Latest Pages") {
    return {
      badge: "Updated continuously",
      kicker: "Latest discovery",
      eyebrow: "Newest pages added",
      intro:
        "Browse the newest scam check pages discovered across your sitemap sources. This is the fastest way to see fresh suspicious message topics, account warning pages, delivery scam pages, and payment alert coverage in one place.",
      statA: "Newest additions",
      statB: "Fast discovery",
      statC: "Built for reuse",
    };
  }

  if (title.startsWith("Pages Added ")) {
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

  if (title === "Pages This Week") {
    return {
      badge: "This week",
      kicker: "Weekly discovery",
      eyebrow: "Recent pages from this week",
      intro:
        "Browse scam check pages discovered over the last week. This gives you a broader view of recent scam topics, warning patterns, and message types without having to dig through individual sitemap files.",
      statA: "7-day coverage",
      statB: "Broader view",
      statC: "Recent patterns",
    };
  }

  if (title === "HTML Sitemap") {
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

  return {
    badge: "Discovery page",
    kicker: "Scam detection discovery",
    eyebrow: "Browse scam check pages",
    intro:
      "Use this discovery page to move through scam check topics quickly, compare suspicious message patterns, and reach a focused warning page before clicking links, replying, sending money, or sharing personal information.",
    statA: "Clear access",
    statB: "Structured navigation",
    statC: "Return visits",
  };
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

  return `
    <div class="related-card">
      <div class="related-top">
        <h3>Related discovery pages</h3>
        <p>Move through more scam discovery surfaces, recent pages, topic collections, and supporting navigation hubs.</p>
      </div>
      <ul class="related-grid">
        ${links
          .map(
            (item) => `
          <li>
            <a class="related-link" href="${htmlEscape(item.href)}">
              <span class="related-label">${htmlEscape(item.label)}</span>
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

function pageShell({ title, intro = "", items = [], extraSections = [] }) {
  const meta = getPageMeta(title);
  const sections = [...extraSections, globalRelatedDiscoverySection()].filter(Boolean);
  const canonicalUrl = canonicalForDiscoveryTitle(title);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>${htmlEscape(title)}</title>
  <meta name="description" content="${htmlEscape(intro || title)}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="${htmlEscape(canonicalUrl)}">

  <meta property="og:title" content="${htmlEscape(title)}">
  <meta property="og:description" content="${htmlEscape(intro || title)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="${htmlEscape(canonicalUrl)}">

  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="${htmlEscape(title)}">
  <meta name="twitter:description" content="${htmlEscape(intro || title)}">

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
      --ink-dark:#132033;
      --muted:#9eb0cf;
      --muted-2:#7e93b5;

      --line:rgba(148,163,184,.20);
      --line-2:rgba(255,255,255,.10);

      --cyan:#22d3ee;
      --cyan-2:#06b6d4;
      --blue:#3b82f6;
      --blue-2:#2563eb;
      --violet:#8b5cf6;
      --violet-2:#7c3aed;
      --emerald:#10b981;
      --amber:#f59e0b;

      --shadow-xl:0 32px 90px rgba(2,6,23,.42);
      --shadow-lg:0 20px 54px rgba(2,6,23,.30);
      --shadow-md:0 12px 30px rgba(2,6,23,.22);
      --shadow-sm:0 8px 20px rgba(2,6,23,.16);
    }

    *{
      box-sizing:border-box;
    }

    html{
      -webkit-text-size-adjust:100%;
      scroll-behavior:smooth;
    }

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

    a{
      color:#8be9ff;
      text-decoration:none;
    }

    a:hover{
      text-decoration:underline;
    }

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
      color:var(--ink-strong);
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

    .container > *{
      position:relative;
      z-index:1;
    }

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

    .links-list li{
      margin:0;
    }

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

    .link-copy{
      min-width:0;
    }

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

    .related-grid li{
      margin:0;
    }

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
                  <span class="link-sub">${htmlEscape(formatDisplayUrl(item.href))}</span>
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

  const latestEntries = entries.slice(0, MAX_LATEST);
  const todayEntries = filterToday(entries).slice(0, MAX_TODAY);
  const weekEntries = filterThisWeek(entries).slice(0, MAX_WEEK);
  const htmlEntries = entries.slice(0, MAX_HTML);
  const feedEntries = entries.slice(0, MAX_FEED);

  writeFile(
    path.join(DISCOVERY_DIR, "latest/index.html"),
    pageShell({
      title: "Latest Pages",
      intro: "Newest URLs discovered from all sitemaps.",
      items: entriesToListItems(latestEntries),
    })
  );

  writeFile(
    path.join(DISCOVERY_DIR, "today/index.html"),
    pageShell({
      title: `Pages Added ${todayString()}`,
      intro: "Today's URLs from all sitemaps.",
      items: entriesToListItems(todayEntries),
    })
  );

  writeFile(
    path.join(DISCOVERY_DIR, "this-week/index.html"),
    pageShell({
      title: "Pages This Week",
      intro: "Recent URLs from all sitemaps.",
      items: entriesToListItems(weekEntries),
    })
  );

  writeFile(
    path.join(DISCOVERY_DIR, "html-sitemap/index.html"),
    pageShell({
      title: "HTML Sitemap",
      intro: "Combined sitemap view.",
      items: entriesToListItems(htmlEntries),
    })
  );

  writeFile(DISCOVERY_SITEMAP_PATH, buildXmlSitemap(entries.map((e) => e.url)));

  console.log("Discovery layer built successfully.");
  console.log(`Total URLs: ${entries.length}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});