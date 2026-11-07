"""
Mohamed Nabil AI Hub — private data model.

Public portfolio data stays in `core` (PersonalInfo, WorkExperience, Skill,
Portfolio...). This app only stores PRIVATE data and agent/approval state and is
never referenced by public views, serializers, the sitemap or search.
"""
import hashlib
import json
import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models, transaction
from django.utils import timezone

from . import crypto


def private_storage():
    # Outside MEDIA_ROOT: never served by the public media route.
    return FileSystemStorage(location=settings.HUB_PRIVATE_ROOT, base_url=None)


class Level(models.TextChoices):
    READ = "read", "Read"
    PREPARE = "prepare", "Prepare"
    WRITE = "write", "Write"
    EXTERNAL = "external", "External action"
    CRITICAL = "critical", "Critical"


def payload_digest(data) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


# --------------------------------------------------------------------------- config
class HubSettings(models.Model):
    """Singleton (pk=1). Holds the global kill switch."""
    kill_switch = models.BooleanField(default=False)
    kill_switch_at = models.DateTimeField(null=True, blank=True)
    kill_switch_reason = models.CharField(max_length=300, blank=True)
    approval_ttl_minutes = models.PositiveIntegerField(default=60)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hub settings"
        verbose_name_plural = "Hub settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class OwnerMFA(models.Model):
    """TOTP (RFC 6238) second factor for the hub owner."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hub_mfa")
    secret_enc = models.TextField()
    enabled = models.BooleanField(default=False)
    last_used_step = models.BigIntegerField(default=0)  # replay protection
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def secret(self):
        return crypto.decrypt(self.secret_enc)


# --------------------------------------------------------------------------- audit
class AuditEvent(models.Model):
    ACTOR = [("user", "User"), ("agent", "Agent"), ("system", "System")]
    OUTCOME = [("ok", "OK"), ("denied", "Denied"), ("error", "Error")]

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    actor_type = models.CharField(max_length=10, choices=ACTOR)
    actor_label = models.CharField(max_length=120, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    device = models.ForeignKey("AgentDevice", null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=80, db_index=True)
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.READ)
    target_type = models.CharField(max_length=60, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    outcome = models.CharField(max_length=10, choices=OUTCOME, default="ok")
    ip = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["target_type", "target_id"])]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.actor_type} {self.action} {self.outcome}"


# --------------------------------------------------------------------------- personal data
class Provenance(models.Model):
    STATUS = [("verified", "Verified"), ("unverified", "Unverified"), ("needs_review", "Needs review")]
    VISIBILITY = [("private", "Private"), ("public", "Public")]

    source = models.CharField(max_length=200, help_text="Where this came from, e.g. 'CV Gulf 2026-11-06'")
    verified_at = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default="unverified")
    visibility = models.CharField(max_length=10, choices=VISIBILITY, default="private")

    class Meta:
        abstract = True


class PrivateFact(Provenance):
    """Structured private profile records (identity, contact, preferences, certifications...)."""
    SECTION = [
        ("identity", "Identity"), ("summary", "Professional summary"), ("contact", "Contact"),
        ("link", "Professional link"), ("language", "Language"), ("certification", "Certification"),
        ("education", "Education"), ("employment", "Employment note"), ("answer", "Standard application answer"),
        ("other", "Other"),
    ]
    section = models.CharField(max_length=20, choices=SECTION)
    key = models.SlugField(max_length=80)
    value_en = models.TextField(blank=True)
    value_ar = models.TextField(blank=True)
    sensitive = models.BooleanField(default=False, help_text="Never sent to the agent without an approval")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["section", "key"]
        constraints = [models.UniqueConstraint(fields=["section", "key"], name="hub_fact_unique_key")]

    def __str__(self):
        return f"{self.section}:{self.key}"


class CVDocument(Provenance):
    MARKET = [("general", "General"), ("egypt", "Egypt"), ("gulf", "Gulf (KSA / UAE)")]
    KIND = [("cv", "CV"), ("cover_letter_template", "Cover letter template"), ("other", "Other document")]
    LANG = [("en", "English"), ("ar", "Arabic")]

    title = models.CharField(max_length=160)
    kind = models.CharField(max_length=25, choices=KIND, default="cv")
    market = models.CharField(max_length=10, choices=MARKET, default="general")
    language = models.CharField(max_length=2, choices=LANG, default="en")
    file = models.FileField(storage=private_storage, upload_to="documents/%Y/", blank=True)
    text_content = models.TextField(blank=True, help_text="Template text (cover letters) or extracted text")
    sha256 = models.CharField(max_length=64, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["kind", "market", "-uploaded_at"]
        indexes = [models.Index(fields=["kind", "market", "is_active"])]

    def __str__(self):
        return self.title


class JobPreference(models.Model):
    name = models.CharField(max_length=80, default="Default")
    is_active = models.BooleanField(default=True)
    roles = models.JSONField(default=list)
    locations = models.JSONField(default=list)
    work_modes = models.JSONField(default=list, help_text="remote / hybrid / onsite")
    seniority = models.JSONField(default=list, help_text="junior / mid / senior")
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=3, blank=True)
    required_tech = models.JSONField(default=list)
    excluded_tech = models.JSONField(default=list)
    employment_types = models.JSONField(default=list, help_text="full_time / contract / part_time")
    needs_sponsorship = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @classmethod
    def active(cls):
        return cls.objects.filter(is_active=True).order_by("-updated_at").first()


# --------------------------------------------------------------------------- providers & accounts
CAPABILITIES = [
    ("oauth", "Official OAuth"),
    ("api", "Official API"),
    ("job_discovery", "Job discovery"),
    ("job_details", "Job details"),
    ("profile_access", "Profile access"),
    ("draft_preparation", "Application draft preparation"),
    ("submission", "Application submission"),
    ("status_tracking", "Application status tracking"),
    ("user_assisted", "User-assisted browser workflow"),
]
CAPABILITY_STATUS = [
    ("supported", "Supported (official)"),
    ("assisted", "User-assisted only"),
    ("local", "Done locally by the hub"),
    ("unsupported", "Not supported"),
    ("unknown", "Unknown — not researched/tested"),
]


class Provider(models.Model):
    CATEGORY = [("job_board", "Job board"), ("ats", "ATS"), ("career_portal", "Company career portal"),
                ("developer", "Developer platform"), ("google", "Google")]
    METHODS = [("oauth", "Official OAuth"), ("api", "Official API credentials / public API"),
               ("browser_local", "Local browser-assisted"), ("manual", "Manual")]

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=80)
    category = models.CharField(max_length=20, choices=CATEGORY)
    website = models.URLField()
    logo_text = models.CharField(max_length=3, blank=True, help_text="Monogram used as logo (no third-party logos bundled)")
    capabilities = models.JSONField(default=dict, help_text="{capability: status}")
    connection_methods = models.JSONField(default=list)
    limitations = models.TextField(blank=True)
    docs_url = models.URLField(blank=True)
    reviewed_at = models.DateField(null=True, blank=True)
    connector = models.CharField(max_length=30, blank=True, help_text="Hub connector implemented for this provider (empty = none yet)")
    is_custom = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["category", "order", "name"]

    def __str__(self):
        return self.name

    def cap(self, key):
        return self.capabilities.get(key, "unknown")

    @property
    def can_submit(self):
        return self.cap("submission") == "supported"


class ConnectedAccount(models.Model):
    STATUS = [("pending", "Pending"), ("connected", "Connected"), ("expired", "Authorization expired"),
              ("revoked", "Access revoked"), ("unavailable", "Provider unavailable"),
              ("error", "Connection error"), ("disconnected", "Disconnected")]
    PERMISSIONS = ["read", "prepare", "write", "submit"]

    provider = models.ForeignKey(Provider, on_delete=models.PROTECT, related_name="accounts")
    label = models.CharField(max_length=120, blank=True)
    account_identifier = models.CharField(max_length=200, blank=True, help_text="Username / email / board token (not a password)")
    method = models.CharField(max_length=15, choices=Provider.METHODS)
    status = models.CharField(max_length=15, choices=STATUS, default="pending")
    scopes = models.JSONField(default=list, blank=True)
    permissions = models.JSONField(default=dict, blank=True)
    config = models.JSONField(default=dict, blank=True, help_text="Non-secret settings (e.g. public board token)")
    verified_capabilities = models.JSONField(default=dict, blank=True, help_text="Result of the last real connection test")
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    last_error = models.CharField(max_length=500, blank=True)
    required_action = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["provider__name", "label"]
        constraints = [models.UniqueConstraint(fields=["provider", "account_identifier"], name="hub_account_unique")]

    def __str__(self):
        return f"{self.provider.name} — {self.label or self.account_identifier}"

    def allowed(self, perm):
        if perm == "submit" and not self.provider.can_submit:
            return False
        return bool(self.permissions.get(perm)) and self.status == "connected"

    def token(self, kind):
        t = self.tokens.filter(kind=kind, revoked_at__isnull=True).order_by("-created_at").first()
        return t.value if t else ""


class IntegrationToken(models.Model):
    """Access and refresh tokens are separate rows; ciphertext only."""
    KIND = [("access", "Access token"), ("refresh", "Refresh token")]
    account = models.ForeignKey(ConnectedAccount, on_delete=models.CASCADE, related_name="tokens")
    kind = models.CharField(max_length=10, choices=KIND)
    ciphertext = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["account", "kind", "revoked_at"])]

    def __str__(self):  # never print the secret
        return f"{self.kind} token for account {self.account_id}"

    @property
    def value(self):
        return crypto.decrypt(self.ciphertext)

    @classmethod
    def store(cls, account, kind, plaintext, expires_at=None):
        cls.objects.filter(account=account, kind=kind, revoked_at__isnull=True).update(revoked_at=timezone.now())
        return cls.objects.create(account=account, kind=kind, ciphertext=crypto.encrypt(plaintext), expires_at=expires_at)


# --------------------------------------------------------------------------- agent
class AgentDevice(models.Model):
    name = models.CharField(max_length=80)
    token_prefix = models.CharField(max_length=12, unique=True)
    secret_hash = models.CharField(max_length=64)
    token_version = models.PositiveIntegerField(default=1)
    is_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    agent_version = models.CharField(max_length=40, blank=True)
    status_note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def online(self):
        return bool(self.last_heartbeat and timezone.now() - self.last_heartbeat < timedelta(seconds=90)) and not self.is_revoked

    @classmethod
    def register(cls, name):
        """Returns (device, plaintext_credential). The credential is shown once and only its hash is stored."""
        prefix = secrets.token_hex(4)
        secret = secrets.token_urlsafe(32)
        dev = cls.objects.create(name=name, token_prefix=prefix, secret_hash=crypto.sha256_hex(secret))
        return dev, f"mnpdev_{prefix}_{secret}"

    def rotate_secret(self):
        secret = secrets.token_urlsafe(32)
        self.secret_hash = crypto.sha256_hex(secret)
        self.token_version += 1
        self.save(update_fields=["secret_hash", "token_version"])
        return f"mnpdev_{self.token_prefix}_{secret}"

    def check_secret(self, secret):
        return secrets.compare_digest(self.secret_hash, crypto.sha256_hex(secret))


class RateBucket(models.Model):
    """Fixed-window counters in the DB so limits hold across all gunicorn workers."""
    key = models.CharField(max_length=160, unique=True)
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)


class AgentNonce(models.Model):
    """Replay protection shared by all gunicorn workers (unique per device + request id)."""
    device = models.ForeignKey(AgentDevice, on_delete=models.CASCADE)
    nonce = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["device", "nonce"], name="hub_nonce_unique")]


class AgentToolPermission(models.Model):
    device = models.ForeignKey(AgentDevice, on_delete=models.CASCADE, related_name="tool_permissions")
    tool = models.CharField(max_length=60)
    enabled = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["device", "tool"], name="hub_tool_perm_unique")]


class AgentTask(models.Model):
    STATUS = [("queued", "Queued"), ("awaiting_approval", "Awaiting approval"), ("running", "Running"),
              ("succeeded", "Succeeded"), ("failed", "Failed"), ("cancelled", "Cancelled"), ("denied", "Denied")]
    INITIATOR = [("user", "Owner (dashboard)"), ("agent", "Agent")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(AgentDevice, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    initiator = models.CharField(max_length=10, choices=INITIATOR)
    tool = models.CharField(max_length=60)
    level = models.CharField(max_length=10, choices=Level.choices)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="queued", db_index=True)
    progress = models.PositiveSmallIntegerField(default=0)
    log = models.JSONField(default=list, blank=True)
    result = models.JSONField(default=dict, blank=True)
    error = models.CharField(max_length=500, blank=True)
    cancel_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["device", "status"])]

    def add_log(self, message, save=True):
        self.log = (self.log or [])[-199:] + [{"at": timezone.now().isoformat(), "msg": str(message)[:500]}]
        if save:
            self.save(update_fields=["log"])

    @property
    def finished(self):
        return self.status in ("succeeded", "failed", "cancelled", "denied")


class ApprovalRequest(models.Model):
    STATUS = [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"),
              ("expired", "Expired"), ("consumed", "Used"), ("executed", "Executed")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=60)
    level = models.CharField(max_length=10, choices=Level.choices)
    title = models.CharField(max_length=200)
    summary = models.JSONField(default=dict, help_text="Exactly what will be done / submitted")
    payload = models.JSONField(default=dict)
    payload_hash = models.CharField(max_length=64)
    task = models.ForeignKey(AgentTask, null=True, blank=True, on_delete=models.SET_NULL, related_name="approvals")
    application = models.ForeignKey("JobApplication", null=True, blank=True, on_delete=models.SET_NULL, related_name="approvals")
    account = models.ForeignKey(ConnectedAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name="approvals")
    requested_by = models.CharField(max_length=120)
    status = models.CharField(max_length=10, choices=STATUS, default="pending", db_index=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    decided_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @classmethod
    def open(cls, *, action, level, title, summary, payload, requested_by, **links):
        ttl = HubSettings.get().approval_ttl_minutes
        return cls.objects.create(action=action, level=level, title=title[:200], summary=summary, payload=payload,
                                  payload_hash=payload_digest(payload), requested_by=requested_by,
                                  expires_at=timezone.now() + timedelta(minutes=ttl), **links)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def expire_if_needed(self):
        if self.status in ("pending", "approved") and self.is_expired:
            self.status = "expired"
            self.save(update_fields=["status"])
        return self.status

    @classmethod
    def consume(cls, approval_id, *, action, payload):
        """Single use: valid only for the same action + identical payload, before expiry."""
        with transaction.atomic():
            appr = cls.objects.select_for_update().filter(pk=approval_id).first()
            if not appr:
                return None, "approval_not_found"
            if appr.expire_if_needed() == "expired":
                return None, "approval_expired"
            if appr.status != "approved":
                return None, f"approval_{appr.status}"
            if appr.action != action or appr.payload_hash != payload_digest(payload):
                return None, "approval_does_not_match_request"
            appr.status, appr.consumed_at = "consumed", timezone.now()
            appr.save(update_fields=["status", "consumed_at"])
            return appr, "ok"


# --------------------------------------------------------------------------- jobs
class Job(models.Model):
    WORK_MODE = [("remote", "Remote"), ("hybrid", "Hybrid"), ("onsite", "On-site"), ("unknown", "Not stated")]

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=160)
    location = models.CharField(max_length=160, blank=True)
    market = models.CharField(max_length=10, blank=True, help_text="egypt / ksa / uae / other")
    work_mode = models.CharField(max_length=10, choices=WORK_MODE, default="unknown")
    source = models.CharField(max_length=60, help_text="manual, greenhouse, lever, remoteok, ...")
    provider = models.ForeignKey(Provider, null=True, blank=True, on_delete=models.SET_NULL)
    url = models.URLField(max_length=600)
    url_hash = models.CharField(max_length=64, unique=True)
    fingerprint = models.CharField(max_length=64, db_index=True)
    description = models.TextField(blank=True, help_text="UNTRUSTED external text — never treated as instructions")
    required_skills = models.JSONField(default=list, blank=True)
    preferred_skills = models.JSONField(default=list, blank=True)
    experience_text = models.CharField(max_length=200, blank=True)
    min_years = models.PositiveSmallIntegerField(null=True, blank=True)
    seniority = models.CharField(max_length=20, blank=True)
    employment_type = models.CharField(max_length=20, blank=True)
    language_requirements = models.CharField(max_length=200, blank=True)
    salary_text = models.CharField(max_length=120, blank=True, help_text="Only if publicly stated")
    posted_at = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["-discovered_at"]

    def __str__(self):
        return f"{self.title} — {self.company}"


class JobMatch(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name="match")
    preference = models.ForeignKey(JobPreference, null=True, on_delete=models.SET_NULL)
    score = models.PositiveSmallIntegerField()
    breakdown = models.JSONField(default=dict)
    computed_at = models.DateTimeField(auto_now=True)


class JobApplication(models.Model):
    STATUS = [
        ("discovered", "Discovered"), ("analyzed", "Analyzed"), ("shortlisted", "Shortlisted"),
        ("draft", "Draft prepared"), ("awaiting_approval", "Awaiting approval"), ("ready", "Ready to apply"),
        ("submitted", "Submitted"), ("assessment", "Assessment"), ("interview", "Interview"),
        ("offer", "Offer"), ("rejected", "Rejected"), ("withdrawn", "Withdrawn"),
    ]
    ACTIVE_AFTER_SUBMIT = {"submitted", "assessment", "interview", "offer"}

    job = models.OneToOneField(Job, on_delete=models.PROTECT, related_name="application")
    account = models.ForeignKey(ConnectedAccount, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS, default="discovered", db_index=True)
    cv = models.ForeignKey(CVDocument, null=True, blank=True, on_delete=models.SET_NULL, related_name="applications")
    cover_letter = models.TextField(blank=True)
    answers = models.JSONField(default=dict, blank=True)
    flags = models.JSONField(default=list, blank=True, help_text="Missing / uncertain information")
    applied_at = models.DateTimeField(null=True, blank=True)
    submission_evidence = models.TextField(blank=True)
    follow_up_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Application: {self.job}"


class ApplicationDocument(models.Model):
    KIND = [("cv", "CV"), ("cover_letter", "Cover letter"), ("answers", "Form answers"), ("other", "Other")]
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="documents")
    kind = models.CharField(max_length=15, choices=KIND)
    cv_document = models.ForeignKey(CVDocument, null=True, blank=True, on_delete=models.SET_NULL)
    content = models.TextField(blank=True)
    sha256 = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.content and not self.sha256:
            self.sha256 = crypto.sha256_hex(self.content)
        super().save(*args, **kwargs)
