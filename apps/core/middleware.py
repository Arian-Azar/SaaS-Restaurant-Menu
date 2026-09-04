"""
Middleware مربوط به Multi-Tenancy.
"""

from .tenant import clear_current_restaurant, set_current_restaurant


class TenantMiddleware:
    """
    در ابتدای هر request، اگر کاربر لاگین کرده و صاحب یک رستوران است،
    آن رستوران را به‌عنوان «رستوران جاری» ثبت می‌کند تا TenantAwareManager
    بتواند QuerySetها را خودکار به همان رستوران محدود کند.

    نکات مهم:
    - Super Admin (is_superuser=True) عمداً هیچ رستورانی برایش ست نمی‌شود،
      چون او باید بتواند به داده‌ی همه‌ی رستوران‌ها دسترسی داشته باشد
      (از طریق unscoped_objects در Viewهای مخصوص Super Admin).
    - کاربر مهمان (Customer بدون لاگین) هم رستورانی ست نمی‌شود؛ صفحات عمومی
      منو باید صراحتاً بر اساس slug در URL، رستوران را پیدا و فیلتر کنند.
    - در پایان request، کانتکست حتماً پاک می‌شود تا بین requestهای بعدی
      (خصوصاً در محیط‌های async/threaded) نشتی رخ ندهد.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        restaurant = None
        user = getattr(request, 'user', None)

        if user is not None and user.is_authenticated and not user.is_superuser:
            # OneToOneField باعث می‌شود دسترسی user.restaurant باشد؛
            # اگر کاربر هنوز رستورانی نساخته باشد (بین ثبت‌نام و تکمیل فرآیند)
            # این مقدار وجود ندارد، پس با getattr محافظت می‌کنیم.
            restaurant = getattr(user, 'restaurant', None)

        set_current_restaurant(restaurant)
        try:
            response = self.get_response(request)
        finally:
            clear_current_restaurant()

        return response
