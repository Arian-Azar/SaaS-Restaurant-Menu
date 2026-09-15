from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from apps.core.mixins import RestaurantOwnerRequiredMixin
from apps.menu.models import Category, Product

from .forms import HeroSlideForm, RestaurantImageForm, RestaurantStatForm, TestimonialForm
from .models import HeroSlide, Restaurant, RestaurantImage, RestaurantStat, Testimonial
from .seo import build_product_json_ld, build_restaurant_json_ld
from .utils import generate_qr_code_png


@login_required
def dashboard(request):
    """
    نسخه‌ی خیلی اولیه‌ی پنل مدیریت رستوران — فقط برای اثبات اینکه بعد از
    ورود، کاربر واقعاً فقط داده‌ی رستوران خودش را می‌بیند (از طریق
    TenantMiddleware که در بخش ۲ ساختیم).

    نسخه‌ی کامل با CRUD واقعی روی Category/Product در بخش ۵ ساخته شد.
    """
    restaurant = getattr(request.user, 'restaurant', None)

    if restaurant is None:
        # کاربری بدون رستوران (مثلاً Super Admin) اینجا کاری ندارد.
        if request.user.is_superuser:
            return redirect('admin:index')
        return redirect('login')

    context = {
        'restaurant': restaurant,
        # این دو خط عمداً بدون .filter(restaurant=...) نوشته شده‌اند تا نشان دهند
        # TenantAwareManager به‌تنهایی محدودسازی را انجام می‌دهد.
        'category_count': Category.objects.count(),
        'product_count': Product.objects.count(),
        'public_menu_url': request.build_absolute_uri(
            reverse('public_menu', kwargs={'slug': restaurant.slug})
        ),
    }
    return render(request, 'restaurants/dashboard.html', context)


@login_required
def qr_code(request):
    """
    تولید تصویر QR Code لینک منوی عمومی رستوران کاربر لاگین‌شده.

    - بدون پارامتر: تصویر PNG به‌صورت inline برگردانده می‌شود (برای پیش‌نمایش
      در پنل مدیریت با تگ <img>).
    - با پارامتر ?download=1: هدر Content-Disposition برای دانلود مستقیم
      فایل تنظیم می‌شود.
    """
    restaurant = getattr(request.user, 'restaurant', None)
    if restaurant is None:
        return redirect('login')

    public_url = request.build_absolute_uri(
        reverse('public_menu', kwargs={'slug': restaurant.slug})
    )
    png_bytes = generate_qr_code_png(public_url)

    response = HttpResponse(png_bytes, content_type='image/png')
    if request.GET.get('download'):
        response['Content-Disposition'] = f'attachment; filename="qr-{restaurant.slug}.png"'
    return response


def restaurant_public_page(request, slug):
    """
    صفحه‌ی عمومی منوی رستوران — Server-Rendered (طبق تصمیم معماری بخش ۱ برای SEO)
    و در دسترس همه (بدون نیاز به لاگین)، از طریق اسکن QR Code یا لینک مستقیم.

    نکته مهم: برخلاف Viewهای پنل مدیریت (بخش ۵)، اینجا کاربر لاگین نیست، پس
    TenantMiddleware هیچ «رستوران جاری»ای ست نمی‌کند (restaurant=None در
    context) و TenantAwareManager بدون فیلتر عمل می‌کند. به همین دلیل اینجا
    باید صراحتاً `.filter(restaurant=restaurant)` بنویسیم — دقیقاً همان
    استثنایی که در کامنت‌های core/tenant.py درباره‌اش هشدار داده بودیم.
    """
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)

    available_products = Product.objects.filter(is_available=True).order_by('sort_order', 'name')
    categories = (
        Category.objects.filter(restaurant=restaurant, is_active=True)
        .prefetch_related(Prefetch('products', queryset=available_products))
        .order_by('sort_order', 'name')
    )

    hero_slides = HeroSlide.objects.filter(restaurant=restaurant, is_active=True)
    testimonials = Testimonial.objects.filter(restaurant=restaurant, is_active=True)

    context = {
        'restaurant': restaurant,
        'categories': categories,
        # RestaurantImage.objects هم Tenant-Aware است، پس همان استدلال بالا
        # (کاربر anonymous → context خالی) اینجا هم صادق است؛ صراحتاً فیلتر می‌کنیم.
        'gallery_images': RestaurantImage.objects.filter(restaurant=restaurant),
        'hero_slides': hero_slides,
        'has_multiple_hero_slides': hero_slides.count() > 1,
        'testimonials': testimonials,
        'has_multiple_testimonials': testimonials.count() > 1,
        'stats': RestaurantStat.objects.filter(restaurant=restaurant),
        # آمار «تعداد غذاهای منو» عمداً محاسبه‌شده است، نه یک RestaurantStat
        # دستی — تا همیشه با واقعیت منو هماهنگ بماند (نگاه کن به کامنت
        # بالای مدل RestaurantStat در models.py).
        'product_count': Product.objects.filter(restaurant=restaurant, is_available=True).count(),
        'json_ld': build_restaurant_json_ld(request, restaurant, categories, testimonials=testimonials),
    }
    return render(request, 'restaurants/public_menu.html', context)


def product_detail_public(request, slug, pk):
    """
    صفحه‌ی اختصاصی هر محصول (فاز ۲ / بخش ۲).

    در صفحه‌ی اصلی منو (restaurant_public_page) هر محصول فقط یک ردیف
    خلاصه است؛ اینجا نسخه‌ی کامل با عکس بزرگ‌تر و توضیح کامل نمایش داده
    می‌شود. مثل restaurant_public_page، اینجا هم کاربر لاگین نیست، پس
    صراحتاً هم رستوران و هم محصول را با .filter/get_object_or_404 محدود
    می‌کنیم (TenantAwareManager در این کانتکست بدون فیلتر عمل می‌کند).
    """
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)
    product = get_object_or_404(
        Product, pk=pk, restaurant=restaurant, is_available=True, category__is_active=True
    )

    context = {
        'restaurant': restaurant,
        'product': product,
        'json_ld': build_product_json_ld(request, product),
    }
    return render(request, 'restaurants/product_detail.html', context)


# -----------------------------------------------------------------------
# گالری تصاویر رستوران (فاز ۲ / بخش ۱)
# -----------------------------------------------------------------------
class RestaurantImageListView(RestaurantOwnerRequiredMixin, ListView):
    model = RestaurantImage
    template_name = 'restaurants/gallery_list.html'
    context_object_name = 'images'

    def get_queryset(self):
        # RestaurantImage.objects از TenantAwareManager ارث می‌برد (چون
        # RestaurantImage از TenantModel ساخته شده)، پس خودکار به رستوران
        # کاربر لاگین‌شده محدود است.
        return RestaurantImage.objects.all()


class RestaurantImageCreateView(RestaurantOwnerRequiredMixin, CreateView):
    model = RestaurantImage
    form_class = RestaurantImageForm
    template_name = 'restaurants/gallery_form.html'
    success_url = reverse_lazy('gallery_list')

    def form_valid(self, form):
        form.instance.restaurant = self.get_restaurant()
        messages.success(self.request, 'تصویر با موفقیت اضافه شد.')
        return super().form_valid(form)


class RestaurantImageDeleteView(RestaurantOwnerRequiredMixin, DeleteView):
    model = RestaurantImage
    template_name = 'restaurants/gallery_confirm_delete.html'
    success_url = reverse_lazy('gallery_list')

    def get_queryset(self):
        # همان استدلال بخش ۵: چون queryset خودکار به رستوران جاری محدود
        # است، دستکاری pk در URL برای حذف تصویر رستوران دیگر منجر به ۴۰۴
        # می‌شود، نه دسترسی غیرمجاز.
        return RestaurantImage.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'تصویر حذف شد.')
        return super().form_valid(form)


# -----------------------------------------------------------------------
# اسلایدر هیرو (HeroSlide)
# -----------------------------------------------------------------------
class HeroSlideListView(RestaurantOwnerRequiredMixin, ListView):
    model = HeroSlide
    template_name = 'restaurants/hero_slide_list.html'
    context_object_name = 'slides'

    def get_queryset(self):
        return HeroSlide.objects.all()


class HeroSlideCreateView(RestaurantOwnerRequiredMixin, CreateView):
    model = HeroSlide
    form_class = HeroSlideForm
    template_name = 'restaurants/hero_slide_form.html'
    success_url = reverse_lazy('hero_slide_list')

    def form_valid(self, form):
        form.instance.restaurant = self.get_restaurant()
        messages.success(self.request, 'اسلاید هیرو با موفقیت اضافه شد.')
        return super().form_valid(form)


class HeroSlideDeleteView(RestaurantOwnerRequiredMixin, DeleteView):
    model = HeroSlide
    template_name = 'restaurants/hero_slide_confirm_delete.html'
    success_url = reverse_lazy('hero_slide_list')

    def get_queryset(self):
        return HeroSlide.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'اسلاید حذف شد.')
        return super().form_valid(form)


# -----------------------------------------------------------------------
# نظرات مشتریان (Testimonial)
# -----------------------------------------------------------------------
class TestimonialListView(RestaurantOwnerRequiredMixin, ListView):
    model = Testimonial
    template_name = 'restaurants/testimonial_list.html'
    context_object_name = 'testimonials'

    def get_queryset(self):
        return Testimonial.objects.all()


class TestimonialCreateView(RestaurantOwnerRequiredMixin, CreateView):
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'restaurants/testimonial_form.html'
    success_url = reverse_lazy('testimonial_list')

    def form_valid(self, form):
        form.instance.restaurant = self.get_restaurant()
        messages.success(self.request, 'نظر مشتری با موفقیت اضافه شد.')
        return super().form_valid(form)


class TestimonialDeleteView(RestaurantOwnerRequiredMixin, DeleteView):
    model = Testimonial
    template_name = 'restaurants/testimonial_confirm_delete.html'
    success_url = reverse_lazy('testimonial_list')

    def get_queryset(self):
        return Testimonial.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'نظر حذف شد.')
        return super().form_valid(form)


# -----------------------------------------------------------------------
# آمار/شمارنده صفحه اصلی (RestaurantStat)
# -----------------------------------------------------------------------
class RestaurantStatListView(RestaurantOwnerRequiredMixin, ListView):
    model = RestaurantStat
    template_name = 'restaurants/stat_list.html'
    context_object_name = 'stats'

    def get_queryset(self):
        return RestaurantStat.objects.all()


class RestaurantStatCreateView(RestaurantOwnerRequiredMixin, CreateView):
    model = RestaurantStat
    form_class = RestaurantStatForm
    template_name = 'restaurants/stat_form.html'
    success_url = reverse_lazy('stat_list')

    def form_valid(self, form):
        form.instance.restaurant = self.get_restaurant()
        messages.success(self.request, 'آمار جدید اضافه شد.')
        return super().form_valid(form)


class RestaurantStatDeleteView(RestaurantOwnerRequiredMixin, DeleteView):
    model = RestaurantStat
    template_name = 'restaurants/stat_confirm_delete.html'
    success_url = reverse_lazy('stat_list')

    def get_queryset(self):
        return RestaurantStat.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'آمار حذف شد.')
        return super().form_valid(form)
