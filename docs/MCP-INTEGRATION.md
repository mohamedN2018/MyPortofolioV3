# MCP Integration — Claude Code

The hub is exposed to Claude Code through a **local MCP server over stdio** (`mnp-agent mcp`). Claude Code launches it as a child process; it talks to the hub with the device credential from Windows Credential Manager. Opening the website does **not** give Claude Code any access to your PC.

## Add to Claude Code
After `mnp-agent login` works (see `LOCAL-AGENT-SETUP.md`):

```powershell
claude mcp add mnp-hub --scope user -- "F:\4_docker-composer\Django Project\1-Online\MyPortofolioV3\agent\.venv\Scripts\mnp-agent.exe" mcp
```
or in a project `.mcp.json`:
```json
{
  "mcpServers": {
    "mnp-hub": {
      "command": "F:\\4_docker-composer\\Django Project\\1-Online\\MyPortofolioV3\\agent\\.venv\\Scripts\\mnp-agent.exe",
      "args": ["mcp"]
    }
  }
}
```
Check with `/mcp` inside Claude Code — 29 tools should be listed.

## Tools (all map 1:1 to the server registry; a test enforces the match)
| Level | Tools |
|---|---|
| READ | `get_my_profile`, `search_my_projects`, `get_cv_versions`, `get_job_preferences`, `search_jobs`, `get_job_details`, `get_application`, `get_pending_approvals`, `get_agent_status`, `get_activity_history`, `list_job_accounts`, `get_job_account_status`, `get_job_account_capabilities`, `get_job_account_permissions`, `test_job_account_connection`, `search_jobs_from_connected_sources` |
| PREPARE | `analyze_job_match`, `prepare_application`, `prepare_job_application` |
| WRITE | `add_job`, `create_application_draft`, `request_application_approval`, `record_application_result`, `request_job_account_connection`, `request_job_account_permission` |
| EXTERNAL | `submit_application` (needs your approval) · local: `open_application_page` (only for approved applications) |
| CRITICAL (request only) | `disconnect_job_account`, `revoke_job_account_access` |

## Example session
> "Find Django jobs in Saudi Arabia that fit me and prepare the best one."

1. `search_jobs_from_connected_sources` → `search_jobs(market="ksa", min_score=70)`
2. `get_job_details(job_id)` — description arrives marked **untrusted**
3. `prepare_application(job_id, questions=[...])` → flags show what only you can answer
4. `create_application_draft(...)` → `request_application_approval(application_id)`
5. You open `/hub/approvals/`, read the full preview (company, URL, CV, letter, answers), approve.
6. `submit_application(application_id, approval_id)` → `manual_handoff` → `open_application_page` opens the official page; **you** submit.
7. `record_application_result(status="submitted", evidence="confirmation #…")`.

## Verified (2026-11-07, local server)
- MCP stdio handshake + `list_tools` = 29 tools.
- Without a stored credential the tools return `agent_not_configured` (no crash).
- With the credential in Credential Manager: `get_agent_status`, `submit_application` (approved → manual hand-off; second use → `approval_consumed`), `record_application_result` (no evidence → `evidence_required`; with evidence → `submitted`), `get_application`. The test credential was removed afterwards.
