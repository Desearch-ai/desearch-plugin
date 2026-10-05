# Desearch plugin

Plugin bundle for Claude Code, Cursor, and Grok Build. It loads the npm package `desearch-mcp-server`. The tools call Desearch for AI search, X search, web search, page extraction, and X trends. This repository is the plugin root. It does not publish the server.

## Requirements

- Node.js 20.18.1 or newer (Node 22 is supported; Node 18 is not), so `npx` can start the server
- A Desearch API key from [console.desearch.ai/api-keys](https://console.desearch.ai/api-keys)

The MCP config launches `npx -y desearch-mcp-server@0.1.4` and passes `DESEARCH_API_KEY` into that process. The bundle does not contain a key.

Claude Code asks for the key through `userConfig`. Cursor asks for it through plugin variables. To run the server yourself:

```bash
export DESEARCH_API_KEY="your-api-key"
npx -y desearch-mcp-server@0.1.4
```

## Data flow and privacy

Search queries, URLs, and X/Twitter identifiers the user asks about are sent to the Desearch API (https://api.desearch.ai) using the user's own API key. Results return to the assistant. The plugin itself stores nothing.

- Desearch: https://desearch.ai
- Privacy policy: https://www.desearch.ai/privacy

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

To try it locally, copy this repository to `~/.cursor/plugins/local/desearch`, then run Developer: Reload Window. Open Customize and confirm the Desearch skill and MCP server. Local plugin imports must be allowed.

## Skill

`skills/desearch/SKILL.md` tells the agent which Desearch tool to call. It lists only the tools the server registers. `ai-search` `tools` uses the short ids `web`, `twitter`, `arxiv`, `wikipedia`, `hackernews`, and `reddit`. `youtube` is not accepted. The default is `web` and `twitter`.

## Grok Build

Manifest: `.grok-plugin/plugin.json`.
MCP config: `mcp.json`, set with `"mcpServers": "./mcp.json"`. A string path replaces the default `.mcp.json` load, so Grok Build reads `${DESEARCH_API_KEY}` from `mcp.json` instead of `${user_config.DESEARCH_API_KEY}`.
Skills: `"skills": "./skills/desearch"`. That path points at the skill directory, and the default `skills/` scan still applies.

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
