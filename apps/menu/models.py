"""
مدل‌های منو: Category و Product.

هر دو از apps.core.models.TenantModel ارث‌بری می‌کنند، پس به‌صورت خودکار:
    - فیلد restaurant (ForeignKey) دارند
    - فیلدهای created_at / updated_at دارند
    - manager پیش‌فرض‌شان (`objects`) خودکار بر اساس رستوران جاری فیلتر می‌شود
      (به core/models.py و core/tenant.py در بخش ۲ مراجعه کن)

یعنی این مدل‌ها اولین جایی هستند که واقعاً معماری Tenant Isolation ساخته‌شده
در بخش ۲ را عملاً استفاده می‌کنند.
"""

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.imaging import optimize_image_field
from apps.core.models import TenantModel


class Category(TenantModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='menu/categories/', blank=True, null=True)
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text='ترتیب نمایش دسته‌بندی در منو؛ عدد کوچک‌تر زودتر نمایش داده می‌شود.',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        # دو رستوران می‌توانند دسته‌بندی هم‌نام داشته باشند (مثلاً هر دو "پیتزا")
        # اما یک رستوران نمی‌تواند دو دسته‌بندی با نام یکسان داشته باشد.
        constraints = [
            models.UniqueConstraint(
                fields=['restaurant', 'name'],
                name='unique_category_name_per_restaurant',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.restaurant.name})'

    def save(self, *args, **kwargs):
        optimize_image_field(self.image, max_width=800, max_height=800)
        super().save(*args, **kwargs)


class Product(TenantModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
        help_text='در صورت وجود، قیمت بعد از تخفیف. باید کمتر از price باشد.',
    )
    image = models.ImageField(upload_to='menu/products/', blank=True, null=True)
    is_available = models.BooleanField(
        default=True,
        help_text='اگر غیرفعال شود، محصول در منوی عمومی نمایش داده نمی‌شود (مثلاً تمام‌شده).',
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.name} ({self.restaurant.name})'

    def clean(self):
        # نکته امنیتی/صحت داده مهم: دسته‌بندی انتخاب‌شده باید متعلق به همان
        # رستوانِ محصول باشد؛ وگرنه یک رستوران می‌تواند محصولش را زیر
        # دسته‌بندیِ رستوران دیگر ثبت کند که هم منطقاً غلط است و هم یک نوع
        # نشتی داده بین Tenantها محسوب می‌شود.
        if self.category_id and self.restaurant_id and self.category.restaurant_id != self.restaurant_id:
            raise ValidationError(
                {'category': 'دسته‌بندی انتخاب‌شده متعلق به رستوران دیگری است.'}
            )

        if self.discount_price is not None and self.price is not None and self.discount_price >= self.price:
            raise ValidationError(
                {'discount_price': 'قیمت تخفیف‌خورده باید کمتر از قیمت اصلی باشد.'}
            )

    def save(self, *args, **kwargs):
        optimize_image_field(self.image, max_width=1000, max_height=1000)
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        """قیمت نهایی برای نمایش: قیمت تخفیف‌خورده اگر تنظیم شده باشد، وگرنه قیمت اصلی."""
        return self.discount_price if self.discount_price is not None else self.price
