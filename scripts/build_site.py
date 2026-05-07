#!/usr/bin/env python3
"""Generate the static GitHub Pages site from structured source data."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CLOUDFLARE = '<!-- Cloudflare Web Analytics --><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token": "ce86138e8d17417db1b5cb824d2d3c86"}\'></script><!-- End Cloudflare Web Analytics -->'
HOME_ICON = '<svg class="home-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11.5 12 4l9 7.5"></path><path d="M5 10.5V20h5v-6h4v6h5v-9.5"></path></svg>'
READING_NOTE = "התמצית שלעיל היא תמצית עצמאית בעברית, שנכתבה בסיוע כלי בינה מלאכותית ובעריכה אנושית, על בסיס המאמר המקורי. היא אינה תרגום רשמי של התקציר או של המאמר, אינה מטעם המחברים או כתב העת, ואינה מחליפה קריאה במקור"


def h(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json_ld(data: object, indent: int = 2) -> str:
    return json.dumps(data, ensure_ascii=False, indent=indent)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def absolute(site: dict, path: str = "") -> str:
    base = site["baseUrl"]
    return base + path


def with_prefix(src: str, prefix: str) -> str:
    if src.startswith(("http://", "https://")):
        return src
    return prefix + src


def with_version(src: str, version: str | None) -> str:
    return f"{src}?v={version}" if version else src


def paper_image_src(paper: dict, prefix: str = "") -> str:
    image = paper.get("image", {})
    return with_version(with_prefix(image.get("src", ""), prefix), image.get("version"))


def topic_image_src(topic: dict, site: dict, prefix: str = "") -> str:
    return with_version(with_prefix(topic["image"], prefix), site.get("topicImageVersion"))


def load_data() -> tuple[dict, list[dict], dict, list[str]]:
    site = load_json(DATA / "site.json")
    order = load_json(DATA / "paper_order.json")
    papers_by_file = {}
    for path in sorted((DATA / "papers").glob("*.json")):
        paper = load_json(path)
        papers_by_file[paper["file"]] = paper
    missing = [file_name for file_name in order if file_name not in papers_by_file]
    if missing:
        raise RuntimeError(f"paper_order.json references missing paper data files: {missing}")
    topics = load_json(ROOT / "topics.json")
    papers = [papers_by_file[file_name] for file_name in order]
    validate_topics(topics["topics"], papers_by_file)
    return site, papers, topics, order


def validate_topics(topics: list[dict], papers_by_file: dict[str, dict]) -> None:
    errors = []
    for topic in topics:
        for file_name in topic.get("articles", []):
            if file_name not in papers_by_file:
                errors.append(f"{topic['id']} references missing article {file_name}")
    for paper in papers_by_file.values():
        topic_ids = {topic["id"] for topic in topics if paper["file"] in topic.get("articles", [])}
        if topic_ids != set(paper.get("topics", [])):
            errors.append(f"{paper['file']} topic mismatch: topics.json={sorted(topic_ids)} data={sorted(paper.get('topics', []))}")
    if errors:
        raise RuntimeError("\n".join(errors))


def topics_for_paper(paper: dict, topics: list[dict]) -> list[dict]:
    wanted = set(paper.get("topics", []))
    return [topic for topic in topics if topic["id"] in wanted]


def topic_by_id(topics: list[dict]) -> dict[str, dict]:
    return {topic["id"]: topic for topic in topics}


def item_list(site: dict, papers: list[dict]) -> list[dict]:
    return [
        {
            "@type": "ListItem",
            "position": index,
            "url": absolute(site, paper["file"]),
            "name": paper["titleHe"],
            "description": paper["summaryHe"],
        }
        for index, paper in enumerate(papers, start=1)
    ]


def paper_card(paper: dict, *, prefix: str = "", eager: bool = False, show_new: bool = False) -> str:
    attrs = 'decoding="async" fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    badge = '\n          <span class="new-badge">חדש!</span>' if show_new else ""
    return f'''      <a class="item" href="{h(prefix + paper["file"])}">
        <img class="preview" src="{h(paper_image_src(paper, prefix))}" alt="{h(paper["image"].get("altHe", ""))}" width="800" height="600" {attrs}>
        <span class="content">{badge}
          <h2>{h(paper["titleHe"])}</h2>
          <p class="authors">{h(paper["authorsCardHe"])}</p>
          <p class="summary">{h(paper["summaryHe"])}</p>
          <span class="open">לקריאת העמוד</span>
        </span>
      </a>'''


def article_json_ld(site: dict, paper: dict) -> dict:
    based_on = {
        "@type": "ScholarlyArticle",
        "name": paper["paperTitle"],
        "author": paper.get("sourceAuthors", []),
    }
    if paper.get("journal"):
        based_on["isPartOf"] = {"@type": "Periodical", "name": paper["journal"]}
    if paper.get("doiUrl"):
        based_on["identifier"] = paper["doiUrl"]
        based_on["url"] = paper["doiUrl"]
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": paper["titleHe"],
        "description": paper["descriptionHe"],
        "inLanguage": "he",
        "url": absolute(site, paper["file"]),
        "mainEntityOfPage": absolute(site, paper["file"]),
        "dateModified": paper["dateModified"],
        "image": absolute(site, paper["image"]["src"]),
        "isPartOf": {
            "@type": "WebSite",
            "name": site["siteNameHe"],
            "url": site["baseUrl"],
        },
        "about": paper.get("keywords", []),
        "author": paper.get("authors", []),
        "isBasedOn": based_on,
    }


ARTICLE_CSS = """    :root {
      color-scheme: light;
      --ink: #202124;
      --muted: #666;
      --accent: #16555d;
      --accent-dark: #16404d;
      --rule: #d9e1e3;
      --paper: #fff;
      --page: #f5f7f8;
      font-family: Arial, "Noto Sans Hebrew", "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    .skip-link { position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 10px 14px; background: #ffffff; color: #0563c1; border: 2px solid #16555d; border-radius: 4px; font-weight: 700; transform: translateY(-140%); transition: transform 120ms ease; }
    .skip-link:focus { transform: translateY(0); }
    body { margin: 0; background: var(--page); color: var(--ink); direction: rtl; text-align: right; line-height: 1.65; font-size: 18px; }
    main { width: min(920px, calc(100% - 32px)); margin: 32px auto; padding: 48px 56px; background: var(--paper); border: 1px solid var(--rule); }
    .logo-link { display: block; width: min(260px, 70vw); margin: 0 0 28px auto; }
    .logo-link:focus-visible, .home-link:focus-visible, .topic-nav-link:focus-visible { outline: 2px solid var(--accent); outline-offset: 4px; }
    .site-logo { display: block; width: 100%; height: auto; margin: 0; }
    .page-nav { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 12px; margin: 0 0 20px; }
    .page-nav .home-link { margin: 0; }
    .topic-nav-label { color: var(--muted); font-size: 15px; font-weight: 700; }
    .topic-nav-link { display: inline-flex; align-items: center; min-height: 30px; padding: 3px 10px; border: 1px solid var(--rule); border-radius: 6px; background: #f7fbfb; color: var(--accent-dark); font-size: 15px; font-weight: 700; line-height: 1.3; text-decoration: none; }
    .topic-nav-link:hover { border-color: var(--accent); text-decoration: underline; }
    .home-link { display: inline-flex; align-items: center; gap: 8px; margin: 0 0 20px; color: #0563c1; font-weight: 700; text-decoration: none; }
    .home-link:hover { text-decoration: underline; }
    .home-icon { width: 19px; height: 19px; flex: 0 0 auto; }
    h1, h2, p, .meta-row { direction: rtl; text-align: right; }
    h1 { margin: 0 0 4px; color: var(--accent-dark); font-size: 34px; line-height: 1.2; font-weight: 700; }
    .subtitle { margin: 0 0 24px; color: var(--muted); font-size: 19px; font-weight: 700; }
    .metadata { margin: 0 0 24px; }
    .meta-row { margin: 2px 0; }
    .meta-label { font-weight: 700; }
    .meta-value { unicode-bidi: plaintext; }
    .topic-links { display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: baseline; margin: -8px 0 28px; color: var(--muted); font-size: 16px; }
    .topic-label { font-weight: 700; color: var(--accent-dark); }
    .topic-links a { color: #0563c1; font-weight: 700; }
    .latin { direction: ltr; unicode-bidi: embed; display: inline-block; max-width: 100%; text-align: left; vertical-align: top; }
    a { color: #0563c1; text-decoration: underline; overflow-wrap: anywhere; }
    .one-liner { margin: 28px 0; color: var(--accent); font-size: 20px; line-height: 1.5; font-weight: 700; }
    section { margin: 22px 0 0; }
    h2 { margin: 0 0 8px; color: var(--accent); font-size: 25px; line-height: 1.3; }
    p { margin: 0 0 9px; }
    .note { margin-top: 28px; color: #707070; font-size: 16px; }
    .last-updated { margin: 10px 0 0; color: #707070; font-size: 15px; }
    .footer-links { margin-top: 30px; padding-top: 18px; border-top: 1px solid var(--rule); color: #666; font-size: 15px; }
    .footer-links a { color: #0563c1; font-weight: 700; }
    a:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
    @media (max-width: 640px) { body { font-size: 16px; } main { width: 100%; margin: 0; padding: 28px 20px; border-width: 0; } h1 { font-size: 28px; } h2 { font-size: 22px; } .one-liner { font-size: 18px; } }
    @media print { body { background: #fff; } main { width: auto; margin: 0; padding: 0; border: 0; } }
"""


def topic_nav(topic_list: list[dict]) -> str:
    links = "\n".join(
        f'      <a class="topic-nav-link" href="{h(topic["page"])}">{h(topic["shortTitleHe"])}</a>'
        for topic in topic_list
    )
    return f'''    <nav class="page-nav" aria-label="ניווט עמוד המאמר" data-pagefind-ignore>
      <a class="home-link" href="index.html" aria-label="חזרה לעמוד הבית" data-pagefind-ignore>
        {HOME_ICON}
        <span>לעמוד הבית</span>
      </a>
      <span class="topic-nav-label">נושאים:</span>
{links}
    </nav>'''


def inline_topic_links(topic_list: list[dict]) -> str:
    links = ",\n      ".join(f'<a href="{h(topic["page"])}">{h(topic["shortTitleHe"])}</a>' for topic in topic_list)
    return f'''    <nav class="topic-links" aria-label="נושאים">
      <span class="topic-label">נושאים:</span>
      {links}
    </nav>'''


def article_metadata(paper: dict) -> str:
    rows = [
        f'''        <div class="meta-row">
          <span class="meta-label">מאמר:</span>
          <span class="meta-value latin" dir="ltr">{h(paper["paperTitle"])}</span>
        </div>''',
        f'''        <div class="meta-row">
          <span class="meta-label">חוקרים:</span>
          <span class="meta-value latin" dir="ltr">{paper["authorsHtml"]}</span>
        </div>''',
    ]
    if paper.get("journal"):
        rows.append(f'''        <div class="meta-row">
          <span class="meta-label">כתב עת:</span>
          <span class="meta-value latin" dir="ltr">{h(paper["journal"])}</span>
        </div>''')
    if paper.get("dateText"):
        rows.append(f'''        <div class="meta-row">
          <span class="meta-label">תאריך:</span>
          <span class="meta-value">{h(paper["dateText"])}</span>
        </div>''')
    if paper.get("doiUrl"):
        rows.append(f'''        <div class="meta-row">
          <span class="meta-label">DOI:</span>
          <a class="meta-value latin" dir="ltr" href="{h(paper["doiUrl"])}" target="_blank" rel="noopener noreferrer">{h(paper["doiLabel"] or paper["doiUrl"])}</a>
        </div>''')
    return "\n".join(rows)


def article_sections(paper: dict) -> str:
    chunks = []
    for section in paper.get("sections", []):
        paragraphs = "\n".join(f"          <p>{paragraph}</p>" for paragraph in section.get("paragraphsHtml", []))
        chunks.append(f'''      <section>
        <h2>{h(section["headingHe"])}</h2>
{paragraphs}
      </section>''')
    return "\n".join(chunks)


def render_article(site: dict, paper: dict, topics: list[dict]) -> str:
    topic_list = topics_for_paper(paper, topics)
    schema = article_json_ld(site, paper)
    image_abs = absolute(site, paper["image"]["src"])
    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(paper["titleHe"])}</title>
  <!-- Search and AI discovery metadata -->
  <meta name="description" content="{h(paper["descriptionHe"])}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{h(absolute(site, paper["file"]))}">
  <meta property="og:locale" content="he_IL">
  <meta property="og:site_name" content="{h(site["siteNameHe"])}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{h(paper["titleHe"])}">
  <meta property="og:description" content="{h(paper["descriptionHe"])}">
  <meta property="og:url" content="{h(absolute(site, paper["file"]))}">
  <meta property="og:image" content="{h(image_abs)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{h(paper["titleHe"])}">
  <meta name="twitter:description" content="{h(paper["descriptionHe"])}">
  <meta name="twitter:image" content="{h(image_abs)}">
  <script type="application/ld+json">
{dump_json_ld(schema)}
  </script>
  <!-- End search and AI discovery metadata -->
  <style>
{ARTICLE_CSS}  </style>
</head>
<body>
  <a class="skip-link" href="#main-content">דילוג לתוכן המרכזי</a>
  <main id="main-content" tabindex="-1" data-pagefind-body>
    <a class="logo-link" href="https://www.tau.ac.il/" aria-label="אתר אוניברסיטת תל אביב" data-pagefind-ignore target="_blank" rel="noopener noreferrer">
      <img class="site-logo" src="HEB_bold.jpg" alt="לוגו אוניברסיטת תל אביב">
    </a>
{topic_nav(topic_list)}
    <h1>{h(paper["titleHe"])}</h1>
    <p class="subtitle">{h(paper["subtitleHe"])}</p>

    <div class="metadata">
{article_metadata(paper)}
    </div>

{inline_topic_links(topic_list)}

    <p class="one-liner">{paper["oneLinerHtml"]}</p>

{article_sections(paper)}

    <p class="note">{READING_NOTE}</p>
    <p class="last-updated" data-pagefind-ignore>עודכן לאחרונה: {h(paper["lastUpdatedHe"])}</p>
    <footer class="footer-links" data-pagefind-ignore>
      <a href="accessibility.html">הצהרת נגישות</a>
    </footer>
  </main>
  {CLOUDFLARE}
</body>
</html>
'''


HOME_CSS = '''    :root { color-scheme: light; --ink:#202124; --muted:#5f6368; --accent:#16555d; --accent-dark:#16404d; --line:#d9e1e3; --paper:#ffffff; --page:#f5f7f8; --link:#0563c1; font-family: Arial, "Noto Sans Hebrew", "Segoe UI", sans-serif; }
    * { box-sizing: border-box; }
    .skip-link { position:absolute; top:10px; right:10px; z-index:1000; padding:10px 14px; background:#fff; color:#0563c1; border:2px solid #16555d; border-radius:4px; font-weight:700; transform:translateY(-140%); transition:transform 120ms ease; }
    .skip-link:focus { transform:translateY(0); }
    body { margin:0; background:var(--page); color:var(--ink); direction:rtl; text-align:right; line-height:1.65; font-size:18px; }
    main { width:min(1120px, calc(100% - 32px)); margin:0 auto; padding:44px 0 56px; }
    header { padding:18px 0 28px; border-bottom:1px solid var(--line); }
    .logo-link { display:block; width:min(280px, 70vw); margin:0 0 18px auto; }
    .logo-link:focus-visible { outline:2px solid var(--accent); outline-offset:4px; }
    .site-logo { display:block; width:100%; height:auto; margin:0; }
    h1 { margin:0; color:var(--accent-dark); font-size:42px; line-height:1.2; font-weight:700; }
    .intro { max-width:820px; margin:12px 0 0; color:var(--muted); font-size:20px; }
    .search-panel { margin-top:24px; max-width:720px; --pagefind-ui-scale:.92; --pagefind-ui-primary:var(--accent); --pagefind-ui-text:var(--ink); --pagefind-ui-background:var(--paper); --pagefind-ui-border:var(--line); --pagefind-ui-border-width:1px; --pagefind-ui-border-radius:8px; --pagefind-ui-image-border-radius:6px; --pagefind-ui-font:Arial, "Noto Sans Hebrew", "Segoe UI", sans-serif; }
    .search-panel .pagefind-ui { direction:rtl; text-align:right; }
    .search-panel .pagefind-ui__form { margin:0; }
    .search-panel .pagefind-ui__search-input { text-align:right; }
    .section { margin-top:34px; }
    .section-heading { margin:0 0 8px; color:var(--accent-dark); font-size:28px; line-height:1.25; }
    .section .grid, .topic-grid { margin-top:18px; }
    .topic-grid { display:grid; grid-template-columns:repeat(5, minmax(0, 1fr)); gap:16px; }
    .topic-card, .item { display:flex; flex-direction:column; min-height:100%; overflow:hidden; background:var(--paper); border:1px solid var(--line); border-radius:8px; color:inherit; text-decoration:none; transition:border-color 160ms ease, transform 160ms ease; }
    .topic-card:hover, .topic-card:focus-visible, .item:hover, .item:focus-visible { border-color:var(--accent); transform:translateY(-2px); outline:none; }
    .topic-preview, .preview { display:block; width:100%; height:auto; max-width:100%; aspect-ratio:4 / 3; object-fit:cover; object-position:top center; border-bottom:1px solid var(--line); background:#eef3f4; }
    .topic-content, .content { display:flex; flex-direction:column; flex:1; padding:18px; }
    .topic-content { padding:15px; }
    .topic-content h2 { font-size:19px; }
    .topic-content p { color:var(--muted); font-size:15px; line-height:1.5; }
    .topic-count { margin-top:auto; padding-top:12px; color:var(--link); font-size:14px; font-weight:700; }
    .grid { display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:18px; margin-top:28px; }
    h2 { margin:0 0 8px; color:var(--accent); font-size:22px; line-height:1.35; }
    p { margin:0; }
    .summary { color:var(--muted); font-size:16px; }
    .authors { margin-bottom:8px; color:var(--accent-dark); font-size:15px; font-weight:700; }
    .new-badge { align-self:flex-start; margin-bottom:8px; color:#b3261e; font-size:15px; font-weight:700; line-height:1; }
    .open { margin-top:auto; padding-top:16px; color:var(--link); font-weight:700; }
    .footer-links { margin-top:32px; padding-top:18px; border-top:1px solid var(--line); color:var(--muted); font-size:15px; }
    .footer-links a { color:var(--link); font-weight:700; }
    a:focus-visible { outline:3px solid var(--accent); outline-offset:3px; }
    @media (max-width:1100px) { .topic-grid { grid-template-columns:repeat(3, minmax(0, 1fr)); } }
    @media (max-width:980px) { .grid { grid-template-columns:repeat(2, minmax(0, 1fr)); } }
    @media (max-width:700px) { .grid, .topic-grid { grid-template-columns:1fr; } h1 { font-size:34px; } .intro { font-size:18px; } }
    @media (max-width:520px) { main { width:min(100% - 24px, 1120px); padding-top:26px; } h1 { font-size:29px; } .content { padding:16px; } }
'''


def topic_card(topic: dict, site: dict) -> str:
    count = len(topic.get("articles", []))
    return f'''      <a class="topic-card" href="{h(topic["page"])}">
        <img class="topic-preview" src="{h(topic_image_src(topic, site))}" alt="{h(topic["imageAltHe"])}" width="800" height="600" loading="lazy" decoding="async">
        <span class="topic-content">
          <h2>{h(topic["titleHe"])}</h2>
          <p>{h(topic["descriptionHe"])}</p>
          <span class="topic-count">{count} תמציות בנושא</span>
        </span>
      </a>'''


def render_index(site: dict, papers: list[dict], topics: list[dict]) -> str:
    latest_count = site.get("homepageLatestCount", 9)
    latest = papers[:latest_count]
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": site["siteNameHe"],
        "description": site["homeDescriptionHe"],
        "inLanguage": "he",
        "url": site["baseUrl"],
        "isPartOf": {"@type": "WebSite", "name": site["siteNameHe"], "url": site["baseUrl"]},
        "mainEntity": {"@type": "ItemList", "itemListElement": item_list(site, papers)},
    }
    latest_cards = "\n".join(
        paper_card(paper, eager=index < 3, show_new=index < 3)
        for index, paper in enumerate(latest)
    )
    topic_cards = "\n".join(topic_card(topic, site) for topic in topics)
    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(site["siteNameHe"])}</title>
  <!-- Search and AI discovery metadata -->
  <meta name="description" content="{h(site["homeDescriptionHe"])}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{h(site["baseUrl"])}">
  <meta property="og:locale" content="he_IL">
  <meta property="og:site_name" content="{h(site["siteNameHe"])}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{h(site["siteNameHe"])}">
  <meta property="og:description" content="{h(site["homeDescriptionHe"])}">
  <meta property="og:url" content="{h(site["baseUrl"])}">
  <meta property="og:image" content="{h(absolute(site, "HEB_bold.jpg"))}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{h(site["siteNameHe"])}">
  <meta name="twitter:description" content="{h(site["homeDescriptionHe"])}">
  <meta name="twitter:image" content="{h(absolute(site, "HEB_bold.jpg"))}">
  <script type="application/ld+json">
{dump_json_ld(schema)}
  </script>
  <!-- End search and AI discovery metadata -->
  <link href="pagefind/pagefind-ui.css" rel="stylesheet">
  <style>
{HOME_CSS}  </style>
</head>
<body>
  <a class="skip-link" href="#main-content">דילוג לתוכן המרכזי</a>
  <main id="main-content" tabindex="-1">
    <header>
      <a class="logo-link" href="https://www.tau.ac.il/" aria-label="אתר אוניברסיטת תל אביב" target="_blank" rel="noopener noreferrer">
        <img class="site-logo" src="HEB_bold.jpg" alt="לוגו אוניברסיטת תל אביב">
      </a>
      <h1>{h(site["homeTitleHe"])}</h1>
      <p class="intro">{h(site["homeIntroHe"])}</p>
      <div class="search-panel" id="search" role="search" aria-label="חיפוש בתמציות"></div>
    </header>

    <section class="section latest-section" aria-labelledby="latest-heading">
      <h2 class="section-heading" id="latest-heading">חדש באתר</h2>
      <div class="grid" aria-label="תשע התמציות האחרונות">
{latest_cards}
      </div>
    </section>

    <section class="section topics-section" aria-labelledby="topics-heading">
      <h2 class="section-heading" id="topics-heading">נושאים מרכזיים</h2>
      <div class="topic-grid" aria-label="דפי נושאים מרכזיים">
{topic_cards}
      </div>
    </section>
    <footer class="footer-links" data-pagefind-ignore>
      <a href="accessibility.html">הצהרת נגישות</a>
    </footer>
  </main>
  <script src="pagefind/pagefind-ui.js"></script>
  <script>
    window.addEventListener("DOMContentLoaded", () => {{
      window.siteSearch = new PagefindUI({{
        element: "#search",
        showSubResults: true,
        showImages: false,
        translations: {{
          placeholder: "חיפוש בתמציות",
          clear_search: "ניקוי החיפוש",
          load_more: "תוצאות נוספות",
          search_label: "חיפוש באתר",
          filters_label: "מסננים",
          zero_results: "לא נמצאו תוצאות עבור [SEARCH_TERM]",
          many_results: "[COUNT] תוצאות עבור [SEARCH_TERM]",
          one_result: "תוצאה אחת עבור [SEARCH_TERM]",
          alt_search: "לא נמצאו תוצאות עבור [SEARCH_TERM]. מוצגות תוצאות עבור [DIFFERENT_TERM]",
          search_suggestion: "לא נמצאו תוצאות עבור [SEARCH_TERM]. כדאי לנסות את [DIFFERENT_TERM]"
        }}
      }});
    }});
  </script>
  {CLOUDFLARE}
</body>
</html>
'''


TOPIC_CSS = '''    :root { color-scheme: light; --ink:#202124; --muted:#5f6368; --accent:#16555d; --accent-dark:#16404d; --line:#d9e1e3; --paper:#fff; --page:#f5f7f8; --link:#0563c1; font-family: Arial, "Noto Sans Hebrew", "Segoe UI", sans-serif; }
    * { box-sizing: border-box; }
    .skip-link { position:absolute; top:10px; right:10px; z-index:1000; padding:10px 14px; background:#fff; color:#0563c1; border:2px solid #16555d; border-radius:4px; font-weight:700; transform:translateY(-140%); transition:transform 120ms ease; }
    .skip-link:focus { transform: translateY(0); }
    body { margin:0; background:var(--page); color:var(--ink); direction:rtl; text-align:right; line-height:1.65; font-size:18px; }
    main { width:min(1120px, calc(100% - 32px)); margin:0 auto; padding:36px 0 56px; }
    header { padding:18px 0 28px; border-bottom:1px solid var(--line); }
    .logo-link { display:block; width:min(260px, 70vw); margin:0 0 20px auto; }
    .logo-link:focus-visible, .home-link:focus-visible { outline:2px solid var(--accent); outline-offset:4px; }
    .site-logo { display:block; width:100%; height:auto; margin:0; }
    .home-link { display:inline-flex; align-items:center; gap:8px; margin:0 0 18px; color:var(--link); font-weight:700; text-decoration:none; }
    .home-link:hover { text-decoration: underline; }
    .home-icon { width:19px; height:19px; flex:0 0 auto; }
    h1 { margin:0; color:var(--accent-dark); font-size:38px; line-height:1.2; }
    .intro { max-width:820px; margin:12px 0 0; color:var(--muted); font-size:19px; }
    .topic-hero { display:grid; grid-template-columns:minmax(0, 1.2fr) minmax(280px, .8fr); gap:24px; align-items:center; margin:28px 0 0; }
    .topic-hero img { display:block; width:100%; height:auto; aspect-ratio:4 / 3; object-fit:cover; border:1px solid var(--line); border-radius:8px; background:#eef3f4; }
    .topic-note { color:var(--muted); font-size:17px; }
    .grid { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:18px; margin-top:28px; }
    .item { display:flex; flex-direction:column; min-height:100%; overflow:hidden; background:var(--paper); border:1px solid var(--line); border-radius:8px; color:inherit; text-decoration:none; transition:border-color 160ms ease, transform 160ms ease; }
    .item:hover, .item:focus-visible { border-color:var(--accent); transform:translateY(-2px); outline:none; }
    .preview { display:block; width:100%; height:auto; max-width:100%; aspect-ratio:4 / 3; object-fit:cover; object-position:top center; border-bottom:1px solid var(--line); background:#eef3f4; }
    .content { display:flex; flex-direction:column; flex:1; padding:18px; }
    h2 { margin:0 0 8px; color:var(--accent); font-size:22px; line-height:1.35; }
    p { margin:0; }
    .summary { color:var(--muted); font-size:16px; }
    .authors { margin-bottom:8px; color:var(--accent-dark); font-size:15px; font-weight:700; }
    .new-badge { align-self:flex-start; margin-bottom:8px; color:#b3261e; font-size:15px; font-weight:700; line-height:1; }
    .open { margin-top:auto; padding-top:16px; color:var(--link); font-weight:700; }
    .pagination { display:flex; flex-wrap:wrap; gap:10px; margin:30px 0 0; color:var(--muted); }
    .pagination a, .pagination span { padding:4px 10px; border:1px solid var(--line); border-radius:6px; background:var(--paper); color:var(--link); font-weight:700; }
    .pagination span { color:var(--muted); }
    .footer-links { margin-top:32px; padding-top:18px; border-top:1px solid var(--line); color:var(--muted); font-size:15px; }
    .footer-links a { color:var(--link); font-weight:700; }
    a:focus-visible { outline:3px solid var(--accent); outline-offset:3px; }
    @media (max-width:980px) { .grid { grid-template-columns:repeat(2, minmax(0,1fr)); } .topic-hero { grid-template-columns:1fr; } }
    @media (max-width:700px) { .grid { grid-template-columns:1fr; } h1 { font-size:31px; } .intro { font-size:18px; } }
    @media (max-width:520px) { main { width:min(100% - 24px, 1120px); padding-top:26px; } .content { padding:16px; } }
'''


def topic_page_path(topic: dict, page_number: int) -> str:
    if page_number == 1:
        return topic["page"]
    stem = topic["page"].removesuffix(".html")
    return f"{stem}-page-{page_number}.html"


def render_topic_page(
    site: dict,
    topic: dict,
    papers: list[dict],
    latest_new_files: set[str],
    page_number: int = 1,
    total_pages: int = 1,
) -> str:
    page_path = topic_page_path(topic, page_number)
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": topic["titleHe"],
        "description": topic["descriptionHe"],
        "inLanguage": "he",
        "url": absolute(site, page_path),
        "image": absolute(site, topic["image"]),
        "isPartOf": {"@type": "WebSite", "name": site["siteNameHe"], "url": site["baseUrl"]},
        "about": topic.get("keywords", []),
        "mainEntity": {"@type": "ItemList", "itemListElement": item_list(site, papers)},
    }
    cards = "\n".join(paper_card(paper, prefix="../", show_new=paper["file"] in latest_new_files) for paper in papers)
    if total_pages > 1:
        links = []
        for index in range(1, total_pages + 1):
            label = str(index)
            if index == page_number:
                links.append(f"<span>{label}</span>")
            else:
                links.append(f'<a href="../{h(topic_page_path(topic, index))}">{label}</a>')
        pagination = f'''    <nav class="pagination" aria-label="עמודי נושא" data-pagefind-ignore>
      {" ".join(links)}
    </nav>'''
    else:
        pagination = ""
    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(topic["titleHe"])} | {h(site["siteNameHe"])}</title>
  <meta name="description" content="{h(topic["descriptionHe"])}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{h(absolute(site, page_path))}">
  <meta property="og:locale" content="he_IL">
  <meta property="og:site_name" content="{h(site["siteNameHe"])}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{h(topic["titleHe"])}">
  <meta property="og:description" content="{h(topic["descriptionHe"])}">
  <meta property="og:url" content="{h(absolute(site, page_path))}">
  <meta property="og:image" content="{h(absolute(site, topic["image"]))}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{h(topic["titleHe"])}">
  <meta name="twitter:description" content="{h(topic["descriptionHe"])}">
  <meta name="twitter:image" content="{h(absolute(site, topic["image"]))}">
  <script type="application/ld+json">
{dump_json_ld(schema)}
  </script>
  <style>
{TOPIC_CSS}  </style>
</head>
<body>
  <a class="skip-link" href="#main-content">דילוג לתוכן המרכזי</a>
  <main id="main-content" tabindex="-1" data-pagefind-body>
    <header>
      <a class="logo-link" href="https://www.tau.ac.il/" aria-label="אתר אוניברסיטת תל אביב" data-pagefind-ignore target="_blank" rel="noopener noreferrer">
        <img class="site-logo" src="../HEB_bold.jpg" alt="לוגו אוניברסיטת תל אביב">
      </a>
      <a class="home-link" href="../index.html" aria-label="חזרה לעמוד הבית" data-pagefind-ignore>{HOME_ICON}<span>לעמוד הבית</span></a>
      <h1>{h(topic["titleHe"])}</h1>
      <p class="intro">{h(topic["descriptionHe"])}</p>
      <div class="topic-hero">
        <p class="topic-note">מאמר יכול להופיע ביותר מנושא אחד כאשר הוא עוסק, למשל, גם בזכויות וגם במוסדות או גם בפופוליזם וגם בבית המשפט. בעמוד זה מופיעות {len(papers)} תמציות שמשויכות לנושא.</p>
        <img src="{h(topic_image_src(topic, site, "../"))}" alt="{h(topic["imageAltHe"])}" width="800" height="600" decoding="async" fetchpriority="high">
      </div>
    </header>
    <section class="grid" aria-label="תמציות בנושא {h(topic["titleHe"])}">
{cards}
    </section>
{pagination}
    <footer class="footer-links" data-pagefind-ignore>
      <a href="../accessibility.html">הצהרת נגישות</a>
    </footer>
  </main>
  {CLOUDFLARE}
</body>
</html>
'''


def render_sitemap(site: dict, papers: list[dict], topics: list[dict]) -> str:
    entries = [
        (site["baseUrl"], site["lastUpdated"], "weekly", "1.0"),
        (absolute(site, "accessibility.html"), site["lastUpdated"], "weekly", "0.6"),
    ]
    for topic in topics:
        entries.append((absolute(site, topic["page"]), site["lastUpdated"], "weekly", "0.9"))
    for paper in papers:
        entries.append((absolute(site, paper["file"]), paper["dateModified"], "weekly", "0.8"))
    chunks = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, changefreq, priority in entries:
        chunks.append(f'''  <url>
    <loc>{h(loc)}</loc>
    <lastmod>{h(lastmod)}</lastmod>
    <changefreq>{h(changefreq)}</changefreq>
    <priority>{h(priority)}</priority>
  </url>''')
    chunks.append("</urlset>")
    return "\n".join(chunks) + "\n"


def render_llms(site: dict, papers: list[dict], topics: list[dict]) -> str:
    lines = [
        f"# {site['siteNameHe']}",
        "",
        f"> {site['homeDescriptionHe']}",
        "",
        f"אתר עברי המרכז תמציות נגישות לקהל הרחב של מאמרים אקדמיים מאת חוקרות וחוקרים ישראלים בנושאי דמוקרטיה ליברלית, זכויות, מוסדות ושלטון החוק.",
        "",
        "## נושאים מרכזיים",
        "",
    ]
    for topic in topics:
        lines.append(f"- [{topic['titleHe']}]({absolute(site, topic['page'])}): {topic['descriptionHe']}")
    lines.extend(["", "## תוכן האתר", ""])
    for paper in papers:
        lines.append(f"- [{paper['titleHe']}]({absolute(site, paper['file'])}): {paper['summaryHe']}. מחברות/מחברים: {paper['authorsCardHe']}.")
    lines.extend(
        [
            "",
            "## קבצים שימושיים לזחלנים ולמנועי AI",
            "",
            f"- [הצהרת נגישות]({absolute(site, 'accessibility.html')})",
            f"- [מפת אתר]({absolute(site, 'sitemap.xml')})",
            f"- [מדיניות זחילה]({absolute(site, 'robots.txt')})",
            "",
            "## הערות שימוש",
            "",
            "כל עמוד תמצית כולל קישור DOI או מקור יציב למאמר האקדמי שעליו הוא מבוסס. התמציות מיועדות להסבר ציבורי בעברית ואינן מחליפות את קריאת המאמר המקורי. מאמר יכול להופיע ביותר מנושא מרכזי אחד כאשר הוא רלוונטי לכמה שאלות מחקר.",
        ]
    )
    return "\n".join(lines) + "\n"


def build() -> None:
    site, papers, topics_data, _order = load_data()
    topics = topics_data["topics"]
    papers_by_file = {paper["file"]: paper for paper in papers}
    latest_new_files = {paper["file"] for paper in papers[:3]}

    for paper in papers:
        write(ROOT / paper["file"], render_article(site, paper, topics))
    write(ROOT / "index.html", render_index(site, papers, topics))

    page_size = int(site.get("topicPageSize", 50))
    for topic in topics:
        topic_papers = [papers_by_file[file_name] for file_name in topic["articles"]]
        pages = [topic_papers[index : index + page_size] for index in range(0, len(topic_papers), page_size)] or [[]]
        for page_number, page_papers in enumerate(pages, start=1):
            write(
                ROOT / topic_page_path(topic, page_number),
                render_topic_page(site, topic, page_papers, latest_new_files, page_number, len(pages)),
            )

    write(ROOT / "sitemap.xml", render_sitemap(site, papers, topics))
    write(ROOT / "llms.txt", render_llms(site, papers, topics))
    print(f"Built {len(papers)} paper pages, {len(topics)} topic pages, index.html, sitemap.xml, and llms.txt")


if __name__ == "__main__":
    build()
