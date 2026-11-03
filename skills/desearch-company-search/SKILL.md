---
name: desearch-company-search
description: Find companies that match a plain-language description, or enrich domains the user already has, with their public emails, phones, social profiles, and leaders, using the Desearch Company Search MCP tools. Use when the user asks for a list of companies, accounts, or leads with contacts, or for the contacts and leaders of companies they name by domain, or to find more after a search stopped early. Starting a task is billed and runs in the background for minutes.
---

# Desearch Company Search

Company Search returns companies, not pages. Describe the companies you want in plain language, for example "Series A fintech startups in Berlin building payment infrastructure". Desearch looks for their websites, reads each homepage, and scores how well each company fits. It then reads the company's contact, about, team, and imprint pages for emails, phones, and social profiles, finds its leaders (CEO, founders, CTO, and CFO by default) with their LinkedIn profiles, infers their emails from the company's address pattern, and checks every email. Company Enrich collects the same data for domains the user already has, one company per domain, without a fit score. Every contact keeps the page it came from. Public data only.

The plugin launches `npx -y desearch-mcp-server@0.9.0`, which registers the seven tools below. For people or creators found by what they post, use the `desearch-people-search` skill instead.

## Billing

`company-search` and `company-enrich` are the only billed Company Search tools. Each reserves companies at its per-company price (`reserved_cost_usd` in the response). When the task ends the user pays only for the companies it delivered, with a minimum per task that delivers any. The rest of the reservation is returned automatically. A task that delivers no company is free, and a company left out by `min_score` or `require` is not billed. A Company Search with a search budget (`max_cost_usd`, below) is the exception: it also pays for its search effort.

| Tool | Finds | Reserves | Price | Minimum billed per task that delivers any company |
|------|-------|----------|-------|---------------------------------------------------|
| `company-search` | Companies that match a description, each with a fit score | `count` companies, or the whole `max_cost_usd` budget | $0.045 per company | 1 company |
| `company-enrich` | One company per domain sent, no fit score | One company per domain (duplicates are returned) | $0.05 per company | 1 company |

Status, results, task control, and the task list are free. The task's `reserved_cost_usd` and `final_cost_usd` are the amounts that count; current prices are at https://desearch.ai/pricing.

### Search budget (`max_cost_usd`)

Without a budget, a Company Search stops once its search costs more than the companies it found pay for. The task then ends with `completion_reason` `cost_limit` and `coverage_limited: true`, often before `count` when the companies are rare. A budget lets it search further:

- `max_cost_usd` is the most the task may charge, in USD: more than 0, at most 100, and at least `count` times the price (50 companies at $0.045 need at least $2.25; less is refused with HTTP 422, which gives the minimum).
- The whole budget is reserved, and the search goes on until it delivers `count` or spends the budget.
- The user pays for the companies delivered, or for the search effort when they do not cover it, up to the budget. **The effort is charged even when the search finds few companies or none.** The unused part is returned when the task ends, and `progress.effort_units` then shows the effort in companies. A cancelled search with a budget pays for its effort so far the same way; a `failed` or `partial` one pays only for the companies it delivered.

**Consent rule.** Never set `max_cost_usd` on your own, and never pick the amount for the user. Set it only when the user agreed to a dollar amount after you told them it is charged for the search effort even if few or no companies are found. A request for "50 companies" is not consent to a budget. Without that agreement, start the search without `max_cost_usd`.

## Workflow

1. **Check what the user already has.** Call `company-search-tasks` (filter by `type`, `status`, or `metadata`) when the user may have run this search or enrichment before, then read that task with `company-search-status`. It is free and does not start a task.
2. **Confirm before spending.** Tell the user which tool, `count` (or the number of domains), and the maximum reservation (that number times the price above). With a budget the maximum is `max_cost_usd`, and the user must agree to it under the consent rule above. Call `company-search` only when the user asks to find companies, and `company-enrich` only when they ask for the contacts of domains they have.
3. **Start once.** Call the tool one time with a new `idempotency_key` (for example a UUID). If the call fails or times out, retry with the same `idempotency_key`; the API returns the first task (`existing_task: true`) instead of starting and charging a second one. Keep the returned `task_id`.
4. **Poll.** A task runs for minutes. Call `company-search-status` with the `task_id` every 15 to 30 seconds. Companies appear while it runs with `enrichment.status` `partial`, and later stages (contact pages, leaders, inferred emails, email checks) fill them in place. Pass the returned `next_cursor` as `cursor` to get only the companies delivered since the previous call. `stage` `enriching` means every company is delivered and only later stages are left. Each response has a `next` hint that says what to do.
5. **Finish.** The task is done when `done` is true (`status` is `completed`, `partial`, `failed`, `cancelled`, or `expired`) and `has_more` is false. Then call `company-search-status` once more without `cursor`, and page on with the returned cursor, to read every company in its final version. Report `final_cost_usd`, why it stopped (`completion_reason`, `coverage_limited`), and any `warnings` with the results.
6. **Offer to find more.** When a Company Search ended with `coverage_limited: true` (for example `cost_limit`), tell the user more companies may match and offer to continue it with `continue_from` (below). Start it only when the user says yes.

## Find more (`continue_from`)

`continue_from` continues an ended Company Search with new companies only:

- Call `company-search` again with the same `query` and filters (`countries`, `require`, `min_score`, `roles`), `continue_from` set to the ended task's `task_id`, and `count` set to the companies still wanted (at least 5). The status `next` hint gives the numbers.
- The new search leaves out every company the earlier one delivered, held for review, or was told to exclude, plus its own `exclude`. To continue again, use the latest `task_id`: its exclusions already include the earlier ones.
- It is a new billed task: confirm its reservation and send a new `idempotency_key`. A budget may be added only under the consent rule above. Without one it can stop at `cost_limit` again.
- The API answers 409 while the earlier task has not ended (queued, running, or paused), and 404 when the `task_id` is not the user's Company Search (a Company Enrich or People Search `task_id`).

## Check only the companies the user names

When the user wants named companies checked against a description, rather than companies like them, put each company's website in `query`: "Family-owned civil contractors in Western Australia. Restrict this search to Acme (acme.com.au) and Beta (beta.co.uk). Return only those."

- Only those domains are checked against the rest of the description, with no web search. The task lists them as `only_domains` and ends with `completion_reason` `all_domains_processed`.
- A named company is delivered, with a fit score, only when it fits. Set `count` to the number named (at least 5); only the companies delivered are billed.
- Companies named without their websites do not restrict the search. It runs as a normal web search, and the task has the warning `scope_not_applied`. Find their websites first. "Companies like acme.com.au" is an example, not a restriction.
- To get only the contacts of domains the user has, with no fit check, use `company-enrich`.

## Which tool

- **Company Search** (`company-search`, billed): Start a background task that finds companies from a description. Arguments: `query` (required, 3 to 1000 characters: what they do, where, how far along), `count` (optional, 5 to 200, API default 25), `min_score` (optional, 0 to 100), `exclude` (optional domains or URLs to leave out, up to 1000), `countries` (optional ISO codes or country names, up to 20), `require` (optional list of `email`, `phone`, `linkedin` (the company's LinkedIn page), `leader`, `leader_email`; a company without all of them is not delivered or billed), `max_cost_usd` (optional search budget in USD, up to 100; only with the user's agreement, see Search budget), `continue_from` (optional `task_id` of an ended Company Search, see Find more), plus the options below. `countries` and `require` are top-level arguments; the server sends them as `filters`.
- **Company Enrich** (`company-enrich`, billed): Start a background task for companies the user already knows. Arguments: `domains` (required, 1 to 200 domains or URLs; each is reduced to its host without `www.`, and duplicates are removed), plus the options below.
- Options both take: `roles` (optional list of `ceo`, `founder`, `cto`, `cfo`, `coo`, `cmo`, `president`, `owner`, `managing_director`; default `ceo`, `founder`, `cto`, `cfo`), `infer_emails` (optional, default true: guess leaders' emails from the company's address pattern), `verify_emails` (optional, default true: check every email), `metadata` (optional labels such as `{"campaign": "q4-outbound"}`: up to 10 keys of a-z, 0-9, `_`, `.`, `-`, string values up to 200 characters; returned on the task and usable as a filter), `idempotency_key` (optional, reuse it on a retry).
- **Company Search Status** (`company-search-status`): Status, stage, progress, cost, and a page of companies for one Company Search or Company Enrich task. Arguments: `task_id` (required), `cursor` (optional, the previous `next_cursor`; omit it to read from the first company, each in its latest version), `limit` (optional, 1 to 100, default 10), `include_companies` (optional, `false` reads only status and cost).
- **Pause Company Search** (`company-search-pause`): Argument: `task_id` (required). A running task finishes its current batch first; companies delivered so far stay readable and the reservation stays as it is. A task paused for more than 7 days is cancelled.
- **Resume Company Search** (`company-search-resume`): Argument: `task_id` (required). Resume is not charged again and works only on a paused task.
- **Cancel Company Search** (`company-search-cancel`): Argument: `task_id` (required). Cancel cannot be undone; the user pays only for the companies already delivered (a search with `max_cost_usd`: its search effort so far when that is more, up to the budget).
- **List Company Search Tasks** (`company-search-tasks`): The user's Company Search and Company Enrich tasks, newest first. Arguments: `type` (`search` or `enrich`), `status` (list, for example `["running", "paused"]`), `limit` (1 to 100), `cursor`, `metadata` (up to 3 labels a task must have, exact match), all optional. People Search tasks are not listed. A new task is refused with 429 while too many People Search and Company Search tasks are queued, running, or paused.

A People Search `task_id` does not work on these tools, and a company `task_id` does not work on the People Search tools.

## Results

Each company has `domain`, `name`, `url`, `industry`, `location`, a short `description`, `score` (0 to 100; `null` for Company Enrich), `why` it matched and up to three `reasons`, `fully_verified` and `unverified_criteria` (Company Search: what its own pages do and do not confirm), `primary_email` and `primary_contact`, `contact_coverage`, public `emails`, `phones`, and `socials` (each with the `source_url` it came from), `leaders` (name, `title`, `roles`, `verified`, LinkedIn profile, and emails), and `enrichment`: each stage (`profile`, `contacts`, `people`, `email_patterns`, `email_check`) as `pending`, `done`, `failed`, or `skipped`, and a `status` that is `partial` while any stage is `pending`, then `complete`. A stage is `skipped` when the request turned it off, it had nothing to do, or the task's time limit cut it (then `enrichment.errors` says so and the task has the `enrichment_time_limit` warning).

Each email has a `verification` status once the checks ran: `valid`, `invalid`, `risky`, or `unknown`. An email with `source` `inferred` is a guess from the company's address pattern, with a `confidence` (`high` or `low`) and the `pattern`; tell the user it is inferred. A missing field means the company did not publish it, not that it has none.

A task shows `max_cost_usd` when it has a budget, `continue_from` when it continues an earlier search, and `only_domains` when its query restricted it to named domains. An ended task has `completion_reason` (why it stopped; `all_domains_processed` for Company Enrich or a search restricted to named domains), `coverage_limited: true` when a limit (`cost_limit`, `candidate_budget`, `time_limit`) stopped it before `count` (more companies may match; see Find more), and `warnings`, each with a `code` and a `message`:

| `code` | Meaning |
|--------|---------|
| `planning_fallback` | The search was planned without AI, so results may be broader. |
| `scope_not_applied` | The query named companies without their websites, so the search was not restricted to them. Give their websites to check only those companies. |
| `ai_scoring_unavailable` | AI scoring was unavailable, so companies were matched by the search's words only. |
| `enrichment_time_limit` | Some companies were not fully enriched before the task's time limit. Their remaining stages are `skipped`. |
| `linkedin_verification_unavailable` | Leaders found through LinkedIn search could not be checked against their LinkedIn profiles. |

Treat a `code` not in this table as information and show its `message`.

The MCP tools do not export files. To download a task as CSV or JSON Lines, use the Desearch Console or `GET /desearch/companies/tasks/{task_id}/export?format=csv` (or `format=jsonl`) on the API. Results stay available for 30 days after a task ends.

## When not to use these tools

Do not start a Company Search for one company the user already names; use `company-enrich` with its domain, or `extract` on its site for the page text. Do not use these tools to find people by what they post (use People Search) or to answer a question about a topic. These tools do not contact the companies or people they find, send email, or change Desearch account settings.
