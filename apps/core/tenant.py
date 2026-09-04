"""
Context جاری برای Tenant (رستوران).

از contextvars استفاده می‌کنیم (نه یک متغیر global ساده) چون در محیط async
یا چند-ریسمانی امن است و هر request کانتکست جدا و ایزوله‌ی خودش را دارد.

نحوه کارکرد:
    ۱. TenantMiddleware در ابتدای هر request، رستورانِ کاربر لاگین‌شده را
       با set_current_restaurant() ثبت می‌کند.
    ۲. TenantAwareManager (در core/models.py) موقع ساخت QuerySet،
       با get_current_restaurant() رستوران جاری را می‌خواند و queryset را
       بر همان اساس فیلتر می‌کند.
    ۳. در پایان request، TenantMiddleware با clear_current_restaurant()
       کانتکست را پاک می‌کند تا بین request های مختلف نشتی نداشته باشیم.

نکته امنیتی مهم:
    اگر رستوران جاری تنظیم نشده باشد (مثلاً در shell، مدیریت Super Admin،
    یا اسکریپت‌های داخلی)، TenantAwareManager هیچ فیلتری اعمال نمی‌کند و
    کل داده‌ها را برمی‌گرداند. این عمدی است، اما یعنی هر View که باید
    محدود به یک رستوران باشد، باید مطمئن شود کاربر لاگین است و
    TenantMiddleware به‌درستی رستوران را ست کرده — در غیر این صورت باید
    صراحتاً با .filter(restaurant=...) کار کند.
"""

from contextvars import ContextVar

_current_restaurant: ContextVar = ContextVar('current_restaurant', default=None)


def set_current_restaurant(restaurant) -> None:
    """رستوران جاری را برای این request/context ثبت می‌کند."""
    _current_restaurant.set(restaurant)


def get_current_restaurant():
    """رستوران جاری را برمی‌گرداند؛ اگر ست نشده باشد None است."""
    return _current_restaurant.get()


def clear_current_restaurant() -> None:
    """کانتکست را پاک می‌کند (باید حتماً در انتهای هر request صدا زده شود)."""
    _current_restaurant.set(None)
