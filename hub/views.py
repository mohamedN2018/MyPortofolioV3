"""Private dashboard (/hub/). Every view is owner-only (superuser + optional TOTP)."""
import csv
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from . import control, matching, oauth, providers, tools
from .crypto import encrypt, explicit_key_configured, sha256_hex
from .forms import AccountForm, DocumentForm, FactForm, JobForm, PreferenceForm, TaskForm
from .models import (AgentDevice, AgentTask, AgentToolPermission, ApprovalRequest, AuditEvent, ConnectedAccount,
                     CVDocument, HubSettings, Job, JobApplication, JobPreference, Level, OwnerMFA, PrivateFact, Provider)
from .security import (MFA_SESSION_KEY, audit, client_ip, is_owner, limit_reached, new_totp_secret, owner_required, rate_limited,
                       totp_uri, verify_totp)


def _next(request, default="hub:overview"):
    nxt = request.POST.get("next") or request.GET.get("next")
    if nxt and nxt.startswith("/hub/") and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return nxt
    return reverse(default)


def _confirm_password(request):
    ok = request.user.check_password(request.POST.get("confirm_password", ""))
    if not ok:
        messages.error(request, "Password confirmation failed.")
        audit("password_confirmation_failed", request=request, outcome="denied")
    return ok


# ------------------------------------------------------------------ auth
def hub_login(request):
    if is_owner(request.user) and (request.session.get(MFA_SESSION_KEY) or not OwnerMFA.objects.filter(user=request.user, enabled=True).exists()):
        return redirect(_next(request))
    error = ""
    if request.method == "POST":
        ip = client_ip(request) or "unknown"
        if limit_reached(f"hub-login:{ip}", 5, 900):
            error = "Too many attempts. Try again in 15 minutes."
            audit("login_rate_limited", request=request, outcome="denied")
        else:
            user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
            if user and is_owner(user):
                login(request, user)
                request.session.cycle_key()
                request.session[MFA_SESSION_KEY] = False
                audit("login", request=request, user=user)
                if OwnerMFA.objects.filter(user=user, enabled=True).exists():
                    return redirect(f"{reverse('hub:mfa')}?next={_next(request)}")
                return redirect(_next(request))
            error = "Invalid credentials."
            rate_limited(f"hub-login:{ip}", 5, 900)  # count failures only
            audit("login_failed", request=request, outcome="denied", username=request.POST.get("username", "")[:60])
    resp = render(request, "hub/login.html", {"error": error, "next": request.GET.get("next", "")})
    resp["X-Robots-Tag"] = "noindex, nofollow"
    return resp


def hub_mfa(request):
    if not is_owner(request.user):
        return redirect("hub:login")
    mfa = OwnerMFA.objects.filter(user=request.user, enabled=True).first()
    if not mfa:
        return redirect(_next(request))
    error = ""
    if request.method == "POST":
        if limit_reached(f"hub-mfa:{request.user.pk}", 5, 300):
            error = "Too many attempts. Wait 5 minutes."
        elif verify_totp(mfa, request.POST.get("code", "")):
            request.session[MFA_SESSION_KEY] = True
            audit("mfa_verified", request=request)
            return redirect(_next(request))
        else:
            error = "Invalid code."
            rate_limited(f"hub-mfa:{request.user.pk}", 5, 300)
            audit("mfa_failed", request=request, outcome="denied")
    return render(request, "hub/mfa.html", {"error": error, "next": request.GET.get("next", "")})


@require_POST
def hub_logout(request):
    if request.user.is_authenticated:
        audit("logout", request=request)
    logout(request)
    return redirect("hub:login")


# ------------------------------------------------------------------ overview
@owner_required
def overview(request):
    devices = AgentDevice.objects.filter(is_revoked=False)
    apps = dict(JobApplication.objects.values_list("status").annotate(n=Count("id")))
    ctx = {
        "devices": devices, "online": [d for d in devices if d.online],
        "pending": ApprovalRequest.objects.filter(status="pending").count(),
        "running": AgentTask.objects.filter(status="running").select_related("device")[:5],
        "failed": AgentTask.objects.filter(status__in=["failed", "denied"]).select_related("device")[:5],
        "apps": apps, "app_total": sum(apps.values()),
        "jobs": Job.objects.filter(archived=False).count(),
        "top_jobs": Job.objects.filter(archived=False, match__isnull=False).select_related("match").order_by("-match__score")[:5],
        "accounts": ConnectedAccount.objects.select_related("provider"),
        "events": AuditEvent.objects.select_related("device")[:10],
        "key_ok": explicit_key_configured(),
    }
    return render(request, "hub/overview.html", ctx)


# ------------------------------------------------------------------ personal data
@owner_required
def profile(request, pk=None):
    from core import identity
    fact = get_object_or_404(PrivateFact, pk=pk) if pk else None
    form = FactForm(request.POST or None, instance=fact)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        audit("fact_saved", request=request, level="write", target=obj)
        messages.success(request, "Saved.")
        return redirect("hub:profile")
    facts = PrivateFact.objects.all()
    return render(request, "hub/profile.html", {"form": form, "editing": fact, "facts": facts,
                                                "identity": identity, "profiles": identity.get_profiles(),
                                                "skills": sorted(matching.verified_skills())})


@owner_required
@require_POST
def fact_delete(request, pk):
    fact = get_object_or_404(PrivateFact, pk=pk)
    if request.POST.get("confirm") != "DELETE":
        messages.error(request, "Type DELETE to confirm.")
        return redirect("hub:profile")
    audit("fact_deleted", request=request, level="critical", target=fact, key=f"{fact.section}:{fact.key}")
    fact.delete()
    messages.success(request, "Deleted.")
    return redirect("hub:profile")


@owner_required
def documents(request, pk=None):
    doc = get_object_or_404(CVDocument, pk=pk) if pk else None
    form = DocumentForm(request.POST or None, request.FILES or None, instance=doc)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        if "file" in request.FILES:
            f = request.FILES["file"]
            import hashlib
            h = hashlib.sha256()
            for chunk in f.chunks():
                h.update(chunk)
            obj.sha256 = h.hexdigest()
            f.seek(0)
        elif obj.text_content:
            obj.sha256 = sha256_hex(obj.text_content)
        obj.save()
        if obj.is_default:
            CVDocument.objects.filter(kind=obj.kind, market=obj.market, language=obj.language).exclude(pk=obj.pk).update(is_default=False)
        audit("document_saved", request=request, level="write", target=obj)
        messages.success(request, "Document saved.")
        return redirect("hub:documents")
    return render(request, "hub/documents.html", {"form": form, "editing": doc, "docs": CVDocument.objects.all()})


@owner_required
def document_download(request, pk):
    doc = get_object_or_404(CVDocument, pk=pk)
    if not doc.file:
        raise Http404
    audit("document_downloaded", request=request, target=doc)
    return FileResponse(doc.file.open("rb"), as_attachment=True, filename=doc.file.name.rsplit("/", 1)[-1])


@owner_required
@require_POST
def document_toggle(request, pk):
    doc = get_object_or_404(CVDocument, pk=pk)
    doc.is_active = not doc.is_active
    doc.save(update_fields=["is_active"])
    audit("document_toggled", request=request, level="write", target=doc, active=doc.is_active)
    return redirect("hub:documents")


@owner_required
def preferences(request):
    pref = JobPreference.active() or JobPreference(name="Default")
    form = PreferenceForm(request.POST or None, instance=pref)
    if request.method == "POST" and form.is_valid():
        form.save()
        for job in Job.objects.filter(archived=False):
            matching.compute(job)
        audit("preferences_saved", request=request, level="write")
        messages.success(request, "Preferences saved and all match scores recalculated.")
        return redirect("hub:preferences")
    return render(request, "hub/preferences.html", {"form": form})


# ------------------------------------------------------------------ jobs
@owner_required
def jobs(request):
    qs = Job.objects.filter(archived=False).select_related("match", "application")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(company__icontains=q) | Q(location__icontains=q))
    if request.GET.get("market"):
        qs = qs.filter(market=request.GET["market"])
    page = Paginator(qs.order_by("-match__score", "-discovered_at"), 25).get_page(request.GET.get("page"))
    form = JobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        job, created = providers.upsert_job(url=d.pop("url"), title=d.pop("title"), company=d.pop("company"), source="manual", **d)
        audit("job_added", request=request, level="write", target=job, created=created)
        dup = providers.find_duplicates(job)
        messages.success(request, "Job saved." + (" Possible duplicate of an existing job — check it." if dup else "") + ("" if created else " (Already existed — updated.)"))
        return redirect("hub:job", pk=job.pk)
    return render(request, "hub/jobs.html", {"page": page, "form": form, "q": q,
                                             "sources": ConnectedAccount.objects.filter(provider__connector__in=list(providers.FETCHERS)).select_related("provider")})


@owner_required
def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related("match"), pk=pk)
    if not hasattr(job, "match"):
        matching.compute(job)
        job.refresh_from_db()
    return render(request, "hub/job.html", {"job": job, "dupes": providers.find_duplicates(job),
                                            "app": JobApplication.objects.filter(job=job).first()})


@owner_required
@require_POST
def job_prepare(request, pk):
    job = get_object_or_404(Job, pk=pk)
    try:
        draft = tools.prepare_application(None, {"job_id": job.pk})
        app = tools.create_application_draft(None, {"job_id": job.pk, "cv_id": (draft["cv"] or {}).get("id"),
                                                     "cover_letter": draft["cover_letter"], "answers": draft["answers"], "flags": draft["flags"]})
    except tools.ToolError as exc:
        messages.error(request, f"Not prepared: {exc.code.replace('_', ' ')}")
        return redirect("hub:job", pk=pk)
    audit("application_prepared", request=request, level="prepare", target=job)
    messages.success(request, "Draft prepared. Review it before requesting approval.")
    return redirect("hub:application", pk=app["application_id"])


@owner_required
@require_POST
def job_archive(request, pk):
    job = get_object_or_404(Job, pk=pk)
    job.archived = True
    job.save(update_fields=["archived"])
    audit("job_archived", request=request, level="write", target=job)
    return redirect("hub:jobs")


@owner_required
@require_POST
def jobs_sync(request, account_pk):
    acc = get_object_or_404(ConnectedAccount, pk=account_pk)
    if not acc.allowed("read"):
        messages.error(request, "This account is not connected or its Read permission is off.")
        return redirect("hub:jobs")
    try:
        res = providers.discover_jobs(acc)
        messages.success(request, f"{acc}: {res['created']} new, {res['updated']} updated.")
        audit("jobs_synced", request=request, target=acc, **res)
    except providers.ConnectorError as exc:
        messages.error(request, f"{acc}: {exc}")
        audit("jobs_sync_failed", request=request, target=acc, outcome="error", error=str(exc))
    return redirect("hub:jobs")


# ------------------------------------------------------------------ applications
@owner_required
def applications(request):
    qs = JobApplication.objects.select_related("job", "cv", "account__provider")
    columns = [(key, label, [a for a in qs if a.status == key]) for key, label in JobApplication.STATUS]
    return render(request, "hub/applications.html", {"columns": columns, "apps": qs, "view": request.GET.get("view", "board")})


@owner_required
def applications_csv(request):
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="applications.csv"'
    resp.write("﻿")
    w = csv.writer(resp)
    w.writerow(["id", "status", "company", "title", "source", "url", "cv", "applied_at", "follow_up", "updated"])
    for a in JobApplication.objects.select_related("job", "cv"):
        w.writerow([a.pk, a.get_status_display(), a.job.company, a.job.title, a.job.source, a.job.url,
                    a.cv.title if a.cv else "", a.applied_at or "", a.follow_up_at or "", a.updated_at])
    audit("applications_exported", request=request)
    return resp


@owner_required
def application_detail(request, pk):
    app = get_object_or_404(JobApplication.objects.select_related("job", "cv", "account__provider"), pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_draft" and app.status in ("discovered", "analyzed", "shortlisted", "draft", "awaiting_approval"):
            app.cover_letter = request.POST.get("cover_letter", "")[:10000]
            try:
                answers = json.loads(request.POST.get("answers") or "{}")
                assert isinstance(answers, dict)
                app.answers = answers
            except (ValueError, AssertionError):
                messages.error(request, "Answers must be a JSON object.")
                return redirect("hub:application", pk=pk)
            cv_id = request.POST.get("cv")
            app.cv = CVDocument.objects.filter(pk=cv_id, kind="cv").first() if cv_id else None
            if app.status == "awaiting_approval":  # editing invalidates the pending approval
                app.approvals.filter(status__in=["pending", "approved"]).update(status="expired")
            app.status = "draft"
            app.save()
            audit("application_edited", request=request, level="write", target=app)
            messages.success(request, "Draft saved.")
        elif action == "request_approval":
            try:
                res = tools.request_application_approval(None, {"application_id": app.pk})
                messages.success(request, "Approval request created.")
                return redirect("hub:approval", pk=res["approval_id"])
            except tools.ToolError as exc:
                messages.error(request, f"Cannot request approval: {exc.code.replace('_', ' ')} {exc.extra.get('questions', '')}")
        elif action == "status":
            new = request.POST.get("status")
            if new == "submitted" and not request.POST.get("evidence"):
                messages.error(request, "Add evidence (confirmation email, reference number…) to mark as submitted.")
            elif new in dict(JobApplication.STATUS) and new not in ("awaiting_approval", "ready"):
                app.status = new
                if new == "submitted" and not app.applied_at:
                    app.applied_at = timezone.now()
                if request.POST.get("evidence"):
                    app.submission_evidence = (app.submission_evidence + "\n" if app.submission_evidence else "") + request.POST["evidence"][:2000]
                app.follow_up_at = request.POST.get("follow_up_at") or app.follow_up_at
                if request.POST.get("notes"):
                    app.notes = request.POST["notes"][:5000]
                app.save()
                audit("application_status", request=request, level="write", target=app, status=new)
                messages.success(request, "Status updated.")
        return redirect("hub:application", pk=pk)
    return render(request, "hub/application.html", {"app": app, "cvs": CVDocument.objects.filter(kind="cv", is_active=True),
                                                    "answers_json": json.dumps(app.answers, ensure_ascii=False, indent=2),
                                                    "statuses": [s for s in JobApplication.STATUS if s[0] not in ("awaiting_approval", "ready")]})


# ------------------------------------------------------------------ accounts (developer / google)
@owner_required
def integrations(request):
    provs = Provider.objects.filter(category__in=["developer", "google"]).prefetch_related("accounts")
    return render(request, "hub/integrations.html", {"providers": [(p, oauth.configured(p.connector), p.accounts.all()) for p in provs]})


@owner_required
@require_POST
def oauth_start(request, slug):
    p = get_object_or_404(Provider, slug=slug)
    if "oauth" not in p.connection_methods:
        raise Http404
    acc = ConnectedAccount.objects.filter(provider=p, method="oauth").first() or \
        ConnectedAccount.objects.create(provider=p, method="oauth", account_identifier=f"{p.slug}-oauth", label=p.name,
                                        permissions={"read": True})
    try:
        url = oauth.start(request, acc)
    except oauth.OAuthError as exc:
        messages.error(request, f"{p.name}: {exc} — set HUB_OAUTH_{p.connector.upper()}_CLIENT_ID / _SECRET in the server environment.")
        return redirect(_next(request, "hub:integrations"))
    audit("oauth_started", request=request, target=acc)
    return redirect(url)


@owner_required
def oauth_callback(request, key):
    try:
        acc = oauth.finish(request, key, state=request.GET.get("state", ""), code=request.GET.get("code", ""), error=request.GET.get("error", ""))
    except oauth.OAuthError as exc:
        audit("oauth_failed", request=request, outcome="denied", provider=key, reason=str(exc))
        messages.error(request, f"Authorization failed: {exc}")
        return redirect("hub:integrations")
    audit("oauth_connected", request=request, target=acc, scopes=acc.scopes)
    providers.test_connection(acc)
    messages.success(request, f"{acc.provider.name} connected with scopes: {', '.join(acc.scopes)}")
    return redirect("hub:account", pk=acc.pk)


# ------------------------------------------------------------------ job accounts
@owner_required
def job_accounts(request):
    provs = Provider.objects.exclude(category__in=["developer", "google"])
    accounts = ConnectedAccount.objects.select_related("provider").exclude(provider__category__in=["developer", "google"])
    from .models import CAPABILITIES
    return render(request, "hub/job_accounts.html", {
        "providers": provs, "connected": [a for a in accounts if a.status == "connected"],
        "other": [a for a in accounts if a.status != "connected"], "capabilities": CAPABILITIES})


@owner_required
def job_account_add(request, slug=None):
    if not slug:
        return render(request, "hub/job_account_add.html", {"providers": Provider.objects.exclude(category__in=["developer", "google"]), "step": 1})
    p = get_object_or_404(Provider.objects.exclude(category__in=["developer", "google"]), slug=slug)
    form = AccountForm(p, request.POST or None)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        acc, created = ConnectedAccount.objects.get_or_create(provider=p, account_identifier=d["account_identifier"],
                                                              defaults={"method": d["method"]})
        acc.method, acc.label = d["method"], d["label"] or acc.label
        if acc.method == "api" and p.connector in ("greenhouse", "lever"):
            acc.config = {"board": d["account_identifier"]}
        acc.permissions, acc.status = form.permissions(), "pending"
        acc.save()
        audit("job_account_added" if created else "job_account_updated", request=request, level="write", target=acc, permissions=acc.permissions)
        ok, report = providers.test_connection(acc)
        messages.success(request, "Connected and tested." if ok else f"Saved, but the test failed: {report.get('error')}")
        return redirect("hub:account", pk=acc.pk)
    return render(request, "hub/job_account_add.html", {"provider": p, "form": form, "step": 2})


@owner_required
def account_detail(request, pk):
    acc = get_object_or_404(ConnectedAccount.objects.select_related("provider"), pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "permissions":
            new = {perm: bool(request.POST.get(f"perm_{perm}")) for perm in ConnectedAccount.PERMISSIONS}
            new["submit"] = new["submit"] and acc.provider.can_submit
            acc.permissions = new
            acc.save(update_fields=["permissions"])
            audit("account_permissions_changed", request=request, level="critical", target=acc, permissions=new)
            messages.success(request, "Permissions updated.")
        elif action == "test":
            ok, report = providers.test_connection(acc)
            audit("account_tested", request=request, target=acc, outcome="ok" if ok else "error", result=report.get("error", "ok"))
            messages.success(request, "Connection works.") if ok else messages.error(request, f"Test failed: {report.get('error')}")
        elif action == "disconnect":
            acc.status, acc.permissions = "disconnected", {}
            acc.save(update_fields=["status", "permissions"])
            audit("account_disconnected", request=request, level="critical", target=acc)
            messages.success(request, "Disconnected. Tokens kept encrypted until you revoke.")
        elif action == "revoke":
            result = oauth.revoke(acc)
            audit("account_revoked", request=request, level="critical", target=acc, result=result)
            messages.success(request, f"Access revoked ({result.replace('_', ' ')}).")
        elif action == "reconnect":
            if acc.method == "oauth":
                try:
                    return redirect(oauth.start(request, acc))
                except oauth.OAuthError as exc:
                    messages.error(request, str(exc))
            else:
                ok, report = providers.test_connection(acc)
                messages.success(request, "Reconnected.") if ok else messages.error(request, f"Still failing: {report.get('error')}")
        return redirect("hub:account", pk=pk)
    from .models import CAPABILITIES
    history = AuditEvent.objects.filter(target_type="ConnectedAccount", target_id=str(acc.pk))[:30]
    return render(request, "hub/account.html", {"acc": acc, "capabilities": CAPABILITIES, "history": history,
                                                "perm_list": [(p, acc.permissions.get(p, False)) for p in ConnectedAccount.PERMISSIONS],
                                                "token_rows": acc.tokens.all()})


@owner_required
@require_POST
def job_accounts_emergency(request):
    n, stopped = control.disable_job_connections(request)
    messages.warning(request, f"Emergency stop: {n} job accounts disabled, {stopped} agent tasks stopped.")
    return redirect("hub:job_accounts")


# ------------------------------------------------------------------ agent
@owner_required
def agent(request):
    new_credential = request.session.pop("hub_new_credential", None)
    task_form = TaskForm(request.POST or None)
    if request.method == "POST" and request.POST.get("action") == "task" and task_form.is_valid():
        d = task_form.cleaned_data
        level = tools.REGISTRY[d["tool"]].level if d["tool"] in tools.REGISTRY else tools.LOCAL_TOOLS[d["tool"]]
        if level in (Level.EXTERNAL, Level.CRITICAL):
            messages.error(request, "External/critical operations go through an approval request, not a direct task.")
        else:
            t = AgentTask.objects.create(device=d["device"], initiator="user", tool=d["tool"], level=level, payload=d["payload"])
            audit("task_created", request=request, level=level, target=t, tool=t.tool)
            messages.success(request, "Task queued for the agent.")
        return redirect("hub:agent")
    tasks_qs = AgentTask.objects.select_related("device")
    if request.GET.get("status"):
        tasks_qs = tasks_qs.filter(status=request.GET["status"])
    return render(request, "hub/agent.html", {"devices": AgentDevice.objects.all(), "new_credential": new_credential,
                                              "tasks": Paginator(tasks_qs, 30).get_page(request.GET.get("page")),
                                              "task_form": task_form, "tool_defs": tools.describe(),
                                              "kill": HubSettings.get().kill_switch})


@owner_required
@require_POST
def device_register(request):
    if not _confirm_password(request):
        return redirect("hub:agent")
    name = (request.POST.get("name") or "Windows PC").strip()[:80]
    dev, credential = AgentDevice.register(name)
    request.session["hub_new_credential"] = {"device": dev.name, "credential": credential}
    audit("device_registered", request=request, level="critical", target=dev)
    return redirect("hub:agent")


@owner_required
@require_POST
def device_action(request, pk):
    dev = get_object_or_404(AgentDevice, pk=pk)
    action = request.POST.get("action")
    if action == "revoke":
        dev.is_revoked = True
        dev.token_version += 1
        dev.save(update_fields=["is_revoked", "token_version"])
        AgentTask.objects.filter(device=dev, status__in=["queued", "running"]).update(status="cancelled", cancel_requested=True, finished_at=timezone.now())
        audit("device_revoked", request=request, level="critical", target=dev)
        messages.success(request, f"{dev.name} revoked. Its tokens stop working immediately.")
    elif action == "rotate":
        if not _confirm_password(request):
            return redirect("hub:agent")
        credential = dev.rotate_secret()
        request.session["hub_new_credential"] = {"device": dev.name, "credential": credential}
        audit("device_rotated", request=request, level="critical", target=dev)
    elif action == "tools":
        enabled = set(request.POST.getlist("tools"))
        for name in tools.REGISTRY:
            AgentToolPermission.objects.update_or_create(device=dev, tool=name, defaults={"enabled": name in enabled})
        audit("device_tools_changed", request=request, level="critical", target=dev, enabled=sorted(enabled))
        messages.success(request, "Tool permissions saved.")
    return redirect("hub:agent")


@owner_required
def task_detail(request, pk):
    task = get_object_or_404(AgentTask.objects.select_related("device"), pk=pk)
    if request.method == "POST" and request.POST.get("action") == "cancel" and not task.finished:
        task.cancel_requested = True
        if task.status == "queued":
            task.status, task.finished_at = "cancelled", timezone.now()
        task.add_log("cancel requested by owner", save=False)
        task.save()
        audit("task_cancel_requested", request=request, target=task)
        return redirect("hub:task", pk=pk)
    return render(request, "hub/task.html", {"task": task, "approvals": task.approvals.all(),
                                             "events": AuditEvent.objects.filter(target_type="AgentTask", target_id=str(task.pk))})


@owner_required
def device_tools(request, pk):
    dev = get_object_or_404(AgentDevice, pk=pk)
    states = {p.tool: p.enabled for p in dev.tool_permissions.all()}
    rows = [(t.name, t.level, t.description, states.get(t.name, True)) for t in tools.REGISTRY.values()]
    return render(request, "hub/device_tools.html", {"device": dev, "rows": rows})


# ------------------------------------------------------------------ approvals
@owner_required
def approvals(request):
    for a in ApprovalRequest.objects.filter(status__in=["pending", "approved"]):
        a.expire_if_needed()
    return render(request, "hub/approvals.html", {
        "pending": ApprovalRequest.objects.filter(status="pending").select_related("application__job", "account"),
        "history": ApprovalRequest.objects.exclude(status="pending").select_related("decided_by")[:50]})


@owner_required
def approval_detail(request, pk):
    appr = get_object_or_404(ApprovalRequest, pk=pk)
    appr.expire_if_needed()
    if request.method == "POST" and appr.status == "pending":
        decision = request.POST.get("decision")
        if decision == "approve":
            if appr.action == "submit_application" and appr.application:
                if tools.application_payload(appr.application) != appr.payload:
                    appr.status = "expired"
                    appr.save(update_fields=["status"])
                    messages.error(request, "The application changed after this request — it was invalidated. Request a new approval.")
                    return redirect("hub:approval", pk=pk)
            if HubSettings.get().kill_switch:
                messages.error(request, "Kill switch is active. Turn it off first.")
                return redirect("hub:approval", pk=pk)
            appr.status, appr.decided_by, appr.decided_at = "approved", request.user, timezone.now()
            appr.save(update_fields=["status", "decided_by", "decided_at"])
            audit("approval_approved", request=request, level=appr.level, target=appr, action_name=appr.action)
            if appr.level == Level.CRITICAL:
                result = control.execute_critical(request, appr)
                messages.success(request, f"Approved and executed: {result.replace('_', ' ')}")
            else:
                if appr.application:
                    appr.application.status = "ready"
                    appr.application.save(update_fields=["status", "updated_at"])
                messages.success(request, "Approved. Valid once, for this exact request, until it expires.")
        elif decision == "reject":
            appr.status, appr.decided_by, appr.decided_at = "rejected", request.user, timezone.now()
            appr.save(update_fields=["status", "decided_by", "decided_at"])
            if appr.application and appr.application.status == "awaiting_approval":
                appr.application.status = "draft"
                appr.application.save(update_fields=["status", "updated_at"])
            audit("approval_rejected", request=request, level=appr.level, target=appr)
            messages.success(request, "Rejected.")
        return redirect("hub:approval", pk=pk)
    return render(request, "hub/approval.html", {"a": appr, "summary_json": json.dumps(appr.summary, ensure_ascii=False, indent=2, default=str)})


# ------------------------------------------------------------------ activity, content, security
@owner_required
def activity(request):
    qs = AuditEvent.objects.select_related("user", "device")
    for f in ("actor_type", "outcome", "level"):
        if request.GET.get(f):
            qs = qs.filter(**{f: request.GET[f]})
    if request.GET.get("q"):
        qs = qs.filter(action__icontains=request.GET["q"][:60])
    return render(request, "hub/activity.html", {"page": Paginator(qs, 50).get_page(request.GET.get("page"))})


@owner_required
def content(request):
    from core.models import BlogPost, Portfolio
    return render(request, "hub/content.html", {"projects": Portfolio.objects.filter(language__code="en").count(),
                                                "posts": BlogPost.objects.count()})


@owner_required
def security(request):
    hs = HubSettings.get()
    mfa = OwnerMFA.objects.filter(user=request.user).first()
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "kill_on":
            c, e = control.activate_kill_switch(request, request.POST.get("reason", ""))
            messages.warning(request, f"Kill switch ON. {c} tasks cancelled, {e} approvals expired, all agent tokens revoked.")
        elif action == "kill_off" and _confirm_password(request):
            control.deactivate_kill_switch(request)
            messages.success(request, "Kill switch off. Agents must request new tokens.")
        elif action == "mfa_setup":
            secret = new_totp_secret()
            mfa, _ = OwnerMFA.objects.update_or_create(user=request.user, defaults={"secret_enc": encrypt(secret), "enabled": False, "last_used_step": 0})
            audit("mfa_setup_started", request=request, level="critical")
        elif action == "mfa_enable" and mfa and not mfa.enabled:
            if verify_totp(mfa, request.POST.get("code", "")):
                mfa.enabled = True
                mfa.save(update_fields=["enabled"])
                request.session[MFA_SESSION_KEY] = True
                audit("mfa_enabled", request=request, level="critical")
                messages.success(request, "Two-factor authentication enabled.")
            else:
                messages.error(request, "Invalid code.")
        elif action == "mfa_disable" and mfa and _confirm_password(request):
            mfa.delete()
            audit("mfa_disabled", request=request, level="critical")
            messages.warning(request, "Two-factor authentication disabled.")
        return redirect("hub:security")
    pending_secret = mfa.secret if (mfa and not mfa.enabled) else None
    return render(request, "hub/security.html", {"hs": hs, "mfa": mfa, "pending_secret": pending_secret,
                                                 "otp_uri": totp_uri(pending_secret, request.user.get_username()) if pending_secret else "",
                                                 "key_ok": explicit_key_configured(),
                                                 "security_events": AuditEvent.objects.filter(level="critical")[:20]})
