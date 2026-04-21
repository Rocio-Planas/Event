# core/context_processors.py
from django.conf import settings

def cookie_consent_processor(request):
    """
    Añade 'cookie_consent_required' a todas las plantillas.
    True si el usuario NO ha dado aún su consentimiento (debe mostrar el banner).
    """
    cookie_name = getattr(settings, 'COOKIE_CONSENT_NAME', 'cookie_consent')
    has_consent = request.COOKIES.get(cookie_name) is not None
    return {'cookie_consent_required': not has_consent}