# mnp-agent — local agent for the Mohamed Nabil AI Hub

Outbound-only agent + MCP server that lets Claude Code use your private hub through a fixed list of tools.

```
src/mnp_agent/
  __main__.py          CLI: login | logout | status | tools | run | mcp
  config.py            config.yaml loader (refuses secrets, requires https)
  client.py            HTTPS client: device credential → 15-min token, X-Request-Id on writes
  worker.py            heartbeat + task loop with cancellation and back-off
  mcp_server.py        MCP stdio server (29 tools)
  tools/registry.py    local allowlist (must equal the server registry — tested)
  connectors/browser_handoff.py   opens the official page of an APPROVED application (no automation)
  security/vault.py    Windows Credential Manager via keyring (no plaintext fallback)
  audit_log.py         rotating log with credential/token redaction
tests/test_agent.py    17 unit tests
```

Quick start: see `../docs/LOCAL-AGENT-SETUP.md` and `../docs/MCP-INTEGRATION.md`.

```powershell
py -3.11 -m venv .venv; .venv\Scripts\pip install -e .
copy config.example.yaml $env:USERPROFILE\.mnp-agent\config.yaml
.venv\Scripts\mnp-agent login
claude mcp add mnp-hub --scope user -- "$PWD\.venv\Scripts\mnp-agent.exe" mcp
```

Tests: `.venv\Scripts\python -m unittest discover -s tests`
