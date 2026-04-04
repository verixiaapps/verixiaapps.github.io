name: Build Discovery B

on:
  workflow_dispatch:
  schedule:
    - cron: "17 */3 * * *"

permissions:
  contents: write

concurrency:
  group: discovery-b-build
  cancel-in-progress: false

jobs:
  build-discovery-b:
    runs-on: ubuntu-latest

    env:
      SITE_URL: https://verixiaapps.com
      SOURCE_DIR: scam-check-now-b
      DISCOVERY_DIR: discovery-b
      DISCOVERY_SITEMAP_PATH: discovery-b-sitemap.xml
      MAX_LATEST_URLS: 100
      MAX_TODAY_URLS: 100
      MAX_THIS_WEEK_URLS: 700
      MAX_HTML_SITEMAP_URLS: 500
      MAX_FEED_URLS: 100

    steps:
      - name: Check out repo
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Build Discovery-B
        run: node scripts/build-discovery-layer-b.js

      - name: Commit and push generated Discovery-B files
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add discovery-b discovery-b-sitemap.xml

          if git diff --cached --quiet; then
            echo "No Discovery-B changes to commit."
            exit 0
          fi

          git commit -m "Build Discovery-B"
          git push
// scripts/build-discovery-layer-b.js
'use strict';

const fs = require('fs');
const fsp = require('fs/promises');
const path = require('path');
const crypto = require('crypto');

const SITE_URL = normalizeSiteUrl(process.env.SITE_URL || 'https://verixiaapps.com');
const SOURCE_DIR = path.resolve(process.cwd(), process.env.SOURCE_DIR || 'scam-check-now-b');
const DISCOVERY_DIR = path.resolve(process.cwd(), process.env.DISCOVERY_DIR || 'discovery-b');
const DISCOVERY_SITEMAP_PATH = path.resolve(process.cwd(), process.env.DISCOVERY_SITEMAP_PATH || 'discovery-b-sitemap.xml');

const MAX_LATEST_URLS = toInt(process.env.MAX_LATEST_URLS, 100);
const MAX_TODAY_URLS = toInt(process.env.MAX_TODAY_URLS, 100);
const MAX_THIS_WEEK_URLS = toInt(process.env.MAX_THIS_WEEK_URLS, 700);
const MAX_HTML_SITEMAP_URLS = toInt(process.env.MAX_HTML_SITEMAP_URLS, 500);
const MAX_FEED_URLS = toInt(process.env.MAX_FEED_URLS, 100);

const DISCOVERY_BASE = '/discovery-b';
const SOURCE_BASE = '/scam-check-now-b';
const PAGE_SIZE = 60;
const HTML_SITEMAP_PAGE_SIZE = 200;
const RUNWAY_PAGE_SIZE = 100;
const RANDOM_PAGE_SIZE = 80;
const MAX_TOPICS = 120;
const MAX_PLATFORMS = 40;
const MAX_CLUSTERS = 80;
const MAX_HYBRIDS = 120;
const MAX_TOPIC_PAGE_ITEMS = 250;
const MAX_PLATFORM_PAGE_ITEMS = 250;
const MAX_CLUSTER_PAGE_ITEMS = 200;
const MAX_HYBRID_PAGE_ITEMS = 200;

const NOW = new Date();
const TODAY_KEY = formatDateUTC(NOW);
const THIS_WEEK_START = startOfWeekUTC(NOW);
const THIS_WEEK_END = addDaysUTC(THIS_WEEK_START, 7);

const STOP_WORDS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'before', 'best', 'by', 'can', 'check', 'checker',
  'for', 'from', 'get', 'guide', 'how', 'if', 'in', 'into', 'is', 'it', 'its', 'may', 'more',
  'new', 'not', 'now', 'of', 'on', 'or', 'our', 'page', 'pages', 'review', 'safe', 'scam',
  'scams', 'should', 'site', 'sites', 'that', 'the', 'this', 'tips', 'to', 'tool', 'up',
  'use', 'using', 'what', 'when', 'why', 'with', 'your', 'you', 'vs', 'versus', 'way', 'ways',
  'online', 'message', 'messages', 'link', 'links', 'text', 'email', 'emails'
]);

const PLATFORM_SYNONYMS = {
  paypal: 'PayPal',
  venmo: 'Venmo',
  cashapp: 'Cash App',
  cash: 'Cash App',
  app: 'Cash App',
  zelle: 'Zelle',
  apple: 'Apple',
  imessage: 'iMessage',
  whatsapp: 'WhatsApp',
  telegram: 'Telegram',
  signal: 'Signal',
  instagram: 'Instagram',
  facebook: 'Facebook',
  messenger: 'Messenger',
  meta: 'Meta',
  x: 'X',
  twitter: 'X',
  tiktok: 'TikTok',
  youtube: 'YouTube',
  gmail: 'Gmail',
  google: 'Google',
  outlook: 'Outlook',
  microsoft: 'Microsoft',
  linkedin: 'LinkedIn',
  amazon: 'Amazon',
  ebay: 'eBay',
  etsy: 'Etsy',
  craigslist: 'Craigslist',
  coinbase: 'Coinbase',
  binance: 'Binance',
  crypto: 'Crypto',
  bitcoin: 'Bitcoin',
  usdt: 'USDT',
  usdc: 'USDC',
  fedex: 'FedEx',
  ups: 'UPS',
  usps: 'USPS',
  dhl: 'DHL',
  netflix: 'Netflix',
  spotify: 'Spotify',
  steam: 'Steam',
  discord: 'Discord',
  slack: 'Slack',
  zoom: 'Zoom',
  teams: 'Microsoft Teams',
  office: 'Microsoft',
  chase: 'Chase',
  bank: 'Banking',
  wells: 'Wells Fargo',
  citi: 'Citi',
  capitalone: 'Capital One',
  att: 'AT&T',
  verizon: 'Verizon',
  tmobile: 'T-Mobile',
  ebaymotors: 'eBay',
  airbnb: 'Airbnb',
  uber: 'Uber',
  lyft: 'Lyft'
};

async function main() {
  assertSourceDirExists();

  await ensureDir(DISCOVERY_DIR);
  await cleanDir(DISCOVERY_DIR);

  const entries = await scanSourceEntries(SOURCE_DIR);
  if (!entries.length) {
    throw new Error(`No source pages found under ${SOURCE_DIR}. Expected nested index.html files.`);
  }

  const uniqueEntries = dedupeEntries(entries);
  const enrichedEntries = enrichEntries(uniqueEntries);

  const sortedByFreshness = [...enrichedEntries].sort(sortByFreshness);
  const latestEntries = sortedByFreshness.slice(0, Math.max(MAX_LATEST_URLS, PAGE_SIZE));
  const todayEntries = sortedByFreshness
    .filter((e) => e.dateKey === TODAY_KEY)
    .slice(0, Math.max(MAX_TODAY_URLS, PAGE_SIZE));
  const thisWeekEntries = sortedByFreshness
    .filter((e) => e.lastmodDate >= THIS_WEEK_START && e.lastmodDate < THIS_WEEK_END)
    .slice(0, Math.max(MAX_THIS_WEEK_URLS, PAGE_SIZE));

  const platformMap = buildPlatformMap(enrichedEntries);
  const topicMap = buildTopicMap(enrichedEntries);
  const clusterMap = buildClusterMap(enrichedEntries);
  const hybridMap = buildHybridMap(enrichedEntries);

  const topicPages = selectTopTaxonomy(topicMap, MAX_TOPICS, MAX_TOPIC_PAGE_ITEMS);
  const platformPages = selectTopTaxonomy(platformMap, MAX_PLATFORMS, MAX_PLATFORM_PAGE_ITEMS);
  const clusterPages = selectTopTaxonomy(clusterMap, MAX_CLUSTERS, MAX_CLUSTER_PAGE_ITEMS);
  const hybridPages = selectTopTaxonomy(hybridMap, MAX_HYBRIDS, MAX_HYBRID_PAGE_ITEMS);

  const discoveryPageRecords = [];

  const addPageRecord = async (relDir, html, lastmod = isoDateTimeUTC(NOW)) => {
    await writePage(relDir, html);
    const loc = joinUrl(SITE_URL, DISCOVERY_BASE, relDirToUrl(relDir));
    discoveryPageRecords.push({ loc, lastmod });
  };

  const addXmlRecord = async (relPath, content, bucket, lastmod = isoDateTimeUTC(NOW)) => {
    const fullPath = path.join(DISCOVERY_DIR, relPath);
    await ensureDir(path.dirname(fullPath));
    await fsp.writeFile(fullPath, content, 'utf8');
    const loc = joinUrl(SITE_URL, DISCOVERY_BASE, relPath.replace(/\\/g, '/'));
    return { loc, lastmod, bucket };
  };

  const navigation = buildNavigation({
    latestCount: latestEntries.length,
    todayCount: todayEntries.length,
    thisWeekCount: thisWeekEntries.length,
    topicCount: topicPages.length,
    platformCount: platformPages.length,
    clusterCount: clusterPages.length,
    hybridCount: hybridPages.length
  });

  const rootCards = [
    buildStatCard('Latest', `${latestEntries.length} fresh discovery links`, joinUrl(SITE_URL, DISCOVERY_BASE, '/latest/')),
    buildStatCard('Today', `${todayEntries.length} pages updated today`, joinUrl(SITE_URL, DISCOVERY_BASE, '/today/')),
    buildStatCard('This Week', `${thisWeekEntries.length} pages updated this week`, joinUrl(SITE_URL, DISCOVERY_BASE, '/this-week/')),
    buildStatCard('Topics', `${topicPages.length} grouped topic hubs`, joinUrl(SITE_URL, DISCOVERY_BASE, '/topics/')),
    buildStatCard('Platforms', `${platformPages.length} grouped platform hubs`, joinUrl(SITE_URL, DISCOVERY_BASE, '/platforms/')),
    buildStatCard('Clusters', `${clusterPages.length} grouped pattern clusters`, joinUrl(SITE_URL, DISCOVERY_BASE, '/clusters/')),
    buildStatCard('Hybrids', `${hybridPages.length} combined intent pages`, joinUrl(SITE_URL, DISCOVERY_BASE, '/hybrids/')),
    buildStatCard('HTML Sitemap', `${Math.min(enrichedEntries.length, MAX_HTML_SITEMAP_URLS)} sitemap links`, joinUrl(SITE_URL, DISCOVERY_BASE, '/html-sitemap/'))
  ];

  const rootSections = [
    renderCardGridSection('Discovery surfaces', rootCards),
    renderLinkCardsSection('Freshest pages', latestEntries.slice(0, 18).map(renderEntryCard)),
    renderLinkCardsSection('Today by topic', topTopicCardsFromEntries(todayEntries, topicPages, 12)),
    renderLinkCardsSection('Latest by platform', topPlatformCardsFromEntries(latestEntries, platformPages, 12)),
    renderLinkCardsSection(
      'Explore clusters',
      clusterPages.slice(0, 12).map((item) => renderTaxonomyCard('Cluster', item.label, item.entries.length, taxonomyUrl('clusters', item.slug)))
    ),
    renderLinkCardsSection(
      'Explore hybrids',
      hybridPages.slice(0, 12).map((item) => renderTaxonomyCard('Hybrid', item.label, item.entries.length, taxonomyUrl('hybrids', item.slug)))
    )
  ];

  await addPageRecord(
    '',
    renderShell({
      pageTitle: 'Discovery B | Verixia Apps',
      metaDescription: 'Discovery-B hub for Verixia Apps. Fresh scam-check-now-b page discovery, topics, platforms, clusters, hybrids, feed, and sitemap access.',
      canonicalPath: `${DISCOVERY_BASE}/`,
      heroEyebrow: 'Discovery B',
      heroTitle: 'Fresh discovery pages built from scam-check-now-b',
      heroText: 'This discovery layer reads from scam-check-now-b pages and publishes premium discovery surfaces under discovery-b only.',
      navigation,
      sections: rootSections
    })
  );

  await buildLatestPages({ latestEntries, navigation, addPageRecord });
  await buildTodayPages({ todayEntries, navigation, addPageRecord });
  await buildThisWeekPage({ thisWeekEntries, navigation, addPageRecord });
  await buildHtmlSitemapPages({ entries: enrichedEntries.slice(0, MAX_HTML_SITEMAP_URLS), navigation, addPageRecord });
  await buildRunwayPages({ entries: enrichedEntries, navigation, addPageRecord });
  await buildRandomPages({ entries: enrichedEntries, navigation, addPageRecord });
  await buildRevisitPage({ entries: enrichedEntries, navigation, addPageRecord });
  await buildTopicsPages({ topicPages, navigation, addPageRecord });
  await buildTodayTopicsPage({ todayEntries, topicPages, navigation, addPageRecord });
  await buildPlatformsPages({ platformPages, latestEntries, navigation, addPageRecord });
  await buildLatestPlatformsPage({ latestEntries, platformPages, navigation, addPageRecord });
  await buildClustersPages({ clusterPages, navigation, addPageRecord });
  await buildHybridsPages({ hybridPages, navigation, addPageRecord });
  await buildFeed({ entries: sortedByFreshness.slice(0, MAX_FEED_URLS), addXmlRecord });

  const sitemapXmlRecords = [];
  sitemapXmlRecords.push(...await buildBucketSitemaps({
    discoveryPageRecords,
    addXmlRecord
  }));

  await writeSitemapIndex(sitemapXmlRecords);

  console.log('Discovery-B complete.');
  console.log(`Source entries: ${enrichedEntries.length}`);
  console.log(`Generated pages: ${discoveryPageRecords.length}`);
  console.log(`Generated sitemap buckets: ${sitemapXmlRecords.length}`);
}

function normalizeSiteUrl(url) {
  return String(url || '').trim().replace(/\/+$/, '');
}

function toInt(value, fallback) {
  const n = Number.parseInt(String(value ?? ''), 10);
  return Number.isFinite(n) && n > 0 ? n : fallback;
}

function assertSourceDirExists() {
  if (!fs.existsSync(SOURCE_DIR)) {
    throw new Error(`SOURCE_DIR does not exist: ${SOURCE_DIR}`);
  }
  const stat = fs.statSync(SOURCE_DIR);
  if (!stat.isDirectory()) {
    throw new Error(`SOURCE_DIR is not a directory: ${SOURCE_DIR}`);
  }
}

async function ensureDir(dir) {
  await fsp.mkdir(dir, { recursive: true });
}

async function cleanDir(dir) {
  await ensureDir(dir);
  const entries = await fsp.readdir(dir, { withFileTypes: true });
  await Promise.all(entries.map(async (entry) => {
    const full = path.join(dir, entry.name);
    await fsp.rm(full, { recursive: true, force: true });
  }));
}

async function scanSourceEntries(rootDir) {
  const results = [];
  await walkDir(rootDir, async (fullPath, dirent) => {
    if (!dirent.isFile()) return;
    if (dirent.name !== 'index.html') return;

    const rel = path.relative(rootDir, fullPath).replace(/\\/g, '/');
    const slug = rel.replace(/\/index\.html$/, '').replace(/^\/+|\/+$/g, '');
    if (!slug) return;

    const stat = await fsp.stat(fullPath);
    const html = await safeReadText(fullPath);
    const extracted = extractSourceMeta(html);

    const sourcePath = `${SOURCE_BASE}/${slug}/`;
    const sourceUrl = joinUrl(SITE_URL, sourcePath);

    results.push({
      id: sha1(sourceUrl),
      slug,
      sourcePath,
      sourceUrl,
      filePath: fullPath,
      fileMtimeMs: stat.mtimeMs,
      lastmod: stat.mtime.toISOString(),
      title: extracted.title || prettifySlug(slug),
      metaDescription: extracted.metaDescription || buildDefaultSourceDescription(slug),
      h1: extracted.h1 || extracted.title || prettifySlug(slug)
    });
  });
  return results;
}

async function walkDir(dir, onEntry) {
  const entries = await fsp.readdir(dir, { withFileTypes: true });
  for (const dirent of entries) {
    const fullPath = path.join(dir, dirent.name);
    if (dirent.isDirectory()) {
      await walkDir(fullPath, onEntry);
    } else {
      await onEntry(fullPath, dirent);
    }
  }
}

async function safeReadText(filePath) {
  try {
    return await fsp.readFile(filePath, 'utf8');
  } catch {
    return '';
  }
}

function extractSourceMeta(html) {
  const title = matchTag(html, /<title[^>]*>([\s\S]*?)<\/title>/i);
  const h1 = matchTag(html, /<h1[^>]*>([\s\S]*?)<\/h1>/i);
  const metaDescription =
    matchAttr(html, /<meta[^>]+name=["']description["'][^>]+content=["']([^"']+)["'][^>]*>/i) ||
    matchAttr(html, /<meta[^>]+content=["']([^"']+)["'][^>]+name=["']description["'][^>]*>/i);

  return {
    title: cleanText(title),
    h1: cleanText(h1),
    metaDescription: cleanText(metaDescription)
  };
}

function matchTag(html, regex) {
  const m = String(html || '').match(regex);
  return m ? stripHtml(m[1]) : '';
}

function matchAttr(html, regex) {
  const m = String(html || '').match(regex);
  return m ? stripHtml(m[1]) : '';
}

function stripHtml(input) {
  return String(input || '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

function cleanText(input) {
  return String(input || '').replace(/\s+/g, ' ').trim();
}

function buildDefaultSourceDescription(slug) {
  return `Scam Check Now B discovery source for ${prettifySlug(slug)}.`;
}

function dedupeEntries(entries) {
  const map = new Map();
  for (const entry of entries) {
    const key = entry.sourceUrl;
    const existing = map.get(key);
    if (!existing || entry.fileMtimeMs > existing.fileMtimeMs) {
      map.set(key, entry);
    }
  }
  return [...map.values()];
}

function enrichEntries(entries) {
  return entries.map((entry) => {
    const normalizedSlug = entry.slug.toLowerCase();
    const slugParts = normalizedSlug.split('/').flatMap((s) => s.split('-')).filter(Boolean);
    const tokens = tokenize([...slugParts, entry.title, entry.h1].join(' '));
    const uniqueTokens = [...new Set(tokens)];

    const platformLabels = detectPlatforms(uniqueTokens);
    const topics = detectTopics(uniqueTokens);
    const dateObj = new Date(entry.lastmod);

    return {
      ...entry,
      tokens: uniqueTokens,
      platformLabels,
      topicLabels: topics,
      clusterTokens: uniqueTokens.filter((t) => !STOP_WORDS.has(t)).slice(0, 20),
      sourceLabel: entry.h1 || entry.title || prettifySlug(entry.slug),
      dateKey: formatDateUTC(dateObj),
      lastmodDate: dateObj,
      discoveryLabel: normalizeDiscoveryLabel(entry)
    };
  });
}

function normalizeDiscoveryLabel(entry) {
  const title = cleanText(entry.h1 || entry.title || prettifySlug(entry.slug));
  return title.length > 90 ? `${title.slice(0, 87)}…` : title;
}

function tokenize(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s/-]+/g, ' ')
    .replace(/[\/_-]+/g, ' ')
    .split(/\s+/)
    .map((t) => t.trim())
    .filter(Boolean)
    .filter((t) => t.length > 1 || t === 'x');
}

function detectPlatforms(tokens) {
  const labels = new Set();

  for (const token of tokens) {
    if (PLATFORM_SYNONYMS[token]) {
      labels.add(PLATFORM_SYNONYMS[token]);
    }
  }

  const combos = tokens.join(' ');
  if (/\bcash app\b/.test(combos)) labels.add('Cash App');
  if (/\bapple pay\b/.test(combos)) labels.add('Apple');
  if (/\bfacebook marketplace\b/.test(combos)) labels.add('Facebook');
  if (/\bgoogle voice\b/.test(combos)) labels.add('Google');
  if (/\bmicrosoft teams\b/.test(combos)) labels.add('Microsoft Teams');

  return [...labels].sort((a, b) => a.localeCompare(b));
}

function detectTopics(tokens) {
  const result = new Set();

  for (const token of tokens) {
    if (STOP_WORDS.has(token)) continue;
    if (PLATFORM_SYNONYMS[token]) continue;
    if (/^\d+$/.test(token)) continue;
    if (token.length < 3) continue;
    result.add(prettifyToken(token));
  }

  return [...result].slice(0, 8);
}

function buildPlatformMap(entries) {
  const map = new Map();
  for (const entry of entries) {
    for (const label of entry.platformLabels) {
      if (!map.has(label)) map.set(label, []);
      map.get(label).push(entry);
    }
  }
  return map;
}

function buildTopicMap(entries) {
  const map = new Map();
  for (const entry of entries) {
    for (const label of entry.topicLabels) {
      if (!map.has(label)) map.set(label, []);
      map.get(label).push(entry);
    }
  }
  return map;
}

function buildClusterMap(entries) {
  const map = new Map();
  for (const entry of entries) {
    const clusterTokens = entry.clusterTokens
      .filter((t) => !entry.platformLabels.some((p) => slugify(p) === t))
      .slice(0, 8);

    const pairs = pickTokenPairs(clusterTokens, 3);
    for (const pair of pairs) {
      const label = pair.map(prettifyToken).join(' + ');
      if (!map.has(label)) map.set(label, []);
      map.get(label).push(entry);
    }
  }
  return map;
}

function buildHybridMap(entries) {
  const map = new Map();
  for (const entry of entries) {
    const topics = entry.topicLabels.slice(0, 3);
    const platforms = entry.platformLabels.slice(0, 2);

    for (const platform of platforms) {
      for (const topic of topics) {
        const label = `${platform} + ${topic}`;
        if (!map.has(label)) map.set(label, []);
        map.get(label).push(entry);
      }
    }

    if (!platforms.length && topics.length >= 2) {
      const label = `${topics[0]} + ${topics[1]}`;
      if (!map.has(label)) map.set(label, []);
      map.get(label).push(entry);
    }
  }
  return map;
}

function selectTopTaxonomy(map, maxCount, maxItemsPerPage) {
  const items = [];

  for (const [label, entries] of map.entries()) {
    const deduped = dedupeBySourceUrl(entries).sort(sortByFreshness).slice(0, maxItemsPerPage);
    if (deduped.length < 2) continue;

    items.push({
      label,
      slug: slugify(label),
      entries: deduped,
      lastmod: deduped[0].lastmod
    });
  }

  return items
    .sort((a, b) => {
      if (b.entries.length !== a.entries.length) return b.entries.length - a.entries.length;
      return a.label.localeCompare(b.label);
    })
    .slice(0, maxCount);
}

function dedupeBySourceUrl(entries) {
  const seen = new Map();
  for (const entry of entries) {
    const existing = seen.get(entry.sourceUrl);
    if (!existing || entry.fileMtimeMs > existing.fileMtimeMs) {
      seen.set(entry.sourceUrl, entry);
    }
  }
  return [...seen.values()];
}

function sortByFreshness(a, b) {
  if (b.fileMtimeMs !== a.fileMtimeMs) return b.fileMtimeMs - a.fileMtimeMs;
  return a.sourceUrl.localeCompare(b.sourceUrl);
}

function pickTokenPairs(tokens, maxPairs) {
  const pairs = [];
  for (let i = 0; i < tokens.length; i += 1) {
    for (let j = i + 1; j < tokens.length; j += 1) {
      const a = tokens[i];
      const b = tokens[j];
      if (!a || !b || a === b) continue;
      if (STOP_WORDS.has(a) || STOP_WORDS.has(b)) continue;
      const pair = [a, b].sort();
      const key = pair.join('|');
      if (!pairs.some((p) => p.join('|') === key)) pairs.push(pair);
      if (pairs.length >= maxPairs) return pairs;
    }
  }
  return pairs;
}

async function buildLatestPages({ latestEntries, navigation, addPageRecord }) {
  const relBase = 'latest';
  const pages = paginate(latestEntries, PAGE_SIZE);

  await addPageRecord(
    relBase,
    renderListingPage({
      pageTitle: 'Latest Discovery B Pages | Verixia Apps',
      metaDescription: 'Latest discovery pages from scam-check-now-b.',
      canonicalPath: `${DISCOVERY_BASE}/latest/`,
      heroEyebrow: 'Latest',
      heroTitle: 'Latest Discovery-B pages',
      heroText: `${latestEntries.length} recent source pages from scam-check-now-b.`,
      entries: pages[0] || [],
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Latest' }],
      pager: renderPagination(`${DISCOVERY_BASE}/latest/`, pages.length, 1)
    })
  );

  for (let i = 1; i < pages.length; i += 1) {
    const pageNumber = i + 1;
    await addPageRecord(
      path.join(relBase, 'page', String(pageNumber)),
      renderListingPage({
        pageTitle: `Latest Discovery B Pages - Page ${pageNumber} | Verixia Apps`,
        metaDescription: `Latest Discovery-B pages page ${pageNumber}.`,
        canonicalPath: `${DISCOVERY_BASE}/latest/page/${pageNumber}/`,
        heroEyebrow: 'Latest',
        heroTitle: `Latest pages · page ${pageNumber}`,
        heroText: `${latestEntries.length} recent source pages from scam-check-now-b.`,
        entries: pages[i],
        navigation,
        breadcrumb: [
          { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
          { label: 'Latest', href: `${DISCOVERY_BASE}/latest/` },
          { label: `Page ${pageNumber}` }
        ],
        pager: renderPagination(`${DISCOVERY_BASE}/latest/`, pages.length, pageNumber)
      })
    );
  }
}

async function buildTodayPages({ todayEntries, navigation, addPageRecord }) {
  const relBase = 'today';
  const pages = paginate(todayEntries, PAGE_SIZE);

  await addPageRecord(
    relBase,
    renderListingPage({
      pageTitle: 'Today Discovery B Pages | Verixia Apps',
      metaDescription: 'Today updates in discovery-b from scam-check-now-b.',
      canonicalPath: `${DISCOVERY_BASE}/today/`,
      heroEyebrow: 'Today',
      heroTitle: 'Updated today',
      heroText: `${todayEntries.length} pages updated today.`,
      entries: pages[0] || [],
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Today' }],
      pager: renderPagination(`${DISCOVERY_BASE}/today/`, pages.length, 1),
      extraSections: [
        renderLinkCardsSection('Today by topic', topTopicCardsFromEntries(todayEntries, selectTopTaxonomy(buildTopicMap(todayEntries), 24, 200), 18))
      ]
    })
  );

  for (let i = 1; i < pages.length; i += 1) {
    const pageNumber = i + 1;
    await addPageRecord(
      path.join(relBase, 'page', String(pageNumber)),
      renderListingPage({
        pageTitle: `Today Discovery B Pages - Page ${pageNumber} | Verixia Apps`,
        metaDescription: `Today discovery-b pages page ${pageNumber}.`,
        canonicalPath: `${DISCOVERY_BASE}/today/page/${pageNumber}/`,
        heroEyebrow: 'Today',
        heroTitle: `Updated today · page ${pageNumber}`,
        heroText: `${todayEntries.length} pages updated today.`,
        entries: pages[i],
        navigation,
        breadcrumb: [
          { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
          { label: 'Today', href: `${DISCOVERY_BASE}/today/` },
          { label: `Page ${pageNumber}` }
        ],
        pager: renderPagination(`${DISCOVERY_BASE}/today/`, pages.length, pageNumber)
      })
    );
  }
}

async function buildThisWeekPage({ thisWeekEntries, navigation, addPageRecord }) {
  await addPageRecord(
    'this-week',
    renderListingPage({
      pageTitle: 'This Week Discovery B Pages | Verixia Apps',
      metaDescription: 'This week updates in discovery-b from scam-check-now-b.',
      canonicalPath: `${DISCOVERY_BASE}/this-week/`,
      heroEyebrow: 'This Week',
      heroTitle: 'Updated this week',
      heroText: `${thisWeekEntries.length} pages updated this week.`,
      entries: thisWeekEntries.slice(0, Math.max(PAGE_SIZE * 2, thisWeekEntries.length)),
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'This Week' }]
    })
  );
}

async function buildHtmlSitemapPages({ entries, navigation, addPageRecord }) {
  const relBase = 'html-sitemap';
  const pages = paginate(entries, HTML_SITEMAP_PAGE_SIZE);

  await addPageRecord(
    relBase,
    renderHtmlSitemapPage({
      pageTitle: 'HTML Sitemap Discovery B | Verixia Apps',
      metaDescription: 'HTML sitemap for discovery-b.',
      canonicalPath: `${DISCOVERY_BASE}/html-sitemap/`,
      heroEyebrow: 'HTML Sitemap',
      heroTitle: 'Browse discovery-b source links',
      heroText: `${entries.length} source links available in the HTML sitemap.`,
      entries: pages[0] || [],
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'HTML Sitemap' }],
      pager: renderPagination(`${DISCOVERY_BASE}/html-sitemap/`, pages.length, 1)
    })
  );

  for (let i = 1; i < pages.length; i += 1) {
    const pageNumber = i + 1;
    await addPageRecord(
      path.join(relBase, 'page', String(pageNumber)),
      renderHtmlSitemapPage({
        pageTitle: `HTML Sitemap Discovery B - Page ${pageNumber} | Verixia Apps`,
        metaDescription: `HTML sitemap page ${pageNumber} for discovery-b.`,
        canonicalPath: `${DISCOVERY_BASE}/html-sitemap/page/${pageNumber}/`,
        heroEyebrow: 'HTML Sitemap',
        heroTitle: `HTML sitemap · page ${pageNumber}`,
        heroText: `${entries.length} source links available in the HTML sitemap.`,
        entries: pages[i],
        navigation,
        breadcrumb: [
          { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
          { label: 'HTML Sitemap', href: `${DISCOVERY_BASE}/html-sitemap/` },
          { label: `Page ${pageNumber}` }
        ],
        pager: renderPagination(`${DISCOVERY_BASE}/html-sitemap/`, pages.length, pageNumber)
      })
    );
  }
}

async function buildRunwayPages({ entries, navigation, addPageRecord }) {
  const runwayEntries = [...entries].sort((a, b) => a.sourceLabel.localeCompare(b.sourceLabel));
  const relBase = 'runway';
  const pages = paginate(runwayEntries, RUNWAY_PAGE_SIZE);

  await addPageRecord(
    relBase,
    renderListingPage({
      pageTitle: 'Runway Discovery B | Verixia Apps',
      metaDescription: 'Runway alphabetical discovery surface for discovery-b.',
      canonicalPath: `${DISCOVERY_BASE}/runway/`,
      heroEyebrow: 'Runway',
      heroTitle: 'Alphabetical runway',
      heroText: `${runwayEntries.length} source pages sorted alphabetically.`,
      entries: pages[0] || [],
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Runway' }],
      pager: renderPagination(`${DISCOVERY_BASE}/runway/`, pages.length, 1)
    })
  );

  for (let i = 1; i < pages.length; i += 1) {
    const pageNumber = i + 1;
    await addPageRecord(
      path.join(relBase, 'page', String(pageNumber)),
      renderListingPage({
        pageTitle: `Runway Discovery B - Page ${pageNumber} | Verixia Apps`,
        metaDescription: `Runway page ${pageNumber} for discovery-b.`,
        canonicalPath: `${DISCOVERY_BASE}/runway/page/${pageNumber}/`,
        heroEyebrow: 'Runway',
        heroTitle: `Alphabetical runway · page ${pageNumber}`,
        heroText: `${runwayEntries.length} source pages sorted alphabetically.`,
        entries: pages[i],
        navigation,
        breadcrumb: [
          { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
          { label: 'Runway', href: `${DISCOVERY_BASE}/runway/` },
          { label: `Page ${pageNumber}` }
        ],
        pager: renderPagination(`${DISCOVERY_BASE}/runway/`, pages.length, pageNumber)
      })
    );
  }
}

async function buildRandomPages({ entries, navigation, addPageRecord }) {
  const shuffled1 = stableShuffle(entries, 'random-1').slice(0, RANDOM_PAGE_SIZE);
  const shuffled2 = stableShuffle(entries, 'random-2').slice(0, RANDOM_PAGE_SIZE);
  const shuffled3 = stableShuffle(entries, 'random-3').slice(0, RANDOM_PAGE_SIZE);

  await addPageRecord(
    'random',
    renderListingPage({
      pageTitle: 'Random Discovery B Pages | Verixia Apps',
      metaDescription: 'Random discovery pages from scam-check-now-b.',
      canonicalPath: `${DISCOVERY_BASE}/random/`,
      heroEyebrow: 'Random',
      heroTitle: 'Random discovery sample',
      heroText: 'A stable random sample of source pages.',
      entries: shuffled1,
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Random' }]
    })
  );

  await addPageRecord(
    'random-2',
    renderListingPage({
      pageTitle: 'Random 2 Discovery B Pages | Verixia Apps',
      metaDescription: 'Second random discovery page sample from scam-check-now-b.',
      canonicalPath: `${DISCOVERY_BASE}/random-2/`,
      heroEyebrow: 'Random 2',
      heroTitle: 'Random discovery sample · set 2',
      heroText: 'A second stable random sample of source pages.',
      entries: shuffled2,
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Random 2' }]
    })
  );

  await addPageRecord(
    'random-3',
    renderListingPage({
      pageTitle: 'Random 3 Discovery B Pages | Verixia Apps',
      metaDescription: 'Third random discovery page sample from scam-check-now-b.',
      canonicalPath: `${DISCOVERY_BASE}/random-3/`,
      heroEyebrow: 'Random 3',
      heroTitle: 'Random discovery sample · set 3',
      heroText: 'A third stable random sample of source pages.',
      entries: shuffled3,
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Random 3' }]
    })
  );
}

async function buildRevisitPage({ entries, navigation, addPageRecord }) {
  const revisit = [...entries]
    .filter((e) => {
      const ageDays = Math.floor((NOW.getTime() - e.lastmodDate.getTime()) / 86400000);
      return ageDays >= 2 && ageDays <= 30;
    })
    .sort(sortByFreshness)
    .slice(0, 120);

  await addPageRecord(
    'revisit',
    renderListingPage({
      pageTitle: 'Revisit Discovery B Pages | Verixia Apps',
      metaDescription: 'Revisit source pages recently updated in the last 30 days.',
      canonicalPath: `${DISCOVERY_BASE}/revisit/`,
      heroEyebrow: 'Revisit',
      heroTitle: 'Recently updated, worth revisiting',
      heroText: `${revisit.length} pages updated recently but not just today.`,
      entries: revisit,
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Revisit' }]
    })
  );
}

async function buildTopicsPages({ topicPages, navigation, addPageRecord }) {
  await addPageRecord(
    'topics',
    renderTaxonomyIndexPage({
      pageTitle: 'Topics Discovery B | Verixia Apps',
      metaDescription: 'Topic hubs for discovery-b.',
      canonicalPath: `${DISCOVERY_BASE}/topics/`,
      heroEyebrow: 'Topics',
      heroTitle: 'Topic hubs',
      heroText: `${topicPages.length} topic pages built from scam-check-now-b.`,
      items: topicPages,
      kind: 'Topic',
      basePath: `${DISCOVERY_BASE}/topics/`,
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Topics' }]
    })
  );

  for (const item of topicPages) {
    await addPageRecord(
      path.join('topics', item.slug),
      renderTaxonomyChildPage({
        pageTitle: `${item.label} Discovery B Topic | Verixia Apps`,
        metaDescription: `Discovery-b topic page for ${item.label}.`,
        canonicalPath: `${DISCOVERY_BASE}/topics/${item.slug}/`,
        heroEyebrow: 'Topic',
        heroTitle: item.label,
        heroText: `${item.entries.length} source pages grouped under this topic.`,
        entries: item.entries,
        kind: 'Topic',
        item,
        navigation,
        breadcrumb: [
          { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
          { label: 'Topics', href: `${DISCOVERY_BASE}/topics/` },
          { label: item.label }
        ]
      }),
      item.lastmod
    );
  }
}

async function buildTodayTopicsPage({ todayEntries, topicPages, navigation, addPageRecord }) {
  const todayTopicCards = topicPages
    .map((item) => ({
      ...item,
      todayEntries: item.entries.filter((entry) => todayEntries.some((t) => t.sourceUrl === entry.sourceUrl))
    }))
    .filter((item) => item.todayEntries.length > 0)
    .sort((a, b) => b.todayEntries.length - a.todayEntries.length || a.label.localeCompare(b.label));

  await addPageRecord(
    path.join('today', 'topics'),
    renderTodayTopicsPage({
      pageTitle: 'Today Topics Discovery B | Verixia Apps',
      metaDescription: 'Topic view for pages updated today in discovery-b.',
      canonicalPath: `${DISCOVERY_BASE}/today/topics/`,
      heroEyebrow: 'Today / Topics',
      heroTitle: 'Today by topic',
      heroText: `${todayTopicCards.length} topics with updates today.`,
      items: todayTopicCards,
      navigation,
      breadcrumb: [
        { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
        { label: 'Today', href: `${DISCOVERY_BASE}/today/` },
        { label: 'Topics' }
      ]
    })
  );
}

async function buildPlatformsPages({ platformPages, latestEntries, navigation, addPageRecord }) {
  await addPageRecord(
    'platforms',
    renderTaxonomyIndexPage({
      pageTitle: 'Platforms Discovery B | Verixia Apps',
      metaDescription: 'Platform hubs for discovery-b.',
      canonicalPath: `${DISCOVERY_BASE}/platforms/`,
      heroEyebrow: 'Platforms',
      heroTitle: 'Platform hubs',
      heroText: `${platformPages.length} platform pages built from scam-check-now-b.`,
      items: platformPages,
      kind: 'Platform',
      basePath: `${DISCOVERY_BASE}/platforms/`,
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Platforms' }],
      extraSections: [
        renderLinkCardsSection(
          'Latest platform jumps',
          platformPages.slice(0, 12).map((item) =>
            renderTaxonomyCard('Platform', item.label, item.entries.length, taxonomyUrl('platforms', item.slug))
          )
        )
      ]
    })
  );

  for (const item of platformPages) {
    await addPageRecord(
      path.join('platforms', item.slug),
      renderTaxonomyChildPage({
        pageTitle: `${item.label} Discovery B Platform | Verixia Apps`,
        metaDescription: `Discovery-b platform page for ${item.label}.`,
        canonicalPath: `${DISCOVERY_BASE}/platforms/${item.slug}/`,
        heroEyebrow: 'Platform',
        heroTitle: item.label,
        heroText: `${item.entries.length} source pages grouped under this platform.`,
        entries: item.entries,
        kind: 'Platform',
        item,
        navigation,
        breadcrumb: [
          { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
          { label: 'Platforms', href: `${DISCOVERY_BASE}/platforms/` },
          { label: item.label }
        ],
        extraSections: [
          renderLinkCardsSection(
            'Latest on this platform',
            latestEntries
              .filter((entry) => entry.platformLabels.includes(item.label))
              .slice(0, 12)
              .map(renderEntryCard)
          )
        ]
      }),
      item.lastmod
    );
  }
}

async function buildLatestPlatformsPage({ latestEntries, platformPages, navigation, addPageRecord }) {
  const cards = platformPages
    .map((item) => ({
      item,
      count: latestEntries.filter((entry) => entry.platformLabels.includes(item.label)).length
    }))
    .filter((row) => row.count > 0)
    .sort((a, b) => b.count - a.count || a.item.label.localeCompare(b.item.label));

  await addPageRecord(
    path.join('latest', 'platforms'),
    renderLatestPlatformsPage({
      pageTitle: 'Latest Platforms Discovery B | Verixia Apps',
      metaDescription: 'Latest platform view for discovery-b.',
      canonicalPath: `${DISCOVERY_BASE}/latest/platforms/`,
      heroEyebrow: 'Latest / Platforms',
      heroTitle: 'Latest by platform',
      heroText: `${cards.length} platforms represented in the latest set.`,
      cards,
      navigation,
      breadcrumb: [
        { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
        { label: 'Latest', href: `${DISCOVERY_BASE}/latest/` },
        { label: 'Platforms' }
      ]
    })
  );
}

async function buildClustersPages({ clusterPages, navigation, addPageRecord }) {
  await addPageRecord(
    'clusters',
    renderTaxonomyIndexPage({
      pageTitle: 'Clusters Discovery B | Verixia Apps',
      metaDescription: 'Cluster hubs for discovery-b.',
      canonicalPath: `${DISCOVERY_BASE}/clusters/`,
      heroEyebrow: 'Clusters',
      heroTitle: 'Pattern clusters',
      heroText: `${clusterPages.length} cluster pages built from token pair groupings.`,
      items: clusterPages,
      kind: 'Cluster',
      basePath: `${DISCOVERY_BASE}/clusters/`,
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Clusters' }]
    })
  );

  for (const item of clusterPages) {
    await addPageRecord(
      path.join('clusters', item.slug),
      renderTaxonomyChildPage({
        pageTitle: `${item.label} Discovery B Cluster | Verixia Apps`,
        metaDescription: `Discovery-b cluster page for ${item.label}.`,
        canonicalPath: `${DISCOVERY_BASE}/clusters/${item.slug}/`,
        heroEyebrow: 'Cluster',
        heroTitle: item.label,
        heroText: `${item.entries.length} source pages grouped in this cluster.`,
        entries: item.entries,
        kind: 'Cluster',
        item,
        navigation,
        breadcrumb: [
          { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
          { label: 'Clusters', href: `${DISCOVERY_BASE}/clusters/` },
          { label: item.label }
        ]
      }),
      item.lastmod
    );
  }
}

async function buildHybridsPages({ hybridPages, navigation, addPageRecord }) {
  await addPageRecord(
    'hybrids',
    renderTaxonomyIndexPage({
      pageTitle: 'Hybrids Discovery B | Verixia Apps',
      metaDescription: 'Hybrid hubs for discovery-b.',
      canonicalPath: `${DISCOVERY_BASE}/hybrids/`,
      heroEyebrow: 'Hybrids',
      heroTitle: 'Hybrid intent pages',
      heroText: `${hybridPages.length} hybrid pages built from combined topic and platform signals.`,
      items: hybridPages,
      kind: 'Hybrid',
      basePath: `${DISCOVERY_BASE}/hybrids/`,
      navigation,
      breadcrumb: [{ label: 'Discovery B', href: `${DISCOVERY_BASE}/` }, { label: 'Hybrids' }]
    })
  );

  for (const item of hybridPages) {
    await addPageRecord(
      path.join('hybrids', item.slug),
      renderTaxonomyChildPage({
        pageTitle: `${item.label} Discovery B Hybrid | Verixia Apps`,
        metaDescription: `Discovery-b hybrid page for ${item.label}.`,
        canonicalPath: `${DISCOVERY_BASE}/hybrids/${item.slug}/`,
        heroEyebrow: 'Hybrid',
        heroTitle: item.label,
        heroText: `${item.entries.length} source pages grouped in this hybrid.`,
        entries: item.entries,
        kind: 'Hybrid',
        item,
        navigation,
        breadcrumb: [
          { label: 'Discovery B', href: `${DISCOVERY_BASE}/` },
          { label: 'Hybrids', href: `${DISCOVERY_BASE}/hybrids/` },
          { label: item.label }
        ]
      }),
      item.lastmod
    );
  }
}

async function buildFeed({ entries, addXmlRecord }) {
  const feedPath = 'feed.xml';
  const updated = entries[0]?.lastmod || isoDateTimeUTC(NOW);

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Verixia Apps Discovery B Feed</title>
    <link>${escapeXml(joinUrl(SITE_URL, DISCOVERY_BASE, '/'))}</link>
    <description>Latest Discovery-B pages sourced from scam-check-now-b.</description>
    <lastBuildDate>${escapeXml(new Date(updated).toUTCString())}</lastBuildDate>
    ${entries.map((entry) => `    <item>
      <title>${escapeXml(entry.discoveryLabel)}</title>
      <link>${escapeXml(entry.sourceUrl)}</link>
      <guid>${escapeXml(entry.sourceUrl)}</guid>
      <pubDate>${escapeXml(new Date(entry.lastmod).toUTCString())}</pubDate>
      <description>${escapeXml(entry.metaDescription || entry.sourceLabel)}</description>
    </item>`).join('\n')}
  </channel>
</rss>
`;
  await addXmlRecord(feedPath, xml, 'explore', updated);
}

async function buildBucketSitemaps({ discoveryPageRecords, addXmlRecord }) {
  const records = {
    core: [],
    topics: [],
    platforms: [],
    hybrids: [],
    clusters: [],
    explore: []
  };

  for (const page of discoveryPageRecords) {
    const pathname = new URL(page.loc).pathname;
    if (pathname.includes('/topics/')) records.topics.push(page);
    else if (pathname.includes('/platforms/')) records.platforms.push(page);
    else if (pathname.includes('/hybrids/')) records.hybrids.push(page);
    else if (pathname.includes('/clusters/')) records.clusters.push(page);
    else if (
      pathname.includes('/html-sitemap/') ||
      pathname.includes('/random') ||
      pathname.includes('/revisit') ||
      pathname.includes('/runway/')
    ) {
      records.explore.push(page);
    } else {
      records.core.push(page);
    }
  }

  const bucketDefs = [
    { name: 'core', records: records.core },
    { name: 'topics', records: records.topics },
    { name: 'platforms', records: records.platforms },
    { name: 'hybrids', records: records.hybrids },
    { name: 'clusters', records: records.clusters },
    { name: 'explore', records: records.explore }
  ];

  const sitemapIndexRecords = [];

  for (const bucket of bucketDefs) {
    const relPath = path.join('sitemaps', `${bucket.name}.xml`);
    const xml = renderUrlSet(bucket.records);
    const latest = getLatestLastmod(bucket.records) || isoDateTimeUTC(NOW);
    const result = await addXmlRecord(relPath, xml, bucket.name, latest);
    sitemapIndexRecords.push(result);
  }

  return sitemapIndexRecords;
}

async function writeSitemapIndex(sitemapRecords) {
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapRecords.map((record) => `  <sitemap>
    <loc>${escapeXml(record.loc)}</loc>
    <lastmod>${escapeXml(record.lastmod)}</lastmod>
  </sitemap>`).join('\n')}
</sitemapindex>
`;
  await fsp.writeFile(DISCOVERY_SITEMAP_PATH, xml, 'utf8');
}

function renderUrlSet(records) {
  const deduped = dedupeByLoc(records).sort((a, b) => a.loc.localeCompare(b.loc));
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${deduped.map((record) => `  <url>
    <loc>${escapeXml(record.loc)}</loc>
    <lastmod>${escapeXml(record.lastmod)}</lastmod>
  </url>`).join('\n')}
</urlset>
`;
}

function dedupeByLoc(records) {
  const seen = new Map();
  for (const record of records) {
    const existing = seen.get(record.loc);
    if (!existing || new Date(record.lastmod).getTime() > new Date(existing.lastmod).getTime()) {
      seen.set(record.loc, record);
    }
  }
  return [...seen.values()];
}

function getLatestLastmod(records) {
  if (!records.length) return '';
  return records.reduce((latest, record) => {
    return new Date(record.lastmod).getTime() > new Date(latest).getTime() ? record.lastmod : latest;
  }, records[0].lastmod);
}

async function writePage(relDir, html) {
  const outDir = path.join(DISCOVERY_DIR, relDir);
  await ensureDir(outDir);
  await fsp.writeFile(path.join(outDir, 'index.html'), html, 'utf8');
}

function renderListingPage({
  pageTitle,
  metaDescription,
  canonicalPath,
  heroEyebrow,
  heroTitle,
  heroText,
  entries,
  navigation,
  breadcrumb,
  pager = '',
  extraSections = []
}) {
  const sections = [
    renderBreadcrumbs(breadcrumb),
    renderEntriesSection(entries),
    pager ? renderRawSection(pager) : '',
    ...extraSections
  ].filter(Boolean);

  return renderShell({
    pageTitle,
    metaDescription,
    canonicalPath,
    heroEyebrow,
    heroTitle,
    heroText,
    navigation,
    sections
  });
}

function renderHtmlSitemapPage({
  pageTitle,
  metaDescription,
  canonicalPath,
  heroEyebrow,
  heroTitle,
  heroText,
  entries,
  navigation,
  breadcrumb,
  pager = ''
}) {
  const listItems = entries.map((entry) => {
    return `<li><a href="${escapeHtml(entry.sourceUrl)}">${escapeHtml(entry.discoveryLabel)}</a><span>${escapeHtml(entry.sourcePath)}</span></li>`;
  }).join('\n');

  const sections = [
    renderBreadcrumbs(breadcrumb),
    `<section class="section">
      <div class="container">
        <div class="panel">
          <h2>HTML sitemap links</h2>
          <ul class="html-sitemap-list">
            ${listItems}
          </ul>
        </div>
      </div>
    </section>`,
    pager ? renderRawSection(pager) : ''
  ];

  return renderShell({
    pageTitle,
    metaDescription,
    canonicalPath,
    heroEyebrow,
    heroTitle,
    heroText,
    navigation,
    sections
  });
}

function renderTaxonomyIndexPage({
  pageTitle,
  metaDescription,
  canonicalPath,
  heroEyebrow,
  heroTitle,
  heroText,
  items,
  kind,
  basePath,
  navigation,
  breadcrumb,
  extraSections = []
}) {
  const cards = items.map((item) => renderTaxonomyCard(kind, item.label, item.entries.length, `${basePath}${item.slug}/`));

  const sections = [
    renderBreadcrumbs(breadcrumb),
    renderLinkCardsSection(`${kind} hubs`, cards),
    ...extraSections
  ];

  return renderShell({
    pageTitle,
    metaDescription,
    canonicalPath,
    heroEyebrow,
    heroTitle,
    heroText,
    navigation,
    sections
  });
}

function renderTaxonomyChildPage({
  pageTitle,
  metaDescription,
  canonicalPath,
  heroEyebrow,
  heroTitle,
  heroText,
  entries,
  kind,
  item,
  navigation,
  breadcrumb,
  extraSections = []
}) {
  const sections = [
    renderBreadcrumbs(breadcrumb),
    renderCardGridSection('Overview', [
      buildStatCard('Type', kind, null, true),
      buildStatCard('Grouped pages', String(entries.length), null, true),
      buildStatCard('Freshest update', formatDateDisplay(item.entries[0]?.lastmodDate || NOW), null, true)
    ]),
    renderEntriesSection(entries),
    ...extraSections,
    renderLinkCardsSection('Related discovery jumps', buildRelatedJumpCards(item, kind))
  ];

  return renderShell({
    pageTitle,
    metaDescription,
    canonicalPath,
    heroEyebrow,
    heroTitle,
    heroText,
    navigation,
    sections
  });
}

function renderTodayTopicsPage({ pageTitle, metaDescription, canonicalPath, heroEyebrow, heroTitle, heroText, items, navigation, breadcrumb }) {
  const cards = items.map((item) => {
    return renderTaxonomyCard('Topic', item.label, item.todayEntries.length, taxonomyUrl('topics', item.slug), `${item.todayEntries.length} today`);
  });

  const sections = [
    renderBreadcrumbs(breadcrumb),
    renderLinkCardsSection('Topics with updates today', cards)
  ];

  return renderShell({
    pageTitle,
    metaDescription,
    canonicalPath,
    heroEyebrow,
    heroTitle,
    heroText,
    navigation,
    sections
  });
}

function renderLatestPlatformsPage({ pageTitle, metaDescription, canonicalPath, heroEyebrow, heroTitle, heroText, cards, navigation, breadcrumb }) {
  const blocks = cards.map((row) => renderTaxonomyCard('Platform', row.item.label, row.count, taxonomyUrl('platforms', row.item.slug), `${row.count} latest`));

  const sections = [
    renderBreadcrumbs(breadcrumb),
    renderLinkCardsSection('Platforms represented in the latest set', blocks)
  ];

  return renderShell({
    pageTitle,
    metaDescription,
    canonicalPath,
    heroEyebrow,
    heroTitle,
    heroText,
    navigation,
    sections
  });
}

function renderEntriesSection(entries) {
  return renderLinkCardsSection('Source pages', entries.map(renderEntryCard));
}

function renderEntryCard(entry) {
  const tags = [
    ...entry.platformLabels.slice(0, 2).map((label) => `<span class="tag">${escapeHtml(label)}</span>`),
    ...entry.topicLabels.slice(0, 3).map((label) => `<span class="tag">${escapeHtml(label)}</span>`)
  ].join('');

  return `<a class="card" href="${escapeHtml(entry.sourceUrl)}">
    <div class="card-eyebrow">Source page</div>
    <h3>${escapeHtml(entry.discoveryLabel)}</h3>
    <p>${escapeHtml(entry.metaDescription || entry.sourceLabel)}</p>
    <div class="card-meta">
      <span>${escapeHtml(formatDateDisplay(entry.lastmodDate))}</span>
      <span>${escapeHtml(entry.sourcePath)}</span>
    </div>
    <div class="tag-row">${tags}</div>
  </a>`;
}

function renderTaxonomyCard(kind, label, count, href, countOverrideText) {
  const countText = countOverrideText || `${count} pages`;
  return `<a class="card" href="${escapeHtml(joinUrl(SITE_URL, href))}">
    <div class="card-eyebrow">${escapeHtml(kind)}</div>
    <h3>${escapeHtml(label)}</h3>
    <p>${escapeHtml(countText)}</p>
    <div class="card-meta">
      <span>Open ${escapeHtml(kind.toLowerCase())} page</span>
    </div>
  </a>`;
}

function buildStatCard(title, value, href = null, plain = false) {
  const inner = `
    <div class="card-eyebrow">Overview</div>
    <h3>${escapeHtml(title)}</h3>
    <p>${escapeHtml(value)}</p>
  `;
  if (!href || plain) return `<div class="card card-static">${inner}</div>`;
  return `<a class="card" href="${escapeHtml(href)}">${inner}</a>`;
}

function renderCardGridSection(title, cards) {
  return `<section class="section">
    <div class="container">
      <div class="section-head">
        <h2>${escapeHtml(title)}</h2>
      </div>
      <div class="card-grid">
        ${cards.join('\n')}
      </div>
    </div>
  </section>`;
}

function renderLinkCardsSection(title, cards) {
  if (!cards.length) return '';
  return `<section class="section">
    <div class="container">
      <div class="section-head">
        <h2>${escapeHtml(title)}</h2>
      </div>
      <div class="card-grid">
        ${cards.join('\n')}
      </div>
    </div>
  </section>`;
}

function renderRawSection(content) {
  return `<section class="section"><div class="container">${content}</div></section>`;
}

function renderPagination(basePath, totalPages, currentPage) {
  if (totalPages <= 1) return '';
  const links = [];
  for (let i = 1; i <= totalPages; i += 1) {
    const href = i === 1 ? basePath : `${basePath}page/${i}/`;
    links.push(`<a class="pager-link ${i === currentPage ? 'active' : ''}" href="${escapeHtml(joinUrl(SITE_URL, href))}">${i}</a>`);
  }
  return `<div class="panel pager-panel">
    <h2>Pages</h2>
    <div class="pager">${links.join('')}</div>
  </div>`;
}

function renderBreadcrumbs(items) {
  const html = items.map((item, index) => {
    const isLast = index === items.length - 1;
    if (!item.href || isLast) {
      return `<span>${escapeHtml(item.label)}</span>`;
    }
    return `<a href="${escapeHtml(joinUrl(SITE_URL, item.href))}">${escapeHtml(item.label)}</a>`;
  }).join('<span class="crumb-sep">/</span>');

  return `<section class="section section-tight">
    <div class="container">
      <nav class="breadcrumbs">${html}</nav>
    </div>
  </section>`;
}

function renderShell({
  pageTitle,
  metaDescription,
  canonicalPath,
  heroEyebrow,
  heroTitle,
  heroText,
  navigation,
  sections
}) {
  const canonicalUrl = joinUrl(SITE_URL, canonicalPath);
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>${escapeHtml(pageTitle)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="${escapeHtml(metaDescription)}">
  <link rel="canonical" href="${escapeHtml(canonicalUrl)}">
  <meta property="og:title" content="${escapeHtml(pageTitle)}">
  <meta property="og:description" content="${escapeHtml(metaDescription)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="${escapeHtml(canonicalUrl)}">
  <meta name="twitter:card" content="summary_large_image">
  <style>
    :root{
      --bg:#08111d;
      --bg2:#0d1726;
      --panel:#0f1c30;
      --panel2:#12233d;
      --line:rgba(255,255,255,.08);
      --text:#eef4ff;
      --muted:#a9b7d0;
      --accent:#6ea8ff;
      --accent2:#9fd0ff;
      --good:#7fe8c3;
      --shadow:0 18px 50px rgba(0,0,0,.28);
      --radius:20px;
      --max:1200px;
    }
    *{box-sizing:border-box}
    html,body{margin:0;padding:0;background:
      radial-gradient(circle at top left, rgba(110,168,255,.14), transparent 28%),
      radial-gradient(circle at top right, rgba(127,232,195,.08), transparent 24%),
      linear-gradient(180deg,var(--bg),var(--bg2));
      color:var(--text);
      font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    }
    a{color:inherit;text-decoration:none}
    .container{max-width:var(--max);margin:0 auto;padding:0 20px}
    .topbar{
      position:sticky;top:0;z-index:40;
      background:rgba(8,17,29,.78);
      backdrop-filter:blur(12px);
      border-bottom:1px solid var(--line);
    }
    .topbar-inner{
      display:flex;align-items:center;justify-content:space-between;gap:20px;
      min-height:72px;
    }
    .brand{display:flex;align-items:center;gap:12px;font-weight:800;letter-spacing:.01em}
    .brand-mark{
      width:40px;height:40px;border-radius:12px;
      background:linear-gradient(135deg,var(--accent),var(--accent2));
      display:grid;place-items:center;color:#061120;font-weight:900;
      box-shadow:var(--shadow);
    }
    .top-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
    .btn{
      display:inline-flex;align-items:center;justify-content:center;
      min-height:44px;padding:0 16px;border-radius:999px;
      border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--text);
      font-weight:700;
    }
    .btn-primary{
      background:linear-gradient(135deg,var(--accent),var(--accent2));
      color:#061120;border:none;
    }
    .hero{padding:52px 0 24px}
    .hero-panel{
      background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,.02));
      border:1px solid var(--line);
      border-radius:28px;
      padding:34px;
      box-shadow:var(--shadow);
    }
    .eyebrow{
      display:inline-flex;align-items:center;gap:8px;
      padding:8px 12px;border-radius:999px;
      background:rgba(110,168,255,.12);
      border:1px solid rgba(110,168,255,.2);
      color:var(--accent2);
      font-size:13px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;
      margin-bottom:14px;
    }
    h1{
      margin:0 0 14px;
      font-size:clamp(34px,5vw,56px);
      line-height:1.02;
      letter-spacing:-.03em;
      max-width:950px;
    }
    .hero p{
      margin:0;
      max-width:860px;
      color:var(--muted);
      font-size:18px;
      line-height:1.65;
    }
    .quick-nav{
      margin-top:22px;
      display:flex;flex-wrap:wrap;gap:10px;
    }
    .quick-nav a{
      padding:10px 14px;border-radius:999px;
      background:rgba(255,255,255,.03);
      border:1px solid var(--line);
      color:var(--muted);
      font-weight:700;font-size:14px;
    }
    .section{padding:12px 0 22px}
    .section-tight{padding:0 0 6px}
    .section-head{margin-bottom:14px}
    .section-head h2{margin:0;font-size:28px;letter-spacing:-.02em}
    .breadcrumbs{
      display:flex;flex-wrap:wrap;gap:10px;align-items:center;
      color:var(--muted);font-size:14px;
    }
    .breadcrumbs a{color:var(--accent2)}
    .crumb-sep{opacity:.5}
    .card-grid{
      display:grid;
      grid-template-columns:repeat(auto-fit,minmax(255px,1fr));
      gap:16px;
    }
    .card,.panel{
      background:linear-gradient(180deg,var(--panel),var(--panel2));
      border:1px solid var(--line);
      border-radius:var(--radius);
      box-shadow:var(--shadow);
    }
    .card{
      padding:20px;
      transition:transform .16s ease,border-color .16s ease,background .16s ease;
      min-height:210px;
      display:flex;flex-direction:column;
    }
    .card:hover{transform:translateY(-2px);border-color:rgba(110,168,255,.28)}
    .card-static:hover{transform:none}
    .card-eyebrow{
      color:var(--good);
      font-size:12px;
      font-weight:800;
      letter-spacing:.08em;
      text-transform:uppercase;
      margin-bottom:10px;
    }
    .card h3{
      margin:0 0 10px;
      font-size:22px;
      line-height:1.18;
      letter-spacing:-.02em;
    }
    .card p{
      margin:0;
      color:var(--muted);
      line-height:1.6;
      flex:1;
    }
    .card-meta{
      margin-top:16px;
      display:flex;flex-wrap:wrap;gap:8px 14px;
      color:var(--muted);
      font-size:13px;
    }
    .tag-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
    .tag{
      display:inline-flex;align-items:center;
      padding:6px 10px;border-radius:999px;
      background:rgba(255,255,255,.04);
      border:1px solid var(--line);
      color:var(--muted);font-size:12px;font-weight:700;
    }
    .panel{padding:22px}
    .panel h2{margin:0 0 14px;font-size:24px}
    .html-sitemap-list{
      list-style:none;padding:0;margin:0;
      display:grid;grid-template-columns:1fr;gap:12px;
    }
    .html-sitemap-list li{
      display:flex;flex-direction:column;gap:4px;
      padding:12px 0;border-top:1px solid var(--line);
    }
    .html-sitemap-list li:first-child{border-top:none;padding-top:0}
    .html-sitemap-list a{font-weight:700;color:var(--text)}
    .html-sitemap-list span{color:var(--muted);font-size:13px}
    .pager-panel{margin-top:10px}
    .pager{display:flex;flex-wrap:wrap;gap:10px}
    .pager-link{
      min-width:42px;height:42px;border-radius:12px;display:grid;place-items:center;
      border:1px solid var(--line);background:rgba(255,255,255,.03);font-weight:800;
    }
    .pager-link.active{
      background:linear-gradient(135deg,var(--accent),var(--accent2));
      color:#061120;border:none;
    }
    .footer{padding:26px 0 48px}
    .footer-panel{
      display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;
      color:var(--muted);
    }
    @media (max-width:700px){
      .hero-panel{padding:24px}
      .topbar-inner{min-height:66px}
      .top-actions{gap:8px}
      .btn{min-height:40px;padding:0 14px}
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="container topbar-inner">
      <a class="brand" href="${escapeHtml(SITE_URL)}">
        <span class="brand-mark">V</span>
        <span>Scam Check Now</span>
      </a>
      <div class="top-actions">
        <a class="btn" href="${escapeHtml(joinUrl(SITE_URL, '/app/'))}">📱 Get App</a>
        <a class="btn btn-primary" href="${escapeHtml(joinUrl(SITE_URL, '/'))}">Run Check</a>
      </div>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="container">
        <div class="hero-panel">
          <div class="eyebrow">${escapeHtml(heroEyebrow)}</div>
          <h1>${escapeHtml(heroTitle)}</h1>
          <p>${escapeHtml(heroText)}</p>
          <div class="quick-nav">
            ${navigation.map((item) => `<a href="${escapeHtml(joinUrl(SITE_URL, item.href))}">${escapeHtml(item.label)}</a>`).join('')}
          </div>
        </div>
      </div>
    </section>

    ${sections.join('\n')}
  </main>

  <footer class="footer">
    <div class="container">
      <div class="panel footer-panel">
        <div>Discovery-B generated from local scam-check-now-b pages.</div>
        <div>
          <a href="${escapeHtml(joinUrl(SITE_URL, DISCOVERY_BASE, '/html-sitemap/'))}">HTML Sitemap</a>
          ·
          <a href="${escapeHtml(joinUrl(SITE_URL, '/discovery-b-sitemap.xml'))}">XML Sitemap</a>
          ·
          <a href="${escapeHtml(joinUrl(SITE_URL, DISCOVERY_BASE, '/feed.xml'))}">Feed</a>
        </div>
      </div>
    </div>
  </footer>
</body>
</html>`;
}

function buildNavigation(stats) {
  return [
    { label: 'Hub', href: `${DISCOVERY_BASE}/` },
    { label: `Latest (${stats.latestCount})`, href: `${DISCOVERY_BASE}/latest/` },
    { label: `Today (${stats.todayCount})`, href: `${DISCOVERY_BASE}/today/` },
    { label: `This Week (${stats.thisWeekCount})`, href: `${DISCOVERY_BASE}/this-week/` },
    { label: 'Runway', href: `${DISCOVERY_BASE}/runway/` },
    { label: `Topics (${stats.topicCount})`, href: `${DISCOVERY_BASE}/topics/` },
    { label: `Platforms (${stats.platformCount})`, href: `${DISCOVERY_BASE}/platforms/` },
    { label: `Clusters (${stats.clusterCount})`, href: `${DISCOVERY_BASE}/clusters/` },
    { label: `Hybrids (${stats.hybridCount})`, href: `${DISCOVERY_BASE}/hybrids/` },
    { label: 'Random', href: `${DISCOVERY_BASE}/random/` },
    { label: 'Revisit', href: `${DISCOVERY_BASE}/revisit/` },
    { label: 'HTML Sitemap', href: `${DISCOVERY_BASE}/html-sitemap/` }
  ];
}

function buildRelatedJumpCards(item, kind) {
  const cards = [];
  if (kind !== 'Topic') {
    cards.push(renderTaxonomyCard('Topics', 'View all topics', 0, `${DISCOVERY_BASE}/topics/`, 'Browse'));
  }
  if (kind !== 'Platform') {
    cards.push(renderTaxonomyCard('Platforms', 'View all platforms', 0, `${DISCOVERY_BASE}/platforms/`, 'Browse'));
  }
  if (kind !== 'Cluster') {
    cards.push(renderTaxonomyCard('Clusters', 'View all clusters', 0, `${DISCOVERY_BASE}/clusters/`, 'Browse'));
  }
  if (kind !== 'Hybrid') {
    cards.push(renderTaxonomyCard('Hybrids', 'View all hybrids', 0, `${DISCOVERY_BASE}/hybrids/`, 'Browse'));
  }
  cards.push(renderTaxonomyCard('Latest', 'Latest discovery pages', 0, `${DISCOVERY_BASE}/latest/`, 'Open'));
  return cards;
}

function topTopicCardsFromEntries(entries, topicPages, maxCards) {
  const counts = new Map();

  for (const entry of entries) {
    for (const topic of entry.topicLabels) {
      counts.set(topic, (counts.get(topic) || 0) + 1);
    }
  }

  const topicByLabel = new Map(topicPages.map((item) => [item.label, item]));
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, maxCards)
    .map(([label, count]) => {
      const item = topicByLabel.get(label);
      if (!item) {
        return renderTaxonomyCard('Topic', label, count, `${DISCOVERY_BASE}/topics/`, `${count} pages`);
      }
      return renderTaxonomyCard('Topic', label, count, taxonomyUrl('topics', item.slug), `${count} pages`);
    });
}

function topPlatformCardsFromEntries(entries, platformPages, maxCards) {
  const counts = new Map();

  for (const entry of entries) {
    for (const platform of entry.platformLabels) {
      counts.set(platform, (counts.get(platform) || 0) + 1);
    }
  }

  const platformByLabel = new Map(platformPages.map((item) => [item.label, item]));
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, maxCards)
    .map(([label, count]) => {
      const item = platformByLabel.get(label);
      if (!item) {
        return renderTaxonomyCard('Platform', label, count, `${DISCOVERY_BASE}/platforms/`, `${count} pages`);
      }
      return renderTaxonomyCard('Platform', label, count, taxonomyUrl('platforms', item.slug), `${count} pages`);
    });
}

function taxonomyUrl(kind, slug) {
  return `${DISCOVERY_BASE}/${kind}/${slug}/`;
}

function paginate(items, pageSize) {
  if (!items.length) return [[]];
  const pages = [];
  for (let i = 0; i < items.length; i += pageSize) {
    pages.push(items.slice(i, i + pageSize));
  }
  return pages;
}

function stableShuffle(items, seed) {
  return [...items]
    .map((item) => ({
      item,
      weight: sha1(`${seed}:${item.sourceUrl}`)
    }))
    .sort((a, b) => a.weight.localeCompare(b.weight))
    .map((row) => row.item);
}

function sha1(value) {
  return crypto.createHash('sha1').update(String(value)).digest('hex');
}

function prettifySlug(slug) {
  const piece = String(slug || '')
    .split('/')
    .filter(Boolean)
    .pop() || '';
  return piece
    .replace(/[-_]+/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .trim();
}

function prettifyToken(token) {
  const lower = String(token || '').toLowerCase();
  if (PLATFORM_SYNONYMS[lower]) return PLATFORM_SYNONYMS[lower];
  return lower.replace(/\b\w/g, (c) => c.toUpperCase());
}

function slugify(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-{2,}/g, '-');
}

function joinUrl(...parts) {
  const safeParts = parts.filter((part) => part !== undefined && part !== null).map((part) => String(part));
  if (!safeParts.length) return '/';

  const first = safeParts[0];
  const hasAbsoluteBase = /^https?:\/\//i.test(first);
  const lastHadTrailingSlash = /\/$/.test(safeParts[safeParts.length - 1]);

  if (hasAbsoluteBase) {
    const base = first.replace(/\/+$/, '') + '/';
    const normalizedPath = safeParts
      .slice(1)
      .map((part) => part.replace(/^\/+|\/+$/g, ''))
      .filter(Boolean)
      .join('/');

    const url = normalizedPath ? new URL(normalizedPath, base).toString() : new URL('', base).toString();
    if (lastHadTrailingSlash) {
      return url.endsWith('/') ? url : `${url}/`;
    }
    return url.endsWith('/') && normalizedPath ? url.slice(0, -1) : url;
  }

  const pathOnly = safeParts
    .map((part, index) => {
      if (index === 0) return part.replace(/\/+$/, '');
      return part.replace(/^\/+|\/+$/g, '');
    })
    .filter(Boolean)
    .join('/');

  let result = pathOnly.startsWith('/') ? pathOnly : `/${pathOnly}`;
  result = result.replace(/\/{2,}/g, '/');

  if (lastHadTrailingSlash && !result.endsWith('/')) result += '/';
  if (!lastHadTrailingSlash && result.length > 1 && result.endsWith('/')) result = result.slice(0, -1);

  return result || '/';
}

function relDirToUrl(relDir) {
  if (!relDir) return '/';
  return `/${String(relDir).replace(/\\/g, '/').replace(/^\/+|\/+$/g, '')}/`;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeXml(value) {
  return escapeHtml(value).replace(/'/g, '&apos;');
}

function formatDateUTC(date) {
  const d = new Date(date);
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`;
}

function isoDateTimeUTC(date) {
  return new Date(date).toISOString();
}

function startOfWeekUTC(date) {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  const day = d.getUTCDay();
  const diff = (day + 6) % 7;
  d.setUTCDate(d.getUTCDate() - diff);
  d.setUTCHours(0, 0, 0, 0);
  return d;
}

function addDaysUTC(date, days) {
  const d = new Date(date);
  d.setUTCDate(d.getUTCDate() + days);
  return d;
}

function pad(value) {
  return String(value).padStart(2, '0');
}

function formatDateDisplay(date) {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC'
  });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});


