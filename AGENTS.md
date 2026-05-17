# Codex Agent Instructions

Read `HANDOFF.md` and `README.md` before changing this repository.

This repository is the Jekyll source for the Hebrew democracy summaries site. Do not manually edit generated HTML, `_site/`, or `pagefind/`. Shared layout changes belong in `_layouts/`, `_includes/`, `_data/site.json`, and `assets/css/site.css`.

For paper additions:

- Use `_data/paper_index.json` as the primary duplicate and ordering index.
- Add one source file per paper under `_papers/`.
- Use existing topic IDs from `_data/topics.json` unless a durable new topic is really needed.
- Add or reuse 800x600 landscape JPEG paper images and keep `image_catalog.json` current.
- Regenerate the compact index with `python3 scripts/validate_sources.py --write-index`.
- Validate with `python3 scripts/validate_sources.py` before committing.

For publishing, stage only intentional changes, commit with a clear message, push `main`, and monitor the GitHub Pages workflow. `todo.md` is tracked and should be committed when it changes.
