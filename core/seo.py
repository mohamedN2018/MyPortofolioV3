"""
SEO + entity helpers: canonical/hreflang URLs, Open Graph defaults and the
Schema.org JSON-LD graph that describes ONE Person entity (Mohamed Nabil).

All absolute URLs are built from settings.SITE_URL (env-driven), never from
the request host, so a dev/preview host can never leak into canonical tags.
"""
import json

from django.templatetags.static import static
from django.utils import translation
from django.utils.safestring import mark_safe

from . import identity

PERSON_ID = "/#person"
WEBSITE_ID = "/#website"

# Two portrait sets; choose with the BRAND_PORTRAIT env/setting:
#   "studio" — the stylised studio portrait the owner prefers (default)
#   "camera" — the unedited camera photo (IMG_20260129_192328.jpg)
PORTRAIT_SETS = {
    "studio": {"base": "brand/mohamed-nabil-software-engineer", "size": 768, "og": "brand/mohamed-nabil-pro-og.jpg"},
    "camera": {"base": "brand/mohamed-nabil-photo", "size": 1200, "og": "brand/mohamed-nabil-pro-og-photo.jpg"},
}


def portrait_set():
    from django.conf import settings
    return PORTRAIT_SETS.get(getattr(settings, "BRAND_PORTRAIT", "studio"), PORTRAIT_SETS["studio"])


def portrait_path(variant=""):
    """variant: '' (full jpg), '400.webp', '800.webp', '400.jpg', '800.jpg'."""
    base = portrait_set()["base"]
    return f"{base}.jpg" if not variant else f"{base}-{variant}"

# Pages whose single URL serves both languages (switch via ?lang=xx), so
# hreflang alternates are meaningful. Detail pages use per-language slugs.
BILINGUAL_URL_NAMES = {
    "home", "about", "identity", "cv", "services", "portfolio", "blog",
    "contact", "gallery",
}

SUPPORTED_LANGS = ("en", "ar")
DEFAULT_LANG = "en"


def absolute(path):
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return identity.site_url() + (path if path.startswith("/") else "/" + path)


def static_abs(path):
    return absolute(static(path))


def current_lang():
    code = (translation.get_language() or DEFAULT_LANG).lower()
    return "ar" if code.startswith("ar") else "en"


def lang_url(path, lang):
    """Public URL of `path` in `lang` (default language has no parameter)."""
    if lang == DEFAULT_LANG:
        return absolute(path)
    return absolute(path) + "?lang=" + lang


def canonical_for(request, lang=None):
    lang = lang or current_lang()
    url = lang_url(request.path, lang)
    page = request.GET.get("page")
    if page and page.isdigit() and page != "1":
        url += ("&" if "?" in url else "?") + "page=" + page
    return url


def alternates_for(request):
    match = getattr(request, "resolver_match", None)
    if not match or match.url_name not in BILINGUAL_URL_NAMES:
        return []
    alts = [{"hreflang": code, "href": lang_url(request.path, code)} for code in SUPPORTED_LANGS]
    alts.append({"hreflang": "x-default", "href": absolute(request.path)})
    return alts


def to_jsonld(data):
    """Serialize for <script type="application/ld+json"> safely."""
    raw = json.dumps(data, ensure_ascii=False, indent=None, separators=(",", ":"))
    raw = raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(raw)


def person_entity(site_settings=None, lang=None):
    lang = lang or current_lang()
    ar = lang == "ar"
    profiles = identity.get_profiles(site_settings)
    portrait = static_abs(portrait_path())
    person = {
        "@type": "Person",
        "@id": absolute(PERSON_ID),
        "name": identity.NAME_EN,
        "alternateName": [identity.NAME_AR, identity.BRAND],
        "url": absolute("/"),
        "mainEntityOfPage": absolute("/about/mohamed-nabil/"),
        "image": {
            "@type": "ImageObject",
            "@id": absolute("/#portrait"),
            "url": portrait,
            "contentUrl": portrait,
            "width": portrait_set()["size"],
            "height": portrait_set()["size"],
            "caption": "Mohamed Nabil (محمد نبيل) — Software Engineer",
        },
        "jobTitle": identity.JOB_TITLE_AR if ar else identity.JOB_TITLE_EN,
        "description": identity.TAGLINE_AR if ar else identity.TAGLINE_EN,
        "knowsAbout": identity.KNOWS_ABOUT,
        "knowsLanguage": ["ar", "en"],
        "worksFor": {"@type": "Organization", "name": identity.WORKS_FOR["name"], "url": identity.WORKS_FOR["url"]},
        "address": {"@type": "PostalAddress", "addressCountry": "EG"},
        "sameAs": [p["url"] for p in profiles],
    }
    email = getattr(site_settings, "contact_email", "") if site_settings else ""
    if email:
        person["email"] = "mailto:" + email
    if site_settings and getattr(site_settings, "show_phone_publicly", False) and site_settings.contact_phone:
        person["telephone"] = site_settings.contact_phone
    return person


def website_entity():
    return {
        "@type": "WebSite",
        "@id": absolute(WEBSITE_ID),
        "url": absolute("/"),
        "name": identity.BRAND,
        "alternateName": [identity.NAME_EN, identity.NAME_AR],
        "inLanguage": ["en", "ar"],
        "publisher": {"@id": absolute(PERSON_ID)},
        "about": {"@id": absolute(PERSON_ID)},
    }


def page_entity(request, title, description, page_type="WebPage", lang=None, breadcrumbs=None):
    lang = lang or current_lang()
    url = canonical_for(request, lang)
    page = {
        "@type": page_type,
        "@id": url + "#webpage",
        "url": url,
        "name": title,
        "description": description,
        "inLanguage": lang,
        "isPartOf": {"@id": absolute(WEBSITE_ID)},
        "about": {"@id": absolute(PERSON_ID)},
    }
    if page_type == "ProfilePage":
        page["mainEntity"] = {"@id": absolute(PERSON_ID)}
    if breadcrumbs:
        page["breadcrumb"] = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": absolute(href)}
                for i, (name, href) in enumerate(breadcrumbs)
            ],
        }
    return page


def graph(*nodes):
    return to_jsonld({"@context": "https://schema.org", "@graph": [n for n in nodes if n]})


def seo_context(request):
    """Context processor: identity + canonical/hreflang + default JSON-LD."""
    from .models import SiteSetting  # local import: avoid app-loading cycles

    from .models import PersonalInfo

    try:
        site_settings = SiteSetting.objects.first()
        from .brand_views import CV_STATIC
        cv_available = CV_STATIC.is_file() or PersonalInfo.objects.exclude(
            resume_file="").exclude(resume_file__isnull=True).exists()
    except Exception:  # DB not ready (e.g. during migrate)
        site_settings, cv_available = None, False

    lang = current_lang()
    ar = lang == "ar"
    name = identity.NAME_AR if ar else identity.NAME_EN
    default_title = (
        f"{identity.NAME_AR} | {identity.JOB_TITLE_AR} — {identity.BRAND}" if ar
        else f"{identity.NAME_EN} | {identity.JOB_TITLE_EN} — {identity.BRAND}"
    )
    default_description = identity.TAGLINE_AR if ar else identity.TAGLINE_EN

    return {
        "brand": {
            "name": name,
            "name_en": identity.NAME_EN,
            "name_ar": identity.NAME_AR,
            "brand": identity.BRAND,
            "job_title": identity.JOB_TITLE_AR if ar else identity.JOB_TITLE_EN,
            "headline": identity.HEADLINE_AR if ar else identity.HEADLINE_EN,
            "tagline": default_description,
            "roles": identity.ROLES_AR if ar else identity.ROLES_EN,
            "country": identity.COUNTRY_AR if ar else identity.COUNTRY_EN,
            "profiles": identity.get_profiles(site_settings),
            "portrait": static(portrait_path()),
            "portrait_400_webp": static(portrait_path("400.webp")),
            "portrait_800_webp": static(portrait_path("800.webp")),
            "portrait_400_jpg": static(portrait_path("400.jpg")),
            "portrait_800_jpg": static(portrait_path("800.jpg")),
            # the other portrait set (shown in the gallery as an additional photo)
            "alt_portrait_800_jpg": static(next(v["base"] for k, v in PORTRAIT_SETS.items() if v is not portrait_set()) + "-800.jpg"),
            "portrait_alt": (
                "صورة محمد نبيل (Mohamed Nabil) — مهندس برمجيات" if ar
                else "Photo of Mohamed Nabil (محمد نبيل) — Software Engineer"
            ),
            "show_phone": bool(site_settings and site_settings.show_phone_publicly and site_settings.contact_phone),
            "email": getattr(site_settings, "contact_email", "") if site_settings else "",
            "cv_available": cv_available,
        },
        "seo": {
            "site_url": identity.site_url(),
            "canonical": canonical_for(request, lang),
            "alternates": alternates_for(request),
            "default_title": default_title,
            "default_description": default_description,
            "og_image": static_abs(portrait_set()["og"]),
            "og_locale": "ar_EG" if ar else "en_US",
            "og_locale_alt": "en_US" if ar else "ar_EG",
            "lang": lang,
            "dir": "rtl" if ar else "ltr",
            "default_jsonld": graph(website_entity(), person_entity(site_settings, lang)),
        },
    }
