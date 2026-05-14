"""
Django settings for backend_project project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Load .env from project root (optional; env vars can also be set in the shell)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass  # python-dotenv not installed; use system env only

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-change-this-in-production'
)

# Render sets RENDER=true; default DEBUG off there unless DJANGO_DEBUG overrides.
_RENDER = os.environ.get('RENDER', '').lower() in ('true', '1', 'yes')
_default_debug = 'false' if _RENDER else 'true'
DEBUG = os.environ.get('DJANGO_DEBUG', _default_debug).lower() in ('true', '1', 'yes')

# Hosts: env ALLOWED_HOSTS (comma-separated) plus sensible defaults (no duplicate block later).
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
for _h in ('localhost', '127.0.0.1', '0.0.0.0', 'cox-solution.onrender.com'):
    if _h not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_h)
if DEBUG and '0.0.0.0' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('0.0.0.0')

# Frontend URL for CORS and CSRF (comma-separated for multiple origins)
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000').strip()
FRONTEND_ORIGINS = [o.strip() for o in FRONTEND_URL.split(',') if o.strip()]
if not FRONTEND_ORIGINS:
    FRONTEND_ORIGINS = ['http://localhost:3000']  # fallback so CORS works in dev

# Application definition (manage.py is the CLI script for runserver/migrate etc.; it is not an app and is not listed here)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',  # Token auth for REST API (use with TokenAuthentication)
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'backend_project.middleware.DisableCSRFForAPI',  # avoid 403/Network Error for /api/
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend_project.wsgi.application'

# Database: DATABASE_URL (Render Postgres, etc.) > MySQL (USE_SQLITE=false) > SQLite
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
_database_url = os.environ.get('DATABASE_URL', '').strip()
_use_sqlite = os.environ.get('USE_SQLITE', 'True').lower() in ('true', '1', 'yes')

if _database_url:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600),
    }
elif not _use_sqlite:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE', 'backend_db'),
            'USER': os.environ.get('MYSQL_USER', 'root'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
            'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (for uploaded images/files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# CORS: dev defaults + FRONTEND_URL (comma-separated) + CORS_EXTRA_ORIGINS
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5173',
    'http://localhost:5173',
    'http://127.0.0.1:5174',
    'http://localhost:5174',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://cox-solution-admin.vercel.app',
]
for _origin in FRONTEND_ORIGINS:
    if _origin and _origin not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(_origin)
for _origin in os.environ.get('CORS_EXTRA_ORIGINS', '').split(','):
    _origin = _origin.strip()
    if _origin and _origin not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(_origin)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # allow any origin in dev to avoid Network Error
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "x-csrftoken",
    "x-requested-with",
]

# CSRF: trust frontend origins (must be full URL with scheme; include HTTPS prod)
CSRF_TRUSTED_ORIGINS = list(CORS_ALLOWED_ORIGINS)

# Behind Render / reverse proxy HTTPS
if _RENDER:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True

# API base URL (for frontend .env: REACT_APP_API_URL or VITE_API_URL etc.)
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000').strip()

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
