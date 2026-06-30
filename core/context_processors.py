# context_processors.py
from django.utils import translation
from django.db.models import Avg
from .models import Language, SiteSetting, Menu

def site_settings(request):
    """توفير إعدادات الموقع لجميع القوالب مع الترجمة"""
    try:
        settings = SiteSetting.objects.first()
    except:
        settings = None
    return {
        'site_settings': settings,
    }

def site_languages(request):
    """توفير اللغات المتاحة واللغة الحالية"""
    try:
        languages = Language.objects.filter(is_active=True)
    except:
        languages = []
    
    # الحصول على اللغة الحالية
    current_lang_code = translation.get_language()
    if not current_lang_code:
        current_lang_code = request.session.get('django_language', 'ar')
    
    try:
        current_language = Language.objects.get(code=current_lang_code)
    except Language.DoesNotExist:
        current_language = languages.filter(is_default=True).first()
        if not current_language and languages:
            current_language = languages.first()
    
    # تفعيل اللغة
    if current_language:
        translation.activate(current_language.code)
        request.session['django_language'] = current_language.code
    
    return {
        'available_languages': languages,
        'current_language': current_language,
    }

def site_menus(request):
    """توفير القوائم حسب اللغة الحالية"""
    current_lang_code = translation.get_language()
    
    try:
        language = Language.objects.get(code=current_lang_code, is_active=True)
    except:
        language = Language.objects.filter(is_default=True).first()
        if not language:
            language = Language.objects.first()
    
    menus = {}
    if language:
        try:
            for menu in Menu.objects.filter(language=language, is_active=True):
                items = menu.items.filter(parent__isnull=True, is_active=True).order_by('order')
                menus[menu.location] = items
        except:
            pass
    
    return {
        'menus': menus,
    }

def global_settings(request):
    """توفير الإعدادات العامة"""
    settings_dict = {}
    try:
        from .models import GlobalSetting
        for setting in GlobalSetting.objects.all():
            if setting.setting_type == 'boolean':
                settings_dict[setting.setting_key] = setting.setting_value.lower() == 'true'
            elif setting.setting_type == 'number':
                try:
                    settings_dict[setting.setting_key] = float(setting.setting_value)
                except:
                    settings_dict[setting.setting_key] = setting.setting_value
            else:
                settings_dict[setting.setting_key] = setting.setting_value
    except:
        pass
    
    return {
        'global_settings': settings_dict,
    }


def dashboard_stats(request):
    """توفير إحصائيات لوحة التحكم لكل صفحات الـ dashboard.

    تُحسب فقط لمسارات /dashboard/ ولمستخدم superuser، حتى تظهر شارات
    (badges) التقييمات المعلّقة والرسائل غير المقروءة في القائمة الجانبية
    على جميع الصفحات وليس صفحة الـ index فقط.
    """
    path = request.path or ''
    user = getattr(request, 'user', None)

    if not path.startswith('/dashboard'):
        return {}
    if not (user and user.is_authenticated and user.is_superuser):
        return {}

    # استيراد محلي لتجنّب أي تعارض في الاستيراد عند تحميل التطبيق
    from .models import (
        Portfolio, Service, BlogPost, ProjectRating,
        ContactMessage, Testimonial, Skill, WorkExperience,
    )

    try:
        stats = {
            'total_portfolios': Portfolio.objects.filter(is_active=True).count(),
            'total_portfolios_all': Portfolio.objects.count(),
            'total_services': Service.objects.filter(is_active=True).count(),
            'total_blog_posts': BlogPost.objects.filter(is_published=True).count(),
            'total_ratings': ProjectRating.objects.count(),
            'pending_ratings': ProjectRating.objects.filter(is_approved=False).count(),
            'total_messages': ContactMessage.objects.count(),
            'unread_messages': ContactMessage.objects.filter(status='unread').count(),
            'total_testimonials': Testimonial.objects.filter(is_active=True).count(),
            'total_skills': Skill.objects.filter(is_active=True).count(),
            'total_experiences': WorkExperience.objects.filter(is_active=True).count(),
            'avg_rating': ProjectRating.objects.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0,
        }
    except Exception:
        stats = {}

    return {'stats': stats}
    
    
    

