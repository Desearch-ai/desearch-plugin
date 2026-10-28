---
name: desearch
description: Choose which Desearch MCP tool to call. Use when the task needs AI search, web search, a page as text or HTML, X posts, X trends, finding people and creators on X, YouTube, LinkedIn, or TikTok, or finding companies and their public contacts and leaders (or enriching domains you already have).
---

# Desearch

Pick one Desearch tool from this list. Do not call a tool that is not registered.

The host passes `DESEARCH_API_KEY` into the server. The plugin launches `npx -y desearch-mcp-server@0.4.0`. The search, page, and X tools send read requests. They do not post, follow, delete, or change an account. `people-search` starts a billed background search, and `people-search-pause`, `people-search-resume`, and `people-search-cancel` pause, resume, or cancel one. `company-search` and `company-enrich` start billed background company tasks, and `company-search-pause`, `company-search-resume`, and `company-search-cancel` pause, resume, or cancel one. For People Search, follow the `desearch-people-search` skill. For Company Search and Company Enrich, follow the `desearch-company-search` skill.

## Which tool

- **AI Search** (`ai-search`): Calls Desearch AI search. Arguments: `prompt` (required). `tools` is optional and defaults to `web` and `twitter`. Allowed `tools` values are `web`, `twitter`, `arxiv`, `wikipedia`, `hackernews`, and `reddit`. `youtube` is not accepted. Older labels such as `Web Search` are accepted and rewritten to the short id. Optional: `date_filter`, `start_date`, `end_date` (UTC), `result_type` (`ONLY_LINKS` or `LINKS_WITH_FINAL_SUMMARY`), `include_domains`, `exclude_domains`, `model` (`NOVA` or `ORBIT`, default `NOVA`).
- **Search** (`search`): Web search that returns `results` with `id`, `title`, and `url`. Argument: `query` (required). Use this when a client asks for a search tool.
- **Fetch Page** (`fetch`): Read one public page as text. Argument: `id` (required, an `http` or `https` URL, usually a `search` result URL).
- **Web Search** (`web-search`): Web search. Returns titles, links, and snippets. Arguments: `query` (required), `start` (optional offset: 0, 10, 20, ...).
- **Web Links Search** (`web-links-search`): Link search. Arguments: `prompt` (required), `tools` (optional, only `web`, default `["web"]`), `count` (optional, 10 to 200). `Web Search` is accepted and rewritten to `web`. Other sources are rejected. This tool does not accept X.
- **Extract** (`extract`): Read one public URL as text or HTML. Arguments: `url` (required), `format` (optional, `html` or `text`), `js` (optional), `wait` (optional milliseconds).
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
- **People Search** (`people-search`): Start a billed background search for people on `x`, `youtube`, `linkedin`, or `tiktok` who match a plain-language description. Arguments: `platform` and `query` (required), `count`, `min_score`, `exclude`, `idempotency_key`, and platform filters. See the `desearch-people-search` skill before calling it.
- **People Search Status** (`people-search-status`): Status, progress, cost, and a page of people for one task. Arguments: `task_id` (required), `cursor`, `limit`, `include_people`.
- **Pause People Search** (`people-search-pause`): Pause a task. Argument: `task_id` (required).
- **Resume People Search** (`people-search-resume`): Resume a paused task with no new charge. Argument: `task_id` (required).
- **Cancel People Search** (`people-search-cancel`): Stop a task for good; only people already delivered are billed. Argument: `task_id` (required). Cancel cannot be undone.
- **List People Search Tasks** (`people-search-tasks`): Your searches, newest first. Arguments: `platform`, `status`, `limit`, `cursor`, all optional.
- **List People Found** (`people-profiles`): Everyone your searches found on one platform, with filters. Free; it does not start a search. Arguments: `platform` (required) and optional filters.
- **Company Search** (`company-search`): Start a billed background task that finds companies on the web matching a plain-language description, with each one's public emails, phones, social profiles, and leaders. Arguments: `query` (required), `count`, `min_score`, `exclude`, `countries`, `require`, `roles`, `infer_emails`, `verify_emails`, `metadata`, `idempotency_key`. See the `desearch-company-search` skill before calling it.
- **Company Enrich** (`company-enrich`): Start a billed background task that collects the same data for domains you already have, one company per domain, with no fit score. Arguments: `domains` (required, 1 to 200), `roles`, `infer_emails`, `verify_emails`, `metadata`, `idempotency_key`. See the `desearch-company-search` skill before calling it.
- **Company Search Status** (`company-search-status`): Status, progress, cost, and a page of companies for one Company Search or Company Enrich task. Arguments: `task_id` (required), `cursor`, `limit`, `include_companies`.
- **Pause Company Search** (`company-search-pause`): Pause a company task. Argument: `task_id` (required).
- **Resume Company Search** (`company-search-resume`): Resume a paused company task with no new charge. Argument: `task_id` (required).
- **Cancel Company Search** (`company-search-cancel`): Stop a company task for good; only companies already delivered are billed. Argument: `task_id` (required). Cancel cannot be undone.
- **List Company Search Tasks** (`company-search-tasks`): Your Company Search and Company Enrich tasks, newest first. Arguments: `type` (`search` or `enrich`), `status`, `limit`, `cursor`, `metadata`, all optional.

## When not to use these tools

Skip Desearch when the task is only about files in the current project, or when the text you need is already in the conversation. These tools do not browse a logged-in site, post to X, contact the people or companies they find, or change Desearch account settings.
