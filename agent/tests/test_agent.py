import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mnp_agent import audit_log, config as cfg, worker  # noqa: E402
from mnp_agent.client import HubClient, HubError  # noqa: E402
from mnp_agent.connectors import browser_handoff as bh  # noqa: E402
from mnp_agent.security import vault  # noqa: E402
from mnp_agent.tools import registry  # noqa: E402


def resp(status, data):
    r = mock.Mock(status_code=status)
    r.json.return_value = data
    return r


class ConfigTests(unittest.TestCase):
    def write(self, text):
        d = tempfile.mkdtemp()
        p = Path(d) / "config.yaml"
        p.write_text(text, encoding="utf-8")
        return p

    def test_requires_https(self):
        with self.assertRaises(cfg.ConfigError):
            cfg.load(self.write("server_url: http://mohamednabilpro.deplois.net\n"))
        self.assertEqual(cfg.load(self.write("server_url: http://127.0.0.1:8000\n")).server_url, "http://127.0.0.1:8000")

    def test_refuses_secrets_in_config(self):
        with self.assertRaises(cfg.ConfigError):
            cfg.load(self.write("server_url: https://x.example\ndevice_credential: mnpdev_a_b\n"))

    def test_minimum_intervals(self):
        c = cfg.load(self.write("server_url: https://x.example/\npoll_seconds: 1\n"))
        self.assertEqual((c.poll_seconds, c.server_url), (5, "https://x.example"))


class VaultTests(unittest.TestCase):
    def test_no_plaintext_fallback(self):
        from keyring.backends import fail
        with mock.patch("keyring.get_keyring", return_value=fail.Keyring()):
            with self.assertRaises(vault.VaultError):
                vault.save_credential("https://x", "mnpdev_ab_cd")

    def test_rejects_non_credentials(self):
        with self.assertRaises(vault.VaultError):
            vault.save_credential("https://x", "my-password")


class RegistryTests(unittest.TestCase):
    def test_unknown_and_shell_tools_rejected(self):
        for t in ("execute_shell_command", "read_file", "rm"):
            with self.assertRaises(registry.TaskRejected):
                registry.validate_task({"tool": t, "payload": {}})

    def test_external_tools_cannot_be_queued(self):
        with self.assertRaises(registry.TaskRejected):
            registry.validate_task({"tool": "submit_application", "payload": {}})

    def test_payload_must_be_object(self):
        with self.assertRaises(registry.TaskRejected):
            registry.validate_task({"tool": "search_jobs", "payload": ["x"]})


class HandoffTests(unittest.TestCase):
    def test_url_checks(self):
        for bad in ("http://x.example/apply", "javascript:alert(1)", "https://user:pw@x.example/", "file:///C:/Windows"):
            with self.assertRaises(bh.HandoffRefused):
                bh.check_url(bad)
        with self.assertRaises(bh.HandoffRefused):
            bh.check_url("https://evil.example/", ["boards.greenhouse.io"])
        self.assertTrue(bh.check_url("https://job-boards.boards.greenhouse.io/a", ["boards.greenhouse.io"]))

    def test_only_approved_applications_open(self):
        conf = cfg.Config(server_url="https://x.example")
        client = mock.Mock()
        client.call.return_value = {"application": {"status": "draft", "apply_url": "https://jobs.example/1"}}
        opener = mock.Mock()
        with self.assertRaises(bh.HandoffRefused):
            bh.open_application_page(client, {"application_id": 1}, conf, opener)
        opener.assert_not_called()
        client.call.return_value = {"application": {"status": "ready", "apply_url": "https://jobs.example/1"}}
        bh.open_application_page(client, {"application_id": 1}, conf, opener)
        opener.assert_called_once_with("https://jobs.example/1", new=2)


class ClientTests(unittest.TestCase):
    def make(self):
        s = mock.Mock()
        s.headers = {}
        return HubClient("https://x.example", lambda: "mnpdev_ab_secret", session=s), s

    def test_token_exchange_and_request_id(self):
        c, s = self.make()
        s.post.return_value = resp(200, {"ok": True, "access_token": "AT", "expires_in": 900})
        s.request.return_value = resp(200, {"ok": True, "result": {"x": 1}})
        self.assertEqual(c.call("search_jobs", {}), {"x": 1})
        self.assertEqual(s.post.call_args.kwargs["headers"]["Authorization"], "Device mnpdev_ab_secret")
        h = s.request.call_args.kwargs["headers"]
        self.assertEqual(h["Authorization"], "Bearer AT")
        self.assertGreaterEqual(len(h["X-Request-Id"]), 16)
        self.assertFalse(s.request.call_args.kwargs["allow_redirects"])

    def test_single_retry_on_401(self):
        c, s = self.make()
        s.post.return_value = resp(200, {"ok": True, "access_token": "AT", "expires_in": 900})
        s.request.return_value = resp(401, {"ok": False, "error": "unauthorized"})
        with self.assertRaises(HubError):
            c.call("search_jobs")
        self.assertEqual(s.request.call_count, 2)
        self.assertEqual(s.post.call_count, 2)


class WorkerTests(unittest.TestCase):
    def test_execute_success_and_cancel(self):
        conf = cfg.Config(server_url="https://x.example")
        client = mock.Mock()
        client.call.return_value = {"jobs": []}
        client.progress.return_value = {"ok": True, "cancel": False}
        self.assertEqual(worker.execute(client, conf, {"id": "t1", "tool": "search_jobs", "payload": {}}), "succeeded")
        client.progress.return_value = {"ok": True, "cancel": True}
        self.assertEqual(worker.execute(client, conf, {"id": "t2", "tool": "search_jobs", "payload": {}}), "cancelled")

    def test_rejected_task_reported(self):
        client = mock.Mock()
        self.assertEqual(worker.execute(client, cfg.Config(server_url="https://x"), {"id": "t", "tool": "execute_shell_command", "payload": {}}), "rejected")
        client.call.assert_not_called()
        self.assertEqual(client.complete.call_args.args[1], "failed")

    def test_revoked_credential_stops_loop(self):
        client = mock.Mock()
        client.heartbeat.side_effect = HubError("invalid_device_credential", 401)
        self.assertEqual(worker.run(client, cfg.Config(server_url="https://x"), sleep=lambda s: None), 2)


class RedactionTests(unittest.TestCase):
    def test_redacts(self):
        s = audit_log.redact("cred mnpdev_ab12_SeCrEt-x and Bearer 1:2:abc token=xyz")
        for leak in ("SeCrEt", "1:2:abc", "xyz"):
            self.assertNotIn(leak, s)


class McpTests(unittest.TestCase):
    def test_mcp_tools_match_allowlist(self):
        try:
            import asyncio
            from mnp_agent import mcp_server
        except ImportError:
            self.skipTest("mcp not installed")
        names = {t.name for t in asyncio.run(mcp_server.mcp.list_tools())}
        self.assertEqual(names, registry.SERVER_TOOLS | registry.LOCAL_TOOLS)
        self.assertFalse({n for n in names if "shell" in n or n.endswith("_file") or "command" in n})


if __name__ == "__main__":
    unittest.main()
