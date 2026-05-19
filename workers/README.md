# Paper Suggestion Worker

GitHub Pages is static, so the public form cannot append to `suggest_queue.csv` or enforce an IP/source limit by itself. This Cloudflare Worker is the server-side endpoint for the form.

The Worker:

- accepts `paperTitle`, `doi`, `submitterName`, and `submitterEmail`;
- validates that all fields are present;
- stores only a daily salted hash of the submitter IP, not the raw IP address;
- allows up to two accepted submissions per source per Israel calendar day;
- appends accepted rows to `suggest_queue.csv` through the GitHub Contents API.

## Deploy

Copy `wrangler.toml.example` to `wrangler.toml`, then set secrets:

```sh
cd workers
wrangler secret put GITHUB_TOKEN
wrangler secret put IP_HASH_SECRET
wrangler deploy
```

`GITHUB_TOKEN` needs permission to write repository contents. After deployment, copy the Worker URL into `_data/site.json` as `suggestPaperEndpoint`.

If this repository is public, remember that names and emails committed to `suggest_queue.csv` are visible in GitHub history even though the file is excluded from the built Jekyll site. For private handling of personal data, point `GITHUB_REPO` and `QUEUE_PATH` at a private repository and adjust the nightly automation to read that private queue.
