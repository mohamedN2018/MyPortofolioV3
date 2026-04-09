# context_processors.py
from .models import Language, SiteSetting, Menu, GlobalSetting

def site_settings(request):
    """توفير إعدادات الموقع لجميع القوالب"""
    try:
        settings = SiteSetting.objects.first()
    except:
        settings = None
    return {
        'site_settings': settings,
    }

def site_languages(request):
    """توفير اللغات المتاحة"""
    try:
        languages = Language.objects.filter(is_active=True)
    except:
        languages = []
    
    # الحصول على اللغة الحالية من الجلسة - جعل العربية الافتراضية
    current_language_code = request.session.get('django_language', 'ar')
    try:
        current_language = Language.objects.get(code=current_language_code)
    except:
        current_language = languages.filter(is_default=True).first()
        if not current_language and languages:
            current_language = languages.first()
    
    return {
        'available_languages': languages,
        'current_language': current_language,
    }

def site_menus(request):
    """توفير القوائم لجميع القوالب"""
    current_lang = request.session.get('django_language', 'ar')
    
    try:
        language = Language.objects.get(code=current_lang, is_active=True)
    except:
        language = Language.objects.filter(is_default=True).first()
        if not language:
            language = Language.objects.first()
    
    menus = {}
    if language:
        for menu in Menu.objects.filter(language=language, is_active=True):
            items = menu.items.filter(parent__isnull=True, is_active=True).order_by('order')
            menus[menu.location] = items
    
    return {
        'menus': menus,
    }

def global_settings(request):
    """توفير الإعدادات العامة"""
    settings_dict = {}
    try:
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