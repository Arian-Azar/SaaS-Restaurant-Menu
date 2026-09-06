"""
Mixin های مشترک برای Viewهای پنل مدیریت رستوران‌دار.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RestaurantOwnerRequiredMixin(LoginRequiredMixin):
    """
    برای تمام Viewهای پنل مدیریت (بخش ۵) استفاده می‌شود.

    نکته مهم: خودِ محدودسازی داده (Tenant Isolation) توسط TenantAwareManager
    و TenantMiddleware (بخش ۲) به‌صورت خودکار انجام می‌شود؛ این Mixin فقط
    مطمئن می‌شود کاربر اصلاً صاحب یک رستوران است (نه Super Admin بدون
    رستوران، نه کاربری با حساب ناقص) و در غیر این صورت پیام خطای مناسب
    می‌دهد به‌جای یک AttributeError خام.
    """

    def get_restaurant(self):
        restaurant = getattr(self.request.user, 'restaurant', None)
        if restaurant is None:
            raise PermissionDenied('این بخش فقط برای صاحبان رستوران در دسترس است.')
        return restaurant

    def dispatch(self, request, *args, **kwargs):
        # ابتدا LoginRequiredMixin بررسی می‌کند که کاربر اصلاً لاگین است؛
        # سپس همین‌جا مطمئن می‌شویم کاربر صاحب یک رستوران است، قبل از
        # اینکه منطق اصلی View (که فرض می‌کند رستوران وجود دارد) اجرا شود.
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get(self, request, *args, **kwargs):
        self.get_restaurant()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_restaurant()
        return super().post(request, *args, **kwargs)
