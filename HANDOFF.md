# Democracy Website Codex Handoff

Prepared on 2026-05-17 for continuing this project from another OpenAI Codex account.

## Project Snapshot

- GitHub repo: `https://github.com/tal69/hebrew-democracy-info.git`
- Branch: `main`
- Live site: `https://tal69.github.io/hebrew-democracy-info/`
- Source directory on this machine: `/Users/talraviv/Library/CloudStorage/Dropbox/My Mac (Tals-MacBook-Air.local)/Documents/DemocracyWebSite/github_pages_publish`
- Content source commit at handoff start: `2224e881af3e`
- Current content count: 27 paper summaries, 5 topics.
- Latest source validation at handoff: `python3 scripts/validate_sources.py` passed with 27 papers and 5 topics.

This is a Jekyll source repository. Generated pages are built by GitHub Actions and should not be maintained manually.

## What The Site Contains

The site publishes Hebrew plain-language summaries of academic papers by Israeli researchers about liberal democracy, rights, institutions, constitutionalism, rule of law, courts, civil society, democratic backsliding, equality, and related subjects.

The site is right-to-left Hebrew, uses shared Jekyll layouts, includes Pagefind search, GoatCounter analytics, Open Graph tags, JSON-LD, an accessibility page, topic pages, paper pages, a CARRD/Tel Aviv University split header logo, and a standard Hebrew disclaimer at the bottom of paper pages.

## Important Source Files

- `README.md` - user-facing source workflow and build notes.
- `AGENTS.md` - short instructions for future Codex agents.
- `Authors.MD` - optional preferred-author list for nightly scans.
- `_papers/*.md` - one paper summary per Markdown/front matter file.
- `_data/site.json` - site-level settings, including `homepageLatestCount`, `topicPageSize`, `lastUpdated`, image-version labels, and the standard disclaimer.
- `_data/topics.json` - topic taxonomy. Paper membership is read from each paper file's `topics` list.
- `_data/paper_index.json` - generated compact paper index for fast duplicate and ordering checks. Do not hand edit.
- `_layouts/` and `_includes/` - shared page templates.
- `_includes/analytics.html` - site-wide GoatCounter snippet.
- `_includes/site_logo.html` - centered split CARRD/Tel Aviv University logo.
- `assets/css/site.css` - shared styling.
- `assets/topic-icons/` - topic icons.
- `html_qa/` - paper graphics, currently expected to be 800x600 landscape JPEGs.
- `image_catalog.json` - internal metadata for image reuse and homepage-image avoidance.
- `scripts/validate_sources.py` - main validator and paper-index generator.
- `.github/workflows/pages.yml` - GitHub Pages build and deploy workflow.
- `todo.md` - user-maintained project task list; track and commit changes.

Build artifacts `_site/`, `pagefind/`, `.npm-cache/`, and local dependency folders are not committed.

## Deployment Flow

GitHub Actions is the canonical deploy path:

1. Push source changes to `main`.
2. Workflow `Build and deploy Jekyll site` runs.
3. It builds Jekyll into `_site`.
4. It runs Pagefind inside `_site`.
5. It deploys `_site` to GitHub Pages.

Useful commands:

```sh
git status --short --branch
python3 scripts/validate_sources.py
gh run list --repo tal69/hebrew-democracy-info --workflow pages.yml --limit 5
```

Local Jekyll may fail on this machine if Ruby/Bundler is not configured. Do not block normal work on local Jekyll if source validation passes and the GitHub Actions workflow succeeds.

## Adding Papers

Use this sequence for manual or automated paper additions:

1. Read `README.md`, `Authors.MD`, `_data/paper_index.json`, `_data/topics.json`, `_data/site.json`, and `image_catalog.json`.
2. Check `_data/paper_index.json` for duplicate DOI, slug, title, author, and theme.
3. If `Authors.MD` lists preferred authors, search first for recent relevant publications by those authors. Do not add an out-of-scope paper only because the author is listed.
4. Add a new `_papers/*.md` file with JSON front matter between `---` markers.
5. Give new papers larger numeric `sortKey` values than existing records, usually `YYYYMMDD0001`, `YYYYMMDD0002`, etc. The index sorts descending by `sortKey`.
6. Assign one or more existing topic IDs from `_data/topics.json`.
7. Link author names only when the author identity is certain and the link is an official academic profile or clearly maintained academic home page.
8. Make external paper and author links open in a new tab with `target="_blank"` and `rel="noopener noreferrer"` in stored HTML fields.
9. Add or reuse an 800x600 landscape JPEG in `html_qa/`.
10. Update `image_catalog.json`.
11. Run `python3 scripts/validate_sources.py --write-index`.
12. Run `python3 scripts/validate_sources.py`.
13. Commit and push source changes only.

Do not edit generated root HTML pages, `_site/`, or `pagefind/` by hand.

## Homepage Spotlight

The homepage spotlight count is controlled by `_data/site.json`:

```json
"homepageLatestCount": 6
```

The nightly automation does not need to know this count for layout. It only needs to avoid reusing images currently appearing in the newest 6 homepage cards, because repeated images at the top of the site look bad.

The first three homepage cards get high-priority image loading in the shared layout. Later cards are lazy-loaded.

## Images

Paper images should be:

- 800x600 landscape JPEG.
- Similar in style to the current better images.
- Polished editorial illustration, not crude cartoon or flat clip art.
- Warm cream and ochre tones, muted teal/deep-blue accents, Mediterranean civic architecture, dignified human figures when useful, natural light, symbolic but concrete composition.
- No text, letters, logos, flags, watermarks, UI widgets, or pasted-looking layers.

Before creating a new image, check `image_catalog.json`. Reuse an existing image if the topic fit is strong and the image is not used by any of the newest homepage cards.

## Site-Wide Features

- Search: Pagefind is generated by GitHub Actions after Jekyll builds `_site`.
- Analytics: GoatCounter snippet lives in `_includes/analytics.html`.
- Logo: `_includes/site_logo.html` uses the transparent CARRD/Tel Aviv University image. The upper part links to `https://carrdtau.sites.tau.ac.il/` in the same tab; the lower TAU part links to `https://www.tau.ac.il/` in the same tab.
- Paper footer: the full Hebrew disclaimer is stored in `_data/site.json` as `readingNoteHe`.
- Last updated: paper pages show the last-updated value from the source data.
- Accessibility: `accessibility.html` exists; `todo.md` still notes that public accessibility contact details are needed.

## Nightly Automation Handoff

The current Codex automation is local to the original account and machine. A different OpenAI Codex account will need to recreate it.

Current local automation file:

```text
/Users/talraviv/.codex/automations/daily-democracy-paper-additions/automation.toml
```

Current automation memory file:

```text
/Users/talraviv/.codex/automations/daily-democracy-paper-additions/memory.md
```

Current automation state at handoff:

- Automation name: `Daily democracy paper additions`
- Status: `PAUSED`
- Schedule: daily at 05:00 Asia/Jerusalem
- Working directory in the automation: top-level `DemocracyWebSite`, then the prompt instructs it to work in `github_pages_publish`
- Model requested: `gpt-5.5`
- Reasoning effort: `xhigh`

A ready-to-use prompt based on the current automation is copied into `AUTOMATION_PROMPT.md` for recreation in the new account. The memory file itself is not in this repo; if preserving run history matters, copy the local memory file or summarize its latest entries into the new account's automation memory.

Latest known automation run added three papers and pushed commit `2224e88`:

- Sommer, Colson, and Schmidt - judicial revolution/reconceptualized democracy.
- Navot and Goldshmidt - state deconstruction.
- Arad and Freedman - Knesset democracy framings.

The GitHub Pages workflow run for that commit succeeded.

## New Account Setup Checklist

1. Sign in to the new OpenAI Codex account.
2. Ensure the GitHub account or connector has access to `tal69/hebrew-democracy-info`.
3. Clone the repo or open the local folder:

```sh
git clone https://github.com/tal69/hebrew-democracy-info.git
cd hebrew-democracy-info
```

4. Check GitHub CLI/auth if local push and workflow monitoring are needed:

```sh
gh auth status
gh repo view tal69/hebrew-democracy-info
```

5. Validate source:

```sh
python3 scripts/validate_sources.py
```

6. Recreate the daily automation using `AUTOMATION_PROMPT.md`.
7. After the first new-account automation run, confirm:

```sh
git status --short --branch
python3 scripts/validate_sources.py
gh run list --repo tal69/hebrew-democracy-info --workflow pages.yml --limit 5
```

## Known Caveats

- The live source is the nested `github_pages_publish` directory in the local Dropbox workspace. The top-level `DemocracyWebSite` folder is not itself the publish repo.
- GitHub authentication and OpenAI/Codex authentication are separate.
- Local Jekyll can be unavailable even when GitHub Actions builds correctly.
- Dropbox-backed Git checkouts can sometimes show `.git/index.lock` issues. If this happens, inspect carefully before deleting a lock file; only remove it when no Git process is running.
- Do not commit generated `_site/`, `pagefind/`, `.npm-cache/`, or dependency folders.
- The handoff files are excluded from Jekyll output, but they are still repo files.

## Current Todo Notes

See `todo.md`. At handoff, the main remaining themes are:

- Domain under `tau.ac.il`.
- Contact/about pages and a contact mailbox.
- More search engine and AI-crawler visibility work.
- PR/search promotion and social media promotion.
- Possible Arabic translation.
- Author affiliations and author notification/opt-out workflow.
- Accessibility improvements, especially public accessibility contact details.
