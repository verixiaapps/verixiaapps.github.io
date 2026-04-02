import os
import re
import html
from typing import Dict, List, Optional, Set

TARGET_TEMPLATE = os.getenv("TARGET_TEMPLATE", "all").strip().lower()
REFRESH_SCOPE = os.getenv("REFRESH_SCOPE", "pages").strip().lower()
MAX_URLS = int(os.getenv("MAX_URLS_TO_REFRESH", "1"))
DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() == "true"

TEMPLATE_PATHS = {
    "a": "scam-check-now",
    "b": "scam-check-now-b",
    "c": "scam-check-now-c",
}

# IMPORTANT:
# Paste your exact approved shell HTML into these 3 constants.
# Do not change the placeholders inside them.
TEMPLATE_A = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>{{TITLE}}</title>
<meta name="description" content="{{DESCRIPTION}}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{{CANONICAL_URL}}">

<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESCRIPTION}}">
<meta property="og:type" content="website">
<meta property="og:url" content="{{CANONICAL_URL}}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{TITLE}}">
<meta name="twitter:description" content="{{DESCRIPTION}}">

<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@type":"WebPage",
  "name":"{{TITLE}}",
  "description":"{{DESCRIPTION}}",
  "url":"{{CANONICAL_URL}}"
}
</script>

<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"How can I tell if something is a scam?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Look for urgency, requests for money or codes, suspicious links, and messages that pressure you to act quickly. Always verify through official sources."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I clicked a suspicious link?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Avoid entering any information, close the page, run a security check on your device, and change important passwords if needed."
      }
    },
    {
      "@type":"Question",
      "name":"Are scam messages common?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Yes, scam messages are increasingly common across email, text, social media, and messaging apps. They often impersonate trusted companies or people."
      }
    }
  ]
}
</script>

<style>
:root{
--bg:#06101b;
--bg-2:#0a1324;
--bg-3:#0f1b31;
--bg-4:#132341;

--surface:rgba(255,255,255,.05);
--surface-2:rgba(255,255,255,.07);
--surface-3:rgba(255,255,255,.10);
--surface-4:#ffffff;

--card:#101c33;
--card-2:#15233d;
--card-3:#182a48;

--ink:#e9f1ff;
--ink-strong:#ffffff;
--ink-dark:#132033;
--muted:#a7b7d3;
--muted-2:#8296b7;

--line:rgba(148,163,184,.18);
--line-2:rgba(255,255,255,.09);
--line-3:rgba(255,255,255,.14);

--cyan:#66d9ef;
--cyan-2:#28bfd9;
--blue:#5b8cff;
--blue-2:#3f72ee;
--violet:#8b78f2;
--violet-2:#7460e8;
--emerald:#18b67f;
--emerald-2:#109466;
--amber:#e7a93d;
--red:#d96574;
--red-2:#b94b5f;

--blue-soft:#dbeafe;
--violet-soft:#ede9fe;
--green-soft:#ecfdf5;
--amber-soft:#fffbeb;
--red-soft:#fef2f2;

--shadow-xl:0 32px 90px rgba(2,6,23,.46);
--shadow-lg:0 22px 56px rgba(2,6,23,.34);
--shadow-md:0 14px 34px rgba(2,6,23,.24);
--shadow-sm:0 8px 20px rgba(2,6,23,.16);
--shadow-xs:0 4px 12px rgba(2,6,23,.10);

--radius-xl:30px;
--radius-lg:24px;
--radius-md:20px;
--radius-sm:16px;
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
radial-gradient(circle at 14% 8%, rgba(102,217,239,.10), transparent 22%),
radial-gradient(circle at 84% 0%, rgba(139,120,242,.14), transparent 26%),
radial-gradient(circle at 50% 100%, rgba(24,182,127,.05), transparent 24%),
linear-gradient(180deg,var(--bg) 0%, var(--bg-2) 34%, var(--bg-3) 70%, var(--bg-4) 100%);
}

a{
color:#9cecff;
text-decoration:none;
}

a:hover{
text-decoration:underline;
}

button,
textarea,
input{
font-family:inherit;
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
background:rgba(10,18,35,.62);
border:1px solid rgba(255,255,255,.10);
backdrop-filter:blur(14px);
box-shadow:var(--shadow-sm);
text-decoration:none;
}

.logo:hover{
text-decoration:none;
border-color:rgba(255,255,255,.16);
background:rgba(12,21,39,.72);
}

.logo-dot{
width:10px;
height:10px;
border-radius:50%;
background:linear-gradient(180deg,var(--cyan) 0%,var(--violet) 100%);
box-shadow:0 0 0 4px rgba(139,120,242,.12);
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
border:1px solid rgba(255,255,255,.11);
white-space:nowrap;
background:linear-gradient(180deg,rgba(255,255,255,.12) 0%,rgba(255,255,255,.06) 100%);
backdrop-filter:blur(10px);
box-shadow:var(--shadow-xs);
}

.app-top:hover{
text-decoration:none;
background:linear-gradient(180deg,rgba(255,255,255,.16) 0%,rgba(255,255,255,.07) 100%);
}

.upgrade-top{
pointer-events:auto;
padding:11px 15px;
font-size:14px;
border-radius:16px;
font-weight:900;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
border:none;
cursor:pointer;
white-space:nowrap;
box-shadow:0 14px 28px rgba(40,191,217,.14);
transition:transform .15s ease, box-shadow .15s ease, opacity .15s ease;
}

.upgrade-top:hover{
transform:translateY(-1px);
box-shadow:0 18px 34px rgba(40,191,217,.18);
}

.page-shell{
max-width:940px;
margin:0 auto;
padding:0 14px 40px;
}

.hero{
position:relative;
padding:18px 8px 24px;
max-width:980px;
margin:0 auto 14px;
text-align:center;
}

.hero-badge-row{
display:flex;
flex-wrap:wrap;
justify-content:center;
gap:10px;
margin-bottom:16px;
}

.hero-badge{
display:inline-flex;
align-items:center;
justify-content:center;
gap:8px;
padding:9px 13px;
border-radius:999px;
font-size:12px;
font-weight:900;
letter-spacing:.01em;
color:#d9e8ff;
background:rgba(255,255,255,.07);
border:1px solid rgba(255,255,255,.09);
backdrop-filter:blur(10px);
box-shadow:var(--shadow-xs);
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
color:#c8d7ec;
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
color:#dde9fb;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
box-shadow:var(--shadow-xs);
}

.container,
.content-section{
max-width:820px;
margin:auto;
padding:24px;
border-radius:var(--radius-xl);
position:relative;
overflow:hidden;
border:1px solid rgba(255,255,255,.10);
background:
linear-gradient(180deg, rgba(17,28,51,.95) 0%, rgba(11,19,36,.985) 100%);
box-shadow:var(--shadow-xl);
}

.container::before,
.content-section::before{
content:"";
position:absolute;
top:-120px;
right:-90px;
width:260px;
height:260px;
border-radius:50%;
background:radial-gradient(circle, rgba(102,217,239,.11), transparent 65%);
pointer-events:none;
}

.container::after,
.content-section::after{
content:"";
position:absolute;
left:-80px;
bottom:-120px;
width:220px;
height:220px;
border-radius:50%;
background:radial-gradient(circle, rgba(139,120,242,.08), transparent 68%);
pointer-events:none;
}

.container > *,
.content-section > *{
position:relative;
z-index:1;
}

.system-badge{
display:flex;
justify-content:center;
align-items:center;
gap:8px;
margin-bottom:14px;
font-size:11px;
font-weight:900;
color:#99eaff;
letter-spacing:.10em;
text-transform:uppercase;
text-align:center;
}

.preview-card,
.tool-shell,
.app-link-card,
.upgrade,
.inline-info-card{
background:linear-gradient(180deg, rgba(255,255,255,.075) 0%, rgba(255,255,255,.04) 100%);
border:1px solid rgba(255,255,255,.10);
border-radius:var(--radius-lg);
box-shadow:var(--shadow-md);
}

.preview-card{
position:relative;
margin-bottom:20px;
padding:20px;
background:
linear-gradient(135deg, rgba(217,101,116,.10) 0%, rgba(139,120,242,.08) 56%, rgba(102,217,239,.06) 100%),
linear-gradient(180deg, rgba(255,255,255,.075) 0%, rgba(255,255,255,.04) 100%);
overflow:hidden;
}

.preview-card::before{
content:"";
position:absolute;
inset:0;
background:
radial-gradient(circle at top right, rgba(217,101,116,.10), transparent 34%),
radial-gradient(circle at bottom left, rgba(102,217,239,.08), transparent 38%);
pointer-events:none;
}

.preview-card > *{
position:relative;
z-index:1;
}

.preview-top{
display:flex;
align-items:flex-start;
justify-content:space-between;
gap:12px;
flex-wrap:wrap;
}

.preview-badge{
display:inline-flex;
align-items:center;
gap:8px;
padding:8px 14px;
border-radius:999px;
background:linear-gradient(135deg,var(--red) 0%,var(--red-2) 100%);
color:#fff;
font-size:11px;
font-weight:900;
letter-spacing:.03em;
box-shadow:0 10px 20px rgba(185,75,95,.14);
line-height:1;
}

.preview-score-wrap{
display:flex;
flex-direction:column;
gap:7px;
min-width:154px;
flex:0 0 auto;
}

.preview-score{
padding:8px 10px;
border-radius:999px;
background:rgba(255,255,255,.08);
border:1px solid rgba(255,255,255,.11);
font-size:11px;
font-weight:900;
color:#ffe2e6;
text-align:center;
line-height:1.1;
}

.preview-score-bar{
height:8px;
border-radius:999px;
background:rgba(255,255,255,.07);
overflow:hidden;
border:1px solid rgba(255,255,255,.09);
}

.preview-score-fill{
height:100%;
width:18%;
background:linear-gradient(90deg,#d96574 0%, #c55467 60%, #a94458 100%);
border-radius:999px;
box-shadow:none;
}

.preview-domain{
margin-top:14px;
font-size:26px;
font-weight:900;
line-height:1.06;
color:#fff;
letter-spacing:-.03em;
word-break:break-word;
}

.preview-sub{
margin-top:6px;
font-size:13px;
color:#d8e5f8;
font-weight:800;
line-height:1.5;
}

.preview-signals{
margin-top:14px;
display:grid;
gap:10px;
}

.preview-signal{
display:flex;
align-items:flex-start;
gap:10px;
padding:12px 13px;
border-radius:16px;
background:rgba(255,255,255,.055);
border:1px solid rgba(255,255,255,.08);
font-size:13px;
font-weight:850;
color:#fde8ec;
line-height:1.45;
}

.preview-signal-icon{
width:18px;
height:18px;
display:flex;
align-items:center;
justify-content:center;
font-size:12px;
flex:0 0 18px;
line-height:1;
}

.tool-shell{
padding:24px;
margin-top:0;
background:
linear-gradient(135deg, rgba(102,217,239,.08) 0%, rgba(139,120,242,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.045) 100%);
border-color:rgba(255,255,255,.11);
}

textarea,input{
width:100%;
padding:16px 16px;
margin-top:12px;
border-radius:18px;
border:1.5px solid rgba(255,255,255,.11);
font-size:16px;
background:rgba(7,16,29,.76);
color:#eef6ff;
box-shadow:none;
transition:border-color .15s ease, box-shadow .15s ease, background .15s ease;
}

textarea{
height:156px;
resize:none;
}

textarea::placeholder,
input::placeholder{
color:#89a0c4;
}

textarea:focus,
input:focus{
outline:none;
border-color:rgba(102,217,239,.48);
box-shadow:0 0 0 5px rgba(102,217,239,.08);
background:rgba(8,18,33,.86);
}

button{
border:none;
border-radius:18px;
cursor:pointer;
font-size:16px;
padding:16px;
min-height:50px;
}

.check{
width:100%;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
margin-top:18px;
font-weight:900;
font-size:18px;
letter-spacing:.2px;
box-shadow:0 16px 34px rgba(40,191,217,.16);
transition:transform .15s ease, box-shadow .15s ease, opacity .15s ease;
}

.check:hover{
transform:translateY(-1px);
box-shadow:0 20px 40px rgba(40,191,217,.20);
}

.check:active{
transform:scale(.985);
}

.note,
.input-help{
margin-top:12px;
font-size:14px;
color:#a4b6d2;
text-align:center;
text-wrap:balance;
}

.success{
margin-top:12px;
font-size:14px;
color:#86efac;
text-align:center;
font-weight:900;
display:none;
}

.app-link-card{
margin-top:20px;
padding:22px;
text-align:center;
background:
linear-gradient(135deg, rgba(24,182,127,.10) 0%, rgba(102,217,239,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
}

.app-link-card h4{
margin:0 0 6px;
font-size:21px;
color:#fff;
font-weight:900;
letter-spacing:-.02em;
}

.app-link-card p{
margin:0 0 14px;
font-size:14px;
color:#cfddf1;
line-height:1.7;
}

.app-link-button{
display:block;
width:100%;
text-align:center;
background:linear-gradient(135deg,var(--emerald) 0%,var(--cyan-2) 100%);
color:#fff;
font-weight:900;
padding:15px;
border-radius:16px;
box-sizing:border-box;
box-shadow:0 12px 24px rgba(16,148,102,.14);
text-decoration:none;
}

.app-link-button:hover{
text-decoration:none;
}

#result{
margin-top:26px;
display:none;
}

.result-card{
background:rgba(255,255,255,.97);
border-radius:26px;
padding:22px;
box-shadow:var(--shadow-lg);
border:1px solid rgba(15,23,42,.08);
overflow:hidden;
color:var(--ink-dark);
}

.result-card.high{
border:2px solid #f1c8cf;
box-shadow:0 20px 46px rgba(185,75,95,.10);
}

.result-card.medium{
border:2px solid #f4ddb0;
box-shadow:0 20px 46px rgba(231,169,61,.09);
}

.result-card.low{
border:2px solid #c2efd7;
box-shadow:0 20px 46px rgba(24,182,127,.09);
}

.result-card.unknown{
border:1px solid #dbe4f0;
}

.result-top{
display:flex;
align-items:flex-start;
justify-content:space-between;
gap:12px;
flex-wrap:wrap;
}

.risk{
font-size:21px;
font-weight:900;
margin-bottom:0;
padding:11px 16px;
border-radius:999px;
display:inline-flex;
align-items:center;
gap:10px;
letter-spacing:.01em;
box-shadow:var(--shadow-sm);
}

.risk.high{
background:var(--red);
color:#fff;
}
.risk.medium{
background:var(--amber);
color:#fff;
}
.risk.low{
background:var(--emerald);
color:#fff;
}
.risk.unknown{
background:#e5e7eb;
color:#374151;
}

.result-chip{
padding:9px 13px;
border-radius:999px;
font-size:12px;
font-weight:900;
background:#fff;
border:1px solid #d9e2ec;
color:#334155;
box-shadow:var(--shadow-xs);
}

.result-summary{
margin:16px 0 0;
font-size:16px;
color:#334155;
font-weight:800;
line-height:1.58;
}

.result-continuation{
margin-top:14px;
padding:14px 15px;
border-radius:16px;
font-size:14px;
font-weight:900;
line-height:1.55;
background:#f8fafc;
border:1px solid #e2e8f0;
color:#334155;
}

.result-card.high .result-continuation{
background:#fff8f9;
border-color:#eed1d7;
color:#7f1d2c;
}

.result-card.medium .result-continuation{
background:#fffdf7;
border-color:#f4ddb0;
color:#8a5710;
}

.result-card.unknown .result-continuation{
background:#f8fafc;
border-color:#e2e8f0;
color:#334155;
}

.section{
margin-top:18px;
padding:18px;
border-radius:20px;
background:#f8fafc;
border:1px solid #e7eef6;
}

.section-title{
font-weight:900;
margin-bottom:10px;
color:#0f172a;
font-size:16px;
letter-spacing:-.01em;
}

.signal-list{
list-style:none;
padding:0;
margin:0;
display:grid;
gap:10px;
}

.signal-item{
display:flex;
align-items:flex-start;
gap:12px;
padding:14px 15px;
border-radius:16px;
background:#fff;
border:1px solid #e2e8f0;
font-size:14px;
font-weight:800;
color:#334155;
line-height:1.45;
}

.result-card.high .signal-item{
background:#fffafb;
border-color:#f1d2d8;
color:#7f1d2c;
}

.result-card.medium .signal-item{
background:#fffdf7;
border-color:#f4ddb0;
color:#8a5710;
}

.result-card.low .signal-item{
background:#f7fff9;
border-color:#c2efd7;
color:#166534;
}

.signal-icon{
width:22px;
height:22px;
display:flex;
align-items:center;
justify-content:center;
font-size:16px;
line-height:1;
flex:0 0 22px;
}

.action-box{
padding:15px 16px;
border-radius:16px;
background:#eef6ff;
border:1px solid #bfdbfe;
font-size:14px;
font-weight:900;
color:#1e3a8a;
line-height:1.55;
}

.result-payline{
margin-top:18px;
padding:16px;
background:#f8fafc;
border:1px solid #e2e8f0;
border-radius:18px;
font-size:14px;
color:#334155;
font-weight:900;
line-height:1.55;
}

.result-card.high .result-payline{
background:#fff8f9;
border-color:#eed1d7;
color:#7f1d2c;
}

.result-card.medium .result-payline{
background:#fffdf7;
border-color:#f4ddb0;
color:#8a5710;
}

.result-card.low .result-payline{
background:#f7fff9;
border-color:#c2efd7;
color:#166534;
}

.result-actions{
margin-top:16px;
display:grid;
gap:12px;
}

.result-cta{
margin-top:0;
}

.share-wrap{
margin-top:4px;
padding:18px;
border-radius:20px;
background:linear-gradient(180deg,#fff 0%,#f8fafc 100%);
border:1px solid #e2e8f0;
text-align:center;
box-shadow:var(--shadow-xs);
}

.share-alert{
font-size:13px;
font-weight:900;
color:#0f172a;
margin-bottom:6px;
letter-spacing:.01em;
}

.share-copy{
font-size:14px;
font-weight:800;
color:#475569;
line-height:1.55;
margin-bottom:14px;
max-width:560px;
margin-left:auto;
margin-right:auto;
}

.share-grid{
display:grid;
grid-template-columns:repeat(2,minmax(0,1fr));
gap:10px;
}

.share-btn{
display:inline-flex;
align-items:center;
justify-content:center;
gap:8px;
min-height:46px;
padding:12px 14px;
border-radius:14px;
font-size:14px;
font-weight:900;
transition:transform .15s ease, box-shadow .15s ease, background .15s ease;
}

.share-btn:hover{
transform:translateY(-1px);
}

.share-btn.primary{
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
box-shadow:0 10px 20px rgba(40,191,217,.14);
}

.share-btn.dark{
background:linear-gradient(135deg,#111827 0%,#1f2937 100%);
color:#fff;
box-shadow:0 10px 20px rgba(15,23,42,.12);
}

.share-btn.light{
background:#eef2ff;
color:#1e293b;
border:1px solid #dbe3f8;
}

.share-status{
margin-top:12px;
min-height:20px;
font-size:13px;
font-weight:900;
color:#059669;
}

.upgrade{
display:none;
margin-top:28px;
padding:26px 24px;
text-align:center;
background:
linear-gradient(135deg, rgba(139,120,242,.16) 0%, rgba(102,217,239,.13) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.045) 100%);
}

.upgrade h3{
margin:0 0 8px;
font-size:30px;
line-height:1.15;
color:#fff;
text-wrap:balance;
}

.upgrade-copy{
margin:0 auto;
max-width:600px;
color:#d7e4f8;
font-size:15px;
line-height:1.7;
}

.plan{
width:100%;
margin-top:14px;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
font-weight:900;
padding:15px;
box-shadow:0 12px 24px rgba(40,191,217,.14);
}

.plan.secondary{
background:linear-gradient(135deg,#466ff0 0%,#29bfd9 100%);
}

.plan.tertiary{
background:linear-gradient(135deg,#0e7b6f 0%,#18b67f 100%);
}

.subscriber-link{
margin-top:14px;
text-align:center;
}

.subscriber-link button{
background:none;
border:none;
padding:0;
min-height:auto;
font-size:14px;
color:#c6f7ff;
font-weight:800;
text-decoration:underline;
cursor:pointer;
}

.content-section{
margin-top:36px;
padding-bottom:38px;
}

.content-bridge{
margin:0 0 24px;
padding:18px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
font-size:15px;
color:#d7e4f8;
font-weight:800;
line-height:1.68;
}

.inline-info-card{
margin:0 0 22px;
padding:18px;
background:
linear-gradient(135deg, rgba(91,140,255,.10) 0%, rgba(139,120,242,.08) 100%),
linear-gradient(180deg, rgba(255,255,255,.06) 0%, rgba(255,255,255,.04) 100%);
}

.hub-link-block{
display:block;
}

.hub-link-label{
display:block;
margin-bottom:6px;
font-size:12px;
font-weight:900;
letter-spacing:.08em;
text-transform:uppercase;
color:#9cecff;
}

.hub-link-anchor{
display:inline;
font-size:15px;
font-weight:900;
color:#fff;
}

.content-section h2,
.content-section h3{
margin:0 0 14px;
color:#fff;
line-height:1.08;
letter-spacing:-.035em;
font-weight:900;
text-wrap:balance;
}

.content-section h2{
font-size:40px;
}

.content-section h3{
font-size:28px;
margin-top:30px;
}

.content-body{
font-size:18px;
color:#d7e4f8;
}

.content-body p{
margin:0 0 20px;
}

.content-body ul{
margin:0 0 20px;
padding-left:22px;
}

.content-body li{
margin-bottom:10px;
}

.link-section{
margin-top:28px;
padding-top:24px;
border-top:1px solid rgba(255,255,255,.08);
}

.related-links{
margin:0;
padding-left:22px;
}

.related-links li{
margin-bottom:10px;
}

.related-links a{
color:#9cecff;
font-weight:800;
}

.content-close{
margin-top:28px;
padding:18px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
font-size:15px;
font-weight:800;
color:#d7e4f8;
line-height:1.72;
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
color:#9cecff;
font-weight:700;
}

@media (max-width:640px){
body{padding-top:84px;}
.hero{padding:14px 6px 18px;}
.hero h1{font-size:34px;}
.hero p{margin-top:10px;font-size:17px;}
.container,.content-section{margin-left:12px;margin-right:12px;padding:18px;border-radius:24px;}
.top-bar{padding:10px 10px;}
.top-actions{gap:8px;margin-right:0;}
.logo{font-size:13px;margin-left:2px;padding:9px 12px;}
.app-top{font-size:13px;padding:8px 10px;}
.upgrade-top{font-size:13px;padding:8px 10px;margin-right:0;}
.upgrade h3{font-size:24px;}
.content-section h2{font-size:30px;line-height:1.12;}
.content-section h3{font-size:24px;}
.content-body{font-size:16px;}
.system-badge{margin-bottom:8px;font-size:11px;}
.preview-card{padding:14px;border-radius:20px;}
.preview-top{align-items:flex-start;gap:8px;}
.preview-badge{font-size:10px;padding:8px 12px;gap:6px;}
.preview-score-wrap{min-width:128px;gap:5px;}
.preview-score{font-size:10px;padding:7px 9px;}
.preview-score-bar{height:7px;}
.preview-domain{margin-top:8px;font-size:18px;line-height:1.08;}
.preview-sub{margin-top:3px;font-size:11px;line-height:1.3;}
.preview-signals{margin-top:8px;gap:6px;}
.preview-signal{padding:9px 10px;font-size:11px;gap:7px;border-radius:12px;}
.preview-signal-icon{width:14px;height:14px;font-size:11px;flex:0 0 14px;}
.result-top{align-items:flex-start;}
.result-chip{font-size:12px;}
.risk{font-size:19px;padding:10px 14px;}
.result-summary{font-size:15px;}
.signal-item{font-size:14px;}
.inline-info-card{padding:14px 15px;}
.content-close{padding:15px;}
.share-grid{grid-template-columns:1fr;}
.share-btn{width:100%;}
}
</style>
</head>

<body>

<div class="top-bar">
  <a class="logo" href="https://verixiaapps.com/check/">
    <span class="logo-dot"></span>
    <span>Scam Check Now</span>
  </a>
  <div class="top-actions">
    <a class="app-top" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">📱 Get App</a>
    <button class="upgrade-top" onclick="showUpgrade()">Upgrade</button>
  </div>
</div>

<div class="page-shell">

  <div class="hero">
    <div class="hero-badge-row">
      <div class="hero-badge">Live scam checking</div>
      <div class="hero-badge">Shareable warning page</div>
      <div class="hero-badge">Built for repeat use</div>
    </div>

    <h1 id="heroKeyword"></h1>
    <p id="heroSubheading"></p>

    <div class="hero-trust">
      <div class="hero-trust-chip">Check before you click</div>
      <div class="hero-trust-chip">Check before you reply</div>
      <div class="hero-trust-chip">Check before you send money</div>
    </div>
  </div>

  <div class="container">

    <div class="system-badge">Example scam pattern for reference</div>

    <div class="preview-card">
      <div class="preview-top">
        <div class="preview-badge" id="previewBadge">🔴 Example Risk Pattern</div>
        <div class="preview-score-wrap">
          <div class="preview-score" id="previewScore">Risk Example</div>
          <div class="preview-score-bar"><div class="preview-score-fill" id="previewScoreFill"></div></div>
        </div>
      </div>

      <div class="preview-domain" id="previewDomain">Example suspicious message</div>
      <div class="preview-sub" id="previewSub">Common signals found in similar scams</div>

      <div class="preview-signals" id="previewSignals">
        <div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>Suspicious domain mismatch</span></div>
        <div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>Urgent language detected</span></div>
        <div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>Payment request via gift card</span></div>
      </div>
    </div>

    <div class="tool-shell">
      <textarea id="text" placeholder="Paste the message, email, website, link, or job offer you're unsure about..."></textarea>

      <div class="input-help">Examples: delivery text, PayPal alert, crypto message, job offer, account warning</div>

      <button class="check" onclick="check()">🔍 Check Scam Risk</button>

      <div class="note">No signup required • 1 free check • Results in seconds</div>

      <input id="email" placeholder="Already subscribed? Enter your payment email to unlock unlimited checks">

      <div class="note">Use the same email you entered during checkout</div>

      <div id="postPurchase" class="success">
        ✅ Payment successful — unlimited access is active on this browser
      </div>

      <div class="note">Get a clear risk level, key red flags, and what to do next</div>

      <div id="result"></div>
    </div>

    <div class="app-link-card">
      <h4>Check suspicious messages anytime</h4>
      <p>Scam attempts often do not happen once. Use the app to check the next message before you click, reply, or send money.</p>
      <a class="app-link-button" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">Download the App</a>
    </div>

    <div class="upgrade" id="upgrade">
      <h3>Don’t Miss the Next Scam</h3>

      <div class="upgrade-copy">
        Most scam attempts do not happen once. If you are seeing suspicious messages, links, or requests, more may follow. Check each one before it costs you.
      </div>

      <div style="margin-top:10px;font-size:13px;color:#d4e2f5;">
        Built for ongoing protection against scams, phishing, impersonation, and risky payment requests
      </div>

      <div style="margin-top:8px;margin-bottom:10px;font-size:14px;color:#d4e2f5;">
        Unlimited scam checks • Cancel anytime
      </div>

      <button class="plan" onclick="checkout('price_1T8KOTJjMzyHDzeQDDg1A2TF')">Weekly Protection</button>
      <button class="plan secondary" onclick="checkout('price_1T8KOUJjMzyHDzeQxaqPFOSB')">Monthly Protection</button>
      <button class="plan tertiary" onclick="checkout('price_1T8KOQJjMzyHDzeQfcU1C1MQ')">Yearly Protection</button>

      <div style="margin-top:14px;font-size:13px;color:#d4e2f5;">
        Secure payments powered by Stripe
      </div>

      <div class="subscriber-link">
        <button type="button" onclick="scrollToEmail()">Already subscribed? Enter your email</button>
      </div>
    </div>

  </div>

  <section class="content-section">
    <div id="contentBridge" class="content-bridge"></div>

    <div class="inline-info-card" id="hubLinkWrap">
      {{HUB_LINK}}
    </div>

    <h2 id="contentHeading"></h2>
    <div id="seoContent" class="content-body">{{AI_CONTENT}}</div>

    <div class="link-section">
      <h3 id="relatedHeading">Check Similar Messages</h3>
      <ul id="relatedLinks" class="related-links">{{RELATED_LINKS}}</ul>
    </div>

    <div class="link-section" id="moreLinksWrap">
      <h3 id="moreLinksHeading">More Scam Checks</h3>
      <ul id="moreLinks" class="related-links">{{MORE_LINKS}}</ul>
    </div>

    <div class="content-close">
      Messages like this are one of the most common ways people lose money, share codes, or hand over access without realizing it. When something feels off, pause and verify it through official sources before taking action.
    </div>
  </section>

  <footer class="footer">
    <div>
      By using this website you agree to our
      <a href="https://verixiaapps.com/website-policies/scam-check/" target="_blank" rel="noopener noreferrer">Terms and Privacy Policy</a>.
    </div>
    <div style="margin-top:10px">
      Scam Check Now © 2026 • Scam detection and risk analysis tool
    </div>
  </footer>

</div>

<script>
const API = "https://awake-integrity-production-faa0.up.railway.app";
const RAW_KEYWORD = "{{KEYWORD}}";
const BROWSER_SUB_KEY = "scam_check_browser_subscribed";

window.addEventListener("load", function () {
  const params = new URLSearchParams(window.location.search);

  if (params.get("subscribed") === "true") {
    localStorage.setItem(BROWSER_SUB_KEY, "true");
    document.getElementById("postPurchase").style.display = "block";
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  if (isBrowserSubscribed()) {
    document.getElementById("postPurchase").style.display = "block";
  }

  setKeywordHeadings();
  applyPreviewCard();
  applyIntentToChecker();
  cleanSeoContent();
  cleanRelatedLinks();
  cleanHubLink();
  cleanMoreLinks();
});

function isBrowserSubscribed() {
  return localStorage.getItem(BROWSER_SUB_KEY) === "true";
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;")
    .replace(/'/g,"&#39;");
}

function normalizeKeyword(str) {
  return String(str || "")
    .replace(/\s+/g, " ")
    .replace(/[–—]/g, "-")
    .trim();
}

function stripLeadingQuestionPrefixes(text) {
  return String(text || "")
    .replace(/^\s*is\s+/i, "")
    .replace(/^\s*can\s+i\s+trust\s+/i, "")
    .replace(/^\s*did\s+i\s+get\s+scammed\s+(?:by|on|with)\s+/i, "")
    .trim();
}

function stripTrailingQuestionSuffixes(text) {
  return String(text || "")
    .replace(/\s+a\s+scam$/i, "")
    .replace(/\s+or\s+legit$/i, "")
    .replace(/\s+or\s+scam$/i, "")
    .replace(/\s+legit$/i, "")
    .replace(/\s+real$/i, "")
    .replace(/\s+safe$/i, "")
    .replace(/\s+scam$/i, "")
    .replace(/\s+a$/i, "")
    .trim();
}

function cleanKeywordBase(keyword) {
  let text = normalizeKeyword(keyword);
  text = stripLeadingQuestionPrefixes(text);
  text = stripTrailingQuestionSuffixes(text);
  return text.replace(/\s+/g, " ").trim();
}

function cleanKeywordForSentence(keyword) {
  return cleanKeywordBase(keyword)
    .replace(/\bmessage\b/gi, "")
    .replace(/\bmessages\b/gi, "")
    .replace(/\bemail\b/gi, "")
    .replace(/\bemails\b/gi, "")
    .replace(/\btext\b/gi, "")
    .replace(/\btexts\b/gi, "")
    .replace(/\blink\b/gi, "")
    .replace(/\blinks\b/gi, "")
    .replace(/\bwebsite\b/gi, "")
    .replace(/\bwebsites\b/gi, "")
    .replace(/\balert\b/gi, "")
    .replace(/\balerts\b/gi, "")
    .replace(/\bwarning\b/gi, "")
    .replace(/\bwarnings\b/gi, "")
    .replace(/\bnotification\b/gi, "")
    .replace(/\bnotifications\b/gi, "")
    .replace(/\brequest\b/gi, "")
    .replace(/\brequests\b/gi, "")
    .replace(/\boffer\b/gi, "")
    .replace(/\boffers\b/gi, "")
    .replace(/\bscam\b/gi, "")
    .replace(/\bscams\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

function displayKeyword(str) {
  const text = normalizeKeyword(str);
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function displayCleanKeyword(str) {
  return displayKeyword(cleanKeywordBase(str));
}

function containsAny(text, phrases) {
  return phrases.some(phrase => text.includes(phrase));
}

function isGuidanceStyleKeyword(lower) {
  return (
    lower.startsWith("how to ") ||
    lower.startsWith("what to do after ") ||
    lower.startsWith("how to recover after ") ||
    lower.startsWith("how to secure ") ||
    lower.startsWith("how to block ") ||
    lower.startsWith("how to avoid ") ||
    lower.startsWith("what happens after ") ||
    lower.startsWith("what is ") ||
    lower.startsWith("why ") ||
    lower.startsWith("when ") ||
    lower.startsWith("where ") ||
    lower.startsWith("who ")
  );
}

function isQuestionStyleKeyword(lower) {
  return (
    lower.startsWith("is ") ||
    lower.startsWith("can ") ||
    lower.startsWith("should ") ||
    lower.startsWith("could ") ||
    lower.startsWith("would ") ||
    lower.startsWith("do ") ||
    lower.startsWith("does ") ||
    lower.startsWith("did ")
  );
}

function chooseBridgeIntro(baseKeyword) {
  const readable = displayKeyword(baseKeyword);
  const variants = [
    `If this ${readable} just showed up,`,
    `If you're unsure about this ${readable},`,
    `If you're looking at this ${readable} right now,`
  ];
  const index = baseKeyword.length % variants.length;
  return variants[index];
}

function buildHeroTitle(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const cleanTitle = displayCleanKeyword(keywordRaw);
  const readableTitle = displayKeyword(raw);

  if (!raw) {
    return "Is this a scam? Check Before You Click or Send Money";
  }

  if (isGuidanceStyleKeyword(lower)) {
    return `${readableTitle}: Safety Tips, Warning Signs & What To Do`;
  }

  if (lower.startsWith("did i get scammed")) {
    return `${readableTitle}? Signs, Risks & What To Do Next`;
  }

  if (lower.startsWith("can scammers") || lower.startsWith("can someone")) {
    return `${readableTitle}? Risks, Warning Signs & What To Do`;
  }

  if (lower.startsWith("almost ")) {
    return `${readableTitle}? Warning Signs & Safety Steps`;
  }

  if (lower.startsWith("is this ")) {
    return `${readableTitle}? Check Warning Signs & What To Do`;
  }

  if (lower.startsWith("is ") && lower.includes(" legit")) {
    const withoutLegit = raw.replace(/\s+legit\b/i, "").trim();
    return `${displayKeyword(withoutLegit)} Legit or a Scam? Warning Signs & What To Do`;
  }

  if (isQuestionStyleKeyword(lower)) {
    return `${readableTitle}? Risks, Warning Signs & What To Know`;
  }

  return `Is ${cleanTitle} a Scam? Check Before You Click or Send Money`;
}

function buildHeroSubheading(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const readableKeyword = displayKeyword(cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw);

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker below to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information.";
  }

  return `Messages related to ${readableKeyword} can be used to steal money, codes, or account access. Paste it below before you click, reply, send money, or take action.`;
}

function buildContentHeading(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const readableTitle = displayKeyword(raw);
  const cleanTitle = displayCleanKeyword(keywordRaw);

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower) || lower.startsWith("almost ")) {
    return readableTitle;
  }

  return `What ${cleanTitle} Messages, Links, and Offers Often Look Like`;
}

function buildContentBridge(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const cleanSentenceKeyword = cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw;

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker above to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information.";
  }

  if (lower.startsWith("almost ")) {
    return "If you are unsure what happened, use the checker above to review suspicious messages, emails, links, and offers before taking action.";
  }

  return `${chooseBridgeIntro(cleanSentenceKeyword)} use the checker above before you click links, reply, send money, or share information. Messages like this are one of the most common ways people lose money or hand over account access without realizing it.`;
}

function setKeywordHeadings() {
  const keywordRaw = (RAW_KEYWORD || "this message").trim();

  document.getElementById("heroKeyword").textContent = buildHeroTitle(keywordRaw);
  document.getElementById("heroSubheading").textContent = buildHeroSubheading(keywordRaw);
  document.getElementById("contentHeading").textContent = buildContentHeading(keywordRaw);
  document.getElementById("contentBridge").textContent = buildContentBridge(keywordRaw);
}

function applyPreviewCard() {
  const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
  const cleanTitle = displayCleanKeyword(keywordRaw) || "Suspicious Message";
  const lower = keywordRaw.toLowerCase();

  const previewDomain = document.getElementById("previewDomain");
  const previewSub = document.getElementById("previewSub");
  const previewBadge = document.getElementById("previewBadge");
  const previewScore = document.getElementById("previewScore");
  const previewScoreFill = document.getElementById("previewScoreFill");
  const previewSignals = document.getElementById("previewSignals");

  if (!previewDomain || !previewSub || !previewBadge || !previewScore || !previewScoreFill || !previewSignals) {
    return;
  }

  let riskLabel = "Example Risk Pattern";
  let trustScore = "Risk Example";
  let fillWidth = "18%";
  let sub = "Common signals found in similar scams";
  let signals = [
    "Suspicious domain mismatch",
    "Urgent language detected",
    "Payment request via gift card"
  ];

  if (containsAny(lower, ["job", "recruiter", "interview", "hiring", "onboarding"])) {
    signals = [
      "Pressure to move quickly",
      "Requests for personal details or fees",
      "Offer appears unusually fast or high-paying"
    ];
  } else if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft"])) {
    signals = [
      "Urgent transfer or wallet request",
      "High-return or recovery promise",
      "Support or investment impersonation risk"
    ];
  } else if (containsAny(lower, ["delivery", "usps", "ups", "fedex", "package", "shipment", "parcel"])) {
    signals = [
      "Tracking or delivery pressure",
      "Link may lead to a fake page",
      "Small payment or verification request"
    ];
  } else if (containsAny(lower, ["bank", "paypal", "venmo", "zelle", "cash app", "amazon", "refund", "payment"])) {
    signals = [
      "Account or payment urgency",
      "Possible fake login or verification page",
      "Requests for money or sensitive details"
    ];
  } else if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    riskLabel = "Scam Risk Check";
    trustScore = "Pattern Review";
    fillWidth = "34%";
    signals = [
      "Review sender, links, and urgency",
      "Verify outside the original message",
      "Do not send money or codes until confirmed"
    ];
  }

  previewBadge.textContent = `🔴 ${riskLabel}`;
  previewScore.textContent = trustScore;
  previewScoreFill.style.width = fillWidth;
  previewDomain.textContent = cleanTitle;
  previewSub.textContent = sub;
  previewSignals.innerHTML = signals.map(signal =>
    `<div class="preview-signal"><span class="preview-signal-icon">⚠️</span><span>${escapeHtml(signal)}</span></div>`
  ).join("");
}

function applyIntentToChecker() {
  const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
  const lower = keywordRaw.toLowerCase();
  const textarea = document.getElementById("text");
  const inputHelp = document.querySelector(".input-help");

  if (!textarea || !inputHelp) return;

  if (containsAny(lower, ["job", "recruiter", "interview", "hiring", "onboarding"])) {
    textarea.placeholder = "Paste the job message, recruiter email, interview request, or onboarding text you're unsure about...";
    inputHelp.textContent = "Examples: recruiter email, interview request, onboarding message, job offer, payment request";
    return;
  }

  if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft"])) {
    textarea.placeholder = "Paste the crypto message, wallet request, token offer, or support message you're unsure about...";
    inputHelp.textContent = "Examples: wallet connect message, token airdrop, exchange alert, support DM, recovery offer";
    return;
  }

  if (containsAny(lower, ["delivery", "usps", "ups", "fedex", "package", "shipment", "parcel"])) {
    textarea.placeholder = "Paste the delivery text, tracking update, shipping email, or package link you're unsure about...";
    inputHelp.textContent = "Examples: USPS text, FedEx email, tracking link, customs fee message, missed delivery alert";
    return;
  }

  if (containsAny(lower, ["bank", "paypal", "venmo", "zelle", "cash app", "amazon", "refund", "payment"])) {
    textarea.placeholder = "Paste the payment alert, account message, refund email, or login request you're unsure about...";
    inputHelp.textContent = "Examples: PayPal alert, bank text, Amazon refund email, Venmo request, Zelle message";
    return;
  }

  textarea.placeholder = "Paste the message, email, website, link, or job offer you're unsure about...";
  inputHelp.textContent = "Examples: delivery text, PayPal alert, crypto message, job offer, account warning";
}

function cleanSeoContent() {
  const seoContent = document.getElementById("seoContent");
  if (!seoContent) return;

  seoContent.innerHTML = seoContent.innerHTML
    .replace(/\*\*/g, "")
    .replace(/<p>\s*<\/p>/g, "")
    .trim();
}

function cleanRelatedLinks() {
  const relatedLinks = document.getElementById("relatedLinks");
  const relatedHeading = document.getElementById("relatedHeading");
  if (!relatedLinks || !relatedHeading) return;

  relatedLinks.innerHTML = relatedLinks.innerHTML.replace(/\*\*/g, "").trim();

  const links = relatedLinks.querySelectorAll("li a");

  if (links.length === 0) {
    relatedLinks.style.display = "none";
    relatedHeading.style.display = "none";
  }
}

function cleanHubLink() {
  const hubLinkWrap = document.getElementById("hubLinkWrap");
  if (!hubLinkWrap) return;

  hubLinkWrap.innerHTML = hubLinkWrap.innerHTML.replace(/\*\*/g, "").trim();

  const anchor = hubLinkWrap.querySelector("a");
  if (!anchor) {
    hubLinkWrap.style.display = "none";
    return;
  }

  const safeHref = anchor.getAttribute("href") || "#";
  const safeText = (anchor.textContent || "").trim();
  const target = anchor.getAttribute("target");
  const rel = anchor.getAttribute("rel");

  if (!safeText) {
    hubLinkWrap.style.display = "none";
    return;
  }

  hubLinkWrap.innerHTML = `
    <div class="hub-link-block">
      <span class="hub-link-label">Related scam category</span>
      <a class="hub-link-anchor" href="${escapeHtml(safeHref)}"${target ? ` target="${escapeHtml(target)}"` : ""}${rel ? ` rel="${escapeHtml(rel)}"` : ""}>${escapeHtml(safeText)}</a>
    </div>
  `;
}

function cleanMoreLinks() {
  const moreLinksWrap = document.getElementById("moreLinksWrap");
  const moreLinks = document.getElementById("moreLinks");
  const moreLinksHeading = document.getElementById("moreLinksHeading");

  if (!moreLinksWrap || !moreLinks || !moreLinksHeading) return;

  moreLinks.innerHTML = moreLinks.innerHTML.replace(/\*\*/g, "").trim();

  const links = moreLinks.querySelectorAll("li a");
  if (links.length === 0) {
    moreLinksWrap.style.display = "none";
    moreLinksHeading.style.display = "none";
  }
}

function summaryForRisk(riskClass) {
  if (riskClass === "high") {
    return "This message shows multiple scam signals. Treat it as unsafe until you verify it directly through the official website, app, company, or platform.";
  }
  if (riskClass === "medium") {
    return "This message shows warning signs. Be cautious and verify the sender, offer, or website before you click, reply, send money, or share information.";
  }
  if (riskClass === "low") {
    return "This message shows fewer obvious scam signals, but you should still verify anything involving links, payments, logins, or personal information before taking action.";
  }
  return "We could not determine a clear risk level. Treat the message cautiously and verify it through official sources before you do anything else.";
}

function paylineForRisk(riskClass) {
  if (riskClass === "high") {
    return "People lose money from messages like this every day. If another one shows up tomorrow, guessing wrong could cost you.";
  }
  if (riskClass === "medium") {
    return "Suspicious messages often do not stop at one. If you have seen one, more may follow. Check the next one before you click, reply, or pay.";
  }
  if (riskClass === "low") {
    return "Even lower-risk messages can become expensive when later versions ask for logins, payments, codes, or urgent action.";
  }
  return "When the risk is unclear, the safest move is to pause, verify this one, and treat the next similar message carefully too.";
}

function cardClassForRisk(risk) {
  if (risk === "high") return "high";
  if (risk === "medium") return "medium";
  if (risk === "low") return "low";
  return "unknown";
}

function iconForRisk(risk) {
  if (risk === "high") return "🔴";
  if (risk === "medium") return "🟠";
  if (risk === "low") return "🟢";
  return "⚪";
}

function signalIconForRisk(risk) {
  if (risk === "high") return "⚠️";
  if (risk === "medium") return "⚠️";
  if (risk === "low") return "✔️";
  return "•";
}

function chipByRisk(risk) {
  if (risk === "high") return "Pattern Match: Strong";
  if (risk === "medium") return "Pattern Match: Moderate";
  if (risk === "low") return "Pattern Match: Lower Risk";
  return "Pattern Match: Review Needed";
}

function scrollToTopCheck() {
  const textarea = document.getElementById("text");
  if (!textarea) return;
  window.scrollTo({ top: 0, behavior: "smooth" });
  setTimeout(() => textarea.focus(), 300);
}

function getShareUrl() {
  return window.location.href;
}

function getShareText() {
  return "This message may be a scam. Check it before you click, reply, or send money:";
}

function getWarningMessage() {
  return `This message may be a scam.
Check it before you click, reply, or send money:
${getShareUrl()}`;
}

function showShareStatus(message) {
  const status = document.getElementById("shareStatus");
  if (!status) return;
  status.textContent = message;
  clearTimeout(showShareStatus.timeoutId);
  showShareStatus.timeoutId = setTimeout(() => {
    status.textContent = "";
  }, 2200);
}

function shareNative() {
  const shareData = {
    title: document.title,
    text: getShareText(),
    url: getShareUrl()
  };

  if (navigator.share) {
    navigator.share(shareData).catch(() => {});
    return;
  }

  copyWarningMessage();
}

function shareX() {
  const text = encodeURIComponent(getShareText());
  const url = encodeURIComponent(getShareUrl());
  window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, "_blank", "noopener,noreferrer");
}

function copyLink() {
  const url = getShareUrl();

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(() => {
      showShareStatus("Link copied.");
    }).catch(() => {
      fallbackCopy(url, "Link copied.");
    });
    return;
  }

  fallbackCopy(url, "Link copied.");
}

function copyWarningMessage() {
  const message = getWarningMessage();

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(message).then(() => {
      showShareStatus("Warning copied.");
    }).catch(() => {
      fallbackCopy(message, "Warning copied.");
    });
    return;
  }

  fallbackCopy(message, "Warning copied.");
}

function fallbackCopy(value, successMessage) {
  const input = document.createElement("textarea");
  input.value = value;
  input.setAttribute("readonly", "");
  input.style.position = "absolute";
  input.style.left = "-9999px";
  document.body.appendChild(input);
  input.select();
  input.setSelectionRange(0, 99999);
  document.execCommand("copy");
  document.body.removeChild(input);
  showShareStatus(successMessage);
}

function formatResult(raw) {
  const lines = String(raw || "").split("\n").map(l => l.trim()).filter(Boolean);

  let risk = "";
  let signals = [];
  let actions = [];
  let mode = "";

  lines.forEach(line => {
    const lower = line.toLowerCase();

    if (lower.includes("risk level")) {
      risk = line.split(":").slice(1).join(":").trim();
      return;
    }

    if (lower.includes("key signals")) {
      mode = "signals";
      return;
    }

    if (lower.includes("recommended action")) {
      mode = "actions";
      return;
    }

    if (line.startsWith("-")) {
      const cleaned = line.replace(/^-+\s*/, "");
      if (mode === "signals") signals.push(cleaned);
      if (mode === "actions") actions.push(cleaned);
    }
  });

  const riskClass = (risk || "review").trim().toLowerCase();
  const safeRiskClass = cardClassForRisk(riskClass);
  const signalIcon = signalIconForRisk(safeRiskClass);
  const continuationLine = safeRiskClass !== "low"
    ? `<div class="result-continuation">If this reached you once, similar messages may already be on the way. Scammers often repeat the same pattern across many people.</div>`
    : "";

  if (signals.length === 0) {
    signals = ["Review the sender, links, and any requests for money, urgency, or personal information."];
  }

  if (actions.length === 0) {
    actions = ["Do not reply, do not click links, and verify directly through the official website, app, company, or platform before taking action."];
  }

  return `
  <div class="result-card ${safeRiskClass}">
    <div class="result-top">
      <div class="risk ${safeRiskClass}">${iconForRisk(safeRiskClass)} ${safeRiskClass === "unknown" ? "Risk Level: REVIEW" : "Risk Level: " + safeRiskClass.toUpperCase()}</div>
      <div class="result-chip">${chipByRisk(safeRiskClass)}</div>
    </div>

    <div class="result-summary">${escapeHtml(summaryForRisk(safeRiskClass))}</div>
    ${continuationLine}

    <div class="section">
      <div class="section-title">Detected Signals</div>
      <ul class="signal-list">
        ${signals.map(s => `<li class="signal-item"><span class="signal-icon">${signalIcon}</span><span>${escapeHtml(s)}</span></li>`).join("")}
      </ul>
    </div>

    <div class="section">
      <div class="section-title">Recommended Actions</div>
      <div class="action-box">${escapeHtml(actions[0])}</div>
    </div>

    <div class="result-payline">${escapeHtml(paylineForRisk(safeRiskClass))}</div>

    <div class="result-actions">
      <button class="check result-cta" onclick="scrollToTopCheck()">🔁 Not sure about another message? Check it now</button>

      <div class="share-wrap">
        <div class="share-alert">⚠️ Messages like this are often sent in waves</div>
        <div class="share-copy">Know someone who could receive this same message? Send this warning before they click, reply, or send money.</div>
        <div class="share-grid">
          <button type="button" class="share-btn primary" onclick="copyWarningMessage()">⚠️ Copy Warning</button>
          <button type="button" class="share-btn dark" onclick="shareNative()">📤 Share</button>
          <button type="button" class="share-btn light" onclick="shareX()">𝕏 Share to X</button>
          <button type="button" class="share-btn light" onclick="copyLink()">🔗 Copy Link</button>
        </div>
        <div class="share-status" id="shareStatus" aria-live="polite"></div>
      </div>
    </div>
  </div>
  `;
}

function showUpgrade() {
  const el = document.getElementById("upgrade");
  if (!el) return;
  el.style.display = "block";
  setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
}

function scrollToEmail() {
  const emailField = document.getElementById("email");
  if (!emailField) return;
  emailField.scrollIntoView({ behavior: "smooth", block: "center" });
  setTimeout(() => emailField.focus(), 150);
}

async function check() {
  const text = document.getElementById("text").value.trim();
  const email = document.getElementById("email").value.trim().toLowerCase();
  const subscribed = isBrowserSubscribed();
  const result = document.getElementById("result");

  if (!text) {
    result.innerHTML = `
      <div class="result-card unknown">
        <div class="result-top">
          <div class="risk unknown">⚪ Paste Something To Check</div>
          <div class="result-chip">Awaiting Input</div>
        </div>
        <div class="result-summary">Paste a suspicious message, email, website, link, job offer, or investment pitch to check scam risk before you act.</div>
      </div>
    `;
    result.style.display = "block";
    return;
  }

  result.style.display = "block";
  result.innerHTML = `
    <div class="result-card unknown">
      <div class="result-top">
        <div class="risk unknown">⚪ Analyzing...</div>
        <div class="result-chip">Scan In Progress</div>
      </div>
      <div class="result-summary">Checking for scam signals, risky patterns, payment traps, impersonation, and suspicious links.</div>
    </div>
  `;

  try {
    const response = await fetch(API + "/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, email, subscribed })
    });

    const data = await response.json();

    if (data.limit) {
      result.innerHTML = `
        <div class="result-card medium">
          <div class="result-top">
            <div class="risk medium">🟠 Free Check Used</div>
            <div class="result-chip">Upgrade Available</div>
          </div>
          <div class="result-summary">Unlock unlimited protection so you can check the next suspicious message, link, or request before it costs you.</div>
        </div>
      `;
      showUpgrade();
      return;
    }

    result.innerHTML = formatResult(data.result || "");
    showUpgrade();
  } catch (e) {
    result.innerHTML = `
      <div class="result-card unknown">
        <div class="result-top">
          <div class="risk unknown">⚪ Unable To Analyze</div>
          <div class="result-chip">Try Again</div>
        </div>
        <div class="result-summary">We could not analyze this right now. Please try again in a moment.</div>
      </div>
    `;
  }
}

async function checkout(priceId) {
  const pageUrl = window.location.origin + window.location.pathname;

  const response = await fetch(API + "/create-checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      priceId,
      email: null,
      successUrl: pageUrl + "?subscribed=true",
      cancelUrl: pageUrl
    })
  });

  const data = await response.json();

  if (data.url) {
    window.location = data.url;
  } else {
    alert("Checkout failed.");
  }
}
</script>

</body>
</html>"""
TEMPLATE_B = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>{{TITLE}}</title>
<meta name="description" content="{{DESCRIPTION}}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{{CANONICAL_URL}}">

<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESCRIPTION}}">
<meta property="og:type" content="website">
<meta property="og:url" content="{{CANONICAL_URL}}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{{TITLE}}">
<meta name="twitter:description" content="{{DESCRIPTION}}">

<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@type":"WebPage",
  "name":"{{TITLE}}",
  "description":"{{DESCRIPTION}}",
  "url":"{{CANONICAL_URL}}"
}
</script>

<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"How can I tell if something is a scam?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Look for urgency, requests for money or codes, suspicious links, and messages that pressure you to act quickly. Always verify through official sources."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I clicked a suspicious link?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Avoid entering any information, close the page, run a security check on your device, and change important passwords if needed."
      }
    },
    {
      "@type":"Question",
      "name":"Are scam messages common?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Yes, scam messages are increasingly common across email, text, social media, and messaging apps. They often impersonate trusted companies or people."
      }
    }
  ]
}
</script>

<style>
:root{
--bg:#07111f;
--bg-2:#0c1728;
--bg-3:#12203a;
--surface:rgba(255,255,255,.06);
--surface-2:rgba(255,255,255,.08);
--surface-3:#ffffff;
--card:#101c33;
--card-2:#162541;

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
--emerald-2:#059669;
--amber:#f59e0b;
--red:#ef4444;

--blue-soft:#dbeafe;
--violet-soft:#ede9fe;
--green-soft:#ecfdf5;
--amber-soft:#fffbeb;
--red-soft:#fef2f2;

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

button,
textarea,
input{
font-family:inherit;
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
padding:11px 15px;
font-size:14px;
border-radius:16px;
font-weight:900;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
border:none;
cursor:pointer;
white-space:nowrap;
box-shadow:0 16px 34px rgba(34,211,238,.16);
max-width:none;
overflow:visible;
text-overflow:unset;
}

.page-shell{
max-width:940px;
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

.container,
.content-section{
max-width:820px;
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

.container::before,
.content-section::before{
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

.container > *,
.content-section > *{
position:relative;
z-index:1;
}

.answer-card,
.pattern-card,
.warning-card,
.tool-shell,
.app-link-card,
.upgrade{
background:linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
border:1px solid rgba(255,255,255,.10);
border-radius:24px;
box-shadow:var(--shadow-md);
}

.answer-card{
padding:18px;
background:
linear-gradient(135deg, rgba(34,211,238,.12) 0%, rgba(139,92,246,.12) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.05) 100%);
}

.answer-kicker{
font-size:12px;
font-weight:900;
letter-spacing:.08em;
text-transform:uppercase;
color:#8be9ff;
margin-bottom:8px;
}

.answer-card h2{
margin:0;
font-size:28px;
line-height:1.08;
letter-spacing:-.03em;
color:#fff;
}

.answer-card p{
margin:10px 0 0;
font-size:15px;
font-weight:800;
color:#d8e5f8;
line-height:1.7;
}

.precheck-layout{
display:grid;
gap:16px;
margin-top:16px;
margin-bottom:18px;
}

.pattern-card,
.warning-card{
padding:18px;
}

.card-heading{
margin:0 0 10px;
font-size:21px;
line-height:1.14;
letter-spacing:-.02em;
font-weight:900;
color:#fff;
}

.card-copy{
margin:0 0 12px;
font-size:14px;
font-weight:800;
color:#b9c9e3;
line-height:1.68;
}

.steps-grid,
.warning-grid{
display:grid;
gap:10px;
}

.step-item,
.warning-item{
display:flex;
align-items:flex-start;
gap:12px;
padding:14px 15px;
border-radius:18px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
}

.step-number{
width:28px;
height:28px;
border-radius:999px;
display:flex;
align-items:center;
justify-content:center;
flex:0 0 28px;
font-size:13px;
font-weight:900;
background:linear-gradient(180deg,var(--cyan) 0%,var(--violet) 100%);
color:#fff;
box-shadow:0 8px 18px rgba(34,211,238,.18);
}

.warning-icon{
width:24px;
height:24px;
border-radius:999px;
display:flex;
align-items:center;
justify-content:center;
flex:0 0 24px;
font-size:14px;
background:rgba(239,68,68,.16);
color:#fecaca;
}

.step-text strong,
.warning-text strong{
display:block;
font-size:14px;
line-height:1.35;
color:#fff;
margin-bottom:2px;
}

.step-text span,
.warning-text span{
display:block;
font-size:13px;
line-height:1.58;
font-weight:800;
color:#bfd0ea;
}

.example-band{
margin-top:12px;
padding:14px 15px;
border-radius:18px;
background:linear-gradient(180deg, rgba(139,92,246,.16) 0%, rgba(34,211,238,.10) 100%);
border:1px solid rgba(139,92,246,.24);
font-size:14px;
font-weight:800;
line-height:1.65;
color:#efe9ff;
}

.example-band strong{
display:block;
margin-bottom:4px;
font-size:13px;
letter-spacing:.04em;
text-transform:uppercase;
color:#c4b5fd;
}

.tool-shell{
padding:22px;
margin-top:18px;
background:
linear-gradient(135deg, rgba(34,211,238,.10) 0%, rgba(139,92,246,.10) 100%),
linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.04) 100%);
}

.tool-top{
text-align:center;
margin-bottom:16px;
}

.tool-top h2{
margin:0;
font-size:30px;
line-height:1.10;
letter-spacing:-.04em;
color:#fff;
}

.tool-top p{
margin:8px auto 0;
max-width:620px;
font-size:15px;
color:#c8d6ec;
font-weight:700;
line-height:1.7;
}

textarea,input{
width:100%;
padding:16px 16px;
margin-top:12px;
border-radius:18px;
border:1.5px solid rgba(255,255,255,.12);
font-size:16px;
background:rgba(7,16,29,.72);
color:#eef6ff;
box-shadow:none;
}

textarea{
height:156px;
resize:none;
}

textarea::placeholder,
input::placeholder{
color:#89a0c4;
}

textarea:focus,
input:focus{
outline:none;
border-color:rgba(34,211,238,.60);
box-shadow:0 0 0 5px rgba(34,211,238,.10);
}

button{
border:none;
border-radius:18px;
cursor:pointer;
font-size:16px;
padding:16px;
min-height:50px;
}

.check{
width:100%;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
margin-top:18px;
font-weight:900;
font-size:18px;
letter-spacing:.2px;
box-shadow:0 18px 40px rgba(34,211,238,.20);
transition:transform .15s ease, box-shadow .15s ease;
}

.check:hover{
transform:translateY(-1px);
box-shadow:0 22px 44px rgba(34,211,238,.24);
}

.check:active{
transform:scale(.985);
}

.note,
.input-help{
margin-top:12px;
font-size:14px;
color:#9fb0cc;
text-align:center;
text-wrap:balance;
}

.success{
margin-top:12px;
font-size:14px;
color:#86efac;
text-align:center;
font-weight:900;
display:none;
}

.tool-assurance{
margin-top:14px;
padding:14px 15px;
border-radius:18px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
font-size:14px;
font-weight:800;
color:#cbdaf0;
line-height:1.6;
text-align:center;
}

.app-link-card{
margin-top:18px;
padding:20px;
text-align:center;
background:
linear-gradient(135deg, rgba(16,185,129,.12) 0%, rgba(34,211,238,.10) 100%),
linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.04) 100%);
}

.app-link-card h4{
margin:0 0 6px;
font-size:20px;
color:#fff;
font-weight:900;
letter-spacing:-.02em;
}

.app-link-card p{
margin:0 0 12px;
font-size:14px;
color:#c9d8ee;
line-height:1.65;
}

.app-link-button{
display:block;
width:100%;
text-align:center;
background:linear-gradient(135deg,var(--emerald) 0%,var(--cyan-2) 100%);
color:#fff;
font-weight:900;
padding:15px;
border-radius:16px;
box-sizing:border-box;
box-shadow:0 14px 30px rgba(16,185,129,.18);
text-decoration:none;
}

#result{
margin-top:26px;
display:none;
}

.result-card{
background:rgba(255,255,255,.96);
border-radius:26px;
padding:22px;
box-shadow:var(--shadow-lg);
border:1px solid rgba(15,23,42,.08);
overflow:hidden;
color:var(--ink-dark);
}

.result-card.high{
border:2px solid #fecaca;
box-shadow:0 22px 50px rgba(239,68,68,.12);
}

.result-card.medium{
border:2px solid #fde68a;
box-shadow:0 22px 50px rgba(245,158,11,.10);
}

.result-card.low{
border:2px solid #bbf7d0;
box-shadow:0 22px 50px rgba(16,185,129,.10);
}

.result-card.unknown{
border:1px solid #dbe4f0;
}

.result-top{
display:flex;
align-items:flex-start;
justify-content:space-between;
gap:12px;
flex-wrap:wrap;
}

.risk{
font-size:21px;
font-weight:900;
margin-bottom:0;
padding:11px 16px;
border-radius:999px;
display:inline-flex;
align-items:center;
gap:10px;
letter-spacing:.01em;
box-shadow:var(--shadow-sm);
}

.risk.high{
background:var(--red);
color:#fff;
}
.risk.medium{
background:var(--amber);
color:#fff;
}
.risk.low{
background:var(--emerald);
color:#fff;
}
.risk.unknown{
background:#e5e7eb;
color:#374151;
}

.result-chip{
padding:9px 13px;
border-radius:999px;
font-size:12px;
font-weight:900;
background:#fff;
border:1px solid #d9e2ec;
color:#334155;
box-shadow:var(--shadow-sm);
}

.result-summary{
margin:16px 0 0;
font-size:16px;
color:#334155;
font-weight:800;
line-height:1.58;
}

.result-continuation{
margin-top:14px;
padding:14px 15px;
border-radius:16px;
font-size:14px;
font-weight:900;
line-height:1.55;
background:#f8fafc;
border:1px solid #e2e8f0;
color:#334155;
}

.result-card.high .result-continuation{
background:#fff8f8;
border-color:#f3c5cf;
color:#7f1d1d;
}

.result-card.medium .result-continuation{
background:#fffdf5;
border-color:#fde68a;
color:#92400e;
}

.result-card.unknown .result-continuation{
background:#f8fafc;
border-color:#e2e8f0;
color:#334155;
}

.section{
margin-top:18px;
padding:18px;
border-radius:20px;
background:#f8fafc;
border:1px solid #e7eef6;
}

.section-title{
font-weight:900;
margin-bottom:10px;
color:#0f172a;
font-size:16px;
letter-spacing:-.01em;
}

.signal-list{
list-style:none;
padding:0;
margin:0;
display:grid;
gap:10px;
}

.signal-item{
display:flex;
align-items:flex-start;
gap:12px;
padding:14px 15px;
border-radius:16px;
background:#fff;
border:1px solid #e2e8f0;
font-size:14px;
font-weight:800;
color:#334155;
line-height:1.45;
}

.result-card.high .signal-item{
background:#fffafa;
border-color:#f5c2cc;
color:#7f1d1d;
}

.result-card.medium .signal-item{
background:#fffdf5;
border-color:#fde68a;
color:#92400e;
}

.result-card.low .signal-item{
background:#f7fff8;
border-color:#bbf7d0;
color:#166534;
}

.signal-icon{
width:22px;
height:22px;
display:flex;
align-items:center;
justify-content:center;
font-size:16px;
line-height:1;
flex:0 0 22px;
}

.action-box{
padding:15px 16px;
border-radius:16px;
background:#eef6ff;
border:1px solid #bfdbfe;
font-size:14px;
font-weight:900;
color:#1e3a8a;
line-height:1.55;
}

.result-payline{
margin-top:18px;
padding:16px;
background:#f8fafc;
border:1px solid #e2e8f0;
border-radius:18px;
font-size:14px;
color:#334155;
font-weight:900;
line-height:1.55;
}

.result-card.high .result-payline{
background:#fff8f8;
border-color:#f3c5cf;
color:#7f1d1d;
}

.result-card.medium .result-payline{
background:#fffdf5;
border-color:#fde68a;
color:#92400e;
}

.result-card.low .result-payline{
background:#f7fff8;
border-color:#bbf7d0;
color:#166534;
}

.result-actions{
margin-top:16px;
display:grid;
gap:12px;
}

.result-cta{
margin-top:0;
}

.share-wrap{
margin-top:4px;
padding:18px;
border-radius:20px;
background:linear-gradient(180deg,#fff 0%,#f8fafc 100%);
border:1px solid #e2e8f0;
text-align:center;
box-shadow:var(--shadow-sm);
}

.share-alert{
font-size:13px;
font-weight:900;
color:#0f172a;
margin-bottom:6px;
letter-spacing:.01em;
}

.share-copy{
font-size:14px;
font-weight:800;
color:#475569;
line-height:1.55;
margin-bottom:14px;
max-width:560px;
margin-left:auto;
margin-right:auto;
}

.share-grid{
display:grid;
grid-template-columns:repeat(2,minmax(0,1fr));
gap:10px;
}

.share-btn{
display:inline-flex;
align-items:center;
justify-content:center;
gap:8px;
min-height:46px;
padding:12px 14px;
border-radius:14px;
font-size:14px;
font-weight:900;
transition:transform .15s ease, box-shadow .15s ease;
}

.share-btn:hover{
transform:translateY(-1px);
}

.share-btn.primary{
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
box-shadow:0 12px 24px rgba(34,211,238,.18);
}

.share-btn.dark{
background:linear-gradient(135deg,#111827 0%,#1f2937 100%);
color:#fff;
box-shadow:0 12px 24px rgba(15,23,42,.14);
}

.share-btn.light{
background:#eef2ff;
color:#1e293b;
border:1px solid #dbe3f8;
}

.share-status{
margin-top:12px;
min-height:20px;
font-size:13px;
font-weight:900;
color:#059669;
}

.upgrade{
display:none;
margin-top:28px;
padding:24px;
text-align:center;
background:
linear-gradient(135deg, rgba(139,92,246,.18) 0%, rgba(34,211,238,.16) 100%),
linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.04) 100%);
}

.upgrade h3{
margin:0 0 8px;
font-size:30px;
line-height:1.15;
color:#fff;
text-wrap:balance;
}

.upgrade-copy{
margin:0 auto;
max-width:600px;
color:#d5e2f4;
font-size:15px;
line-height:1.68;
}

.plan{
width:100%;
margin-top:14px;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
font-weight:900;
padding:15px;
box-shadow:0 14px 28px rgba(34,211,238,.18);
}

.plan.secondary{
background:linear-gradient(135deg,#2563eb 0%,#06b6d4 100%);
}

.plan.tertiary{
background:linear-gradient(135deg,#0f766e 0%,#10b981 100%);
}

.subscriber-link{
margin-top:14px;
text-align:center;
}

.subscriber-link button{
background:none;
border:none;
padding:0;
min-height:auto;
font-size:14px;
color:#bff7ff;
font-weight:800;
text-decoration:underline;
cursor:pointer;
}

.content-section{
margin-top:34px;
padding-bottom:36px;
}

.content-bridge{
margin:0 0 24px;
padding:18px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
font-size:15px;
color:#d6e3f7;
font-weight:800;
line-height:1.66;
}

.content-header-band{
display:grid;
gap:14px;
margin:0 0 24px;
}

.content-pulse{
display:grid;
grid-template-columns:repeat(3,minmax(0,1fr));
gap:12px;
}

.pulse-card{
padding:14px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
}

.pulse-label{
font-size:12px;
font-weight:900;
letter-spacing:.08em;
text-transform:uppercase;
color:#8be9ff;
margin-bottom:6px;
}

.pulse-card p{
margin:0;
font-size:14px;
font-weight:800;
line-height:1.6;
color:#d6e3f7;
}

.content-section h2,
.content-section h3{
margin:0 0 14px;
color:#fff;
line-height:1.08;
letter-spacing:-.035em;
font-weight:900;
text-wrap:balance;
}

.content-section h2{
font-size:40px;
}

.content-section h3{
font-size:28px;
margin-top:30px;
}

.content-body{
font-size:18px;
color:#d7e4f8;
}

.content-body p{
margin:0 0 20px;
}

.content-body ul{
margin:0 0 20px;
padding-left:22px;
}

.content-body li{
margin-bottom:10px;
}

.link-section{
margin-top:28px;
padding-top:24px;
border-top:1px solid rgba(255,255,255,.08);
}

.related-links{
margin:0;
padding-left:22px;
}

.related-links li{
margin-bottom:10px;
}

.related-links a{
color:#8be9ff;
font-weight:800;
}

.related-links a:hover{
text-decoration:underline;
}

.share-loop-panel{
margin-top:28px;
padding:20px;
border-radius:24px;
background:
linear-gradient(135deg, rgba(16,185,129,.12) 0%, rgba(34,211,238,.12) 100%),
linear-gradient(180deg, rgba(255,255,255,.06) 0%, rgba(255,255,255,.04) 100%);
border:1px solid rgba(255,255,255,.10);
box-shadow:var(--shadow-md);
}

.share-loop-panel h3{
margin-top:0;
}

.share-loop-copy{
font-size:15px;
font-weight:800;
color:#d7e4f8;
line-height:1.68;
margin-bottom:14px;
}

.share-loop-grid{
display:grid;
grid-template-columns:repeat(3,minmax(0,1fr));
gap:10px;
}

.loop-box{
padding:14px;
border-radius:18px;
background:rgba(255,255,255,.06);
border:1px solid rgba(255,255,255,.08);
}

.loop-box strong{
display:block;
font-size:13px;
margin-bottom:4px;
color:#fff;
}

.loop-box span{
display:block;
font-size:13px;
font-weight:800;
line-height:1.56;
color:#c8d7ed;
}

.content-close{
margin-top:28px;
padding:18px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
font-size:15px;
font-weight:800;
color:#d7e4f8;
line-height:1.72;
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
.container,.content-section{margin-left:12px;margin-right:12px;padding:18px;border-radius:24px;}
.top-bar{padding:10px 10px;}
.top-actions{gap:8px;margin-right:0;}
.logo{font-size:13px;margin-left:2px;padding:9px 12px;}
.app-top{font-size:13px;padding:8px 10px;}
.upgrade-top{font-size:13px;padding:8px 10px;margin-right:0;}
.upgrade h3{font-size:24px;}
.content-section h2{font-size:30px;line-height:1.12;}
.content-section h3{font-size:24px;}
.content-body{font-size:16px;}
.answer-card h2{font-size:22px;}
.card-heading{font-size:18px;}
.tool-top h2{font-size:24px;}
.share-grid,.content-pulse,.share-loop-grid{grid-template-columns:1fr;}
.share-btn{width:100%;}
}
</style>
</head>

<body>

<div class="top-bar">
  <a class="logo" href="https://verixiaapps.com/check/">
    <span class="logo-dot"></span>
    <span>Scam Check Now</span>
  </a>
  <div class="top-actions">
    <a class="app-top" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">📱 Get App</a>
    <button class="upgrade-top" onclick="showUpgrade()">Upgrade</button>
  </div>
</div>

<div class="page-shell">

  <div class="hero">
    <div class="hero-badge-row">
      <div class="hero-badge">Live scam checking</div>
      <div class="hero-badge">Premium warning page</div>
      <div class="hero-badge">Built for repeat use</div>
    </div>

    <h1 id="heroKeyword"></h1>
    <p id="heroSubheading"></p>

    <div class="hero-trust">
      <div class="hero-trust-chip">Check before you click</div>
      <div class="hero-trust-chip">Check before you reply</div>
      <div class="hero-trust-chip">Check before you send money</div>
    </div>
  </div>

  <div class="container">
    <div class="answer-card" id="answerCard">
      <div class="answer-kicker">Quick answer</div>
      <h2 id="answerHeading">Should you trust this message?</h2>
      <p id="answerSummary">Use the checker below before you click, reply, send money, or share personal information. Messages like this often use urgency, fake authority, and misleading links to push fast decisions.</p>
    </div>

    <div class="precheck-layout" id="precheckLayout">
      <div class="pattern-card" id="patternCard">
        <h3 class="card-heading" id="patternHeading">How this scam pattern usually works</h3>
        <p class="card-copy" id="patternCopy">These messages often try to create pressure first, then push you toward a payment, login, code, or urgent reply.</p>
        <div class="steps-grid" id="patternSteps"></div>
        <div class="example-band" id="exampleBand"></div>
      </div>

      <div class="warning-card" id="warningCard">
        <h3 class="card-heading" id="warningHeading">Red flags to look for before you act</h3>
        <p class="card-copy" id="warningCopy">Even when the message looks polished, a few small warning signs are often enough to stop a costly mistake.</p>
        <div class="warning-grid" id="warningGrid"></div>
      </div>
    </div>

    <div class="tool-shell">
      <div class="tool-top">
        <h2 id="toolHeading">Check the suspicious message now</h2>
        <p id="toolCopy">Paste the message, email, website, job offer, or link below to review scam risk, warning signs, and what to do next.</p>
      </div>

      <textarea id="text" placeholder="Paste the message, email, website, link, or job offer you're unsure about..."></textarea>

      <div class="input-help">Examples: delivery text, PayPal alert, crypto message, job offer, account warning</div>

      <button class="check" onclick="check()">🔍 Check Scam Risk</button>

      <div class="note">No signup required • 1 free check • Results in seconds</div>

      <input id="email" placeholder="Already subscribed? Enter your payment email to unlock unlimited checks">

      <div class="note">Use the same email you entered during checkout</div>

      <div id="postPurchase" class="success">
        ✅ Payment successful — unlimited access is active on this browser
      </div>

      <div class="tool-assurance">Get a clear risk level, key warning signs, and what to do next before you click, reply, send money, or share information.</div>

      <div id="result"></div>
    </div>

    <div class="app-link-card">
      <h4>Keep it on your phone for the next one</h4>
      <p>Scam attempts often do not happen once. Keep the checker ready so the next text, DM, email, or link is easier to review in seconds.</p>
      <a class="app-link-button" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">Download the App</a>
    </div>

    <div class="upgrade" id="upgrade">
      <h3>Stay Ready for the Next Suspicious Message</h3>

      <div class="upgrade-copy">
        Most scam attempts do not happen once. If you are seeing suspicious messages, links, or requests, more may follow. Check each one before it costs you.
      </div>

      <div style="margin-top:10px;font-size:13px;color:#d4e2f5;">
        Built for ongoing protection against scams, phishing, impersonation, and risky payment requests
      </div>

      <div style="margin-top:8px;margin-bottom:10px;font-size:14px;color:#d4e2f5;">
        Unlimited scam checks • Cancel anytime
      </div>

      <button class="plan" onclick="checkout('price_1T8KOTJjMzyHDzeQDDg1A2TF')">Weekly Protection</button>
      <button class="plan secondary" onclick="checkout('price_1T8KOUJjMzyHDzeQxaqPFOSB')">Monthly Protection</button>
      <button class="plan tertiary" onclick="checkout('price_1T8KOQJjMzyHDzeQfcU1C1MQ')">Yearly Protection</button>

      <div style="margin-top:14px;font-size:13px;color:#d4e2f5;">
        Secure payments powered by Stripe
      </div>

      <div class="subscriber-link">
        <button type="button" onclick="scrollToEmail()">Already subscribed? Enter your email</button>
      </div>
    </div>
  </div>

  <section class="content-section">
    <div id="contentBridge" class="content-bridge"></div>

    <div class="content-header-band">
      <div class="content-pulse">
        <div class="pulse-card">
          <div class="pulse-label">Trust signal</div>
          <p>Focused pages and clearer warnings help people slow down before clicking or paying.</p>
        </div>
        <div class="pulse-card">
          <div class="pulse-label">Return signal</div>
          <p>People often come back when the next suspicious message, link, or request shows up.</p>
        </div>
        <div class="pulse-card">
          <div class="pulse-label">Search signal</div>
          <p>Clean topic coverage and strong internal links make this easier to discover and reuse.</p>
        </div>
      </div>
    </div>

    <h2 id="contentHeading"></h2>
    <div id="seoContent" class="content-body">{{AI_CONTENT}}</div>

    <div class="link-section" id="relatedLinksWrap">
      <h3 id="relatedHeading">Check Similar Messages</h3>
      <ul id="relatedLinks" class="related-links">{{RELATED_LINKS}}</ul>
    </div>

    <div class="link-section" id="moreLinksWrap">
      <h3 id="moreLinksHeading">More Scam Checks</h3>
      <ul id="moreLinks" class="related-links">{{MORE_LINKS}}</ul>
    </div>

    <div class="share-loop-panel">
      <h3>Why this page works beyond one visit</h3>
      <div class="share-loop-copy">
        A strong warning page should not only answer one question. It should help someone pause, verify, return later, and use the checker again when the next suspicious message appears.
      </div>
      <div class="share-loop-grid">
        <div class="loop-box">
          <strong>1. Find it</strong>
          <span>Search lands people on a focused page for the exact suspicious topic they are dealing with.</span>
        </div>
        <div class="loop-box">
          <strong>2. Use it</strong>
          <span>They run the checker before clicking links, replying, paying, or sharing personal details.</span>
        </div>
        <div class="loop-box">
          <strong>3. Reuse it</strong>
          <span>They return when another text, email, job offer, tracking alert, or payment request shows up.</span>
        </div>
      </div>
    </div>

    <div class="content-close">
      Messages like this are one of the most common ways people lose money, share codes, or hand over access without realizing it. When something feels off, pause and verify it through official sources before taking action.
    </div>
  </section>

  <footer class="footer">
    <div>
      By using this website you agree to our
      <a href="https://verixiaapps.com/website-policies/scam-check/" target="_blank" rel="noopener noreferrer">Terms and Privacy Policy</a>.
    </div>
    <div style="margin-top:10px">
      Scam Check Now © 2026 • Scam detection and risk analysis tool
    </div>
  </footer>

</div>

<script>
const API = "https://awake-integrity-production-faa0.up.railway.app";
const RAW_KEYWORD = "{{KEYWORD}}";
const BROWSER_SUB_KEY = "scam_check_browser_subscribed";

window.addEventListener("load", function () {
  const params = new URLSearchParams(window.location.search);

  if (params.get("subscribed") === "true") {
    localStorage.setItem(BROWSER_SUB_KEY, "true");
    document.getElementById("postPurchase").style.display = "block";
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  if (isBrowserSubscribed()) {
    document.getElementById("postPurchase").style.display = "block";
  }

  setKeywordHeadings();
  applyPreviewContent();
  applyIntentToChecker();
  cleanSeoContent();
  cleanRelatedLinks();
  cleanMoreLinks();
  normalizeBottomLinks();
});

function isBrowserSubscribed() {
  return localStorage.getItem(BROWSER_SUB_KEY) === "true";
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;")
    .replace(/'/g,"&#39;");
}

function normalizeKeyword(str) {
  return String(str || "")
    .replace(/\s+/g, " ")
    .replace(/[–—]/g, "-")
    .trim();
}

function stripLeadingQuestionPrefixes(text) {
  return String(text || "")
    .replace(/^\s*is\s+/i, "")
    .replace(/^\s*can\s+i\s+trust\s+/i, "")
    .replace(/^\s*did\s+i\s+get\s+scammed\s+(?:by|on|with)\s+/i, "")
    .trim();
}

function stripTrailingQuestionSuffixes(text) {
  return String(text || "")
    .replace(/\s+a\s+scam$/i, "")
    .replace(/\s+or\s+legit$/i, "")
    .replace(/\s+or\s+scam$/i, "")
    .replace(/\s+legit$/i, "")
    .replace(/\s+real$/i, "")
    .replace(/\s+safe$/i, "")
    .replace(/\s+scam$/i, "")
    .replace(/\s+a$/i, "")
    .trim();
}

function cleanKeywordBase(keyword) {
  let text = normalizeKeyword(keyword);
  text = stripLeadingQuestionPrefixes(text);
  text = stripTrailingQuestionSuffixes(text);
  return text.replace(/\s+/g, " ").trim();
}

function cleanKeywordForSentence(keyword) {
  return cleanKeywordBase(keyword)
    .replace(/\bmessage\b/gi, "")
    .replace(/\bmessages\b/gi, "")
    .replace(/\bemail\b/gi, "")
    .replace(/\bemails\b/gi, "")
    .replace(/\btext\b/gi, "")
    .replace(/\btexts\b/gi, "")
    .replace(/\blink\b/gi, "")
    .replace(/\blinks\b/gi, "")
    .replace(/\bwebsite\b/gi, "")
    .replace(/\bwebsites\b/gi, "")
    .replace(/\balert\b/gi, "")
    .replace(/\balerts\b/gi, "")
    .replace(/\bwarning\b/gi, "")
    .replace(/\bwarnings\b/gi, "")
    .replace(/\bnotification\b/gi, "")
    .replace(/\bnotifications\b/gi, "")
    .replace(/\brequest\b/gi, "")
    .replace(/\brequests\b/gi, "")
    .replace(/\boffer\b/gi, "")
    .replace(/\boffers\b/gi, "")
    .replace(/\bscam\b/gi, "")
    .replace(/\bscams\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

function displayKeyword(str) {
  const text = normalizeKeyword(str);
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function displayCleanKeyword(str) {
  return displayKeyword(cleanKeywordBase(str));
}

function containsAny(text, phrases) {
  return phrases.some(phrase => text.includes(phrase));
}

function isGuidanceStyleKeyword(lower) {
  return (
    lower.startsWith("how to ") ||
    lower.startsWith("what to do after ") ||
    lower.startsWith("how to recover after ") ||
    lower.startsWith("how to secure ") ||
    lower.startsWith("how to block ") ||
    lower.startsWith("how to avoid ") ||
    lower.startsWith("what happens after ") ||
    lower.startsWith("what is ") ||
    lower.startsWith("why ") ||
    lower.startsWith("when ") ||
    lower.startsWith("where ") ||
    lower.startsWith("who ")
  );
}

function isQuestionStyleKeyword(lower) {
  return (
    lower.startsWith("is ") ||
    lower.startsWith("can ") ||
    lower.startsWith("should ") ||
    lower.startsWith("could ") ||
    lower.startsWith("would ") ||
    lower.startsWith("do ") ||
    lower.startsWith("does ") ||
    lower.startsWith("did ")
  );
}

function chooseBridgeIntro(baseKeyword) {
  const readable = displayKeyword(baseKeyword);
  const variants = [
    `If this ${readable} just showed up,`,
    `If you're unsure about this ${readable},`,
    `If you're looking at this ${readable} right now,`
  ];
  const index = baseKeyword.length % variants.length;
  return variants[index];
}

function getVariantNumber(keyword) {
  const text = normalizeKeyword(keyword || "default");
  let sum = 0;
  for (let i = 0; i < text.length; i++) sum += text.charCodeAt(i);
  return (sum % 3) + 1;
}

function buildHeroTitle(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const cleanTitle = displayCleanKeyword(keywordRaw);
  const readableTitle = displayKeyword(raw);

  if (!raw) {
    return "Is this a scam? Check Before You Click or Send Money";
  }

  if (isGuidanceStyleKeyword(lower)) {
    return `${readableTitle}: Safety Tips, Warning Signs & What To Do`;
  }

  if (lower.startsWith("did i get scammed")) {
    return `${readableTitle}? Signs, Risks & What To Do Next`;
  }

  if (lower.startsWith("can scammers") || lower.startsWith("can someone")) {
    return `${readableTitle}? Risks, Warning Signs & What To Do`;
  }

  if (lower.startsWith("almost ")) {
    return `${readableTitle}? Warning Signs & Safety Steps`;
  }

  if (lower.startsWith("is this ")) {
    return `${readableTitle}? Check Warning Signs & What To Do`;
  }

  if (lower.startsWith("is ") && lower.includes(" legit")) {
    const withoutLegit = raw.replace(/\s+legit\b/i, "").trim();
    return `${displayKeyword(withoutLegit)} Legit or a Scam? Warning Signs & What To Do`;
  }

  if (isQuestionStyleKeyword(lower)) {
    return `${readableTitle}? Risks, Warning Signs & What To Know`;
  }

  return `Is ${cleanTitle} a Scam? Check Before You Click or Send Money`;
}

function buildHeroSubheading(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const readableKeyword = displayKeyword(cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw);

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker below to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information.";
  }

  return `Messages related to ${readableKeyword} can be used to steal money, codes, or account access. Paste it below before you click, reply, send money, or take action.`;
}

function buildContentHeading(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const readableTitle = displayKeyword(raw);
  const cleanTitle = displayCleanKeyword(keywordRaw);

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower) || lower.startsWith("almost ")) {
    return readableTitle;
  }

  return `What ${cleanTitle} Messages, Links, and Offers Often Look Like`;
}

function buildContentBridge(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const cleanSentenceKeyword = cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw;

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker above to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information.";
  }

  if (lower.startsWith("almost ")) {
    return "If you are unsure what happened, use the checker above to review suspicious messages, emails, links, and offers before taking action.";
  }

  return `${chooseBridgeIntro(cleanSentenceKeyword)} use the checker above before you click links, reply, send money, or share information. Messages like this are one of the most common ways people lose money or hand over account access without realizing it.`;
}

function buildAnswerHeading(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const cleanTitle = displayCleanKeyword(keywordRaw);

  if (!raw) return "Should you trust this message?";

  if (isGuidanceStyleKeyword(lower)) return `${displayKeyword(raw)}`;
  if (isQuestionStyleKeyword(lower)) return `${displayKeyword(raw)}`;
  return `${cleanTitle}: quick scam check`;
}

function buildAnswerSummary(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const readable = displayKeyword(cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw);

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker below before you click, reply, send money, or share personal information. Scam messages often rely on urgency, fake authority, and misleading links to push fast decisions.";
  }

  return `${readable} messages can be used to push fake urgency, steal account access, or trigger payments before you have time to verify what is real. Use the checker below before taking action.`;
}

function setKeywordHeadings() {
  const keywordRaw = (RAW_KEYWORD || "this message").trim();

  document.getElementById("heroKeyword").textContent = buildHeroTitle(keywordRaw);
  document.getElementById("heroSubheading").textContent = buildHeroSubheading(keywordRaw);
  document.getElementById("contentHeading").textContent = buildContentHeading(keywordRaw);
  document.getElementById("contentBridge").textContent = buildContentBridge(keywordRaw);
  document.getElementById("answerHeading").textContent = buildAnswerHeading(keywordRaw);
  document.getElementById("answerSummary").textContent = buildAnswerSummary(keywordRaw);
}

function setStepItems(items) {
  const wrap = document.getElementById("patternSteps");
  wrap.innerHTML = items.map((item, index) => `
    <div class="step-item">
      <div class="step-number">${index + 1}</div>
      <div class="step-text">
        <strong>${escapeHtml(item.title)}</strong>
        <span>${escapeHtml(item.text)}</span>
      </div>
    </div>
  `).join("");
}

function setWarningItems(items) {
  const wrap = document.getElementById("warningGrid");
  wrap.innerHTML = items.map(item => `
    <div class="warning-item">
      <div class="warning-icon">⚠️</div>
      <div class="warning-text">
        <strong>${escapeHtml(item.title)}</strong>
        <span>${escapeHtml(item.text)}</span>
      </div>
    </div>
  `).join("");
}

function buildVariantLayout(variant, options) {
  const precheckLayout = document.getElementById("precheckLayout");
  const patternCard = document.getElementById("patternCard");
  const warningCard = document.getElementById("warningCard");

  if (variant === 1) {
    precheckLayout.innerHTML = "";
    precheckLayout.appendChild(patternCard);
    precheckLayout.appendChild(warningCard);
  } else if (variant === 2) {
    precheckLayout.innerHTML = "";
    precheckLayout.appendChild(warningCard);
    precheckLayout.appendChild(patternCard);
  } else {
    precheckLayout.innerHTML = "";
    precheckLayout.appendChild(patternCard);
    precheckLayout.appendChild(warningCard);
  }

  document.getElementById("patternHeading").textContent = options.patternHeading;
  document.getElementById("patternCopy").textContent = options.patternCopy;
  document.getElementById("warningHeading").textContent = options.warningHeading;
  document.getElementById("warningCopy").textContent = options.warningCopy;
  document.getElementById("exampleBand").innerHTML = `<strong>${escapeHtml(options.exampleLabel)}</strong>${escapeHtml(options.exampleText)}`;

  setStepItems(options.steps);
  setWarningItems(options.warnings);
}

function applyPreviewContent() {
  const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
  const lower = keywordRaw.toLowerCase();
  const variant = getVariantNumber(keywordRaw);

  let options = {
    patternHeading: "How this scam pattern usually works",
    patternCopy: "These messages often try to create pressure first, then push you toward a payment, login, code, or urgent reply.",
    warningHeading: "Red flags to look for before you act",
    warningCopy: "Even when the message looks polished, a few small warning signs are often enough to stop a costly mistake.",
    exampleLabel: "Common example",
    exampleText: "Urgent message asking you to verify an account, send money, click a link, or share a one-time code.",
    steps: [
      { title: "Create urgency", text: "The message tries to make delay feel risky or expensive." },
      { title: "Push one action", text: "It points you toward a link, payment, code, reply, or login." },
      { title: "Reduce verification", text: "It tries to keep you inside the message instead of checking through official sources." }
    ],
    warnings: [
      { title: "Urgency or pressure", text: "Warnings, deadlines, threats, or limited-time demands." },
      { title: "Requests for money or codes", text: "Gift cards, transfers, payment apps, or one-time passcodes." },
      { title: "Suspicious links or sender details", text: "A message that looks official but points somewhere slightly wrong." }
    ]
  };

  if (containsAny(lower, ["job", "recruiter", "interview", "hiring", "onboarding"])) {
    options = {
      patternHeading: "How fake job messages usually work",
      patternCopy: "Scammers often use fast praise, remote-work appeal, and urgent next steps to move people quickly toward fees, personal details, or fake onboarding.",
      warningHeading: "Job offer warning signs to notice first",
      warningCopy: "A message can sound professional and still be dangerous when the details move too fast or ask for the wrong things too early.",
      exampleLabel: "Common example",
      exampleText: "A recruiter says you are hired quickly, then asks for identity details, a payment, or a chat on a non-official app.",
      steps: [
        { title: "Create excitement fast", text: "The message suggests quick approval, easy money, or immediate hiring." },
        { title: "Move off-platform", text: "You are pushed to text, Telegram, WhatsApp, or another channel quickly." },
        { title: "Ask for sensitive info or money", text: "The scam often shifts toward fees, identity details, or payment setup." }
      ],
      warnings: [
        { title: "Too fast or too easy", text: "No real screening, instant offer, or unusually high pay for little detail." },
        { title: "Payment or equipment requests", text: "You are asked to buy something, send money, or use a personal account." },
        { title: "Unverified recruiter identity", text: "The sender domain, company site, or role details do not fully match." }
      ]
    };
  } else if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft"])) {
    options = {
      patternHeading: "How crypto scams usually work",
      patternCopy: "Crypto scams often combine urgency, technical-looking language, and promises of recovery, support, or rewards to trigger fast transfers or wallet approvals.",
      warningHeading: "Crypto red flags to catch early",
      warningCopy: "When a message wants speed, trust, and wallet access at the same time, that is usually the danger zone.",
      exampleLabel: "Common example",
      exampleText: "A message claims your wallet is at risk, an airdrop is waiting, or funds can be recovered if you act now.",
      steps: [
        { title: "Create fear or greed", text: "The message warns of loss or promises a fast gain or recovery." },
        { title: "Push wallet action", text: "You are asked to connect, approve, sign, or transfer." },
        { title: "Use urgency to bypass caution", text: "It tries to stop you from checking the project, wallet, or support source." }
      ],
      warnings: [
        { title: "Wallet connect pressure", text: "The message wants you to approve something immediately." },
        { title: "Recovery or support claims", text: "Scammers often impersonate exchange staff, support, or recovery services." },
        { title: "Guaranteed returns or rewards", text: "Airdrops, presales, and recovery promises are common hooks." }
      ]
    };
  } else if (containsAny(lower, ["delivery", "usps", "ups", "fedex", "package", "shipment", "parcel"])) {
    options = {
      patternHeading: "How delivery scams usually work",
      patternCopy: "Delivery scams use missing-package anxiety, tracking confusion, and small payment requests to get fast clicks before you verify the shipment.",
      warningHeading: "Delivery message red flags to check",
      warningCopy: "A package message can feel routine, which is exactly why fake tracking links work so well.",
      exampleLabel: "Common example",
      exampleText: "A text says your package is delayed and asks you to click a tracking link or pay a small fee to release it.",
      steps: [
        { title: "Trigger concern", text: "The message suggests a missed package, delay, customs issue, or failed delivery." },
        { title: "Push a link", text: "You are sent to a fake tracking or payment page." },
        { title: "Collect details", text: "The scam then asks for payment info, personal data, or account credentials." }
      ],
      warnings: [
        { title: "Unexpected link", text: "The message sends you somewhere other than the official carrier app or site." },
        { title: "Small payment demand", text: "A fake re-delivery or customs fee is a common trap." },
        { title: "Timing pressure", text: "It says the package will be returned or cancelled if you do not act fast." }
      ]
    };
  } else if (containsAny(lower, ["bank", "paypal", "venmo", "zelle", "cash app", "amazon", "refund", "payment"])) {
    options = {
      patternHeading: "How payment and account scams usually work",
      patternCopy: "These scams often create account panic first, then steer you toward a fake login, urgent transfer, or verification step.",
      warningHeading: "Account and payment red flags",
      warningCopy: "When a message makes you feel like your money or account is in danger, slowing down matters most.",
      exampleLabel: "Common example",
      exampleText: "A message says there was suspicious activity, a refund issue, or a payment problem and asks you to verify immediately.",
      steps: [
        { title: "Create account fear", text: "The message suggests fraud, payment failure, refund issues, or suspicious activity." },
        { title: "Push a verification step", text: "You are told to log in, call a number, or confirm details through the message." },
        { title: "Collect money or access", text: "The scam targets your credentials, payment details, or direct transfer." }
      ],
      warnings: [
        { title: "Unexpected account warning", text: "The message appears serious but arrives without context or through the wrong channel." },
        { title: "Login or money request", text: "It asks for payment details, credentials, or direct transfer confirmation." },
        { title: "Unofficial contact path", text: "Links, phone numbers, or reply instructions do not match the real company." }
      ]
    };
  } else if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    options = {
      patternHeading: "How scam messages often work",
      patternCopy: "Most scams rely on pressure, confusion, and trust signals that look real enough to trigger quick action before proper verification happens.",
      warningHeading: "What to check before you trust it",
      warningCopy: "The safest move is to slow the message down and look at the sender, request, and path it wants you to take.",
      exampleLabel: "Common example",
      exampleText: "A polished message claims something urgent happened and tells you to click, verify, or send something immediately.",
      steps: [
        { title: "Create urgency", text: "The message makes the problem sound immediate or costly." },
        { title: "Direct one action", text: "It funnels you toward a link, reply, code, login, or payment." },
        { title: "Avoid outside verification", text: "It tries to keep you from checking through the real company or platform." }
      ],
      warnings: [
        { title: "A fast decision is required", text: "Pressure is one of the most reliable scam indicators." },
        { title: "You are asked for money, codes, or logins", text: "That is where the scam usually becomes costly." },
        { title: "The message wants trust before proof", text: "Real verification should happen outside the message itself." }
      ]
    };
  }

  document.getElementById("toolHeading").textContent = "Check the suspicious message now";
  document.getElementById("toolCopy").textContent = "Paste the message, email, website, job offer, or link below to review scam risk, warning signs, and what to do next.";

  buildVariantLayout(variant, options);
}

function applyIntentToChecker() {
  const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
  const lower = keywordRaw.toLowerCase();
  const textarea = document.getElementById("text");
  const inputHelp = document.querySelector(".input-help");

  if (!textarea || !inputHelp) return;

  if (containsAny(lower, ["job", "recruiter", "interview", "hiring", "onboarding"])) {
    textarea.placeholder = "Paste the job message, recruiter email, interview request, or onboarding text you're unsure about...";
    inputHelp.textContent = "Examples: recruiter email, interview request, onboarding message, job offer, payment request";
    return;
  }

  if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft"])) {
    textarea.placeholder = "Paste the crypto message, wallet request, token offer, or support message you're unsure about...";
    inputHelp.textContent = "Examples: wallet connect message, token airdrop, exchange alert, support DM, recovery offer";
    return;
  }

  if (containsAny(lower, ["delivery", "usps", "ups", "fedex", "package", "shipment", "parcel"])) {
    textarea.placeholder = "Paste the delivery text, tracking update, shipping email, or package link you're unsure about...";
    inputHelp.textContent = "Examples: USPS text, FedEx email, tracking link, customs fee message, missed delivery alert";
    return;
  }

  if (containsAny(lower, ["bank", "paypal", "venmo", "zelle", "cash app", "amazon", "refund", "payment"])) {
    textarea.placeholder = "Paste the payment alert, account message, refund email, or login request you're unsure about...";
    inputHelp.textContent = "Examples: PayPal alert, bank text, Amazon refund email, Venmo request, Zelle message";
    return;
  }

  textarea.placeholder = "Paste the message, email, website, link, or job offer you're unsure about...";
  inputHelp.textContent = "Examples: delivery text, PayPal alert, crypto message, job offer, account warning";
}

function cleanSeoContent() {
  const seoContent = document.getElementById("seoContent");
  if (!seoContent) return;

  seoContent.innerHTML = seoContent.innerHTML
    .replace(/\*\*/g, "")
    .replace(/<p>\s*<\/p>/g, "")
    .trim();
}

function cleanRelatedLinks() {
  const relatedLinksWrap = document.getElementById("relatedLinksWrap");
  const relatedLinks = document.getElementById("relatedLinks");
  const relatedHeading = document.getElementById("relatedHeading");
  if (!relatedLinksWrap || !relatedLinks || !relatedHeading) return;

  relatedLinks.innerHTML = relatedLinks.innerHTML.replace(/\*\*/g, "").trim();

  const links = relatedLinks.querySelectorAll("li a");

  if (links.length === 0) {
    relatedLinksWrap.style.display = "none";
    return;
  }

  relatedLinksWrap.style.display = "";
  relatedLinks.style.display = "";
  relatedHeading.style.display = "";
}

function cleanMoreLinks() {
  const moreLinksWrap = document.getElementById("moreLinksWrap");
  const moreLinks = document.getElementById("moreLinks");
  const moreLinksHeading = document.getElementById("moreLinksHeading");

  if (!moreLinksWrap || !moreLinks || !moreLinksHeading) return;

  moreLinks.innerHTML = moreLinks.innerHTML.replace(/\*\*/g, "").trim();

  const links = moreLinks.querySelectorAll("li a");
  if (links.length === 0) {
    moreLinksWrap.style.display = "none";
    return;
  }

  moreLinksWrap.style.display = "";
  moreLinks.style.display = "";
  moreLinksHeading.style.display = "";
}

function normalizeBottomLinks() {
  const relatedLinksWrap = document.getElementById("relatedLinksWrap");
  const relatedLinks = document.getElementById("relatedLinks");
  const relatedHeading = document.getElementById("relatedHeading");
  const moreLinksWrap = document.getElementById("moreLinksWrap");
  const moreLinks = document.getElementById("moreLinks");
  const moreLinksHeading = document.getElementById("moreLinksHeading");

  if (!relatedLinksWrap || !relatedLinks || !relatedHeading || !moreLinksWrap || !moreLinks || !moreLinksHeading) return;

  const relatedCount = relatedLinks.querySelectorAll("li a").length;
  const moreCount = moreLinks.querySelectorAll("li a").length;

  if (relatedCount === 0 && moreCount > 0) {
    moreLinksHeading.textContent = "Related Scam Checks";
  }

  if (relatedCount > 0 && moreCount > 0) {
    moreLinksHeading.textContent = "More Scam Checks";
  }
}

function summaryForRisk(riskClass) {
  if (riskClass === "high") {
    return "This message shows multiple scam signals. Treat it as unsafe until you verify it directly through the official website, app, company, or platform.";
  }
  if (riskClass === "medium") {
    return "This message shows warning signs. Be cautious and verify the sender, offer, or website before you click, reply, send money, or share information.";
  }
  if (riskClass === "low") {
    return "This message shows fewer obvious scam signals, but you should still verify anything involving links, payments, logins, or personal information before taking action.";
  }
  return "We could not determine a clear risk level. Treat the message cautiously and verify it through official sources before you do anything else.";
}

function paylineForRisk(riskClass) {
  if (riskClass === "high") {
    return "People lose money from messages like this every day. If another one shows up tomorrow, guessing wrong could cost you.";
  }
  if (riskClass === "medium") {
    return "Suspicious messages often do not stop at one. If you have seen one, more may follow. Check the next one before you click, reply, or pay.";
  }
  if (riskClass === "low") {
    return "Even lower-risk messages can become expensive when later versions ask for logins, payments, codes, or urgent action.";
  }
  return "When the risk is unclear, the safest move is to pause, verify this one, and treat the next similar message carefully too.";
}

function cardClassForRisk(risk) {
  if (risk === "high") return "high";
  if (risk === "medium") return "medium";
  if (risk === "low") return "low";
  return "unknown";
}

function iconForRisk(risk) {
  if (risk === "high") return "🔴";
  if (risk === "medium") return "🟠";
  if (risk === "low") return "🟢";
  return "⚪";
}

function signalIconForRisk(risk) {
  if (risk === "high") return "⚠️";
  if (risk === "medium") return "⚠️";
  if (risk === "low") return "✔️";
  return "•";
}

function chipByRisk(risk) {
  if (risk === "high") return "Pattern Match: Strong";
  if (risk === "medium") return "Pattern Match: Moderate";
  if (risk === "low") return "Pattern Match: Lower Risk";
  return "Pattern Match: Review Needed";
}

function scrollToTopCheck() {
  const textarea = document.getElementById("text");
  if (!textarea) return;
  window.scrollTo({ top: 0, behavior: "smooth" });
  setTimeout(() => textarea.focus(), 300);
}

function getShareUrl() {
  return window.location.href;
}

function getShareText() {
  return "This message may be a scam. Check it before you click, reply, or send money:";
}

function getWarningMessage() {
  return `This message may be a scam.
Check it before you click, reply, or send money:
${getShareUrl()}`;
}

function showShareStatus(message) {
  const status = document.getElementById("shareStatus");
  if (!status) return;
  status.textContent = message;
  clearTimeout(showShareStatus.timeoutId);
  showShareStatus.timeoutId = setTimeout(() => {
    status.textContent = "";
  }, 2200);
}

function shareNative() {
  const shareData = {
    title: document.title,
    text: getShareText(),
    url: getShareUrl()
  };

  if (navigator.share) {
    navigator.share(shareData).catch(() => {});
    return;
  }

  copyWarningMessage();
}

function shareX() {
  const text = encodeURIComponent(getShareText());
  const url = encodeURIComponent(getShareUrl());
  window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, "_blank", "noopener,noreferrer");
}

function copyLink() {
  const url = getShareUrl();

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(() => {
      showShareStatus("Link copied.");
    }).catch(() => {
      fallbackCopy(url, "Link copied.");
    });
    return;
  }

  fallbackCopy(url, "Link copied.");
}

function copyWarningMessage() {
  const message = getWarningMessage();

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(message).then(() => {
      showShareStatus("Warning copied.");
    }).catch(() => {
      fallbackCopy(message, "Warning copied.");
    });
    return;
  }

  fallbackCopy(message, "Warning copied.");
}

function fallbackCopy(value, successMessage) {
  const input = document.createElement("textarea");
  input.value = value;
  input.setAttribute("readonly", "");
  input.style.position = "absolute";
  input.style.left = "-9999px";
  document.body.appendChild(input);
  input.select();
  input.setSelectionRange(0, 99999);
  document.execCommand("copy");
  document.body.removeChild(input);
  showShareStatus(successMessage);
}

function formatResult(raw) {
  const lines = String(raw || "").split("\n").map(l => l.trim()).filter(Boolean);

  let risk = "";
  let signals = [];
  let actions = [];
  let mode = "";

  lines.forEach(line => {
    const lower = line.toLowerCase();

    if (lower.includes("risk level")) {
      risk = line.split(":").slice(1).join(":").trim();
      return;
    }

    if (lower.includes("key signals")) {
      mode = "signals";
      return;
    }

    if (lower.includes("recommended action")) {
      mode = "actions";
      return;
    }

    if (line.startsWith("-")) {
      const cleaned = line.replace(/^-+\s*/, "");
      if (mode === "signals") signals.push(cleaned);
      if (mode === "actions") actions.push(cleaned);
    }
  });

  const riskClass = (risk || "review").trim().toLowerCase();
  const safeRiskClass = cardClassForRisk(riskClass);
  const signalIcon = signalIconForRisk(safeRiskClass);
  const continuationLine = safeRiskClass !== "low"
    ? `<div class="result-continuation">If this reached you once, similar messages may already be on the way. Scammers often repeat the same pattern across many people.</div>`
    : "";

  if (signals.length === 0) {
    signals = ["Review the sender, links, and any requests for money, urgency, or personal information."];
  }

  if (actions.length === 0) {
    actions = ["Do not reply, do not click links, and verify directly through the official website, app, company, or platform before taking action."];
  }

  return `
  <div class="result-card ${safeRiskClass}">
    <div class="result-top">
      <div class="risk ${safeRiskClass}">${iconForRisk(safeRiskClass)} ${safeRiskClass === "unknown" ? "Risk Level: REVIEW" : "Risk Level: " + safeRiskClass.toUpperCase()}</div>
      <div class="result-chip">${chipByRisk(safeRiskClass)}</div>
    </div>

    <div class="result-summary">${escapeHtml(summaryForRisk(safeRiskClass))}</div>
    ${continuationLine}

    <div class="section">
      <div class="section-title">Detected Signals</div>
      <ul class="signal-list">
        ${signals.map(s => `<li class="signal-item"><span class="signal-icon">${signalIcon}</span><span>${escapeHtml(s)}</span></li>`).join("")}
      </ul>
    </div>

    <div class="section">
      <div class="section-title">Recommended Actions</div>
      <div class="action-box">${escapeHtml(actions[0])}</div>
    </div>

    <div class="result-payline">${escapeHtml(paylineForRisk(safeRiskClass))}</div>

    <div class="result-actions">
      <button class="check result-cta" onclick="scrollToTopCheck()">🔁 Not sure about another message? Check it now</button>

      <div class="share-wrap">
        <div class="share-alert">⚠️ Messages like this are often sent in waves</div>
        <div class="share-copy">Know someone who could receive this same message? Send this warning before they click, reply, or send money.</div>
        <div class="share-grid">
          <button type="button" class="share-btn primary" onclick="copyWarningMessage()">⚠️ Copy Warning</button>
          <button type="button" class="share-btn dark" onclick="shareNative()">📤 Share</button>
          <button type="button" class="share-btn light" onclick="shareX()">𝕏 Share to X</button>
          <button type="button" class="share-btn light" onclick="copyLink()">🔗 Copy Link</button>
        </div>
        <div class="share-status" id="shareStatus" aria-live="polite"></div>
      </div>
    </div>
  </div>
  `;
}

function showUpgrade() {
  const el = document.getElementById("upgrade");
  if (!el) return;
  el.style.display = "block";
  setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
}

function scrollToEmail() {
  const emailField = document.getElementById("email");
  if (!emailField) return;
  emailField.scrollIntoView({ behavior: "smooth", block: "center" });
  setTimeout(() => emailField.focus(), 150);
}

async function check() {
  const text = document.getElementById("text").value.trim();
  const email = document.getElementById("email").value.trim().toLowerCase();
  const subscribed = isBrowserSubscribed();
  const result = document.getElementById("result");

  if (!text) {
    result.innerHTML = `
      <div class="result-card unknown">
        <div class="result-top">
          <div class="risk unknown">⚪ Paste Something To Check</div>
          <div class="result-chip">Awaiting Input</div>
        </div>
        <div class="result-summary">Paste a suspicious message, email, website, link, job offer, or investment pitch to check scam risk before you act.</div>
      </div>
    `;
    result.style.display = "block";
    return;
  }

  result.style.display = "block";
  result.innerHTML = `
    <div class="result-card unknown">
      <div class="result-top">
        <div class="risk unknown">⚪ Analyzing...</div>
        <div class="result-chip">Scan In Progress</div>
      </div>
      <div class="result-summary">Checking for scam signals, risky patterns, payment traps, impersonation, and suspicious links.</div>
    </div>
  `;

  try {
    const response = await fetch(API + "/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, email, subscribed })
    });

    const data = await response.json();

    if (data.limit) {
      result.innerHTML = `
        <div class="result-card medium">
          <div class="result-top">
            <div class="risk medium">🟠 Free Check Used</div>
            <div class="result-chip">Upgrade Available</div>
          </div>
          <div class="result-summary">Unlock unlimited protection so you can check the next suspicious message, link, or request before it costs you.</div>
        </div>
      `;
      showUpgrade();
      return;
    }

    result.innerHTML = formatResult(data.result || "");
    showUpgrade();
  } catch (e) {
    result.innerHTML = `
      <div class="result-card unknown">
        <div class="result-top">
          <div class="risk unknown">⚪ Unable To Analyze</div>
          <div class="result-chip">Try Again</div>
        </div>
        <div class="result-summary">We could not analyze this right now. Please try again in a moment.</div>
      </div>
    `;
  }
}

async function checkout(priceId) {
  const pageUrl = window.location.origin + window.location.pathname;

  const response = await fetch(API + "/create-checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      priceId,
      email: null,
      successUrl: pageUrl + "?subscribed=true",
      cancelUrl: pageUrl
    })
  });

  const data = await response.json();

  if (data.url) {
    window.location = data.url;
  } else {
    alert("Checkout failed.");
  }
}
</script>

</body>
</html>"""
TEMPLATE_C = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>{{TITLE}}</title>
<meta name="description" content="{{DESCRIPTION}}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{{CANONICAL_URL}}">

<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESCRIPTION}}">
<meta property="og:type" content="website">
<meta property="og:url" content="{{CANONICAL_URL}}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{TITLE}}">
<meta name="twitter:description" content="{{DESCRIPTION}}">

<!-- Schema: WebPage -->
<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@type":"WebPage",
  "name":"{{TITLE}}",
  "description":"{{DESCRIPTION}}",
  "url":"{{CANONICAL_URL}}"
}
</script>

<!-- Schema: FAQ (for SERP lift) -->
<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@type":"FAQPage",
  "mainEntity":[
    {
      "@type":"Question",
      "name":"How can I tell if something is a scam?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Look for urgency, requests for money or codes, suspicious links, and pressure to act quickly. Always verify through official sources."
      }
    },
    {
      "@type":"Question",
      "name":"What should I do if I clicked a suspicious link?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Do not enter any information, close the page, run a security check, and change important passwords if needed."
      }
    },
    {
      "@type":"Question",
      "name":"Why are scam messages so common now?",
      "acceptedAnswer":{
        "@type":"Answer",
        "text":"Scammers use automation and impersonation across email, text, and social platforms to reach large numbers of people quickly."
      }
    }
  ]
}
</script>

<style>
:root{
--bg:#07111f;
--bg-2:#0c1728;
--bg-3:#12203a;
--surface:rgba(255,255,255,.06);
--surface-2:rgba(255,255,255,.08);
--surface-3:#ffffff;
--card:#101c33;
--card-2:#162541;

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
--emerald-2:#059669;
--amber:#f59e0b;
--red:#ef4444;

--blue-soft:#dbeafe;
--violet-soft:#ede9fe;
--green-soft:#ecfdf5;
--amber-soft:#fffbeb;
--red-soft:#fef2f2;

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

button,
textarea,
input{
font-family:inherit;
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
padding:11px 15px;
font-size:14px;
border-radius:16px;
font-weight:900;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
border:none;
cursor:pointer;
white-space:nowrap;
box-shadow:0 16px 34px rgba(34,211,238,.16);
}

.page-shell{
max-width:940px;
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

.container,
.content-section{
max-width:820px;
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

.container::before,
.content-section::before{
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

.container > *,
.content-section > *{
position:relative;
z-index:1;
}

.answer-card,
.pattern-card,
.warning-card,
.community-card,
.tool-shell,
.app-link-card,
.upgrade{
background:linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.04) 100%);
border:1px solid rgba(255,255,255,.10);
border-radius:24px;
box-shadow:var(--shadow-md);
}

.answer-card{
padding:18px;
background:
linear-gradient(135deg, rgba(34,211,238,.12) 0%, rgba(139,92,246,.12) 100%),
linear-gradient(180deg, rgba(255,255,255,.08) 0%, rgba(255,255,255,.05) 100%);
}

.answer-kicker{
font-size:12px;
font-weight:900;
letter-spacing:.08em;
text-transform:uppercase;
color:#8be9ff;
margin-bottom:8px;
}

.answer-card h2{
margin:0;
font-size:28px;
line-height:1.08;
letter-spacing:-.03em;
color:#fff;
}

.answer-card p{
margin:10px 0 0;
font-size:15px;
font-weight:800;
color:#d8e5f8;
line-height:1.7;
}

.precheck-layout{
display:grid;
gap:16px;
margin-top:16px;
margin-bottom:18px;
}

.pattern-card,
.warning-card,
.community-card{
padding:18px;
}

.card-heading{
margin:0 0 10px;
font-size:21px;
line-height:1.14;
letter-spacing:-.02em;
font-weight:900;
color:#fff;
}

.card-copy{
margin:0 0 12px;
font-size:14px;
font-weight:800;
color:#b9c9e3;
line-height:1.68;
}

.steps-grid,
.warning-grid,
.community-grid{
display:grid;
gap:10px;
}

.step-item,
.warning-item,
.community-item{
display:flex;
align-items:flex-start;
gap:12px;
padding:14px 15px;
border-radius:18px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
}

.step-number{
width:28px;
height:28px;
border-radius:999px;
display:flex;
align-items:center;
justify-content:center;
flex:0 0 28px;
font-size:13px;
font-weight:900;
background:linear-gradient(180deg,var(--cyan) 0%,var(--violet) 100%);
color:#fff;
box-shadow:0 8px 18px rgba(34,211,238,.18);
}

.warning-icon,
.community-icon{
width:24px;
height:24px;
border-radius:999px;
display:flex;
align-items:center;
justify-content:center;
flex:0 0 24px;
font-size:14px;
}

.warning-icon{
background:rgba(239,68,68,.16);
color:#fecaca;
}

.community-icon{
background:rgba(16,185,129,.16);
color:#a7f3d0;
}

.step-text strong,
.warning-text strong,
.community-text strong{
display:block;
font-size:14px;
line-height:1.35;
color:#fff;
margin-bottom:2px;
}

.step-text span,
.warning-text span,
.community-text span{
display:block;
font-size:13px;
line-height:1.58;
font-weight:800;
color:#bfd0ea;
}

.example-band{
margin-top:12px;
padding:14px 15px;
border-radius:18px;
background:linear-gradient(180deg, rgba(139,92,246,.16) 0%, rgba(34,211,238,.10) 100%);
border:1px solid rgba(139,92,246,.24);
font-size:14px;
font-weight:800;
line-height:1.65;
color:#efe9ff;
}

.example-band strong{
display:block;
margin-bottom:4px;
font-size:13px;
letter-spacing:.04em;
text-transform:uppercase;
color:#c4b5fd;
}

.tool-shell{
padding:22px;
margin-top:18px;
background:
linear-gradient(135deg, rgba(34,211,238,.10) 0%, rgba(139,92,246,.10) 100%),
linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.04) 100%);
}

.tool-top{
text-align:center;
margin-bottom:16px;
}

.tool-top h2{
margin:0;
font-size:30px;
line-height:1.10;
letter-spacing:-.04em;
color:#fff;
}

.tool-top p{
margin:8px auto 0;
max-width:620px;
font-size:15px;
color:#c8d6ec;
font-weight:700;
line-height:1.7;
}

textarea,input{
width:100%;
padding:16px 16px;
margin-top:12px;
border-radius:18px;
border:1.5px solid rgba(255,255,255,.12);
font-size:16px;
background:rgba(7,16,29,.72);
color:#eef6ff;
box-shadow:none;
}

textarea{
height:156px;
resize:none;
}

textarea::placeholder,
input::placeholder{
color:#89a0c4;
}

textarea:focus,
input:focus{
outline:none;
border-color:rgba(34,211,238,.60);
box-shadow:0 0 0 5px rgba(34,211,238,.10);
}

button{
border:none;
border-radius:18px;
cursor:pointer;
font-size:16px;
padding:16px;
min-height:50px;
}

.check{
width:100%;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
margin-top:18px;
font-weight:900;
font-size:18px;
letter-spacing:.2px;
box-shadow:0 18px 40px rgba(34,211,238,.20);
transition:transform .15s ease, box-shadow .15s ease;
}

.check:hover{
transform:translateY(-1px);
box-shadow:0 22px 44px rgba(34,211,238,.24);
}

.check:active{
transform:scale(.985);
}

.note,
.input-help{
margin-top:12px;
font-size:14px;
color:#9fb0cc;
text-align:center;
text-wrap:balance;
}

.success{
margin-top:12px;
font-size:14px;
color:#86efac;
text-align:center;
font-weight:900;
display:none;
}

.tool-assurance{
margin-top:14px;
padding:14px 15px;
border-radius:18px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
font-size:14px;
font-weight:800;
color:#cbdaf0;
line-height:1.6;
text-align:center;
}

.app-link-card{
margin-top:18px;
padding:20px;
text-align:center;
background:
linear-gradient(135deg, rgba(16,185,129,.12) 0%, rgba(34,211,238,.10) 100%),
linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.04) 100%);
}

.app-link-card h4{
margin:0 0 6px;
font-size:20px;
color:#fff;
font-weight:900;
letter-spacing:-.02em;
}

.app-link-card p{
margin:0 0 12px;
font-size:14px;
color:#c9d8ee;
line-height:1.65;
}

.app-link-button{
display:block;
width:100%;
text-align:center;
background:linear-gradient(135deg,var(--emerald) 0%,var(--cyan-2) 100%);
color:#fff;
font-weight:900;
padding:15px;
border-radius:16px;
box-sizing:border-box;
box-shadow:0 14px 30px rgba(16,185,129,.18);
text-decoration:none;
}

#result{
margin-top:26px;
display:none;
}

.result-card{
background:rgba(255,255,255,.96);
border-radius:26px;
padding:22px;
box-shadow:var(--shadow-lg);
border:1px solid rgba(15,23,42,.08);
overflow:hidden;
color:var(--ink-dark);
}

.result-card.high{
border:2px solid #fecaca;
box-shadow:0 22px 50px rgba(239,68,68,.12);
}

.result-card.medium{
border:2px solid #fde68a;
box-shadow:0 22px 50px rgba(245,158,11,.10);
}

.result-card.low{
border:2px solid #bbf7d0;
box-shadow:0 22px 50px rgba(16,185,129,.10);
}

.result-card.unknown{
border:1px solid #dbe4f0;
}

.result-top{
display:flex;
align-items:flex-start;
justify-content:space-between;
gap:12px;
flex-wrap:wrap;
}

.risk{
font-size:21px;
font-weight:900;
margin-bottom:0;
padding:11px 16px;
border-radius:999px;
display:inline-flex;
align-items:center;
gap:10px;
letter-spacing:.01em;
box-shadow:var(--shadow-sm);
}

.risk.high{
background:var(--red);
color:#fff;
}
.risk.medium{
background:var(--amber);
color:#fff;
}
.risk.low{
background:var(--emerald);
color:#fff;
}
.risk.unknown{
background:#e5e7eb;
color:#374151;
}

.result-chip{
padding:9px 13px;
border-radius:999px;
font-size:12px;
font-weight:900;
background:#fff;
border:1px solid #d9e2ec;
color:#334155;
box-shadow:var(--shadow-sm);
}

.result-summary{
margin:16px 0 0;
font-size:16px;
color:#334155;
font-weight:800;
line-height:1.58;
}

.result-continuation{
margin-top:14px;
padding:14px 15px;
border-radius:16px;
font-size:14px;
font-weight:900;
line-height:1.55;
background:#f8fafc;
border:1px solid #e2e8f0;
color:#334155;
}

.result-card.high .result-continuation{
background:#fff8f8;
border-color:#f3c5cf;
color:#7f1d1d;
}

.result-card.medium .result-continuation{
background:#fffdf5;
border-color:#fde68a;
color:#92400e;
}

.result-card.unknown .result-continuation{
background:#f8fafc;
border-color:#e2e8f0;
color:#334155;
}

.section{
margin-top:18px;
padding:18px;
border-radius:20px;
background:#f8fafc;
border:1px solid #e7eef6;
}

.section-title{
font-weight:900;
margin-bottom:10px;
color:#0f172a;
font-size:16px;
letter-spacing:-.01em;
}

.signal-list{
list-style:none;
padding:0;
margin:0;
display:grid;
gap:10px;
}

.signal-item{
display:flex;
align-items:flex-start;
gap:12px;
padding:14px 15px;
border-radius:16px;
background:#fff;
border:1px solid #e2e8f0;
font-size:14px;
font-weight:800;
color:#334155;
line-height:1.45;
}

.result-card.high .signal-item{
background:#fffafa;
border-color:#f5c2cc;
color:#7f1d1d;
}

.result-card.medium .signal-item{
background:#fffdf5;
border-color:#fde68a;
color:#92400e;
}

.result-card.low .signal-item{
background:#f7fff8;
border-color:#bbf7d0;
color:#166534;
}

.signal-icon{
width:22px;
height:22px;
display:flex;
align-items:center;
justify-content:center;
font-size:16px;
line-height:1;
flex:0 0 22px;
}

.action-box{
padding:15px 16px;
border-radius:16px;
background:#eef6ff;
border:1px solid #bfdbfe;
font-size:14px;
font-weight:900;
color:#1e3a8a;
line-height:1.55;
}

.result-payline{
margin-top:18px;
padding:16px;
background:#f8fafc;
border:1px solid #e2e8f0;
border-radius:18px;
font-size:14px;
color:#334155;
font-weight:900;
line-height:1.55;
}

.result-card.high .result-payline{
background:#fff8f8;
border-color:#f3c5cf;
color:#7f1d1d;
}

.result-card.medium .result-payline{
background:#fffdf5;
border-color:#fde68a;
color:#92400e;
}

.result-card.low .result-payline{
background:#f7fff8;
border-color:#bbf7d0;
color:#166534;
}

.result-actions{
margin-top:16px;
display:grid;
gap:12px;
}

.result-cta{
margin-top:0;
}

.share-wrap{
margin-top:4px;
padding:18px;
border-radius:20px;
background:linear-gradient(180deg,#fff 0%,#f8fafc 100%);
border:1px solid #e2e8f0;
text-align:center;
box-shadow:var(--shadow-sm);
}

.share-alert{
font-size:13px;
font-weight:900;
color:#0f172a;
margin-bottom:6px;
letter-spacing:.01em;
}

.share-copy{
font-size:14px;
font-weight:800;
color:#475569;
line-height:1.55;
margin-bottom:14px;
max-width:560px;
margin-left:auto;
margin-right:auto;
}

.share-grid{
display:grid;
grid-template-columns:repeat(2,minmax(0,1fr));
gap:10px;
}

.share-btn{
display:inline-flex;
align-items:center;
justify-content:center;
gap:8px;
min-height:46px;
padding:12px 14px;
border-radius:14px;
font-size:14px;
font-weight:900;
transition:transform .15s ease, box-shadow .15s ease;
}

.share-btn:hover{
transform:translateY(-1px);
}

.share-btn.primary{
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
box-shadow:0 12px 24px rgba(34,211,238,.18);
}

.share-btn.dark{
background:linear-gradient(135deg,#111827 0%,#1f2937 100%);
color:#fff;
box-shadow:0 12px 24px rgba(15,23,42,.14);
}

.share-btn.light{
background:#eef2ff;
color:#1e293b;
border:1px solid #dbe3f8;
}

.share-status{
margin-top:12px;
min-height:20px;
font-size:13px;
font-weight:900;
color:#059669;
}

.upgrade{
display:none;
margin-top:28px;
padding:24px;
text-align:center;
background:
linear-gradient(135deg, rgba(139,92,246,.18) 0%, rgba(34,211,238,.16) 100%),
linear-gradient(180deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,.04) 100%);
}

.upgrade h3{
margin:0 0 8px;
font-size:30px;
line-height:1.15;
color:#fff;
text-wrap:balance;
}

.upgrade-copy{
margin:0 auto;
max-width:600px;
color:#d5e2f4;
font-size:15px;
line-height:1.68;
}

.plan{
width:100%;
margin-top:14px;
background:linear-gradient(135deg,var(--violet) 0%,var(--cyan-2) 100%);
color:#fff;
font-weight:900;
padding:15px;
box-shadow:0 14px 28px rgba(34,211,238,.18);
}

.plan.secondary{
background:linear-gradient(135deg,#2563eb 0%,#06b6d4 100%);
}

.plan.tertiary{
background:linear-gradient(135deg,#0f766e 0%,#10b981 100%);
}

.subscriber-link{
margin-top:14px;
text-align:center;
}

.subscriber-link button{
background:none;
border:none;
padding:0;
min-height:auto;
font-size:14px;
color:#bff7ff;
font-weight:800;
text-decoration:underline;
cursor:pointer;
}

.content-section{
margin-top:34px;
padding-bottom:36px;
}

.content-bridge{
margin:0 0 24px;
padding:18px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.09);
font-size:15px;
color:#d6e3f7;
font-weight:800;
line-height:1.66;
}

.content-header-band{
display:grid;
gap:14px;
margin:0 0 24px;
}

.content-pulse{
display:grid;
grid-template-columns:repeat(3,minmax(0,1fr));
gap:12px;
}

.pulse-card{
padding:14px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
}

.pulse-label{
font-size:12px;
font-weight:900;
letter-spacing:.08em;
text-transform:uppercase;
color:#8be9ff;
margin-bottom:6px;
}

.pulse-card p{
margin:0;
font-size:14px;
font-weight:800;
line-height:1.6;
color:#d6e3f7;
}

.content-section h2,
.content-section h3{
margin:0 0 14px;
color:#fff;
line-height:1.08;
letter-spacing:-.035em;
font-weight:900;
text-wrap:balance;
}

.content-section h2{
font-size:40px;
}

.content-section h3{
font-size:28px;
margin-top:30px;
}

.content-body{
font-size:18px;
color:#d7e4f8;
}

.content-body p{
margin:0 0 20px;
}

.content-body ul{
margin:0 0 20px;
padding-left:22px;
}

.content-body li{
margin-bottom:10px;
}

.link-section{
margin-top:28px;
padding-top:24px;
border-top:1px solid rgba(255,255,255,.08);
}

.related-links{
margin:0;
padding-left:22px;
}

.related-links li{
margin-bottom:10px;
}

.related-links a{
color:#8be9ff;
font-weight:800;
}

.share-loop-panel{
margin-top:28px;
padding:20px;
border-radius:24px;
background:
linear-gradient(135deg, rgba(16,185,129,.12) 0%, rgba(34,211,238,.12) 100%),
linear-gradient(180deg, rgba(255,255,255,.06) 0%, rgba(255,255,255,.04) 100%);
border:1px solid rgba(255,255,255,.10);
box-shadow:var(--shadow-md);
}

.share-loop-panel h3{
margin-top:0;
}

.share-loop-copy{
font-size:15px;
font-weight:800;
color:#d7e4f8;
line-height:1.68;
margin-bottom:14px;
}

.share-loop-grid{
display:grid;
grid-template-columns:repeat(3,minmax(0,1fr));
gap:10px;
}

.loop-box{
padding:14px;
border-radius:18px;
background:rgba(255,255,255,.06);
border:1px solid rgba(255,255,255,.08);
}

.loop-box strong{
display:block;
font-size:13px;
margin-bottom:4px;
color:#fff;
}

.loop-box span{
display:block;
font-size:13px;
font-weight:800;
line-height:1.56;
color:#c8d7ed;
}

.content-close{
margin-top:28px;
padding:18px;
border-radius:20px;
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
font-size:15px;
font-weight:800;
color:#d7e4f8;
line-height:1.72;
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
.container,.content-section{margin-left:12px;margin-right:12px;padding:18px;border-radius:24px;}
.top-bar{padding:10px 10px;}
.top-actions{gap:8px;margin-right:0;}
.logo{font-size:13px;margin-left:2px;padding:9px 12px;}
.app-top{font-size:13px;padding:8px 10px;}
.upgrade-top{font-size:13px;padding:8px 10px;margin-right:0;}
.upgrade h3{font-size:24px;}
.content-section h2{font-size:30px;line-height:1.12;}
.content-section h3{font-size:24px;}
.content-body{font-size:16px;}
.answer-card h2{font-size:22px;}
.card-heading{font-size:18px;}
.tool-top h2{font-size:24px;}
.share-grid,.content-pulse,.share-loop-grid{grid-template-columns:1fr;}
.share-btn{width:100%;}
}
</style>
</head>
<body>

<div class="top-bar">
  <a class="logo" href="https://verixiaapps.com/check/">
    <span class="logo-dot"></span>
    <span>Scam Check Now</span>
  </a>
  <div class="top-actions">
    <a class="app-top" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">📱 Get App</a>
    <button class="upgrade-top" onclick="showUpgrade()">Upgrade</button>
  </div>
</div>

<div class="page-shell">

  <div class="hero">
    <div class="hero-badge-row">
      <div class="hero-badge">Live scam checking</div>
      <div class="hero-badge">Shareable warning page</div>
      <div class="hero-badge">Built for repeat use</div>
    </div>

    <h1 id="heroKeyword"></h1>
    <p id="heroSubheading"></p>

    <div class="hero-trust">
      <div class="hero-trust-chip">Check before you click</div>
      <div class="hero-trust-chip">Check before you reply</div>
      <div class="hero-trust-chip">Check before you send money</div>
    </div>
  </div>

  <div class="container">
    <div class="answer-card" id="answerCard">
      <div class="answer-kicker">Quick answer</div>
      <h2 id="answerHeading">Should you trust this message?</h2>
      <p id="answerSummary">Use the checker below before you click, reply, send money, or share personal information. Messages like this often use urgency, fake authority, and misleading links to push fast decisions.</p>
    </div>

    <div class="precheck-layout" id="precheckLayout">
      <div class="pattern-card" id="patternCard">
        <h3 class="card-heading" id="patternHeading">How this scam pattern usually works</h3>
        <p class="card-copy" id="patternCopy">These messages often try to create pressure first, then push you toward a payment, login, code, or urgent reply.</p>
        <div class="steps-grid" id="patternSteps"></div>
        <div class="example-band" id="exampleBand"></div>
      </div>

      <div class="warning-card" id="warningCard">
        <h3 class="card-heading" id="warningHeading">Red flags to look for before you act</h3>
        <p class="card-copy" id="warningCopy">Even when the message looks polished, a few small warning signs are often enough to stop a costly mistake.</p>
        <div class="warning-grid" id="warningGrid"></div>
      </div>

      <div class="community-card" id="communityCard">
        <h3 class="card-heading">Why people share pages like this</h3>
        <p class="card-copy">This version is built to help people warn friends, compare patterns, and come back quickly the next time something suspicious shows up.</p>
        <div class="community-grid">
          <div class="community-item">
            <div class="community-icon">↗</div>
            <div class="community-text">
              <strong>Easy to share</strong>
              <span>Send the page itself when someone gets a similar message.</span>
            </div>
          </div>
          <div class="community-item">
            <div class="community-icon">⟲</div>
            <div class="community-text">
              <strong>Easy to revisit</strong>
              <span>Use the checker again when the next suspicious message arrives.</span>
            </div>
          </div>
          <div class="community-item">
            <div class="community-icon">◎</div>
            <div class="community-text">
              <strong>Easy to scan</strong>
              <span>See warning patterns fast without digging through clutter.</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="tool-shell">
      <div class="tool-top">
        <h2 id="toolHeading">Check the suspicious message now</h2>
        <p id="toolCopy">Paste the message, email, website, job offer, or link below to review scam risk, warning signs, and what to do next.</p>
      </div>

      <textarea id="text" placeholder="Paste the message, email, website, link, or job offer you're unsure about..."></textarea>

      <div class="input-help">Examples: delivery text, PayPal alert, crypto message, job offer, account warning</div>

      <button class="check" onclick="check()">🔍 Check Scam Risk</button>

      <div class="note">No signup required • 1 free check • Results in seconds</div>

      <input id="email" placeholder="Already subscribed? Enter your payment email to unlock unlimited checks">

      <div class="note">Use the same email you entered during checkout</div>

      <div id="postPurchase" class="success">
        ✅ Payment successful — unlimited access is active on this browser
      </div>

      <div class="tool-assurance">Get a clear risk level, key warning signs, and what to do next before you click, reply, send money, or share information.</div>

      <div id="result"></div>
    </div>

    <div class="app-link-card">
      <h4>Keep it on your phone for the next one</h4>
      <p>Suspicious messages rarely happen once. Keep the checker close so the next text, DM, email, or link is easier to review in seconds.</p>
      <a class="app-link-button" href="https://apps.apple.com/app/id6759490910" target="_blank" rel="noopener noreferrer">Download the App</a>
    </div>

    <div class="upgrade" id="upgrade">
      <h3>Stay Ready for the Next Suspicious Message</h3>

      <div class="upgrade-copy">
        Most scam attempts do not happen once. If you are seeing suspicious messages, links, or requests, more may follow. Keep checking them before they turn into a costly mistake.
      </div>

      <div style="margin-top:10px;font-size:13px;color:#d4e2f5;">
        Built for ongoing protection against scams, phishing, impersonation, and risky payment requests
      </div>

      <div style="margin-top:8px;margin-bottom:10px;font-size:14px;color:#d4e2f5;">
        Unlimited scam checks • Cancel anytime
      </div>

      <button class="plan" onclick="checkout('price_1T8KOTJjMzyHDzeQDDg1A2TF')">Weekly Protection</button>
      <button class="plan secondary" onclick="checkout('price_1T8KOUJjMzyHDzeQxaqPFOSB')">Monthly Protection</button>
      <button class="plan tertiary" onclick="checkout('price_1T8KOQJjMzyHDzeQfcU1C1MQ')">Yearly Protection</button>

      <div style="margin-top:14px;font-size:13px;color:#d4e2f5;">
        Secure payments powered by Stripe
      </div>

      <div class="subscriber-link">
        <button type="button" onclick="scrollToEmail()">Already subscribed? Enter your email</button>
      </div>
    </div>
  </div>

  <section class="content-section">
    <div id="contentBridge" class="content-bridge"></div>

    <div class="content-header-band">
      <div class="content-pulse">
        <div class="pulse-card">
          <div class="pulse-label">Share signal</div>
          <p>Pages like this work best when passed along before someone clicks or replies.</p>
        </div>
        <div class="pulse-card">
          <div class="pulse-label">Return signal</div>
          <p>People often come back when the next suspicious message appears.</p>
        </div>
        <div class="pulse-card">
          <div class="pulse-label">Search signal</div>
          <p>Clear topic pages and strong internal links make this easier to discover.</p>
        </div>
      </div>
    </div>

    <h2 id="contentHeading"></h2>
    <div id="seoContent" class="content-body">{{AI_CONTENT}}</div>

    <div class="link-section" id="relatedLinksWrap">
      <h3 id="relatedHeading">Check Similar Messages</h3>
      <ul id="relatedLinks" class="related-links">{{RELATED_LINKS}}</ul>
    </div>

    <div class="link-section" id="moreLinksWrap">
      <h3 id="moreLinksHeading">More Scam Checks</h3>
      <ul id="moreLinks" class="related-links">{{MORE_LINKS}}</ul>
    </div>

    <div class="share-loop-panel">
      <h3>How this page keeps helping after one visit</h3>
      <div class="share-loop-copy">
        A good warning page should not only answer one question. It should help someone share it, return to it later, and use it again when the next suspicious message shows up.
      </div>
      <div class="share-loop-grid">
        <div class="loop-box">
          <strong>1. Find it</strong>
          <span>Search lands people on a focused page for the exact suspicious topic.</span>
        </div>
        <div class="loop-box">
          <strong>2. Share it</strong>
          <span>They send the page or warning to someone else who may get the same message.</span>
        </div>
        <div class="loop-box">
          <strong>3. Reuse it</strong>
          <span>They come back when a new message, email, text, or link needs checking.</span>
        </div>
      </div>
    </div>

    <div class="content-close">
      Messages like this are one of the most common ways people lose money, share codes, or hand over access without realizing it. When something feels off, pause and verify it through official sources before taking action.
    </div>
  </section>

  <footer class="footer">
    <div>
      By using this website you agree to our
      <a href="https://verixiaapps.com/website-policies/scam-check/" target="_blank" rel="noopener noreferrer">Terms and Privacy Policy</a>.
    </div>
    <div style="margin-top:10px">
      Scam Check Now © 2026 • Scam detection and risk analysis tool
    </div>
  </footer>

</div>

<script>
const API = "https://awake-integrity-production-faa0.up.railway.app";
const RAW_KEYWORD = "{{KEYWORD}}";
const BROWSER_SUB_KEY = "scam_check_browser_subscribed";

window.addEventListener("load", function () {
  const params = new URLSearchParams(window.location.search);

  if (params.get("subscribed") === "true") {
    localStorage.setItem(BROWSER_SUB_KEY, "true");
    document.getElementById("postPurchase").style.display = "block";
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  if (isBrowserSubscribed()) {
    document.getElementById("postPurchase").style.display = "block";
  }

  setKeywordHeadings();
  applyPreviewContent();
  applyIntentToChecker();
  cleanSeoContent();
  cleanRelatedLinks();
  cleanMoreLinks();
  normalizeBottomLinks();
});

function isBrowserSubscribed() {
  return localStorage.getItem(BROWSER_SUB_KEY) === "true";
}

function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;")
    .replace(/'/g,"&#39;");
}

function normalizeKeyword(str) {
  return String(str || "")
    .replace(/\s+/g, " ")
    .replace(/[–—]/g, "-")
    .trim();
}

function stripLeadingQuestionPrefixes(text) {
  return String(text || "")
    .replace(/^\s*is\s+/i, "")
    .replace(/^\s*can\s+i\s+trust\s+/i, "")
    .replace(/^\s*did\s+i\s+get\s+scammed\s+(?:by|on|with)\s+/i, "")
    .trim();
}

function stripTrailingQuestionSuffixes(text) {
  return String(text || "")
    .replace(/\s+a\s+scam$/i, "")
    .replace(/\s+or\s+legit$/i, "")
    .replace(/\s+or\s+scam$/i, "")
    .replace(/\s+legit$/i, "")
    .replace(/\s+real$/i, "")
    .replace(/\s+safe$/i, "")
    .replace(/\s+scam$/i, "")
    .replace(/\s+a$/i, "")
    .trim();
}

function cleanKeywordBase(keyword) {
  let text = normalizeKeyword(keyword);
  text = stripLeadingQuestionPrefixes(text);
  text = stripTrailingQuestionSuffixes(text);
  return text.replace(/\s+/g, " ").trim();
}

function cleanKeywordForSentence(keyword) {
  return cleanKeywordBase(keyword)
    .replace(/\bmessage\b/gi, "")
    .replace(/\bmessages\b/gi, "")
    .replace(/\bemail\b/gi, "")
    .replace(/\bemails\b/gi, "")
    .replace(/\btext\b/gi, "")
    .replace(/\btexts\b/gi, "")
    .replace(/\blink\b/gi, "")
    .replace(/\blinks\b/gi, "")
    .replace(/\bwebsite\b/gi, "")
    .replace(/\bwebsites\b/gi, "")
    .replace(/\balert\b/gi, "")
    .replace(/\balerts\b/gi, "")
    .replace(/\bwarning\b/gi, "")
    .replace(/\bwarnings\b/gi, "")
    .replace(/\bnotification\b/gi, "")
    .replace(/\bnotifications\b/gi, "")
    .replace(/\brequest\b/gi, "")
    .replace(/\brequests\b/gi, "")
    .replace(/\boffer\b/gi, "")
    .replace(/\boffers\b/gi, "")
    .replace(/\bscam\b/gi, "")
    .replace(/\bscams\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

function displayKeyword(str) {
  const text = normalizeKeyword(str);
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function displayCleanKeyword(str) {
  return displayKeyword(cleanKeywordBase(str));
}

function containsAny(text, phrases) {
  return phrases.some(phrase => text.includes(phrase));
}

function isGuidanceStyleKeyword(lower) {
  return (
    lower.startsWith("how to ") ||
    lower.startsWith("what to do after ") ||
    lower.startsWith("how to recover after ") ||
    lower.startsWith("how to secure ") ||
    lower.startsWith("how to block ") ||
    lower.startsWith("how to avoid ") ||
    lower.startsWith("what happens after ") ||
    lower.startsWith("what is ") ||
    lower.startsWith("why ") ||
    lower.startsWith("when ") ||
    lower.startsWith("where ") ||
    lower.startsWith("who ")
  );
}

function isQuestionStyleKeyword(lower) {
  return (
    lower.startsWith("is ") ||
    lower.startsWith("can ") ||
    lower.startsWith("should ") ||
    lower.startsWith("could ") ||
    lower.startsWith("would ") ||
    lower.startsWith("do ") ||
    lower.startsWith("does ") ||
    lower.startsWith("did ")
  );
}

function chooseBridgeIntro(baseKeyword) {
  const readable = displayKeyword(baseKeyword);
  const variants = [
    `If this ${readable} just showed up,`,
    `If you're unsure about this ${readable},`,
    `If you're looking at this ${readable} right now,`
  ];
  const index = baseKeyword.length % variants.length;
  return variants[index];
}

function getVariantNumber(keyword) {
  const text = normalizeKeyword(keyword || "default");
  let sum = 0;
  for (let i = 0; i < text.length; i++) sum += text.charCodeAt(i);
  return (sum % 3) + 1;
}

function buildHeroTitle(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const cleanTitle = displayCleanKeyword(keywordRaw);
  const readableTitle = displayKeyword(raw);

  if (!raw) return "Check suspicious messages before you click or reply";

  if (isGuidanceStyleKeyword(lower)) return `${readableTitle}: Safety Tips, Warning Signs & What To Do`;
  if (lower.startsWith("did i get scammed")) return `${readableTitle}? Signs, Risks & What To Do Next`;
  if (lower.startsWith("can scammers") || lower.startsWith("can someone")) return `${readableTitle}? Risks, Warning Signs & What To Do`;
  if (lower.startsWith("almost ")) return `${readableTitle}? Warning Signs & Safety Steps`;
  if (lower.startsWith("is this ")) return `${readableTitle}? Check Warning Signs & What To Do`;

  if (lower.startsWith("is ") && lower.includes(" legit")) {
    const withoutLegit = raw.replace(/\s+legit\b/i, "").trim();
    return `${displayKeyword(withoutLegit)} Legit or a Scam? Warning Signs & What To Do`;
  }

  if (isQuestionStyleKeyword(lower)) return `${readableTitle}? Risks, Warning Signs & What To Know`;

  return `Is ${cleanTitle} a Scam? Check Before You Click or Send Money`;
}

function buildHeroSubheading(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const readableKeyword = displayKeyword(cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw);

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker below to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information.";
  }

  return `Messages related to ${readableKeyword} can be used to steal money, codes, or account access. Paste it below before you click, reply, send money, or take action.`;
}

function buildContentHeading(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const readableTitle = displayKeyword(raw);
  const cleanTitle = displayCleanKeyword(keywordRaw);

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower) || lower.startsWith("almost ")) {
    return readableTitle;
  }

  return `What ${cleanTitle} Messages, Links, and Offers Often Look Like`;
}

function buildContentBridge(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const cleanSentenceKeyword = cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw;

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker above to review suspicious messages, emails, links, and offers before you click, reply, send money, or share information.";
  }

  if (lower.startsWith("almost ")) {
    return "If you are unsure what happened, use the checker above to review suspicious messages, emails, links, and offers before taking action.";
  }

  return `${chooseBridgeIntro(cleanSentenceKeyword)} use the checker above before you click links, reply, send money, or share information. Pages like this work best when they help you act early, share quickly, and come back when the next suspicious message shows up.`;
}

function buildAnswerHeading(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const cleanTitle = displayCleanKeyword(keywordRaw);

  if (!raw) return "Should you trust this message?";
  if (isGuidanceStyleKeyword(lower)) return `${displayKeyword(raw)}`;
  if (isQuestionStyleKeyword(lower)) return `${displayKeyword(raw)}`;
  return `${cleanTitle}: quick scam check`;
}

function buildAnswerSummary(keywordRaw) {
  const raw = normalizeKeyword(keywordRaw);
  const lower = raw.toLowerCase();
  const readable = displayKeyword(cleanKeywordForSentence(raw) || cleanKeywordBase(raw) || raw);

  if (isGuidanceStyleKeyword(lower) || isQuestionStyleKeyword(lower)) {
    return "Use the checker below before you click, reply, send money, or share personal information. Scam messages often rely on urgency, fake authority, and misleading links to push fast decisions.";
  }

  return `${readable} messages can be used to push fake urgency, steal account access, or trigger payments before you have time to verify what is real. Use the checker below before taking action.`;
}

function setKeywordHeadings() {
  const keywordRaw = (RAW_KEYWORD || "this message").trim();

  document.getElementById("heroKeyword").textContent = buildHeroTitle(keywordRaw);
  document.getElementById("heroSubheading").textContent = buildHeroSubheading(keywordRaw);
  document.getElementById("contentHeading").textContent = buildContentHeading(keywordRaw);
  document.getElementById("contentBridge").textContent = buildContentBridge(keywordRaw);
  document.getElementById("answerHeading").textContent = buildAnswerHeading(keywordRaw);
  document.getElementById("answerSummary").textContent = buildAnswerSummary(keywordRaw);
}

function setStepItems(items) {
  const wrap = document.getElementById("patternSteps");
  wrap.innerHTML = items.map((item, index) => `
    <div class="step-item">
      <div class="step-number">${index + 1}</div>
      <div class="step-text">
        <strong>${escapeHtml(item.title)}</strong>
        <span>${escapeHtml(item.text)}</span>
      </div>
    </div>
  `).join("");
}

function setWarningItems(items) {
  const wrap = document.getElementById("warningGrid");
  wrap.innerHTML = items.map(item => `
    <div class="warning-item">
      <div class="warning-icon">⚠️</div>
      <div class="warning-text">
        <strong>${escapeHtml(item.title)}</strong>
        <span>${escapeHtml(item.text)}</span>
      </div>
    </div>
  `).join("");
}

function buildVariantLayout(variant, options) {
  const precheckLayout = document.getElementById("precheckLayout");
  const patternCard = document.getElementById("patternCard");
  const warningCard = document.getElementById("warningCard");
  const communityCard = document.getElementById("communityCard");

  precheckLayout.innerHTML = "";

  if (variant === 1) {
    precheckLayout.appendChild(patternCard);
    precheckLayout.appendChild(warningCard);
    precheckLayout.appendChild(communityCard);
  } else if (variant === 2) {
    precheckLayout.appendChild(warningCard);
    precheckLayout.appendChild(patternCard);
    precheckLayout.appendChild(communityCard);
  } else {
    precheckLayout.appendChild(patternCard);
    precheckLayout.appendChild(communityCard);
    precheckLayout.appendChild(warningCard);
  }

  document.getElementById("patternHeading").textContent = options.patternHeading;
  document.getElementById("patternCopy").textContent = options.patternCopy;
  document.getElementById("warningHeading").textContent = options.warningHeading;
  document.getElementById("warningCopy").textContent = options.warningCopy;
  document.getElementById("exampleBand").innerHTML = `<strong>${escapeHtml(options.exampleLabel)}</strong>${escapeHtml(options.exampleText)}`;

  setStepItems(options.steps);
  setWarningItems(options.warnings);
}

function applyPreviewContent() {
  const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
  const lower = keywordRaw.toLowerCase();
  const variant = getVariantNumber(keywordRaw);

  let options = {
    patternHeading: "How this scam pattern usually works",
    patternCopy: "These messages often try to create pressure first, then push you toward a payment, login, code, or urgent reply.",
    warningHeading: "Red flags to look for before you act",
    warningCopy: "Even when the message looks polished, a few small warning signs are often enough to stop a costly mistake.",
    exampleLabel: "Common example",
    exampleText: "Urgent message asking you to verify an account, send money, click a link, or share a one-time code.",
    steps: [
      { title: "Create urgency", text: "The message tries to make delay feel risky or expensive." },
      { title: "Push one action", text: "It points you toward a link, payment, code, reply, or login." },
      { title: "Reduce verification", text: "It tries to keep you inside the message instead of checking through official sources." }
    ],
    warnings: [
      { title: "Urgency or pressure", text: "Warnings, deadlines, threats, or limited-time demands." },
      { title: "Requests for money or codes", text: "Gift cards, transfers, payment apps, or one-time passcodes." },
      { title: "Suspicious links or sender details", text: "A message that looks official but points somewhere slightly wrong." }
    ]
  };

  if (containsAny(lower, ["job", "recruiter", "interview", "hiring", "onboarding"])) {
    options = {
      patternHeading: "How fake job messages usually work",
      patternCopy: "Scammers often use fast praise, remote-work appeal, and urgent next steps to move people quickly toward fees, personal details, or fake onboarding.",
      warningHeading: "Job offer warning signs to notice first",
      warningCopy: "A message can sound professional and still be dangerous when the details move too fast or ask for the wrong things too early.",
      exampleLabel: "Common example",
      exampleText: "A recruiter says you are hired quickly, then asks for identity details, a payment, or a chat on a non-official app.",
      steps: [
        { title: "Create excitement fast", text: "The message suggests quick approval, easy money, or immediate hiring." },
        { title: "Move off-platform", text: "You are pushed to text, Telegram, WhatsApp, or another channel quickly." },
        { title: "Ask for sensitive info or money", text: "The scam often shifts toward fees, identity details, or payment setup." }
      ],
      warnings: [
        { title: "Too fast or too easy", text: "No real screening, instant offer, or unusually high pay for little detail." },
        { title: "Payment or equipment requests", text: "You are asked to buy something, send money, or use a personal account." },
        { title: "Unverified recruiter identity", text: "The sender domain, company site, or role details do not fully match." }
      ]
    };
  } else if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft"])) {
    options = {
      patternHeading: "How crypto scams usually work",
      patternCopy: "Crypto scams often combine urgency, technical-looking language, and promises of recovery, support, or rewards to trigger fast transfers or wallet approvals.",
      warningHeading: "Crypto red flags to catch early",
      warningCopy: "When a message wants speed, trust, and wallet access at the same time, that is usually the danger zone.",
      exampleLabel: "Common example",
      exampleText: "A message claims your wallet is at risk, an airdrop is waiting, or funds can be recovered if you act now.",
      steps: [
        { title: "Create fear or greed", text: "The message warns of loss or promises a fast gain or recovery." },
        { title: "Push wallet action", text: "You are asked to connect, approve, sign, or transfer." },
        { title: "Use urgency to bypass caution", text: "It tries to stop you from checking the project, wallet, or support source." }
      ],
      warnings: [
        { title: "Wallet connect pressure", text: "The message wants you to approve something immediately." },
        { title: "Recovery or support claims", text: "Scammers often impersonate exchange staff, support, or recovery services." },
        { title: "Guaranteed returns or rewards", text: "Airdrops, presales, and recovery promises are common hooks." }
      ]
    };
  }

  document.getElementById("toolHeading").textContent = "Check the suspicious message now";
  document.getElementById("toolCopy").textContent = "Paste the message, email, website, job offer, or link below to review scam risk, warning signs, and what to do next.";

  buildVariantLayout(variant, options);
}

function applyIntentToChecker() {
  const keywordRaw = normalizeKeyword(RAW_KEYWORD || "");
  const lower = keywordRaw.toLowerCase();
  const textarea = document.getElementById("text");
  const inputHelp = document.querySelector(".input-help");

  if (!textarea || !inputHelp) return;

  if (containsAny(lower, ["job", "recruiter", "interview", "hiring", "onboarding"])) {
    textarea.placeholder = "Paste the job message, recruiter email, interview request, or onboarding text you're unsure about...";
    inputHelp.textContent = "Examples: recruiter email, interview request, onboarding message, job offer, payment request";
    return;
  }

  if (containsAny(lower, ["crypto", "bitcoin", "ethereum", "wallet", "airdrop", "nft"])) {
    textarea.placeholder = "Paste the crypto message, wallet request, token offer, or support message you're unsure about...";
    inputHelp.textContent = "Examples: wallet connect message, token airdrop, exchange alert, support DM, recovery offer";
    return;
  }

  textarea.placeholder = "Paste the message, email, website, link, or job offer you're unsure about...";
  inputHelp.textContent = "Examples: delivery text, PayPal alert, crypto message, job offer, account warning";
}

function cleanSeoContent() {
  const seoContent = document.getElementById("seoContent");
  if (!seoContent) return;

  seoContent.innerHTML = seoContent.innerHTML
    .replace(/\*\*/g, "")
    .replace(/<p>\s*<\/p>/g, "")
    .trim();
}

function cleanRelatedLinks() {
  const relatedLinksWrap = document.getElementById("relatedLinksWrap");
  const relatedLinks = document.getElementById("relatedLinks");
  const relatedHeading = document.getElementById("relatedHeading");
  if (!relatedLinksWrap || !relatedLinks || !relatedHeading) return;

  relatedLinks.innerHTML = relatedLinks.innerHTML.replace(/\*\*/g, "").trim();

  const links = relatedLinks.querySelectorAll("li a");
  if (links.length === 0) {
    relatedLinksWrap.style.display = "none";
    return;
  }

  relatedLinksWrap.style.display = "";
}

function cleanMoreLinks() {
  const moreLinksWrap = document.getElementById("moreLinksWrap");
  const moreLinks = document.getElementById("moreLinks");
  const moreLinksHeading = document.getElementById("moreLinksHeading");

  if (!moreLinksWrap || !moreLinks || !moreLinksHeading) return;

  moreLinks.innerHTML = moreLinks.innerHTML.replace(/\*\*/g, "").trim();

  const links = moreLinks.querySelectorAll("li a");
  if (links.length === 0) {
    moreLinksWrap.style.display = "none";
    return;
  }

  moreLinksWrap.style.display = "";
}

function normalizeBottomLinks() {
  const relatedLinks = document.getElementById("relatedLinks");
  const moreLinks = document.getElementById("moreLinks");
  const moreLinksHeading = document.getElementById("moreLinksHeading");

  if (!relatedLinks || !moreLinks || !moreLinksHeading) return;

  const relatedCount = relatedLinks.querySelectorAll("li a").length;
  const moreCount = moreLinks.querySelectorAll("li a").length;

  if (relatedCount === 0 && moreCount > 0) {
    moreLinksHeading.textContent = "Related Scam Checks";
  }

  if (relatedCount > 0 && moreCount > 0) {
    moreLinksHeading.textContent = "More Scam Checks";
  }
}

function summaryForRisk(riskClass) {
  if (riskClass === "high") return "This message shows multiple scam signals. Treat it as unsafe until you verify it directly through the official website, app, company, or platform.";
  if (riskClass === "medium") return "This message shows warning signs. Be cautious and verify the sender, offer, or website before you click, reply, send money, or share information.";
  if (riskClass === "low") return "This message shows fewer obvious scam signals, but you should still verify anything involving links, payments, logins, or personal information before taking action.";
  return "We could not determine a clear risk level. Treat the message cautiously and verify it through official sources before you do anything else.";
}

function paylineForRisk(riskClass) {
  if (riskClass === "high") return "People lose money from messages like this every day. If another one shows up tomorrow, guessing wrong could cost you.";
  if (riskClass === "medium") return "Suspicious messages often do not stop at one. If you have seen one, more may follow. Check the next one before you click, reply, or pay.";
  if (riskClass === "low") return "Even lower-risk messages can become expensive when later versions ask for logins, payments, codes, or urgent action.";
  return "When the risk is unclear, the safest move is to pause, verify this one, and treat the next similar message carefully too.";
}

function cardClassForRisk(risk) {
  if (risk === "high") return "high";
  if (risk === "medium") return "medium";
  if (risk === "low") return "low";
  return "unknown";
}

function iconForRisk(risk) {
  if (risk === "high") return "🔴";
  if (risk === "medium") return "🟠";
  if (risk === "low") return "🟢";
  return "⚪";
}

function signalIconForRisk(risk) {
  if (risk === "high") return "⚠️";
  if (risk === "medium") return "⚠️";
  if (risk === "low") return "✔️";
  return "•";
}

function chipByRisk(risk) {
  if (risk === "high") return "Pattern Match: Strong";
  if (risk === "medium") return "Pattern Match: Moderate";
  if (risk === "low") return "Pattern Match: Lower Risk";
  return "Pattern Match: Review Needed";
}

function scrollToTopCheck() {
  const textarea = document.getElementById("text");
  if (!textarea) return;
  window.scrollTo({ top: 0, behavior: "smooth" });
  setTimeout(() => textarea.focus(), 300);
}

function getShareUrl() {
  return window.location.href;
}

function getShareText() {
  return "This message may be a scam. Check it before you click, reply, or send money:";
}

function getWarningMessage() {
  return `This message may be a scam.\nCheck it before you click, reply, or send money:\n${getShareUrl()}`;
}

function showShareStatus(message) {
  const status = document.getElementById("shareStatus");
  if (!status) return;
  status.textContent = message;
  clearTimeout(showShareStatus.timeoutId);
  showShareStatus.timeoutId = setTimeout(() => {
    status.textContent = "";
  }, 2200);
}

function shareNative() {
  const shareData = { title: document.title, text: getShareText(), url: getShareUrl() };
  if (navigator.share) {
    navigator.share(shareData).catch(() => {});
    return;
  }
  copyWarningMessage();
}

function shareX() {
  const text = encodeURIComponent(getShareText());
  const url = encodeURIComponent(getShareUrl());
  window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, "_blank", "noopener,noreferrer");
}

function copyLink() {
  const url = getShareUrl();
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(() => showShareStatus("Link copied.")).catch(() => fallbackCopy(url, "Link copied."));
    return;
  }
  fallbackCopy(url, "Link copied.");
}

function copyWarningMessage() {
  const message = getWarningMessage();
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(message).then(() => showShareStatus("Warning copied.")).catch(() => fallbackCopy(message, "Warning copied."));
    return;
  }
  fallbackCopy(message, "Warning copied.");
}

function fallbackCopy(value, successMessage) {
  const input = document.createElement("textarea");
  input.value = value;
  input.setAttribute("readonly", "");
  input.style.position = "absolute";
  input.style.left = "-9999px";
  document.body.appendChild(input);
  input.select();
  input.setSelectionRange(0, 99999);
  document.execCommand("copy");
  document.body.removeChild(input);
  showShareStatus(successMessage);
}

function formatResult(raw) {
  const lines = String(raw || "").split("\n").map(l => l.trim()).filter(Boolean);

  let risk = "";
  let signals = [];
  let actions = [];
  let mode = "";

  lines.forEach(line => {
    const lower = line.toLowerCase();

    if (lower.includes("risk level")) {
      risk = line.split(":").slice(1).join(":").trim();
      return;
    }

    if (lower.includes("key signals")) {
      mode = "signals";
      return;
    }

    if (lower.includes("recommended action")) {
      mode = "actions";
      return;
    }

    if (line.startsWith("-")) {
      const cleaned = line.replace(/^-+\s*/, "");
      if (mode === "signals") signals.push(cleaned);
      if (mode === "actions") actions.push(cleaned);
    }
  });

  const riskClass = (risk || "review").trim().toLowerCase();
  const safeRiskClass = cardClassForRisk(riskClass);
  const signalIcon = signalIconForRisk(safeRiskClass);
  const continuationLine = safeRiskClass !== "low"
    ? `<div class="result-continuation">If this reached you once, similar messages may already be on the way. Scammers often repeat the same pattern across many people.</div>`
    : "";

  if (signals.length === 0) {
    signals = ["Review the sender, links, and any requests for money, urgency, or personal information."];
  }

  if (actions.length === 0) {
    actions = ["Do not reply, do not click links, and verify directly through the official website, app, company, or platform before taking action."];
  }

  return `
  <div class="result-card ${safeRiskClass}">
    <div class="result-top">
      <div class="risk ${safeRiskClass}">${iconForRisk(safeRiskClass)} ${safeRiskClass === "unknown" ? "Risk Level: REVIEW" : "Risk Level: " + safeRiskClass.toUpperCase()}</div>
      <div class="result-chip">${chipByRisk(safeRiskClass)}</div>
    </div>

    <div class="result-summary">${escapeHtml(summaryForRisk(safeRiskClass))}</div>
    ${continuationLine}

    <div class="section">
      <div class="section-title">Detected Signals</div>
      <ul class="signal-list">
        ${signals.map(s => `<li class="signal-item"><span class="signal-icon">${signalIcon}</span><span>${escapeHtml(s)}</span></li>`).join("")}
      </ul>
    </div>

    <div class="section">
      <div class="section-title">Recommended Actions</div>
      <div class="action-box">${escapeHtml(actions[0])}</div>
    </div>

    <div class="result-payline">${escapeHtml(paylineForRisk(safeRiskClass))}</div>

    <div class="result-actions">
      <button class="check result-cta" onclick="scrollToTopCheck()">🔁 Check another message now</button>

      <div class="share-wrap">
        <div class="share-alert">Share this page with anyone who could get the same message</div>
        <div class="share-copy">This template is built for quick warning loops: find, share, revisit, and check again when the next suspicious message arrives.</div>
        <div class="share-grid">
          <button type="button" class="share-btn primary" onclick="copyWarningMessage()">⚠️ Copy Warning</button>
          <button type="button" class="share-btn dark" onclick="shareNative()">📤 Share</button>
          <button type="button" class="share-btn light" onclick="shareX()">𝕏 Share to X</button>
          <button type="button" class="share-btn light" onclick="copyLink()">🔗 Copy Link</button>
        </div>
        <div class="share-status" id="shareStatus" aria-live="polite"></div>
      </div>
    </div>
  </div>
  `;
}

function showUpgrade() {
  const el = document.getElementById("upgrade");
  if (!el) return;
  el.style.display = "block";
  setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
}

function scrollToEmail() {
  const emailField = document.getElementById("email");
  if (!emailField) return;
  emailField.scrollIntoView({ behavior: "smooth", block: "center" });
  setTimeout(() => emailField.focus(), 150);
}

async function check() {
  const text = document.getElementById("text").value.trim();
  const email = document.getElementById("email").value.trim().toLowerCase();
  const subscribed = isBrowserSubscribed();
  const result = document.getElementById("result");

  if (!text) {
    result.innerHTML = `
      <div class="result-card unknown">
        <div class="result-top">
          <div class="risk unknown">⚪ Paste Something To Check</div>
          <div class="result-chip">Awaiting Input</div>
        </div>
        <div class="result-summary">Paste a suspicious message, email, website, link, job offer, or investment pitch to check scam risk before you act.</div>
      </div>
    `;
    result.style.display = "block";
    return;
  }

  result.style.display = "block";
  result.innerHTML = `
    <div class="result-card unknown">
      <div class="result-top">
        <div class="risk unknown">⚪ Analyzing...</div>
        <div class="result-chip">Scan In Progress</div>
      </div>
      <div class="result-summary">Checking for scam signals, risky patterns, payment traps, impersonation, and suspicious links.</div>
    </div>
  `;

  try {
    const response = await fetch(API + "/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, email, subscribed })
    });

    const data = await response.json();

    if (data.limit) {
      result.innerHTML = `
        <div class="result-card medium">
          <div class="result-top">
            <div class="risk medium">🟠 Free Check Used</div>
            <div class="result-chip">Upgrade Available</div>
          </div>
          <div class="result-summary">Unlock unlimited protection so you can check the next suspicious message, link, or request before it costs you.</div>
        </div>
      `;
      showUpgrade();
      return;
    }

    result.innerHTML = formatResult(data.result || "");
    showUpgrade();
  } catch (e) {
    result.innerHTML = `
      <div class="result-card unknown">
        <div class="result-top">
          <div class="risk unknown">⚪ Unable To Analyze</div>
          <div class="result-chip">Try Again</div>
        </div>
        <div class="result-summary">We could not analyze this right now. Please try again in a moment.</div>
      </div>
    `;
  }
}

async function checkout(priceId) {
  const pageUrl = window.location.origin + window.location.pathname;

  const response = await fetch(API + "/create-checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      priceId,
      email: null,
      successUrl: pageUrl + "?subscribed=true",
      cancelUrl: pageUrl
    })
  });

  const data = await response.json();

  if (data.url) {
    window.location = data.url;
  } else {
    alert("Checkout failed.");
  }
}
</script>

</body>
</html>
"""

TEMPLATE_HTML = {
    "a": TEMPLATE_A,
    "b": TEMPLATE_B,
    "c": TEMPLATE_C,
}

TODAY_TARGET_SLUGS = [
    "is-amazon-refund-message-legit-or-scam",
    "is-google-account-disabled-email-legit-or-scam",
    "is-fedex-customs-charge-email-legit-or-scam",
    "is-venmo-verification-code-text-real-or-fake",
    "is-bank-debit-card-suspension-email-legit-or-scam",
    "is-whatsapp-unusual-login-email-legit-or-scam",
    "is-telegram-suspicious-activity-message-legit-or-scam",
    "is-usps-tracking-text-legit-or-scam",
    "is-venmo-security-alert-email-legit-or-scam",
    "is-bank-account-closure-email-legit-or-scam",
    "is-apple-account-verification-email-legit-or-scam",
    "snapchat-scams",
    "is-fedex-delivery-legit-or-scam",
    "is-security-alert-message-legit-or-scam",
]

SPECIAL_REPLACEMENTS = {
    "usps": "USPS",
    "ups": "UPS",
    "fedex": "FedEx",
    "amazon": "Amazon",
    "google": "Google",
    "apple": "Apple",
    "id": "ID",
    "whatsapp": "WhatsApp",
    "telegram": "Telegram",
    "snapchat": "Snapchat",
    "venmo": "Venmo",
    "paypal": "PayPal",
    "zelle": "Zelle",
}

STRIP_WORDS = {
    "is",
    "this",
    "a",
    "an",
    "the",
    "or",
    "and",
    "legit",
    "scam",
    "real",
    "fake",
}

LOWERCASE_LINK_WORDS = {"a", "an", "and", "or", "the"}

TITLE_MAP = {
    "is-amazon-refund-message-legit-or-scam": "Amazon Refund Message Scam? Warning Signs and What to Do",
    "is-google-account-disabled-email-legit-or-scam": "Google Account Disabled Email Scam? How to Spot the Warning Signs",
    "is-fedex-customs-charge-email-legit-or-scam": "FedEx Customs Charge Email Scam? What to Check First",
    "is-venmo-verification-code-text-real-or-fake": "Venmo Verification Code Text Scam? Real or Fake Warning Signs",
    "is-bank-debit-card-suspension-email-legit-or-scam": "Bank Debit Card Suspension Email Scam? Warning Signs and What to Do",
    "is-whatsapp-unusual-login-email-legit-or-scam": "WhatsApp Unusual Login Email Scam? How to Check Safely",
    "is-telegram-suspicious-activity-message-legit-or-scam": "Telegram Suspicious Activity Message Scam? Warning Signs and What to Do",
    "is-usps-tracking-text-legit-or-scam": "USPS Tracking Text Scam? What to Check Before You Click",
    "is-venmo-security-alert-email-legit-or-scam": "Venmo Security Alert Email Scam? How to Spot the Warning Signs",
    "is-bank-account-closure-email-legit-or-scam": "Bank Account Closure Email Scam? Warning Signs and What to Do",
    "is-apple-account-verification-email-legit-or-scam": "Apple Account Verification Email Scam? How to Spot the Warning Signs",
    "snapchat-scams": "Snapchat Scams: Common Warning Signs and What to Do",
    "is-fedex-delivery-legit-or-scam": "FedEx Delivery Message Scam? What to Check First",
    "is-security-alert-message-legit-or-scam": "Security Alert Message Scam? Warning Signs and What to Do",
}

DESCRIPTION_MAP = {
    "is-amazon-refund-message-legit-or-scam": "Got an Amazon refund message? Learn the scam warning signs, suspicious link risks, and what to do before you click, reply, or send information.",
    "is-google-account-disabled-email-legit-or-scam": "Received a Google account disabled email? Learn the warning signs of fake account alerts and how to verify the message safely.",
    "is-fedex-customs-charge-email-legit-or-scam": "Got a FedEx customs charge email? Review the scam signs, payment risks, and what to do before clicking or paying anything.",
    "is-venmo-verification-code-text-real-or-fake": "Received a Venmo verification code text? Learn how to spot scam signs, fake urgency, and risky requests before taking action.",
    "is-bank-debit-card-suspension-email-legit-or-scam": "Received a bank debit card suspension email? Learn the common warning signs, suspicious link risks, and how to verify it safely.",
    "is-whatsapp-unusual-login-email-legit-or-scam": "Got a WhatsApp unusual login email? Review the scam warning signs and what to do before you click or share information.",
    "is-telegram-suspicious-activity-message-legit-or-scam": "Received a Telegram suspicious activity message? Learn the warning signs of fake security alerts and risky login links.",
    "is-usps-tracking-text-legit-or-scam": "Got a USPS tracking text? Review the scam warning signs, fake tracking link risks, and what to do before clicking.",
    "is-venmo-security-alert-email-legit-or-scam": "Received a Venmo security alert email? Learn the warning signs of fake account alerts and how to verify it safely.",
    "is-bank-account-closure-email-legit-or-scam": "Got a bank account closure email? Review the scam warning signs, suspicious link risks, and what to do before taking action.",
    "is-apple-account-verification-email-legit-or-scam": "Received an Apple account verification email? Learn the scam signs, suspicious link risks, and how to verify it safely.",
    "snapchat-scams": "Learn common Snapchat scam warning signs, fake account risks, and what to do before replying, clicking, or sharing information.",
    "is-fedex-delivery-legit-or-scam": "Got a FedEx delivery message? Review the scam signs, fake tracking link risks, and what to do before clicking.",
    "is-security-alert-message-legit-or-scam": "Received a security alert message? Learn the warning signs of fake alerts, suspicious links, and what to do next.",
}

ANSWER_SUMMARY_MAP = {
    "is-amazon-refund-message-legit-or-scam": "Use the checker below before you trust an Amazon refund message, click links, reply, or share personal information. Messages like this often use fake urgency and refund confusion to push fast decisions.",
    "is-google-account-disabled-email-legit-or-scam": "Use the checker below before you trust a Google account disabled email, click links, or enter account details. Messages like this often use fear and fake account warnings to trigger fast action.",
    "is-fedex-customs-charge-email-legit-or-scam": "Use the checker below before you trust a FedEx customs charge email, click a payment link, or send information. Messages like this often use delivery pressure and small-fee requests to push fast decisions.",
    "is-venmo-verification-code-text-real-or-fake": "Use the checker below before you trust a Venmo verification code text, share a code, or reply. Messages like this often use fake urgency and account access tricks to push fast decisions.",
    "is-bank-debit-card-suspension-email-legit-or-scam": "Use the checker below before you trust a bank debit card suspension email, click links, or enter account details. Messages like this often use fake account threats to pressure quick action.",
    "is-whatsapp-unusual-login-email-legit-or-scam": "Use the checker below before you trust a WhatsApp unusual login email, click links, or share account information. Messages like this often use fake security pressure to trigger fast decisions.",
    "is-telegram-suspicious-activity-message-legit-or-scam": "Use the checker below before you trust a Telegram suspicious activity message, click links, or enter login details. Messages like this often use fake security alerts to pressure quick action.",
    "is-usps-tracking-text-legit-or-scam": "Use the checker below before you trust a USPS tracking text, click a tracking link, or pay anything. Messages like this often use delivery urgency and fake tracking pages to push fast decisions.",
    "is-venmo-security-alert-email-legit-or-scam": "Use the checker below before you trust a Venmo security alert email, click links, or enter account information. Messages like this often use fake warnings and misleading details to push fast action.",
    "is-bank-account-closure-email-legit-or-scam": "Use the checker below before you trust a bank account closure email, click links, or share personal information. Messages like this often use fake urgency and account threats to push fast decisions.",
    "is-apple-account-verification-email-legit-or-scam": "Use the checker below before you trust an Apple account verification email, click links, or enter login details. Messages like this often use fake authority and misleading details to push fast action.",
    "snapchat-scams": "Use the checker below before you trust suspicious Snapchat messages, links, or account requests. Scams like this often rely on urgency, impersonation, and misleading details to push quick decisions.",
    "is-fedex-delivery-legit-or-scam": "Use the checker below before you trust a FedEx delivery message, click links, or send information. Messages like this often use fake shipping pressure and misleading tracking details to push quick action.",
    "is-security-alert-message-legit-or-scam": "Use the checker below before you trust a security alert message, click links, or enter account details. Messages like this often use fear and fake warnings to pressure fast decisions.",
}

CONTENT_BRIDGE_MAP = {
    "is-amazon-refund-message-legit-or-scam": "If you are unsure about an Amazon refund message, use the checker above before clicking links, replying, or sharing information. Pages like this help you spot refund scam warning signs early and avoid costly mistakes.",
    "is-google-account-disabled-email-legit-or-scam": "If you are unsure about a Google account disabled email, use the checker above before clicking links or entering login details. Pages like this help you slow down, verify safely, and avoid fake account alert scams.",
    "is-fedex-customs-charge-email-legit-or-scam": "If you are unsure about a FedEx customs charge email, use the checker above before clicking payment links or sending information. Pages like this help you spot delivery-payment scams before taking action.",
    "is-venmo-verification-code-text-real-or-fake": "If you are unsure about a Venmo verification code text, use the checker above before replying or sharing any code. Pages like this help you catch account access scams before they turn into a bigger problem.",
    "is-bank-debit-card-suspension-email-legit-or-scam": "If you are unsure about a bank debit card suspension email, use the checker above before clicking links or entering account details. Pages like this help you catch fake banking alerts before taking action.",
    "is-whatsapp-unusual-login-email-legit-or-scam": "If you are unsure about a WhatsApp unusual login email, use the checker above before clicking links or sharing information. Pages like this help you slow down and spot fake security alerts early.",
    "is-telegram-suspicious-activity-message-legit-or-scam": "If you are unsure about a Telegram suspicious activity message, use the checker above before clicking links or entering login details. Pages like this help you catch fake security messages before they cost you access.",
    "is-usps-tracking-text-legit-or-scam": "If you are unsure about a USPS tracking text, use the checker above before clicking links or paying anything. Pages like this help you spot fake delivery messages and risky tracking pages early.",
    "is-venmo-security-alert-email-legit-or-scam": "If you are unsure about a Venmo security alert email, use the checker above before clicking links or entering account details. Pages like this help you spot fake payment-app warnings before taking action.",
    "is-bank-account-closure-email-legit-or-scam": "If you are unsure about a bank account closure email, use the checker above before clicking links or sharing information. Pages like this help you catch fake banking alerts and avoid costly mistakes.",
    "is-apple-account-verification-email-legit-or-scam": "If you are unsure about an Apple account verification email, use the checker above before clicking links or entering login details. Pages like this help you catch fake account verification scams early.",
    "snapchat-scams": "If you are dealing with suspicious Snapchat messages or account requests, use the checker above before clicking links, replying, or sharing information. Pages like this help you spot common Snapchat scam patterns early.",
    "is-fedex-delivery-legit-or-scam": "If you are unsure about a FedEx delivery message, use the checker above before clicking links or sending information. Pages like this help you spot fake delivery messages before taking action.",
    "is-security-alert-message-legit-or-scam": "If you are unsure about a security alert message, use the checker above before clicking links or entering account details. Pages like this help you slow down, verify safely, and avoid fake alert scams.",
}

HUB_MAP = {
    "is-google-account-disabled-email-legit-or-scam": ("Account Security Scam Hub", "/account-security-scam-hub/"),
    "is-whatsapp-unusual-login-email-legit-or-scam": ("Account Security Scam Hub", "/account-security-scam-hub/"),
    "is-telegram-suspicious-activity-message-legit-or-scam": ("Account Security Scam Hub", "/account-security-scam-hub/"),
    "is-security-alert-message-legit-or-scam": ("Account Security Scam Hub", "/account-security-scam-hub/"),
    "is-bank-debit-card-suspension-email-legit-or-scam": ("Banking and Payment Scam Hub", "/banking-and-payment-scam-hub/"),
    "is-bank-account-closure-email-legit-or-scam": ("Banking and Payment Scam Hub", "/banking-and-payment-scam-hub/"),
    "is-venmo-verification-code-text-real-or-fake": ("Banking and Payment Scam Hub", "/banking-and-payment-scam-hub/"),
    "is-venmo-security-alert-email-legit-or-scam": ("Banking and Payment Scam Hub", "/banking-and-payment-scam-hub/"),
    "is-amazon-refund-message-legit-or-scam": ("Banking and Payment Scam Hub", "/banking-and-payment-scam-hub/"),
    "is-fedex-customs-charge-email-legit-or-scam": ("Delivery Scam Hub", "/delivery-scam-hub/"),
    "is-usps-tracking-text-legit-or-scam": ("Delivery Scam Hub", "/delivery-scam-hub/"),
    "is-fedex-delivery-legit-or-scam": ("Delivery Scam Hub", "/delivery-scam-hub/"),
    "snapchat-scams": ("Social Media Scam Hub", "/social-media-scam-hub/"),
}


def get_target_dirs() -> List[str]:
    if TARGET_TEMPLATE == "all":
        return [TEMPLATE_PATHS["a"], TEMPLATE_PATHS["b"], TEMPLATE_PATHS["c"]]
    if TARGET_TEMPLATE not in TEMPLATE_PATHS:
        raise ValueError(f"Invalid TARGET_TEMPLATE: {TARGET_TEMPLATE}")
    return [TEMPLATE_PATHS[TARGET_TEMPLATE]]


def get_target_slugs() -> List[str]:
    if MAX_URLS <= 0:
        raise ValueError(f"Invalid MAX_URLS_TO_REFRESH: {MAX_URLS}")
    return TODAY_TARGET_SLUGS[:MAX_URLS]


def template_key_from_path(path: str) -> Optional[str]:
    normalized = path.replace("\\", "/")
    if normalized.startswith("scam-check-now/"):
        return "a"
    if normalized.startswith("scam-check-now-b/"):
        return "b"
    if normalized.startswith("scam-check-now-c/"):
        return "c"
    return None


def is_allowed_seo_page(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return (
        normalized.startswith("scam-check-now/")
        or normalized.startswith("scam-check-now-b/")
        or normalized.startswith("scam-check-now-c/")
    ) and normalized.endswith("/index.html")


def slug_from_path(path: str) -> Optional[str]:
    normalized = path.replace("\\", "/").strip("/")
    parts = normalized.split("/")
    if len(parts) < 2:
        return None
    return parts[-2].strip() or None


def get_target_files() -> List[str]:
    files: List[str] = []
    seen: Set[str] = set()

    for base_dir in get_target_dirs():
        for slug in get_target_slugs():
            candidate = os.path.join(base_dir, slug, "index.html")
            normalized_candidate = candidate.replace("\\", "/")
            if (
                os.path.exists(candidate)
                and is_allowed_seo_page(candidate)
                and normalized_candidate not in seen
            ):
                files.append(candidate)
                seen.add(normalized_candidate)

    return files


def humanize_word(word: str) -> str:
    lower = word.lower()
    if lower in SPECIAL_REPLACEMENTS:
        return SPECIAL_REPLACEMENTS[lower]
    return lower.capitalize()


def slug_to_topic_phrase(slug: str) -> str:
    words = [w for w in slug.split("-") if w]
    cleaned = [humanize_word(w) for w in words if w.lower() not in STRIP_WORDS]
    if not cleaned:
        cleaned = [humanize_word(w) for w in words]
    return " ".join(cleaned).strip() or "Suspicious message"


def slug_to_question_label(slug: str) -> str:
    if slug == "snapchat-scams":
        return "Snapchat Scams"

    words = [w for w in slug.split("-") if w]
    rendered: List[str] = []

    for index, word in enumerate(words):
        lower = word.lower()
        if lower in SPECIAL_REPLACEMENTS:
            rendered.append(SPECIAL_REPLACEMENTS[lower])
        elif index == 0 and lower == "is":
            rendered.append("Is")
        elif lower in LOWERCASE_LINK_WORDS:
            rendered.append(lower)
        elif lower == "scam":
            rendered.append("Scam")
        else:
            rendered.append(lower.capitalize())

    label = " ".join(rendered).strip()
    if label.startswith("Is ") and not label.endswith("?"):
        label = f"{label}?"
    label = label.replace(" Legit Or Scam?", " Legit or a Scam?")
    label = label.replace(" Real Or Fake?", " Real or Fake?")
    label = label.replace(" Legit Or Scam", " Legit or a Scam")
    label = label.replace(" Real Or Fake", " Real or Fake")
    return label


def build_title(slug: str) -> str:
    return TITLE_MAP.get(slug, f"{slug_to_topic_phrase(slug)} Scam? Warning Signs and What to Do")


def build_description(slug: str) -> str:
    return DESCRIPTION_MAP.get(
        slug,
        f"Check whether {slug_to_topic_phrase(slug)} is a scam. Review warning signs, suspicious link risks, and what to do before acting.",
    )


def build_answer_summary(slug: str) -> str:
    return ANSWER_SUMMARY_MAP.get(
        slug,
        f"Use the checker below before you trust {slug_to_topic_phrase(slug).lower()}, click links, reply, send money, or share personal information.",
    )


def build_content_bridge(slug: str) -> str:
    return CONTENT_BRIDGE_MAP.get(
        slug,
        f"If you are unsure about {slug_to_topic_phrase(slug).lower()}, use the checker above before clicking links, replying, or sending information.",
    )


def build_internal_link_targets(slug: str) -> List[str]:
    category_keywords = [part for part in slug.split("-") if part and part not in STRIP_WORDS]
    preferred: List[str] = []
    fallback: List[str] = []

    for candidate in TODAY_TARGET_SLUGS:
        if candidate == slug:
            continue
        if any(keyword in candidate for keyword in category_keywords[:3]):
            preferred.append(candidate)
        else:
            fallback.append(candidate)

    return (preferred + fallback)[:10]


def build_link_items_html(slugs: List[str]) -> str:
    items: List[str] = []
    for target_slug in slugs:
        href = f"/{target_slug}/"
        label = slug_to_question_label(target_slug)
        items.append(
            f'<li><a href="{html.escape(href, quote=True)}">{html.escape(label)}</a></li>'
        )
    return "".join(items)


def build_hub_link_html(slug: str) -> str:
    label, href = HUB_MAP.get(slug, ("", ""))
    if not label or not href:
        return ""
    return (
        '<div class="hub-link-block">'
        '<span class="hub-link-label">Related scam category</span>'
        f'<a class="hub-link-anchor" href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
        "</div>"
    )


def extract_first(pattern: str, content: str, flags: int = re.DOTALL | re.IGNORECASE) -> Optional[str]:
    match = re.search(pattern, content, flags)
    if not match:
        return None
    return match.group(1).strip()


def extract_canonical_url(content: str, slug: str) -> str:
    extracted = extract_first(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', content)
    if extracted:
        return extracted
    return f"https://verixiaapps.com/{slug}/"


def extract_keyword(content: str, slug: str) -> str:
    extracted = extract_first(r'const\s+RAW_KEYWORD\s*=\s*["\'](.*?)["\']', content)
    if extracted:
        return extracted
    title = build_title(slug)
    return title.replace(" Scam? Warning Signs and What to Do", "").replace(" Scam?", "")


def extract_ai_content(content: str) -> str:
    extracted = extract_first(
        r'<div[^>]*id=["\']seoContent["\'][^>]*>(.*?)</div>',
        content,
    )
    if extracted is not None:
        return extracted
    return "<p>Scam warning information will be added here.</p>"


def extract_hub_link(content: str) -> str:
    extracted = extract_first(
        r'<div[^>]*id=["\']hubLinkWrap["\'][^>]*>(.*?)</div>',
        content,
    )
    if not extracted:
        return ""
    if "<a" not in extracted.lower():
        return ""
    return extracted


def render_from_shell(path: str, original: str, slug: str) -> str:
    template_key = template_key_from_path(path)
    if template_key is None:
        raise ValueError(f"Could not determine template for path: {path}")

    shell = TEMPLATE_HTML[template_key]
    if not shell or "PASTE EXACT" in shell:
        raise ValueError(f"Template shell for '{template_key}' is not populated.")

    title = build_title(slug)
    description = build_description(slug)
    canonical_url = extract_canonical_url(original, slug)
    keyword = extract_keyword(original, slug)
    ai_content = extract_ai_content(original)
    hub_link = extract_hub_link(original) or build_hub_link_html(slug)

    targets = build_internal_link_targets(slug)
    related_links = build_link_items_html(targets[:5])
    more_links = build_link_items_html(targets[5:10])

    replacements: Dict[str, str] = {
        "{{TITLE}}": html.escape(title),
        "{{DESCRIPTION}}": html.escape(description, quote=True),
        "{{CANONICAL_URL}}": html.escape(canonical_url, quote=True),
        "{{KEYWORD}}": keyword,
        "{{AI_CONTENT}}": ai_content,
        "{{RELATED_LINKS}}": related_links,
        "{{MORE_LINKS}}": more_links,
        "{{HUB_LINK}}": hub_link,
    }

    rendered = shell
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    return normalize_whitespace(rendered)


def replace_title(content: str, new_title: str) -> str:
    return re.sub(
        r"<title>.*?</title>",
        f"<title>{html.escape(new_title)}</title>",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_meta_description(content: str, new_description: str) -> str:
    return re.sub(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\'].*?["\'][^>]*>',
        f'<meta name="description" content="{html.escape(new_description, quote=True)}">',
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_answer_summary(content: str, new_text: str) -> str:
    return re.sub(
        r'(<p[^>]*id=["\']answerSummary["\'][^>]*>)(.*?)(</p>)',
        lambda match: f"{match.group(1)}{html.escape(new_text)}{match.group(3)}",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_content_bridge(content: str, new_text: str) -> str:
    return re.sub(
        r'(<div[^>]*id=["\']contentBridge["\'][^>]*>)(.*?)(</div>)',
        lambda match: f"{match.group(1)}{html.escape(new_text)}{match.group(3)}",
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def replace_list_by_id(content: str, list_id: str, items_html: str) -> str:
    patterns = [
        rf'(<ul[^>]*id="{re.escape(list_id)}"[^>]*>)(.*?)(</ul>)',
        rf"(<ul[^>]*id='{re.escape(list_id)}'[^>]*>)(.*?)(</ul>)",
    ]

    updated = content
    for pattern in patterns:
        updated, count = re.subn(
            pattern,
            lambda match: f"{match.group(1)}{items_html}{match.group(3)}",
            updated,
            count=1,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if count:
            return updated
    return updated


def update_internal_links_only(content: str, slug: str) -> str:
    targets = build_internal_link_targets(slug)
    updated = replace_list_by_id(content, "relatedLinks", build_link_items_html(targets[:5]))
    updated = replace_list_by_id(updated, "moreLinks", build_link_items_html(targets[5:10]))
    return updated


def normalize_whitespace(content: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", content).strip() + "\n"


def should_full_rebuild() -> bool:
    return REFRESH_SCOPE in {"pages", "mixed"}


def should_update_metadata_only() -> bool:
    return REFRESH_SCOPE == "metadata"


def should_update_internal_links_only() -> bool:
    return REFRESH_SCOPE == "internal-links"


def process_file(path: str) -> bool:
    if not is_allowed_seo_page(path):
        print(f"SKIPPED (not allowed): {path}")
        return False

    slug = slug_from_path(path)
    if not slug:
        print(f"SKIPPED (no slug): {path}")
        return False

    with open(path, "r", encoding="utf-8") as file:
        original = file.read()

    if should_full_rebuild():
        updated = render_from_shell(path, original, slug)
    elif should_update_metadata_only():
        updated = original
        updated = replace_title(updated, build_title(slug))
        updated = replace_meta_description(updated, build_description(slug))
        updated = normalize_whitespace(updated)
    elif should_update_internal_links_only():
        updated = update_internal_links_only(original, slug)
        updated = normalize_whitespace(updated)
    else:
        raise ValueError(f"Invalid REFRESH_SCOPE: {REFRESH_SCOPE}")

    if updated == original:
        print(f"NO CHANGE: {path}")
        return False

    print(f"UPDATED: {path}")

    if not DRY_RUN:
        with open(path, "w", encoding="utf-8") as file:
            file.write(updated)

    return True


def main() -> None:
    if REFRESH_SCOPE not in {"pages", "metadata", "internal-links", "mixed"}:
        raise ValueError(f"Invalid REFRESH_SCOPE: {REFRESH_SCOPE}")

    target_files = get_target_files()

    if not target_files:
        print("No matching GSC target SEO pages found.")
        return

    print(f"TARGET_TEMPLATE={TARGET_TEMPLATE}")
    print(f"REFRESH_SCOPE={REFRESH_SCOPE}")
    print(f"MAX_URLS_TO_REFRESH={MAX_URLS}")
    print(f"DRY_RUN={DRY_RUN}")
    print(f"Processing {len(target_files)} exact GSC target SEO pages...")

    updated_count = 0
    for file_path in target_files:
        if process_file(file_path):
            updated_count += 1

    print(f"Updated {updated_count} file(s).")
    print("Done.")


if __name__ == "__main__":
    main()