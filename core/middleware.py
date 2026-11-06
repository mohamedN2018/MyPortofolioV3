from django.conf import settings
from django.utils import translation


class RequestLanguageIsolationMiddleware:
    """
    Views call ``translation.activate()`` without LocaleMiddleware, so the
    active language used to leak from one request to the next in the same
    worker thread. A cookie-less crawler could then get "/" in Arabic or
    English depending on the previous visitor — inconsistent for SEO.

    Reset to the site default before each request and deactivate afterwards.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        translation.activate(getattr(settings, "SITE_DEFAULT_LANGUAGE", "en"))
        try:
            return self.get_response(request)
        finally:
            translation.deactivate()
