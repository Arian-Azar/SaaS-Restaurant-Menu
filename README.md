# Restaurant SaaS Platform

پلتفرم SaaS چندمستأجری برای منوی دیجیتال و وب‌سایت رستوران‌ها.
مرجع کامل معماری در فایل `PROJECT_CONTEXT.md` (در چت اصلی پروژه نگهداری می‌شود).

## اجرای پروژه (فاز ۱ / بخش ۱)

```bash
# ۱. ساخت محیط مجازی
python3 -m venv venv
source venv/bin/activate      # ویندوز: venv\Scripts\activate

# ۲. نصب وابستگی‌ها
pip install -r requirements.txt

# ۳. ساخت فایل .env از روی نمونه
cp .env.example .env

# ۴. اجرای migrations
python manage.py migrate

# ۵. ساخت سوپریوزر (برای دسترسی به /admin/)
python manage.py createsuperuser

# ۶. اجرای سرور
python manage.py runserver
```

سپس به آدرس زیر بروید:
- پنل ادمین: http://127.0.0.1:8000/admin/

## ساختار پروژه

```
restaurant_saas/
├── config/
│   ├── settings/
│   │   ├── base.py           # تنظیمات مشترک
│   │   ├── development.py    # تنظیمات dev (فعلاً پیش‌فرض manage.py)
│   │   └── production.py     # تنظیمات production (اسکلت اولیه)
│   ├── urls.py
│   ├── wsgi.py                # پیش‌فرض: production settings
│   └── asgi.py                # پیش‌فرض: production settings
│
├── apps/
│   ├── core/                  # ابزارهای مشترک (TenantAwareManager و ...) — بخش ۲
│   ├── accounts/              # User سفارشی — بخش ۲
│   ├── restaurants/           # مدل Restaurant، ثبت‌نام، پنل — بخش‌های ۲ و ۴ و ۵
│   └── menu/                  # Category, Product — بخش ۳
│
├── templates/                 # قالب‌های سراسری
├── static/                    # فایل‌های استاتیک سراسری (CSS/JS مشترک)
├── media/                     # فایل‌های آپلودی کاربران (لوگو، تصاویر محصول)
│
├── .env.example                # نمونه متغیرهای محیطی
├── requirements.txt
└── manage.py
```

## وضعیت فعلی

### بخش ۱ — راه‌اندازی پروژه و زیرساخت ✅
- [x] ساختار Modular پروژه (`config` + `apps.*`)
- [x] پیکربندی مبتنی بر environment variable (`python-decouple`)
- [x] جداسازی settings برای dev/production
- [x] پایگاه‌داده: SQLite (فعلاً — مهاجرت به PostgreSQL در فازهای بعدی بدون تغییر کد اپلیکیشن)
- [x] Django REST Framework نصب و در `INSTALLED_APPS` فعال شد

### بخش ۲ — مدل‌های هسته + Tenant Isolation ✅
- [x] مدل `User` سفارشی (`apps/accounts`) با فیلد `role` (SUPER_ADMIN / RESTAURANT_OWNER)
- [x] `AUTH_USER_MODEL = 'accounts.User'` فعال شد
- [x] مدل `Restaurant` (`apps/restaurants`) با تولید خودکار و یکتای slug
- [x] `apps/core/tenant.py` — کانتکست جاری رستوران با `contextvars`
- [x] `apps/core/models.py` — `TimeStampedModel`, `TenantAwareManager`, `TenantModel` انتزاعی
- [x] `apps/core/middleware.py` — `TenantMiddleware` (رستوران کاربر لاگین‌شده را خودکار ست می‌کند)
- [x] ثبت `User` و `Restaurant` در Django Admin (فقط برای Super Admin)
- [x] تست‌های واحد برای Middleware (`apps/core/tests.py`) — همه سبز

### نحوه‌ی کار Tenant Isolation (خلاصه)

```
درخواست HTTP
     │
     ▼
AuthenticationMiddleware   (request.user را ست می‌کند)
     │
     ▼
TenantMiddleware           (اگر user رستوران دارد و Super Admin نیست،
     │                      set_current_restaurant(user.restaurant))
     ▼
View / Serializer
     │
     ▼
Model.objects.all()   ← TenantAwareManager خودکار .filter(restaurant=...) می‌زند
     │
     ▼
پاسخ برگردانده می‌شود
     │
     ▼
TenantMiddleware           clear_current_restaurant()  ← پاکسازی کانتکست
```

هر مدلی که در آینده (Category، Product، Order، ...) از `apps.core.models.TenantModel`
ارث‌بری کند، به‌صورت خودکار همین محافظت را دارد — بدون نیاز به نوشتن
`.filter(restaurant=...)` در هر View.

⚠️ **نکته مهم برای فازهای بعدی:** `unscoped_objects` (Manager بدون فیلتر) فقط
باید در اسکریپت‌های داخلی یا پنل Super Admin استفاده شود، هرگز در Viewهای
عمومی یا پنل رستوران‌دار.

### بخش ۳ — منو (Category + Product) ✅
- [x] مدل `Category` (`apps/menu`) — ارث‌بری از `TenantModel`، با `UniqueConstraint` روی `(restaurant, name)`
- [x] مدل `Product` — ارث‌بری از `TenantModel`، با اعتبارسنجی:
      - `category` باید متعلق به همان `restaurant` محصول باشد (جلوگیری از نشتی داده بین Tenantها)
      - `discount_price` باید کمتر از `price` باشد
- [x] property `final_price` روی Product (برای نمایش ساده در صفحه عمومی/فازهای بعد)
- [x] ثبت در Django Admin با Inline (محصولات هر دسته‌بندی داخل صفحه‌ی همان دسته‌بندی)
- [x] ۸ تست واحد که **با داده‌ی واقعی** ثابت می‌کنند Tenant Isolation کار می‌کند:
      رستوران A هرگز دسته‌بندی/محصول رستوران B را از طریق `Category.objects` / `Product.objects` نمی‌بیند.

### نتیجه تست‌های کل پروژه تا این مرحله

```
Ran 11 tests in ~9s
OK
```
(۳ تست بخش ۲ برای Middleware + ۸ تست بخش ۳ برای Category/Product)

### بخش ۴ — ثبت‌نام و احراز هویت ✅
- [x] `apps/accounts/services.py::register_restaurant_owner()` — ساخت اتمیک User + Restaurant
      (اگر ساخت Restaurant fail شود، User هم Rollback می‌شود — تست شده با mock)
- [x] فرم ترکیبی ثبت‌نام (`RestaurantRegistrationForm`): نام کاربری تکراری، تطابق رمز عبور،
      قوانین استاندارد قدرت رمز عبور (از `AUTH_PASSWORD_VALIDATORS`)
- [x] `RestaurantRegisterView` — بعد از ثبت‌نام موفق، کاربر خودکار لاگین می‌شود
- [x] `RestaurantOwnerLoginView` / `RestaurantOwnerLogoutView` (بر پایه‌ی LoginView/LogoutView جنگو)
- [x] `LOGIN_URL` / `LOGIN_REDIRECT_URL` / `LOGOUT_REDIRECT_URL` تنظیم شد
- [x] پنل داشبورد Placeholder (`apps/restaurants/views.py::dashboard`) — نسخه‌ی کامل در بخش ۵
- [x] قالب‌های HTML پایه (RTL) برای register/login/dashboard در `templates/`
- [x] ۱۲ تست جدید (اتمیک بودن سرویس، فرم، جریان کامل HTTP، و Tenant Isolation
      این‌بار از طریق یک session لاگین‌شده‌ی واقعی نه فقط RequestFactory)

### نتیجه تست‌های کل پروژه تا این مرحله

```
Ran 23 tests in ~15s
OK
```

### نکته مهم درباره Logout

از Django نسخه ۴.۱ به بعد، `LogoutView` فقط درخواست `POST` را قبول می‌کند
(به دلایل امنیتی در برابر CSRF از طریق لینک). به همین دلیل دکمه‌ی خروج در
`templates/base.html` یک فرم با `method="post"` است، نه یک لینک ساده — این
یک نکته‌ی رایج است که در پروژه‌های جدیدتر جنگو باید حواس‌مان باشد.

### بخش ۵ — پنل مدیریت رستوران‌دار ✅
- [x] CRUD کامل روی `Category` و `Product` (`apps/menu/views.py`) با Class-Based Views
- [x] `RestaurantOwnerRequiredMixin` (`apps/core/mixins.py`) — تضمین می‌کند فقط صاحب رستوران وارد پنل شود
- [x] فرم‌ها (`apps/menu/forms.py`) — در `ProductForm`، dropdown دسته‌بندی فقط دسته‌بندی‌های
      همان رستوران را نشان می‌دهد (چون `Category.objects` از قبل Tenant-Aware است)
- [x] مسیرها زیر `/panel/categories/...` و `/panel/products/...`
- [x] قالب‌های HTML برای فهرست/فرم افزودن‌وویرایش/تأیید حذف
- [x] پیام‌های موفقیت (Django messages) بعد از هر عملیات
- [x] لینک‌های ناوبری در `base.html` و داشبورد

### نکته امنیتی مهم این بخش

در `CategoryUpdateView` / `CategoryDeleteView` / `ProductUpdateView` / `ProductDeleteView`
عمداً از `Category.objects.all()` (نه `Category.unscoped_objects.all()`) استفاده شده.
یعنی اگر یک صاحب رستوران URL را دستی به `pk` رستوران دیگری تغییر دهد
(مثلاً `/panel/categories/17/edit/`)، چون آن رکورد اصلاً در queryset
محدودشده به رستوران او وجود ندارد، جنگو خودکار **404** برمی‌گرداند —
نه اینکه داده‌ی رستوران دیگر لو برود یا خطای دسترسی مبهم بدهد. این دقیقاً
همان مزیتی است که در بخش ۲ با ساختن `TenantAwareManager` هدف‌گذاری کرده بودیم.

⚠️ تست‌های خودکار برای این بخش نوشته نشد (به درخواست صریح برای صرفه‌جویی
در توکن). قبل از رفتن به بخش ۶ پیشنهاد می‌شود حداقل یک بار CRUD کامل
(افزودن/ویرایش/حذف دسته‌بندی و محصول، و تست دسترسی متقابل بین دو رستوران)
به‌صورت دستی یا با تست خودکار بررسی شود.

### بخش ۶ — صفحه عمومی منو + QR Code ✅
- [x] `restaurant_public_page` — صفحه عمومی Server-Rendered در آدرس `/<slug>/` (بدون نیاز به لاگین)
- [x] فقط رستوران‌های `is_active=True`، دسته‌بندی‌های `is_active=True` و محصولات `is_available=True` نمایش داده می‌شوند
- [x] Meta tag های SEO پایه (description، og:title، og:description، og:image)
- [x] `templates/public_base.html` — layout جدا و ساده برای مشتری نهایی (بدون منوی ادمین SaaS)
- [x] تولید QR Code واقعی (`apps/restaurants/utils.py` با کتابخانه `qrcode`) — On-the-fly، بدون ذخیره روی دیسک
- [x] پیش‌نمایش QR Code و دکمه دانلود در داشبورد

### دو باگ واقعی که در همین بخش پیدا و رفع شد

۱. **مبدل URL `<slug:slug>` یونیکد را قبول نمی‌کند.**
   چون `Restaurant.slug` با `allow_unicode=True` ساخته شده (می‌تواند فارسی باشد،
   مثل `کافه-آریان`)، اما مبدل پیش‌فرض `slug:` در URLconf جنگو فقط
   `[-a-zA-Z0-9_]+` (ASCII) را می‌پذیرد. با تغییر به `<str:slug>` حل شد.
   این دقیقاً همان نکته‌ای بود که موقع تست دستی (نه فقط با فرض درست بودن کد) کشف شد.

۲. **ترتیب URLها مهم است.** الگوی `<str:slug>/` باید همیشه **آخرین** آیتم در
   `apps/restaurants/urls.py` باشد؛ وگرنه مسیرهایی مثل `/dashboard/` یا
   `/qr-code/` به اشتباه به‌عنوان اسلاگ یک رستوران تفسیر می‌شدند.

### نکته معماری مهم این بخش

صفحه‌ی عمومی تنها Viewی است که کاربرش لاگین نیست، پس `TenantMiddleware`
هیچ «رستوران جاری»ای ست نمی‌کند و `TenantAwareManager` بدون فیلتر عمل
می‌کند. به همین دلیل در `restaurant_public_page` صراحتاً
`.filter(restaurant=restaurant)` نوشته شده — دقیقاً همان استثنایی که از
بخش ۲ در کامنت‌های `core/tenant.py` درباره‌اش هشدار داده بودیم.

### تست شد (دستی، نه Automated)
```
✅ صفحه عمومی با اسلاگ فارسی درست باز می‌شود و فقط محصولات موجود را نشان می‌دهد
✅ اسلاگ نامعتبر/رستوران غیرفعال → 404
✅ QR Code واقعی و معتبر (PNG 296x296) برای کاربر لاگین‌شده تولید می‌شود
✅ درخواست QR Code بدون لاگین → ریدایرکت به صفحه ورود
```

## 🎉 فاز ۱ (MVP) کامل شد

هر ۶ بخش فاز ۱ طبق نقشه راه اولیه تکمیل شدند:
۱) راه‌اندازی پروژه ۲) Tenant Isolation ۳) منو ۴) احراز هویت ۵) پنل مدیریت ۶) صفحه عمومی + QR

**جریان کامل MVP اکنون کار می‌کند:**
```
ثبت‌نام رستوران → ورود خودکار → افزودن دسته‌بندی/محصول در پنل
      → دریافت لینک/QR Code → مشتری اسکن می‌کند → منوی عمومی را می‌بیند
```

## گام بعدی

➡️ v0.2 (فاز ۲ در نقشه اصلی پروژه) — تکمیل UI عمومی (گالری، ریسپانسیو کامل‌تر)
یا طبق نقشه راه اصلی، شروع v0.3 (سبد خرید و سفارش). پیشنهاد می‌شود قبل از آن،
یک دور تست دستی/خودکار کامل روی کل فاز ۱ انجام شود.
