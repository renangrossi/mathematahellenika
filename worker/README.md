# Magister AI — backend deployment

This folder is **not** part of the GitHub Pages site (nothing under
`worker/` is linked from any HTML page). It's the source for a
separate Cloudflare Worker that acts as a secure proxy between your
website and the Groq API — the only place your Groq API key lives.

Ported from the sibling Latin-course project's `worker/` (itself
ported from the English course's — same architecture: CORS, rate
limiting, Groq call, course-catalog grounding) — this is a **separate,
independently deployed Worker** with its own name, its own KV
namespace, and its own Classical-Greek-aware system prompt/course
catalog. It does not share state with the English or Latin courses'
Workers, and deploying one has no effect on the others.

## Why a separate deployment?

GitHub Pages only serves static files — there's no way to keep a
secret out of the browser if the AI call happened directly from your
site's JavaScript. The Worker runs on Cloudflare's servers, holds the
key there, and your site's JS only ever talks to the Worker.

## One-time setup (about 15 minutes)

### 1. Create free accounts (no credit card required for either)
- **Groq**: [console.groq.com](https://console.groq.com) → sign up → **API Keys** → Create API Key. Copy it somewhere safe. (If you already deployed the English or Latin course's Worker, you can reuse the same Groq account/key — Groq's free-tier quota is shared per-account either way, so keep that in mind when tuning `DAILY_LIMIT_PER_ANON` below, especially now split three ways.)
- **Cloudflare**: [dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up) → sign up, or reuse the account you already created for the other courses' Workers — a Cloudflare account can host multiple, independent Workers.

### 2. Install Wrangler (Cloudflare's deploy tool)
```bash
npm install -g wrangler
wrangler login
```
This opens a browser window to connect Wrangler to your Cloudflare account. Skip this if you already did it for another course's Worker — it's the same account/tool.

### 3. Create the KV namespace (used for rate-limit counters)
```bash
cd worker
wrangler kv namespace create AI_TEACHER_KV
```
This prints something like:
```
id = "abcd1234..."
```
Copy that `id` value into `wrangler.toml`, replacing `REPLACE_WITH_YOUR_KV_NAMESPACE_ID`. **Do not reuse another course's KV namespace id** — each course needs its own so their rate-limit counters (and daily quotas) stay independent.

### 4. Set your Groq API key as a secret (never committed to git)
```bash
wrangler secret put GROQ_API_KEY
```
Paste your Groq key when prompted (the same key as another course's Worker is fine, or a separate one). This stores it encrypted on Cloudflare's side — it is never written to any file in this repo.

### 5. Confirm the allowed origin
Open `worker.js` and check the top of the file:
```js
const ALLOWED_ORIGIN = "https://renangrossi.github.io";
```
This is just the scheme+host of GitHub Pages — the same value works for every repo/project page under that account, so it's already correct regardless of the final repo name this course is published under.

### 6. Deploy
```bash
wrangler deploy
```
This prints your live Worker URL, something like:
```
https://ai-teacher-el.your-subdomain.workers.dev
```
Note the worker is named `ai-teacher-el` (see `wrangler.toml`) specifically so it doesn't collide with the English (`ai-teacher`) or Latin (`ai-teacher-la`) courses' Workers if all three are deployed under the same Cloudflare account.

### 7. Point the website at your Worker
The `data-ai-endpoint` attribute is currently pre-filled with a **predicted, unverified** URL following the same naming pattern as the sibling sites (`https://ai-teacher-el.englishclasses.workers.dev` — matching `ai-teacher-la.englishclasses.workers.dev` for Latin) in **two places** — both need the REAL URL from Step 6 once you have it, since a predicted guess is not guaranteed to be your account's actual Workers subdomain:

1. `scripts/site_chrome.py` — the `<script src="{rel}assets/js/ai-teacher.js" data-ai-endpoint="...">` line in `footer()`. After editing, regenerate every generated page:
   ```bash
   python3 scripts/build_lesson.py curriculum/*/*.json
   python3 scripts/build_level_page.py --all
   python3 scripts/build_static_pages.py
   python3 scripts/build_exercise_index.py
   ```
2. Also update `SITE_BASE_URL` near the top of `worker.js` if this course ends up published under a different repo name than `mathematahellenika` (see this repo's project report for the local-folder/repo-name discrepancy noted at scaffold time) — it must match the real GitHub Pages project-site path, or every link the model shares will 404.

Commit and push as usual — the chat widget will now reach your live Worker.

## Adjusting limits

At the top of `worker.js`:
- `DAILY_LIMIT_PER_ANON` — questions per browser per day (default 20).
- `BURST_LIMIT_PER_IP` / `BURST_WINDOW_SECONDS` — short-term abuse brake (default 8 requests/60s per IP).
- `MAX_MESSAGE_LENGTH` — longest question accepted (keep in sync with the `maxlength` on the textarea rendered by `scripts/site_chrome.py`'s `footer()`, and in `index.html`/`lexicon.html`, if you change it).

## Course catalog (`course-catalog.json`)

So Magister AI can recommend a *real* lesson link instead of guessing
one, `worker.js` imports `course-catalog.json` — a list of every real
course page (the 7 gradus overview pages, the Gradus I lesson pages
and its "Te Ipsum Proba" cumulative-review page, and the site-wide
utility pages Exercitationes/Lexicon/Varia) with their real on-site
URLs. At request time the Worker does a lightweight, deterministic
keyword match between the student's message (plus recent
conversation) and this catalog, and only ever hands the model URLs
that come out of that match — the model is instructed to never output
a URL that wasn't supplied to it that turn, so it's structurally
unable to invent one.

**Hand-written for this course's first scaffold** (unlike the Latin
course's catalog, which was generated once from `assets/data/search-index.json`
and then hand-enriched) — there simply isn't enough built yet to
generate from. As more Gradus get real lessons, regenerate the base
entries from `assets/data/search-index.json` (built by
`scripts/build_exercise_index.py`) and merge in `aliases` (English/
Portuguese synonyms for topics where student phrasing won't share
words with the on-site Latin title) by hand, the way the Latin course's
own README describes.

Each entry:
```json
{ "level": "I", "title": "Spiritus et Accentus", "url": "gradus/fundamenta/spiritus-et-accentus.html", "type": "lesson", "aliases": ["breathing", "breathings", "accent", "spirito"] }
```
- `url` is site-root-relative (no leading slash, no domain) — the Worker resolves it against `SITE_BASE_URL` in `worker.js`.
- `type` is `"lesson"` (a gradus lesson page — grammar explanation AND its own exercises together), `"test"` (a gradus's "Te Ipsum Proba" cumulative review page), or `"page"` (site-wide utility pages: Exercitationes, Lexicon, Varia).
- `level` is the Roman-numeral gradus code (`"I"`–`"VII"`), or `null` for a `"page"`-type entry that isn't gradus-specific.
- Optional `aliases`: extra search terms in Latin/English/Portuguese for topics where student phrasing doesn't share words with the on-site Latin title.

After editing the catalog, redeploy with `wrangler deploy` (it's bundled into the Worker at deploy time, not fetched at runtime).

## What data is sent/stored

- The student's message and the current conversation (kept in the browser tab's memory only, lost on reload) are sent to the Worker, then to Groq, to generate a reply.
- The Worker stores nothing except two small rate-limit counters in KV: an anonymous ID (a random string generated in the browser, no personal info) plus a request count, both auto-expiring after 24 hours or 60 seconds.
- Per Groq's terms (worth re-checking at console.groq.com before relying on it long-term), free-tier requests may be logged for abuse monitoring; nothing here is guaranteed private, so the frontend also tells students not to share personal information.

## Free-tier reality check

Groq's `openai/gpt-oss-120b` free tier is roughly 1,000 requests/day
**shared across every visitor to your site**, not per-student — and if
you're using the *same* Groq account/key across all three courses
(English, Latin, Greek), that quota is shared across all of them too.
The Worker automatically falls back to the `openai/gpt-oss-20b` model
(same ~1,000 requests/day, but a separate quota pool) if the primary
model's daily quota is exhausted, so the feature keeps working at
slightly lower quality rather than going down entirely. The
per-browser daily cap (`DAILY_LIMIT_PER_ANON`) exists specifically to
stop one visitor from using up the whole day's shared quota.
