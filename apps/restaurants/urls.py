from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('qr-code/', views.qr_code, name='qr_code'),

    # این باید همیشه آخرین الگو باشد؛ چون <slug:slug> هر مسیر یک‌بخشی
    # را می‌گیرد و اگر بالاتر قرار می‌گرفت، مسیرهایی مثل /dashboard/
    # یا /qr-code/ را هم به اشتباه به‌عنوان اسلاگ رستوران تفسیر می‌کرد.
    # نکته مهم: از <str:slug> استفاده شده، نه <slug:slug>؛ چون مبدل پیش‌فرض
    # slug در جنگو فقط کاراکترهای ASCII را می‌پذیرد، در حالی که Restaurant.slug
    # با allow_unicode=True ساخته شده (می‌تواند فارسی باشد، مثل «کافه-آریان»).
    path('<str:slug>/', views.restaurant_public_page, name='public_menu'),
]
