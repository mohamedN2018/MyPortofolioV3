"""
Canonical personal-brand identity for the site.

ONE person, three names:
    English (primary):  Mohamed Nabil
    Arabic (primary):   محمد نبيل
    Brand:              Mohamed Nabil Pro

Everything that renders the owner's name, metadata or Person JSON-LD should
read from here (via the ``brand`` context processor) so the spelling never
drifts again ("Mohammed", "MohaMed NabiL", ...).

Only *verified* official profiles belong in PROFILES. They feed both the
visible social links and ``Person.sameAs``. A profile URL stored in
SiteSetting (editable from the admin/dashboard) overrides the default here.
"""
from django.conf import settings
from django.utils import translation

NAME_EN = "Mohamed Nabil"
NAME_AR = "محمد نبيل"
BRAND = "Mohamed Nabil Pro"

JOB_TITLE_EN = "Software Engineer"
JOB_TITLE_AR = "مهندس برمجيات"

# Short professional headline used in hero / titles / descriptions.
HEADLINE_EN = "Software Engineer at Q-Tech Solutions · Backend Developer (Python / Django)"
HEADLINE_AR = "مهندس برمجيات في Q-Tech Solutions · مطور Backend (Python / Django)"

TAGLINE_EN = (
    "Backend developer (Python / Django / DRF) building business systems end-to-end — "
    "HR & payroll, multi-vendor e-commerce and offline-first POS — from requirements "
    "and architecture to production deployment with Docker."
)
TAGLINE_AR = (
    "مطور Backend (Python / Django / DRF) يبني أنظمة الأعمال من البداية للنهاية — الموارد "
    "البشرية والرواتب، المتاجر متعددة البائعين، ونقاط البيع التي تعمل دون إنترنت — من "
    "المتطلبات والمعمارية حتى النشر على الإنتاج باستخدام Docker."
)

# Roles shown as rotating/typed headline items (no inflated claims).
ROLES_EN = ["Software Engineer", "Backend Developer", "Python & Django Developer"]
ROLES_AR = ["مهندس برمجيات", "مطور Backend", "مطور Python و Django"]

COUNTRY_EN = "Egypt"
COUNTRY_AR = "مصر"

KNOWS_ABOUT = [
    "Python", "Django", "Django REST Framework", "PostgreSQL", "MySQL", "Redis",
    "Docker", "Dokploy", "REST APIs", "Backend Development", "HR & Payroll Systems",
    "E-Commerce", "POS Systems", "ERP Systems",
]
WORKS_FOR = {"name": "Q-Tech Solutions", "url": "https://q-tech-solutions.com/"}

# key -> (label, bootstrap-icon class, default verified URL, SiteSetting field)
PROFILES = [
    ("linkedin", "LinkedIn", "bi-linkedin",
     "https://www.linkedin.com/in/mohamed-nabil-1458872b2/", "linkedin_url"),
    ("github", "GitHub", "bi-github",
     "https://github.com/mohamedN2018", "github_url"),
    ("gitlab", "GitLab", "bi-gitlab",
     "https://gitlab.com/mohamedN2024", "gitlab_url"),
    ("stackoverflow", "Stack Overflow", "bi-stack-overflow",
     "https://stackoverflow.com/users/28639128/mohamed-nabil", "stackoverflow_url"),
    ("behance", "Behance", "bi-behance",
     "https://www.behance.net/moh24832c3ae", "behance_url"),
    ("facebook", "Facebook", "bi-facebook",
     "https://www.facebook.com/MohaMedNabiLPro", "facebook_url"),
]

# Optional extra profiles: shown ONLY if the owner fills them in SiteSetting.
OPTIONAL_PROFILES = [
    ("twitter", "X (Twitter)", "bi-twitter-x", "twitter_url"),
    ("instagram", "Instagram", "bi-instagram", "instagram_url"),
]


def site_url():
    """Absolute production base URL without trailing slash (from env)."""
    configured = getattr(settings, "SITE_URL", "") or ""
    return configured.rstrip("/")


def is_arabic(lang_code=None):
    code = (lang_code or translation.get_language() or "en").lower()
    return code.startswith("ar")


def display_name(lang_code=None):
    return NAME_AR if is_arabic(lang_code) else NAME_EN


def get_profiles(site_settings=None):
    """List of dicts for verified + optional profiles, deduplicated."""
    profiles, seen = [], set()
    for key, label, icon, default, field in PROFILES:
        url = (getattr(site_settings, field, "") or "").strip() if site_settings else ""
        url = url or default
        if url and url not in seen:
            seen.add(url)
            profiles.append({"key": key, "label": label, "icon": icon, "url": url})
    for key, label, icon, field in OPTIONAL_PROFILES:
        url = (getattr(site_settings, field, "") or "").strip() if site_settings else ""
        if url and url not in seen:
            seen.add(url)
            profiles.append({"key": key, "label": label, "icon": icon, "url": url})
    return profiles
