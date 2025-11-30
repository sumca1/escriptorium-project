# app/escriptorium/settings_local.py
"""
🚀 Native Development Settings - No Docker!
Override settings.py for local Windows machine
"""
from .settings import *
import os

# =============================================================================
# DEVELOPMENT MODE
# =============================================================================
DEBUG = True
ALLOWED_HOSTS = ['*']

print("=" * 80)
print("✅ Using LOCAL DEVELOPMENT settings (Native - No Docker)")
print("=" * 80)

# =============================================================================
# DATABASE - PostgreSQL Local
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'escriptorium',
        'USER': 'escriptorium',
        'PASSWORD': 'escriptorium',
        'HOST': 'localhost',  # Not 'db'! Local PostgreSQL
        'PORT': '5432',
    }
}

# =============================================================================
# REDIS - Local (Memurai or WSL)
# =============================================================================
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# =============================================================================
# STATIC & MEDIA FILES
# =============================================================================
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# =============================================================================
# TESSERACT OCR - Windows Path
# =============================================================================
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Fallback paths if not in default location
if not os.path.exists(TESSERACT_CMD):
    # Try Program Files (x86)
    alt_path = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    if os.path.exists(alt_path):
        TESSERACT_CMD = alt_path
    else:
        # Try to find in PATH
        import shutil
        tesseract_in_path = shutil.which('tesseract')
        if tesseract_in_path:
            TESSERACT_CMD = tesseract_in_path
        else:
            print("⚠️  WARNING: Tesseract not found! Install from:")
            print("   https://github.com/UB-Mannheim/tesseract/wiki")

# =============================================================================
# KRAKEN MODELS
# =============================================================================
KRAKEN_MODELS_DIR = os.path.join(BASE_DIR, 'kraken_models')
os.makedirs(KRAKEN_MODELS_DIR, exist_ok=True)

# =============================================================================
# SECURITY - Disabled for Development
# =============================================================================
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# =============================================================================
# EMAIL - Console Backend for Development
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# LOGGING - More Verbose
# =============================================================================
LOGGING['loggers']['core']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['django.db.backends']['level'] = 'WARNING'  # SQL queries

# =============================================================================
# DEVELOPMENT TOOLS
# =============================================================================
# Django Debug Toolbar (if installed)
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
except ImportError:
    pass

# Django Extensions (if installed)
try:
    import django_extensions
    INSTALLED_APPS += ['django_extensions']
except ImportError:
    pass

# =============================================================================
# CORS - Allow all for development
# =============================================================================
if 'corsheaders' in INSTALLED_APPS:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# DEVELOPMENT SERVER SETTINGS
# =============================================================================
# Allow connections from Vue dev server
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',  # Vue dev server
    'http://localhost:8000',  # Django
    'http://127.0.0.1:5173',
    'http://127.0.0.1:8000',
]

print(f"📊 Database: PostgreSQL at {DATABASES['default']['HOST']}:{DATABASES['default']['PORT']}")
print(f"📡 Redis: {CELERY_BROKER_URL}")
print(f"🔧 Tesseract: {TESSERACT_CMD}")
print(f"📦 Kraken Models: {KRAKEN_MODELS_DIR}")
print("=" * 80)
