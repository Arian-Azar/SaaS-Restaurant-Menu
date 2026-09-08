from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('qr-code/', views.qr_code, name='qr_code'),

    path('gallery/', views.RestaurantImageListView.as_view(), name='gallery_list'),
    path('gallery/add/', views.RestaurantImageCreateView.as_view(), name='gallery_add'),
    path('gallery/<int:pk>/delete/', views.RestaurantImageDeleteView.as_view(), name='gallery_delete'),

    # صفحه‌ی جزئیات محصول (فاز ۲ / بخش ۲) — چون دو بخشی است (اسلاگ + pk)،
    # هرگز با الگوی تک‌بخشیِ <str:slug>/ زیرش تداخل نمی‌کند؛ با این حال طبق
    # قرارداد این فایل، همچنان بالاتر از آن نوشته شده تا خوانا بماند.
    path('<str:slug>/products/<int:pk>/', views.product_detail_public, name='product_detail'),

    # این باید همیشه آخرین الگو باشد؛ چون <str:slug> هر مسیر یک‌بخشی
    # را می‌گیرد و اگر بالاتر قرار می‌گرفت، مسیرهایی مثل /dashboard/
    # یا /gallery/ را هم به اشتباه به‌عنوان اسلاگ رستوران تفسیر می‌کرد.
    # نکته مهم: از <str:slug> استفاده شده، نه <slug:slug>؛ چون مبدل پیش‌فرض
    # slug در جنگو فقط کاراکترهای ASCII را می‌پذیرد، در حالی که Restaurant.slug
    # با allow_unicode=True ساخته شده (می‌تواند فارسی باشد، مثل «کافه-آریان»).
    path('<str:slug>/', views.restaurant_public_page, name='public_menu'),
]
