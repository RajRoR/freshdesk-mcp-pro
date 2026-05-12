# Freshdesk MCP Server (Pro Fork)

Fork of [effytech/freshdesk_mcp](https://github.com/effytech/freshdesk_mcp). Adds tools for ticket archaeology and multi-account credentials.

## What's new in this fork

- `get_ticket_full` — fetch ticket + ALL conversations (paginated, no truncation), with requester/agent expansion and status label decoding
- `download_ticket_attachments` — pull every ticket-level + per-conversation attachment to disk
- `extract_inline_images` — resolve `cid:` refs and download `<img>` URLs from description + every conversation body
- `decode_ticket_status` — turn a status integer into its label (custom statuses included)
- Multi-account credentials via `~/.mcp/freshdesk/accounts.json` (env vars still work)

Original feature set (tickets, contacts, agents, groups, companies, solutions, canned responses, ticket fields, contact fields, summaries) remains intact.

> **Heads up — large payloads.** `get_ticket_full` on busy tickets routinely exceeds 256 KB and 25 k tokens. MCP hosts (Claude Code, Claude Desktop) will spill the result to a file. Slice it with `jq` rather than reading the whole thing back into context.

## Install

> Smithery and PyPI publishing for the `-pro` fork are not set up yet. Install directly from GitHub.

### Prerequisites
- Python ≥ 3.10
- `uv` / `uvx` (`pip install uv` or `brew install uv`)
- Freshdesk API key + domain

### Run from GitHub with `uvx`

```bash
uvx --from git+https://github.com/RajRoR/freshdesk-mcp-pro freshdesk-mcp-pro
```

### Editable install for development

```bash
git clone https://github.com/RajRoR/freshdesk-mcp-pro.git
cd freshdesk-mcp-pro
uv pip install -e .
freshdesk-mcp-pro
```

## Credentials

Two ways. The server picks **env vars first**, then falls back to the accounts file.

### Option 1 — env vars

```
FRESHDESK_API_KEY=<key>
FRESHDESK_DOMAIN=yourcompany.freshdesk.com
```

`FRESHDESK_DOMAIN` may be the bare subdomain (`yourcompany`) or the full host (`yourcompany.freshdesk.com`).

### Option 2 — multi-account file

Create `~/.mcp/freshdesk/accounts.json`:

```json
{
  "defaultDomain": "yourcompany",
  "accounts": [
    {
      "domain": "yourcompany",
      "apiKey": "FD_API_KEY_HERE"
    },
    {
      "domain": "another.freshdesk.com",
      "apiKey": "ANOTHER_KEY"
    }
  ]
}
```

Selection rules:
- If `defaultDomain` is set, the matching account is used.
- Otherwise the first account in the list is used.
- Bare subdomains are auto-suffixed with `.freshdesk.com`.

## Usage with Claude Desktop / Claude Code

Add to `claude_desktop_config.json` (or `~/.claude.json` for Claude Code):

```json
{
  "mcpServers": {
    "freshdesk-pro": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/RajRoR/freshdesk-mcp-pro",
        "freshdesk-mcp-pro"
      ],
      "env": {
        "FRESHDESK_API_KEY": "<YOUR_KEY>",
        "FRESHDESK_DOMAIN": "<yourcompany.freshdesk.com>"
      }
    }
  }
}
```

Or omit `env` and rely on `~/.mcp/freshdesk/accounts.json`.

## Tools

### Pro additions (new in this fork)

- **`get_ticket_full`** — full ticket + every conversation, no truncation
  - `ticket_id` (int, required)
  - `include_requester` (bool, default `true`)
  - `include_agent` (bool, default `true`)
  - `decode_status` (bool, default `true`) — adds `status_label`
  - Returns: ticket fields, `conversations[]`, `requester`, `agent`, `status_label`, `attachments_index`

- **`download_ticket_attachments`** — saves ticket-level + per-conversation attachments under `<dest_dir>/<ticket_id>/`
  - `ticket_id` (int, required)
  - `dest_dir` (string, optional; defaults to `/tmp/fd`)
  - `size_limit_mb` (int, default `50`) — per-file cap; larger files are skipped with an error entry

- **`extract_inline_images`** — resolves `cid:` references against attachments and downloads remote `<img src>` URLs from description and every conversation body
  - `ticket_id` (int, required)
  - `dest_dir` (string, optional)
  - `size_limit_mb` (int, default `25`)

- **`decode_ticket_status`** — int status → label (handles custom statuses)
  - `status_id` (int, required)

### Tickets
- `get_tickets` — `page`, `per_page`
- `get_ticket` — `ticket_id`
- `create_ticket` — `subject`, `description`, `source`, `priority`, `status`, optional `email`, `requester_id`, `custom_fields`, `additional_fields`
- `update_ticket` — `ticket_id`, `ticket_fields`
- `delete_ticket` — `ticket_id`
- `search_tickets` — `query`
- `get_ticket_fields`
- `get_ticket_conversation` — `ticket_id`
- `create_ticket_reply` — `ticket_id`, `body`
- `create_ticket_note` — `ticket_id`, `body`
- `update_ticket_conversation` — `conversation_id`, `body`
- `view_ticket_summary` — `ticket_id`
- `update_ticket_summary` — `ticket_id`, `body`
- `delete_ticket_summary` — `ticket_id`

### Ticket fields
- `create_ticket_field` — `ticket_field_fields`
- `view_ticket_field` — `ticket_field_id`
- `update_ticket_field` — `ticket_field_id`, `ticket_field_fields`
- `get_field_properties` — `field_name`

### Agents
- `get_agents` — `page`, `per_page`
- `view_agent` — `agent_id`
- `create_agent` — `agent_fields`
- `update_agent` — `agent_id`, `agent_fields`
- `search_agents` — `query`

### Contacts
- `list_contacts` — `page`, `per_page`
- `get_contact` — `contact_id`
- `search_contacts` — `query`
- `update_contact` — `contact_id`, `contact_fields`

### Contact fields
- `list_contact_fields`
- `view_contact_field` — `contact_field_id`
- `create_contact_field` — `contact_field_fields`
- `update_contact_field` — `contact_field_id`, `contact_field_fields`

### Companies
- `list_companies` — `page`, `per_page`
- `view_company` — `company_id`
- `search_companies` — `query`
- `find_company_by_name` — `name`
- `list_company_fields`

### Groups
- `list_groups` — `page`, `per_page`
- `view_group` — `group_id`
- `create_group` — `group_fields`
- `update_group` — `group_id`, `group_fields`

### Canned responses
- `list_canned_response_folders`
- `list_canned_responses` — `folder_id`
- `view_canned_response` — `canned_response_id`
- `create_canned_response` — `canned_response_fields`
- `update_canned_response` — `canned_response_id`, `canned_response_fields`
- `create_canned_response_folder` — `name`
- `update_canned_response_folder` — `folder_id`, `name`

### Solutions
- `list_solution_categories`
- `view_solution_category` — `category_id`
- `create_solution_category` — `category_fields`
- `update_solution_category` — `category_id`, `category_fields`
- `list_solution_folders` — `category_id`
- `create_solution_category_folder` — `category_id`, `folder_fields`
- `view_solution_category_folder` — `folder_id`
- `update_solution_category_folder` — `folder_id`, `folder_fields`
- `list_solution_articles` — `folder_id`
- `view_solution_article` — `article_id`
- `create_solution_article` — `folder_id`, `article_fields`
- `update_solution_article` — `article_id`, `article_fields`

## Example operations

- "Fetch ticket 63562 with all conversations and attachments, then summarize the RCA"
- "List high-priority tickets created in the last 30 days"
- "Update the status of ticket #12345 to 'Resolved'"
- "Find all tickets from contact a101@acme.com"

## Tips for large tickets

`get_ticket_full` returns everything — every conversation body, every attachment metadata block. On busy tickets that's hundreds of KB.

Workflow that survives the host's 256 KB / 25 k token Read cap:

```bash
# Result is auto-persisted by the host. Slice with jq.
jq -r '.conversations[] | {id, private, incoming, created_at, body_text: (.body_text[:400])}' /path/to/persisted.json
```

Then re-read only the conversation IDs you actually need.

## Troubleshooting

- **`401 Unauthorized`** — wrong API key, or the key belongs to a different domain than `FRESHDESK_DOMAIN`.
- **`404` on `get_ticket`** — ticket archived or in a different account.
- **Empty attachments list** — Freshdesk API does not return attachment URLs for some ticket sources (e.g., portal forms with inline images only). Use `extract_inline_images` to recover those.
- **Rate limits** — Freshdesk caps API at 50–700 calls/minute depending on plan. Pagination loops in `get_ticket_full` respect rate limits but tight loops across many tickets may 429.
- **`uvx` not found** — `pip install uv` or `brew install uv`, then ensure `~/.local/bin` (or equivalent) is on `PATH`.

## Development

```bash
git clone https://github.com/RajRoR/freshdesk-mcp-pro.git
cd freshdesk-mcp-pro
uv sync
uv run freshdesk-mcp-pro
```

Tests live under `tests/`.

## License

MIT — see [LICENSE](LICENSE).

## Credits

Upstream: [effytech/freshdesk_mcp](https://github.com/effytech/freshdesk_mcp) by Gopi Krishnan and Maanaesh Swamy. Pro fork additions by Raj Ayyangar.
