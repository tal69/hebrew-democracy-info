# הנגשת מידע בנושאי דמוקרטיה

Static Hebrew RTL homepage and article summaries for GitHub Pages.

## Generated Site Workflow

The public HTML is generated from structured source data:

- `data/site.json` - site-level settings.
- `data/paper_order.json` - global paper order, newest first.
- `data/papers/*.json` - one structured record per paper summary.
- `topics.json` - topic taxonomy and article membership.
- `scripts/build_site.py` - generates article pages, topic pages, `index.html`, `sitemap.xml`, and `llms.txt`.

To rebuild the site after changing paper or topic data:

```sh
python3 scripts/build_site.py
npm_config_cache="$PWD/.npm-cache" npx -y pagefind --site . --output-subdir pagefind
rm -rf .npm-cache
```

`scripts/extract_site_data.py` is a one-time migration helper that extracted the original hand-edited HTML into `data/`.
