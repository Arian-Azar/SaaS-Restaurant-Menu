from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.core.mixins import RestaurantOwnerRequiredMixin

from .forms import CategoryForm, ProductForm
from .models import Category, Product


# -----------------------------------------------------------------------
# Category
# -----------------------------------------------------------------------
class CategoryListView(RestaurantOwnerRequiredMixin, ListView):
    model = Category
    template_name = 'menu/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Category.objects از قبل توسط TenantAwareManager به رستوران جاری
        # (کاربر لاگین‌شده) محدود شده — نیازی به .filter(restaurant=...) نیست.
        return Category.objects.all()


class CategoryCreateView(RestaurantOwnerRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'menu/category_form.html'
    success_url = reverse_lazy('menu:category_list')

    def form_valid(self, form):
        form.instance.restaurant = self.get_restaurant()
        messages.success(self.request, 'دسته‌بندی با موفقیت اضافه شد.')
        return super().form_valid(form)


class CategoryUpdateView(RestaurantOwnerRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'menu/category_form.html'
    success_url = reverse_lazy('menu:category_list')

    def get_queryset(self):
        # نکته امنیتی مهم: چون Category.objects خودکار به رستوران جاری
        # محدود است، اگر کاربر با دستکاری URL بخواهد pk رستوران دیگری را
        # وارد کند، اینجا Http404 برمی‌گردد (نه اینکه داده‌ی رستوران دیگر
        # لو برود). این دقیقاً همان مزیت معماری TenantAwareManager است.
        return Category.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'دسته‌بندی به‌روزرسانی شد.')
        return super().form_valid(form)


class CategoryDeleteView(RestaurantOwnerRequiredMixin, DeleteView):
    model = Category
    template_name = 'menu/category_confirm_delete.html'
    success_url = reverse_lazy('menu:category_list')

    def get_queryset(self):
        return Category.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'دسته‌بندی حذف شد.')
        return super().form_valid(form)


# -----------------------------------------------------------------------
# Product
# -----------------------------------------------------------------------
class ProductListView(RestaurantOwnerRequiredMixin, ListView):
    model = Product
    template_name = 'menu/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.select_related('category').all()


class ProductCreateView(RestaurantOwnerRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'menu/product_form.html'
    success_url = reverse_lazy('menu:product_list')

    def form_valid(self, form):
        form.instance.restaurant = self.get_restaurant()
        messages.success(self.request, 'محصول با موفقیت اضافه شد.')
        return super().form_valid(form)


class ProductUpdateView(RestaurantOwnerRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'menu/product_form.html'
    success_url = reverse_lazy('menu:product_list')

    def get_queryset(self):
        return Product.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'محصول به‌روزرسانی شد.')
        return super().form_valid(form)


class ProductDeleteView(RestaurantOwnerRequiredMixin, DeleteView):
    model = Product
    template_name = 'menu/product_confirm_delete.html'
    success_url = reverse_lazy('menu:product_list')

    def get_queryset(self):
        return Product.objects.all()

    def form_valid(self, form):
        messages.success(self.request, 'محصول حذف شد.')
        return super().form_valid(form)
