"""
Idempotent setup: provider catalog, default job preferences, verified CV facts,
and (optionally) the published CV imported as a private CV version.
Never deletes anything.
"""
import os
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from hub import crypto, providers
from hub.models import CVDocument, HubSettings, JobPreference, PrivateFact

CV_SOURCE = "Mohammed_Nabil_Backend_Developer_CV_Gulf.pdf (owner, 2026-11-06)"
CV_DATE = date(2026, 11, 6)

# Only facts stated in the CV / by the owner. Contact details are private + sensitive.
FACTS = [
    ("identity", "full-name", "Mohamed Nabil (CV spelling: Mohammed Nabil)", "محمد نبيل", False, "public"),
    ("identity", "brand-name", "Mohamed Nabil Pro", "Mohamed Nabil Pro", False, "public"),
    ("identity", "years-experience", "3", "3", False, "public"),
    ("identity", "location", "Egypt (open to relocation)", "مصر (مستعد للانتقال)", False, "public"),
    ("identity", "current-role", "Software Engineer at Q-Tech Solutions (since 05/2026)", "مهندس برمجيات في Q-Tech Solutions (منذ 05/2026)", False, "public"),
    ("summary", "headline", "Mid-Level Backend Developer | Python / Django | ERP, HR & E-Commerce Systems",
     "مطوّر Backend متوسط الخبرة | Python / Django | أنظمة ERP والموارد البشرية والتجارة الإلكترونية", False, "public"),
    ("language", "arabic", "Arabic — native", "العربية — اللغة الأم", False, "public"),
    ("language", "english", "English — intermediate (technical reading & documentation)", "الإنجليزية — متوسط", False, "public"),
    ("education", "secondary-diploma", "Industrial Secondary Diploma – Decoration & Design (2019–2022)", "دبلوم ثانوي صناعي – زخرفة وتصميم (2019–2022)", False, "public"),
    ("certification", "fullstack-diploma", "Full-Stack Web Development Diploma (100 h)", "دبلومة تطوير الويب Full-Stack (100 ساعة)", False, "public"),
    ("contact", "email", "MohaMedNabiLpro2024@gmail.com", "", True, "private"),
    ("contact", "phone", "+20 106 027 3497", "", True, "private"),
    ("link", "linkedin", "https://www.linkedin.com/in/mohamed-nabil-1458872b2/", "", False, "public"),
    ("link", "github", "https://github.com/mohamedN2018", "", False, "public"),
    ("link", "portfolio", "https://mohamednabilpro.deplois.net/", "", False, "public"),
]


class Command(BaseCommand):
    help = "Seed the AI Hub (idempotent, non-destructive)."

    def add_arguments(self, parser):
        parser.add_argument("--import-cv", action="store_true", help="Copy static/brand/cv/Mohamed-Nabil-CV.pdf in as the Gulf CV")

    def handle(self, *args, **opts):
        HubSettings.get()
        self._owner()
        n = providers.seed_catalog()
        self.stdout.write(f"providers: {n} new, catalog size {len(providers.CATALOG)}")
        if not JobPreference.objects.exists():
            JobPreference.objects.create(
                name="Default", roles=["Backend Developer", "Python Developer", "Django Developer", "Software Engineer", "Full-Stack Developer"],
                locations=["Egypt", "Saudi Arabia", "KSA", "UAE", "Remote"], work_modes=["remote", "hybrid", "onsite"],
                seniority=["mid"], required_tech=["Python", "Django"], employment_types=["full_time"])
            self.stdout.write("job preference: created (edit it in /hub/jobs/preferences/)")
        created = 0
        for section, key, en, ar, sensitive, vis in FACTS:
            _, c = PrivateFact.objects.get_or_create(section=section, key=key, defaults=dict(
                value_en=en, value_ar=ar, sensitive=sensitive, visibility=vis, source=CV_SOURCE, verified_at=CV_DATE, status="verified"))
            created += c
        self.stdout.write(f"facts: {created} new")
        if opts["import_cv"]:
            src = Path(settings.BASE_DIR) / "static" / "brand" / "cv" / "Mohamed-Nabil-CV.pdf"
            if not src.exists():
                self.stderr.write("CV file not found")
            elif CVDocument.objects.filter(kind="cv", source=CV_SOURCE).exists():
                self.stdout.write("cv: already imported")
            else:
                data = src.read_bytes()
                doc = CVDocument(title="Backend Developer CV — Gulf (EN)", kind="cv", market="gulf", language="en",
                                 is_default=True, source=CV_SOURCE, verified_at=CV_DATE, status="verified", visibility="public",
                                 sha256=__import__("hashlib").sha256(data).hexdigest())
                with src.open("rb") as fh:
                    doc.file.save("Mohamed-Nabil-CV-Gulf.pdf", File(fh), save=True)
                self.stdout.write(f"cv: imported ({len(data)} bytes)")
        if not crypto.explicit_key_configured():
            self.stdout.write(self.style.WARNING("HUB_ENCRYPTION_KEYS is not set — using a key derived from SECRET_KEY (dev only)."))

    def _owner(self):
        """HUB_OWNER_USERNAME: make sure this account exists and is a superuser.
        HUB_OWNER_INITIAL_PASSWORD is used ONLY when the account is created (never overwrites a password)."""
        from django.contrib.auth import get_user_model
        username = os.environ.get("HUB_OWNER_USERNAME", "").strip()
        if not username:
            return
        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user is None:
            pw = os.environ.get("HUB_OWNER_INITIAL_PASSWORD", "")
            if len(pw) < 16:
                self.stderr.write("owner: not created (HUB_OWNER_INITIAL_PASSWORD missing or shorter than 16 chars)")
                return
            User.objects.create_superuser(username=username, email="", password=pw)
            self.stdout.write("owner: created")
        elif not (user.is_superuser and user.is_staff and user.is_active):
            user.is_superuser = user.is_staff = user.is_active = True
            user.save(update_fields=["is_superuser", "is_staff", "is_active"])
            self.stdout.write("owner: promoted to superuser")
        else:
            self.stdout.write("owner: ok")
