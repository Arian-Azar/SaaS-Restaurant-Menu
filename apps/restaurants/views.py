from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.menu.models import Category, Product

from .models import Restaurant
from .utils import generate_qr_code_png


@login_required
def dashboard(request):
    """
    نسخه‌ی خیلی اولیه‌ی پنل مدیریت رستوران — فقط برای اثبات اینکه بعد از
    ورود، کاربر واقعاً فقط داده‌ی رستوران خودش را می‌بیند (از طریق
    TenantMiddleware که در بخش ۲ ساختیم).

    نسخه‌ی کامل با CRUD واقعی روی Category/Product در بخش ۵ ساخته شد.
    """
    restaurant = getattr(request.user, 'restaurant', None)

    if restaurant is None:
        # کاربری بدون رستوران (مثلاً Super Admin) اینجا کاری ندارد.
        if request.user.is_superuser:
            return redirect('admin:index')
        return redirect('login')

    context = {
        'restaurant': restaurant,
        # این دو خط عمداً بدون .filter(restaurant=...) نوشته شده‌اند تا نشان دهند
        # TenantAwareManager به‌تنهایی محدودسازی را انجام می‌دهد.
        'category_count': Category.objects.count(),
        'product_count': Product.objects.count(),
        'public_menu_url': request.build_absolute_uri(
            reverse('public_menu', kwargs={'slug': restaurant.slug})
        ),
    }
    return render(request, 'restaurants/dashboard.html', context)


@login_required
def qr_code(request):
    """
    تولید تصویر QR Code لینک منوی عمومی رستوران کاربر لاگین‌شده.

    - بدون پارامتر: تصویر PNG به‌صورت inline برگردانده می‌شود (برای پیش‌نمایش
      در پنل مدیریت با تگ <img>).
    - با پارامتر ?download=1: هدر Content-Disposition برای دانلود مستقیم
      فایل تنظیم می‌شود.
    """
    restaurant = getattr(request.user, 'restaurant', None)
    if restaurant is None:
        return redirect('login')

    public_url = request.build_absolute_uri(
        reverse('public_menu', kwargs={'slug': restaurant.slug})
    )
    png_bytes = generate_qr_code_png(public_url)

    response = HttpResponse(png_bytes, content_type='image/png')
    if request.GET.get('download'):
        response['Content-Disposition'] = f'attachment; filename="qr-{restaurant.slug}.png"'
    return response


def restaurant_public_page(request, slug):
    """
    صفحه‌ی عمومی منوی رستوران — Server-Rendered (طبق تصمیم معماری بخش ۱ برای SEO)
    و در دسترس همه (بدون نیاز به لاگین)، از طریق اسکن QR Code یا لینک مستقیم.

    نکته مهم: برخلاف Viewهای پنل مدیریت (بخش ۵)، اینجا کاربر لاگین نیست، پس
    TenantMiddleware هیچ «رستوران جاری»ای ست نمی‌کند (restaurant=None در
    context) و TenantAwareManager بدون فیلتر عمل می‌کند. به همین دلیل اینجا
    باید صراحتاً `.filter(restaurant=restaurant)` بنویسیم — دقیقاً همان
    استثنایی که در کامنت‌های core/tenant.py درباره‌اش هشدار داده بودیم.
    """
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)

    available_products = Product.objects.filter(is_available=True).order_by('sort_order', 'name')
    categories = (
        Category.objects.filter(restaurant=restaurant, is_active=True)
        .prefetch_related(Prefetch('products', queryset=available_products))
        .order_by('sort_order', 'name')
    )

    context = {
        'restaurant': restaurant,
        'categories': categories,
    }
    return render(request, 'restaurants/public_menu.html', context)
