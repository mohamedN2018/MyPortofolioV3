# Design System — Mohamed Nabil Pro (v2)

Source of truth: `static/assets/css/brand.css` (tokens + components) and `static/assets/js/brand.js` (interactions).

## 1. Principles
- **Credible, not flashy.** One accent colour, restrained gradients (hero title only), no glassmorphism except the sticky nav.
- **Content first.** Everything important is server-rendered HTML; JS only adds motion.
- **Bilingual by design.** Logical properties (`inset-inline-*`, `padding-inline-*`) so LTR/RTL share one stylesheet; RTL Bootstrap builds for Arabic.

## 2. Colour tokens
| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#f6f7fb` | `#0a0b10` | page |
| `--bg-elev` | `#ffffff` | `#12141c` | cards, inputs |
| `--bg-sunken` | `#eef0f6` | `#0e1017` | alternate sections, footer |
| `--ink` | `#0b0d14` | `#f5f6fa` | headings |
| `--text` | `#2a2f3d` | `#c9cdd8` | body |
| `--muted` | `#5d6474` | `#8f96a8` | secondary text |
| `--accent` | `#4f46e5` | `#8b8dff` | the single brand accent (indigo, matches the portrait halo) |
| `--line` / `--line-strong` | 9% / 16% ink | 8% / 16% white | borders |
Contrast: body text ≥ 7:1, muted ≥ 4.6:1, accent on surfaces ≥ 4.5:1 (Lighthouse a11y 96, contrast audit passed).

## 3. Typography
- Latin body: **Inter** 400/500/600/700; Latin display: **Plus Jakarta Sans** 700/800.
- Arabic: **Cairo** 400/600/700/800 for body and display; no letter-spacing, line-height 1.85.
- Scale: hero `clamp(2.6rem, 6.6vw, 5rem)`, page title `clamp(2rem, 4.6vw, 3.2rem)`, section title `clamp(1.75rem, 3.4vw, 2.6rem)`, body 16px, prose 17px/1.8.
- Fonts load non-blocking (`rel=preload` + `onload`), `display=swap`; only the families needed for the current language are requested.

## 4. Spacing, radius, containers
- Section rhythm `--space-section: clamp(56px, 8vw, 112px)`.
- Radius: 10 / 14 / 20 / 28 px (`--r-sm…--r-xl`).
- Container 1200px; padding 20px (24px ≥ 992px to absorb `g-lg-5` gutters).
- Breakpoints (Bootstrap): 576 / 768 / 992 / 1200; nav collapses at **1100px**.

## 5. Components
| Component | Class | Notes |
|---|---|---|
| Buttons | `.mnp-btn` + `-primary` / `-outline` / `-ghost` / `-sm` | min-height 46px (touch ≥ 44px) |
| Icon button | `.mnp-icon-btn` | 42×42 (40×40 on phones) |
| Nav | `.mnp-nav`, `.mnp-menu`, `.mnp-burger` | sticky, blur, `aria-expanded`, Esc closes, link click closes |
| Card | `.mnp-card` | surface + 1px line + shadow-1 |
| Project card | `.mnp-project` (`.shot`, `.body`, `.meta`, `.go`) | whole card clickable via stretched link; 3D tilt `data-tilt` |
| Chip | `.mnp-chip` | technologies/skills — no percentages |
| Section head | `.mnp-section-head` + `.kicker` | |
| Page head | `.mnp-page-head` + `.mnp-breadcrumbs` | every inner page |
| Timeline | `.mnp-timeline` | experience / education |
| Facts list | `.mnp-facts` | collapses to 1 column on phones |
| CV band | `.mnp-cv-band` | dark band, recruiter CTA |
| Filters / search / pagination | `.mnp-filters`, `.mnp-filter`, `.mnp-search`, `.mnp-pagination` | 40–44px targets |
| Prose | `.mnp-prose` | articles, case studies |
| Gallery | `.mnp-gallery`, `.mnp-shots` | masonry columns / horizontal snap strip |

## 6. Motion rules
- Reveal on scroll: `[data-reveal]` (opacity + 18px rise, 700ms, once). Hidden state only when JS runs (`html.js`).
- 3D: hero canvas point-sphere (520 points desktop, paused off-screen, **hidden < 992px**), portrait stage with `preserve-3d` depth layers, tilt on cards (`pointer: fine` only).
- Floating tech labels: gentle 6s bob; disabled on phones.
- `prefers-reduced-motion: reduce` → no animation, sphere drawn once, reveals shown immediately.

## 7. Conventions
- Never hard-code colours in templates; use tokens.
- Every page: `mnp-page-head` (breadcrumb + kicker + h1 + intro) → `mnp-section` blocks.
- Images: explicit `width`/`height`, `loading="lazy"` except the LCP image (`fetchpriority="high"`).
- Portrait comes from `brand.portrait_*` (switch set with `BRAND_PORTRAIT=studio|camera`).
