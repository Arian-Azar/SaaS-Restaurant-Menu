from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    پنل ادمین کاربران — این بخش فقط برای Super Admin (پلتفرم) قابل مشاهده است،
    نه برای Restaurant Owner (طبق تصمیم معماری: Restaurant Owner از Django Admin
    خام استفاده نمی‌کند).
    """

    list_display = DjangoUserAdmin.list_display + ('role', 'phone_number')
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('اطلاعات تکمیلی SaaS', {'fields': ('role', 'phone_number')}),
    )
