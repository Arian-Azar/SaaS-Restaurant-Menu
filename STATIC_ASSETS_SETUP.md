# راهنمای قرار دادن فایل‌های استاتیک تمپلیت (Feliciano / Colorlib)

این پروژه از تمپلیت شما (Bootstrap 4 + jQuery + Owl Carousel + AOS و...) برای
صفحات عمومی مشتری (`/<slug>/` و `/<slug>/products/<pk>/`) استفاده می‌کند.
پنل مدیریت و بخش‌های دیگر پروژه با استایل خودشان (که در فازهای قبل ساختیم) باقی مانده‌اند.

## کجا فایل‌ها را بگذارم؟

فایل‌های اصلی تمپلیت شما (که خودتان دارید) را **دقیقاً با همان ساختار پوشه‌ای که
در پکیج اصلی تمپلیت بود** (یعنی پوشه‌های `css/`, `js/`, `fonts/`, `images/` کنار هم)
داخل مسیر زیر در پروژه کپی کنید:

```
restaurant_saas/
└── static/
    └── menu_theme/          ← این پوشه را از قبل ساخته‌ایم
        ├── css/
        │   ├── style.css                         ← از تمپلیت شما
        │   ├── animate.css                        ← از تمپلیت شما
        │   ├── owl.carousel.min.css               ← از تمپلیت شما
        │   ├── owl.theme.default.min.css          ← از تمپلیت شما
        │   ├── magnific-popup.css                 ← از تمپلیت شما
        │   ├── aos.css                             ← از تمپلیت شما
        │   ├── ionicons.min.css                   ← از تمپلیت شما
        │   ├── bootstrap-datepicker.css           ← از تمپلیت شما
        │   ├── jquery.timepicker.css              ← از تمپلیت شما
        │   ├── flaticon.css                        ← از تمپلیت شما
        │   ├── icomoon.css                         ← از تمپلیت شما
        │   └── rtl-fix.css                         ← ⚠️ همین الان توسط من ساخته و اینجا گذاشته شده، از قبل موجود است
        │
        ├── js/
        │   ├── jquery.min.js                       ← از تمپلیت شما
        │   ├── jquery-migrate-3.0.1.min.js
        │   ├── popper.min.js
        │   ├── bootstrap.min.js
        │   ├── jquery.easing.1.3.js
        │   ├── jquery.waypoints.min.js
        │   ├── jquery.stellar.min.js
        │   ├── owl.carousel.min.js
        │   ├── jquery.magnific-popup.min.js
        │   ├── aos.js
        │   ├── jquery.animateNumber.min.js
        │   ├── bootstrap-datepicker.js
        │   ├── jquery.timepicker.min.js
        │   ├── scrollax.min.js
        │   └── main.js                             ← از تمپلیت شما (بدون تغییر)
        │
        ├── fonts/                                  ← کل پوشه fonts تمپلیت (icomoon, flaticon,
        │                                              ionicons, open-iconic) را همین‌طور که هست کپی کنید
        │
        └── images/                                 ← کل پوشه images تمپلیت را کپی کنید
```

## نکته‌ی مهم فنی (چرا دقیقاً همین چیدمان؟)

فایل‌های CSS مثل `icomoon.css` و `flaticon.css` داخل خودشان به فونت‌ها با مسیر
نسبی (`url(../fonts/...)`) اشاره می‌کنند. تا وقتی که پوشه‌های `css/` و `fonts/`
**درست کنار هم** و با همین اسم باشند (دقیقاً مثل پکیج اصلی تمپلیت)، مرورگر
خودش این مسیرهای نسبی را درست پیدا می‌کند — نیازی به تغییر چیزی داخل خود
فایل‌های CSS تمپلیت نیست.

## چیزی که عمداً اضافه/حذف شده

1. **`rtl-fix.css`** — فایلی که من نوشته‌ام و از قبل در `static/menu_theme/css/`
   قرار دارد. چون تمپلیت اصلی LTR است، این فایل کلاس‌های جهت‌دار Bootstrap
   (`mr-`, `ml-`, `pr-`, `pl-`, `text-right`, `text-left`, `float-*` و...) را
   برای نمایش درست محتوای فارسی به RTL برمی‌گرداند. این فایل باید **آخرین**
   `<link>` در `<head>` باشد (همین‌طور در `templates/public_base.html` تنظیم شده).

2. **Google Maps API و `google-map.js`** — عمداً include نشده‌اند، چون صفحه‌ی
   منو نقشه‌ای ندارد و اسکریپت Maps نیاز به یک API Key واقعی دارد که نباید
   کلید تمپلیت دمو استفاده شود.

## بعد از کپی کردن فایل‌ها

```bash
python manage.py collectstatic   # فقط لازم است در Production
python manage.py runserver       # در توسعه، فایل‌های static/ مستقیم سرو می‌شوند
```

سپس صفحه‌ی `/<اسلاگ رستوران>/` را باز کنید — باید دقیقاً با ظاهر تمپلیت
(رنگ طلایی، فونت Poppins، تب‌های دسته‌بندی، چیدمان زیگزاگ آیتم‌های منو) نمایش
داده شود، ولی این‌بار با محتوای واقعی و پویای رستوران‌های ثبت‌شده در سیستم.
