from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.views.i18n import set_language as django_set_language
from django.utils.translation import gettext_lazy as _

from django.urls import re_path

from . import views
from . import brand_views
from .sitemaps import StaticViewSitemap, BlogSitemap, PortfolioSitemap, ServiceSitemap

# تعريف Sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
    'portfolio': PortfolioSitemap,
    'services': ServiceSitemap,
}


urlpatterns = [
    # ======================
    # الصفحات الرئيسية
    # ======================
    path('', views.home_page, name='home'),
    # الصفحة الرسمية للهوية (Official identity page) + السيرة الذاتية + المعرض
    path('about/mohamed-nabil/', brand_views.identity_page, name='identity'),
    path('cv/', brand_views.cv_page, name='cv'),
    path('cv/view/', brand_views.cv_view, name='cv_view'),
    path('cv/download/', brand_views.cv_download, name='cv_download'),
    path('gallery/', brand_views.gallery_page, name='gallery'),
    path(_('about/'), views.about_page, name='about'),
    path(_('contact/'), views.contact_page, name='contact'),
    path(_('search/'), views.search_page, name='search'),
    
    
    path('dashboard/', include('core.dashboard.urls', namespace='dashboard')),


    # ======================
    # صفحات الخدمات
    # ======================
    path(_('services/'), views.services_page, name='services'),
    path(_('services/<slug:slug>/'), views.service_detail_page, name='service_detail'),
    
    # ======================
    # صفحات المشاريع (Portfolio)
    # ======================
    path(_('portfolio/'), views.portfolio_page, name='portfolio'),
    path(_('portfolio/<slug:slug>/'), views.portfolio_detail_page, name='portfolio_detail'),
    
    # ======================
    # صفحات المدونة
    # ======================
    path(_('blog/'), views.blog_page, name='blog'),
    path(_('blog/<slug:slug>/'), views.blog_detail_page, name='blog_detail'),
    path(_('blog/category/<slug:slug>/'), views.blog_category_page, name='blog_category'),
    
    # ======================
    # الصفحات الثابتة الديناميكية
    # ======================
    path(_('page/<slug:slug>/'), views.static_page_view, name='static_page'),
    
    # ======================
    # تغيير اللغة
    # ======================
    path('set-language/', views.set_language, name='set_language'),
    path('i18n/', django_set_language, name='django_set_language'),
    
    # ======================
    
    # API endpoints (AJAX)
    # ======================
    path('api/portfolio-filter/', views.api_portfolio_filter, name='api_portfolio_filter'),
    path('api/testimonials/', views.api_testimonials, name='api_testimonials'),
    path('api/services/', views.api_services, name='api_services'),
    path('api/newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # ======================
    # Sitemap و Robots
    # ======================
    path('sitemap.xml', brand_views.sitemap_xml, name='sitemap'),
    path('robots.txt', brand_views.robots_txt, name='robots'),
    path('llms.txt', brand_views.llms_txt, name='llms_txt'),
    # Google Search Console HTML verification (served byte-for-byte from /public)
    re_path(r'^(?P<filename>google[0-9a-f]{8,32}\.html)$', brand_views.public_root_file, name='public_root_file'),
]

