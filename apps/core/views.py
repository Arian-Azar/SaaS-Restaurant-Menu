from django.shortcuts import render

from apps.restaurants.models import Restaurant


def platform_home(request):
    """
    صفحه اصلی پلتفرم (marketing/landing) — نه صفحه‌ی هیچ رستوران خاصی.

    کسی که مستقیم دامنه را باز می‌کند (نه لینک یک رستوران خاص) باید بفهمد
    این پلتفرم چیست و چطور می‌تواند برای کسب‌وکار خودش ثبت‌نام کند. یک
    نمونه‌ی واقعی (رستوران ساخته‌شده با seed_demo، اگر وجود داشته باشد) هم
    نشان داده می‌شود تا کسی که هنوز ثبت‌نام نکرده، نتیجه‌ی نهایی را ببیند.
    """
    demo_restaurant = Restaurant.objects.filter(is_active=True).order_by('created_at').first()

    restaurants_count = Restaurant.objects.filter(is_active=True).count()

    context = {
        'demo_restaurant': demo_restaurant,
        'restaurants_count': restaurants_count,
    }
    return render(request, 'platform_home.html', context)
