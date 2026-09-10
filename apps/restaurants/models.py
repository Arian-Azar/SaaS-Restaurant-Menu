"""
مدل Restaurant — هسته‌ی اصلی Multi-Tenancy.

نکته طراحی مهم: Restaurant خودش TenantModel نیست (چون خودش «مستأجر/Tenant»
است، نه داده‌ی متعلق به یک مستأجر). مدل‌های بعدی مثل Category و Product
(در بخش ۳) هستند که از core.models.TenantModel ارث‌بری می‌کنند و
restaurant = ForeignKey خودکار می‌گیرند.

تصمیم فعلی: هر User حداکثر یک Restaurant دارد (OneToOneField).
این یک ساده‌سازی آگاهانه برای MVP است؛ اگر در فاز ۶ (چند شعبه) نیاز شد که
یک مالک چند رستوران داشته باشد، این رابطه به ForeignKey تغییر می‌کند —
تغییری که در آن زمان باید با migration و بازبینی همه‌ی جاهایی که از
`request.user.restaurant` استفاده می‌کنند همراه باشد.
"""

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.core.imaging import optimize_image_field
from apps.core.models import TenantModel, TimeStampedModel


class Restaurant(TimeStampedModel):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurant',
    )

    name = models.CharField(max_length=150)
    slug = models.SlugField(
        max_length=170,
        unique=True,
        blank=True,
        allow_unicode=True,
        help_text='بخش اختصاصی URL؛ در صورت خالی گذاشتن، خودکار از روی نام ساخته می‌شود.',
    )

    logo = models.ImageField(upload_to='restaurants/logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='restaurants/covers/', blank=True, null=True)
    description = models.TextField(blank=True)

    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    is_active = models.BooleanField(
        default=True,
        help_text='اگر غیرفعال شود، صفحه عمومی رستوران و منو در دسترس نخواهد بود.',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()

        # بهینه‌سازی تصاویر (فاز ۲ / بخش ۵): لوگو معمولاً مربعی و کوچک است،
        # کاور یک بنر عریض‌تر — پس اندازه‌ی هدف هرکدام متفاوت است.
        optimize_image_field(self.logo, max_width=400, max_height=400)
        optimize_image_field(self.cover_image, max_width=1200, max_height=500)

        super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.name, allow_unicode=True) or 'restaurant'
        slug = base_slug
        counter = 1
        # تضمین یکتا بودن slug حتی اگر دو رستوران نام مشابه داشته باشند.
        while Restaurant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            counter += 1
            slug = f'{base_slug}-{counter}'
        return slug


class RestaurantImage(TenantModel):
    """
    گالری تصاویر رستوران (فاز ۲ / بخش ۱).

    برخلاف logo/cover_image که تک‌فیلد روی خود Restaurant هستند، اینجا هر
    رستوران می‌تواند چند تصویر داشته باشد (مثلاً فضای داخلی، میزها، غذاهای
    آماده). چون این مدل ذاتاً «متعلق به یک رستوران» است، از TenantModel
    ارث‌بری می‌کند تا همان محافظت Tenant Isolation بخش ۲ را خودکار داشته باشد.
    """

    image = models.ImageField(upload_to='restaurants/gallery/')
    caption = models.CharField(max_length=150, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return self.caption or f'تصویر گالری {self.restaurant.name}'

    def save(self, *args, **kwargs):
        optimize_image_field(self.image, max_width=1200, max_height=1200)
        super().save(*args, **kwargs)
