import os
from pathlib import Path
import environ
import logging
from dotenv import load_dotenv
import os

load_dotenv()  # Charge les variables depuis le fichier .env

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("La clé secrète DJANGO_SECRET_KEY n'est pas définie.")


# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize the environment
env = environ.Env()
environ.Env.read_env()  # Load environment variables from .env file

# Debug mode
DEBUG = env.bool('DJANGO_DEBUG', default=True)

# Security settings
SECRET_KEY = env('DJANGO_SECRET_KEY')
FIELD_ENCRYPTION_KEY = env('FIELD_ENCRYPTION_KEY')

# Allowed hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])

# Custom user model
AUTH_USER_MODEL = "users.CustomUser"

# Caching configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Session engine
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Celery configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default backend
    'allauth.account.auth_backends.AuthenticationBackend',  # Enable Allauth backend
    'axes.backends.AxesStandaloneBackend',  # Using AxesStandaloneBackend for protection
]

# Allauth settings
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_FORM_CLASS = 'users.forms.CustomLoginForm'

# Login and logout redirects
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Installed apps
INSTALLED_APPS = [
    # Custom apps
    'users',
    'core',
    'vehicles',
    'payments',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_celery_beat",
    'sslserver',
    'crispy_forms',
    'django_otp',
    'axes',
    'storages',

    # Django Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

# Middleware settings
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'axes.middleware.AxesMiddleware',
]

# URL configuration
ROOT_URLCONF = 'gestion_vehicules.urls'

# Template settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Template directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_vehicules.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='gestion_vehicules'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='P0liss3@@'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# PayPal configuration
PAYPAL_CLIENT_ID = env('PAYPAL_CLIENT_ID', default='VOTRE CLIENT ID')
PAYPAL_CLIENT_SECRET = env('PAYPAL_CLIENT_SECRET', default='VOTRE SECRET')
PAYPAL_MODE = env('PAYPAL_MODE', default='Sandbox')

# Password validation settings
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Security settings for production
SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# Timezone and language settings
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files settings
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Optional: Additional static files directories
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Ensure this directory exists
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),  # Make sure the log file directory exists
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Axes settings (for brute force protection)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCK_OUT_AT_FAILURE = True
AXES_BEHIND_REVERSE_PROXY = False

# SSL configuration (make sure the paths are correct)
SSL_CERTIFICATE = os.path.join(BASE_DIR, 'ssl', 'cert.crt')
SSL_KEY = os.path.join(BASE_DIR, 'ssl', 'private.key')
