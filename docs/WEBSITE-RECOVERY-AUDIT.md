# Website Recovery Audit — Mohamed Nabil Pro

**Date:** 2026-11-07 · **Branch audited:** `main` @ `60450ce` (live) · **Work branch:** `redesign/premium-v2`

> ملخص: الموقع الحالي على الإنتاج يعمل لكنه مبني على قالب SnapFolio بشريط جانبي، وفيه مشاكل تصميم وتجاوب واضحة (زر القائمة فوق العناوين على التابلت والموبايل، زر الوضع الليلي عائم فوق المحتوى، صفحات قديمة بتصميم مختلف). هذا التقرير يوثّق السبب والحالة قبل إعادة البناء.

## 1. Architecture (verified)

| Item | Finding |
|---|---|
| Framework | Django 5.2.11, Python 3.11, single app `core` (+ `core/dashboard` custom admin) |
| Templates | Django templates; until now the BootstrapMade "SnapFolio" template (left sidebar, Bootstrap 5, AOS, Swiper, Isotope, Typed, PureCounter) |
| Data | Production: PostgreSQL 17 in Docker Compose on Dokploy; local: SQLite seed data |
| i18n | `Language` FK per model, `?lang=` / session switch, `-ar` slugs for Arabic objects |
| Deploy | GitHub `main` → Dokploy auto-deploy (verified 2026-11-06), behind Cloudflare; Traefik with Let's Encrypt |
| Static | WhiteNoise with finders (Docker build `collectstatic` fails silently without env vars) |

## 2. Git state at start of this phase

- `main` = `60450ce` (brand/SEO rebuild, deployed with owner approval 2026-11-06).
- Uncommitted local work at start: new hero/nav experiment + portrait swap. Moved to branch `redesign/premium-v2`.
- Owner's own unstaged deletions (`media/profile/*`, `static/assets/img/*`) were left untouched.

## 3. Why the site looked broken (root causes)

1. **Template architecture:** a fixed 330px left sidebar from SnapFolio; at < 1200px it became an off-canvas panel whose toggle (`.header-toggle`) is absolutely positioned at the top-right — in RTL it sat **on top of page titles** (verified in screenshots at 1024px and 390px).
2. **Floating theme toggle** (`#theme-toggle`, fixed position) overlapped content on mobile.
3. **Two design systems at once:** the first rebuild restyled only the home/identity/CV pages; Portfolio, Project detail, Services, Blog and Error pages still used SnapFolio markup with ~1,000-line inline `<style>` blocks → inconsistent look.
4. **Heavy, unused front-end payload:** full Bootstrap (232 KB) + `main.css` (73 KB) + AOS/Swiper/Isotope/Typed/PureCounter/Waypoints JS on every page.
5. **Mobile filters before content:** portfolio filter sidebar rendered above the projects on mobile.
6. **Fabricated defaults:** home testimonials fell back to "Excellent project! Very professional work." when a rating had no comment; skills showed self-rated % bars.

## 4. Other findings

| Severity | Finding | Status |
|---|---|---|
| High | Production ran `DEBUG=True` | Fixed 2026-11-07 via Dokploy env (owner-authorised), verified 404 page no longer the debug page |
| High | 3 CV links return 404: `qshop.deplois.net` (no service has this domain), `walaee.deplois.net`, `qtechpharmasyst.deplois.net` (all containers stopped ~2 weeks ago, exit 0 = stopped deliberately) | **Not changed** — needs owner decision |
| Medium | pgAdmin published on host port 5020 with `SERVER_MODE=False` (no login) | Reachable only from the LAN (192.168.0.7), not from the internet; recommend removing the port mapping |
| Medium | Domain `config-db.deplois.net` routed to the Postgres service on port 3000 (useless, confusing) | Not changed; recommend deleting in Dokploy |
| Low | Cloudflare does not force HTTPS for visitors (http → 200) | Recommend "Always Use HTTPS" in Cloudflare (not changed) |
| Info | New CV PDF not on disk (only sent as chat attachment) | Waiting for owner to save `static/brand/cv/Mohamed-Nabil-CV.pdf` |

## 5. Media inventory

| Asset | Type | Use |
|---|---|---|
| `old-profile` (production `media/profile/Gemini_9QUYVuR.png`) | Studio-style portrait, **AI-enhanced (Gemini)**; owner explicitly prefers it | Default site portrait (`BRAND_PORTRAIT=studio`) — see decision in rebuild report |
| `media/testimonials/IMG_20260129_192328.jpg` | Unedited camera photo | `BRAND_PORTRAIT=camera` set + shown in gallery |
| SESHAT / Q-Tech / SWENET repo screenshots, live screenshots of hrs / nesmacakes / q-tech-solutions.com | Real product UI | Project covers & galleries |
| Boots photo, antiviral image, Egypt-map art in testimonials/favicon slots | Unrelated | Not used |

## 6. Recovery plan (executed on `redesign/premium-v2`)

1. Replace the sidebar with a sticky top navigation and an accessible mobile menu.
2. One design system (`static/assets/css/brand.css`) for every public page; delete legacy inline styles by rewriting templates.
3. Load only Bootstrap reboot + grid + utilities (RTL builds for Arabic); drop `main.css`, AOS, Swiper, Isotope, Typed, PureCounter, Waypoints; lightbox only on project pages.
4. Hero with a lightweight 3D scene (canvas point-sphere + CSS 3D depth), desktop-only effects, reduced-motion respected.
5. Keep all URLs, views, models, admin and data. No new migrations.
