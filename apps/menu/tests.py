from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.core.tenant import clear_current_restaurant, set_current_restaurant
from apps.restaurants.models import Restaurant

from .models import Category, Product

User = get_user_model()


class MenuTenantIsolationTests(TestCase):
    """
    این تست‌ها اثبات می‌کنند که TenantAwareManager (ساخته‌شده در بخش ۲)
    واقعاً روی مدل‌های واقعی (Category, Product) کار می‌کند: یعنی
    Restaurant A هرگز دسته‌بندی یا محصول Restaurant B را نمی‌بیند —
    نه فقط در تئوری، بلکه با یک QuerySet واقعی.
    """

    def setUp(self):
        owner1 = User.objects.create_user(username='owner1', password='pass12345')
        owner2 = User.objects.create_user(username='owner2', password='pass12345')
        self.r1 = Restaurant.objects.create(owner=owner1, name='کافه اول')
        self.r2 = Restaurant.objects.create(owner=owner2, name='کافه دوم')

        # این create ها عمداً بدون تنظیم رستوران جاری انجام می‌شوند چون
        # TenantAwareManager فقط روی خواندن (queryset) اثر دارد، نه روی create.
        self.cat1 = Category.objects.create(restaurant=self.r1, name='پیتزا')
        self.cat2 = Category.objects.create(restaurant=self.r2, name='پیتزا')  # نام تکراری، رستوران متفاوت -> باید مجاز باشد

        self.addCleanup(clear_current_restaurant)

    def test_categories_are_isolated_per_restaurant(self):
        set_current_restaurant(self.r1)
        names = list(Category.objects.values_list('name', 'restaurant_id'))
        self.assertEqual(names, [('پیتزا', self.r1.id)])

        set_current_restaurant(self.r2)
        names = list(Category.objects.values_list('name', 'restaurant_id'))
        self.assertEqual(names, [('پیتزا', self.r2.id)])

    def test_no_current_restaurant_returns_everything(self):
        clear_current_restaurant()
        self.assertEqual(Category.objects.count(), 2)

    def test_unscoped_objects_always_bypasses_isolation(self):
        set_current_restaurant(self.r1)
        # objects محدود به r1 است اما unscoped_objects باید همه را برگرداند.
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.unscoped_objects.count(), 2)

    def test_same_category_name_rejected_within_same_restaurant(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(restaurant=self.r1, name='پیتزا')

    def test_product_isolated_per_restaurant(self):
        Product.objects.create(
            restaurant=self.r1, category=self.cat1, name='پیتزا مخصوص', price=Decimal('450000')
        )
        Product.objects.create(
            restaurant=self.r2, category=self.cat2, name='پیتزا پپرونی', price=Decimal('380000')
        )

        set_current_restaurant(self.r1)
        self.assertEqual(list(Product.objects.values_list('name', flat=True)), ['پیتزا مخصوص'])

        set_current_restaurant(self.r2)
        self.assertEqual(list(Product.objects.values_list('name', flat=True)), ['پیتزا پپرونی'])

    def test_product_cannot_use_category_from_another_restaurant(self):
        with self.assertRaises(ValidationError):
            Product.objects.create(
                restaurant=self.r1,
                category=self.cat2,  # cat2 متعلق به r2 است
                name='محصول نامعتبر',
                price=Decimal('100000'),
            )

    def test_discount_price_must_be_lower_than_price(self):
        with self.assertRaises(ValidationError):
            Product.objects.create(
                restaurant=self.r1,
                category=self.cat1,
                name='محصول با تخفیف نامعتبر',
                price=Decimal('100000'),
                discount_price=Decimal('150000'),
            )

    def test_final_price_property(self):
        with_discount = Product.objects.create(
            restaurant=self.r1, category=self.cat1, name='محصول تخفیف‌دار',
            price=Decimal('200000'), discount_price=Decimal('150000'),
        )
        without_discount = Product.objects.create(
            restaurant=self.r1, category=self.cat1, name='محصول بدون تخفیف',
            price=Decimal('200000'),
        )
        self.assertEqual(with_discount.final_price, Decimal('150000'))
        self.assertEqual(without_discount.final_price, Decimal('200000'))
