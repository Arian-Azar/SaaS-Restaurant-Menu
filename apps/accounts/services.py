"""
سرویس ثبت‌نام رستوران.

منطق «اتمیک بودنِ» ساخت User + Restaurant عمداً از View جدا شده و اینجا
قرار گرفته، به دو دلیل:
    ۱. قابل تست مستقل بدون نیاز به شبیه‌سازی HTTP request
    ۲. در آینده اگر بخواهیم از جای دیگری (مثلاً API موبایل یا مدیریت دستی
       توسط Super Admin) کاربر جدید بسازیم، همین تابع دوباره استفاده می‌شود.
"""

from django.db import transaction

from apps.restaurants.models import Restaurant

from .models import User


def register_restaurant_owner(
    *,
    username: str,
    password: str,
    restaurant_name: str,
    email: str = '',
    phone_number: str = '',
    full_name: str = '',
) -> tuple[User, Restaurant]:
    """
    یک صاحب رستوران جدید به همراه رستوران خودش می‌سازد.

    نکته مهم: کل عملیات داخل transaction.atomic() است. یعنی اگر بعد از
    ساخت User، ساخت Restaurant با هر دلیلی (خطای پایگاه‌داده، Validation و...)
    شکست بخورد، User ساخته‌شده هم Rollback می‌شود — پس هرگز کاربری بدون
    رستوران در سیستم باقی نمی‌ماند (طبق نمودار فرآیند ثبت‌نام در پروپوزال).
    """
    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name,
            phone_number=phone_number,
            role=User.Role.RESTAURANT_OWNER,
        )
        restaurant = Restaurant.objects.create(owner=user, name=restaurant_name)

    return user, restaurant
