"""
تنظیمات محیط توسعه (Development).

اجرا با:
    DJANGO_SETTINGS_MODULE=config.settings.development python manage.py runserver
یا با تنظیم متغیر در فایل .env (پیشنهادی، پایین‌تر توضیح داده شده).
"""

from .base import *  # noqa

DEBUG = True

# در dev اجازه می‌دهیم از هر هاستی سرو شود تا تست روی موبایل/شبکه محلی راحت باشد.
ALLOWED_HOSTS = ['*']

# ایمیل در dev فقط در کنسول چاپ می‌شود، ارسال واقعی انجام نمی‌شود.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# نمایش خطاهای دقیق‌تر برای دیباگ
INTERNAL_IPS = ['127.0.0.1']
