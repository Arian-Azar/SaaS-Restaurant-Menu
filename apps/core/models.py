"""
مدل‌های پایه و انتزاعی مشترک بین همه‌ی اپ‌های پروژه.

این ماژول قلب معماری Multi-Tenant است. هر مدل تجاری‌ای که متعلق به یک
رستوران خاص باشد (Category، Product، Order و ...) باید از TenantModel
ارث‌بری کند تا Tenant Isolation به‌صورت خودکار و بدون نیاز به فیلتر دستی
در هر View اعمال شود.
"""

from django.db import models

from .tenant import get_current_restaurant


class TimeStampedModel(models.Model):
    """کلاس پایه انتزاعی برای افزودن خودکار created_at/updated_at."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantAwareManager(models.Manager):
    """
    Manager پیش‌فرض برای مدل‌های وابسته به رستوران.

    اگر یک «رستوران جاری» از طریق TenantMiddleware ثبت شده باشد،
    QuerySet به‌صورت خودکار به همان رستوران محدود می‌شود؛ یعنی حتی اگر
    توسعه‌دهنده در یک View فراموش کند `.filter(restaurant=...)` بنویسد،
    نشتی داده بین رستوران‌ها اتفاق نمی‌افتد.

    اگر هیچ رستورانی ست نشده باشد (مثلاً در Django shell یا کانتکست
    Super Admin)، کل داده‌ها بدون محدودیت برگردانده می‌شود؛ محدودسازی در
    آن حالت باید صریح و آگاهانه انجام شود.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        restaurant = get_current_restaurant()
        if restaurant is not None:
            return qs.filter(restaurant=restaurant)
        return qs


class TenantModel(TimeStampedModel):
    """
    کلاس پایه انتزاعی برای هر مدلی که به یک رستوران خاص تعلق دارد.

    استفاده:
        class Category(TenantModel):
            name = models.CharField(max_length=100)

    دو Manager در دسترس است:
        - objects            : خودکار بر اساس رستوران جاری فیلتر می‌شود (پیش‌فرض، امن).
        - unscoped_objects    : بدون هیچ فیلتری؛ فقط برای اسکریپت‌های داخلی/
                                Super Admin که آگاهانه به همه‌ی داده‌ها نیاز دارند.
                                هرگز در Viewهای عمومی یا پنل رستوران‌دار استفاده نشود.
    """

    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
    )

    objects = TenantAwareManager()
    unscoped_objects = models.Manager()

    class Meta:
        abstract = True
