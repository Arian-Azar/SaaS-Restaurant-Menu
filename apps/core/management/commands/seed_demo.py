"""
دستور مدیریتی برای ساخت داده‌ی نمونه‌ی کامل (Demo Seed).

هدف: بعد از هر تغییر فرانت‌اند، بتوانیم بدون وارد کردن دستی ده‌ها رکورد،
یک رستوران نمونه‌ی کامل (با اسلایدر هیرو، گالری، منو، آمار، نظرات) داشته
باشیم تا صفحه‌ی عمومی را واقعی و پر ببینیم.

نکات مهم:
- **Idempotent است**: اگر قبلاً اجرا شده باشد، ابتدا رستوران نمونه‌ی قبلی
  (و تمام داده‌های وابسته به آن، به‌خاطر CASCADE) حذف و از نو ساخته می‌شود.
  یعنی هر چند بار که `python manage.py seed_demo` را اجرا کنی، وضعیت
  یکسان و تمیزی می‌گیری، نه انباشت رکوردهای تکراری.
- **تصاویر واقعی نیستند** — چون فایل عکس واقعی نداریم، با Pillow تصاویر
  رنگی ساده (placeholder) با یک برچسب کوتاه لاتین/عددی روی هرکدام تولید
  می‌شود، فقط برای اینکه فیلدهای ImageField خالی نمانند و چیدمان صفحه
  قابل بررسی باشد. صاحب واقعی رستوران بعداً این‌ها را با عکس واقعی جایگزین می‌کند.

اجرا:
    python manage.py seed_demo
"""

import io

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw

from apps.menu.models import Category, Product
from apps.restaurants.models import (
    BlogPost,
    HeroSlide,
    Restaurant,
    RestaurantImage,
    RestaurantStat,
    TeamMember,
    Testimonial,
)

User = get_user_model()

DEMO_USERNAME = 'demo_owner'
DEMO_PASSWORD = 'DemoPass123!'
DEMO_RESTAURANT_NAME = 'رستوران و کافه آرامیس'


def make_placeholder_image(label: str, color: tuple, size=(800, 600)) -> ContentFile:
    """
    یک تصویر رنگی ساده با یک برچسب کوتاه (لاتین/عددی) می‌سازد.

    عمداً از متن فارسی روی تصویر استفاده نشده، چون رندر درست حروف فارسی
    (اتصال حروف + جهت راست‌به‌چپ) با Pillow نیاز به کتابخانه‌های اضافه‌ی
    شکل‌دهی متن (reshaping/bidi) دارد که خارج از هدف این اسکریپت placeholder‌ساز است.
    """
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    text = label
    # موقعیت تقریبی وسط تصویر (بدون نیاز به اندازه‌گیری دقیق فونت).
    draw.text((size[0] / 2 - len(text) * 5, size[1] / 2 - 10), text, fill=(255, 255, 255))
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    return ContentFile(buffer.read(), name=f'{label.replace(" ", "_")}.jpg')


class Command(BaseCommand):
    help = 'یک رستوران نمونه‌ی کامل با منو، اسلایدر، گالری، آمار و نظرات می‌سازد (idempotent).'

    @transaction.atomic
    def handle(self, *args, **options):
        # اگر از اجرای قبلی مانده، پاک‌سازی کامل (CASCADE همه‌چیز وابسته را هم پاک می‌کند).
        User.objects.filter(username=DEMO_USERNAME).delete()

        owner = User.objects.create_user(
            username=DEMO_USERNAME,
            password=DEMO_PASSWORD,
            email='demo@example.com',
            first_name='مالک نمونه',
            role=User.Role.RESTAURANT_OWNER,
        )

        restaurant = Restaurant.objects.create(
            owner=owner,
            name=DEMO_RESTAURANT_NAME,
            description=(
                'رستورانی با فضایی دنج و منویی متنوع از غذاهای ایرانی و بین‌المللی؛ '
                'جایی برای یک وعده‌ی غذایی آرام در کنار خانواده و دوستان.'
            ),
            phone='02188776655',
            address='تهران، خیابان ولیعصر، نرسیده به پارک ملت',
            instagram='aramis_restaurant',
            is_active=True,
        )
        restaurant.cover_image = make_placeholder_image('COVER', (60, 50, 45))
        restaurant.logo = make_placeholder_image('LOGO', (200, 160, 100))
        restaurant.save()

        # --- اسلایدر هیرو ---
        hero_data = [
            ('طعمی که یادت می‌ماند', 'خوش آمدید', (70, 55, 45)),
            ('غذاهای تازه، هرروز', 'منوی روز', (90, 40, 35)),
            ('فضایی دنج برای دورهمی', 'رستوران آرامیس', (45, 60, 55)),
        ]
        for i, (title, subtitle, color) in enumerate(hero_data):
            HeroSlide.objects.create(
                restaurant=restaurant,
                image=make_placeholder_image(f'HERO {i + 1}', color),
                title=title,
                subtitle=subtitle,
                sort_order=i,
                is_active=True,
            )

        # --- گالری ---
        gallery_data = [
            ('فضای داخلی', (120, 100, 80)),
            ('میز چیده‌شده', (100, 110, 90)),
            ('بار قهوه', (80, 70, 60)),
            ('حیاط رستوران', (70, 90, 70)),
        ]
        for i, (caption, color) in enumerate(gallery_data):
            RestaurantImage.objects.create(
                restaurant=restaurant,
                image=make_placeholder_image(f'GALLERY {i + 1}', color),
                caption=caption,
                sort_order=i,
            )

        # --- منو: دسته‌بندی و محصولات ---
        # آیتم چهارم تاپل یعنی discount_price، پنجمی یعنی is_featured
        # (برای بخش «غذاهای پیشنهادی» صفحه اصلی).
        menu_plan = {
            'پیش‌غذا': [
                ('سالاد سزار', 'کاهو، مرغ گریل‌شده، سس مخصوص و پارمزان', 145000, None, True),
                ('سوپ جو', 'سوپ سنتی با جو پرک و سبزیجات تازه', 95000, None, False),
            ],
            'غذای اصلی': [
                ('چلوکباب کوبیده', 'دو سیخ کباب کوبیده مخصوص با برنج ایرانی', 320000, 280000, True),
                ('استیک مرغ گریل', 'سینه مرغ گریل‌شده با سبزیجات بخارپز', 280000, None, False),
                ('پیتزا مخصوص آرامیس', 'پپرونی، قارچ، فلفل دلمه و پنیر موزارلا', 250000, 220000, True),
            ],
            'دسر': [
                ('تیرامیسو', 'دسر ایتالیایی با قهوه و ماسکارپونه', 150000, None, True),
            ],
            'نوشیدنی': [
                ('اسپرسو', 'قهوه غلیظ ایتالیایی', 90000, None, False),
                ('آب‌میوه طبیعی', 'پرتقال یا هویج تازه', 85000, None, False),
            ],
        }

        product_colors = [
            (150, 90, 60), (90, 130, 100), (170, 130, 70),
            (110, 90, 140), (60, 110, 130), (140, 70, 90),
            (100, 100, 60), (80, 140, 140),
        ]
        color_index = 0

        for cat_index, (cat_name, products) in enumerate(menu_plan.items()):
            category = Category.objects.create(
                restaurant=restaurant,
                name=cat_name,
                sort_order=cat_index,
                is_active=True,
            )
            for prod_index, (name, desc, price, discount, featured) in enumerate(products):
                Product.objects.create(
                    restaurant=restaurant,
                    category=category,
                    name=name,
                    description=desc,
                    price=price,
                    discount_price=discount,
                    image=make_placeholder_image(name[:12], product_colors[color_index % len(product_colors)]),
                    is_available=True,
                    is_featured=featured,
                    sort_order=prod_index,
                )
                color_index += 1

        # --- آمار صفحه اصلی ---
        RestaurantStat.objects.create(restaurant=restaurant, label='سال‌های تجربه', number=8, sort_order=0)
        RestaurantStat.objects.create(restaurant=restaurant, label='مشتری راضی', number=1200, sort_order=1)
        RestaurantStat.objects.create(restaurant=restaurant, label='جایزه کیفیت', number=3, sort_order=2)

        # --- نظرات مشتریان ---
        testimonials_data = [
            ('سارا محمدی', 'کیفیت غذا و برخورد کارکنان فوق‌العاده بود، حتماً دوباره میایم.', 5),
            ('علی رضایی', 'فضای دنجی داره و غذاها خیلی تازه بودن.', 5),
            ('مریم کریمی', 'قیمت‌ها منصفانه بود و کباب کوبیده‌شون عالی بود.', 4),
        ]
        for i, (customer_name, comment, rating) in enumerate(testimonials_data):
            Testimonial.objects.create(
                restaurant=restaurant,
                customer_name=customer_name,
                comment=comment,
                rating=rating,
                is_active=True,
                sort_order=i,
            )

        # --- تیم / آشپزها ---
        team_data = [
            ('رضا احمدی', 'سرآشپز', (110, 80, 60)),
            ('نگار حسینی', 'مدیر رستوران', (90, 100, 120)),
            ('کیان مرادی', 'دستیار آشپز', (100, 70, 90)),
        ]
        for i, (name, position, color) in enumerate(team_data):
            TeamMember.objects.create(
                restaurant=restaurant,
                name=name,
                position=position,
                photo=make_placeholder_image(f'TEAM {i + 1}', color),
                is_active=True,
                sort_order=i,
            )

        # --- وبلاگ ---
        blog_data = [
            ('راز طعم کباب کوبیده خانگی', 'کباب کوبیده خوب با نسبت درست گوشت و پیاز و کمی صبر روی زغال به دست می‌آید...'),
            ('چرا صبحانه ایرانی بهترین شروع روز است', 'صبحانه‌ی سنتی ایرانی با نان تازه، پنیر و گردو، انرژی روز شما را تأمین می‌کند...'),
        ]
        for i, (title, content) in enumerate(blog_data):
            BlogPost.objects.create(
                restaurant=restaurant,
                title=title,
                content=content,
                image=make_placeholder_image(f'BLOG {i + 1}', (80, 90, 70)),
                is_published=True,
            )

        self.stdout.write(self.style.SUCCESS('✅ داده‌ی نمونه با موفقیت ساخته شد.'))
        self.stdout.write('')
        self.stdout.write(f'   نام کاربری ورود به پنل: {DEMO_USERNAME}')
        self.stdout.write(f'   رمز عبور:               {DEMO_PASSWORD}')
        self.stdout.write(f'   لینک صفحه عمومی:        /{restaurant.slug}/')
