# הנגשת מידע בנושאי דמוקרטיה

Static Hebrew RTL homepage and article summaries for GitHub Pages, built with Jekyll and indexed with Pagefind.

For transferring this project to another Codex/OpenAI account, start with `HANDOFF.md` and `AGENTS.md`.

## Source Workflow

The repository source is now Jekyll content, not hand-edited generated HTML:

- `_papers/*.md` - one Markdown/front-matter source file per paper summary.
- `Authors.MD` - optional preferred-author list for the nightly scan. Add author names, affiliations, public email addresses, ORCIDs, official profile URLs, or search notes there when new publications by specific researchers should be prioritized.
- `_data/site.json` - site-level settings.
- `_data/topics.json` - topic taxonomy and topic metadata. Paper membership is read from each paper's `topics` list.
- `_data/paper_index.json` - compact generated index for duplicate checks and nightly updates. Regenerate it from `_papers/*.md`; do not edit it manually.
- `_layouts/` and `_includes/` - shared page templates.
- `_includes/analytics.html` - site-wide GoatCounter analytics snippet.
- `assets/css/site.css` - shared visual styling.
- `assets/topic-icons/` and `html_qa/` - topic icons and article images.
- `scripts/validate_sources.py` - source validator and paper-index generator.

Codex nightly updates should read `Authors.MD` first, then use `_data/paper_index.json` for duplicate checks. If `Authors.MD` lists preferred authors, the scan should first look for recent, relevant, non-duplicate publications by those authors and prioritize them over equally suitable papers by unlisted authors. A listed author is only a priority signal; every added paper must still fit the site's subject scope and pass the same source-quality checks.

After selecting papers, Codex nightly updates should add new papers as `_papers/*.md` files, add or reuse images, update `image_catalog.json`, regenerate `_data/paper_index.json`, and then commit/push. Update `_data/topics.json` only when adding or changing a topic. They should not edit generated HTML pages manually.

Each paper source has a stable `sortKey`. New papers should receive larger `sortKey` values, such as `YYYYMMDD0001`, `YYYYMMDD0002`, and `YYYYMMDD0003`, so the newest papers sort first without rewriting older paper files.

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

The generated `_site/` directory and `pagefind/` output are build artifacts and are not committed.
