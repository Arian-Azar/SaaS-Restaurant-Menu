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


class Testimonial(TenantModel):
    """
    نظرات مشتریان (بخش «صفحه اصلی» تمپلیت — Testimonials).

    برخلاف تمپلیت اصلی که این نظرات ثابت/دمو بودند، اینجا هر صاحب رستوران
    از پنل مدیریت خودش نظرات واقعی مشتریانش را وارد می‌کند (مثلاً کپی از
    گوگل/اینستاگرام). این مدل هیچ فرم ثبت نظر عمومی برای مشتری ندارد —
    یعنی مشتری نمی‌تواند مستقیماً نظر ثبت کند؛ چون آن نیاز به یک فرآیند
    تعدیل (moderation) دارد که فعلاً خارج از محدوده است.
    """

    customer_name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text='امتیاز از ۱ تا ۵ (اختیاری).',
    )
    avatar = models.ImageField(upload_to='restaurants/testimonials/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return f'{self.customer_name} — {self.restaurant.name}'

    def save(self, *args, **kwargs):
        optimize_image_field(self.avatar, max_width=200, max_height=200)
        super().save(*args, **kwargs)


class RestaurantStat(TenantModel):
    """
    آمار/شمارنده‌های صفحه اصلی (بخش Counter تمپلیت: «۱۸ سال تجربه» و مشابه).

    برخلاف تمپلیت اصلی که این اعداد برای همه یکسان و ثابت بودند، اینجا هر
    رستوران آمار دلخواه خودش را تعریف می‌کند (مثلاً «۱۰ سال تجربه»،
    «۵۰۰+ مشتری راضی»). عمداً یک مدل عمومیِ (label, number) طراحی شده،
    نه فیلدهای ثابت (years_of_experience, staff_count, ...) روی خود
    Restaurant، چون این‌طوری هر رستوران می‌تواند هر تعداد و هر نوع آماری
    که برایش معنادار است اضافه کند، بدون نیاز به migration جدید.

    نکته: یکی از آمارهای رایج («تعداد غذاهای منو») نیازی به این مدل ندارد
    و مستقیماً و همیشه صحیح از طریق Product.objects.count() در View محاسبه
    می‌شود — پس دوباره اینجا وارد نمی‌شود تا داده تکراری/ناهماهنگ نشود.
    """

    label = models.CharField(max_length=100, help_text='مثلاً «سال‌های تجربه» یا «مشتری راضی»')
    number = models.PositiveIntegerField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.label}: {self.number} ({self.restaurant.name})'


class HeroSlide(TenantModel):
    """
    اسلاید اختصاصی هیرو (بخش بالای صفحه اصلی).

    این مدل عمداً از RestaurantImage (گالری) جداست، چون هدف و فیلدهای
    موردنیازش فرق دارد: هر اسلاید هیرو نیاز به یک عنوان بزرگ (title) و یک
    زیرعنوان کوچک (subtitle) دارد که مستقیم روی تصویر با فونت درشت نمایش
    داده می‌شود — چیزی که یک caption ساده‌ی گالری برایش طراحی نشده بود.
    جدا نگه‌داشتن این دو مدل یعنی صاحب رستوران می‌تواند گالری عمومی و
    اسلایدر هیرو را کاملاً مستقل از هم مدیریت کند.
    """

    image = models.ImageField(upload_to='restaurants/hero/')
    title = models.CharField(
        max_length=150,
        blank=True,
        help_text='عنوان بزرگ روی اسلاید؛ اگر خالی بماند، نام رستوران نمایش داده می‌شود.',
    )
    subtitle = models.CharField(
        max_length=100,
        blank=True,
        help_text='زیرعنوان کوچک (مثلاً یک شعار کوتاه).',
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return self.title or f'اسلاید هیرو {self.restaurant.name}'

    def save(self, *args, **kwargs):
        # ابعاد بزرگ‌تر از بقیه‌ی تصاویر چون این عکس تمام‌عرض/تمام‌صفحه نمایش داده می‌شود.
        optimize_image_field(self.image, max_width=1920, max_height=1080)
        super().save(*args, **kwargs)


class TeamMember(TenantModel):
    """
    عضو تیم/آشپز (بخش «Our Master Chef» تمپلیت).

    برخلاف تمپلیت اصلی که این افراد و عکس‌هایشان کاملاً دمو بودند، هر رستوران
    اعضای واقعی تیم خودش (سرآشپز، مدیر رستوران و ...) را از پنل مدیریت وارد می‌کند.
    """

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, help_text='مثلاً «سرآشپز» یا «مدیر رستوران»')
    photo = models.ImageField(upload_to='restaurants/team/', blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f'{self.name} ({self.position}) — {self.restaurant.name}'

    def save(self, *args, **kwargs):
        optimize_image_field(self.photo, max_width=500, max_height=500)
        super().save(*args, **kwargs)


class Reservation(TenantModel):
    """
    درخواست رزرو میز (بخش «Make Reservation» تمپلیت).

    برخلاف فرم دمو تمپلیت که هیچ‌کجا ذخیره نمی‌شد (action="#")، این فرم
    واقعاً در دیتابیس ذخیره می‌شود و صاحب رستوران آن را در پنل مدیریت
    (`/reservations/`) به‌عنوان یک درخواست ورودی می‌بیند و وضعیتش را
    مدیریت می‌کند. پرداخت/تأیید خودکار در این مرحله نیست — فقط ثبت درخواست.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'در انتظار بررسی'
        CONFIRMED = 'confirmed', 'تأیید شده'
        CANCELLED = 'cancelled', 'لغو شده'

    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    party_size = models.PositiveSmallIntegerField(default=2)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ['-reservation_date', '-reservation_time']

    def __str__(self):
        return f'{self.customer_name} — {self.reservation_date} ({self.restaurant.name})'


class BlogPost(TenantModel):
    """
    پست وبلاگ (بخش «Recent Posts» تمپلیت).

    نسخه‌ی حداقلی و واقعی: عنوان + عکس + متن. بدون سیستم نظرات یا
    دسته‌بندی وبلاگ — اگر در آینده نیاز واقعی به یک وبلاگ کامل‌تر بود،
    می‌تواند به‌عنوان یک فاز مجزا گسترش یابد.
    """

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='restaurants/blog/', blank=True, null=True)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return f'{self.title} — {self.restaurant.name}'

    def save(self, *args, **kwargs):
        optimize_image_field(self.image, max_width=1000, max_height=700)
        super().save(*args, **kwargs)
