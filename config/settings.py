import os
from pathlib import Path
import dj_database_url          # ← NUEVO: para conectar con PostgreSQL en Render

BASE_DIR = Path(__file__).resolve().parent.parent

# Para que Django detecte HTTPS detrás del proxy de Render
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ─── SEGURIDAD Y ENTORNO ─────────────────────────────────
# En producción (Render) estas variables se definirán en el panel de control.
# En desarrollo local, se usan los valores por defecto.
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-l#w9bo)b5mha(4^2josjk-dt@-a84-q+9spx8+wy#4)qd0ujsk')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Permitir el dominio de Render y los entornos locales
ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,.onrender.com'
).split(',')

# ─── APLICACIONES ─────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'channels',
    'core',
    'usuarios',
    'chat',
    'cookie_consent',

    # Eventos virtuales
    'virtualEvent.apps.VirtualEventConfig',
    've_streaming',
    've_chat',
    've_invitations',

    # Eventos presenciales
    'in_person_events.apps.InPersonEventsConfig',
    'pe_registration.apps.PeRegistrationConfig',
    'pe_agenda.apps.AgendaConfig',
    'pe_inventory.apps.PeInventoryConfig',
    'pe_stand',
    'pe_staff',
    'pe_communication',
    'pe_analytics',
    'pe_surveys',

    'django.contrib.humanize',
    'anymail',
]

# ─── MIDDLEWARE (IMPORTANTE: WhiteNoise añadido) ──────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # ← NUEVO: Sirve estáticos eficientemente
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'virtualEvent.middleware.VisitTrackingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'core.context_processors.cookie_consent_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'   # ← NUEVO: necesario para WebSockets/Channels

# ─── BASE DE DATOS (Automática con dj_database_url) ──────
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),  # Render la proveerá al crear la BD
        conn_max_age=600,
        engine='django.db.backends.postgresql',
    )
}

# ─── VALIDACIÓN DE CONTRASEÑAS ────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── INTERNACIONALIZACIÓN ─────────────────────────────────
USE_I18N = True
USE_TZ = True
LANGUAGE_CODE = 'es'
LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# ─── ARCHIVOS ESTÁTICOS Y MEDIA ───────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # ← NUEVO

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── COOKIES Y CONSENTIMIENTO ─────────────────────────────
COOKIE_CONSENT_NAME = "cookie_consent"

# ─── MODELO DE USUARIO PERSONALIZADO ──────────────────────
AUTH_USER_MODEL = 'usuarios.Usuario'

LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'usuarios:perfil'
LOGOUT_REDIRECT_URL = 'usuarios:login'

# ─── CONFIGURACIÓN DE CORREO CON GMAIL (SMTP) ──────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'rocioplanash@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'rocioplanash@gmail.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

BASE_URL = 'http://127.0.0.1:8000'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# ─── CANALES (WebSocket) ──────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ─── ZONA HORARIA ─────────────────────────────────────────
TIME_ZONE = 'America/Havana'
USE_TZ = True

# ─── SEGURIDAD ADICIONAL (solo en producción) ─────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ─── MODERACIÓN DE CHAT ───────────────────────────────────
OFFENSIVE_WORDS = [
    'mierda', 'puta', 'cabron', 'cojones', 'hostia', 'joder', 'pendejo',
    'imbecil', 'estupido', 'gilipollas', 'capullo', 'zorra', 'maricon',
    'culo', 'tonto', 'idiota', 'maldito', 'malparido', 'hijueputa',
    'carajo', 'verga', 'chucha', 'concha', 'pija', 'bobo'
]

# ─── CSRF y orígenes de confianza ─────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# En producción, agregaremos automáticamente el dominio de Render
if not DEBUG:
    CSRF_TRUSTED_ORIGINS.append('https://*.onrender.com')

# Configuración por defecto (Render la ajustará con HTTPS)
CSRF_COOKIE_SECURE = DEBUG is False    # ← True en producción, False en desarrollo
SESSION_COOKIE_SECURE = DEBUG is False

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'