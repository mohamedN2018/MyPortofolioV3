# Local Agent Setup — Windows 11

The agent runs on your PC, connects **out** to the hub over HTTPS and never opens a port.

## 1. Install (once)
```powershell
cd "F:\4_docker-composer\Django Project\1-Online\MyPortofolioV3\agent"
py -3.11 -m venv .venv
.venv\Scripts\pip install -e .
```
Tested with Python 3.11, `mcp 1.30.0`, `keyring 25.6.0` (Windows Credential Manager backend), `requests 2.32.5`, `PyYAML 6.0.2`.

## 2. Configure
```powershell
mkdir $env:USERPROFILE\.mnp-agent
copy config.example.yaml $env:USERPROFILE\.mnp-agent\config.yaml
```
Edit `server_url` (default `https://mohamednabilpro.deplois.net`). The file must not contain secrets — the agent refuses to start if it finds `token`, `password`, `secret`, `credential` or `cookie` keys.

## 3. Register the device
1. Open `/hub/agent/` → **Register device** (asks for your password).
2. Copy the credential `mnpdev_…` — it is shown **once**.
3. On the PC:
```powershell
.venv\Scripts\mnp-agent login      # paste the credential (hidden input) → saved in Windows Credential Manager
.venv\Scripts\mnp-agent status     # should print kill_switch false + your device
.venv\Scripts\mnp-agent tools      # allowlisted tools and whether each is enabled
```

## 4. Run
- **Interactive with Claude Code** — see `docs/MCP-INTEGRATION.md` (Claude Code starts the MCP server itself).
- **Background worker** (picks up tasks you assign in `/hub/agent/`, sends heartbeats):
```powershell
.venv\Scripts\mnp-agent run
```
Optional autostart: Task Scheduler → "At log on" → `…\agent\.venv\Scripts\mnp-agent.exe run`.

## 5. Status, cancel, disconnect
| Need | Do |
|---|---|
| Is it online? | `/hub/agent/` (green dot = heartbeat < 90 s) |
| Cancel a task | `/hub/agent/tasks/<id>/` → Cancel (agent sees it on its next progress report) |
| Disable some tools | `/hub/agent/` → Tool permissions |
| New credential | Rotate credential (old one + all tokens stop working) → `mnp-agent login` again |
| Emergency | `/hub/security/` kill switch, or Revoke device, or `mnp-agent logout` |

Logs: `%USERPROFILE%\.mnp-agent\agent.log` (credentials and bearer tokens are redacted).

## 6. What the agent can never do
Run shell commands, read or write arbitrary files, make arbitrary HTTP requests, read browser cookies/sessions, fill or submit forms on job sites, or approve its own requests.
