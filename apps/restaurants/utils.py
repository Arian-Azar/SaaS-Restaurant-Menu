"""
تولید QR Code برای لینک صفحه‌ی عمومی هر رستوران.

عمداً روی دیسک ذخیره نمی‌کنیم (به‌عنوان ImageField)؛ چون:
    - محتوای QR فقط یک URL است که هر بار می‌تواند On-the-fly تولید شود.
    - اگر بعداً دامنه یا اسلاگ عوض شد، نیازی به regenerate/migration نیست.
"""

import io

import qrcode


def generate_qr_code_png(data: str) -> bytes:
    """یک تصویر PNG از روی رشته‌ی ورودی (اینجا: URL منوی عمومی) می‌سازد."""
    img = qrcode.make(data, box_size=8, border=2)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()
