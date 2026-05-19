# Daily Democracy Paper Additions Automation Prompt

Use this prompt when recreating the nightly Codex automation in another OpenAI account.

Recommended schedule: daily at 04:00 Asia/Jerusalem.

Recommended working directory: the live repository root, for example `/Users/talraviv/Documents/DemocracyWebSite/github_pages_publish`.

Recommended execution environment: `local`, so failed runs leave recoverable edits in the normal checkout.

```text
Execute the nightly democracy website update mission from the live Jekyll repository.

The nightly run is queue-first. Read `paper_queue.csv`, `_data/paper_index.json`, `_data/topics.json`, `_data/site.json`, `image_catalog.json`, `Authors.MD`, `README.md`, and `AGENTS.md`. The queue CSV columns are `paper_name,authors,doi,topic`; `topic` is the primary existing topic ID. If the queue has at least 3 rows at the start, do not run a broad paper-discovery search. Use the first 3 queued papers, add Hebrew public-facing summaries for them, and remove exactly those consumed rows from `paper_queue.csv` in the same commit.

If `paper_queue.csv` has fewer than 3 rows at the start, first prepare the next 30 relevant non-duplicate queue rows using the same criteria: academic papers by Israeli researchers with a liberal-democracy, rights, institutions, constitutionalism, rule-of-law, democratic-backsliding, equality, minority-rights, courts, civil-society, public-opinion, polarization, or related focus. Use `Authors.MD` only as a priority signal; do not queue an out-of-scope paper just because an author is listed there. Avoid papers already present in `_data/paper_index.json` and avoid duplicate DOI/title entries inside the queue. Prefer DOI URLs or stable SSRN/publisher URLs. After replenishing the queue, consume the first 3 rows.

Do not ask the user for confirmation for normal nightly actions. Proceed autonomously with source edits, queue edits, validation, commit, push, and workflow checks. If a command genuinely requires interactive credentials or a blocked permission, stop and report the exact blocker instead of waiting silently.

At the start, run `git status --short --branch`. This automation runs in the user's normal local checkout, so unrelated local edits may exist. Do not overwrite or stage unrelated files. Stage only intentional nightly files: new `_papers/*.md`, `_data/paper_index.json`, `_data/site.json` when the paper count/date changes, `image_catalog.json`, new or reused image metadata/assets under `html_qa/`, and `paper_queue.csv`. If there are unfinished related nightly changes from a previous failed run, validate and complete those changes instead of creating duplicate papers.

For each selected queued paper, use the DOI/publisher/SSRN page and reliable public metadata to create one Markdown source file under `_papers/` with JSON front matter between `---` markers. Use existing paper files only as schema examples when needed. Include at least: `layout: "paper"`, `title`, `titleHe`, `descriptionHe`, `summaryHe`, `authorsCardHe`, `authorsHtml`, `paperTitle`, `journal`, `dateText`, `doiUrl` when available, `authors`, `sourceAuthors`, `topics`, `keywords`, `image`, `dateModified`, `lastUpdatedHe`, `oneLinerHtml`, `sections`, `slug`, `file`, `permalink`, `paper_url`, and a numeric `sortKey`.

Use `_data/paper_index.json` as the duplicate and ordering index. New papers must receive larger `sortKey` values than existing papers, such as `YYYYMMDD0001`, `YYYYMMDD0002`, and `YYYYMMDD0003`, ordered so the newest three appear first. Do not rewrite older `_papers/*.md` files merely to renumber or reorder them.

Assign every new paper to one or more existing topic IDs from `_data/topics.json`. Start from the queued primary topic, but add additional existing topics when substantively appropriate. Add or edit `_data/topics.json` only when a new durable central topic is genuinely needed.

Before generating a new paper graphic, consult `image_catalog.json`; reuse an existing 800x600 JPEG when the topic fit is strong and the image is not used by the newest 6 homepage cards listed in `_data/paper_index.json`. If no suitable reusable image exists, create a new 800x600 landscape JPEG in `html_qa/` and add it to `image_catalog.json`. Paper graphics must match the site's existing polished editorial illustration style and must not contain text, letters, logos, flags, watermarks, UI widgets, or pasted-looking layers.

Apply the GEO/AI-crawler writing guide when creating paper data: use descriptive search-friendly Hebrew titles and headings; put a clear 2-3 sentence conclusion near the top that starts from the finding; include explicit visible credit with authors, institutional affiliation when confidently verified, journal, year/date, and active DOI; repeat full author names and key institutions/concepts enough that quoted passages remain attributable; make each paragraph's first sentence a standalone thesis sentence; keep paragraphs short; keep DOI/source links active; and include FAQ-style question headings/answers when the format allows.

On each new article record, link author names in the article-page metadata row to official academic home pages only when you are certain about the researcher's identity. Prefer official institutional profiles or clearly maintained academic personal home pages; leave a name unlinked when uncertain. Do not add author links on the home page cards. When adding author-page links, also add the same URL to the corresponding JSON-LD author object in the paper data. Make every external HTML link in stored HTML fields open in a new tab by adding `target="_blank"` and `rel="noopener noreferrer"`.

After source changes, run `python3 scripts/validate_sources.py --write-index`, then run `python3 scripts/validate_sources.py`. The validator checks paper sources, the generated paper index, and `paper_queue.csv`. If local Jekyll is available, run `bundle exec jekyll build`; if it is unavailable because of the machine Ruby environment, note that and rely on the GitHub Actions workflow after source validation.

Commit the source changes with a clear message and push to `main` using local shell git commands. In a normal local checkout use `git push origin main`; if the checkout is ever detached, use `git push origin HEAD:main`. After pushing, verify that `origin/main` advanced with `git ls-remote origin refs/heads/main`, and when possible check/report the GitHub Pages workflow result. If fewer than 3 suitable papers can be added from the queue, add only the suitable papers and clearly report why.
```
