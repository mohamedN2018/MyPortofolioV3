# AI Hub — Security

## Threat model in one line
The hub holds private data and can trigger real-world actions, so: **only the owner can see it, the agent can only call a fixed list of operations, and nothing external happens without a fresh, specific approval.**

## Controls

| Threat | Control | Where | Test |
|---|---|---|---|
| Unauthorised access | Every `/hub/` view requires an active **superuser**; staff users get 403 | `security.owner_required` | `AccessControlTests` |
| Password theft | Optional **TOTP 2FA** (RFC 6238, ±30 s, codes can't be replayed); login rate-limited (5 failures / 15 min / IP) | `security.verify_totp`, `views.hub_login` | `MfaTests`, `test_login_rate_limited` |
| CSRF | Django CSRF on all owner POSTs; agent API is bearer-only (no cookies) | — | `test_csrf_enforced_on_owner_posts` |
| Open redirect | `next` must start with `/hub/` and pass `url_has_allowed_host_and_scheme` | `views._next` | `test_login_open_redirect_blocked` |
| IDOR | Single-owner system; agent task endpoints scoped to the calling device | `api._own_task` | `test_other_device_cannot_touch_task` |
| Stolen agent token | Access tokens are signed, **15-minute** TTL, bound to `token_version`; revoke/rotate bumps the version | `security.issue_access_token` | `AgentAuthTests` |
| Stolen device credential | Stored **hashed** (SHA-256) on the server; locally in **Windows Credential Manager**; revoke in one click | `AgentDevice`, `agent/.../vault.py` | `test_token_flow_and_bad_credentials` |
| Replay | Every agent write needs a unique `X-Request-Id`, stored in the DB per device (unique constraint) | `security.agent_required` | `test_replay_blocked` |
| Abuse / loops | DB-backed limits: 120 calls/min/device, 10 token requests / 5 min / IP, 5 failed logins / 15 min / IP; agent backs off exponentially | `rate_limited`, `worker.run` | `test_rate_limit` |
| Remote code execution | **No shell, file or generic HTTP tool** on server or agent; unknown tools → 404; local allowlist double-checks | `tools.REGISTRY`, `agent/.../registry.py` | `test_no_shell_or_file_tools_exist`, agent `RegistryTests` |
| Prompt injection | External text returned as `{"untrusted": true, ...}`; server never interprets it; approvals can't be created or granted by the agent | `tools.untrusted` | `test_prompt_injection_cannot_submit_without_approval` |
| Approval misuse | Approval = owner + specific action + **payload hash** + TTL (60 min) + **single use**; editing the application invalidates it | `ApprovalRequest.consume` | `ApprovalTests` (5 tests) |
| SSRF | Connectors call **fixed HTTPS hosts** only; board names validated `^[a-z0-9-]{1,64}$`; no redirects; 5 MB cap; user job URLs are stored, never fetched | `providers.safe_get` | `test_ssrf_guard`, `test_board_identifier_validated` |
| OAuth attacks | `state` (32 bytes, hashed in session, single use, 10-min TTL, bound to provider), **PKCE S256**, fixed redirect URI from `SITE_URL`, least-privilege read scopes | `hub/oauth.py` | `OAuthTests` |
| Token leakage | Tokens Fernet-encrypted; never rendered, logged or returned; audit details with secret-like keys are redacted; revoke wipes ciphertext | `crypto.py`, `security.audit` | `CryptoTests`, `test_agent_never_receives_tokens` |
| Malicious uploads | PDF/DOCX **magic-byte** check + extension match, 5 MB max, stored outside `MEDIA_ROOT`, downloaded only via authenticated views | `forms.DocumentForm` | `test_upload_validates_magic_bytes_and_serves_privately` |
| XSS | Django autoescape everywhere; job descriptions rendered inside `<pre>` as text | templates | — |
| SQL injection | ORM only | — | — |
| Data leaking to public | `/hub/` in robots `Disallow`, `X-Robots-Tag: noindex`, `Cache-Control: no-store`; context processor returns nothing outside `/hub/` | | `test_robots_disallows_hub_and_public_pages_leak_nothing` |

## Kill switches
- **Global kill switch** (`/hub/security/`): stops new tasks, cancels queued/running ones, revokes **all** agent tokens, expires pending approvals, turns off `write`/`submit` on every account. Audit log kept. Turning it off needs your password; old tokens stay invalid.
- **Emergency stop for job platforms** (`/hub/accounts/jobs/`): disconnects every job account and stops pending tasks.
- **Local**: `mnp-agent logout` removes the credential from this PC.

## Production checklist (before merging)
1. Generate a key: `python manage.py hub_check --new-key` → set `HUB_ENCRYPTION_KEYS` in Dokploy env (keep a copy in your password manager — losing it makes stored tokens unreadable).
2. Deploy, then `python manage.py hub_setup --import-cv` once.
3. Create/confirm your superuser, sign in at `/hub/login/`, **enable 2FA** in `/hub/security/`.
4. `python manage.py hub_check` → must print "All hub security checks passed."
5. Key rotation later: put the new key first (`new,old`), run `hub_check --rotate`, then remove the old key.

## Known limits
- Replay nonces (`AgentNonce`) and rate-limit counters (`RateBucket`) are stored in the database, so they hold across all 25 gunicorn workers (the site's cache is per-process local memory).
- Single-owner design: multi-user roles would need object-level ownership on every model.
