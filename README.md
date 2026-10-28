# Desearch plugin

Plugin bundle for Claude Code, Cursor, and Grok Build. It loads the npm package `desearch-mcp-server`. The tools call Desearch for AI search, X search, web search, the Search API, page extraction, X trends, public TikTok, Facebook, and Instagram data, and People Search (finding people and creators on X, YouTube, LinkedIn, and TikTok). This repository is the plugin root. It does not publish the server.

> **Release gate for plugin 0.3.0:** this version pins `desearch-mcp-server@0.4.0`. Do not merge or release it until `desearch-mcp-server@0.4.0` is published on npm. Until then `npx -y desearch-mcp-server@0.4.0` fails and the Desearch server does not start in any host. Check with `npm view desearch-mcp-server@0.4.0 version`.
>
> Server 0.4.0 adds `search-api`, `tiktok`, `facebook`, `instagram`, and `people-search-export`, and replaces `people-search-control` with `people-search-pause`, `people-search-resume`, and `people-search-cancel` (no alias). The skills name the new tools.

## Requirements

- Node.js 20.18.1 or newer (Node 22 is supported; Node 18 is not), so `npx` can start the server
- A Desearch API key from [console.desearch.ai/api-keys](https://console.desearch.ai/api-keys)

The MCP config launches `npx -y desearch-mcp-server@0.4.0` and passes `DESEARCH_API_KEY` into that process. The bundle does not contain a key.

Claude Code asks for the key through `userConfig`. Cursor asks for it through plugin variables. To run the server yourself:

```bash
export DESEARCH_API_KEY="your-api-key"
npx -y desearch-mcp-server@0.4.0
```

## Data flow and privacy

Search queries, URLs, X/Twitter, TikTok, Facebook, and Instagram identifiers (usernames, post and profile IDs, hashtags), and People Search descriptions the user asks about are sent to the Desearch API (https://api.desearch.ai) using the user's own API key. Results return to the assistant. People Search results are public profile data (name, handle, bio, audience, public links, and contacts such as an email listed in a bio); Desearch keeps them in the user's account for 30 days after a search ends. The plugin itself stores nothing.

Most tools are billed per request. `people-search` is different: it starts a background search that reserves `count` people at the platform's per-person price and settles to the people it delivers. A search that finds no one is free. Status, results, pause, resume, cancel, the task list, the profiles library, and `people-search-export` are free.

- Desearch: https://desearch.ai
- Privacy policy: https://www.desearch.ai/privacy

## Tools

`desearch-mcp-server@0.4.0` registers 29 tools. The search, page, X, TikTok, Facebook, and Instagram tools only read public data.

| Group | Tools |
| --- | --- |
| AI and web search | `ai-search`, `search`, `fetch`, `web-search`, `search-api`, `web-links-search` |
| Page extraction | `extract`, `web-crawl` (legacy route; prefer `extract`) |
| X | `x-search`, `x-links-search`, `x-posts-by-urls`, `x-post-by-id`, `x-posts-by-user`, `x-user-posts`, `x-user-replies`, `x-post-replies`, `x-post-retweeters`, `x-trends` |
| TikTok, Facebook, Instagram | `tiktok`, `facebook`, `instagram` |
| People Search | `people-search` (billed), `people-search-status`, `people-search-pause`, `people-search-resume`, `people-search-cancel`, `people-search-tasks`, `people-profiles`, `people-search-export` |

New in server 0.4.0:

- `search-api`: ranked web pages, each with the passage that best matches the query (`POST /search`). Optional `mode` (`fast` or `balanced`), `count` (10, 15, or 20), date range, `highlights`, and `page_text` for each page's full text.
- `tiktok`, `facebook`, `instagram`: public data for each platform. `action` picks the route (for example `search`, `post`, `profile`, `profile_posts`, `comments`, `hashtag`; TikTok also has `trending`, Instagram has `media` instead of `post`). List actions return `results` and `next_cursor`; pass `next_cursor` back unchanged as `cursor` with the same action and target for the next page. Facebook `search` and `hashtag` return Meta Ad Library ads, not organic posts.
- `people-search-export`: the people found by one search (`task_id`) or on one platform (`platform`), as CSV or JSON Lines text, up to `max_rows` rows (1 to 1000, default 100). Free.
- `people-search-pause`, `people-search-resume`, `people-search-cancel`: replace `people-search-control`.

## Claude Code

Manifest: `.claude-plugin/plugin.json` ([plugin manifest](https://code.claude.com/docs/en/plugins-reference)).
Marketplace: `.claude-plugin/marketplace.json` ([plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)).
MCP config: `.mcp.json` at the plugin root ([MCP servers in plugins](https://code.claude.com/docs/en/plugins-reference#mcp-servers)).

`userConfig.DESEARCH_API_KEY` has `type` `string`, `sensitive` `true`, and `required` `true`. The title and description are `Desearch API key from https://console.desearch.ai`. Claude Code substitutes `${user_config.DESEARCH_API_KEY}` into the server `env` block ([User configuration](https://code.claude.com/docs/en/plugins-reference#user-configuration)). The Claude manifest schema has no logo field, so the logo is not listed there. Unrecognized manifest fields are warnings, and `claude plugin validate --strict` treats warnings as errors.

`.mcp.json` can stay separate from `plugin.json`. Docs allow either `.mcp.json` at the plugin root or an inline `mcpServers` object. This plugin keeps the Claude server in `.mcp.json`. The `env` value is not a shell command, so `${user_config.DESEARCH_API_KEY}` is allowed there. Shell-form hook commands, monitor commands, and MCP `headersHelper` reject that placeholder.

Add the marketplace, then install the plugin. The in-app `/plugin install` prompts for the key:

```text
/plugin marketplace add Desearch-ai/desearch-plugin
/plugin install desearch@desearch
```

From the command line, `claude plugin install desearch@desearch` does not prompt. Set the key afterwards with `/plugin configure desearch@desearch` inside Claude Code, or with `claude plugin configure desearch@desearch`.

Load this directory while you develop:

```bash
claude --plugin-dir .
```

Check the manifest:

```bash
claude plugin validate . --strict
```

## Cursor

Manifest: `.cursor-plugin/plugin.json` ([Cursor plugins reference](https://cursor.com/docs/reference/plugins)).
Logo: `assets/logo.png`, referenced by the `logo` field ([Logos](https://cursor.com/docs/reference/plugins#logos)).
MCP config: `mcp.json`, set with `"mcpServers": "./mcp.json"` so Cursor loads that file instead of `.mcp.json`.

`mcp.json` sets `DESEARCH_API_KEY` from the plugin variable `${DESEARCH_API_KEY}`. The name is declared under `variables` in `.cursor-plugin/plugin.json`. Users set the value in the dashboard under Plugins, then Configure. Plugin config does not use shell `${env:...}` placeholders ([Variables](https://cursor.com/docs/reference/plugins#variables)).

User and project `mcp.json` files use a different syntax. [Config interpolation](https://cursor.com/docs/mcp) (also published at https://cursor.com/docs/context/mcp) expands `${env:NAME}`, along with `${userHome}`, `${workspaceFolder}`, `${workspaceFolderBasename}`, `${pathSeparator}`, and `${/}`. cursor.directory reads `.mcp.json`. That file is the Claude Code config and uses `${user_config.DESEARCH_API_KEY}`, which Cursor does not expand. No single placeholder works for both hosts, so the configs are split. Cursor marketplace installs should follow `mcp.json`.

To try it locally, copy this repository to `~/.cursor/plugins/local/desearch`, then run Developer: Reload Window. Open Customize and confirm the Desearch skills and MCP server. Local plugin imports must be allowed.

## Skills

`skills/desearch/SKILL.md` tells the agent which Desearch tool to call. It lists only the tools the server registers (29 in 0.4.0), including the `action` values and cursor paging for `tiktok`, `facebook`, and `instagram`. `ai-search` `tools` uses the short ids `web`, `twitter`, `arxiv`, `wikipedia`, `hackernews`, and `reddit`. `youtube` is not accepted. The default is `web` and `twitter`.

`skills/desearch-people-search/SKILL.md` covers the eight People Search tools: `people-search` (billed), `people-search-status`, `people-search-pause`, `people-search-resume`, `people-search-cancel`, `people-search-tasks`, `people-profiles`, and `people-search-export`. It tells the agent to check the profiles library first, confirm the reservation with the user, send an `idempotency_key`, poll status with the returned cursor, and export with `people-search-export` when the user wants a file. Prices and per-search minimums are listed in the skill.

## Grok Build

Manifest: `.grok-plugin/plugin.json`.
MCP config: `mcp.json`, set with `"mcpServers": "./mcp.json"`. A string path replaces the default `.mcp.json` load, so Grok Build reads `${DESEARCH_API_KEY}` from `mcp.json` instead of `${user_config.DESEARCH_API_KEY}`.
Skills: `"skills": "./skills/desearch"`. That path points at the skill directory, and the default `skills/` scan still applies, so `skills/desearch-people-search` loads too.

Export the key in your environment, then install:

```bash
export DESEARCH_API_KEY=...
grok plugin marketplace add Desearch-ai/desearch-plugin
grok plugin install desearch --trust
```

Grok Build expands `${VAR}` and `${VAR:-default}` in the server command, args, env, url, and headers.

`marketplace/grok-marketplace-entry.json` is a draft catalog entry for [xai-org/plugin-marketplace](https://github.com/xai-org/plugin-marketplace). The entry points at `https://github.com/Desearch-ai/desearch-plugin.git`. Its `sha` stays at the current pin. After that pin matches the commit you want listed, the marketplace change is a pull request that adds this object to `.grok-plugin/marketplace.json`, then:

```bash
python3 scripts/generate-plugin-index.py
python3 scripts/validate-catalog.py
```
