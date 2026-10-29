---
name: desearch-company-search
description: Find companies that match a plain-language description, or enrich domains the user already has, with their public emails, phones, social profiles, and leaders, using the Desearch Company Search MCP tools. Use when the user asks for a list of companies, accounts, or leads with contacts, or for the contacts and leaders of companies they name by domain. Starting a task is billed and runs in the background for minutes.
---

# Desearch Company Search

Company Search returns companies, not pages. Describe the companies you want in plain language, for example "Series A fintech startups in Berlin building payment infrastructure". Desearch looks for their websites, reads each homepage, and scores how well each company fits. It then reads the company's contact, about, team, and imprint pages for emails, phones, and social profiles, finds its leaders (CEO, founders, CTO, and CFO by default) with their LinkedIn profiles, infers their emails from the company's address pattern, and checks every email. Company Enrich collects the same data for domains the user already has, one company per domain, without a fit score. Every contact keeps the page it came from. Public data only.

The plugin launches `npx -y desearch-mcp-server@0.6.0`, which registers the seven tools below. For people or creators found by what they post, use the `desearch-people-search` skill instead.

## Billing

`company-search` and `company-enrich` are the only billed Company Search tools. Each reserves companies at its per-company price (`reserved_cost_usd` in the response). When the task ends the user pays only for the companies it delivered, with a minimum per task that delivers any. The rest of the reservation is returned automatically. A task that delivers no company is free, and a company left out by `min_score` or `require` is not billed.

| Tool | Finds | Reserves | Price | Minimum billed per task that delivers any company |
|------|-------|----------|-------|---------------------------------------------------|
| `company-search` | Companies that match a description, each with a fit score | `count` companies | $0.09 per company | 2 companies |
| `company-enrich` | One company per domain sent, no fit score | One company per domain (duplicates are returned) | $0.05 per company | 1 company |

Status, results, task control, and the task list are free. The task's `reserved_cost_usd` and `final_cost_usd` are the amounts that count; current prices are at https://desearch.ai/pricing.

## Workflow

1. **Check what the user already has.** Call `company-search-tasks` (filter by `type`, `status`, or `metadata`) when the user may have run this search or enrichment before, then read that task with `company-search-status`. It is free and does not start a task.
2. **Confirm before spending.** Tell the user which tool, `count` (or the number of domains), and the maximum reservation (that number times the price above). Call `company-search` only when the user asks to find companies, and `company-enrich` only when they ask for the contacts of domains they have.
3. **Start once.** Call the tool one time with a new `idempotency_key` (for example a UUID). If the call fails or times out, retry with the same `idempotency_key`; the API returns the first task (`existing_task: true`) instead of starting and charging a second one. Keep the returned `task_id`.
4. **Poll.** A task runs for minutes. Call `company-search-status` with the `task_id` every 15 to 30 seconds. Companies appear while it runs with `enrichment.status` `partial`, and later stages (contact pages, leaders, inferred emails, email checks) fill them in place. Pass the returned `next_cursor` as `cursor` to get only the companies delivered since the previous call. `stage` `enriching` means every company is delivered and only later stages are left. Each response has a `next` hint that says what to do.
5. **Finish.** The task is done when `done` is true (`status` is `completed`, `partial`, `failed`, `cancelled`, or `expired`) and `has_more` is false. Then call `company-search-status` once more without `cursor`, and page on with the returned cursor, to read every company in its final version. Report `final_cost_usd`, why it stopped (`completion_reason`, `coverage_limited`), and any `warnings` with the results.

## Which tool

- **Company Search** (`company-search`, billed): Start a background task that finds companies from a description. Arguments: `query` (required, 3 to 1000 characters: what they do, where, how far along), `count` (optional, 5 to 200, API default 25), `min_score` (optional, 0 to 100), `exclude` (optional domains or URLs to leave out, up to 1000), `countries` (optional ISO codes or country names, up to 20), `require` (optional list of `email`, `phone`, `linkedin` (the company's LinkedIn page), `leader`, `leader_email`; a company without all of them is not delivered or billed), plus the options below. `countries` and `require` are top-level arguments; the server sends them as `filters`.
- **Company Enrich** (`company-enrich`, billed): Start a background task for companies the user already knows. Arguments: `domains` (required, 1 to 200 domains or URLs; each is reduced to its host without `www.`, and duplicates are removed), plus the options below.
- Options both take: `roles` (optional list of `ceo`, `founder`, `cto`, `cfo`, `coo`, `cmo`, `president`, `owner`, `managing_director`; default `ceo`, `founder`, `cto`, `cfo`), `infer_emails` (optional, default true: guess leaders' emails from the company's address pattern), `verify_emails` (optional, default true: check every email), `metadata` (optional labels such as `{"campaign": "q4-outbound"}`: up to 10 keys of a-z, 0-9, `_`, `.`, `-`, string values up to 200 characters; returned on the task and usable as a filter), `idempotency_key` (optional, reuse it on a retry).
- **Company Search Status** (`company-search-status`): Status, stage, progress, cost, and a page of companies for one Company Search or Company Enrich task. Arguments: `task_id` (required), `cursor` (optional, the previous `next_cursor`; omit it to read from the first company, each in its latest version), `limit` (optional, 1 to 100, default 10), `include_companies` (optional, `false` reads only status and cost).
- **Pause Company Search** (`company-search-pause`): Argument: `task_id` (required). A running task finishes its current batch first; companies delivered so far stay readable and the reservation stays as it is. A task paused for more than 7 days is cancelled.
- **Resume Company Search** (`company-search-resume`): Argument: `task_id` (required). Resume is not charged again and works only on a paused task.
- **Cancel Company Search** (`company-search-cancel`): Argument: `task_id` (required). Cancel cannot be undone; the user pays only for the companies already delivered.
- **List Company Search Tasks** (`company-search-tasks`): The user's Company Search and Company Enrich tasks, newest first. Arguments: `type` (`search` or `enrich`), `status` (list, for example `["running", "paused"]`), `limit` (1 to 100), `cursor`, `metadata` (up to 3 labels a task must have, exact match), all optional. People Search tasks are not listed. A new task is refused with 429 while too many People Search and Company Search tasks are queued, running, or paused.

A People Search `task_id` does not work on these tools, and a company `task_id` does not work on the People Search tools.

## Results

Each company has `domain`, `name`, `url`, `industry`, `location`, a short `description`, `score` (0 to 100; `null` for Company Enrich), `why` it matched and up to three `reasons`, `fully_verified` and `unverified_criteria` (Company Search: what its own pages do and do not confirm), `primary_email` and `primary_contact`, `contact_coverage`, public `emails`, `phones`, and `socials` (each with the `source_url` it came from), `leaders` (name, `title`, `roles`, `verified`, LinkedIn profile, and emails), and `enrichment`: each stage (`profile`, `contacts`, `people`, `email_patterns`, `email_check`) as `pending`, `done`, `failed`, or `skipped`, and a `status` that is `partial` while any stage is `pending`, then `complete`. A stage is `skipped` when the request turned it off, it had nothing to do, or the task's time limit cut it (then `enrichment.errors` says so and the task has the `enrichment_time_limit` warning).

Each email has a `verification` status once the checks ran: `valid`, `invalid`, `risky`, or `unknown`. An email with `source` `inferred` is a guess from the company's address pattern, with a `confidence` (`high` or `low`) and the `pattern`; tell the user it is inferred. A missing field means the company did not publish it, not that it has none.

An ended task has `completion_reason` (why it stopped; `all_domains_processed` for Company Enrich), `coverage_limited: true` when a budget stopped it before `count` (more companies may match), and `warnings`, each with a `code` and a `message`:

| `code` | Meaning |
|--------|---------|
| `planning_fallback` | The search was planned without AI, so results may be broader. |
| `ai_scoring_unavailable` | AI scoring was unavailable, so companies were matched by the search's words only. |
| `enrichment_time_limit` | Some companies were not fully enriched before the task's time limit. Their remaining stages are `skipped`. |
| `linkedin_verification_unavailable` | Leaders found through LinkedIn search could not be checked against their LinkedIn profiles. |

Treat a `code` not in this table as information and show its `message`.

The MCP tools do not export files. To download a task as CSV or JSON Lines, use the Desearch Console or `GET /desearch/companies/tasks/{task_id}/export?format=csv` (or `format=jsonl`) on the API. Results stay available for 30 days after a task ends.

## When not to use these tools

Do not start a Company Search for one company the user already names; use `company-enrich` with its domain, or `extract` on its site for the page text. Do not use these tools to find people by what they post (use People Search) or to answer a question about a topic. These tools do not contact the companies or people they find, send email, or change Desearch account settings.
