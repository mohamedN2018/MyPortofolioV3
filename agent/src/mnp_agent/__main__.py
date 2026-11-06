"""mnp-agent CLI: login | logout | status | tools | run | mcp"""
import argparse
import getpass
import json
import sys

from . import __version__, audit_log
from . import config as cfg
from .client import HubClient, HubError
from .security import vault


def _client(conf):
    return HubClient(conf.server_url, lambda: vault.load_credential(conf.server_url))


def main(argv=None):
    p = argparse.ArgumentParser(prog="mnp-agent", description="Mohamed Nabil AI Hub — local agent")
    p.add_argument("--config", help="Path to config.yaml")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login", help="Store the device credential in Windows Credential Manager")
    sub.add_parser("logout", help="Remove the stored credential (emergency disconnect)")
    sub.add_parser("status", help="Check connection, kill switch and this device")
    sub.add_parser("tools", help="List allowlisted tools")
    sub.add_parser("run", help="Heartbeat + execute tasks assigned in /hub/agent/")
    sub.add_parser("mcp", help="Run the MCP server on stdio (started by Claude Code)")
    sub.add_parser("version")
    a = p.parse_args(argv)

    if a.cmd == "version":
        print(__version__)
        return 0
    if a.cmd == "mcp":
        from .mcp_server import main as mcp_main
        mcp_main()
        return 0
    conf = cfg.load(a.config)
    log = audit_log.setup(conf.log_file)
    if a.cmd == "login":
        cred = getpass.getpass("Paste the device credential from /hub/agent/ (input hidden): ").strip()
        vault.save_credential(conf.server_url, cred)
        try:
            _client(conf).heartbeat("login")
            print("Stored in Windows Credential Manager and verified with the server.")
        except HubError as exc:
            print(f"Stored, but the server refused it: {exc.code}")
            return 1
        return 0
    if a.cmd == "logout":
        vault.delete_credential(conf.server_url)
        print("Credential removed from this computer. Also revoke the device in /hub/agent/ if it may be compromised.")
        return 0
    client = _client(conf)
    try:
        if a.cmd == "status":
            print(json.dumps(client.call("get_agent_status"), indent=2))
        elif a.cmd == "tools":
            for t in client.tools():
                print(f"{t['name']:<38} {t['level']:<9} {'on' if t.get('enabled') else 'OFF'}")
        elif a.cmd == "run":
            from .worker import run
            log.info("agent %s started for %s", __version__, conf.server_url)
            return run(client, conf)
    except HubError as exc:
        print(f"error: {exc.code}", file=sys.stderr)
        return 1
    except vault.VaultError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
