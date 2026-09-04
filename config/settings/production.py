"""
تنظیمات محیط Production.

این فایل فعلاً یک اسکلت اولیه است؛ در فازهای بعدی (مهاجرت به PostgreSQL،
افزودن Redis/Celery، دامنه واقعی) تکمیل خواهد شد.
"""

from .base import *  # noqa
from decouple import config, Csv

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# در Production حتماً باید HTTPS باشد.
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# نکته فاز بعدی: اینجا DATABASES باید به PostgreSQL سوییچ شود
# (از طریق متغیرهای DB_ENGINE / DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT در .env)
