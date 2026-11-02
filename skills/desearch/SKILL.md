---
name: desearch
description: Choose which Desearch MCP tool to call. Use when the task needs AI search, web search, the Search API, a page as text or HTML, X posts, X trends, public YouTube (videos, transcripts, comments, channels), Reddit, Threads, TikTok, Facebook, or Instagram data, finding people and creators on X, YouTube, LinkedIn, or TikTok, or finding companies and their public contacts and leaders (or enriching domains you already have).
---

# Desearch

Pick one Desearch tool from this list. Do not call a tool that is not registered.

The host passes `DESEARCH_API_KEY` into the server. The plugin launches `npx -y desearch-mcp-server@0.8.0`, which registers 39 tools. The search, page, X, and social tools send read requests. They do not post, follow, delete, or change an account. `people-search` starts a billed background search, and `people-search-pause`, `people-search-resume`, and `people-search-cancel` pause, resume, or cancel one. `company-search` and `company-enrich` start billed background company tasks, and `company-search-pause`, `company-search-resume`, and `company-search-cancel` pause, resume, or cancel one. For People Search, follow the `desearch-people-search` skill. For Company Search and Company Enrich, follow the `desearch-company-search` skill. For YouTube, Reddit, Threads, TikTok, Facebook, and Instagram, follow the `desearch-social` skill.

## Which tool

- **AI Search** (`ai-search`): Calls Desearch AI search. Arguments: `prompt` (required). `tools` is optional and defaults to `web` and `twitter`. Allowed `tools` values are `web`, `twitter`, `arxiv`, `wikipedia`, `hackernews`, and `reddit`. `youtube` is not accepted. Older labels such as `Web Search` are accepted and rewritten to the short id. Optional: `date_filter`, `start_date`, `end_date` (UTC), `result_type` (`ONLY_LINKS` or `LINKS_WITH_FINAL_SUMMARY`), `include_domains`, `exclude_domains`, `model` (`NOVA` or `ORBIT`, default `NOVA`).
- **Search** (`search`): Web search that returns `results` with `id`, `title`, and `url`. Argument: `query` (required). Use this when a client asks for a search tool.
- **Fetch Page** (`fetch`): Read one public page as text. Argument: `id` (required, an `http` or `https` URL, usually a `search` result URL).
- **Web Search** (`web-search`): Web search. Returns titles, links, and snippets. Arguments: `query` (required), `start` (optional offset: 0, 10, 20, ...).
- **Search API** (`search-api`): Ranked web pages, each with the passage that best matches the query. Arguments: `query` (required), `mode` (optional, `fast` or `balanced`), `count` (optional, 10, 15, or 20), `start_date` and `end_date` (optional, YYYY-MM-DD), `highlights` (optional), `page_text` (optional, adds each page's full text).
- **Web Links Search** (`web-links-search`): Link search. Arguments: `prompt` (required), `tools` (optional, only `web`, default `["web"]`), `count` (optional, 10 to 200). `Web Search` is accepted and rewritten to `web`. Other sources are rejected. This tool does not accept X.
- **Extract** (`extract`): Read one public URL as text, markdown or HTML. Arguments: `url` (required), `format` (optional, `text`, `markdown` or `html`), `js` (optional), `wait` (optional milliseconds), `full_page` (optional, `text` only: every visible section of the page instead of its main content). Errors carry an `error_code`: `js_required` (retry with `js: true`), `blocked` (the site refused or showed a bot check), `page_not_found`.
- **Web Crawl** (`web-crawl`): Same arguments as Extract, on the legacy `/web/crawl` route. The SDK marks `webCrawl` deprecated in favor of `extract`. This tool stays so that route remains reachable.
- **X Search** (`x-search`): Search posts on X. Arguments: `query` (required), `count` (optional, default 20). Sort stays Top. Optional filters: `user`, `start_date`, `end_date` (YYYY-MM-DD), `lang`, `verified`, `blue_verified`, `is_quote`, `is_video`, `is_image`, `min_retweets`, `min_replies`, `min_likes`.
- **X Links Search** (`x-links-search`): Search for X post links. Arguments: `prompt` (required), `count` (optional, 10 to 200).
- **X Posts by URLs** (`x-posts-by-urls`): Posts for a list of post URLs. Argument: `urls` (required).
- **X Post by ID** (`x-post-by-id`): One post by ID. Argument: `id` (required).
- **X Posts by User** (`x-posts-by-user`): Posts by one user. Arguments: `user` (required), `query` (optional), `count` (optional, 1 to 100).
- **X User Posts** (`x-user-posts`): Posts from a username. Arguments: `username` (required), `cursor` (optional, from a previous response).
- **X User Replies** (`x-user-replies`): Posts and replies by one user. Arguments: `user` (required), `count` (optional, 1 to 100), `query` (optional).
- **X Post Replies** (`x-post-replies`): Replies to one post. Arguments: `post_id` (required), `count` (optional, 1 to 100), `query` (optional).
- **X Post Retweeters** (`x-post-retweeters`): Users who retweeted a post. Arguments: `id` (required), `cursor` (optional).
- **X Trends** (`x-trends`): Trends for a location WOEID. Arguments: `woeid` (required), `count` (optional, 30 to 100).
- **YouTube** (`youtube`): Public YouTube data. `action` (required): `search` (`query`; optional `type`, `upload_date`, `sort_by`, `duration`, `cursor`), `video` (`id`: video or Short ID or URL), `transcript` (`video_id`; optional `language`), `comments` (`video_id`; optional `order`, `cursor`), `channel` (`handle` or `UC...` channel ID), `channel_videos` (`handle`; optional `sort`, `cursor`).
- **Reddit** (`reddit`): Public Reddit data. `action` (required): `search` (`query`; optional `sort`, `timeframe`, `cursor`), `subreddit` (`name`, case-sensitive), `subreddit_posts` (`name`; optional `sort`, `timeframe`, `cursor`), `post` (`id`: post ID or URL), `comments` (`post_id`; optional `cursor`).
- **Threads** (`threads`): Public Threads data. `action` (required): `search` (`query`; optional `start_date`, `end_date`), `search_users` (`query`), `profile` (`username`), `profile_posts` (`username`), `post` (`id`: post URL or shortcode). One page each; no cursor.
- **TikTok** (`tiktok`): Public TikTok data. `action` (required): `search` (`query`; optional `count`, `sort`, `cursor`), `post` (`id`), `profile` (`username`), `profile_posts` (`username`; optional `count`, `cursor`), `comments` (`video_id`; optional `count`, `cursor`), `hashtag` (`tag`; optional `count`, `cursor`), `trending` (optional `region`, `count`).
- **Facebook** (`facebook`): Public Facebook data. `action` (required): `search` (`query`) and `hashtag` (`tag`) return Meta Ad Library ads; `post` (`id`), `profile` (`profile_id`), `profile_posts` (`profile_id`), `comments` (`post_id`). List actions take optional `count` and `cursor`.
- **Instagram** (`instagram`): Public Instagram data. `action` (required): `search` (`query`; optional `count`; no cursor), `media` (`id`), `profile` (`username`), `profile_posts` (`username`), `comments` (`shortcode` from the post URL), `hashtag` (`tag`). List actions take optional `count` and `cursor`.
- Paging for the social tools: list actions return `results`, `next_cursor`, and `next`. For the next page, call the same action with the same target and `cursor` set to `next_cursor`, unchanged. `next_cursor` is null on the last page; a cursor lasts 24 hours.
- **People Search** (`people-search`): Start a billed background search for people on `x`, `youtube`, `linkedin`, or `tiktok` who match a plain-language description. Arguments: `platform` and `query` (required), `count`, `min_score`, `exclude`, `idempotency_key`, and platform filters. See the `desearch-people-search` skill before calling it.
- **People Search Status** (`people-search-status`): Status, progress, cost, and a page of people for one task. Arguments: `task_id` (required), `cursor`, `limit`, `include_people`.
- **Pause People Search** (`people-search-pause`): Pause a task. Argument: `task_id` (required).
- **Resume People Search** (`people-search-resume`): Resume a paused task with no new charge. Argument: `task_id` (required).
- **Cancel People Search** (`people-search-cancel`): Stop a task for good; only people already delivered are billed. Argument: `task_id` (required). Cancel cannot be undone.
- **List People Search Tasks** (`people-search-tasks`): Your searches, newest first. Arguments: `platform`, `status`, `limit`, `cursor`, all optional.
- **List People Found** (`people-profiles`): Everyone your searches found on one platform, with filters. Free; it does not start a search. Arguments: `platform` (required) and optional filters.
- **Export People Found** (`people-search-export`): One search (`task_id`) or everyone found on a platform (`platform`) as CSV or JSON Lines text. Optional `format` (`csv` or `jsonl`), the `people-profiles` filters, and `max_rows` (1 to 1000, default 100). Free.
- **Company Search** (`company-search`): Start a billed background task that finds companies on the web matching a plain-language description, with each one's public emails, phones, social profiles, and leaders. Arguments: `query` (required), `count`, `min_score`, `exclude`, `countries`, `require`, `roles`, `infer_emails`, `verify_emails`, `metadata`, `idempotency_key`. See the `desearch-company-search` skill before calling it.
- **Company Enrich** (`company-enrich`): Start a billed background task that collects the same data for domains you already have, one company per domain, with no fit score. Arguments: `domains` (required, 1 to 200), `roles`, `infer_emails`, `verify_emails`, `metadata`, `idempotency_key`. See the `desearch-company-search` skill before calling it.
- **Company Search Status** (`company-search-status`): Status, progress, cost, and a page of companies for one Company Search or Company Enrich task. Arguments: `task_id` (required), `cursor`, `limit`, `include_companies`.
- **Pause Company Search** (`company-search-pause`): Pause a company task. Argument: `task_id` (required).
- **Resume Company Search** (`company-search-resume`): Resume a paused company task with no new charge. Argument: `task_id` (required).
- **Cancel Company Search** (`company-search-cancel`): Stop a company task for good; only companies already delivered are billed. Argument: `task_id` (required). Cancel cannot be undone.
- **List Company Search Tasks** (`company-search-tasks`): Your Company Search and Company Enrich tasks, newest first. Arguments: `type` (`search` or `enrich`), `status`, `limit`, `cursor`, `metadata`, all optional.

## When not to use these tools

Skip Desearch when the task is only about files in the current project, or when the text you need is already in the conversation. These tools do not browse a logged-in site, post to X or any other platform, contact the people or companies they find, or change Desearch account settings.
