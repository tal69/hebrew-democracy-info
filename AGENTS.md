# Codex Agent Instructions

Read `HANDOFF.md` and `README.md` before changing this repository.

This repository is the Jekyll source for the Hebrew democracy summaries site. Do not manually edit generated HTML, `_site/`, or `pagefind/`. Shared layout changes belong in `_layouts/`, `_includes/`, `_data/site.json`, and `assets/css/site.css`.

For paper additions:

- Read `Authors.MD` before searching. Prioritize relevant non-duplicate papers by listed authors, but do not add out-of-scope papers only because the author is listed.
- Use `_data/paper_index.json` as the primary duplicate and ordering index.
- Nightly updates should consume `paper_queue.csv` first. Use the first 3 queued rows, remove those rows only after adding the papers, and search for a new 30-paper queue only when the queue has fewer than 3 rows at the start.
- Add one source file per paper under `_papers/`.
- Use existing topic IDs from `_data/topics.json` unless a durable new topic is really needed.
- Add or reuse 800x600 landscape JPEG paper images and keep `image_catalog.json` current.
- Keep `paper_queue.csv` in CSV format with `paper_name,authors,doi,topic` columns. The `topic` value should use existing topic IDs.
- Bump `_data/site.json` `lastUpdated` and `cacheVersion` on each successful content update so returning browsers refresh stale HTML/CSS/Pagefind assets.
- Regenerate the compact index with `python3 scripts/validate_sources.py --write-index`.
- Validate with `python3 scripts/validate_sources.py` before committing; this also checks the paper queue for duplicate DOI/title and invalid topic IDs.

For publishing, stage only intentional changes, commit with a clear message, push `main`, and monitor the GitHub Pages workflow. `todo.md` is tracked and should be committed when it changes.
