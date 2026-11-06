"""
Identity / discoverability views:

* public root files (Google Search Console verification) — served byte-for-byte
* robots.txt, sitemap.xml (with hreflang + image entries), llms.txt
* /about/mohamed-nabil/  — authoritative, server-rendered identity page
* /cv/, /cv/view/, /cv/download/ — recruiter-first CV experience
* /gallery/ — approved public images only
"""
import logging
import mimetypes
import re
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from . import identity, seo
from .models import (
    BlogPost, Education, GalleryItem, Portfolio, PersonalInfo, Skill,
    SkillCategory, WorkExperience,
)
from .views import get_common_context, get_current_language, get_model_data

logger = logging.getLogger(__name__)

PUBLIC_FILE_RE = re.compile(r"^google[0-9a-f]{8,32}\.html$")
CV_DOWNLOAD_NAME = "Mohamed-Nabil-CV.pdf"


# ---------------------------------------------------------------------------
# Public root files
# ---------------------------------------------------------------------------
@require_GET
def public_root_file(request, filename):
    """Serve whitelisted files from PUBLIC_ROOT exactly as uploaded."""
    if not PUBLIC_FILE_RE.match(filename):
        raise Http404
    root = Path(settings.PUBLIC_ROOT).resolve()
    path = (root / filename).resolve()
    if path.parent != root or not path.is_file():
        raise Http404
    data = path.read_bytes()  # raw bytes: content preserved exactly
    response = HttpResponse(data, content_type="text/html; charset=utf-8")
    response["Cache-Control"] = "public, max-age=3600"
    response["X-Robots-Tag"] = "noindex"
    return response


@require_GET
@cache_control(public=True, max_age=3600)
def robots_txt(request):
    base = identity.site_url()
    lines = [
        "# robots.txt — " + identity.BRAND,
        "# Public portfolio content is open to search engines and AI search crawlers.",
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /hub/",
        "Disallow: /api/",
        "Disallow: /search/",
        "Disallow: /set-language/",
        "Disallow: /i18n/",
        "",
        f"Sitemap: {base}/sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def _lastmod(value):
    if not value:
        return None
    try:
        return value.date().isoformat()
    except AttributeError:
        return value.isoformat()


@require_GET
@cache_control(public=True, max_age=3600)
def sitemap_xml(request):
    """Absolute-URL sitemap with hreflang alternates and image entries."""
    from xml.sax.saxutils import escape

    entries = []  # (loc, lastmod, alternates[(lang, href)], images[(loc, caption)])
    portrait = (seo.static_abs(seo.portrait_path()), "Mohamed Nabil (محمد نبيل) — Software Engineer")

    static_pages = [
        ("home", [portrait]), ("identity", [portrait]), ("cv", [portrait]),
        ("about", [portrait]), ("portfolio", []), ("services", []),
        ("blog", []), ("gallery", []), ("contact", []),
    ]
    for name, images in static_pages:
        path = reverse(name)
        alts = [(code, seo.lang_url(path, code)) for code in seo.SUPPORTED_LANGS]
        alts.append(("x-default", seo.absolute(path)))
        for code in seo.SUPPORTED_LANGS:
            entries.append((seo.lang_url(path, code), None, alts, images if code == seo.DEFAULT_LANG else []))

    for p in Portfolio.objects.filter(is_active=True).select_related("language"):
        path = reverse("portfolio_detail", args=[p.slug])
        imgs = []
        if p.cover_image:
            imgs.append((seo.absolute(p.cover_image.url), p.title))
        entries.append((seo.lang_url(path, p.language.code), _lastmod(p.project_date), [], imgs))

    for b in BlogPost.objects.filter(is_published=True).select_related("language"):
        path = reverse("blog_detail", args=[b.slug])
        imgs = [(seo.absolute(b.featured_image.url), b.title)] if b.featured_image else []
        entries.append((seo.lang_url(path, b.language.code), _lastmod(b.updated_date), [], imgs))

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
           'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    seen = set()
    for loc, lastmod, alts, images in entries:
        if loc in seen:
            continue
        seen.add(loc)
        out.append("  <url>")
        out.append(f"    <loc>{escape(loc)}</loc>")
        if lastmod:
            out.append(f"    <lastmod>{lastmod}</lastmod>")
        for code, href in alts:
            out.append(f'    <xhtml:link rel="alternate" hreflang="{code}" href="{escape(href)}"/>')
        for img, caption in images:
            out.append(f"    <image:image><image:loc>{escape(img)}</image:loc></image:image>")
        out.append("  </url>")
    out.append("</urlset>")
    return HttpResponse("\n".join(out) + "\n", content_type="application/xml; charset=utf-8")


@require_GET
@cache_control(public=True, max_age=3600)
def llms_txt(request):
    """llms.txt — optional, human/LLM-readable summary (not a ranking signal)."""
    from .models import SiteSetting

    base = identity.site_url()
    site_settings = SiteSetting.objects.first()
    profiles = identity.get_profiles(site_settings)
    projects = (Portfolio.objects.filter(is_active=True, language__code="en")
                .order_by("-is_featured", "order", "-project_date")[:12])
    posts = BlogPost.objects.filter(is_published=True, language__code="en")[:10]

    lines = [
        f"# {identity.NAME_EN} ({identity.NAME_AR}) — {identity.BRAND}",
        "",
        f"> {identity.NAME_EN} (Arabic: {identity.NAME_AR}), publicly known online as "
        f"\"{identity.BRAND}\", is a {identity.JOB_TITLE_EN.lower()} based in {identity.COUNTRY_EN}. "
        f"{identity.TAGLINE_EN}",
        "",
        f"This website ({base}/) is the official source of public information about him. "
        "\"Mohamed Nabil\", \"محمد نبيل\" and \"Mohamed Nabil Pro\" refer to the same person.",
        "",
        "## Key pages",
        f"- [Official profile / identity page]({base}/about/mohamed-nabil/): who Mohamed Nabil is, verified skills, projects and profiles",
        f"- [CV / Resume]({base}/cv/): professional summary, experience, skills, education; PDF at {base}/cv/download/",
        f"- [Projects]({base}/portfolio/): software projects and case studies",
        f"- [Articles]({base}/blog/): technical writing",
        f"- [Contact]({base}/contact/)",
        f"- Arabic versions: append `?lang=ar` (e.g. {base}/about/mohamed-nabil/?lang=ar)",
        "",
        "## Official profiles",
    ]
    lines += [f"- [{p['label']}]({p['url']})" for p in profiles]
    if projects:
        lines += ["", "## Projects"]
        for p in projects:
            lines.append(f"- [{p.title}]({base}{reverse('portfolio_detail', args=[p.slug])}): {p.short_description}")
    if posts:
        lines += ["", "## Articles"]
        for b in posts:
            lines.append(f"- [{b.title}]({base}{reverse('blog_detail', args=[b.slug])}): {b.excerpt[:160]}")
    lines += ["", f"_Generated {timezone.now().date().isoformat()} from the live site content._", ""]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


# ---------------------------------------------------------------------------
# Shared data for identity + CV pages
# ---------------------------------------------------------------------------
def _profile_data(language):
    personal = get_model_data(PersonalInfo, language, fallback=True).first()
    categories = list(get_model_data(SkillCategory, language, fallback=True, is_active=True))
    skills = list(get_model_data(Skill, language, fallback=True, is_active=True).select_related("category"))
    if not any(s.category_id in {c.id for c in categories} for s in skills):
        # Skills may only exist in the default language: group by their own categories.
        categories = list({s.category_id: s.category for s in skills}.values())
    grouped = []
    for c in sorted(categories, key=lambda c: c.order):
        names = []
        for s in skills:
            if s.category_id == c.id and s.name not in names:
                names.append(s.name)
        if names:
            grouped.append({"name": c.name, "icon": c.icon, "skills": names})
    experiences = list(get_model_data(WorkExperience, language, fallback=True, is_active=True))
    educations = list(get_model_data(Education, language, fallback=True, is_active=True))
    projects = list(get_model_data(Portfolio, language, fallback=True, is_active=True)
                    .order_by("-is_featured", "order", "-project_date")[:8])
    return {
        "personal": personal,
        "skill_groups": grouped,
        "experiences": experiences,
        "educations": educations,
        "projects": projects,
    }


CV_STATIC = Path(settings.BASE_DIR) / "static" / "brand" / "cv" / CV_DOWNLOAD_NAME


def _cv_file(language):
    """The single official CV: the version-controlled static PDF, else a CMS upload."""
    if CV_STATIC.is_file():
        return CV_STATIC
    personal = get_model_data(PersonalInfo, language, fallback=True).first()
    if personal and personal.resume_file:
        return personal.resume_file
    for p in PersonalInfo.objects.exclude(resume_file="").exclude(resume_file__isnull=True):
        if p.resume_file:
            return p.resume_file
    return None


def identity_page(request):
    language, lang_code = get_current_language(request)
    data = _profile_data(language)
    ar = seo.current_lang() == "ar"
    title = ("محمد نبيل (Mohamed Nabil) — الملف الرسمي | Mohamed Nabil Pro" if ar
             else "Mohamed Nabil (محمد نبيل) — Official Profile | Mohamed Nabil Pro")
    description = identity.TAGLINE_AR if ar else identity.TAGLINE_EN
    ctx = get_common_context(request, language, data)
    ctx.update({
        "page_title": title,
        "page_description": description,
        "cv_available": _cv_file(language) is not None,
        "page_jsonld": seo.graph(
            seo.website_entity(),
            seo.person_entity(ctx.get("site_settings")),
            seo.page_entity(request, title, description, "ProfilePage", breadcrumbs=[
                ("Home" if not ar else "الرئيسية", "/"),
                (identity.NAME_AR if ar else identity.NAME_EN, request.path),
            ]),
        ),
    })
    return render(request, "identity.html", ctx)


def cv_page(request):
    language, lang_code = get_current_language(request)
    data = _profile_data(language)
    ar = seo.current_lang() == "ar"
    title = ("السيرة الذاتية — محمد نبيل، مهندس برمجيات | Mohamed Nabil CV" if ar
             else "CV / Resume — Mohamed Nabil, Software Engineer | محمد نبيل")
    description = ("السيرة الذاتية لمحمد نبيل: الخبرات، المهارات التقنية، المشاريع والتعليم — مع تحميل نسخة PDF."
                   if ar else
                   "Mohamed Nabil's CV: professional summary, experience, technical skills, projects and "
                   "education — with a downloadable PDF.")
    ctx = get_common_context(request, language, data)
    from .brand_content import LANGUAGES, TRAINING
    ctx.update({
        "page_title": title,
        "page_description": description,
        "cv_available": _cv_file(language) is not None,
        "cv_languages": LANGUAGES["ar" if ar else "en"],
        "cv_training": TRAINING["ar" if ar else "en"],
        "page_jsonld": seo.graph(
            seo.website_entity(),
            seo.person_entity(ctx.get("site_settings")),
            seo.page_entity(request, title, description, "ProfilePage", breadcrumbs=[
                ("Home" if not ar else "الرئيسية", "/"),
                ("CV" if not ar else "السيرة الذاتية", request.path),
            ]),
        ),
    })
    return render(request, "cv.html", ctx)


def _serve_cv(request, as_attachment):
    language, _ = get_current_language(request)
    cv = _cv_file(language)
    if not cv:
        raise Http404("CV not uploaded yet")
    try:
        fh = cv.open("rb")
    except (FileNotFoundError, OSError):
        logger.error("CV file missing on storage: %s", getattr(cv, "name", cv))
        raise Http404("CV file missing")
    response = FileResponse(fh, as_attachment=as_attachment, filename=CV_DOWNLOAD_NAME,
                            content_type="application/pdf")
    response["Cache-Control"] = "public, max-age=600"
    response["X-Robots-Tag"] = "noindex"  # index the /cv/ HTML page, not duplicate PDFs
    return response


@require_GET
def cv_download(request):
    return _serve_cv(request, as_attachment=True)


@require_GET
def cv_view(request):
    return _serve_cv(request, as_attachment=False)


def gallery_page(request):
    language, lang_code = get_current_language(request)
    ar = seo.current_lang() == "ar"
    items = list(GalleryItem.objects.filter(is_public=True))
    categories = [(k, v) for k, v in GalleryItem.CATEGORY_CHOICES if any(i.category == k for i in items)]
    projects = [p for p in get_model_data(Portfolio, language, fallback=True, is_active=True) if p.cover_image]
    title = ("معرض الصور — محمد نبيل | Mohamed Nabil Pro" if ar
             else "Media Gallery — Mohamed Nabil | Mohamed Nabil Pro")
    description = ("صور محمد نبيل المهنية ولقطات من مشاريعه البرمجية." if ar
                   else "Professional photos of Mohamed Nabil and screenshots of his software projects.")
    ctx = get_common_context(request, language, {
        "items": items,
        "categories": categories,
        "project_shots": projects,
        "page_title": title,
        "page_description": description,
    })
    ctx["page_jsonld"] = seo.graph(
        seo.website_entity(), seo.person_entity(ctx.get("site_settings")),
        seo.page_entity(request, title, description, "CollectionPage"),
    )
    return render(request, "gallery.html", ctx)
