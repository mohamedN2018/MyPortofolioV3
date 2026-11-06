# SEO & Google Search Console Report

**Property:** https://mohamednabilpro.deplois.net/ — **verified** by the owner (HTML file method). Verification file `public/google6dc94822b91e8a80.html` is untouched and still served (200, byte-identical) — covered by an automated test.

## 1. Technical SEO (implemented, live since 2026-11-06; v2 keeps all of it)
| Item | Implementation | Evidence |
|---|---|---|
| Titles | Unique per page: `Page | Mohamed Nabil — Mohamed Nabil Pro`; projects use `meta_title` | template blocks |
| Descriptions | Per page, Arabic and English | template blocks |
| Canonical | Absolute, from `SITE_URL`; Arabic variant `?lang=ar` | tests `test_home_english_head`, `test_home_arabic_rtl` |
| hreflang | en / ar / x-default on bilingual URLs | tests |
| robots meta | `index, follow, max-image-preview:large`; `noindex` on search + error pages | templates |
| robots.txt | Allows all; disallows `/admin/ /dashboard/ /api/ /search/ /set-language/ /i18n/`; absolute sitemap. Cloudflare prepends its managed content-signal block (search=yes, ai-train=no) | live 200 |
| sitemap.xml | Valid XML, absolute HTTPS, hreflang alternates, image entries, active objects only | live 200, `test_sitemap_is_valid_absolute_and_bilingual` |
| Status codes | Real 404 (custom page, `noindex`), `/about/` → 301 | tests, live |
| Breadcrumbs | Visible on every inner page + `BreadcrumbList` in JSON-LD | templates |
| OG / Twitter | `og:*`, `profile:*`, `summary_large_image`; per-project/article images | templates |
| Language | `<html lang dir>` correct; RTL Bootstrap for Arabic in v2 | tests |
| Arabic crawlability | `-ar` detail pages resolve without session (fixed bug) | `test_arabic_slug_resolves_without_session` |

## 2. Structured data
One `@graph` per page: `WebSite` + a single `Person` (`/#person`; `name`, `alternateName` [محمد نبيل, Mohamed Nabil Pro], `image` ImageObject, `jobTitle`, `worksFor` Q-Tech Solutions (stated in CV), `knowsAbout`, `sameAs` ×6) + page node (`ProfilePage` for identity/CV, `CollectionPage`, `WebPage` + `BreadcrumbList`, `CreativeWork` for projects, `BlogPosting` for articles). No reviews/ratings/awards markup. JSON-LD parsed for every crawled page (59 blocks, 0 errors).
**Not yet run:** Google Rich Results Test on the live URLs — do this after merging v2.

## 3. URLs to inspect in Search Console (URL Inspection → Test live → Request indexing)
1. `https://mohamednabilpro.deplois.net/`
2. `https://mohamednabilpro.deplois.net/?lang=ar`
3. `https://mohamednabilpro.deplois.net/about/mohamed-nabil/`
4. `https://mohamednabilpro.deplois.net/about/mohamed-nabil/?lang=ar`
5. `https://mohamednabilpro.deplois.net/cv/`
6. `https://mohamednabilpro.deplois.net/portfolio/`
7. `https://mohamednabilpro.deplois.net/portfolio/hr-payroll-system/`
8. `https://mohamednabilpro.deplois.net/portfolio/seshat-pos-business-management/`
9. `https://mohamednabilpro.deplois.net/portfolio/qtech-company-platform/`
10. `https://mohamednabilpro.deplois.net/blog/`
Then **Sitemaps → submit** `https://mohamednabilpro.deplois.net/sitemap.xml` (once). A successful live test or request does not guarantee indexing.

## 4. Search visibility (measured 2026-11-06)
Web searches for "Mohamed Nabil Pro", "Mohamed Nabil software engineer Django Egypt", the domain, and "محمد نبيل مطور برمجيات Django" did **not** return the site yet (not indexed at that time). The only owned result was the GitLab profile, which still links to the old `mohamednabilpro.netlify.app` — update it.

## 5. Recommendations
- Update the website field on GitLab, GitHub, LinkedIn, Stack Overflow, Behance, Facebook to this domain; use the same portrait.
- Add Bing Webmaster Tools (import from Search Console).
- Fix or remove the three CV links that return 404.
- Re-check Search Console → Pages / Performance after 2–4 weeks.
