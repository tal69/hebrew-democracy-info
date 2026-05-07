#!/usr/bin/env python3
"""Extract the current hand-authored HTML site into structured source data.

This is a migration helper. The ongoing workflow should edit data files and run
scripts/build_site.py rather than editing generated HTML directly.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://tal69.github.io/hebrew-democracy-info/"
PAPERS_DIR = ROOT / "data" / "papers"


def read(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def rel_url(url: str | None) -> str:
    if not url:
        return ""
    if url.startswith(BASE_URL):
        return url[len(BASE_URL) :]
    return url


def first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, flags=re.S)
    return match.group(1).strip() if match else default


def json_ld_from(html_text: str) -> dict:
    raw = first_match(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html_text,
    )
    if not raw:
        return {}
    return json.loads(raw)


def meta_content(html_text: str, attr: str, value: str) -> str:
    return html.unescape(
        first_match(
            rf'<meta\s+{attr}=["\']{re.escape(value)}["\']\s+content=["\'](.*?)["\']',
            html_text,
        )
    )


def extract_order(index_html: str) -> list[str]:
    schema = json_ld_from(index_html)
    items = schema.get("mainEntity", {}).get("itemListElement", [])
    return [rel_url(item["url"]) for item in items]


def extract_cards() -> dict[str, dict]:
    cards: dict[str, dict] = {}
    sources = [ROOT / "index.html", *sorted((ROOT / "topics").glob("*.html"))]
    for source in sources:
        text = read(source)
        for match in re.finditer(r'<a class="item" href="([^"]+)">(.*?)</a>', text, flags=re.S):
            href = match.group(1).replace("../", "")
            body = match.group(2)
            if href in cards:
                continue
            img = re.search(r'<img class="preview" src="([^"]+)" alt="([^"]*)"', body, flags=re.S)
            src = img.group(1).replace("../", "") if img else ""
            alt = html.unescape(img.group(2)) if img else ""
            if "?v=" in src:
                image_src, cache_bust = src.split("?v=", 1)
            else:
                image_src, cache_bust = src, ""
            cards[href] = {
                "titleHe": clean_text(first_match(r"<h2>(.*?)</h2>", body)),
                "authorsHe": clean_text(first_match(r'<p class="authors">(.*?)</p>', body)),
                "summaryHe": clean_text(first_match(r'<p class="summary">(.*?)</p>', body)),
                "imageSrc": image_src,
                "imageVersion": cache_bust,
                "imageAltHe": alt,
                "isNew": "new-badge" in body,
            }
    return cards


def extract_metadata(html_text: str) -> dict:
    rows = []
    for match in re.finditer(r'<div class="meta-row">\s*(.*?)\s*</div>', html_text, flags=re.S):
        row = match.group(1)
        label = clean_text(first_match(r'<span class="meta-label">(.*?)</span>', row)).rstrip(":")
        value_match = re.search(r'<(span|a) class="meta-value[^"]*"[^>]*>(.*?)</\1>', row, flags=re.S)
        value_html = value_match.group(2).strip() if value_match else ""
        href = first_match(r'href="([^"]+)"', row)
        rows.append({"labelHe": label, "valueHtml": value_html, "valueText": clean_text(value_html), "href": href})
    keyed = {row["labelHe"]: row for row in rows}
    return {
        "rows": rows,
        "paperTitle": keyed.get("מאמר", {}).get("valueText", ""),
        "authorsHtml": keyed.get("חוקרים", {}).get("valueHtml", ""),
        "authorsText": keyed.get("חוקרים", {}).get("valueText", ""),
        "journal": keyed.get("כתב עת", {}).get("valueText", ""),
        "dateText": keyed.get("תאריך", {}).get("valueText", ""),
        "doiUrl": keyed.get("DOI", {}).get("href", ""),
        "doiLabel": keyed.get("DOI", {}).get("valueText", ""),
    }


def extract_sections(html_text: str) -> list[dict]:
    sections = []
    for match in re.finditer(r"<section>\s*<h2>(.*?)</h2>(.*?)</section>", html_text, flags=re.S):
        body = match.group(2)
        paragraphs = [p.strip() for p in re.findall(r"<p>(.*?)</p>", body, flags=re.S)]
        sections.append({"headingHe": clean_text(match.group(1)), "paragraphsHtml": paragraphs})
    return sections


def build_topic_lookup(topics: list[dict]) -> dict[str, list[str]]:
    lookup: dict[str, list[str]] = {}
    for topic in topics:
        for article in topic["articles"]:
            lookup.setdefault(article, []).append(topic["id"])
    return lookup


def extract_papers() -> None:
    topics_data = json.loads(read(ROOT / "topics.json"))
    topics = topics_data["topics"]
    topic_lookup = build_topic_lookup(topics)
    index_html = read(ROOT / "index.html")
    order = extract_order(index_html)
    cards = extract_cards()

    site = {
        "version": 1,
        "baseUrl": BASE_URL,
        "siteNameHe": "הנגשת מידע בנושאי דמוקרטיה",
        "homeTitleHe": clean_text(first_match(r"<h1>(.*?)</h1>", index_html)),
        "homeDescriptionHe": meta_content(index_html, "name", "description"),
        "homeIntroHe": clean_text(first_match(r'<p class="intro">(.*?)</p>', index_html)),
        "homepageLatestCount": topics_data.get("homepageLatestCount", 9),
        "topicPageSize": 50,
        "lastUpdated": topics_data.get("lastUpdated", ""),
        "topicImageVersion": "20260507-topic-icons",
        "paperImageVersion": "800x600-landscape",
    }
    write_json(ROOT / "data" / "site.json", site)
    write_json(ROOT / "data" / "paper_order.json", order)

    article_files = sorted(ROOT.glob("democracy_*_summary_he.html"))
    missing_order = [path.name for path in article_files if path.name not in order]
    if missing_order:
        raise RuntimeError(f"Article pages missing from index order: {missing_order}")

    for position, file_name in enumerate(order, start=1):
        path = ROOT / file_name
        text = read(path)
        schema = json_ld_from(text)
        metadata = extract_metadata(text)
        based_on = schema.get("isBasedOn", {})
        card = cards.get(file_name, {})
        last_updated_he = clean_text(first_match(r'<p class="last-updated"[^>]*>(.*?)</p>', text))
        if last_updated_he.startswith("עודכן לאחרונה:"):
            last_updated_he = last_updated_he.split(":", 1)[1].strip()
        paper = {
            "version": 1,
            "file": file_name,
            "slug": Path(file_name).stem,
            "order": position,
            "titleHe": clean_text(first_match(r"<h1>(.*?)</h1>", text)) or schema.get("headline", ""),
            "subtitleHe": clean_text(first_match(r'<p class="subtitle">(.*?)</p>', text)),
            "descriptionHe": schema.get("description", ""),
            "summaryHe": card.get("summaryHe") or schema.get("description", ""),
            "authorsCardHe": card.get("authorsHe") or metadata["authorsText"],
            "paperTitle": based_on.get("name") or metadata["paperTitle"],
            "authorsHtml": metadata["authorsHtml"],
            "journal": based_on.get("isPartOf", {}).get("name") or metadata["journal"],
            "dateText": metadata["dateText"],
            "doiUrl": based_on.get("url") or metadata["doiUrl"],
            "doiLabel": metadata["doiLabel"] or based_on.get("url") or based_on.get("identifier", ""),
            "authors": schema.get("author", []),
            "sourceAuthors": based_on.get("author", []),
            "topics": topic_lookup.get(file_name, []),
            "keywords": schema.get("about", []),
            "image": {
                "src": card.get("imageSrc") or rel_url(schema.get("image", "")),
                "version": card.get("imageVersion") or "800x600-landscape",
                "altHe": card.get("imageAltHe", ""),
            },
            "dateModified": schema.get("dateModified", ""),
            "lastUpdatedHe": last_updated_he,
            "oneLinerHtml": first_match(r'<p class="one-liner">(.*?)</p>', text),
            "sections": extract_sections(text),
        }
        write_json(PAPERS_DIR / f"{Path(file_name).stem}.json", paper)

    print(f"Extracted {len(order)} papers into {PAPERS_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    extract_papers()
