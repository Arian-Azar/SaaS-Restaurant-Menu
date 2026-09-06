from django import forms

from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'sort_order', 'is_active']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'description', 'price',
            'discount_price', 'image', 'is_available', 'sort_order',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Category.objects از قبل توسط TenantAwareManager به رستوران جاری
        # محدود شده (بخش ۲)؛ پس مالک رستوران هرگز دسته‌بندیِ رستوران دیگری
        # را در این dropdown نمی‌بیند و در نتیجه نمی‌تواند انتخابش کند.
        self.fields['category'].queryset = Category.objects.all()
