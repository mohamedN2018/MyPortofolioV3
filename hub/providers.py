"""
Provider catalog, capability registry and connectors.

Capability values are what the provider officially offers to an individual job
seeker as researched on the `reviewed_at` date. They are NOT proof the hub can
do it: `Provider.connector` says which connector is actually implemented, and
`ConnectedAccount.verified_capabilities` holds the result of a real test.

SSRF protection: connectors only call fixed HTTPS hosts below; user input is
limited to a validated slug inserted into a fixed path. User-provided job URLs
are stored but never fetched by the server.
"""
import re
from datetime import date

import requests
from django.utils import timezone
from django.utils.html import strip_tags

from . import matching
from .models import Job, Provider

REVIEWED = date(2026, 11, 7)
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.lever.co", "remoteok.com",
                 "api.github.com", "gitlab.com", "openidconnect.googleapis.com"}
MAX_BYTES = 5 * 1024 * 1024
UA = "MohamedNabilAIHub/1.0 (+https://mohamednabilpro.deplois.net/)"

S, A, U, K, L = "supported", "assisted", "unsupported", "unknown", "local"

CATALOG = [
    # slug, name, category, website, monogram, capabilities, methods, connector, limitations, docs
    ("linkedin", "LinkedIn", "job_board", "https://www.linkedin.com/jobs/", "in",
     dict(oauth=S, api=U, job_discovery=U, job_details=U, profile_access=S, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["manual"], "",
     "Official OAuth (Sign In with LinkedIn / OpenID Connect) only returns name, photo and email. Job search and Easy Apply have no public API (partner programs only). Automation and scraping are prohibited by LinkedIn's User Agreement → manual handoff only.",
     "https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2"),
    ("indeed", "Indeed", "job_board", "https://www.indeed.com/", "id",
     dict(oauth=U, api=U, job_discovery=U, job_details=U, profile_access=U, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["manual"], "", "Job-seeker APIs are not offered; Indeed Apply is for partner ATSs. Manual handoff only.", ""),
    ("glassdoor", "Glassdoor", "job_board", "https://www.glassdoor.com/", "gd",
     dict(oauth=U, api=U, job_discovery=U, job_details=U, profile_access=U, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["manual"], "", "Public API discontinued. Manual handoff only.", ""),
    ("wuzzuf", "Wuzzuf", "job_board", "https://wuzzuf.net/", "wz",
     dict(oauth=K, api=K, job_discovery=K, job_details=K, profile_access=K, draft_preparation=L, submission=K, status_tracking=K, user_assisted=A),
     ["manual"], "", "No public job-seeker API found. Manual handoff until an official integration is confirmed.", ""),
    ("bayt", "Bayt", "job_board", "https://www.bayt.com/", "by",
     dict(oauth=K, api=K, job_discovery=K, job_details=K, profile_access=K, draft_preparation=L, submission=K, status_tracking=K, user_assisted=A),
     ["manual"], "", "No public job-seeker API found. Manual handoff.", ""),
    ("gulftalent", "GulfTalent", "job_board", "https://www.gulftalent.com/", "gt",
     dict(oauth=K, api=K, job_discovery=K, job_details=K, profile_access=K, draft_preparation=L, submission=K, status_tracking=K, user_assisted=A),
     ["manual"], "", "No public job-seeker API found. Manual handoff.", ""),
    ("naukrigulf", "Naukrigulf", "job_board", "https://www.naukrigulf.com/", "ng",
     dict(oauth=K, api=K, job_discovery=K, job_details=K, profile_access=K, draft_preparation=L, submission=K, status_tracking=K, user_assisted=A),
     ["manual"], "", "No public job-seeker API found. Manual handoff.", ""),
    ("wellfound", "Wellfound", "job_board", "https://wellfound.com/jobs", "wf",
     dict(oauth=K, api=U, job_discovery=U, job_details=U, profile_access=U, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["manual"], "", "No public API. Manual handoff.", ""),
    ("remoteok", "Remote OK", "job_board", "https://remoteok.com/", "ro",
     dict(oauth=U, api=S, job_discovery=S, job_details=S, profile_access=U, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["api"], "remoteok",
     "Public JSON feed (https://remoteok.com/api). Terms require linking back to Remote OK and crediting it as the source. Applying happens on each employer's page → manual handoff.",
     "https://remoteok.com/api"),
    ("weworkremotely", "We Work Remotely", "job_board", "https://weworkremotely.com/", "wr",
     dict(oauth=U, api=S, job_discovery=S, job_details=S, profile_access=U, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["manual"], "", "Official RSS feeds exist per category; hub connector not implemented yet.", "https://weworkremotely.com/remote-job-rss-feed"),
    ("greenhouse", "Greenhouse (company boards)", "ats", "https://www.greenhouse.com/", "gh",
     dict(oauth=U, api=S, job_discovery=S, job_details=S, profile_access=U, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["api"], "greenhouse",
     "Public Job Board API: GET boards/{board_token}/jobs. Submitting applications through the API needs the EMPLOYER's API key, so candidates apply on the official page (manual handoff). Add one account per company board token.",
     "https://developers.greenhouse.io/job-board.html"),
    ("lever", "Lever (company boards)", "ats", "https://www.lever.co/", "lv",
     dict(oauth=U, api=S, job_discovery=S, job_details=S, profile_access=U, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["api"], "lever",
     "Public Postings API: GET v0/postings/{site}. API applications require the employer's key → manual handoff. One account per company site name.",
     "https://github.com/lever/postings-api"),
    ("workday", "Workday (company portals)", "ats", "https://www.workday.com/", "wd",
     dict(oauth=U, api=U, job_discovery=K, job_details=K, profile_access=U, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["manual"], "", "No candidate API. Each employer runs its own portal → manual handoff.", ""),
    ("career-portal", "Company career portal (custom)", "career_portal", "https://mohamednabilpro.deplois.net/", "cp",
     dict(oauth=U, api=U, job_discovery=K, job_details=K, profile_access=U, draft_preparation=L, submission=U, status_tracking=U, user_assisted=A),
     ["manual"], "", "Add the company's careers URL; jobs are added by URL and applications are completed by you on the official page.", ""),
    ("github", "GitHub", "developer", "https://github.com/", "GH",
     dict(oauth=S, api=S, profile_access=S, job_discovery=U, submission=U, user_assisted=U),
     ["oauth"], "github", "OAuth App with read-only scope `read:user`. Configure HUB_OAUTH_GITHUB_CLIENT_ID / _SECRET.", "https://docs.github.com/en/apps/oauth-apps"),
    ("gitlab", "GitLab", "developer", "https://gitlab.com/", "GL",
     dict(oauth=S, api=S, profile_access=S, job_discovery=U, submission=U, user_assisted=U),
     ["oauth"], "gitlab", "OAuth application with scope `read_user` + PKCE. Configure HUB_OAUTH_GITLAB_CLIENT_ID / _SECRET.", "https://docs.gitlab.com/api/oauth2/"),
    ("google", "Google account", "google", "https://myaccount.google.com/", "G",
     dict(oauth=S, api=S, profile_access=S, job_discovery=U, submission=U, user_assisted=U),
     ["oauth"], "google", "OpenID Connect (openid email profile) only. Gmail scopes are restricted and NOT requested in this phase.", "https://developers.google.com/identity/protocols/oauth2"),
]


def seed_catalog():
    created = 0
    for i, (slug, name, cat, site, mono, caps, methods, connector, limits, docs) in enumerate(CATALOG):
        _, was_created = Provider.objects.update_or_create(slug=slug, defaults=dict(
            name=name, category=cat, website=site, logo_text=mono, capabilities=caps, connection_methods=methods,
            connector=connector, limitations=limits, docs_url=docs, reviewed_at=REVIEWED, order=i))
        created += was_created
    return created


# ------------------------------------------------------------------ HTTP
class ConnectorError(Exception):
    pass


def safe_get(url, *, headers=None, params=None):
    host = requests.utils.urlparse(url).hostname
    if not url.startswith("https://") or host not in ALLOWED_HOSTS:
        raise ConnectorError("host_not_allowed")
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/json", **(headers or {})},
                         params=params, timeout=15, allow_redirects=False, stream=True)
        body = r.raw.read(MAX_BYTES + 1, decode_content=True)
    except requests.RequestException as exc:
        raise ConnectorError(f"network_error: {exc.__class__.__name__}") from exc
    if len(body) > MAX_BYTES:
        raise ConnectorError("response_too_large")
    r._content = body
    return r


def _clean(text, limit=20000):
    return strip_tags(text or "").replace("\x00", "").strip()[:limit]


def _board_slug(account):
    slug = (account.config.get("board") or account.account_identifier or "").strip().lower()
    if not SLUG_RE.match(slug):
        raise ConnectorError("invalid_board_identifier")
    return slug


def _guess_mode(text):
    t = (text or "").lower()
    return "remote" if "remote" in t else "hybrid" if "hybrid" in t else "unknown"


# ------------------------------------------------------------------ connectors
def _greenhouse_fetch(account):
    r = safe_get(f"https://boards-api.greenhouse.io/v1/boards/{_board_slug(account)}/jobs", params={"content": "true"})
    if r.status_code == 404:
        raise ConnectorError("board_not_found")
    if r.status_code != 200:
        raise ConnectorError(f"provider_http_{r.status_code}")
    for j in r.json().get("jobs", []):
        loc = (j.get("location") or {}).get("name", "")
        yield dict(title=j.get("title", ""), company=account.label or account.account_identifier, location=loc,
                   url=j.get("absolute_url", ""), description=_clean(j.get("content")), work_mode=_guess_mode(loc))


def _lever_fetch(account):
    r = safe_get(f"https://api.lever.co/v0/postings/{_board_slug(account)}", params={"mode": "json"})
    if r.status_code == 404:
        raise ConnectorError("board_not_found")
    if r.status_code != 200:
        raise ConnectorError(f"provider_http_{r.status_code}")
    for j in r.json():
        cats = j.get("categories") or {}
        yield dict(title=j.get("text", ""), company=account.label or account.account_identifier, location=cats.get("location", ""),
                   url=j.get("hostedUrl", ""), description=_clean(j.get("descriptionPlain") or j.get("description")),
                   work_mode=(j.get("workplaceType") or "unknown").replace("on-site", "onsite"), employment_type=cats.get("commitment", ""))


def _remoteok_fetch(account):
    r = safe_get("https://remoteok.com/api")
    if r.status_code != 200:
        raise ConnectorError(f"provider_http_{r.status_code}")
    for j in r.json()[1:]:  # element 0 is the legal notice
        yield dict(title=j.get("position", ""), company=j.get("company", ""), location=j.get("location", "") or "Remote",
                   url=j.get("url", ""), description=_clean(j.get("description")), work_mode="remote",
                   required_skills=[t for t in (j.get("tags") or [])][:20],
                   salary_text=(f"{j['salary_min']}–{j['salary_max']} USD" if j.get("salary_min") and j.get("salary_max") else ""))


FETCHERS = {"greenhouse": _greenhouse_fetch, "lever": _lever_fetch, "remoteok": _remoteok_fetch}


def _profile_check(account):
    token = account.token("access")
    if not token:
        raise ConnectorError("not_authorized")
    url = {"github": "https://api.github.com/user", "gitlab": "https://gitlab.com/api/v4/user",
           "google": "https://openidconnect.googleapis.com/v1/userinfo"}[account.provider.connector]
    r = safe_get(url, headers={"Authorization": f"Bearer {token}"})
    if r.status_code == 401:
        raise ConnectorError("authorization_expired")
    if r.status_code != 200:
        raise ConnectorError(f"provider_http_{r.status_code}")
    data = r.json()
    return {"identity": data.get("login") or data.get("username") or data.get("email") or ""}


def test_connection(account):
    """Runs a REAL check and records what actually works. Returns (ok, report)."""
    p = account.provider
    report = {"tested_at": timezone.now().isoformat(), "method": account.method}
    try:
        if account.method in ("manual", "browser_local") or not p.connector:
            report.update(note="No automated connector: jobs are added by URL and you apply on the official page.",
                          job_discovery="manual", submission="manual_handoff")
            ok = True
        elif p.connector in FETCHERS:
            jobs = list(FETCHERS[p.connector](account))
            report.update(job_discovery="verified", job_details="verified", jobs_visible=len(jobs), submission="manual_handoff")
            ok = True
        else:
            report.update(profile_access="verified", **_profile_check(account))
            ok = True
        account.status, account.last_error, account.required_action = "connected", "", ""
        account.last_success_at = timezone.now()
    except ConnectorError as exc:
        ok = False
        code = str(exc)
        report["error"] = code
        account.status = "expired" if code == "authorization_expired" else "error"
        account.last_error, account.last_failure_at = code, timezone.now()
        account.required_action = "Reconnect the account" if code in ("authorization_expired", "not_authorized") else "Check the identifier and test again"
    account.verified_capabilities = report
    account.save()
    return ok, report


def discover_jobs(account, limit=200):
    """Pull jobs from a connected public-API source into the Job table (deduplicated)."""
    p = account.provider
    if p.connector not in FETCHERS:
        raise ConnectorError("discovery_not_supported_for_provider")
    created = updated = 0
    for raw in list(FETCHERS[p.connector](account))[:limit]:
        if not raw.get("url", "").startswith("https://") or not raw.get("title"):
            continue
        job, was_created = upsert_job(source=p.slug, provider=p, **raw)
        created += was_created
        updated += not was_created
    account.last_sync_at = timezone.now()
    account.save(update_fields=["last_sync_at"])
    return {"created": created, "updated": updated}


def upsert_job(*, url, title, company, source, **fields):
    allowed = {f.name for f in Job._meta.get_fields()}
    data = {k: v for k, v in fields.items() if k in allowed and v not in (None, "")}
    if data.get("work_mode") not in dict(Job.WORK_MODE):
        data["work_mode"] = "unknown"
    h = matching.url_hash(url)
    job = Job.objects.filter(url_hash=h).first()
    created = job is None
    job = job or Job(url_hash=h)
    job.url, job.title, job.company, job.source = url[:600], title[:200], company[:160], source
    for k, v in data.items():
        setattr(job, k, v)
    job.fingerprint = matching.fingerprint(job.company, job.title, job.location)
    if not job.required_skills:
        job.required_skills = matching.extract_skills(job.description)
    job.save()
    matching.compute(job)
    return job, created


def find_duplicates(job):
    return Job.objects.filter(fingerprint=job.fingerprint).exclude(pk=job.pk)
