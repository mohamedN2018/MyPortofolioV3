# Website Rebuild Report — Mohamed Nabil Pro (v2)

**Branch:** `redesign/premium-v2` (not merged, not deployed) · **Date:** 2026-11-07

> ملخص: إعادة بناء كاملة للواجهة على فرع منفصل — قائمة علوية حديثة بدل الشريط الجانبي، واجهة رئيسية بتأثير ثلاثي الأبعاد، نظام تصميم واحد لكل الصفحات، تخفيف الملفات، والصورة القديمة رجعت كما طلبت (مع إمكانية التبديل للصورة الحقيقية). لم يتم النشر — بانتظار موافقتك.

## 1. What changed

| Area | Before | After |
|---|---|---|
| Navigation | Fixed left sidebar; toggle overlapped titles on tablet/mobile | Sticky top bar, CV button always visible, accessible mobile panel |
| Home | Mixed sections, old SnapFolio styles, fabricated review fallback | Hero (3D scene) → Projects → About → CV → Skills → Experience → Services → real Reviews (only if any) → Contact |
| Inner pages | Portfolio / Project / Services / Blog / Errors in legacy styles | All rewritten on one design system |
| Portrait | Unedited camera photo (first rebuild) | Owner-preferred studio portrait restored; camera photo kept in gallery; switchable by env |
| CSS/JS | Bootstrap full + main.css + 7 vendor libs | Bootstrap reboot/grid/utilities (RTL for Arabic) + brand.css; brand.js (~4 KB); lightbox only on project pages |
| Skills | % bars | Chips grouped by CV categories |
| Mobile | Filters before projects; floating theme button | Projects first; theme toggle in nav |

## 2. Files
**New:** `static/assets/js/brand.js`, `templates/includes/post_card.html`, `static/brand/mohamed-nabil-photo{,-400,-800}.{jpg,webp}`, `static/brand/mohamed-nabil-pro-og-photo.jpg`, `docs/screenshots/*.jpg`, the six docs.
**Rewritten:** `templates/includes/header.html`, `templates/index.html`, `portfolio.html`, `portfolio-detail.html`, `services.html`, `service-detail.html`, `blog.html`, `blog-detail.html`, `blog-category.html`, `static-page.html`, `search-results.html`, `error/{400,403,404,500}.html`, `static/assets/css/brand.css`.
**Modified:** `templates/base.html` (CSS stack, fonts, no-flash theme, scripts), `templates/identity.html`, `templates/gallery.html`, `core/seo.py` (portrait sets), `config/settings.py` (`BRAND_PORTRAIT`), `core/templatetags/blog_extras.py` (`split_tags`), `core/tests.py`.
**Not touched:** models, migrations, views' logic, URLs, admin, dashboard, data.

## 3. Decisions
1. **Portrait.** The owner asked (2026-11-07) to bring back the previous photo. It is AI-enhanced (Gemini). The master prompt forbids presenting AI-generated photos as the owner. Resolution: default `studio` per the owner's explicit request; the unedited photo is one setting away (`BRAND_PORTRAIT=camera`) and is shown in the gallery. **Owner confirmation requested.**
2. **No new migrations / no content invention.** Project role text on case studies is generic ("Planning, development & deployment") pending owner wording.
3. **Desktop-only 3D.** Sphere hidden < 992px; tilt only on precise pointers.

## 4. Deployment (owner-controlled)
1. Review the branch: `git checkout redesign/premium-v2 && python manage.py runserver`.
2. Merge: `git checkout main && git merge --no-ff redesign/premium-v2 && git push origin main` → Dokploy auto-deploys (≈3 min).
3. Optional env: `BRAND_PORTRAIT=camera` in Dokploy to use the unedited photo.
4. Verify: `/`, `/?lang=ar`, `/cv/`, `/portfolio/hr-payroll-system/`, `/google6dc94822b91e8a80.html`, `/sitemap.xml`.

## 5. Rollback
- Code: `git revert -m 1 <merge-commit> && git push origin main` (or redeploy the previous deployment from Dokploy → Deployments).
- No database changes in this phase, so no data rollback is needed.
