# Restaurant SaaS Platform


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
،

➡️ v0.2 (فاز ۲ در نقشه اصلی پروژه) — تکمیل UI عمومی (گالری، ریسپانسیو کامل‌تر)
یا طبق نقشه راه اصلی، شروع v0.3 (سبد خرید و سفارش). پیشنهاد می‌شود قبل از آن،
یک دور تست دستی/خودکار کامل روی کل فاز ۱ انجام شود.
