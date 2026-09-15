from django.contrib import admin

from .models import HeroSlide, Restaurant, RestaurantImage, RestaurantStat, Testimonial


class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 0
    fields = ('image', 'caption', 'sort_order')


class HeroSlideInline(admin.TabularInline):
    model = HeroSlide
    extra = 0
    fields = ('image', 'title', 'subtitle', 'is_active', 'sort_order')


class TestimonialInline(admin.TabularInline):
    model = Testimonial
    extra = 0
    fields = ('customer_name', 'rating', 'comment', 'is_active', 'sort_order')


class RestaurantStatInline(admin.TabularInline):
    model = RestaurantStat
    extra = 0
    fields = ('label', 'number', 'sort_order')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """
    این پنل فقط برای Super Admin پلتفرم است (طبق تصمیم معماری، Restaurant
    Owner از این پنل استفاده نمی‌کند و پنل مدیریت اختصاصی خودش را دارد که
    در بخش ۵ ساخته می‌شود).
    """

    list_display = ('name', 'slug', 'owner', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'owner__username', 'owner__email')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [HeroSlideInline, RestaurantImageInline, TestimonialInline, RestaurantStatInline]
