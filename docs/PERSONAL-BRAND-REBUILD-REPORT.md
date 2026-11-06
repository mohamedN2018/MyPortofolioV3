# Personal Brand Rebuild — Engineering Report

**Project:** MyPortofolioV3 (https://mohamednabilpro.deplois.net/)
**Date:** 2026-11-06 · **Status:** implemented locally, tested, **not deployed** (production untouched, nothing committed).

> **الملخص بالعربي:** تم توحيد الهوية (محمد نبيل / Mohamed Nabil / Mohamed Nabil Pro)، تجهيز ملف Google للتحقق على جذر الموقع، بناء صفحة الهوية الرسمية وصفحة السيرة الذاتية والمعرض، SEO تقني كامل (canonical، hreflang، sitemap صحيح، robots، JSON-LD لشخص واحد)، صورة شخصية حقيقية محسّنة، إصلاح 6 أخطاء موجودة مسبقاً (منها صفحة About فارغة، Sitemap غير صالح، صفحات عربية ترجع 404 لجوجل، تسرّب اللغة بين الطلبات، Open Redirect)، و25 اختباراً آلياً ناجحاً. يتبقى: النشر على Dokploy + تشغيل أمر المزامنة على قاعدة الإنتاج + التحقق في Search Console.

---

## 1. Original project audit (Phase 1)

| Area | Finding |
|---|---|
| Stack | Django 5.2.11, Python 3.11, single app `core`, Django templates + Bootstrap 5 (BootstrapMade "SnapFolio"), custom `/dashboard/` CMS + Django admin |
| Data | Production: PostgreSQL 17 (Docker Compose on Dokploy, behind Cloudflare). Local: SQLite with **seed/demo data** (fake testimonials, `*.example.com` URLs) — production content differs and lives only in the production DB |
| i18n | Bilingual via `Language` FK on every model + session/`?lang=` switch (no URL prefixes). Arabic objects use separate `-ar` slugs |
| Deploy | `Dockerfile` (gunicorn, `collectstatic`), `media/` is a Docker **volume** (files in repo `media/` do not reach production) |
| Tests | `core/tests.py` was empty — 0 tests |

### Bugs found before changes (all fixed)

| # | Severity | Bug | Evidence |
|---|---|---|---|
| 1 | **Critical (security)** | Production runs with **`DEBUG=True`** — Django's technical 404 page (URL map) is public | `GET /nonexistent-xyz/` on production returns "Page not found at /nonexistent-xyz/" debug page |
| 2 | **Critical (SEO)** | `/sitemap.xml` invalid: blank line before `<?xml …?>` and **relative** `<loc>/about/</loc>` URLs (`site_settings.site_url` does not exist) | live response |
| 3 | **Critical (SEO)** | `robots.txt` points to a relative `Sitemap: /sitemap.xml` | live response |
| 4 | **High** | `/about/` returns **HTTP 200 with an empty body** (`templates/about.html` is 0 bytes) | live response size 0 |
| 5 | **High (SEO)** | Arabic detail pages (`/portfolio/<slug>-ar/`, `/services/<slug>-ar/`) returned **404 for visitors without an Arabic session — including Googlebot** | local crawl |
| 6 | **High (SEO)** | Active language leaked between requests in the same worker (views call `translation.activate()` with no reset) → a cookie-less crawler could get `/` in Arabic or English depending on the previous visitor | failing test, fixed with middleware |
| 7 | Medium (security) | Open redirect in `set_language` (`redirect(request.POST['next'])` unvalidated) | code review |
| 8 | Medium | No spam protection on the contact form | code review |
| 9 | Medium | Template placeholders leaked fake data: "New York, NY 10001", "+1 5589 55488 55", "info@example.com", stat counters "98% Client Satisfaction", "1463 Hours Of Support", "Hard Workers" | `index.html`, `contact.html`, `views.get_common_context` |
| 10 | Medium | Identity inconsistency: "Mohammed Nabil", "MohaMed NabiL", "SnapFolio"; `<title>` "Contact \| " (field `site_settings.site_name` doesn't exist) | live HTML |
| 11 | Low | Missing static placeholders (`assets/img/portfolio/placeholder.jpg`, blog placeholders) → 404s | crawl |
| 12 | Low | No canonical, hreflang, Open Graph, Twitter cards or JSON-LD; empty meta description | live HTML |

## 2. New architecture (incremental, no rewrite)

```
core/identity.py        ← single source of truth: names, titles, verified profiles
core/seo.py             ← canonical/hreflang/OG + Schema.org graph (one Person @id) + context processor
core/brand_views.py     ← google file, robots, sitemap, llms.txt, identity page, CV, gallery
core/middleware.py      ← per-request language isolation (bug #6)
core/management/commands/sync_brand_identity.py ← idempotent DB alignment (dry-run by default)
public/google6dc94822b91e8a80.html ← served byte-for-byte at the site root
static/brand/           ← authentic portrait (sizes/formats), OG image, project screenshots
static/assets/css/brand.css ← brand design layer (loaded after existing CSS)
templates/identity.html, cv.html, gallery.html, includes/contact_block.html
```

Migration `0004_brand_identity_and_gallery` is **additive only**: 4 new `SiteSetting` fields (`gitlab_url`, `stackoverflow_url`, `behance_url`, `show_phone_publicly`) + new `GalleryItem` table. No column removed or altered.

## 3. Pages redesigned / created

| URL | Status |
|---|---|
| `/` | New identity-first hero (three names, real portrait, CTAs: Explore My Work · Download CV · View My CV · Contact), verified profiles, short About + facts card, **CV band**, new project cards, unified contact block. Removed fabricated stats section |
| `/about/mohamed-nabil/` | **New** official identity page (AI/SEO readable, server-rendered, `ProfilePage`) |
| `/about/` | 301 → `/about/mohamed-nabil/` (was an empty 200 page) |
| `/cv/` | **New** recruiter page: HTML CV (summary, skills, experience, projects, education, languages) + lazy PDF preview, mobile fallback |
| `/cv/download/`, `/cv/view/` | PDF as `Mohamed-Nabil-CV.pdf` (attachment / inline), `application/pdf`, `X-Robots-Tag: noindex` |
| `/gallery/` | **New** — authentic portrait, approved `GalleryItem`s (`is_public=False` by default), project screenshots |
| `/contact/` | Rewritten: no fake address/phone, honeypot, rate limit, labels, CV link for recruiters |
| Header / footer | Brand block with portrait, **"My CV" nav item with PDF badge**, Projects, Gallery; footer with CV link + all official profiles |
| All pages | Unified `<title>`, meta description, canonical, hreflang, OG/Twitter, JSON-LD |

Design: deep navy + sky accent (matches OG image), Inter (Latin) / Cairo (Arabic) — Google Fonts reduced from 5 families × all weights to 2 × 5 weights. Light/dark theme kept, skip-link, visible focus, `prefers-reduced-motion` honoured, `aria-current`, labelled form fields.

## 4. Files created or modified

**New:** `core/identity.py`, `core/seo.py`, `core/brand_views.py`, `core/middleware.py`, `core/management/commands/sync_brand_identity.py`, `core/migrations/0004_brand_identity_and_gallery.py`, `public/google6dc94822b91e8a80.html`, `static/brand/*` (6 portrait/OG files + 11 project screenshots), `static/assets/css/brand.css`, `static/assets/img/{portfolio,blog}/placeholder*.jpg`, `templates/identity.html`, `templates/cv.html`, `templates/gallery.html`, `templates/includes/contact_block.html`, `docs/*.md`.

**Modified:** `config/settings.py` (SITE_URL, WhiteNoise, SERVE_MEDIA, PUBLIC_ROOT, security headers, cache, middleware, context processor), `config/urls.py` (media in production), `core/urls.py`, `core/views.py` (about redirect, translated-object lookup, open-redirect fix, honeypot + rate limit, JSON-LD for projects/posts, no fabricated stats), `core/models.py`, `core/admin.py`, `core/dashboard/views.py`, `templates/dashboard/settings.html`, `templates/base.html`, `templates/index.html`, `templates/contact.html`, `templates/includes/{header,footer,social_links}.html`, title/description blocks in all other page templates, `core/tests.py`.

Backups: git is the baseline (working tree was clean except your own deleted media files, which I did not touch). Local DB backup: `C:\Users\MOHAME~1\AppData\Local\Temp\claude\de7e02055d446579\b59cfd54-4d66-45e9-b826-f7fd0062b6df\scratchpad\db.sqlite3.bak`.

## 5. Google Search Console verification

* The provided path `F:\4_docker-composer\Django Project\1- google6dc94822b91e8a80` **does not exist**. The real file was found at `media/google6dc94822b91e8a80.html` (53 bytes: `google-site-verification: google6dc94822b91e8a80.html`).
* `media/` is a Docker volume, so a file there **would not be deployed**. It was copied byte-identical (`cmp` = identical, SHA-256 `cd29df79…19fe`) to `public/` and served by a whitelisted route (`^google[0-9a-f]{8,32}\.html$`) that returns the raw bytes, `200`, `text/html`, exempt from the HTTPS redirect.
* Verified locally (DEBUG=True and DEBUG=False, HTTP and HTTPS): status 200, body identical to the original.
* **Production currently returns 404** for `/google6dc94822b91e8a80.html` (checked 2026-11-06) — it will work only after deployment. **Verification has NOT been completed.**

## 6. SEO improvements

Canonical (absolute, from `SITE_URL` env, default `https://<MAIN_DOMAIN>`), `hreflang` en/ar/x-default on bilingual URLs (`?lang=ar`), unique titles `Page | Mohamed Nabil — Mohamed Nabil Pro`, meta descriptions, OG (`profile`/`article`), Twitter `summary_large_image`, `robots` meta (`noindex` on search + error pages), valid XML sitemap with absolute URLs + `xhtml:link` alternates + image entries, robots.txt with absolute sitemap and private paths disallowed, `llms.txt`, 301 for `/about/`, real 404 status, image `alt`/`width`/`height`/`loading="lazy"`/`fetchpriority`.

## 7. Structured data

One `@graph` per page: `WebSite` (`/#website`) + **one** `Person` (`/#person`, `name: Mohamed Nabil`, `alternateName: [محمد نبيل, Mohamed Nabil Pro]`, `image` ImageObject of the authentic portrait, `jobTitle`, `knowsAbout`, `knowsLanguage`, `addressCountry: EG`, `sameAs` = 6 verified profiles, `email`; `telephone` only if `show_phone_publicly`) + page node (`ProfilePage` for identity/CV, `CollectionPage` for gallery, `WebPage` + `BreadcrumbList`; `CreativeWork` for projects and `BlogPosting` for posts, both with `author → /#person`). Microdata was deliberately not added, to avoid a second Person entity.
Validation: 58 JSON-LD blocks parsed during the crawl; tests assert exactly one Person per page with the same `@id`. **Not yet validated with Google's Rich Results Test / validator.schema.org** (requires the deployed URL).

## 8. Media audit & optimisation

| File | Classification | Use |
|---|---|---|
| `media/testimonials/IMG_20260129_192328.jpg` (1771×2560) | **Authentic camera photo** of Mohamed Nabil | Official portrait. Crop + resize only (no retouching): `static/brand/mohamed-nabil-software-engineer{,-400,-800}.{jpg,webp}` (14–144 KB), OG image `mohamed-nabil-pro-og.jpg` 1200×630 |
| `media/profile/5954150915667332638_121.jpg`, `Gemini_Generated_Image_*.jpg`, production `profile/Gemini_9QUYVuR.png` | **AI-generated/edited (Gemini ✦ mark)** | Not used as documentary photo. Recommend not using as the profile photo |
| `media/profile/1-.png` | Branded graphic "#MohaMed NabiL Pro" | Not used (inconsistent spelling) |
| `media/logo/Gemini_Generate.png` | "MN" logo | Brand asset, unchanged |
| `media/testimonials/31qTl2XzraL._AC_.jpg` (boots), `media/blog/*antiviral*.webp`, `media/favicon/651103916…jpg` (Egypt map art) | **Unrelated images** | Not used; should be removed from testimonials/favicon in the CMS |
| `media/portfolio/cover/t.png` (10×10) | Broken placeholder | Not used |
| Project screenshots from SESHAT, SWENET, Qtech_company repos | Real UI screenshots | Optimised WebP in `static/brand/projects/` (13–56 KB) |

Originals were not modified or deleted.

## 9. CV

* Six CV files exist (4 local + 2 on production) — **all are the same document** (MD5 `8460732bf6…`, created 2026-02-12). No newer version exists.
* Content conflicts to fix in the PDF (I did not generate a new CV): name spelled "**Mohammed** Nabil"; title "Backend Developer" only; experience "2025-01 – Present" while the website DB says 2023; does not mention Seshat, SWENET or Q-Tech; includes the private phone number.
* Implemented: `/cv/` page, `/cv/download/` (`Mohamed-Nabil-CV.pdf`, attachment), `/cv/view/` (inline), PDF preview iframe loaded only on `/cv/` (lazy), mobile fallback buttons, CV entry points in nav (highlighted), hero (Download + View), homepage CV section, identity/About page, footer, contact block. Download buttons are hidden automatically when no PDF is uploaded (the `/cv/` page then shows a placeholder, never an invented document).
* Not implemented: download analytics (no analytics stack exists; adding a third-party tracker was out of scope / privacy).

## 10. Verified project content (case studies)

Facts were gathered from each repository's README/docs/dependency files. The `sync_brand_identity --projects` command creates EN + AR case studies:

| Project | Ownership as stated | Evidence |
|---|---|---|
| Seshat — POS & Business Management | Q-Tech Solutions product ("Proprietary. © Q-Tech Solutions"), repo `github.com/mohamedN2018/SESHAT`, live `seshat.deplois.net` | README, docs/STATE.md (1,136 passing tests) |
| SWENET — Vehicle Care Platform | Personal project; TypeScript rebuild of the "CarCare" graduation project (original authors credited) | ROADMAP.md, git remotes |
| Q-Tech Solutions — Company Platform | Q-Tech Solutions; public site q-tech-solutions.com | settings, FRONTEND_REBUILD_PLAN.md |

Not created (insufficient verified material): **Q Run** (only a mention on the Q-Tech site), **Q-Tech PharmaSyst** (only a store card in a Q-Tech screenshot), **HRS** (repo under `Code-Any-Way` org in a testing folder), **Qshop** (offline desktop: no screenshots/remote). Kunooz already exists in the DB.
**Please review "My role" wording** — the repos show you as main committer, but your exact title (founder/CTO/lead) for Q-Tech is not documented anywhere I could verify, so I did not claim it.

## 11. Tests executed (actual results)

| Check | Result |
|---|---|
| `python manage.py check` | 0 issues |
| `python manage.py test core` | **25 tests, all passed** (Google file bytes/404s/HTTPS exemption, robots, sitemap XML + absolute URLs + hreflang + images, llms.txt, EN/AR `lang`/`dir`/canonical, single Person entity on 4 page types, ProfilePage, CreativeWork author, `/about/` 301, phone privacy, no fabricated stats, safe external links, 404, CV download/view headers + bytes, CV entry points, open-redirect, `?lang` stripping, honeypot, rate limit, gallery privacy, Arabic slug without session) |
| Internal link crawl (local server) | 102 URLs, **0 broken** (after fixing 16 pre-existing 404s) |
| JSON-LD parse | 58 blocks, all valid JSON |
| `collectstatic` with WhiteNoise compressed storage | 236 files, OK |
| DEBUG=False simulation | Google file 200 (HTTP + HTTPS), media 200, CV download 200, unknown URL 404 |
| `check --deploy` (DEBUG=False) | 3 warnings: HSTS not set (intentional, opt-in), **SECRET_KEY weak in local .env** (check production), X_FRAME_OPTIONS=SAMEORIGIN (intentional, for CV preview) |
| Screenshots (Playwright + Chrome) | Home EN/AR desktop + mobile (390px), identity, CV EN/AR mobile, project, gallery — RTL/LTR correct, no horizontal overflow (`scrollWidth == viewport`) |
| External links | GitHub 200, GitLab 200, Behance 200, seshat.deplois.net 200, q-tech-solutions.com 200; LinkedIn 999, Stack Overflow 403, Facebook 400 = **bot protection**, verify manually in a browser |
| Not executed | Lighthouse/Core Web Vitals (no Lighthouse installed), Google Rich Results Test, production HTTP tests of new routes (not deployed) |

## 12. Outstanding issues

1. Production `DEBUG=True` — must be set to `False` in Dokploy env (code now serves static via WhiteNoise and media via Django, so it keeps working).
2. Production DB still holds old names/titles/bio and the Gemini profile image → run the sync command (below).
3. CV PDF needs a real update by you (see §9).
4. Seed/demo content in production? Production testimonials list "No reviews yet", but experience entries contain unverified claims ("15+ projects for clients worldwide", "10,000+ job listings", "reducing development time by 30%") and two duplicated freelance entries → edit from the dashboard.
5. Skills section still shows self-rated percentages (existing CMS data).
6. Unrelated images in testimonials/favicon slots (boots, antiviral, Egypt map).
7. Remaining legacy templates (services, blog list, portfolio list) keep the old SnapFolio layout styled by the new tokens; a deeper visual pass is possible later.

## 13. Manual steps required

1. **Back up the production DB** (Dokploy → postgres → `pg_dump`).
2. Deploy (Dokploy rebuild). Set env: `MY_DEBUG=False`; optional `SITE_URL=https://mohamednabilpro.deplois.net`.
3. In the container: `python manage.py migrate` then
   `python manage.py sync_brand_identity` (review dry run) →
   `python manage.py sync_brand_identity --apply --projects --portrait --bio --clear-unverified-profiles`
   (drop `--bio` / `--portrait` if you prefer to edit those by hand).
4. Open `https://mohamednabilpro.deplois.net/google6dc94822b91e8a80.html` → must show the one-line token → click **Verify** in Search Console. Keep the file forever.
5. Search Console → Sitemaps → submit `https://mohamednabilpro.deplois.net/sitemap.xml`; URL Inspection → request indexing for `/`, `/about/mohamed-nabil/`, `/cv/`, `/?lang=ar`.
6. Run https://search.google.com/test/rich-results on `/about/mohamed-nabil/`.
7. Upload an updated CV PDF from the dashboard (Personal Info → resume).
8. Add each profile's "website" field = `https://mohamednabilpro.deplois.net/` and use the same portrait + name on LinkedIn, GitHub, GitLab, Stack Overflow, Behance, Facebook (reciprocal links).

## 14. Production deployment checklist

- [ ] DB backup taken
- [ ] `MY_DEBUG=False` in Dokploy env
- [ ] Image rebuilt (Dockerfile `collectstatic` picks up `static/brand`)
- [ ] `migrate` (0004, additive)
- [ ] `sync_brand_identity` dry run reviewed, then `--apply`
- [ ] `/google6dc94822b91e8a80.html` → 200 + token, then Verify
- [ ] `/robots.txt`, `/sitemap.xml`, `/llms.txt` → 200
- [ ] `/cv/download/` → PDF named `Mohamed-Nabil-CV.pdf`
- [ ] `/portfolio/<slug>-ar/` opens in a private window (no session)
- [ ] `/x-not-found/` shows the custom 404 (not the Django debug page)
- [ ] Rich Results Test passes; sitemap submitted
