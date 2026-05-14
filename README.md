# הנגשת מידע בנושאי דמוקרטיה

Static Hebrew RTL homepage and article summaries for GitHub Pages, built with Jekyll and indexed with Pagefind.

## Source Workflow

The repository source is now Jekyll content, not hand-edited generated HTML:

- `_papers/*.md` - one Markdown/front-matter source file per paper summary.
- `_data/site.json` - site-level settings.
- `_data/topics.json` - topic taxonomy and topic metadata. Paper membership is read from each paper's `topics` list.
- `_data/paper_index.json` - compact generated index for duplicate checks and nightly updates. Regenerate it from `_papers/*.md`; do not edit it manually.
- `_layouts/` and `_includes/` - shared page templates.
- `_includes/analytics.html` - site-wide GoatCounter analytics snippet.
- `assets/css/site.css` - shared visual styling.
- `assets/topic-icons/` and `html_qa/` - topic icons and article images.
- `scripts/validate_sources.py` - source validator and paper-index generator.

Codex nightly updates should read `_data/paper_index.json` for duplicate checks, then add new papers as `_papers/*.md` files, add or reuse images, update `image_catalog.json`, regenerate `_data/paper_index.json`, and then commit/push. Update `_data/topics.json` only when adding or changing a topic. They should not edit generated HTML pages manually.

Each paper source has a stable `sortKey`. New papers should receive larger `sortKey` values, such as `YYYYMMDD01`, `YYYYMMDD02`, and `YYYYMMDD03`, so the newest papers sort first without rewriting older paper files.

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
