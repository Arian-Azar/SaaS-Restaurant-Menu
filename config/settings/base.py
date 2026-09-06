"""
Django base settings for Restaurant SaaS Platform.

این فایل تنظیمات مشترک بین همه محیط‌ها (dev/prod) است.
تنظیمات خاص هر محیط در development.py و production.py قرار دارد.
"""

from pathlib import Path
from decouple import config, Csv

# BASE_DIR باید به ریشه‌ی پروژه (جایی که manage.py هست) اشاره کند.
# مسیر این فایل: config/settings/base.py -> سه پله بالا برو تا ریشه پروژه.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# -----------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-env-file')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


# -----------------------------------------------------------------------
# Applications
# -----------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
]

# اپ‌های اختصاصی پروژه؛ ترتیب مهم است چون accounts باید قبل از باقی apps
# لود شود (User Model سفارشی به آن وابسته است).
LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.restaurants',
    'apps.menu',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# -----------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.TenantMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'


# -----------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # قالب‌های سراسری پروژه (نه مخصوص یک اپ) اینجا قرار می‌گیرند.
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# -----------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------
# فاز فعلی: SQLite (ساده، بدون نیاز به سرویس جداگانه).
# فازهای بعدی: مهاجرت به PostgreSQL فقط با تغییر این بخش (یا متغیرهای .env)
# انجام می‌شود؛ کد اپلیکیشن نیازی به تغییر ندارد چون از Django ORM استفاده می‌شود.
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
    }
}


# -----------------------------------------------------------------------
# Custom User Model
# -----------------------------------------------------------------------
# در بخش ۲ مدل User ساخته شد؛ این خط اکنون فعال است.
AUTH_USER_MODEL = 'accounts.User'


# -----------------------------------------------------------------------
# Password validation
# -----------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -----------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------
LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True


# -----------------------------------------------------------------------
# Static & Media files
# -----------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# -----------------------------------------------------------------------
# Django REST Framework (پیکربندی پایه؛ در فازهای بعدی توسعه می‌یابد)
# -----------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -----------------------------------------------------------------------
# Authentication redirects
# -----------------------------------------------------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
