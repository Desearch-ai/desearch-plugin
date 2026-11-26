# Desearch for Claude

Desearch for Claude connects to the hosted MCP service for AI search, X search, web search, page extraction, public social data, People Search, and Company Search. This folder is the self-contained Claude plugin; its four skills and runtime configuration are included here.

## Requirements

Claude uses the remote MCP endpoint `https://mcp.desearch.ai/mcp` and the host's OAuth sign-in flow. No Node.js, local MCP server, plugin API-key setting, or credential environment variable is required for Claude. The Desearch authorization page asks for a Desearch API key from [console.desearch.ai/api-keys](https://console.desearch.ai/api-keys) before granting OAuth access.

## Data flow and privacy

Search queries, URLs, X/Twitter identifiers, YouTube, Reddit, Threads, TikTok, Facebook, and Instagram identifiers (video IDs, channel handles, subreddit names, usernames, post URLs), People Search descriptions, and Company Search descriptions and domains the user asks about are sent to Desearch. Claude sends requests over HTTPS to `https://mcp.desearch.ai/mcp` using the host-managed OAuth authorization. Results return to the assistant. People Search results are public profile data (name, handle, bio, audience, public links, and contacts such as an email listed in a bio). Company Search results are public company data: what a company publishes on its own site, what web search returns, and public LinkedIn profiles of its leaders, including emails inferred from the company's address pattern (marked `source: inferred`). Desearch keeps both in the user's account for 30 days after a task ends. The plugin itself stores nothing.

Most tools are billed per request. The `youtube`, `reddit`, and `threads` tools cost $2.07 per 1,000 requests, an empty page included; a 404, a 422, and a 5xx are free. The `tiktok`, `facebook`, and `instagram` tools cost $2.07 per 1,000 items returned. `people-search` is different: it starts a background search that reserves `count` people at the platform's per-person price and settles to the people it delivers. A search that finds no one is free. `company-search` and `company-enrich` work the same way per company: they reserve `count` companies (Company Search) or one company per domain (Company Enrich) and settle to the companies they deliver; a task that delivers none is free. A Company Search with a search budget (`max_cost_usd`) reserves the whole budget and also pays for its search effort, up to the budget, even when it finds few companies or none; the skill tells the agent to set a budget only when the user agreed to the amount. Status, results, task control, task lists, the profiles library, and `people-search-export` are free.

- Desearch: https://desearch.ai
- Privacy policy: https://www.desearch.ai/privacy

## Data Sources, Legal Basis & Opt-Out

People Search and Company Search return named people's business contact channels at scale. These include a public email or other contact listed on a profile, and emails inferred from a company's address pattern (marked `source: inferred`).

**Data sources.** This information comes from publicly available web and business sources: public profiles on platforms such as X, YouTube, LinkedIn and TikTok; information a company publishes on its own website; and what public web search returns.

**Legal basis.** The legal basis for collecting, holding and providing that business-contact information is legitimate interests.

**Opt-out and removal.** If you are a person listed in People Search or Company Search results and you want your data removed, send an opt-out or removal request to support@desearch.ai or follow the instructions at https://www.desearch.ai/privacy. We respond within 30 days.

## Claude Code

Manifest: `.claude-plugin/plugin.json` ([plugin manifest](https://code.claude.com/docs/en/plugins-reference)).
Marketplace: `.claude-plugin/marketplace.json` in the repository root ([plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)).
MCP config: `.mcp.json` at the plugin root ([MCP servers in plugins](https://code.claude.com/docs/en/plugins-reference#mcp-servers)).

The default `.mcp.json` declares a Streamable HTTP server with `type: "http"` and `url: "https://mcp.desearch.ai/mcp"`. It has no local command, environment variables, static authorization header, or shell helper. Claude discovers the service's OAuth metadata and uses its authorization-code flow with PKCE. The host manages credentials and refresh; the plugin does not store tokens. See [remote MCP authentication](https://code.claude.com/docs/en/mcp#authenticate-with-remote-mcp-servers).

Add the marketplace, then install the plugin:

```text
/plugin marketplace add Desearch-ai/desearch-plugin
/plugin install desearch@desearch
```

Run `/mcp`, select the plugin's Desearch server, and follow the authentication link to the Desearch authorization page. Enter your Desearch API key there and continue to authorize the connection. The service checks the key and keeps it on the server; it is not sent to the localhost callback. If the browser does not open, copy the link into your browser. Complete authorization before making a search. When authorization expires or is rejected, use `/mcp` to authenticate again. Enter the key only on the HTTPS Desearch authorization page. Do not paste it into a chat prompt, a repository file, or an environment variable for this Claude configuration.

From the command line, install with `claude plugin install desearch@desearch`. The Claude plugin v0.5.1 no longer asks for `userConfig.DESEARCH_API_KEY`; an older local installation may still have that saved setting. Updating the plugin uses OAuth instead.

From the repository root, load this package while you develop:

```bash
claude --plugin-dir ./plugins/desearch
```

Check the manifest:

```bash
claude plugin validate ./plugins/desearch --strict
```

## Skills

`skills/desearch/SKILL.md` tells the agent which Desearch tool to call. It lists the 39 tools exposed by the hosted MCP service. `ai-search` `tools` uses the short ids `web`, `twitter`, `arxiv`, `wikipedia`, `hackernews`, and `reddit`. `youtube` is not accepted. The default is `web` and `twitter`.

`skills/desearch-people-search/SKILL.md` covers the seven People Search tools: `people-search` (billed), `people-search-status`, `people-search-pause`, `people-search-resume`, `people-search-cancel`, `people-search-tasks`, and `people-profiles`. It tells the agent to check the profiles library first, confirm the reservation with the user, send an `idempotency_key`, and poll status with the returned cursor. Prices and per-search minimums are listed in the skill.

`skills/desearch-company-search/SKILL.md` covers the seven Company Search tools: `company-search` and `company-enrich` (billed), `company-search-status`, `company-search-pause`, `company-search-resume`, `company-search-cancel`, and `company-search-tasks`. It tells the agent to check the user's earlier tasks first, confirm the reservation, send an `idempotency_key`, poll status with the returned cursor, and read every company once more after the task ends, because later stages fill companies in. It also covers the search budget (`max_cost_usd`, set only with the user's agreement to the amount), continuing a search that stopped early (`continue_from`), and checking only the companies a query names with their websites ("Restrict this search to Acme (acme.com.au)"). Prices and per-task minimums are listed in the skill.

`skills/desearch-social/SKILL.md` covers the six social tools: `youtube`, `reddit`, `threads`, `tiktok`, `facebook`, and `instagram`. It gives each action's arguments and enums, the paging rule (send `next_cursor` back unchanged as `cursor` with the same action and target; Threads never pages), what each call costs, and when to call `transcript` instead of `video`.

`skills/desearch-people-search/SKILL.md` also covers `people-search-export` (CSV or JSON Lines text, up to 1,000 rows).

desearch-mcp-server 0.4.0 replaced `people-search-control` with `people-search-pause`, `people-search-resume`, and `people-search-cancel`, so the skills name those three tools.

