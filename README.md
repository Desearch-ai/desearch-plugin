# Desearch plugin

Plugin bundle for Claude Code, Cursor, and Grok Build. Claude connects to the hosted Desearch MCP service over HTTPS. Cursor and Grok Build load the npm package `desearch-mcp-server`. The tools call Desearch for AI search, X search, web search, the Search API, page extraction, X trends, public YouTube (videos, transcripts, comments, channels), Reddit, Threads, TikTok, Facebook, and Instagram data, People Search (finding people and creators on X, YouTube, LinkedIn, and TikTok), and Company Search (finding companies, or enriching domains you have, with their public contacts and leaders). The Claude plugin root is `plugins/desearch`; other hosts use the repository root. It does not publish the server.

## Requirements

Claude uses the remote MCP endpoint `https://mcp.desearch.ai/mcp` and the host's OAuth sign-in flow. No Node.js, local MCP server, plugin API-key setting, or credential environment variable is required for Claude. The Desearch authorization page asks for a Desearch API key from [console.desearch.ai/api-keys](https://console.desearch.ai/api-keys) before granting OAuth access.

Cursor and Grok Build use the separate `mcp.json` configuration and require Node.js 20.18.1 or newer (Node 22 is supported; Node 18 is not) and a Desearch API key from [console.desearch.ai/api-keys](https://console.desearch.ai/api-keys). Their launcher remains pinned to `desearch-mcp-server@0.9.0`. The bundle contains no key or server implementation.

## Data flow and privacy

Search queries, URLs, X/Twitter identifiers, YouTube, Reddit, Threads, TikTok, Facebook, and Instagram identifiers (video IDs, channel handles, subreddit names, usernames, post URLs), People Search descriptions, and Company Search descriptions and domains the user asks about are sent to Desearch. Claude sends requests over HTTPS to `https://mcp.desearch.ai/mcp` using the host-managed OAuth authorization. Cursor and Grok Build use the Desearch API (https://api.desearch.ai) with the user's own API key. Results return to the assistant. People Search results are public profile data (name, handle, bio, audience, public links, and contacts such as an email listed in a bio). Company Search results are public company data: what a company publishes on its own site, what web search returns, and public LinkedIn profiles of its leaders, including emails inferred from the company's address pattern (marked `source: inferred`). Desearch keeps both in the user's account for 30 days after a task ends. The plugin itself stores nothing.

Most tools are billed per request. The `youtube`, `reddit`, and `threads` tools cost $2.07 per 1,000 requests, an empty page included; a 404, a 422, and a 5xx are free. The `tiktok`, `facebook`, and `instagram` tools cost $2.07 per 1,000 items returned. `people-search` is different: it starts a background search that reserves `count` people at the platform's per-person price and settles to the people it delivers. A search that finds no one is free. `company-search` and `company-enrich` work the same way per company: they reserve `count` companies (Company Search) or one company per domain (Company Enrich) and settle to the companies they deliver; a task that delivers none is free. A Company Search with a search budget (`max_cost_usd`) reserves the whole budget and also pays for its search effort, up to the budget, even when it finds few companies or none; the skill tells the agent to set a budget only when the user agreed to the amount. Status, results, task control, task lists, the profiles library, and `people-search-export` are free.

- Desearch: https://desearch.ai
- Privacy policy: https://www.desearch.ai/privacy

## Claude Code

The Claude marketplace entry in `.claude-plugin/marketplace.json` sources the self-contained `plugins/desearch` package. Its manifest, remote OAuth MCP configuration, four skills, README, license, and assets are inside that folder. See the [Claude installation and authentication instructions](plugins/desearch/README.md).

```text
/plugin marketplace add Desearch-ai/desearch-plugin
/plugin install desearch@desearch
```

From the repository root, develop with `claude --plugin-dir ./plugins/desearch` and validate with `claude plugin validate ./plugins/desearch --strict`. The repository root is a marketplace, not a second Claude plugin.

## Cursor

Manifest: `.cursor-plugin/plugin.json` ([Cursor plugins reference](https://cursor.com/docs/reference/plugins)).
Logo: `assets/logo.png`, referenced by the `logo` field ([Logos](https://cursor.com/docs/reference/plugins#logos)).
MCP config: `mcp.json`, set with `"mcpServers": "./mcp.json"` so Cursor loads that file instead of `.mcp.json`.

`mcp.json` sets `DESEARCH_API_KEY` from the plugin variable `${DESEARCH_API_KEY}`. The name is declared under `variables` in `.cursor-plugin/plugin.json`. Users set the value in the dashboard under Plugins, then Configure. Plugin config does not use shell `${env:...}` placeholders ([Variables](https://cursor.com/docs/reference/plugins#variables)).

User and project `mcp.json` files use a different interpolation syntax; see [Cursor MCP configuration](https://cursor.com/docs/mcp). Cursor marketplace installs should follow `mcp.json`. Claude's separate remote OAuth configuration is `plugins/desearch/.mcp.json`; Cursor continues to use the root `mcp.json`.

To try it locally, copy this repository to `~/.cursor/plugins/local/desearch`, then run Developer: Reload Window. Open Customize and confirm the Desearch skills and MCP server. Local plugin imports must be allowed.

## Skills

`skills/desearch/SKILL.md` tells the agent which Desearch tool to call. It lists only the tools the server registers (39 in 0.9.0). `ai-search` `tools` uses the short ids `web`, `twitter`, `arxiv`, `wikipedia`, `hackernews`, and `reddit`. `youtube` is not accepted. The default is `web` and `twitter`.

`skills/desearch-people-search/SKILL.md` covers the seven People Search tools: `people-search` (billed), `people-search-status`, `people-search-pause`, `people-search-resume`, `people-search-cancel`, `people-search-tasks`, and `people-profiles`. It tells the agent to check the profiles library first, confirm the reservation with the user, send an `idempotency_key`, and poll status with the returned cursor. Prices and per-search minimums are listed in the skill.

`skills/desearch-company-search/SKILL.md` covers the seven Company Search tools: `company-search` and `company-enrich` (billed), `company-search-status`, `company-search-pause`, `company-search-resume`, `company-search-cancel`, and `company-search-tasks`. It tells the agent to check the user's earlier tasks first, confirm the reservation, send an `idempotency_key`, poll status with the returned cursor, and read every company once more after the task ends, because later stages fill companies in. It also covers the search budget (`max_cost_usd`, set only with the user's agreement to the amount), continuing a search that stopped early (`continue_from`), and checking only the companies a query names with their websites ("Restrict this search to Acme (acme.com.au)"). Prices and per-task minimums are listed in the skill.

`skills/desearch-social/SKILL.md` covers the six social tools: `youtube`, `reddit`, `threads`, `tiktok`, `facebook`, and `instagram`. It gives each action's arguments and enums, the paging rule (send `next_cursor` back unchanged as `cursor` with the same action and target; Threads never pages), what each call costs, and when to call `transcript` instead of `video`.

`skills/desearch-people-search/SKILL.md` also covers `people-search-export` (CSV or JSON Lines text, up to 1,000 rows).

desearch-mcp-server 0.4.0 replaced `people-search-control` with `people-search-pause`, `people-search-resume`, and `people-search-cancel`, so the skills name those three tools.

## Grok Build

Manifest: `.grok-plugin/plugin.json`. Grok Build 1.0.77 reads the root `plugin.json` before it, so both set the MCP config.
MCP config: `mcp.json`, set with `"mcpServers": "./mcp.json"` in `plugin.json` and `.grok-plugin/plugin.json`. These explicit paths keep Grok Build on its existing local launcher and `${DESEARCH_API_KEY}` configuration. Claude loads its separate remote configuration from `plugins/desearch/.mcp.json`.
Skills: `"skills": "./skills/desearch"`. That path points at the skill directory, and the default `skills/` scan still applies, so `skills/desearch-people-search`, `skills/desearch-company-search`, and `skills/desearch-social` load too.

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
