"""
مدل User سفارشی.

از همان ابتدا (به‌جای استفاده مستقیم از User پیش‌فرض جنگو) یک User سفارشی
تعریف می‌کنیم، چون تغییر بعدیِ AUTH_USER_MODEL بعد از وجود داده‌ی واقعی در
دیتابیس بسیار پرهزینه و در عمل تقریباً غیرممکن است.

فعلاً فقط دو نقش داریم:
    - SUPER_ADMIN       : مدیر کل پلتفرم (از is_superuser/is_staff هم استفاده می‌شود)
    - RESTAURANT_OWNER   : مالک یک رستوران

نقش‌های بیشتر (مثلاً STAFF یا MANAGER برای کارمندان یک رستوران) در فازهای
بعدی (فاز ۶ - چند شعبه/چند کاربر) به همین Enum اضافه خواهند شد.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'مدیر کل پلتفرم'
        RESTAURANT_OWNER = 'restaurant_owner', 'صاحب رستوران'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESTAURANT_OWNER,
        help_text='نقش کاربر در سیستم. مدیر کل پلتفرم معمولاً is_superuser=True نیز هست.',
    )
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_restaurant_owner(self) -> bool:
        return self.role == self.Role.RESTAURANT_OWNER
