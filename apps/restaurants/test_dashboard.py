from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.menu.models import Category, Product

from .models import Restaurant

User = get_user_model()


class DashboardTenantIsolationTests(TestCase):
    """
    این تست، برخلاف تست‌های بخش ۲ (که مستقیماً Middleware را با
    RequestFactory صدا می‌زدند)، از یک session لاگین‌شده‌ی واقعی و
    self.client.get() استفاده می‌کند — یعنی کل زنجیره‌ی واقعی
    (Auth → Session → TenantMiddleware → View → Template) را تست می‌کند.
    """

    def setUp(self):
        owner1 = User.objects.create_user(username='owner1', password='StrongPass123!')
        owner2 = User.objects.create_user(username='owner2', password='StrongPass123!')

        self.r1 = Restaurant.objects.create(owner=owner1, name='کافه اول')
        r2 = Restaurant.objects.create(owner=owner2, name='کافه دوم')

        cat1 = Category.objects.create(restaurant=self.r1, name='نوشیدنی')
        cat2 = Category.objects.create(restaurant=r2, name='نوشیدنی')

        Product.objects.create(restaurant=self.r1, category=cat1, name='قهوه', price=Decimal('80000'))
        # رستوران دوم عمداً ۲ محصول دارد تا اگر ایزوله‌سازی درست کار نکند، در شمارش مشخص شود.
        Product.objects.create(restaurant=r2, category=cat2, name='چای', price=Decimal('40000'))
        Product.objects.create(restaurant=r2, category=cat2, name='دمنوش', price=Decimal('45000'))

    def test_owner_dashboard_only_counts_their_own_data(self):
        self.client.login(username='owner1', password='StrongPass123!')
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category_count'], 1)
        self.assertEqual(response.context['product_count'], 1)
        self.assertContains(response, 'کافه اول')
        self.assertNotContains(response, 'کافه دوم')

    def test_second_owner_sees_only_their_own_two_products(self):
        self.client.login(username='owner2', password='StrongPass123!')
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['category_count'], 1)
        self.assertEqual(response.context['product_count'], 2)
