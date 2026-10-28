---
name: desearch
description: Choose which Desearch MCP tool to call. Use when the task needs AI search, web search, ranked pages from the Search API, a page as text or HTML, X posts, X trends, public TikTok, Facebook, or Instagram posts and profiles, or finding people and creators on X, YouTube, LinkedIn, or TikTok.
---

# Desearch

Pick one Desearch tool from this list. Do not call a tool that is not registered.

The host passes `DESEARCH_API_KEY` into the server. The plugin launches `npx -y desearch-mcp-server@0.4.0`. The search, page, X, TikTok, Facebook, and Instagram tools send read requests. They do not post, follow, delete, or change an account. `people-search` starts a billed background search, and `people-search-pause`, `people-search-resume`, and `people-search-cancel` pause, resume, or cancel one. For People Search, follow the `desearch-people-search` skill.

## Which tool

- **AI Search** (`ai-search`): Calls Desearch AI search. Arguments: `prompt` (required). `tools` is optional and defaults to `web` and `twitter`. Allowed `tools` values are `web`, `twitter`, `arxiv`, `wikipedia`, `hackernews`, and `reddit`. Older labels such as `Web Search`, `ArXiv Search`, `Wikipedia Search`, `Hacker News Search`, and `Reddit Search` are accepted and rewritten to the short id. `youtube` is not accepted. Optional: `date_filter`, `start_date`, `end_date` (UTC), `result_type` (`ONLY_LINKS` or `LINKS_WITH_FINAL_SUMMARY`), `include_domains`, `exclude_domains`, `model` (`NOVA` or `ORBIT`, default `NOVA`).
- **Search** (`search`): Web search that returns `results` with `id`, `title`, and `url`. Argument: `query` (required). Use this when a client asks for a search tool.
- **Fetch Page** (`fetch`): Read one public page as text. Argument: `id` (required, an `http` or `https` URL, usually a `search` result URL).
- **Web Search** (`web-search`): Web search. Returns titles, links, and snippets. Arguments: `query` (required), `start` (optional offset: 0, 10, 20, ...).
- **Search API** (`search-api`): Ranked web pages, each with the passage that best matches the query. Arguments: `query` (required), `mode` (optional, `fast` or `balanced`), `count` (optional, 10, 15, or 20), `start_date` and `end_date` (optional, YYYY-MM-DD), `highlights` (optional), `page_text` (optional, adds each page's full text).
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
- **TikTok** (`tiktok`): Public TikTok data. `action` (required): `search` (`query`; optional `count`, `sort`, `cursor`), `post` (`id`), `profile` (`username`), `profile_posts` (`username`; optional `count`, `cursor`), `comments` (`video_id`; optional `count`, `cursor`), `hashtag` (`tag`; optional `count`, `cursor`), `trending` (optional `region`, `count`).
- **Facebook** (`facebook`): Public Facebook data. `action` (required): `search` (`query`) and `hashtag` (`tag`) return Meta Ad Library ads; `post` (`id`), `profile` (`profile_id`), `profile_posts` (`profile_id`), `comments` (`post_id`). List actions take optional `count` and `cursor`.
- **Instagram** (`instagram`): Public Instagram data. `action` (required): `search` (`query`; optional `count`; no cursor), `media` (`id`), `profile` (`username`), `profile_posts` (`username`), `comments` (`shortcode` from the post URL), `hashtag` (`tag`). List actions take optional `count` and `cursor`.
- Paging for `tiktok`, `facebook`, and `instagram`: list actions return `results` and `next_cursor`. For the next page, call the same action with the same target and `cursor` set to `next_cursor`, unchanged. `next_cursor` is null on the last page; a cursor lasts 24 hours.
- **People Search** (`people-search`): Start a billed background search for people on `x`, `youtube`, `linkedin`, or `tiktok` who match a plain-language description. Arguments: `platform` and `query` (required), `count`, `min_score`, `exclude`, `metadata`, `idempotency_key`, and platform filters. See the `desearch-people-search` skill before calling it.
- **People Search Status** (`people-search-status`): Status, progress, cost, and a page of people for one task. Arguments: `task_id` (required), `cursor`, `limit`, `include_people`.
- **Pause People Search** (`people-search-pause`): Pause a task. Argument: `task_id` (required).
- **Resume People Search** (`people-search-resume`): Resume a paused task with no new charge. Argument: `task_id` (required).
- **Cancel People Search** (`people-search-cancel`): Stop a task for good; only people already delivered are billed. Argument: `task_id` (required). Cancel cannot be undone.
- **List People Search Tasks** (`people-search-tasks`): Your searches, newest first. Arguments: `platform`, `status` (list), `limit`, `cursor`, `metadata` (up to 3 labels a task must have, exact match), all optional.
- **List People Found** (`people-profiles`): Everyone your searches found on one platform, with filters. Free; it does not start a search. Arguments: `platform` (required) and optional filters.
- **Export People Found** (`people-search-export`): The people found as CSV or JSON Lines text, after a note with the row count. Arguments: `task_id` (one search) or `platform` (everyone found there), `format` (`csv` or `jsonl`), the `people-profiles` filters, and `max_rows` (1 to 1000, default 100). Free.

Before `people-search`, check `people-profiles` when the user may already have searched for these people. Start a new search only when the user asks to find people.

## Choosing between similar tools

- Web: `ai-search` for an answer with sources, `web-search` for result snippets, `search-api` for ranked pages with the matching passage (and full page text with `page_text`), then `extract` or `fetch` to read one page.
- Social posts and profiles: use the `x-*` tools for X, and `tiktok`, `facebook`, or `instagram` with the matching `action` for those platforms. To find people who fit a description rather than posts, use `people-search`.
- Facebook `search` and `hashtag` read the Meta Ad Library (ads), not organic posts. Use them for ads; use `profile_posts` for a page's own posts.
- Instagram `comments` takes the shortcode from the post URL (`DeuOR-CjKE9` in `https://www.instagram.com/p/DeuOR-CjKE9/`), not a numeric media ID.
- TikTok `trending` and Instagram `search` return one page and take no `cursor`.

## When not to use these tools

Skip Desearch when the task is only about files in the current project, or when the text you need is already in the conversation. These tools do not browse a logged-in site, post to X or any other platform, contact the people they find, or change Desearch account settings.
