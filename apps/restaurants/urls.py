from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('qr-code/', views.qr_code, name='qr_code'),

    path('gallery/', views.RestaurantImageListView.as_view(), name='gallery_list'),
    path('gallery/add/', views.RestaurantImageCreateView.as_view(), name='gallery_add'),
    path('gallery/<int:pk>/delete/', views.RestaurantImageDeleteView.as_view(), name='gallery_delete'),

    path('hero-slides/', views.HeroSlideListView.as_view(), name='hero_slide_list'),
    path('hero-slides/add/', views.HeroSlideCreateView.as_view(), name='hero_slide_add'),
    path('hero-slides/<int:pk>/delete/', views.HeroSlideDeleteView.as_view(), name='hero_slide_delete'),

    path('testimonials/', views.TestimonialListView.as_view(), name='testimonial_list'),
    path('testimonials/add/', views.TestimonialCreateView.as_view(), name='testimonial_add'),
    path('testimonials/<int:pk>/delete/', views.TestimonialDeleteView.as_view(), name='testimonial_delete'),

    path('stats/', views.RestaurantStatListView.as_view(), name='stat_list'),
    path('stats/add/', views.RestaurantStatCreateView.as_view(), name='stat_add'),
    path('stats/<int:pk>/delete/', views.RestaurantStatDeleteView.as_view(), name='stat_delete'),

    path('reservations/', views.ReservationListView.as_view(), name='reservation_list'),
    path('reservations/<int:pk>/status/', views.ReservationStatusUpdateView.as_view(), name='reservation_status'),

    path('team/', views.TeamMemberListView.as_view(), name='team_list'),
    path('team/add/', views.TeamMemberCreateView.as_view(), name='team_add'),
    path('team/<int:pk>/delete/', views.TeamMemberDeleteView.as_view(), name='team_delete'),

    path('blog/', views.BlogPostListView.as_view(), name='blog_list'),
    path('blog/add/', views.BlogPostCreateView.as_view(), name='blog_add'),
    path('blog/<int:pk>/delete/', views.BlogPostDeleteView.as_view(), name='blog_delete'),

    # صفحه‌ی جزئیات محصول (فاز ۲ / بخش ۲) — چون دو بخشی است (اسلاگ + pk)،
    # هرگز با الگوی تک‌بخشیِ <str:slug>/ زیرش تداخل نمی‌کند؛ با این حال طبق
    # قرارداد این فایل، همچنان بالاتر از آن نوشته شده تا خوانا بماند.
    path('<str:slug>/products/<int:pk>/', views.product_detail_public, name='product_detail'),
    path('<str:slug>/blog/<int:pk>/', views.blog_post_detail_public, name='blog_detail'),
    path('<str:slug>/reserve/', views.reservation_create, name='reservation_create'),

    # این باید همیشه آخرین الگو باشد؛ چون <str:slug> هر مسیر یک‌بخشی
    # را می‌گیرد و اگر بالاتر قرار می‌گرفت، مسیرهایی مثل /dashboard/
    # یا /gallery/ را هم به اشتباه به‌عنوان اسلاگ رستوران تفسیر می‌کرد.
    # نکته مهم: از <str:slug> استفاده شده، نه <slug:slug>؛ چون مبدل پیش‌فرض
    # slug در جنگو فقط کاراکترهای ASCII را می‌پذیرد، در حالی که Restaurant.slug
    # با allow_unicode=True ساخته شده (می‌تواند فارسی باشد، مثل «کافه-آریان»).
    path('<str:slug>/', views.restaurant_public_page, name='public_menu'),
]
