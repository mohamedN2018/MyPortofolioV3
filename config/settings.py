import os
from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# BASE & SECURITY
# =========================

SECRET_KEY = config('MY_SECRET_KEY')

DEBUG = config('MY_DEBUG', default=False, cast=bool)


if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True



USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = not DEBUG


MAIN_DOMAIN = config('MAIN_DOMAIN', default='mohamednabilpro.deplois.net').replace('https://', '').replace('http://', '')


ALLOWED_HOSTS = [MAIN_DOMAIN, f'www.{MAIN_DOMAIN}', '127.0.0.1', 'localhost', 'testserver']

# Absolute public base URL used for canonical URLs, sitemap, robots.txt,
# Open Graph and JSON-LD. Never hardcode a development URL here.
SITE_URL = config('SITE_URL', default=f'https://{MAIN_DOMAIN}').rstrip('/')

if DEBUG:
    ALLOWED_HOSTS += ['127.0.0.1', 'localhost', 'https://mohamednabilpro.deplois.net/', 'http://mohamednabilpro.deplois.net/']


# CSRF_TRUSTED_ORIGINS = [
#     f'{MAIN_DOMAIN}',
# ]

CSRF_TRUSTED_ORIGINS = [
    f'https://{MAIN_DOMAIN}',
    f'https://www.{MAIN_DOMAIN}',
    f'http://{MAIN_DOMAIN}',
    f'http://www.{MAIN_DOMAIN}',

]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security headers (safe defaults; HSTS only when explicitly enabled)
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # allows the same-origin CV PDF preview iframe
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
# Health checks / internal probes hit plain HTTP; keep the public redirect
# to HTTPS but never redirect the Google verification file or robots.
SECURE_REDIRECT_EXEMPT = [r'^google[0-9a-f]+\.html$', r'^robots\.txt$']


if DEBUG:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
else:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = [
    # 'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'rangefilter',
    # 'import_export',

    'core',
]

# Debug Toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

SITE_ID = 1



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middleware.RequestLanguageIsolationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # Important for translation
                'core.context_processors.site_settings',
                'core.context_processors.site_languages',
                'core.context_processors.site_menus',
                'core.context_processors.global_settings',
                'core.context_processors.dashboard_stats',
                'core.seo.seo_context',

            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

if LOCAL := config('LOCAL', default=True, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': config('DB_ENGINE'),
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT', cast=int),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =========================
# INTERNATIONALIZATION
# =========================

LANGUAGE_CODE = 'en-us'
# Language served to visitors without an explicit choice (no ?lang=, no session).
SITE_DEFAULT_LANGUAGE = config('SITE_DEFAULT_LANGUAGE', default='en')
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
]

# إعدادات الترجمة
USE_I18N = True     
USE_L10N = True
    
# تنسيق التاريخ والوقت بالعربية
DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y',
    '%d %B %Y', '%d %b %Y',
]

TIME_INPUT_FORMATS = [
    '%H:%M:%S', '%H:%M',
]

# إعدادات إضافية للعربية
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
DECIMAL_SEPARATOR = '.'
NUMBER_GROUPING = 3


LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# =========================
# STATIC & MEDIA
# =========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise serves /static/ in production (DEBUG=False) without nginx.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Serve straight from STATICFILES_DIRS as well, so new assets work even if the
# Docker build's `collectstatic || true` step fails (no env vars at build time).
WHITENOISE_USE_FINDERS = True

# Public root files (e.g. Google Search Console verification) served at "/<name>".
PUBLIC_ROOT = BASE_DIR / "public"

# Serve user-uploaded /media/ through Django when there is no separate web
# server for it (Dokploy/Traefik setup). Set SERVE_MEDIA=False if nginx serves it.
SERVE_MEDIA = config('SERVE_MEDIA', default=True, cast=bool)

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =========================
# EMAIL
# =========================
# الافتراضي console (يطبع الإيميل في اللوج) حتى لا يتعطّل التطوير.
# للإرسال الفعلي: اضبط EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# مع بيانات SMTP في ملف .env
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=(EMAIL_HOST_USER or 'no-reply@localhost'))
# البريد الذي تصل إليه إشعارات نموذج الاتصال (افتراضياً نفس بريد المُرسِل)
CONTACT_NOTIFY_EMAIL = config('CONTACT_NOTIFY_EMAIL', default=EMAIL_HOST_USER)

# Simple per-IP throttling for the public contact form (uses the cache).
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mnp-default',
    }
}
CONTACT_RATE_LIMIT = config('CONTACT_RATE_LIMIT', default=5, cast=int)  # messages / hour / IP

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




# JAZZMIN_SETTINGS = {
#     'site_header': "Desphixs",
#     'site_brand': "No1 Digital Marketplace for everyone.",
#     'site_logo': "assets/imgs/logo.png",
#     'copyright':  "All Right Reserved 2023",
#     "welcome_sign": "Welcome to Desphixs, Login Now.",
    
#     "topmenu_links": [
#         {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
#         {"name": "Company", "url": "/admin/addons/company/"},
#         {"name": "Users", "url": "/admin/userauths/user/"},
#     ],

#     "order_with_respect_to": [
#         # replace with your own models
#         "store",
#         "store.product",
#         "store.cartorder",
#         "store.cartorderitem",
#         "store.category",
#         "store.brand",
#         "store.productfaq",
#         "store.productoffers",
#         "store.productbidders",
#         "store.review",
#         "vendor",
#         "userauths"
#         "addons",
#         "addons.Company",
#         "addons.BasicAddon"
#     ],
    
#     "icons": {
#         # replace with your own model & icon 
#         "admin.LogEntry": "fas fa-file",

#         "auth": "fas fa-users-cog",
#         "auth.user": "fas fa-user",

#         "userauths.User": "fas fa-user",
#         "userauths.Profile":"fas fa-address-card",

#     },
#     "show_ui_builder" : True
# }



# JAZZMIN_UI_TWEAKS = {
#     "navbar_small_text": False,
#     "footer_small_text": False,
#     "body_small_text": True,
#     "brand_small_text": False,
#     "brand_colour": "navbar-indigo",
#     "accent": "accent-olive",
#     "navbar": "navbar-indigo navbar-dark",
#     "no_navbar_border": False,
#     "navbar_fixed": False,
#     "layout_boxed": False,
#     "footer_fixed": False,
#     "sidebar_fixed": False,
#     "sidebar": "sidebar-dark-indigo",
#     "sidebar_nav_small_text": False,
#     "sidebar_disable_expand": False,
#     "sidebar_nav_child_indent": False,
#     "sidebar_nav_compact_style": False,
#     "sidebar_nav_legacy_style": False,
#     "sidebar_nav_flat_style": False,
#     "theme": "flatly",
#     "dark_mode_theme": "cyborg",
#     "button_classes": {
#         "primary": "btn-outline-primary",
#         "secondary": "btn-outline-secondary",
#         "info": "btn-info",
#         "warning": "btn-warning",
#         "danger": "btn-danger",
#         "success": "btn-success"
#     }
# }