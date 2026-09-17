from django.contrib import admin

from .models import (
    BlogPost,
    HeroSlide,
    Reservation,
    Restaurant,
    RestaurantImage,
    RestaurantStat,
    TeamMember,
    Testimonial,
)


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


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0
    fields = ('name', 'position', 'photo', 'is_active', 'sort_order')


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
    inlines = [HeroSlideInline, RestaurantImageInline, TeamMemberInline, TestimonialInline, RestaurantStatInline]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    درخواست‌های رزرو میز — Super Admin می‌تواند همه را ببیند (برای پشتیبانی)؛
    صاحب رستوران از پنل اختصاصی خودش (`/reservations/`) فقط رزروهای خودش را می‌بیند.
    """

    list_display = ('customer_name', 'restaurant', 'reservation_date', 'reservation_time', 'party_size', 'status')
    list_filter = ('status', 'reservation_date', 'restaurant')
    search_fields = ('customer_name', 'phone_number', 'restaurant__name')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'restaurant', 'is_published', 'published_at')
    list_filter = ('is_published', 'restaurant')
    search_fields = ('title', 'restaurant__name')
