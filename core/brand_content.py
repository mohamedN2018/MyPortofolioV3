"""
Site content derived from the owner's latest verified CV
("Mohammed_Nabil_Backend_Developer_CV_Gulf.pdf", provided 2026-11-06).

Used by:
  * migration 0005_cv_content (runs once on deploy), and
  * `manage.py sync_brand_identity` (manual re-sync, dry-run by default).

`apply_brand_content(get_model, ...)` only uses `get_model`, so it works with
historical models inside migrations. It never deletes rows: outdated rows are
deactivated (is_active=False) and can be re-enabled from the admin.
"""
import datetime
from pathlib import Path

from django.conf import settings
from django.core.files import File

NAME_EN, NAME_AR, BRAND = "Mohamed Nabil", "محمد نبيل", "Mohamed Nabil Pro"

PROFILES = {
    "linkedin_url": "https://www.linkedin.com/in/mohamed-nabil-1458872b2/",
    "github_url": "https://github.com/mohamedN2018",
    "gitlab_url": "https://gitlab.com/mohamedN2024",
    "stackoverflow_url": "https://stackoverflow.com/users/28639128/mohamed-nabil",
    "behance_url": "https://www.behance.net/moh24832c3ae",
    "facebook_url": "https://www.facebook.com/MohaMedNabiLPro",
}

TITLE_EN = "Software Engineer at Q-Tech Solutions · Backend Developer (Python / Django) · ERP, HR & E-Commerce Systems"
TITLE_AR = "مهندس برمجيات في Q-Tech Solutions · مطور Backend (Python / Django) · أنظمة ERP والموارد البشرية والتجارة الإلكترونية"

SHORT_EN = ("Backend developer (Python / Django / DRF) building business systems end-to-end — "
            "HR & payroll, multi-vendor e-commerce, offline-first POS — from requirements to production.")
SHORT_AR = ("مطور Backend (Python / Django / DRF) يبني أنظمة الأعمال من البداية للنهاية — الموارد البشرية "
            "والرواتب، المتاجر متعددة البائعين، ونقاط البيع التي تعمل دون إنترنت — من المتطلبات حتى الإنتاج.")

BIO_EN = (
    "Mohamed Nabil (Arabic: محمد نبيل), known online as Mohamed Nabil Pro, is a backend developer "
    "(Python / Django / Django REST Framework) from Egypt with 3+ years of experience. He is currently a "
    "Software Engineer at Q-Tech Solutions, where he was promoted within his first months.\n\n"
    "He builds business systems end-to-end — from requirements and feasibility study to architecture, APIs "
    "and production deployment on Linux VPS with Docker and Dokploy. His work includes an enterprise HR & "
    "payroll system with biometric attendance, a multi-vendor marketplace with multi-currency, tax zones and "
    "seller payouts, an offline-first POS & inventory system, a multi-store loyalty network and a company "
    "operations platform used by every department.\n\n"
    "He builds bilingual Arabic / English (RTL) products and works spec-first with AI coding agents: he writes "
    "the plan, architecture and data model, then reviews, tests and refines the generated code."
)
BIO_AR = (
    "محمد نبيل (Mohamed Nabil)، المعروف على الإنترنت باسم Mohamed Nabil Pro، مطور Backend "
    "(Python / Django / Django REST Framework) من مصر بخبرة تزيد عن 3 سنوات. يعمل حالياً مهندس برمجيات في "
    "Q-Tech Solutions، وحصل على ترقية خلال أشهره الأولى.\n\n"
    "يبني أنظمة الأعمال من البداية للنهاية — من جمع المتطلبات ودراسة الجدوى إلى المعمارية وواجهات API والنشر "
    "على خوادم Linux باستخدام Docker و Dokploy. من أعماله: نظام موارد بشرية ورواتب مع أجهزة البصمة، متجر "
    "متعدد البائعين بعملات متعددة ومناطق ضريبية ومستحقات البائعين، نظام نقاط بيع ومخزون يعمل دون إنترنت، شبكة "
    "ولاء مشتركة بين المتاجر، ومنصة تشغيل لشركة تخدم كل الأقسام.\n\n"
    "يبني منتجات ثنائية اللغة عربي / إنجليزي (RTL)، ويعمل بأسلوب «المواصفات أولاً» مع أدوات البرمجة بالذكاء "
    "الاصطناعي: يكتب الخطة والمعمارية ونموذج البيانات، ثم يراجع الكود المُنتَج ويختبره ويحسّنه."
)

EXPERIENCES = [
    {
        "start": datetime.date(2026, 5, 1), "current": True, "website": "https://q-tech-solutions.com/", "order": 1,
        "tech": "Python, Django, Django REST Framework, PostgreSQL, Vue.js, Docker, Dokploy",
        "en": {
            "title": "Software Engineer (Backend – Python / Django)", "company": "Q-Tech Solutions · Full-time",
            "description": "Software engineer building and running the company's business systems. Promoted within the first months of joining.",
            "achievements": [
                "Promoted within the first months of joining.",
                "Built the company operations platform used by management and all departments: employee hub with payslips, modular department dashboards, client portal (projects, invoices, support tickets) and the corporate website (q-tech-solutions.com).",
                "Built the enterprise HR & payroll system with 15+ modules: biometric attendance, leaves, overtime, bonuses, deductions, salary structures and automated monthly payroll (hrs.deplois.net).",
                "Built Q-Tech PharmaSyst, a pharmacy management system with medicine inventory, batch and expiry tracking, sales, purchasing and reporting.",
                "Deploy and maintain company systems in production on Hostinger VPS with Dokploy and Docker.",
            ],
        },
        "ar": {
            "title": "مهندس برمجيات (Backend – Python / Django)", "company": "Q-Tech Solutions · دوام كامل",
            "description": "مهندس برمجيات يبني ويشغّل أنظمة الشركة. حصل على ترقية خلال الأشهر الأولى.",
            "achievements": [
                "ترقية خلال الأشهر الأولى من الانضمام.",
                "بناء منصة تشغيل الشركة المستخدمة من الإدارة وكل الأقسام: بوابة الموظفين وكشوف الرواتب، لوحات أقسام معيارية، بوابة العملاء (المشاريع والفواتير وتذاكر الدعم) وموقع الشركة (q-tech-solutions.com).",
                "بناء نظام الموارد البشرية والرواتب بأكثر من 15 وحدة: الحضور بأجهزة البصمة، الإجازات، الإضافي، المكافآت، الخصومات، هياكل الرواتب ومسير الرواتب الشهري الآلي (hrs.deplois.net).",
                "بناء Q-Tech PharmaSyst لإدارة الصيدليات: مخزون الأدوية، تتبع التشغيلات والصلاحية، المبيعات، المشتريات والتقارير.",
                "نشر وصيانة أنظمة الشركة على بيئة الإنتاج (Hostinger VPS + Dokploy + Docker).",
            ],
        },
    },
    {
        "start": datetime.date(2022, 1, 1), "current": True, "website": "", "order": 2,
        "tech": "Python, Django, DRF, PostgreSQL, MySQL, Redis, Docker, Dokploy",
        "en": {
            "title": "Backend Developer (Python / Django)", "company": "Freelance (Self-Employed) · Remote",
            "description": "Builds complete systems for clients from zero to launch.",
            "achievements": [
                "Build complete systems from zero to launch: idea, planning, requirements, database design, backend, frontend, testing, deployment and post-launch support.",
                "Delivered 10+ client platforms including a multi-vendor marketplace, an offline-first POS & inventory system, a multi-store loyalty network and content platforms.",
                "Design REST APIs with Django REST Framework: JWT authentication, role-based permissions, versioning, filtering, pagination and audit logging.",
                "Model relational schemas in PostgreSQL and MySQL and optimise queries with indexing, select_related / prefetch_related and Redis caching.",
                "Deploy to production on Hostinger VPS with Dokploy: domains and DNS, SSL, environment variables, databases and scheduled backups.",
                "Work spec-first with AI coding agents: write the plan, architecture and data model, then review, test and refine the generated code.",
            ],
        },
        "ar": {
            "title": "مطور Backend (Python / Django)", "company": "عمل حر · عن بُعد",
            "description": "بناء أنظمة متكاملة للعملاء من الفكرة حتى الإطلاق.",
            "achievements": [
                "بناء أنظمة كاملة من الصفر حتى الإطلاق: الفكرة، التخطيط، المتطلبات، تصميم قاعدة البيانات، Backend و Frontend، الاختبار، النشر والدعم بعد الإطلاق.",
                "تسليم أكثر من 10 منصات لعملاء، منها متجر متعدد البائعين، نظام نقاط بيع ومخزون يعمل دون إنترنت، شبكة ولاء متعددة المتاجر ومنصات محتوى.",
                "تصميم REST APIs باستخدام Django REST Framework: مصادقة JWT، صلاحيات حسب الدور، الإصدارات، الفلترة، الترقيم وسجلات التدقيق.",
                "تصميم قواعد بيانات علائقية في PostgreSQL و MySQL وتحسين الاستعلامات بالفهارس و select_related / prefetch_related وتخزين Redis المؤقت.",
                "النشر على Hostinger VPS باستخدام Dokploy: النطاقات و DNS، شهادات SSL، متغيرات البيئة، قواعد البيانات والنسخ الاحتياطي المجدول.",
                "العمل بأسلوب «المواصفات أولاً» مع أدوات البرمجة بالذكاء الاصطناعي: كتابة الخطة والمعمارية ونموذج البيانات ثم مراجعة الكود واختباره.",
            ],
        },
    },
]

EDUCATION = {
    "start": 2019, "end": 2022,
    "en": {"degree": "Diploma of Industrial Secondary Education – Decoration & Design", "field": "Fine Arts & Graphic Design", "institution": "Industrial Secondary School, Egypt"},
    "ar": {"degree": "دبلوم الثانوية الصناعية – الديكور والتصميم", "field": "الفنون الجميلة والتصميم الجرافيكي", "institution": "المدرسة الثانوية الصناعية، مصر"},
}

TRAINING = {
    "en": "Full-Stack Web Development Diploma (100 hours) — HTML, CSS, JavaScript, Vue.js, PHP, MySQL, Laravel.",
    "ar": "دبلومة تطوير الويب Full-Stack (100 ساعة) — HTML و CSS و JavaScript و Vue.js و PHP و MySQL و Laravel.",
}
LANGUAGES = {"en": "Arabic (native) · English (intermediate — technical reading and documentation)",
             "ar": "العربية (اللغة الأم) · الإنجليزية (متوسط — قراءة تقنية وتوثيق)"}

SKILL_GROUPS = [
    ("bi-server", "Backend", "الـ Backend", ["Python", "Django", "Django REST Framework", "RESTful API design", "JWT authentication", "Django Channels (WebSockets)", "Django ORM", "Query optimization"]),
    ("bi-database", "Databases", "قواعد البيانات", ["PostgreSQL", "MySQL", "Redis", "SQLite", "Database design & normalization"]),
    ("bi-cloud-arrow-up", "Deployment & DevOps", "النشر و DevOps", ["Docker", "Docker Compose", "Linux VPS", "Hostinger", "Dokploy", "Domains / DNS", "SSL", "Git", "GitHub"]),
    ("bi-window", "Frontend", "الواجهات", ["HTML5", "CSS3", "JavaScript", "Bootstrap", "Tailwind CSS"]),
    ("bi-plug", "Integrations", "التكاملات", ["Payment gateways", "WhatsApp", "Third-party REST APIs"]),
    ("bi-diagram-3", "Product & Analysis", "المنتج والتحليل", ["Requirements gathering", "Feasibility studies", "System architecture", "Technical documentation"]),
    ("bi-robot", "AI-assisted delivery", "التطوير بمساعدة الذكاء الاصطناعي", ["Vue.js SPAs", "PWA", "Arabic RTL dashboards", "Claude Code & AI coding agents", "Spec-driven development"]),
]

STATIC_PROJECTS = "brand/projects/"

# Projects exactly as listed in the CV. `url` is set only for sites that answered
# HTTP 200 on 2026-11-06 (qshop / walaee / qtechpharmasyst returned 404 that day).
PROJECTS = [
    {"slug": "hr-payroll-system", "order": 1, "cover": "hr-payroll-system.webp", "gallery": [], "url": "https://hrs.deplois.net/",
     "tech": ["Django", "Django REST Framework", "PostgreSQL", "JWT", "Vue.js", "Docker"], "cat": "business-systems",
     "en": {"title": "Enterprise HR & Payroll Management System", "client": "Q-Tech Solutions",
            "short": "HR platform with 15+ modules: biometric attendance, leaves, overtime, salary structures and automated monthly payroll.",
            "overview": "A complete HR platform covering employee records, departments, positions, work schedules, attendance, leave types and requests, overtime, bonuses and deductions.",
            "challenge": "Companies need attendance, leave and payroll in one place, with accurate data from biometric devices and a self-service portal for employees.",
            "solution": "Configurable salary structures feed an automated monthly payroll run; an employee self-service portal covers attendance, leaves, overtime and salary slips. Biometric attendance devices are integrated, and the API is secured with JWT (access/refresh tokens), role-based permissions and full activity logs.",
            "result": "Live at hrs.deplois.net, with a CMS-managed public website (features, pricing, FAQs, testimonials, theme settings) and API reference documentation."},
     "ar": {"title": "نظام الموارد البشرية والرواتب للمؤسسات", "client": "Q-Tech Solutions",
            "short": "منصة موارد بشرية بأكثر من 15 وحدة: حضور بالبصمة، إجازات، إضافي، هياكل رواتب ومسير رواتب شهري آلي.",
            "overview": "منصة متكاملة تغطي ملفات الموظفين والأقسام والوظائف وجداول العمل والحضور وأنواع الإجازات وطلباتها والإضافي والمكافآت والخصومات.",
            "challenge": "الشركات تحتاج الحضور والإجازات والرواتب في مكان واحد ببيانات دقيقة من أجهزة البصمة مع بوابة خدمة ذاتية للموظفين.",
            "solution": "هياكل رواتب قابلة للتهيئة تغذي مسير الرواتب الشهري الآلي، وبوابة خدمة ذاتية للحضور والإجازات والإضافي وكشوف الرواتب، مع ربط أجهزة البصمة وتأمين الـ API بـ JWT وصلاحيات حسب الدور وسجلات نشاط كاملة.",
            "result": "يعمل على hrs.deplois.net مع موقع عام يُدار من CMS (المميزات، الأسعار، الأسئلة الشائعة، الآراء، إعدادات الثيم) وتوثيق للـ API."}},
    {"slug": "qtech-company-platform", "order": 2, "cover": "qtech-solutions-website.webp",
     "gallery": ["qtech-platform-home.webp", "qtech-platform-store.webp", "qtech-platform-work.webp"], "url": "https://q-tech-solutions.com/",
     "tech": ["Django", "Django REST Framework", "PostgreSQL", "Vue.js", "Docker"], "cat": "business-systems",
     "en": {"title": "Q-Tech Solutions — Company Operations Platform", "client": "Q-Tech Solutions",
            "short": "Corporate website and internal platform with 30+ screens across 3 portals, used by management and all departments.",
            "overview": "The corporate website plus an internal platform with three portals: public site, employee hub and client portal.",
            "challenge": "One platform had to serve the public website, the employees and the clients of the company.",
            "solution": "Employee hub with profiles, payslips and a modular dashboard where each department's tools load as separate modules; client portal for project tracking, invoices and support tickets; public site with team, careers, blog, products store and portfolio; live chat, email verification, password recovery and a visitor analytics API.",
            "result": "Live at q-tech-solutions.com and used by management and all departments."},
     "ar": {"title": "Q-Tech Solutions — منصة تشغيل الشركة", "client": "Q-Tech Solutions",
            "short": "موقع الشركة ومنصة داخلية بأكثر من 30 شاشة عبر 3 بوابات، تستخدمها الإدارة وكل الأقسام.",
            "overview": "موقع الشركة الرسمي مع منصة داخلية من ثلاث بوابات: الموقع العام، بوابة الموظفين، وبوابة العملاء.",
            "challenge": "منصة واحدة تخدم الموقع العام والموظفين والعملاء.",
            "solution": "بوابة موظفين بالملفات وكشوف الرواتب ولوحة معيارية تُحمَّل فيها أدوات كل قسم كوحدة مستقلة؛ بوابة عملاء لمتابعة المشاريع والفواتير وتذاكر الدعم؛ موقع عام بالفريق والوظائف والمدونة ومتجر المنتجات والأعمال؛ شات مباشر وتأكيد البريد واستعادة كلمة المرور و API لتحليلات الزوار.",
            "result": "يعمل على q-tech-solutions.com وتستخدمه الإدارة وكل الأقسام."}},
    {"slug": "qshop-multi-vendor-marketplace", "order": 3, "cover": "qshop-marketplace-cover.webp", "gallery": [], "url": "",
     "tech": ["Django", "Django REST Framework", "PostgreSQL", "Redis", "Vue.js", "Docker"], "cat": "e-commerce",
     "en": {"title": "q-shop — Multi-Vendor Marketplace", "client": "Own product (concept & delivery)",
            "short": "80+ REST endpoints across 20+ modules serving a customer storefront, a seller console and a platform admin.",
            "overview": "Designed the product concept and full scope, delivered with an AI-assisted workflow.",
            "challenge": "A marketplace needs catalogue, inventory, procurement and a finance layer that handles many sellers, currencies and tax rules.",
            "solution": "Catalogue with variants, attributes, brands, bundles and digital products (license keys); cart, coupons and checkout; multi-warehouse inventory and procurement (suppliers, purchase orders, BOMs, work orders, batches, serial numbers); multi-currency with exchange rates, tax zones, multiple payment gateways, seller payouts with a commission ledger, fraud checks, returns, promotions, gift cards and analytics.",
            "result": ""},
     "ar": {"title": "q-shop — متجر متعدد البائعين", "client": "منتج خاص (الفكرة والتنفيذ)",
            "short": "أكثر من 80 REST endpoint عبر أكثر من 20 وحدة تخدم واجهة العملاء ولوحة البائعين وإدارة المنصة.",
            "overview": "تصميم فكرة المنتج ونطاقه بالكامل وتنفيذه بأسلوب عمل مدعوم بالذكاء الاصطناعي.",
            "challenge": "المتجر متعدد البائعين يحتاج كتالوجاً ومخزوناً ومشتريات وطبقة مالية تتعامل مع بائعين وعملات وقواعد ضريبية متعددة.",
            "solution": "كتالوج بالمتغيرات والخصائص والعلامات والحزم والمنتجات الرقمية؛ سلة وكوبونات ودفع؛ مخزون متعدد المستودعات ومشتريات (موردون، أوامر شراء، BOM، أوامر تشغيل، تشغيلات وأرقام تسلسلية)؛ عملات متعددة بأسعار صرف، مناطق ضريبية، بوابات دفع متعددة، مستحقات البائعين بدفتر عمولات، فحص الاحتيال، المرتجعات، العروض، بطاقات الهدايا والتحليلات.",
            "result": ""}},
    {"slug": "seshat-pos-business-management", "order": 4, "cover": "seshat-pos-dashboard.webp",
     "gallery": ["seshat-pos-register.webp", "seshat-pos-catalogue.webp", "seshat-pos-inventory.webp", "seshat-pos-licence.webp"],
     "url": "https://seshat.deplois.net/",
     "tech": ["Windows desktop app", "Encrypted local database", "Django REST Framework", "PostgreSQL", "Docker"], "cat": "business-systems",
     "en": {"title": "Seshat — Offline-First POS & Inventory System", "client": "Q-Tech Solutions (product)",
            "short": "Arabic-native cashier and inventory for retail stores that keeps working without internet, with cloud licensing and encrypted backups.",
            "overview": "Planned the full product and technical design; built for retail stores (supermarkets, pharmacies, clothing and spare-parts shops) with an Arabic-native RTL interface.",
            "challenge": "Retail stores need a cashier that never stops when the connection drops, while still being licensed and backed up remotely.",
            "solution": "Offline-first architecture: sales, inventory and reports run on a local encrypted database; the cloud handles licensing and encrypted backups with automatic sync on reconnect. Cashier (barcode, split payments, suspended invoices, returns, thermal receipts), inventory (variants, unit conversion, POs, warehouse transfers, stock counts, FEFO expiry tracking), shift management with cash-drawer reconciliation, permissions, audit logs and 12 report types exported to CSV, Excel and PDF.",
            "result": "Per-device trial, annual and lifetime licensing; product site at seshat.deplois.net."},
     "ar": {"title": "Seshat — نظام نقاط بيع ومخزون يعمل دون إنترنت", "client": "Q-Tech Solutions (منتج)",
            "short": "كاشير ومخزون بواجهة عربية لمتاجر التجزئة يعمل بدون إنترنت، مع ترخيص سحابي ونسخ احتياطي مشفّر.",
            "overview": "تخطيط المنتج والتصميم التقني بالكامل لمتاجر التجزئة (سوبر ماركت، صيدليات، ملابس، قطع غيار) بواجهة عربية RTL.",
            "challenge": "المتاجر تحتاج كاشير لا يتوقف عند انقطاع الاتصال، مع إمكانية الترخيص والنسخ الاحتياطي عن بُعد.",
            "solution": "معمارية تعمل أولاً دون اتصال: المبيعات والمخزون والتقارير على قاعدة بيانات محلية مشفّرة، والسحابة للترخيص والنسخ الاحتياطي المشفّر مع مزامنة تلقائية عند عودة الاتصال. كاشير (باركود، دفع مقسّم، فواتير معلّقة، مرتجعات، إيصالات حرارية)، مخزون (متغيرات، تحويل وحدات، أوامر شراء، تحويلات بين المخازن، جرد، تتبع الصلاحية FEFO)، إدارة الورديات ومطابقة الدرج، صلاحيات، سجلات تدقيق و12 نوع تقرير بصيغ CSV و Excel و PDF.",
            "result": "ترخيص لكل جهاز (تجريبي، سنوي، مدى الحياة)؛ موقع المنتج seshat.deplois.net."}},
    {"slug": "walaee-loyalty-network", "order": 5, "cover": "walaee-loyalty-cover.webp", "gallery": [], "url": "",
     "tech": ["Django REST Framework", "PostgreSQL", "JWT", "Vue.js"], "cat": "platforms",
     "en": {"title": "Walaee — Multi-Store Loyalty Network", "client": "Client project (freelance)",
            "short": "One shared loyalty program across a network of partner stores, with merchant dashboards and customer accounts.",
            "overview": "Turned a client idea into a product: led planning, market research and the feasibility study, defined the business model and technical architecture, then delivered the product.",
            "challenge": "Independent stores want a loyalty program their customers can use across the whole network.",
            "solution": "A shared loyalty program with merchant dashboards, customer accounts and a versioned REST API (v1) secured with JWT.",
            "result": ""},
     "ar": {"title": "Walaee — شبكة ولاء متعددة المتاجر", "client": "مشروع لعميل (عمل حر)",
            "short": "برنامج ولاء واحد مشترك بين شبكة من المتاجر الشريكة، بلوحات للتجار وحسابات للعملاء.",
            "overview": "تحويل فكرة عميل إلى منتج: قيادة التخطيط وبحث السوق ودراسة الجدوى وتحديد نموذج العمل والمعمارية التقنية ثم تنفيذ المنتج.",
            "challenge": "المتاجر المستقلة تريد برنامج ولاء يستخدمه عملاؤها عبر الشبكة كلها.",
            "solution": "برنامج ولاء مشترك بلوحات للتجار وحسابات للعملاء و REST API بإصدارات (v1) مؤمّن بـ JWT.",
            "result": ""}},
    {"slug": "qtech-pharmasyst", "order": 6, "cover": "qtech-pharmasyst-cover.webp", "gallery": [], "url": "",
     "tech": ["Django", "Django REST Framework", "PostgreSQL"], "cat": "business-systems",
     "en": {"title": "Q-Tech PharmaSyst — Pharmacy Management System", "client": "Q-Tech Solutions",
            "short": "Medicine inventory with batch and expiry tracking, sales, purchasing, suppliers and reporting.",
            "overview": "Planned and delivered a pharmacy management system for Q-Tech Solutions.",
            "challenge": "Pharmacies must track every batch and expiry date while selling and purchasing daily.",
            "solution": "Medicine inventory with batch and expiry tracking, sales, purchasing and suppliers, and reporting.",
            "result": ""},
     "ar": {"title": "Q-Tech PharmaSyst — نظام إدارة الصيدليات", "client": "Q-Tech Solutions",
            "short": "مخزون أدوية بتتبع التشغيلات والصلاحية، مبيعات، مشتريات، موردون وتقارير.",
            "overview": "تخطيط وتسليم نظام لإدارة الصيدليات لصالح Q-Tech Solutions.",
            "challenge": "الصيدليات لازم تتابع كل تشغيلة وتاريخ صلاحية مع البيع والشراء اليومي.",
            "solution": "مخزون أدوية بتتبع التشغيلات والصلاحية، المبيعات، المشتريات والموردين، والتقارير.",
            "result": ""}},
    {"slug": "nesma-cakes-bakery-pwa", "order": 7, "cover": "nesma-cakes-bakery.webp", "gallery": [], "url": "https://nesmacakes.deplois.net/",
     "tech": ["Django", "PWA", "WhatsApp integration"], "cat": "platforms",
     "en": {"title": "Nesma Cakes — Bakery Ordering Web App (PWA)", "client": "Nesma Cakes (local bakery)",
            "short": "Bilingual ordering site for a local bakery with WhatsApp ordering, installable as a mobile app.",
            "overview": "Designed and built a focused ordering site for a local bakery.",
            "challenge": "A small bakery needed online ordering that fits how its customers already order: WhatsApp, on mobile.",
            "solution": "Categorized catalogue, custom cake requests, gallery and reviews, WhatsApp ordering, Arabic / English, installable as a PWA.",
            "result": "Live at nesmacakes.deplois.net."},
     "ar": {"title": "نسمة كيك — تطبيق طلبات لمخبز (PWA)", "client": "نسمة كيك (مخبز محلي)",
            "short": "موقع طلبات ثنائي اللغة لمخبز محلي مع الطلب عبر واتساب، قابل للتثبيت كتطبيق على الموبايل.",
            "overview": "تصميم وبناء موقع طلبات مركّز لمخبز محلي.",
            "challenge": "مخبز صغير يحتاج طلبات أونلاين تناسب طريقة عملائه: واتساب ومن الموبايل.",
            "solution": "كتالوج مصنّف، طلبات كيك مخصصة، معرض وتقييمات، الطلب عبر واتساب، عربي / إنجليزي، وقابل للتثبيت كـ PWA.",
            "result": "يعمل على nesmacakes.deplois.net."}},
]

CATEGORY_NAMES = {
    "business-systems": ("Business Systems", "أنظمة الأعمال"),
    "e-commerce": ("E-Commerce", "التجارة الإلكترونية"),
    "platforms": ("Platforms", "منصات"),
}

PORTRAIT = "brand/mohamed-nabil-software-engineer.jpg"


def _static_path(rel):
    return Path(settings.BASE_DIR) / "static" / rel


def apply_brand_content(get_model, log=print, dry_run=False):
    """Idempotent content alignment with the CV. Never deletes rows."""
    Language = get_model("core", "Language")
    SiteSetting = get_model("core", "SiteSetting")
    PersonalInfo = get_model("core", "PersonalInfo")
    WorkExperience = get_model("core", "WorkExperience")
    Education = get_model("core", "Education")
    SkillCategory = get_model("core", "SkillCategory")
    Skill = get_model("core", "Skill")
    Portfolio = get_model("core", "Portfolio")
    PortfolioCategory = get_model("core", "PortfolioCategory")

    langs = {l.code: l for l in Language.objects.filter(code__in=["en", "ar"])}
    if "en" not in langs:
        log("No 'en' Language row — content sync skipped.")
        return

    def save(obj, fields=None):
        if not dry_run:
            obj.save(update_fields=fields) if fields else obj.save()

    # --- Site settings ------------------------------------------------------
    ss = SiteSetting.objects.first()
    if ss:
        ss.site_name_en, ss.site_name_ar = BRAND, f"{NAME_AR} | {BRAND}"
        ss.footer_text_en, ss.footer_text_ar = f"© {NAME_EN} — {BRAND}", f"© {NAME_AR} — {BRAND}"
        for f, v in PROFILES.items():
            setattr(ss, f, v)
        ss.twitter_url = ss.instagram_url = ""
        save(ss)
        log("SiteSetting: names, footer and official profiles updated.")

    # --- Personal info --------------------------------------------------------
    portrait = _static_path(PORTRAIT)
    for code, name, title, short, bio in (("en", NAME_EN, TITLE_EN, SHORT_EN, BIO_EN), ("ar", NAME_AR, TITLE_AR, SHORT_AR, BIO_AR)):
        lang = langs.get(code)
        if not lang:
            continue
        pi = PersonalInfo.objects.filter(language=lang).first()
        if not pi:
            log(f"PersonalInfo[{code}] missing — skipped.")
            continue
        pi.name, pi.title, pi.short_bio, pi.bio = name, title, short, bio
        pi.years_experience, pi.projects_completed = 3, 13
        # old CV versions are no longer linked: the site serves static/brand/cv/Mohamed-Nabil-CV.pdf
        pi.resume_file = ""
        if portrait.exists() and "mohamed-nabil-software-engineer" not in (pi.profile_image.name or ""):
            if not dry_run:
                with portrait.open("rb") as fh:
                    pi.profile_image.save(portrait.name, File(fh), save=False)
        save(pi)
        log(f"PersonalInfo[{code}]: name/title/bio/portrait updated, old CV link cleared.")

    # --- Experience (deactivate old, create CV entries) ------------------------
    for code, lang in langs.items():
        cv_titles = {e[code]["title"] for e in EXPERIENCES}
        n = WorkExperience.objects.filter(language=lang).exclude(job_title__in=cv_titles).update(is_active=False) if not dry_run else 0
        log(f"WorkExperience[{code}]: {n} old entries deactivated.")
        for e in EXPERIENCES:
            d = e[code]
            if WorkExperience.objects.filter(language=lang, job_title=d["title"]).exists():
                continue
            log(f"WorkExperience[{code}] + {d['title']}")
            if not dry_run:
                WorkExperience.objects.create(
                    language=lang, job_title=d["title"], company_name=d["company"], company_website=e["website"],
                    start_date=e["start"], is_current=e["current"], description=d["description"],
                    achievements=d["achievements"], technologies=e["tech"], order=e["order"], is_active=True)

    # --- Education --------------------------------------------------------------
    for code, lang in langs.items():
        d = EDUCATION[code]
        if not dry_run:
            Education.objects.filter(language=lang).exclude(degree=d["degree"]).update(is_active=False)
            if not Education.objects.filter(language=lang, degree=d["degree"]).exists():
                Education.objects.create(language=lang, degree=d["degree"], field_of_study=d["field"],
                                         institution=d["institution"], start_year=EDUCATION["start"],
                                         end_year=EDUCATION["end"], is_active=True)
        log(f"Education[{code}]: aligned with CV.")

    # --- Skills (deactivate old, create CV groups) -------------------------------
    for code, lang in langs.items():
        cv_cat_names = {(g[1] if code == "en" else g[2]) for g in SKILL_GROUPS}
        if not dry_run:
            SkillCategory.objects.filter(language=lang).exclude(name__in=cv_cat_names).update(is_active=False)
            Skill.objects.filter(language=lang).exclude(category__name__in=cv_cat_names).update(is_active=False)
            for i, (icon, en_name, ar_name, skills) in enumerate(SKILL_GROUPS):
                cat, _ = SkillCategory.objects.get_or_create(
                    language=lang, name=en_name if code == "en" else ar_name,
                    defaults={"icon": icon, "order": i, "is_active": True})
                for j, s in enumerate(skills):
                    Skill.objects.get_or_create(language=lang, category=cat, name=s,
                                                defaults={"order": j, "is_active": True, "proficiency": 0})
        log(f"Skills[{code}]: {len(SKILL_GROUPS)} CV groups.")

    # --- Projects ------------------------------------------------------------------
    new_slugs = {p["slug"] for p in PROJECTS} | {p["slug"] + "-ar" for p in PROJECTS}
    if not dry_run:
        Portfolio.objects.exclude(slug__in=new_slugs).update(is_featured=False)
        # the old "HR System Project" entry is replaced by the detailed case study
        Portfolio.objects.filter(title__icontains="HR System").exclude(slug__in=new_slugs).update(is_active=False)
    today = datetime.date(2026, 11, 6)
    for code, lang in langs.items():
        suffix = "" if code == "en" else "-ar"
        for p in PROJECTS:
            d, slug = p[code], p["slug"] + suffix
            cat_en, cat_ar = CATEGORY_NAMES[p["cat"]]
            obj = Portfolio.objects.filter(slug=slug, language=lang).first()
            log(f"Portfolio[{code}] {'update' if obj else 'create'} {slug}")
            if dry_run:
                continue
            cat, _ = PortfolioCategory.objects.get_or_create(
                language=lang, slug=p["cat"] + suffix, defaults={"name": cat_en if code == "en" else cat_ar})
            obj = obj or Portfolio(language=lang, slug=slug)
            obj.project_date = today
            obj.category, obj.title, obj.client_name = cat, d["title"], d["client"]
            obj.project_url, obj.short_description, obj.overview = p["url"], d["short"], d["overview"]
            obj.challenge, obj.solution, obj.result = d["challenge"], d["solution"], d["result"]
            obj.technologies, obj.order, obj.is_featured, obj.is_active = p["tech"], p["order"], True, True
            obj.gallery_images = [f"{settings.STATIC_URL}{STATIC_PROJECTS}{g}" for g in p["gallery"]]
            obj.meta_title = f"{d['title']} — {NAME_EN if code == 'en' else NAME_AR}"
            obj.meta_description = d["short"]
            cover = _static_path(STATIC_PROJECTS + p["cover"])
            if cover.exists() and Path(obj.cover_image.name or "").stem.split("_")[0] != Path(p["cover"]).stem:
                with cover.open("rb") as fh:
                    obj.cover_image.save(p["cover"], File(fh), save=False)
            obj.save()
