from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib import admin
from django.views.i18n import set_language as django_set_language
from django.utils.translation import gettext_lazy as _

from . import views
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
    # path(_('about/'), views.about_page, name='about'),
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
    path('sitemap.xml', views.sitemap_view, name='sitemap'),
    path('robots.txt', views.robots_view, name='robots'),
]

