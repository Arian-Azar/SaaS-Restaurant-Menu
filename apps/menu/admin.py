from django.contrib import admin

from .models import Category, Product


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name', 'price', 'discount_price', 'is_available', 'sort_order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    این پنل فقط برای Super Admin پلتفرم است (طبق تصمیم معماری بخش ۱).
    Super Admin هیچ رستوران جاری‌ای در context ندارد (به core/middleware.py
    مراجعه کن)، پس اینجا queryset پیش‌فرض (`objects`) بدون محدودیت،
    داده‌ی همه‌ی رستوران‌ها را نشان می‌دهد.
    """

    list_display = ('name', 'restaurant', 'sort_order', 'is_active')
    list_filter = ('is_active', 'restaurant')
    search_fields = ('name', 'restaurant__name')
    inlines = [ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'discount_price', 'is_available')
    list_filter = ('is_available', 'restaurant', 'category')
    search_fields = ('name', 'restaurant__name', 'category__name')
