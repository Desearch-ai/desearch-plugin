---
name: desearch-people-search
description: Find people and creators on X, YouTube, LinkedIn, or TikTok who match a plain-language description with the Desearch People Search MCP tools. Use when the user asks for a list of people, creators, prospects, or influencers, or to export people already found as CSV or JSON Lines. Starting a search is billed and runs in the background for 1 to 5 minutes.
---

# Desearch People Search

People Search returns people, not posts. Describe who you want in plain language, for example "Skincare creators who review sunscreen". Desearch searches public posts, videos, and profiles on one platform, reads each matching profile, and scores how well each person fits. Each person comes with a fit score, why they matched, their audience, and public contacts and links. Public data only.

The plugin launches `npx -y desearch-mcp-server@0.4.0`, which registers the eight tools below. For posts that match a keyword, use `x-search` or `ai-search` instead.

## Billing

`people-search` is the only billed People Search tool. It reserves `count` people at the platform's price (`reserved_cost_usd` in the response). When the search ends the user pays only for the qualified people it delivered, with a minimum per search that finds anyone. The rest of the reservation is returned automatically. A search that finds no one is free.

| Platform | Finds | Price | Minimum billed per search that finds anyone |
|----------|-------|-------|---------------------------------------------|
| `x` | X profiles | $0.04 per profile | 5 profiles |
| `youtube` | YouTube creators | $0.05 per creator | 3 creators |
| `linkedin` | LinkedIn members | $0.05 per profile | 2 profiles |
| `tiktok` | TikTok creators | $0.05 per creator | 2 creators |

Status, results, pause, resume, cancel, the task list, the profiles library, and export are free. The task's `reserved_cost_usd` and `final_cost_usd` are the amounts that count.

## Workflow

1. **Check what the user already has.** Call `people-profiles` for the platform (with `q` or filters) when the user may have searched for these people before. It is free and does not start a search.
2. **Confirm before spending.** Tell the user the platform, `count`, and the maximum reservation (`count` times the price above). Call `people-search` only when the user asks for a new search.
3. **Start once.** Call `people-search` one time with a new `idempotency_key` (for example a UUID). If the call fails or times out, retry with the same `idempotency_key`; the API returns the first task instead of starting and charging a second search. Keep the returned `task_id`.
4. **Poll.** The search usually takes 1 to 5 minutes. Call `people-search-status` with the `task_id` every 15 to 30 seconds. People appear while it runs. Pass the returned `next_cursor` as `cursor` to get only the people found since the previous call. Each response has a `next` hint that says what to do.
5. **Finish.** The search is done when `done` is true (`status` is `completed`, `partial`, `failed`, `cancelled`, or `expired`) and `has_more` is false. Report `final_cost_usd` with the results.
6. **Export when asked.** If the user wants a file, call `people-search-export` with the `task_id` (or with `platform` for everyone found there). It is free.

## Which tool

- **People Search** (`people-search`, billed): Start a background search. Arguments: `platform` (required: `x`, `youtube`, `linkedin`, `tiktok`), `query` (required, 3 to 1000 characters), `count` (optional, 5 to 200, API default 25), `min_score` (optional, 0 to 100), `exclude` (optional handles to leave out), `metadata` (optional labels such as `{"campaign": "q4-outbound"}`: up to 10 keys of a-z, 0-9, `_`, `.`, `-`, string values up to 200 characters; returned on the task), `idempotency_key` (optional, reuse it on a retry). Platform filters are top-level arguments, and a filter that does not apply to the platform is rejected before the billed call:
  - `x`: `min_followers`, `max_followers`, `verified_only`, `countries`, `keywords`, `exclude_keywords`
  - `youtube`: `min_subscribers`, `max_subscribers`, `countries`, `require_contact`, `keywords`, `exclude_keywords`
  - `linkedin`: `min_followers`, `max_followers`, `countries`, `keywords`, `exclude_keywords`
  - `tiktok`: `min_followers`, `max_followers`, `require_contact`, `keywords`, `exclude_keywords`
- **People Search Status** (`people-search-status`): Status, stage, progress, cost, and a page of people for one task. Arguments: `task_id` (required), `cursor` (optional, the previous `next_cursor`), `limit` (optional, 1 to 100, default 25), `include_people` (optional, `false` reads only status and cost).
- **Pause People Search** (`people-search-pause`): Pause a task. Argument: `task_id` (required). A queued search pauses at once; a running one finishes its current batch first. No data is lost and billing does not change. A search paused for more than 7 days is cancelled by the API and can no longer be resumed.
- **Resume People Search** (`people-search-resume`): Resume a paused task from where it stopped, with no new charge. Argument: `task_id` (required). Works only on a paused search within 7 days of pausing (409 otherwise).
- **Cancel People Search** (`people-search-cancel`): Stop a task for good. Argument: `task_id` (required). The user pays only for the people it already delivered; the rest of the reservation is returned. Cancel cannot be undone.
- **List People Search Tasks** (`people-search-tasks`): The user's searches, newest first. Arguments: `platform`, `status` (list, for example `["running", "paused"]`), `limit` (1 to 100), `cursor`, `metadata` (up to 3 labels a task must have, exact match), all optional. A new search is refused with 429 while too many are queued, running, or paused.
- **List People Found** (`people-profiles`): Everyone the user's searches found on one platform, one entry per person, with the search that found them (`found_by`). Arguments: `platform` (required), `q`, `sort` (`score`, `recent`, `audience`), `limit` (1 to 200), `cursor`, `has` (list of `email`, `website`, `x`, `linkedin`, `instagram`, `youtube`, `tiktok`), `min_audience`, `max_audience`, `min_score`, `location`, `verified` (X and TikTok only). People from searches that ended more than 30 days ago are left out.
- **Export People Found** (`people-search-export`): The people found as CSV or JSON Lines text. Free; it runs no new search. Arguments: `task_id` (export one search) or `platform` without `task_id` (export everyone found on that platform), `format` (`csv` default, or `jsonl`), the filters `has`, `min_audience`, `max_audience`, `min_score`, `location`, `verified`, plus `q` and `sort` (platform export only), and `max_rows` (1 to 1000, default 100).

## Results

Each person has `name`, `handle`, `url`, `platform`, `audience` (followers, or subscribers on YouTube), `location`, `score` (0 to 100), `why` they matched, `reasons`, public `contacts` and `links`, and an `evidence_url`. LinkedIn people also have `headline` and `company`; X and TikTok people have `verified`. A missing field means the platform did not report it, not zero.

`people-search-export` replies with a note (rows in the file, rows shown, rows cut and why, and the API URL for the whole file), then the file text cut at a row boundary to `max_rows` rows and 50,000 characters. CSV keeps its header row. For a file larger than that, give the user the API URL from the note (`GET /desearch/people/tasks/{task_id}/export` for one search, `GET /desearch/people/profiles/export` for a platform, called with their API key) or point them to the Desearch Console. Results stay available for 30 days after a search ends.

## When not to use these tools

Do not start a People Search for a single known account; use the X tools or `extract` on the profile URL. Do not start one to answer a question about posts or topics. These tools do not contact the people they find, post anything, or change Desearch account settings.
