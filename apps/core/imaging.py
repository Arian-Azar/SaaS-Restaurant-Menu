"""
بهینه‌سازی خودکار تصاویر آپلودی (فاز ۲ / بخش ۵).

هدف: کاربر (صاحب رستوران) هر عکسی با هر اندازه‌ای آپلود کند (مثلاً یک عکس
۸ مگابایتی مستقیم از دوربین گوشی)، قبل از ذخیره روی دیسک به یک اندازه‌ی
معقول resize و فشرده می‌شود — هم سرعت لود صفحه‌ی عمومی برای مشتری بهتر
می‌شود، هم فضای ذخیره‌سازی سرور کمتر مصرف می‌شود.

این تابع عمداً یک‌جا (اینجا) نوشته شده و در models.py چند اپ مختلف
(restaurants, menu) صدا زده می‌شود، تا منطق تکراری نشود.
"""

import io

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image


def optimize_image_field(image_field, max_width: int, max_height: int, quality: int = 82) -> None:
    """
    یک ImageField (مثل self.logo یا self.image) را در محل، resize و
    فشرده می‌کند. باید قبل از super().save() مدل صدا زده شود.

    نکته مهم: فقط زمانی پردازش انجام می‌شود که فایل واقعاً «تازه آپلود شده»
    باشد (یعنی از نوع UploadedFile است)، نه فایلی که از قبل روی دیسک/Storage
    بوده. بدون این چک، هر بار که رکورد ذخیره می‌شود (حتی فقط برای تغییر یک
    فیلد دیگر مثل caption)، عکس دوباره باز و فشرده می‌شد که هم غیرضروری است
    و هم به‌مرور کیفیت را (به‌خاطر فشرده‌سازی مکرر JPEG) پایین می‌آورد.
    """
    if not image_field:
        return

    try:
        file_obj = image_field.file
    except (ValueError, FileNotFoundError):
        # فیلد خالی است یا فایل هنوز روی دیسک نیست.
        return

    if not isinstance(file_obj, UploadedFile):
        return

    try:
        img = Image.open(image_field)
        img.load()
    except Exception:
        # اگر فایل خراب/غیرقابل‌خواندن بود، بگذار خود ImageField validation
        # جنگو خطای مناسب را بدهد؛ اینجا کاری نمی‌کنیم که کرش نکند.
        return

    img_format = (img.format or 'JPEG').upper()
    original_name = image_field.name

    # resize فقط در صورت لزوم کوچک می‌کند (هرگز عکس کوچک را بزرگ نمی‌کند).
    img.thumbnail((max_width, max_height), Image.LANCZOS)

    buffer = io.BytesIO()
    if img_format in ('JPEG', 'JPG'):
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
    elif img_format == 'PNG':
        img.save(buffer, format='PNG', optimize=True)
    elif img_format == 'WEBP':
        img.save(buffer, format='WEBP', quality=quality)
    else:
        # فرمت ناشناس: بدون تغییر رها می‌کنیم تا رفتار غیرمنتظره پیش نیاید.
        return

    buffer.seek(0)
    # save=False چون خود مدل قرار است بلافاصله super().save() را صدا بزند؛
    # اینجا فقط محتوای فایل در حافظه جایگزین می‌شود.
    image_field.save(original_name, ContentFile(buffer.read()), save=False)
