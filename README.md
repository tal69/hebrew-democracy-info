# הנגשת מידע בנושאי דמוקרטיה

Static Hebrew RTL homepage and article summaries for GitHub Pages, built with Jekyll and indexed with Pagefind.

For transferring this project to another Codex/OpenAI account, start with `HANDOFF.md` and `AGENTS.md`.

## Source Workflow

The repository source is now Jekyll content, not hand-edited generated HTML:

- `_papers/*.md` - one Markdown/front-matter source file per paper summary.
- `Authors.MD` - optional preferred-author list for the nightly scan. Add author names, affiliations, public email addresses, ORCIDs, official profile URLs, or search notes there when new publications by specific researchers should be prioritized.
- `paper_queue.csv` - editable nightly queue of upcoming papers. It uses `paper_name,authors,doi,topic` columns; the nightly automation consumes the first 3 rows and removes them after the corresponding paper pages are added.
- `_data/site.json` - site-level settings.
- `_data/topics.json` - topic taxonomy and topic metadata. Paper membership is read from each paper's `topics` list.
- `_data/paper_index.json` - compact generated index for duplicate checks and nightly updates. Regenerate it from `_papers/*.md`; do not edit it manually.
- `_layouts/` and `_includes/` - shared page templates.
- `_includes/analytics.html` - site-wide GoatCounter analytics snippet.
- `assets/css/site.css` - shared visual styling.
- `assets/topic-icons/` and `html_qa/` - topic icons and article images.
- `scripts/validate_sources.py` - source validator and paper-index generator.

Codex nightly updates should read `paper_queue.csv` first, then use `_data/paper_index.json` for duplicate checks. If the queue has at least 3 rows, the nightly job should not do a broad discovery scan; it should use the first 3 queued papers, add the paper pages, then remove those consumed rows from the CSV in the same commit. If the queue has fewer than 3 rows at the start, Codex should prepare the next 30 relevant non-duplicate queued papers using the same criteria, with `Authors.MD` as a priority signal, before consuming the first 3 rows.

After selecting papers, Codex nightly updates should add new papers as `_papers/*.md` files, add or reuse images, update `image_catalog.json`, update `paper_queue.csv`, bump `_data/site.json` `lastUpdated` and `cacheVersion`, regenerate `_data/paper_index.json`, and then commit/push. Update `_data/topics.json` only when adding or changing a topic. They should not edit generated HTML pages manually.

Each paper source has a stable `sortKey`. New papers should receive larger `sortKey` values, such as `YYYYMMDD0001`, `YYYYMMDD0002`, and `YYYYMMDD0003`, so the newest papers sort first without rewriting older paper files.

The shared head includes a cache-refresh check against `site-version.json`. When deployed `cacheVersion` differs from the version in a user's cached page, the browser reloads that page once with a `site_version` query parameter. Use a new `cacheVersion` value for every content deploy, for example `2026-05-20-nightly`.

Paper pages distinguish creation from later edits. `datePublished` is the date the page was first created on this site and should not change later; `dateModified` and `lastUpdatedHe` describe the latest edit/update. The red `חדש!` badge is creation-date based, not position-based: `_data/site.json` `newBadgeDays` controls the window, and cards show the badge only when `datePublished` falls within that many calendar days of the build date.

## Summary Writing Guidance

New paper summaries should follow the admin GEO brief: no model preamble or sign-off; a clear H1-style `titleHe` and H3-style `subtitleHe`; organized metadata for authors, venue, date, volume/issue when available, and DOI/source link; a deeper analytical summary that foregrounds the paper's democratic-liberal, rights, legal, institutional, social, or economic implications; only verified numbers/statistics from the paper or source metadata; 2-3 short translated direct quotes only when source text is available and the quote is important; and at least 10 FAQ-style question/answer sections using realistic search or AI-chat questions.

## Build and Deploy

GitHub Actions builds and deploys the site:

1. `bundle exec jekyll build`
2. `npx -y pagefind --site _site --output-subdir pagefind`
3. upload `_site` to GitHub Pages

For local testing:

```sh
bundle install
bundle exec jekyll build
npm_config_cache="$PWD/.npm-cache" npx -y pagefind --site _site --output-subdir pagefind
rm -rf .npm-cache
```

Use a Ruby version compatible with the `github-pages` gem for local builds. The GitHub Actions workflow is the canonical deployment build.

## Source Validation

Regenerate the compact paper index after changing `_papers/*.md`:

```sh
python3 scripts/validate_sources.py --write-index
```

Check source consistency before committing:

```sh
python3 scripts/validate_sources.py
```

This also checks `paper_queue.csv` for duplicate queued titles/DOIs, queue entries already present on the site, and invalid topic IDs. The generated `_site/` directory and `pagefind/` output are build artifacts and are not committed.
