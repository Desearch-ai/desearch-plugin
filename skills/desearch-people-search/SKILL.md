---
name: desearch-people-search
description: Find people and creators on X, YouTube, LinkedIn, or TikTok who match a plain-language description with the Desearch People Search MCP tools. Use when the user asks for a list of people, creators, prospects, or influencers. Starting a search is billed and runs in the background for 1 to 5 minutes.
---

# Desearch People Search

People Search returns people, not posts. Describe who you want in plain language, for example "Skincare creators who review sunscreen". Desearch searches public posts, videos, and profiles on one platform, reads each matching profile, and scores how well each person fits. Each person comes with a fit score, why they matched, their audience, and public contacts and links. Public data only.

The plugin launches `npx -y desearch-mcp-server@0.2.4`, which registers the five tools below. For posts that match a keyword, use `x-search` or `ai-search` instead.

## Billing

`people-search` is the only billed People Search tool. It reserves `count` people at the platform's price (`reserved_cost_usd` in the response). When the search ends the user pays only for the qualified people it delivered, with a minimum per search that finds anyone. The rest of the reservation is returned automatically. A search that finds no one is free.

| Platform | Finds | Price | Minimum billed per search that finds anyone |
|----------|-------|-------|---------------------------------------------|
| `x` | X profiles | $0.04 per profile | 5 profiles |
| `youtube` | YouTube creators | $0.05 per creator | 3 creators |
| `linkedin` | LinkedIn members | $0.05 per profile | 2 profiles |
| `tiktok` | TikTok creators | $0.05 per creator | 2 creators |

Status, results, task control, the task list, and the profiles library are free. The task's `reserved_cost_usd` and `final_cost_usd` are the amounts that count.

## Workflow

1. **Check what the user already has.** Call `people-profiles` for the platform (with `q` or filters) when the user may have searched for these people before. It is free and does not start a search.
2. **Confirm before spending.** Tell the user the platform, `count`, and the maximum reservation (`count` times the price above). Call `people-search` only when the user asks for a new search.
3. **Start once.** Call `people-search` one time with a new `idempotency_key` (for example a UUID). If the call fails or times out, retry with the same `idempotency_key`; the API returns the first task instead of starting and charging a second search. Keep the returned `task_id`.
4. **Poll.** The search usually takes 1 to 5 minutes. Call `people-search-status` with the `task_id` every 15 to 30 seconds. People appear while it runs. Pass the returned `next_cursor` as `cursor` to get only the people found since the previous call. Each response has a `next` hint that says what to do.
5. **Finish.** The search is done when `done` is true (`status` is `completed`, `partial`, `failed`, `cancelled`, or `expired`) and `has_more` is false. Report `final_cost_usd` with the results.

## Which tool

- **People Search** (`people-search`, billed): Start a background search. Arguments: `platform` (required: `x`, `youtube`, `linkedin`, `tiktok`), `query` (required, 3 to 1000 characters), `count` (optional, 5 to 200, API default 25), `min_score` (optional, 0 to 100), `exclude` (optional handles to leave out), `idempotency_key` (optional, reuse it on a retry). Platform filters are top-level arguments, and a filter that does not apply to the platform is rejected before the billed call:
  - `x`: `min_followers`, `max_followers`, `verified_only`, `countries`, `keywords`, `exclude_keywords`
  - `youtube`: `min_subscribers`, `max_subscribers`, `countries`, `require_contact`, `keywords`, `exclude_keywords`
  - `linkedin`: `min_followers`, `max_followers`, `countries`, `keywords`, `exclude_keywords`
  - `tiktok`: `min_followers`, `max_followers`, `require_contact`, `keywords`, `exclude_keywords`
- **People Search Status** (`people-search-status`): Status, stage, progress, cost, and a page of people for one task. Arguments: `task_id` (required), `cursor` (optional, the previous `next_cursor`), `limit` (optional, 1 to 100, default 25), `include_people` (optional, `false` reads only status and cost).
- **Control People Search** (`people-search-control`): Arguments: `task_id` and `action` (required: `pause`, `resume`, `cancel`). Pause lets a running search finish its current batch first; a search paused for more than 7 days is cancelled. Resume is not charged again. Cancel cannot be undone; the user pays only for the people already delivered.
- **List People Search Tasks** (`people-search-tasks`): The user's searches, newest first. Arguments: `platform`, `status` (list, for example `["running", "paused"]`), `limit` (1 to 100), `cursor`, all optional. A new search is refused with 429 while too many are queued, running, or paused.
- **List People Found** (`people-profiles`): Everyone the user's searches found on one platform, one entry per person, with the search that found them (`found_by`). Arguments: `platform` (required), `q`, `sort` (`score`, `recent`, `audience`), `limit` (1 to 200), `cursor`, `has` (list of `email`, `website`, `x`, `linkedin`, `instagram`, `youtube`, `tiktok`), `min_audience`, `max_audience`, `min_score`, `location`, `verified` (X and TikTok only). People from searches that ended more than 30 days ago are left out.

## Results

Each person has `name`, `handle`, `url`, `platform`, `audience` (followers, or subscribers on YouTube), `location`, `score` (0 to 100), `why` they matched, `reasons`, public `contacts` and `links`, and an `evidence_url`. LinkedIn people also have `headline` and `company`; X and TikTok people have `verified`. A missing field means the platform did not report it, not zero.

The MCP tools do not export files. To download a task as CSV or JSON Lines, use the Desearch Console or `GET /desearch/people/tasks/{task_id}/export?format=csv` on the API. Results stay available for 30 days after a search ends.

## When not to use these tools

Do not start a People Search for a single known account; use the X tools or `extract` on the profile URL. Do not start one to answer a question about posts or topics. These tools do not contact the people they find, post anything, or change Desearch account settings.
