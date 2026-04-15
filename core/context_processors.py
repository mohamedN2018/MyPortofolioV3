# context_processors.py
from django.utils import translation
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
    
    
    

