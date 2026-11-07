# AI Hub — Architecture

**Branch:** `feature/ai-hub` · **Status:** foundation built and tested locally, **not deployed**.

## 1. Phase A audit (what existed)

| Area | Finding | Decision |
|---|---|---|
| Framework | Django 5.2, one app `core` + custom `core/dashboard` (content editor), PostgreSQL in prod, SQLite locally | Add a **separate app `hub`**; reuse `core` for public data |
| Auth | Django auth; `/dashboard/` and `/admin/` for staff; no MFA, no API auth, no DRF | Owner = **superuser**; add TOTP MFA; agent API with device credentials |
| Async | `channels`, `redis` in deps; no Celery worker deployed | No queue needed yet: the **local agent pulls tasks** (outbound polling) |
| Media | `media/` is publicly served (`SERVE_MEDIA`) | Private files go to **`HUB_PRIVATE_ROOT`** (`/usr/src/app/private`, own Docker volume) |
| Deploy | Dokploy auto-deploys `main` | Work on `feature/ai-hub`; merging = deploying, only with approval |
| Public SEO | sitemap, robots, llms.txt, JSON-LD in `core` | `/hub/` disallowed in robots, `noindex` header, never in sitemap/search |

## 2. Components

```
                   Windows PC (owner)                                   Server (Django, Dokploy)
 ┌──────────────────────────────────────────┐            ┌──────────────────────────────────────────────┐
 │ Claude Code ──stdio──▶ mnp-agent mcp      │  HTTPS     │ /hub/api/agent/*  (bearer, 15-min tokens)     │
 │                       (MCP server)        │──────────▶ │   tools.REGISTRY  (fixed allowlist)           │
 │ mnp-agent run  (heartbeat + task loop)    │  outbound  │   ApprovalRequest (single-use, expiring)      │
 │ Windows Credential Manager (device cred)  │   only     │   AuditEvent      (append-only)               │
 │ Browser (YOU sign in & submit)            │            │ /hub/*  owner dashboard (superuser + TOTP)    │
 └──────────────────────────────────────────┘            │ core.*  public portfolio (unchanged)          │
                                                          └──────────────────────────────────────────────┘
```

- **A. Public website**: `core` (unchanged except `Disallow: /hub/` in robots.txt).
- **B. Private AI Hub**: `hub` app, `/hub/` — overview, personal profile, CV & documents, connected accounts, job accounts, job center, preferences, applications (board/table/CSV), AI agent, approvals, activity log, website content (links to the existing dashboard), security.
- **C. Backend API**: `/hub/api/agent/` JSON endpoints (`hub/api.py`).
- **D. Local agent**: `agent/` (`mnp-agent` CLI) — outbound HTTPS only, no listening socket.
- **E. Agent tool interface**: MCP server over **stdio** (`mnp-agent mcp`), 29 tools mirroring the server registry.

## 3. Data model (`hub/models.py`)

| Spec name | Model | Notes |
|---|---|---|
| PersonalProfile | `PrivateFact` + public `core` models | provenance (source, verified_at, status, visibility, sensitive) |
| ProfessionalExperience / Project / Skill | **reused from `core`** (`WorkExperience`, `Portfolio`, `Skill`) | no duplicated records |
| CVDocument | `CVDocument` | market egypt/gulf/general, language, sha256, private storage |
| JobPreference | `JobPreference` | editable from `/hub/jobs/preferences/` |
| ConnectedAccount | `ConnectedAccount` + `Provider` (catalog/capabilities) | permissions per account |
| IntegrationToken | `IntegrationToken` | access/refresh as separate rows, Fernet ciphertext |
| AgentDevice / AgentToolPermission / AgentTask | same names | hashed device secret, per-tool switches, every call recorded |
| Job / JobMatch | same | url hash (unique) + fingerprint for duplicates; transparent breakdown |
| JobApplication / ApplicationDocument | same | one application per job |
| ApprovalRequest | same | bound to action + payload hash, TTL, single use |
| AuditEvent | same | read-only in admin |
| — | `HubSettings` (kill switch), `OwnerMFA` (TOTP) | |

One additive migration: `hub/migrations/0001_initial.py`. No changes to `core` tables.

## 4. Permission model

| Level | Examples | Rule |
|---|---|---|
| READ | profile, CVs, jobs, accounts status | runs if the tool is enabled for the device |
| PREPARE | match analysis, prepare application | same; account `prepare` permission when an account is used |
| WRITE | add job, create draft, request approval, record result | same; account `write` permission when an account is used |
| EXTERNAL | `submit_application` | needs an **approved, unexpired, unused** approval for the **identical payload** |
| CRITICAL | disconnect / revoke account, permission change | agent can only **request**; owner approval executes it |

Owner actions in the dashboard are CSRF-protected POSTs; sensitive ones (register/rotate device, disable MFA, kill switch off) also re-check the password.

## 5. Phases

| Phase | Status |
|---|---|
| A Audit | ✅ (this document) |
| B Dashboard + permission model | ✅ |
| C Personal data + CV management | ✅ (`hub_setup` imports verified CV facts + the Gulf CV) |
| D Connected-account framework | ✅ OAuth (GitHub/GitLab/Google, PKCE, revoke) + job-platform catalog/wizard; **providers need client IDs before use** |
| E Local agent + MCP | ✅ tested end-to-end locally |
| F Job search, matching, tracking | ✅ Remote OK / Greenhouse / Lever public APIs + manual links |
| G Approval center + controlled external actions | ✅ manual hand-off (no platform offers candidate-side submission) |
| H Security tests + docs | ✅ 66 server tests + 17 agent tests + E2E |

Not built yet (next): website-content WRITE tools for the agent, Gmail (restricted scopes need Google verification), WWR RSS connector, Arabic UI for the hub, CV generation to PDF.
