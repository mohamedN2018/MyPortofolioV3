from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.urls import re_path
from django.views.static import serve
from django.utils.translation import gettext_lazy as _
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # path('i18n/', include('django.conf.urls.i18n')),
]


# urlpatterns += i18n_patterns(
#     path('', include('core.urls')),
# )


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# تسجيل معالجات الأخطاء المخصّصة (وإلا لن تُعرض قوالب error/*.html أبداً)
handler400 = 'core.views.handler400'
handler403 = 'core.views.handler403'
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'