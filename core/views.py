from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _
from django.urls import reverse
from django.db.models import Q, Count, Avg
from datetime import datetime
import json
import logging

from .models import *
from .forms import ContactForm, NewsletterForm, ProjectRatingForm
from django.views.decorators.csrf import ensure_csrf_cookie

logger = logging.getLogger(__name__)


def get_current_language(request):
    """الحصول على اللغة الحالية مع التحقق من وجودها"""
    lang_code = request.GET.get('lang')
    if not lang_code:
        lang_code = request.session.get('django_language')
    if not lang_code:
        lang_code = translation.get_language()
    if not lang_code:
        lang_code = 'ar'
    
    try:
        language = Language.objects.get(code=lang_code, is_active=True)
    except Language.DoesNotExist:
        language = Language.objects.filter(is_default=True).first()
        if not language:
            language = Language.objects.filter(is_active=True).first()
        if language:
            lang_code = language.code
        else:
            lang_code = 'ar'
            language = None
    
    translation.activate(lang_code)
    request.session['django_language'] = lang_code
    request.LANGUAGE_CODE = lang_code
    
    return language, lang_code


def get_default_language():
    """الحصول على اللغة الافتراضية"""
    default_language = Language.objects.filter(is_default=True).first()
    if not default_language:
        default_language = Language.objects.filter(is_active=True).first()
    return default_language


def get_model_data(model_class, language, fallback=True, **filters):
    """دالة مساعدة لجلب البيانات من النماذج مع fallback للغة الافتراضية"""
    data = model_class.objects.filter(language=language, **filters)
    
    if fallback and not data.exists():
        default_language = get_default_language()
        if default_language and default_language != language:
            data = model_class.objects.filter(language=default_language, **filters)
    
    return data


def get_section_content(section_key, language):
    """جلب محتوى قسم معين حسب اللغة"""
    try:
        section = DynamicSection.objects.get(section_key=section_key, is_active=True)
        content = SectionContent.objects.get(section=section, language=language)
        return content
    except:
        default_language = get_default_language()
        if default_language and default_language != language:
            try:
                section = DynamicSection.objects.get(section_key=section_key, is_active=True)
                content = SectionContent.objects.get(section=section, language=default_language)
                return content
            except:
                pass
        return None


def get_common_context(request, language, extra_context=None):
    """جلب البيانات المشتركة لجميع الصفحات مع إحصائيات تلقائية"""
    
    # الإحصائيات التلقائية
    total_projects = Portfolio.objects.filter(is_active=True).count()
    total_testimonials = Testimonial.objects.filter(is_active=True).count()
    total_experiences = WorkExperience.objects.filter(is_active=True).count()
    total_blogs = BlogPost.objects.filter(is_published=True).count()
    
    # حساب "العاملين المجتهدين"
    hard_workers_count = PersonalInfo.objects.values('name').distinct().count()
    if hard_workers_count == 0:
        hard_workers_count = 1
    
    # ساعات الدعم التلقائية
    support_hours = total_projects * 10
    if support_hours < 100:
        support_hours = 1463
    
    auto_stats = {
        'total_projects': total_projects,
        'total_testimonials': total_testimonials,
        'total_experiences': total_experiences,
        'total_blogs': total_blogs,
        'hard_workers': hard_workers_count,
        'support_hours': support_hours,
    }
    
    context = {
        'current_language': language,
        'site_settings': SiteSetting.objects.first(),
        'personal_info': get_model_data(PersonalInfo, language, fallback=True).first(),
        'available_languages': Language.objects.filter(is_active=True),
        'global_settings': {
            setting.setting_key: setting.setting_value 
            for setting in GlobalSetting.objects.all()
        },
        'auto_stats': auto_stats,
    }
    
    if extra_context:
        context.update(extra_context)
    
    return context



@ensure_csrf_cookie
def home_page(request):
    """الصفحة الرئيسية - عرض جميع الأقسام"""
    language, lang_code = get_current_language(request)
    
    # جلب جميع البيانات
    personal_info_obj = get_model_data(PersonalInfo, language, fallback=True).first()
    educations = get_model_data(Education, language, fallback=True, is_active=True)
    work_experiences = get_model_data(WorkExperience, language, fallback=True, is_active=True)
    skill_categories = get_model_data(SkillCategory, language, fallback=True, is_active=True)
    skills = get_model_data(Skill, language, fallback=True, is_active=True)
    services = get_model_data(Service, language, fallback=True, is_active=True)
    featured_portfolios = get_model_data(Portfolio, language, fallback=True, is_active=True, is_featured=True)
    portfolios = get_model_data(Portfolio, language, fallback=True, is_active=True)
    testimonials = get_model_data(Testimonial, language, fallback=True, is_active=True)
    recent_posts = get_model_data(BlogPost, language, fallback=True, is_published=True)
    
    # ========== جلب التقييمات المقبولة من جميع المشاريع ==========
    approved_ratings = ProjectRating.objects.filter(is_approved=True).select_related('portfolio').order_by('-created_at')[:9]
    
    # لا تقم بتعيين average_rating لأنه property يتم حسابه تلقائياً
    # فقط قم بتقييم الـ queryset إذا لزم الأمر
    list(featured_portfolios)  # هذا يقيم الـ queryset
    
    sections = DynamicSection.objects.filter(is_active=True).order_by('order')
    
    section_data = {}
    for section in sections:
        content = get_section_content(section.section_key, language)
        if content:
            section_data[section.section_key] = content
    
    context_data = {
        'sections': sections,
        'section_data': section_data,
        'hero_content': get_section_content('hero', language),
        'about_content': get_section_content('about', language),
        'personal_info': personal_info_obj,
        'educations': educations,
        'work_experiences': work_experiences,
        'skill_categories': skill_categories,
        'skills': skills,
        'services': services[:6],
        'featured_portfolios': featured_portfolios[:6],
        'portfolios': portfolios,
        'testimonials': testimonials,
        'recent_posts': recent_posts[:9],
        'portfolios_count': portfolios.count(),
        'approved_ratings': approved_ratings,  # التقييمات المقبولة للعرض
    }
    
    context = get_common_context(request, language, context_data)
    return render(request, 'index.html', context)


def services_page(request):
    """صفحة جميع الخدمات"""
    language, lang_code = get_current_language(request)
    
    search_query = request.GET.get('search', '')
    featured_only = request.GET.get('featured', '') == 'true'
    
    services = get_model_data(Service, language, fallback=True, is_active=True)
    
    if search_query:
        services = services.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(full_description__icontains=search_query)
        )
    
    if featured_only:
        services = services.filter(is_featured=True)
    
    paginator = Paginator(services, 9)
    page = request.GET.get('page', 1)
    
    try:
        services_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        services_page = paginator.page(1)
    
    context_data = {
        'services': services_page,
        'search_query': search_query,
        'featured_only': featured_only,
        'total_services': services.count(),
    }
    
    context = get_common_context(request, language, context_data)
    return render(request, 'services.html', context)


def service_detail_page(request, slug):
    """صفحة تفاصيل خدمة محددة"""
    language, lang_code = get_current_language(request)
    default_language = get_default_language()
    
    try:
        service = Service.objects.get(slug=slug, language=language, is_active=True)
    except Service.DoesNotExist:
        if default_language:
            service = get_object_or_404(Service, slug=slug, language=default_language, is_active=True)
        else:
            raise
    
    service_details = ServiceDetail.objects.filter(service=service, language=language).order_by('order')
    if not service_details.exists() and default_language:
        service_details = ServiceDetail.objects.filter(service=service, language=default_language).order_by('order')
    
    related_services = Service.objects.filter(language=language, is_active=True).exclude(id=service.id)[:3]
    if not related_services.exists() and default_language:
        related_services = Service.objects.filter(language=default_language, is_active=True).exclude(id=service.id)[:3]
    
    context_data = {
        'service': service,
        'service_details': service_details,
        'related_services': related_services,
    }
    
    context = get_common_context(request, language, context_data)
    return render(request, 'service-detail.html', context)

def portfolio_page(request):
    """صفحة جميع المشاريع مع عرض التقييمات"""
    language, lang_code = get_current_language(request)
    default_language = get_default_language()
    
    category_slug = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    portfolios = get_model_data(Portfolio, language, fallback=True, is_active=True)
    categories = get_model_data(PortfolioCategory, language, fallback=True)
    
    # لا تقم بتعيين average_rating - يتم حسابه تلقائياً عند استخدامه في القالب
    # فقط قم بتقييم الـ queryset إذا لزم الأمر
    list(portfolios)
    
    if category_slug:
        try:
            category = PortfolioCategory.objects.get(slug=category_slug, language=language)
            portfolios = portfolios.filter(category=category)
        except PortfolioCategory.DoesNotExist:
            if default_language:
                try:
                    category = PortfolioCategory.objects.get(slug=category_slug, language=default_language)
                    portfolios = portfolios.filter(category=category)
                except:
                    pass
    
    if search_query:
        portfolios = portfolios.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(client_name__icontains=search_query)
        )
    
    # معالجة المشاريع للتأكد من وجود صور
    for portfolio in portfolios:
        if not portfolio.cover_image or not hasattr(portfolio.cover_image, 'url'):
            portfolio.has_image = False
        else:
            try:
                portfolio.cover_image.url
                portfolio.has_image = True
            except (ValueError, AttributeError):
                portfolio.has_image = False
    
    paginator = Paginator(portfolios, 8)
    page = request.GET.get('page', 1)
    
    try:
        portfolios_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        portfolios_page = paginator.page(1)
    
    context_data = {
        'portfolios': portfolios_page,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'total_projects': portfolios.count(),
    }
    
    context = get_common_context(request, language, context_data)
    return render(request, 'portfolio.html', context)


def portfolio_detail_page(request, slug):
    """صفحة تفاصيل مشروع محدد مع إمكانية التقييم"""
    language, lang_code = get_current_language(request)
    default_language = get_default_language()
    
    try:
        portfolio = Portfolio.objects.get(slug=slug, language=language, is_active=True)
    except Portfolio.DoesNotExist:
        if default_language:
            portfolio = get_object_or_404(Portfolio, slug=slug, language=default_language, is_active=True)
        else:
            raise
    
    # التحقق من وجود الصورة
    if not portfolio.cover_image or not hasattr(portfolio.cover_image, 'url'):
        portfolio.has_image = False
    else:
        try:
            portfolio.cover_image.url
            portfolio.has_image = True
        except (ValueError, AttributeError):
            portfolio.has_image = False
    
    features = PortfolioFeature.objects.filter(portfolio=portfolio, language=language).order_by('order')
    if not features.exists() and default_language:
        features = PortfolioFeature.objects.filter(portfolio=portfolio, language=default_language).order_by('order')
    
    related_portfolios = Portfolio.objects.filter(
        language=language, is_active=True, category=portfolio.category
    ).exclude(id=portfolio.id)[:3]
    if not related_portfolios.exists() and default_language:
        related_portfolios = Portfolio.objects.filter(
            language=default_language, is_active=True, category=portfolio.category
        ).exclude(id=portfolio.id)[:3]
    
    # ========== لا تقم بتعيين avg_rating لأنه property ==========
    # فقط قم بتقييم الـ queryset إذا لزم الأمر
    list(related_portfolios)  # هذا يقيم الـ queryset
    
    # نظام التقييمات
    rating_form = ProjectRatingForm()
    user_has_rated = False
    
    if request.method == 'POST' and 'submit_rating' in request.POST:
        rating_form = ProjectRatingForm(request.POST)
        if rating_form.is_valid():
            email = rating_form.cleaned_data['email']
            existing_rating = ProjectRating.objects.filter(portfolio=portfolio, email=email).first()
            
            if existing_rating:
                messages.warning(request, _('You have already rated this project. Thank you!'))
            else:
                rating = rating_form.save(commit=False)
                rating.portfolio = portfolio
                rating.save()
                messages.success(request, _('Thank you for your rating! It will appear after approval.'))
            
            return redirect('portfolio_detail', slug=portfolio.slug)
    
    # جلب التقييمات المقبولة
    approved_ratings = portfolio.ratings.filter(is_approved=True)
    
    context_data = {
        'portfolio': portfolio,
        'features': features,
        'related_portfolios': related_portfolios,
        'rating_form': rating_form,
        'approved_ratings': approved_ratings,
        'user_has_rated': user_has_rated,
        'average_rating': portfolio.average_rating,
        'ratings_count': portfolio.ratings_count,
    }
    
    context = get_common_context(request, language, context_data)
    return render(request, 'portfolio-detail.html', context)


def blog_page(request):
    """صفحة المدونة الرئيسية"""
    language, lang_code = get_current_language(request)
    default_language = get_default_language()
    
    search_query = request.GET.get('search', '')
    category_slug = request.GET.get('category', '')
    
    posts = get_model_data(BlogPost, language, fallback=True, is_published=True)
    categories = get_model_data(BlogCategory, language, fallback=True)
    
    for category in categories:
        category.post_count = BlogPost.objects.filter(
            category=category, is_published=True
        ).count()
    
    if category_slug:
        try:
            category = BlogCategory.objects.get(slug=category_slug, language=language)
            posts = posts.filter(category=category)
        except BlogCategory.DoesNotExist:
            if default_language:
                try:
                    category = BlogCategory.objects.get(slug=category_slug, language=default_language)
                    posts = posts.filter(category=category)
                except:
                    pass
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    paginator = Paginator(posts, 6)
    page = request.GET.get('page', 1)
    
    try:
        posts_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        posts_page = paginator.page(1)
    
    recent_posts = get_model_data(BlogPost, language, fallback=True, is_published=True)[:5]
    
    context_data = {
        'posts': posts_page,
        'categories': categories,
        'recent_posts': recent_posts,
        'search_query': search_query,
        'current_category': category_slug,
        'total_posts': posts.count(),
    }
    
    context = get_common_context(request, language, context_data)
    return render(request, 'blog.html', context)


def blog_detail_page(request, slug):
    """صفحة تفاصيل مقال محدد"""
    language, lang_code = get_current_language(request)
    default_language = get_default_language()
    
    try:
        post = BlogPost.objects.get(slug=slug, language=language, is_published=True)
    except BlogPost.DoesNotExist:
        if default_language:
            post = get_object_or_404(BlogPost, slug=slug, language=default_language, is_published=True)
        else:
            raise
    
    post.views_count += 1
    post.save()
    
    related_posts = BlogPost.objects.filter(
        language=language, is_published=True, category=post.category
    ).exclude(id=post.id)[:3]
    if not related_posts.exists() and default_language:
        related_posts = BlogPost.objects.filter(
            language=default_language, is_published=True, category=post.category
        ).exclude(id=post.id)[:3]
    
    previous_post = BlogPost.objects.filter(
        language=language, is_published=True, published_date__lt=post.published_date
    ).order_by('-published_date').first()
    
    next_post = BlogPost.objects.filter(
        language=language, is_published=True, published_date__gt=post.published_date
    ).order_by('published_date').first()
    
    context_data = {
        'post': post,
        'related_posts': related_posts,
        'previous_post': previous_post,
        'next_post': next_post,
    }
    
    context = get_common_context(request, language, context_data)
    return render(request, 'blog-detail.html', context)


def blog_category_page(request, slug):
    """صفحة تصنيف محدد من المدونة"""
    language, lang_code = get_current_language(request)
    default_language = get_default_language()
    
    try:
        category = BlogCategory.objects.get(slug=slug, language=language)
    except BlogCategory.DoesNotExist:
        if default_language:
            category = get_object_or_404(BlogCategory, slug=slug, language=default_language)
        else:
            raise
    
    posts = BlogPost.objects.filter(
        category=category, is_published=True
    ).order_by('-published_date')
    
    paginator = Paginator(posts, 6)
    page = request.GET.get('page', 1)
    
    try:
        posts_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        posts_page = paginator.page(1)
    
    context_data = {
        'category': category,
        'posts': posts_page,
        'total_posts': posts.count(),
    }
    
    context = get_common_context(request, language, context_data)
    return render(request, 'blog-category.html', context)


def about_page(request):
    """صفحة من نحن"""
    language, lang_code = get_current_language(request)
    default_language = get_default_language()
    
    try:
        page = StaticPage.objects.get(slug='about', language=language, is_published=True)
    except StaticPage.DoesNotExist:
        if default_language:
            page = StaticPage.objects.filter(slug='about', language=default_language, is_published=True).first()
        else:
            page = None
    
    stats = {
        'projects_count': get_model_data(Portfolio, language, fallback=True, is_active=True).count(),
        'clients_count': get_model_data(Testimonial, language, fallback=True, is_active=True).count(),
        'experience_years': get_model_data(WorkExperience, language, fallback=True, is_active=True).count(),
        'articles_count': get_model_data(BlogPost, language, fallback=True, is_published=True).count(),
    }
    
    context_data = {
        'page': page,
        'stats': stats,
        'skills': get_model_data(Skill, language, fallback=True, is_active=True)[:8],
    }
    
    context = get_common_context(request, language, context_data)
    return render(request, 'about.html', context)


def static_page_view(request, slug):
    """عرض أي صفحة ثابتة ديناميكية"""
    language, lang_code = get_current_language(request)
    default_language = get_default_language()
    
    try:
        page = StaticPage.objects.get(slug=slug, language=language, is_published=True)
    except StaticPage.DoesNotExist:
        if default_language:
            page = get_object_or_404(StaticPage, slug=slug, language=default_language, is_published=True)
        else:
            raise
    
    context_data = {'page': page}
    context = get_common_context(request, language, context_data)
    return render(request, 'static-page.html', context)


def contact_page(request):
    """صفحة الاتصال"""
    language, lang_code = get_current_language(request)
    site_settings = SiteSetting.objects.first()
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                contact_message = ContactMessage(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data.get('phone', ''),
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message'],
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                contact_message.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': _('Your message has been sent successfully!')})
                
                messages.success(request, _('Your message has been sent successfully!'))
                return redirect('contact')
                
            except Exception as e:
                logger.error(f"Error saving contact message: {e}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': _('An error occurred. Please try again.')})
                messages.error(request, _('An error occurred. Please try again.'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(form.errors)})
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ContactForm()
    
    context_data = {'form': form, 'site_settings': site_settings}
    context = get_common_context(request, language, context_data)
    return render(request, 'contact.html', context)


def get_client_ip(request):
    """الحصول على IP الزائر"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def set_language(request):
    """تغيير لغة الموقع"""
    if request.method == 'POST':
        language_code = request.POST.get('language', 'en')
        
        try:
            language = Language.objects.get(code=language_code, is_active=True)
            translation.activate(language_code)
            request.session['django_language'] = language_code
            request.LANGUAGE_CODE = language_code
            
            next_url = request.POST.get('next', '/')
            response = redirect(next_url)
            response.set_cookie('django_language', language_code, max_age=365*24*60*60)
            
            return response
            
        except Language.DoesNotExist:
            pass
    
    return redirect('/')


def search_page(request):
    """صفحة البحث العامة"""
    language, lang_code = get_current_language(request)
    
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')
    
    results = {
        'portfolios': [],
        'blog_posts': [],
        'services': [],
        'total_count': 0,
    }
    
    if query:
        if search_type in ['all', 'portfolio']:
            portfolios = get_model_data(Portfolio, language, fallback=True, is_active=True).filter(
                Q(title__icontains=query) | Q(short_description__icontains=query)
            )[:5]
            results['portfolios'] = portfolios
            results['total_count'] += portfolios.count()
        
        if search_type in ['all', 'blog']:
            blog_posts = get_model_data(BlogPost, language, fallback=True, is_published=True).filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )[:5]
            results['blog_posts'] = blog_posts
            results['total_count'] += blog_posts.count()
        
        if search_type in ['all', 'services']:
            services = get_model_data(Service, language, fallback=True, is_active=True).filter(
                Q(title__icontains=query) | Q(short_description__icontains=query)
            )[:5]
            results['services'] = services
            results['total_count'] += services.count()
    
    context_data = {'query': query, 'search_type': search_type, 'results': results}
    context = get_common_context(request, language, context_data)
    return render(request, 'search-results.html', context)


def newsletter_subscribe(request):
    """الاشتراك في النشرة البريدية"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            messages.success(request, _('Thank you for subscribing!'))
        else:
            messages.error(request, _('Invalid email address.'))
        
        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)
    return redirect('/')


def api_portfolio_filter(request):
    """API لفلترة المشاريع (AJAX)"""
    language, lang_code = get_current_language(request)
    
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    portfolios = get_model_data(Portfolio, language, fallback=True, is_active=True)
    
    if category:
        portfolios = portfolios.filter(category__slug=category)
    
    if search:
        portfolios = portfolios.filter(title__icontains=search)
    
    data = []
    for portfolio in portfolios[:20]:
        data.append({
            'id': portfolio.id,
            'title': portfolio.title,
            'slug': portfolio.slug,
            'cover_image': portfolio.cover_image.url if portfolio.cover_image else '',
            'category': portfolio.category.name if portfolio.category else '',
            'short_description': portfolio.short_description,
            'avg_rating': portfolio.average_rating,
        })
    
    return JsonResponse({'success': True, 'portfolios': data})


def api_testimonials(request):
    """API لجلب الشهادات (للـ AJAX)"""
    language, lang_code = get_current_language(request)
    
    testimonials = get_model_data(Testimonial, language, fallback=True, is_active=True)
    
    data = []
    for testimonial in testimonials:
        data.append({
            'name': testimonial.client_name,
            'position': testimonial.client_position,
            'content': testimonial.content,
            'rating': testimonial.rating,
            'image': testimonial.client_image.url if testimonial.client_image else '',
        })
    
    return JsonResponse({'success': True, 'testimonials': data})


def api_services(request):
    """API لجلب الخدمات"""
    language, lang_code = get_current_language(request)
    
    services = get_model_data(Service, language, fallback=True, is_active=True)
    
    data = []
    for service in services:
        data.append({
            'id': service.id,
            'title': service.title,
            'slug': service.slug,
            'description': service.short_description,
            'icon': service.icon,
            'is_featured': service.is_featured,
        })
    
    return JsonResponse({'success': True, 'services': data})


def sitemap_view(request):
    """إنشاء Sitemap ديناميكي"""
    language, lang_code = get_current_language(request)
    
    urls = [
        {'url': '/', 'priority': 1.0},
        {'url': '/about/', 'priority': 0.8},
        {'url': '/services/', 'priority': 0.8},
        {'url': '/portfolio/', 'priority': 0.8},
        {'url': '/blog/', 'priority': 0.7},
        {'url': '/contact/', 'priority': 0.6},
    ]
    
    for service in get_model_data(Service, language, fallback=True, is_active=True):
        urls.append({'url': f'/services/{service.slug}/', 'priority': 0.7})
    
    for portfolio in get_model_data(Portfolio, language, fallback=True, is_active=True):
        urls.append({'url': f'/portfolio/{portfolio.slug}/', 'priority': 0.7})
    
    for post in get_model_data(BlogPost, language, fallback=True, is_published=True):
        urls.append({'url': f'/blog/{post.slug}/', 'priority': 0.6})
    
    context = {'urls': urls, 'current_language': language}
    return render(request, 'sitemap.xml', context, content_type='application/xml')


def robots_view(request):
    """ملف robots.txt"""
    context = {'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}
    return render(request, 'robots.txt', context, content_type='text/plain')


def handler400(request, exception):
    """صفحة 400 - Bad Request"""
    language, lang_code = get_current_language(request)
    context = get_common_context(request, language)
    context['request_path'] = request.path
    return render(request, 'error/400.html', context, status=400)


def handler403(request, exception):
    """صفحة 403 - Forbidden"""
    language, lang_code = get_current_language(request)
    context = get_common_context(request, language)
    context['request_path'] = request.path
    return render(request, 'error/403.html', context, status=403)


def handler404(request, exception):
    """صفحة 404 - Not Found"""
    language, lang_code = get_current_language(request)
    context = get_common_context(request, language)
    context['request_path'] = request.path
    context['exception'] = str(exception) if exception else None
    return render(request, 'error/404.html', context, status=404)

def handler500(request):
    
    """صفحة 500 - Server Error"""
    language, lang_code = get_current_language(request)
    context = get_common_context(request, language)
    context['debug'] = settings.DEBUG
    
    import sys
    exception_type, exception_value, exception_traceback = sys.exc_info()
    if exception_value:
        context['exception_message'] = str(exception_value)
    
    return render(request, 'error/500.html', context, status=500)



