from django.utils import translation
from django.conf import settings

class ForceAdminEnglishMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            translation.activate('en')
            request.LANGUAGE_CODE = 'en'
        else:
            translation.activate('ro')
            request.LANGUAGE_CODE = 'ro'
        response = self.get_response(request)
        return response


class EnforceDefaultLanguageMiddleware:
    """Ensure the default language (settings.LANGUAGE_CODE) is active when no language
    has been selected via URL/session/cookie. This prevents Django from using the
    browser Accept-Language header as the initial language.

    Place this middleware after `django.middleware.locale.LocaleMiddleware` in
    `MIDDLEWARE` so it can override the negotiated language when needed.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Decide if language was explicitly selected (URL prefix, session, cookie)
        path = request.path_info or request.path
        # check first path segment for language codes like /en/ or /ro/
        first_seg = None
        if path and path.startswith('/'):
            parts = path.split('/')
            if len(parts) > 1 and parts[1]:
                first_seg = parts[1]

        session_lang = request.session.get('django_language') if hasattr(request, 'session') else None
        cookie_lang = request.COOKIES.get(getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language'))

        # If user explicitly selected language via URL prefix, session or cookie, respect it.
        # use configured LANGUAGES codes (static list) to detect URL prefix
        configured_codes = [code for code, _ in getattr(settings, 'LANGUAGES', [])]
        if first_seg in configured_codes:
            # let LocaleMiddleware's language stand
            pass
        elif session_lang or cookie_lang:
            # let LocaleMiddleware's language stand (it will have taken session/cookie)
            pass
        else:
            # No explicit selection -> enforce default language
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE

        response = self.get_response(request)
        return response