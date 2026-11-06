# Test Results — branch `redesign/premium-v2` (2026-11-07)

All results below were actually executed on the local machine (Windows 11, Python 3.11.17, Chrome 13x headless via Playwright, Lighthouse 12.6.0).

## Backend
| Check | Command | Result |
|---|---|---|
| System check | `python manage.py check` | 0 issues |
| Migrations consistency | `python manage.py makemigrations --check --dry-run` | No changes detected |
| Test suite | `python manage.py test core` | **27 tests, OK** |
| Covered by tests | Google file bytes/404/HTTPS exemption · robots · sitemap XML, absolute URLs, hreflang, images · llms.txt · EN/AR `lang`/`dir`/canonical · single Person entity on 4 page types · ProfilePage · CreativeWork author · `/about/` 301 · phone privacy · no fabricated stats · safe external links · 404 · CV download/view headers + bytes · static CV precedence · CV entry points (nav/hero/footer/about/contact) · open-redirect guard · `?lang` stripping · honeypot · rate limit · gallery privacy · Arabic slug without session · idempotent non-destructive content sync | |

## Frontend (automated Playwright sweep)
Pages: home, about/identity, portfolio, project detail, CV, contact, blog, services, gallery, 404 · Languages: EN + AR · Widths: 1920, 1440, 1280, 1024, 768, 390, 360 (140 page loads).

| Check | Result |
|---|---|
| Horizontal overflow (`scrollWidth > viewport`) | **0** (after fixing nav fit ≤ 575px and gutter padding ≥ 992px) |
| JavaScript console / page errors | **0** |
| Broken images | **0** |
| Touch targets < 32px | Only stretched-link titles inside fully clickable cards and radio inputs inside 40px labels (false positives, verified manually) |
| Mobile menu | Opens/closes, Esc closes, link click closes, `aria-expanded` updates (screenshot `docs/screenshots/mobile-menu-open-en.jpg`) |
| Internal link crawl (earlier phase, same URLs) | 109 URLs, 0 broken |

## Lighthouse (mobile emulation, local `runserver`, **no gzip/brotli**)
| Page | Perf | A11y | Best practices | SEO | LCP | CLS |
|---|---|---|---|---|---|---|
| `/?lang=en` | 76 | 96 | 100 | 100 | 4.4 s | 0.01 |
| `/?lang=ar` | 76 | 96 | 100 | 100 | 4.4 s | 0.002 |
| `/cv/?lang=en` | 82 | 96 | 100 | 100 | 3.7 s | 0 |
| `/portfolio/hr-payroll-system/` | 75 | 96 | 100 | 100 | 4.7 s | 0 |
Before the CSS/JS slimming the home page scored 66 (LCP 5.7 s, 925 KB). Production adds Cloudflare compression and caching, which local runs do not include — re-measure after deploy.

## Visual QA
Screenshots reviewed: `docs/screenshots/` (desktop home EN/AR, mobile home EN/AR, about, portfolio, project, CV EN + AR mobile, contact AR, mobile menu). Defects found and fixed during QA: nav overflow at 360–390px, 4px gutter overflow at 1024px, unstyled back-to-top after removing `main.css`, empty blog card images (fallback added), year formatting "2,019".

## Not executed
- Google Rich Results Test / Search Console live tests (require deployed v2 and the owner's Google account).
- Real-device testing (iOS Safari, Android Chrome) — emulation only.
- Screen-reader walkthrough (automated a11y only).
