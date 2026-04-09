from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, Portfolio, Service, Language

class StaticViewSitemap(Sitemap):
    """الصفحات الثابتة"""
    priority = 0.5
    changefreq = 'weekly'
    
    def items(self):
        return ['home', 'about', 'services', 'portfolio', 'blog', 'contact']
    
    def location(self, item):
        return reverse(item)

class BlogSitemap(Sitemap):
    """مقالات المدونة"""
    priority = 0.6
    changefreq = 'weekly'
    
    def items(self):
        # جلب المقالات المنشورة من جميع اللغات
        return BlogPost.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_date
    
    def location(self, obj):
        return reverse('snapfolio:blog_detail', args=[obj.slug])

class PortfolioSitemap(Sitemap):
    """مشاريع البورتفوليو"""
    priority = 0.7
    changefreq = 'monthly'
    
    def items(self):
        # جلب المشاريع النشطة من جميع اللغات
        return Portfolio.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.project_date
    
    def location(self, obj):
        return reverse('snapfolio:portfolio_detail', args=[obj.slug])

class ServiceSitemap(Sitemap):
    """الخدمات"""
    priority = 0.7
    changefreq = 'monthly'
    
    def items(self):
        # جلب الخدمات النشطة من جميع اللغات
        return Service.objects.filter(is_active=True)
    
    def location(self, obj):
        return reverse('snapfolio:service_detail', args=[obj.slug])