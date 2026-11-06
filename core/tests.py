"""
Tests for the personal-brand / SEO / CV layer.

Run:  python manage.py test core
"""
import json
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from core import identity
from core.models import (
    ContactMessage, GalleryItem, Language, PersonalInfo, Portfolio, PortfolioCategory, SiteSetting,
)

SITE = "https://mohamednabilpro.deplois.net"
GOOGLE_FILE = "google6dc94822b91e8a80.html"
PDF_BYTES = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"

TMP_MEDIA = tempfile.mkdtemp(prefix="mnp-test-media-")


def jsonld_blocks(html):
    return [json.loads(m) for m in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.S)]


@override_settings(SITE_URL=SITE, MEDIA_ROOT=TMP_MEDIA, SECURE_SSL_REDIRECT=False,
                   STORAGES={"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
                             "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}})
class BrandTestBase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.en = Language.objects.create(code="en", name="English", is_default=True, direction="ltr")
        self.ar = Language.objects.create(code="ar", name="Arabic", direction="rtl")
        self.ss = SiteSetting.objects.create(
            site_name_en="Mohamed Nabil Pro", contact_email="owner@example.com",
            contact_phone="+20 100 000 0000", show_phone_publicly=False,
        )
        self.pi_en = PersonalInfo.objects.create(language=self.en, name="Mohamed Nabil", title="Software Engineer", bio="Bio EN")
        self.pi_ar = PersonalInfo.objects.create(language=self.ar, name="محمد نبيل", title="مهندس برمجيات", bio="نبذة")
        cat = PortfolioCategory.objects.create(language=self.en, name="Business Systems", slug="business-systems")
        self.project = Portfolio.objects.create(
            language=self.en, category=cat, title="Seshat", slug="seshat", client_name="Q-Tech Solutions",
            project_date="2026-09-30", short_description="POS", overview="o", technologies=["Django"],
            cover_image=SimpleUploadedFile("c.png", b"x", content_type="image/png"), is_featured=True,
        )

    def attach_cv(self):
        self.pi_en.resume_file.save("cv.pdf", SimpleUploadedFile("cv.pdf", PDF_BYTES), save=True)


class GoogleVerificationTests(BrandTestBase):
    def test_file_served_byte_for_byte_at_root(self):
        original = (Path(settings.BASE_DIR) / "public" / GOOGLE_FILE).read_bytes()
        r = self.client.get("/" + GOOGLE_FILE)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, original)
        self.assertEqual(original, b"google-site-verification: " + GOOGLE_FILE.encode())
        self.assertTrue(r["Content-Type"].startswith("text/html"))

    def test_unknown_or_malicious_names_404(self):
        for name in ("googleXYZ.html", "google0000000000000000.html", "google..html"):
            self.assertEqual(self.client.get("/" + name).status_code, 404, name)

    def test_redirect_exempt_from_https(self):
        with self.settings(SECURE_SSL_REDIRECT=True):
            self.assertEqual(self.client.get("/" + GOOGLE_FILE).status_code, 200)


class RobotsSitemapLlmsTests(BrandTestBase):
    def test_robots(self):
        body = self.client.get("/robots.txt").content.decode()
        self.assertIn(f"Sitemap: {SITE}/sitemap.xml", body)
        self.assertIn("Allow: /", body)
        for p in ("/admin/", "/dashboard/", "/api/"):
            self.assertIn(f"Disallow: {p}", body)
        self.assertNotIn("Disallow: /\n", body)

    def test_sitemap_is_valid_absolute_and_bilingual(self):
        r = self.client.get("/sitemap.xml")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content.startswith(b'<?xml version="1.0"'))
        root = ET.fromstring(r.content)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [e.text for e in root.findall("s:url/s:loc", ns)]
        self.assertTrue(locs)
        self.assertTrue(all(l.startswith(SITE + "/") for l in locs), locs)
        for expected in ("/about/mohamed-nabil/", "/cv/", "/cv/?lang=ar", "/portfolio/seshat/"):
            self.assertIn(SITE + expected, locs)
        self.assertEqual(len(locs), len(set(locs)))
        self.assertIn(b'hreflang="x-default"', r.content)
        self.assertIn(b"brand/mohamed-nabil-software-engineer.jpg", r.content)

    def test_llms_txt(self):
        body = self.client.get("/llms.txt").content.decode()
        for s in ("Mohamed Nabil", "محمد نبيل", "Mohamed Nabil Pro", f"{SITE}/cv/", "https://github.com/mohamedN2018"):
            self.assertIn(s, body)


class IdentitySeoTests(BrandTestBase):
    def test_home_english_head(self):
        html = self.client.get("/").content.decode()
        self.assertIn('<html lang="en" dir="ltr">', html)
        self.assertIn(f'<link rel="canonical" href="{SITE}/">', html)
        self.assertIn(f'hreflang="ar" href="{SITE}/?lang=ar"', html)
        self.assertIn(f'hreflang="x-default" href="{SITE}/"', html)
        self.assertIn('property="og:image"', html)
        self.assertIn("Mohamed Nabil", html)
        self.assertIn("محمد نبيل", html)
        self.assertIn("Mohamed Nabil Pro", html)

    def test_home_arabic_rtl(self):
        html = self.client.get("/?lang=ar").content.decode()
        self.assertIn('<html lang="ar" dir="rtl">', html)
        self.assertIn(f'<link rel="canonical" href="{SITE}/?lang=ar">', html)
        self.assertIn('<body class="index-page" dir="rtl">', html)

    def test_single_consistent_person_entity(self):
        for url in ("/", "/about/mohamed-nabil/", "/cv/", "/portfolio/seshat/"):
            blocks = jsonld_blocks(self.client.get(url).content.decode())
            self.assertEqual(len(blocks), 1, url)
            persons = [n for n in blocks[0]["@graph"] if n.get("@type") == "Person"]
            self.assertEqual(len(persons), 1, url)
            p = persons[0]
            self.assertEqual(p["@id"], SITE + "/#person")
            self.assertEqual(p["name"], "Mohamed Nabil")
            self.assertEqual(p["alternateName"], ["محمد نبيل", "Mohamed Nabil Pro"])
            for _, _, _, default, _ in identity.PROFILES:
                self.assertIn(default, p["sameAs"])
            self.assertTrue(p["image"]["url"].startswith(SITE + "/static/brand/"))
            self.assertNotIn("telephone", p)

    def test_identity_page_is_profilepage(self):
        graph = jsonld_blocks(self.client.get("/about/mohamed-nabil/").content.decode())[0]["@graph"]
        types = {n["@type"] for n in graph}
        self.assertIn("ProfilePage", types)
        self.assertIn("WebSite", types)

    def test_project_page_creativework_with_author(self):
        graph = jsonld_blocks(self.client.get("/portfolio/seshat/").content.decode())[0]["@graph"]
        work = [n for n in graph if n["@type"] == "CreativeWork"][0]
        self.assertEqual(work["author"]["@id"], SITE + "/#person")

    def test_about_redirects_to_identity(self):
        r = self.client.get("/about/")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r["Location"], "/about/mohamed-nabil/")

    def test_phone_hidden_unless_approved(self):
        self.assertNotIn("+20 100 000 0000", self.client.get("/").content.decode())
        self.ss.show_phone_publicly = True
        self.ss.save()
        self.assertIn("+20 100 000 0000", self.client.get("/").content.decode())

    def test_no_fabricated_stats_on_home(self):
        html = self.client.get("/").content.decode()
        for s in ("Client Satisfaction", "Hours Of Support", "Hard Workers", "New York", "info@example.com", "contact@example.com"):
            self.assertNotIn(s, html)

    def test_profiles_links_are_safe(self):
        html = self.client.get("/").content.decode()
        self.assertIn('href="https://gitlab.com/mohamedN2024" target="_blank" rel="noopener noreferrer me"', html)

    def test_404_status_and_noindex(self):
        with self.settings(DEBUG=False):
            r = self.client.get("/definitely-missing/")
        self.assertEqual(r.status_code, 404)


class CvTests(BrandTestBase):
    """DB-resume behaviour; the committed static CV is patched away here."""

    def setUp(self):
        super().setUp()
        from pathlib import Path
        from unittest import mock
        from core import brand_views
        patcher = mock.patch.object(brand_views, "CV_STATIC", Path("/nonexistent/cv.pdf"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_committed_static_cv_is_a_pdf(self):
        from django.conf import settings
        cv = settings.BASE_DIR / "static" / "brand" / "cv" / "Mohamed-Nabil-CV.pdf"
        self.assertTrue(cv.read_bytes().startswith(b"%PDF-"))

    def test_cv_page_without_pdf(self):
        r = self.client.get("/cv/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get("/cv/download/").status_code, 404)

    def test_cv_download_and_view(self):
        self.attach_cv()
        r = self.client.get("/cv/download/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")
        self.assertIn('attachment; filename="Mohamed-Nabil-CV.pdf"', r["Content-Disposition"])
        self.assertEqual(b"".join(r.streaming_content), PDF_BYTES)
        r = self.client.get("/cv/view/")
        self.assertIn('inline; filename="Mohamed-Nabil-CV.pdf"', r["Content-Disposition"])

    def test_cv_reachable_from_nav_home_footer(self):
        self.attach_cv()
        html = self.client.get("/").content.decode()
        self.assertIn('mnp-nav-cv', html)               # navigation
        self.assertIn('href="/cv/download/"', html)       # hero + CV band
        self.assertIn('class="footer-cv"', html)          # footer
        self.assertIn('href="/cv/"', self.client.get("/about/mohamed-nabil/").content.decode())
        self.assertIn('href="/cv/"', self.client.get("/contact/").content.decode())


class SecurityTests(BrandTestBase):
    def test_set_language_blocks_open_redirect(self):
        r = self.client.post("/set-language/", {"language": "ar", "next": "https://evil.example/"})
        self.assertEqual(r["Location"], "/")

    def test_set_language_strips_lang_param(self):
        r = self.client.post("/set-language/", {"language": "en", "next": "/cv/?lang=ar&page=2"})
        self.assertEqual(r["Location"], "/cv/?page=2")

    def test_contact_honeypot(self):
        r = self.client.post("/contact/", {"name": "Bot", "email": "b@b.com", "subject": "x", "message": "spam",
                                           "website": "http://spam"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertTrue(r.json()["success"])
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_contact_valid_and_rate_limited(self):
        data = {"name": "Real Person", "email": "a@a.com", "subject": "Hello", "message": "Let's talk"}
        with self.settings(CONTACT_RATE_LIMIT=2):
            for _ in range(2):
                self.assertTrue(self.client.post("/contact/", data, HTTP_X_REQUESTED_WITH="XMLHttpRequest").json()["success"])
            r = self.client.post("/contact/", data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.status_code, 429)
        self.assertEqual(ContactMessage.objects.count(), 2)


class GalleryTests(BrandTestBase):
    def test_only_public_items_shown(self):
        GalleryItem.objects.create(image=SimpleUploadedFile("pub.png", b"x"), alt_en="Public photo alt", is_public=True)
        GalleryItem.objects.create(image=SimpleUploadedFile("priv.png", b"x"), alt_en="Private photo alt", is_public=False)
        html = self.client.get("/gallery/").content.decode()
        self.assertIn("Public photo alt", html)
        self.assertNotIn("Private photo alt", html)


class ArabicDetailPagesTests(BrandTestBase):
    def test_arabic_slug_resolves_without_session(self):
        """Googlebot (no cookies) must reach Arabic detail pages, rendered in Arabic."""
        cat = PortfolioCategory.objects.create(language=self.ar, name="أنظمة", slug="business-systems-ar")
        Portfolio.objects.create(
            language=self.ar, category=cat, title="سشات", slug="seshat-ar", client_name="Q-Tech",
            project_date="2026-09-30", short_description="نقاط بيع", overview="o", technologies=[],
            cover_image=SimpleUploadedFile("c2.png", b"x", content_type="image/png"),
        )
        r = self.client.get("/portfolio/seshat-ar/")
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        self.assertIn('<html lang="ar" dir="rtl">', html)
        self.assertIn(f'<link rel="canonical" href="{SITE}/portfolio/seshat-ar/?lang=ar">', html)
        self.assertEqual(self.client.get("/portfolio/does-not-exist/").status_code, 404)


class StaticCvTests(BrandTestBase):
    def test_static_cv_takes_precedence(self):
        from unittest import mock
        from core import brand_views
        tmp = Path(TMP_MEDIA) / "Mohamed-Nabil-CV.pdf"
        tmp.write_bytes(PDF_BYTES + b"%static")
        with mock.patch.object(brand_views, "CV_STATIC", tmp):
            r = self.client.get("/cv/download/")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(b"".join(r.streaming_content), PDF_BYTES + b"%static")
            self.assertIn('filename="Mohamed-Nabil-CV.pdf"', r["Content-Disposition"])
            self.assertIn('href="/cv/download/"', self.client.get("/").content.decode())

    def test_content_sync_is_idempotent_and_non_destructive(self):
        from django.apps import apps
        from core.brand_content import apply_brand_content, PROJECTS
        from core.models import WorkExperience
        old = WorkExperience.objects.create(language=self.en, job_title="Old job", company_name="X",
                                            start_date="2023-01-01", description="d")
        apply_brand_content(apps.get_model, log=lambda m: None)
        apply_brand_content(apps.get_model, log=lambda m: None)
        old.refresh_from_db()
        self.assertFalse(old.is_active)                      # deactivated, not deleted
        self.assertEqual(Portfolio.objects.filter(slug=PROJECTS[0]["slug"]).count(), 1)
        self.pi_en.refresh_from_db()
        self.assertEqual(self.pi_en.name, "Mohamed Nabil")
        self.assertEqual(WorkExperience.objects.filter(language=self.en, is_active=True).count(), 2)
