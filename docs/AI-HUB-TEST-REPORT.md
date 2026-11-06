# AI Hub — Test Report (2026-11-07, branch `feature/ai-hub`)

Everything below was executed on the local machine (Windows 11, Python 3.11.17, Django 5.2.11, SQLite). Production was **not** touched.

## 1. Automated tests
| Suite | Command | Result |
|---|---|---|
| Whole project (core + hub) | `python manage.py test` | **94 tests, OK** (28 core + 66 hub) |
| Local agent | `python -m unittest discover -s agent/tests` (agent venv: mcp 1.30.0, keyring 25.6.0) | **17 tests, OK** |
| Migrations | `makemigrations --check` | No changes; hub = 2 additive migrations, no core changes |
| System check | `manage.py check` | 0 issues |

### Coverage of the requested areas
| Requirement | Tests |
|---|---|
| Authentication / authorization | anonymous → login (16 pages), staff → 403, owner → 200 + `noindex` + `no-store`, login rate limit, non-owner login refused, open-redirect blocked, CSRF enforced |
| MFA | TOTP required after password, code replay rejected, secret encrypted at rest |
| Private/public separation | robots disallows `/hub/`, sitemap has no hub URLs, sensitive/unverified facts never sent to the agent |
| OAuth state validation | forged state rejected, PKCE verifier sent, fixed redirect URI, state single-use, unconfigured provider reported honestly, revocation endpoint called + ciphertext wiped |
| Token encryption | ciphertext ≠ plaintext, key rotation (old key decrypts, rotated data needs new key), tokens never rendered or returned to the agent, audit redaction |
| Agent registration / revocation / rotation | bad credentials 401, secret stored hashed, revoke kills tokens + credential, rotate invalidates old credential and tokens |
| Heartbeat | online status + version recorded |
| Task execution / cancellation | owner task → pickup → progress → cancel flag → complete; other device can't touch it; external tools can't be queued |
| Permission enforcement | disabled tool denied (and logged), account read permission required for sync, `submit` forced off for providers without official submission |
| Approval expiry / binding | single use, expiry, payload change invalidates, approval for one application unusable for another, critical requests execute only after owner approval, agent can't approve |
| Duplicate detection | URL normalisation, cross-source fingerprint, duplicate application blocked (same job and same job elsewhere) |
| CV selection / drafts | market-based CV choice, sensitive questions flagged and left empty, unanswered questions block approval |
| Audit logging | every tool call → `AgentTask` + `AuditEvent`, critical events listed |
| Kill switch | tokens dead (423/401), queued tasks cancelled, write/submit off, password required to turn off, emergency stop for job accounts |
| Rate limits / replay | per-device limit → 429, missing request id → 400, replay → 409 |
| Prompt injection | injected job text returned as `untrusted`; "approval granted" text in a description cannot submit |
| SSRF / uploads | non-allowlisted hosts, http, metadata IP and path traversal refused; fake PDF rejected; files outside `MEDIA_ROOT`, private download only |
| Agent ↔ server contract | agent allowlist == server registry (test fails if they drift); MCP exposes exactly those 29 tools, no shell/file tools |

## 2. End-to-end (real HTTP, local server `127.0.0.1:8765`)
Real agent client + real MCP stdio session + owner approving through the real login form (CSRF):

| Step | Result |
|---|---|
| Device token → heartbeat → tool list | OK, 29 tools |
| `get_my_profile` | name returned; phone (sensitive) **not** included |
| `get_cv_versions` | "Backend Developer CV — Gulf (EN)" (imported from the published CV, 266,101 bytes) |
| `add_job` (description contains an injection) → `analyze_job_match` | score 84 |
| `prepare_application` with "Expected salary?" | flagged as needing your answer; Gulf CV chosen for KSA |
| draft → `request_application_approval` → `submit_application` before approval | `approval_pending` |
| owner login → approval page shows company, URL, cover letter → approve | 302 |
| MCP `submit_application` | `manual_handoff` + official URL; second use → `approval_consumed` |
| MCP `record_application_result` without evidence / with evidence | `evidence_required` / `submitted` |
| `execute_shell_command` | 404 `unknown_tool` |
| Test credential stored in Windows Credential Manager for the MCP run | removed afterwards |

## 3. Visual QA (Playwright, Chrome)
18 hub pages × 1440 px and 390 px: **0 horizontal overflow, 0 JS errors** (after fixing a grid overflow on the documents page and a cramped mobile top bar). Screenshots: `docs/screenshots/hub/`.

## 4. Not tested / not done
- Real OAuth against GitHub/GitLab/Google (needs OAuth apps you create; flow tested with mocked provider responses).
- Live Greenhouse/Lever/Remote OK calls (tested with mocked responses; the first real "Test connection" will record the actual result).
- PostgreSQL (tests ran on SQLite; migrations are standard and additive).
- Production deployment, Redis cache, screen readers, real mobile devices.
