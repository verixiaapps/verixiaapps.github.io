const fs = require("fs");
const path = require("path");

const BASE_URL = "https://verixiaapps.com";
const CHECK_DIR = path.join(__dirname, "../check");
const OUTPUT_BASE = path.join(__dirname, "../discovery-c");

// ensure folders exist
function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

// get all pages
function getAllPages(dir) {
  let results = [];
  const list = fs.readdirSync(dir);

  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat && stat.isDirectory()) {
      results = results.concat(getAllPages(filePath));
    } else if (file.endsWith(".html")) {
      results.push(filePath);
    }
  });

  return results;
}

// convert to URL
function toUrl(file) {
  const relative = file
    .replace(CHECK_DIR, "")
    .replace(/\\/g, "/")
    .replace(".html", "");

  return BASE_URL + "/check" + relative;
}

// build HTML page
function buildPage(title, description, links) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title>
<meta name="description" content="${description}">
<meta name="robots" content="index,follow">
</head>
<body>

<h1>${title}</h1>
<p>${description}</p>

<ul>
${links.map(l => `<li><a href="${l}">${l.replace(BASE_URL + "/check/", "").replace(/-/g," ")}</a></li>`).join("\n")}
</ul>

</body>
</html>`;
}

// MAIN
function run() {
  const pages = getAllPages(CHECK_DIR);

  // newest
  const newest = [...pages].sort((a,b) => fs.statSync(b).mtime - fs.statSync(a).mtime);

  // random
  const shuffled = [...pages].sort(() => 0.5 - Math.random());

  const latest = newest.slice(0, 200).map(toUrl);
  const today = newest.slice(0, 100).map(toUrl);
  const all = pages.slice(0, 1000).map(toUrl);
  const random = shuffled.slice(0, 200).map(toUrl);

  // create dirs
  const dirs = ["latest","today","all","hub","random"];
  dirs.forEach(d => ensureDir(path.join(OUTPUT_BASE, d)));

  // write pages
  fs.writeFileSync(
    path.join(OUTPUT_BASE, "latest/index.html"),
    buildPage("Latest Scam Checks", "Newest scam pages updated continuously.", latest)
  );

  fs.writeFileSync(
    path.join(OUTPUT_BASE, "today/index.html"),
    buildPage("Today's Scam Alerts", "Fresh scam pages added today.", today)
  );

  fs.writeFileSync(
    path.join(OUTPUT_BASE, "all/index.html"),
    buildPage("All Scam Checks", "Browse all scam detection pages.", all)
  );

  fs.writeFileSync(
    path.join(OUTPUT_BASE, "random/index.html"),
    buildPage("Random Scam Checks", "Explore random scam pages.", random)
  );

  // simple hub (same as latest for now)
  fs.writeFileSync(
    path.join(OUTPUT_BASE, "hub/index.html"),
    buildPage("Scam Detection Hub", "Central page for scam detection topics.", latest)
  );

  console.log("✅ C discovery layer built");
}

run();