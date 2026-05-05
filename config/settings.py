import os
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-l#w9bo)b5mha(4^2josjk-dt@-a84-q+9spx8+wy#4)qd0ujsk')
DEBUG = True
ALLOWED_HOSTS = []

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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'plataforma_eventos'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'admin'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'options': '-c client_encoding=utf8'
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización
USE_I18N = True
USE_TZ = True
LANGUAGE_CODE = 'es'
LANGUAGES = [
    ('es', _('Español')),
    ('en', _('English')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

COOKIE_CONSENT_NAME = "cookie_consent"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

AUTH_USER_MODEL = 'usuarios.Usuario'

LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'usuarios:perfil'
LOGOUT_REDIRECT_URL = 'usuarios:login'

# Configuración de correo para desarrollo (MUESTRA CORREOS EN CONSOLA)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'rocioplanash@gmail.com'
EMAIL_HOST_PASSWORD = 'pifdnblypvrsgoya'
DEFAULT_FROM_EMAIL = 'rocioplanash@gmail.com'
EMAIL_TIMEOUT = 30

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

# Capa de canales en memoria (solo para desarrollo)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

TIME_ZONE = 'America/Havana'
USE_TZ = True

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Palabras ofensivas para moderación automática
OFFENSIVE_WORDS = [
    'mierda', 'puta', 'cabron', 'cojones', 'hostia', 'joder', 'pendejo',
    'imbecil', 'estupido', 'gilipollas', 'capullo', 'zorra', 'maricon',
    'culo', 'tonto', 'idiota', 'maldito', 'malparido', 'hijueputa',
    'carajo', 'verga', 'chucha', 'concha', 'pija', 'bobo'
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False

