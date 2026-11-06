# Account Integrations

Two screens:
- `/hub/accounts/` — developer/Google accounts via **official OAuth** (GitHub, GitLab, Google).
- `/hub/accounts/jobs/` — **Job accounts & connections**: catalog, capability registry, add-account wizard, health, permissions, emergency stop.

The hub never asks for or stores passwords, one-time codes, recovery codes or cookies. The wizard rejects identifiers that look like them.

## Capability registry (reviewed 2026-11-07)
Being in the catalog ≠ automation exists. Columns are what the provider officially offers a job seeker; **Connector** is what this hub implements; **Last real test** on each account is what was actually verified.

| Platform | Discovery | Submission | Hub connector | Method |
|---|---|---|---|---|
| LinkedIn | no public API | no (partner-only) | — | manual hand-off (scraping/automation prohibited by its terms) |
| Indeed | no (job-seeker API not offered) | no | — | manual |
| Glassdoor | no (API discontinued) | no | — | manual |
| Wuzzuf, Bayt, GulfTalent, Naukrigulf | unknown — no public job-seeker API found | unknown | — | manual |
| Wellfound | no | no | — | manual |
| Remote OK | ✅ public JSON API (must credit/link Remote OK) | no | `remoteok` | API |
| We Work Remotely | ✅ official RSS | no | not yet | manual |
| Greenhouse boards | ✅ public Job Board API per company | API needs the employer's key → manual | `greenhouse` | API (board name) |
| Lever boards | ✅ public Postings API per company | employer key → manual | `lever` | API (site name) |
| Workday / custom career portals | per employer | no | — | manual |
| GitHub / GitLab / Google | — | — | OAuth | read-only scopes (`read:user`, `read_user`, `openid email profile`) |

"Unknown" means not confirmed — treat as manual until an official integration is verified.

## Add-account wizard (`/hub/accounts/jobs/add/`)
1 Platform → 2 Method (only methods the provider allows) → 3 Authorization (OAuth redirect, or a public board name, or nothing for manual) → 4 Permissions (Read / Prepare / Write / Submit — Submit is disabled when the provider has no official submission) → 5 **real connection test** on save → 6 saved with status + verified capabilities.

## Permissions per account
`read`, `prepare`, `write`, `submit` — independent, revocable, `submit` off by default and impossible for providers without official submission. The agent can only *request* changes (`request_job_account_permission`), which you approve in `/hub/approvals/`.

## Health states
Connected · Authorization expired · Access revoked · Provider unavailable · Connection error · Disconnected · Pending — with last success, last failure, last error and the required action. Failed tests are **not retried automatically** (avoids suspicious login activity).

## OAuth setup (when you want it)
Create an OAuth app at each provider with callback `https://mohamednabilpro.deplois.net/hub/accounts/oauth/<github|gitlab|google>/callback/`, then set in Dokploy env:
`HUB_OAUTH_GITHUB_CLIENT_ID/SECRET`, `HUB_OAUTH_GITLAB_CLIENT_ID/SECRET`, `HUB_OAUTH_GOOGLE_CLIENT_ID/SECRET`.
Until then the buttons show "Not configured" — nothing is faked.

Flow: state (single use, 10 min) + PKCE S256 → code exchange → tokens encrypted (access and refresh in separate rows) → real profile check. **Revoke** calls the provider's revocation endpoint (GitHub grant delete, GitLab `/oauth/revoke`, Google `/revoke`) and wipes the ciphertext.

## Local browser-assisted workflow
Implemented as **hand-off only**: the agent opens the official page of an *approved* application in your default browser (`open_application_page`). It does not read cookies, fill forms, solve CAPTCHAs or click submit. Your sessions stay in your browser.
