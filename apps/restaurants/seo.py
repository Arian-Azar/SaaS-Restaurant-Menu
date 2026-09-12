"""
تولید داده‌ساختاریافته (Structured Data / JSON-LD) طبق استاندارد schema.org
برای صفحات عمومی — هدف: نمایش بهتر در نتایج جستجوی گوگل (Rich Results)
مثل نمایش نام رستوران، آدرس، تلفن و حتی آیتم‌های منو مستقیم در نتایج جستجو.

⚠️ نکته مهم درباره‌ی priceCurrency:
    schema.org از کدهای استاندارد ISO 4217 برای ارز انتظار دارد. «تومان»
    یک واحد رسمی ISO نیست (واحد رسمی ایران ریال/IRR است، و هر تومان برابر
    ۱۰ ریال است). فعلاً از IRR استفاده شده، اما این یعنی عدد قیمت نمایش‌داده‌شده
    در Structured Data ممکن است با نمایش «تومان» در خود صفحه یک رقم اختلاف
    داشته باشد. این یک نکته‌ی ناقص شناخته‌شده است که باید همزمان با طراحی
    مدل واحد پول (در فاز پرداخت / v0.4) دقیق‌تر حل شود.
"""

import json

from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

from .models import Restaurant


def _safe_json_ld(data: dict) -> str:
    """
    JSON را برای قرارگیری امن داخل تگ <script type="application/ld+json">
    سریالایز می‌کند.

    نکته امنیتی: اگر توضیح یک محصول (که کاربر/صاحب رستوران وارد کرده)
    به‌طور اتفاقی شامل رشته‌ی `</script>` باشد، بدون این escape می‌تواند
    تگ script را زودتر از موعد ببندد و باقی HTML صفحه را بشکند یا حتی
    زمینه‌ساز یک XSS ساده شود. با جایگزینی `</` با `<\\/` این خطر از بین می‌رود
    (این جایگزینی از نظر معنایی روی خودِ JSON اثری ندارد).
    """
    return json.dumps(data, ensure_ascii=False).replace('</', '<\\/')


def build_restaurant_json_ld(request, restaurant, categories) -> str:
    """JSON-LD نوع Restaurant + Menu برای صفحه‌ی اصلی منوی رستوران."""
    menu_sections = []
    for category in categories:
        items = []
        for product in category.products.all():
            item = {'@type': 'MenuItem', 'name': product.name}
            if product.description:
                item['description'] = product.description
            item['offers'] = {
                '@type': 'Offer',
                'price': str(product.final_price),
                'priceCurrency': 'IRR',
            }
            if product.image:
                item['image'] = request.build_absolute_uri(product.image.url)
            items.append(item)

        if items:
            menu_sections.append({
                '@type': 'MenuSection',
                'name': category.name,
                'hasMenuItem': items,
            })

    data = {
        '@context': 'https://schema.org',
        '@type': 'Restaurant',
        'name': restaurant.name,
        'url': request.build_absolute_uri(
            reverse('public_menu', kwargs={'slug': restaurant.slug})
        ),
    }
    if restaurant.description:
        data['description'] = restaurant.description
    if restaurant.address:
        data['address'] = {'@type': 'PostalAddress', 'streetAddress': restaurant.address}
    if restaurant.phone:
        data['telephone'] = restaurant.phone
    if restaurant.cover_image:
        data['image'] = request.build_absolute_uri(restaurant.cover_image.url)
    if menu_sections:
        data['hasMenu'] = {'@type': 'Menu', 'hasMenuSection': menu_sections}

    # ensure_ascii=False تا کاراکترهای فارسی به‌جای \uXXXX خوانا بمانند.
    return _safe_json_ld(data)


def build_product_json_ld(request, product) -> str:
    """JSON-LD نوع MenuItem برای صفحه‌ی اختصاصی هر محصول."""
    data = {
        '@context': 'https://schema.org',
        '@type': 'MenuItem',
        'name': product.name,
        'offers': {
            '@type': 'Offer',
            'price': str(product.final_price),
            'priceCurrency': 'IRR',
        },
    }
    if product.description:
        data['description'] = product.description
    if product.image:
        data['image'] = request.build_absolute_uri(product.image.url)

    return _safe_json_ld(data)


def sitemap_xml_response(request):
    """
    تولید sitemap.xml شامل لینک تمام رستوران‌های فعال.

    عمداً از فریم‌ورک django.contrib.sitemaps استفاده نشده، چون آن فریم‌ورک
    معمولاً وابسته به django.contrib.sites است (برای تعیین دامنه) که برای
    این پروژه اضافه‌بار غیرضروری محسوب می‌شود؛ اینجا دامنه مستقیماً از
    request.build_absolute_uri گرفته می‌شود — ساده‌تر و کافی برای نیاز فعلی.
    """
    restaurants = Restaurant.objects.filter(is_active=True)

    url_entries = []
    for restaurant in restaurants:
        loc = request.build_absolute_uri(
            reverse('public_menu', kwargs={'slug': restaurant.slug})
        )
        lastmod = restaurant.updated_at.date().isoformat()
        url_entries.append(
            f'<url><loc>{escape(loc)}</loc><lastmod>{lastmod}</lastmod></url>'
        )

    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + ''.join(url_entries) +
        '</urlset>'
    )
    return HttpResponse(xml_content, content_type='application/xml')


def robots_txt_response(request):
    """robots.txt ساده: اجازه‌ی کامل ایندکس + آدرس sitemap."""
    sitemap_url = request.build_absolute_uri(reverse('sitemap_xml'))
    lines = [
        'User-agent: *',
        'Allow: /',
        f'Sitemap: {sitemap_url}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
